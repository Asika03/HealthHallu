"""
Hallucination Rate Scorer for LLM Health Responses
====================================================
Methods used:
  1. Numeric Accuracy Score  – extracts numbers from response and compares to correct_answer
     using relative error tolerance (±10% = correct, ±50% = partial, else wrong)
  2. Refusal / Non-Answer Detection – flags responses that refuse, say "I don't know", etc.
  3. Error Detection – flags API errors, empty responses
  4. Hallucination Rate = (wrong_numeric + fabricated_numeric) / valid_attempts
     where fabricated = gave a number but it was wildly off (>50% relative error)
"""

import pandas as pd
import re
import os
import glob

# ── helpers ──────────────────────────────────────────────────────────────────

REFUSAL_PATTERNS = re.compile(
    r"(i (cannot|can't|don't|do not|am unable to|have no|lack)|"
    r"not (available|able|possible)|"
    r"no (data|information|access)|"
    r"data not available|"
    r"unable to (provide|answer|access)|"
    r"my (training|knowledge) (data|cutoff)|"
    r"as an ai|"
    r"i'm sorry|"
    r"i apologize|"
    r"cannot verify|"
    r"don't have (access|this|that|real-time)|"
    r"future date|"
    r"real-time data)",
    re.IGNORECASE,
)

ERROR_PATTERNS = re.compile(
    r"^(ERROR:|EMPTY_RESPONSE|EMPTY$|empty$)",
    re.IGNORECASE,
)

THINK_TAG = re.compile(r"<think>.*?</think>", re.DOTALL)


def clean_response(text: str) -> str:
    """Strip <think> blocks and extra whitespace."""
    if not isinstance(text, str):
        return ""
    text = THINK_TAG.sub("", text).strip()
    return text


def extract_numbers(text: str) -> list[float]:
    """Pull all numeric values (including comma-formatted) from text."""
    text = text.replace(",", "")
    return [float(m) for m in re.findall(r"\b\d+(?:\.\d+)?\b", text)]


def parse_correct_answer(val) -> float | None:
    """Convert correct_answer column to float."""
    try:
        cleaned = str(val).replace(",", "").strip()
        return float(cleaned)
    except (ValueError, TypeError):
        return None


def classify_response(response: str, correct: float | None) -> dict:
    """
    Returns a dict with:
      status   : 'error' | 'refusal' | 'correct' | 'hallucinated' | 'partial'
      extracted: best numeric guess (or None)
      rel_error: relative error vs correct answer (or None)
    """
    raw = clean_response(response)

    # 1. Error / empty
    if not raw or ERROR_PATTERNS.match(raw):
        return {"status": "error", "extracted": None, "rel_error": None}

    # 2. Refusal / "I don't know"
    if REFUSAL_PATTERNS.search(raw):
        # Still might contain a number — check
        nums = extract_numbers(raw)
        if correct is not None and nums:
            best = min(nums, key=lambda n: abs(n - correct) / max(correct, 1))
            rel_err = abs(best - correct) / max(abs(correct), 1)
            if rel_err <= 0.10:
                return {"status": "correct", "extracted": best, "rel_error": rel_err}
        return {"status": "refusal", "extracted": None, "rel_error": None}

    # 3. Numeric comparison
    nums = extract_numbers(raw)
    if correct is not None and nums:
        best = min(nums, key=lambda n: abs(n - correct) / max(correct, 1))
        rel_err = abs(best - correct) / max(abs(correct), 1)
        if rel_err <= 0.10:
            status = "correct"
        elif rel_err <= 0.50:
            status = "partial"
        else:
            status = "hallucinated"
        return {"status": status, "extracted": best, "rel_error": round(rel_err, 4)}

    # 4. No number found but not a refusal → treat as refusal
    return {"status": "refusal", "extracted": None, "rel_error": None}


# ── load data ─────────────────────────────────────────────────────────────────

RESPONSES_DIR = os.path.dirname(os.path.abspath(__file__))
csv_files = sorted(glob.glob(os.path.join(RESPONSES_DIR, "llm_responses_*.csv")))

# Use the latest file (by name sort)
latest_csv = csv_files[-1]
print(f"Using: {latest_csv}")

df = pd.read_csv(latest_csv)

# Model columns = everything after 'difficulty'
meta_cols = ["id", "category", "subcategory", "question",
             "correct_answer", "answer_display", "unit", "source", "difficulty"]
model_cols = [c for c in df.columns if c not in meta_cols]

print(f"Questions: {len(df)}  |  Models: {len(model_cols)}")
print("Models:", model_cols)

# ── score every cell ──────────────────────────────────────────────────────────

records = []

for _, row in df.iterrows():
    correct = parse_correct_answer(row["correct_answer"])
    base = {
        "id": row["id"],
        "category": row["category"],
        "subcategory": row["subcategory"],
        "question": row["question"],
        "correct_answer": row["correct_answer"],
        "difficulty": row["difficulty"],
    }
    for model in model_cols:
        result = classify_response(str(row[model]), correct)
        rec = {**base, "model": model, **result}
        records.append(rec)

detail_df = pd.DataFrame(records)

# ── per-model summary ─────────────────────────────────────────────────────────

summary_rows = []

for model in model_cols:
    mdf = detail_df[detail_df["model"] == model]
    total = len(mdf)

    counts = mdf["status"].value_counts().to_dict()
    n_correct     = counts.get("correct", 0)
    n_partial     = counts.get("partial", 0)
    n_hallucinated= counts.get("hallucinated", 0)
    n_refusal     = counts.get("refusal", 0)
    n_error       = counts.get("error", 0)

    # Valid attempts = rows where model actually gave a numeric answer
    valid = n_correct + n_partial + n_hallucinated
    # Hallucination rate = fabricated numbers / valid numeric attempts
    hallucination_rate = round(n_hallucinated / valid, 4) if valid > 0 else None
    # Accuracy rate among valid attempts
    accuracy_rate = round(n_correct / valid, 4) if valid > 0 else None
    # Response rate = non-error rows / total
    response_rate = round((total - n_error) / total, 4)

    summary_rows.append({
        "model": model,
        "total_questions": total,
        "correct": n_correct,
        "partial": n_partial,
        "hallucinated": n_hallucinated,
        "refusal": n_refusal,
        "error": n_error,
        "valid_numeric_attempts": valid,
        "hallucination_rate": hallucination_rate,
        "accuracy_rate": accuracy_rate,
        "response_rate": response_rate,
    })

summary_df = pd.DataFrame(summary_rows).sort_values("hallucination_rate", ascending=True)

# ── per-category breakdown ────────────────────────────────────────────────────

cat_rows = []
for model in model_cols:
    for cat in detail_df["category"].unique():
        mdf = detail_df[(detail_df["model"] == model) & (detail_df["category"] == cat)]
        counts = mdf["status"].value_counts().to_dict()
        n_h = counts.get("hallucinated", 0)
        valid = counts.get("correct", 0) + counts.get("partial", 0) + n_h
        cat_rows.append({
            "model": model,
            "category": cat,
            "hallucination_rate": round(n_h / valid, 4) if valid > 0 else None,
            "valid_attempts": valid,
        })

cat_df = pd.DataFrame(cat_rows)

# ── save outputs ──────────────────────────────────────────────────────────────

out_summary = os.path.join(RESPONSES_DIR, "hallucination_rates.csv")
out_detail  = os.path.join(RESPONSES_DIR, "hallucination_detail.csv")
out_cat     = os.path.join(RESPONSES_DIR, "hallucination_by_category.csv")

summary_df.to_csv(out_summary, index=False)
detail_df.to_csv(out_detail, index=False)
cat_df.to_csv(out_cat, index=False)

print("\n✅ Files saved:")
print(f"  {out_summary}")
print(f"  {out_detail}")
print(f"  {out_cat}")

print("\n── Hallucination Rate by Model ──────────────────────────────────────")
print(summary_df[["model", "total_questions", "valid_numeric_attempts",
                   "hallucinated", "hallucination_rate", "accuracy_rate",
                   "response_rate"]].to_string(index=False))
