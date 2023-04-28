from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from pydantic import ValidationError
import json
from services import mongo_interface
from controllers import energy_reading_controllers
from utils import templates

class BoardWebsocket:
    def __init__(self, websocket: WebSocket, board_id: str):
        self.websocket = websocket
        self.board_id = board_id
        self.user_id = None
        self.user_config = None
        self.change_stream_task = None
        self.optimization = False
        self.optimization_th = None

    def __del__(self):
        self.stop_listener()
        
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
                # self.get_configurations()
            except WebSocketDisconnect as e:
                print(f"WebSocket client {self.websocket.client.host} disconnected with code {e.code}")
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
        self.optimization_th = board_info['board_config']['power_threshold']

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
            if (self.optimization and self.optimization_th < board_data["POW_ACTIVE"]):
                await self.handle_optimization(data['ade_id'], is_low = True)
            elif (self.optimization and self.optimization_th > board_data["POW_ACTIVE"]):
                await self.handle_optimization(data['ade_id'], is_low = False)

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

            if(board_config['optimize']):
                self.optimization = True
                self.optimization_th = board_config["power_threshold"]
            else:
                self.optimization = False
                self.optimization_th = None
        except Exception as error:
            print(f"Error at handle_config_event {error}")

    async def handle_optimization(self, ade_id: int, is_low: bool):
        #get user id from database
        try:
            if(self.user_config is None):
                self.user_config = mongo_interface.get_user(self.user_id)['config']
            print("OPTIMIZATION CONFIGURATION: ", self.user_config)

            for key in self.user_config:
                if self.user_config[key] == ade_id and is_low:
                    await self.send_optimization_msg(key, "LOW")
                    print("SEND MESSAGE LOW")
                    break
                elif self.user_config[key] == ade_id and not is_low:
                    await self.send_optimization_msg(key, "HIGH")
                    print("SEND MESSAGE HIGH")
                    break
        except Exception as error:
            print(f"Error at handle_optimization {error}")

        return 0
    
    async def send_optimization_msg(self, pin, value):
        optimization_msg = {}
        optimization_msg[pin] = value
        await self.send_message(optimization_msg)

    async def send_message(self, message):
        await self.websocket.send_text(json.dumps(message))
    
    async def close(self, code: int = 1000):
        await self.stop_listener()
        await self.websocket.close(code=code)

    async def stop_listener(self):
        if self.change_stream_task and not self.change_stream_task.done():
            self.change_stream_task.cancel()
            try:
                await self.change_stream_task
            except asyncio.CancelledError as e:
                print(f"Error trying to stop config listener {e}")
                pass