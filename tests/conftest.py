import os
from datetime import date

import pytest
from fastapi import FastAPI
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DB_URL", "sqlite:///./pytest_bootstrap.db")
os.environ.setdefault("DB_ADMIN_USER", "test")
os.environ.setdefault("DB_ADMIN_PASSWORD", "test")
os.environ.setdefault("DB_ADMIN_HOST", "localhost")
os.environ.setdefault("DB_ADMIN_PORT", "5432")
os.environ.setdefault("DB_ADMIN_NAME", "test")
os.environ.setdefault("JWT_EXPIRES_MINUTES", "60")
os.environ.setdefault("JWT_SECRET", "test-secret")
os.environ.setdefault("JWT_ALGORITHM", "HS256")

from models import Base, Paciente, Persona, Recepcionista, Role, Usuario
from routers import patients as patients_router
from db.session import get_db, get_db_audit
from core.dependencias import get_usuario_actual

TEST_DATABASE_URL = "sqlite://"

engine = create_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)


def _seed_roles(db):
    # Nombres deben coincidir EXACTAMENTE con los strings usados en RequireRole(["..."])
    # del router: "Recepcionista", "Talento Humano", "Paciente", "Administrador"
    roles = [
        Role(id_rol=1, nombre_rol="Médico"),
        Role(id_rol=2, nombre_rol="Paciente"),
        Role(id_rol=3, nombre_rol="Farmaceuta"),
        Role(id_rol=4, nombre_rol="Enfermero"),
        Role(id_rol=5, nombre_rol="Talento Humano"),
        Role(id_rol=6, nombre_rol="Recepcionista"),
        Role(id_rol=7, nombre_rol="Administrador"),
    ]
    db.add_all(roles)
    db.commit()


def _seed_receptionist(db):
    persona = Persona(
        num_documento=9000000001,
        nombres="Recepcion",
        apellidos="Prueba",
    )
    db.add(persona)
    db.flush()

    usuario = Usuario(
        num_documento=9000000001,
        password="hashed-password",
        fk_id_rol=6,
        estado=1,
        intentos_login=0,
    )
    db.add(usuario)
    db.flush()

    recepcionista = Recepcionista(
        id_recepcionista=52991334,
        nombres="Recepcion",
        apellidos="Prueba",
        estado=1,
        id_usuario=usuario.id_usuario,
    )
    db.add(recepcionista)
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
    telefono: int = 3000000000,
    contacto_emergencia: str = "Contacto Base",
    genero: str = "Femenino",
    tipo_sangre: str = "O+",
    num_afiliacion: int = 202602281,
):
    status_map = {"Activo": 1, "Inactivo": 0, "Suspendido": 2}

    persona = Persona(
        num_documento=num_documento,
        nombres=nombres,
        apellidos=apellidos,
    )
    db.add(persona)
    db.flush()

    usuario = Usuario(
        num_documento=num_documento,
        password="hashed-password",
        fk_id_rol=2,
        estado=status_map[estado],
        intentos_login=0,
    )
    db.add(usuario)
    db.flush()

    paciente = Paciente(
        id_paciente=num_documento,
        consentimiento_datos=True,
        fecha_nac=date(1990, 5, 15),
        num_afiliacion=num_afiliacion,
        genero=genero,
        direccion=direccion,
        contacto_emergencia=contacto_emergencia,
        telefono_emergencia=telefono,
        grupo_sanguineo=tipo_sangre,
        factor_RH=tipo_sangre[-1],
        email=email,
        id_recepcionista=52991334,
    )
    db.add(paciente)
    db.commit()
    db.refresh(paciente)
    return paciente


def make_mock_usuario(db_session, rol_nombre: str = "Recepcionista", id_rol: int = 6):
    """
    Retorna un objeto Usuario real desde la DB de tests con su rol cargado.
    Si no existe un usuario con ese rol, construye uno en memoria sin persistirlo.
    """
    user = db_session.query(Usuario).filter(Usuario.fk_id_rol == id_rol).first()
    if user is not None:
        # Cargar el rol manualmente si SQLite no lo carga por lazy loading
        if not hasattr(user, "rol") or user.rol is None:
            user.rol = db_session.query(Role).filter(Role.id_rol == id_rol).first()
        return user

    # Fallback: objeto en memoria (no persistido) para que RequireRole no explote
    rol = db_session.query(Role).filter(Role.id_rol == id_rol).first()
    fallback = Usuario(
        id_usuario=9999,
        num_documento=9999,
        password="x",
        fk_id_rol=id_rol,
        estado=1,
        intentos_login=0,
    )
    fallback.rol = rol
    return fallback


@pytest.fixture(scope="function")
def db_session():
    Base.metadata.drop_all(bind=engine)
    Base.metadata.create_all(bind=engine)
    session = TestingSessionLocal()
    _seed_roles(session)
    _seed_receptionist(session)
    try:
        yield session
    finally:
        session.close()


@pytest.fixture(scope="function")
def client(db_session):
    app = FastAPI()
    app.include_router(patients_router.router)

    def override_get_db():
        db = TestingSessionLocal()
        try:
            yield db
        finally:
            db.close()

    # get_db_audit también debe usar la misma DB de tests, si no usa la de producción
    app.dependency_overrides[get_db] = override_get_db
    app.dependency_overrides[get_db_audit] = override_get_db

    # Retorna un recepcionista con rol "Recepcionista" (mayúscula exacta del router)
    def override_get_usuario_actual():
        return make_mock_usuario(db_session, rol_nombre="Recepcionista", id_rol=6)

    app.dependency_overrides[get_usuario_actual] = override_get_usuario_actual

    try:
        yield TestClient(app)
    finally:
        app.dependency_overrides.clear()