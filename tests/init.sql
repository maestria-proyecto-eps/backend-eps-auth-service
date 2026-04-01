-- Schema and seed data for CI integration tests

CREATE TABLE IF NOT EXISTS roles (
    id_rol SERIAL PRIMARY KEY,
    nombre_rol VARCHAR(50) NOT NULL UNIQUE
);

CREATE TABLE IF NOT EXISTS persona (
    num_documento BIGINT PRIMARY KEY,
    nombres VARCHAR(50) NOT NULL,
    apellidos VARCHAR(50) NOT NULL
);

CREATE TABLE IF NOT EXISTS usuarios (
    id_usuario SERIAL PRIMARY KEY,
    password VARCHAR(60) NOT NULL,
    id_rol INTEGER NOT NULL REFERENCES roles(id_rol),
    estado BOOLEAN DEFAULT TRUE,
    intentos_login SMALLINT DEFAULT 0,
    tiempo_de_fallo_login TIMESTAMP,
    num_documento BIGINT NOT NULL REFERENCES persona(num_documento)
);

-- Roles
INSERT INTO roles (id_rol, nombre_rol) VALUES
(1, 'Farmacéutico'),
(2, 'Médico'),
(3, 'Paciente'),
(4, 'Enfermero'),
(5, 'Talento Humano');

SELECT setval('roles_id_rol_seq', (SELECT MAX(id_rol) FROM roles));

-- Personas
INSERT INTO persona (num_documento, nombres, apellidos) VALUES
(80112457,   'Alejandro', 'Ruiz Esparza'),
(1018442903, 'Julián',    'Castro Meza'),
(1018442904, 'Ana',       'Casillas'),
(1012334885, 'Carlos',    'Gaviria'),
(1015442890, 'María',     'Ramírez'),
(52884103,   'Pedro',     'Rojas');

-- Usuarios (passwords hashed with bcrypt rounds=12)
-- id_usuario values match assertions in tests/test_auth.py:
--   id_usuario=1  -> Médico (num_documento=80112457)
--   id_usuario=44 -> Paciente (num_documento=1018442903)
INSERT INTO usuarios (id_usuario, password, id_rol, estado, intentos_login, num_documento) VALUES
(1,  '$2b$12$lwVa7X0VfsrKQGvYd8F36eWUgSWYoEupyfV2KyTtO4kbC7IiD3X9O', 2, true,  0, 80112457),
(2,  '$2b$12$KJrBLcuOM1s.JGOZHj0gt.txTsN82uachD826mTeYg.PlajzNSkRi', 1, true,  0, 1018442904),
(3,  '$2b$12$v1B7xx5FJqDUEennwz1o5eTQl7Zfj.KihfCyPl/R49XdTHC0TllAq', 4, true,  0, 1012334885),
(4,  '$2b$12$ej/jTC2MgK/9yJki96qwyetA58bzwqmWvXGkBFTmauR1t7Lsae8R2', 5, true,  0, 1015442890),
(5,  '$2b$12$iuhok331E6YLIzCYgRnGael3VQkgkD829E1rcOrIaqqIORyRlDDQC', 3, false, 0, 52884103),
(44, '$2b$12$pMH2oXdXAlmv.YxQg.wEheNk.vvcVkPeyq4jo747/sIaY8dZnTBM2', 3, true,  0, 1018442903);

SELECT setval('usuarios_id_usuario_seq', (SELECT MAX(id_usuario) FROM usuarios));
