-- Añadir campos de costos a la tabla cortinas
ALTER TABLE cortinas 
ADD COLUMN IF NOT EXISTS costo_materiales NUMERIC(10,2) NOT NULL DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS costo_mano_obra NUMERIC(10,2) NOT NULL DEFAULT 0.0,
ADD COLUMN IF NOT EXISTS costo_total NUMERIC(10,2) NOT NULL DEFAULT 0.0;

-- Actualizar los registros existentes
UPDATE cortinas 
SET costo_total = COALESCE(costo_materiales, 0) + COALESCE(costo_mano_obra, 0)
WHERE costo_total = 0;

-- Añadir comentarios para documentación
COMMENT ON COLUMN cortinas.costo_materiales IS 'Costo total de los materiales utilizados';
COMMENT ON COLUMN cortinas.costo_mano_obra IS 'Costo de la mano de obra';
COMMENT ON COLUMN cortinas.costo_total IS 'Costo total incluyendo materiales y mano de obra';