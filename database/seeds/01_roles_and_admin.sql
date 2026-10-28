-- =============================================================================
-- Hawlwadaag Primary and Secondary School Management System
-- Database Seed Data (Reference SQL)
-- =============================================================================

-- 1. Insert Core System Roles
INSERT INTO roles (name, description, is_system) VALUES
('ADMIN', 'System and school administrator with full management access', TRUE),
('TEACHER', 'Academic faculty member managing attendance and grades', TRUE),
('STUDENT', 'Enrolled student accessing timetable and results', TRUE),
('PARENT', 'Parent or legal guardian monitoring student progress', TRUE),
('STAFF', 'Administrative and supporting school staff', TRUE)
ON CONFLICT (name) DO NOTHING;

-- 2. Insert School Branding & Core System Settings
INSERT INTO system_settings (key, value, description, is_public) VALUES
('school_name', 'Hawlwadaag Primary and Secondary School', 'Official school institution name', TRUE),
('school_short_name', 'Hawlwadaag School', 'Abbreviated school name', TRUE),
('school_motto', 'Excellence in Education and Character', 'Official school motto', TRUE),
('school_email', 'info@hawlwadaagschool.edu.so', 'Official contact email', TRUE),
('school_phone', '+252 61 0000000', 'Official contact phone number', TRUE),
('school_address', 'Hawlwadaag District, Mogadishu, Somalia', 'Physical campus location', TRUE),
('primary_color', '#1e3a8a', 'Primary school theme branding color', TRUE),
('secondary_color', '#0284c7', 'Secondary theme branding color', TRUE)
ON CONFLICT (key) DO NOTHING;
