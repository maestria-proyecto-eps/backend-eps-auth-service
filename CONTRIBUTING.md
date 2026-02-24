
# 📁 Estructura del Proyecto

```text
app/
├── main.py
├── routers/
├── models/
├── schemas/
├── services/
├── core/
```

---

## 📌 `/routers`

Contiene los endpoints (rutas HTTP).
Aquí se definen los controladores que reciben y responden peticiones.

Ejemplo:

* usuarios.py
* auth.py

---

## 📌 `/models`

Modelos ORM de SQLAlchemy.
Representan las tablas en la base de datos.

Ejemplo:

```python
class User(Base):
    __tablename__ = "users"
```

---

## 📌 `/schemas`

Modelos Pydantic para validación y serialización de datos.
Se usan para entrada (request) y salida (response).

Ejemplo:

```python
class UserCreate(BaseModel):
```

---

## 📌 `/services`

Contiene la lógica de negocio.
Aquí se implementan las reglas del sistema y operaciones sobre los modelos.

---

## 📌 `/core`

Configuraciones globales del proyecto.

Ejemplos:

* config.py → Manejo de variables de entorno
* security.py → JWT, hashing
* settings.py → Configuración general

---



# 🌳 Convención de Ramas (GitFlow Simplificado)

Este proyecto utiliza un **GitFlow simplificado** para mantener orden, claridad y estabilidad en el desarrollo.

### 📌 Estructura de ramas

```
main
develop
feature/*
bugfix/*
hotfix/*
```

---

## 🔹 `main`

* Contiene únicamente código estable y listo para producción.
* Siempre debe estar en estado **deployable**.
* No se permite hacer push directo.
* Solo recibe cambios desde:

  * `develop` (nuevas versiones)
  * `hotfix/*` (correcciones críticas)

---

## 🔹 `develop`

* Rama de integración.
* Base para nuevas funcionalidades.
* Puede contener cambios en validación antes de llegar a producción.
* Recibe merges desde:

  * `feature/*`
  * `bugfix/*`
  * `hotfix/*` (después de aplicar en `main`)

---

## 🚀 `feature/*`

Ramas para nuevas funcionalidades.

### 📌 Convención de nombres

```
feature/<descripcion-corta>
```

### ✅ Ejemplos

```
feature/login-jwt
feature/roi-editor
feature/notifications-module
```

### 🔄 Flujo

1. Se crea desde `develop`
2. Se implementa la funcionalidad
3. Se abre Pull Request hacia `develop`
4. Se elimina después del merge

---

## 🐛 `bugfix/*`

Ramas para corregir errores detectados en `develop` antes de pasar a producción.

### 📌 Convención de nombres

```
bugfix/<descripcion-corta>
```

### ✅ Ejemplos

```
bugfix/fix-token-refresh
bugfix/null-camera-error
```

### 🔄 Flujo

1. Se crea desde `develop`
2. Se corrige el error
3. Se hace Pull Request hacia `develop`
4. Se elimina después del merge

> ⚠ Si el error está en producción, debe usarse `hotfix/*`, no `bugfix/*`.

---

## 🚑 `hotfix/*`

Ramas para correcciones críticas en producción.

### 📌 Convención de nombres

```
hotfix/<descripcion-corta>
```

### ✅ Ejemplos

```
hotfix/security-patch
hotfix/crash-on-startup
```

### 🔄 Flujo

1. Se crea desde `main`
2. Se corrige el problema
3. Se hace merge hacia:

   * `main`
   * `develop` (obligatorio para evitar regresiones)
4. Se elimina después del merge

---

## 📌 Reglas Generales

* ❌ No hacer push directo a `main` ni `develop`
* ✅ Todo cambio debe pasar por Pull Request
* ✅ Mantener nombres descriptivos y en kebab-case
* ✅ Eliminar ramas después del merge
* ✅ Mantener commits claros y atómicos

---

## 🔁 Flujo General

```
feature/* → develop → main
bugfix/*  → develop → main
hotfix/*  → main → develop
```

Este modelo permite:

* Separar desarrollo de producción
* Mantener estabilidad en `main`
* Trabajar en paralelo sin conflictos
* Aplicar correcciones críticas sin afectar el flujo normal

```
```
