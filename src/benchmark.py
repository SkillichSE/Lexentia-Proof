"""
AI Model Benchmarking Script
Runs tests on all configured models and saves results
"""

import os
import json
import time
from datetime import datetime
from pathlib import Path
import requests
from config import MODELS, TESTS, EVALUATION

# API endpoints
GROQ_API = "https://api.groq.com/openai/v1/chat/completions"
GOOGLE_API = "https://generativelanguage.googleapis.com/v1beta/models"

class ModelBenchmark:
    def __init__(self):
        self.groq_key = os.getenv("GROQ_API_KEY")
        self.google_key = os.getenv("GOOGLE_API_KEY")
        self.results = []
        
    def test_groq_model(self, model_id, prompt):
        """Test a Groq model"""
        headers = {
            "Authorization": f"Bearer {self.groq_key}",
            "Content-Type": "application/json"
        }
        
        data = {
            "model": model_id,
            "messages": [{"role": "user", "content": prompt}],
            "temperature": 0.7,
            "max_tokens": 500
        }
        
        start = time.time()
        try:
            response = requests.post(GROQ_API, headers=headers, json=data, timeout=30)
            end = time.time()
            
            if response.status_code == 200:
                result = response.json()
                content = result["choices"][0]["message"]["content"]
                usage = result.get("usage", {})
                
                return {
                    "success": True,
                    "content": content,
                    "total_time": end - start,
                    "tokens": usage.get("total_tokens", 0),
                    "tokens_per_sec": usage.get("total_tokens", 0) / (end - start) if (end - start) > 0 else 0
                }
            else:
                return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def test_google_model(self, model_id, prompt):
        """Test a Google Gemini model"""
        url = f"{GOOGLE_API}/{model_id}:generateContent?key={self.google_key}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }],
            "generationConfig": {
                "temperature": 0.7,
                "maxOutputTokens": 500
            }
        }
        
        start = time.time()
        try:
            response = requests.post(url, json=data, timeout=30)
            end = time.time()
            
            if response.status_code == 200:
                result = response.json()
                content = result["candidates"][0]["content"]["parts"][0]["text"]
                usage = result.get("usageMetadata", {})
                
                return {
                    "success": True,
                    "content": content,
                    "total_time": end - start,
                    "tokens": usage.get("totalTokenCount", 0),
                    "tokens_per_sec": usage.get("totalTokenCount", 0) / (end - start) if (end - start) > 0 else 0
                }
            else:
                return {"success": False, "error": f"Status {response.status_code}"}
        except Exception as e:
            return {"success": False, "error": str(e)}
    
    def evaluate_code(self, code):
        """Simple code evaluation"""
        score = 0
        
        # Check for valid Python syntax (basic check)
        if "def " in code and ":" in code:
            score += 40
        
        # Check for comments
        if "#" in code or '"""' in code:
            score += 30
        
        # Check for return statement
        if "return" in code:
            score += 30
        
        return min(score, 100)
    
    def run_benchmark(self):
        """Run full benchmark suite"""
        print("🚀 Starting AI Model Benchmark...")
        print(f"📅 Date: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        
        for provider, models in MODELS.items():
            for model_key, model_info in models.items():
                print(f"\n🤖 Testing {model_info['name']}...")
                
                model_results = {
                    "model_id": model_key,
                    "model_name": model_info["name"],
                    "provider": model_info["provider"],
                    "size": model_info["size"],
                    "timestamp": datetime.now().isoformat(),
                    "tests": {}
                }
                
                # Speed tests
                print("  ⚡ Speed tests...")
                speed_results = []
                for test_name, prompt in TESTS["speed"].items():
                    if provider == "groq":
                        result = self.test_groq_model(model_info["id"], prompt)
                    elif provider == "google":
                        result = self.test_google_model(model_info["id"], prompt)
                    
                    if result["success"]:
                        speed_results.append({
                            "test": test_name,
                            "time": result["total_time"],
                            "tokens_per_sec": result["tokens_per_sec"]
                        })
                    else:
                        print(f"    ⚠️  Speed test '{test_name}' failed: {result.get('error', 'Unknown')}")
                    
                    time.sleep(2)  # Rate limiting - 2 seconds between requests
                
                avg_speed = sum(r["tokens_per_sec"] for r in speed_results) / len(speed_results) if speed_results else 0
                model_results["tests"]["speed"] = {
                    "avg_tokens_per_sec": round(avg_speed, 2),
                    "details": speed_results
                }
                
                # Code tests
                print("  💻 Code tests...")
                code_results = []
                for test_name, prompt in TESTS["code"].items():
                    if provider == "groq":
                        result = self.test_groq_model(model_info["id"], prompt)
                    elif provider == "google":
                        result = self.test_google_model(model_info["id"], prompt)
                    
                    if result["success"]:
                        score = self.evaluate_code(result["content"])
                        code_results.append({
                            "test": test_name,
                            "score": score,
                            "code": result["content"][:200]  # First 200 chars
                        })
                    else:
                        print(f"    ⚠️  Code test '{test_name}' failed: {result.get('error', 'Unknown')}")
                    
                    time.sleep(2)
                
                avg_code = sum(r["score"] for r in code_results) / len(code_results) if code_results else 0
                model_results["tests"]["code"] = {
                    "avg_score": round(avg_code, 2),
                    "details": code_results
                }
                
                # Overall score
                overall = (avg_speed / 10) * 0.5 + avg_code * 0.5  # Normalized
                model_results["overall_score"] = round(overall, 2)
                
                self.results.append(model_results)
                print(f"  ✅ Overall score: {overall:.2f}")
        
        self.save_results()
    
    def save_results(self):
        """Save results to JSON files"""
        date_str = datetime.now().strftime("%Y-%m-%d")
        
        # Create data directory inside docs/ for GitHub Pages
        Path("../docs/data/results").mkdir(parents=True, exist_ok=True)
        
        # Save daily results
        daily_file = f"../docs/data/results/{date_str}.json"
        with open(daily_file, "w") as f:
            json.dump(self.results, f, indent=2)
        
        # Update latest.json
        latest_file = "../docs/data/results/latest.json"
        with open(latest_file, "w") as f:
            json.dump({
                "date": date_str,
                "timestamp": datetime.now().isoformat(),
                "results": self.results
            }, f, indent=2)
        
        # Update leaderboard
        leaderboard = sorted(self.results, key=lambda x: x["overall_score"], reverse=True)
        leaderboard_file = "../docs/data/results/leaderboard.json"
        with open(leaderboard_file, "w") as f:
            json.dump(leaderboard, f, indent=2)
        
        print(f"\n💾 Results saved to {daily_file}")
        print(f"🏆 Leaderboard updated")

if __name__ == "__main__":
    benchmark = ModelBenchmark()
    benchmark.run_benchmark()
    print("\n✨ Benchmark complete!")
