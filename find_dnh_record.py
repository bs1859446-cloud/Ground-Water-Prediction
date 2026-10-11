import pandas as pd
import glob
import os

LAT = 20.7242
LON = 70.9306

print("=" * 70)
print("SEARCHING FOR DNH / DIU RECORD")
print("=" * 70)

for file in glob.glob("*.csv"):

    if os.path.basename(file) == "groundwater_with_assam_january.csv":
        continue

    try:
        df = pd.read_csv(file)

        if "Latitude" not in df.columns or "Longitude" not in df.columns:
            continue

        result = df[
            (pd.to_numeric(df["Latitude"], errors="coerce") == LAT) &
            (pd.to_numeric(df["Longitude"], errors="coerce") == LON)
        ]

        if len(result) > 0:
            print("\nFILE:", os.path.basename(file))
            print(result.to_string(index=False))

    except Exception:
        pass

print("\n" + "=" * 70)
print("SEARCH COMPLETE")
print("=" * 70)