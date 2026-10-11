import pandas as pd
import os

# ================================================================
# ADD ALL KERALA JANUARY 2025 RECORDS TO THE CORRECT 696-RECORD DATASET
# ================================================================

print("=" * 70)
print("RESTART: ADD KERALA JANUARY 2025 TO 696-RECORD MASTER DATASET")
print("=" * 70)

# ------------------------------------------------
# FILES
# ------------------------------------------------

BASE_FILE = "groundwater_with_goa_january.csv"
KERALA_FILE = "kerala_january_2025.csv"
OUTPUT_FILE = "groundwater_with_kerala_january_final.csv"

REQUIRED_COLUMNS = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

# ------------------------------------------------
# 1. CHECK FILES
# ------------------------------------------------

if not os.path.exists(BASE_FILE):
    print(f"\nERROR: {BASE_FILE} not found.")
    print("Make sure the file is inside:")
    print(os.getcwd())
    raise SystemExit

if not os.path.exists(KERALA_FILE):
    print(f"\nERROR: {KERALA_FILE} not found.")
    raise SystemExit

# ------------------------------------------------
# 2. LOAD 696-RECORD MASTER DATASET
# ------------------------------------------------

print("\n===== LOAD MASTER DATASET =====")

try:
    base = pd.read_csv(
        BASE_FILE,
        dtype=str,
        keep_default_na=False
    )
except Exception as e:
    print("ERROR loading master dataset:")
    print(e)
    raise SystemExit

print("Master records loaded:", len(base))

if len(base) != 696:
    print("\nWARNING!")
    print("Expected exactly 696 records.")
    print("Found:", len(base))
    print("The program will STOP to protect your original dataset.")
    raise SystemExit

# ------------------------------------------------
# 3. CHECK MASTER COLUMNS
# ------------------------------------------------

missing_base = [
    col for col in REQUIRED_COLUMNS
    if col not in base.columns
]

if missing_base:
    print("\nERROR: Missing columns in master dataset:")
    print(missing_base)
    raise SystemExit

base = base[REQUIRED_COLUMNS].copy()

# ------------------------------------------------
# 4. LOAD ALL KERALA JANUARY DATA
# ------------------------------------------------

print("\n===== LOAD KERALA JANUARY DATA =====")

try:
    kerala = pd.read_csv(
        KERALA_FILE,
        dtype=str,
        keep_default_na=False
    )
except Exception as e:
    print("ERROR loading Kerala file:")
    print(e)
    raise SystemExit

print("Kerala rows loaded:", len(kerala))

if len(kerala) == 0:
    print("\nERROR: Kerala file is empty.")
    raise SystemExit

# ------------------------------------------------
# 5. CHECK KERALA COLUMNS
# ------------------------------------------------

missing_kerala = [
    col for col in REQUIRED_COLUMNS
    if col not in kerala.columns
]

if missing_kerala:
    print("\nERROR: Missing columns in Kerala file:")
    print(missing_kerala)
    raise SystemExit

kerala = kerala[REQUIRED_COLUMNS].copy()

# ------------------------------------------------
# 6. CLEAN WHITESPACE
# ------------------------------------------------

for col in REQUIRED_COLUMNS:
    base[col] = base[col].astype(str).str.strip()
    kerala[col] = kerala[col].astype(str).str.strip()

# ------------------------------------------------
# 7. FORCE KERALA STATE
# ------------------------------------------------

kerala["State"] = "Kerala"

# ------------------------------------------------
# 8. REMOVE INCOMPLETE KERALA ROWS
# ------------------------------------------------

print("\n===== VALIDATE KERALA DATA =====")

before_validation = len(kerala)

for col in REQUIRED_COLUMNS:
    kerala[col] = kerala[col].replace(
        ["", "nan", "NaN", "None", "NULL"],
        pd.NA
    )

kerala = kerala.dropna(subset=REQUIRED_COLUMNS)

print("Rows before validation:", before_validation)
print("Valid Kerala rows:", len(kerala))
print("Invalid/incomplete rows removed:",
      before_validation - len(kerala))

# ------------------------------------------------
# 9. CONVERT NUMERIC COLUMNS
# ------------------------------------------------

kerala["Latitude"] = pd.to_numeric(
    kerala["Latitude"],
    errors="coerce"
)

kerala["Longitude"] = pd.to_numeric(
    kerala["Longitude"],
    errors="coerce"
)

kerala["WL_mbgl"] = pd.to_numeric(
    kerala["WL_mbgl"],
    errors="coerce"
)

kerala = kerala.dropna(
    subset=["Latitude", "Longitude", "WL_mbgl"]
)

# ------------------------------------------------
# 10. REMOVE DUPLICATE KERALA RECORDS
# ------------------------------------------------

before_duplicates = len(kerala)

kerala = kerala.drop_duplicates(
    subset=REQUIRED_COLUMNS,
    keep="first"
)

print("Duplicate Kerala rows removed:",
      before_duplicates - len(kerala))

# ------------------------------------------------
# 11. NORMALIZE DATE
# ------------------------------------------------

print("\n===== PROCESS DATES =====")

# Kerala dates are like 10-01-25
kerala["Date"] = pd.to_datetime(
    kerala["Date"],
    format="%d-%m-%y",
    errors="coerce"
)

# Existing dataset may contain multiple date formats
base["Date"] = pd.to_datetime(
    base["Date"],
    errors="coerce",
    dayfirst=True
)

# ------------------------------------------------
# 12. REMOVE KERALA RECORDS ALREADY PRESENT
# ------------------------------------------------

print("\n===== CHECK AGAINST MASTER DATA =====")

# Create a comparison key
def make_key(df):
    return (
        df["State"].astype(str).str.strip().str.lower()
        + "|" +
        df["District"].astype(str).str.strip().str.lower()
        + "|" +
        df["Block"].astype(str).str.strip().str.lower()
        + "|" +
        df["Village"].astype(str).str.strip().str.lower()
        + "|" +
        df["Latitude"].astype(str)
        + "|" +
        df["Longitude"].astype(str)
        + "|" +
        df["Date"].astype(str)
        + "|" +
        df["WL_mbgl"].astype(str)
    )

base_key = make_key(base)
kerala_key = make_key(kerala)

already_exists = kerala_key.isin(set(base_key))

existing_count = already_exists.sum()

print("Kerala records already in master:", existing_count)

kerala_new = kerala.loc[~already_exists].copy()

print("New Kerala records to add:", len(kerala_new))

# ------------------------------------------------
# 13. COMBINE
# ------------------------------------------------

print("\n===== COMBINE DATA =====")

combined = pd.concat(
    [base, kerala_new],
    ignore_index=True
)

print("Rows before final duplicate check:", len(combined))

# ------------------------------------------------
# 14. FINAL DUPLICATE CHECK
# ------------------------------------------------

before_final_duplicates = len(combined)

combined = combined.drop_duplicates(
    subset=REQUIRED_COLUMNS,
    keep="first"
)

final_duplicates_removed = (
    before_final_duplicates - len(combined)
)

print("Final duplicate rows removed:",
      final_duplicates_removed)

# ------------------------------------------------
# 15. SORT BY DATE
# ------------------------------------------------

combined = combined.sort_values(
    by="Date",
    na_position="last"
).reset_index(drop=True)

# ------------------------------------------------
# 16. SAVE
# ------------------------------------------------

combined.to_csv(
    OUTPUT_FILE,
    index=False,
    date_format="%d-%m-%Y"
)

# ------------------------------------------------
# 17. FINAL REPORT
# ------------------------------------------------

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print("Original master records :", len(base))
print("Kerala rows loaded      :", len(kerala))
print("Kerala duplicate rows   :", existing_count)
print("New Kerala records      :", len(kerala_new))
print("Final records            :", len(combined))

print("\n===== STATE COUNTS =====")
print(combined["State"].value_counts())

print("\n===== MISSING VALUES =====")
print(combined.isnull().sum())

print("\n===== DUPLICATES =====")
print(
    "Duplicate rows:",
    combined.duplicated(
        subset=REQUIRED_COLUMNS
    ).sum()
)

print("\n===== DATE RANGE =====")

valid_dates = combined["Date"].dropna()

if len(valid_dates) > 0:
    print("Earliest:", valid_dates.min())
    print("Latest  :", valid_dates.max())
else:
    print("No valid dates found.")

print("\n===== KERALA CHECK =====")

kerala_final = combined[
    combined["State"].astype(str).str.strip().str.lower()
    == "kerala"
]

print(
    "Total Kerala records in final dataset:",
    len(kerala_final)
)

print("\n===== OUTPUT =====")
print(os.path.abspath(OUTPUT_FILE))

print("\n" + "=" * 70)
print("DONE")
print("=" * 70)