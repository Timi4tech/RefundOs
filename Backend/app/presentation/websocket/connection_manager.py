import asyncio
from fastapi import WebSocket
class ConnectionManager:
    def __init__(self):
        self.connections:dict[str,WebSocket]={}
        self._lock=asyncio.Lock()
    async def connect(self,connection_id:str,websocket:WebSocket):
        await websocket.accept()
        async with self._lock: self.connections[connection_id]=websocket
    async def send(self,connection_id:str,payload:dict)->bool:
        websocket=self.connections.get(connection_id)
        if not websocket: return False
        try: await websocket.send_json(payload); return True
        except Exception: await self.disconnect(connection_id); return False
    async def disconnect(self,connection_id:str):
        async with self._lock: self.connections.pop(connection_id,None)
connection_manager=ConnectionManager()
