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
from db.session import get_db, get_db_audit
from core.dependencias import RequireRole

router = APIRouter(
    prefix="/api/patients",
    tags=["Patients"],
)


def _to_patient_response(paciente) -> PacienteResponse:
    persona = getattr(paciente, "persona", None)
    usuario = getattr(paciente, "usuario", None)
    return PacienteResponse(
        id_paciente=paciente.id_paciente,
        estado_afiliacion=PatientService.status_to_string(getattr(usuario, "estado", None)),
        consentimiento_datos=paciente.consentimiento_datos,
        num_afiliacion=paciente.num_afiliacion_formateado,
        num_afiliacion_formateado=paciente.num_afiliacion_formateado,
        fecha_nacimiento=paciente.fecha_nac,
        tipo_sangre=paciente.grupo_sanguineo,
        id_recepcionista=paciente.id_recepcionista,
        nombres=getattr(persona, "nombres", None),
        apellidos=getattr(persona, "apellidos", None),
        genero=paciente.genero,
        direccion=paciente.direccion,
        telefono=paciente.telefono_emergencia,
        contacto_emergencia=paciente.contacto_emergencia,
        email=paciente.email,
    )


@router.post(
    "",
    response_model=PacienteResponse,
    status_code=status.HTTP_201_CREATED,
    summary="Afiliar nuevo paciente",
    description=(
        "Crea un nuevo paciente.\n"
        "Campos clave del request: num_documento, password, nombres, apellidos, fecha_nacimiento, consentimiento_datos.\n"
        "Campos administrados por backend: id_paciente, id_recepcionista, num_afiliacion, estado_afiliacion."
    ),
    dependencies=[Depends(RequireRole(["Recepcionista"]))]
)
def create_patient(
    patient_data: PacienteCreate,
    db: Session = Depends(get_db_audit),
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
            "fecha_nacimiento": "1992-03-03",
      "direccion": "Calle 10 #20-30",
            "telefono": 3001234567,
      "contacto_emergencia": "Carlos Rojas",
            "tipo_sangre": "O+",
      "consentimiento_datos": true
    }
    """
    paciente = PatientService.create_patient(db, patient_data)
    return _to_patient_response(paciente)


@router.get(
    "",
    response_model=dict,
    summary="Listar pacientes",
    description="Lista pacientes.",
    dependencies=[Depends(RequireRole(["Recepcionista", "Talento Humano"]))]
)
def list_patients(
    skip: int = Query(0, ge=0),
    limit: int = Query(10, ge=1, le=100),
    estado: Optional[str] = Query(None, description="Filter by status: Activo, Inactivo"),
    genero: Optional[str] = Query(None, description="Filter by gender"),
    tipo_sangre: Optional[str] = Query(None, description="Filter by blood type"),
    db: Session = Depends(get_db),
):
    """
    Filtros disponibles:
    - **estado**: Activo, Inactivo
    - **genero**
    - **tipo_sangre**

    Ejemplo de uso:
    GET /api/patients?skip=0&limit=10&estado=Activo
    """
    patients, total = PatientService.get_patients(
        db,
        skip=skip,
        limit=limit,
        estado=estado,
        genero=genero,
        tipo_sangre=tipo_sangre,
    )

    return {
        "total": total,
        "skip": skip,
        "limit": limit,
        "patients": [_to_patient_response(p) for p in patients]
    }


@router.get(
    "/{patient_id:int}",
    response_model=PacienteResponse,
    summary="Obtener detalles del paciente",
    description="Retorna un paciente por id_paciente.",
    dependencies=[Depends(RequireRole(["Recepcionista", "Talento Humano"]))]
)
def get_patient(
    patient_id: int,
    db: Session = Depends(get_db)
):
    """Get patient details by ID"""
    paciente = PatientService.get_patient_by_id(db, patient_id)
    return _to_patient_response(paciente)
@router.put(
    "/{patient_id:int}/affiliation-status",
    response_model=PacienteResponse,
    summary="Cambiar estado de afiliación",
    description="Actualiza estado usando valores: Activo, Inactivo.",
    dependencies=[Depends(RequireRole(["Recepcionista", "Talento Humano"]))]
)
def update_affiliation_status(
    patient_id: int,
    status_update: AffiliationStatusUpdate,
    db: Session = Depends(get_db_audit),
):
    """
    Update patient affiliation status

        Ejemplo:
        {
            "estado": "Inactivo",
            "motivo": "Pago no realizado"
        }
    """
    paciente = PatientService.update_affiliation_status(
        db,
        patient_id,
        status_update,
    )
    return _to_patient_response(paciente)


@router.get(
    "/me",
    response_model=PacienteResponse,
    summary="Ver mi perfil",
    description="Consulta perfil por id_paciente."
)
def get_my_profile(
    usuario_actual=Depends(RequireRole(["Paciente"])),
    db: Session = Depends(get_db),
):
    """
    Ejemplo:
    GET /api/patients/me con token Bearer válido
    """
    user_id = getattr(usuario_actual, "id_usuario", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authenticated user")

    paciente = PatientService.get_patient_by_user_id(db, user_id)
    if not paciente:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _to_patient_response(paciente)


@router.put(
    "/me/profile",
    response_model=PacienteResponse,
    summary="Actualizar mi perfil",
    description="Actualiza campos editables del perfil del paciente."
)
def update_my_profile(
    usuario_actual=Depends(RequireRole(["Paciente"])),
    profile_update: PacienteProfileUpdate = Body(...),
    db: Session = Depends(get_db_audit),
):
    """
        Ejemplo:
        PUT /api/patients/me/profile con token Bearer válido
        {
            "direccion": "Carrera 7 #45-10",
            "contacto_emergencia": "María López",
            "telefono": 3009998887
        }
    """
    update_dict = profile_update.model_dump(exclude_unset=True)
    if not update_dict:
        raise HTTPException(status_code=400, detail="No data provided to update")

    user_id = getattr(usuario_actual, "id_usuario", None)
    if user_id is None:
        raise HTTPException(status_code=401, detail="Invalid authenticated user")

    paciente = PatientService.get_patient_by_user_id(db, user_id)

    paciente = PatientService.update_patient_profile(db, paciente.id_paciente, update_dict)
    if not paciente:
        raise HTTPException(status_code=404, detail="Patient not found")
    return _to_patient_response(paciente)


@router.put(
    "/{patient_id:int}",
    response_model=PacienteResponse,
    summary="Actualizar perfil del paciente",
    description="Actualiza perfil por id_paciente usando la estructura vigente de PACIENTES.",
    dependencies=[Depends(RequireRole(["Recepcionista", "Talento Humano"]))]
)
def update_patient_profile(
    patient_id: int,
    profile_update: PacienteProfileUpdate,
    db: Session = Depends(get_db_audit),
):
    """
    Campos editables:
    - direccion
    - telefono
    - contacto_emergencia
    """
    update_dict = profile_update.model_dump(exclude_unset=True)
    paciente = PatientService.update_patient_profile(
        db,
        patient_id,
        update_dict,
    )
    return _to_patient_response(paciente)
