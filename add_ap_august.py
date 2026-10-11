import pandas as pd
import os
import sys

# ============================================================
# FILES
# ============================================================

EXISTING_FILE = "groundwater_with_5_states.csv"
AP_FILE = "andhra_august_2025.csv"
OUTPUT_FILE = "groundwater_final_5_states_august_2025.csv"

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

EXPECTED = {
    "Kerala": 9,
    "Bihar": 72,
    "Andhra Pradesh": 95,
    "Assam": 52,
    "Arunachal Pradesh": 28
}

EXPECTED_EXISTING = 164
EXPECTED_AP = 92
EXPECTED_FINAL = 256


# ============================================================
# STOP FUNCTION
# ============================================================

def stop(message):
    print("\nERROR:", message)
    sys.exit(1)


# ============================================================
# READ CSV
# ============================================================

print("=" * 70)
print("GROUNDWATER DATASET UPDATE")
print("=" * 70)

print("\n===== CHECK FILES =====")

if not os.path.exists(EXISTING_FILE):
    stop(f"{EXISTING_FILE} not found.")

if not os.path.exists(AP_FILE):
    stop(f"{AP_FILE} not found.")

print("Existing file:", EXISTING_FILE)
print("AP file      :", AP_FILE)


# ============================================================
# LOAD EXISTING DATA
# ============================================================

print("\n===== LOAD EXISTING FIVE-STATE DATA =====")

existing = pd.read_csv(
    EXISTING_FILE,
    dtype=str
)

print("Existing rows:", len(existing))

if len(existing) != EXPECTED_EXISTING:
    print(
        f"WARNING: Existing rows expected "
        f"{EXPECTED_EXISTING}, found {len(existing)}"
    )


# ============================================================
# LOAD AP DATA
# ============================================================

print("\n===== LOAD AP AUGUST DATA =====")

ap = pd.read_csv(
    AP_FILE,
    dtype=str
)

print("AP rows loaded:", len(ap))

if len(ap) != EXPECTED_AP:
    print(
        f"WARNING: AP rows expected "
        f"{EXPECTED_AP}, found {len(ap)}"
    )

print("\nAP columns:")
print(list(ap.columns))


# ============================================================
# NORMALIZE COLUMN NAMES
# ============================================================

def normalize_columns(df):

    df.columns = (
        df.columns
        .astype(str)
        .str.replace("\ufeff", "", regex=False)
        .str.strip()
    )

    groundwater_columns = [
        "WL(mbgl)",
        "WL (mbgl)",
        "WL_mbgl",
        "WL",
        "Water Level"
    ]

    for col in groundwater_columns:

        if col in df.columns:

            if col != "WL_mbgl":
                df = df.rename(
                    columns={col: "WL_mbgl"}
                )

            break

    return df


existing = normalize_columns(existing)
ap = normalize_columns(ap)


# ============================================================
# CHECK AP COLUMNS
# ============================================================

print("\n===== COLUMN CHECK =====")

missing_existing = [
    c for c in COLUMNS
    if c not in existing.columns
]

missing_ap = [
    c for c in COLUMNS
    if c not in ap.columns
]

if missing_existing:
    stop(
        "Missing columns in existing dataset: "
        + str(missing_existing)
    )

if missing_ap:
    stop(
        "Missing columns in AP dataset: "
        + str(missing_ap)
    )


# ============================================================
# SELECT REQUIRED COLUMNS
# ============================================================

existing = existing[COLUMNS].copy()
ap = ap[COLUMNS].copy()


# ============================================================
# IMPORTANT REPAIR
# MALFORMED BIHAR ROWS
# ============================================================

print("\n===== REPAIR MALFORMED BIHAR ROWS =====")

malformed = (
    existing["State"]
    .astype(str)
    .str.contains(r"\s*\|\s*", regex=True)
)

print(
    "Malformed rows detected:",
    malformed.sum()
)

if malformed.sum() > 0:

    repaired_rows = []

    for index, row in existing[malformed].iterrows():

        raw = str(row["State"]).strip()

        parts = [
            x.strip()
            for x in raw.split("|")
        ]

        if len(parts) != 8:

            stop(
                f"Could not repair row {index}:\n"
                f"{raw}"
            )

        repaired = {
            "State": parts[0],
            "District": parts[1],
            "Block": parts[2],
            "Village": parts[3],
            "Latitude": parts[4],
            "Longitude": parts[5],
            "Date": parts[6],
            "WL_mbgl": parts[7]
        }

        repaired_rows.append(
            (index, repaired)
        )

    # Apply repaired rows
    for index, repaired in repaired_rows:

        for column in COLUMNS:

            existing.loc[
                index,
                column
            ] = repaired[column]

    print(
        "Repaired rows:",
        len(repaired_rows)
    )


# ============================================================
# CLEAN TEXT
# ============================================================

print("\n===== CLEAN DATA =====")

for df in [existing, ap]:

    for column in [
        "State",
        "District",
        "Block",
        "Village"
    ]:

        df[column] = (
            df[column]
            .astype(str)
            .str.strip()
        )


# ============================================================
# NUMERIC CONVERSION
# ============================================================

for df in [existing, ap]:

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
# DATE CONVERSION
# ============================================================

for df in [existing, ap]:

    df["Date"] = (
        df["Date"]
        .astype(str)
        .str.strip()
    )

    df["Date"] = pd.to_datetime(
        df["Date"],
        format="mixed",
        dayfirst=True,
        errors="coerce"
    )


# ============================================================
# REPAIR MISSING BIHAR DATES
# ============================================================

print("\n===== REPAIR BIHAR DATES =====")

bihar_missing = (
    existing["State"].eq("Bihar")
    & existing["Date"].isna()
)

print(
    "Bihar missing dates:",
    bihar_missing.sum()
)

if bihar_missing.sum() > 0:

    existing.loc[
        bihar_missing,
        "Date"
    ] = pd.Timestamp("2025-08-30")


# ============================================================
# AP STATE CHECK
# ============================================================

print("\n===== AP STATE CHECK =====")

wrong_ap = (
    ~ap["State"].eq("Andhra Pradesh")
)

print(
    "Andhra Pradesh rows:",
    (~wrong_ap).sum()
)

print(
    "Rows from other states:",
    wrong_ap.sum()
)

if wrong_ap.sum() > 0:
    stop(
        "AP dataset contains rows from other states."
    )


# ============================================================
# AP DATE CHECK
# ============================================================

print("\n===== AP DATE CHECK =====")

missing_ap_dates = ap["Date"].isna().sum()

print(
    "Missing/invalid AP dates:",
    missing_ap_dates
)

if missing_ap_dates > 0:

    ap.loc[
        ap["Date"].isna(),
        "Date"
    ] = pd.Timestamp("2025-08-30")


# ============================================================
# AUGUST CHECK
# ============================================================

print("\n===== AUGUST CHECK =====")

not_august = ~ap["Date"].dt.month.eq(8)

print(
    "AP August rows:",
    (~not_august).sum()
)

print(
    "Non-August rows:",
    not_august.sum()
)

if not_august.sum() > 0:
    stop(
        "Non-August AP records found."
    )


# ============================================================
# AP MISSING VALUES
# ============================================================

print("\n===== AP MISSING VALUES =====")

print(
    ap[COLUMNS].isna().sum()
)

if ap[COLUMNS].isna().any().any():

    stop(
        "Missing values exist in AP dataset."
    )


# ============================================================
# AP COORDINATE CHECK
# ============================================================

print("\n===== AP COORDINATE CHECK =====")

bad_ap_coordinates = (
    (ap["Latitude"] < -90)
    | (ap["Latitude"] > 90)
    | (ap["Longitude"] < -180)
    | (ap["Longitude"] > 180)
)

print(
    "Invalid AP coordinates:",
    bad_ap_coordinates.sum()
)

if bad_ap_coordinates.sum() > 0:
    stop(
        "Invalid AP coordinates."
    )


# ============================================================
# AP WL CHECK
# ============================================================

print("\n===== AP GROUNDWATER LEVEL CHECK =====")

print(
    "Minimum WL:",
    ap["WL_mbgl"].min()
)

print(
    "Maximum WL:",
    ap["WL_mbgl"].max()
)

print(
    "Average WL:",
    ap["WL_mbgl"].mean()
)


# ============================================================
# AP DUPLICATES
# ============================================================

print("\n===== AP DUPLICATE CHECK =====")

duplicates = ap.duplicated().sum()

print(
    "Exact duplicate rows:",
    duplicates
)

if duplicates > 0:

    ap = (
        ap
        .drop_duplicates()
        .reset_index(drop=True)
    )


# ============================================================
# COMBINE
# ============================================================

print("\n===== COMBINING DATA =====")

print(
    "Existing rows:",
    len(existing)
)

print(
    "AP rows:",
    len(ap)
)

expected_rows = (
    len(existing)
    + len(ap)
)

print(
    "Expected final rows:",
    expected_rows
)

final = pd.concat(
    [
        existing,
        ap
    ],
    ignore_index=True
)

print(
    "Actual final rows:",
    len(final)
)


# ============================================================
# FINAL STATE CHECK
# ============================================================

print("\n===== FINAL STATE CHECK =====")

state_counts = (
    final["State"]
    .value_counts()
)

print(state_counts)

state_errors = []

for state, expected in EXPECTED.items():

    actual = state_counts.get(
        state,
        0
    )

    if actual != expected:

        state_errors.append(
            f"{state}: expected {expected}, found {actual}"
        )


extra_states = [
    state
    for state in state_counts.index
    if state not in EXPECTED
]

if extra_states:

    state_errors.append(
        "Unexpected states: "
        + str(extra_states)
    )


if state_errors:

    print("\nSTATE VALIDATION FAILED:")

    for error in state_errors:
        print(" -", error)

    stop(
        "State counts are incorrect."
    )


print(
    "\nSTATE VALIDATION: OK"
)


# ============================================================
# FINAL ROW COUNT
# ============================================================

print("\n===== FINAL ROW COUNT =====")

print(
    "Expected:",
    EXPECTED_FINAL
)

print(
    "Actual:",
    len(final)
)

if len(final) != EXPECTED_FINAL:

    stop(
        f"Final row count incorrect. "
        f"Expected {EXPECTED_FINAL}, "
        f"found {len(final)}."
    )

print(
    "ROW COUNT: OK"
)


# ============================================================
# FINAL MISSING VALUES
# ============================================================

print("\n===== FINAL MISSING VALUES =====")

missing = final[COLUMNS].isna().sum()

print(missing)

if missing.any():

    print(
        "\nRows containing missing values:"
    )

    print(
        final[
            final[COLUMNS]
            .isna()
            .any(axis=1)
        ].to_string()
    )

    stop(
        "Missing values exist in final dataset."
    )

print(
    "MISSING VALUE CHECK: OK"
)


# ============================================================
# FINAL COORDINATE CHECK
# ============================================================

print("\n===== FINAL COORDINATE CHECK =====")

bad_coordinates = (
    (final["Latitude"] < -90)
    | (final["Latitude"] > 90)
    | (final["Longitude"] < -180)
    | (final["Longitude"] > 180)
)

print(
    "Invalid final coordinates:",
    bad_coordinates.sum()
)

if bad_coordinates.sum() > 0:

    stop(
        "Invalid coordinates found."
    )

print(
    "COORDINATE CHECK: OK"
)


# ============================================================
# FINAL WL CHECK
# ============================================================

print("\n===== FINAL WL CHECK =====")

negative_wl = (
    final["WL_mbgl"] < 0
)

print(
    "Negative WL values:",
    negative_wl.sum()
)

if negative_wl.sum() > 0:

    stop(
        "Negative groundwater level found."
    )

print(
    "GROUNDWATER LEVEL CHECK: OK"
)


# ============================================================
# SORT
# ============================================================

final = final.sort_values(
    by=[
        "State",
        "District",
        "Block",
        "Village",
        "Date"
    ],
    kind="stable"
).reset_index(drop=True)


# ============================================================
# FORMAT DATE
# ============================================================

final["Date"] = final["Date"].dt.strftime(
    "%d-%m-%Y"
)


# ============================================================
# SAVE
# ============================================================

print("\n===== SAVING FINAL DATASET =====")

final.to_csv(
    OUTPUT_FILE,
    index=False
)

print(
    "Saved:",
    OUTPUT_FILE
)


# ============================================================
# VERIFY SAVED FILE
# ============================================================

print("\n===== VERIFY SAVED FILE =====")

saved = pd.read_csv(
    OUTPUT_FILE,
    dtype=str
)

print(
    "Saved rows:",
    len(saved)
)

if len(saved) != EXPECTED_FINAL:

    stop(
        "Saved row count is incorrect."
    )


saved_state_counts = (
    saved["State"]
    .value_counts()
)

print("\nSaved state counts:")

print(saved_state_counts)


saved_missing = (
    saved[COLUMNS]
    .isna()
    .sum()
)

print("\nSaved missing values:")

print(saved_missing)

if saved_missing.any():

    stop(
        "Saved file contains missing values."
    )


# ============================================================
# SUCCESS
# ============================================================

print("\n")
print("=" * 70)
print("GROUNDWATER DATASET UPDATE COMPLETE")
print("=" * 70)

print(
    "Previous five-state rows:",
    len(existing)
)

print(
    "AP August rows:",
    len(ap)
)

print(
    "Final rows:",
    len(final)
)

print(
    "Output:",
    OUTPUT_FILE
)

print("\nFINAL STATE COUNTS:")

print(saved_state_counts)

print("\nALL CHECKS PASSED SUCCESSFULLY.")

print("=" * 70)