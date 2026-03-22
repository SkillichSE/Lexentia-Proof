# ModelLens — Model configuration
# Last verified: March 2026

MODELS = {
    "groq": {
        # ── Production models (stable, no deprecation planned) ─────────────
        "llama-3.1-8b": {
            "id": "llama-3.1-8b-instant",
            "name": "Llama 3.1 8B Instant",
            "provider": "Groq", "size": "8B",
            "size_category": "small", "context": "131k"
        },
        "llama-3.3-70b": {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama 3.3 70B",
            "provider": "Groq", "size": "70B",
            "size_category": "large", "context": "131k"
        },
        "gpt-oss-120b": {
            "id": "openai/gpt-oss-120b",
            "name": "GPT-OSS 120B",
            "provider": "Groq", "size": "120B",
            "size_category": "large", "context": "131k"
        },
        "gpt-oss-20b": {
            "id": "openai/gpt-oss-20b",
            "name": "GPT-OSS 20B",
            "provider": "Groq", "size": "20B",
            "size_category": "medium", "context": "131k"
        },
        # ── Preview models (for eval, may change) ──────────────────────────
        "llama-4-scout": {
            "id": "meta-llama/llama-4-scout-17b-16e-instruct",
            "name": "Llama 4 Scout 17B",
            "provider": "Groq", "size": "17B",
            "size_category": "medium", "context": "131k"
        },
        "qwen3-32b": {
            "id": "qwen/qwen3-32b",
            "name": "Qwen 3 32B",
            "provider": "Groq", "size": "32B",
            "size_category": "medium", "context": "32k"
        },
        "kimi-k2": {
            "id": "moonshotai/kimi-k2-instruct",
            "name": "Kimi K2",
            "provider": "Groq", "size": "N/A",
            "size_category": "unknown", "context": "131k"
        },
    },

    "openrouter": {
        # All verified on openrouter.ai/collections/free-models, March 2026
        # ── Large ──────────────────────────────────────────────────────────
        "llama-3.3-70b": {
            "id": "meta-llama/llama-3.3-70b-instruct:free",
            "name": "Llama 3.3 70B",
            "provider": "OpenRouter", "size": "70B",
            "size_category": "large", "context": "66k"
        },
        "step-3.5-flash": {
            "id": "stepfun/step-3.5-flash:free",
            "name": "Step 3.5 Flash 196B",
            "provider": "OpenRouter", "size": "196B",
            "size_category": "large", "context": "256k"
        },
        "nemotron-super-120b": {
            "id": "nvidia/nemotron-3-super-120b-a12b:free",
            "name": "Nemotron 3 Super 120B",
            "provider": "OpenRouter", "size": "120B",
            "size_category": "large", "context": "262k"
        },
        "trinity-large": {
            "id": "arcee-ai/trinity-large-preview:free",
            "name": "Trinity Large 400B",
            "provider": "OpenRouter", "size": "400B",
            "size_category": "large", "context": "131k"
        },
        "gpt-oss-120b": {
            "id": "openai/gpt-oss-120b:free",
            "name": "GPT-OSS 120B",
            "provider": "OpenRouter", "size": "120B",
            "size_category": "large", "context": "131k"
        },
        "qwen3-coder": {
            "id": "qwen/qwen3-coder:free",
            "name": "Qwen3 Coder 480B",
            "provider": "OpenRouter", "size": "480B",
            "size_category": "large", "context": "262k"
        },
        "qwen3-next-80b": {
            "id": "qwen/qwen3-next-80b-a3b-instruct:free",
            "name": "Qwen3 Next 80B",
            "provider": "OpenRouter", "size": "80B",
            "size_category": "large", "context": "262k"
        },
        "minimax-m2.5": {
            "id": "minimax/minimax-m2.5:free",
            "name": "MiniMax M2.5",
            "provider": "OpenRouter", "size": "N/A",
            "size_category": "large", "context": "197k"
        },
        # ── Medium ─────────────────────────────────────────────────────────
        "gpt-oss-20b": {
            "id": "openai/gpt-oss-20b:free",
            "name": "GPT-OSS 20B",
            "provider": "OpenRouter", "size": "20B",
            "size_category": "medium", "context": "131k"
        },
        "mistral-small-3.1": {
            "id": "mistralai/mistral-small-3.1-24b-instruct:free",
            "name": "Mistral Small 3.1 24B",
            "provider": "OpenRouter", "size": "24B",
            "size_category": "medium", "context": "128k"
        },
        "trinity-mini": {
            "id": "arcee-ai/trinity-mini:free",
            "name": "Trinity Mini 26B",
            "provider": "OpenRouter", "size": "26B",
            "size_category": "medium", "context": "131k"
        },
        "nemotron-nano-30b": {
            "id": "nvidia/nemotron-3-nano-30b-a3b:free",
            "name": "Nemotron 3 Nano 30B",
            "provider": "OpenRouter", "size": "30B",
            "size_category": "medium", "context": "256k"
        },
        "glm-4.5-air": {
            "id": "z-ai/glm-4.5-air:free",
            "name": "GLM 4.5 Air",
            "provider": "OpenRouter", "size": "N/A",
            "size_category": "medium", "context": "131k"
        },
        # ── Small ──────────────────────────────────────────────────────────
        "nemotron-nano-9b": {
            "id": "nvidia/nemotron-nano-9b-v2:free",
            "name": "Nemotron Nano 9B",
            "provider": "OpenRouter", "size": "9B",
            "size_category": "small", "context": "128k"
        },
        "llama-3.2-3b": {
            "id": "meta-llama/llama-3.2-3b-instruct:free",
            "name": "Llama 3.2 3B",
            "provider": "OpenRouter", "size": "3B",
            "size_category": "small", "context": "131k"
        },
    },
}

TESTS = {
    "speed": {
        "simple": "Write a haiku about artificial intelligence.",
        "medium": "Explain quantum computing in simple terms (200 words).",
        "long":   "Write a detailed tutorial on Python decorators with examples (300 words).",
    },
    "code": {
        "prime": {
            "prompt": "Write a Python function called is_prime(n) that returns True if n is prime, False otherwise. Return ONLY the function, no explanation.",
            "fn": "is_prime",
            "test_input": [2, 3, 4, 17, 100],
            "expected":   [True, True, False, True, False]
        },
        "fibonacci": {
            "prompt": "Write a Python function called fibonacci(n) that returns the nth Fibonacci number (0-indexed, so fibonacci(0)=0, fibonacci(1)=1, fibonacci(7)=13). Return ONLY the function, no explanation.",
            "fn": "fibonacci",
            "test_input": [0, 1, 7, 10],
            "expected":   [0, 1, 13, 55]
        },
        "palindrome": {
            "prompt": "Write a Python function called is_palindrome(s) that returns True if string s is a palindrome (ignore case and spaces). Return ONLY the function, no explanation.",
            "fn": "is_palindrome",
            "test_input": ["racecar", "hello", "A man a plan a canal Panama", "world"],
            "expected":   [True, False, True, False]
        }
    },
    "reasoning": {
        "syllogism": {
            "prompt": "If all bloops are razzies and all razzies are lazzies, are all bloops definitely lazzies? Answer with just Yes or No.",
            "answer": "yes"
        },
        "speed_math": {
            "prompt": "A train travels 120 km in 2 hours. Another train travels 180 km in 3 hours. Which is faster? Answer with: First, Second, or Same.",
            "answer": "same"
        },
        "river_crossing": {
            "prompt": "A farmer has a fox, a chicken, and a bag of grain. He needs to cross a river with a boat that can only carry him and one item. The fox eats the chicken if left alone, and the chicken eats the grain. What does he take first? Answer with one word: Fox, Chicken, or Grain.",
            "answer": "chicken"
        },
        "coin_flip": {
            "prompt": "I flip a fair coin 3 times and get heads each time. What is the probability of getting heads on the 4th flip? Answer with a fraction like 1/2.",
            "answer": "1/2"
        },
        "counting": {
            "prompt": "How many letters are in the word MISSISSIPPI? Answer with just the number.",
            "answer": "11"
        }
    },
    "instruction": {
        "json": {
            "prompt": 'Return a JSON object with exactly these keys: "name", "age", "city". Use any values you like. Return ONLY valid JSON, nothing else.',
            "check": "json_keys",
            "required_keys": ["name", "age", "city"]
        },
        "list": {
            "prompt": "List exactly 5 programming languages, one per line, numbered 1-5. No extra text.",
            "check": "numbered_list",
            "count": 5
        },
        "word_count": {
            "prompt": "Write a description of Paris in exactly 3 sentences. No more, no less.",
            "check": "sentence_count",
            "count": 3
        }
    },
    "translation": {
        "en_ru": {
            "prompt": "Translate to Russian: 'Artificial intelligence is changing the world.' Return only the translation.",
            "check": "cyrillic"
        },
        "ru_en": {
            "prompt": "Translate to English: 'Машинное обучение помогает решать сложные задачи.' Return only the translation.",
            "check": "latin"
        },
        "en_es": {
            "prompt": "Translate to Spanish: 'The future belongs to those who believe in the beauty of their dreams.' Return only the translation.",
            "check": "spanish_words",
            "keywords": ["el", "la", "los", "las", "que", "de", "su", "sus", "futuro", "sueños", "pertenece", "creen", "belleza"]
        }
    }
}

RATE_LIMITS = {
    "groq": 30,
    "openrouter": 8
}
