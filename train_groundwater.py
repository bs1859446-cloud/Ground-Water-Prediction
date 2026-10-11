import pandas as pd
import numpy as np
import joblib

from sklearn.model_selection import train_test_split
from sklearn.compose import ColumnTransformer
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder
from sklearn.impute import SimpleImputer
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_absolute_error, mean_squared_error, r2_score


# ============================================================
# GROUNDWATER LEVEL PREDICTION - MODEL TRAINING
# ============================================================

print("=" * 70)
print("GROUNDWATER LEVEL PREDICTION - MODEL TRAINING")
print("=" * 70)


# ------------------------------------------------------------
# 1. LOAD DATASET
# ------------------------------------------------------------

FILE = "groundwater_with_tamilnadu_january_final.csv"

print("\n===== LOAD DATASET =====")
print("File:", FILE)

df = pd.read_csv(FILE)

print("Total records loaded:", len(df))
print("\nColumns:")
print(df.columns.tolist())


# ------------------------------------------------------------
# 2. STANDARDIZE COLUMN NAMES
# ------------------------------------------------------------

df.columns = df.columns.str.strip()

# Handle possible naming differences
rename_map = {
    "Latitute": "Latitude",
    "Latitude": "Latitude",
    "Longitude": "Longitude",
    "WL(mbgl)": "WL_mbgl",
    "WL_mbgl": "WL_mbgl"
}

df.rename(columns=rename_map, inplace=True)


# ------------------------------------------------------------
# 3. CHECK REQUIRED COLUMNS
# ------------------------------------------------------------

required_columns = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Date",
    "WL_mbgl"
]

missing_columns = [
    col for col in required_columns
    if col not in df.columns
]

if missing_columns:
    print("\nERROR: Missing columns:")
    print(missing_columns)
    raise SystemExit


# ------------------------------------------------------------
# 4. CHECK TAMIL NADU RECORDS
# ------------------------------------------------------------

print("\n===== STATE COUNTS =====")

print(
    df["State"]
    .astype(str)
    .str.strip()
    .value_counts()
)

tn_count = (
    df["State"]
    .astype(str)
    .str.strip()
    .str.lower()
    .eq("tamil nadu")
    .sum()
)

print("\nTamil Nadu records:", tn_count)


# ------------------------------------------------------------
# 5. CLEAN NUMERIC COLUMNS
# ------------------------------------------------------------

print("\n===== CLEAN NUMERIC DATA =====")

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


# ------------------------------------------------------------
# 6. PROCESS DATE
# ------------------------------------------------------------

print("\n===== PROCESS DATES =====")

df["Date"] = pd.to_datetime(
    df["Date"],
    errors="coerce",
    dayfirst=True
)

df["Year"] = df["Date"].dt.year
df["Month"] = df["Date"].dt.month


# ------------------------------------------------------------
# 7. REMOVE INVALID TARGET ROWS
# ------------------------------------------------------------

before = len(df)

df = df.dropna(
    subset=[
        "Latitude",
        "Longitude",
        "WL_mbgl"
    ]
)

after = len(df)

print("Rows before cleaning:", before)
print("Rows after cleaning :", after)
print("Rows removed        :", before - after)


# ------------------------------------------------------------
# 8. FEATURES AND TARGET
# ------------------------------------------------------------

print("\n===== PREPARE FEATURES =====")

features = [
    "State",
    "District",
    "Block",
    "Village",
    "Latitude",
    "Longitude",
    "Year",
    "Month"
]

target = "WL_mbgl"

X = df[features]
y = df[target]

print("Features:")
for feature in features:
    print(" -", feature)

print("\nTarget:", target)


# ------------------------------------------------------------
# 9. TRAIN / TEST SPLIT
# ------------------------------------------------------------

print("\n===== TRAIN / TEST SPLIT =====")

X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.20,
    random_state=42
)

print("Training records :", len(X_train))
print("Testing records  :", len(X_test))


# ------------------------------------------------------------
# 10. CATEGORICAL / NUMERIC FEATURES
# ------------------------------------------------------------

categorical_features = [
    "State",
    "District",
    "Block",
    "Village"
]

numeric_features = [
    "Latitude",
    "Longitude",
    "Year",
    "Month"
]


# ------------------------------------------------------------
# 11. PREPROCESSING
# ------------------------------------------------------------

categorical_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="most_frequent")
        ),
        (
            "encoder",
            OneHotEncoder(
                handle_unknown="ignore"
            )
        )
    ]
)

numeric_pipeline = Pipeline(
    steps=[
        (
            "imputer",
            SimpleImputer(strategy="median")
        )
    ]
)

preprocessor = ColumnTransformer(
    transformers=[
        (
            "categorical",
            categorical_pipeline,
            categorical_features
        ),
        (
            "numeric",
            numeric_pipeline,
            numeric_features
        )
    ]
)


# ------------------------------------------------------------
# 12. RANDOM FOREST MODEL
# ------------------------------------------------------------

print("\n===== CREATE RANDOM FOREST MODEL =====")

model = RandomForestRegressor(
    n_estimators=300,
    max_depth=None,
    min_samples_split=2,
    min_samples_leaf=1,
    random_state=42,
    n_jobs=-1
)


# ------------------------------------------------------------
# 13. COMPLETE PIPELINE
# ------------------------------------------------------------

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


# ------------------------------------------------------------
# 14. TRAIN
# ------------------------------------------------------------

print("\n===== TRAINING MODEL =====")
print("Please wait...")

pipeline.fit(
    X_train,
    y_train
)

print("Training completed successfully.")


# ------------------------------------------------------------
# 15. PREDICTION
# ------------------------------------------------------------

print("\n===== TEST PREDICTIONS =====")

y_pred = pipeline.predict(X_test)


# ------------------------------------------------------------
# 16. EVALUATION
# ------------------------------------------------------------

mae = mean_absolute_error(
    y_test,
    y_pred
)

rmse = np.sqrt(
    mean_squared_error(
        y_test,
        y_pred
    )
)

r2 = r2_score(
    y_test,
    y_pred
)


print("\n" + "=" * 70)
print("MODEL PERFORMANCE")
print("=" * 70)

print(f"MAE  : {mae:.4f} mbgl")
print(f"RMSE : {rmse:.4f} mbgl")
print(f"R²   : {r2:.4f}")

print("=" * 70)


# ------------------------------------------------------------
# 17. SAMPLE PREDICTIONS
# ------------------------------------------------------------

results = X_test.copy()

results["Actual_WL_mbgl"] = y_test.values
results["Predicted_WL_mbgl"] = y_pred

results["Error"] = (
    results["Actual_WL_mbgl"]
    - results["Predicted_WL_mbgl"]
)

print("\n===== SAMPLE PREDICTIONS =====")

print(
    results[
        [
            "State",
            "District",
            "Village",
            "Actual_WL_mbgl",
            "Predicted_WL_mbgl",
            "Error"
        ]
    ].head(20).to_string(index=False)
)


# ------------------------------------------------------------
# 18. SAVE MODEL
# ------------------------------------------------------------

MODEL_FILE = "groundwater_random_forest.pkl"

joblib.dump(
    pipeline,
    MODEL_FILE
)

print("\n===== MODEL SAVED =====")
print(MODEL_FILE)


# ------------------------------------------------------------
# 19. SAVE TEST RESULTS
# ------------------------------------------------------------

RESULT_FILE = "groundwater_test_predictions.csv"

results.to_csv(
    RESULT_FILE,
    index=False
)

print("Test results saved:", RESULT_FILE)


print("\n" + "=" * 70)
print("TRAINING FINISHED SUCCESSFULLY")
print("=" * 70)