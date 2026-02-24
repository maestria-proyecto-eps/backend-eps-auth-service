from pydantic import BaseModel, ConfigDict
from typing import Generic, TypeVar, Optional, List, Any
# Formato de datos en el Loggin
class LoginRequest(BaseModel):
    documento: int
    password: str

# Formato de los datos de usuario
class TokenData(BaseModel):
    id_usuario: int
    documento: int
    id_role: int

# Formato del token
class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"

T = TypeVar("T")

# DTO de Respuesta Genérico
class APIResponse(BaseModel, Generic[T]):
    hasError: bool = False
    Message: str = "Todo Ok"
    Data: Optional[T] = None

# DTO para Paginación
class PaginacionResponse(BaseModel, Generic[T]):
    hasElements: bool
    pages: int
    page: int
    data: List[T]

# DTO Genérico para listas paginadas
class APIPaginatedResponse(BaseModel, Generic[T]):
    hasError: bool = False
    Message: str = "Todo Ok"
    Data: PaginacionResponse[T]

class UserResponse(BaseModel):
    id_usuario: int
    nombre: str
    documento: int
    id_rol: int
    estado: int
    #Se quita pwd por seguridad

    model_config = ConfigDict(from_attributes=True)