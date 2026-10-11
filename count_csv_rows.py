import pandas as pd
import glob
import os

print("=" * 70)
print("CSV FILE ROW COUNTS")
print("=" * 70)

for file in glob.glob("*.csv"):
    try:
        df = pd.read_csv(file)
        print(f"{os.path.basename(file):50} {len(df):>6} rows")
    except Exception as e:
        print(f"{os.path.basename(file):50} ERROR")

print("=" * 70)