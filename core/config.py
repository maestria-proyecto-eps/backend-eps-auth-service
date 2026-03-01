from pydantic_settings import BaseSettings, SettingsConfigDict

class Settings(BaseSettings):
    # Variables de Base de Datos
    user: str
    password: str
    host: str
    port: int = 5432
    dbname: str

    # Variables de JWT
    JWT_SECRET: str
    JWT_ALGORITHM: str
    JWT_EXPIRES_MINUTES: int

    # Configuración para leer el archivo .env
    model_config = SettingsConfigDict(env_file=".env", extra="ignore")

settings = Settings()
