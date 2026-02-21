from fastapi import APIRouter, Depends, HTTPException
from shemas.auth import LoginRequest, TokenResponse, TokenData, APIResponse,UserResponse
from core.security import verificar_pwd, crear_token_acceso, get_pwd_hash
from core.dependencias import get_usuario_actual
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import User
from datetime import datetime, timedelta, timezone

# Rutas endpoints para la autenticación
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Datos de usuario
    user_db = db.query(User).filter(User.username == payload.username).first()

    # Validamos que exista
    if not user_db:
        return {"hasError": True, "Message": "Usuario no encontrado", "Data": None}

    ahora = datetime.now()

    # Bloqueo de 15 min
    if user_db.intentos_login >= 5:
        if user_db.hora_intento and ahora < user_db.hora_intento + timedelta(minutes=15):
            tiempo_restante = (user_db.hora_intento + timedelta(minutes=15)) - ahora
            minutos_espera = int(tiempo_restante.total_seconds() // 60)
            return {
                "hasError": True,
                "Message": f"Bloqueo de seguridad. Intente en {minutos_espera} min.",
                "Data": None
            }
        else:
            # Se cumplió el tiempo de castigo, reseteamos para permitir nuevo intento
            user_db.intentos_login = 0
            db.commit()

    # Reinicio después de 10 min
    if 0 < user_db.intentos_login < 5 and user_db.hora_intento:
        if ahora > user_db.hora_intento + timedelta(minutes=10):
            user_db.intentos_login = 0


    # Validar usuario y contraseña en base de datos
    if payload.username != user_db.username or not verificar_pwd(payload.password, get_pwd_hash(user_db.password)):
        # Si falla se establece hora de primer intento
        if user_db.intentos_login == 0:
            user_db.hora_intento = ahora
        user_db.intentos_login += 1

        # Este error fue el número 5, activamos el reloj de los 15 min último intento
        if user_db.intentos_login >= 5:
            user_db.hora_intento = ahora # El reloj ahora marca el inicio del bloqueo
            mensaje = "Límite superado. Cuenta bloqueada por 15 min."
        else:
            mensaje = f"Credenciales incorrectas. Intento {user_db.intentos_login} de 5."

        db.commit()

        return {
            "hasError": True,
            "Message":  mensaje,
            "Data": None
        }
    # LOGIN EXITOSO
    if user_db.estado == 0:
        return {
            "hasError": True,
            "Message": "Afiliación inactiva.",
            "Data": None
        }
    # Limpiamos si sale bien
    user_db.intentos_login = 0
    user_db.ultimo_intento = None
    db.commit()

    # Datos para el token
    token_data = {
        "id_usuario": user_db.id_usuario,
        "username": user_db.username,
        "id_role": user_db.id_rol
    }
    #Se crea el token y se verifica el formato de la información
    token = crear_token_acceso(token_data)
    return {
        "hasError": False,
        "Message": "Login exitoso",
        "Data": {"access_token": token,"token_type": "bearer"}
    }

# ETAPA DE PRUEBA (2)

# Endpoint PROTEGIDO para acceder a información de usuario
@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(usuario_actual: User = Depends(get_usuario_actual)):
    # usuario_actual viene directamente de la DB gracias a Depends(get_usuario_actual)
    return {
        "hasError": False,
        "Message": "Perfil de usuario obtenido correctamente",
        "Data": usuario_actual
    }

# Endpoint PROTEGIDO para cerrar sesión
@router.post("/logout", response_model=APIResponse[None])
def logout(current_user: TokenData = Depends(get_usuario_actual)):
    # Mensaje de cierre de sesión
    return {
        "hasError": False,
        "Message": f"Sesión de {current_user.username} finalizada correctamente.",
        "Data": None
    }