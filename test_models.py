import os
import requests
import json
import time
from groq import Groq
from dotenv import load_dotenv

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
or_key   = os.getenv("OPENROUTER_API_KEY")

print("=" * 60)
print("  HEALTHHALLU — ALL MODELS TEST")
print("=" * 60)

# ─────────────────────────────────────
# ALL CONFIRMED WORKING MODELS
# ─────────────────────────────────────
GROQ_MODELS = [
    ("LLaMA 3.3 70B",     "llama-3.3-70b-versatile"),
    ("LLaMA 3.1 8B",      "llama-3.1-8b-instant"),
    ("LLaMA 4 Scout 17B", "meta-llama/llama-4-scout-17b-16e-instruct"),
    ("Qwen3 32B",         "qwen/qwen3-32b"),
    ("OpenAI OSS 20B",    "openai/gpt-oss-20b"),
]

OPENROUTER_MODELS = [
    ("NVIDIA Nemotron 120B", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("OpenAI OSS 120B",      "openai/gpt-oss-120b:free"),
    ("Gemma 4 31B",          "google/gemma-4-31b-it:free"),
    ("MiniMax M2.5",         "minimax/minimax-m2.5:free"),
    ("Baidu CoBuddy",        "baidu/cobuddy:free"),
    ("LiquidAI Instruct",    "liquid/lfm-2.5-1.2b-instruct:free"),
    ("OpenAI OSS 20B OR",    "openai/gpt-oss-20b:free"),
    ("Owl Alpha",            "openrouter/owl-alpha"),
    ("Free Router",          "openrouter/free"),
]

working_models = []
failed_models  = []

# ─────────────────────────────────────
# TEST GROQ MODELS
# ─────────────────────────────────────
print(f"\n📡 Testing Groq Models ({len(GROQ_MODELS)} models)...")
print("-" * 60)

client = Groq(api_key=groq_key)

for name, model_id in GROQ_MODELS:
    try:
        r = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user",
                        "content": "Say hi in one word"}],
            max_tokens=15
        )
        reply = r.choices[0].message.content
        reply = reply.strip()[:30] if reply else "Empty"
        print(f"  ✅ {name}: {reply}")
        working_models.append({
            "name": name,
            "model_id": model_id,
            "provider": "groq"
        })
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:60]}")
        failed_models.append(name)
    time.sleep(1)

# ─────────────────────────────────────
# TEST OPENROUTER MODELS
# ─────────────────────────────────────
print(f"\n📡 Testing OpenRouter Models ({len(OPENROUTER_MODELS)} models)...")
print("-" * 60)

for name, model_id in OPENROUTER_MODELS:
    try:
        r = requests.post(
            "https://openrouter.ai/api/v1/chat/completions",
            headers={
                "Authorization": f"Bearer {or_key}",
                "Content-Type": "application/json",
                "HTTP-Referer": "https://healthhallu.project",
                "X-Title": "HealthHallu"
            },
            json={
                "model": model_id,
                "messages": [{"role": "user",
                               "content": "Say hi in one word"}],
                "max_tokens": 15
            },
            timeout=25
        )
        result = r.json()
        if "choices" in result:
            content = result["choices"][0]["message"].get("content")
            if content:
                reply = content.strip()[:30]
                print(f"  ✅ {name}: {reply}")
                working_models.append({
                    "name": name,
                    "model_id": model_id,
                    "provider": "openrouter"
                })
            else:
                print(f"  ⚠️  {name}: Empty response — skipping")
                failed_models.append(name)
        else:
            err = result.get("error", {}).get("message", "unknown")[:50]
            print(f"  ❌ {name}: {err}")
            failed_models.append(name)
    except Exception as e:
        print(f"  ❌ {name}: {str(e)[:60]}")
        failed_models.append(name)
    time.sleep(2)

# ─────────────────────────────────────
# SAVE ALL WORKING MODELS
# ─────────────────────────────────────
config = {
    "total_models": len(working_models),
    "groq_models": [
        m for m in working_models
        if m["provider"] == "groq"
    ],
    "openrouter_models": [
        m for m in working_models
        if m["provider"] == "openrouter"
    ]
}

with open("working_models.json", "w") as f:
    json.dump(config, f, indent=2)

# ─────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────
print("\n" + "=" * 60)
print("  FINAL SUMMARY")
print("=" * 60)
print(f"  ✅ Working models : {len(working_models)}")
print(f"  ❌ Failed models  : {len(failed_models)}")
print(f"  💰 Total cost     : Rs. 0")
print()
print("  ALL WORKING MODELS:")
print("-" * 60)
for i, m in enumerate(working_models, 1):
    print(f"  {i:02d}. {m['name']:<25} via {m['provider']}")
print()
if failed_models:
    print("  SKIPPED MODELS:")
    for m in failed_models:
        print(f"       ✗ {m}")
print()
print("  ✅ Saved to working_models.json")
print("  🚀 Phase 2 — Data Collection starting next!")
print("=" * 60)