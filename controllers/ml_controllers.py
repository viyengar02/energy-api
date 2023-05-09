from fastapi import HTTPException
from services import ml_services

def run_xgboost_controller_v1(days: int):
    try:
        payload = ml_services.run_xgboost(days)
        return payload
    except Exception as error:
        print(f'Error occurred at run_xgboost_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def run_xgboost_controller_compound(days: int):
    try:
        payload = ml_services.run_compund_model(days)
        return payload
    except Exception as error:
        print(f'Error occurred at run_xgboost_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")