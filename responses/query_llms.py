import os
import json
import time
import requests
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()

groq_key = os.getenv("GROQ_API_KEY")
or_key   = os.getenv("OPENROUTER_API_KEY")

print("🤖 HealthHallu — LLM Query Pipeline")
print("=" * 60)
print(f"Started at: {datetime.now().strftime('%H:%M:%S')}")

# ─────────────────────────────────────
# LOAD QUESTIONS
# ─────────────────────────────────────
qdf = pd.read_csv("questions/questions_bank.csv")
print(f"📋 Loaded {len(qdf)} questions")

# ─────────────────────────────────────
# ALL 14 MODELS
# ─────────────────────────────────────
GROQ_MODELS = [
    ("LLaMA_3_3_70B",     "llama-3.3-70b-versatile"),
    ("LLaMA_3_1_8B",      "llama-3.1-8b-instant"),
    ("LLaMA_4_Scout_17B", "meta-llama/llama-4-scout-17b-16e-instruct"),
    ("Qwen3_32B",         "qwen/qwen3-32b"),
    ("OpenAI_OSS_20B",    "openai/gpt-oss-20b"),
]

OPENROUTER_MODELS = [
    ("NVIDIA_Nemotron_120B", "nvidia/nemotron-3-super-120b-a12b:free"),
    ("OpenAI_OSS_120B",      "openai/gpt-oss-120b:free"),
    ("Gemma_4_31B",          "google/gemma-4-31b-it:free"),
    ("MiniMax_M2_5",         "minimax/minimax-m2.5:free"),
    ("Baidu_CoBuddy",        "baidu/cobuddy:free"),
    ("LiquidAI_Instruct",    "liquid/lfm-2.5-1.2b-instruct:free"),
    ("OpenAI_OSS_20B_OR",    "openai/gpt-oss-20b:free"),
    ("Owl_Alpha",            "openrouter/owl-alpha"),
    ("Free_Router",          "openrouter/free"),
]

ALL_MODELS = (
    [(n, m, "groq")       for n, m in GROQ_MODELS] +
    [(n, m, "openrouter") for n, m in OPENROUTER_MODELS]
)

print(f"🤖 Total models: {len(ALL_MODELS)}")
print(f"📊 Total API calls: {len(qdf) * len(ALL_MODELS)}")
print("=" * 60)

# ─────────────────────────────────────
# SYSTEM PROMPT
# ─────────────────────────────────────
SYSTEM_PROMPT = """You are a factual health data assistant.
Answer the question with ONLY a specific number, percentage, 
or country name. Do NOT add explanations or extra text.
Be as precise as possible with numerical values."""

# ─────────────────────────────────────
# QUERY FUNCTIONS
# ─────────────────────────────────────
groq_client = Groq(api_key=groq_key)

def query_groq(model_id, question):
    try:
        r = groq_client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user",   "content": question}
            ],
            max_tokens=50,
            temperature=0
        )
        return r.choices[0].message.content.strip()
    except Exception as e:
        return f"ERROR: {str(e)[:80]}"

def query_openrouter(model_id, question):
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
                "messages": [
                    {"role": "system", "content": SYSTEM_PROMPT},
                    {"role": "user",   "content": question}
                ],
                "max_tokens": 50,
                "temperature": 0
            },
            timeout=30
        )
        result = r.json()
        if "choices" in result:
            content = result["choices"][0]["message"].get("content","")
            return content.strip() if content else "EMPTY_RESPONSE"
        else:
            err = result.get("error",{}).get("message","Unknown error")
            return f"ERROR: {err[:80]}"
    except Exception as e:
        return f"ERROR: {str(e)[:80]}"

# ─────────────────────────────────────
# MAIN QUERY LOOP
# ─────────────────────────────────────
results = []
total_calls = len(qdf) * len(ALL_MODELS)
call_count  = 0
start_time  = time.time()

print("\n🚀 Starting queries...")
print("(This will take some time — be patient!)\n")

for idx, row in qdf.iterrows():
    result_row = {
        "id":             row["id"],
        "category":       row["category"],
        "subcategory":    row["subcategory"],
        "question":       row["question"],
        "correct_answer": row["correct_answer"],
        "answer_display": row["answer_display"],
        "unit":           row["unit"],
        "source":         row["source"],
        "difficulty":     row["difficulty"],
    }

    question = row["question"]

    for model_name, model_id, provider in ALL_MODELS:
        call_count += 1
        pct = (call_count / total_calls) * 100

        # Query the model
        if provider == "groq":
            answer = query_groq(model_id, question)
            time.sleep(0.5)
        else:
            answer = query_openrouter(model_id, question)
            time.sleep(1.5)

        result_row[model_name] = answer

        # Progress update every 14 calls (one full question done)
        if call_count % len(ALL_MODELS) == 0:
            elapsed = time.time() - start_time
            remaining = (elapsed / call_count) * (total_calls - call_count)
            print(f"  ✅ {row['id']} done | "
                  f"{pct:.1f}% complete | "
                  f"~{int(remaining//60)}m {int(remaining%60)}s remaining")

    results.append(result_row)

    # Save progress every 20 questions
    if (idx + 1) % 20 == 0:
        temp_df = pd.DataFrame(results)
        temp_df.to_csv("responses/responses_progress.csv",
                       index=False)
        print(f"  💾 Progress saved at question {idx+1}")

# ─────────────────────────────────────
# SAVE FINAL RESULTS
# ─────────────────────────────────────
print("\n💾 Saving final results...")
rdf = pd.DataFrame(results)

today = datetime.today().strftime("%Y-%m-%d")
final_path    = f"responses/llm_responses_{today}.csv"
latest_path   = "responses/llm_responses_latest.csv"

rdf.to_csv(final_path,  index=False)
rdf.to_csv(latest_path, index=False)

# ─────────────────────────────────────
# SUMMARY
# ─────────────────────────────────────
model_names = [n for n, m, p in ALL_MODELS]
error_counts = {}
empty_counts = {}

for mn in model_names:
    if mn in rdf.columns:
        errors = rdf[mn].astype(str).str.startswith("ERROR").sum()
        empty  = (rdf[mn].astype(str) == "EMPTY_RESPONSE").sum()
        error_counts[mn] = errors
        empty_counts[mn] = empty

total_time = time.time() - start_time

print(f"\n{'=' * 60}")
print("  ✅ LLM QUERYING COMPLETE")
print(f"{'=' * 60}")
print(f"  Questions answered : {len(rdf)}")
print(f"  Models queried     : {len(ALL_MODELS)}")
print(f"  Total API calls    : {total_calls}")
print(f"  Time taken         : {int(total_time//60)}m {int(total_time%60)}s")
print(f"  Saved to           : {latest_path}")
print(f"\n  MODEL ERROR SUMMARY:")
print(f"  {'Model':<25} {'Errors':>8} {'Empty':>8}")
print(f"  {'-'*41}")
for mn in model_names:
    print(f"  {mn:<25} {error_counts.get(mn,0):>8} "
          f"{empty_counts.get(mn,0):>8}")
print(f"{'=' * 60}")
print(f"\n🎯 Next step: Run scoring pipeline!")