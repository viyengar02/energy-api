from fastapi import WebSocket, WebSocketDisconnect
from controllers import energy_reading_controllers
import json

class BoardWebsocket:
    def __init__(self, websocket: WebSocket, board_id: str):
        print("RUNS")
        self.websocket = websocket
        self.board_id = board_id

    async def start(self):
        await self.websocket.accept()

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
            response = energy_reading_controllers.insert_record_controller(self.board_id, data["payload"])
            await self.websocket.send_text(json.dumps(response))
        else:
            await self.websocket.send_text("Invalid or missing action")

    async def send_message(self, message):
        await self.websocket.send_text(json.dumps(message))

    async def close(self, code: int = 1000):
        await self.websocket.close(code=code)