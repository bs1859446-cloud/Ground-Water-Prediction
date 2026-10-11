import pandas as pd
import numpy as np

print("=" * 70)
print("PREPARING FINAL GROUNDWATER TRAINING DATA - CORRECTED")
print("=" * 70)

INPUT = "groundwater_with_assam_january.csv"
OUTPUT = "groundwater_training_final.csv"

# ============================================================
# LOAD DATA
# ============================================================

df = pd.read_csv(INPUT)

print(f"\nOriginal records: {len(df)}")

required = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

# ============================================================
# CHECK COLUMNS
# ============================================================

df.columns = df.columns.str.strip()

missing = [c for c in required if c not in df.columns]

if missing:
    print("\nERROR: Missing columns:")
    print(missing)
    raise SystemExit

# ============================================================
# CLEAN TEXT
# ============================================================

for col in ["State", "District", "Block", "Village"]:
    df[col] = df[col].astype("string").str.strip()

# ============================================================
# CLEAN NUMBERS
# ============================================================

df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
df["WL_mbgl"] = pd.to_numeric(df["WL_mbgl"], errors="coerce")

# ============================================================
# CORRECT ZOLAWADI / DNH RECORD
# ============================================================

mask_zolawadi = (
    (df["Latitude"] == 20.7242) &
    (df["Longitude"] == 70.9306)
)

print(f"\nZolawadi records found: {mask_zolawadi.sum()}")

# Remove incorrect versions
df = df[~mask_zolawadi].copy()

# Add correct record
dnh_record = pd.DataFrame([{
    "State": "Dnh",
    "District": "Diu",
    "Block": pd.NA,
    "Village": "Zolawadi",
    "Latitude": 20.7242,
    "Longitude": 70.9306,
    "Date": "2025-08-30",
    "WL_mbgl": 5.5
}])

df = pd.concat([df, dnh_record], ignore_index=True)

# ============================================================
# CORRECT DATE PARSING
# ============================================================

print("\n===== DATE CONVERSION =====")

original_dates = df["Date"].copy()

# First try YYYY-MM-DD
date1 = pd.to_datetime(
    df["Date"],
    format="%Y-%m-%d",
    errors="coerce"
)

# Then try DD-MM-YY
date2 = pd.to_datetime(
    df["Date"],
    format="%d-%m-%y",
    errors="coerce"
)

# Then try DD-MM-YYYY
date3 = pd.to_datetime(
    df["Date"],
    format="%d-%m-%Y",
    errors="coerce"
)

# Combine all successful conversions
df["Date"] = date1.fillna(date2).fillna(date3)

print("Valid dates:", df["Date"].notna().sum())
print("Invalid dates:", df["Date"].isna().sum())

# ============================================================
# SHOW INVALID DATES
# ============================================================

if df["Date"].isna().sum() > 0:
    print("\nWARNING: Invalid date records:")
    print(
        df.loc[
            df["Date"].isna(),
            ["State", "District", "Village", "Date"]
        ].to_string(index=False)
    )

# ============================================================
# REMOVE INVALID ESSENTIAL DATA
# ============================================================

before = len(df)

df = df.dropna(
    subset=[
        "State",
        "Latitude",
        "Longitude",
        "Date",
        "WL_mbgl"
    ]
).reset_index(drop=True)

print(f"\nInvalid records removed: {before - len(df)}")

# ============================================================
# REMOVE DUPLICATES
# ============================================================

before = len(df)

df = df.drop_duplicates().reset_index(drop=True)

print(f"Duplicate rows removed: {before - len(df)}")

# ============================================================
# SORT
# ============================================================

df = df.sort_values(
    ["Date", "State", "District", "Village"],
    na_position="last"
).reset_index(drop=True)

# ============================================================
# SAVE
# ============================================================

df.to_csv(OUTPUT, index=False)

# ============================================================
# FINAL REPORT
# ============================================================

print("\n" + "=" * 70)
print("FINAL DATASET CREATED")
print("=" * 70)

print(f"\nFinal records: {len(df)}")

print("\n===== STATE COUNTS =====")
print(df["State"].value_counts())

print("\n===== MISSING VALUES =====")
print(df[required].isnull().sum())

print("\n===== DUPLICATES =====")
print("Duplicate rows:", df.duplicated().sum())

print("\n===== DATE RANGE =====")
print("Earliest:", df["Date"].min())
print("Latest  :", df["Date"].max())

print("\n===== DNH / ZOLAWADI CHECK =====")

check = df[
    (df["Latitude"] == 20.7242) &
    (df["Longitude"] == 70.9306)
]

print(check.to_string(index=False))

print("\n===== FINAL COLUMNS =====")
print(df.columns.tolist())

print("\nSaved as:")
print(OUTPUT)

print("=" * 70)