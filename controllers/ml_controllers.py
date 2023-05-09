from fastapi import HTTPException
from services import ml_services

def run_xgboost_controller_v1():
    try:
        payload = ml_services.run_xgboost()
        return payload
    except Exception as error:
        print(f'Error occurred at run_xgboost_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def interior_lighting_controller(days: int):
    try:
        payload = ml_services.run_xgboost_interior_lighting(days)
        return payload
    except Exception as error:
        print(f'Error occurred at run_xgboost_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")