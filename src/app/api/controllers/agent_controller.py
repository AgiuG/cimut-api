from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from typing import Dict, List
import json
import uuid
from datetime import datetime
import asyncio

router = APIRouter()

class AgentManager: 
    def __init__(self):
        self.active_agents: Dict[str, WebSocket] = {}
        self.agent_info: Dict[str, dict] = {}
    
    async def register_agent(self, agent_id: str, websocket: WebSocket, info: dict):
        self.active_agents[agent_id] = websocket
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
    
    async def send_command(self, agent_id: str, command: dict) -> dict:
        if agent_id not in self.active_agents:
            raise HTTPException(status_code=404, detail="Agent not found or offline")
        
        websocket = self.active_agents[agent_id]
        command_id = str(uuid.uuid4())
        command['command_id'] = command_id

        await websocket.send_text(json.dumps(command))

        try:
            response = await asyncio.wait_for(
                websocket.receive_text(),
                timeout=10
            )

            return json.loads(response)
        except asyncio.TimeoutError:
            raise HTTPException(status_code=408, detail="Agent response timeout")
        
agent_manager = AgentManager()

@router.websocket("/agent/connect")
async def agent_websocket(websocket: WebSocket):
    await websocket.accept()
    agent_id = None

    try:
        registration = await websocket.receive_text()
        reg_data = json.loads(registration)

        agent_id = reg_data.get('agent_id')
        if not agent_id:
            await websocket.send_text(json.dumps({
                'error': 'agent_id required'
            }))
            return
        
        await agent_manager.register_agent(agent_id, websocket, reg_data)
        await websocket.send_text(json.dumps({
            'status': 'registered',
            'agent_id': agent_id
        }))

        while True:
            try:
                message = await websocket.receive_text()
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        if agent_id:
            await agent_manager.unregister_agent(agent_id)

@router.get("/agents")
async def list_agents():
    return {
        'agents': agent_manager.agent_info,
        'total': len(agent_manager.agent_info)
    }

@router.post("/agents/{agent_id}/fault")
async def agent_injection_fault(agent_id: str, request: dict): 
    command = {
        'action': 'modify_file',
        'file_path': request['file_path'],
        'line_number': request['line_number'],
        'new_content': request['new_content']
    }

    try: 
        response = await agent_manager.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/agents/{agent_id}/verify")
async def agent_verify_line(agent_id: str, request: dict):
    command = {
        'action': 'read_file',
        'file_path': request['remote_file_path'],
        'line_number': request['line_number']
    }

    try: 
        response = await agent_manager.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))