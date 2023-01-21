from fastapi import HTTPException
from services import mongo_interface

def register_board(payload):
    try:
        data = payload.dict()
        response = mongo_interface.create_board(data["id"], data["board_type"])
        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# def get_board_info(board_id: int, board_type: str):
#     try:
#         response = mongo_interface.create_board(board_id, board_type)
#         return response
#     except Exception as error:
#         print(f'Error occurred at register_board: {error}')
#         raise HTTPException(status_code=500, detail="Internal Server Error")
