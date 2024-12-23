from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, func, text
from sqlalchemy.orm import Session
from database import Base
import schemas
from datetime import datetime, timezone
from typing import List, Optional
from fastapi import HTTPException

class ApiKey(Base):
    """
    Modelo para armazenar as API Keys.
    """
    __tablename__ = "api_keys"

    id = Column(Integer, primary_key=True, index=True)
    key = Column(String, unique=True, index=True)
    description = Column(String)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class ControleProtocolo(Base):
    """
    Modelo para controlar o número atual do protocolo.
    """
    __tablename__ = "controle_protocolo"

    id = Column(Integer, primary_key=True)
    ultimo_numero = Column(Integer, default=0)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Protocolo(Base):
    """
    Modelo para armazenar protocolos de atendimento.
    """
    __tablename__ = "protocolos"

    id = Column(Integer, primary_key=True, index=True)
    numero = Column(String, unique=True, index=True)  # Formato: #12345
    consultor_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

class Consultor(Base):
    """
    Modelo de dados do Consultor.
    """
    __tablename__ = "consultores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    idiomas = Column(ARRAY(String))
    status_ativo = Column(Boolean, default=True)
    status_ativo_sequencial = Column(Boolean, default=True)
    status_online = Column(Boolean, default=False)
    ultimo_atendimento = Column(DateTime(timezone=True), nullable=True)
    id_pipedrive = Column(Integer, nullable=True, index=True)

def get_proximo_numero_protocolo(db: Session) -> str:
    """
    Gera o próximo número de protocolo.
    """
    controle = db.query(ControleProtocolo).first()
    if not controle:
        controle = ControleProtocolo(ultimo_numero=0)
        db.add(controle)
        db.commit()
        db.refresh(controle)
    
    controle.ultimo_numero += 1
    controle.updated_at = datetime.now(timezone.utc)
    db.commit()
    
    return f"#{controle.ultimo_numero:05d}"  # Formato: #00001

def gerar_novo_protocolo(db: Session) -> schemas.ProtocoloResponse:
    """
    Gera um novo número de protocolo sem associá-lo a um consultor.
    """
    try:
        numero = get_proximo_numero_protocolo(db)
        protocolo = Protocolo(
            numero=numero,
            consultor_id=0  # ID 0 indica protocolo não associado
        )
        db.add(protocolo)
        db.commit()
        db.refresh(protocolo)
        return protocolo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao gerar protocolo: {str(e)}")

def criar_protocolo(db: Session, consultor_id: int) -> Protocolo:
    """
    Cria um novo protocolo de atendimento.
    """
    try:
        numero = get_proximo_numero_protocolo(db)
        protocolo = Protocolo(
            numero=numero,
            consultor_id=consultor_id
        )
        db.add(protocolo)
        db.commit()
        db.refresh(protocolo)
        return protocolo
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar protocolo: {str(e)}")

def verify_api_key(db: Session, api_key: str) -> bool:
    """
    Verifica se a API Key é válida.
    """
    key = db.query(ApiKey).filter(
        ApiKey.key == api_key,
        ApiKey.is_active == True
    ).first()
    if not key:
        raise HTTPException(
            status_code=401,
            detail="API Key inválida"
        )
    return True

def get_consultores(db: Session) -> List[Consultor]:
    """
    Retorna todos os consultores.
    """
    return db.query(Consultor).all()

def get_consultor(db: Session, consultor_id: int) -> Optional[Consultor]:
    """
    Retorna um consultor específico pelo ID.
    """
    return db.query(Consultor).filter(Consultor.id == consultor_id).first()

def criar_consultor(db: Session, consultor: schemas.ConsultorCreate) -> Consultor:
    """
    Cria um novo consultor.
    """
    try:
        agora = datetime.now(timezone.utc)
        db_consultor = Consultor(
            nome=consultor.nome,
            idiomas=consultor.idiomas,
            status_ativo=consultor.status_ativo,
            status_ativo_sequencial=consultor.status_ativo_sequencial,
            status_online=consultor.status_online,
            ultimo_atendimento=agora,
            id_pipedrive=consultor.id_pipedrive
        )
        db.add(db_consultor)
        db.commit()
        db.refresh(db_consultor)
        return db_consultor
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Erro ao criar consultor: {str(e)}")

def atualizar_consultor(db: Session, consultor_id: int, consultor: schemas.ConsultorUpdate) -> Optional[Consultor]:
    """
    Atualiza os dados de um consultor.
    """
    db_consultor = get_consultor(db, consultor_id)
    if not db_consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    update_data = consultor.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_consultor, key, value)
    
    db.commit()
    db.refresh(db_consultor)
    return db_consultor

def deletar_consultor(db: Session, consultor_id: int) -> dict:
    """
    Remove um consultor do sistema.
    """
    db_consultor = get_consultor(db, consultor_id)
    if not db_consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    db.delete(db_consultor)
    db.commit()
    return {"detail": "Consultor removido com sucesso"}

def atualizar_status_conexao(db: Session, consultor_id: int, online: bool) -> Optional[Consultor]:
    """
    Atualiza o status de conexão de um consultor.
    """
    db_consultor = get_consultor(db, consultor_id)
    if not db_consultor:
        raise HTTPException(status_code=404, detail="Consultor não encontrado")
    
    db_consultor.status_online = online
    db.commit()
    db.refresh(db_consultor)
    return db_consultor

def get_consultor_da_vez(db: Session, idioma: str) -> schemas.ConsultorDaVezResponse:
    """
    Retorna o próximo consultor disponível para atendimento.
    Query otimizada que seleciona e atualiza o consultor em uma única transação.
    """
    sql = text("""
        WITH consultor_selecionado AS (
            SELECT 
                id,
                nome,
                idiomas,
                status_online,
                id_pipedrive
            FROM consultores
            WHERE status_ativo = true
            AND status_ativo_sequencial = true
            AND status_online = true
            AND :idioma = ANY(idiomas)
            ORDER BY 
                COALESCE(ultimo_atendimento, '1970-01-01'::timestamptz) ASC,
                id ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        ),
        consultor_atualizado AS (
            UPDATE consultores c
            SET ultimo_atendimento = NOW()
            FROM consultor_selecionado cs
            WHERE c.id = cs.id
            RETURNING 
                c.ultimo_atendimento as timestamp_atendimento,
                cs.id,
                cs.nome,
                cs.idiomas,
                cs.status_online,
                cs.id_pipedrive
        )
        SELECT 
            id,
            nome,
            idiomas,
            status_online,
            timestamp_atendimento,
            id_pipedrive
        FROM consultor_atualizado;
    """)

    try:
        result = db.execute(sql, {"idioma": idioma}).fetchone()
        if not result:
            print(f"[ERRO] Nenhum consultor disponível para o idioma {idioma}")
            raise HTTPException(
                status_code=404,
                detail=f"Nenhum consultor disponível para o idioma {idioma}"
            )
        db.commit()

        # Criar protocolo para o atendimento
        protocolo = criar_protocolo(db, result.id)

        response = schemas.ConsultorDaVezResponse(
            consultor_id=result.id,
            consultor_nome=result.nome,
            consultor_idiomas=result.idiomas,
            consultor_status_online=result.status_online,
            consultor_atendimento_iso=result.timestamp_atendimento.isoformat(),
            consultor_id_pipedrive=result.id_pipedrive,
            protocolo=protocolo.numero  # Número do protocolo
        )

        print(f"""
[INFO] Consultor selecionado:
- ID: {response.consultor_id}
- Nome: {response.consultor_nome}
- Idiomas: {', '.join(response.consultor_idiomas)}
- Status Online: {response.consultor_status_online}
- Último Atendimento: {response.consultor_atendimento_iso}
- ID Pipedrive: {response.consultor_id_pipedrive}
- Protocolo: {response.protocolo}
        """)

        return response
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao selecionar consultor: {str(e)}"
        )
