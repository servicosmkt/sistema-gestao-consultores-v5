from pydantic import BaseModel, Field
from typing import List, Optional
from datetime import datetime

def validate_phone(v: Optional[str]) -> Optional[str]:
    if v is None:
        return v
    if not v.startswith('+'):
        raise ValueError('Telefone deve começar com + seguido do código do país (ex: +55)')
    numbers = v[1:]  # Remove o +
    if not numbers.isdigit():
        raise ValueError('Telefone deve conter apenas números após o +')
    if len(numbers) < 10 or len(numbers) > 15:
        raise ValueError('Telefone deve ter entre 10 e 15 números após o código do país')
    return v

def validate_idioma(v: str) -> str:
    if len(v) < 2 or len(v) > 5:
        raise ValueError('Idioma deve ter entre 2 e 5 caracteres')
    return v

class ConsultorBase(BaseModel):
    nome: str = Field(..., min_length=3, max_length=255)
    email: Optional[str] = None
    telefone: Optional[str] = Field(None, validate_default=True, validate_always=True, validator=validate_phone)
    idiomas: List[str] = Field(..., min_items=1, validator=validate_idioma)
    status_ativo: bool = True
    status_ativo_sequencial: bool = True
    status_online: bool = False
    id_pipedrive: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "email": "joao@exemplo.com",
                "telefone": "+5511999999999",
                "idiomas": ["pt", "en"],
                "status_ativo": True,
                "status_ativo_sequencial": True,
                "status_online": True,
                "id_pipedrive": 12345
            }
        }

class ConsultorCreate(ConsultorBase):
    pass

class ConsultorUpdate(BaseModel):
    nome: Optional[str] = Field(None, min_length=3, max_length=255)
    email: Optional[str] = None
    telefone: Optional[str] = Field(None, validate_default=True, validate_always=True, validator=validate_phone)
    idiomas: Optional[List[str]] = Field(None, min_items=1, validator=validate_idioma)
    status_ativo: Optional[bool] = None
    status_ativo_sequencial: Optional[bool] = None
    status_online: Optional[bool] = None
    id_pipedrive: Optional[int] = None

    class Config:
        json_schema_extra = {
            "example": {
                "nome": "João Silva",
                "email": "joao@exemplo.com",
                "telefone": "+5511999999999",
                "idiomas": ["pt", "en"],
                "status_ativo": True,
                "status_ativo_sequencial": True,
                "status_online": True,
                "id_pipedrive": 12345
            }
        }

class ConsultorResponse(ConsultorBase):
    id: int
    ultimo_atendimento: Optional[datetime] = None

    class Config:
        orm_mode = True

class ConsultorDaVezResponse(BaseModel):
    consultor_id: int
    consultor_nome: str
    consultor_email: Optional[str] = None
    consultor_telefone: Optional[str] = None
    consultor_idiomas: List[str]
    consultor_status_online: bool
    consultor_atendimento_iso: str
    consultor_id_pipedrive: Optional[int] = None
    numero_protocolo: str

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
        orm_mode = True

class ProtocoloBase(BaseModel):
    consultor_id: int
    descricao: Optional[str] = None
    prioridade: str = "normal"

class ProtocoloCreate(ProtocoloBase):
    pass

class ProtocoloUpdate(BaseModel):
    descricao: Optional[str] = None
    prioridade: Optional[str] = None
    status: Optional[str] = None

class ProtocoloResponse(BaseModel):
    id: int
    numero: str
    consultor_id: int
    created_at: datetime

    class Config:
        orm_mode = True

class ProtocoloComConsultorResponse(ProtocoloResponse):
    consultor: ConsultorResponse

    class Config:
        orm_mode = True

class NovoProtocoloResponse(BaseModel):
    numero_protocolo: str
