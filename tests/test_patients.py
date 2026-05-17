from models import Paciente, Usuario
from tests.conftest import create_patient_record


def build_patient_payload(suffix: int = 1):
    return {
        "num_documento": 1010000000 + suffix,
        "password": "SecurePass123!",
        "nombres": f"Camila{suffix}",
        "apellidos": "Diaz",
        "email": f"camila{suffix}@example.com",
        "genero": "Femenino",
        "fecha_nacimiento": "1990-05-15",
        "direccion": "Calle 10 #20-30, Apto 301",
        "telefono": 3002004000 + suffix,
        "contacto_emergencia": "Carlos Diaz",
        "tipo_sangre": "O+",
        "consentimiento_datos": True,
    }


def test_create_patient_creates_user_and_patient(client, db_session):
    response = client.post("/api/patients", json=build_patient_payload())

    assert response.status_code == 201
    body = response.json()

    assert body["nombres"] == "Camila1"
    assert body["apellidos"] == "Diaz"
    assert body["email"] == "camila1@example.com"
    assert body["estado_afiliacion"] == "Activo"
    assert body["consentimiento_datos"] is True
    assert body["num_afiliacion"].startswith("EPS-")

    patient = db_session.query(Paciente).filter(Paciente.id_paciente == 1010000001).first()
    user = db_session.query(Usuario).filter(Usuario.num_documento == 1010000001).first()
    assert patient is not None
    assert user is not None
    assert patient.id_paciente == user.num_documento


def test_create_patient_requires_data_consent(client):
    payload = build_patient_payload()
    payload["consentimiento_datos"] = False

    response = client.post("/api/patients", json=payload)

    assert response.status_code == 422
    assert "Data consent" in response.text


def test_list_patients_filters_by_estado(client, db_session):
    active_patient = create_patient_record(
        db_session,
        num_documento=2000000001,
        email="activo@example.com",
        estado="Activo",
        num_afiliacion=202602281,
    )
    create_patient_record(
        db_session,
        num_documento=2000000002,
        email="inactivo@example.com",
        estado="Inactivo",
        num_afiliacion=202602282,
    )

    response = client.get("/api/patients", params={"estado": "Activo"})

    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 1
    assert len(body["patients"]) == 1
    assert body["patients"][0]["id_paciente"] == active_patient.id_paciente
    assert body["patients"][0]["estado_afiliacion"] == "Activo"


def test_update_affiliation_status_changes_patient_state(client, db_session):
    patient = create_patient_record(
        db_session,
        num_documento=2000000010,
        email="estado@example.com",
        estado="Activo",
        num_afiliacion=2026022810,
    )

    response = client.put(
        f"/api/patients/{patient.id_paciente}/affiliation-status",
        json={"estado": "Inactivo", "motivo": "Pago no realizado"},
    )

    assert response.status_code == 200
    assert response.json()["estado_afiliacion"] == "Inactivo"


def test_get_my_profile_returns_patient_data(client, db_session):
    patient = create_patient_record(
        db_session,
        num_documento=2000000020,
        email="perfil@example.com",
        nombres="Laura",
        apellidos="Moreno",
        num_afiliacion=2026022820,
    )

    response = client.get("/api/patients/me")

    assert response.status_code == 200
    body = response.json()
    assert body["id_paciente"] == patient.id_paciente
    assert body["nombres"] == "Laura"
    assert body["apellidos"] == "Moreno"


def test_update_my_profile_updates_allowed_fields(client, db_session):
    patient = create_patient_record(
        db_session,
        num_documento=2000000030,
        email="actualizar@example.com",
        direccion="Calle Original 123",
        contacto_emergencia="Maria Lopez",
        telefono=3000000030,
        num_afiliacion=2026022830,
    )

    response = client.put(
        "/api/patients/me/profile",
        json={
            "direccion": "Carrera 50 # 10-20",
            "contacto_emergencia": "Ana Diaz",
            "telefono": 3001112233,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["direccion"] == "Carrera 50 # 10-20"
    assert body["contacto_emergencia"] == "Ana Diaz"
    assert body["telefono"] == 3001112233