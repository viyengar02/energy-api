from fastapi import HTTPException
from services import mongo_interface
from datetime import datetime, timezone

def insert_record_controller(board_id: str, data: dict):
    try:
        current_date = datetime.now(timezone.utc).strftime('%Y-%m-%dT%H:%M:%S')
        data["_id"] = f'{current_date}'
        mongo_interface.insert_energy_record(board_id, data)
        response = {
            "action": "energy_record_response",
            "payload": data
        }
        return response
    except Exception as error:
        raise Exception(f'Error occurred at insert_energy_record_controller: {error}')

def get_records_controller(user_id: str):
    try:
        user_info = mongo_interface.get_user(user_id)

        if('board_id' not in user_info):
            raise HTTPException(status_code=400, detail="Missing board id from user information.")
            
        records_list = mongo_interface.get_board_records(user_info['board_id'])

        response = {
            "user_id": user_id,
            "board_type": "ADE9000",
            "records": records_list
        }
        return response
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        print(f'Error occurred at get_records_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")