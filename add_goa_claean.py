import pandas as pd
import os

print("=" * 70)
print("ADD GOA AUGUST 2025 DATA")
print("=" * 70)

# ---------------------------------------------------------
# FILE NAMES
# ---------------------------------------------------------
main_file = "groundwater.csv"
goa_file = "goa_august_2025.csv"
output_file = "groundwater_updated.csv"

# ---------------------------------------------------------
# CHECK FILES
# ---------------------------------------------------------
if not os.path.exists(main_file):
    print(f"ERROR: {main_file} not found")
    exit()

if not os.path.exists(goa_file):
    print(f"ERROR: {goa_file} not found")
    print()
    print("Create this file first:")
    print(goa_file)
    exit()

# ---------------------------------------------------------
# REQUIRED COLUMNS
# ---------------------------------------------------------
required_columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

# ---------------------------------------------------------
# LOAD EXISTING DATA
# ---------------------------------------------------------
print("\n===== LOAD EXISTING DATA =====")

main_df = pd.read_csv(main_file)

print("Existing rows:", len(main_df))
print("Existing columns:", list(main_df.columns))

# ---------------------------------------------------------
# LOAD GOA DATA
# ---------------------------------------------------------
print("\n===== LOAD GOA AUGUST DATA =====")

goa_df = pd.read_csv(goa_file)

print("Goa rows:", len(goa_df))
print("Goa columns:", list(goa_df.columns))

# ---------------------------------------------------------
# CHECK COLUMNS
# ---------------------------------------------------------
if list(main_df.columns) != required_columns:
    print("\nERROR: groundwater.csv columns are incorrect.")
    print("Expected:")
    print(required_columns)
    exit()

if list(goa_df.columns) != required_columns:
    print("\nERROR: Goa CSV columns are incorrect.")
    print("Expected:")
    print(required_columns)
    exit()

# ---------------------------------------------------------
# FORCE STATE TO GOA
# ---------------------------------------------------------
goa_df["State"] = "Goa"

# ---------------------------------------------------------
# CONVERT NUMERIC COLUMNS
# ---------------------------------------------------------
for df in [main_df, goa_df]:
    df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
    df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")
    df["WL_mbgl"] = pd.to_numeric(df["WL_mbgl"], errors="coerce")

# ---------------------------------------------------------
# REMOVE COMPLETELY EMPTY ROWS
# ---------------------------------------------------------
main_df = main_df.dropna(how="all")
goa_df = goa_df.dropna(how="all")

# ---------------------------------------------------------
# REMOVE DUPLICATE GOA RECORDS
# ---------------------------------------------------------
goa_df = goa_df.drop_duplicates()

# ---------------------------------------------------------
# APPEND GOA DATA
# ---------------------------------------------------------
updated_df = pd.concat(
    [main_df, goa_df],
    ignore_index=True
)

# ---------------------------------------------------------
# SAVE
# ---------------------------------------------------------
updated_df.to_csv(output_file, index=False)

# ---------------------------------------------------------
# RESULTS
# ---------------------------------------------------------
print("\n===== SUCCESS =====")
print("Original rows :", len(main_df))
print("Goa rows added:", len(goa_df))
print("Final rows    :", len(updated_df))

print("\n===== STATE COUNTS =====")
print(updated_df["State"].value_counts())

print("\n===== GOA RECORDS =====")
print(
    updated_df[
        updated_df["State"].str.strip().str.lower() == "goa"
    ].to_string(index=False)
)

print("\nSaved as:")
print(output_file)