-- Student Database Management System
-- Normalized Schema (3NF)

CREATE DATABASE IF NOT EXISTS student_db;
USE student_db;

-- Departments table
CREATE TABLE IF NOT EXISTS departments (
    dept_id INT AUTO_INCREMENT PRIMARY KEY,
    dept_name VARCHAR(100) NOT NULL UNIQUE
);

-- Students table
CREATE TABLE IF NOT EXISTS students (
    student_id INT AUTO_INCREMENT PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    dob DATE,
    gender ENUM('Male', 'Female') DEFAULT NULL,
    email VARCHAR(100) UNIQUE,
    phone VARCHAR(15),
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Courses table
CREATE TABLE IF NOT EXISTS courses (
    course_id INT AUTO_INCREMENT PRIMARY KEY,
    course_name VARCHAR(100) NOT NULL,
    credits INT NOT NULL DEFAULT 3,
    dept_id INT,
    FOREIGN KEY (dept_id) REFERENCES departments(dept_id)
        ON DELETE SET NULL
        ON UPDATE CASCADE
);

-- Enrollments table (junction table: many-to-many students <-> courses)
CREATE TABLE IF NOT EXISTS enrollments (
    enrollment_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    semester VARCHAR(20),
    grade VARCHAR(2),
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_enrollment (student_id, course_id, semester)
);

-- Attendance table
CREATE TABLE IF NOT EXISTS attendance (
    attendance_id INT AUTO_INCREMENT PRIMARY KEY,
    student_id INT NOT NULL,
    course_id INT NOT NULL,
    attendance_date DATE NOT NULL,
    status ENUM('Present', 'Absent', 'Late') NOT NULL DEFAULT 'Present',
    FOREIGN KEY (student_id) REFERENCES students(student_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    FOREIGN KEY (course_id) REFERENCES courses(course_id)
        ON DELETE CASCADE
        ON UPDATE CASCADE,
    UNIQUE KEY unique_attendance (student_id, course_id, attendance_date)
);

-- Indexes for faster lookups
CREATE INDEX idx_student_name ON students(name);
CREATE INDEX idx_student_dept ON students(dept_id);
CREATE INDEX idx_course_dept ON courses(dept_id);

-- Sample seed data
INSERT INTO departments (dept_name) VALUES
    ('Computer Science'),
    ('Data Analytics'),
    ('Electronics'),
    ('Mechanical')
ON DUPLICATE KEY UPDATE dept_name = dept_name;

INSERT INTO courses (course_name, credits, dept_id) VALUES
    ('Database Systems', 4, 1),
    ('Data Structures', 4, 1),
    ('Python for Analytics', 3, 2),
    ('Statistics', 3, 2)
ON DUPLICATE KEY UPDATE course_name = course_name;
