import matplotlib.pyplot as plt
import base64
from io import BytesIO
from fastapi import HTTPException
from services import mongo_interface
from datetime import datetime, timezone
import pydantic
from bson import ObjectId
pydantic.json.ENCODERS_BY_TYPE[ObjectId]=str

def demo_record_fetch(item_name: str):
    try:
        response = mongo_interface.get_demo_record(item_name)
        return response
    except Exception as error:
        raise Exception(f'Error occurred at insert_energy_record_controller: {error}')
    

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

def insert_dummy_record_controller(payload: dict):
    try:
        data = payload.dict()["data"]
        for item in data:
            item["_id"] = item.pop("id")

        mongo_interface.insert_energy_records_bulk(data)
        response = {
            "SUCCESSS": "A+"
        }
        return response
    except Exception as error:
        raise Exception(f'Error occurred at insert_energy_record_controller: {error}')


""" def get_records_controller(user_id: str):
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
 """
def get_records_controller(user_id: str):
    try:
        # Retrieve user information
        user_info = mongo_interface.get_user(user_id)

        # Check if the user's board ID exists
        if 'board_id' not in user_info:
            raise HTTPException(status_code=400, detail="Missing board ID from user information.")

        # Check the user's auth level
        auth_lvl = user_info.get('auth_lvl', 'user')  # Default to 'user' if not set

        # Determine records to retrieve based on auth level
        if auth_lvl == "admin":
            # Admin users can view all records
            records_list = mongo_interface.get_all_board_records()
        elif auth_lvl == "head":
            # Head users can view their own records and records of all users in their in_comm list
            records_list = []
            
            # Retrieve records for the head user's board ID
            records_list.extend(mongo_interface.get_board_records(user_info['board_id']))

            # Fetch records for users listed in the head user's in_comm
            in_comm_usernames = user_info.get('in_comm', [])
            for username in in_comm_usernames:
                # Find each user's board ID
                comm_user_info = mongo_interface.get_user(username)
                if comm_user_info and 'board_id' in comm_user_info:
                    # Add records for each user in in_comm
                    records_list.extend(mongo_interface.get_board_records(comm_user_info['board_id']))
        else:
            # Non-admin and non-head users can only see records associated with their board
            records_list = mongo_interface.get_board_records(user_info['board_id'])

        response = {
            "user_id": user_id,
            "auth_lvl": auth_lvl,
            "records": records_list
        }
        return response

    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        print(f'Error occurred at get_records_controller: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
