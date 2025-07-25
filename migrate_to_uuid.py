"""
Database Migration Script: Convert all ID fields to UUIDs
This script will help you migrate your Supabase database from auto-increment integers to UUIDs.

IMPORTANT: Run these SQL commands in your Supabase SQL editor or via the Supabase CLI.

Instructions:
1. Back up your current database before running these migrations
2. Execute these SQL commands in the order they appear
3. Test thoroughly after migration
"""

# SQL Migration Commands for Supabase

MIGRATION_SQL = """
-- Enable UUID extension if not already enabled
CREATE EXTENSION IF NOT EXISTS "uuid-ossp";

-- Step 1: Add new UUID columns to all tables
ALTER TABLE colleges ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE departments ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE admin_users ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE students ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();
ALTER TABLE recognition_logs ADD COLUMN new_id UUID DEFAULT uuid_generate_v4();

-- Step 2: Add new UUID foreign key columns
ALTER TABLE departments ADD COLUMN new_college_id UUID;
ALTER TABLE students ADD COLUMN new_college_id UUID;
ALTER TABLE students ADD COLUMN new_department_id UUID;
ALTER TABLE recognition_logs ADD COLUMN new_student_id UUID;

-- Step 3: Update foreign key references with UUID values
UPDATE departments SET new_college_id = colleges.new_id 
FROM colleges WHERE departments.college_id = colleges.id;

UPDATE students SET new_college_id = colleges.new_id 
FROM colleges WHERE students.college_id = colleges.id;

UPDATE students SET new_department_id = departments.new_id 
FROM departments WHERE students.department_id = departments.id;

UPDATE recognition_logs SET new_student_id = students.new_id 
FROM students WHERE recognition_logs.student_id = students.id;

-- Step 4: Drop old foreign key constraints (if any exist)
-- Note: Update these constraint names based on your actual database schema
-- ALTER TABLE departments DROP CONSTRAINT IF EXISTS departments_college_id_fkey;
-- ALTER TABLE students DROP CONSTRAINT IF EXISTS students_college_id_fkey;
-- ALTER TABLE students DROP CONSTRAINT IF EXISTS students_department_id_fkey;
-- ALTER TABLE recognition_logs DROP CONSTRAINT IF EXISTS recognition_logs_student_id_fkey;

-- Step 5: Drop old columns
ALTER TABLE colleges DROP COLUMN id;
ALTER TABLE departments DROP COLUMN college_id;
ALTER TABLE departments DROP COLUMN id;
ALTER TABLE admin_users DROP COLUMN id;
ALTER TABLE students DROP COLUMN college_id;
ALTER TABLE students DROP COLUMN department_id;
ALTER TABLE students DROP COLUMN id;
ALTER TABLE recognition_logs DROP COLUMN student_id;
ALTER TABLE recognition_logs DROP COLUMN id;

-- Step 6: Rename new columns to replace old ones
ALTER TABLE colleges RENAME COLUMN new_id TO id;
ALTER TABLE departments RENAME COLUMN new_college_id TO college_id;
ALTER TABLE departments RENAME COLUMN new_id TO id;
ALTER TABLE admin_users RENAME COLUMN new_id TO id;
ALTER TABLE students RENAME COLUMN new_college_id TO college_id;
ALTER TABLE students RENAME COLUMN new_department_id TO department_id;
ALTER TABLE students RENAME COLUMN new_id TO id;
ALTER TABLE recognition_logs RENAME COLUMN new_student_id TO student_id;
ALTER TABLE recognition_logs RENAME COLUMN new_id TO id;

-- Step 7: Add primary key constraints
ALTER TABLE colleges ADD PRIMARY KEY (id);
ALTER TABLE departments ADD PRIMARY KEY (id);
ALTER TABLE admin_users ADD PRIMARY KEY (id);
ALTER TABLE students ADD PRIMARY KEY (id);
ALTER TABLE recognition_logs ADD PRIMARY KEY (id);

-- Step 8: Add foreign key constraints
ALTER TABLE departments ADD CONSTRAINT departments_college_id_fkey 
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE;

ALTER TABLE students ADD CONSTRAINT students_college_id_fkey 
    FOREIGN KEY (college_id) REFERENCES colleges(id) ON DELETE CASCADE;

ALTER TABLE students ADD CONSTRAINT students_department_id_fkey 
    FOREIGN KEY (department_id) REFERENCES departments(id) ON DELETE CASCADE;

ALTER TABLE recognition_logs ADD CONSTRAINT recognition_logs_student_id_fkey 
    FOREIGN KEY (student_id) REFERENCES students(id) ON DELETE CASCADE;

-- Step 9: Set default UUID generation for new records
ALTER TABLE colleges ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE departments ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE admin_users ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE students ALTER COLUMN id SET DEFAULT uuid_generate_v4();
ALTER TABLE recognition_logs ALTER COLUMN id SET DEFAULT uuid_generate_v4();

-- Step 10: Add NOT NULL constraints where appropriate
ALTER TABLE colleges ALTER COLUMN id SET NOT NULL;
ALTER TABLE departments ALTER COLUMN id SET NOT NULL;
ALTER TABLE departments ALTER COLUMN college_id SET NOT NULL;
ALTER TABLE admin_users ALTER COLUMN id SET NOT NULL;
ALTER TABLE students ALTER COLUMN id SET NOT NULL;
ALTER TABLE students ALTER COLUMN college_id SET NOT NULL;
ALTER TABLE students ALTER COLUMN department_id SET NOT NULL;
ALTER TABLE recognition_logs ALTER COLUMN id SET NOT NULL;
ALTER TABLE recognition_logs ALTER COLUMN student_id SET NOT NULL;

"""

if __name__ == "__main__":
    print("UUID Migration Script for KNUST Student System")
    print("=" * 50)
    print(MIGRATION_SQL)
    print("\n" + "=" * 50)
    print("IMPORTANT:")
    print("1. Backup your database before running these commands")
    print("2. Run these SQL commands in your Supabase SQL editor")
    print("3. Test your application thoroughly after migration")
    print("4. Update any hardcoded integer IDs in your application code")
