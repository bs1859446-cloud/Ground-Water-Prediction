import pandas as pd

# Load groundwater dataset
df = pd.read_csv("groundwater.csv")

print("===== GROUNDWATER DATA CHECK =====")

# 1. Total records
print("\n1. Total records:")
print(len(df))

# 2. Column names
print("\n2. Columns:")
print(df.columns.tolist())

# 3. Number of villages
print("\n3. Number of villages:")
print(df["Village"].nunique())

# 4. Number of dates
print("\n4. Number of different dates:")
print(df["Date"].nunique())

# 5. Dates
print("\n5. Dates:")
print(df["Date"].unique())

# 6. Missing values
print("\n6. Missing values:")
print(df.isnull().sum())

# 7. Groundwater statistics
print("\n7. Groundwater level information:")
print(df["WL_mbgl"].describe())