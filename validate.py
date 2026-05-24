import os
import pandas as pd
import json

print("=" * 60)
print("  HEALTHHALLU — PROJECT VALIDATION")
print("=" * 60)

errors   = []
warnings = []
passed   = []

# ─────────────────────────────────────
# CHECK 1 — FOLDER STRUCTURE
# ─────────────────────────────────────
print("\n1. Checking folder structure...")
required_folders = [
    "data", "questions", "responses",
    "scores", "dashboard"
]
for folder in required_folders:
    if os.path.exists(folder):
        passed.append(f"Folder exists: {folder}/")
        print(f"   PASS  {folder}/")
    else:
        errors.append(f"Missing folder: {folder}/")
        print(f"   FAIL  {folder}/ missing")

# ─────────────────────────────────────
# CHECK 2 — REQUIRED FILES
# ─────────────────────────────────────
print("\n2. Checking required files...")
required_files = [
    ".env",
    "data/collect_data.py",
    "data/latest_health_data.csv",
    "questions/generate_questions.py",
    "questions/questions_bank.csv",
    "responses/query_llms.py",
    "responses/llm_responses_latest.csv",
    "scores/score_responses.py",
    "scores/model_metrics.csv",
    "scores/scored_responses_latest.csv",
    "dashboard/app.py",
]
for f in required_files:
    if os.path.exists(f):
        size = os.path.getsize(f)
        passed.append(f"File exists: {f}")
        print(f"   PASS  {f} ({size:,} bytes)")
    else:
        errors.append(f"Missing file: {f}")
        print(f"   FAIL  {f} missing")

# ─────────────────────────────────────
# CHECK 3 — DATA QUALITY
# ─────────────────────────────────────
print("\n3. Checking data quality...")
try:
    df = pd.read_csv("data/latest_health_data.csv")
    rows = len(df)
    if rows >= 80:
        passed.append(f"Data rows: {rows}")
        print(f"   PASS  {rows} data points collected")
    else:
        warnings.append(
            f"Only {rows} data points (need 80+)")
        print(f"   WARN  Only {rows} rows (need 80+)")

    required_cols = [
        "date","source","region",
        "indicator","value","unit"
    ]
    missing_cols = [
        c for c in required_cols
        if c not in df.columns
    ]
    if not missing_cols:
        passed.append("Data columns correct")
        print(f"   PASS  All required columns present")
    else:
        errors.append(
            f"Missing columns: {missing_cols}")
        print(f"   FAIL  Missing: {missing_cols}")

    sources = df["source"].unique().tolist()
    print(f"   INFO  Sources: {sources}")
    regions = df["region"].nunique()
    print(f"   INFO  Regions: {regions}")

except Exception as e:
    errors.append(f"Data file error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# CHECK 4 — QUESTIONS QUALITY
# ─────────────────────────────────────
print("\n4. Checking questions...")
try:
    qdf = pd.read_csv(
        "questions/questions_bank.csv")
    qrows = len(qdf)

    if qrows >= 150:
        passed.append(f"Questions: {qrows}")
        print(f"   PASS  {qrows} questions generated")
    else:
        warnings.append(
            f"Only {qrows} questions (need 150+)")
        print(f"   WARN  Only {qrows} (need 150+)")

    req_cols = [
        "id","category","question",
        "correct_answer","unit","difficulty"
    ]
    miss = [c for c in req_cols
            if c not in qdf.columns]
    if not miss:
        passed.append("Question columns correct")
        print(f"   PASS  All question columns present")
    else:
        errors.append(f"Missing q columns: {miss}")
        print(f"   FAIL  Missing: {miss}")

    cats = qdf["category"].value_counts()
    print(f"   INFO  Categories:")
    for cat, cnt in cats.items():
        print(f"         {cat}: {cnt}")

    diffs = qdf["difficulty"].value_counts()
    print(f"   INFO  Difficulty: {dict(diffs)}")

    if "data_type" in qdf.columns:
        dtypes = qdf["data_type"].value_counts()
        print(f"   INFO  Data types: {dict(dtypes)}")
    else:
        warnings.append("No data_type column")
        print(f"   WARN  No data_type column")

except Exception as e:
    errors.append(f"Questions file error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# CHECK 5 — RESPONSES QUALITY
# ─────────────────────────────────────
print("\n5. Checking LLM responses...")
try:
    rdf = pd.read_csv(
        "responses/llm_responses_latest.csv")
    rrows = len(rdf)
    print(f"   INFO  {rrows} response rows")

    MODEL_NAMES = [
        "LLaMA_3_3_70B",
        "LLaMA_3_1_8B",
        "LLaMA_4_Scout_17B",
        "Qwen3_32B",
        "OpenAI_OSS_120B",
        "Allam_2_7B",
    ]
    found   = []
    missing = []
    for m in MODEL_NAMES:
        if m in rdf.columns:
            errors_count = rdf[m].astype(str)\
                .str.startswith("ERROR").sum()
            empty_count  = rdf[m].astype(str)\
                .isin(["","nan","EMPTY"]).sum()
            answered = rrows - errors_count - empty_count
            found.append(m)
            status = "PASS" if answered > 50 else "WARN"
            print(f"   {status}  {m:<25} "
                  f"answered:{answered} "
                  f"errors:{errors_count}")
        else:
            missing.append(m)
            print(f"   FAIL  {m} NOT IN RESPONSES")

    if missing:
        errors.append(
            f"Missing model columns: {missing}")

except Exception as e:
    errors.append(f"Responses file error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# CHECK 6 — SCORES QUALITY
# ─────────────────────────────────────
print("\n6. Checking scores...")
try:
    mdf = pd.read_csv("scores/model_metrics.csv")
    print(f"   INFO  {len(mdf)} models scored")

    req_cols = [
        "model","accuracy_pct",
        "hallucination_pct","correct"
    ]
    miss = [c for c in req_cols
            if c not in mdf.columns]
    if not miss:
        passed.append("Metrics columns correct")
        print(f"   PASS  All metric columns present")
    else:
        errors.append(
            f"Missing metric cols: {miss}")
        print(f"   FAIL  Missing: {miss}")

    print(f"\n   RESULTS TABLE:")
    print(f"   {'Model':<25} "
          f"{'Accuracy':>10} "
          f"{'Hallucination':>15}")
    print(f"   {'-'*52}")
    for _, row in mdf.sort_values(
            "accuracy_pct",
            ascending=False).iterrows():
        acc = row.get("accuracy_pct", 0)
        hal = row.get("hallucination_pct", 0)
        flag = ("GOOD" if acc >= 30
                else "AVERAGE" if acc >= 15
                else "POOR")
        print(f"   {row['model']:<25} "
              f"{acc:>9.1f}% "
              f"{hal:>14.1f}%  {flag}")

except Exception as e:
    errors.append(f"Metrics file error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# CHECK 7 — DASHBOARD CODE
# ─────────────────────────────────────
print("\n7. Checking dashboard code...")
try:
    with open("dashboard/app.py","r") as f:
        code = f.read()

    checks = {
        "use_container_width":
            ("BAD — replace with width='stretch'",
             True),
        "applymap":
            ("BAD — replace with .map()", True),
        "width=\"stretch\"":
            ("GOOD — correct width usage", False),
        "st.cache_data":
            ("GOOD — caching enabled", False),
        "try:":
            ("GOOD — error handling present", False),
        "st.divider":
            ("GOOD — sections separated", False),
    }

    for term, (msg, is_bad) in checks.items():
        found = term in code
        if is_bad and found:
            errors.append(
                f"Dashboard: {term} found")
            print(f"   FAIL  {term} — {msg}")
        elif is_bad and not found:
            passed.append(
                f"Dashboard: no {term}")
            print(f"   PASS  No {term} found")
        elif not is_bad and found:
            passed.append(
                f"Dashboard: {term} present")
            print(f"   PASS  {term} — {msg}")
        elif not is_bad and not found:
            warnings.append(
                f"Dashboard: missing {term}")
            print(f"   WARN  {term} not found")

except Exception as e:
    errors.append(f"Dashboard check error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# CHECK 8 — ENV FILE
# ─────────────────────────────────────
print("\n8. Checking .env file...")
try:
    with open(".env","r") as f:
        env = f.read()
    if "GROQ_API_KEY" in env:
        key_line = [l for l in env.split("\n")
                    if "GROQ_API_KEY" in l]
        key_val  = key_line[0].split("=")[-1].strip()
        if len(key_val) > 10 and key_val != "your_groq_key_here":
            passed.append("Groq API key set")
            print(f"   PASS  GROQ_API_KEY found "
                  f"({key_val[:8]}...)")
        else:
            errors.append("Groq API key not set")
            print(f"   FAIL  GROQ_API_KEY not set")
    else:
        errors.append("No GROQ_API_KEY in .env")
        print(f"   FAIL  GROQ_API_KEY missing")
except Exception as e:
    errors.append(f".env error: {e}")
    print(f"   FAIL  {e}")

# ─────────────────────────────────────
# FINAL SUMMARY
# ─────────────────────────────────────
print(f"\n{'='*60}")
print(f"  VALIDATION SUMMARY")
print(f"{'='*60}")
print(f"  PASSED:   {len(passed)}")
print(f"  WARNINGS: {len(warnings)}")
print(f"  ERRORS:   {len(errors)}")

if warnings:
    print(f"\n  WARNINGS:")
    for w in warnings:
        print(f"    - {w}")

if errors:
    print(f"\n  ERRORS TO FIX:")
    for e in errors:
        print(f"    - {e}")
    print(f"\n  STATUS: NOT READY FOR SUBMISSION")
else:
    print(f"\n  STATUS: READY FOR SUBMISSION")
    print(f"  Run: streamlit run dashboard/app.py")

print(f"{'='*60}")