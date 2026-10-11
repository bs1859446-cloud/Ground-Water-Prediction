# train_groundwater_temporal.py

import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ================================================================
# CONFIGURATION
# ================================================================

INPUT_FILE = "groundwater_with_weather.csv"

BEST_MODEL_FILE = "groundwater_temporal_best_model.pkl"
COMPARISON_FILE = "groundwater_temporal_model_comparison.csv"
PREDICTIONS_FILE = "groundwater_temporal_predictions.csv"


print("=" * 70)
print("GROUNDWATER LEVEL PREDICTION")
print("CORRECTED TEMPORAL + WEATHER MODEL")
print("=" * 70)


# ================================================================
# LOAD DATA
# ================================================================

print("\n===== LOAD DATASET =====")

df = pd.read_csv(INPUT_FILE)

print("Total records loaded:", len(df))

print("\nColumns:")
print(list(df.columns))


# ================================================================
# PROCESS DATES
# ================================================================

print("\n===== PROCESS DATES =====")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df["WL_mbgl"] = pd.to_numeric(
    df["WL_mbgl"],
    errors="coerce"
)

# Weather columns
weather_columns = [
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh"
]

for col in weather_columns:
    if col in df.columns:
        df[col] = pd.to_numeric(
            df[col],
            errors="coerce"
        )


# Remove invalid target/date rows

before = len(df)

df = df.dropna(
    subset=[
        "Date",
        "WL_mbgl",
        "Latitude",
        "Longitude"
    ]
).copy()

after = len(df)

print("\n===== TARGET CHECK =====")

print("Rows before cleaning :", before)
print("Rows after cleaning  :", after)
print("Rows removed         :", before - after)


# ================================================================
# CREATE LOCATION ID
# ================================================================

print("\n===== CREATE LOCATION ID =====")

df["Location_ID"] = (
    df["State"].astype(str).str.strip()
    + "|"
    + df["District"].astype(str).str.strip()
    + "|"
    + df["Block"].astype(str).str.strip()
    + "|"
    + df["Village"].astype(str).str.strip()
)

print(
    "Unique locations:",
    df["Location_ID"].nunique()
)


# ================================================================
# SORT DATA
# ================================================================

df = df.sort_values(
    ["Location_ID", "Date"]
).reset_index(drop=True)


# ================================================================
# REMOVE SAME-DATE DUPLICATES FOR TEMPORAL CALCULATION
# ================================================================

print("\n===== TEMPORAL DUPLICATE CHECK =====")

same_date_counts = (
    df.groupby(
        ["Location_ID", "Date"]
    ).size()
)

same_date_duplicate_groups = (
    same_date_counts > 1
).sum()

print(
    "Location/date groups:",
    len(same_date_counts)
)

print(
    "Groups containing multiple records:",
    same_date_duplicate_groups
)


# IMPORTANT:
# We DO NOT treat another record from the same date
# as a previous groundwater observation.
#
# For temporal features we first create one value
# per Location + Date.

temporal_df = (
    df.groupby(
        ["Location_ID", "Date"],
        as_index=False
    )
    .agg(
        Temporal_WL_mbgl=("WL_mbgl", "mean"),
        Temporal_Rainfall_mm=("Rainfall_mm", "mean")
    )
)

temporal_df = temporal_df.sort_values(
    ["Location_ID", "Date"]
).reset_index(drop=True)


# ================================================================
# CREATE TRUE TEMPORAL FEATURES
# ================================================================

print("\n===== CREATE TRUE TEMPORAL FEATURES =====")

# Previous groundwater level
temporal_df["Previous_WL_mbgl"] = (
    temporal_df
    .groupby("Location_ID")["Temporal_WL_mbgl"]
    .shift(1)
)

# Previous rainfall
temporal_df["Previous_Rainfall_mm"] = (
    temporal_df
    .groupby("Location_ID")["Temporal_Rainfall_mm"]
    .shift(1)
)

# Previous measurement date
temporal_df["Previous_Date"] = (
    temporal_df
    .groupby("Location_ID")["Date"]
    .shift(1)
)

# Number of days between measurements

temporal_df["Days_Since_Previous"] = (
    temporal_df["Date"]
    - temporal_df["Previous_Date"]
).dt.days


# ================================================================
# SECOND PREVIOUS GROUNDWATER LEVEL
# ================================================================

temporal_df["Previous_2_WL_mbgl"] = (
    temporal_df
    .groupby("Location_ID")["Temporal_WL_mbgl"]
    .shift(2)
)


# ================================================================
# MERGE TEMPORAL FEATURES BACK
# ================================================================

df = df.merge(
    temporal_df[
        [
            "Location_ID",
            "Date",
            "Previous_WL_mbgl",
            "Previous_2_WL_mbgl",
            "Previous_Rainfall_mm",
            "Days_Since_Previous"
        ]
    ],
    on=["Location_ID", "Date"],
    how="left"
)


# ================================================================
# TEMPORAL INFORMATION
# ================================================================

print("\n===== TEMPORAL COVERAGE =====")

valid_previous = df["Previous_WL_mbgl"].notna().sum()

print(
    "Total records:",
    len(df)
)

print(
    "Records with genuine previous WL:",
    valid_previous
)

print(
    "Records without previous WL:",
    len(df) - valid_previous
)


# ================================================================
# DATE FEATURES
# ================================================================

print("\n===== CREATE DATE FEATURES =====")

df["Year"] = df["Date"].dt.year

df["Month"] = df["Date"].dt.month

df["Day"] = df["Date"].dt.day

df["DayOfYear"] = df["Date"].dt.dayofyear


# Cyclic month features

df["Month_sin"] = np.sin(
    2 * np.pi * df["Month"] / 12
)

df["Month_cos"] = np.cos(
    2 * np.pi * df["Month"] / 12
)


# ================================================================
# SEASON
# ================================================================

def get_season(month):

    if month in [12, 1, 2]:
        return "Winter"

    elif month in [3, 4, 5]:
        return "Pre-Monsoon"

    elif month in [6, 7, 8, 9]:
        return "Monsoon"

    else:
        return "Post-Monsoon"


df["Season"] = df["Month"].apply(get_season)


# ================================================================
# WEATHER CHECK
# ================================================================

print("\n===== WEATHER DATA =====")

for col in weather_columns:

    if col in df.columns:

        valid = df[col].notna().sum()
        missing = df[col].isna().sum()

        print(
            f"{col:<25} Valid: {valid:4d} | Missing: {missing:4d}"
        )


# ================================================================
# REMOVE REDUNDANT PRECIPITATION
# ================================================================

if (
    "Precipitation_mm" in df.columns
    and "Rainfall_mm" in df.columns
):

    if df["Precipitation_mm"].equals(
        df["Rainfall_mm"]
    ):

        print(
            "\nPrecipitation_mm is identical to Rainfall_mm."
        )

        print(
            "Removing Precipitation_mm."
        )

        df = df.drop(
            columns=["Precipitation_mm"]
        )


# ================================================================
# FEATURES
# ================================================================

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
    "Previous_2_WL_mbgl",
    "Days_Since_Previous",

    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh",

    "Previous_Rainfall_mm"
]


# Keep only columns that actually exist

categorical_features = [
    col for col in categorical_features
    if col in df.columns
]

numeric_features = [
    col for col in numeric_features
    if col in df.columns
]


print("\n===== FEATURES =====")

print("\nCategorical:")

for col in categorical_features:
    print(" -", col)

print("\nNumeric:")

for col in numeric_features:
    print(" -", col)

print("\nTarget:")
print(" - WL_mbgl")


# ================================================================
# X / y
# ================================================================

X = df[
    categorical_features + numeric_features
].copy()

y = df["WL_mbgl"].copy()


# ================================================================
# TRAIN / TEST SPLIT
# ================================================================

print("\n===== TRAIN / TEST SPLIT =====")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print(
    "Training records :",
    len(X_train)
)

print(
    "Testing records  :",
    len(X_test)
)


# ================================================================
# PREPROCESSING
# ================================================================

print("\n===== CREATE PREPROCESSING PIPELINE =====")

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="median"
            )
        )
    ]
)


categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(
                strategy="most_frequent"
            )
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)


preprocessor = ColumnTransformer(
    transformers=[
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        ),
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        )
    ]
)


# ================================================================
# MODELS
# ================================================================

models = {

    "Random Forest":
        RandomForestRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        ),

    "Extra Trees":
        ExtraTreesRegressor(
            n_estimators=300,
            max_depth=None,
            min_samples_split=2,
            min_samples_leaf=1,
            random_state=42,
            n_jobs=-1
        ),

    "Gradient Boosting":
        GradientBoostingRegressor(
            n_estimators=200,
            learning_rate=0.05,
            max_depth=3,
            random_state=42
        )
}


# ================================================================
# TRAIN MODELS
# ================================================================

results = []

trained_models = {}

predictions_dictionary = {}


for model_name, model in models.items():

    print("\n")
    print("=" * 70)
    print("TRAINING:", model_name)
    print("=" * 70)

    pipeline = Pipeline(
        steps=[
            (
                "preprocessor",
                preprocessor
            ),
            (
                "model",
                model
            )
        ]
    )

    print("Training...")

    pipeline.fit(
        X_train,
        y_train
    )

    print("Training completed.")

    predictions = pipeline.predict(
        X_test
    )

    mae = mean_absolute_error(
        y_test,
        predictions
    )

    rmse = np.sqrt(
        mean_squared_error(
            y_test,
            predictions
        )
    )

    r2 = r2_score(
        y_test,
        predictions
    )

    print("\nMODEL PERFORMANCE")

    print(
        f"MAE  : {mae:.4f} mbgl"
    )

    print(
        f"RMSE : {rmse:.4f} mbgl"
    )

    print(
        f"R²   : {r2:.4f}"
    )

    results.append(
        {
            "Model": model_name,
            "MAE": mae,
            "RMSE": rmse,
            "R2": r2
        }
    )

    trained_models[
        model_name
    ] = pipeline

    predictions_dictionary[
        model_name
    ] = predictions


# ================================================================
# MODEL COMPARISON
# ================================================================

comparison = pd.DataFrame(
    results
)

comparison = comparison.sort_values(
    "R2",
    ascending=False
).reset_index(drop=True)


print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

print(
    comparison.to_string(
        index=False
    )
)


comparison.to_csv(
    COMPARISON_FILE,
    index=False
)

print(
    "\nModel comparison saved:"
)

print(
    COMPARISON_FILE
)


# ================================================================
# BEST MODEL
# ================================================================

best_model_name = comparison.iloc[0]["Model"]

best_r2 = comparison.iloc[0]["R2"]

best_model = trained_models[
    best_model_name
]

best_predictions = predictions_dictionary[
    best_model_name
]


print("\n===== BEST MODEL =====")

print(
    "Best model :",
    best_model_name
)

print(
    f"Best R²    : {best_r2:.4f}"
)


# ================================================================
# SAVE MODEL
# ================================================================

joblib.dump(
    best_model,
    BEST_MODEL_FILE
)

print(
    "\nModel saved:",
    BEST_MODEL_FILE
)


# ================================================================
# SAVE PREDICTIONS
# ================================================================

test_results = X_test.copy()

test_results["Actual_WL_mbgl"] = y_test.values

test_results[
    "Predicted_WL_mbgl"
] = best_predictions

test_results["Error"] = (
    test_results["Actual_WL_mbgl"]
    -
    test_results["Predicted_WL_mbgl"]
)


# Add original information

test_indices = X_test.index

test_results["State"] = df.loc[
    test_indices,
    "State"
].values

test_results["District"] = df.loc[
    test_indices,
    "District"
].values

test_results["Village"] = df.loc[
    test_indices,
    "Village"
].values

test_results["Date"] = df.loc[
    test_indices,
    "Date"
].values

test_results["Previous_WL_mbgl"] = df.loc[
    test_indices,
    "Previous_WL_mbgl"
].values


test_results.to_csv(
    PREDICTIONS_FILE,
    index=False
)

print(
    "\nTest predictions saved:"
)

print(
    PREDICTIONS_FILE
)


# ================================================================
# SAMPLE PREDICTIONS
# ================================================================

print("\n===== SAMPLE PREDICTIONS =====")

display_columns = [
    "State",
    "District",
    "Village",
    "Date",
    "Previous_WL_mbgl",
    "Actual_WL_mbgl",
    "Predicted_WL_mbgl",
    "Error"
]

print(
    test_results[
        display_columns
    ].head(20).to_string(
        index=False
    )
)


# ================================================================
# FINAL SUMMARY
# ================================================================

print("\n")
print("=" * 70)
print("CORRECTED TEMPORAL + WEATHER TRAINING FINISHED")
print("=" * 70)

print(
    "\nTotal records used:",
    len(df)
)

print(
    "Records with genuine previous WL:",
    valid_previous
)

print(
    "Records without previous WL:",
    len(df) - valid_previous
)

print(
    "\nBest model:",
    best_model_name
)

print(
    f"Best R²    : {best_r2:.4f}"
)

print("\nFeatures used:")

for col in (
    categorical_features +
    numeric_features
):

    print(" -", col)

print("\nTarget:")
print(" - WL_mbgl")

print("\nOutput files:")

print(
    " -",
    BEST_MODEL_FILE
)

print(
    " -",
    COMPARISON_FILE
)

print(
    " -",
    PREDICTIONS_FILE
)

print("\n")
print("=" * 70)