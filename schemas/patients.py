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
    fecha_nac: date = Field(..., description="Fecha de nacimiento")
    direccion: str = Field(..., min_length=5, max_length=100)
    contacto_emergencia: str = Field(..., min_length=2, max_length=50)
    telefono_emergencia: int = Field(..., gt=0, description="Emergency phone")
    grupo_sanguineo: str = Field(..., pattern="^(O|A|B|AB)[+-]$", description="Blood type: O+, O-, A+, etc")
    factor_RH: str = Field(..., pattern="^[+-]$", description="RH factor: + or -")
    consentimiento_datos: bool = Field(
        ...,
        description="Data consent (Ley 1581/2012) - MUST be True"
    )
    
    @field_validator('grupo_sanguineo')
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
                "fecha_nac": "1990-05-15",
                "direccion": "Calle 10 #20-30, Apto 301",
                "contacto_emergencia": "Carlos Diaz",
                "telefono_emergencia": 1234567890,
                "grupo_sanguineo": "O+",
                "factor_RH": "+",
                "consentimiento_datos": True
            }
        }


class PacienteResponse(BaseModel):
    """Schema for patient response"""
    
    id_paciente: int
    nombres: str
    apellidos: str
    estado: int
    consentimiento_datos: bool
    id_usuario: int
    fecha_nac: date
    num_afiliacion: int
    num_afiliacion_formateado: Optional[str] = None
    genero: str
    direccion: Optional[str] = None
    contacto_emergencia: Optional[str] = None
    telefono_emergencia: Optional[int] = None
    grupo_sanguineo: Optional[str] = None
    factor_RH: Optional[str] = None
    email: Optional[str] = None
    id_recepcionista: int
    
    class Config:   
        from_attributes = True
        json_schema_extra = {
            "example": {
                "id_paciente": 1234567890,
                "nombres": "Laura",
                "apellidos": "Rojas",
                "estado": 1,
                "consentimiento_datos": True,
                "id_usuario": 58,
                "fecha_nac": "1992-03-03",
                "num_afiliacion": 202602283,
                "num_afiliacion_formateado": "EPS-20260228-3",
                "genero": "Femenino",
                "direccion": "Calle 10 #20-30",
                "contacto_emergencia": "Carlos Rojas",
                "telefono_emergencia": 3001234567,
                "grupo_sanguineo": "O+",
                "factor_RH": "+",
                "email": "laura.rojas@mail.com",
                "id_recepcionista": 52991334
            }
        }


class PacienteProfileUpdate(BaseModel):
    """Schema for updating patient profile"""
    
    direccion: Optional[str] = Field(None, min_length=5, max_length=100)
    contacto_emergencia: Optional[str] = Field(None, min_length=2, max_length=50)
    telefono_emergencia: Optional[int] = Field(None, gt=0)
    
    class Config:
        json_schema_extra = {
            "example": {
                "direccion": "Carrera 8 #45-20, Apto 401",
                "contacto_emergencia": "Ana Diaz",
                "telefono_emergencia": 1234567891
            }
        }


class AffiliationStatusUpdate(BaseModel):
    """Schema for updating affiliation status"""

    estado: int = Field(..., ge=1, le=3, description="Estado afiliación: 1=Activo, 2=Inactivo, 3=Suspendido")
    motivo: Optional[str] = Field(None, max_length=255)
    
    class Config:
        json_schema_extra = {
            "example": {
                "estado": 3,
                "motivo": "Pago no realizado"
            }
        }


class PacienteFilterParams(BaseModel):
    """Query parameters for patient filtering"""
    
    estado: Optional[int] = None
    genero: Optional[str] = None
    grupo_sanguineo: Optional[str] = None
    skip: int = Field(0, ge=0)
    limit: int = Field(10, ge=1, le=100)
