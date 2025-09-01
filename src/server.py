from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from opentelemetry.instrumentation.fastapi import FastAPIInstrumentor
from src.app.api.controllers import AgentRouter
from src.app.api.controllers.agent_controller import initialize_embeddings
from logging import getLogger

logger = getLogger(__name__)

def init_routers(app_: FastAPI) -> None:
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
  
  # Startup event para inicializar embeddings
  @app_.on_event("startup")
  async def startup_event():
      logger.info("Inicializando embeddings da base de conhecimento...")
      try:
          initialize_embeddings()
          logger.info("Embeddings inicializados com sucesso!")
      except Exception as e:
          logger.error(f"Erro ao inicializar embeddings: {e}")
  
  init_routers(app_=app_)
  return app_

app = create_app()