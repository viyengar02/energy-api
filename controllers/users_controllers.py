from fastapi import HTTPException
from services import mongo_interface
from controllers import security
from fastapi.security import HTTPAuthorizationCredentials
import pymongo
#Creates a new user in the database
def register_user(payload):
    try:
        data = payload.dict()
        response = mongo_interface.create_user(data)
        return response
    except HTTPException as http_error:
        # If an HTTPException was raised, re-raise it
        raise http_error
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

#Authenticates user and generates a token
def login_user(user_credentials):
    try:
        data = user_credentials.dict()

        #Get Board Info from MongoDB
        user_info = check_user_auth(data)

        # Check if the credentials are valid
        if user_info is not None:
            # If the credentials are valid, create a JWT token
            token = security.create_user_access_token(user_info['_id'])
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

#Updates board_id for specified user
def update_user_board(user_id: str, board_id: str):
    try:
        response = mongo_interface.update_user_board(user_id, board_id)
        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

def update_user_config(user_id: str, data):
    try:
        config = data.dict()
        response = mongo_interface.update_user_config(user_id, config)
        return response
    except pymongo.errors.WriteError as e:
        # Handle the error
        print("Update failed:", e)
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
    
def check_user_auth(user_credentials):
    try:
        response = mongo_interface.check_user(user_credentials)
        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")

def get_user_info(user_id: str):
    try:
        response = mongo_interface.get_user(user_id)
        return response
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")
    return 1
def member_to_be_added(payload):
    try:
        data = payload.dict()
        response = mongo_interface.add_member(data)
        return response
    except HTTPException as http_error:
        raise http_error
    except Exception as error:
        print(f'Error occurred at register_board: {error}')
        raise HTTPException(status_code=500, detail="Internal Server Error")