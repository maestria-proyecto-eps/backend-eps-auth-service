from sqlalchemy import create_engine, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

from core.security import Security

# Cargar las variables del archivo .env
load_dotenv()

def _build_database_url() -> str:
    explicit_db_url = os.getenv("DB_URL")
    if explicit_db_url:
        return explicit_db_url

    user = os.getenv("DB_ADMIN_USER")
    password = os.getenv("DB_ADMIN_PASSWORD")
    host = os.getenv("DB_ADMIN_HOST")
    port = os.getenv("DB_ADMIN_PORT")
    dbname = os.getenv("DB_ADMIN_NAME")

    return f"postgresql+psycopg2://{user}:{password}@{host}:{port}/{dbname}?sslmode=require"


engine = None
SessionLocal = sessionmaker(autocommit=False, autoflush=False)


def _ensure_engine_initialized():
    global engine
    if engine is None:
        database_url = _build_database_url()
        if database_url.startswith("sqlite"):
            engine = create_engine(database_url, connect_args={"check_same_thread": False})
        else:
            engine = create_engine(database_url, poolclass=NullPool)
        SessionLocal.configure(bind=engine)
        if database_url.startswith("sqlite"):
            _bootstrap_sqlite_auth_data()


def _bootstrap_sqlite_auth_data():
    db = SessionLocal()
    try:
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS roles (
                id_rol INTEGER PRIMARY KEY,
                nombre_rol VARCHAR(50) NOT NULL UNIQUE
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS usuarios (
                id_usuario INTEGER PRIMARY KEY,
                num_documento BIGINT NOT NULL UNIQUE,
                password VARCHAR(255) NOT NULL,
                id_rol INTEGER NOT NULL,
                estado SMALLINT DEFAULT 1,
                intentos_login INTEGER DEFAULT 0,
                tiempo_de_fallo_login TIMESTAMP NULL
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS medicos (
                id_medico BIGINT PRIMARY KEY,
                nombres VARCHAR(50),
                apellidos VARCHAR(50),
                id_usuario INTEGER
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS pacientes (
                id_paciente BIGINT PRIMARY KEY,
                nombres VARCHAR(50),
                apellidos VARCHAR(50),
                id_usuario INTEGER
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS enfermeros (
                id_enfermero BIGINT PRIMARY KEY,
                nombres VARCHAR(50),
                apellidos VARCHAR(50),
                id_usuario INTEGER
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS farmaceutas (
                id_farmaceuta BIGINT PRIMARY KEY,
                nombres VARCHAR(50),
                apellidos VARCHAR(50),
                id_usuario INTEGER
            )
            """)
        )
        db.execute(
            text("""
            CREATE TABLE IF NOT EXISTS talento_humano (
                id_th BIGINT PRIMARY KEY,
                nombres VARCHAR(50),
                apellidos VARCHAR(50),
                id_usuario INTEGER
            )
            """)
        )
        db.execute(
            text("""
            INSERT OR REPLACE INTO roles (id_rol, nombre_rol) VALUES
            (2, 'Médico'),
            (3, 'Paciente'),
            (4, 'Enfermero'),
            (5, 'Farmaceuta'),
            (7, 'Talento Humano')
            """)
        )

        users = [
            (1, 80112457, 'Med.Ruiz2025!', 2, 1),
            (11, 1018442903, 'Pac.Castro2025!', 3, 1),
            (12, 1018442904, 'Farm.Casillas2025!', 5, 1),
            (13, 1012334885, 'Enf.Gaviria2025!', 4, 1),
            (14, 1015442890, 'TH.Ramirez2025!', 7, 1),
            (15, 52884103, 'Pac.Rojas2025!', 3, 0),
        ]

        for id_usuario, num_documento, plain_password, id_rol, estado in users:
            db.execute(
                text("""
                INSERT OR REPLACE INTO usuarios
                (id_usuario, num_documento, password, id_rol, estado, intentos_login, tiempo_de_fallo_login)
                VALUES (:id_usuario, :num_documento, :password, :id_rol, :estado, 0, NULL)
                """),
                {
                    "id_usuario": id_usuario,
                    "num_documento": num_documento,
                    "password": Security.get_pwd_hash(plain_password),
                    "id_rol": id_rol,
                    "estado": estado,
                },
            )

        db.execute(
            text("""
            INSERT OR REPLACE INTO medicos (id_medico, nombres, apellidos, id_usuario)
            VALUES (1, 'Alejandro', 'Ruiz Esparza', 1)
            """)
        )
        db.execute(
            text("""
            INSERT OR REPLACE INTO pacientes (id_paciente, nombres, apellidos, id_usuario)
            VALUES (1018442903, 'Julián', 'Castro Meza', 11)
            """)
        )

        db.commit()
    finally:
        db.close()

Base = declarative_base()

# Dependencia para los endpoints de FastAPI
def get_db():
    _ensure_engine_initialized()
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
