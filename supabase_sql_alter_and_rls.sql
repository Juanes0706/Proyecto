-- Add imagen column to buses table if it does not exist
DO $$
BEGIN
    IF NOT EXISTS (
        SELECT 1
        FROM information_schema.columns
        WHERE table_name='buses' AND column_name='imagen'
    ) THEN
        ALTER TABLE buses ADD COLUMN imagen VARCHAR(255);
    END IF;
END
$$;

-- Enable Row Level Security on buses and estaciones tables
ALTER TABLE buses ENABLE ROW LEVEL SECURITY;
ALTER TABLE estaciones ENABLE ROW LEVEL SECURITY;

-- Create policy to allow inserts on buses table
CREATE POLICY IF NOT EXISTS "Allow insert on buses"
ON buses
FOR INSERT
TO public
USING (true);

-- Create policy to allow inserts on estaciones table
CREATE POLICY IF NOT EXISTS "Allow insert on estaciones"
ON estaciones
FOR INSERT
TO public
USING (true);
