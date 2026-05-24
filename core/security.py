# Librearia para hash
import bcrypt
#Para crear Tokens
from datetime import datetime, timedelta, timezone
from jose import jwt
#Para garantizar el formato de los datos en token
from schemas.auth import TokenData
#  Para leer archivo .env
from core.config import settings

class Security:

    @staticmethod
    def verify_password(password: str, hashed_password: str) -> bool:
        if not password or not hashed_password:
            return False

        return bcrypt.checkpw(
            password.encode("utf-8"),
            hashed_password.encode("utf-8")
        )

    @staticmethod
    def get_pwd_hash(password: str) -> str:
        # Generar hash
        salt = bcrypt.gensalt(rounds=12)
        hashed = bcrypt.hashpw(password.encode("utf-8"), salt)
        # Retorna como string
        return hashed.decode("utf-8")

def crear_token_acceso(data: dict):

    #cambio de datos temporal
    user_data = TokenData(**data)
    datos = user_data.model_dump()

    to_encode = datos.copy()

    # Determina a qué hora vence el token
    expire = datetime.now(timezone.utc) + timedelta(minutes=settings.JWT_EXPIRES_MINUTES)

    # Fija la hora de expiración
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, settings.JWT_SECRET, algorithm=settings.JWT_ALGORITHM)

    return encoded_jwt



