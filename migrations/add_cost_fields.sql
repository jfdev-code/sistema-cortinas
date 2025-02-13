-- Añadir campos de cliente, telefono y email a la tabla cortinas
ALTER TABLE cortinas 
ADD COLUMN IF NOT EXISTS cliente VARCHAR(100),
ADD COLUMN IF NOT EXISTS telefono VARCHAR(20),
ADD COLUMN IF NOT EXISTS email VARCHAR(100);

-- Actualizar registros existentes con valores por defecto
UPDATE cortinas 
SET 
    cliente = COALESCE(cliente, 'Cliente Sin Nombre'),
    telefono = COALESCE(telefono, 'Sin Teléfono'),
    email = COALESCE(email, 'sin-email@example.com')
WHERE 
    cliente IS NULL OR 
    telefono IS NULL OR 
    email IS NULL;

-- Añadir comentarios para documentación
COMMENT ON COLUMN cortinas.cliente IS 'Nombre del cliente';
COMMENT ON COLUMN cortinas.telefono IS 'Número de teléfono del cliente';
COMMENT ON COLUMN cortinas.email IS 'Correo electrónico del cliente';