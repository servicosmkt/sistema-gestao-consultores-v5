from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConsultorBase(BaseModel):
    nome: str
    email: str
    telefone: Optional[str] = None
    idiomas: List[str]
    status_ativo: bool = True
    status_ativo_sequencial: bool = True
    status_online: bool = False
    id_pipedrive: Optional[int] = None

class ConsultorCreate(ConsultorBase):
    pass

class ConsultorUpdate(BaseModel):
    nome: Optional[str] = None
    email: Optional[str] = None
    telefone: Optional[str] = None
    idiomas: Optional[List[str]] = None
    status_ativo: Optional[bool] = None
    status_ativo_sequencial: Optional[bool] = None
    status_online: Optional[bool] = None
    id_pipedrive: Optional[int] = None

class ConsultorResponse(ConsultorBase):
    id: int
    ultimo_atendimento: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConsultorDaVezResponse(BaseModel):
    consultor_id: int
    consultor_nome: str
    consultor_email: str
    consultor_telefone: Optional[str] = None
    consultor_idiomas: List[str]
    consultor_status_online: bool
    consultor_atendimento_iso: str
    consultor_id_pipedrive: Optional[int] = None
    protocolo: str  # Novo campo

class ProtocoloBase(BaseModel):
    consultor_id: int

class ProtocoloCreate(ProtocoloBase):
    pass

class ProtocoloResponse(ProtocoloBase):
    id: int
    numero: str
    created_at: datetime

    class Config:
        from_attributes = True

class ApiKeyBase(BaseModel):
    key: str
    description: str
    is_active: bool = True

class ApiKeyCreate(ApiKeyBase):
    pass

class ApiKeyResponse(ApiKeyBase):
    id: int
    created_at: datetime

    class Config:
        from_attributes = True
