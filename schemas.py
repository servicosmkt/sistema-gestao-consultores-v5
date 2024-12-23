from pydantic import BaseModel
from typing import List, Optional
from datetime import datetime

class ConsultorBase(BaseModel):
    nome: str
    idiomas: List[str]
    status_ativo: bool = True
    status_ativo_sequencial: bool = True
    status_online: bool = False
    id_pipedrive: Optional[int] = None  # Novo campo

class ConsultorCreate(ConsultorBase):
    pass

class ConsultorUpdate(BaseModel):
    nome: Optional[str] = None
    idiomas: Optional[List[str]] = None
    status_ativo: Optional[bool] = None
    status_ativo_sequencial: Optional[bool] = None
    status_online: Optional[bool] = None
    id_pipedrive: Optional[int] = None  # Novo campo

class ConsultorResponse(ConsultorBase):
    id: int
    ultimo_atendimento: Optional[datetime] = None

    class Config:
        from_attributes = True

class ConsultorDaVezResponse(BaseModel):
    consultor_id: int
    consultor_nome: str
    consultor_idiomas: List[str]
    consultor_status_online: bool
    consultor_atendimento_iso: str
    consultor_id_pipedrive: Optional[int] = None  # Novo campo

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
