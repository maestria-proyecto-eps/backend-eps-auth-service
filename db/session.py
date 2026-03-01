from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
from dotenv import load_dotenv
import os

# Cargar las variables del archivo .env
load_dotenv()

USER = os.getenv("DB_ADMIN_USER")
PASSWORD = os.getenv("DB_ADMIN_PASSWORD")
HOST = os.getenv("DB_ADMIN_HOST")
PORT = os.getenv("DB_ADMIN_PORT")
DBNAME = os.getenv("DB_ADMIN_NAME")
      
# Construcción de la URL con SSL requerido para Supabase
DATABASE_URL = f"postgresql+psycopg2://{USER}:{PASSWORD}@{HOST}:{PORT}/{DBNAME}?sslmode=require"

engine = create_engine(DATABASE_URL, poolclass=NullPool)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
)

Base = declarative_base()

# Dependencia para los endpoints de FastAPI
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
