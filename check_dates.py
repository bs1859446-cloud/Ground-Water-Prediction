import pandas as pd
import os

INPUT_FILE = "groundwater_data.csv"
OUTPUT_FILE = "combined_groundwater_data.csv"

# ============================================================
# 1. LOAD DATA
# ============================================================

print("\n===== INITIAL DATA =====")

df = pd.read_csv(INPUT_FILE, dtype=str)

print("Rows loaded:", len(df))
print("Columns:", len(df.columns))
print("Column names:", list(df.columns))


# ============================================================
# 2. STANDARDIZE COLUMN NAMES
# ============================================================

df.columns = (
    df.columns
    .astype(str)
    .str.strip()
    .str.replace(" ", "_", regex=False)
    .str.replace("WL(mbgl)", "WL_mbgl", regex=False)
)

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

# Handle possible WL column names
if "WL_mbgl" not in df.columns:

    for col in df.columns:

        col_clean = (
            str(col)
            .replace(" ", "")
            .replace("(", "")
            .replace(")", "")
            .replace("/", "")
            .lower()
        )

        if "wl" in col_clean:

            df.rename(
                columns={col: "WL_mbgl"},
                inplace=True
            )

            break


# ============================================================
# 3. REPAIR OLD | SEPARATOR ROWS
# ============================================================

print("\n===== REPAIR CHECK =====")

new_rows = []

pipe_count = 0
repaired_count = 0
failed_count = 0

for _, row in df.iterrows():

    state_value = str(row.get("State", ""))

    # --------------------------------------------------------
    # Old Bihar rows stored entirely inside State column
    # --------------------------------------------------------

    if "|" in state_value:

        pipe_count += 1

        values = [
            value.strip()
            for value in state_value.split("|")
        ]

        if len(values) == 8:

            new_row = dict(
                zip(required_columns, values)
            )

            new_rows.append(new_row)

            repaired_count += 1

        else:

            failed_count += 1

    else:

        new_row = {}

        for column in required_columns:

            if column in df.columns:

                new_row[column] = row[column]

            else:

                new_row[column] = pd.NA

        new_rows.append(new_row)


print(
    "Rows containing | separator:",
    pipe_count
)

print(
    "Successfully repaired:",
    repaired_count
)

print(
    "Failed repairs:",
    failed_count
)


# ============================================================
# 4. CREATE CLEAN DATAFRAME
# ============================================================

df = pd.DataFrame(
    new_rows,
    columns=required_columns
)


# ============================================================
# 5. CLEAN TEXT
# ============================================================

text_columns = [
    "State",
    "District",
    "Block",
    "Village"
]

for column in text_columns:

    df[column] = (
        df[column]
        .astype("string")
        .str.strip()
    )

    df[column] = df[column].replace(
        ["", "nan", "None"],
        pd.NA
    )


# ============================================================
# 6. CLEAN NUMERIC DATA
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
# 7. DATE CLEANING
# ============================================================

print("\n===== DATE CHECK =====")

# Explicitly handle the known DD-MM-YY / DD-MM-YYYY formats
df["Date"] = (
    df["Date"]
    .astype("string")
    .str.strip()
)

df["Date"] = pd.to_datetime(
    df["Date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

missing_dates = df["Date"].isna().sum()

print(
    "Missing/invalid dates:",
    missing_dates
)

print("\nUnique dates:")

unique_dates = (
    df["Date"]
    .dropna()
    .dt.strftime("%d-%m-%Y")
    .unique()
)

for date in sorted(unique_dates):

    print(date)


# ============================================================
# 8. LOCATIONS BY DATE
# ============================================================

print("\n===== LOCATIONS BY DATE =====")

valid_date_df = df.dropna(
    subset=["Date"]
).copy()

valid_date_df["Date_only"] = (
    valid_date_df["Date"]
    .dt.strftime("%Y-%m-%d")
)

location_count = (
    valid_date_df
    .groupby("Date_only")
    [["Latitude", "Longitude"]]
    .apply(
        lambda x:
        x.drop_duplicates().shape[0]
    )
)

print(location_count)


# ============================================================
# 9. STATE CHECK
# ============================================================

print("\n===== STATE CHECK =====")

state_counts = (
    df["State"]
    .value_counts(dropna=False)
)

print(state_counts)


# ============================================================
# 10. REQUIRED FIVE STATE CHECK
# ============================================================

print("\n===== REQUIRED FIVE STATE CHECK =====")

required_states = [
    "Kerala",
    "Bihar",
    "Andhra Pradesh",
    "Assam",
    "Arunachal Pradesh"
]

state_normalized = (
    df["State"]
    .astype("string")
    .str.strip()
    .str.lower()
)

for state in required_states:

    count = (
        state_normalized
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
# 11. STATE SUMMARY
# ============================================================

print("\n===== STATE SUMMARY =====")

valid_states = (
    df["State"]
    .dropna()
    .unique()
)

print(
    "Total unique states:",
    len(valid_states)
)

print("\nAll states in dataset:")

print(
    df["State"]
    .value_counts()
)


# ============================================================
# 12. CHECK PIPE ERRORS
# ============================================================

print("\n===== PIPE ERROR CHECK =====")

remaining_pipe_rows = df[
    df["State"]
    .astype(str)
    .str.contains(
        r"\|",
        regex=True,
        na=False
    )
]

print(
    "Remaining rows containing |:",
    len(remaining_pipe_rows)
)

if len(remaining_pipe_rows) > 0:

    print(
        remaining_pipe_rows.to_string(
            index=False
        )
    )


# ============================================================
# 13. DUPLICATE CHECK
# ============================================================

print("\n===== DUPLICATES =====")

duplicate_count = df.duplicated().sum()

print(
    "Duplicate rows:",
    duplicate_count
)


# ============================================================
# 14. UNIQUE LOCATIONS
# ============================================================

print("\n===== UNIQUE LOCATIONS =====")

print(
    "Unique villages:",
    df["Village"].nunique()
)

print(
    "Unique coordinates:",
    df[
        ["Latitude", "Longitude"]
    ]
    .drop_duplicates()
    .shape[0]
)


# ============================================================
# 15. MISSING VALUES
# ============================================================

print("\n===== MISSING VALUES =====")

missing_values = df.isna().sum()

print(missing_values)


# ============================================================
# 16. INCOMPLETE RECORDS
# ============================================================

print("\n===== INCOMPLETE RECORDS =====")

incomplete = df[
    df[required_columns]
    .isna()
    .any(axis=1)
]

print(
    "Incomplete rows:",
    len(incomplete)
)

if len(incomplete) > 0:

    print("\nIncomplete records:")

    print(
        incomplete.to_string(
            index=False
        )
    )


# ============================================================
# 17. GROUNDWATER LEVEL CHECK
# ============================================================

print("\n===== GROUNDWATER LEVEL CHECK =====")

valid_wl = df[
    "WL_mbgl"
].dropna()

if len(valid_wl) > 0:

    print(
        "Minimum WL:",
        valid_wl.min()
    )

    print(
        "Maximum WL:",
        valid_wl.max()
    )

    print(
        "Average WL:",
        valid_wl.mean()
    )

else:

    print(
        "No valid groundwater levels found."
    )


# ============================================================
# 18. COORDINATE CHECK
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

if len(invalid_coordinates) > 0:

    print(
        "\nInvalid coordinate records:"
    )

    print(
        invalid_coordinates.to_string(
            index=False
        )
    )


# ============================================================
# 19. FIVE STATE ROW COUNT
# ============================================================

print("\n===== FIVE STATE ROW COUNT =====")

for state in required_states:

    count = (
        state_normalized
        .eq(state.lower())
        .sum()
    )

    print(
        f"{state}: {count}"
    )


# ============================================================
# 20. FINAL DATASET CHECK
# ============================================================

print("\n===== FINAL DATASET =====")

print(
    "Total rows:",
    len(df)
)

print(
    "Total columns:",
    len(df.columns)
)

print(
    "Missing dates:",
    df["Date"].isna().sum()
)


# ============================================================
# 21. EXPECTED ROW COUNT
# ============================================================

print("\n===== ROW COUNT CHECK =====")

expected_original = 84
expected_assam = 52
expected_arunachal = 28

expected_total = (
    expected_original
    + expected_assam
    + expected_arunachal
)

print(
    "Original dataset rows:",
    expected_original
)

print(
    "Expected Assam rows:",
    expected_assam
)

print(
    "Expected Arunachal Pradesh rows:",
    expected_arunachal
)

print(
    "Expected total rows:",
    expected_total
)

print(
    "Actual total rows:",
    len(df)
)

if len(df) == expected_total:

    print(
        "ROW COUNT STATUS: OK"
    )

else:

    print(
        "ROW COUNT STATUS: CHECK REQUIRED"
    )


# ============================================================
# 22. SAVE CLEAN DATASET
# ============================================================

# Save dates as DD-MM-YYYY
df["Date"] = (
    df["Date"]
    .dt.strftime("%d-%m-%Y")
)

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 23. FINAL ACTION
# ============================================================

print("\n===== ACTION COMPLETED =====")

print(
    "Cleaned dataset saved as:"
)

print(
    OUTPUT_FILE
)

print("\nStates included:")

for state in sorted(
    df["State"]
    .dropna()
    .unique()
):

    print(
        "-",
        state
    )


# ============================================================
# 24. FINAL STATUS
# ============================================================

print("\n===== FINAL STATUS =====")

if (
    len(df) == expected_total
    and
    all(
        state_normalized.eq(
            state.lower()
        ).sum() > 0
        for state in required_states
    )
):

    print(
        "ALL FIVE STATES ARE PRESENT."
    )

    print(
        "TOTAL ROW COUNT: 164"
    )

else:

    print(
        "DATASET REQUIRES CHECKING."
    )