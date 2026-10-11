import pandas as pd

BASE_FILE = "groundwater_with_arunachal_january.csv"
ASSAM_FILE = "assam_january_2025_fixed.csv"
OUTPUT_FILE = "groundwater_with_assam_january.csv"

print("=" * 70)
print("ADD ASSAM JANUARY 2025 DATA")
print("=" * 70)

base = pd.read_csv(BASE_FILE)
assam = pd.read_csv(ASSAM_FILE)

print(f"\nExisting records: {len(base)}")
print(f"Assam January records: {len(assam)}")

# Remove duplicates inside Assam file
before = len(assam)
assam = assam.drop_duplicates()
print(f"Duplicates inside Assam file removed: {before - len(assam)}")

# Combine
combined = pd.concat([base, assam], ignore_index=True)

print(f"\nRows before final duplicate check: {len(combined)}")

before = len(combined)
combined = combined.drop_duplicates()
print(f"Duplicate rows removed: {before - len(combined)}")

# Save
combined.to_csv(OUTPUT_FILE, index=False)

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print(f"Original records : {len(base)}")
print(f"Assam records    : {len(assam)}")
print(f"Final records    : {len(combined)}")

print("\n===== STATE COUNTS =====")
print(combined["State"].value_counts())

print("\n===== MISSING VALUES =====")
print(combined.isnull().sum())

print("\n===== DUPLICATES =====")
print("Duplicate rows:", combined.duplicated().sum())

print(f"\nSaved as:")
print(OUTPUT_FILE)