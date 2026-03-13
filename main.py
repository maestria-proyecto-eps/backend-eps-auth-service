from fastapi import FastAPI, HTTPException, status , Depends
from fastapi.middleware.cors import CORSMiddleware
from core.logger import setup_logging, get_logger

# Hash para pwd de pruebas
from core.security import Security

# Rutas de loggin
from routers import auth

# Importaciones de Base de Datos
from db.session import SessionLocal, engine, Base,get_db
from sqlalchemy import text
from models.user import USUARIOS,PERSONA, ROLES

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



# rutas de autenticación
app.include_router(auth.router)

# Prueba de conexión e info base de datos
@app.get("/debug-db-connection", tags=["Diagnóstico"])
def test_database_connection(db: SessionLocal = Depends(get_db)):
    """
    Endpoint de diagnóstico para validar la conexión con Supabase.
    Intenta ejecutar una consulta simple de sistema.
    """
    try:
        # 1. Intentamos ejecutar una consulta nativa muy simple
        # Esto valida si las credenciales y el host son correctos
        db.execute(text("SELECT 1"))

        # 2. Obtenemos información del servidor para confirmar
        version = db.execute(text("SELECT version();")).fetchone()

        return {
            "hasError": False,
            "Message": "¡Conexión exitosa con la base de datos!",
            "Data": {
                "db_version": version[0],
                "status": "Online",
                "engine_info": str(engine.url.render_as_string(hide_password=True))
            }
        }
    except Exception as e:
        error_msg = str(e)
        sugerencia = "Verificar credenciales en el archivo .env"

        # Diagnóstico de errores comunes basados en el mensaje
        if "password authentication failed" in error_msg:
            sugerencia = "La contraseña o el usuario son incorrectos. Revisa el .env."
        elif "could not connect to server" in error_msg:
            sugerencia = "No se puede alcanzar el servidor. Revisa el HOST y que tu IP no esté bloqueada."
        elif "psycopg2" in error_msg:
            sugerencia = "Error en el driver. Asegúrate de tener instalado 'psycopg2-binary'."

        return {
            "hasError": True,
            "Message": "Fallo en la conexión a la base de datos",
            "Data": {
                "error_detalle": error_msg,
                "sugerencia": sugerencia,
                "host_configurado": engine.url.host
            }
        }
@app.get("/debug-identificar-tablas", tags=["Busquedas"])
def get_real_table_names(db: SessionLocal = Depends(get_db)):
    """
    Consulta directamente el esquema de información de la DB
    para listar todas las tablas existentes.
    """
    try:
        # Consulta SQL nativa para PostgreSQL (Supabase)
        query = text("""
                     SELECT table_name
                     FROM information_schema.tables
                     WHERE table_schema = 'public'
                     """)

        result = db.execute(query)
        tablas = [row[0] for row in result]

        return {
            "hasError": False,
            "Message": f"Se encontraron {len(tablas)} tablas en el esquema público.",
            "Data": {
                "tablas_existentes": tablas,
                "sugerencia": "Verifica si los nombres están en mayúsculas o minúsculas para ajustar tus modelos."
            }
        }
    except Exception as e:
        return {
            "hasError": True,
            "Message": f"Error al consultar diccionario de datos: {str(e)}",
            "Data": None
        }
@app.get("/debug-usuarios-sistema", tags=["Busquedas"])
def get_all_system_users(db: Session = Depends(get_db)):
    """
    Retorna la información consolidada de todos los usuarios registrados:
    Nombres, apellidos, rol, id_rol, estado, documento e id_usuario.
    """
    try:
        # Realizamos la consulta uniendo las tres tablas necesarias
        usuarios_info = db.query(USUARIOS).join(PERSONA).join(ROLES).all()

        resultado = []
        for u in usuarios_info:
            resultado.append({
                "id_usuario": u.id_usuario,
                "num_documento": u.num_documento,
                "nombres": u.persona.nombres,
                "apellidos": u.persona.apellidos,
                "id_rol": u.id_rol,
                "rol": u.rol.nombre_rol,
                "estado": u.estado
            })

        return {
            "hasError": False,
            "Message": f"Se encontraron {len(resultado)} usuarios en el sistema.",
            "Data": resultado
        }
    except Exception as e:
        return {"hasError": True, "Message": f"Error en consulta: {str(e)}", "Data": None}