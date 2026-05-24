import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from db.session import get_db
from models.user import USUARIOS, ROLES, PERSONA
from core.security import Security
from core.dependencias import get_usuario_actual

client = TestClient(app)

MOCK_USERS = {
    "admin":    {"doc": 101, "rol": "Administrador",  "pass": "admin123"},
    "medico":   {"doc": 102, "rol": "Médico",         "pass": "medico123"},
    "paciente": {"doc": 103, "rol": "Paciente",       "pass": "paciente123"},
    "enfermero":{"doc": 104, "rol": "Enfermero",      "pass": "nurse123"},
    "farma":    {"doc": 105, "rol": "Farmaceuta",     "pass": "pharma123"},
    "recep":    {"doc": 106, "rol": "Recepcionista",  "pass": "recep123"},
    "th":       {"doc": 107, "rol": "Talento Humano", "pass": "hr123"},
}


def make_mock_user(doc: int, rol_nombre: str) -> USUARIOS:
    """Construye un objeto USUARIOS en memoria con su rol ya cargado."""
    rol_obj = ROLES(id_rol=doc, nombre_rol=rol_nombre)
    u = USUARIOS(
        id_usuario=doc,
        num_documento=doc,
        password=Security.get_pwd_hash("x"),
        estado=True,
        intentos_login=0,
        tiempo_de_fallo_login=None,
    )
    u.rol = rol_obj
    u.nombre_rol = rol_nombre
    u.persona = PERSONA(num_documento=doc, nombres="User", apellidos=rol_nombre)
    return u


@pytest.fixture(autouse=True)
def setup_db_mock():
    """
    Mockea la sesión de DB para los endpoints que necesitan acceder a la BD.
    El override de get_usuario_actual se hace por test individual para poder
    controlar el rol sin depender del flujo de login + JWT.
    """
    mock_session = MagicMock()

    def mock_query_logic(model):
        query_mock = MagicMock()

        def mock_filter(criterion):
            doc_val = getattr(criterion.right, "value", None)
            user_data = next(
                (v for v in MOCK_USERS.values() if v["doc"] == doc_val), None
            )
            filter_mock = MagicMock()
            if user_data:
                filter_mock.first.return_value = make_mock_user(
                    user_data["doc"], user_data["rol"]
                )
            else:
                filter_mock.first.return_value = None
            return filter_mock

        query_mock.join.return_value.filter.side_effect = mock_filter
        query_mock.filter.side_effect = mock_filter
        return query_mock

    mock_session.query.side_effect = mock_query_logic
    app.dependency_overrides[get_db] = lambda: mock_session
    yield
    app.dependency_overrides = {}


# ---------------------------------------------------------------------------
# Tests
# ---------------------------------------------------------------------------

def test_acceso_medico_exitoso():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(102, "Médico")
    response = client.get("/api/test-roles/medico")
    assert response.status_code == 200
    assert response.json()["Data"]["rol"] == "Médico"


def test_acceso_paciente_exitoso():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(103, "Paciente")
    response = client.get("/api/test-roles/paciente")
    assert response.status_code == 200


def test_acceso_enfermero_exitoso():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(104, "Enfermero")
    response = client.get("/api/test-roles/enfermero")
    assert response.status_code == 200


def test_acceso_talento_humano_exitoso():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(107, "Talento Humano")
    response = client.get("/api/test-roles/th")
    assert response.status_code == 200


def test_admin_cualquier_endpoint():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(101, "Administrador")
    response = client.get("/api/test-roles/farmaceuta")
    assert response.status_code == 200


def test_acceso_prohibido():
    app.dependency_overrides[get_usuario_actual] = lambda: make_mock_user(103, "Paciente")
    response = client.get("/api/test-roles/medico")
    assert response.status_code == 403
    assert "Acceso denegado" in response.json()["detail"]["Message"]