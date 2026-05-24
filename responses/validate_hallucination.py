"""
Hallucination Dataset Validator
================================
Validates hallucination_rates.csv, hallucination_detail.csv,
and hallucination_by_category.csv for:

  V1  Row count integrity  — detail rows == questions × models
  V2  Column completeness  — no unexpected missing columns
  V3  Status enum check    — only valid status values used
  V4  Math consistency     — correct+partial+hallucinated+refusal+error == total
  V5  Rate bounds          — all rates in [0, 1]
  V6  Rate formula check   — hallucination_rate == hallucinated / valid_numeric
  V7  Accuracy formula     — accuracy_rate == correct / valid_numeric
  V8  Response rate        — response_rate == (total - error) / total
  V9  Year-token false pos — flag rows where extracted == 2026 (year leak)
  V10 Zero-coverage models — models with 0 valid attempts flagged
  V11 Category coverage    — categories with 0 valid attempts flagged
  V12 Rel-error sanity     — correct rows must have rel_error <= 0.10
  V13 Hallucinated rows    — must have rel_error > 0.50
  V14 Partial rows         — rel_error must be in (0.10, 0.50]
  V15 Cross-file model set — same models in summary and detail

Outputs:
  validation_report.csv   — per-check pass/fail/warn with details
  hallucination_rates_validated.csv  — corrected summary (year-leak fixed)
  hallucination_detail_validated.csv — corrected detail (year-leak fixed)
"""

import pandas as pd
import numpy as np
import os

RESPONSES_DIR = os.path.dirname(os.path.abspath(__file__))

SUMMARY_FILE  = os.path.join(RESPONSES_DIR, "hallucination_rates.csv")
DETAIL_FILE   = os.path.join(RESPONSES_DIR, "hallucination_detail.csv")
CATEGORY_FILE = os.path.join(RESPONSES_DIR, "hallucination_by_category.csv")

VALID_STATUSES = {"correct", "partial", "hallucinated", "refusal", "error"}

results = []  # list of dicts for report

def log(check_id, name, status, detail="", affected=0):
    icon = {"PASS": "✅", "FAIL": "❌", "WARN": "⚠️ ", "FIX": "🔧"}[status]
    print(f"  {icon} [{check_id}] {name}: {detail}")
    results.append({
        "check_id": check_id,
        "check_name": name,
        "status": status,
        "detail": detail,
        "affected_rows": affected,
    })

print("\n" + "="*65)
print("  HALLUCINATION DATASET VALIDATOR")
print("="*65)

# ── Load files ────────────────────────────────────────────────────────────────
print("\n📂 Loading files...")
try:
    summary  = pd.read_csv(SUMMARY_FILE)
    detail   = pd.read_csv(DETAIL_FILE)
    category = pd.read_csv(CATEGORY_FILE)
    print(f"  summary  : {len(summary)} rows")
    print(f"  detail   : {len(detail)} rows")
    print(f"  category : {len(category)} rows")
except Exception as e:
    print(f"  ❌ FATAL: Could not load files — {e}")
    exit(1)

n_models    = len(summary)
n_questions = detail["id"].nunique()
n_detail    = len(detail)

print(f"\n  Models: {n_models}  |  Questions: {n_questions}  |  Detail rows: {n_detail}")

# ── V1: Row count integrity ───────────────────────────────────────────────────
print("\n── Checks ──────────────────────────────────────────────────────────────")
expected_rows = n_models * n_questions
if n_detail == expected_rows:
    log("V1", "Row count integrity",
        "PASS", f"{n_detail} == {n_models} models × {n_questions} questions")
else:
    log("V1", "Row count integrity",
        "FAIL", f"Expected {expected_rows}, got {n_detail}",
        affected=abs(n_detail - expected_rows))

# ── V2: Column completeness ───────────────────────────────────────────────────
required_summary_cols = {
    "model","total_questions","correct","partial","hallucinated",
    "refusal","error","valid_numeric_attempts",
    "hallucination_rate","accuracy_rate","response_rate"
}
required_detail_cols = {
    "id","category","subcategory","question","correct_answer",
    "difficulty","model","status","extracted","rel_error"
}
required_cat_cols = {"model","category","hallucination_rate","valid_attempts"}

missing_s = required_summary_cols - set(summary.columns)
missing_d = required_detail_cols  - set(detail.columns)
missing_c = required_cat_cols     - set(category.columns)

for label, missing in [("summary", missing_s), ("detail", missing_d), ("category", missing_c)]:
    if not missing:
        log("V2", f"Column completeness [{label}]", "PASS", "All required columns present")
    else:
        log("V2", f"Column completeness [{label}]", "FAIL",
            f"Missing: {missing}", affected=len(missing))

# ── V3: Status enum check ─────────────────────────────────────────────────────
bad_status = detail[~detail["status"].isin(VALID_STATUSES)]
if bad_status.empty:
    log("V3", "Status enum values", "PASS", f"All values in {VALID_STATUSES}")
else:
    log("V3", "Status enum values", "FAIL",
        f"Invalid values: {bad_status['status'].unique().tolist()}",
        affected=len(bad_status))

# ── V4: Math consistency (counts sum to total) ────────────────────────────────
summary["_computed_total"] = (
    summary["correct"] + summary["partial"] +
    summary["hallucinated"] + summary["refusal"] + summary["error"]
)
mismatch = summary[summary["_computed_total"] != summary["total_questions"]]
if mismatch.empty:
    log("V4", "Count totals sum correctly", "PASS",
        "correct+partial+hallucinated+refusal+error == total_questions for all models")
else:
    log("V4", "Count totals sum correctly", "FAIL",
        f"Mismatch in: {mismatch['model'].tolist()}", affected=len(mismatch))
summary.drop(columns=["_computed_total"], inplace=True)

# ── V5: Rate bounds [0, 1] ────────────────────────────────────────────────────
rate_cols = ["hallucination_rate", "accuracy_rate", "response_rate"]
out_of_bounds = []
for col in rate_cols:
    vals = summary[col].dropna()
    bad  = vals[(vals < 0) | (vals > 1)]
    if not bad.empty:
        out_of_bounds.append(f"{col}: {bad.tolist()}")

if not out_of_bounds:
    log("V5", "Rate bounds [0,1]", "PASS", "All rates within valid range")
else:
    log("V5", "Rate bounds [0,1]", "FAIL", "; ".join(out_of_bounds))

# ── V6: Hallucination rate formula ───────────────────────────────────────────
def check_rate(row, numerator_col, denominator_col, rate_col, tol=0.001):
    denom = row[denominator_col]
    if pd.isna(row[rate_col]):
        return denom == 0  # NaN is correct when denom is 0
    if denom == 0:
        return False
    expected = row[numerator_col] / denom
    return abs(expected - row[rate_col]) <= tol

h_bad = summary[~summary.apply(
    lambda r: check_rate(r, "hallucinated", "valid_numeric_attempts", "hallucination_rate"),
    axis=1
)]
if h_bad.empty:
    log("V6", "Hallucination rate formula", "PASS",
        "hallucinated / valid_numeric_attempts matches for all models")
else:
    log("V6", "Hallucination rate formula", "FAIL",
        f"Formula mismatch: {h_bad['model'].tolist()}", affected=len(h_bad))

# ── V7: Accuracy rate formula ─────────────────────────────────────────────────
a_bad = summary[~summary.apply(
    lambda r: check_rate(r, "correct", "valid_numeric_attempts", "accuracy_rate"),
    axis=1
)]
if a_bad.empty:
    log("V7", "Accuracy rate formula", "PASS",
        "correct / valid_numeric_attempts matches for all models")
else:
    log("V7", "Accuracy rate formula", "FAIL",
        f"Formula mismatch: {a_bad['model'].tolist()}", affected=len(a_bad))

# ── V8: Response rate formula ─────────────────────────────────────────────────
summary["_rr_check"] = (summary["total_questions"] - summary["error"]) / summary["total_questions"]
rr_bad = summary[abs(summary["_rr_check"] - summary["response_rate"]) > 0.001]
if rr_bad.empty:
    log("V8", "Response rate formula", "PASS",
        "(total - error) / total matches for all models")
else:
    log("V8", "Response rate formula", "FAIL",
        f"Mismatch: {rr_bad['model'].tolist()}", affected=len(rr_bad))
summary.drop(columns=["_rr_check"], inplace=True)

# ── V9: Year-token false positives (extracted == 2026.0) ─────────────────────
year_leak = detail[detail["extracted"] == 2026.0]
if year_leak.empty:
    log("V9", "Year-token false positives", "PASS", "No year-leak extractions found")
else:
    affected_models = year_leak["model"].value_counts().to_dict()
    log("V9", "Year-token false positives", "FIX",
        f"{len(year_leak)} rows extracted year '2026' from question text, not answer. "
        f"Models: {affected_models}. Reclassifying as 'refusal'.",
        affected=len(year_leak))

    # Apply fix: reclassify year-leak rows as refusal
    detail.loc[detail["extracted"] == 2026.0, "status"]    = "refusal"
    detail.loc[detail["extracted"] == 2026.0, "extracted"] = np.nan
    detail.loc[detail["extracted"] == 2026.0, "rel_error"] = np.nan

# ── V10: Zero-coverage models ─────────────────────────────────────────────────
zero_cov = summary[summary["valid_numeric_attempts"] == 0]
if zero_cov.empty:
    log("V10", "Zero-coverage models", "PASS", "All models have numeric attempts")
else:
    log("V10", "Zero-coverage models", "WARN",
        f"Models with 0 numeric answers (rates are N/A): {zero_cov['model'].tolist()}",
        affected=len(zero_cov))

# ── V11: Category coverage ────────────────────────────────────────────────────
zero_cat = category[category["valid_attempts"] == 0]
if zero_cat.empty:
    log("V11", "Category coverage", "PASS", "All category rows have valid attempts")
else:
    log("V11", "Category coverage", "WARN",
        f"{len(zero_cat)} category rows have 0 valid attempts (will be flagged as insufficient_data in output)",
        affected=len(zero_cat))

# ── V12: Correct rows rel_error <= 0.10 ──────────────────────────────────────
correct_rows = detail[detail["status"] == "correct"]
bad_correct  = correct_rows[correct_rows["rel_error"].notna() & (correct_rows["rel_error"] > 0.10)]
if bad_correct.empty:
    log("V12", "Correct rows rel_error ≤ 0.10", "PASS",
        f"All {len(correct_rows)} correct rows have rel_error ≤ 0.10")
else:
    log("V12", "Correct rows rel_error ≤ 0.10", "FAIL",
        f"{len(bad_correct)} correct rows have rel_error > 0.10",
        affected=len(bad_correct))

# ── V13: Hallucinated rows rel_error > 0.50 ──────────────────────────────────
hall_rows = detail[detail["status"] == "hallucinated"]
bad_hall  = hall_rows[hall_rows["rel_error"].notna() & (hall_rows["rel_error"] <= 0.50)]
if bad_hall.empty:
    log("V13", "Hallucinated rows rel_error > 0.50", "PASS",
        f"All {len(hall_rows)} hallucinated rows have rel_error > 0.50")
else:
    log("V13", "Hallucinated rows rel_error > 0.50", "FAIL",
        f"{len(bad_hall)} hallucinated rows have rel_error ≤ 0.50",
        affected=len(bad_hall))

# ── V14: Partial rows rel_error in (0.10, 0.50] ──────────────────────────────
partial_rows = detail[detail["status"] == "partial"]
bad_partial  = partial_rows[
    partial_rows["rel_error"].notna() &
    ~((partial_rows["rel_error"] >= 0.10) & (partial_rows["rel_error"] <= 0.50))
]
if bad_partial.empty:
    log("V14", "Partial rows rel_error in (0.10, 0.50]", "PASS",
        f"All {len(partial_rows)} partial rows have rel_error in correct range")
else:
    log("V14", "Partial rows rel_error in (0.10, 0.50]", "FAIL",
        f"{len(bad_partial)} partial rows outside (0.10, 0.50]",
        affected=len(bad_partial))

# ── V15: Cross-file model set consistency ─────────────────────────────────────
summary_models  = set(summary["model"])
detail_models   = set(detail["model"])
category_models = set(category["model"])

diff_sd = summary_models.symmetric_difference(detail_models)
diff_sc = summary_models.symmetric_difference(category_models)

if not diff_sd and not diff_sc:
    log("V15", "Cross-file model set", "PASS",
        "Same models in summary, detail, and category files")
else:
    msg = []
    if diff_sd: msg.append(f"summary↔detail diff: {diff_sd}")
    if diff_sc: msg.append(f"summary↔category diff: {diff_sc}")
    log("V15", "Cross-file model set", "FAIL", "; ".join(msg))

# ── Recompute summary after year-leak fix ─────────────────────────────────────
print("\n🔧 Recomputing summary after year-leak fix...")

new_summary_rows = []
for model in summary["model"]:
    mdf = detail[detail["model"] == model]
    counts = mdf["status"].value_counts().to_dict()
    n_correct      = counts.get("correct", 0)
    n_partial      = counts.get("partial", 0)
    n_hallucinated = counts.get("hallucinated", 0)
    n_refusal      = counts.get("refusal", 0)
    n_error        = counts.get("error", 0)
    total          = len(mdf)
    valid          = n_correct + n_partial + n_hallucinated

    h_rate = round(n_hallucinated / valid, 4) if valid > 0 else None
    a_rate = round(n_correct / valid, 4)      if valid > 0 else None
    r_rate = round((total - n_error) / total, 4)

    new_summary_rows.append({
        "model": model,
        "total_questions": total,
        "correct": n_correct,
        "partial": n_partial,
        "hallucinated": n_hallucinated,
        "refusal": n_refusal,
        "error": n_error,
        "valid_numeric_attempts": valid,
        "hallucination_rate": h_rate,
        "accuracy_rate": a_rate,
        "response_rate": r_rate,
    })

new_summary = pd.DataFrame(new_summary_rows).sort_values(
    "hallucination_rate", ascending=True, na_position="last"
)

# Recompute category rates too
new_cat_rows = []
for model in detail["model"].unique():
    for cat in detail["category"].unique():
        mdf = detail[(detail["model"] == model) & (detail["category"] == cat)]
        counts = mdf["status"].value_counts().to_dict()
        n_h   = counts.get("hallucinated", 0)
        valid = counts.get("correct", 0) + counts.get("partial", 0) + n_h
        new_cat_rows.append({
            "model": model,
            "category": cat,
            "hallucination_rate": round(n_h / valid, 4) if valid > 0 else None,
            "valid_attempts": valid,
            "data_status": "ok" if valid > 0 else "insufficient_data",
        })

new_category = pd.DataFrame(new_cat_rows)

# ── Save validated outputs ────────────────────────────────────────────────────
out_summary  = os.path.join(RESPONSES_DIR, "hallucination_rates_validated.csv")
out_detail   = os.path.join(RESPONSES_DIR, "hallucination_detail_validated.csv")
out_category = os.path.join(RESPONSES_DIR, "hallucination_by_category_validated.csv")
out_report   = os.path.join(RESPONSES_DIR, "validation_report.csv")

new_summary.to_csv(out_summary, index=False)
detail.to_csv(out_detail, index=False)
new_category.to_csv(out_category, index=False)

report_df = pd.DataFrame(results)
report_df.to_csv(out_report, index=False)

# ── Final summary ─────────────────────────────────────────────────────────────
print("\n" + "="*65)
print("  VALIDATION SUMMARY")
print("="*65)

counts = report_df["status"].value_counts().to_dict()
print(f"  ✅ PASS : {counts.get('PASS', 0)}")
print(f"  ❌ FAIL : {counts.get('FAIL', 0)}")
print(f"  ⚠️  WARN : {counts.get('WARN', 0)}")
print(f"  🔧 FIX  : {counts.get('FIX', 0)}")

fails = report_df[report_df["status"] == "FAIL"]
if not fails.empty:
    print(f"\n  Issues to review:")
    for _, r in fails.iterrows():
        print(f"    [{r['check_id']}] {r['check_name']}: {r['detail']}")

print(f"\n  📊 Corrected hallucination rates (after year-leak fix):")
print(f"\n  {'Model':<25} {'Valid Attempts':>15} {'Hallucinated':>14} {'Halluc. Rate':>14} {'Accuracy':>10}")
print(f"  {'-'*80}")
for _, row in new_summary.iterrows():
    h_rate = f"{row['hallucination_rate']:.1%}" if pd.notna(row['hallucination_rate']) else "N/A"
    a_rate = f"{row['accuracy_rate']:.1%}"      if pd.notna(row['accuracy_rate'])      else "N/A"
    print(f"  {row['model']:<25} {int(row['valid_numeric_attempts']):>15} "
          f"{int(row['hallucinated']):>14} {h_rate:>14} {a_rate:>10}")

print(f"\n  📁 Validated files saved:")
print(f"    {out_summary}")
print(f"    {out_detail}")
print(f"    {out_category}")
print(f"    {out_report}")
print("="*65)
