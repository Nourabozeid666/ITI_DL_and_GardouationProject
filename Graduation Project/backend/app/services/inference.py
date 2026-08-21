import pickle
from pathlib import Path
from typing import Any, Optional

import joblib
import numpy as np
import pandas as pd

from app.core.config import settings
from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.preprocessing import preprocessing_service
from app.utils.logging_config import logger


def format_inr(amount: float) -> str:
    """Formats numeric amount into Indian denomination string (₹ ... Lac / ₹ ... Cr)."""
    if amount >= 10000000:
        cr = amount / 10000000.0
        return f"₹ {cr:.2f} Cr"
    elif amount >= 100000:
        lac = amount / 100000.0
        return f"₹ {lac:.2f} Lac"
    else:
        return f"₹ {amount:,.0f}"


class InferenceService:
    def __init__(self, model_path: Path = settings.MODEL_PATH):
        self.model_path = model_path
        self.model: Optional[Any] = None
        self.load_model()

    def load_model(self) -> bool:
        """
        Loads the scikit-learn model/pipeline from disk using joblib.
        Falls back to notebooks/house_price.pkl if the backend/models copy is absent.
        """
        search_paths = [
            self.model_path,
            settings.BASE_DIR.parent / "notebooks" / "house_price.pkl",
        ]

        for path in search_paths:
            if path.exists():
                try:
                    # Attempt joblib loading first
                    self.model = joblib.load(path)
                    logger.info(f"ML model successfully loaded from {path}")
                    return True
                except Exception as e_joblib:
                    logger.debug(f"joblib.load failed for {path}: {e_joblib}, trying pickle...")
                    try:
                        with open(path, "rb") as f:
                            self.model = pickle.load(f)
                        logger.info(f"ML model loaded via pickle from {path}")
                        return True
                    except Exception as e_pickle:
                        logger.error(f"Failed to load model from {path}: {e_pickle}")

        logger.warning(
            f"No valid ML model found at {self.model_path}. "
            "InferenceService will use heuristic fallback."
        )
        self.model = None
        return False

    def predict(self, request: PredictionRequest) -> PredictionResponse:
        """
        Executes price prediction for the given request.
        Passes a single-row DataFrame to the pipeline if available,
        or uses a fallback estimation algorithm if the model artifact is a placeholder.
        """
        df: pd.DataFrame = preprocessing_service.preprocess_to_df(request)

        if self.model is not None and hasattr(self.model, "predict"):
            try:
                pred = self.model.predict(df)
                # Extract first prediction value
                if isinstance(pred, (list, np.ndarray, pd.Series)):
                    raw_price = float(pred[0])
                else:
                    raw_price = float(pred)
                price = raw_price
            except Exception as e:
                logger.warning(
                    f"Model predict failed with error: {e}. "
                    "Falling back to heuristic calculation."
                )
                price = self._heuristic_prediction(request)
        else:
            price = self._heuristic_prediction(request)

        price = round(float(price), 2)
        formatted = format_inr(price)

        return PredictionResponse(
            predicted_price=price,
            currency="INR",
            formatted_price=formatted,
            features_used=request,
        )

    def _heuristic_prediction(self, request: PredictionRequest) -> float:
        """Fallback baseline estimation when a fully-trained ML model is not available."""
        base_rate = 5500.0  # ₹ per sqft baseline
        area_component = request.carpet_area_sqft * base_rate
        bath_component = request.bathroom * 75000.0
        balcony_component = request.balcony * 30000.0
        floor_component = max(0, request.floor_num) * 15000.0

        furnishing_multiplier = {
            "Furnished": 1.15,
            "Semi-Furnished": 1.05,
            "Unfurnished": 1.0,
        }.get(request.furnishing, 1.0)

        total = (area_component + bath_component + balcony_component + floor_component) * furnishing_multiplier
        return round(total, 2)


inference_service = InferenceService()
