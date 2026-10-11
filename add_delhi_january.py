import pandas as pd
import os

print("=" * 70)
print("ADD DELHI JANUARY 2025 DATA")
print("=" * 70)

# Existing final dataset
existing_file = "groundwater_training_final.csv"

# Delhi January data file
delhi_file = "delhi_january_2025_fixed.csv"

if not os.path.exists(existing_file):
    print(f"ERROR: {existing_file} not found")
    exit()

if not os.path.exists(delhi_file):
    print(f"ERROR: {delhi_file} not found")
    print("Create delhi_january_2025_fixed.csv first.")
    exit()

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------

existing = pd.read_csv(existing_file)
delhi = pd.read_csv(delhi_file)

print(f"\nExisting records: {len(existing)}")
print(f"Delhi January records: {len(delhi)}")

# ---------------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------------

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

# Check columns
if list(delhi.columns) != required_columns:
    print("\nERROR: Delhi columns are incorrect.")
    print("Found:")
    print(list(delhi.columns))
    print("\nRequired:")
    print(required_columns)
    exit()

# ---------------------------------------------------------
# FORCE STATE = DELHI
# ---------------------------------------------------------

delhi["State"] = delhi["State"].astype(str).str.strip()

if not (delhi["State"].str.lower() == "delhi").all():
    print("\nERROR: Non-Delhi record found.")
    print(delhi[delhi["State"].str.lower() != "delhi"])
    exit()

# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------

for col in ["District", "Block", "Village"]:
    delhi[col] = delhi[col].astype(str).str.strip()

# Convert invalid strings to missing values
delhi = delhi.replace(
    ["nan", "NaN", "None", "", "<NA>"],
    pd.NA
)

# ---------------------------------------------------------
# NUMERIC COLUMNS
# ---------------------------------------------------------

delhi["Latitude"] = pd.to_numeric(delhi["Latitude"], errors="coerce")
delhi["Longitude"] = pd.to_numeric(delhi["Longitude"], errors="coerce")
delhi["WL_mbgl"] = pd.to_numeric(delhi["WL_mbgl"], errors="coerce")

# ---------------------------------------------------------
# DATE
# ---------------------------------------------------------

delhi["Date"] = pd.to_datetime(
    delhi["Date"],
    dayfirst=True,
    errors="coerce"
)

# ---------------------------------------------------------
# REMOVE INVALID RECORDS
# ---------------------------------------------------------

before = len(delhi)

delhi = delhi.dropna(
    subset=[
        "State",
        "District",
        "Block",
        "Village",
        "Latitude",
        "Longitude",
        "Date",
        "WL_mbgl"
    ]
)

removed = before - len(delhi)

print(f"\nInvalid/incomplete Delhi records removed: {removed}")

# ---------------------------------------------------------
# REMOVE EXACT DUPLICATES INSIDE DELHI
# ---------------------------------------------------------

before = len(delhi)

delhi = delhi.drop_duplicates()

duplicates_inside = before - len(delhi)

print(f"Duplicate Delhi rows removed: {duplicates_inside}")

# ---------------------------------------------------------
# COMBINE WITH EXISTING DATA
# ---------------------------------------------------------

combined = pd.concat(
    [existing, delhi],
    ignore_index=True
)

print(f"\nRows before final duplicate check: {len(combined)}")

before = len(combined)

combined = combined.drop_duplicates()

duplicates_final = before - len(combined)

print(f"Duplicate rows removed: {duplicates_final}")

# ---------------------------------------------------------
# SORT
# ---------------------------------------------------------

combined = combined.sort_values(
    by=["State", "District", "Block", "Village", "Date"]
).reset_index(drop=True)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------

output_file = "groundwater_with_delhi_january.csv"

combined.to_csv(
    output_file,
    index=False,
    date_format="%Y-%m-%d"
)

# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(f"Original records : {len(existing)}")
print(f"Delhi records    : {len(delhi)}")
print(f"Final records    : {len(combined)}")

print("\n===== STATE COUNTS =====")
print(combined["State"].value_counts())

print("\n===== MISSING VALUES =====")
print(combined[required_columns].isna().sum())

print("\n===== DUPLICATES =====")
print("Duplicate rows:", combined.duplicated().sum())
combined["Date"] = pd.to_datetime(
    combined["Date"],
    errors="coerce"
)
print("\n===== DATE RANGE =====")
print("Earliest:", combined["Date"].min())
print("Latest  :", combined["Date"].max())

print("\nSaved as:")
print(output_file)

print("=" * 70)