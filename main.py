from fastapi import FastAPI, Depends, HTTPException, Query, Security, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session
from typing import List
import models, schemas
from database import get_db, engine, Base
from fastapi.security import APIKeyHeader
import os
from dotenv import load_dotenv

# Carrega variáveis de ambiente
load_dotenv()

# Configuração da API Key
API_KEY = os.getenv("AUTHENTICATION_API_KEY")
if not API_KEY:
    raise ValueError("AUTHENTICATION_API_KEY não encontrada nas variáveis de ambiente")

# Configuração de segurança
api_key_header = APIKeyHeader(name="api-key", description="API Key para autenticação")

# Cria as tabelas no banco de dados
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Sistema de Gestão de Consultores V6",
    version="6.0.0",
    description="""
    API para gerenciamento de consultores com distribuição sequencial de atendimentos.
    
    ## Funcionalidades

    ### Distribuição de Atendimentos
    - Sistema inteligente de distribuição sequencial
    - Priorização baseada em último atendimento
    - Suporte a múltiplos idiomas
    - Controle de status online/offline
    - Integração com Pipedrive
    - Sistema de protocolos de atendimento

    ### Gestão de Consultores
    - Cadastro e atualização de consultores
    - Controle de status ativo/inativo
    - Gerenciamento de idiomas atendidos
    - Monitoramento de disponibilidade
    - ID do Pipedrive vinculado

    ### Protocolos de Atendimento
    - Geração automática de protocolos (#12345)
    - Histórico de atendimentos por consultor
    - Criação manual de protocolos
    - Endpoint separado para geração de protocolos

    ### Segurança
    - Autenticação via API Key
    - Todas as rotas protegidas
    - Gerenciamento de chaves de API

    ## Autenticação

    Todas as requisições devem incluir o header `api-key` com uma chave de API válida.
    """,
    openapi_tags=[
        {
            "name": "Distribuição",
            "description": "Endpoints relacionados à distribuição sequencial de atendimentos"
        },
        {
            "name": "Consultores",
            "description": "Operações de CRUD para gerenciamento de consultores"
        },
        {
            "name": "Status",
            "description": "Endpoints para gerenciamento de status dos consultores"
        },
        {
            "name": "Protocolos",
            "description": "Endpoints para gerenciamento de protocolos de atendimento"
        }
    ]
)

# Configuração CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Configuração de segurança global
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
    """
    Dependency para verificar a API Key em todas as rotas.
    """
    if api_key != API_KEY:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )
    return True

# Rotas de Distribuição
@app.get(
    "/consultor/da-vez",
    response_model=schemas.ConsultorDaVezResponse,
    tags=["Distribuição"],
    summary="Obter próximo consultor para atendimento",
    description="""
    Retorna o próximo consultor disponível para atendimento, selecionado com base em critérios específicos.
    
    A seleção é feita considerando:
    1. Status ativo na empresa (consultor deve estar ativo)
    2. Participação na distribuição sequencial (consultor deve estar participando)
    3. Status online (consultor deve estar online)
    4. Compatibilidade com o idioma solicitado (consultor deve atender no idioma)
    5. Tempo desde o último atendimento (prioriza quem está há mais tempo sem atender)

    Retorna também:
    - ID do Pipedrive do consultor
    - Número do protocolo (#12345)
    """
)
async def obter_consultor_da_vez(
    idioma: str = Query(
        ...,
        description="Código do idioma desejado (ex: pt, en, es)",
        example="pt"
    ),
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Endpoint para obter o próximo consultor disponível para atendimento.
    """
    return models.get_consultor_da_vez(db, idioma)

# Rotas de Protocolos
@app.post(
    "/protocolo",
    response_model=schemas.ProtocoloResponse,
    tags=["Protocolos"],
    summary="Criar novo protocolo",
    description="Cria um novo protocolo de atendimento manualmente para um consultor específico."
)
async def criar_protocolo(
    protocolo: schemas.ProtocoloCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Endpoint para criar um novo protocolo manualmente.
    """
    return models.criar_protocolo(db, protocolo.consultor_id)

@app.post(
    "/protocolo/gerar",
    response_model=schemas.ProtocoloResponse,
    tags=["Protocolos"],
    summary="Gerar novo número de protocolo",
    description="Gera um novo número de protocolo sem associá-lo a um consultor."
)
async def gerar_protocolo(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Endpoint para gerar um novo número de protocolo.
    """
    return models.gerar_novo_protocolo(db)

# Rotas de Consultores
@app.get(
    "/consultores",
    response_model=List[schemas.ConsultorResponse],
    tags=["Consultores"],
    summary="Listar todos os consultores",
    description="Retorna a lista completa de consultores cadastrados no sistema."
)
async def listar_consultores(
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Lista todos os consultores cadastrados no sistema.
    """
    return models.get_consultores(db)

@app.post(
    "/consultor",
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Criar novo consultor",
    description="Cria um novo consultor no sistema, incluindo opcionalmente o ID do Pipedrive."
)
async def criar_consultor(
    consultor: schemas.ConsultorCreate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Cria um novo consultor no sistema.
    """
    return models.criar_consultor(db, consultor)

@app.get(
    "/consultor/{consultor_id}",
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Obter consultor por ID",
    description="Retorna os detalhes de um consultor específico baseado em seu ID."
)
async def obter_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Obtém os detalhes de um consultor específico pelo ID.
    """
    consultor = models.get_consultor(db, consultor_id)
    if not consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    return consultor

@app.put(
    "/consultor/{consultor_id}",
    response_model=schemas.ConsultorResponse,
    tags=["Consultores"],
    summary="Atualizar consultor",
    description="Atualiza as informações de um consultor existente, incluindo o ID do Pipedrive."
)
async def atualizar_consultor(
    consultor_id: int,
    consultor: schemas.ConsultorUpdate,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Atualiza os dados de um consultor específico.
    """
    return models.atualizar_consultor(db, consultor_id, consultor)

@app.delete(
    "/consultor/{consultor_id}",
    tags=["Consultores"],
    summary="Remover consultor",
    description="Remove um consultor do sistema."
)
async def deletar_consultor(
    consultor_id: int,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Remove um consultor do sistema.
    """
    return models.deletar_consultor(db, consultor_id)

@app.put(
    "/consultor/{consultor_id}/connection",
    response_model=schemas.ConsultorResponse,
    tags=["Status"],
    summary="Atualizar status de conexão",
    description="Atualiza o status de conexão (online/offline) de um consultor."
)
async def atualizar_status_conexao(
    consultor_id: int,
    status: bool,
    db: Session = Depends(get_db),
    _: bool = Depends(verify_api_key)
):
    """
    Atualiza o status de conexão de um consultor.
    """
    return models.atualizar_status_conexao(db, consultor_id, status)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
