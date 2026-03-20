"""
Configuration for AI model benchmarks.
All models are 100% free — no billing required on any provider.

Providers:
  - Groq:       free tier, no credit card needed
  - Google:     free tier via aistudio.google.com (get key there, not cloud console)
  - OpenRouter: only :free suffix models ($0/M tokens)
  - Cerebras:   free tier, extremely fast inference
  - Together:   free tier models
"""

MODELS = {
    "groq": {
        "llama-3.1-8b": {
            "id": "llama-3.1-8b-instant",
            "name": "Llama 3.1 8B",
            "provider": "Groq",
            "size": "8B",
            "context": "128k"
        },
        "llama-3.3-70b": {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama 3.3 70B",
            "provider": "Groq",
            "size": "70B",
            "context": "128k"
        },
        "llama-4-scout": {
            "id": "meta-llama/llama-4-scout-17b-16e-instruct",
            "name": "Llama 4 Scout 17B",
            "provider": "Groq",
            "size": "17Bx16E",
            "context": "131k"
        },
        "qwen3-32b": {
            "id": "qwen/qwen3-32b",
            "name": "Qwen 3 32B",
            "provider": "Groq",
            "size": "32B",
            "context": "32k"
        },
        "gpt-oss-120b": {
            "id": "openai/gpt-oss-120b",
            "name": "GPT-OSS 120B",
            "provider": "Groq",
            "size": "120B",
            "context": "128k"
        }
    },
    "google": {
        "gemini-2.0-flash": {
            "id": "gemini-2.0-flash",
            "name": "Gemini 2.0 Flash",
            "provider": "Google",
            "size": "N/A",
            "context": "1M"
        },
        "gemini-2.0-flash-lite": {
            "id": "gemini-2.0-flash-lite",
            "name": "Gemini 2.0 Flash Lite",
            "provider": "Google",
            "size": "N/A",
            "context": "1M"
        }
    },
    # All OpenRouter models MUST have :free suffix — verified $0/M tokens
    "openrouter": {
        "step-3.5-flash": {
            "id": "stepfun/step-3.5-flash:free",
            "name": "Step 3.5 Flash",
            "provider": "OpenRouter",
            "size": "196B",
            "context": "256k"
        },
        "nemotron-super-120b": {
            "id": "nvidia/nemotron-3-super-120b-a12b:free",
            "name": "Nemotron 3 Super 120B",
            "provider": "OpenRouter",
            "size": "120B",
            "context": "262k"
        },
        "gpt-oss-120b-or": {
            "id": "openai/gpt-oss-120b:free",
            "name": "GPT-OSS 120B",
            "provider": "OpenRouter",
            "size": "120B",
            "context": "131k"
        },
        "gpt-oss-20b": {
            "id": "openai/gpt-oss-20b:free",
            "name": "GPT-OSS 20B",
            "provider": "OpenRouter",
            "size": "20B",
            "context": "131k"
        },
        "mistral-small-3.1": {
            "id": "mistralai/mistral-small-3.1-24b-instruct:free",
            "name": "Mistral Small 3.1 24B",
            "provider": "OpenRouter",
            "size": "24B",
            "context": "128k"
        },
        "minimax-m2.5": {
            "id": "minimax/minimax-m2.5:free",
            "name": "MiniMax M2.5",
            "provider": "OpenRouter",
            "size": "N/A",
            "context": "197k"
        },
        "llama-3.3-70b-or": {
            "id": "meta-llama/llama-3.3-70b-instruct:free",
            "name": "Llama 3.3 70B",
            "provider": "OpenRouter",
            "size": "70B",
            "context": "66k"
        },
        "qwen3-4b": {
            "id": "qwen/qwen3-4b:free",
            "name": "Qwen 3 4B",
            "provider": "OpenRouter",
            "size": "4B",
            "context": "41k"
        }
    }
}

# ── Tests ──────────────────────────────────────────────────────────────────────
# Each test has a PROMPT and an EXPECTED answer for deterministic scoring.
# Speed tests are prompt-only (no grading needed, we measure tok/s).
TESTS = {
    "speed": {
        "simple": "Write a haiku about artificial intelligence.",
        "medium": "Explain quantum computing in simple terms (200 words).",
        "long":   "Write a detailed tutorial on Python decorators with examples (300 words)."
    },

    # Code: graded by actually running the code in a subprocess
    "code": {
        "prime": {
            "prompt": "Write a Python function called is_prime(n) that returns True if n is prime, False otherwise. Return ONLY the function, no explanation.",
            "test_input": [2, 3, 4, 17, 100],
            "expected":   [True, True, False, True, False]
        },
        "fibonacci": {
            "prompt": "Write a Python function called fibonacci(n) that returns the nth Fibonacci number (0-indexed, so fibonacci(0)=0, fibonacci(1)=1, fibonacci(7)=13). Return ONLY the function, no explanation.",
            "test_input": [0, 1, 7, 10],
            "expected":   [0, 1, 13, 55]
        },
        "palindrome": {
            "prompt": "Write a Python function called is_palindrome(s) that returns True if string s is a palindrome (ignore case and spaces). Return ONLY the function, no explanation.",
            "test_input": ["racecar", "hello", "A man a plan a canal Panama", "world"],
            "expected":   [True, False, True, False]
        }
    },

    # Reasoning: graded against known correct answers
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

    # Instruction following: graded by exact format checks
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

    # Translation: graded by script/keyword detection
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

EVALUATION = {
    "speed":       {"weight": 0.20},
    "code":        {"weight": 0.30},
    "reasoning":   {"weight": 0.25},
    "instruction": {"weight": 0.15},
    "translation": {"weight": 0.10}
}

NEWS_SOURCES = {
    "groq":        {"url": "https://groq.com/blog/", "selector": "article", "keywords": ["release", "launch", "update", "model"]},
    "google":      {"url": "https://ai.google.dev/gemini-api/docs/changelog", "selector": ".changelog-entry", "keywords": ["gemini", "release", "update"]},
    "huggingface": {"rss": "https://huggingface.co/blog/feed.xml", "keywords": ["release", "model", "launch"]},
    "together":    {"url": "https://www.together.ai/blog", "selector": "article", "keywords": ["release", "model", "update"]}
}

RATE_LIMITS = {
    "groq": 30,
    "google": 15,
    "openrouter": 20
}
