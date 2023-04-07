from models.predictions import run_predictions

def run_xgboost():
    try:
        payload = run_predictions()
        predictions = payload[0]
        response = {
            "xgboost_predictions": predictions.tolist()
        }
        return response
    except Exception as error:
        print(f'Error occurred at load_xgboost: {error}')
        raise f'Error occurred at load_xgboost: {error}'