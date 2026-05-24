import os
import time
import pandas as pd
from groq import Groq
from dotenv import load_dotenv
from datetime import datetime

load_dotenv()
groq_key = os.getenv("GROQ_API_KEY")
client   = Groq(api_key=groq_key)

print("🤖 Querying 4 NEW Groq Models")
print("=" * 60)
print(f"Started: {datetime.now().strftime('%H:%M:%S')}")

# ── Load questions ──
qdf = pd.read_csv("questions/questions_bank.csv")
print(f"📋 Questions: {len(qdf)}")

# ── Load existing responses ──
existing = pd.read_csv(
    "responses/llm_responses_latest.csv")
print(f"✅ Existing responses loaded: "
      f"{len(existing)} rows")

# ── 4 New Models ──
NEW_MODELS = [
    ("Groq_Compound",      "groq/compound"),
    ("Groq_Compound_Mini", "groq/compound-mini"),
    ("Allam_2_7B",         "allam-2-7b"),
    ("OSS_Safeguard_20B",  "openai/gpt-oss-safeguard-20b"),
]

print(f"🆕 New models to query: {len(NEW_MODELS)}")
print(f"📊 Total API calls: "
      f"{len(qdf) * len(NEW_MODELS)}")
print("=" * 60)

SYSTEM_PROMPT = """You are a factual health data assistant.
Answer with ONLY a specific number, percentage, or country name.
Do NOT add explanations. Be as precise as possible."""

def query_groq(model_id, question):
    try:
        r = client.chat.completions.create(
            model=model_id,
            messages=[
                {"role": "system",
                 "content": SYSTEM_PROMPT},
                {"role": "user",
                 "content": question}
            ],
            max_tokens=50,
            temperature=0
        )
        content = r.choices[0].message.content
        return content.strip() if content else "EMPTY"
    except Exception as e:
        return f"ERROR: {str(e)[:80]}"

# ── Query all questions for each new model ──
results = {row["id"]: {} for _, row in qdf.iterrows()}

total  = len(qdf) * len(NEW_MODELS)
done   = 0
start  = time.time()

for model_name, model_id in NEW_MODELS:
    print(f"\n🔄 Querying {model_name}...")
    print("-" * 40)

    for idx, row in qdf.iterrows():
        answer = query_groq(model_id, row["question"])
        results[row["id"]][model_name] = answer
        done += 1

        if done % len(NEW_MODELS) == 0:
            elapsed   = time.time() - start
            remaining = (elapsed/done) * (total-done)
            pct = (done/total)*100
            print(f"  ✅ {row['id']} | "
                  f"{pct:.1f}% | "
                  f"~{int(remaining//60)}m "
                  f"{int(remaining%60)}s left")

        time.sleep(0.5)

# ── Add new model columns to existing data ──
print("\n💾 Merging with existing responses...")

for model_name, _ in NEW_MODELS:
    existing[model_name] = existing["id"].map(
        lambda qid: results.get(
            qid, {}).get(model_name, "ERROR")
    )

# ── Save updated file ──
existing.to_csv(
    "responses/llm_responses_latest.csv",
    index=False)
existing.to_csv(
    f"responses/llm_responses_"
    f"{datetime.today().strftime('%Y-%m-%d')}.csv",
    index=False)

print(f"\n{'='*60}")
print("✅ DONE!")
print(f"{'='*60}")
print(f"  Questions:    {len(qdf)}")
print(f"  New models:   {len(NEW_MODELS)}")
print(f"  API calls:    {len(qdf)*len(NEW_MODELS)}")
print(f"  Time taken:   "
      f"{int((time.time()-start)//60)}m "
      f"{int((time.time()-start)%60)}s")
print(f"\n  New columns added:")
for mn, _ in NEW_MODELS:
    print(f"    + {mn}")
print(f"\n🎯 Next: python3 scores/score_responses.py")