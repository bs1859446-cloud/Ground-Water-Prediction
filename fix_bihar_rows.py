import pandas as pd

INPUT_FILE = "groundwater_updated.csv"
OUTPUT_FILE = "groundwater_clean.csv"

print("=" * 70)
print("FIX MALFORMED BIHAR RECORDS")
print("=" * 70)

# ---------------------------------------------------------
# LOAD DATA
# ---------------------------------------------------------
df = pd.read_csv(INPUT_FILE)

print("\nOriginal rows:", len(df))

# ---------------------------------------------------------
# FIND MALFORMED ROWS
# ---------------------------------------------------------
# A malformed Bihar row has the entire record inside State
# and contains the "|" separator.
malformed = df["State"].astype(str).str.contains(r"\|", regex=True)

print("Malformed rows found:", malformed.sum())

# ---------------------------------------------------------
# DISPLAY MALFORMED ROWS
# ---------------------------------------------------------
if malformed.sum() > 0:
    print("\n===== MALFORMED ROWS =====")
    print(df.loc[malformed, "State"].to_string(index=False))

# ---------------------------------------------------------
# EXTRACT AND REBUILD MALFORMED ROWS
# ---------------------------------------------------------
fixed_rows = []

for value in df.loc[malformed, "State"]:

    parts = [x.strip() for x in str(value).split("|")]

    if len(parts) != 8:
        print("\nWARNING: Could not repair:")
        print(value)
        continue

    fixed_rows.append({
        "State": parts[0],
        "District": parts[1],
        "Block": parts[2],
        "Village": parts[3],
        "Latitude": parts[4],
        "Longitude": parts[5],
        "Date": parts[6],
        "WL_mbgl": parts[7]
    })

# ---------------------------------------------------------
# REMOVE MALFORMED ROWS
# ---------------------------------------------------------
df_clean = df.loc[~malformed].copy()

# ---------------------------------------------------------
# ADD REPAIRED ROWS
# ---------------------------------------------------------
if fixed_rows:
    fixed_df = pd.DataFrame(fixed_rows)

    df_clean = pd.concat(
        [df_clean, fixed_df],
        ignore_index=True
    )

# ---------------------------------------------------------
# CONVERT DATA TYPES
# ---------------------------------------------------------
df_clean["Latitude"] = pd.to_numeric(
    df_clean["Latitude"],
    errors="coerce"
)

df_clean["Longitude"] = pd.to_numeric(
    df_clean["Longitude"],
    errors="coerce"
)

df_clean["WL_mbgl"] = pd.to_numeric(
    df_clean["WL_mbgl"],
    errors="coerce"
)

# ---------------------------------------------------------
# CLEAN TEXT
# ---------------------------------------------------------
text_columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Date"
]

for column in text_columns:
    df_clean[column] = (
        df_clean[column]
        .astype(str)
        .str.strip()
    )

# ---------------------------------------------------------
# REMOVE DUPLICATES
# ---------------------------------------------------------
before_duplicates = len(df_clean)

df_clean = df_clean.drop_duplicates()

duplicates_removed = before_duplicates - len(df_clean)

# ---------------------------------------------------------
# RESET INDEX
# ---------------------------------------------------------
df_clean = df_clean.reset_index(drop=True)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
df_clean.to_csv(
    OUTPUT_FILE,
    index=False
)

# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------
print("\n===== CLEANING COMPLETE =====")

print("Original rows       :", len(df))
print("Malformed repaired  :", len(fixed_rows))
print("Duplicates removed  :", duplicates_removed)
print("Final rows          :", len(df_clean))

print("\n===== COLUMN CHECK =====")
print(df_clean.columns.tolist())

print("\n===== STATE COUNTS =====")
print(df_clean["State"].value_counts())

print("\n===== REPAIRED BIHAR RECORDS =====")
print(
    df_clean[
        (df_clean["State"] == "Bihar") &
        (df_clean["Date"] == "30-08-25")
    ].to_string(index=False)
)

print("\n===== GOA CHECK =====")
goa = df_clean[df_clean["State"] == "Goa"]

print("Goa records:", len(goa))

print(goa.head().to_string(index=False))

print("\nSaved as:")
print(OUTPUT_FILE)