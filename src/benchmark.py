import os, re, json, time, subprocess, argparse
from datetime import datetime
from pathlib import Path
import requests
from config import MODELS, TESTS, TESTS_BY_TIER, SCORE_WEIGHTS


def get_tests_for_tier(tier):
    """Return the test-suite dict for a given size_category tier."""
    return TESTS_BY_TIER.get(tier, TESTS_BY_TIER.get("medium", TESTS))


GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"
CEREBRAS_API = "https://api.cerebras.ai/v1/chat/completions"
TOGETHER_API = "https://api.together.xyz/v1/chat/completions"
SAMBANOVA_API = "https://api.sambanova.ai/v1/chat/completions"

REQUEST_DELAY = {"groq": 2, "google": 6, "openrouter": 4, "cerebras": 1, "together": 2}

import random

REASONING_ANSWERS = {
    "syllogism":    ["yes", "correct", "true", "definitely"],
    "speed_math":   ["same", "equal", "neither", "both"],
    "river_crossing": ["chicken"],
    "coin_flip":    ["1/2", "0.5", "50%", "50 percent", "one half", "half"],
    "counting":     ["11", "eleven"],
    "knights_knaves": ["knight"],
    "word_problem": ["14", "fourteen"],
    "deduction":    ["yes", "correct", "true"],
    "scheduling":   ["no", "not possible", "impossible"],
    "base_rate":    ["healthy", "not sick", "more likely healthy"],
}

_OR_ROTATE_STATUSES = {429, 402}

_OR_KEY_COOLDOWN = 62
_FATAL_MODEL_PATTERNS = (
    "decommissioned",
    "no longer supported",
    "not found",
    "unable to access model",
    "credit limit exceeded",
    "all keys at limit",
)


def size_category(size_str, config_category=None):
    """Determine size category.
    If config_category is provided and not 'unknown', use it directly —
    the config author knows better (e.g. Gemini 2.5 Flash has size='N/A').
    Only fall back to heuristic parsing when no config value is present.
    """
    if config_category and config_category != "unknown":
        return config_category
    s = size_str.upper().replace(" ", "")
    if s in ("N/A", "UNKNOWN", ""):
        return "unknown"
    moe = re.search(r"(\d+(?:\.\d+)?)B\s*[Xx]\s*(\d+)", s)
    if moe:
        return _bucket(float(moe.group(1)))
    plain = re.search(r"(\d+(?:\.\d+)?)B", s)
    if plain:
        return _bucket(float(plain.group(1)))
    return "unknown"


def _bucket(b):
    # small: ≤10B  |  medium: 11–50B  |  large: >50B
    if b <= 10:  return "small"
    if b <= 50:  return "medium"
    return "large"


def _load_openrouter_keys():
    keys = []

    i = 1
    while True:
        k = os.getenv(f"OPENROUTER_API_KEY_{i}", "").strip()
        if not k:
            break
        keys.append(k)
        i += 1

    plain = os.getenv("OPENROUTER_API_KEY", "").strip()
    if plain and plain not in keys:
        keys.append(plain)
    return keys


class ModelBenchmark:
    def __init__(self, active_providers=None, active_models=None, merge=False):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.cerebras_key = os.getenv("CEREBRAS_API_KEY")
        self.together_key = os.getenv("TOGETHER_API_KEY")
        self.sambanova_key = os.getenv("SAMBANOVA_API_KEY")
        self._openrouter_keys = _load_openrouter_keys()
        self._or_key_index = 0

        self._or_key_limited_until = {}
        self.active_providers = active_providers
        self.active_models = active_models
        self.merge = merge
        self.results = []

    @property
    def openrouter_key(self):
        if not self._openrouter_keys:
            return None
        return self._openrouter_keys[self._or_key_index]

    def _mark_or_key_limited(self, idx):
        """Mark a key as rate-limited for _OR_KEY_COOLDOWN seconds."""
        self._or_key_limited_until[idx] = time.time() + _OR_KEY_COOLDOWN

    def _next_available_or_key(self):
        """Return index of first non-limited key, or None if all are limited."""
        now = time.time()
        for i, key in enumerate(self._openrouter_keys):
            until = self._or_key_limited_until.get(i, 0)
            if now >= until:
                return i
        return None

    def _reset_openrouter_keys(self):
        """Reset index for next model (no waiting)."""
        self._or_key_index = 0

    def _ping_openrouter_keys_parallel(self, model_id):
        """Check all OR keys in parallel with a tiny prompt. Returns True if at least one works."""
        import concurrent.futures
        now = time.time()

        candidates = [i for i, k in enumerate(self._openrouter_keys)
                      if now >= self._or_key_limited_until.get(i, 0)]
        if not candidates:
            return False

        mini_prompt = "Hi"

        def try_key(idx):
            key = self._openrouter_keys[idx]
            try:
                r = requests.post(OPENROUTER_API, headers={
                    "Authorization": f"Bearer {key}",
                    "Content-Type": "application/json",
                    "HTTP-Referer": "https://modellens.ai",
                    "X-Title": "Lexentia Proof",
                }, json={
                    "model": model_id,
                    "messages": [{"role": "user", "content": mini_prompt}],
                    "max_tokens": 1,
                }, timeout=10)
                return idx, r.status_code
            except Exception:
                return idx, 0

        with concurrent.futures.ThreadPoolExecutor(max_workers=len(candidates)) as ex:
            futures = {ex.submit(try_key, i): i for i in candidates}
            any_ok = False
            for f in concurrent.futures.as_completed(futures):
                idx, status = f.result()
                if status in _OR_ROTATE_STATUSES:
                    self._mark_or_key_limited(idx)
                elif status == 200:
                    any_ok = True

        return any_ok

    def _openai_post(self, url, headers, model_id, prompt, timeout=45):
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.1,
            "max_tokens": 300,
        }
        start = time.time()
        try:
            r = requests.post(url, headers=headers, json=data, timeout=timeout)
            elapsed = time.time() - start
            if r.status_code == 200:
                body = r.json()
                content = body["choices"][0]["message"].get("content") or ""
                usage = body.get("usage", {})
                tokens = usage.get("completion_tokens", 0) or usage.get("total_tokens", 0)
                return {"success": True, "content": content,
                        "total_time": round(elapsed, 3), "tokens": tokens,
                        "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0}
            err = f"Status {r.status_code}"
            try:
                msg = r.json().get("error", {}).get("message", "")
                if msg: err += f" - {msg[:120]}"
            except Exception:
                pass
            return {"success": False, "error": err}
        except Exception as e:
            return {"success": False, "error": str(e)[:120]}

    def call_groq(self, model_id, prompt):
        if not self.groq_key:
            return {"success": False, "error": "GROQ_API_KEY not set"}
        return self._openai_post(GROQ_API,
                                 {"Authorization": f"Bearer {self.groq_key}", "Content-Type": "application/json"},
                                 model_id, prompt)

    def call_google(self, model_id, prompt):
        if not self.google_key:
            return {"success": False, "error": "GOOGLE_API_KEY not set"}
        url = (f"https://generativelanguage.googleapis.com/v1beta/models/"
               f"{model_id}:generateContent?key={self.google_key}")
        data = {
            "contents": [{"parts": [{"text": prompt}]}],
            "generationConfig": {"temperature": 0.1, "maxOutputTokens": 300},
        }
        start = time.time()
        try:
            r = requests.post(url, json=data, timeout=20)
            elapsed = time.time() - start
            if r.status_code == 200:
                body = r.json()
                if not body.get("candidates"):
                    return {"success": False, "error": "no candidates"}
                content = body["candidates"][0]["content"]["parts"][0].get("text") or ""
                tokens = body.get("usageMetadata", {}).get("candidatesTokenCount", 0) or body.get("usageMetadata", {}).get("totalTokenCount", 0)
                return {"success": True, "content": content,
                        "total_time": round(elapsed, 3), "tokens": tokens,
                        "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0}
            err = f"Status {r.status_code}"
            try:
                msg = r.json().get("error", {}).get("message", "")
                if msg: err += f" - {msg[:120]}"
            except Exception:
                pass
            return {"success": False, "error": err}
        except Exception as e:
            return {"success": False, "error": str(e)[:120]}

    def call_openrouter(self, model_id, prompt):
        if not self._openrouter_keys:
            return {"success": False, "error": "no OPENROUTER_API_KEY configured"}

        start_idx = self._next_available_or_key()
        if start_idx is None:
            return {"success": False, "error": "all keys at limit (skipped)"}
        self._or_key_index = start_idx
        tried = set()
        while True:
            idx = self._or_key_index
            if idx in tried:
                print(f"\n    [openrouter] all {len(self._openrouter_keys)} keys at limit, skipping", flush=True)
                return {"success": False, "error": "all keys at limit (skipped)"}
            tried.add(idx)
            hint = self._openrouter_keys[idx][:12] + "..."
            if idx > 0:
                print(f"\n    [openrouter] key #{idx + 1}/{len(self._openrouter_keys)} ({hint})", end="", flush=True)
            result = self._openai_post(OPENROUTER_API, {
                "Authorization": f"Bearer {self._openrouter_keys[idx]}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://modellens.ai",
                "X-Title": "Lexentia Proof",
            }, model_id, prompt, timeout=45)
            if result["success"]:
                return result
            err = result.get("error", "")
            m = re.search(r"Status (\d+)", err)
            status = int(m.group(1)) if m else 0
            if status in _OR_ROTATE_STATUSES:
                self._mark_or_key_limited(idx)
                next_idx = self._next_available_or_key()
                if next_idx is not None and next_idx not in tried:
                    self._or_key_index = next_idx
                    continue

                print(f"\n    [openrouter] all {len(self._openrouter_keys)} keys at limit, skipping", flush=True)
                return {"success": False, "error": "all keys at limit (skipped)"}
            return result

    def call_cerebras(self, model_id, prompt):
        if not self.cerebras_key:
            return {"success": False, "error": "CEREBRAS_API_KEY not set"}
        return self._openai_post(CEREBRAS_API,
                                 {"Authorization": f"Bearer {self.cerebras_key}", "Content-Type": "application/json"},
                                 model_id, prompt)

    def call_together(self, model_id, prompt):
        if not self.together_key:
            return {"success": False, "error": "TOGETHER_API_KEY not set"}
        return self._openai_post(TOGETHER_API,
                                 {"Authorization": f"Bearer {self.together_key}", "Content-Type": "application/json"},
                                 model_id, prompt)

    def call_sambanova(self, model_id, prompt):
        if not self.sambanova_key:
            return {"success": False, "error": "SAMBANOVA_API_KEY not set"}
        return self._openai_post(SAMBANOVA_API,
                                 {"Authorization": f"Bearer {self.sambanova_key}", "Content-Type": "application/json"},
                                 model_id, prompt)

    def _call(self, provider, model_id, prompt):
        fn = {"groq": self.call_groq, "google": self.call_google,
              "openrouter": self.call_openrouter,
              "cerebras": self.call_cerebras,
              "together": self.call_together,
              "sambanova": self.call_sambanova}.get(provider)
        if not fn:
            return {"success": False, "error": f"unknown provider: {provider}"}
        result = fn(model_id, prompt)

        if not result["success"] and "429" in result.get("error", ""):
            model_info = self._current_model_info
            fallbacks = model_info.get("fallbacks", [])
            for fb_provider, fb_model_id in fallbacks:
                print(f"\n    [fallback] {provider} 429 → trying {fb_provider}/{fb_model_id}", end="", flush=True)
                time.sleep(1 + random.random())
                fb_fn = {"groq": self.call_groq, "cerebras": self.call_cerebras,
                         "together": self.call_together}.get(fb_provider)
                if fb_fn:
                    fb_result = fb_fn(fb_model_id, prompt)
                    if fb_result["success"]:
                        fb_result["via_fallback"] = f"{fb_provider}/{fb_model_id}"
                        return fb_result
        return result

    def _is_fatal_model_error(self, err):
        if not err:
            return False
        low = err.lower()
        return any(p in low for p in _FATAL_MODEL_PATTERNS)

    def eval_code(self, test_name, response, tier_tests=None):
        if tier_tests is None:
            tier_tests = TESTS
        cfg = tier_tests["code"][test_name]
        fn_name = cfg.get("fn") or cfg["prompt"].split("called ")[1].split("(")[0].strip()
        if not response:
            return {"pass_rate": 0.0, "passed": 0, "total": len(cfg["expected"]), "error": "empty response"}
        code_match = re.search(r"```(?:python)?\s*\n([\s\S]+?)```", response)
        code = code_match.group(1).strip() if code_match else response.strip()
        lines, code_lines, found_def = code.splitlines(), [], False
        for line in lines:
            if line.strip().startswith("def ") or found_def:
                found_def = True
                code_lines.append(line)
        if code_lines:
            code = "\n".join(code_lines)
        results = []
        for inp, expected in zip(cfg["test_input"], cfg["expected"]):
            # Support tuple inputs for multi-argument functions (e.g. binary_search(arr, target))
            call_expr = f"{fn_name}(*{repr(inp)})" if isinstance(inp, tuple) else f"{fn_name}({repr(inp)})"
            try:
                proc = subprocess.run(
                    ["python3", "-c", f"{code}\nprint(repr({call_expr}))"],
                    capture_output=True, text=True, timeout=5)
                if proc.returncode == 0:
                    output = proc.stdout.strip()
                    results.append({"input": repr(inp), "expected": repr(expected),
                                    "got": output, "passed": output == repr(expected)})
                else:
                    results.append({"input": repr(inp), "expected": repr(expected),
                                    "got": proc.stderr.strip()[:100], "passed": False})
            except subprocess.TimeoutExpired:
                results.append({"input": repr(inp), "expected": repr(expected), "got": "timeout", "passed": False})
            except Exception as e:
                results.append({"input": repr(inp), "expected": repr(expected), "got": str(e)[:80], "passed": False})
        passed_count = sum(1 for r in results if r["passed"])
        return {"pass_rate": round(passed_count / len(results), 2),
                "passed": passed_count, "total": len(results), "details": results}

    def eval_reasoning(self, test_name, response):
        if not response:
            return {"correct": False, "score": 0}
        short = response.lower().strip()[:60]
        correct = any(a in short for a in REASONING_ANSWERS.get(test_name, []))
        return {"correct": correct, "score": 100 if correct else 0, "answer_given": response.strip()}

    def eval_instruction(self, test_name, response, tier_tests=None):
        if tier_tests is None:
            tier_tests = TESTS
        if not response:
            return {"score": 0, "reason": "empty response"}
        cfg = tier_tests["instruction"][test_name]
        if cfg["check"] == "json_keys":
            m = re.search(r'\{[\s\S]*\}', response)
            if not m:
                return {"score": 0, "reason": "no JSON found"}
            try:
                obj = json.loads(m.group())
                missing = [k for k in cfg["required_keys"] if k not in obj]
                return {"score": 50 if missing else 100, "reason": f"missing: {missing}" if missing else "ok"}
            except json.JSONDecodeError as e:
                return {"score": 0, "reason": f"invalid JSON: {str(e)[:60]}"}
        if cfg["check"] == "numbered_list":
            lines = [l.strip() for l in response.strip().split('\n') if l.strip()]
            numbered = [l for l in lines if re.match(r'^\d+[\.\)]\s+\S', l)]
            return {"score": 100 if len(numbered) == cfg["count"] else 50 if numbered else 0,
                    "found": len(numbered), "expected": cfg["count"]}
        if cfg["check"] == "sentence_count":
            sentences = [s.strip() for s in re.split(r'[.!?]+(?:\s|$)', response.strip()) if s.strip()]
            return {"score": 100 if len(sentences) == cfg["count"] else 50 if abs(
                len(sentences) - cfg["count"]) <= 1 else 0,
                    "found": len(sentences), "expected": cfg["count"]}
        if cfg["check"] == "json_nested_user":
            m = re.search(r'\{[\s\S]*\}', response)
            if not m:
                return {"score": 0, "reason": "no JSON found"}
            try:
                obj = json.loads(m.group())
                user = obj.get("user", {})
                ok = (
                        isinstance(user, dict)
                        and isinstance(user.get("name"), str)
                        and isinstance(user.get("scores"), list) and len(user["scores"]) == 3
                        and isinstance(user.get("active"), bool)
                )
                return {"score": 100 if ok else 50, "reason": "ok" if ok else "structure mismatch"}
            except json.JSONDecodeError as e:
                return {"score": 0, "reason": f"invalid JSON: {str(e)[:60]}"}
        return {"score": 0, "reason": "unknown check type"}

    def eval_translation(self, test_name, response, tier_tests=None):
        if tier_tests is None:
            tier_tests = TESTS
        if not response:
            return {"score": 0}
        cfg = tier_tests["translation"][test_name]
        text = response.strip()
        if cfg["check"] == "cyrillic":
            ratio = sum(1 for c in text if '\u0400' <= c <= '\u04FF') / max(len(text), 1)
            return {"score": 100 if ratio > 0.2 else 0, "cyrillic_ratio": round(ratio, 2)}
        if cfg["check"] == "latin":
            ratio = sum(1 for c in text if c.isascii() and c.isalpha()) / max(len(text), 1)
            return {"score": 100 if ratio > 0.6 else 0, "latin_ratio": round(ratio, 2)}
        if cfg["check"] == "spanish_words":
            found = sum(1 for w in cfg["keywords"] if w in text.lower())
            return {"score": 100 if found >= 3 else 50 if found >= 1 else 0, "keywords_found": found}
        return {"score": 0}

    def run_model(self, provider, model_info):
        delay = REQUEST_DELAY.get(provider, 2)
        mid = model_info["id"]
        self._current_model_info = model_info
        success_calls = 0
        if provider == "openrouter":
            self._or_key_index = 0

            if self._next_available_or_key() is None:
                print("  [openrouter] all keys at limit — skipping model")
                return None

            has_live = self._ping_openrouter_keys_parallel(mid)
            if not has_live:
                print("  [openrouter] all keys at limit — skipping model")
                return None

        cat = size_category(model_info["size"], model_info.get("size_category"))
        tier_tests = TESTS_BY_TIER[cat]  # picks the right difficulty tier

        # display_provider is the human-readable label from config (e.g. "Groq",
        # "OpenRouter"). if it's missing for any reason fall back to the routing
        # key capitalized. api_provider is always the lowercase routing key used
        # internally (groq / openrouter / cerebras / together / google / sambanova).
        display_provider = model_info.get("provider") or provider.capitalize()

        result = {
            "model_id":       model_info.get("key", mid),
            "model_name":     model_info["name"],
            "provider":       display_provider,
            "api_provider":   provider,
            "is_open_source": model_info.get("is_open_source", False),
            "size":           model_info["size"],
            "size_category":  cat,
            "tier":           cat,
            "context":        model_info.get("context", "N/A"),
            "timestamp":      datetime.now().isoformat(),
            "tests":          {},
        }

        print("  speed...", end=" ", flush=True)
        speed_raw = []
        for name, prompt in tier_tests["speed"].items():
            r = self._call(provider, mid, prompt)
            if r["success"]:
                success_calls += 1
                speed_raw.append({"test": name, "time": r["total_time"],
                                  "tokens_per_sec": r["tokens_per_sec"], "tokens": r["tokens"]})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                if self._is_fatal_model_error(r.get("error")):
                    print("\n  [skip] fatal model error")
                    return None
            time.sleep(delay)
        avg_tps = round(sum(x["tokens_per_sec"] for x in speed_raw) / len(speed_raw), 2) if speed_raw else 0
        result["tests"]["speed"] = {"avg_tokens_per_sec": avg_tps, "details": speed_raw}
        print(f"done ({avg_tps} tok/s)")

        print("  code...", end=" ", flush=True)
        code_raw = []
        for name in tier_tests["code"]:
            r = self._call(provider, mid, tier_tests["code"][name]["prompt"])
            if r["success"]:
                success_calls += 1
                code_raw.append({"test": name, **self.eval_code(name, r["content"], tier_tests)})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                code_raw.append({"test": name, "pass_rate": 0.0, "passed": 0,
                                 "total": len(tier_tests["code"][name]["expected"]), "error": r["error"]})
            time.sleep(delay)
        avg_code = round(sum(x["pass_rate"] for x in code_raw) / len(code_raw) * 100, 1) if code_raw else 0
        result["tests"]["code"] = {"avg_score": avg_code, "details": code_raw}
        print(f"done ({sum(x.get('passed', 0) for x in code_raw)}/{sum(x.get('total', 0) for x in code_raw)} passed)")

        print("  reasoning...", end=" ", flush=True)
        reasoning_raw = []
        for name, cfg in tier_tests["reasoning"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
                success_calls += 1
                reasoning_raw.append({"test": name, **self.eval_reasoning(name, r["content"])})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                reasoning_raw.append({"test": name, "correct": False, "score": 0})
            time.sleep(delay)
        correct_count = sum(1 for x in reasoning_raw if x.get("correct"))
        reasoning_score = round(correct_count / len(reasoning_raw) * 100, 1) if reasoning_raw else 0
        result["tests"]["reasoning"] = {"score": reasoning_score, "correct": correct_count,
                                        "total": len(reasoning_raw), "details": reasoning_raw}
        print(f"done ({correct_count}/{len(reasoning_raw)} correct)")

        print("  instructions...", end=" ", flush=True)
        instr_raw = []
        for name, cfg in tier_tests["instruction"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
                success_calls += 1
                instr_raw.append({"test": name, **self.eval_instruction(name, r["content"], tier_tests)})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                instr_raw.append({"test": name, "score": 0, "error": r["error"]})
            time.sleep(delay)
        avg_instr = round(sum(x["score"] for x in instr_raw) / len(instr_raw), 1) if instr_raw else 0
        result["tests"]["instruction"] = {"avg_score": avg_instr, "details": instr_raw}
        print(f"done ({avg_instr}/100)")

        print("  translation...", end=" ", flush=True)
        trans_raw = []
        for name, cfg in tier_tests["translation"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
                success_calls += 1
                trans_raw.append({"test": name, **self.eval_translation(name, r["content"], tier_tests)})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                trans_raw.append({"test": name, "score": 0})
            time.sleep(delay)
        avg_trans = round(sum(x["score"] for x in trans_raw) / len(trans_raw), 1) if trans_raw else 0
        result["tests"]["translation"] = {"avg_score": avg_trans, "details": trans_raw}
        print(f"done ({avg_trans}/100)")

        quality = round(avg_code * SCORE_WEIGHTS['code'] + reasoning_score * SCORE_WEIGHTS['reasoning'] + avg_instr * SCORE_WEIGHTS['instruction'] + avg_trans * SCORE_WEIGHTS['translation'], 1)
        result["quality_score"] = quality
        result["raw_speed"] = avg_tps
        result["overall_score"] = quality
        if success_calls == 0:
            print("  [skip] no successful API responses")
            return None
        if quality == 0 and avg_tps == 0:
            print("  [skip] model returned only zero metrics")
            return None
        return result

    def run_benchmark(self):
        print("Lexentia Proof Benchmark")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        key_map = {"groq": self.groq_key, "google": self.google_key,
                   "openrouter": bool(self._openrouter_keys),
                   "cerebras": self.cerebras_key, "together": self.together_key,
                   "sambanova": self.sambanova_key}
        active = []
        if self.groq_key: active.append("Groq")
        if self.google_key: active.append("Google")
        if self._openrouter_keys:
            n = len(self._openrouter_keys)
            active.append(f"Openrouter ({n} key{'s' if n > 1 else ''})")
        if self.cerebras_key: active.append("Cerebras")
        if self.together_key: active.append("Together")
        if self.sambanova_key: active.append("SambaNova")
        print(f"Providers: {', '.join(active) or 'none'}")

        for provider, models in MODELS.items():
            if self.active_providers and provider not in self.active_providers:
                print(f"Skip {provider} (not in --providers)")
                continue
            if not key_map.get(provider):
                print(f"Skip {provider} (no API key)")
                continue
            for mkey, minfo in models.items():
                if self.active_models and mkey not in self.active_models:
                    continue
                minfo = dict(minfo, key=mkey)
                cat = size_category(minfo["size"], minfo.get("size_category"))
                print(f"\n{minfo['name']} [{cat}] via {provider}")
                r = self.run_model(provider, minfo)
                if r:
                    self.results.append(r)
                    print(f"  -> quality={r['quality_score']}  speed={r['raw_speed']} tok/s")

        self.save_results()

    def save_results(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        now_iso  = datetime.now().isoformat()

        # max history points kept per model (~3 months of daily runs)
        MAX_HISTORY = 90
        # max proof files kept total; oldest are deleted when exceeded
        MAX_PROOFS  = 30

        # output dirs resolved relative to this file, not the caller's cwd
        base        = Path(__file__).resolve().parent.parent / "docs" / "data"
        results_dir = base / "results"
        models_dir  = base / "models"
        proofs_dir  = base / "proofs"
        for d in (results_dir, models_dir, proofs_dir):
            d.mkdir(parents=True, exist_ok=True)

        # ------------------------------------------------------------------ #
        # normalize speed and quality scores within each size tier so that
        # models compete only against peers of the same size category
        # ------------------------------------------------------------------ #
        for cat in ["small", "medium", "large", "unknown"]:
            speeds = [r["raw_speed"] for r in self.results
                      if r.get("size_category") == cat and r["raw_speed"] > 0]
            max_spd = max(speeds, default=1)
            quals   = [r["quality_score"] for r in self.results
                       if r.get("size_category") == cat and r["quality_score"] > 0]
            max_q   = max(quals, default=1)
            for r in self.results:
                if r.get("size_category") == cat:
                    r["speed_score"]       = round(r["raw_speed"]     / max_spd * 100, 1)
                    r["tier_quality_score"] = round(r["quality_score"] / max_q   * 100, 1)

        # ------------------------------------------------------------------ #
        # legacy daily snapshot — kept so existing frontend code keeps working
        # ------------------------------------------------------------------ #
        daily_path = results_dir / f"{date_str}.json"
        if self.merge and daily_path.exists():
            try:
                existing   = json.loads(daily_path.read_text())
                tested_ids = {r["model_id"] for r in self.results}
                kept       = [r for r in existing if r["model_id"] not in tested_ids]
                self.results = kept + self.results
                print(f"  merged with {len(kept)} existing results")
            except Exception as e:
                print(f"  merge failed ({e}), overwriting")

        with open(daily_path, "w") as f:
            json.dump(self.results, f, indent=2)
        with open(results_dir / "latest.json", "w") as f:
            json.dump({"date": date_str, "timestamp": now_iso,
                       "results": self.results}, f, indent=2)

        # ------------------------------------------------------------------ #
        # helper: pick the best result per unique model name
        # ------------------------------------------------------------------ #
        def _best_per_model(results, sort_key):
            seen = {}
            for r in sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True):
                if r.get("quality_score", 0) == 0 and r.get("raw_speed", 0) == 0:
                    continue
                if r["model_name"] not in seen:
                    seen[r["model_name"]] = r
            return list(seen.values())

        # ------------------------------------------------------------------ #
        # 1. leaderboard.json — flat minimal array, fully overwritten each run
        #    contains only what the ui list view needs; no raw test data
        # ------------------------------------------------------------------ #
        leaderboard_rows = []
        for rank, r in enumerate(
            sorted(_best_per_model(self.results, "quality_score"),
                   key=lambda x: x["quality_score"], reverse=True), start=1
        ):
            # api_provider is the routing key (groq/openrouter/…); provider is
            # the display label (Groq / OpenRouter / Google …). if provider is
            # missing for any reason, fall back to api_provider capitalized.
            display_provider = r.get("provider") or r.get("api_provider", "unknown").capitalize()

            leaderboard_rows.append({
                "id":           r["model_id"],
                "rank":         rank,
                "name":         r["model_name"],
                "provider":     display_provider,
                "api_provider": r.get("api_provider", ""),
                "size":         r.get("size", "N/A"),
                "tier":         r.get("size_category", "unknown"),
                "score":        r["quality_score"],
                "speed":        r["raw_speed"],
                "speed_score":  r.get("speed_score", 0),
                "tier_score":   r.get("tier_quality_score", 0),
                "context":      r.get("context", "N/A"),
                "is_os":        r.get("is_open_source", False),
                "status":       "online",
                "updated":      r.get("timestamp", now_iso),
            })

        with open(results_dir / "leaderboard.json", "w") as f:
            json.dump(leaderboard_rows, f, indent=2)

        # legacy speed leaderboard kept for any frontend code still reading it
        s_board = sorted(_best_per_model(self.results, "raw_speed"),
                         key=lambda x: x["raw_speed"], reverse=True)
        with open(results_dir / "leaderboard_speed.json", "w") as f:
            json.dump(s_board, f, indent=2)

        # ------------------------------------------------------------------ #
        # summary.json — lightweight integration endpoint
        # one entry per model, all key fields, no raw test data
        # ------------------------------------------------------------------ #
        summary_models = []
        for rank, r in enumerate(
            sorted(_best_per_model(self.results, "quality_score"),
                   key=lambda x: x["quality_score"], reverse=True), start=1
        ):
            t = r.get("tests", {})
            summary_models.append({
                "id":       r["model_id"],
                "rank":     rank,
                "name":     r["model_name"],
                "provider": r.get("provider") or r.get("api_provider", "unknown").capitalize(),
                "api_provider": r.get("api_provider", ""),
                "size":     r.get("size", "N/A"),
                "tier":     r.get("size_category", "unknown"),
                "context":  r.get("context", "N/A"),
                "is_os":    r.get("is_open_source", False),
                "quality":  r["quality_score"],
                "speed":    r["raw_speed"],
                "scores": {
                    "code":   round(t.get("code",        {}).get("avg_score", 0), 1),
                    "reason": round(t.get("reasoning",   {}).get("score",     0), 1),
                    "instr":  round(t.get("instruction", {}).get("avg_score", 0), 1),
                    "trans":  round(t.get("translation", {}).get("avg_score", 0), 1),
                },
                "updated": r.get("timestamp", now_iso),
            })

        summary_doc = {
            "v":         2,
            "generated": now_iso,
            "date":      date_str,
            "count":     len(summary_models),
            "weights":   {"code": 0.35, "reasoning": 0.30, "instruction": 0.20, "translation": 0.15},
            "models":    summary_models,
        }
        with open(results_dir / "summary.json", "w") as f:
            json.dump(summary_doc, f, separators=(",", ":"))

        # ------------------------------------------------------------------ #
        # 2. /models/{model_id}.json — tech passport + rolling history
        #    history is appended on each run then trimmed to MAX_HISTORY points
        #    so the file never grows unbounded
        # ------------------------------------------------------------------ #
        for r in self.results:
            mid        = r["model_id"]
            model_path = models_dir / f"{mid}.json"

            history_point = {
                "date":  r.get("timestamp", now_iso),
                "score": r["quality_score"],
                "tps":   r["raw_speed"],
            }

            existing_model = {}
            if model_path.exists():
                try:
                    existing_model = json.loads(model_path.read_text())
                except Exception:
                    pass  # corrupted file — start fresh

            # rolling window: append new point, then keep only the last N
            history = existing_model.get("history", []) + [history_point]
            history = history[-MAX_HISTORY:]

            # derive strengths from category scores above the threshold
            tests     = r.get("tests", {})
            strengths = []
            if tests.get("code",        {}).get("avg_score", 0) >= 70:
                strengths.append("code")
            if tests.get("reasoning",   {}).get("score",     0) >= 70:
                strengths.append("reasoning")
            if tests.get("instruction", {}).get("avg_score", 0) >= 70:
                strengths.append("instruction-following")
            if tests.get("translation", {}).get("avg_score", 0) >= 70:
                strengths.append("translation")

            display_provider = r.get("provider") or r.get("api_provider", "unknown").capitalize()

            model_doc = {
                "meta": {
                    "id":           mid,
                    "name":         r["model_name"],
                    "provider":     display_provider,
                    "api_provider": r.get("api_provider", ""),
                    "size":         r.get("size", "N/A"),
                    "tier":         r.get("size_category", "unknown"),
                    "context":      r.get("context", "N/A"),
                    "is_os":        r.get("is_open_source", False),
                },
                "history":      history,
                "strengths":    strengths,
                "last_updated": now_iso,
            }

            with open(model_path, "w") as f:
                json.dump(model_doc, f, indent=2)

        # ------------------------------------------------------------------ #
        # 3. /proofs/{date}_test_{n}.json — raw evidence per session
        #    one new file per run; oldest files are deleted once MAX_PROOFS
        #    is exceeded so the folder never accumulates indefinitely
        # ------------------------------------------------------------------ #
        existing_proofs = sorted(proofs_dir.glob("*_test_*.json"))
        session_idx     = len(existing_proofs) + 1
        proof_filename  = f"{date_str}_test_{session_idx:02d}.json"

        proof_results = {}
        for r in self.results:
            mid        = r["model_id"]
            tests      = r.get("tests", {})
            raw_by_test = {}

            for category, cat_data in tests.items():
                for item in cat_data.get("details", []):
                    test_name = item.get("test", category)
                    verdict   = "passed" if item.get(
                        "pass_rate", item.get("score", item.get("correct", 0))
                    ) else "failed"
                    entry = {
                        "category":    category,
                        "verdict":     verdict,
                        "raw_output":  item.get("answer_given", item.get("got", "")),
                        "token_count": item.get("tokens", 0),
                    }
                    # code tests carry per-case execution detail
                    if "details" in item:
                        entry["execution_log"] = "; ".join(
                            f"{d['input']} -> {d['got']} (expected {d['expected']})"
                            for d in item["details"]
                        )
                    raw_by_test[test_name] = entry

            display_provider = r.get("provider") or r.get("api_provider", "unknown").capitalize()

            proof_results[mid] = {
                "model_name":    r["model_name"],
                "provider":      display_provider,
                "api_provider":  r.get("api_provider", ""),
                "quality_score": r["quality_score"],
                "speed_tps":     r["raw_speed"],
                "tests":         raw_by_test,
            }

        proof_doc = {
            "session_info": {
                "id":          proof_filename.replace(".json", ""),
                "date":        date_str,
                "timestamp":   now_iso,
                "model_count": len(self.results),
            },
            "results": proof_results,
        }

        with open(proofs_dir / proof_filename, "w") as f:
            json.dump(proof_doc, f, indent=2)

        # rotate out oldest proof files if the cap is exceeded
        all_proofs = sorted(proofs_dir.glob("*_test_*.json"))
        for old in all_proofs[:-MAX_PROOFS]:
            try:
                old.unlink()
            except Exception:
                pass

        print(f"\nsaved {date_str}.json        ({len(self.results)} models)")
        print(f"saved leaderboard.json       ({len(leaderboard_rows)} entries)")
        print(f"saved models/*.json          ({len(self.results)} passports, max {MAX_HISTORY} history pts)")
        print(f"saved proofs/{proof_filename} ({len(all_proofs)} total, cap {MAX_PROOFS})")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default=None)
    parser.add_argument("--models", default=None)
    parser.add_argument("--merge", action="store_true")
    args = parser.parse_args()

    active_providers = [p.strip().lower() for p in args.providers.split(",")] if args.providers else None
    active_models = [m.strip() for m in args.models.split(",")] if args.models else None

    ModelBenchmark(active_providers=active_providers,
                   active_models=active_models,
                   merge=args.merge).run_benchmark()