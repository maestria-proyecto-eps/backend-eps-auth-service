from fastapi import FastAPI, HTTPException, status , Depends
from fastapi.middleware.cors import CORSMiddleware
from core.logger import setup_logging, get_logger

# Hash para pwd de pruebas
from core.security import Security

# Rutas de loggin
from routers import auth

# Importaciones de Base de Datos
from db.session import SessionLocal, engine, Base
from models.user import USUARIOS
from models.profiles import MEDICOS,PACIENTES,FARMACEUTA,ENFERMEROS,TALENTO_HUMANO
Base.metadata.create_all(bind=engine)

Base.metadata.drop_all(bind=engine)
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="EPS API 2",
    description="EPS management API 2",
    version="0.1"
)

origins = ["*"]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

setup_logging()

# Logger call example
#logger = get_logger(__name__)




@app.get("/")
def root():
    """Root endpoint"""
    #logger.info("Root endpoint called")
    return {
        "message": "EPS API",
        "features": [
            "EPS management API"
        ],
        "docs": "/docs",
        "redoc": "/redoc"
    }

@app.get("/health")
def root():
    """health endpoint"""
    return {
        "message": "ok"
    }

#Base de datos de prueba

# CARGA INICIAL DE USUARIOS (SEED)
def seed_users():
    db = SessionLocal()
    try:
        if db.query(USUARIOS).count() == 0:
            # 1. Crear Usuario (Farmaceuta)
            u_farm = USUARIOS(
                id_usuario=1,
                num_documento=1234567890,
                password=Security.get_pwd_hash("EPS_2026_Clave"),
                id_rol=3,
                estado=1,
                intentos_login=0
            )
            db.add(u_farm)
            db.flush()
            db.add(FARMACEUTA(
                id_farmaceuta=1,
                nombres="Roberto Antonio",
                apellidos="Pérez Villamizar",
                id_usuario=1
            ))

            # 2. Crear Usuario (Médico)
            u_med = USUARIOS(
                id_usuario=2,
                num_documento=1234567891,
                password=Security.get_pwd_hash("EPS_2026_Med"),
                id_rol=1,
                estado=1,
                intentos_login=0
            )
            db.add(u_med)
            db.flush()
            db.add(MEDICOS(
                id_medico=1,
                nombres="Ana María",
                apellidos="Casas Buendía",
                id_usuario=2
            ))

            # 3. Crear Usuario (Paciente) - Activo
            u_pac_act = USUARIOS(
                id_usuario=3,
                num_documento=1234567892,
                password=Security.get_pwd_hash("EPS_2026_Pac1"),
                id_rol=2,
                estado=1,
                intentos_login=0
            )
            db.add(u_pac_act)
            db.flush()
            db.add(PACIENTES(
                id_paciente=1,
                nombres="Juan Sebastián",
                apellidos="Soto Aristizábal",
                id_usuario=3
            ))

            # 4. Crear Usuario (Paciente) - Inactivo
            u_pac_ina = USUARIOS(
                id_usuario=4,
                num_documento=1234567893,
                password=Security.get_pwd_hash("EPS_2026_Pac2"),
                id_rol=2,
                estado=0,
                intentos_login=0
            )
            db.add(u_pac_ina)
            db.flush()
            db.add(PACIENTES(
                id_paciente=2,
                nombres="Carlos Alberto",
                apellidos="Ruiz Gallego",
                id_usuario=4
            ))

            # 5. Crear Usuario (ENFERMERO)
            u_enf = USUARIOS(
                id_usuario=5,
                num_documento=1234567894,
                password=Security.get_pwd_hash("EPS_2026_Enf"),
                id_rol=4,
                estado=1,
                intentos_login=0
            )
            db.add(u_enf)
            db.flush()
            db.add(ENFERMEROS(
                id_enfermero=1,
                nombres="María Luisa",
                apellidos="Ruiz Parra",
                id_usuario=5
            ))

            # 6. Crear Usuario (TH)
            u_th = USUARIOS(
                id_usuario=6,
                num_documento=1234567895,
                password=Security.get_pwd_hash("EPS_2026_Th"),
                id_rol=4,
                estado=1,
                intentos_login=0
            )
            db.add(u_th)
            db.flush()
            db.add(TALENTO_HUMANO(
                id_TH=1,
                nombres="Luisa Amelia",
                apellidos="Parra Bonilla",
                id_usuario=6
            ))

            db.commit()
            print("Base de Datos: Semilla cargada con perfiles detallados.")
    except Exception as e:
        db.rollback()
        print(f"Error en seed: {e}")
    finally:
        db.close()

# Ejecutamos la carga al arrancar el servidor
seed_users()

# rutas de autenticación
app.include_router(auth.router)