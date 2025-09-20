from fastapi import APIRouter, WebSocket, WebSocketDisconnect, HTTPException
from src.app.api.schemas.requests import (
    InjectionFaultRequest, 
    VerifyLineRequest
)
from src.app.services import agent_service_instance
import json

router = APIRouter()
        
service = agent_service_instance

@router.post("/agents/{agent_id}/find-fault-target")
async def find_fault_target(agent_id: str, request: dict):
    """Encontra arquivo alvo para injeção de falha baseado na pergunta do usuário"""
    try:
        user_query = request.get('query', '')
        
        if not user_query:
            raise HTTPException(status_code=400, detail="Query é obrigatória")
        
        response = await service.llm_injection_fault(agent_id, user_query)
        
        return response        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

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
        
        await service.register_agent(agent_id, websocket, reg_data)
        await websocket.send_text(json.dumps({
            'status': 'registered',
            'agent_id': agent_id
        }))

        while True:
            try:
                message = await websocket.receive_text()
                await service.handle_message(agent_id, message)
            except WebSocketDisconnect:
                break
    except WebSocketDisconnect:
        pass
    finally:
        if agent_id:
            await service.unregister_agent(agent_id)

@router.get("/agents")
async def list_agents():
    return {
        'agents': service.agent_info,
        'total': len(service.agent_info)
    }

@router.post("/agents/{agent_id}/fault")
async def agent_injection_fault(agent_id: str, request: InjectionFaultRequest): 
    command = {
        'action': 'modify_file',
        'file_path': request.file_path,
        'line_number': request.line_number,
        'new_content': request.new_content
    }

    try: 
        response = await service.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
@router.post("/agents/{agent_id}/verify")
async def agent_verify_line(agent_id: str, request: VerifyLineRequest):
    command = {
        'action': 'read_file',
        'file_path': request.file_path,
        'line_number': request.line_number
    }

    try: 
        response = await service.send_command(agent_id, command)
        return response
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))