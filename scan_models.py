import requests
import os
import time
from dotenv import load_dotenv

load_dotenv()
key = os.getenv("OPENROUTER_API_KEY")

print("🔍 Scanning ALL free OpenRouter models...")
print("=" * 60)

# Get full list of free models
r = requests.get(
    "https://openrouter.ai/api/v1/models",
    headers={"Authorization": f"Bearer {key}"},
    timeout=15
)
all_models = r.json()

# Filter only free ones
free_models = []
for m in all_models["data"]:
    pricing = m.get("pricing", {})
    prompt_cost = float(pricing.get("prompt", 1))
    if prompt_cost == 0:
        free_models.append({
            "id":   m["id"],
            "name": m["name"]
        })

print(f"Found {len(free_models)} free models")
print(f"Testing each one...\n")

# Skip models already working
already_working = [
    "nvidia/nemotron-3-super-120b-a12b:free",
    "openai/gpt-oss-120b:free",
    "google/gemma-4-31b-it:free",
    "minimax/minimax-m2.5:free",
    "baidu/cobuddy:free",
    "liquid/lfm-2.5-1.2b-instruct:free",
    "openai/gpt-oss-20b:free",
    "openrouter/owl-alpha",
    "openrouter/free",
]

working = []
failed  = []

for m in free_models:
    if m["id"] in already_working:
        continue

    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization":  f"Bearer {key}",
                "Content-Type":   "application/json",
                "HTTP-Referer":   "https://healthhallu.project",
                "X-Title":        "HealthHallu"
            },
            json={
                "model": m["id"],
                "messages": [{
                    "role":    "user",
                    "content": "Reply with one word: Hello"
                }],
                "max_tokens": 15
            },
            timeout=20
        )
        result = r.json()

        if "choices" in result:
            content = result["choices"][0][
                "message"].get("content", "")
            if content and len(content.strip()) > 0:
                print(f"✅ {m['name'][:40]}")
                print(f"   ID: {m['id']}")
                print(f"   Reply: {content.strip()[:30]}")
                print()
                working.append(m)
            else:
                print(f"⚠️  {m['name'][:40]} — empty")
                failed.append(m)
        else:
            err = result.get("error", {}).get(
                "message", "unknown")[:40]
            print(f"❌ {m['name'][:40]} — {err}")
            failed.append(m)

    except Exception as e:
        print(f"❌ {m['name'][:40]} — {str(e)[:40]}")
        failed.append(m)

    time.sleep(2)

print("\n" + "=" * 60)
print(f"✅ WORKING MODELS FOUND: {len(working)}")
print("=" * 60)
for w in working:
    print(f"  Name: {w['name']}")
    print(f"  ID:   {w['id']}")
    print()