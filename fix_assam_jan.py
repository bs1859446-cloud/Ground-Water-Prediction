import pandas as pd

INPUT_FILE = "assam_january_2025.csv"
OUTPUT_FILE = "assam_january_2025_fixed.csv"

print("=" * 70)
print("FIX ASSAM JANUARY 2025 DATA")
print("=" * 70)

df = pd.read_csv(INPUT_FILE)

print("\nOriginal columns:")
print(df.columns.tolist())

print("Original rows:", len(df))

# The records are stored as text separated by |
# Convert each row into 8 proper columns

rows = []

for value in df.iloc[:, 0]:

    if pd.isna(value):
        continue

    value = str(value).strip()

    # Remove numbering such as "1. "
    if ". " in value[:6]:
        value = value.split(". ", 1)[1]

    parts = [x.strip() for x in value.split("|")]

    if len(parts) != 8:
        print("WARNING - Invalid row:")
        print(value)
        print("Fields found:", len(parts))
        continue

    rows.append(parts)

columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

fixed = pd.DataFrame(rows, columns=columns)

# Convert numeric columns
fixed["Latitude"] = pd.to_numeric(fixed["Latitude"], errors="coerce")
fixed["Longitude"] = pd.to_numeric(fixed["Longitude"], errors="coerce")
fixed["WL_mbgl"] = pd.to_numeric(fixed["WL_mbgl"], errors="coerce")

# Remove accidental duplicate records
before = len(fixed)
fixed = fixed.drop_duplicates()
duplicates = before - len(fixed)

print("\n" + "=" * 70)
print("FIX COMPLETE")
print("=" * 70)

print("Valid Assam records:", len(fixed))
print("Duplicates removed:", duplicates)

print("\nColumns:")
print(fixed.columns.tolist())

print("\nFirst 10 records:")
print(fixed.head(10).to_string(index=False))

print("\nState count:")
print(fixed["State"].value_counts())

print("\nMissing values:")
print(fixed.isnull().sum())

fixed.to_csv(OUTPUT_FILE, index=False)

print("\nSaved as:")
print(OUTPUT_FILE)