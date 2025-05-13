from models.predictions import run_predictions, run_predictions_v2
from fastapi import HTTPException
import requests
from requests.auth import HTTPBasicAuth
from urllib.parse import urlencode
import os

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



def send_pred_twilio(phonenum, predictions):
    filtered_response = {}

    for key, value in predictions.items():
        if value.get("flagged_times"):
            filtered_response[key] = {
                "flagged_times": value["flagged_times"]
            }

    return send_sms(phonenum, filtered_response)

def send_sms(phone_number, times):
    load_dotenv()
    url = f"https://api.twilio.com/2010-04-01/Accounts/{os.getenv('TWILIO_ACCOUNT_SID')}/Messages.json"

    auth = HTTPBasicAuth(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))

    print(os.getenv('TWILIO_ACCOUNT_SID'), os.getenv('TWILIO_AUTH_TOKEN'))
    
    body = "🚨 Power Consumption Alerts 🚨\n\n"

    for key, value in times.items():
        body += f"* {key.replace('-', ' ').title()}:\n"

        for i, time in enumerate(value['flagged_times'], 1):
            body += f"   {time}\n"

        body+="\n"
    
    headers = {
        'Content-Type': 'application/x-www-form-urlencoded'
    }
    
    data = {
        'To': phone_number,
        'From': os.getenv('TWILIO_PHONE_NUMBER'),
        'Body': body
    }
    
    response = requests.post(
        url,
        auth=auth,
        headers=headers,
        data=data
    )
    
    return response.json()
