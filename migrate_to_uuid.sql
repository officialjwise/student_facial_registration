-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: Remove default and drop any existing auto-increment sequences
ALTER TABLE admin_users ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS admin_users_id_seq;
ALTER TABLE colleges ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS colleges_id_seq;
ALTER TABLE departments ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS departments_id_seq;
ALTER TABLE students ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS students_id_seq;
ALTER TABLE recognition_logs ALTER COLUMN id DROP DEFAULT;
DROP SEQUENCE IF EXISTS recognition_logs_id_seq;

-- Step 2: Add new UUID columns to all tables
ALTER TABLE colleges ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE departments ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE admin_users ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE students ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE recognition_logs ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();

-- Step 3: Add new UUID foreign key columns
ALTER TABLE departments ADD COLUMN new_college_id UUID;
ALTER TABLE students ADD COLUMN new_college_id UUID;
ALTER TABLE students ADD COLUMN new_department_id UUID;
ALTER TABLE recognition_logs ADD COLUMN new_student_id UUID;

-- Step 4: Update foreign key references with UUID values
UPDATE departments SET new_college_id = colleges.new_id 
FROM colleges WHERE departments.college_id = colleges.id;

UPDATE students SET new_college_id = colleges.new_id 
FROM colleges WHERE students.college_id = colleges.id;

UPDATE students SET new_department_id = departments.new_id 
FROM departments WHERE students.department_id = departments.id;

UPDATE recognition_logs SET new_student_id = students.new_id 
FROM students WHERE recognition_logs.student_id = students.id;

-- Step 5: Drop old foreign key constraints (if any exist)
ALTER TABLE departments DROP CONSTRAINT IF EXISTS departments_college_id_fkey;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_college_id_fkey;
ALTER TABLE students DROP CONSTRAINT IF EXISTS students_department_id_fkey;
ALTER TABLE recognition_logs DROP CONSTRAINT IF EXISTS recognition_logs_student_id_fkey;

-- Step 6: Drop old columns
ALTER TABLE colleges DROP COLUMN IF EXISTS id;
ALTER TABLE departments DROP COLUMN IF EXISTS college_id;
ALTER TABLE departments DROP COLUMN IF EXISTS id;
ALTER TABLE admin_users DROP COLUMN IF EXISTS id;
ALTER TABLE students DROP COLUMN IF EXISTS college_id;
ALTER TABLE students DROP COLUMN IF EXISTS department_id;
ALTER TABLE students DROP COLUMN IF EXISTS id;
ALTER TABLE recognition_logs DROP COLUMN IF EXISTS student_id;
ALTER TABLE recognition_logs DROP COLUMN IF EXISTS id;

-- Step 7: Rename new columns to replace old ones
ALTER TABLE colleges RENAME COLUMN new_id TO id;
ALTER TABLE departments RENAME COLUMN new_college_id TO college_id;
ALTER TABLE departments RENAME COLUMN new_id TO id;
ALTER TABLE admin_users RENAME COLUMN new_id TO id;
ALTER TABLE students RENAME COLUMN new_college_id TO college_id;
ALTER TABLE students RENAME COLUMN new_department_id TO department_id;
ALTER TABLE students RENAME COLUMN new_id TO id;
ALTER TABLE recognition_logs RENAME COLUMN new_student_id TO student_id;
ALTER TABLE recognition_logs RENAME COLUMN new_id TO id;

-- Step 8: Add primary key constraints
ALTER TABLE colleges ADD PRIMARY KEY (id);
ALTER TABLE departments ADD PRIMARY KEY (id);
ALTER TABLE admin_users ADD PRIMARY KEY (id);
ALTER TABLE students ADD PRIMARY KEY (id);
ALTER TABLE recognition_logs ADD PRIMARY KEY (id);

-- Step 9: Add foreign key constraints
ALTER TABLE departments ADD CONSTRAINT departments_college_id_fkey 
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE;

ALTER TABLE students ADD CONSTRAINT students_college_id_fkey 
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE;

ALTER TABLE students ADD CONSTRAINT students_department_id_fkey 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;

ALTER TABLE recognition_logs ADD CONSTRAINT recognition_logs_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Step 10: Set default UUID generation for new records
ALTER TABLE colleges ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE departments ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE admin_users ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE students ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE recognition_logs ALTER COLUMN id SET DEFAULT uuid_generate_v4();

-- Step 11: Add NOT NULL constraints where appropriate
ALTER TABLE colleges ALTER COLUMN id SET NOT NULL;
ALTER TABLE departments ALTER COLUMN id SET NOT NULL;
ALTER TABLE departments ALTER COLUMN college_id SET NOT NULL;
ALTER TABLE admin_users ALTER COLUMN id SET NOT NULL;
ALTER TABLE students ALTER COLUMN id SET NOT NULL;
ALTER TABLE students ALTER COLUMN college_id SET NOT NULL;
ALTER TABLE students ALTER COLUMN department_id SET NOT NULL;
ALTER TABLE recognition_logs ALTER COLUMN id SET NOT NULL;
ALTER TABLE recognition_logs ALTER COLUMN student_id SET NOT NULL;

-- Step 12: Verify table structure
CREATE OR REPLACE VIEW migration_verification AS
SELECT 
    table_name,
    column_name,
    data_type,
    is_nullable,
    column_default
FROM information_schema.columns
WHERE table_name IN ('colleges', 'departments', 'admin_users', 'students', 'recognition_logs')
AND column_name IN ('id', 'college_id', 'department_id', 'student_id');
