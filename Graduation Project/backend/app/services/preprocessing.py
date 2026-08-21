import json
from pathlib import Path
from typing import Set

import pandas as pd

from app.core.config import settings
from app.schemas.prediction import PredictionRequest
from app.utils.logging_config import logger


class PreprocessingService:
    def __init__(self, locations_path: Path = settings.LOCATIONS_PATH):
        self.locations_path = locations_path
        self.allowed_locations: Set[str] = self._load_allowed_locations()

    def _load_allowed_locations(self) -> Set[str]:
        """
        Loads the list of allowed locations exported during training.
        Falls back to notebooks/locations.json if the model directory copy does not exist.
        """
        search_paths = [
            self.locations_path,
            settings.BASE_DIR.parent / "notebooks" / "locations.json",
        ]
        for path in search_paths:
            if path.exists():
                try:
                    with open(path, "r", encoding="utf-8") as f:
                        locations = json.load(f)
                        if isinstance(locations, list):
                            logger.info(f"Loaded {len(locations)} allowed locations from {path}")
                            return set(locations)
                except Exception as e:
                    logger.warning(f"Failed to load locations from {path}: {e}")

        logger.warning(
            "Allowed locations file not found. "
            "Unmatched locations will default to 'other'."
        )
        return set()

    def reload_locations(self) -> None:
        """Reload allowed locations from disk."""
        self.allowed_locations = self._load_allowed_locations()

    def preprocess_to_df(self, request: PredictionRequest) -> pd.DataFrame:
        """
        Transforms a PredictionRequest into a single-row pandas DataFrame
        with the exact column schema expected by the scikit-learn training pipeline:
        ['carpet_area_sqft', 'floor_num', 'bathroom', 'balcony', 'location_grouped',
         'Furnishing', 'Transaction', 'Ownership', 'facing']
        """
        loc = request.location.strip()
        location_grouped = loc if (self.allowed_locations and loc in self.allowed_locations) else "other"

        row = {
            "carpet_area_sqft": [float(request.carpet_area_sqft)],
            "floor_num": [int(request.floor_num)],
            "bathroom": [int(request.bathroom)],
            "balcony": [int(request.balcony)],
            "location_grouped": [location_grouped],
            "Furnishing": [str(request.furnishing)],
            "Transaction": [str(request.transaction)],
            "Ownership": [str(request.ownership)],
            "facing": [str(request.facing)],
        }

        return pd.DataFrame(row)

    def preprocess_input(self, request: PredictionRequest) -> pd.DataFrame:
        """Alias for preprocess_to_df."""
        return self.preprocess_to_df(request)


preprocessing_service = PreprocessingService()

