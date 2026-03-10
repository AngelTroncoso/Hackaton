-- Supabase schema for BioTwin AI

-- Tabla de pacientes (datos anonimizados)
CREATE TABLE IF NOT EXISTS pacientes (
    id_anonimo uuid PRIMARY KEY DEFAULT gen_random_uuid(),
    edad smallint NOT NULL CHECK (edad >= 0),
    genero varchar(16) NOT NULL CHECK (genero IN ('masculino','femenino','otro','no informado'))
);

-- Tabla de biomarcadores, registro extendido
CREATE TABLE IF NOT EXISTS biomarcadores (
    id serial PRIMARY KEY,
    paciente_id uuid NOT NULL REFERENCES pacientes(id_anonimo) ON DELETE CASCADE,
    tipo varchar(64) NOT NULL,
    valor numeric NOT NULL,
    unidad varchar(32) NOT NULL,
    fecha_registro timestamptz NOT NULL DEFAULT now(),
    CHECK (valor >= 0)
);

-- Vista para promedio de glucosa por paciente en los últimos 30 días
CREATE OR REPLACE VIEW promedio_glucosa_30dias AS
SELECT
    p.id_anonimo AS paciente_id,
    AVG(b.valor) AS promedio_glucosa
FROM biomarcadores b
JOIN pacientes p ON p.id_anonimo = b.paciente_id
WHERE b.tipo = 'glucosa'
  AND b.fecha_registro >= now() - interval '30 days'
GROUP BY p.id_anonimo;
