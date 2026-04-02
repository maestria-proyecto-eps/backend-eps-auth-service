"""
Schemas for Patient management
Pydantic models for request/response validation
"""

from datetime import date
from typing import Optional
from pydantic import BaseModel, EmailStr, Field, field_validator


class PacienteCreate(BaseModel):
    """Schema for creating a new patient with user"""
    
    # Usuario data
    num_documento: int = Field(..., gt=0, description="Document number")
    password: str = Field(..., min_length=8, description="User password")
    
    # Paciente data
    nombres: str = Field(..., min_length=2, max_length=50)
    apellidos: str = Field(..., min_length=2, max_length=50)
    email: EmailStr
    genero: str = Field(..., description="Género: Masculino, Femenino, Otro")
    fecha_nacimiento: date = Field(..., description="Fecha de nacimiento")
    direccion: str = Field(..., min_length=5, max_length=100)
    telefono: Optional[int] = Field(None, gt=0, description="Phone")
    contacto_emergencia: str = Field(..., min_length=2, max_length=50)
    tipo_sangre: str = Field(..., pattern="^(O|A|B|AB)[+-]$", description="Blood type: O+, O-, A+, etc")
    consentimiento_datos: bool = Field(
        ...,
        description="Data consent (Ley 1581/2012) - MUST be True"
    )
    
    @field_validator('tipo_sangre')
    @classmethod
    def validate_blood_type(cls, v):
        valid = {'O+', 'O-', 'A+', 'A-', 'B+', 'B-', 'AB+', 'AB-'}
        if v not in valid:
            raise ValueError(f'Blood type must be one of {valid}')
        return v
    
    @field_validator('consentimiento_datos')
    @classmethod
    def validate_consent(cls, v):
        if not v:
            raise ValueError('Data consent (Ley 1581/2012) is mandatory')
        return v
    
    class Config:
        json_schema_extra = {
            "example": {
                "num_documento": 1012345678,
                "password": "SecurePass123!",
                "nombres": "Camila",
                "apellidos": "Diaz",
                "email": "camila.diaz@example.com",
                "genero": "Femenino",
                "fecha_nacimiento": "1990-05-15",
                "direccion": "Calle 10 #20-30, Apto 301",
                "telefono": 3001234567,
                "contacto_emergencia": "Carlos Diaz",
                "tipo_sangre": "O+",
                "consentimiento_datos": True
            }
        }


class PacienteResponse(BaseModel):
    """Schema for patient response"""
    
    id_paciente: int
    nombres: Optional[str] = None
    apellidos: Optional[str] = None
    estado_afiliacion: str
    consentimiento_datos: bool
    fecha_nacimiento: Optional[date] = None
    num_afiliacion: str
    num_afiliacion_formateado: Optional[str] = None
    genero: Optional[str] = None
    direccion: Optional[str] = None
    telefono: Optional[int] = None
    contacto_emergencia: Optional[str] = None
    tipo_sangre: str
    email: Optional[str] = None
    id_recepcionista: int
    
    class Config:   
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_paciente": 1234567890,
                "nombres": "Laura",
                "apellidos": "Rojas",
                "estado_afiliacion": "Activo",
                "consentimiento_datos": True,
                "fecha_nacimiento": "1992-03-03",
                "num_afiliacion": "EPS-20260228-3",
                "num_afiliacion_formateado": "EPS-20260228-3",
                "genero": "Femenino",
                "direccion": "Calle 10 #20-30",
                "telefono": 3001234567,
                "contacto_emergencia": "Carlos Rojas",
                "tipo_sangre": "O+",
                "email": "laura.rojas@mail.com",
                "id_recepcionista": 52991334
            }
        }


class PacienteProfileUpdate(BaseModel):
    """Schema for updating patient profile"""
    
    direccion: Optional[str] = Field(None, min_length=5, max_length=100)
    telefono: Optional[int] = Field(None, gt=0)
    contacto_emergencia: Optional[str] = Field(None, min_length=2, max_length=50)
    
    class Config:
        json_schema_extra = {
            "example": {
                "direccion": "Carrera 8 #45-20, Apto 401",
                "contacto_emergencia": "Ana Diaz",
                "telefono": 1234567891
            }
        }


class AffiliationStatusUpdate(BaseModel):
    """Schema for updating affiliation status"""

    estado: str = Field(..., description="Estado afiliación: Activo, Inactivo")
    motivo: Optional[str] = Field(None, max_length=255)

    @field_validator('estado')
    @classmethod
    def validate_estado(cls, value: str) -> str:
        valid_states = {"Activo", "Inactivo"}
        normalized = value.strip().title()
        if normalized not in valid_states:
            raise ValueError("Estado must be one of: Activo, Inactivo")
        return normalized
    
    class Config:
        json_schema_extra = {
            "example": {
                "estado": "Inactivo",
                "motivo": "Pago no realizado"
            }
        }


class PacienteFilterParams(BaseModel):
    """Query parameters for patient filtering"""
    
    estado: Optional[str] = None
    genero: Optional[str] = None
    tipo_sangre: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
