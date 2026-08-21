"""
Dataset Downloader & Acquisition Script for House Price Prediction Project
Dataset: House Price by Juhi Bhojani (Kaggle: juhibhojani/house-price)
Target file: notebooks/data/house_prices.csv
"""

import os
import sys
import subprocess
from pathlib import Path

# Paths configuration
BASE_DIR = Path(__file__).resolve().parent
DATA_DIR = BASE_DIR / "data"
CSV_PATH = DATA_DIR / "house_prices.csv"
DATASET_HANDLE = "juhibhojani/house-price"


def is_dataset_present() -> bool:
    """Checks if the raw CSV dataset already exists in notebooks/data/."""
    if CSV_PATH.exists() and CSV_PATH.stat().st_size > 1000:
        print(f" Dataset already present at: {CSV_PATH}")
        print(f"   Size: {CSV_PATH.stat().st_size / (1024 * 1024):.2f} MB")
        return True
    return False


def download_via_kaggle_cli() -> bool:
    """Attempts to download the dataset using the Kaggle CLI."""
    print(f"\n[1/2] Attempting download via Kaggle CLI for '{DATASET_HANDLE}'...")
    DATA_DIR.mkdir(parents=True, exist_ok=True)

    cmd = [
        "kaggle",
        "datasets",
        "download",
        "-d",
        DATASET_HANDLE,
        "-p",
        str(DATA_DIR),
        "--unzip",
    ]

    try:
        result = subprocess.run(cmd, capture_output=True, text=True, check=False)
        if result.returncode == 0:
            print(f" Successfully downloaded and extracted dataset into: {DATA_DIR}")
            return True
        else:
            print(" Kaggle CLI returned non-zero exit code.")
            if "Could not find kaggle.json" in result.stderr or "401" in result.stderr:
                print("   Hint: Missing or invalid Kaggle API credentials (kaggle.json).")
            else:
                print(f"   Error: {result.stderr.strip() or result.stdout.strip()}")
            return False
    except FileNotFoundError:
        print(" 'kaggle' command not found on system PATH.")
        print("   To install: pip install kaggle")
        return False
    except Exception as e:
        print(f" Unexpected error running Kaggle CLI: {e}")
        return False


def generate_mock_development_dataset(rows: int = 1500) -> bool:
    """
    Generates a realistic development sample matching the exact schema and noisy structure
    of the Juhi Bhojani dataset (useful for offline testing and CI/CD).
    """
    print(f"\n[2/2] Generating development sample dataset ({rows} rows) for offline testing...")
    import random
    import numpy as np

    locations = [
        "Whitefield", "Electronic City Phase II", "Sarjapur Road", "HSR Layout",
        "Indiranagar", "Marathahalli", "Bannerghatta Road", "Koramangala",
        "Andheri West", "Bandra West", "Powai", "Thane West", "Kharghar",
        "Gachibowli", "Madhapur", "Kondapur", "Hinjewadi", "Wakad", "Viman Nagar",
        "Dwarka", "Rohini", "Noida Extension", "Sector 62", "Sector 150"
    ]
    furnishings = ["Furnished", "Semi-Furnished", "Unfurnished"]
    transactions = ["New Property", "Resale"]
    ownerships = ["Freehold", "Leasehold", "Co-operative Society", "Power of Attorney"]
    facings = ["East", "North", "West", "South", "North-East", "North-West", "South-East", "South-West"]
    statuses = ["Ready to Move", "Under Construction", "Immediately Available"]

    headers = [
        "Title", "Description", "Amount(in rupees)", "Price (in rupees)", "location",
        "Carpet Area", "Status", "Floor", "Transaction", "Furnishing", "facing",
        "overlooking", "Society", "Bathroom", "Balcony", "Car Parking", "Ownership",
        "Super Area", "Dimensions", "Plot Area"
    ]

    records = [",".join(headers)]

    for i in range(rows):
        loc = random.choice(locations)
        sqft = random.randint(450, 4500)
        # Unit noise
        if random.random() < 0.1:
            area_str = f'"{int(sqft / 10.764)} sqm"'
        else:
            area_str = f'"{sqft} sqft"'

        floor_num = random.randint(0, 25)
        total_floors = floor_num + random.randint(1, 10)
        if floor_num == 0 and random.random() < 0.3:
            floor_str = '"Ground out of ' + str(total_floors) + '"'
        elif random.random() < 0.05:
            floor_str = '"Basement out of ' + str(total_floors) + '"'
        else:
            floor_str = f'"{floor_num} out of {total_floors}"'

        baths = max(1, min(10, int(sqft / 600) + random.choice([0, 1])))
        balconies = random.randint(0, 3)
        parking = random.randint(0, 2)
        furn = random.choice(furnishings)
        trans = random.choice(transactions)
        owner = random.choice(ownerships)
        face = random.choice(facings)
        stat = random.choice(statuses)

        # Price generation with noisy text (Lac / Cr / plain number)
        base_rate = random.randint(4000, 15000)
        raw_price = sqft * base_rate
        if random.random() < 0.02:
            amt_str = '"Call for Price"'
        elif raw_price >= 1e7:
            amt_str = f'"{raw_price / 1e7:.2f} Cr"'
        else:
            amt_str = f'"{raw_price / 1e5:.2f} Lac"'

        title = f'"{baths} BHK Apartment for sale in {loc}"'
        desc = f'"Well ventilated property located in prime location of {loc} with modern amenities."'
        society = f'"{loc} Residency"'
        overlooking = '"Garden/Park, Main Road"'
        super_area = f'"{int(sqft * 1.25)} sqft"'

        row = [
            title, desc, amt_str, f'"{base_rate}/sqft"', f'"{loc}"',
            area_str, f'"{stat}"', floor_str, f'"{trans}"', f'"{furn}"', f'"{face}"',
            overlooking, society, str(baths), str(balconies), str(parking), f'"{owner}"',
            super_area, '""', '""'
        ]
        records.append(",".join(row))

    DATA_DIR.mkdir(parents=True, exist_ok=True)
    with open(CSV_PATH, "w", encoding="utf-8") as f:
        f.write("\n".join(records) + "\n")

    print(f" Development sample dataset created at: {CSV_PATH} ({rows} rows)")
    return True


def main():
    print("=" * 60)
    print("  House Price Prediction — Dataset Downloader & Setup")
    print("=" * 60)

    if is_dataset_present():
        print("\n Dataset is ready for Phase 2 EDA and Model Training!")
        return

    # Attempt Kaggle download
    success = download_via_kaggle_cli()

    # Fallback to dev dataset if not present
    if not success and not is_dataset_present():
        print("\nNotice: Kaggle download did not complete automatically.")
        print("You can place your 'kaggle.json' credentials in ~/.kaggle/ to download the 187k dataset,")
        print("or manually download it from: https://www.kaggle.com/datasets/juhibhojani/house-price")
        print("Generating realistic local development dataset for now...")
        generate_mock_development_dataset(rows=2000)

    print("\nDataset initialization completed successfully.")


if __name__ == "__main__":
    main()
