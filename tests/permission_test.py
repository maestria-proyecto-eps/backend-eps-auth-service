import pytest
from fastapi.testclient import TestClient
from unittest.mock import MagicMock
from main import app
from db.session import get_db
from models.user import USUARIOS, ROLES, PERSONA
from core.security import Security

client = TestClient(app)

MOCK_USERS = {
    "admin": {"doc": 101, "rol": "Administrador", "pass": "admin123"},
    "medico": {"doc": 102, "rol": "Médico", "pass": "medico123"},
    "paciente": {"doc": 103, "rol": "Paciente", "pass": "paciente123"},
    "enfermero": {"doc": 104, "rol": "Enfermero", "pass": "nurse123"},
    "farma": {"doc": 105, "rol": "Farmaceuta", "pass": "pharma123"},
    "recep": {"doc": 106, "rol": "Recepcionista", "pass": "recep123"},
    "th": {"doc": 107, "rol": "Talento Humano", "pass": "hr123"},
}

@pytest.fixture(autouse=True)
def setup_db_mock():
    mock_session = MagicMock()

    def mock_query_logic(model):
        query_mock = MagicMock()

        def mock_filter(criterion):
            # Extraemos el valor del documento del query
            doc_val = getattr(criterion.right, 'value', None)
            user_data = next((v for v in MOCK_USERS.values() if v["doc"] == doc_val), None)

            filter_mock = MagicMock()
            if user_data:
                # Creamos el objeto ROL
                rol_obj = ROLES(id_rol=user_data["doc"], nombre_rol=user_data["rol"])

                # Creamos el objeto USUARIOS
                u = USUARIOS(
                    id_usuario=user_data["doc"],
                    num_documento=user_data["doc"],
                    password=Security.get_pwd_hash(user_data["pass"]),
                    estado=True,
                    id_rol=user_data["doc"],
                    intentos_login=0,
                    tiempo_de_fallo_login=None
                )

                # RELACIONES CRUCIALES:
                # 1. Relación de objeto (para user.rol.nombre_rol)
                u.rol = rol_obj
                # 2. Atributo directo (para evitar AttributeError si el código pide user.nombre_rol)
                u.nombre_rol = user_data["rol"]

                # Mock de la Persona relacionada
                u.persona = PERSONA(num_documento=user_data["doc"], nombres="User", apellidos=user_data["rol"])

                filter_mock.first.return_value = u
            else:
                filter_mock.first.return_value = None
            return filter_mock

        # Soportamos query().join().filter() y query().filter()
        query_mock.join.return_value.filter.side_effect = mock_filter
        query_mock.filter.side_effect = mock_filter
        return query_mock

    mock_session.query.side_effect = mock_query_logic
    app.dependency_overrides[get_db] = lambda: mock_session
    yield
    app.dependency_overrides = {}

def get_auth_headers(doc, password):
    response = client.post("/api/auth/login", json={"num_documento": doc, "password": password})
    token = response.json()["Data"]["access_token"]
    return {"Authorization": f"Bearer {token}"}

def test_acceso_medico_exitoso():
    headers = get_auth_headers(MOCK_USERS["medico"]["doc"], MOCK_USERS["medico"]["pass"])
    response = client.get("/api/test-roles/medico", headers=headers)
    assert response.status_code == 200
    assert response.json()["Data"]["rol"] == "Médico"

def test_acceso_paciente_exitoso():
    headers = get_auth_headers(MOCK_USERS["paciente"]["doc"], MOCK_USERS["paciente"]["pass"])
    response = client.get("/api/test-roles/paciente", headers=headers)
    assert response.status_code == 200

def test_acceso_enfermero_exitoso():
    headers = get_auth_headers(MOCK_USERS["enfermero"]["doc"], MOCK_USERS["enfermero"]["pass"])
    response = client.get("/api/test-roles/enfermero", headers=headers)
    assert response.status_code == 200

def test_acceso_talento_humano_exitoso():
    headers = get_auth_headers(MOCK_USERS["th"]["doc"], MOCK_USERS["th"]["pass"])
    response = client.get("/api/test-roles/th", headers=headers)
    assert response.status_code == 200

def test_admin_cualquier_endpoint():

    headers = get_auth_headers(MOCK_USERS["admin"]["doc"], MOCK_USERS["admin"]["pass"])
    response = client.get("/api/test-roles/farmaceuta", headers=headers)

    assert response.status_code == 200

def test_acceso_prohibido():

    headers = get_auth_headers(MOCK_USERS["paciente"]["doc"], MOCK_USERS["paciente"]["pass"])
    response = client.get("/api/test-roles/medico", headers=headers)

    assert response.status_code == 403
    assert "Acceso denegado" in response.json()["detail"]["Message"]