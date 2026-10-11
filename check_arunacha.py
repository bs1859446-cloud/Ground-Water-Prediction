import pandas as pd

FILE = "groundwater_7states_corrected.csv"

df = pd.read_csv(FILE)

print("=" * 70)
print("ARUNACHAL PRADESH CHECK")
print("=" * 70)

arun = df[df["State"].astype(str).str.strip() == "Arunachal Pradesh"]

print("Existing Arunachal records:", len(arun))

print("\nExisting records:")
print(arun.to_string(index=False))

print("\nTotal dataset records:", len(df))