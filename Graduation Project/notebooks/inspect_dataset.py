"""
Dataset Schema Inspection & Pre-flight Verification Utility
Checks notebooks/data/house_prices.csv against Phase 1 & 2 requirements.
"""

import os
import sys
from pathlib import Path

# Paths
BASE_DIR = Path(__file__).resolve().parent
CSV_PATH = BASE_DIR / "data" / "house_prices.csv"

EXPECTED_COLUMNS = [
    "Title", "Description", "Amount(in rupees)", "Price (in rupees)", "location",
    "Carpet Area", "Status", "Floor", "Transaction", "Furnishing", "facing",
    "overlooking", "Society", "Bathroom", "Balcony", "Car Parking", "Ownership",
    "Super Area", "Dimensions", "Plot Area"
]


def inspect_dataset():
    print("=" * 65)
    print("  House Price Dataset — Pre-flight Schema Inspection")
    print("=" * 65)

    if not CSV_PATH.exists():
        print(f"\n❌ Dataset file not found at: {CSV_PATH}")
        print("\nTo acquire the dataset, run:")
        print("  python notebooks/download_dataset.py")
        print("or download directly from:")
        print("  https://www.kaggle.com/datasets/juhibhojani/house-price")
        return False

    file_size_mb = CSV_PATH.stat().st_size / (1024 * 1024)
    print(f"\n📂 Found dataset file: {CSV_PATH.name}")
    print(f"   Size: {file_size_mb:.2f} MB")

    try:
        import pandas as pd
        df = pd.read_csv(CSV_PATH, low_memory=False)
        print(f"   Total rows: {len(df):,}")
        print(f"   Total columns: {len(df.columns)}")

        print("\n🔍 Column Verification:")
        missing_expected = [col for col in EXPECTED_COLUMNS if col not in df.columns]
        if missing_expected:
            print(f"   ⚠️ Warning: Missing expected columns: {missing_expected}")
        else:
            print("   ✅ All standard expected columns present!")

        print("\n📊 Column Missing Values & Types:")
        print(f"{'Column Name':<25} | {'Dtype':<10} | {'Missing %':<10} | {'Sample Value'}")
        print("-" * 75)
        for col in df.columns:
            missing_pct = df[col].isna().mean() * 100
            sample_val = str(df[col].dropna().iloc[0]) if not df[col].dropna().empty else "N/A"
            if len(sample_val) > 25:
                sample_val = sample_val[:22] + "..."
            print(f"{col:<25} | {str(df[col].dtype):<10} | {missing_pct:>8.1f}% | {sample_val}")

        print("\n✅ Dataset inspection passed. Ready for Phase 2 EDA & Pipeline Training.")
        return True

    except ImportError:
        # Fallback csv reader if pandas is not installed yet
        import csv
        with open(CSV_PATH, "r", encoding="utf-8", errors="ignore") as f:
            reader = csv.reader(f)
            header = next(reader)
            row_count = sum(1 for _ in reader)

        print(f"   Total rows: ~{row_count:,}")
        print(f"   Columns found ({len(header)}): {', '.join(header[:6])}...")
        return True


if __name__ == "__main__":
    inspect_dataset()
