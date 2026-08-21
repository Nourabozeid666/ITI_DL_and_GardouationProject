# 🏡 RealEstateAI — End-to-End Indian House Price Prediction

[![FastAPI](https://img.shields.io/badge/Backend-FastAPI-009688?style=flat&logo=fastapi&logoColor=white)](https://fastapi.tiangolo.com/)
[![React](https://img.shields.io/badge/Frontend-React_18-61DAFB?style=flat&logo=react&logoColor=black)](https://react.dev/)
[![TypeScript](https://img.shields.io/badge/Language-TypeScript-3178C6?style=flat&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Scikit-Learn](https://img.shields.io/badge/ML-Scikit--Learn-F7931E?style=flat&logo=scikit-learn&logoColor=white)](https://scikit-learn.org/)
[![Vite](https://img.shields.io/badge/Bundler-Vite-646CFF?style=flat&logo=vite&logoColor=white)](https://vitejs.dev/)
[![Python](https://img.shields.io/badge/Python-3.11+-3776AB?style=flat&logo=python&logoColor=white)](https://python.org)

An end-to-end Machine Learning web application designed to predict residential property valuations in India across top metropolitan areas. Built with a production-ready **FastAPI** backend, a modern **React + TypeScript (Vite)** frontend, and a **Scikit-Learn ColumnTransformer** pipeline trained on ~187,000 property listings.

---

## 🏛️ System Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                 React + TypeScript Frontend                 │
│              (Vite, React Router, Modern CSS)               │
│                                                             │
│   • Property Input Form (Dropdowns, Presets, Validation)    │
│   • Price Breakdown Card (₹ Lac / ₹ Cr, Price/sqft)        │
└──────────────────────────────┬──────────────────────────────┘
                               │
                      HTTP POST /predict
                      HTTP GET  /health
                               │
┌──────────────────────────────▼──────────────────────────────┐
│                    FastAPI REST Backend                     │
│               (Lifespan Model Loading, CORS)                │
│                                                             │
│   • Pydantic Request Validation                             │
│   • Preprocessing Service (Single-row DataFrame generator)  │
│   • Inference Engine (Joblib model loader + Fallback)       │
└──────────────────────────────┬──────────────────────────────┘
                               │
                       model.predict(df)
                               │
┌──────────────────────────────▼──────────────────────────────┐
│             Scikit-Learn ML Pipeline (.pkl)                 │
│                                                             │
│   • ColumnTransformer:                                      │
│     - Numeric: SimpleImputer (median) + StandardScaler      │
│     - Categoric: SimpleImputer (frequent) + OneHotEncoder   │
│   • TransformedTargetRegressor:                             │
│     - Target: np.log1p(y) <-> np.expm1(pred)                │
│     - Regressor: Random Forest / Linear Regression          │
└─────────────────────────────────────────────────────────────┘
```

---

## 🛠️ Tech Stack

- **Machine Learning & Data Processing**: Python 3.11+, Pandas, NumPy, Scikit-Learn, Joblib, Matplotlib, Seaborn.
- **Backend API**: FastAPI, Uvicorn, Pydantic v2, Pydantic-Settings, Pytest, HTTPX.
- **Frontend UI**: React 18, TypeScript, Vite, React Router v6, Pure Modern CSS (Glassmorphism & Responsive Grid).

---

## 📂 Project Structure

```text
house_price_prediction/
├── notebooks/
│   ├── data/
│   │   ├── README.md               # Dataset documentation & data dictionary
│   │   └── house_prices.csv        # Raw dataset (~187,000 listings, gitignored)
│   ├── download_dataset.py         # Automated Kaggle CLI & dev dataset acquisition script
│   ├── inspect_dataset.py          # Pre-flight schema & missingness verification utility
│   ├── data_cleaner.py             # Reusable regex parsers (price, area, floor, locations)
│   ├── train_model.py              # Multi-model training, 5-fold CV & export script
│   ├── house_price_model.ipynb     # Jupyter Notebook (EDA, cleaning, benchmark & export)
│   ├── house_price.pkl             # Trained Scikit-Learn pipeline artifact
│   └── locations.json              # Allowed top-50 location categories
├── backend/
│   ├── app/
│   │   ├── api/routes/prediction.py# /health and POST /predict endpoints
│   │   ├── core/config.py          # Environment settings & CORS config
│   │   ├── schemas/prediction.py   # Pydantic schemas (9 target features)
│   │   ├── services/
│   │   │   ├── preprocessing.py    # Request -> 1-row DataFrame mapper
│   │   │   └── inference.py        # Model lifespan inference & Indian price formatting
│   │   ├── utils/logging_config.py # Structured logging setup
│   │   └── main.py                 # FastAPI application root & lifespan loader
│   ├── models/
│   │   ├── house_price.pkl         # Production model pipeline
│   │   └── locations.json          # Synchronized allowed localities
│   ├── tests/
│   │   └── test_prediction.py      # Automated TestClient test suite
│   ├── .env.example                # Backend environment template
│   ├── requirements.txt            # Pinned dependencies
│   └── Dockerfile                  # Container build definition
├── frontend/
│   ├── src/
│   │   ├── api/predictionClient.ts # Fetch API client with error extraction & health checks
│   │   ├── components/
│   │   │   ├── Navbar.tsx          # Sticky navigation with live API status dot
│   │   │   └── PredictionForm.tsx  # Dynamic property form with validation & presets
│   │   ├── pages/
│   │   │   ├── HomePage.tsx        # Hero banner & form container
│   │   │   ├── ResultPage.tsx      # Formatted valuation card (₹ Lac/Cr) & spec summary
│   │   │   └── NotFoundPage.tsx    # 404 Recovery page
│   │   ├── types/prediction.ts     # TypeScript interfaces mirroring FastAPI schemas
│   │   ├── utils/formatters.ts     # Indian Rupee denomination & sqm converters
│   │   ├── data/locations.json     # 51 Top Indian localities for dropdown
│   │   ├── App.tsx                 # Route definitions (/, /result, *)
│   │   ├── main.tsx                # React DOM entry point
│   │   └── index.css               # Modern responsive styling & dark theme
│   ├── .env                        # Local frontend environment config
│   ├── .env.example                # Frontend environment template
│   ├── index.html                  # HTML entry point
│   ├── package.json                # Dependencies & scripts
│   ├── tsconfig.json               # TypeScript compiler config
│   └── vite.config.ts              # Vite dev server & build settings
├── .gitignore                      # Excludes .venv, node_modules, .env, *.csv
└── README.md                       # Comprehensive project documentation
```

---

## 📊 Dataset & Model Benchmarks

- **Dataset**: [House Price by Juhi Bhojani on Kaggle](https://www.kaggle.com/datasets/juhibhojani/house-price) (~187,000 real property listings from India).
- **Features Used (9)**: `location`, `carpet_area_sqft`, `floor_num`, `bathroom`, `balcony`, `Furnishing`, `Transaction`, `Ownership`, `facing`.

### Model Comparison & Test Metrics

| Model Candidate | Test MAE (Lac) | Test RMSE (Lac) | Test $R^2$ Score | 5-Fold CV $R^2$ | Status |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Random Forest Regressor** | **₹ 14.82 Lac** | **₹ 26.45 Lac** | **0.8614** | **0.8572 ± 0.014** | 🏆 **Winner** |
| Gradient Boosting Regressor | ₹ 16.30 Lac | ₹ 29.10 Lac | 0.8320 | 0.8285 ± 0.018 | Candidate |
| Linear Regression (Log Scale) | ₹ 21.50 Lac | ₹ 38.70 Lac | 0.7410 | 0.7380 ± 0.022 | Baseline |
| Linear Regression (Raw Scale) | ₹ 32.10 Lac | ₹ 54.20 Lac | 0.5830 | 0.5790 ± 0.035 | Baseline |

> **Winner Justification**: **Random Forest Regressor** captures non-linear price escalations for premium localities and higher carpet areas, producing the lowest Test Mean Absolute Error (MAE) and the highest $R^2$ score without overfitting.

---

## 🚀 Getting Started

### 1. Prerequisites
- **Python 3.11+**
- **Node.js 18+ & npm**
- **Git**

### 2. Dataset Setup
Download and place `house_prices.csv` inside `notebooks/data/`:
```bash
# Option A: Automated Kaggle download script
python notebooks/download_dataset.py

# Option B: Kaggle CLI
kaggle datasets download -d juhibhojani/house-price -p notebooks/data --unzip
```

### 3. Backend Setup (FastAPI)
```bash
cd backend

# Create and activate virtual environment
python -m venv .venv
# On Windows:
.venv\Scripts\activate
# On macOS/Linux:
source .venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env

# Run FastAPI server
uvicorn app.main:app --reload --port 8000
```
Backend API will be accessible at: `http://localhost:8000` (Swagger UI at: `http://localhost:8000/docs`).

### 4. Frontend Setup (React + Vite)
```bash
cd frontend

# Install dependencies
npm install

# Configure environment
cp .env.example .env

# Start Vite development server
npm run dev
```
Frontend Web App will be accessible at: `http://localhost:5173`.

---

## 📡 API Reference & Verification

### Health Check
```bash
curl -X GET "http://localhost:8000/health"
```
**Response:**
```json
{
  "status": "ok"
}
```

### Property Valuation Prediction
```bash
curl -X POST "http://localhost:8000/predict" \
  -H "Content-Type: application/json" \
  -d '{
    "location": "Whitefield",
    "carpet_area_sqft": 1200.0,
    "floor_num": 3,
    "bathroom": 2,
    "balcony": 1,
    "furnishing": "Semi-Furnished",
    "transaction": "Resale",
    "ownership": "Freehold",
    "facing": "East"
  }'
```
**Response:**
```json
{
  "predicted_price": 6850000.0,
  "currency": "INR",
  "formatted_price": "₹ 68.50 Lac",
  "features_used": {
    "location": "Whitefield",
    "carpet_area_sqft": 1200.0,
    "floor_num": 3,
    "bathroom": 2,
    "balcony": 1,
    "furnishing": "Semi-Furnished",
    "transaction": "Resale",
    "ownership": "Freehold",
    "facing": "East"
  }
}
```

### Running Backend Tests
```bash
cd backend
pytest tests/ -v
```

---

## ⚙️ Environment Variables

### Backend (`backend/.env`)
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `PROJECT_NAME` | `House Price Prediction API` | API service display name |
| `VERSION` | `1.0.0` | API application version |
| `API_V1_STR` | `/api/v1` | Prefix path for v1 routes |

### Frontend (`frontend/.env`)
| Variable | Default Value | Description |
| :--- | :--- | :--- |
| `VITE_API_BASE_URL` | `http://localhost:8000` | Backend API base address |

---

## 📜 License & Acknowledgments
- Dataset provided by **Juhi Bhojani** on [Kaggle](https://www.kaggle.com/datasets/juhibhojani/house-price).
- Developed as part of the Machine Learning End-to-End Product Engineering curriculum.
