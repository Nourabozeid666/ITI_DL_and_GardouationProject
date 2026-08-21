"""
Data Cleaning & Feature Engineering Module for House Price Prediction
Dataset: House Price by Juhi Bhojani (Kaggle: juhibhojani/house-price)

Handles:
1. Parsing messy text prices (e.g. '42 Lac', '1.2 Cr', 'Call for Price') to numeric INR.
2. Parsing and converting area units (sqft / sqm -> standard sqft).
3. Parsing floor strings (e.g. '3 out of 10', 'Ground', 'Basement') to integer floor levels.
4. Handling missing values and numeric conversions for Bathroom, Balcony, Car Parking.
5. High-cardinality grouping for locations (Top-N + 'other').
6. Outlier removal based on price-per-sqft percentiles.
"""

import re
from typing import Any, Optional, List, Tuple
import pandas as pd
import numpy as np


def parse_amount(x: Any) -> Optional[float]:
    """
    Converts messy Indian property price strings to numeric INR.
    Examples:
        '42 Lac'         -> 4,200,000.0
        '1.2 Cr'         -> 12,000,000.0
        '85,00,000'      -> 8,500,000.0
        'Call for Price' -> None
    """
    if pd.isna(x) or not isinstance(x, (str, int, float)):
        return None
    if isinstance(x, (int, float)):
        return float(x) if x > 0 else None

    x_str = str(x).strip().lower().replace(",", "")
    if "call for price" in x_str or "price on request" in x_str:
        return None

    try:
        if "cr" in x_str:
            num = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x_str)[0])
            return num * 1e7
        elif "lac" in x_str or "lakh" in x_str:
            num = float(re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x_str)[0])
            return num * 1e5
        else:
            nums = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x_str)
            if nums:
                return float(nums[0])
            return None
    except (ValueError, IndexError):
        return None


def parse_area_to_sqft(x: Any) -> Optional[float]:
    """
    Extracts area values and normalizes units into square feet (sqft).
    1 sqm ≈ 10.764 sqft
    1 sqyrd ≈ 9 sqft
    """
    if pd.isna(x) or not isinstance(x, (str, int, float)):
        return None
    if isinstance(x, (int, float)):
        return float(x) if x > 0 else None

    x_str = str(x).strip().lower().replace(",", "")
    nums = re.findall(r"[-+]?(?:\d*\.\d+|\d+)", x_str)
    if not nums:
        return None

    val = float(nums[0])
    if "sqm" in x_str or "sq.m" in x_str or "sq meter" in x_str:
        return round(val * 10.764, 2)
    elif "sqyrd" in x_str or "sq.yrd" in x_str or "sq yard" in x_str:
        return round(val * 9.0, 2)
    return round(val, 2)


def parse_floor(x: Any) -> int:
    """
    Extracts floor level as integer:
        '3 out of 10' -> 3
        'Ground'      -> 0
        'Basement'    -> -1
        'Upper Basement' -> -1
        'Lower Basement' -> -2
    """
    if pd.isna(x):
        return 1  # Standard default floor level

    x_str = str(x).strip().lower()
    if "lower basement" in x_str:
        return -2
    if "basement" in x_str:
        return -1
    if "ground" in x_str:
        return 0

    nums = re.findall(r"[-+]?\d+", x_str)
    if nums:
        return int(nums[0])
    return 1


def clean_house_prices_dataset(
    df: pd.DataFrame,
    top_n_locations: int = 50,
    price_per_sqft_lower_pct: float = 0.01,
    price_per_sqft_upper_pct: float = 0.99,
) -> Tuple[pd.DataFrame, List[str]]:
    """
    Applies the full data cleaning and feature engineering pipeline on raw dataframe.

    Returns:
        Tuple of (cleaned DataFrame, list of allowed location categories)
    """
    data = df.copy()

    # 1. Clean Price
    price_col = "Amount(in rupees)" if "Amount(in rupees)" in data.columns else "price"
    data["price_clean"] = data[price_col].apply(parse_amount)
    data = data.dropna(subset=["price_clean"])
    data = data[data["price_clean"] > 0]

    # 2. Clean Area
    if "Carpet Area" in data.columns:
        data["carpet_area_sqft"] = data["Carpet Area"].apply(parse_area_to_sqft)
    elif "Super Area" in data.columns:
        data["carpet_area_sqft"] = data["Super Area"].apply(parse_area_to_sqft)
    else:
        data["carpet_area_sqft"] = None

    # Fallback to Super Area if Carpet Area is missing
    if "Super Area" in data.columns:
        data["carpet_area_sqft"] = data["carpet_area_sqft"].fillna(
            data["Super Area"].apply(parse_area_to_sqft)
        )

    data = data.dropna(subset=["carpet_area_sqft"])
    data = data[(data["carpet_area_sqft"] >= 100) & (data["carpet_area_sqft"] <= 50000)]

    # 3. Clean Floor
    if "Floor" in data.columns:
        data["floor_num"] = data["Floor"].apply(parse_floor)
    else:
        data["floor_num"] = 1

    # 4. Clean Bathrooms, Balconies
    if "Bathroom" in data.columns:
        data["bathroom"] = pd.to_numeric(data["Bathroom"], errors="coerce").fillna(2).astype(int)
    else:
        data["bathroom"] = 2

    if "Balcony" in data.columns:
        data["balcony"] = pd.to_numeric(data["Balcony"], errors="coerce").fillna(1).astype(int)
    else:
        data["balcony"] = 1

    data["bathroom"] = data["bathroom"].clip(lower=1, upper=20)
    data["balcony"] = data["balcony"].clip(lower=0, upper=10)

    # 5. Clean Categoricals
    cat_defaults = {
        "Furnishing": "Semi-Furnished",
        "Transaction": "Resale",
        "Ownership": "Freehold",
        "facing": "East",
    }
    for col, default_val in cat_defaults.items():
        if col in data.columns:
            data[col] = data[col].fillna(default_val).astype(str).str.strip()
        else:
            data[col] = default_val

    # 6. Group High-Cardinality Locations
    loc_col = "location" if "location" in data.columns else "Location"
    data["location_raw"] = data[loc_col].fillna("other").astype(str).str.strip()
    top_locations = (
        data["location_raw"]
        .value_counts()
        .head(top_n_locations)
        .index
        .tolist()
    )

    data["location_grouped"] = data["location_raw"].apply(
        lambda x: x if x in top_locations else "other"
    )
    allowed_locations = sorted(list(set(top_locations + ["other"])))

    # 7. Outlier Removal based on Price Per Sqft
    data["price_per_sqft"] = data["price_clean"] / data["carpet_area_sqft"]
    lower_limit = data["price_per_sqft"].quantile(price_per_sqft_lower_pct)
    upper_limit = data["price_per_sqft"].quantile(price_per_sqft_upper_pct)

    data_cleaned = data[
        (data["price_per_sqft"] >= lower_limit) &
        (data["price_per_sqft"] <= upper_limit)
    ].copy()

    # Drop intermediate and unneeded columns
    cols_to_drop = [
        "Index", "Title", "Description", "Dimensions", "Plot Area", "overlooking", "Society"
    ]
    for col in cols_to_drop:
        if col in data_cleaned.columns:
            data_cleaned = data_cleaned.drop(columns=[col])

    return data_cleaned, allowed_locations
