from fastapi import HTTPException
from services import mongo_interface
from controllers import security
from controllers import users_controllers
from fastapi.security import HTTPAuthorizationCredentials

def register_board(payload, user_id: str):
    try:
        data = payload.dict()

        #1. Check if board exists in the boards collection and remove it
        mongo_interface.delete_board_entry(data["id"])

        #2. Create a new board entry
        response = mongo_interface.create_board(data["id"], data["board_type"])

        #3. Update user board_id field
        users_controllers.update_user_board(user_id, data["id"])

        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")


def autenticate_board(payload):
    try:
        data = payload.dict()

        #Get Board Info from MongoDB
        board_info = get_board_info(data['id'])

        # Check if the credentials are valid
        if board_info is not None and data['id'] == board_info['_id'] and data['board_type'] == board_info['board-type']:
            # If the credentials are valid, create a JWT token
            token = security.create_board_access_token(data['id'])
            return {"token": token}
        # If the credentials are invalid, raise an HTTPException with a 401 status code
        raise HTTPException(status_code=401, detail="Invalid credentials")
    except HTTPException as http_error:
        # If an HTTPException was raised, re-raise it
        raise http_error
    except Exception as error:
        # If any other exception was raised, log the error and raise an HTTPException with a 500 status code
        print(f'Error occurred at autenticate_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

#Checks if the board id is authenticated and returns the board information
def get_current_active_board(token: HTTPAuthorizationCredentials):
    try:
        board_id = security.verify_board_access_token(token)
        board_info = get_board_info(board_id)

        if board_info is None:
            raise HTTPException(status_code=404, detail="Board Not Found")
        return board_info
    
    except HTTPException as http_error:
        # If an HTTPException was raised, re-raise it
        raise http_error
    except Exception as error:
        print(f'Error occurred at get_current_active_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_board_info(board_id: str):
    try:
        response = mongo_interface.get_board(board_id)
        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

# #Updates the pin configuration of a board in MongoDB
# def update_board_config(board_id: int, config):
#     try:
#         response = mongo_interface.create_board(board_id, config)
#         return response
#     except Exception as error:
#         print(f'Error occurred at register_board: {error}')
#         raise HTTPException(status_code=500, detail="Internal Server Error")
