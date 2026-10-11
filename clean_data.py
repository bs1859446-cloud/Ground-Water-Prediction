import pandas as pd

# Load the groundwater dataset
df = pd.read_csv("groundwater.csv")

print("===== DATA CLEANING =====")

# Remove spaces from column names
df.columns = df.columns.str.strip()

# Check duplicate rows
duplicates = df.duplicated().sum()
print("\nDuplicate rows:", duplicates)

# Remove duplicate rows
df = df.drop_duplicates()

# Check missing values
print("\nMissing values:")
print(df.isnull().sum())

# Convert Latitude and Longitude to numbers
df["Latitude"] = pd.to_numeric(df["Latitude"], errors="coerce")
df["Longitude"] = pd.to_numeric(df["Longitude"], errors="coerce")

# Convert groundwater level to number
df["WL_mbgl"] = pd.to_numeric(df["WL_mbgl"], errors="coerce")

# Convert Date
df["Date"] = pd.to_datetime(
    df["Date"],
    dayfirst=True,
    errors="coerce"
)

# Display data types
print("\nData types:")
print(df.dtypes)

# Display groundwater statistics
print("\nGroundwater level statistics:")
print(df["WL_mbgl"].describe())

# Save cleaned dataset
df.to_csv("groundwater_cleaned.csv", index=False)

print("\nCleaned dataset saved successfully!")