# House Prices Dataset (India Real Estate)

## Dataset Overview
- **Source**: [House Price by Juhi Bhojani on Kaggle](https://www.kaggle.com/datasets/juhibhojani/house-price)
- **File Name**: `house_prices.csv`
- **Volume**: ~187,000 property listing records
- **Context**: Real estate listings across major Indian cities with property attributes, pricing, amenities, and locations.

---

## Column Data Dictionary

| Column Name | Expected Type | Description | Handling Notes in Pipeline |
| :--- | :--- | :--- | :--- |
| `Title` | Text / String | Listing heading summary | High cardinality / mostly descriptive |
| `Description` | Text / String | Extended property description | Freeform text / dropped in baseline model |
| `Amount(in rupees)` | Text / String | Raw price string (e.g. `"42 Lac"`, `"1.2 Cr"`, `"Call for Price"`) | Cleaned into numeric target `price_clean` |
| `Price (in rupees)` | Text / Numeric | Price per sqft or secondary price | Auxiliary reference |
| `location` | Categorical | Locality / neighborhood name | High cardinality $\rightarrow$ Top 50 + `"other"` |
| `Carpet Area` | Text / String | Usable floor area (e.g. `"1200 sqft"`, `"140 sqm"`) | Extracted & converted to standard `carpet_area_sqft` |
| `Super Area` | Text / String | Total built-up area including common areas | Secondary area feature |
| `Status` | Categorical | Possession state (e.g. `"Ready to Move"`, `"Under Construction"`) | Categorical indicator |
| `Floor` | Text / String | Floor description (e.g. `"3 out of 10"`, `"Ground"`, `"Basement"`) | Extracted to numeric `floor_num` |
| `Transaction` | Categorical | Type of sale (`"New Property"`, `"Resale"`) | One-Hot Encoded |
| `Furnishing` | Categorical | Furnishing level (`"Furnished"`, `"Semi-Furnished"`, `"Unfurnished"`) | One-Hot Encoded |
| `facing` | Categorical | Directional orientation (`"East"`, `"North"`, `"South"`, etc.) | One-Hot Encoded |
| `overlooking` | Text / String | View description (e.g. `"Garden/Park"`, `"Main Road"`) | High missingness |
| `Society` | Categorical | Gated society / apartment complex name | High cardinality |
| `Bathroom` | Numeric / Text | Number of bathrooms | Converted to integer, imputed with median |
| `Balcony` | Numeric / Text | Number of balconies | Converted to integer, imputed with median/0 |
| `Car Parking` | Numeric / Text | Number of parking spots | Converted to numeric |
| `Ownership` | Categorical | Title ownership (`"Freehold"`, `"Leasehold"`, etc.) | One-Hot Encoded |
| `Dimensions` | Text / String | Plot/room dimensions | Sparse / mostly empty |
| `Plot Area` | Text / String | Plot dimensions for independent houses | Sparse |

---

## Download Instructions

### Option A: Kaggle CLI (Recommended)
1. Install Kaggle CLI:
   ```bash
   pip install kaggle
   ```
2. Place your `kaggle.json` API token in `~/.kaggle/kaggle.json` (or `C:\Users\<user>\.kaggle\kaggle.json` on Windows).
3. Execute:
   ```bash
   kaggle datasets download -d juhibhojani/house-price -p notebooks/data --unzip
   ```

### Option B: Automated Script
Run the automated downloader script from the repository root:
```bash
python notebooks/download_dataset.py
```

### Option C: Manual Download
1. Visit [https://www.kaggle.com/datasets/juhibhojani/house-price](https://www.kaggle.com/datasets/juhibhojani/house-price).
2. Click **Download** and extract the zip archive.
3. Place `house_prices.csv` inside `notebooks/data/`.
