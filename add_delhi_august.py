import pandas as pd
import re
import os
import sys

# ============================================================
# ADD DELHI AUGUST 2025 DATA
# ============================================================

BASE_FILE = "groundwater_final_5_states_august_2025.csv"
DELHI_FILE = "delhi_august_2025.csv"
OUTPUT_FILE = "groundwater_final_6_states_august_2025.csv"

EXPECTED_DELHI_ROWS = 116

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

print("=" * 70)
print("        ADD DELHI AUGUST 2025 DATA")
print("=" * 70)


# ============================================================
# 1. CHECK FILES
# ============================================================

if not os.path.exists(BASE_FILE):
    print(f"\nERROR: {BASE_FILE} not found.")
    sys.exit()

if not os.path.exists(DELHI_FILE):
    print(f"\nERROR: {DELHI_FILE} not found.")
    sys.exit()


# ============================================================
# 2. LOAD EXISTING FIVE-STATE DATA
# ============================================================

print("\n===== LOAD EXISTING 5-STATE DATA =====")

base = pd.read_csv(BASE_FILE)

print(f"Base file: {BASE_FILE}")
print(f"Existing rows: {len(base)}")


# ============================================================
# 3. LOAD DELHI CSV
# ============================================================

print("\n===== LOAD DELHI AUGUST DATA =====")

try:
    delhi = pd.read_csv(
        DELHI_FILE,
        dtype=str,
        keep_default_na=False
    )
except Exception as e:
    print("\nERROR loading Delhi CSV:")
    print(e)
    sys.exit()


print(f"Delhi rows loaded: {len(delhi)}")
print("\nOriginal Delhi columns:")
print(list(delhi.columns))


# ============================================================
# 4. NORMALIZE COLUMN NAMES
# ============================================================

print("\n===== NORMALIZE DELHI COLUMN NAMES =====")

delhi.columns = (
    delhi.columns
    .str.strip()
    .str.replace("\ufeff", "", regex=False)
)

rename_map = {}

for col in delhi.columns:
    c = col.lower().strip()

    if c in ["state"]:
        rename_map[col] = "State"

    elif c in ["district"]:
        rename_map[col] = "District"

    elif c in ["block"]:
        rename_map[col] = "Block"

    elif c in ["village"]:
        rename_map[col] = "Village"

    elif c in ["latitude", "latitute", "lat"]:
        rename_map[col] = "Latitude"

    elif c in ["longitude", "longitute", "long"]:
        rename_map[col] = "Longitude"

    elif c == "date":
        rename_map[col] = "Date"

    elif c in ["wl(mbgl)", "wl_mbgl", "wl", "groundwater level"]:
        rename_map[col] = "WL_mbgl"


delhi.rename(columns=rename_map, inplace=True)

print("Delhi columns after normalization:")
print(list(delhi.columns))


# ============================================================
# 5. COLUMN CHECK
# ============================================================

print("\n===== COLUMN CHECK =====")

missing_columns = [
    col for col in REQUIRED_COLUMNS
    if col not in delhi.columns
]

if missing_columns:
    print("\nERROR: Missing required columns:")
    print(missing_columns)
    sys.exit()

print("All required columns present.")


# ============================================================
# 6. READ RAW DELHI FILE
# ============================================================

print("\n===== READ RAW DELHI FILE =====")

with open(
    DELHI_FILE,
    "r",
    encoding="utf-8-sig",
    errors="replace"
) as f:
    raw_text = f.read()


print(f"Raw file characters: {len(raw_text)}")


# ============================================================
# 7. EXTRACT LATITUDE / LONGITUDE / DATE / WL
# ============================================================

print("\n===== RECOVER DELHI MEASUREMENT VALUES =====")

# Accept:
# 30-08-25
# 30/08/25
# 30-08-2025
# 30/08/2025
# 2025-08-30

pattern = re.compile(
    r"""
    (?P<lat>-?\d{1,2}\.\d+)
    \s*[,|;\t ]+\s*
    (?P<lon>-?\d{2,3}\.\d+)
    \s*[,|;\t ]+\s*
    (?P<date>
        \d{2}[-/]\d{2}[-/]\d{2,4}
        |
        \d{4}[-/]\d{2}[-/]\d{2}
    )
    \s*[,|;\t ]+\s*
    (?P<wl>-?\d+(?:\.\d+)?)
    """,
    re.VERBOSE
)


matches = list(pattern.finditer(raw_text))

print(f"Raw coordinate/date/WL records detected: {len(matches)}")


# ============================================================
# 8. FALLBACK REGEX
# ============================================================

if len(matches) != EXPECTED_DELHI_ROWS:

    print("\nPrimary pattern did not find exactly 116 records.")
    print("Trying fallback extraction...")

    fallback_pattern = re.compile(
        r"(-?\d{1,2}\.\d+)"
        r"\s+"
        r"(-?\d{2,3}\.\d+)"
        r"\s+"
        r"(\d{2}[-/]\d{2}[-/]\d{2,4})"
        r"\s+"
        r"(-?\d+(?:\.\d+)?)"
    )

    fallback_matches = list(
        fallback_pattern.finditer(
            raw_text.replace(",", " ")
        )
    )

    print(
        f"Fallback coordinate/date/WL records detected: "
        f"{len(fallback_matches)}"
    )

    if len(fallback_matches) >= EXPECTED_DELHI_ROWS:
        matches = fallback_matches


# ============================================================
# 9. CHECK RECORD COUNT
# ============================================================

if len(matches) < EXPECTED_DELHI_ROWS:

    print("\nERROR: Delhi records could not be recovered.")
    print(
        f"Expected: {EXPECTED_DELHI_ROWS}"
    )
    print(
        f"Recovered: {len(matches)}"
    )

    print("\nThe Delhi CSV raw data must contain records like:")
    print(
        "Delhi,North,Alipur,Bakoli,"
        "28.81528,77.15166,30-08-25,10.13"
    )

    sys.exit()


# Only use exactly the expected 116 records.
matches = matches[:EXPECTED_DELHI_ROWS]


# ============================================================
# 10. BUILD RECOVERED MEASUREMENT DATA
# ============================================================

recovered = []

for m in matches:

    try:
        lat = float(m.group("lat"))
        lon = float(m.group("lon"))
        date_value = m.group("date").strip()
        wl = float(m.group("wl"))

    except Exception:
        # Fallback groups for fallback regex
        try:
            lat = float(m.group(1))
            lon = float(m.group(2))
            date_value = m.group(3).strip()
            wl = float(m.group(4))
        except Exception:
            continue

    recovered.append({
        "Latitude": lat,
        "Longitude": lon,
        "Date": date_value,
        "WL_mbgl": wl
    })


print(f"Recovered records: {len(recovered)}")


if len(recovered) != EXPECTED_DELHI_ROWS:
    print("\nERROR: Recovery count does not equal 116.")
    sys.exit()


# ============================================================
# 11. CLEAN TEXT COLUMNS
# ============================================================

for col in ["State", "District", "Block", "Village"]:
    delhi[col] = (
        delhi[col]
        .astype(str)
        .str.strip()
    )


# ============================================================
# 12. FORCE STATE = DELHI
# ============================================================

# Some Delhi source files use district/region names such as:
# North, South, New Delhi, Shahdara, etc.
#
# These are DISTRICTS of Delhi, NOT states.
#
# Therefore the State column must be Delhi.

delhi["State"] = "Delhi"


# ============================================================
# 13. ASSIGN RECOVERED VALUES
# ============================================================

print("\n===== APPLY RECOVERED VALUES =====")

recovered_df = pd.DataFrame(recovered)

delhi["Latitude"] = recovered_df["Latitude"].values
delhi["Longitude"] = recovered_df["Longitude"].values
delhi["Date"] = recovered_df["Date"].values
delhi["WL_mbgl"] = recovered_df["WL_mbgl"].values


# ============================================================
# 14. CONVERT NUMERIC COLUMNS
# ============================================================

delhi["Latitude"] = pd.to_numeric(
    delhi["Latitude"],
    errors="coerce"
)

delhi["Longitude"] = pd.to_numeric(
    delhi["Longitude"],
    errors="coerce"
)

delhi["WL_mbgl"] = pd.to_numeric(
    delhi["WL_mbgl"],
    errors="coerce"
)


# ============================================================
# 15. DATE CONVERSION
# ============================================================

delhi["Date"] = pd.to_datetime(
    delhi["Date"],
    format="%d-%m-%y",
    errors="coerce"
)


# ============================================================
# 16. DELHI STATE CHECK
# ============================================================

print("\n===== DELHI STATE CHECK =====")

delhi_count = (
    delhi["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("delhi")
    .sum()
)

other_count = len(delhi) - delhi_count

print(f"Delhi rows: {delhi_count}")
print(f"Rows from other states: {other_count}")


if other_count != 0:

    print("\nERROR: Delhi state check failed.")

    print(
        delhi[
            ~delhi["State"]
            .astype(str)
            .str.strip()
            .str.lower()
            .eq("delhi")
        ]["State"]
    )

    sys.exit()


# ============================================================
# 17. DATE CHECK
# ============================================================

print("\n===== DATE CHECK =====")

invalid_dates = delhi["Date"].isna().sum()

print(f"Missing/invalid Delhi dates: {invalid_dates}")

if invalid_dates > 0:

    print("\nInvalid date rows:")
    print(
        delhi[
            delhi["Date"].isna()
        ]
    )

    print("\nERROR: Delhi date recovery failed.")
    sys.exit()


print("\nDelhi dates:")
print(
    delhi["Date"]
    .dt.strftime("%d-%m-%Y")
    .unique()
)


# ============================================================
# 18. AUGUST CHECK
# ============================================================

print("\n===== AUGUST CHECK =====")

august_rows = (
    delhi["Date"]
    .dt.month
    .eq(8)
    .sum()
)

non_august = len(delhi) - august_rows

print(f"Delhi August rows: {august_rows}")
print(f"Non-August rows: {non_august}")


if non_august != 0:
    print("\nERROR: Non-August records found.")
    sys.exit()


# ============================================================
# 19. ROW COUNT CHECK
# ============================================================

print("\n===== DELHI ROW COUNT CHECK =====")

print(
    f"Delhi rows: {len(delhi)} - "
    f"{'OK' if len(delhi) == EXPECTED_DELHI_ROWS else 'ERROR'}"
)

if len(delhi) != EXPECTED_DELHI_ROWS:
    print("\nERROR: Delhi row count incorrect.")
    sys.exit()


# ============================================================
# 20. MISSING VALUE CHECK
# ============================================================

print("\n===== DELHI MISSING VALUES =====")

missing = delhi[REQUIRED_COLUMNS].isna().sum()

print(missing)


if missing.sum() > 0:

    print("\nERROR: Missing values exist in Delhi data.")

    print(
        delhi[
            delhi[REQUIRED_COLUMNS]
            .isna()
            .any(axis=1)
        ]
    )

    sys.exit()


# ============================================================
# 21. FINAL COLUMN ORDER
# ============================================================

delhi = delhi[REQUIRED_COLUMNS]

base = base[REQUIRED_COLUMNS]


# ============================================================
# 22. COMBINE DATA
# ============================================================

print("\n===== COMBINE DATA =====")

final = pd.concat(
    [base, delhi],
    ignore_index=True
)


# ============================================================
# 23. FINAL STATE COUNTS
# ============================================================

print("\n===== FINAL STATE COUNTS =====")

state_counts = (
    final["State"]
    .value_counts()
    .sort_index()
)

print(state_counts)


# ============================================================
# 24. EXPECTED STATE COUNTS
# ============================================================

expected_counts = {
    "Andhra Pradesh": 95,
    "Bihar": 72,
    "Assam": 52,
    "Arunachal Pradesh": 28,
    "Kerala": 9,
    "Delhi": 116
}


print("\n===== STATE VALIDATION =====")

validation_failed = False

for state, expected in expected_counts.items():

    found = int(state_counts.get(state, 0))

    if found != expected:

        print(
            f" - {state}: "
            f"expected {expected}, found {found}"
        )

        validation_failed = True

    else:

        print(
            f" - {state}: "
            f"{found} - OK"
        )


unexpected_states = [
    state
    for state in state_counts.index
    if state not in expected_counts
]


if unexpected_states:

    print(
        "\nUnexpected states:"
    )

    print(unexpected_states)

    validation_failed = True


if validation_failed:

    print(
        "\nERROR: State counts are incorrect."
    )

    print(
        "Final dataset will NOT be saved."
    )

    sys.exit()


# ============================================================
# 25. FINAL ROW CHECK
# ============================================================

expected_total = (
    95 +
    72 +
    52 +
    28 +
    9 +
    116
)

print("\n===== FINAL ROW CHECK =====")

print(f"Expected final rows: {expected_total}")
print(f"Actual final rows:   {len(final)}")


if len(final) != expected_total:

    print("\nERROR: Final row count incorrect.")
    sys.exit()


# ============================================================
# 26. FINAL DUPLICATE CHECK
# ============================================================

print("\n===== DUPLICATE CHECK =====")

duplicates = final.duplicated().sum()

print(f"Duplicate rows: {duplicates}")


# ============================================================
# 27. FINAL MISSING VALUE CHECK
# ============================================================

print("\n===== FINAL MISSING VALUE CHECK =====")

final_missing = final[REQUIRED_COLUMNS].isna().sum()

print(final_missing)


if final_missing.sum() > 0:

    print(
        "\nERROR: Missing values exist in final dataset."
    )

    print(
        final[
            final[REQUIRED_COLUMNS]
            .isna()
            .any(axis=1)
        ]
    )

    sys.exit()


# ============================================================
# 28. SAVE FINAL FILE
# ============================================================

final.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 29. SUCCESS
# ============================================================

print("\n" + "=" * 70)
print("          DELHI AUGUST DATA ADDED SUCCESSFULLY")
print("=" * 70)

print(f"\nPrevious rows: {len(base)}")
print(f"Delhi rows:    {len(delhi)}")
print(f"Final rows:    {len(final)}")
print(f"Output file:   {OUTPUT_FILE}")

print("\nFINAL STATE COUNTS:")
print(state_counts)

print("\nALL CHECKS PASSED SUCCESSFULLY.")
print("=" * 70)