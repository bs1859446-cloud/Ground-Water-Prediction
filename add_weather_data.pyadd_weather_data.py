import pandas as pd
import requests
import time
import os

# ============================================================
# ADD HISTORICAL WEATHER DATA TO GROUNDWATER DATASET
# ============================================================

INPUT_FILE = "groundwater_with_tamilnadu_january_final.csv"
OUTPUT_FILE = "groundwater_with_weather.csv"

API_URL = "https://archive-api.open-meteo.com/v1/archive"

print("=" * 70)
print("GROUNDWATER + HISTORICAL WEATHER DATA")
print("=" * 70)

# ------------------------------------------------------------
# 1. LOAD GROUNDWATER DATA
# ------------------------------------------------------------

print("\n===== LOAD GROUNDWATER DATA =====")

df = pd.read_csv(INPUT_FILE)

print("Records loaded:", len(df))

# ------------------------------------------------------------
# 2. CLEAN COLUMN NAMES
# ------------------------------------------------------------

df.columns = df.columns.str.strip()

if "Latitute" in df.columns:
    df.rename(columns={"Latitute": "Latitude"}, inplace=True)

if "WL(mbgl)" in df.columns:
    df.rename(columns={"WL(mbgl)": "WL_mbgl"}, inplace=True)

required = [
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

for col in required:
    if col not in df.columns:
        print(f"ERROR: Missing column: {col}")
        raise SystemExit

# ------------------------------------------------------------
# 3. PROCESS DATA TYPES
# ------------------------------------------------------------

print("\n===== PROCESS DATA =====")

df["Latitude"] = pd.to_numeric(
    df["Latitude"],
    errors="coerce"
)

df["Longitude"] = pd.to_numeric(
    df["Longitude"],
    errors="coerce"
)

df["WL_mbgl"] = pd.to_numeric(
    df["WL_mbgl"],
    errors="coerce"
)

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
    dayfirst=True
)

# ------------------------------------------------------------
# 4. REMOVE INVALID ROWS
# ------------------------------------------------------------

before = len(df)

df = df.dropna(
    subset=[
        "Latitude",
        "Longitude",
        "Date",
        "WL_mbgl"
    ]
).copy()

print("Rows before cleaning:", before)
print("Rows after cleaning :", len(df))
print("Rows removed        :", before - len(df))

# ------------------------------------------------------------
# 5. WEATHER FUNCTION
# ------------------------------------------------------------

def get_weather(latitude, longitude, date):

    date_string = date.strftime("%Y-%m-%d")

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "start_date": date_string,
        "end_date": date_string,

        "hourly": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "rain,"
            "surface_pressure,"
            "wind_speed_10m"
        ),

        "timezone": "auto",

        "temperature_unit": "celsius",

        "wind_speed_unit": "kmh",

        "precipitation_unit": "mm"
    }

    try:

        response = requests.get(
            API_URL,
            params=params,
            timeout=30
        )

        response.raise_for_status()

        data = response.json()

        if "hourly" not in data:
            return None

        hourly = data["hourly"]

        # Convert hourly values to daily averages/sums
        temperature = hourly.get("temperature_2m", [])
        humidity = hourly.get("relative_humidity_2m", [])
        precipitation = hourly.get("precipitation", [])
        rain = hourly.get("rain", [])
        pressure = hourly.get("surface_pressure", [])
        wind = hourly.get("wind_speed_10m", [])

        result = {
            "Temperature_C": (
                sum(temperature) / len(temperature)
                if temperature else None
            ),

            "Humidity_percent": (
                sum(humidity) / len(humidity)
                if humidity else None
            ),

            "Rainfall_mm": (
                sum(rain)
                if rain else None
            ),

            "Precipitation_mm": (
                sum(precipitation)
                if precipitation else None
            ),

            "Pressure_hPa": (
                sum(pressure) / len(pressure)
                if pressure else None
            ),

            "WindSpeed_kmh": (
                sum(wind) / len(wind)
                if wind else None
            )
        }

        return result

    except Exception as e:

        print(
            f"Weather API error "
            f"({latitude}, {longitude}, {date_string}): {e}"
        )

        return None


# ------------------------------------------------------------
# 6. FETCH WEATHER
# ------------------------------------------------------------

print("\n===== FETCH HISTORICAL WEATHER =====")

weather_results = []

total = len(df)

for index, row in df.iterrows():

    print(
        f"[{index + 1}/{total}] "
        f"{row['State']} | "
        f"{row['District']} | "
        f"{row['Village']} | "
        f"{row['Date'].strftime('%Y-%m-%d')}"
    )

    weather = get_weather(
        row["Latitude"],
        row["Longitude"],
        row["Date"]
    )

    if weather is None:

        weather_results.append({
            "Temperature_C": None,
            "Humidity_percent": None,
            "Rainfall_mm": None,
            "Precipitation_mm": None,
            "Pressure_hPa": None,
            "WindSpeed_kmh": None
        })

    else:

        weather_results.append(weather)

    # Small delay to avoid sending requests too rapidly
    time.sleep(0.1)


# ------------------------------------------------------------
# 7. ADD WEATHER TO DATASET
# ------------------------------------------------------------

print("\n===== MERGE WEATHER DATA =====")

weather_df = pd.DataFrame(weather_results)

weather_df.index = df.index

df = pd.concat(
    [
        df,
        weather_df
    ],
    axis=1
)

# ------------------------------------------------------------
# 8. WEATHER COVERAGE
# ------------------------------------------------------------

print("\n===== WEATHER COVERAGE =====")

weather_columns = [
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Precipitation_mm",
    "Pressure_hPa",
    "WindSpeed_kmh"
]

for col in weather_columns:

    available = df[col].notna().sum()

    print(
        f"{col:<25}: "
        f"{available}/{len(df)}"
    )

# ------------------------------------------------------------
# 9. SAVE
# ------------------------------------------------------------

print("\n===== SAVE DATASET =====")

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Output file:")
print(os.path.abspath(OUTPUT_FILE))

print("\nFinal records:", len(df))

print("\nColumns:")
print(df.columns.tolist())

print("\n" + "=" * 70)
print("WEATHER DATA ADDED SUCCESSFULLY")
print("=" * 70)