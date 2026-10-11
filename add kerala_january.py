import pandas as pd
import re
from io import StringIO

print("=" * 70)
print("ADD KERALA JANUARY 2025 TO EXISTING GROUNDWATER DATASET")
print("=" * 70)

# ============================================================
# 1. EXISTING DATASET
# ============================================================

INPUT_FILE = "groundwater_with_goa_january.csv"
OUTPUT_FILE = "groundwater_with_kerala_january.csv"

df_existing = pd.read_csv(INPUT_FILE)

print("\n===== LOAD EXISTING DATA =====")
print("Existing records:", len(df_existing))


# ============================================================
# 2. KERALA JANUARY 2025 DATA
# ============================================================
# Paste ALL Kerala records inside these triple quotes.
#
# Format:
# Kerala District Block Village Latitude Longitude Date WL
#
# Do NOT put commas between values.
# ============================================================

KERALA_DATA = r"""
Kerala Alappuzha Ambalappuzha Ambalappuzha 9.38347 76.3707 10-01-25 1.39
Kerala Alappuzha Ambalappuzha Kaidavana 9.40773 76.3508 10-01-25 1.96
Kerala Alappuzha Ambalappuzha Naduvattom 9.271781 76.48147 10-01-25 1.27
Kerala Alappuzha Ambalappuzha Punnapra 9.43259 76.3454 10-01-25 1.53
Kerala Alappuzha Ambalappuzha Purakkad 9.353172 76.37267 10-01-25 2.55
Kerala Alappuzha Ambalappuzha Vandanam 9.41366 76.3494 10-01-25 1.88
Kerala Alappuzha Aryad Alappuzha Beach 9.49409 76.3209 10-01-25 1.94
Kerala Alappuzha Aryad Alappuzha Town 9.49519 76.3341 10-01-25 4.24
Kerala Alappuzha Aryad Aryad 9.57193 76.3471 10-01-25 2.25
Kerala Alappuzha Aryad Kaidavana 9.47298 76.3436 10-01-25 1.08
Kerala Alappuzha Aryad Kalavoor 9.56774 76.3272 10-01-25 0.99
Kerala Alappuzha Aryad Kattoor 9.55 76.32 10-01-25 1.08
Kerala Alappuzha Aryad Mannanchery 9.62493 76.3671 10-01-25 1.49
Kerala Alappuzha Aryad Valavanad 9.58957 76.3278 10-01-25 1.17

# ============================================================
# PASTE THE REST OF YOUR KERALA JANUARY RECORDS HERE
# ============================================================

"""


# ============================================================
# 3. CLEAN REPEATED HEADINGS
# ============================================================

KERALA_DATA = re.sub(
    r"January month Depth to Water Level.*?Aquifer",
    "",
    KERALA_DATA,
    flags=re.IGNORECASE
)

KERALA_DATA = re.sub(
    r"State\s+District\s+Block\s+Village\s+Latitute\s+Longitude\s+Date\s+WL\(mbgl\)",
    "",
    KERALA_DATA,
    flags=re.IGNORECASE
)

# Remove blank lines
KERALA_DATA = re.sub(r"\n\s*\n", "\n", KERALA_DATA)


# ============================================================
# 4. EXTRACT KERALA RECORDS
# ============================================================

# Each record ends with:
# Latitude Longitude Date WL

pattern = re.compile(
    r"Kerala\s+"
    r"(\S+)\s+"                  # District
    r"(\S+)\s+"                  # Block
    r"(.+?)\s+"                  # Village
    r"(\d+(?:\.\d+)?)\s+"        # Latitude
    r"(\d+(?:\.\d+)?)\s+"        # Longitude
    r"(\d{2}-\d{2}-\d{2})\s+"    # Date
    r"(\d+(?:\.\d+)?)"           # WL
)

records = []

for match in pattern.finditer(KERALA_DATA):

    district = match.group(1)
    block = match.group(2)
    village = match.group(3).strip()

    latitude = float(match.group(4))
    longitude = float(match.group(5))
    date = match.group(6)
    wl = float(match.group(7))

    records.append([
        "Kerala",
        district,
        block,
        village,
        latitude,
        longitude,
        date,
        wl
    ])


# ============================================================
# 5. CREATE KERALA DATAFRAME
# ============================================================

df_kerala = pd.DataFrame(
    records,
    columns=[
        "State",
        "District",
        "Block",
        "Village",
        "Latitude",
        "Longitude",
        "Date",
        "WL_mbgl"
    ]
)

print("\n===== KERALA DATA =====")
print("Kerala records found:", len(df_kerala))


# ============================================================
# 6. CHECK KERALA DATA
# ============================================================

print("\n===== KERALA FIRST 5 =====")
print(df_kerala.head().to_string(index=False))

print("\n===== KERALA LAST 5 =====")
print(df_kerala.tail().to_string(index=False))

print("\nKerala missing values:")
print(df_kerala.isnull().sum())

print("\nKerala duplicates:")
print(df_kerala.duplicated().sum())


# ============================================================
# 7. COMBINE EXISTING + KERALA
# ============================================================

df_final = pd.concat(
    [df_existing, df_kerala],
    ignore_index=True
)

print("\n===== COMBINE DATA =====")
print("Existing records :", len(df_existing))
print("Kerala records   :", len(df_kerala))
print("Combined records :", len(df_final))


# ============================================================
# 8. FINAL DUPLICATE CHECK
# ============================================================

duplicate_count = df_final.duplicated().sum()

print("\n===== FINAL DUPLICATES =====")
print("Duplicate rows:", duplicate_count)

# We remove only exact duplicate rows.
if duplicate_count > 0:
    df_final = df_final.drop_duplicates().reset_index(drop=True)


# ============================================================
# 9. FINAL STATE COUNTS
# ============================================================

print("\n===== STATE COUNTS =====")
print(df_final["State"].value_counts())


# ============================================================
# 10. MISSING VALUES
# ============================================================

print("\n===== MISSING VALUES =====")
print(df_final.isnull().sum())


# ============================================================
# 11. DATE RANGE
# ============================================================

df_final["Date"] = pd.to_datetime(
    df_final["Date"],
    dayfirst=True,
    errors="coerce"
)

print("\n===== DATE RANGE =====")
print("Earliest:", df_final["Date"].min())
print("Latest  :", df_final["Date"].max())


# ============================================================
# 12. SAVE FINAL DATASET
# ============================================================

df_final.to_csv(
    OUTPUT_FILE,
    index=False,
    date_format="%d-%m-%y"
)

print("\n" + "=" * 70)
print("SUCCESS")
print("=" * 70)

print("Original records :", len(df_existing))
print("Kerala records   :", len(df_kerala))
print("Final records    :", len(df_final))

print("\nSaved as:")
print(OUTPUT_FILE)

print("=" * 70)