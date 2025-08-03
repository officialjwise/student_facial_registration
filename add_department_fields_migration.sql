-- Migration to add department_head and description fields to departments table
-- Run this on your Supabase database

-- Add the new columns to the departments table
ALTER TABLE departments 
ADD COLUMN IF NOT EXISTS department_head VARCHAR(255),
ADD COLUMN IF NOT EXISTS description TEXT;

-- Add comments to document the new fields
COMMENT ON COLUMN departments.department_head IS 'Name of the department head or chairperson';
COMMENT ON COLUMN departments.description IS 'Description of the department, its focus areas, and objectives';

-- Update any existing departments with placeholder values if needed
-- (Optional - you can skip this if you want to leave existing records with NULL values)
-- UPDATE departments SET 
--     department_head = 'TBD',
--     description = 'Department description to be added'
-- WHERE department_head IS NULL OR description IS NULL;
