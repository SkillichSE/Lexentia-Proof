"""
Configuration for AI model benchmarks.
Model IDs last verified: 2026-03-20
Groq deprecations: https://console.groq.com/docs/deprecations
OpenRouter models:  https://openrouter.ai/models
"""

MODELS = {
    "groq": {
        # ── Production (stable, won't be yanked without notice) ──────────────
        "llama-3.1-8b": {
            "id": "llama-3.1-8b-instant",
            "name": "Llama 3.1 8B Instant",
            "provider": "Groq",
            "size": "8B",
            "context": "128k",
        },
        "llama-3.3-70b": {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama 3.3 70B Versatile",
            "provider": "Groq",
            "size": "70B",
            "context": "128k",
        },
        "gpt-oss-120b": {
            "id": "openai/gpt-oss-120b",        # replaces deepseek-r1-distill-llama-70b
            "name": "GPT-OSS 120B",
            "provider": "Groq",
            "size": "120B",
            "context": "131k",
        },
        # ── Preview (may change, but currently active) ───────────────────────
        "llama-4-scout": {
            "id": "meta-llama/llama-4-scout-17b-16e-instruct",
            "name": "Llama 4 Scout 17B",
            "provider": "Groq",
            "size": "17Bx16E",
            "context": "131k",
        },
        "qwen3-32b": {
            "id": "qwen/qwen3-32b",             # replaces qwen-qwq-32b
            "name": "Qwen 3 32B",
            "provider": "Groq",
            "size": "32B",
            "context": "32k",
        },
    },

    "google": {
        "gemini-2.0-flash": {
            "id": "gemini-2.0-flash",
            "name": "Gemini 2.0 Flash",
            "provider": "Google",
            "size": "N/A",
            "context": "1M",
        },
        "gemini-2.0-flash-lite": {
            "id": "gemini-2.0-flash-lite",
            "name": "Gemini 2.0 Flash Lite",
            "provider": "Google",
            "size": "N/A",
            "context": "1M",
        },
    },

    # Set OPENROUTER_API_KEY in GitHub Secrets to enable these.
    "openrouter": {
        "deepseek-r1": {
            "id": "deepseek/deepseek-r1",       # still valid
            "name": "DeepSeek R1",
            "provider": "OpenRouter",
            "size": "671B",
            "context": "64k",
        },
        "deepseek-v3": {
            "id": "deepseek/deepseek-chat-v3-0324",
            "name": "DeepSeek V3",
            "provider": "OpenRouter",
            "size": "671B",
            "context": "128k",
        },
        "claude-haiku": {
            "id": "anthropic/claude-haiku-4-5",
            "name": "Claude Haiku 4.5",
            "provider": "OpenRouter",
            "size": "N/A",
            "context": "200k",
        },
        "qwen-3-235b": {
            "id": "qwen/qwen3-235b-a22b",
            "name": "Qwen 3 235B",
            "provider": "OpenRouter",
            "size": "235B",
            "context": "41k",
        },
        "mistral-small": {
            "id": "mistralai/mistral-small-3.2-24b-instruct",
            "name": "Mistral Small 3.2 24B",
            "provider": "OpenRouter",
            "size": "24B",
            "context": "128k",
        },
        "llama-4-maverick": {
            "id": "meta-llama/llama-4-maverick",
            "name": "Llama 4 Maverick",
            "provider": "OpenRouter",
            "size": "17Bx128E",
            "context": "1M",
        },
    },
}

TESTS = {
    "speed": {
        "simple": "Write a haiku about artificial intelligence.",
        "medium": "Explain quantum computing in simple terms (200 words).",
        "long":   "Write a detailed tutorial on Python decorators with examples.",
    },
    "code": {
        "easy":   "Write a Python function to check if a number is prime.",
        "medium": "Create a binary search implementation in Python with comments.",
        "hard":   "Implement a LRU cache in Python using OrderedDict.",
    },
    "reasoning": {
        "logic":  "If all bloops are razzies and all razzies are lazzies, are all bloops definitely lazzies?",
        "math":   "A train travels 120 km in 2 hours. Another train travels 180 km in 3 hours. Which is faster?",
        "puzzle": "You have 12 balls, one is slightly heavier. Using a balance scale only 3 times, how do you find it?",
    },
    "translation": {
        "en_ru":   "Translate to Russian: 'The quick brown fox jumps over the lazy dog.'",
        "ru_en":   "Translate to English: 'Искусственный интеллект меняет мир.'",
        "complex": "Translate to Spanish: 'Machine learning models require substantial computational resources.'",
    },
}

RATE_LIMITS = {
    "groq":       30,
    "google":     15,
    "openrouter": 20,
}
