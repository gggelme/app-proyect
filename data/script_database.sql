-- Limpieza total del esquema para empezar de cero
DROP SCHEMA public CASCADE;
CREATE SCHEMA public;

-- 1. PERSONA
CREATE TABLE persona (
    id SERIAL PRIMARY KEY,
    dni VARCHAR(20) UNIQUE NOT NULL,
    nomb_apel VARCHAR(100) NOT NULL,
    fecha_nac DATE,
    domicilio TEXT,
    telefono VARCHAR(20),
    email VARCHAR(100),
    fecha_registro TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- 2. ALUMNO
CREATE TABLE alumno (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER NOT NULL UNIQUE REFERENCES persona(id) ON DELETE CASCADE,
    fecha_ing DATE DEFAULT CURRENT_DATE,
    estado_activo BOOLEAN DEFAULT TRUE
);

-- 3. PROFESOR
CREATE TABLE profesor (
    id SERIAL PRIMARY KEY,
    id_persona INTEGER NOT NULL UNIQUE REFERENCES persona(id) ON DELETE CASCADE,
    alias VARCHAR(50),
    especialidad TEXT
);

-- 4. CUOTA
CREATE TABLE cuota (
    id SERIAL PRIMARY KEY,
    nombre VARCHAR(100) NOT NULL, 
    precio_cuota DECIMAL(10, 2) NOT NULL,
    descripcion TEXT
);

-- 5. ALUMNO_CUOTA
CREATE TABLE alumno_cuota (
    id SERIAL PRIMARY KEY,
    id_alumno INTEGER NOT NULL REFERENCES alumno(id),
    id_cuota INTEGER NOT NULL REFERENCES cuota(id),
    CONSTRAINT ak_alumno_cuota UNIQUE (id_alumno, id_cuota)
);

-- 6. PAGO
CREATE TABLE pago (
    id SERIAL PRIMARY KEY,
    id_alumno_cuota INTEGER NOT NULL REFERENCES alumno_cuota(id),
    fecha_pago TIMESTAMP, 
    pagado_bool BOOLEAN DEFAULT FALSE, -- Se crea como deuda por defecto
    mes_correspondiente DATE NOT NULL, 
    monto_a_pagar DECIMAL(10, 2) NOT NULL,
    monto_recibido DECIMAL(10, 2) DEFAULT 0,
    metodo_pago VARCHAR(50),
    CONSTRAINT ak_pago_unico_mes UNIQUE (id_alumno_cuota, mes_correspondiente)
);

-- 7. CLASE
CREATE TABLE clase (
    id SERIAL PRIMARY KEY,
    nombre_clase VARCHAR(100) NOT NULL,
    id_profesor INTEGER NOT NULL REFERENCES profesor(id),
    nivel VARCHAR(50)
);

-- 8. ALUMNO_CLASE
CREATE TABLE alumno_clase (
    id SERIAL PRIMARY KEY,
    id_alumno INTEGER NOT NULL REFERENCES alumno(id),
    id_clase INTEGER NOT NULL REFERENCES clase(id),
    CONSTRAINT ak_alumno_clase UNIQUE (id_alumno, id_clase)
);

-- 9. HORARIO (Con Clave Alternativa)
CREATE TABLE horario (
    id SERIAL PRIMARY KEY,
    dia VARCHAR(15) NOT NULL, 
    hora_init TIME NOT NULL,
    hora_fin TIME NOT NULL,
    -- La Clave Alternativa asegura que no haya duplicados de tiempo
    CONSTRAINT ak_horario_dia_hora UNIQUE (dia, hora_init) 
);

-- 10. HORARIO_CLASE
CREATE TABLE horario_clase (
    id SERIAL PRIMARY KEY,
    id_horario INTEGER NOT NULL REFERENCES horario(id),
    id_clase INTEGER NOT NULL REFERENCES clase(id),
    aula VARCHAR(50),
    CONSTRAINT ak_horario_clase UNIQUE (id_horario, id_clase)
);