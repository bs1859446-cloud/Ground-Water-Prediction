import pandas as pd
import os

print("=" * 70)
print("RESTART: ADD TAMIL NADU JANUARY 2025 TO 984-RECORD MASTER DATASET")
print("=" * 70)

# ============================================================
# FILE NAMES
# ============================================================

MASTER_FILE = "groundwater_with_kerala_january_final.csv"
TN_FILE = "tamilnadu_january_2025.csv"
OUTPUT_FILE = "groundwater_with_tamilnadu_january_final.csv"

# ============================================================
# REQUIRED COLUMNS
# ============================================================

COLUMNS = [
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
# CHECK FILES
# ============================================================

if not os.path.exists(MASTER_FILE):
    print(f"ERROR: {MASTER_FILE} not found")
    exit()

if not os.path.exists(TN_FILE):
    print(f"ERROR: {TN_FILE} not found")
    print()
    print("Create this file first:")
    print(TN_FILE)
    exit()

# ============================================================
# LOAD MASTER DATASET
# ============================================================

print("\n===== LOAD MASTER DATASET =====")

master = pd.read_csv(MASTER_FILE)

print(f"Master records loaded: {len(master)}")

# Make sure columns exist
missing_master = [c for c in COLUMNS if c not in master.columns]

if missing_master:
    print("ERROR: Missing columns in master:")
    print(missing_master)
    exit()

master = master[COLUMNS].copy()

# ============================================================
# REPAIR MASTER DATA
# ============================================================

print("\n===== CHECK MASTER DATA =====")

for col in ["State", "District", "Block", "Village"]:
    master[col] = master[col].astype(str).str.strip()

master["Latitude"] = pd.to_numeric(
    master["Latitude"], errors="coerce"
)

master["Longitude"] = pd.to_numeric(
    master["Longitude"], errors="coerce"
)

master["WL_mbgl"] = pd.to_numeric(
    master["WL_mbgl"], errors="coerce"
)

# ============================================================
# LOAD TAMIL NADU DATA
# ============================================================

print("\n===== LOAD TAMIL NADU JANUARY DATA =====")

tn = pd.read_csv(TN_FILE)

print(f"Tamil Nadu rows loaded: {len(tn)}")

missing_tn = [c for c in COLUMNS if c not in tn.columns]

if missing_tn:
    print("ERROR: Missing columns in Tamil Nadu file:")
    print(missing_tn)
    exit()

tn = tn[COLUMNS].copy()

# ============================================================
# CLEAN TAMIL NADU DATA
# ============================================================

print("\n===== CLEAN TAMIL NADU DATA =====")

for col in ["State", "District", "Block", "Village"]:
    tn[col] = tn[col].astype(str).str.strip()

tn["Latitude"] = pd.to_numeric(
    tn["Latitude"], errors="coerce"
)

tn["Longitude"] = pd.to_numeric(
    tn["Longitude"], errors="coerce"
)

tn["WL_mbgl"] = pd.to_numeric(
    tn["WL_mbgl"], errors="coerce"
)

# ============================================================
# PROCESS DATE
# ============================================================

print("\n===== PROCESS DATES =====")

master["Date"] = pd.to_datetime(
    master["Date"],
    errors="coerce",
    dayfirst=True
)

tn["Date"] = pd.to_datetime(
    tn["Date"],
    errors="coerce",
    dayfirst=True
)

# ============================================================
# FORCE STATE NAME
# ============================================================

tn["State"] = "Tamil Nadu"

# ============================================================
# VALIDATE TAMIL NADU DATA
# ============================================================

print("\n===== VALIDATE TAMIL NADU DATA =====")

before_validation = len(tn)

tn = tn.dropna(
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

after_validation = len(tn)

print(f"Rows before validation       : {before_validation}")
print(f"Valid Tamil Nadu rows        : {after_validation}")
print(
    f"Invalid/incomplete removed   : "
    f"{before_validation - after_validation}"
)

# ============================================================
# REMOVE DUPLICATE TN RECORDS
# ============================================================

before_duplicates = len(tn)

tn = tn.drop_duplicates()

after_duplicates = len(tn)

print(
    f"Tamil Nadu duplicate rows removed: "
    f"{before_duplicates - after_duplicates}"
)

# ============================================================
# CHECK AGAINST MASTER
# ============================================================

print("\n===== CHECK AGAINST MASTER DATA =====")

# Create comparison key
key_columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

master_keys = set(
    master[key_columns].astype(str).agg("|".join, axis=1)
)

tn_keys = tn[key_columns].astype(str).agg("|".join, axis=1)

already_exists = tn_keys.isin(master_keys)

existing_count = already_exists.sum()

tn_new = tn[~already_exists].copy()

print(f"Tamil Nadu records already in master: {existing_count}")
print(f"New Tamil Nadu records to add        : {len(tn_new)}")

# ============================================================
# COMBINE
# ============================================================

print("\n===== COMBINE DATA =====")

combined = pd.concat(
    [master, tn_new],
    ignore_index=True
)

print(f"Rows before final duplicate check: {len(combined)}")

before_final_duplicates = len(combined)

combined = combined.drop_duplicates(
    subset=key_columns
)

after_final_duplicates = len(combined)

print(
    f"Duplicate rows removed: "
    f"{before_final_duplicates - after_final_duplicates}"
)

# ============================================================
# SORT DATA
# ============================================================

combined = combined.sort_values(
    by=["State", "District", "Block", "Village", "Date"]
).reset_index(drop=True)

# ============================================================
# SAVE
# ============================================================

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

# ============================================================
# SUCCESS
# ============================================================

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(f"Original master records : {len(master)}")
print(f"Tamil Nadu rows loaded  : {len(tn)}")
print(f"New Tamil Nadu records  : {len(tn_new)}")
print(f"Final records           : {len(combined)}")

# ============================================================
# STATE COUNTS
# ============================================================

print("\n===== STATE COUNTS =====")

print(
    combined["State"].value_counts()
)

# ============================================================
# MISSING VALUES
# ============================================================

print("\n===== MISSING VALUES =====")

print(
    combined[COLUMNS].isnull().sum()
)

# ============================================================
# DUPLICATES
# ============================================================

print("\n===== DUPLICATES =====")

print(
    "Duplicate rows:",
    combined.duplicated(subset=key_columns).sum()
)

# ============================================================
# DATE RANGE
# ============================================================

print("\n===== DATE RANGE =====")

valid_dates = combined["Date"].dropna()

if len(valid_dates) > 0:
    print("Earliest:", valid_dates.min())
    print("Latest  :", valid_dates.max())
else:
    print("No valid dates found")

# ============================================================
# KERALA CHECK
# ============================================================

print("\n===== KERALA CHECK =====")

kerala_count = (
    combined["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("kerala")
    .sum()
)

print(
    f"Total Kerala records in final dataset: {kerala_count}"
)

# ============================================================
# TAMIL NADU CHECK
# ============================================================

print("\n===== TAMIL NADU CHECK =====")

tn_count = (
    combined["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("tamil nadu")
    .sum()
)

print(
    f"Total Tamil Nadu records in final dataset: {tn_count}"
)

# ============================================================
# OUTPUT
# ============================================================

print("\n===== OUTPUT =====")

print(
    os.path.abspath(OUTPUT_FILE)
)

print("=" * 70)
print("DONE")
print("=" * 70)