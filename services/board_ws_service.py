from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from pydantic import ValidationError
import json
from services import mongo_interface
from controllers import energy_reading_controllers
from utils import templates
from controllers import ml_controllers
from cachetools import cached, TTLCache

class BoardWebsocket:
    def __init__(self, websocket: WebSocket, board_id: str):
        self.websocket = websocket
        self.board_id = board_id
        self.user_id = None
        self.user_config = None
        self.change_stream_task = None
        self.optimization = 0
        self.value = None # Optimization Threshold Or percent difference
        self.model_name = "electricity-fans"

    async def start(self):

        #Get the necessary configurations
        try:
            if(self.user_id is None):
                self.get_configurations()
            await self.websocket.accept()
            self.change_stream_task = asyncio.create_task(self.conf_change_sub())
        except Exception as error:
            print(f"Error when setting up configs {error}")
            await self.websocket.close(code=500)
            return
        
        while True:
            try:
                await self.board_ws_eventloop()
            except WebSocketDisconnect as e:
                print(f"WebSocket client {self.websocket.client.host} disconnected with code {e.code}")
                await self.stop_listener()
                break
            except Exception as error:
                print(f'Websocket Error {error}')
                await self.websocket.send_text(f'Invalid message {error}')

    async def board_ws_eventloop(self):
        raw_message = await self.websocket.receive_text()
        data = json.loads(raw_message)
        print(data)
        if data["action"] == "ping":
            pong_response = {
                "action": "pong"
            }
            await self.websocket.send_text(json.dumps(pong_response))
        elif data["action"] == "energy_record":
            await self.handle_energy_record(self.board_id, data)
        else:
            await self.websocket.send_text("Invalid or missing action")

    def get_configurations(self):
        board_info = mongo_interface.get_board(self.board_id)
        user_info = mongo_interface.get_user(board_info["user_id"])
        self.user_config = user_info['config']
        self.optimization = board_info['board_config']['optimize']
        self.value = board_info['board_config']['value']

    async def handle_energy_record(self, board_id: str, data):
        try:
            if 'ade_id' not in data or not isinstance(data['ade_id'], int):
                raise 'Missing or invalid ade_id'
            
            payload = data['payload']
            board_data = templates.BoardData(**payload)
            board_data = board_data.dict()
            board_info = {
                'board_id': board_id,
                'ade_id': data['ade_id']
            }
            await self.optimization_checker(board_data, data)
        except ValidationError as e:
            print(f'Validation Error For Energy Record {e}')
            await self.send_message({
                "message": f'Validation Error For Energy Record {e}'
            })
            return 1
        # The payload is valid, insert the board data into the database or do other processing
        response = energy_reading_controllers.insert_record_controller(board_info, board_data)
        await self.send_message(response)
        return 0
    
    #Subscribes to changes for that the specific board configuration
    async def conf_change_sub(self):
        try:
            change_stream =  mongo_interface.subscribe_board_config(self.board_id)
            async for change in change_stream:
                self.handle_config_event(change)
        except Exception as error:
            print("conf_change_sub: ", error)

    def handle_config_event(self, event):
        try:
            #Process the event
            board_config = event['fullDocument']['board_config']

            if (self.user_id is None):#Shouldn't happen
                self.user_id = event['fullDocument']['user_id']

            self.optimization = board_config['optimize'] 
            if(board_config['optimize'] == 1 or board_config['optimize'] == 2):
                self.value = board_config["value"]
            else:
                self.value = None
        except Exception as error:
            print(f"Error at handle_config_event {error}")

    async def optimization_checker(self, board_data: dict, data: dict):
        try:
            #Check for user settings and if missing - pull from database
            if(self.user_config is None):
                self.user_config = mongo_interface.get_user(self.user_id)['config']
            if(self.optimization == 1):#Handle Optimization through manual threshold
                await self.handle_optimization_th(data['ade_id'], board_data["POW_ACTIVE"], self.value)
            elif (self.optimization == 2):
                await self.handle_optimization_ml(data['ade_id'], board_data["POW_ACTIVE"])
        except Exception as error:
            print(f"Error at optimization_checker {error}")

    async def handle_optimization_ml(self, ade_id: int, board_power: float):
        try:
            #1) Run the ML model - hardcoded to 1 day
            predictions = self.get_predictions()
            next_hour_val = predictions[self.model_name]['predictions'][0]
            adjusted_th = next_hour_val*(1+self.value/100)#Adjust the theshold based on user config
            print(next_hour_val, adjusted_th)
            await self.handle_optimization_th(ade_id, board_power, adjusted_th)
        except Exception as error:
            print(f"Error at handle_optimization_ml {error}")

    #Handles optimization based on a user preset threhsold
    async def handle_optimization_th(self, ade_id: int, board_power: float, threshold: float):
        try:
            for key in self.user_config:
                if self.user_config[key] == ade_id and board_power > threshold:
                    await self.send_optimization_msg(key, "LOW")
                    break
                elif self.user_config[key] == ade_id and board_power < threshold:
                    await self.send_optimization_msg(key, "HIGH")
                    break
        except Exception as error:
            print(f"Error at handle_optimization_manual {error}")

        return 0
    
    async def send_optimization_msg(self, pin, value):
        optimization_msg = {
            "action": "pin_select",
            "payload": {}
        }
        optimization_msg["payload"][pin] = value
        await self.send_message(optimization_msg)

    # Cache with a maximum size of 1 and 2-minute TTL
    @cached(cache=TTLCache(maxsize=1, ttl=120))
    def get_predictions(self):
        return ml_controllers.run_xgboost_controller_compound(1)
    
    async def send_message(self, message):
        await self.websocket.send_text(json.dumps(message))
    
    async def close(self, code: int = 1000):
        await self.stop_listener()
        await self.websocket.close(code=code)

    async def stop_listener(self):
        if self.change_stream_task and not self.change_stream_task.done():
            is_canceled = self.change_stream_task.cancel()
            try:
                if(is_canceled):
                    print("Config Listener Stopped Successfully")
            except asyncio.CancelledError as e:
                print(f"Error trying to stop config listener {e}")
                pass