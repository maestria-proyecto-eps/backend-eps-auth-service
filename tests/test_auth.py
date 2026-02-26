from fastapi.testclient import TestClient
from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_login_exitoso():
    payload = {
        "num_documento": 1234567890,
        "password": "EPS_2026_Clave"
    }
    response = client.post("/api/auth/login", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert json_response["Message"] == "Login exitoso"
    assert "access_token" in json_response["Data"]
    assert json_response["Data"]["token_type"] == "bearer"

def test_login_afiliacion_inactiva():
    payload = {
        "num_documento": 12345678901,
        "password": "paciente123"
    }
    response = client.post("/api/auth/login", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["hasError"] is True
    assert data["Message"] == "Afiliación inactiva."
    assert data["Data"] is None

def test_bloqueo_seguridad():

    # 4 intentos fallidos
    for i in range(1, 5):
        payload = {
            "num_documento": 12345678902,
            "password": "clave_incorrecta"
        }
        response = client.post("/api/auth/login", json=payload)
        data = response.json()
        assert data["hasError"] is True
        assert f"Credenciales incorrectas. Intento {i} de 5" in data["Message"]

    # El 5to intento fallido debe activar el bloqueo
    payload_quinto_intento = {
        "num_documento": 12345678902,
        "password": "clave_incorrecta"
    }
    response_5 = client.post("/api/auth/login", json=payload_quinto_intento)
    data_5 = response_5.json()

    assert data_5["hasError"] is True
    assert "Límite superado. Cuenta bloqueada por 15 min." in data_5["Message"]

    # Un 6to intento debe decir cuánto tiempo falta
    payload_sexto_intento = {
        "num_documento": 12345678902,
        "password": "paciente1234"
    }
    response_6 = client.post("/api/auth/login", json=payload_sexto_intento)
    data_6 = response_6.json()

    assert data_6["hasError"] is True
    assert "Bloqueo de seguridad. Intente en" in data_6["Message"]

def test_obtener_mi_perfil():
    # Login
    login_payload = {
        "num_documento": 1234567890,
        "password": "EPS_2026_Clave"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    token = login_response.json()["Data"]["access_token"]

    # Usar el token en los Headers para ir a /me
    headers = {"Authorization": f"Bearer {token}"}
    response = client.get("/api/auth/me", headers=headers)
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["hasError"] is False

    # Validamos cada campo de Userio
    user_data = json_response["Data"]
    assert user_data["id_usuario"] == 1
    assert user_data["num_documento"] == 1234567890
    assert user_data["id_rol"] == 1
    assert user_data["estado"] == 1
    assert user_data["nombres"] == "Juan Sebastián"
    assert user_data["apellidos"] == "Martínez López"

def test_acceso_denegado_sin_token():
    # Intentamos entrar a un endpoint protegido
    response = client.get("/api/auth/me")

    # FastAPI devuelve 401 Unauthorized automáticamente si falta el header
    assert response.status_code == 401

def test_logout_exitoso():
    # Login
    login_payload = {
        "num_documento": 1234567890,
        "password": "EPS_2026_Clave"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    token = login_response.json()["Data"]["access_token"]

    # Logout con el token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/auth/logout", headers=headers)
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert "Sesión de Juan Sebastián Martínez López finalizada correctamente." in json_response["Message"]