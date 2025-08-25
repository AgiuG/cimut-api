from fastapi import APIRouter, HTTPException, Depends
from src.app.api.schemas.requests import (
  InjectionFaultRequest, 
  VerifyLineRequest
)
from src.app.services import FaultService

router = APIRouter()

service = FaultService()

@router.get("/")
async def root():
    return {"message": "Bem-vindo à API FastAPI!", "status": "online"}

@router.post("/fault")
def injection_fault(request: InjectionFaultRequest):
  try:
    response = service.change_line_content(
      request.host, 
      request.port, 
      request.user, 
      request.password, 
      request.file_path, 
      request.line_number, 
      request.new_content,
    )

    return {"response": response}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))


@router.post("/verify")
def verify_line(request: VerifyLineRequest):
  try:
    response = service.get_line_content(
      request.host, 
      request.port, 
      request.user, 
      request.password, 
      request.remote_file_path, 
      request.line_number,
    )
    
    return {"response": response}
  except Exception as e:
    raise HTTPException(status_code=500, detail=str(e))