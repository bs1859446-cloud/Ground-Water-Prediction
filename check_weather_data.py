import pandas as pd
import os

# ================================================================
# CHECK GROUNDWATER + WEATHER DATA
# ================================================================

FILE = "groundwater_with_weather.csv"

print("=" * 70)
print("GROUNDWATER + WEATHER DATA CHECK")
print("=" * 70)

# ================================================================
# LOAD FILE
# ================================================================

if not os.path.exists(FILE):
    print(f"\nERROR: {FILE} not found.")
    print("Make sure the weather collection completed successfully.")
    exit()

df = pd.read_csv(FILE)

print("\n===== BASIC INFORMATION =====")
print(f"File              : {FILE}")
print(f"Total records     : {len(df)}")
print(f"Total columns     : {len(df.columns)}")

# ================================================================
# COLUMNS
# ================================================================

print("\n===== COLUMNS =====")

for i, column in enumerate(df.columns, 1):
    print(f"{i:2}. {column}")

# ================================================================
# REQUIRED WEATHER COLUMNS
# ================================================================

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

print("\n===== WEATHER DATA CHECK =====")

for column in weather_columns:

    if column not in df.columns:
        print(f"{column:30} NOT FOUND")
        continue

    numeric = pd.to_numeric(df[column], errors="coerce")

    valid = numeric.notna().sum()
    missing = numeric.isna().sum()

    print(
        f"{column:30} "
        f"Valid: {valid:4} | "
        f"Missing: {missing:4}"
    )

# ================================================================
# GROUNDWATER TARGET
# ================================================================

print("\n===== GROUNDWATER TARGET =====")

if "WL_mbgl" in df.columns:

    wl = pd.to_numeric(df["WL_mbgl"], errors="coerce")

    print(f"Valid WL values    : {wl.notna().sum()}")
    print(f"Missing WL values  : {wl.isna().sum()}")

    print("\nGroundwater level statistics:")
    print(wl.describe())

else:
    print("ERROR: WL_mbgl column not found.")

# ================================================================
# DATE CHECK
# ================================================================

print("\n===== DATE CHECK =====")

if "Date" in df.columns:

    dates = pd.to_datetime(
        df["Date"],
        errors="coerce"
    )

    print(f"Valid dates        : {dates.notna().sum()}")
    print(f"Missing dates      : {dates.isna().sum()}")

    if dates.notna().any():
        print(f"Earliest date      : {dates.min().date()}")
        print(f"Latest date        : {dates.max().date()}")

else:
    print("ERROR: Date column not found.")

# ================================================================
# LOCATION CHECK
# ================================================================

print("\n===== LOCATION CHECK =====")

for column in ["Latitude", "Longitude"]:

    if column in df.columns:

        values = pd.to_numeric(
            df[column],
            errors="coerce"
        )

        print(
            f"{column:15} "
            f"Valid: {values.notna().sum()} | "
            f"Missing: {values.isna().sum()}"
        )

# ================================================================
# STATE COUNTS
# ================================================================

print("\n===== STATE COUNTS =====")

if "State" in df.columns:

    print(
        df["State"]
        .value_counts()
        .to_string()
    )

# ================================================================
# WEATHER STATISTICS
# ================================================================

print("\n===== WEATHER STATISTICS =====")

available_weather = [
    column
    for column in weather_columns
    if column in df.columns
]

if available_weather:

    print(
        df[available_weather]
        .apply(pd.to_numeric, errors="coerce")
        .describe()
        .T
        .to_string()
    )

# ================================================================
# SAMPLE DATA
# ================================================================

print("\n===== SAMPLE RECORDS =====")

sample_columns = [
    "State",
    "District",
    "Village",
    "Date",
    "WL_mbgl",
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "WindSpeed_Max_kmh",
    "ET0_mm"
]

sample_columns = [
    column
    for column in sample_columns
    if column in df.columns
]

print(
    df[sample_columns]
    .head(10)
    .to_string(index=False)
)

# ================================================================
# FINAL SUMMARY
# ================================================================

print("\n" + "=" * 70)
print("WEATHER DATA CHECK COMPLETED")
print("=" * 70)

print(f"\nTotal records available: {len(df)}")

print("\nNext step:")
print("If the weather columns contain valid values,")
print("we can train the groundwater model using:")
print()
print("Temperature + Humidity + Rainfall + Wind + Solar Radiation")
print("+ Location + Date")
print()
print("Target: WL_mbgl")

print("=" * 70)