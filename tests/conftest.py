import os
from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DB_URL", "sqlite:///./pytest_bootstrap.db")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from app.main import app
from app.models import Base, Paciente, Role, Usuario
from db.session import get_db

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed_roles(db):
    roles = [
        Role(id_rol=1, nombre_rol="medico"),
        Role(id_rol=2, nombre_rol="paciente"),
        Role(id_rol=3, nombre_rol="farmaceuta"),
        Role(id_rol=4, nombre_rol="enfermero"),
        Role(id_rol=5, nombre_rol="talento_humano"),
    ]
    db.add_all(roles)
    db.commit()


def create_patient_record(
    db,
    *,
    num_documento: int,
    email: str,
    estado: str = "Activo",
    nombres: str = "Paciente",
    apellidos: str = "Prueba",
    direccion: str = "Calle 1 # 2-3",
    contacto_emergencia: str = "Contacto Base",
    telefono_emergencia: int = 3000000000,
    grupo_sanguineo: str = "O+",
    factor_rh: str = "+",
    num_afiliacion: int = 2026022800001,
):
    usuario = Usuario(
        num_documento=num_documento,
        password="hashed-password",
        fk_id_rol=2,
        estado="activo",
        intentos_login=0,
    )
    db.add(usuario)
    db.flush()

    paciente = Paciente(
        nombres=nombres,
        apellidos=apellidos,
        estado=estado,
        consentimiento_datos=True,
        num_afiliacion=num_afiliacion,
        genero="Femenino",
        fecha_nacimiento=datetime(1990, 5, 15),
        direccion=direccion,
        contacto_emergencia=contacto_emergencia,
        telefono_emergencia=telefono_emergencia,
        grupo_sanguineo=grupo_sanguineo,
        factor_RH=factor_rh,
        email=email,
        fk_id_usuario=usuario.id_usuario,
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    _seed_roles(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    app.dependency_overrides[get_db] = override_get_db
    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()

