import pandas as pd

# ============================================================
# 1. INPUT / OUTPUT FILES
# ============================================================

INPUT_FILE = "groundwater_with_assam.csv"
OUTPUT_FILE = "groundwater_with_5_states.csv"


# ============================================================
# 2. LOAD EXISTING 136-ROW DATASET
# ============================================================

print("\n===== LOAD EXISTING DATA =====")

df = pd.read_csv(INPUT_FILE, dtype=str)

print("Existing rows:", len(df))


# ============================================================
# 3. ARUNACHAL PRADESH DATA
# ============================================================

arunachal_data = """State,District,Block,Village,Latitude,Longitude,Date,WL_mbgl
Arunachal Pradesh,Changlang,Changlang,Jairampur,27.20833,96.04166,30-08-25,3.00
Arunachal Pradesh,Changlang,Changlang,Namchik,27.41667,96.04583,30-08-25,1.39
Arunachal Pradesh,Changlang,Khagam-Miao,Namphai,27.45833,96.10833,30-08-25,1.56
Arunachal Pradesh,Changlang,Khagam-Miao,Newlisan Kharsang,27.50000,96.13333,30-08-25,3.92
Arunachal Pradesh,East Siang,Pasighat,Pasighat,28.15139,95.29583,30-08-25,5.67
Arunachal Pradesh,East Siang,Pasighat,Pasighat,27.06444,95.31028,30-08-25,5.67
Arunachal Pradesh,East Siang,Pasighat,Satmile,27.97672,95.33163,30-08-25,1.25
Arunachal Pradesh,East Siang,Ruksin,Oyan,27.89022,95.31833,30-08-25,6.24
Arunachal Pradesh,East Siang,Ruksin,Ruksin,27.83778,95.21817,30-08-25,0.50
Arunachal Pradesh,East Siang,Ruksin,Sika Baman Todee 1,27.89778,95.32389,30-08-25,1.86
Arunachal Pradesh,Kamle,Tamen-Raga,Bomte,27.48950,94.19442,30-08-25,0.43
Arunachal Pradesh,Lohit,Wakro,Medo,27.79096,96.17737,30-08-25,0.17
Arunachal Pradesh,Lower Dibang Valley,Roing,Kangklong,27.97171,95.75741,30-08-25,1.60
Arunachal Pradesh,Lower Subansiri,Ziro-I,Rajgarh,27.40475,94.15225,30-08-25,0.47
Arunachal Pradesh,Namsai,Namsai,Adi Ningroo,27.63561,95.90167,30-08-25,2.88
Arunachal Pradesh,Namsai,Namsai,Lathow,27.66667,95.87500,30-08-25,4.67
Arunachal Pradesh,Namsai,Namsai,Wingko,27.63077,95.94920,30-08-25,0.41
Arunachal Pradesh,Papum Pare,Balijan,Holangi,26.96228,93.59205,30-08-25,1.27
Arunachal Pradesh,Papum Pare,Balijan,Sonajuli,27.02814,93.74130,30-08-25,0.98
Arunachal Pradesh,Papum Pare,Borum,Naharlagun,27.10306,93.69473,30-08-25,5.53
Arunachal Pradesh,Papum Pare,Borum,Nirjuli,27.13111,93.73306,30-08-25,0.38
Arunachal Pradesh,Papum Pare,Borum,Nirjuli,27.13000,93.73361,30-08-25,0.58
Arunachal Pradesh,Papum Pare,Doimukh,Banderdewa,27.10528,93.82584,30-08-25,11.13
Arunachal Pradesh,Papum Pare,Doimukh,Doimukh,27.15000,93.75000,30-08-25,0.89
Arunachal Pradesh,Papum Pare,Kimin,Kimin,27.30428,93.97071,30-08-25,0.14
Arunachal Pradesh,Tirap,Borduria,Borduria,27.01667,95.46667,30-08-25,4.32
Arunachal Pradesh,Tirap,Borduria,Hukanjuri,27.00833,95.46667,30-08-25,3.93
Arunachal Pradesh,Tirap,Namsang,Deomali,27.20000,95.52500,30-08-25,3.05
"""


# ============================================================
# 4. READ ARUNACHAL DATA
# ============================================================

from io import StringIO

arunachal_df = pd.read_csv(
    StringIO(arunachal_data),
    dtype=str
)

print("\n===== ARUNACHAL PRADESH DATA =====")
print("Arunachal Pradesh rows:", len(arunachal_df))


# ============================================================
# 5. CHECK ARUNACHAL ROW COUNT
# ============================================================

if len(arunachal_df) != 28:
    print("WARNING: Expected 28 Arunachal Pradesh rows!")
else:
    print("Arunachal Pradesh row count: OK")


# ============================================================
# 6. COMBINE DATA
# ============================================================

df = pd.concat(
    [df, arunachal_df],
    ignore_index=True
)


# ============================================================
# 7. CLEAN COLUMN NAMES
# ============================================================

df.columns = [
    str(col).strip()
    .replace("WL(mbgl)", "WL_mbgl")
    .replace(" ", "_")
    for col in df.columns
]


# ============================================================
# 8. CHECK FIVE REQUIRED STATES
# ============================================================

print("\n===== FIVE STATE CHECK =====")

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
        .astype(str)
        .str.strip()
        .str.lower()
        .eq(state.lower())
        .sum()
    )

    status = "OK" if count > 0 else "MISSING"

    print(f"{state}: {count} rows - {status}")


# ============================================================
# 9. STATE SUMMARY
# ============================================================

print("\n===== STATE SUMMARY =====")

print(
    df["State"].value_counts()
)


# ============================================================
# 10. CHECK MISSING VALUES
# ============================================================

print("\n===== MISSING VALUES =====")

print(
    df.isna().sum()
)


# ============================================================
# 11. CONVERT NUMERIC COLUMNS
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
# 12. DATE CHECK
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

print("\nUnique dates:")

print(
    df["Date"]
    .dropna()
    .dt.strftime("%d-%m-%Y")
    .unique()
)


# ============================================================
# 13. DUPLICATE CHECK
# ============================================================

print("\n===== DUPLICATES =====")

print(
    "Duplicate rows:",
    df.duplicated().sum()
)


# ============================================================
# 14. COORDINATE CHECK
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
# 15. GROUNDWATER LEVEL CHECK
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
# 16. FINAL ROW COUNT CHECK
# ============================================================

print("\n===== ROW CHECK =====")

original_rows = 136
arunachal_rows = len(arunachal_df)

expected_rows = (
    original_rows +
    arunachal_rows
)

actual_rows = len(df)

print("Previous dataset rows:", original_rows)
print("Arunachal Pradesh rows:", arunachal_rows)
print("Expected total rows:", expected_rows)
print("Actual total rows:", actual_rows)

if expected_rows == actual_rows:
    print("ROW COUNT STATUS: OK")
else:
    print("ROW COUNT STATUS: CHECK REQUIRED")


# ============================================================
# 17. SAVE FINAL DATASET
# ============================================================

df["Date"] = df["Date"].dt.strftime("%d-%m-%Y")

df.to_csv(
    OUTPUT_FILE,
    index=False
)


# ============================================================
# 18. FINAL STATUS
# ============================================================

print("\n===== ACTION COMPLETED =====")

print(
    "Final dataset saved as:"
)

print(OUTPUT_FILE)

print("\nFinal states:")

for state in sorted(
    df["State"].dropna().unique()
):
    print("-", state)


print("\n===== FINAL TOTAL =====")
print("Total rows:", len(df))
print("Total columns:", len(df.columns))

if len(df) == 164:
    print("FINAL STATUS: SUCCESS")
    print("All 5 states are combined successfully.")
else:
    print("FINAL STATUS: CHECK REQUIRED")