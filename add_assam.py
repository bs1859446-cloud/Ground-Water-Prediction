import pandas as pd

INPUT_FILE = "groundwater_data.csv"
OUTPUT_FILE = "groundwater_with_assam.csv"

# ============================================================
# LOAD EXISTING DATA
# ============================================================

df = pd.read_csv(INPUT_FILE, dtype=str)

print("Original rows:", len(df))


# ============================================================
# ASSAM DATA - 52 RECORDS
# ============================================================

assam_data = """State,District,Block,Village,Latitude,Longitude,Date,WL_mbgl
Assam,Tirap,Namsang,Deomali,27.20000,95.52500,30-08-25,3.05
Assam,Bajali,Bajali,Tihu,26.47500,91.25750,30-08-25,1.45
Assam,Bajali,Bhabanipur,Bhabanipur,26.45779,91.06548,30-08-25,2.18
Assam,Bajali,Bhabanipur,Dakshin Hati,26.31835,91.01424,30-08-25,3.41
Assam,Bajali,Bhabanipur,Galia,26.49000,90.60000,30-08-25,4.36
Assam,Bajali,Bhabanipur,Sarupeta,26.49861,91.07500,30-08-25,2.75
Assam,Baksa,Baksa,Lokpala,26.62028,91.39833,30-08-25,1.80
Assam,Baksa,Baksa,Uzanbari Village,26.64972,91.04417,30-08-25,0.92
Assam,Baksa,Barama,Makharia,26.33983,91.36639,30-08-25,0.98
Assam,Baksa,Baska,Aithabari,26.73472,91.35833,30-08-25,7.43
Assam,Baksa,Baska,Arnibil,26.74990,91.35662,30-08-25,13.92
Assam,Baksa,Baska,Charaimari,26.67700,91.29400,30-08-25,2.65
Assam,Baksa,Baska,Pub Bengabari,26.67900,91.34700,30-08-25,3.64
Assam,Baksa,Baska,Shripur Deor,26.61800,91.34400,30-08-25,1.14
Assam,Baksa,Baska,Sonapur (Doomni),26.71374,91.30647,30-08-25,2.01
Assam,Baksa,Gobardhana,Gyati Gaon,26.65935,90.99915,30-08-25,3.20
Assam,Baksa,Gobardhana,Khusurabari,26.58222,91.02444,30-08-25,3.28
Assam,Baksa,Jalah,Bangalipara,26.71500,91.71194,30-08-25,3.42
Assam,Baksa,Jalah,Chapla,26.73389,91.71111,30-08-25,7.24
Assam,Barpeta,Chakchaka,Sorbhog,26.47500,90.90278,30-08-25,2.44
Assam,Barpeta,Chenga,Daulasal,26.27208,91.21403,30-08-25,0.54
Assam,Barpeta,Chenga,Daulasal,26.27097,91.22075,30-08-25,1.53
Assam,Barpeta,Gobardhana,Howly,26.41294,90.97851,30-08-25,1.81
Assam,Barpeta,Gobardhana,Ujanborbori,26.60000,91.10000,30-08-25,2.56
Assam,Barpeta,Gomaphulbari,Sila,26.28710,91.07473,30-08-25,3.09
Assam,Barpeta,Mandia,Bhakatpara,26.31497,91.00478,30-08-25,2.97
Assam,Barpeta,Mandia,Jania,26.32194,90.91685,30-08-25,2.08
Assam,Barpeta,Mandia,Mandia,26.26483,90.96344,30-08-25,1.36
Assam,Barpeta,Pakabetbari,Phulguri,26.41046,91.06474,30-08-25,1.25
Assam,Barpeta,Pakabetbari,Simla,26.68333,91.21667,30-08-25,0.84
Assam,Barpeta,Ruposhi,Raha,26.44056,90.86567,30-08-25,0.49
Assam,Biswanath,Baghmara,Bihupukhuri,26.74722,93.25000,30-08-25,6.44
Assam,Biswanath,Behali,Behali,26.83233,93.35775,30-08-25,1.26
Assam,Biswanath,Biswanath,Biswanath Ghat,26.66117,93.17203,30-08-25,2.08
Assam,Biswanath,Chaiduar,Buroighat,26.86778,93.41639,30-08-25,1.20
Assam,Biswanath,Chaiduar,Gohpur,26.88001,93.60987,30-08-25,0.32
Assam,Biswanath,Chaiduar,Helem,26.85000,93.46584,30-08-25,0.17
Assam,Biswanath,Pub Chaiduar,Gopalpur,26.88444,93.66056,30-08-25,0.02
Assam,Biswanath,Pub Chaiduar,Kheroni,26.92017,93.61955,30-08-25,0.15
Assam,Biswanath,Sootea,Sootia,26.73806,93.04134,30-08-25,1.78
Assam,Bongaigaon,Boitamari,Chalantapara,26.23778,90.59167,30-08-25,6.12
Assam,Bongaigaon,Dangtol,Bongaigaon (Circuit House),26.48528,90.54583,30-08-25,3.87
Assam,Bongaigaon,Dangtol,Chalantapara1,26.26694,90.59278,30-08-25,6.12
Assam,Bongaigaon,Dangtol,Chaprakata,26.48722,90.63333,30-08-25,1.01
Assam,Bongaigaon,Dangtol,Chaprakata,26.48889,90.60099,30-08-25,2.18
Assam,Bongaigaon,Dangtol,Circuit House Bongaigaon,26.48500,90.55000,30-08-25,3.87
Assam,Bongaigaon,Dangtol,Majgaon,26.41889,90.59084,30-08-25,1.49
Assam,Bongaigaon,Manikpur,Manikpur,26.46667,90.80833,30-08-25,0.75
Assam,Bongaigaon,Srijangram,Abhayapuri,26.36667,90.63333,30-08-25,0.77
Assam,Bongaigaon,Srijangram,Abhayapuri,26.44069,90.65543,30-08-25,1.98
Assam,Bongaigaon,Srijangram,Baghpara,26.38486,90.55962,30-08-25,3.08
Assam,Bongaigaon,Srijangram,Medhipara,26.34964,90.63215,30-08-25,1.60
"""


# ============================================================
# CONVERT ASSAM TEXT TO DATAFRAME
# ============================================================

from io import StringIO

assam_df = pd.read_csv(
    StringIO(assam_data),
    dtype=str
)

print("Assam records prepared:", len(assam_df))


# ============================================================
# CHECK ASSAM DATA
# ============================================================

print("\n===== ASSAM CHECK =====")

print(
    assam_df["State"].value_counts()
)

print(
    "Assam rows:",
    len(assam_df)
)

print(
    "Missing values:"
)

print(
    assam_df.isna().sum()
)


# ============================================================
# COMBINE
# ============================================================

combined = pd.concat(
    [df, assam_df],
    ignore_index=True
)


# ============================================================
# SAVE
# ============================================================

combined.to_csv(
    OUTPUT_FILE,
    index=False
)

print("\n===== ACTION COMPLETED =====")

print(
    "Original rows:",
    len(df)
)

print(
    "Assam rows:",
    len(assam_df)
)

print(
    "Final rows:",
    len(combined)
)

print(
    "Saved as:",
    OUTPUT_FILE
)


# ============================================================
# EXPECTED RESULT
# ============================================================

expected = 84 + 52

print("\n===== ROW CHECK =====")

print(
    "Expected rows:",
    expected
)

print(
    "Actual rows:",
    len(combined)
)

if len(combined) == expected:

    print(
        "ROW COUNT STATUS: OK"
    )

else:

    print(
        "ROW COUNT STATUS: CHECK REQUIRED"
    )