
import re
from io import BytesIO
from pathlib import Path
from datetime import datetime, timedelta, timezone
from zoneinfo import ZoneInfo

import pandas as pd
import requests

# ============================================================
# CONFIGURATION
# ============================================================

POINT_ID = 732400
POINT_TYPE_ID = 2

PARAMETERS = [
    "nprolohs",  # Low cloud cover
    "gre000h0",  # Global radiation
    "sre000h0",  # Sunshine duration
    "ods000h0",  # Diffuse radiation
    "tre200h0",  # Air temperature
]

BASE_URL = "https://data.geo.admin.ch/api/stac/v1"
COLLECTION = "ch.meteoschweiz.ogd-local-forecasting"

ROOT = Path(__file__).resolve().parent
DATA_DIR = ROOT / "archive"

session = requests.Session()

# ============================================================
# 1. DISCOVER AVAILABLE FORECAST RUNS
# ============================================================

today = datetime.now(
    ZoneInfo("Europe/Zurich")
).date()

assets_by_run = {}

for day in [today, today - timedelta(days=1)]:

    day_id = day.strftime("%Y%m%d")
    url = (
        f"{BASE_URL}/collections/{COLLECTION}"
        f"/items/{day_id}-ch"
    )

    response = session.get(url, timeout=60)

    if response.status_code == 404:
        continue

    response.raise_for_status()

    for key, asset in response.json()["assets"].items():

        parts = key.split(".")

        if len(parts) < 4:
            continue

        run_id = parts[2]

        if not re.fullmatch(r"\d{12}", run_id):
            continue

        for parameter in PARAMETERS:
            if key.endswith(f".{parameter}.csv"):
                assets_by_run.setdefault(
                    run_id, {}
                )[parameter] = asset

# Only use runs containing all parameters
complete_runs = sorted(
    run_id
    for run_id, assets in assets_by_run.items()
    if all(p in assets for p in PARAMETERS)
)

if not complete_runs:
    raise RuntimeError("No complete forecast runs found.")

selected_runs = complete_runs

print("Available complete runs:", len(complete_runs))
print("Checking runs:", selected_runs)

# ============================================================
# 2. DOWNLOAD AND COMBINE FORECASTS
# ============================================================

for run_id in selected_runs:

    output_dir = (
        DATA_DIR / run_id[:4] / run_id[4:6]
    )
    output_dir.mkdir(parents=True, exist_ok=True)

    output_file = (
        output_dir / f"{run_id}_vilters.csv.gz"
    )

    if output_file.exists():
        print(f"Already archived: {run_id}")
        continue

    combined = None

    for parameter in PARAMETERS:

        asset = assets_by_run[run_id][parameter]

        response = session.get(
            asset["href"], timeout=120
        )
        response.raise_for_status()

        df = pd.read_csv(
            BytesIO(response.content),
            sep=";",
            encoding="latin1",
            usecols=[
                "point_id",
                "point_type_id",
                "Date",
                parameter,
            ]
        )

        # Filter to Vilters
        df = df[
            (df["point_id"] == POINT_ID) &
            (df["point_type_id"] == POINT_TYPE_ID)
        ].copy()

        if df.empty:
            raise RuntimeError(
                f"No Vilters data: {run_id}, {parameter}"
            )

        df["valid_at_utc"] = pd.to_datetime(
            df["Date"].astype(str),
            format="%Y%m%d%H%M",
            utc=True
        )

        df = df[["valid_at_utc", parameter]]

        if combined is None:
            combined = df
        else:
            combined = combined.merge(
                df, on="valid_at_utc", how="outer",
                validate="one_to_one"
            )

    # ========================================================
    # 3. ADD METADATA AND SAVE
    # ========================================================

    retrieved_at = datetime.now(timezone.utc)

    run_time = datetime.strptime(
        run_id, "%Y%m%d%H%M"
    ).replace(tzinfo=timezone.utc)

    combined["run_at_utc"] = run_time.isoformat()
    combined["retrieved_at_utc"] = (
        retrieved_at.isoformat()
    )
    combined["point_id"] = POINT_ID
    combined["point_type_id"] = POINT_TYPE_ID
    combined["source"] = "MeteoSwiss"

    combined = combined.sort_values("valid_at_utc")

    # Temporary file prevents incomplete archives
    temp_file = Path(str(output_file) + ".tmp")

    combined.to_csv(
        temp_file,
        index=False,
        compression="gzip"
    )

    temp_file.replace(output_file)

    print(f"Archived: {run_id}")
    print(f"Records: {len(combined)}")
    print(f"Saved: {output_file}")

print("\nCollection completed.")