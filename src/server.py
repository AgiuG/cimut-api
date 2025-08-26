from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.app.api.controllers import (
  FaultRouter,
  AgentRouter
)
from logging import getLogger

logger = getLogger(__name__)

def init_routers(app_: FastAPI) -> None:
  app_.include_router(FaultRouter)
  app_.include_router(AgentRouter, prefix="/api")

def create_app() -> FastAPI:
  app_ = FastAPI(
      title="FastAPI CIMut",
      description="FastAPI CIMut by Guilherme Silva",
      version="1.0.0",
  )

  FastAPIInstrumentor.instrument_app(app_)

  app_.add_middleware(
      CORSMiddleware,
      allow_origins=["*"],
      allow_credentials=True,
      allow_methods=["*"],
      allow_headers=["*"],
  )
  init_routers(app_=app_)
  return app_

app = create_app()