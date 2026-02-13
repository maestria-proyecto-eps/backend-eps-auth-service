from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    model_config = SettingsConfigDict(env_file=".env", env_file_encoding="utf-8")

    DB_URL: str

    #jwt
    JWT_EXPIRES_MINUTES: int
    JWT_SECRET: str
    JWT_ALGORITHM: str

settings = Settings()
