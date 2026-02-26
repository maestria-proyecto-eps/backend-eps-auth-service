from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from core.config import settings
from shemas.auth import TokenData

from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User

# Endpoint protegido para datos del usuario actual
end_protegido = OAuth2PasswordBearer(tokenUrl="/api/auth/login")

def get_usuario_actual(token: str = Depends(end_protegido),db: Session = Depends(get_db)):

    try:
        # Decodificar token
        datos = jwt.decode(token, settings.JWT_SECRET, algorithms=[settings.JWT_ALGORITHM])

        # Extraer información del token
        id_usuario: int = datos.get("id_usuario")
        num_documento: int = datos.get("num_documento")
        id_role: int = datos.get("id_role")

        # validación de información existente
        if num_documento is None or id_usuario is None or id_role is None:
            raise HTTPException(status_code=401, detail="Token inválido")

        user = db.query(User).filter(User.id_usuario == id_usuario).first()
        # Validamos que esté en base de datos
        if user is None:
            raise HTTPException(status_code=404, detail="Usuario no encontrado en el sistema")

        # Retorna los datos del usuario con el token ingresado
        return user

    except JWTError:
        raise HTTPException(status_code=401, detail="Token expirado")

