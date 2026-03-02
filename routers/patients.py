"""
Patient Router - API endpoints for patient management
Handles affiliation, profile updates, and patient listing
"""

from typing import Optional
from fastapi import APIRouter, Body, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from schemas.patients import (
    AffiliationStatusUpdate,
    PacienteCreate,
    PacienteProfileUpdate,
    PacienteResponse,
)
from service.patient_service import PatientService
from db.session import get_db

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)


@router.post(
    "",
    response_model=PacienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Afiliar nuevo paciente",
    description=(
        "Crea un nuevo paciente.\n"
        "Campos clave del request: num_documento, password, nombres, apellidos, fecha_nac, consentimiento_datos.\n"
        "Campos administrados por backend: id_paciente, id_usuario, id_recepcionista, num_afiliacion."
    )
)
def create_patient(
    patient_data: PacienteCreate,
    db: Session = Depends(get_db),
):
    """
    Ejemplo de inserción (request body):
    {
      "num_documento": 1234567890,
      "password": "Paciente123!",
      "nombres": "Laura",
      "apellidos": "Rojas",
      "email": "laura.rojas@mail.com",
      "genero": "Femenino",
      "fecha_nac": "1992-03-03",
      "direccion": "Calle 10 #20-30",
      "contacto_emergencia": "Carlos Rojas",
      "telefono_emergencia": 3001234567,
      "grupo_sanguineo": "O+",
      "factor_RH": "+",
      "consentimiento_datos": true
    }
    """
    paciente = PatientService.create_patient(db, patient_data)
    return paciente


@router.get(
    "",
    response_model=dict,
    summary="Listar pacientes",
    description="Lista pacientes."
)
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[int] = Query(None, ge=1, le=3, description="Filter by status: 1=Activo, 2=Inactivo, 3=Suspendido"),
    genero: Optional[str] = Query(None, description="Filter by gender"),
    grupo_sanguineo: Optional[str] = Query(None, description="Filter by blood type"),
    db: Session = Depends(get_db),
):
    """
    Filtros disponibles:
    - **estado**: 1=Activo, 2=Inactivo, 3=Suspendido
    - **genero**
    - **grupo_sanguineo**

    Ejemplo de uso:
    GET /api/patients?skip=0&limit=10&estado=1
    """
    patients, total = PatientService.get_patients(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        genero=genero,
        grupo_sanguineo=grupo_sanguineo,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "patients": [PacienteResponse.model_validate(p) for p in patients]
    }


@router.get(
    "/{patient_id:int}",
    response_model=PacienteResponse,
    summary="Obtener detalles del paciente",
    description="Retorna un paciente por id_paciente."
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get patient details by ID"""
    paciente = PatientService.get_patient_by_id(db, patient_id)
    return paciente
@router.put(
    "/{patient_id:int}/affiliation-status",
    response_model=PacienteResponse,
    summary="Cambiar estado de afiliación",
    description="Actualiza estado usando valores numéricos: 1=Activo, 2=Inactivo, 3=Suspendido."
)
def update_affiliation_status(
    patient_id: int,
    status_update: AffiliationStatusUpdate,
    db: Session = Depends(get_db),
):
    """
    Update patient affiliation status

        Ejemplo:
        {
            "estado": 2,
            "motivo": "Pago no realizado"
        }
    """
    paciente = PatientService.update_affiliation_status(
        db,
        patient_id,
        status_update,
    )
    return paciente


@router.get(
    "/me",
    response_model=PacienteResponse,
    summary="Ver mi perfil",
    description="Consulta perfil por id_paciente."
)
def get_my_profile(
    patient_id: int = Query(..., description="Patient ID"),
    db: Session = Depends(get_db),
):
    """
    Ejemplo:
    GET /api/patients/me?patient_id=1018442903
    """
    paciente = PatientService.get_patient_by_id(db, patient_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Patient not found")
    return paciente


@router.put(
    "/me/profile",
    response_model=PacienteResponse,
    summary="Actualizar mi perfil",
    description="Actualiza campos editables del perfil del paciente."
)
def update_my_profile(
    patient_id: int = Query(..., description="Patient ID"),
    profile_update: PacienteProfileUpdate = Body(...),
    db: Session = Depends(get_db),
):
    """
        Ejemplo:
        PUT /api/patients/me/profile?patient_id=1018442903
        {
            "direccion": "Carrera 7 #45-10",
            "contacto_emergencia": "María López",
            "telefono_emergencia": 3009998887
        }
    """
    update_dict = profile_update.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided to update")

    paciente = PatientService.update_patient_profile(
        db,
        patient_id,
        update_dict,
    )
    if not paciente:
        raise HTTPException(status_code=404, detail="Patient not found")
    return paciente


@router.put(
    "/{patient_id:int}",
    response_model=PacienteResponse,
    summary="Actualizar perfil del paciente",
    description="Actualiza perfil por id_paciente usando la estructura vigente de PACIENTES."
)
def update_patient_profile(
    patient_id: int,
    profile_update: PacienteProfileUpdate,
    db: Session = Depends(get_db),
):
    """
    Campos editables:
    - direccion
    - contacto_emergencia
    - telefono_emergencia
    """
    update_dict = profile_update.model_dump(exclude_unset=True)
    paciente = PatientService.update_patient_profile(
        db,
        patient_id,
        update_dict,
    )
    return paciente
