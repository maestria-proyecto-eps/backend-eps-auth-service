from fastapi import FastAPI, HTTPException, status , Depends
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from core.logger import setup_logging, get_logger

# Rutas de loggin
from routers import auth

# Importaciones de Base de Datos
from db.session import SessionLocal, engine, Base
from models.user import User
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
#Base de datos de prueba

# CARGA INICIAL DE USUARIOS (SEED)
def seed_users():
    db = SessionLocal()
    try:
        # Verificamos si ya existen usuarios para no duplicarlos
        user_count = db.query(User).count()
        if user_count == 0:
            print("Base de Datos: No se encontraron usuarios. Cargando datos de prueba...")

            usuarios_prueba = [
                User(
                    username="oscar_admin",
                    password="EPS_2026_Clave",
                    id_rol=1,
                    estado=1
                ),
                User(
                    username="manuel",
                    password="paciente123",
                    id_rol=2,
                    estado=0
                )
            ]

            db.add_all(usuarios_prueba)
            db.commit()
            print("Base de Datos: Usuarios 'oscar_admin' y 'paco_paciente' creados exitosamente.")
        else:
            print(f"Base de Datos: Ya existen {user_count} usuarios. Seed omitido.")

    except Exception as e:
        print(f"Error en seed_users: {e}")
        db.rollback()
    finally:
        db.close()

# Ejecutamos la carga al arrancar el servidor
seed_users()

# rutas de autenticación
app.include_router(auth.router)