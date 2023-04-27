from fastapi import WebSocket, WebSocketDisconnect
import asyncio
from pydantic import ValidationError
import json
from bson.json_util import dumps
from services import mongo_interface
from controllers import energy_reading_controllers
from utils import templates

class BoardWebsocket:
    def __init__(self, websocket: WebSocket, board_id: str):
        self.websocket = websocket
        self.board_id = board_id
        self.change_stream_task = None

    def __del__(self):
        self.stop_listener()
        
    async def start(self):
        await self.websocket.accept()
        self.change_stream_task = asyncio.create_task(self.conf_change_sub())

        while True:
            try:
                await self.board_ws_eventloop()
            except WebSocketDisconnect as e:
                print(f"WebSocket client {self.websocket.client.host} disconnected with code {e.code}")
                break
            except Exception as error:
                print(f'Websocket Error {error}')
                await self.websocket.send_text(f'Invalid message {error}')

    async def board_ws_eventloop(self):
        raw_message = await self.websocket.receive_text()
        print(raw_message)
        data = json.loads(raw_message)
        print(data)

        if data["action"] == "ping":
            pong_response = {
                "action": "pong"
            }
            await self.websocket.send_text(json.dumps(pong_response))
        elif data["action"] == "energy_record":
            await self.handle_energy_record(self.board_id, data["payload"])
        else:
            await self.websocket.send_text("Invalid or missing action")

    async def handle_energy_record(self, board_id: str, data):
        try:
            board_data = templates.BoardData(**data)
        except ValidationError as e:
            print(f'Validation Error For Energy Record {e}')
            await self.send_message({
                "message": f'Validation Error For Energy Record {e}'
            })
            return 1
        # The payload is valid, insert the board data into the database or do other processing
        response = energy_reading_controllers.insert_record_controller(board_id, board_data.dict())
        await self.send_message(response)
        return 0
    
    #Subscribes to changes for that the specific board configuration
    async def conf_change_sub(self):
        try:
            print("SUBSCRIBING1 ")
            change_stream =  mongo_interface.subscribe_board_config(self.board_id)
            async for change in change_stream:
                print("CHANGEEEEEEE")
                print(change)
                # Yield the change as a stream response
                # yield f"data: {change}\n\n"
        except Exception as error:
            print("conf_change_sub: ", error)

    def handle_config_event(self, event):
        print('Received event!!!!!:')
        print(dumps(event))

    async def voltage_thershold_optimization(self, user_id: str, threshold: int):
        return 0
    
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