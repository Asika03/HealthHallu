import requests
import pandas as pd
import os

print("Downloading datasets...")
print("=" * 60)

os.makedirs("data/raw", exist_ok=True)

datasets = [
    {
        "name": "Life Expectancy",
        "url": "https://ourworldindata.org/grapher/life-expectancy.csv",
        "file": "data/raw/life_expectancy.csv"
    },
    {
        "name": "Child Mortality",
        "url": "https://ourworldindata.org/grapher/child-mortality.csv",
        "file": "data/raw/child_mortality.csv"
    },
    {
    "name": "Measles Vaccination",
    "url": "https://ourworldindata.org/grapher/share-of-children-vaccinated-against-measles.csv",
    "file": "data/raw/measles_vaccination.csv"
    },
    {
        "name": "Health Expenditure",
        "url": "https://ourworldindata.org/grapher/total-healthcare-expenditure-gdp.csv",
        "file": "data/raw/health_expenditure.csv"
    },
    {
        "name": "Infant Mortality",
        "url": "https://ourworldindata.org/grapher/infant-mortality.csv",
        "file": "data/raw/infant_mortality.csv"
    },
    {
        "name": "Hospital Beds",
        "url": "https://ourworldindata.org/grapher/hospital-beds-per-1000-people.csv",
        "file": "data/raw/hospital_beds.csv"
    },
    {
        "name": "TB Incidence",
        "url": "https://ourworldindata.org/grapher/incidence-of-tuberculosis-sdgs.csv",
        "file": "data/raw/tb_incidence.csv"
    },
    {
        "name": "Maternal Mortality",
        "url": "https://ourworldindata.org/grapher/maternal-mortality.csv",
        "file": "data/raw/maternal_mortality.csv"
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (compatible; research project)",
    "Accept": "text/csv,application/csv,text/plain"
}

downloaded = []
failed     = []

for ds in datasets:
    print(f"\nDownloading {ds['name']}...")
    try:
        r = requests.get(
            ds["url"],
            headers=HEADERS,
            timeout=30
        )
        if r.status_code == 200:
            with open(ds["file"], "wb") as f:
                f.write(r.content)
            # Quick check
            df = pd.read_csv(ds["file"])
            print(f"  PASS  {ds['name']}: "
                  f"{len(df)} rows, "
                  f"columns: {list(df.columns)}")
            downloaded.append(ds["name"])
        else:
            print(f"  FAIL  HTTP {r.status_code}")
            failed.append(ds["name"])
    except Exception as e:
        print(f"  FAIL  {str(e)[:60]}")
        failed.append(ds["name"])

print(f"\n{'='*60}")
print(f"Downloaded: {len(downloaded)}")
print(f"Failed:     {len(failed)}")
if failed:
    print(f"Failed:     {failed}")
print(f"{'='*60}")