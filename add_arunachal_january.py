import pandas as pd

BASE = "groundwater_7states_corrected.csv"
NEW = "arunachal_january_2025.csv"
OUTPUT = "groundwater_with_arunachal_january.csv"

print("=" * 70)
print("ADD ARUNACHAL PRADESH JANUARY 2025 DATA")
print("=" * 70)

# Load existing dataset
df = pd.read_csv(BASE)

# Load January Arunachal data
new_df = pd.read_csv(NEW)

print("\nExisting records:", len(df))
print("New Arunachal records:", len(new_df))

# Make sure columns match
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

new_df = new_df[columns]

# Remove exact duplicates
before = len(new_df)

combined = pd.concat(
    [df, new_df],
    ignore_index=True
)

combined = combined.drop_duplicates()

duplicates_removed = (
    len(df) + len(new_df) - len(combined)
)

print("\nDuplicates removed:", duplicates_removed)

# Save
combined.to_csv(
    OUTPUT,
    index=False
)

print("\n===== SUCCESS =====")
print("Original records :", len(df))
print("January records  :", len(new_df))
print("Final records    :", len(combined))

print("\n===== STATE COUNTS =====")
print(combined["State"].value_counts())

print("\nSaved as:")
print(OUTPUT)