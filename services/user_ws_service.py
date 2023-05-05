from fastapi import WebSocket, WebSocketDisconnect
import json
from services import mongo_interface
import asyncio

class UserWebsocket:
    def __init__(self, websocket: WebSocket, user_id: str):
        self.websocket = websocket
        self.user_id = user_id
        self.energy_listener = None
        self.board_id = None
        self.energy_stream = None

    async def start(self):
        try:
            await self.get_user_board()
            await self.websocket.accept()
            self.energy_stream = asyncio.create_task(self.sub_energy_records())
        except Exception as error:
            await self.websocket.accept()
            print(f"Error when getting user info {error}")
            await self.websocket.close(code=500)
            return
    
        while True:
            try:
                await self.user_ws_eventloop()
            except WebSocketDisconnect as e:
                print(f"WebSocket client {self.websocket.client.host} disconnected with code {e.code}")
                await self.stop_listener()
                break
            except Exception as error:
                print(f'Websocket Error {error}')
                await self.websocket.send_text(f'Invalid message {error}')

    async def user_ws_eventloop(self):
        raw_message = await self.websocket.receive_text()
        data = json.loads(raw_message)
        print(data)
        if data["action"] == "ping":
            pong_response = {
                "action": "pong"
            }
            await self.send_message(pong_response)
        else:
            await self.websocket.send_text("Invalid or missing action")

    #Get the User's board id
    async def get_user_board(self):
        try:
            user_info = mongo_interface.get_user(self.user_id)
            self.board_id= user_info["board_id"]
        except Exception as error:
            print(f'Error when get_user_board {error}')
    
    #Subscribes to changes for that the specific board configuration
    async def sub_energy_records(self):
        try:
            change_stream =  mongo_interface.subscribe_energy_records(self.board_id)
            async for change in change_stream:
                await self.send_message(change['fullDocument'])
        except Exception as error:
            print("conf_change_sub: ", error)

    async def send_message(self, message):
        await self.websocket.send_text(json.dumps(message))
    
    async def close(self, code: int = 1000):
        await self.stop_listener()
        await self.websocket.close(code=code)

    async def stop_listener(self):
        if self.energy_stream and not self.energy_stream.done():
            is_canceled = self.energy_stream.cancel()
            try:
                if(is_canceled):
                    print("Energy Listener Stopped Successfully")
            except asyncio.CancelledError as e:
                print(f"Error trying to stop config listener {e}")
                pass
