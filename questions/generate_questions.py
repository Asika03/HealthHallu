import pandas as pd
from datetime import datetime

print("🤔 HealthHallu — Question Generation (200+ Questions)")
print("=" * 60)

df = pd.read_csv("data/latest_health_data.csv")
today = datetime.today().strftime("%B %d, %Y")
questions = []

def get(region, indicator):
    row = df[(df["region"] == region) & (df["indicator"] == indicator)]
    if not row.empty:
        val = row.iloc[0]["value"]
        src = row.iloc[0]["source"]
        yr  = row.iloc[0].get("reference_year", "")
        return val, src, yr
    return None, None, None

def fmt(n):
    return f"{int(n):,}"

def add(category, subcategory, question,
        correct_answer, answer_display,
        unit, source, difficulty):
    questions.append({
        "id":             f"Q{len(questions)+1:03d}",
        "category":       category,
        "subcategory":    subcategory,
        "question":       question,
        "correct_answer": correct_answer,
        "answer_display": answer_display,
        "unit":           unit,
        "source":         source,
        "difficulty":     difficulty,
        "date_generated": today
    })

# ─────────────────────────────────────
# CATEGORY 1 — Global Disease Stats
# ─────────────────────────────────────
print("\n  Building Category 1 — Global Disease Statistics...")

v,s,y = get("Global","global_total_cases")
if v:
    add("Disease Statistics","Global",
        f"What is the total number of globally reported disease cases as of {today}?",
        int(v), fmt(v), "cases", s, "Medium")
    add("Disease Statistics","Global",
        f"How many people worldwide have been infected by disease in total as of {today}?",
        int(v), fmt(v), "cases", s, "Medium")
    add("Disease Statistics","Global",
        f"According to disease.sh, what is the global cumulative disease case count as of {today}?",
        int(v), fmt(v), "cases", s, "Hard")

v,s,y = get("Global","global_total_deaths")
if v:
    add("Disease Statistics","Global",
        f"How many total deaths have been recorded globally due to disease as of {today}?",
        int(v), fmt(v), "deaths", s, "Medium")
    add("Disease Statistics","Global",
        f"What is the global disease death toll as of {today}?",
        int(v), fmt(v), "deaths", s, "Medium")
    add("Disease Statistics","Global",
        f"How many people have died from disease globally according to disease.sh as of {today}?",
        int(v), fmt(v), "deaths", s, "Hard")

v,s,y = get("Global","global_active_cases")
if v:
    add("Disease Statistics","Global",
        f"What is the current number of active disease cases worldwide as of {today}?",
        int(v), fmt(v), "active cases", s, "Hard")
    add("Disease Statistics","Global",
        f"How many people are currently sick with disease globally as of {today}?",
        int(v), fmt(v), "active cases", s, "Hard")

v,s,y = get("Global","global_recovered")
if v:
    add("Disease Statistics","Global",
        f"How many people have recovered from disease globally as of {today}?",
        int(v), fmt(v), "recovered", s, "Medium")
    add("Disease Statistics","Global",
        f"What is the global disease recovery count as of {today}?",
        int(v), fmt(v), "recovered", s, "Medium")

v,s,y = get("Global","global_critical_cases")
if v:
    add("Disease Statistics","Global",
        f"How many critical disease cases are there globally as of {today}?",
        int(v), fmt(v), "critical cases", s, "Hard")
    add("Disease Statistics","Global",
        f"What is the number of patients in critical condition due to disease worldwide as of {today}?",
        int(v), fmt(v), "critical cases", s, "Hard")

# ─────────────────────────────────────
# CATEGORY 2 — India Disease Stats
# ─────────────────────────────────────
print("  Building Category 2 — India Disease Statistics...")

v,s,y = get("India","total_cases")
if v:
    add("Disease Statistics","India",
        f"What is the total number of disease cases reported in India as of {today}?",
        int(v), fmt(v), "cases", s, "Medium")
    add("Disease Statistics","India",
        f"How many Indians have been infected by disease in total as of {today}?",
        int(v), fmt(v), "cases", s, "Medium")
    add("Disease Statistics","India",
        f"According to disease.sh what is India's cumulative disease case count as of {today}?",
        int(v), fmt(v), "cases", s, "Hard")

v,s,y = get("India","total_deaths")
if v:
    add("Disease Statistics","India",
        f"How many disease-related deaths have been recorded in India as of {today}?",
        int(v), fmt(v), "deaths", s, "Medium")
    add("Disease Statistics","India",
        f"What is India's total disease death count as of {today}?",
        int(v), fmt(v), "deaths", s, "Medium")
    add("Disease Statistics","India",
        f"How many people in India have died from disease according to disease.sh as of {today}?",
        int(v), fmt(v), "deaths", s, "Hard")

v,s,y = get("India","active_cases")
if v:
    add("Disease Statistics","India",
        f"How many active disease cases does India currently have as of {today}?",
        int(v), fmt(v), "active cases", s, "Hard")
    add("Disease Statistics","India",
        f"What is the number of currently active disease patients in India as of {today}?",
        int(v), fmt(v), "active cases", s, "Hard")

v,s,y = get("India","cases_per_million")
if v:
    add("Disease Statistics","India",
        "What is India's total disease case rate per one million population?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")
    add("Disease Statistics","India",
        "How many disease cases per million people has India recorded?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")

v,s,y = get("India","deaths_per_million")
if v:
    add("Disease Statistics","India",
        "What is India's disease death rate per one million population?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")
    add("Disease Statistics","India",
        "How many disease deaths per million people has India recorded?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")

v,s,y = get("India","tests_per_million")
if v:
    add("Disease Statistics","India",
        "How many disease tests per million population has India conducted?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")
    add("Disease Statistics","India",
        "What is India's disease testing rate per one million people?",
        round(float(v),1), str(round(float(v),1)), "per million", s, "Hard")

# ─────────────────────────────────────
# CATEGORY 3 — Country Disease Stats
# ─────────────────────────────────────
print("  Building Category 3 — Country Disease Comparisons...")

for country in ["USA","France","Germany","Brazil",
                "S. Korea","Japan","UK","Russia"]:
    v,s,y = get(country,"total_cases")
    if v:
        add("Disease Statistics","Global Comparison",
            f"What is the total number of disease cases reported in {country} as of {today}?",
            int(v), fmt(v), "cases", s, "Medium")
        add("Disease Statistics","Global Comparison",
            f"How many disease infections have been recorded in {country} in total as of {today}?",
            int(v), fmt(v), "cases", s, "Medium")

    v,s,y = get(country,"total_deaths")
    if v:
        add("Disease Statistics","Global Comparison",
            f"How many disease deaths have been reported in {country} as of {today}?",
            int(v), fmt(v), "deaths", s, "Medium")
        add("Disease Statistics","Global Comparison",
            f"What is the total disease death toll in {country} as of {today}?",
            int(v), fmt(v), "deaths", s, "Medium")

# ─────────────────────────────────────
# CATEGORY 4 — Life Expectancy
# ─────────────────────────────────────
print("  Building Category 4 — Life Expectancy...")

countries_le = [
    ("India","India"),("China","China"),
    ("USA","United States"),("Brazil","Brazil"),
    ("UK","United Kingdom"),("Pakistan","Pakistan"),
    ("Bangladesh","Bangladesh"),
]

for country, label in countries_le:
    v,s,y = get(country,"life_expectancy_wb")
    if v:
        add("Mortality & Life Stats","Life Expectancy",
            f"What is the current life expectancy at birth in {label} according to World Bank ({y})?",
            round(float(v),1), str(round(float(v),1)), "years", s, "Easy")
        add("Mortality & Life Stats","Life Expectancy",
            f"How many years does an average person in {label} live according to World Bank data ({y})?",
            round(float(v),1), str(round(float(v),1)), "years", s, "Easy")
        add("Mortality & Life Stats","Life Expectancy",
            f"According to World Bank, what is {label}'s life expectancy figure for {y}?",
            round(float(v),1), str(round(float(v),1)), "years", s, "Medium")

    v,s,y = get(country,"life_expectancy_both")
    if v:
        add("Mortality & Life Stats","Life Expectancy",
            f"What is the life expectancy at birth in {label} according to WHO data ({y})?",
            round(float(v),1), str(round(float(v),1)), "years", s, "Easy")
        add("Mortality & Life Stats","Life Expectancy",
            f"According to WHO what is the average lifespan in {label} as of {y}?",
            round(float(v),1), str(round(float(v),1)), "years", s, "Medium")

# ─────────────────────────────────────
# CATEGORY 5 — Mortality Rates
# ─────────────────────────────────────
print("  Building Category 5 — Mortality Rates...")

v,s,y = get("India","infant_mortality_per_1000")
if v:
    add("Mortality & Life Stats","Mortality Rates",
        f"What is India's infant mortality rate per 1,000 live births according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"How many infants die per 1,000 live births in India according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"According to World Bank data for {y}, what is India's infant mortality figure?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Hard")

v,s,y = get("India","under5_mortality_per_1000")
if v:
    add("Mortality & Life Stats","Mortality Rates",
        f"What is India's under-5 child mortality rate per 1,000 live births ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"How many children under age 5 die per 1,000 live births in India ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"According to World Bank what is India's under-5 mortality rate for {y}?",
        round(float(v),1), str(round(float(v),1)), "per 1000 live births", s, "Hard")

v,s,y = get("India","maternal_mortality_ratio")
if v:
    add("Mortality & Life Stats","Mortality Rates",
        f"What is India's maternal mortality ratio per 100,000 live births according to WHO ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 100,000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"How many mothers die per 100,000 live births in India according to WHO ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 100,000 live births", s, "Medium")
    add("Mortality & Life Stats","Mortality Rates",
        f"According to WHO data for {y} what is India's maternal death ratio?",
        round(float(v),1), str(round(float(v),1)), "per 100,000 live births", s, "Hard")

for country in ["China","USA","Brazil","Bangladesh"]:
    v,s,y = get(country,"infant_mortality_rate")
    if v:
        add("Mortality & Life Stats","Mortality Rates",
            f"What is the infant mortality rate in {country} according to WHO ({y})?",
            round(float(v),1), str(round(float(v),1)), "per 1000", s, "Medium")
        add("Mortality & Life Stats","Mortality Rates",
            f"How many infants per 1,000 live births die in {country} according to WHO ({y})?",
            round(float(v),1), str(round(float(v),1)), "per 1000", s, "Medium")

    v,s,y = get(country,"maternal_mortality_ratio")
    if v:
        add("Mortality & Life Stats","Mortality Rates",
            f"What is the maternal mortality ratio in {country} according to WHO ({y})?",
            round(float(v),1), str(round(float(v),1)), "per 100,000", s, "Medium")

# ─────────────────────────────────────
# CATEGORY 6 — Healthcare Infrastructure
# ─────────────────────────────────────
print("  Building Category 6 — Healthcare Infrastructure...")

for country in ["India","China","USA","UK","Pakistan"]:
    v,s,y = get(country,"hospital_beds_per_1000")
    if v:
        add("Healthcare Infrastructure","Hospital Resources",
            f"How many hospital beds per 1,000 population does {country} have according to World Bank ({y})?",
            round(float(v),2), str(round(float(v),2)), "beds per 1000", s, "Hard")
        add("Healthcare Infrastructure","Hospital Resources",
            f"What is {country}'s hospital bed density per 1,000 people according to World Bank ({y})?",
            round(float(v),2), str(round(float(v),2)), "beds per 1000", s, "Hard")
        add("Healthcare Infrastructure","Hospital Resources",
            f"According to World Bank data for {y} how many hospital beds per 1,000 does {country} have?",
            round(float(v),2), str(round(float(v),2)), "beds per 1000", s, "Hard")

v,s,y = get("India","physicians_per_1000")
if v:
    add("Healthcare Infrastructure","Medical Workforce",
        f"What is the number of physicians per 1,000 people in India according to World Bank ({y})?",
        round(float(v),3), str(round(float(v),3)), "per 1000 people", s, "Hard")
    add("Healthcare Infrastructure","Medical Workforce",
        f"How many doctors per 1,000 population does India have according to World Bank ({y})?",
        round(float(v),3), str(round(float(v),3)), "per 1000 people", s, "Hard")
    add("Healthcare Infrastructure","Medical Workforce",
        f"According to World Bank what is India's physician density per 1,000 people for {y}?",
        round(float(v),3), str(round(float(v),3)), "per 1000 people", s, "Hard")

v,s,y = get("India","health_expenditure_pct_gdp")
if v:
    add("Healthcare Infrastructure","Health Spending",
        f"What percentage of its GDP does India spend on healthcare according to World Bank ({y})?",
        round(float(v),2), str(round(float(v),2)), "% of GDP", s, "Medium")
    add("Healthcare Infrastructure","Health Spending",
        f"What is India's healthcare expenditure as a percentage of GDP according to World Bank ({y})?",
        round(float(v),2), str(round(float(v),2)), "% of GDP", s, "Medium")
    add("Healthcare Infrastructure","Health Spending",
        f"According to World Bank for {y} how much of India's GDP goes to health spending?",
        round(float(v),2), str(round(float(v),2)), "% of GDP", s, "Hard")

v,s,y = get("USA","health_expenditure_pct_gdp")
if v:
    add("Healthcare Infrastructure","Health Spending",
        f"What percentage of its GDP does the USA spend on healthcare according to World Bank ({y})?",
        round(float(v),2), str(round(float(v),2)), "% of GDP", s, "Medium")
    add("Healthcare Infrastructure","Health Spending",
        f"What is the USA's health expenditure as a share of GDP according to World Bank ({y})?",
        round(float(v),2), str(round(float(v),2)), "% of GDP", s, "Medium")

v,s,y = get("India","tb_incidence_per_100k")
if v:
    add("Healthcare Infrastructure","Disease Burden",
        f"What is India's tuberculosis incidence rate per 100,000 population according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 100,000", s, "Hard")
    add("Healthcare Infrastructure","Disease Burden",
        f"How many new TB cases per 100,000 people does India report according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "per 100,000", s, "Hard")
    add("Healthcare Infrastructure","Disease Burden",
        f"According to World Bank what is India's TB burden per 100,000 people for {y}?",
        round(float(v),1), str(round(float(v),1)), "per 100,000", s, "Hard")

# ─────────────────────────────────────
# CATEGORY 7 — Vaccination
# ─────────────────────────────────────
print("  Building Category 7 — Vaccination...")

for country, label in [
    ("India","India"),
    ("China","China"),
    ("Bangladesh","Bangladesh"),
]:
    v,s,y = get(country,"measles_vaccination_pct")
    if v:
        add("Vaccination & Prevention","Coverage Rates",
            f"What percentage of children in {label} are vaccinated against measles according to World Bank ({y})?",
            round(float(v),1), str(round(float(v),1)), "percentage", s, "Medium")
        add("Vaccination & Prevention","Coverage Rates",
            f"What is {label}'s measles immunization coverage rate among children according to World Bank ({y})?",
            round(float(v),1), str(round(float(v),1)), "percentage", s, "Medium")
        add("Vaccination & Prevention","Coverage Rates",
            f"According to World Bank for {y} what is {label}'s measles vaccination coverage?",
            round(float(v),1), str(round(float(v),1)), "percentage", s, "Hard")

v,s,y = get("India","dpt_vaccination_pct")
if v:
    add("Vaccination & Prevention","Coverage Rates",
        f"What is the DPT vaccination coverage rate among children in India according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "percentage", s, "Hard")
    add("Vaccination & Prevention","Coverage Rates",
        f"What percentage of Indian children receive the DPT vaccine according to World Bank ({y})?",
        round(float(v),1), str(round(float(v),1)), "percentage", s, "Hard")
    add("Vaccination & Prevention","Coverage Rates",
        f"According to World Bank for {y} what is India's DPT immunization rate?",
        round(float(v),1), str(round(float(v),1)), "percentage", s, "Hard")

# ─────────────────────────────────────
# CATEGORY 8 — India vs Global
# ─────────────────────────────────────
print("  Building Category 8 — India vs Global Comparisons...")

ind_beds,_,_ = get("India","hospital_beds_per_1000")
chn_beds,_,_ = get("China","hospital_beds_per_1000")
usa_beds,_,_ = get("USA","hospital_beds_per_1000")
uk_beds,_,_  = get("UK","hospital_beds_per_1000")
pak_beds,_,_ = get("Pakistan","hospital_beds_per_1000")

pairs_beds = [
    ("China",   chn_beds, "China"),
    ("USA",     usa_beds, "USA"),
    ("UK",      uk_beds,  "UK"),
    ("Pakistan",pak_beds, "India"),
]
questions_beds = [
    "Which country has more hospital beds per 1,000 population — India or {c}?",
    "Between India and {c} which has higher hospital bed density per 1,000 people?",
    "Does India or {c} have more hospital beds available per 1,000 population?",
]
for c, cv, winner in pairs_beds:
    if cv and ind_beds:
        w = winner if winner != "India" else ("India" if ind_beds > cv else c)
        for q_tmpl in questions_beds:
            add("India vs Global","Infrastructure",
                q_tmpl.format(c=c),
                w, f"{c} ({cv}) vs India ({ind_beds})",
                "country name", "World Bank", "Easy")

ind_le,_,_ = get("India","life_expectancy_wb")
pairs_le = [
    ("China",      get("China","life_expectancy_wb")[0],      "China"),
    ("USA",        get("USA","life_expectancy_wb")[0],        "USA"),
    ("UK",         get("UK","life_expectancy_wb")[0],         "UK"),
    ("Pakistan",   get("Pakistan","life_expectancy_wb")[0],   "India"),
    ("Bangladesh", get("Bangladesh","life_expectancy_wb")[0], "Bangladesh"),
]
questions_le = [
    "Which country has higher life expectancy — India or {c}?",
    "Between India and {c} which country has a longer average lifespan?",
    "Does India or {c} have a higher life expectancy at birth?",
]
for c, cv, winner in pairs_le:
    if cv and ind_le:
        w = winner if winner != "India" else ("India" if ind_le > cv else c)
        for q_tmpl in questions_le:
            add("India vs Global","Life Expectancy",
                q_tmpl.format(c=c),
                w, f"{c} ({cv}) vs India ({ind_le})",
                "country name", "World Bank", "Easy")

ind_im,_,_ = get("India","infant_mortality_per_1000")
pairs_im = [
    ("China", get("China","infant_mortality_rate")[0]),
    ("USA",   get("USA","infant_mortality_rate")[0]),
]
questions_im = [
    "Which country has a lower infant mortality rate — India or {c}?",
    "Between India and {c} which has fewer infant deaths per 1,000 live births?",
    "Does India or {c} have a better infant survival rate?",
]
for c, cv in pairs_im:
    if cv and ind_im:
        winner = c if cv < ind_im else "India"
        for q_tmpl in questions_im:
            add("India vs Global","Mortality",
                q_tmpl.format(c=c),
                winner, f"{c} ({cv}) vs India ({ind_im})",
                "country name", "WHO/World Bank", "Medium")

# ─────────────────────────────────────
# CATEGORY 9 — Tricky Hallucination
# These are designed to confuse LLMs
# ─────────────────────────────────────
print("  Building Category 9 — Hallucination Trap Questions...")

v,s,y = get("India","life_expectancy_wb")
if v:
    add("Hallucination Traps","Temporal",
        "Is India's current life expectancy above or below 70 years according to World Bank?",
        "Above 70" if v > 70 else "Below 70",
        f"{'Above 70' if v > 70 else 'Below 70'} — actual value: {v}",
        "above/below 70", s, "Easy")
    add("Hallucination Traps","Temporal",
        "Has India's life expectancy crossed 75 years yet according to World Bank latest data?",
        "No" if v < 75 else "Yes",
        f"{'No' if v < 75 else 'Yes'} — actual value: {round(float(v),1)}",
        "yes/no", s, "Medium")

v,s,y = get("India","measles_vaccination_pct")
if v:
    add("Hallucination Traps","Factual",
        "Has India achieved above 90% measles vaccination coverage according to World Bank?",
        "Yes" if v > 90 else "No",
        f"{'Yes' if v > 90 else 'No'} — actual value: {v}%",
        "yes/no", s, "Easy")

v,s,y = get("India","tb_incidence_per_100k")
if v:
    add("Hallucination Traps","Factual",
        "Does India have more than 100 TB cases per 100,000 population according to World Bank?",
        "Yes" if v > 100 else "No",
        f"{'Yes' if v > 100 else 'No'} — actual: {v} per 100,000",
        "yes/no", s, "Medium")

ind_le,_,_ = get("India","life_expectancy_wb")
pak_le,_,_ = get("Pakistan","life_expectancy_wb")
if ind_le and pak_le:
    add("Hallucination Traps","Comparison",
        "Does India have higher life expectancy than Pakistan according to World Bank?",
        "Yes" if ind_le > pak_le else "No",
        f"India ({ind_le}) vs Pakistan ({pak_le})",
        "yes/no", s, "Easy")

ind_beds,_,_ = get("India","hospital_beds_per_1000")
chn_beds,_,_ = get("China","hospital_beds_per_1000")
if ind_beds and chn_beds:
    add("Hallucination Traps","Comparison",
        "Does India have more hospital beds per 1,000 people than China?",
        "No" if ind_beds < chn_beds else "Yes",
        f"India ({ind_beds}) vs China ({chn_beds})",
        "yes/no", s, "Easy")

v,s,y = get("India","hospital_beds_per_1000")
if v:
    add("Hallucination Traps","Numerical",
        "Does India have more than 2 hospital beds per 1,000 population?",
        "No" if v < 2 else "Yes",
        f"{'No' if v < 2 else 'Yes'} — actual: {v}",
        "yes/no", s, "Medium")
    add("Hallucination Traps","Numerical",
        "Is India's hospital bed density above 3 per 1,000 population?",
        "No" if v < 3 else "Yes",
        f"{'No' if v < 3 else 'Yes'} — actual: {v}",
        "yes/no", s, "Medium")

v,s,y = get("USA","health_expenditure_pct_gdp")
if v:
    add("Hallucination Traps","Numerical",
        "Does the USA spend more than 15% of its GDP on healthcare?",
        "Yes" if v > 15 else "No",
        f"{'Yes' if v > 15 else 'No'} — actual: {round(float(v),2)}%",
        "yes/no", s, "Medium")

v,s,y = get("India","health_expenditure_pct_gdp")
if v:
    add("Hallucination Traps","Numerical",
        "Does India spend more than 5% of its GDP on healthcare?",
        "No" if v < 5 else "Yes",
        f"{'No' if v < 5 else 'Yes'} — actual: {round(float(v),2)}%",
        "yes/no", s, "Medium")

v,s,y = get("India","infant_mortality_per_1000")
if v:
    add("Hallucination Traps","Numerical",
        "Is India's infant mortality rate below 30 per 1,000 live births according to World Bank?",
        "Yes" if v < 30 else "No",
        f"{'Yes' if v < 30 else 'No'} — actual: {v}",
        "yes/no", s, "Medium")

ind_im,_,_ = get("India","infant_mortality_per_1000")
usa_im,_,_ = get("USA","infant_mortality_rate")
if ind_im and usa_im:
    add("Hallucination Traps","Comparison",
        "Is India's infant mortality rate higher than USA's?",
        "Yes" if ind_im > usa_im else "No",
        f"India ({ind_im}) vs USA ({usa_im})",
        "yes/no", s, "Medium")

# ─────────────────────────────────────
# CATEGORY 10 — Ranking Questions
# ─────────────────────────────────────
print("  Building Category 10 — Ranking Questions...")

country_cases = {}
for c in ["USA","India","France","Germany","Brazil",
          "S. Korea","Japan","UK","Russia"]:
    v,s,y = get(c,"total_cases")
    if v:
        country_cases[c] = int(v)

if country_cases:
    sorted_countries = sorted(country_cases.items(),
                              key=lambda x: x[1], reverse=True)
    top1 = sorted_countries[0][0]
    top2 = sorted_countries[1][0]
    top3 = sorted_countries[2][0]

    add("Ranking Questions","Disease Cases",
        f"Which country has the highest total disease case count as of {today}?",
        top1, f"{top1} with {fmt(country_cases[top1])} cases",
        "country name", "disease.sh", "Medium")

    add("Ranking Questions","Disease Cases",
        f"Which country ranks second in total disease cases globally as of {today}?",
        top2, f"{top2} with {fmt(country_cases[top2])} cases",
        "country name", "disease.sh", "Hard")

    add("Ranking Questions","Disease Cases",
        f"Which country ranks third in total disease cases globally as of {today}?",
        top3, f"{top3} with {fmt(country_cases[top3])} cases",
        "country name", "disease.sh", "Hard")

    add("Ranking Questions","Disease Cases",
        f"Which country among USA, India, Brazil has the most disease cases as of {today}?",
        top1 if top1 in ["USA","India","Brazil"] else "USA",
        f"Based on: USA={fmt(country_cases.get('USA',0))}, "
        f"India={fmt(country_cases.get('India',0))}, "
        f"Brazil={fmt(country_cases.get('Brazil',0))}",
        "country name", "disease.sh", "Medium")

    add("Ranking Questions","Disease Cases",
        f"Between France and Germany which country has more total disease cases as of {today}?",
        "France" if country_cases.get("France",0) > country_cases.get("Germany",0) else "Germany",
        f"France={fmt(country_cases.get('France',0))}, "
        f"Germany={fmt(country_cases.get('Germany',0))}",
        "country name", "disease.sh", "Medium")

    add("Ranking Questions","Disease Cases",
        f"Between UK and Russia which country has more total disease cases as of {today}?",
        "UK" if country_cases.get("UK",0) > country_cases.get("Russia",0) else "Russia",
        f"UK={fmt(country_cases.get('UK',0))}, "
        f"Russia={fmt(country_cases.get('Russia',0))}",
        "country name", "disease.sh", "Medium")

country_deaths = {}
for c in ["USA","India","Brazil","UK","Russia"]:
    v,s,y = get(c,"total_deaths")
    if v:
        country_deaths[c] = int(v)

if country_deaths:
    sorted_deaths = sorted(country_deaths.items(),
                           key=lambda x: x[1], reverse=True)
    add("Ranking Questions","Disease Deaths",
        f"Which country has the highest disease death toll among USA, India, Brazil, UK, Russia as of {today}?",
        sorted_deaths[0][0],
        f"{sorted_deaths[0][0]} with {fmt(sorted_deaths[0][1])} deaths",
        "country name", "disease.sh", "Medium")

    add("Ranking Questions","Disease Deaths",
        f"Between India and Brazil which country has more disease deaths as of {today}?",
        "India" if country_deaths.get("India",0) > country_deaths.get("Brazil",0) else "Brazil",
        f"India={fmt(country_deaths.get('India',0))}, "
        f"Brazil={fmt(country_deaths.get('Brazil',0))}",
        "country name", "disease.sh", "Medium")

beds_rank = {}
for c in ["India","China","USA","UK","Pakistan"]:
    v,_,_ = get(c,"hospital_beds_per_1000")
    if v: beds_rank[c] = float(v)

if beds_rank:
    sorted_beds = sorted(beds_rank.items(),
                         key=lambda x: x[1], reverse=True)
    add("Ranking Questions","Healthcare Infrastructure",
        "Which country among India, China, USA, UK, Pakistan has the most hospital beds per 1,000 population?",
        sorted_beds[0][0],
        f"{sorted_beds[0][0]} with {sorted_beds[0][1]} beds per 1000",
        "country name", "World Bank", "Hard")

    add("Ranking Questions","Healthcare Infrastructure",
        "Which country among India, China, USA, UK, Pakistan has the fewest hospital beds per 1,000 population?",
        sorted_beds[-1][0],
        f"{sorted_beds[-1][0]} with {sorted_beds[-1][1]} beds per 1000",
        "country name", "World Bank", "Hard")

le_rank = {}
for c in ["India","China","USA","UK","Pakistan","Bangladesh"]:
    v,_,_ = get(c,"life_expectancy_wb")
    if v: le_rank[c] = float(v)

if le_rank:
    sorted_le = sorted(le_rank.items(),
                       key=lambda x: x[1], reverse=True)
    add("Ranking Questions","Life Expectancy",
        "Which country among India, China, USA, UK, Pakistan, Bangladesh has the highest life expectancy?",
        sorted_le[0][0],
        f"{sorted_le[0][0]} with {sorted_le[0][1]} years",
        "country name", "World Bank", "Medium")

    add("Ranking Questions","Life Expectancy",
        "Which country among India, China, USA, UK, Pakistan, Bangladesh has the lowest life expectancy?",
        sorted_le[-1][0],
        f"{sorted_le[-1][0]} with {sorted_le[-1][1]} years",
        "country name", "World Bank", "Medium")
# ─────────────────────────────────────
# CATEGORY 11 — HISTORICAL QUESTIONS
# Questions LLMs should know from training
# ─────────────────────────────────────
print("  Building Category 11 — Historical Questions...")

def get_hist(region, indicator):
    row = df[(df["region"] == region) &
             (df["indicator"] == indicator)]
    if not row.empty:
        val = row.iloc[0]["value"]
        src = row.iloc[0]["source"]
        yr  = row.iloc[0].get("reference_year","")
        return val, src, yr
    return None, None, None

# India Life Expectancy Historical
v,s,y = get_hist("India","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was India's life expectancy at birth in 2019 according to WHO?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")
    add("Historical Questions","Life Expectancy",
        f"According to WHO data, what was the average lifespan in India in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

v,s,y = get_hist("India","life_expectancy_2020")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was India's life expectancy in 2020 according to WHO data?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

# China Historical
v,s,y = get_hist("China","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was China's life expectancy in 2019 according to WHO?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

v,s,y = get_hist("China","life_expectancy_2020")
if v:
    add("Historical Questions","Life Expectancy",
        f"According to WHO, what was the life expectancy in China in 2020?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

# USA Historical
v,s,y = get_hist("USA","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was the life expectancy in the United States in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

v,s,y = get_hist("USA","life_expectancy_2020")
if v:
    add("Historical Questions","Life Expectancy",
        f"According to WHO what was USA's life expectancy in 2020?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

# Brazil & UK Historical
v,s,y = get_hist("Brazil","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was Brazil's life expectancy in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

v,s,y = get_hist("UK","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was the life expectancy in the United Kingdom in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

v,s,y = get_hist("Pakistan","life_expectancy_2019")
if v:
    add("Historical Questions","Life Expectancy",
        f"What was Pakistan's life expectancy in 2019 according to WHO?",
        round(float(v),1), str(round(float(v),1)),
        "years", s, "Easy")

# Infant Mortality Historical
v,s,y = get_hist("India","infant_mortality_2019")
if v:
    add("Historical Questions","Mortality",
        f"What was India's infant mortality rate per 1000 live births in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "per 1000", s, "Medium")
    add("Historical Questions","Mortality",
        f"How many infants per 1000 live births died in India in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "per 1000", s, "Medium")

v,s,y = get_hist("India","infant_mortality_2020")
if v:
    add("Historical Questions","Mortality",
        f"What was India's infant mortality rate in 2020 according to World Bank?",
        round(float(v),1), str(round(float(v),1)),
        "per 1000", s, "Medium")

v,s,y = get_hist("India","infant_mortality_2021")
if v:
    add("Historical Questions","Mortality",
        f"According to World Bank what was India's infant mortality rate in 2021?",
        round(float(v),1), str(round(float(v),1)),
        "per 1000", s, "Medium")

# Vaccination Historical
v,s,y = get_hist("India","measles_vax_2019")
if v:
    add("Historical Questions","Vaccination",
        f"What was India's measles vaccination coverage among children in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "percentage", s, "Medium")

v,s,y = get_hist("India","measles_vax_2020")
if v:
    add("Historical Questions","Vaccination",
        f"What percentage of Indian children were vaccinated against measles in 2020?",
        round(float(v),1), str(round(float(v),1)),
        "percentage", s, "Medium")

v,s,y = get_hist("India","measles_vax_2021")
if v:
    add("Historical Questions","Vaccination",
        f"According to World Bank what was India's measles vaccination rate in 2021?",
        round(float(v),1), str(round(float(v),1)),
        "percentage", s, "Medium")

# TB Historical
v,s,y = get_hist("India","tb_incidence_2019")
if v:
    add("Historical Questions","Disease Burden",
        f"What was India's tuberculosis incidence rate per 100,000 population in 2019?",
        round(float(v),1), str(round(float(v),1)),
        "per 100k", s, "Hard")

v,s,y = get_hist("India","tb_incidence_2020")
if v:
    add("Historical Questions","Disease Burden",
        f"How many new TB cases per 100,000 people did India report in 2020?",
        round(float(v),1), str(round(float(v),1)),
        "per 100k", s, "Hard")

# Hospital Beds Historical
v,s,y = get_hist("China","hospital_beds_2019")
if v:
    add("Historical Questions","Infrastructure",
        f"How many hospital beds per 1000 population did China have in 2019?",
        round(float(v),2), str(round(float(v),2)),
        "per 1000", s, "Hard")

v,s,y = get_hist("USA","hospital_beds_2019")
if v:
    add("Historical Questions","Infrastructure",
        f"What was the hospital bed density per 1000 people in the USA in 2019?",
        round(float(v),2), str(round(float(v),2)),
        "per 1000", s, "Hard")

v,s,y = get_hist("UK","hospital_beds_2019")
if v:
    add("Historical Questions","Infrastructure",
        f"How many hospital beds per 1000 people did the UK have in 2019?",
        round(float(v),2), str(round(float(v),2)),
        "per 1000", s, "Hard")

# COVID Historical (well-known data)
v,s,y = get_hist("Global","covid_deaths_2020")
if v:
    add("Historical Questions","COVID Historical",
        f"How many deaths were attributed to COVID-19 globally in the year 2020?",
        int(v), f"{int(v):,}",
        "deaths", s, "Medium")

v,s,y = get_hist("Global","covid_deaths_2021")
if v:
    add("Historical Questions","COVID Historical",
        f"What was the global COVID-19 death toll for the year 2021?",
        int(v), f"{int(v):,}",
        "deaths", s, "Medium")

v,s,y = get_hist("India","covid_cases_2021")
if v:
    add("Historical Questions","COVID Historical",
        f"How many total COVID-19 cases did India record by end of 2021?",
        int(v), f"{int(v):,}",
        "cases", s, "Medium")

v,s,y = get_hist("India","covid_deaths_2021")
if v:
    add("Historical Questions","COVID Historical",
        f"What was India's total COVID-19 death count by end of 2021?",
        int(v), f"{int(v):,}",
        "deaths", s, "Medium")

# Also tag existing questions as real-time
# for comparison in scoring
print(f"  ✅ Historical questions added")
# ─────────────────────────────────────
# SAVE
# ─────────────────────────────────────
qdf = pd.DataFrame(questions)
qdf.to_csv("questions/questions_bank.csv", index=False)

print(f"\n{'=' * 60}")
print("  ✅ QUESTION GENERATION COMPLETE")
print(f"{'=' * 60}")
print(f"  Total questions   : {len(questions)}")
print(f"  Categories        :")
for cat, cnt in qdf["category"].value_counts().items():
    print(f"    {cat:<40} : {cnt}")
print(f"  Difficulty split  :")
for diff, cnt in qdf["difficulty"].value_counts().items():
    print(f"    {diff:<10} : {cnt}")
print(f"\n  Saved to: questions/questions_bank.csv")
print(f"{'=' * 60}")
# Tag every question as real-time or historical
def tag_data_type(row):
    if row["category"] == "Historical Questions":
        return "historical"
    elif any(word in row["question"].lower()
             for word in ["2019","2020","2021"]):
        return "historical"
    else:
        return "real-time"

qdf["data_type"] = qdf.apply(tag_data_type, axis=1)

print(f"\n  Data type split:")
print(f"  Real-time:  "
      f"{(qdf['data_type']=='real-time').sum()}")
print(f"  Historical: "
      f"{(qdf['data_type']=='historical').sum()}")