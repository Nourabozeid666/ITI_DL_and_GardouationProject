"""
Multi-Model Training & Evaluation Pipeline for House Price Prediction
Dataset: House Price by Juhi Bhojani (Kaggle: juhibhojani/house-price)

Trains and compares:
1. Linear Regression (Baseline)
2. Linear Regression with Log-transformed target (log1p / expm1)
3. Random Forest Regressor
4. Gradient Boosting Regressor

Performs:
- Train / Test split (80/20)
- 5-Fold Cross-Validation (MAE & R²)
- Test set evaluation (MAE, RMSE, R²)
- Comparison table generation & winner selection
- Exporting the winning model to house_price.pkl and locations.json
"""

import json
import os
import sys
from pathlib import Path
from typing import Dict, Any, Tuple, List

import joblib
import numpy as np
import pandas as pd
from sklearn.compose import ColumnTransformer, TransformedTargetRegressor
from sklearn.ensemble import RandomForestRegressor, GradientBoostingRegressor
from sklearn.impute import SimpleImputer
from sklearn.linear_model import LinearRegression
from sklearn.metrics import mean_absolute_error, root_mean_squared_error, r2_score
from sklearn.model_selection import train_test_split, cross_val_score, KFold
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler

# Add local path for data_cleaner import
BASE_DIR = Path(__file__).resolve().parent
if str(BASE_DIR) not in sys.path:
    sys.path.append(str(BASE_DIR))

from data_cleaner import clean_house_prices_dataset

CSV_PATH = BASE_DIR / "data" / "house_prices.csv"
MODEL_EXPORT_PATH = BASE_DIR / "house_price.pkl"
LOCATIONS_EXPORT_PATH = BASE_DIR / "locations.json"
BACKEND_MODEL_PATH = BASE_DIR.parent / "backend" / "models" / "house_price.pkl"


def build_preprocessor() -> ColumnTransformer:
    """
    Constructs ColumnTransformer preprocessing numerical and categorical features.
    Bundles imputation, scaling, and one-hot encoding inside the pipeline.
    """
    numeric_features = ["carpet_area_sqft", "floor_num", "bathroom", "balcony"]
    categorical_features = [
        "location_grouped",
        "Furnishing",
        "Transaction",
        "Ownership",
        "facing",
    ]

    num_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="median")),
        ("scale", StandardScaler()),
    ])

    cat_pipeline = Pipeline([
        ("impute", SimpleImputer(strategy="most_frequent")),
        ("onehot", OneHotEncoder(handle_unknown="ignore", sparse_output=False)),
    ])

    preprocessor = ColumnTransformer(
        transformers=[
            ("num", num_pipeline, numeric_features),
            ("cat", cat_pipeline, categorical_features),
        ],
        remainder="drop",
    )
    return preprocessor


def create_pipeline(regressor: Any, use_log_target: bool = True) -> Pipeline:
    """
    Wraps a regressor in an end-to-end scikit-learn Pipeline with ColumnTransformer.
    Optionally applies log1p/expm1 target transformation for skewed distributions.
    """
    preprocessor = build_preprocessor()

    if use_log_target:
        model = TransformedTargetRegressor(
            regressor=regressor,
            func=np.log1p,
            inverse_func=np.expm1,
        )
    else:
        model = regressor

    return Pipeline([
        ("prep", preprocessor),
        ("reg", model),
    ])


def evaluate_models(
    df: pd.DataFrame,
    test_size: float = 0.2,
    random_state: int = 42,
    run_cv: bool = True,
) -> Tuple[Dict[str, Pipeline], pd.DataFrame, str]:
    """
    Trains multiple regression models, performs 5-fold CV, evaluates on test set,
    and returns models dictionary, comparison table, and winning model name.
    """
    feature_cols = [
        "carpet_area_sqft", "floor_num", "bathroom", "balcony",
        "location_grouped", "Furnishing", "Transaction", "Ownership", "facing"
    ]
    X = df[feature_cols]
    y = df["price_clean"]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state
    )

    print(f"Data split: {len(X_train):,} training records, {len(X_test):,} test records.\n")

    # Define models to train and compare
    candidate_regressors = {
        "Linear Regression (Raw Price)": (LinearRegression(), False),
        "Linear Regression (Log Price)": (LinearRegression(), True),
        "Random Forest Regressor": (RandomForestRegressor(n_estimators=100, max_depth=15, random_state=random_state, n_jobs=-1), True),
        "Gradient Boosting Regressor": (GradientBoostingRegressor(n_estimators=120, max_depth=5, learning_rate=0.08, random_state=random_state), True),
    }

    trained_pipelines: Dict[str, Pipeline] = {}
    comparison_records: List[Dict[str, Any]] = []

    for name, (regressor, use_log) in candidate_regressors.items():
        print(f"Training: {name}...")
        pipe = create_pipeline(regressor, use_log_target=use_log)
        pipe.fit(X_train, y_train)
        trained_pipelines[name] = pipe

        # Test set predictions
        y_pred = pipe.predict(X_test)
        mae = mean_absolute_error(y_test, y_pred)
        rmse = root_mean_squared_error(y_test, y_pred)
        r2 = r2_score(y_test, y_pred)

        # 5-fold cross validation score on training set
        cv_r2_mean = np.nan
        cv_r2_std = np.nan
        if run_cv:
            try:
                # 5-fold CV
                cv = KFold(n_splits=5, shuffle=True, random_state=random_state)
                # Quick CV with subset if data is very large
                sample_idx = np.random.RandomState(random_state).choice(len(X_train), min(1000, len(X_train)), replace=False)
                cv_scores = cross_val_score(pipe, X_train.iloc[sample_idx], y_train.iloc[sample_idx], cv=cv, scoring="r2")
                cv_r2_mean = float(np.mean(cv_scores))
                cv_r2_std = float(np.std(cv_scores))
            except Exception as e:
                print(f"  CV calculation notice for {name}: {e}")

        comparison_records.append({
            "Model": name,
            "Test MAE (₹)": f"₹ {mae:,.2f}",
            "Test MAE (Lac)": f"₹ {mae / 1e5:.2f} Lac",
            "Test RMSE (Lac)": f"₹ {rmse / 1e5:.2f} Lac",
            "Test R² Score": round(r2, 4),
            "5-Fold CV R² (Mean ± Std)": f"{cv_r2_mean:.4f} ± {cv_r2_std:.4f}" if not np.isnan(cv_r2_mean) else "N/A",
            "_raw_r2": r2,
            "_raw_mae": mae,
        })

    comparison_df = pd.DataFrame(comparison_records)
    # Pick winner based on highest test R² and lowest MAE
    winner_name = comparison_df.sort_values(by="_raw_r2", ascending=False).iloc[0]["Model"]

    print("\n" + "=" * 90)
    print("                      MODEL COMPARISON SUMMARY TABLE")
    print("=" * 90)
    display_cols = ["Model", "Test MAE (Lac)", "Test RMSE (Lac)", "Test R² Score", "5-Fold CV R² (Mean ± Std)"]
    print(comparison_df[display_cols].to_string(index=False))
    print("=" * 90)
    print(f"🏆 Winning Model Selected: '{winner_name}'")

    return trained_pipelines, comparison_df, winner_name


def run_full_training():
    print("=" * 70)
    print("  House Price Prediction — Complete Multi-Model Training & Benchmark")
    print("=" * 70)

    if not CSV_PATH.exists():
        print(f"❌ Dataset not found at {CSV_PATH}. Acquiring dataset...")
        import subprocess
        subprocess.run([sys.executable, str(BASE_DIR / "download_dataset.py")], check=False)

    df_raw = pd.read_csv(CSV_PATH, low_memory=False)
    print(f"Raw listings loaded: {len(df_raw):,}")

    df_clean, allowed_locations = clean_house_prices_dataset(df_raw, top_n_locations=50)
    print(f"Cleaned listings: {len(df_clean):,} (after outlier removal & normalization)")

    pipelines, comparison_df, winner_name = evaluate_models(df_clean, run_cv=True)
    winning_model = pipelines[winner_name]

    # Export artifacts
    print("\n📦 Exporting Winning Model Artifacts...")
    joblib.dump(winning_model, MODEL_EXPORT_PATH)
    print(f"  Exported winning model ({winner_name}) to: {MODEL_EXPORT_PATH}")

    with open(LOCATIONS_EXPORT_PATH, "w", encoding="utf-8") as f:
        json.dump(allowed_locations, f, indent=2)
    print(f"  Exported {len(allowed_locations)} locations to: {LOCATIONS_EXPORT_PATH}")

    # Sync to backend
    if BACKEND_MODEL_PATH.parent.exists():
        joblib.dump(winning_model, BACKEND_MODEL_PATH)
        print(f"  Synced winning model to backend: {BACKEND_MODEL_PATH}")

    print("\n✅ Multi-model evaluation and artifact export complete!")
    return winning_model, comparison_df


if __name__ == "__main__":
    run_full_training()
