import requests
import pandas as pd
from datetime import datetime
import os

print("HealthHallu — Historical Data Collection (2005-2015)")
print("=" * 60)

today    = datetime.today().strftime("%Y-%m-%d")
all_data = []

COUNTRIES = {
    "IND": "India",
    "CHN": "China",
    "USA": "USA",
    "BRA": "Brazil",
    "GBR": "UK",
    "PAK": "Pakistan",
    "BGD": "Bangladesh",
    "NGA": "Nigeria",
    "ZAF": "South Africa",
    "MEX": "Mexico",
}

WB_COUNTRIES = {
    "IN":  "India",
    "CN":  "China",
    "US":  "USA",
    "BR":  "Brazil",
    "GB":  "UK",
    "PK":  "Pakistan",
    "BD":  "Bangladesh",
    "NG":  "Nigeria",
    "ZA":  "South Africa",
    "MX":  "Mexico",
}

YEARS = list(range(2005, 2016))

# ─────────────────────────────────────
# SOURCE 1 — WHO GHO API
# Fetch specific years 2005-2015
# ─────────────────────────────────────
print("\nFetching WHO data (2005-2015)...")

WHO_INDICATORS = {
    "WHOSIS_000001": "life_expectancy_both",
    "WHOSIS_000002": "life_expectancy_male",
    "WHOSIS_000007": "life_expectancy_female",
    "MDG_0000000026": "infant_mortality_rate",
    "MDG_0000000007": "maternal_mortality_ratio",
    "WHOSIS_000015": "healthy_life_expectancy",
}

for code, indicator_name in WHO_INDICATORS.items():
    for country_code, country_name in COUNTRIES.items():
        for year in YEARS:
            try:
                url = (
                    f"https://ghoapi.azureedge.net/api/{code}"
                    f"?$filter=SpatialDim eq '{country_code}'"
                    f" and TimeDim eq {year}"
                )
                resp = requests.get(
                    url, timeout=15).json()
                values = resp.get("value", [])
                if values and values[0].get(
                        "NumericValue"):
                    val = values[0]["NumericValue"]
                    all_data.append({
                        "date":           today,
                        "source":         "WHO GHO",
                        "region":         country_name,
                        "indicator":      indicator_name,
                        "value":          round(float(val), 2),
                        "unit":           "WHO standard",
                        "reference_year": year,
                        "data_type":      "historical"
                    })
                    print(f"  WHO {country_name} "
                          f"{indicator_name} {year}: {val:.2f}")
            except Exception as e:
                pass

# ─────────────────────────────────────
# SOURCE 2 — WORLD BANK API
# Fetch specific years 2005-2015
# ─────────────────────────────────────
print("\nFetching World Bank data (2005-2015)...")

WB_INDICATORS = {
    "SP.DYN.LE00.IN":    "life_expectancy",
    "SP.DYN.IMRT.IN":    "infant_mortality_per_1000",
    "SH.DYN.MORT":       "under5_mortality_per_1000",
    "SH.STA.MMRT":       "maternal_mortality_ratio",
    "SH.MED.BEDS.ZS":    "hospital_beds_per_1000",
    "SH.MED.PHYS.ZS":    "physicians_per_1000",
    "SH.XPD.CHEX.GD.ZS": "health_expenditure_pct_gdp",
    "SH.IMM.MEAS":       "measles_vaccination_pct",
    "SH.IMM.IDPT":       "dpt_vaccination_pct",
    "SH.TBS.INCD":       "tb_incidence_per_100k",
    "SH.HIV.INCD.ZS":    "hiv_incidence_per_1000",
    "SP.DYN.TFRT.IN":    "fertility_rate",
    "SH.XPD.PUBL.GD.ZS": "public_health_expenditure_pct_gdp",
}

for wb_code, indicator_name in WB_INDICATORS.items():
    for country_code, country_name in WB_COUNTRIES.items():
        try:
            url = (
                f"https://api.worldbank.org/v2/country"
                f"/{country_code}/indicator/{wb_code}"
                f"?format=json&date=2005:2015&per_page=20"
            )
            resp = requests.get(
                url, timeout=15).json()
            if len(resp) > 1 and resp[1]:
                for entry in resp[1]:
                    if entry.get("value") and entry.get("date"):
                        year = int(entry["date"])
                        if 2005 <= year <= 2015:
                            all_data.append({
                                "date":      today,
                                "source":    "World Bank",
                                "region":    country_name,
                                "indicator": indicator_name,
                                "value":     round(
                                    float(entry["value"]), 3),
                                "unit":      "WB standard",
                                "reference_year": year,
                                "data_type": "historical"
                            })
                            print(f"  WB {country_name} "
                                  f"{indicator_name} "
                                  f"{year}: {entry['value']}")
        except Exception as e:
            pass

# ─────────────────────────────────────
# SOURCE 3 — HARDCODED VERIFIED DATA
# From WHO/UNICEF/World Bank reports
# ─────────────────────────────────────
print("\nAdding hardcoded verified data...")

verified = [
    # India Life Expectancy
    {"region":"India","indicator":"life_expectancy_verified","value":63.5,"reference_year":2005,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":64.4,"reference_year":2006,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":65.2,"reference_year":2007,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":66.0,"reference_year":2008,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":66.8,"reference_year":2009,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":67.5,"reference_year":2010,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":68.0,"reference_year":2011,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":68.5,"reference_year":2012,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":68.8,"reference_year":2013,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":69.1,"reference_year":2014,"source":"WHO Verified"},
    {"region":"India","indicator":"life_expectancy_verified","value":69.4,"reference_year":2015,"source":"WHO Verified"},
    # China Life Expectancy
    {"region":"China","indicator":"life_expectancy_verified","value":73.2,"reference_year":2005,"source":"WHO Verified"},
    {"region":"China","indicator":"life_expectancy_verified","value":74.0,"reference_year":2007,"source":"WHO Verified"},
    {"region":"China","indicator":"life_expectancy_verified","value":74.8,"reference_year":2010,"source":"WHO Verified"},
    {"region":"China","indicator":"life_expectancy_verified","value":75.7,"reference_year":2013,"source":"WHO Verified"},
    {"region":"China","indicator":"life_expectancy_verified","value":76.1,"reference_year":2015,"source":"WHO Verified"},
    # USA Life Expectancy
    {"region":"USA","indicator":"life_expectancy_verified","value":77.4,"reference_year":2005,"source":"WHO Verified"},
    {"region":"USA","indicator":"life_expectancy_verified","value":77.8,"reference_year":2007,"source":"WHO Verified"},
    {"region":"USA","indicator":"life_expectancy_verified","value":78.5,"reference_year":2010,"source":"WHO Verified"},
    {"region":"USA","indicator":"life_expectancy_verified","value":78.8,"reference_year":2013,"source":"WHO Verified"},
    {"region":"USA","indicator":"life_expectancy_verified","value":78.7,"reference_year":2015,"source":"WHO Verified"},
    # India Infant Mortality
    {"region":"India","indicator":"infant_mortality_verified","value":56.0,"reference_year":2005,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":53.0,"reference_year":2006,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":50.0,"reference_year":2007,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":47.0,"reference_year":2008,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":44.0,"reference_year":2009,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":41.0,"reference_year":2010,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":39.0,"reference_year":2011,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":37.0,"reference_year":2012,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":35.0,"reference_year":2013,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":34.0,"reference_year":2014,"source":"UNICEF Verified"},
    {"region":"India","indicator":"infant_mortality_verified","value":33.0,"reference_year":2015,"source":"UNICEF Verified"},
    # India Measles Vaccination
    {"region":"India","indicator":"measles_vaccination_verified","value":56.0,"reference_year":2005,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":59.0,"reference_year":2006,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":67.0,"reference_year":2007,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":70.0,"reference_year":2008,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":71.0,"reference_year":2009,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":74.0,"reference_year":2010,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":74.0,"reference_year":2011,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":74.0,"reference_year":2012,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":83.0,"reference_year":2013,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":84.0,"reference_year":2014,"source":"WHO Verified"},
    {"region":"India","indicator":"measles_vaccination_verified","value":87.0,"reference_year":2015,"source":"WHO Verified"},
    # India TB Incidence
    {"region":"India","indicator":"tb_incidence_verified","value":283.0,"reference_year":2005,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":275.0,"reference_year":2006,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":265.0,"reference_year":2007,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":255.0,"reference_year":2008,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":245.0,"reference_year":2009,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":236.0,"reference_year":2010,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":226.0,"reference_year":2011,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":217.0,"reference_year":2012,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":209.0,"reference_year":2013,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":200.0,"reference_year":2014,"source":"WHO Verified"},
    {"region":"India","indicator":"tb_incidence_verified","value":193.0,"reference_year":2015,"source":"WHO Verified"},
    # India Hospital Beds
    {"region":"India","indicator":"hospital_beds_verified","value":0.7,"reference_year":2005,"source":"WB Verified"},
    {"region":"India","indicator":"hospital_beds_verified","value":0.7,"reference_year":2010,"source":"WB Verified"},
    {"region":"India","indicator":"hospital_beds_verified","value":0.7,"reference_year":2015,"source":"WB Verified"},
    {"region":"China","indicator":"hospital_beds_verified","value":2.4,"reference_year":2005,"source":"WB Verified"},
    {"region":"China","indicator":"hospital_beds_verified","value":3.6,"reference_year":2010,"source":"WB Verified"},
    {"region":"China","indicator":"hospital_beds_verified","value":4.2,"reference_year":2015,"source":"WB Verified"},
    {"region":"USA","indicator":"hospital_beds_verified","value":3.1,"reference_year":2005,"source":"WB Verified"},
    {"region":"USA","indicator":"hospital_beds_verified","value":3.0,"reference_year":2010,"source":"WB Verified"},
    {"region":"USA","indicator":"hospital_beds_verified","value":2.9,"reference_year":2015,"source":"WB Verified"},
    # Health Expenditure
    {"region":"India","indicator":"health_expenditure_pct_gdp","value":4.2,"reference_year":2005,"source":"WB Verified"},
    {"region":"India","indicator":"health_expenditure_pct_gdp","value":4.0,"reference_year":2010,"source":"WB Verified"},
    {"region":"India","indicator":"health_expenditure_pct_gdp","value":3.9,"reference_year":2015,"source":"WB Verified"},
    {"region":"USA","indicator":"health_expenditure_pct_gdp","value":15.2,"reference_year":2005,"source":"WB Verified"},
    {"region":"USA","indicator":"health_expenditure_pct_gdp","value":16.4,"reference_year":2010,"source":"WB Verified"},
    {"region":"USA","indicator":"health_expenditure_pct_gdp","value":16.8,"reference_year":2015,"source":"WB Verified"},
]

for item in verified:
    all_data.append({
        "date":           today,
        "source":         item["source"],
        "region":         item["region"],
        "indicator":      item["indicator"],
        "value":          item["value"],
        "unit":           "verified",
        "reference_year": item["reference_year"],
        "data_type":      "historical"
    })

print(f"  Added {len(verified)} hardcoded verified points")

# ─────────────────────────────────────
# SAVE
# ─────────────────────────────────────
df = pd.DataFrame(all_data)
df = df.drop_duplicates(
    subset=["region","indicator","reference_year"])

os.makedirs("data", exist_ok=True)
df.to_csv("data/latest_health_data.csv", index=False)
df.to_csv(
    f"data/health_data_{today}.csv", index=False)

print(f"\n{'='*60}")
print(f"  DATA COLLECTION COMPLETE")
print(f"{'='*60}")
print(f"  Total data points : {len(df)}")
print(f"  Sources           : {df['source'].nunique()}")
print(f"  Regions           : {df['region'].nunique()}")
print(f"  Years covered     : "
      f"{df['reference_year'].min()} - "
      f"{df['reference_year'].max()}")
print(f"  Indicators        : {df['indicator'].nunique()}")
print(f"  Saved to          : data/latest_health_data.csv")
print(f"{'='*60}")