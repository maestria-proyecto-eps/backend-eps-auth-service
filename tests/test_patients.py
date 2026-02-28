from app.models import Paciente, Usuario
from tests.conftest import create_patient_record


def build_patient_payload(suffix: int = 1):
    return {
        "num_documento": 1010000000 + suffix,
        "password": "SecurePass123!",
        "nombres": f"Camila{suffix}",
        "apellidos": "Diaz",
        "email": f"camila{suffix}@example.com",
        "genero": "Femenino",
        "fecha_nacimiento": "1990-05-15T00:00:00",
        "direccion": "Calle 10 #20-30, Apto 301",
        "contacto_emergencia": "Carlos Diaz",
        "telefono_emergencia": 3001234500 + suffix,
        "grupo_sanguineo": "O+",
        "factor_RH": "+",
        "consentimiento_datos": True,
    }


def test_create_patient_creates_user_and_patient(client, db_session):
    response = client.post("/api/patients", json=build_patient_payload())

    assert response.status_code == 201
    body = response.json()

    assert body["nombres"] == "Camila1"
    assert body["apellidos"] == "Diaz"
    assert body["email"] == "camila1@example.com"
    assert body["estado"] == "Activo"
    assert body["consentimiento_datos"] is True
    assert isinstance(body["num_afiliacion"], int)

    patient = db_session.query(Paciente).filter(Paciente.email == "camila1@example.com").first()
    user = db_session.query(Usuario).filter(Usuario.num_documento == 1010000001).first()
    assert patient is not None
    assert user is not None
    assert patient.fk_id_usuario == user.id_usuario


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
        num_afiliacion=2026022800001,
    )
    create_patient_record(
        db_session,
        num_documento=2000000002,
        email="inactivo@example.com",
        estado="Inactivo",
        num_afiliacion=2026022800002,
    )

    response = client.get("/api/patients", params={"estado": "Activo"})

    assert response.status_code == 200
    body = response.json()

    assert body["total"] == 1
    assert len(body["patients"]) == 1
    assert body["patients"][0]["id_paciente"] == active_patient.id_paciente
    assert body["patients"][0]["estado"] == "Activo"


def test_update_affiliation_status_changes_patient_state(client, db_session):
    patient = create_patient_record(
        db_session,
        num_documento=2000000010,
        email="estado@example.com",
        estado="Activo",
        num_afiliacion=2026022800010,
    )

    response = client.put(
        f"/api/patients/{patient.id_paciente}/affiliation-status",
        json={"estado": "Suspendido", "motivo": "Pago no realizado"},
    )

    assert response.status_code == 200
    assert response.json()["estado"] == "Suspendido"


def test_get_my_profile_returns_patient_data(client, db_session):
    patient = create_patient_record(
        db_session,
        num_documento=2000000020,
        email="perfil@example.com",
        nombres="Laura",
        apellidos="Moreno",
        num_afiliacion=2026022800020,
    )

    response = client.get("/api/patients/me", params={"patient_id": patient.id_paciente})

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
        telefono_emergencia=3000000030,
        num_afiliacion=2026022800030,
    )

    response = client.put(
        "/api/patients/me/profile",
        params={"patient_id": patient.id_paciente},
        json={
            "direccion": "Carrera 50 # 10-20",
            "contacto_emergencia": "Ana Diaz",
            "telefono_emergencia": 3001112233,
        },
    )

    assert response.status_code == 200
    body = response.json()
    assert body["direccion"] == "Carrera 50 # 10-20"
    assert body["contacto_emergencia"] == "Ana Diaz"
    assert body["telefono_emergencia"] == 3001112233
