from utils.get_mongo_client import get_database
from fastapi import HTTPException
from bson import ObjectId

db_client = get_database("empms-db")

''' ========== insert_energy_record
* Inserts an energy reading from an ADE9000 Chip
* Collection Name = "ADE9000/{board_id}"
* payload: {<do be defined>}
'''
def insert_energy_record(board_id: int, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    payload['board_id'] = board_id
    collection_name.insert_one(payload)

def insert_energy_records(board_id: int, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    # collection_name.insert_many([payload])
    # collection_name.insert_many([payload])

#=================== BOARD MONGODB SERVICES=======================
def get_collection_items(board_id: int, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}-records']
    item_details = collection_name.find({ "board_id": board_id})
    response_list = []
    for item in item_details:
        response_list.append(item)
    return response_list

def create_board(board_id: int, board_type: str):
    collection_name = db_client["boards"]
    payload = {
        "_id": board_id,
        "board-type": board_type
    }
    collection_name.insert_one(payload)
    return payload

def get_board(board_id: int):
    collection_name = db_client['boards']
    board_info = collection_name.find_one({"_id":board_id})
    return board_info

def update_board_info(board_id: int, config):
    collection_name = db_client['boards']
    id_query = {"_id": board_id}
    new_config = { "$set": { "pin_config": config } }
    response = collection_name.update_one(id_query, new_config)
    print(response)
    return 1

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