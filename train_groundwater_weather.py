import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.pipeline import Pipeline

from sklearn.ensemble import (
    RandomForestRegressor,
    ExtraTreesRegressor,
    GradientBoostingRegressor
)

from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


print("=" * 70)
print("GROUNDWATER LEVEL PREDICTION - WEATHER MODEL V2")
print("=" * 70)


# ==============================================================
# 1. LOAD DATA
# ==============================================================

FILE = "groundwater_with_weather.csv"

print("\n===== LOAD DATASET =====")

df = pd.read_csv(FILE)

print("Total records loaded:", len(df))

print("\nColumns:")
print(list(df.columns))


# ==============================================================
# 2. PROCESS DATE
# ==============================================================

print("\n===== PROCESS DATES =====")

df["Date"] = pd.to_datetime(df["Date"], errors="coerce")

df = df.dropna(subset=["Date"])

# Date features
df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month
df["Day"] = df["Date"].dt.day
df["DayOfYear"] = df["Date"].dt.dayofyear

# Cyclic seasonal features
df["Month_sin"] = np.sin(2 * np.pi * df["Month"] / 12)
df["Month_cos"] = np.cos(2 * np.pi * df["Month"] / 12)

# Simple season classification
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


# ==============================================================
# 3. TARGET CLEANING
# ==============================================================

print("\n===== TARGET CHECK =====")

df["WL_mbgl"] = pd.to_numeric(df["WL_mbgl"], errors="coerce")

before = len(df)

df = df.dropna(subset=["WL_mbgl"])

after = len(df)

print("Rows before cleaning :", before)
print("Rows after cleaning  :", after)
print("Rows removed         :", before - after)


# ==============================================================
# 4. REMOVE REDUNDANT FEATURE
# ==============================================================

print("\n===== FEATURE CLEANING =====")

# Rainfall and precipitation are identical in the current dataset.
if "Precipitation_mm" in df.columns:

    difference = (
        df["Rainfall_mm"].fillna(-999)
        - df["Precipitation_mm"].fillna(-999)
    ).abs().max()

    if difference == 0:

        print("Precipitation_mm is identical to Rainfall_mm.")
        print("Removing Precipitation_mm.")

        df = df.drop(columns=["Precipitation_mm"])


# ==============================================================
# 5. FEATURES
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
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh"
]

# Keep only features that actually exist
categorical_features = [
    x for x in categorical_features
    if x in df.columns
]

numeric_features = [
    x for x in numeric_features
    if x in df.columns
]


print("\n===== FEATURES =====")

print("\nCategorical:")
for f in categorical_features:
    print(" -", f)

print("\nNumeric:")
for f in numeric_features:
    print(" -", f)


X = df[categorical_features + numeric_features]

y = df["WL_mbgl"]


# ==============================================================
# 6. WEATHER INFORMATION
# ==============================================================

print("\n===== WEATHER DATA =====")

weather_columns = [
    "Temperature_C",
    "Humidity_percent",
    "Rainfall_mm",
    "Pressure_hPa",
    "WindSpeed_kmh"
]

for col in weather_columns:

    if col in df.columns:

        valid = df[col].notna().sum()
        missing = df[col].isna().sum()

        print(
            f"{col:25s} "
            f"Valid: {valid:4d} | "
            f"Missing: {missing:4d}"
        )


# ==============================================================
# 7. TRAIN / TEST SPLIT
# ==============================================================

print("\n===== TRAIN / TEST SPLIT =====")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training records :", len(X_train))
print("Testing records  :", len(X_test))


# ==============================================================
# 8. PREPROCESSING
# ==============================================================

print("\n===== CREATE PREPROCESSING PIPELINE =====")

numeric_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)

categorical_transformer = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "onehot",
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
            numeric_transformer,
            numeric_features
        ),
        (
            "categorical",
            categorical_transformer,
            categorical_features
        )
    ]
)


# ==============================================================
# 9. MODELS
# ==============================================================

models = {

    "Random Forest": RandomForestRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    ),

    "Extra Trees": ExtraTreesRegressor(
        n_estimators=500,
        max_depth=None,
        min_samples_split=2,
        min_samples_leaf=1,
        random_state=42,
        n_jobs=-1
    ),

    "Gradient Boosting": GradientBoostingRegressor(
        n_estimators=300,
        learning_rate=0.03,
        max_depth=3,
        min_samples_split=2,
        min_samples_leaf=2,
        random_state=42
    )
}


# ==============================================================
# 10. TRAIN MODELS
# ==============================================================

results = []

best_model = None
best_pipeline = None
best_r2 = -999


for model_name, model in models.items():

    print("\n" + "=" * 70)
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
    pipeline.fit(X_train, y_train)

    print("Training completed.")

    # Predictions
    predictions = pipeline.predict(X_test)

    # Metrics
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

    print(f"MAE  : {mae:.4f} mbgl")
    print(f"RMSE : {rmse:.4f} mbgl")
    print(f"R²   : {r2:.4f}")

    results.append({
        "Model": model_name,
        "MAE": mae,
        "RMSE": rmse,
        "R2": r2
    })

    # Best model
    if r2 > best_r2:

        best_r2 = r2
        best_model = model_name
        best_pipeline = pipeline

        best_predictions = predictions


# ==============================================================
# 11. MODEL COMPARISON
# ==============================================================

print("\n")
print("=" * 70)
print("MODEL COMPARISON")
print("=" * 70)

results_df = pd.DataFrame(results)

results_df = results_df.sort_values(
    by="R2",
    ascending=False
)

print(
    results_df.to_string(
        index=False
    )
)


# ==============================================================
# 12. SAVE RESULTS
# ==============================================================

results_df.to_csv(
    "groundwater_weather_model_comparison.csv",
    index=False
)

print(
    "\nModel comparison saved:"
    " groundwater_weather_model_comparison.csv"
)


# ==============================================================
# 13. SAVE BEST MODEL
# ==============================================================

MODEL_FILE = "groundwater_weather_best_model.pkl"

joblib.dump(
    best_pipeline,
    MODEL_FILE
)

print("\n===== BEST MODEL =====")

print("Best model :", best_model)
print(f"Best R²    : {best_r2:.4f}")

print("\nModel saved:")
print(MODEL_FILE)


# ==============================================================
# 14. SAVE TEST PREDICTIONS
# ==============================================================

test_results = X_test.copy()

test_results["Actual_WL_mbgl"] = y_test.values

test_results["Predicted_WL_mbgl"] = best_predictions

test_results["Error"] = (
    test_results["Actual_WL_mbgl"]
    - test_results["Predicted_WL_mbgl"]
)

test_results.to_csv(
    "groundwater_weather_v2_predictions.csv",
    index=False
)

print(
    "\nTest predictions saved:"
    " groundwater_weather_v2_predictions.csv"
)


# ==============================================================
# 15. SAMPLE PREDICTIONS
# ==============================================================

print("\n===== SAMPLE PREDICTIONS =====")

display_columns = [
    "State",
    "District",
    "Village",
    "Actual_WL_mbgl",
    "Predicted_WL_mbgl",
    "Error"
]

display_columns = [
    x for x in display_columns
    if x in test_results.columns
]

print(
    test_results[
        display_columns
    ].head(20).to_string(index=False)
)


# ==============================================================
# 16. FINAL SUMMARY
# ==============================================================

print("\n")
print("=" * 70)
print("WEATHER MODEL V2 TRAINING FINISHED")
print("=" * 70)

print("\nBest model:", best_model)

print(f"Best R²    : {best_r2:.4f}")

print("\nFeatures used:")

for f in categorical_features + numeric_features:
    print(" -", f)

print("\nTarget:")
print(" - WL_mbgl")

print("\nOutput files:")
print(" - groundwater_weather_best_model.pkl")
print(" - groundwater_weather_model_comparison.csv")
print(" - groundwater_weather_v2_predictions.csv")

print("=" * 70)