from fastapi import FastAPI, Request, status, Depends
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from controllers import energy_reading_controllers
from controllers import board_controller
from pydantic import BaseModel
from fastapi.security import OAuth2PasswordBearer

class BoardData(BaseModel):
    VA_MAG: float
    VB_MAG: float
    IA_MAG: float
    IB_MAG: float

class BoardInformation(BaseModel):
    id: str
    board_type: str

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
@app.get("/")
def root():
    return "Hello EMP System!"

@app.post("/energy-records/{board_id}")
def insert_energy_record(board_id: int, data: BoardData):
    return energy_reading_controllers.insert_record_controller(board_id, data)

@app.get("/energy-records/{board_id}")
def get_energy_record(board_id: int, token: str = Depends(oauth2_scheme)):
    print(token)
    return energy_reading_controllers.get_records_controller(board_id)

@app.post("/boards")
def get_energy_record(data: BoardInformation):
    return board_controller.register_board(data)


# async def get_current_user(token: str = Depends(oauth2_scheme)):
#     user = fake_decode_token(token)
#     return user

# @app.get("/boards")
# async def get_board_info(current_user: User = Depends(get_current_user)):
#     return current_user

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.post("/login")
def login(data: BoardInformation):
    # user_dict = fake_users_db.get(form_data.username)
    # if not user_dict:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")
    # user = UserInDB(**user_dict)
    # hashed_password = fake_hash_password(form_data.password)
    # if not hashed_password == user.hashed_password:
    #     raise HTTPException(status_code=400, detail="Incorrect username or password")

    # return {"access_token": user.username, "token_type": "bearer"}
    response = board_controller.autenticate_board(data)
    return response

