from fastapi import Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from db.session import get_db
from models.user import USUARIOS
from core.auth_utils import get_current_user_id

def get_usuario_actual(
    user_id: int = Depends(get_current_user_id),
    db: Session = Depends(get_db)
) -> USUARIOS:
    user = (
        db.query(USUARIOS)
        .options(joinedload(USUARIOS.rol))
        .filter(USUARIOS.id_usuario == user_id)
        .first()
    )

    if user is None:
        raise HTTPException(
            status_code=404,
            detail="Usuario no encontrado en el sistema"
        )

    return user


class RequireRole:
    def __init__(self, allowed_roles: list[str]):
        self.allowed_roles = allowed_roles

    def __call__(self, user: USUARIOS = Depends(get_usuario_actual)) -> USUARIOS:
        if (
            user.rol.nombre_rol not in self.allowed_roles
            and user.rol.nombre_rol != "Administrador"
        ):
            raise HTTPException(
                status_code=403,
                detail={
                    "hasError": True,
                    "Message": f"Acceso denegado. Se requiere uno de estos roles: {self.allowed_roles}",
                    "Data": None
                }
            )
        return user