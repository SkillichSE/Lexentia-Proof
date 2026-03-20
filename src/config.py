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
        "qwen2.5-72b": {
            "id": "qwen/qwen2.5-72b",
            "name": "Qwen 2.5 72B",
            "provider": "Groq",
            "size": "72B",
            "context": "128k"
        },
        "qwen3-32b": {
            "id": "qwen/qwen3-32b",
            "name": "Qwen 3 32B",
            "provider": "Groq",
            "size": "32B",
            "context": "32k"
        },
        "mistral-large-2": {
            "id": "mistral-large-latest",
            "name": "Mistral Large 2",
            "provider": "Groq",
            "size": "123B",
            "context": "128k"
        },
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
    "openrouter": {
        "llama-3.1-405b": {
            "id": "meta-llama/llama-3.1-405b-instruct:free",
            "name": "Llama 3.1 405B",
            "provider": "OpenRouter",
            "size": "405B",
            "context": "128k"
        },
        "llama-3.1-70b-or": {
            "id": "meta-llama/llama-3.1-70b-instruct:free",
            "name": "Llama 3.1 70B",
            "provider": "OpenRouter",
            "size": "70B",
            "context": "128k"
        },
        "llama-3.2-3b": {
            "id": "meta-llama/llama-3.2-3b-instruct:free",
            "name": "Llama 3.2 3B",
            "provider": "OpenRouter",
            "size": "3B",
            "context": "131k"
        },
        "qwen2.5-7b": {
            "id": "qwen/qwen-2.5-7b-instruct:free",
            "name": "Qwen 2.5 7B",
            "provider": "OpenRouter",
            "size": "7B",
            "context": "128k"
        },
        "mistral-7b": {
            "id": "mistralai/mistral-7b-instruct:free",
            "name": "Mistral 7B",
            "provider": "OpenRouter",
            "size": "7B",
            "context": "32k"
        },
        "mistral-small-3.1": {
            "id": "mistralai/mistral-small-3.1-24b-instruct:free",
            "name": "Mistral Small 3.1 24B",
            "provider": "OpenRouter",
            "size": "24B",
            "context": "128k"
        },
        "nemotron-super-49b": {
            "id": "nvidia/llama-3.1-nemotron-70b-instruct:free",
            "name": "Nemotron 70B",
            "provider": "OpenRouter",
            "size": "70B",
            "context": "131k"
        },
        "deepseek-r1": {
            "id": "deepseek/deepseek-r1:free",
            "name": "DeepSeek R1",
            "provider": "OpenRouter",
            "size": "671B",
            "context": "164k"
        },
        "deepseek-v3": {
            "id": "deepseek/deepseek-chat-v3-0324:free",
            "name": "DeepSeek V3",
            "provider": "OpenRouter",
            "size": "671B",
            "context": "131k"
        },
    }
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
    "google": 15,
    "openrouter": 20
}
