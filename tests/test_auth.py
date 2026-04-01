import os
import sys
from pathlib import Path

from fastapi.testclient import TestClient

os.environ.setdefault("JWT_SECRET", "clave_secreta")
os.environ.setdefault("JWT_ALGORITHM", "HS256")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "480")

from main import app

client = TestClient(app)

def test_health_check():
    response = client.get("/")
    assert response.status_code in [200, 404]

def test_login_exitoso_FARMACEUTA():
    payload = {
        "num_documento": 1018442904,
        "password": "Farm.Casillas2025!"
    }
    response = client.post("/api/auth/login", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert json_response["Message"] == "Login exitoso"
    assert "access_token" in json_response["Data"]
    assert json_response["Data"]["token_type"] == "bearer"

def test_login_exitoso_MEDICO():
    payload = {
        "num_documento": 80112457,
        "password": "Med.Ruiz2025!"
    }

    response = client.post("/api/auth/login", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert json_response["Message"] == "Login exitoso"
    assert "access_token" in json_response["Data"]
    assert json_response["Data"]["token_type"] == "bearer"

def test_login_exitoso_PACIENTE():
    payload = {
        "num_documento": 1018442903,
        "password": "Pac.Castro2025!"
    }
    response = client.post("/api/auth/login", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert json_response["Message"] == "Login exitoso"
    assert "access_token" in json_response["Data"]
    assert json_response["Data"]["token_type"] == "bearer"

def test_login_exitoso_ENFERMERO():
    payload = {
        "num_documento": 1012334885,
        "password": "Enf.Gaviria2025!"
    }
    response = client.post("/api/auth/login", json=payload)
    json_response = response.json()
    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert json_response["Message"] == "Login exitoso"
    assert "access_token" in json_response["Data"]
    assert json_response["Data"]["token_type"] == "bearer"

def test_login_exitoso_TH():
    payload = {
        "num_documento": 1015442890,
        "password": "TH.Ramirez2025!"
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
        "num_documento": 52884103,
        "password": "Pac.Rojas2025!"
    }
    response = client.post("/api/auth/login", json=payload)
    data = response.json()

    assert response.status_code == 200
    assert data["hasError"] is True
    assert data["Message"] == "Afiliación inactiva."
    assert data["Data"] is None

def test_bloqueo_seguridad_paciente():

    # LIMPIEZA INICIAL
    reset_payload = {"num_documento": 1018442903, "password": ""}
    client.post("/api/auth/reset-attempts", json=reset_payload)

    # SIMULAR 4 INTENTOS FALLIDOS
    for i in range(1, 5):
        payload_error = {
            "num_documento": 1018442903,
            "password": "clave_erronea_123"
        }
        response = client.post("/api/auth/login", json=payload_error)
        data = response.json()

        assert response.status_code == 200
        assert data["hasError"] is True
        assert f"Credenciales incorrectas. Intento {i} de 5" in data["Message"]

    # 5 INTENTO: Debe activar el mensaje de bloqueo por 15 min
    payload_quinto = {
        "num_documento": 1018442903,
        "password": "clave_mal"
    }
    response_5 = client.post("/api/auth/login", json=payload_quinto)
    data_5 = response_5.json()
    assert data_5["hasError"] is True
    assert "Límite superado. Cuenta bloqueada por 15 min." in data_5["Message"]

    # 6 INTENTO:Debe estar bloqueado
    payload_sexto = {
        "num_documento": 1018442903,
        "password": "Pac.Castro2025!"
    }
    response_6 = client.post("/api/auth/login", json=payload_sexto)
    data_6 = response_6.json()
    assert data_6["hasError"] is True
    assert "Bloqueo de seguridad. Intente en" in data_6["Message"]

    # LIMPIEZA FINAL
    final_reset = client.post("/api/auth/reset-attempts", json=reset_payload)
    assert final_reset.json()["hasError"] is False

def test_obtener_mi_perfil_MEDICO():
    # Login
    login_payload = {
        "num_documento": 80112457,
        "password": "Med.Ruiz2025!"
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
    assert user_data["num_documento"] == 80112457
    assert user_data["id_rol"] == 2
    assert user_data["estado"] == 1
    assert user_data["role"] == "Médico"
    assert user_data["nombres"] == "Alejandro"
    assert user_data["apellidos"] == "Ruiz Esparza"

def test_obtener_mi_perfil_PACIENTE():
    # Login
    login_payload = {
        "num_documento": 1018442903,
        "password": "Pac.Castro2025!"
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
    assert user_data["id_usuario"] == 44
    assert user_data["num_documento"] == 1018442903
    assert user_data["id_rol"] == 3
    assert user_data["estado"] == 1
    assert user_data["role"] == "Paciente"
    assert user_data["nombres"] == "Julián"
    assert user_data["apellidos"] == "Castro Meza"

def test_acceso_denegado_sin_token():
    # Intentamos entrar a un endpoint protegido
    response = client.get("/api/auth/me")

    # FastAPI devuelve 401 Unauthorized automáticamente si falta el header
    assert response.status_code == 401

def test_logout_exitoso():
    # Login
    login_payload = {
        "num_documento": 80112457,
        "password": "Med.Ruiz2025!"
    }
    login_response = client.post("/api/auth/login", json=login_payload)
    token = login_response.json()["Data"]["access_token"]

    # Logout con el token
    headers = {"Authorization": f"Bearer {token}"}
    response = client.post("/api/auth/logout", headers=headers)
    json_response = response.json()

    assert response.status_code == 200
    assert json_response["hasError"] is False
    assert "Sesión de Alejandro Ruiz Esparza finalizada correctamente." in json_response["Message"]
