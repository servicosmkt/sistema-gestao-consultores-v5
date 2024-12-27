from fastapi import FastAPI, Depends, HTTPException, Query, Security, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.encoders import jsonable_encoder
from fastapi.responses import JSONResponse, Response
import json
from sqlalchemy.orm import Session
from typing import List, Optional
import models, schemas
from database import get_db, engine, Base
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv
import logging
import time
from datetime import datetime

# Remover handlers existentes
logging.getLogger().handlers = []

# Configurar formato do log
formatter = logging.Formatter('%(asctime)s | %(message)s', '%Y-%m-%d %H:%M:%S')

# Configurar handler
handler = logging.StreamHandler()
handler.setFormatter(formatter)

# Configurar logger principal
logger = logging.getLogger("api")
logger.setLevel(logging.INFO)
logger.addHandler(handler)
logger.propagate = False

# Desabilitar outros loggers
logging.getLogger("uvicorn").setLevel(logging.WARNING)
logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
logging.getLogger("uvicorn.error").setLevel(logging.WARNING)

load_dotenv()

API_KEY = os.getenv("AUTHENTICATION_API_KEY")
if not API_KEY:
    raise ValueError("AUTHENTICATION_API_KEY não encontrada nas variáveis de ambiente")

api_key_header = APIKeyHeader(name="api-key", description="API Key para autenticação")

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Consultores V6",
    version="6.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Middleware para logging de requisições
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    
    # Gera ID único para a requisição
    request_id = f"{int(time.time() * 1000):x}"
    
    # Log da requisição
    request_log = {
        "id": request_id,
        "method": request.method,
        "path": request.url.path,
        "params": dict(request.query_params) if request.query_params else None
    }
    logger.info(f"REQ {request_id} | {json.dumps(request_log, separators=(',', ':'))}")
    
    try:
        response = await call_next(request)
        
        # Calcula o tempo de processamento
        process_time = time.time() - start_time
        
        # Captura o body da resposta
        response_body = [chunk async for chunk in response.body_iterator]
        
        # Recria o objeto de resposta com o body capturado
        response = Response(
            content=b"".join(response_body),
            status_code=response.status_code,
            headers=dict(response.headers),
            media_type=response.media_type
        )
        
        # Log da resposta
        try:
            body_json = json.loads(response.body)
            response_log = {
                "id": request_id,
                "status": response.status_code,
                "time": f"{process_time:.2f}s",
                "data": body_json
            }
        except:
            response_log = {
                "id": request_id,
                "status": response.status_code,
                "time": f"{process_time:.2f}s"
            }
        
        logger.info(f"RES {request_id} | {json.dumps(response_log, separators=(',', ':'))}")
        return response
        
    except Exception as e:
        # Log de erro caso algo falhe durante o processamento
        error_log = {
            "id": request_id,
            "method": request.method,
            "path": request.url.path,
            "error": str(e)
        }
        logger.error(f"ERR {request_id} | {json.dumps(error_log, separators=(',', ':'))}")
        raise

security_scheme = {
    "type": "apiKey",
    "in": "header",
    "name": "api-key",
    "description": "API Key para autenticação"
}

app.openapi_components = {
    "securitySchemes": {
        "ApiKeyAuth": security_scheme
    }
}

app.openapi_security = [{"ApiKeyAuth": []}]

async def verify_api_key(api_key: str = Security(api_key_header)):
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )
    return True

@app.get(
    "/consultor/da-vez",
    response_model=schemas.ConsultorDaVezResponse,
    tags=["Distribuição"],
    summary="Obter próximo consultor para atendimento",
    description="Retorna o próximo consultor disponível baseado em idioma, status e tempo de espera"
)
async def obter_consultor_da_vez(
    idioma: str = Query(..., example="pt"),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.get_consultor_da_vez(db, idioma)

@app.get(
    "/consultores", 
    response_model=List[schemas.ConsultorResponse],
    tags=["Consultores"],
    summary="Listar consultores",
    description="Retorna a lista de todos os consultores cadastrados"
)
async def listar_consultores(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.get_consultores(db)

@app.post(
    "/consultor",
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Criar consultor",
    description="Cadastra um novo consultor no sistema"
)
async def criar_consultor(
    consultor: schemas.ConsultorCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.criar_consultor(db, consultor)

@app.get(
    "/consultor/{consultor_id}", 
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Obter consultor",
    description="Retorna os dados de um consultor específico"
)
async def obter_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    consultor = models.get_consultor(db, consultor_id)
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    return consultor

@app.put(
    "/consultor/{consultor_id}",
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Atualizar consultor",
    description="Atualiza os dados de um consultor existente"
)
async def atualizar_consultor(
    consultor_id: int,
    consultor: schemas.ConsultorUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.atualizar_consultor(db, consultor_id, consultor)

@app.delete(
    "/consultor/{consultor_id}",
    tags=["Consultores"],
    summary="Remover consultor",
    description="Remove um consultor do sistema"
)
async def deletar_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.deletar_consultor(db, consultor_id)

@app.put(
    "/consultor/{consultor_id}/connection",
    response_model=schemas.ConsultorResponse,
    tags=["Status"],
    summary="Atualizar status",
    description="Atualiza o status online/offline do consultor"
)
async def atualizar_status_conexao(
    consultor_id: int,
    status: bool,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.atualizar_status_conexao(db, consultor_id, status)

@app.get(
    "/protocolos",
    response_model=List[schemas.ProtocoloResponse],
    tags=["Protocolos"],
    summary="Listar protocolos",
    description="Retorna a lista de protocolos com paginação e filtro por consultor"
)
async def listar_protocolos(
    consultor_id: Optional[int] = Query(None),
    skip: int = Query(0),
    limit: int = Query(100),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.get_protocolos(db, consultor_id=consultor_id, skip=skip, limit=limit)

@app.get(
    "/protocolo/{protocolo_id}",
    response_model=schemas.ProtocoloResponse,
    tags=["Protocolos"],
    summary="Obter protocolo",
    description="Retorna os dados de um protocolo específico"
)
async def obter_protocolo(
    protocolo_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    protocolo = models.get_protocolo(db, protocolo_id)
    if not protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")
    return protocolo

@app.put(
    "/protocolo/{protocolo_id}",
    response_model=schemas.ProtocoloResponse,
    tags=["Protocolos"],
    summary="Atualizar protocolo",
    description="Atualiza os dados de um protocolo existente"
)
async def atualizar_protocolo(
    protocolo_id: int,
    protocolo: schemas.ProtocoloUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    return models.atualizar_protocolo(db, protocolo_id, protocolo)

@app.get(
    "/gerar-protocolo",
    response_model=schemas.NovoProtocoloResponse,
    tags=["Protocolos"],
    summary="Gerar protocolo",
    description="Gera um novo número de protocolo sequencial"
)
async def gerar_novo_protocolo(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    protocolo = models.gerar_novo_protocolo(db)
    return schemas.NovoProtocoloResponse(numero_protocolo=protocolo.numero)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
