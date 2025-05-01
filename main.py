#uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
#harrison use the above for local
#uvicorn main:socket_app --reload --host 172.20.10.10 --port 8000
#use the above with YOUR OWN IP for hosting 
from fastapi import FastAPI, HTTPException, Request, status, Depends, WebSocket, APIRouter, Body
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from jose import JWTError, jwt
from fastapi.middleware.cors import CORSMiddleware
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
from services import ml_services
from fastapi.security import HTTPBearer
from utils.tools import get_config_file
from typing import Optional
from services.board_ws_service import BoardWebsocket
from services.user_ws_service import UserWebsocket
from typing import Dict
import socketio

board_connections = {}

http_token_bearer = HTTPBearer()
api_config = get_config_file("api.config.json")

app = FastAPI()
sio = socketio.AsyncServer(cors_allowed_origins='*', async_mode='asgi')
socket_app = socketio.ASGIApp(sio, other_asgi_app=app)
router = APIRouter()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  
    allow_credentials=True,
    allow_methods=["*"], 
    allow_headers=["*"],  
)

security = HTTPBearer()

def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    try:
        token = credentials.credentials
        payload = jwt.decode(token, "alexiscool", algorithms=["HS256"])
        return payload
    except JWTError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials",
        )
    
def parseEnergyData(lst: templates.PostBoardData):
    for i in lst:
        i = 0
        # you have the template, step through every value based piece of the record and sum them. Avg at the end.
    return lst


#uvicorn main:socket_app --reload --host 0.0.0.0 --port 8000
#uvicorn main:socket_app --reload --host 172.20.10.10 --port 8000
#make sure to add board creds to the database for nate to connect to
#check ifconfig for broadcast ip
@app.get("/")
def root():
    return "Hello EMP System!"
#connecting to websocket
@sio.event
async def connect(sid, environ):
    print(f"Client connected: {sid}")
#websocket from lora to here to frontend
@app.post("/lora")
async def button_pressed(request: Request):
    print("Button pressed from secondary device!")
    await sio.emit("button_event", {"message": "Button was pressed!"})
    return JSONResponse(content={"status": "ok"})

#============ Energy Routes =====================

@app.get("/energy-records")
def get_energy_record(token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return energy_reading_controllers.get_records_controller(user_id)

@app.post("/energy-recordss")
def post_energy_records(data: templates.PostBoardData, token: str = Depends(http_token_bearer)):
    user_id = security.verify_user_access_token(token)
    return energy_reading_controllers.insert_dummy_record_controller(data)

@app.get("/energy_records/test")
def test(name: str):
    return energy_reading_controllers.demo_record_fetch(name)

@app.get("/energy_records/test_bulk")
def testBulk():
    return energy_reading_controllers.demo_record_fetch_bulk()

@app.post("/energy_data")
def post_energy_records(data: templates.PostBoardData):
    return parseEnergyData(energy_reading_controllers.insert_record_controller_demo("ADE9000",data))

#============ Board Routes =====================

@app.get("/demo")
def lora_ping():
    return "Lora ping received"

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

@app.get("/actuate")
async def actuate_outlet():
    message = {
        "action": "pin_select",
        "payload": {
            "PIN_1": "HIGH"  # Example payload
        }
    }
    print(board_connections)
    for board_id, connection in board_connections.items():
        try:
            await connection.websocket.send_json(message)
        except Exception as e:
            print(f"Error sending to board {board_id}: {e}")
    
    return {"status": "Command sent to all boards"}

#============ Users Routes =====================

# @app.get("/users")
# async def get_user_info(token: str = Depends(http_token_bearer)):
#     user_id = security.verify_user_access_token(token)
#     return users_controllers.get_user_info(user_id)

@app.get("/users")
async def get_user_info(username: str):
    return users_controllers.get_user_info(username)

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

@app.put("/users/hierarchy/add")
def add_member_under(data: templates.MemberToBeAdded):
    return users_controllers.member_to_be_added(data)

@app.put("/users/hierarchy/remove")
def add_member_under(data: templates.MemberToBeAdded):
    return users_controllers.member_to_be_removed(data)

@app.get("/test")
def testGetCall():
    return "succeeded get call"

#============ ML Models Routes =====================
@app.get("/models/xgboost")
def run_xgboost(token: str = Depends(http_token_bearer), days: int = 1):
    user_id = verify_token(token)
    return ml_controllers.run_xgboost_controller_v1(days)

@app.get("/models/compound")
def run_xgboost(token: str = Depends(http_token_bearer), days: int = 1):
    user_id = verify_token(token)
    return ml_controllers.run_xgboost_controller_compound(days)

@app.get("/models/refresh")
def refresh_flagged_times(phonenum: str, token: str = Depends(http_token_bearer), days: int = 1,):
    user_id = verify_token(token)
    predictions = ml_controllers.run_xgboost_controller_compound(days)
    return ml_services.send_pred_twilio(phonenum, predictions)

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
        #board_id = security.verify_board_access_token(websocket.headers.get("Authorization"))
        board_id = "680984395ae884f071d887ae"
    except Exception as error:
        print(error)
    
    if board_id is None: 
        await websocket.close(code=401)
        return

    board_ws = BoardWebsocket(websocket, board_id)
    print("this is where the board_ws prints")
    print(board_ws)
    board_connections[board_id] = board_ws
    
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
    print("this is where the user_ws prints")
    print(user_ws)
    # Call the start method of the BoardWebSocket class
    await user_ws.start()
