import pandas as pd
import numpy as np
import re
import os
from datetime import datetime

print("📊 HealthHallu — Scoring Pipeline v3")
print("=" * 60)

# ─────────────────────────────────────
# LOAD DATA
# ─────────────────────────────────────
rdf = pd.read_csv("responses/llm_responses_latest.csv")
print(f"✅ Loaded {len(rdf)} questions")
print(f"✅ Columns: {list(rdf.columns[:5])}...")

MODEL_NAMES = [
    "LLaMA_3_3_70B",
    "LLaMA_3_1_8B",
    "LLaMA_4_Scout_17B",
    "Qwen3_32B",
    "OpenAI_OSS_120B",
    "Allam_2_7B",
]

# ─────────────────────────────────────
# STEP 1 — SEE RAW ANSWERS FIRST
# This shows us what format LLMs use
# ─────────────────────────────────────
print("\n🔍 SAMPLE RAW ANSWERS from top 3 models")
print("-" * 60)
for _, row in rdf.head(8).iterrows():
    print(f"\nQ{row['id']}: {row['question'][:55]}...")
    print(f"  ✅ Correct: {row['correct_answer']}"
          f" ({row['unit']})")
    for m in ["LLaMA_3_3_70B",
              "LLaMA_4_Scout_17B",
              "OpenAI_OSS_120B"]:
        if m in rdf.columns:
            ans = str(row.get(m, "N/A"))[:70]
            print(f"  {m[:22]}: {ans}")

# ─────────────────────────────────────
# HELPER — IS ERROR?
# Errors are NOT hallucinations
# ─────────────────────────────────────
def is_error(text):
    if not text or pd.isna(text):
        return True
    t = str(text).strip()
    return (
        t.startswith("ERROR:") or
        t == "EMPTY_RESPONSE" or
        len(t) == 0 or
        t == "nan"
    )

# ─────────────────────────────────────
# HELPER — EXTRACT NUMBER
# Handles every format LLMs use
# ─────────────────────────────────────
def extract_number(text):
    if not text or pd.isna(text):
        return None
    text = str(text).strip()
    if is_error(text):
        return None

    t = text.lower()
    t = t.replace("$","").replace(
        "€","").replace("£","").replace("₹","")

    # Billion
    b = re.search(r'(\d+\.?\d*)\s*billion', t)
    if b:
        return float(b.group(1)) * 1_000_000_000

    # Million
    m = re.search(r'(\d+\.?\d*)\s*million', t)
    if m:
        return float(m.group(1)) * 1_000_000

    # Crore (Indian)
    cr = re.search(r'(\d+\.?\d*)\s*crore', t)
    if cr:
        return float(cr.group(1)) * 10_000_000

    # Lakh (Indian)
    lk = re.search(r'(\d+\.?\d*)\s*lakh', t)
    if lk:
        return float(lk.group(1)) * 100_000

    # Thousand
    th = re.search(r'(\d+\.?\d*)\s*thousand', t)
    if th:
        return float(th.group(1)) * 1_000

    # Numbers with commas — 704,753,890
    comma = re.findall(r'\d{1,3}(?:,\d{3})+', text)
    if comma:
        vals = [float(x.replace(",",""))
                for x in comma]
        return max(vals)

    # Percentage — 97% or 97.5%
    pct = re.search(r'(\d+\.?\d*)\s*%', text)
    if pct:
        return float(pct.group(1))

    # Decimal numbers — 72.2
    decimals = re.findall(r'\b\d+\.\d+\b', text)
    if decimals:
        non_years = [float(x) for x in decimals
                     if not (1900 <= float(x) <= 2100)]
        if non_years:
            return non_years[0]
        return float(decimals[0])

    # Plain integers
    integers = re.findall(r'\b\d+\b', text)
    if integers:
        vals = [int(x) for x in integers]
        non_years = [v for v in vals
                     if not (1900 <= v <= 2100)]
        if non_years:
            return float(max(non_years))
        if vals:
            return float(max(vals))

    return None


# ─────────────────────────────────────
# HELPER — EXTRACT COUNTRY
# ─────────────────────────────────────
def extract_country(text):
    if not text or pd.isna(text):
        return None
    t = str(text).lower()
    countries = {
        "united states of america": "USA",
        "united states": "USA",
        "usa": "USA",
        "u.s.a": "USA",
        "u.s": "USA",
        "america": "USA",
        "china": "China",
        "india": "India",
        "brazil": "Brazil",
        "brasil": "Brazil",
        "united kingdom": "UK",
        "great britain": "UK",
        "britain": "UK",
        "england": "UK",
        "uk": "UK",
        "russia": "Russia",
        "pakistan": "Pakistan",
        "bangladesh": "Bangladesh",
        "france": "France",
        "germany": "Germany",
        "japan": "Japan",
        "south korea": "S. Korea",
        "korea": "S. Korea",
        "italy": "Italy",
    }
    # Check longest match first
    for key in sorted(countries.keys(),
                      key=len, reverse=True):
        if key in t:
            return countries[key]
    return None


# ─────────────────────────────────────
# HELPER — EXTRACT YES/NO
# ─────────────────────────────────────
def extract_yes_no(text):
    if not text or pd.isna(text):
        return None
    t = str(text).lower().strip()

    if t.startswith("yes"):
        return "Yes"
    if t.startswith("no"):
        return "No"
    # ── YES / NO ──
    if unit == "yes/no":
        # Check refusal first
        refusal_phrases = [
            "i cannot","i can't","i don't have",
            "real-time","not available","i'm sorry",
            "as an ai","cannot provide"
        ]
        if any(p in llm_str.lower()
               for p in refusal_phrases):
            return 0.0
        extracted = extract_yes_no(llm_str)
    positives = [
        "correct", "true", "indeed",
        "has crossed", "has achieved",
        "above", "higher than", "more than",
        "it does", "it has"
    ]
    negatives = [
        "incorrect", "false", "below",
        "has not", "hasn't", "not yet",
        "does not", "doesn't", "lower than",
        "it does not", "it has not"
    ]
    for w in positives:
        if w in t[:100]:
            return "Yes"
    for w in negatives:
        if w in t[:100]:
            return "No"
    return None
    # ── YES / NO ──
    if unit == "yes/no":
        # Check refusal first
        refusal_phrases = [
            "i cannot","i can't","i don't have",
            "real-time","not available","i'm sorry",
            "as an ai","cannot provide"
        ]
        if any(p in llm_str.lower()
               for p in refusal_phrases):
            return 0.0
        extracted = extract_yes_no(llm_str)

# ─────────────────────────────────────
# HELPER — CONFIDENT WRONG?
# ─────────────────────────────────────
def is_confident_wrong(text):
    if not text or pd.isna(text):
        return False
    t = str(text).lower()
    words = [
        "exactly", "precisely", "definitely",
        "certainly", "the exact figure",
        "to be exact", "without doubt",
        "absolutely", "it is exactly",
        "the answer is exactly"
    ]
    return any(w in t for w in words)


# ─────────────────────────────────────
# MAIN SCORING FUNCTION
# Returns: 1.0, 0.5, 0.0, -0.5, "ERROR"
# ─────────────────────────────────────
def score_answer(llm_answer, correct_answer, unit):

    # Separate errors from wrong answers
    if is_error(llm_answer):
        return "ERROR"

    llm_str     = str(llm_answer).strip()
    correct_str = str(correct_answer).lower().strip()

    # ── YES / NO ──
    if unit == "yes/no":
        extracted = extract_yes_no(llm_str)
        if not extracted:
            return 0.0
        correct_yn = "Yes" if correct_str in [
            "yes","above 70","true",
            "above","higher"] else "No"
        if extracted.lower() == correct_yn.lower():
            return 1.0
        return (-0.5 if is_confident_wrong(llm_str)
                else 0.0)

    # ── COUNTRY NAME ──
    if unit == "country name":
        extracted  = extract_country(llm_str)
        correct_c  = extract_country(correct_str)
        if not correct_c:
            correct_c = correct_str.strip().title()
        if not extracted:
            return 0.0
        if extracted.lower() == correct_c.lower():
            return 1.0
        if (extracted.lower() in correct_str or
                correct_str in extracted.lower()):
            return 1.0
        return (-0.5 if is_confident_wrong(llm_str)
                else 0.0)

    # ── NUMERICAL ──
    # ── NUMERICAL ──
    try:
        correct_num = float(
            str(correct_answer).replace(",",""))
        extracted   = extract_number(llm_str)

        # Refusal phrases = wrong answer
        refusal_phrases = [
            "i cannot", "i can't", "i don't have",
            "real-time", "not available",
            "i'm sorry", "as an ai", "i am unable",
            "no access", "cannot provide",
            "do not have access", "i lack",
            "beyond my", "my training",
            "i'm not able", "not able to provide",
            "cannot answer", "don't have access"
        ]
        llm_lower = llm_str.lower()
        if any(phrase in llm_lower
               for phrase in refusal_phrases):
            return 0.0

        if extracted is None:
            return 0.0

        if correct_num == 0:
            return 1.0 if extracted == 0 else 0.0

        error_pct = (
            abs(extracted - correct_num)
            / abs(correct_num)
        ) * 100

        if error_pct <= 10:
            return 1.0   # Within 10% → Correct
        elif error_pct <= 30:
            return 0.5   # Within 30% → Partial
        else:
            return (-0.5
                    if is_confident_wrong(llm_str)
                    else 0.0)
    except Exception:
        return 0.0


# ─────────────────────────────────────
# RUN SCORING FOR ALL 14 MODELS
# ─────────────────────────────────────
print("\n\n🔢 Scoring all 2,814 responses...")
print("-" * 60)
print(f"  {'Model':<25} {'✅Cor':>6} {'⚠️Par':>6}"
      f" {'❌Wrg':>6} {'😱Con':>6} {'🚫Err':>6}"
      f" {'Acc%':>7}")
print(f"  {'-'*65}")

for model in MODEL_NAMES:
    if model not in rdf.columns:
        print(f"  {model:<25} NOT FOUND IN DATA")
        continue

    score_col = f"{model}_score"
    scores    = []

    for _, row in rdf.iterrows():
        s = score_answer(
            row[model],
            row["correct_answer"],
            row["unit"])
        scores.append(s)

    rdf[score_col] = scores

    correct    = scores.count(1.0)
    partial    = scores.count(0.5)
    wrong      = scores.count(0.0)
    conf_wrong = scores.count(-0.5)
    errors     = scores.count("ERROR")
    total      = len(scores)
    acc        = (correct / total) * 100

    print(f"  {model:<25} {correct:>6} {partial:>6}"
          f" {wrong:>6} {conf_wrong:>6} {errors:>6}"
          f" {acc:>6.1f}%")

# ─────────────────────────────────────
# CALCULATE METRICS PER MODEL
# ─────────────────────────────────────
print("\n📊 Calculating final metrics...")

model_metrics = []

for model in MODEL_NAMES:
    score_col = f"{model}_score"
    if score_col not in rdf.columns:
        continue

    scores = rdf[score_col].tolist()
    total  = len(scores)

    correct    = scores.count(1.0)
    partial    = scores.count(0.5)
    wrong      = scores.count(0.0)
    conf_wrong = scores.count(-0.5)
    errors     = scores.count("ERROR")
    answered   = total - errors

    # Accuracy over all 201 questions
    accuracy_pct = (correct / total) * 100

    # Hallucination only among answered questions
    # So errors don't inflate hallucination rate
    if answered > 0:
        hallucination_pct = (
            (wrong + conf_wrong) / answered) * 100
    else:
        hallucination_pct = 0.0

    error_pct   = (errors / total) * 100
    partial_pct = (partial / total) * 100

    # Category breakdown
    cat_scores = {}
    for cat in rdf["category"].unique():
        mask   = rdf["category"] == cat
        cat_s  = rdf.loc[mask, score_col].tolist()
        total_c = len(cat_s)
        correct_c = cat_s.count(1.0)
        acc_c = (correct_c / total_c) * 100 \
            if total_c > 0 else 0
        cat_scores[cat] = round(acc_c, 1)

    # Difficulty breakdown
    diff_scores = {}
    for diff in ["Easy", "Medium", "Hard"]:
        mask   = rdf["difficulty"] == diff
        diff_s = rdf.loc[mask, score_col].tolist()
        total_d = len(diff_s)
        correct_d = diff_s.count(1.0)
        acc_d = (correct_d / total_d) * 100 \
            if total_d > 0 else 0
        diff_scores[diff] = round(acc_d, 1)

    model_metrics.append({
        "model":             model,
        "total":             total,
        "correct":           correct,
        "partial":           partial,
        "wrong":             wrong,
        "confidently_wrong": conf_wrong,
        "errors":            errors,
        "answered":          answered,
        "accuracy_pct":      round(accuracy_pct, 1),
        "hallucination_pct": round(hallucination_pct,1),
        "error_pct":         round(error_pct, 1),
        "partial_pct":       round(partial_pct, 1),
        **{f"cat_{k[:20]}": v
           for k, v in cat_scores.items()},
        **{f"diff_{k}": v
           for k, v in diff_scores.items()},
    })

metrics_df = pd.DataFrame(model_metrics) \
               .sort_values("accuracy_pct",
                             ascending=False)

# Convert score column to numeric for saving
for model in MODEL_NAMES:
    sc = f"{model}_score"
    if sc in rdf.columns:
        rdf[sc] = pd.to_numeric(
            rdf[sc], errors="coerce").fillna(-1)

# ─────────────────────────────────────
# SAVE FILES
# ─────────────────────────────────────
os.makedirs("scores", exist_ok=True)
today = datetime.today().strftime("%Y-%m-%d")

rdf.to_csv(
    "scores/scored_responses_latest.csv",
    index=False)
metrics_df.to_csv(
    "scores/model_metrics.csv",
    index=False)

# ─────────────────────────────────────
# PRINT FINAL RESULTS
# ─────────────────────────────────────
print(f"\n{'='*60}")
print("  🏆 FINAL BENCHMARK RESULTS")
print(f"{'='*60}")
print(f"\n  {'Rank':<5} {'Model':<25} "
      f"{'Accuracy':>9} {'Hallucin':>9} "
      f"{'Errors':>8} {'Correct':>9}")
print(f"  {'-'*67}")

for rank, (_, row) in enumerate(
        metrics_df.iterrows(), 1):
    acc = row["accuracy_pct"]
    hal = row["hallucination_pct"]
    err = row["error_pct"]
    cor = row["correct"]
    ans = row["answered"]

    if ans == 0:
        flag = "⚫ API Failed"
    elif acc >= 35:
        flag = "🟢 Good"
    elif acc >= 20:
        flag = "🟡 Average"
    else:
        flag = "🔴 Poor"

    print(f"  {rank:<5} {row['model']:<25} "
          f"{acc:>8.1f}% {hal:>8.1f}% "
          f"{err:>7.1f}% {cor:>7}/201  {flag}")

print(f"\n{'='*60}")
print("  📊 CATEGORY BREAKDOWN (top 3 models only)")
print(f"{'='*60}")

top3 = metrics_df[
    metrics_df["answered"] > 0
].head(3)["model"].tolist()

for cat in rdf["category"].unique():
    print(f"\n  {cat}:")
    for model in top3:
        key = f"cat_{cat[:20]}"
        row = metrics_df[
            metrics_df["model"] == model]
        if not row.empty and key in row.columns:
            val = row.iloc[0][key]
            bar = "█" * int(val / 5)
            print(f"    {model:<25} "
                  f"{val:>6.1f}%  {bar}")

print(f"\n{'='*60}")
print("  📈 DIFFICULTY BREAKDOWN (top 3 models)")
print(f"{'='*60}")

for diff in ["Easy", "Medium", "Hard"]:
    key = f"diff_{diff}"
    print(f"\n  {diff} Questions:")
    for model in top3:
        row = metrics_df[
            metrics_df["model"] == model]
        if not row.empty and key in row.columns:
            val = row.iloc[0][key]
            bar = "█" * int(val / 5)
            print(f"    {model:<25} "
                  f"{val:>6.1f}%  {bar}")

print(f"\n{'='*60}")
print("  🔬 KEY RESEARCH FINDINGS")
print(f"{'='*60}")

answered_df = metrics_df[
    metrics_df["answered"] > 0]
failed_df   = metrics_df[
    metrics_df["answered"] == 0]

if not answered_df.empty:
    best      = answered_df.iloc[0]
    worst_hal = answered_df.loc[
        answered_df[
            "hallucination_pct"].idxmax()]
    llama70   = metrics_df[
        metrics_df["model"] == "LLaMA_3_3_70B"]
    llama8    = metrics_df[
        metrics_df["model"] == "LLaMA_3_1_8B"]

    print(f"\n  1. Best model overall:")
    print(f"     {best['model']} → "
          f"{best['accuracy_pct']}% accuracy "
          f"| {best['correct']}/201 correct")

    print(f"\n  2. Most hallucinating (among answered):")
    print(f"     {worst_hal['model']} → "
          f"{worst_hal['hallucination_pct']:.1f}% "
          f"hallucination rate")

    if not llama70.empty and not llama8.empty:
        diff = (llama70.iloc[0]["accuracy_pct"] -
                llama8.iloc[0]["accuracy_pct"])
        print(f"\n  3. Model size effect:")
        print(f"     LLaMA 70B: "
              f"{llama70.iloc[0]['accuracy_pct']}%"
              f"  vs  LLaMA 8B: "
              f"{llama8.iloc[0]['accuracy_pct']}%")
        print(f"     → 70B outperforms 8B "
              f"by {diff:.1f}% accuracy")

    if not failed_df.empty:
        names = ", ".join(failed_df["model"].tolist())
        print(f"\n  4. Complete API failures "
              f"({len(failed_df)} models):")
        print(f"     {names}")
        print(f"     → These returned only errors "
              f"(OpenRouter rate limits)")
        print(f"     → NOT counted as hallucinations")

print(f"\n{'='*60}")
print(f"  ✅ Saved: scores/scored_responses_latest.csv")
print(f"  ✅ Saved: scores/model_metrics.csv")
print(f"{'='*60}")
print(f"\n🎯 Next step: "
      f"streamlit run dashboard/app.py")