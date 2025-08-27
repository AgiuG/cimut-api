from fastapi import WebSocket, HTTPException
from typing import Dict
import json
import uuid
from datetime import datetime
import asyncio

class AgentService: 
    def __init__(self):
        self.active_agents: Dict[str, WebSocket] = {}
        self.agent_info: Dict[str, dict] = {}
        self.pending_responses: Dict[str, asyncio.Future] = {}
    
    async def register_agent(self, agent_id: str, websocket: WebSocket, info: dict):
        self.active_agents[agent_id] = websocket

        
        if agent_id in self.agent_info:
            self.agent_info[agent_id].update({
                **info,
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            })
        else:
            self.agent_info[agent_id] = {
                **info,
                'connected_at': datetime.now().isoformat(),
                'status': 'online'
            }

    async def unregister_agent(self, agent_id: str):
        if agent_id in self.active_agents:
            del self.active_agents[agent_id]
        if agent_id in self.agent_info:
            self.agent_info[agent_id]['status'] = 'offline'

        for command_id in list(self.pending_responses.keys()):
            if command_id.startswith(agent_id):
                future = self.pending_responses.pop(command_id, None)
                if future and not future.done():
                    future.cancel()
    
    async def handle_message(self, agent_id: str, message: str):
        try:
            data = json.loads(message)
            command_id = data.get('command_id')
            
            if command_id and command_id in self.pending_responses:
                future = self.pending_responses.pop(command_id)
                if not future.done():
                    future.set_result(data)
        
            
        except json.JSONDecodeError:
            pass 
    
    async def send_command(self, agent_id: str, command: dict) -> dict:
        if agent_id not in self.active_agents:
            raise HTTPException(status_code=404, detail="Agent not found or offline")
        
        websocket = self.active_agents[agent_id]
        command_id = str(uuid.uuid4())
        command['command_id'] = command_id

        future = asyncio.Future()
        self.pending_responses[command_id] = future

        try:
            await websocket.send_text(json.dumps(command))
            
            response = await asyncio.wait_for(future, timeout=10)
            return response
            
        except asyncio.TimeoutError:
            self.pending_responses.pop(command_id, None)
            raise HTTPException(status_code=408, detail="Agent response timeout")
        except Exception as e:
            self.pending_responses.pop(command_id, None)
            raise HTTPException(status_code=500, detail=str(e))