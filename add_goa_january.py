import pandas as pd
import os

print("=" * 70)
print("ADD GOA JANUARY 2025 DATA")
print("=" * 70)

# --------------------------------------------------
# FILES
# --------------------------------------------------

existing_file = "groundwater_with_delhi_january.csv"
goa_file = "goa_january_2025.csv"
output_file = "groundwater_with_goa_january.csv"

# --------------------------------------------------
# LOAD EXISTING DATA
# --------------------------------------------------

if not os.path.exists(existing_file):
    print(f"ERROR: {existing_file} not found")
    exit()

if not os.path.exists(goa_file):
    print(f"ERROR: {goa_file} not found")
    exit()

existing = pd.read_csv(existing_file)
goa = pd.read_csv(goa_file)

print(f"\nExisting records: {len(existing)}")
print(f"Goa January records: {len(goa)}")

# --------------------------------------------------
# REQUIRED COLUMNS
# --------------------------------------------------

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
if list(goa.columns) != required_columns:
    print("\nERROR: Goa columns are incorrect.")
    print("Found:")
    print(list(goa.columns))
    print("\nExpected:")
    print(required_columns)
    exit()

# --------------------------------------------------
# CHECK STATE
# --------------------------------------------------

non_goa = goa[
    goa["State"].astype(str).str.strip().str.lower() != "goa"
]

if len(non_goa) > 0:
    print("\nERROR: Non-Goa record found.")
    print(non_goa)
    exit()

# --------------------------------------------------
# REMOVE DUPLICATES INSIDE GOA FILE
# --------------------------------------------------

before = len(goa)

goa = goa.drop_duplicates()

removed_inside = before - len(goa)

print(f"Duplicates inside Goa file removed: {removed_inside}")

# --------------------------------------------------
# CONVERT NUMERIC COLUMNS
# --------------------------------------------------

for col in ["Latitude", "Longitude", "WL_mbgl"]:
    goa[col] = pd.to_numeric(goa[col], errors="coerce")

# --------------------------------------------------
# CHECK INVALID RECORDS
# --------------------------------------------------

invalid = goa[
    goa[required_columns].isna().any(axis=1)
]

if len(invalid) > 0:
    print("\nERROR: Invalid/incomplete Goa records found:")
    print(invalid)
    exit()

# --------------------------------------------------
# COMBINE
# --------------------------------------------------

combined = pd.concat(
    [existing, goa],
    ignore_index=True
)

print(f"\nRows before final duplicate check: {len(combined)}")

# --------------------------------------------------
# REMOVE DUPLICATES
# --------------------------------------------------

before_duplicate = len(combined)

combined = combined.drop_duplicates()

duplicates_removed = before_duplicate - len(combined)

print(f"Duplicate rows removed: {duplicates_removed}")

# --------------------------------------------------
# SAVE
# --------------------------------------------------

combined.to_csv(output_file, index=False)

# --------------------------------------------------
# RESULTS
# --------------------------------------------------

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(f"Original records : {len(existing)}")
print(f"Goa records      : {len(goa)}")
print(f"Final records    : {len(combined)}")

print("\n===== STATE COUNTS =====")
print(combined["State"].value_counts())

print("\n===== MISSING VALUES =====")
print(combined[required_columns].isna().sum())

print("\n===== DUPLICATES =====")
print("Duplicate rows:", combined.duplicated().sum())

# --------------------------------------------------
# DATE CHECK
# --------------------------------------------------

combined["Date"] = pd.to_datetime(
    combined["Date"],
    dayfirst=True,
    errors="coerce"
)

print("\n===== DATE RANGE =====")
print("Earliest:", combined["Date"].min())
print("Latest  :", combined["Date"].max())

# Save again with normalized date
combined.to_csv(output_file, index=False)

print("\nSaved as:")
print(output_file)

print("=" * 70) 