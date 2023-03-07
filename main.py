from fastapi import FastAPI, Request, status, Depends, HTTPException
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from controllers import energy_reading_controllers
from controllers import board_controller
from controllers import security
from controllers import users_controllers
from pydantic import BaseModel
from fastapi.security import HTTPBearer
from utils.tools import get_config_file

http_token_bearer = HTTPBearer()
api_config = get_config_file("api.config.json")

class BoardData(BaseModel):
    VA_MAG: float
    VB_MAG: float
    IA_MAG: float
    IB_MAG: float

class BoardLoginInformation(BaseModel):
    id: str
    board_type: str

class BoardPinConfiguration(BaseModel):
    PIN_1: str or None
    PIN_2: str or None
    PIN_3: str or None
    PIN_4: str or None
    PIN_5: str or None

class UserInformation(BaseModel):
    username: str
    password: str
    email: str

class LoginUser(BaseModel):
    email: str
    password: str

app = FastAPI()

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
@app.get("/")
def root():
    return "Hello EMP System!"

#============ Energy Routes =====================
@app.post("/energy-records")
def insert_energy_record(data: BoardData, token: str = Depends(http_token_bearer)):
    board_id = security.verify_board_access_token(token)
    return energy_reading_controllers.insert_record_controller(board_id, data)

@app.get("/energy-records")
def get_energy_record(token: str = Depends(http_token_bearer)):
    board_id = security.verify_board_access_token(token)
    return energy_reading_controllers.get_records_controller(board_id)

#============ Board Routes =====================

@app.post("/boards/authenticate")
def login_board(data: BoardLoginInformation):
    return board_controller.autenticate_board(data)

@app.get("/boards")
async def get_board_info(token: str = Depends(http_token_bearer)):
    return board_controller.get_current_active_board(token)

@app.post("/boards")
def register_new_board(data: BoardLoginInformation):
    return board_controller.register_board(data)

#============ Users Routes =====================

@app.get("/users")
async def get_user_info(token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    print(user_id)
    return users_controllers.get_user_info(user_id)

@app.post("/users")
def register_new_user(data: UserInformation):
    return users_controllers.register_user(data)

@app.post("/users/login")
def login_user(data: LoginUser):
    return users_controllers.login_user(data)

#============ Other Stuff =====================

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )
