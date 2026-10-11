import pandas as pd
import os
import sys

# ============================================================
# FILES
# ============================================================

BASE_FILE = "groundwater_final_5_states_august_2025.csv"
AP_FILE = "delhi_august_2025.csv"
OUTPUT_FILE = "groundwater_final_6_states_august_2025.csv"

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

EXPECTED_STATES = {
    "Andhra Pradesh": 95,
    "Bihar": 72,
    "Assam": 52,
    "Arunachal Pradesh": 28,
    "Kerala": 9
}


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def stop(message):
    print()
    print("=" * 70)
    print("ERROR:", message)
    print("=" * 70)
    sys.exit(1)


def find_base_file():
    candidates = [
        "groundwater_final_5_states_august_2025.csv",
        "groundwater_with_5_states.csv",
        "final_groundwater_dataset.csv"
    ]

    for file in candidates:
        if os.path.exists(file):
            return file

    stop(
        "5-state groundwater dataset not found.\n"
        "Expected:\n"
        "groundwater_final_5_states_august_2025.csv"
    )


# ============================================================
# LOAD BASE DATA
# ============================================================

print()
print("=" * 70)
print("GROUNDWATER DATASET - ADD DELHI AUGUST 2025")
print("=" * 70)

BASE_FILE = find_base_file()

print()
print("===== LOAD EXISTING 5-STATE DATA =====")
print("Base file:", BASE_FILE)

try:
    base = pd.read_csv(BASE_FILE, dtype=str)
except Exception as e:
    stop(f"Could not read base dataset: {e}")

print("Existing rows:", len(base))


# ============================================================
# NORMALIZE BASE COLUMNS
# ============================================================

base.columns = [str(c).strip() for c in base.columns]

# Fix possible groundwater column name
for col in list(base.columns):
    if col.strip().lower() in [
        "wl(mbgl)",
        "wl_mbgl",
        "wl",
        "groundwater level",
        "groundwater_level"
    ]:
        if col != "WL_mbgl":
            base.rename(columns={col: "WL_mbgl"}, inplace=True)
        break


# ============================================================
# LOAD DELHI DATA
# ============================================================

print()
print("===== LOAD DELHI AUGUST DATA =====")

if not os.path.exists(AP_FILE):
    stop(
        f"{AP_FILE} not found.\n\n"
        "Create the file first with the Delhi August 2025 records."
    )

try:
    delhi = pd.read_csv(AP_FILE, dtype=str)
except Exception as e:
    stop(f"Could not read Delhi dataset: {e}")

print("Delhi rows loaded:", len(delhi))

print()
print("Delhi columns detected:")
print(list(delhi.columns))


# ============================================================
# NORMALIZE DELHI COLUMN NAMES
# ============================================================

print()
print("===== NORMALIZE DELHI COLUMN NAMES =====")

rename_map = {}

for col in delhi.columns:
    clean = str(col).strip()

    if clean.lower() == "latitute":
        rename_map[col] = "Latitude"

    elif clean.lower() == "latitude":
        rename_map[col] = "Latitude"

    elif clean.lower() == "longitude":
        rename_map[col] = "Longitude"

    elif clean.lower() == "date":
        rename_map[col] = "Date"

    elif clean.lower() in [
        "wl(mbgl)",
        "wl_mbgl",
        "wl",
        "groundwater level",
        "groundwater_level"
    ]:
        rename_map[col] = "WL_mbgl"

    elif clean.lower() == "state":
        rename_map[col] = "State"

    elif clean.lower() == "district":
        rename_map[col] = "District"

    elif clean.lower() == "block":
        rename_map[col] = "Block"

    elif clean.lower() == "village":
        rename_map[col] = "Village"


delhi.rename(columns=rename_map, inplace=True)

print("Delhi columns after normalization:")
print(list(delhi.columns))


# ============================================================
# COLUMN CHECK
# ============================================================

print()
print("===== COLUMN CHECK =====")

missing = [c for c in REQUIRED_COLUMNS if c not in delhi.columns]

if missing:
    stop(
        "Missing columns in Delhi dataset:\n"
        + str(missing)
    )

print("All required columns present.")


# ============================================================
# SELECT ONLY REQUIRED COLUMNS
# ============================================================

delhi = delhi[REQUIRED_COLUMNS].copy()
base = base[[c for c in REQUIRED_COLUMNS if c in base.columns]].copy()

missing_base = [c for c in REQUIRED_COLUMNS if c not in base.columns]

if missing_base:
    stop(
        "Missing columns in existing 5-state dataset:\n"
        + str(missing_base)
    )


# ============================================================
# REMOVE ACCIDENTAL PIPE-CORRUPTED ROWS
# ============================================================

print()
print("===== CHECK FOR CORRUPTED ROWS =====")

for df_name, df in [
    ("BASE", base),
    ("DELHI", delhi)
]:

    bad_state = df["State"].astype(str).str.contains(
        r"\|",
        regex=True,
        na=False
    )

    if bad_state.any():

        print()
        print(df_name, "contains corrupted state rows:")
        print(df.loc[bad_state].to_string(index=False))

        if df_name == "DELHI":
            stop(
                "Delhi file contains malformed rows where the entire "
                "record appears inside the State column.\n"
                "Fix delhi_august_2025.csv before continuing."
            )

        else:
            stop(
                "Existing 5-state dataset contains malformed rows."
            )

print("No corrupted state rows found.")


# ============================================================
# CLEAN TEXT COLUMNS
# ============================================================

print()
print("===== CLEAN DATA =====")

for df in [base, delhi]:

    for col in ["State", "District", "Block", "Village"]:
        df[col] = (
            df[col]
            .astype(str)
            .str.strip()
        )

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


# ============================================================
# DELHI STATE CHECK
# ============================================================

print()
print("===== DELHI STATE CHECK =====")

delhi_count = (
    delhi["State"]
    .str.strip()
    .str.casefold()
    .eq("delhi")
    .sum()
)

other_state_rows = delhi[
    ~delhi["State"]
    .str.strip()
    .str.casefold()
    .eq("delhi")
]

print("Delhi rows:", delhi_count)
print("Rows from other states:", len(other_state_rows))

if len(other_state_rows) > 0:
    print()
    print("Unexpected states found:")
    print(other_state_rows["State"].value_counts())

    stop("Delhi file contains records from other states/UTs.")


# ============================================================
# DATE CHECK
# ============================================================

print()
print("===== DATE CHECK =====")

delhi["Date"] = pd.to_datetime(
    delhi["Date"],
    format="%d-%m-%y",
    errors="coerce"
)

invalid_dates = delhi["Date"].isna().sum()

print("Missing/invalid Delhi dates:", invalid_dates)

if invalid_dates > 0:
    print()
    print(delhi[delhi["Date"].isna()])
    stop("Invalid or missing dates found in Delhi dataset.")

print()
print("Delhi dates:")
print(
    delhi["Date"]
    .dt.strftime("%d-%m-%Y")
    .unique()
)


# ============================================================
# AUGUST CHECK
# ============================================================

print()
print("===== AUGUST CHECK =====")

august_rows = delhi[
    delhi["Date"].dt.month == 8
]

non_august_rows = delhi[
    delhi["Date"].dt.month != 8
]

print("Delhi August rows:", len(august_rows))
print("Non-August rows:", len(non_august_rows))

if len(non_august_rows) > 0:
    stop("Non-August records found in Delhi dataset.")


# ============================================================
# MISSING VALUE CHECK
# ============================================================

print()
print("===== DELHI MISSING VALUES =====")

missing_values = delhi[REQUIRED_COLUMNS].isna().sum()

print(missing_values)

if missing_values.sum() > 0:
    print()
    print("Rows containing missing values:")
    print(
        delhi[
            delhi[REQUIRED_COLUMNS].isna().any(axis=1)
        ].to_string(index=False)
    )

    stop("Missing values exist in Delhi dataset.")


# ============================================================
# COORDINATE CHECK
# ============================================================

print()
print("===== DELHI COORDINATE CHECK =====")

invalid_coordinates = (
    (delhi["Latitude"] < -90) |
    (delhi["Latitude"] > 90) |
    (delhi["Longitude"] < -180) |
    (delhi["Longitude"] > 180)
).sum()

print("Invalid Delhi coordinates:", invalid_coordinates)

if invalid_coordinates > 0:
    print(
        delhi[
            (delhi["Latitude"] < -90) |
            (delhi["Latitude"] > 90) |
            (delhi["Longitude"] < -180) |
            (delhi["Longitude"] > 180)
        ]
    )

    stop("Invalid coordinates found.")


# ============================================================
# GROUNDWATER LEVEL CHECK
# ============================================================

print()
print("===== DELHI GROUNDWATER LEVEL CHECK =====")

print("Minimum WL:", delhi["WL_mbgl"].min())
print("Maximum WL:", delhi["WL_mbgl"].max())
print("Average WL:", delhi["WL_mbgl"].mean())

if (delhi["WL_mbgl"] < 0).any():
    stop("Negative groundwater levels found.")


# ============================================================
# DUPLICATE CHECK
# ============================================================

print()
print("===== DELHI DUPLICATE CHECK =====")

duplicate_count = delhi.duplicated().sum()

print("Exact duplicate rows:", duplicate_count)

if duplicate_count > 0:
    print()
    print("Duplicate rows:")
    print(
        delhi[
            delhi.duplicated(keep=False)
        ].sort_values(REQUIRED_COLUMNS)
    )

    stop(
        "Exact duplicate rows found. "
        "Remove duplicates before continuing."
    )


# ============================================================
# BASE DATA VALIDATION
# ============================================================

print()
print("===== VALIDATE EXISTING 5-STATE DATA =====")

base_state_counts = (
    base["State"]
    .value_counts()
)

print(base_state_counts)

for state, expected in EXPECTED_STATES.items():

    found = int(base_state_counts.get(state, 0))

    if found != expected:
        stop(
            f"{state}: expected {expected}, found {found}"
        )

print()
print("Existing 5-state dataset is valid.")


# ============================================================
# COMBINE
# ============================================================

print()
print("===== COMBINING DATA =====")

previous_rows = len(base)
delhi_rows = len(delhi)

expected_final_rows = previous_rows + delhi_rows

print("Previous five-state rows:", previous_rows)
print("Delhi August rows:", delhi_rows)
print("Expected final rows:", expected_final_rows)

final = pd.concat(
    [base, delhi],
    ignore_index=True
)

print("Actual final rows:", len(final))

if len(final) != expected_final_rows:
    stop("Final row count mismatch.")


# ============================================================
# FINAL CLEANUP
# ============================================================

final["State"] = (
    final["State"]
    .astype(str)
    .str.strip()
)

final["District"] = (
    final["District"]
    .astype(str)
    .str.strip()
)

final["Block"] = (
    final["Block"]
    .astype(str)
    .str.strip()
)

final["Village"] = (
    final["Village"]
    .astype(str)
    .str.strip()
)

final["Latitude"] = pd.to_numeric(
    final["Latitude"],
    errors="coerce"
)

final["Longitude"] = pd.to_numeric(
    final["Longitude"],
    errors="coerce"
)

final["WL_mbgl"] = pd.to_numeric(
    final["WL_mbgl"],
    errors="coerce"
)


# ============================================================
# FINAL DATE NORMALIZATION
# ============================================================

final["Date"] = pd.to_datetime(
    final["Date"],
    errors="coerce"
)


# ============================================================
# FINAL MISSING CHECK
# ============================================================

print()
print("===== FINAL MISSING VALUES =====")

final_missing = final[REQUIRED_COLUMNS].isna().sum()

print(final_missing)

if final_missing.sum() > 0:

    print()
    print("Rows containing missing values:")
    print(
        final[
            final[REQUIRED_COLUMNS].isna().any(axis=1)
        ].to_string(index=False)
    )

    stop(
        "Missing values exist in final dataset. "
        "Final dataset will NOT be saved."
    )


# ============================================================
# FINAL COORDINATE CHECK
# ============================================================

print()
print("===== FINAL COORDINATE CHECK =====")

invalid_final_coordinates = (
    (final["Latitude"] < -90) |
    (final["Latitude"] > 90) |
    (final["Longitude"] < -180) |
    (final["Longitude"] > 180)
).sum()

print(
    "Invalid final coordinates:",
    invalid_final_coordinates
)

if invalid_final_coordinates > 0:
    stop("Invalid coordinates exist in final dataset.")


# ============================================================
# FINAL STATE VALIDATION
# ============================================================

print()
print("===== FINAL STATE VALIDATION =====")

final_state_counts = final["State"].value_counts()

print()
print("FINAL STATE COUNTS:")
print(final_state_counts)


# Expected original states
validation_errors = []

for state, expected in EXPECTED_STATES.items():

    found = int(final_state_counts.get(state, 0))

    if found != expected:
        validation_errors.append(
            f"{state}: expected {expected}, found {found}"
        )


# Delhi must exist
if int(final_state_counts.get("Delhi", 0)) != delhi_rows:

    validation_errors.append(
        f"Delhi: expected {delhi_rows}, "
        f"found {int(final_state_counts.get('Delhi', 0))}"
    )


# Only expected states allowed
allowed_states = set(EXPECTED_STATES.keys()) | {"Delhi"}

unexpected_states = [
    state
    for state in final_state_counts.index
    if state not in allowed_states
]

if unexpected_states:
    validation_errors.append(
        f"Unexpected states: {unexpected_states}"
    )


if validation_errors:

    print()
    print("STATE VALIDATION FAILED:")

    for error in validation_errors:
        print(" -", error)

    stop(
        "State counts are incorrect. "
        "Do not save the final dataset."
    )


print()
print("STATE VALIDATION PASSED.")


# ============================================================
# FINAL ROW COUNT CHECK
# ============================================================

print()
print("===== FINAL ROW COUNT CHECK =====")

if len(final) != expected_final_rows:
    stop(
        f"Expected {expected_final_rows} rows, "
        f"found {len(final)}"
    )

print("Expected final rows:", expected_final_rows)
print("Actual final rows:", len(final))
print("ROW COUNT STATUS: OK")


# ============================================================
# SAVE
# ============================================================

print()
print("===== SAVING FINAL DATASET =====")

final.to_csv(
    OUTPUT_FILE,
    index=False
)

print("Final dataset saved as:", OUTPUT_FILE)


# ============================================================
# VERIFY SAVED FILE
# ============================================================

print()
print("===== VERIFY SAVED FILE =====")

try:
    saved = pd.read_csv(
        OUTPUT_FILE
    )
except Exception as e:
    stop(f"Could not read saved file: {e}")

print("Saved rows:", len(saved))

if len(saved) != expected_final_rows:
    stop("Saved row count does not match expected row count.")


# ============================================================
# VERIFY SAVED STATE COUNTS
# ============================================================

saved_state_counts = saved["State"].value_counts()

print()
print("SAVED STATE COUNTS:")
print(saved_state_counts)

for state, expected in EXPECTED_STATES.items():

    found = int(saved_state_counts.get(state, 0))

    if found != expected:
        stop(
            f"Saved dataset validation failed: "
            f"{state} expected {expected}, found {found}"
        )

if int(saved_state_counts.get("Delhi", 0)) != delhi_rows:

    stop(
        "Saved dataset validation failed for Delhi."
    )


# ============================================================
# FINAL SUCCESS
# ============================================================

print()
print("=" * 70)
print("GROUNDWATER DATASET UPDATE COMPLETE")
print("=" * 70)

print()
print("Previous five-state rows :", previous_rows)
print("Delhi August rows        :", delhi_rows)
print("Final rows               :", len(saved))
print("Output file              :", OUTPUT_FILE)

print()
print("FINAL STATE COUNTS:")
print(saved_state_counts)

print()
print("ALL CHECKS PASSED SUCCESSFULLY.")
print("=" * 70)