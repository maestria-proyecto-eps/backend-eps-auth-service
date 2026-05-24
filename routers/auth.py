from fastapi import APIRouter, Depends, HTTPException
from schemas.auth import LoginRequest, TokenResponse, TokenData, APIResponse,UserResponse
from core.security import Security, crear_token_acceso
from core.dependencias import get_usuario_actual
from sqlalchemy.orm import Session
from db.session import get_db
from models.user import USUARIOS, ROLES,PERSONA

from datetime import datetime, timedelta, timezone

# Rutas endpoints para la autenticación
router = APIRouter(
    prefix="/api/auth",
    tags=["Autenticación"]
)


@router.post("/login", response_model=APIResponse[TokenResponse])
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    # Datos de usuario
    user_db = db.query(USUARIOS).join(PERSONA).filter(USUARIOS.num_documento == payload.num_documento).first()

    # Validamos que exista
    if not user_db:
        return {"hasError": True, "Message": "Credenciales incorrectas.", "Data": None}

    ahora = datetime.now()

    # Bloqueo de 15 min
    if user_db.intentos_login >= 5:
        if user_db.tiempo_de_fallo_login and ahora < user_db.tiempo_de_fallo_login + timedelta(minutes=15):
            tiempo_restante = (user_db.tiempo_de_fallo_login + timedelta(minutes=15)) - ahora
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
    if 0 < user_db.intentos_login < 5 and user_db.tiempo_de_fallo_login:
        if ahora > user_db.tiempo_de_fallo_login + timedelta(minutes=10):
            user_db.intentos_login = 0
            db.commit()


    # Validar usuario y contraseña en base de datos
    if payload.num_documento != user_db.num_documento or not Security.verify_password(payload.password, user_db.password):
        # Si falla se establece hora de primer intento
        if user_db.intentos_login == 0:
            user_db.tiempo_de_fallo_login = ahora

        user_db.intentos_login += 1

        # Este error fue el número 5, activamos el reloj de los 15 min último intento
        if user_db.intentos_login >= 5:
            user_db.tiempo_de_fallo_login = ahora # El reloj ahora marca el inicio del bloqueo
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
    if user_db.estado ==0:
        return {
            "hasError": True,
            "Message": "Afiliación inactiva.",
            "Data": None
        }
    # Limpiamos si sale bien
    user_db.intentos_login = 0
    user_db.tiempo_de_fallo_login = None
    db.commit()


    rol_db = db.query(ROLES).filter(ROLES.id_rol == user_db.id_rol).first()
    nombre_role = rol_db.nombre_rol if rol_db else "Paciente"
    # Datos para el token
    token_data = {
        "id_usuario": user_db.id_usuario,
        "num_documento": user_db.num_documento,
        "id_role": user_db.id_rol,
        "role": nombre_role
    }
    #Se crea el token y se verifica el formato de la información
    token = crear_token_acceso(token_data)
    return {
        "hasError": False,
        "Message": "Login exitoso",
        "Data": {"access_token": token,"token_type": "bearer"}
    }

# Endpoint PROTEGIDO para acceder a información de usuario
@router.get("/me", response_model=APIResponse[UserResponse])
def get_me(usuario_actual: USUARIOS = Depends(get_usuario_actual),db: Session = Depends(get_db)):

    rol_db = db.query(ROLES).filter(ROLES.id_rol == usuario_actual.id_rol).first()
    nombre_role = rol_db.nombre_rol if rol_db else "Paciente"

    persona = db.query(PERSONA).filter(PERSONA.num_documento == usuario_actual.num_documento).first()
    nombres = persona.nombres if persona else "Desconocido"
    apellidos = persona.apellidos if persona else "Desconocido"
    estado= 1 if usuario_actual.estado else 0

    return {
        "hasError": False,
        "Message": "Perfil de usuario obtenido correctamente",
        "Data": {
            "id_usuario": usuario_actual.id_usuario,
            "num_documento": usuario_actual.num_documento,
            "id_rol": usuario_actual.id_rol,
            "role": nombre_role,
            "estado": estado,
            "nombres": nombres,
            "apellidos": apellidos
        }
    }

# Endpoint PROTEGIDO para cerrar sesión
@router.post("/logout", response_model=APIResponse[None])
def logout(current_user: USUARIOS = Depends(get_usuario_actual),db: Session = Depends(get_db)):

    persona = db.query(PERSONA).filter(PERSONA.num_documento == current_user.num_documento).first()
    nombre_completo = f"{persona.nombres} {persona.apellidos}" if persona else "Paciente"
    # Mensaje de cierre de sesión
    return {
        "hasError": False,
        "Message": f"Sesión de {nombre_completo} finalizada correctamente.",
        "Data": None
    }

@router.post("/reset-attempts", response_model=APIResponse[None])
def reset_user_attempts(payload: LoginRequest, db: Session = Depends(get_db)):

    # Buscar al usuario por documento
    user_db = db.query(USUARIOS).filter(USUARIOS.num_documento == payload.num_documento).first()

    if not user_db:
        return {
            "hasError": True,
            "Message": "Usuario no encontrado.",
            "Data": None
        }

    # Reiniciar valores de bloqueo
    user_db.intentos_login = 0
    user_db.tiempo_de_fallo_login = None

    try:
        db.commit()
        return {
            "hasError": False,
            "Message": f"Intentos reiniciados para el documento {payload.num_documento}.",
            "Data": None
        }
    except Exception as e:
        db.rollback()
        return {
            "hasError": True,
            "Message": f"Error al reiniciar: {str(e)}",
            "Data": None
        }