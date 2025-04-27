from utils.get_mongo_client import get_database, get_database_2
from fastapi import HTTPException
from bson import ObjectId
import json

db_client = get_database("empms-db")

db_client_2 = get_database_2("empms-db")

''' ========== insert_energy_record
* Inserts an energy reading from an ADE9000 Chip
* Collection Name = "ADE9000/{board_id}"
* payload: {<do be defined>}
'''
def insert_energy_record(board_info: object, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    payload['board_info'] = board_info
    collection_name.insert_one(payload)

def insert_energy_records_bulk(payload: list, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    collection_name.insert_many(payload)

def insert_energy_record_demo(board_info: object, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    documents = payload["data"]  # Get the list of records
    collection_name.insert_many(documents)

#=================== BOARD MONGODB SERVICES=======================
def get_board_records(board_id: str, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    item_details = collection_name.find({ "board_info.board_id": board_id})
    response_list = []
    for item in item_details:
        response_list.append(item)
    return response_list

def get_demo_record(item_name: str):
    collection_name = db_client['data']
    item_info = collection_name.find_one({"name": item_name})
    if not item_info:
        return None
        
    # Convert MongoDB ObjectId to string
    item_info['_id'] = str(item_info['_id'])
    
    # Keep data as strings - we'll parse in the controller
    return item_info

#for admins to use
def get_all_board_records(board_type="ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    item_details = collection_name.find()  # No filter to get all records
    response_list = []
    for item in item_details:
        response_list.append(item)
    return response_list

def create_board(board_id: str, board_type: str, user_id: str):
    collection_name = db_client["boards"]
    payload = {
        "_id": board_id,
        "board-type": board_type,
        "user_id": user_id,
        "board_config": {
            "optimize": False,
            "power-threshold": None
        }
    }
    collection_name.insert_one(payload)
    return payload

def get_board(board_id: str):
    collection_name = db_client['boards']
    board_info = collection_name.find_one({"id":board_id})
    print("this is board info")
    print(board_info)
    return board_info

def delete_board_entry(board_id: int):
    collection_name = db_client['boards']
    id_query = {"_id": board_id}
    response = collection_name.delete_one(id_query)
    print(response)
    return 1

def update_board_config(board_id: str, optimization_config: object):
    collection_name = db_client['boards']
    filter = {'_id': board_id}
    update = {'$set': {"board_config": optimization_config}}
    collection_name.update_one(filter, update)
    board_info = get_board(board_id)
    return board_info

def subscribe_board_config(board_id: str):
    collection_name = db_client_2['boards']
    
    print("Subscribing for: ", board_id)
    pipeline = [
        {'$match': {'fullDocument._id': board_id}}
    ] 
    try:
        change_stream = collection_name.watch(pipeline=pipeline, full_document='updateLookup')
        return change_stream
    except Exception as e:
        print("An error occurred while creating the change stream:", e)
        raise

def subscribe_energy_records(board_id: str):
    collection_name = db_client_2['ADE9000-records']
    
    print("Subscribing for: ", board_id)
    pipeline = [
        {'$match': {'fullDocument.board_info.board_id': board_id}}
    ] 
    try:
        change_stream = collection_name.watch(pipeline=[], full_document='updateLookup')
        return change_stream
    except Exception as e:
        print("An error occurred while creating the change stream:", e)
        raise
#=================== USER MONGODB SERVICES=======================

def create_user(payload):
    collection_name = db_client['users']

    filter = {'email': payload['email']}
    
    update = {'$setOnInsert': payload}

    result = collection_name.update_one(filter, update, upsert=True)

    if result.upserted_id is not None:
        payload["_id"] = str(result.upserted_id)
        return payload
    else:
        raise HTTPException(status_code=409, detail="User Already Exists!")

def check_user(payload):
    collection_name = db_client['users']
    user_info = collection_name.find_one(payload)
    user_info["_id"] = str(user_info["_id"])
    return user_info
 
def get_user(user_id: str):
    collection_name = db_client['users']
    user_info = collection_name.find_one({"_id": ObjectId(user_id)})
    user_info["_id"] = str(user_info["_id"])
    return user_info


def update_user_board(user_id: str, board_id: str):
    collection_name = db_client['users']
    filter = {'_id': ObjectId(user_id)}
    update = {'$set': {"board_id": board_id}}
    user_info = collection_name.update_one(filter, update)
    return user_info
def add_member(payload):
    collection_name = db_client['users']
    higher_username = payload['higher']
    lower_username = payload['lower']

    # Retrieve the higher user
    higher_user = collection_name.find_one({"username": higher_username})
    if not higher_user:
        raise HTTPException(status_code=404, detail="Higher user not found.")

    # Retrieve the lower user
    lower_user = collection_name.find_one({"username": lower_username})
    if not lower_user:
        raise HTTPException(status_code=404, detail="Lower user not found.")

    # Update the in_comm list of the higher user
    if lower_username not in higher_user['in_comm'] & higher_user.get("auth_lvl").equals("head"):
        collection_name.update_one(
            {"username": higher_username},
            {"$addToSet": {"in_comm": lower_username}}  # Use $addToSet to avoid duplicates
        )
        return {"message": f"{lower_username} has been added under {higher_username}."}
    else:
        raise HTTPException(status_code=409, detail="User already exists under this hierarchy.")

def remove_member(payload):
    collection_name = db_client['users']
    higher_username = payload['higher']
    lower_username = payload['lower']

    # Retrieve the higher user
    higher_user = collection_name.find_one({"username": higher_username})
    if not higher_user:
        raise HTTPException(status_code=404, detail="Higher user not found.")

    # Ensure that the higher user has the correct authorization level
    if higher_user.get("auth_lvl") != "head":
        raise HTTPException(status_code=403, detail="User does not have permission to manage members.")

    # Check if the lower user is in the in_comm list of the higher user
    if lower_username in higher_user.get('in_comm', []):
        # Remove the lower user from the in_comm list
        collection_name.update_one(
            {"username": higher_username},
            {"$pull": {"in_comm": lower_username}}  # Use $pull to remove the user from the array
        )
        return {"message": f"{lower_username} has been removed from under {higher_username}."}
    else:
        raise HTTPException(status_code=404, detail="User not found in hierarchy.")


def update_user_config(user_id: str, config):
    collection_name = db_client['users']
    filter = {'_id': ObjectId(user_id)}
    update = {'$set': {"config": config}}
    collection_name.update_one(filter, update)
    user_info = get_user(user_id)    
    return user_info