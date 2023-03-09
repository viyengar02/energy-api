from jose import jwt
from fastapi import HTTPException
from utils.tools import get_config_file
from datetime import datetime, timedelta
from fastapi.security import HTTPAuthorizationCredentials

api_config = get_config_file("api.config.json")

def create_board_access_token(board_id: str):
    expire = datetime.utcnow() + timedelta(hours=api_config['token_exp'])
    to_encode = {
        "id": board_id,
        "exp": expire
    }
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, api_config['secret'], algorithm=api_config['algorithm'])
    return encoded_jwt

def verify_board_access_token(token: HTTPAuthorizationCredentials):
    try:
        payload = jwt.decode(token.credentials, api_config['secret'], algorithms=[api_config['algorithm']])
        id = payload.get("id")
        #Check user_id
        if id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return id
    except Exception as error:
        print(f'Error occurred at verify_access_token: {error}')
        raise HTTPException(status_code=401, detail="Invalid token")

def create_user_access_token(board_id: str):
    expire = datetime.utcnow() + timedelta(hours=api_config['token_exp'])
    to_encode = {
        "user_id": board_id,
        "exp": expire
    }
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, api_config['secret'], algorithm=api_config['algorithm'])
    return encoded_jwt

def verify_user_access_token(token: HTTPAuthorizationCredentials):
    try:
        payload = jwt.decode(token.credentials, api_config['secret'], algorithms=[api_config['algorithm']])
        user_id = payload.get("user_id")
        #Check user_id
        if user_id is None:
            raise HTTPException(status_code=401, detail="Invalid token")
        return user_id
    except Exception as error:
        print(f'Error occurred at verify_access_token: {error}')
        raise HTTPException(status_code=401, detail="Invalid token")
    
# def extend_access_token():
#     return 1