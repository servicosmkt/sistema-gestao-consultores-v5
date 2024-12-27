from sqlalchemy import Column, Integer, String, Boolean, DateTime, ARRAY, func, text, ForeignKey, inspect
from sqlalchemy.orm import Session, relationship
from database import Base, engine
import schemas
from datetime import datetime, timezone
from typing import List, Optional, Tuple
from fastapi import HTTPException

def check_table_exists(table_name: str) -> bool:
    """
    Verifica se uma tabela existe no banco de dados.
    """
    inspector = inspect(engine)
    return table_name in inspector.get_table_names()

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
    numero = Column(String, unique=True, index=True)  # Formato: #00001
    consultor_id = Column(Integer, index=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    def to_dict(self):
        """
        Converte o modelo para um dicionário com serialização adequada.
        """
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    def __json__(self):
        """
        Método especial para serialização JSON.
        """
        return self.to_dict()

class Consultor(Base):
    """
    Modelo de dados do Consultor.
    """
    __tablename__ = "consultores"

    id = Column(Integer, primary_key=True, index=True)
    nome = Column(String, index=True)
    email = Column(String, nullable=True)
    telefone = Column(String, nullable=True)
    idiomas = Column(ARRAY(String))
    status_ativo = Column(Boolean, default=True)
    status_ativo_sequencial = Column(Boolean, default=True)
    status_online = Column(Boolean, default=False)
    ultimo_atendimento = Column(DateTime(timezone=True), nullable=True)
    id_pipedrive = Column(Integer, nullable=True, index=True)

    def to_dict(self):
        """
        Converte o modelo para um dicionário com serialização adequada.
        """
        result = {}
        for key in self.__mapper__.c.keys():
            value = getattr(self, key)
            if isinstance(value, datetime):
                result[key] = value.isoformat()
            else:
                result[key] = value
        return result

    def __json__(self):
        """
        Método especial para serialização JSON.
        """
        return self.to_dict()

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
        consultor = db.query(Consultor).filter(Consultor.status_ativo == True).first()
        if not consultor:
            raise HTTPException(status_code=400, detail="Não há consultores ativos no sistema")
            
        numero = get_proximo_numero_protocolo(db)
        protocolo = Protocolo(
            numero=numero,
            consultor_id=consultor.id
        )
        db.add(protocolo)
        db.commit()
        db.refresh(protocolo)
        return protocolo
    except HTTPException:
        db.rollback()
        raise
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
        if consultor.email:
            existente = db.query(Consultor).filter(Consultor.email == consultor.email).first()
            if existente:
                raise HTTPException(status_code=400, detail="Email já cadastrado")

        agora = datetime.now(timezone.utc)
        db_consultor = Consultor(
            nome=consultor.nome,
            email=consultor.email,
            telefone=consultor.telefone,
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
    except HTTPException:
        db.rollback()
        raise
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro interno ao criar consultor: {str(e)}"
        )

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
    Retorna o próximo consultor disponível para atendimento e gera um protocolo.
    Query otimizada que seleciona e atualiza o consultor em uma única transação.
    """
    sql = text("""
        -- Primeiro, desabilita o trigger
        DROP TRIGGER IF EXISTS trg_create_protocol_on_consultant_selection ON consultores;
        
        -- Depois, seleciona e atualiza o consultor
        WITH consultor_selecionado AS (
            SELECT 
                c.id,
                c.nome,
                c.email,
                c.telefone,
                c.idiomas,
                c.status_online,
                c.id_pipedrive,
                NOW() as timestamp_atendimento
            FROM consultores c
            WHERE c.status_ativo = true
            AND c.status_ativo_sequencial = true
            AND c.status_online = true
            AND :idioma = ANY(c.idiomas)
            ORDER BY 
                COALESCE(c.ultimo_atendimento, '1970-01-01'::timestamptz) ASC,
                c.id ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
        ),
        consultor_atualizado AS (
            UPDATE consultores c
            SET ultimo_atendimento = cs.timestamp_atendimento
            FROM consultor_selecionado cs
            WHERE c.id = cs.id
            RETURNING 
                cs.*
        ),
        numero_protocolo AS (
            UPDATE controle_protocolo
            SET ultimo_numero = ultimo_numero + 1,
                updated_at = NOW()
            WHERE id = 1
            RETURNING ultimo_numero
        ),
        protocolo_gerado AS (
            INSERT INTO protocolos (numero, consultor_id, created_at)
            SELECT 
                '#' || LPAD(CAST(np.ultimo_numero AS TEXT), 5, '0'),
                ca.id,
                ca.timestamp_atendimento
            FROM consultor_atualizado ca
            CROSS JOIN numero_protocolo np
            RETURNING numero
        )
        SELECT 
            json_build_object(
                'consultor_id', ca.id,
                'consultor_nome', ca.nome,
                'consultor_email', ca.email,
                'consultor_telefone', ca.telefone,
                'consultor_idiomas', ca.idiomas,
                'consultor_status_online', ca.status_online,
                'consultor_atendimento_iso', ca.timestamp_atendimento,
                'consultor_id_pipedrive', ca.id_pipedrive,
                'numero_protocolo', pg.numero
            ) as result
        FROM consultor_atualizado ca
        CROSS JOIN protocolo_gerado pg;
    """)

    try:
        result = db.execute(sql, {"idioma": idioma}).fetchone()
        if not result:
            raise HTTPException(status_code=404, detail=f"Não há consultor disponível para o idioma {idioma}")

        data = result.result
        db.commit()
        return schemas.ConsultorDaVezResponse(**data)
    except Exception as e:
        db.rollback()
        raise HTTPException(
            status_code=500,
            detail=f"Erro ao selecionar consultor: {str(e)}"
        )

def get_protocolos(db: Session, consultor_id: Optional[int] = None, skip: int = 0, limit: int = 100) -> List[Protocolo]:
    """
    Retorna todos os protocolos com paginação.
    Se consultor_id for fornecido, filtra por consultor.
    """
    query = db.query(Protocolo)
    if consultor_id is not None:
        query = query.filter(Protocolo.consultor_id == consultor_id)
    return query.offset(skip).limit(limit).all()

def get_protocolo(db: Session, protocolo_id: int) -> Optional[Protocolo]:
    """
    Retorna um protocolo específico pelo ID.
    """
    return db.query(Protocolo).filter(Protocolo.id == protocolo_id).first()

def atualizar_protocolo(db: Session, protocolo_id: int, protocolo: schemas.ProtocoloUpdate) -> Optional[Protocolo]:
    """
    Atualiza os dados de um protocolo.
    """
    db_protocolo = get_protocolo(db, protocolo_id)
    if not db_protocolo:
        raise HTTPException(status_code=404, detail="Protocolo não encontrado")
    
    update_data = protocolo.dict(exclude_unset=True)
    for key, value in update_data.items():
        setattr(db_protocolo, key, value)
    
    db.commit()
    db.refresh(db_protocolo)
    return db_protocolo
