import pandas as pd
import requests
import time
import os

# ================================================================
# GROUNDWATER + HISTORICAL WEATHER DATA
# ================================================================

INPUT_FILE = "groundwater_with_tamilnadu_january_final.csv"
OUTPUT_FILE = "groundwater_with_weather.csv"

API_URL = "https://archive-api.open-meteo.com/v1/archive"

print("=" * 70)
print("GROUNDWATER + HISTORICAL WEATHER DATA")
print("=" * 70)

# ================================================================
# LOAD GROUNDWATER DATA
# ================================================================

print("\n===== LOAD GROUNDWATER DATA =====")

if not os.path.exists(INPUT_FILE):
    print(f"ERROR: {INPUT_FILE} not found")
    print("Put this Python file in the same folder as the CSV.")
    exit()

df = pd.read_csv(INPUT_FILE)

print(f"Records loaded: {len(df)}")

# ================================================================
# CHECK REQUIRED COLUMNS
# ================================================================

required_columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

missing = [col for col in required_columns if col not in df.columns]

if missing:
    print("\nERROR: Missing columns:")
    print(missing)
    exit()

# ================================================================
# CLEAN ONLY INVALID BASIC VALUES
# DO NOT DELETE ROWS BECAUSE WEATHER IS MISSING
# ================================================================

print("\n===== PROCESS DATA =====")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["WL_mbgl"] = pd.to_numeric(df["WL_mbgl"], errors="coerce")

before = len(df)

# Only remove rows where the actual groundwater observation
# cannot be used.
df = df.dropna(
    subset=[
        "Latitude",
        "Longitude",
        "Date",
        "WL_mbgl"
    ]
).copy()

after = len(df)

print(f"Rows before cleaning : {before}")
print(f"Rows after cleaning  : {after}")
print(f"Rows removed         : {before - after}")

# ================================================================
# WEATHER FUNCTION
# ================================================================

def get_weather(latitude, longitude, date):

    date_string = date.strftime("%Y-%m-%d")

    params = {
        "latitude": latitude,
        "longitude": longitude,

        "start_date": date_string,
        "end_date": date_string,

        "daily": ",".join([
            "temperature_2m_mean",
            "temperature_2m_max",
            "temperature_2m_min",
            "relative_humidity_2m_mean",
            "relative_humidity_2m_max",
            "relative_humidity_2m_min",
            "precipitation_sum",
            "rain_sum",
            "wind_speed_10m_max",
            "wind_gusts_10m_max",
            "shortwave_radiation_sum",
            "et0_fao_evapotranspiration"
        ]),

        "timezone": "auto",

        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm"
    }

    # Retry 3 times
    for attempt in range(3):

        try:

            response = requests.get(
                API_URL,
                params=params,
                timeout=15
            )

            response.raise_for_status()

            data = response.json()

            if "daily" not in data:
                return None

            daily = data["daily"]

            if len(daily.get("time", [])) == 0:
                return None

            result = {
                "Temperature_C":
                    daily.get("temperature_2m_mean", [None])[0],

                "Temperature_Max_C":
                    daily.get("temperature_2m_max", [None])[0],

                "Temperature_Min_C":
                    daily.get("temperature_2m_min", [None])[0],

                "Humidity_percent":
                    daily.get("relative_humidity_2m_mean", [None])[0],

                "Humidity_Max_percent":
                    daily.get("relative_humidity_2m_max", [None])[0],

                "Humidity_Min_percent":
                    daily.get("relative_humidity_2m_min", [None])[0],

                "Rainfall_mm":
                    daily.get("rain_sum", [None])[0],

                "Precipitation_mm":
                    daily.get("precipitation_sum", [None])[0],

                "WindSpeed_Max_kmh":
                    daily.get("wind_speed_10m_max", [None])[0],

                "WindGust_Max_kmh":
                    daily.get("wind_gusts_10m_max", [None])[0],

                "SolarRadiation_MJ_m2":
                    daily.get("shortwave_radiation_sum", [None])[0],

                "ET0_mm":
                    daily.get("et0_fao_evapotranspiration", [None])[0]
            }

            return result

        except Exception as e:

            if attempt < 2:
                print(
                    f"  Retry {attempt + 1}/2 "
                    f"for ({latitude}, {longitude}, {date_string})"
                )

                time.sleep(2)

            else:
                print(
                    f"  Weather API failed "
                    f"({latitude}, {longitude}, {date_string})"
                )

    return None


# ================================================================
# FETCH WEATHER
# ================================================================

print("\n===== FETCH HISTORICAL WEATHER =====")

weather_columns = [
    "Temperature_C",
    "Temperature_Max_C",
    "Temperature_Min_C",
    "Humidity_percent",
    "Humidity_Max_percent",
    "Humidity_Min_percent",
    "Rainfall_mm",
    "Precipitation_mm",
    "WindSpeed_Max_kmh",
    "WindGust_Max_kmh",
    "SolarRadiation_MJ_m2",
    "ET0_mm"
]

# Create empty weather columns first
for column in weather_columns:
    df[column] = None


total = len(df)

success_count = 0
failed_count = 0

# Cache weather data.
# If several groundwater records have the same
# latitude + longitude + date, we don't call the API again.

weather_cache = {}

for index, row in df.iterrows():

    latitude = row["Latitude"]
    longitude = row["Longitude"]
    date = row["Date"]

    cache_key = (
        round(float(latitude), 4),
        round(float(longitude), 4),
        date.strftime("%Y-%m-%d")
    )

    if cache_key in weather_cache:

        weather = weather_cache[cache_key]

    else:

        weather = get_weather(
            latitude,
            longitude,
            date
        )

        weather_cache[cache_key] = weather

        # Small delay to avoid excessive requests
        time.sleep(0.2)

    if weather is not None:

        for column in weather_columns:
            df.at[index, column] = weather.get(column)

        success_count += 1

    else:

        # IMPORTANT:
        # Keep the groundwater record.
        # Weather values remain empty.
        failed_count += 1

    # Display progress every 10 records
    current = list(df.index).index(index) + 1

    if current % 10 == 0 or current == total:

        print(
            f"[{current}/{total}] "
            f"Success: {success_count} | "
            f"Failed: {failed_count}"
        )


# ================================================================
# SAVE DATASET
# ================================================================

print("\n===== SAVE DATASET =====")

df.to_csv(
    OUTPUT_FILE,
    index=False
)

print(f"Output file: {OUTPUT_FILE}")

print(f"\nOriginal usable groundwater records : {after}")
print(f"Weather successfully fetched        : {success_count}")
print(f"Weather failed                      : {failed_count}")
print(f"Final records                       : {len(df)}")

print("\n===== FINAL COLUMNS =====")

for column in df.columns:
    print(" -", column)

print("\n===== WEATHER DATA SAMPLE =====")

print(
    df[
        [
            "State",
            "District",
            "Village",
            "Date",
            "WL_mbgl",
            "Temperature_C",
            "Humidity_percent",
            "Rainfall_mm"
        ]
    ].head(10).to_string(index=False)
)

print("\n" + "=" * 70)
print("WEATHER DATA PROCESSING FINISHED")
print("=" * 70)