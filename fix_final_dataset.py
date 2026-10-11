import pandas as pd

INPUT_FILE = "groundwater_with_5_states.csv"
OUTPUT_FILE = "final_groundwater_dataset.csv"

# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n===== LOAD FINAL DATA =====")

df = pd.read_csv(INPUT_FILE, dtype=str)

print("Rows loaded:", len(df))


# ============================================================
# 2. REPAIR PIPE ROWS
# ============================================================

print("\n===== REPAIR PIPE ROWS =====")

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

repaired = 0
failed = 0

new_rows = []

for _, row in df.iterrows():

    state_value = str(row["State"])

    if "|" in state_value:

        values = [
            x.strip()
            for x in state_value.split("|")
        ]

        if len(values) == 8:

            new_row = dict(zip(columns, values))

            new_rows.append(new_row)

            repaired += 1

        else:

            new_rows.append(
                row.to_dict()
            )

            failed += 1

    else:

        new_rows.append(
            row.to_dict()
        )


df = pd.DataFrame(
    new_rows,
    columns=columns
)


print("Rows repaired:", repaired)
print("Failed repairs:", failed)


# ============================================================
# 3. CONVERT NUMERIC COLUMNS
# ============================================================

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
# 4. DATE CHECK
# ============================================================

print("\n===== DATE CHECK =====")

df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

print(
    "Missing/invalid dates:",
    df["Date"].isna().sum()
)


# ============================================================
# 5. STATE CHECK
# ============================================================

print("\n===== FINAL STATE CHECK =====")

state_counts = (
    df["State"]
    .str.strip()
    .value_counts()
)

print(state_counts)


# ============================================================
# 6. REQUIRED FIVE STATES
# ============================================================

print("\n===== REQUIRED FIVE STATE CHECK =====")

required_states = [
    "Kerala",
    "Bihar",
    "Andhra Pradesh",
    "Assam",
    "Arunachal Pradesh"
]

for state in required_states:

    count = (
        df["State"]
        .str.strip()
        .str.lower()
        .eq(state.lower())
        .sum()
    )

    if count > 0:
        status = "OK"
    else:
        status = "MISSING"

    print(
        f"{state}: {count} rows - {status}"
    )


# ============================================================
# 7. CHECK REMAINING PIPE ROWS
# ============================================================

print("\n===== PIPE ERROR CHECK =====")

remaining = df[
    df["State"]
    .astype(str)
    .str.contains(
        r"\|",
        regex=True,
        na=False
    )
]

print(
    "Remaining pipe rows:",
    len(remaining)
)


# ============================================================
# 8. MISSING VALUES
# ============================================================

print("\n===== MISSING VALUES =====")

print(
    df.isna().sum()
)


# ============================================================
# 9. DUPLICATES
# ============================================================

print("\n===== DUPLICATES =====")

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


# ============================================================
# 10. GROUNDWATER CHECK
# ============================================================

print("\n===== GROUNDWATER LEVEL CHECK =====")

print(
    "Minimum WL:",
    df["WL_mbgl"].min()
)

print(
    "Maximum WL:",
    df["WL_mbgl"].max()
)

print(
    "Average WL:",
    df["WL_mbgl"].mean()
)


# ============================================================
# 11. COORDINATE CHECK
# ============================================================

print("\n===== COORDINATE CHECK =====")

invalid_coordinates = df[
    df["Latitude"].isna()
    |
    df["Longitude"].isna()
    |
    (df["Latitude"] < -90)
    |
    (df["Latitude"] > 90)
    |
    (df["Longitude"] < -180)
    |
    (df["Longitude"] > 180)
]

print(
    "Invalid coordinates:",
    len(invalid_coordinates)
)


# ============================================================
# 12. FINAL ROW CHECK
# ============================================================

print("\n===== FINAL ROW CHECK =====")

expected_rows = 164
actual_rows = len(df)

print("Expected rows:", expected_rows)
print("Actual rows:", actual_rows)

if expected_rows == actual_rows:
    print("ROW COUNT STATUS: OK")
else:
    print("ROW COUNT STATUS: CHECK REQUIRED")


# ============================================================
# 13. SAVE FINAL DATASET
# ============================================================

df["Date"] = df["Date"].dt.strftime(
    "%d-%m-%Y"
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 14. FINAL STATUS
# ============================================================

print("\n===== ACTION COMPLETED =====")

print(
    "Final dataset saved as:"
)

print(OUTPUT_FILE)

print("\n===== FINAL STATUS =====")

if (
    len(df) == 164
    and repaired == 18
    and len(remaining) == 0
    and df["Date"].isna().sum() == 0
    and df["Latitude"].isna().sum() == 0
    and df["Longitude"].isna().sum() == 0
    and df["WL_mbgl"].isna().sum() == 0
):
    print("SUCCESS")
    print("All 164 records are valid.")
else:
    print("CHECK REQUIRED")