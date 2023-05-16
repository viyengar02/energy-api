from fastapi import FastAPI, Request, status, Depends, WebSocket, WebSocketDisconnect
from fastapi.exceptions import RequestValidationError
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse
from utils import templates
from controllers import energy_reading_controllers
from controllers import optimizations_controllers
from controllers import board_controller
from controllers import security
from controllers import users_controllers
from controllers import ml_controllers
from fastapi.security import HTTPBearer
from utils.tools import get_config_file
from typing import Optional
from services.board_ws_service import BoardWebsocket
from services.user_ws_service import UserWebsocket

http_token_bearer = HTTPBearer()
api_config = get_config_file("api.config.json")

app = FastAPI()

#uvicorn main:app --reload --host 0.0.0.0 --port 8000
@app.get("/")
def root():
    return "Hello EMP System!"

#============ Energy Routes =====================

@app.get("/energy-records")
def get_energy_record(token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return energy_reading_controllers.get_records_controller(user_id)

@app.post("/energy-recordss")
def post_energy_records(data: templates.PostBoardData, token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return energy_reading_controllers.insert_dummy_record_controller(data)

#============ Board Routes =====================

@app.post("/boards/authenticate")
def login_board(data: templates.BoardLoginInformation):
    return board_controller.autenticate_board(data)

@app.get("/boards")
async def get_board_info(token: str = Depends(http_token_bearer)):
    return board_controller.get_current_active_board(token)

@app.post("/boards")
def register_new_board(data: templates.BoardLoginInformation, token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return board_controller.register_board(data, user_id)

#============ Users Routes =====================

@app.get("/users")
async def get_user_info(token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return users_controllers.get_user_info(user_id)

@app.post("/users")
def register_new_user(data: templates.UserInformation):
    return users_controllers.register_user(data)

@app.put("/users")
def configure_user(data: templates.BoardPinConfiguration, token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    print(data)
    return users_controllers.update_user_config(user_id, data)

@app.post("/users/login")
def login_user(data: templates.LoginUser):
    return users_controllers.login_user(data)

#============ ML Models Routes =====================
@app.get("/models/xgboost")
def run_xgboost(token: str = Depends(http_token_bearer), days: int = 1):
    user_id = security.verify_user_access_token(token)
    return ml_controllers.run_xgboost_controller_v1(days)

@app.get("/models/compound")
def run_xgboost(token: str = Depends(http_token_bearer), days: int = 1):
    user_id = security.verify_user_access_token(token)
    return ml_controllers.run_xgboost_controller_compound(days)

#============ Optimization Routes ===================
@app.post("/optimization/threshold")
def optimization_treshold(optimization_options: templates.OptimizationThreshold, token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return optimizations_controllers.enable_th_optimization(user_id, optimization_options)

#============ Other Stuff =====================

@app.exception_handler(RequestValidationError)
def validation_exception_handler(request: Request, exc: RequestValidationError):
    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
    )

@app.websocket("/boards/socket")
async def websocket_endpoint(websocket: WebSocket):
    # Perform authentication with JWT token
    board_id = None
    try:
        board_id = security.verify_board_access_token(websocket.headers.get("Authorization"))
    except Exception as error:
        print(error)
    
    if board_id is None: 
        await websocket.close(code=401)
        return

    board_ws = BoardWebsocket(websocket, board_id)
    
    # Call the start method of the BoardWebSocket class
    await board_ws.start()

users_ws = {}

@app.websocket("/users/socket")
async def websocket_endpoint(websocket: WebSocket):
    # Perform authentication with JWT token
    user_id = None
    try:
        user_id = security.verify_user_access_token(websocket.headers.get("Authorization"))
    except Exception as error:
        print(error)
    
    if user_id is None: 
        await websocket.close(code=401)
        return

    user_ws = UserWebsocket(websocket, user_id)
    # Call the start method of the BoardWebSocket class
    await user_ws.start()
    