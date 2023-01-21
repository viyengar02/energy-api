from fastapi import FastAPI, Request, status
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from controllers import energy_reading_controllers
from controllers import board_controller
from pydantic import BaseModel

class BoardData(BaseModel):
    VA_MAG: float
    VB_MAG: float
    IA_MAG: float
    IB_MAG: float

class BoardInformation(BaseModel):
    id: str
    board_type: str

app = FastAPI()

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
@app.get("/")
def root():
    return {"message": "Hello World"}

@app.post("/energy-records/{board_id}")
def insert_energy_record(board_id: int, data: BoardData):
    return energy_reading_controllers.insert_record_controller(board_id, data)

@app.get("/energy-records/{board_id}")
def get_energy_record(board_id: int):
    return energy_reading_controllers.get_records_controller(board_id)

@app.post("/boards")
def get_energy_record(data: BoardInformation):
    return board_controller.register_board(data)

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

