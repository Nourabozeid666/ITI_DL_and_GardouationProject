from typing import Dict
from fastapi import APIRouter, HTTPException, status

from app.schemas.prediction import PredictionRequest, PredictionResponse
from app.services.inference import inference_service
from app.utils.logging_config import logger

router = APIRouter(tags=["Prediction"])


@router.get("/health", status_code=status.HTTP_200_OK, tags=["Health"])
def health_check() -> Dict[str, str]:
    """
    Health check endpoint for the prediction service.
    Returns standard status 'ok'.
    """
    return {"status": "ok"}


@router.post(
    "/predict",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    summary="Predict House Price",
    description="Accepts property features and returns the predicted market price.",
)
@router.post(
    "/predict/",
    response_model=PredictionResponse,
    status_code=status.HTTP_200_OK,
    include_in_schema=False,
)
def predict_price(request: PredictionRequest) -> PredictionResponse:
    """
    Predicts house price given input property features.
    """
    try:
        logger.info(
            f"Prediction requested for location='{request.location}', "
            f"area={request.carpet_area_sqft} sqft, bath={request.bathroom}, floor={request.floor_num}"
        )
        response = inference_service.predict(request)
        return response
    except Exception as e:
        logger.error(f"Prediction failed with exception: {e}", exc_info=True)
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Inference service failed: {str(e)}",
        )


