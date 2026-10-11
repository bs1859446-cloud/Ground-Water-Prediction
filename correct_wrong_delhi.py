import pandas as pd

INPUT = "groundwater_7states_final.csv"
OUTPUT = "groundwater_7states_corrected.csv"

df = pd.read_csv(INPUT)

# Identify the incorrect Delhi record by its exact coordinates
mask = (
    (df["Latitude"] == 20.7242) &
    (df["Longitude"] == 70.9306) &
    (df["State"].astype(str).str.strip() == "Delhi")
)

print("Records found:", mask.sum())

if mask.sum() != 1:
    print("ERROR: Expected exactly 1 incorrect record.")
    exit()

# Correct the geographical information
df.loc[mask, "State"] = "Dnh"
df.loc[mask, "District"] = "Diu"
df.loc[mask, "Block"] = pd.NA
df.loc[mask, "Village"] = "Zolawadi"

# Save corrected dataset
df.to_csv(OUTPUT, index=False)

print("\n===== CORRECTION COMPLETE =====")
print(df.loc[mask].to_string(index=False))

print("\nTotal records:", len(df))
print("\nState counts:")
print(df["State"].value_counts())

print("\nSaved as:")
print(OUTPUT)