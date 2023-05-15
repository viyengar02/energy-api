from models.predictions import run_predictions, run_predictions_v2
from fastapi import HTTPException

def run_xgboost(days: int):
    try:
        payload = run_predictions(days)
        predictions = payload[0]
        response = {
            "xgboost_predictions": predictions.tolist()
        }
        return response
    except Exception as error:
        print(f'Error occurred at load_xgboost: {error}')
        raise f'Error occurred at load_xgboost: {error}'
    
def run_compund_model(days: int):
    try:
        payload = run_predictions_v2(days)
        response = {
            "electricity-interior_lighting": {
                "predictions": payload['electricity-interior_lighting']["predictions"].tolist(),
                "flagged_times": payload['electricity-interior_lighting']["flagged_times"].tolist()
            },
            "electricity-fans": {
                "predictions": payload['electricity-fans']["predictions"].tolist(),
                "flagged_times": payload['electricity-fans']["flagged_times"].tolist()
            },
            "electricity-interior_equipment": {
                "predictions": payload['electricity-interior_equipment']["predictions"].tolist(),
                "flagged_times": payload['electricity-interior_equipment']["flagged_times"].tolist()
            }
        }
        return response
    except Exception as error:
        print(f'Error occurred at load_xgboost: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")