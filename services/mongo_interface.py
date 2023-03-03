from utils.get_mongo_client import get_database

db_client = get_database("empms-db")

''' ========== insert_energy_record
* Inserts an energy reading from an ADE9000 Chip
* Collection Name = "ADE9000/{board_id}"
* payload: {<do be defined>}
'''
def insert_energy_record(board_id: int, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}/{board_id}']
    # collection_name.insert_many([payload])
    collection_name.insert_one(payload)

def insert_energy_records(board_id: int, payload: dict, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}/{board_id}']
    # collection_name.insert_many([payload])
    # collection_name.insert_many([payload])

#Get Data From Connection
def get_collection_items(board_id: int, board_type = "ADE9000"):
    collection_name = db_client[f'{board_type}/{board_id}']
    item_details = collection_name.find()
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
    collection_name = db_client["boards"]
    board_info = collection_name.find_one({"_id":board_id})
    return board_info