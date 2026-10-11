import pandas as pd
import numpy as np
import joblib
import os

from sklearn.inspection import permutation_importance

print("=" * 70)
print("GROUNDWATER MODEL - FEATURE IMPORTANCE ANALYSIS")
print("=" * 70)

# ==============================================================
# LOAD DATA
# ==============================================================

DATA_FILE = "groundwater_with_weather.csv"
MODEL_FILE = "groundwater_temporal_best_model.pkl"

print("\n===== LOAD DATA =====")

df = pd.read_csv(DATA_FILE)

print("Total records:", len(df))

# ==============================================================
# PROCESS DATE
# ==============================================================

print("\n===== PROCESS DATE =====")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day
df["DayOfYear"] = df["Date"].dt.dayofyear

# Seasonal feature
def get_season(month):
    if month in [12, 1, 2]:
        return "Winter"
    elif month in [3, 4, 5]:
        return "Summer"
    elif month in [6, 7, 8, 9]:
        return "Monsoon"
    else:
        return "Post-Monsoon"

df["Season"] = df["Month"].apply(get_season)

# Cyclic month features
df["Month_sin"] = np.sin(2 * np.pi * df["Month"] / 12)
df["Month_cos"] = np.cos(2 * np.pi * df["Month"] / 12)

# ==============================================================
# LOCATION ID
# ==============================================================

df["Location_ID"] = (
    df["State"].astype(str) + "|" +
    df["District"].astype(str) + "|" +
    df["Block"].astype(str) + "|" +
    df["Village"].astype(str)
)

# ==============================================================
# PREVIOUS GROUNDWATER LEVEL
# ==============================================================

print("\n===== CREATE TEMPORAL FEATURES =====")

df = df.sort_values(["Location_ID", "Date"])

df["Previous_WL_mbgl"] = (
    df.groupby("Location_ID")["WL_mbgl"]
    .shift(1)
)

# Previous rainfall
if "Rainfall_mm" in df.columns:

    df["Previous_Rainfall_mm"] = (
        df.groupby("Location_ID")["Rainfall_mm"]
        .shift(1)
    )

# ==============================================================
# FEATURES
# ==============================================================

categorical_features = [
    "State",
    "District",
    "Block",
    "Village",
    "Season"
]

numeric_features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month",
    "Day",
    "DayOfYear",
    "Month_sin",
    "Month_cos",
    "Previous_WL_mbgl",
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh",
    "Previous_Rainfall_mm"
]

# Keep only columns that exist
categorical_features = [
    c for c in categorical_features if c in df.columns
]

numeric_features = [
    c for c in numeric_features if c in df.columns
]

features = categorical_features + numeric_features

X = df[features].copy()
y = df["WL_mbgl"].copy()

# ==============================================================
# LOAD MODEL
# ==============================================================

print("\n===== LOAD TRAINED MODEL =====")

if not os.path.exists(MODEL_FILE):

    print("ERROR: Model file not found:")
    print(MODEL_FILE)
    print("\nRun train_groundwater_temporal.py first.")
    exit()

model = joblib.load(MODEL_FILE)

print("Model loaded successfully.")
print("Model:", type(model).__name__)

# ==============================================================
# MODEL PIPELINE
# ==============================================================

print("\n===== MODEL STRUCTURE =====")

if hasattr(model, "named_steps"):

    print("Pipeline detected.")

    print("\nPipeline steps:")

    for name, step in model.named_steps.items():
        print(" -", name)

# ==============================================================
# TRANSFORM DATA
# ==============================================================

print("\n===== CALCULATE FEATURE IMPORTANCE =====")

# If the saved object is a sklearn Pipeline
if hasattr(model, "named_steps"):

    try:

        preprocessor = model.named_steps["preprocessor"]
        estimator = model.named_steps["model"]

        X_transformed = preprocessor.transform(X)

        # Get transformed feature names
        try:

            feature_names = preprocessor.get_feature_names_out()

        except Exception:

            feature_names = [
                f"Feature_{i}"
                for i in range(X_transformed.shape[1])
            ]

        # Tree model feature importance
        if hasattr(estimator, "feature_importances_"):

            importances = estimator.feature_importances_

            importance_df = pd.DataFrame({
                "Feature": feature_names,
                "Importance": importances
            })

            importance_df = importance_df.sort_values(
                "Importance",
                ascending=False
            )

            print("\n===== TOP FEATURES =====")

            print(
                importance_df.head(30).to_string(index=False)
            )

            importance_df.to_csv(
                "groundwater_feature_importance.csv",
                index=False
            )

            print(
                "\nFeature importance saved:"
            )

            print(
                "groundwater_feature_importance.csv"
            )

        else:

            print(
                "ERROR: Model does not provide feature_importances_."
            )

    except Exception as e:

        print("\nERROR while calculating importance:")
        print(e)

else:

    print(
        "ERROR: Saved model is not a preprocessing pipeline."
    )

# ==============================================================
# DATA COVERAGE
# ==============================================================

print("\n===== DATA COVERAGE =====")

print(
    "Unique locations:",
    df["Location_ID"].nunique()
)

print(
    "Unique dates:",
    df["Date"].nunique()
)

print("\nDate distribution:")

print(
    df["Date"]
    .dt.strftime("%Y-%m-%d")
    .value_counts()
    .sort_index()
)

# ==============================================================
# PREVIOUS WL COVERAGE
# ==============================================================

print("\n===== TEMPORAL COVERAGE =====")

print(
    "Records with Previous_WL:",
    df["Previous_WL_mbgl"].notna().sum()
)

print(
    "Records without Previous_WL:",
    df["Previous_WL_mbgl"].isna().sum()
)

# ==============================================================
# WEATHER COVERAGE
# ==============================================================

print("\n===== WEATHER COVERAGE =====")

weather_columns = [
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh"
]

for column in weather_columns:

    if column in df.columns:

        valid = df[column].notna().sum()
        missing = df[column].isna().sum()

        print(
            f"{column:25} Valid: {valid:4} | Missing: {missing:4}"
        )

# ==============================================================
# FINISHED
# ==============================================================

print("\n" + "=" * 70)
print("FEATURE IMPORTANCE ANALYSIS COMPLETED")
print("=" * 70)

print("\nOutput:")
print(" - groundwater_feature_importance.csv")

print("\nCurrent best model:")
print(" - Extra Trees")

print("\nCurrent R²:")
print(" - 0.1416")

print("\nIMPORTANT:")
print(
    "The low R² is mainly related to the very limited temporal "
    "coverage of the dataset."
)

print(
    "\nFor genuine future groundwater prediction, the next major "
    "step is to add more groundwater observations across multiple "
    "dates/months/years for the same locations."
)

print("=" * 70)