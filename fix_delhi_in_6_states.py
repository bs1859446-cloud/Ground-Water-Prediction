import pandas as pd
import os
import glob

print("=" * 70)
print("FIND ORIGINAL 6-STATE GROUNDWATER DATASET")
print("=" * 70)

DATA_FOLDER = r"C:\Users\hp\coe\data"

EXPECTED_STATES = {
    "Andhra Pradesh",
    "Arunachal Pradesh",
    "Assam",
    "Bihar",
    "Delhi",
    "Kerala"
}

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

print("\n===== SEARCHING CSV FILES =====")

files = glob.glob(
    os.path.join(DATA_FOLDER, "*.csv")
)

print("CSV files found:", len(files))

if not files:
    print("ERROR: No CSV files found.")
    raise SystemExit

found = []

for file in files:

    filename = os.path.basename(file)

    try:

        df = pd.read_csv(
            file,
            dtype=str,
            keep_default_na=False
        )

        print("\n----------------------------------------")
        print("FILE:", filename)
        print("Rows:", len(df))
        print("Columns:", list(df.columns))

        if not all(
            col in df.columns
            for col in REQUIRED_COLUMNS
        ):
            print("Not a groundwater dataset.")
            continue

        states = set(
            df["State"]
            .astype(str)
            .str.strip()
            .unique()
        )

        matched = states.intersection(
            EXPECTED_STATES
        )

        print("States found:", sorted(matched))

        if len(matched) >= 4:

            found.append(
                (
                    file,
                    len(df),
                    matched
                )
            )

    except Exception as e:

        print(
            "Could not read:",
            filename
        )

        print("Reason:", e)

# ============================================================
# RESULTS
# ============================================================

print("\n" + "=" * 70)
print("SEARCH RESULT")
print("=" * 70)

if not found:

    print("""
No other CSV containing the missing 6-state data was found.

Your current groundwater.csv contains only:
    Andhra Pradesh
    Bihar
    Kerala

Therefore the missing:
    Arunachal Pradesh
    Assam
    Delhi

are not available in the data folder.

You must restore/upload the original 6-state CSV.
""")

    raise SystemExit

print("\nPossible original datasets:")

for i, item in enumerate(found, 1):

    file, rows, states = item

    print(f"""
{i}. {os.path.basename(file)}
   Rows: {rows}
   States: {sorted(states)}
""")

# ============================================================
# SELECT BEST FILE
# ============================================================

best_file = max(
    found,
    key=lambda x: (
        len(x[2]),
        x[1]
    )
)

source_file = best_file[0]

print("\n===== BEST MATCH =====")
print("Source:", source_file)
print("Rows:", best_file[1])
print("States:", sorted(best_file[2]))

if not EXPECTED_STATES.issubset(best_file[2]):

    print("""
WARNING:
This file still does not contain all 6 states.

Do not overwrite your current dataset.
""")

    raise SystemExit

# ============================================================
# LOAD ORIGINAL
# ============================================================

df = pd.read_csv(
    source_file,
    dtype=str,
    keep_default_na=False
)

df = df[REQUIRED_COLUMNS].copy()

# ============================================================
# CLEAN
# ============================================================

for col in [
    "State",
    "District",
    "Block",
    "Village"
]:

    df[col] = (
        df[col]
        .astype(str)
        .str.strip()
        .str.replace(
            r"\s+",
            " ",
            regex=True
        )
    )

# ============================================================
# PIPE REPAIR
# ============================================================

for idx in df.index:

    raw = str(df.at[idx, "State"])

    if "|" not in raw:
        continue

    parts = [
        x.strip()
        for x in raw.split("|")
    ]

    if len(parts) == 8:

        df.loc[
            idx,
            REQUIRED_COLUMNS
        ] = parts

# ============================================================
# NUMERIC
# ============================================================

for col in [
    "Latitude",
    "Longitude",
    "WL_mbgl"
]:

    df[col] = pd.to_numeric(
        df[col],
        errors="coerce"
    )

# ============================================================
# DATE
# ============================================================

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
    dayfirst=True
)

# ============================================================
# DELHI
# ============================================================

delhi = (
    df["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    == "delhi"
)

df.loc[
    delhi & df["Date"].isna(),
    "Date"
] = pd.Timestamp(
    "2025-08-30"
)

# ============================================================
# REMOVE CORRUPTED DIU
# ============================================================

diu = (
    df["State"]
    .astype(str)
    .str.contains(
        "Diu",
        case=False,
        na=False
    )
)

print(
    "\nCorrupted Diu rows:",
    diu.sum()
)

df = df.loc[~diu].copy()

# ============================================================
# VALIDATION
# ============================================================

print("\n===== FINAL VALIDATION =====")

print("Rows:", len(df))

print("\nState counts:")
print(df["State"].value_counts())

print("\nMissing values:")
print(df.isna().sum())

actual_states = set(
    df["State"].dropna().unique()
)

missing_states = (
    EXPECTED_STATES - actual_states
)

if missing_states:

    print("\nERROR: Missing states:")
    print(sorted(missing_states))
    raise SystemExit

if df.isna().sum().sum() > 0:

    print("\nERROR: Missing values remain.")
    raise SystemExit

# ============================================================
# SAVE
# ============================================================

OUTPUT = os.path.join(
    DATA_FOLDER,
    "groundwater_6states_fixed.csv"
)

df["Date"] = df["Date"].dt.strftime(
    "%Y-%m-%d"
)

df.to_csv(
    OUTPUT,
    index=False
)

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print("Saved:")
print(OUTPUT)

print("\nFinal rows:", len(df))

print("\nFinal states:")
print(
    sorted(
        df["State"].unique()
    )
)

print("\nNext step:")
print("Use groundwater_6states_fixed.csv")
print("to add Goa August 2025.")