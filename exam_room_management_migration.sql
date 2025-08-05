-- Migration to create exam room management tables
-- Run this on your Supabase database

-- Create exam_rooms table for index range assignments
CREATE TABLE IF NOT EXISTS exam_rooms (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    room_code VARCHAR(50) UNIQUE NOT NULL,
    room_name VARCHAR(255) NOT NULL,
    index_start VARCHAR(20) NOT NULL,
    index_end VARCHAR(20) NOT NULL,
    capacity INTEGER,
    description TEXT,
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    updated_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Create room_recognition_logs table for tracking recognition attempts
CREATE TABLE IF NOT EXISTS room_recognition_logs (
    id UUID PRIMARY KEY DEFAULT uuid_generate_v4(),
    student_id UUID REFERENCES students(id) ON DELETE SET NULL,
    room_code VARCHAR(50) NOT NULL,
    status VARCHAR(20) NOT NULL CHECK (status IN ('valid', 'invalid')),
    beep_type VARCHAR(20) NOT NULL CHECK (beep_type IN ('confirmation', 'warning')),
    index_number VARCHAR(20),
    message TEXT NOT NULL,
    timestamp TIMESTAMP WITH TIME ZONE DEFAULT NOW(),
    created_at TIMESTAMP WITH TIME ZONE DEFAULT NOW()
);

-- Add indexes for better performance
CREATE INDEX IF NOT EXISTS idx_exam_rooms_room_code ON exam_rooms(room_code);
CREATE INDEX IF NOT EXISTS idx_exam_rooms_index_range ON exam_rooms(index_start, index_end);
CREATE INDEX IF NOT EXISTS idx_room_recognition_logs_room_code ON room_recognition_logs(room_code);
CREATE INDEX IF NOT EXISTS idx_room_recognition_logs_student_id ON room_recognition_logs(student_id);
CREATE INDEX IF NOT EXISTS idx_room_recognition_logs_timestamp ON room_recognition_logs(timestamp);
CREATE INDEX IF NOT EXISTS idx_room_recognition_logs_status ON room_recognition_logs(status);

-- Add comments for documentation
COMMENT ON TABLE exam_rooms IS 'Exam room assignments mapping index number ranges to specific rooms';
COMMENT ON TABLE room_recognition_logs IS 'Logs of facial recognition attempts in exam rooms with validation results';

COMMENT ON COLUMN exam_rooms.room_code IS 'Unique identifier for the exam room (e.g., "ROOM_A1", "LAB_01")';
COMMENT ON COLUMN exam_rooms.room_name IS 'Human-readable name of the exam room';
COMMENT ON COLUMN exam_rooms.index_start IS 'Starting index number for this room assignment';
COMMENT ON COLUMN exam_rooms.index_end IS 'Ending index number for this room assignment';
COMMENT ON COLUMN exam_rooms.capacity IS 'Maximum number of students that can be seated in this room';

COMMENT ON COLUMN room_recognition_logs.status IS 'Validation result: valid (student in correct room) or invalid (wrong room)';
COMMENT ON COLUMN room_recognition_logs.beep_type IS 'Audio feedback type: confirmation (success beep) or warning (error beep)';
COMMENT ON COLUMN room_recognition_logs.message IS 'Human-readable message explaining the recognition result';

-- Function to update updated_at timestamp
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$ language 'plpgsql';

-- Trigger to automatically update updated_at
CREATE TRIGGER update_exam_rooms_updated_at 
    BEFORE UPDATE ON exam_rooms 
    FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();

-- Sample data (optional - remove if not needed)
INSERT INTO exam_rooms (room_code, room_name, index_start, index_end, capacity, description) VALUES
    ('ROOM_A1', 'Examination Room A1', '20200001', '20200050', 50, 'Main examination hall - Ground floor'),
    ('ROOM_A2', 'Examination Room A2', '20200051', '20200100', 50, 'Main examination hall - Ground floor'),
    ('LAB_01', 'Computer Lab 1', '20200101', '20200130', 30, 'Computer laboratory with individual workstations'),
    ('HALL_B', 'Great Hall B', '20200131', '20200230', 100, 'Large capacity examination hall')
ON CONFLICT (room_code) DO NOTHING;
