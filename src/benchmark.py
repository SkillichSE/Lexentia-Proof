import os, re, json, time, subprocess, argparse
from datetime import datetime
from pathlib import Path
import requests
from config import MODELS, TESTS

GROQ_API       = "https://api.groq.com/openai/v1/chat/completions"
OPENROUTER_API = "https://openrouter.ai/api/v1/chat/completions"

REQUEST_DELAY = {"groq": 2, "google": 6, "openrouter": 2}

REASONING_ANSWERS = {
    "syllogism":      ["yes", "correct", "true", "definitely"],
    "speed_math":     ["same", "equal", "neither", "both"],
    "river_crossing": ["chicken"],
    "coin_flip":      ["1/2", "0.5", "50%", "50 percent", "one half", "half"],
    "counting":       ["11", "eleven"],
}

_OR_ROTATE_STATUSES = {429, 402}


def size_category(size_str):
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
    if b <= 10:  return "small"
    if b <= 50:  return "medium"
    return "large"


def _load_openrouter_keys():
    keys = []
    for i in range(1, 11):
        k = os.getenv(f"OPENROUTER_API_KEY_{i}", "").strip()
        if k:
            keys.append(k)
    plain = os.getenv("OPENROUTER_API_KEY", "").strip()
    if plain and plain not in keys:
        keys.append(plain)
    return keys


class ModelBenchmark:
    def __init__(self, active_providers=None, active_models=None, merge=False):
        self.groq_key         = os.getenv("GROQ_API_KEY")
        self.google_key       = os.getenv("GOOGLE_API_KEY")
        self._openrouter_keys = _load_openrouter_keys()
        self._or_key_index    = 0
        self.active_providers = active_providers
        self.active_models    = active_models
        self.merge            = merge
        self.results          = []

    @property
    def openrouter_key(self):
        if not self._openrouter_keys:
            return None
        return self._openrouter_keys[self._or_key_index]

    def _rotate_openrouter_key(self):
        if self._or_key_index + 1 < len(self._openrouter_keys):
            self._or_key_index += 1
            hint = self._openrouter_keys[self._or_key_index][:8] + "..."
            print(f"\n    [openrouter] rate-limited → key #{self._or_key_index + 1}/{len(self._openrouter_keys)} ({hint})", end="")
            return True
        return False

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
                tokens = usage.get("total_tokens", 0) or usage.get("completion_tokens", 0)
                return {"success": True, "content": content,
                        "total_time": round(elapsed, 3), "tokens": tokens,
                        "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0}
            err = f"Status {r.status_code}"
            try:
                msg = r.json().get("error", {}).get("message", "")
                if msg: err += f" - {msg[:120]}"
            except Exception: pass
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
                tokens = body.get("usageMetadata", {}).get("totalTokenCount", 0)
                return {"success": True, "content": content,
                        "total_time": round(elapsed, 3), "tokens": tokens,
                        "tokens_per_sec": round(tokens / elapsed, 2) if elapsed > 0 else 0}
            err = f"Status {r.status_code}"
            try:
                msg = r.json().get("error", {}).get("message", "")
                if msg: err += f" - {msg[:120]}"
            except Exception: pass
            return {"success": False, "error": err}
        except Exception as e:
            return {"success": False, "error": str(e)[:120]}

    def call_openrouter(self, model_id, prompt):
        if not self._openrouter_keys:
            return {"success": False, "error": "no OPENROUTER_API_KEY configured"}
        while True:
            result = self._openai_post(OPENROUTER_API, {
                "Authorization": f"Bearer {self.openrouter_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://modellens.ai",
                "X-Title": "ModelLens",
            }, model_id, prompt, timeout=45)
            if result["success"]:
                return result
            err = result.get("error", "")
            m = re.search(r"Status (\d+)", err)
            status = int(m.group(1)) if m else 0
            if status in _OR_ROTATE_STATUSES and self._rotate_openrouter_key():
                continue
            if status in _OR_ROTATE_STATUSES:
                print(f"\n    [openrouter] all {len(self._openrouter_keys)} key(s) exhausted", end="")
            return result

    def _call(self, provider, model_id, prompt):
        return {"groq": self.call_groq, "google": self.call_google,
                "openrouter": self.call_openrouter}[provider](model_id, prompt)

    def eval_code(self, test_name, response):
        cfg = TESTS["code"][test_name]
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
            try:
                proc = subprocess.run(
                    ["python3", "-c", f"{code}\nprint(repr({fn_name}({repr(inp)})))"],
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
        return {"correct": correct, "score": 100 if correct else 0, "answer_given": response.strip()[:80]}

    def eval_instruction(self, test_name, response):
        if not response:
            return {"score": 0, "reason": "empty response"}
        cfg = TESTS["instruction"][test_name]
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
            return {"score": 100 if len(sentences) == cfg["count"] else 50 if abs(len(sentences)-cfg["count"]) <= 1 else 0,
                    "found": len(sentences), "expected": cfg["count"]}
        return {"score": 0, "reason": "unknown check type"}

    def eval_translation(self, test_name, response):
        if not response:
            return {"score": 0}
        cfg = TESTS["translation"][test_name]
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
        mid   = model_info["id"]
        result = {
            "model_id":      model_info.get("key", mid),
            "model_name":    model_info["name"],
            "provider":      model_info["provider"],
            "size":          model_info["size"],
            "size_category": size_category(model_info["size"]),
            "context":       model_info.get("context", "N/A"),
            "timestamp":     datetime.now().isoformat(),
            "tests":         {},
        }

        print("  speed...", end=" ", flush=True)
        speed_raw = []
        for name, prompt in TESTS["speed"].items():
            r = self._call(provider, mid, prompt)
            if r["success"]:
                speed_raw.append({"test": name, "time": r["total_time"],
                                  "tokens_per_sec": r["tokens_per_sec"], "tokens": r["tokens"]})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
            time.sleep(delay)
        avg_tps = round(sum(x["tokens_per_sec"] for x in speed_raw) / len(speed_raw), 2) if speed_raw else 0
        result["tests"]["speed"] = {"avg_tokens_per_sec": avg_tps, "details": speed_raw}
        print(f"done ({avg_tps} tok/s)")

        print("  code...", end=" ", flush=True)
        code_raw = []
        for name in TESTS["code"]:
            r = self._call(provider, mid, TESTS["code"][name]["prompt"])
            if r["success"]:
                code_raw.append({"test": name, **self.eval_code(name, r["content"])})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                code_raw.append({"test": name, "pass_rate": 0.0, "passed": 0,
                                 "total": len(TESTS["code"][name]["expected"]), "error": r["error"]})
            time.sleep(delay)
        avg_code = round(sum(x["pass_rate"] for x in code_raw) / len(code_raw) * 100, 1) if code_raw else 0
        result["tests"]["code"] = {"avg_score": avg_code, "details": code_raw}
        print(f"done ({sum(x.get('passed',0) for x in code_raw)}/{sum(x.get('total',0) for x in code_raw)} passed)")

        print("  reasoning...", end=" ", flush=True)
        reasoning_raw = []
        for name, cfg in TESTS["reasoning"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
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
        for name, cfg in TESTS["instruction"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
                instr_raw.append({"test": name, **self.eval_instruction(name, r["content"])})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                instr_raw.append({"test": name, "score": 0, "error": r["error"]})
            time.sleep(delay)
        avg_instr = round(sum(x["score"] for x in instr_raw) / len(instr_raw), 1) if instr_raw else 0
        result["tests"]["instruction"] = {"avg_score": avg_instr, "details": instr_raw}
        print(f"done ({avg_instr}/100)")

        print("  translation...", end=" ", flush=True)
        trans_raw = []
        for name, cfg in TESTS["translation"].items():
            r = self._call(provider, mid, cfg["prompt"])
            if r["success"]:
                trans_raw.append({"test": name, **self.eval_translation(name, r["content"])})
            else:
                print(f"\n    [{name}] {r['error']}", end="")
                trans_raw.append({"test": name, "score": 0})
            time.sleep(delay)
        avg_trans = round(sum(x["score"] for x in trans_raw) / len(trans_raw), 1) if trans_raw else 0
        result["tests"]["translation"] = {"avg_score": avg_trans, "details": trans_raw}
        print(f"done ({avg_trans}/100)")

        quality = round(avg_code * 0.30 + reasoning_score * 0.25 + avg_instr * 0.15 + avg_trans * 0.10, 1)
        result["quality_score"] = quality
        result["raw_speed"]     = avg_tps
        result["overall_score"] = quality
        return result

    def run_benchmark(self):
        print("ModelLens Benchmark")
        print(f"Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

        key_map = {"groq": self.groq_key, "google": self.google_key, "openrouter": bool(self._openrouter_keys)}
        active = []
        if self.groq_key: active.append("Groq")
        if self.google_key: active.append("Google")
        if self._openrouter_keys:
            n = len(self._openrouter_keys)
            active.append(f"Openrouter ({n} key{'s' if n > 1 else ''})")
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
                cat = size_category(minfo["size"])
                print(f"\n{minfo['name']} [{cat}] via {provider}")
                r = self.run_model(provider, minfo)
                if r:
                    self.results.append(r)
                    print(f"  -> quality={r['quality_score']}  speed={r['raw_speed']} tok/s")

        self.save_results()

    def save_results(self):
        date_str = datetime.now().strftime("%Y-%m-%d")
        Path("../docs/data/results").mkdir(parents=True, exist_ok=True)

        for cat in ["small", "medium", "large", "unknown"]:
            cat_speeds = [r["raw_speed"] for r in self.results if r.get("size_category") == cat and r["raw_speed"] > 0]
            max_speed = max(cat_speeds, default=1)
            for r in self.results:
                if r.get("size_category") == cat:
                    r["speed_score"] = round(r["raw_speed"] / max_speed * 100, 1)

        daily_path = Path(f"../docs/data/results/{date_str}.json")
        if self.merge and daily_path.exists():
            try:
                existing = json.loads(daily_path.read_text())
                tested_ids = {r["model_id"] for r in self.results}
                kept = [r for r in existing if r["model_id"] not in tested_ids]
                self.results = kept + self.results
                print(f"  merged with {len(kept)} existing results")
            except Exception as e:
                print(f"  merge failed ({e}), overwriting")

        with open(daily_path, "w") as f:
            json.dump(self.results, f, indent=2)
        with open("../docs/data/results/latest.json", "w") as f:
            json.dump({"date": date_str, "timestamp": datetime.now().isoformat(),
                       "results": self.results}, f, indent=2)

        def best_per_model(results, sort_key):
            seen = {}
            for r in sorted(results, key=lambda x: x.get(sort_key, 0), reverse=True):
                if r.get("quality_score", 0) == 0 and r.get("raw_speed", 0) == 0:
                    continue
                if r["model_name"] not in seen:
                    seen[r["model_name"]] = r
            return list(seen.values())

        q_board = sorted(best_per_model(self.results, "quality_score"), key=lambda x: x["quality_score"], reverse=True)
        with open("../docs/data/results/leaderboard.json", "w") as f:
            json.dump(q_board, f, indent=2)

        s_board = sorted(best_per_model(self.results, "raw_speed"), key=lambda x: x["raw_speed"], reverse=True)
        with open("../docs/data/results/leaderboard_speed.json", "w") as f:
            json.dump(s_board, f, indent=2)

        print(f"\nSaved {date_str}.json ({len(self.results)} models)")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--providers", default=None)
    parser.add_argument("--models",    default=None)
    parser.add_argument("--merge",     action="store_true")
    args = parser.parse_args()

    active_providers = [p.strip().lower() for p in args.providers.split(",")] if args.providers else None
    active_models    = [m.strip() for m in args.models.split(",")]            if args.models    else None

    ModelBenchmark(active_providers=active_providers,
                   active_models=active_models,
                   merge=args.merge).run_benchmark()
