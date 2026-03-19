"""
Configuration for AI model benchmarks
"""

# Models to test (all free tier)
MODELS = {
    "groq": {
        "llama-3.1-8b": {
            "id": "llama-3.1-8b-instant",
            "name": "Llama 3.1 8B",
            "provider": "Groq",
            "size": "8B",
            "context": "128k"
        },
        "llama-3.1-70b": {
            "id": "llama-3.1-70b-versatile",
            "name": "Llama 3.1 70B",
            "provider": "Groq",
            "size": "70B",
            "context": "128k"
        },
        "llama-3.3-70b": {
            "id": "llama-3.3-70b-versatile",
            "name": "Llama 3.3 70B",
            "provider": "Groq",
            "size": "70B",
            "context": "128k"
        },
        "llama-guard-3-8b": {
            "id": "llama-guard-3-8b",
            "name": "Llama Guard 3 8B",
            "provider": "Groq",
            "size": "8B",
            "context": "8k"
        }
    },
    "google": {
        "gemini-flash": {
            "id": "gemini-1.5-flash",
            "name": "Gemini 1.5 Flash",
            "provider": "Google",
            "size": "N/A",
            "context": "1M"
        },
        "gemini-pro": {
            "id": "gemini-1.5-pro",
            "name": "Gemini 1.5 Pro",
            "provider": "Google",
            "size": "N/A",
            "context": "2M"
        }
    }
}

# Test prompts
TESTS = {
    "speed": {
        "simple": "Write a haiku about artificial intelligence.",
        "medium": "Explain quantum computing in simple terms (200 words).",
        "long": "Write a detailed tutorial on Python decorators with examples."
    },
    
    "code": {
        "easy": "Write a Python function to check if a number is prime.",
        "medium": "Create a binary search implementation in Python with comments.",
        "hard": "Implement a LRU cache in Python using OrderedDict."
    },
    
    "reasoning": {
        "logic": "If all bloops are razzies and all razzies are lazzies, are all bloops definitely lazzies?",
        "math": "A train travels 120 km in 2 hours. Another train travels 180 km in 3 hours. Which is faster?",
        "puzzle": "You have 12 balls, one is slightly heavier. Using a balance scale only 3 times, how do you find it?"
    },
    
    "translation": {
        "en_ru": "Translate to Russian: 'The quick brown fox jumps over the lazy dog.'",
        "ru_en": "Translate to English: 'Искусственный интеллект меняет мир.'",
        "complex": "Translate to Spanish: 'Machine learning models require substantial computational resources.'"
    }
}

# Evaluation criteria
EVALUATION = {
    "speed": {
        "weight": 0.3,
        "metrics": ["ttft", "tokens_per_sec", "total_time"]
    },
    "code": {
        "weight": 0.3,
        "metrics": ["syntax_valid", "runs_correctly", "has_comments"]
    },
    "reasoning": {
        "weight": 0.2,
        "metrics": ["correct_answer", "explanation_quality"]
    },
    "translation": {
        "weight": 0.2,
        "metrics": ["accuracy", "fluency"]
    }
}

# News sources to monitor
NEWS_SOURCES = {
    "groq": {
        "url": "https://groq.com/blog/",
        "selector": "article",
        "keywords": ["release", "launch", "update", "model"]
    },
    "google": {
        "url": "https://ai.google.dev/gemini-api/docs/changelog",
        "selector": ".changelog-entry",
        "keywords": ["gemini", "release", "update"]
    },
    "huggingface": {
        "rss": "https://huggingface.co/blog/feed.xml",
        "keywords": ["release", "model", "launch"]
    },
    "together": {
        "url": "https://www.together.ai/blog",
        "selector": "article",
        "keywords": ["release", "model", "update"]
    }
}

# Rate limits (requests per minute)
RATE_LIMITS = {
    "groq": 30,
    "google": 60,
    "together": 20,
    "huggingface": 10
}
