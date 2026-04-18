from fastapi import APIRouter, Depends
from core.dependencias import RequireRole
from models.user import USUARIOS
from schemas.auth import APIResponse

router = APIRouter(prefix="/api/test-roles", tags=["Pruebas de Seguridad por Rol"])

@router.get("/administrador", response_model=APIResponse[dict])
def test_admin(user: USUARIOS = Depends(RequireRole(["Administrador"]))):
    return {"hasError": False, "Message": "Acceso concedido al Administrador", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/medico", response_model=APIResponse[dict])
def test_medico(user: USUARIOS = Depends(RequireRole(["Médico"]))):
    return {"hasError": False, "Message": "Acceso concedido al Médico", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/paciente", response_model=APIResponse[dict])
def test_paciente(user: USUARIOS = Depends(RequireRole(["Paciente"]))):
    return {"hasError": False, "Message": "Acceso concedido al Paciente", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/enfermero", response_model=APIResponse[dict])
def test_enfermero(user: USUARIOS = Depends(RequireRole(["Enfermero"]))):
    return {"hasError": False, "Message": "Acceso concedido al Enfermero", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/farmaceuta", response_model=APIResponse[dict])
def test_farmaceuta(user: USUARIOS = Depends(RequireRole(["Farmaceuta"]))):
    return {"hasError": False, "Message": "Acceso concedido al Farmaceuta", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/recepcionista", response_model=APIResponse[dict])
def test_recepcionista(user: USUARIOS = Depends(RequireRole(["Recepcionista"]))):
    return {"hasError": False, "Message": "Acceso concedido al Recepcionista", "Data": {"rol": user.rol.nombre_rol}}

@router.get("/th", response_model=APIResponse[dict])
def test_th(user: USUARIOS = Depends(RequireRole(["Talento Humano"]))):
    return {"hasError": False, "Message": "Acceso concedido a Talento Humano", "Data": {"rol": user.rol.nombre_rol}}