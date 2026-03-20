# ⚡ ModelArena

**Daily automated benchmarks of free AI models — speed and quality ranked separately.**

Live site: [your-username.github.io/ModelArena](https://your-username.github.io/ModelArena)

---

## What is this?

ModelArena runs a benchmark suite every day via GitHub Actions and publishes results to a static website. It tests models across **speed**, **code quality**, **reasoning accuracy**, and **translation** — then ranks them in two separate leaderboards so a 70B model isn't unfairly competing with an 8B on a single score.

All models tested are **100% free** — no billing required on any provider.

---

## How it works

```
GitHub Actions (daily 03:00 UTC)
        │
        ├── benchmark.py  ──►  Groq API          (5 models)
        │                 ──►  OpenRouter :free   (8 models)
        │                 ──►  Google AI Studio   (2 models)
        │
        ├── news_parser.py  ──►  scrapes AI news feeds
        │
        └── git commit  ──►  docs/data/results/  ──►  GitHub Pages
```

Each model receives **12 prompts** across 4 test categories:

| Category | Tests | How scored |
|---|---|---|
| ⚡ Speed | 3 prompts (short → long) | tokens/second, measured live |
| 💻 Code | 3 Python tasks (easy → hard) | heuristic: function, logic, comments |
| 🧠 Reasoning | 3 logic/math/puzzle questions | answer matched against known correct answers |
| 🌍 Translation | 3 language pairs (EN↔RU, EN→ES) | script detection + keyword matching |

**Quality score** = Code×40% + Reasoning×40% + Translation×20%  
**Speed score** = normalised to 100 (fastest model in the run = 100)

Speed and quality are **never mixed** into one number. A small fast model and a large smart model can both win — in their own category.

Models are also grouped by size tier (**small ≤10B / medium 10–50B / large 50B+**) so comparisons within a tier are always available.

---

## Providers & models

| Provider | Free tier | Models tested |
|---|---|---|
| [Groq](https://console.groq.com) | ✅ No card required | Llama 3.1 8B, Llama 3.3 70B, Llama 4 Scout, Qwen 3 32B, GPT-OSS 120B |
| [Google AI Studio](https://aistudio.google.com) | ✅ No card required | Gemini 2.0 Flash, Gemini 2.0 Flash Lite |
| [OpenRouter](https://openrouter.ai) | ✅ `:free` models only | Step 3.5 Flash, Nemotron 3 Super, Llama 3.3 70B, GPT-OSS 120B/20B, Mistral Small 3.1, MiniMax M2.5, Qwen 3 4B |

---

## Setup

### 1. Fork this repo

### 2. Enable GitHub Pages
Settings → Pages → Source: `Deploy from branch` → Branch: `main` → Folder: `/docs`

### 3. Add API keys to Secrets
Settings → Secrets and variables → Actions:

| Secret | Where to get it |
|---|---|
| `GROQ_API_KEY` | [console.groq.com/keys](https://console.groq.com/keys) |
| `GOOGLE_API_KEY` | [aistudio.google.com](https://aistudio.google.com) → Get API key |
| `OPENROUTER_API_KEY` | [openrouter.ai/keys](https://openrouter.ai/keys) |

Google and OpenRouter are optional — the benchmark runs fine with just Groq.

### 4. Trigger the first run
Actions → Daily AI Benchmark → Run workflow

---

## Project structure

```
ModelArena/
├── src/
│   ├── benchmark.py      # main benchmark runner
│   ├── config.py         # models + test prompts
│   └── news_parser.py    # AI news scraper
├── docs/                 # GitHub Pages site
│   ├── index.html        # leaderboards (quality + speed tabs)
│   ├── search.html       # filter/search models
│   ├── trends.html       # historical charts
│   ├── news.html         # AI news feed
│   ├── about.html        # this project explained
│   ├── app.js            # shared JS utilities
│   └── style.css         # dark/light theme
└── .github/workflows/
    └── benchmark.yml     # daily cron + manual trigger
```

---

## Adding models

Edit `src/config.py`. For OpenRouter, only use models with the `:free` suffix — otherwise they'll fail with 402 if your balance is zero.

```python
"my-model": {
    "id": "provider/model-name:free",  # OpenRouter ID
    "name": "Display Name",
    "provider": "OpenRouter",
    "size": "7B",
    "context": "128k"
}
```

---

## License

MIT
