-- Create tables
CREATE TABLE department (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL
);

CREATE TABLE instructor (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    department_id INTEGER REFERENCES department(id)
);

CREATE TABLE room (
    id SERIAL PRIMARY KEY,
    name VARCHAR(50) NOT NULL,
    capacity INTEGER NOT NULL
);

CREATE TABLE subject (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    description TEXT,
    instructor_id INTEGER REFERENCES instructor(id),
    department_id INTEGER REFERENCES department(id)
);

CREATE TABLE student (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    major VARCHAR(100),
    year INTEGER,
    semester INTEGER,
    group_id INTEGER
);

CREATE TABLE group_schedule (
    group_id INTEGER NOT NULL,
    subject_id INTEGER REFERENCES subject(id),
    room_id INTEGER REFERENCES room(id),
    day VARCHAR(20) NOT NULL,
    start_time TIME NOT NULL,
    end_time TIME NOT NULL,
    PRIMARY KEY (group_id, subject_id)
);

CREATE TABLE subject_score (
    student_id INTEGER REFERENCES student(id),
    subject_id INTEGER REFERENCES subject(id),
    score FLOAT NOT NULL,
    semester INTEGER NOT NULL,
    year INTEGER NOT NULL,
    PRIMARY KEY (student_id, subject_id, semester, year)
);

-- Insert sample data

-- Departments
INSERT INTO department (name) VALUES
    ('Physics'),
    ('Computer Science'),
    ('Mathematics'),
    ('Electrical Engineering'),
    ('Biology');

-- Instructors
INSERT INTO instructor (name, email, department_id) VALUES
    ('Jane Smith', 'jane.smith@university.com', 1),
    ('John Doe', 'john.doe@university.com', 2),
    ('Emma Davis', 'emma.davis@university.com', 3),
    ('Robert Brown', 'robert.brown@university.com', 4),
    ('Olivia Johnson', 'olivia.johnson@university.com', 5);

-- Rooms
INSERT INTO room (name, capacity) VALUES
    ('Room 101', 30),
    ('Room 305', 40),
    ('Lab A', 20),
    ('Auditorium', 100);

-- Subjects
INSERT INTO subject (name, description, instructor_id, department_id) VALUES
    ('Advanced Calculus', 'Covers advanced calculus topics.', 3, 3),
    ('Introduction to Programming', 'Basic programming concepts.', 2, 2),
    ('Physics I', 'Mechanics and thermodynamics.', 1, 1),
    ('Digital Systems', 'Introduction to digital electronics.', 4, 4),
    ('Molecular Biology', 'Study of molecular basis of biological activity.', 5, 5),
    ('Data Structures', 'Organizing and storing data efficiently.', 2, 2);

-- Students
INSERT INTO student (name, email, major, year, semester, group_id) VALUES
    ('Alice Brown', 'alice.brown@university.com', 'Computer Science', 3, 1, 1),
    ('Bob Wilson', 'bob.wilson@university.com', 'Mathematics', 2, 2, 2),
    ('Charlie Green', 'charlie.green@university.com', 'Physics', 1, 1, 3),
    ('Daisy Miller', 'daisy.miller@university.com', 'Biology', 4, 2, 4),
    ('Ethan White', 'ethan.white@university.com', 'Electrical Engineering', 2, 1, 5),
    ('Fiona Black', 'fiona.black@university.com', 'Computer Science', 1, 1, 1);

-- Group Schedules
INSERT INTO group_schedule (group_id, subject_id, room_id, day, start_time, end_time) VALUES
    (1, 2, 1, 'Monday', '09:00', '11:00'),   -- Intro to Programming
    (2, 1, 2, 'Wednesday', '13:00', '15:00'), -- Advanced Calculus
    (3, 3, 2, 'Friday', '10:00', '12:00'),    -- Physics I
    (4, 5, 3, 'Tuesday', '14:00', '16:00'),   -- Molecular Biology
    (5, 4, 4, 'Thursday', '08:00', '10:00'),  -- Digital Systems
    (1, 6, 1, 'Wednesday', '11:00', '13:00'); -- Data Structures

-- Subject Scores
INSERT INTO subject_score (student_id, subject_id, score, semester, year) VALUES
    (1, 2, 85.5, 1, 2023),
    (2, 1, 92.0, 2, 2023),
    (3, 3, 78.0, 1, 2023),
    (4, 5, 88.5, 2, 2023),
    (5, 4, 81.0, 1, 2023),
    (6, 6, 90.0, 1, 2023),
    (1, 6, 87.0, 1, 2023); -- Alice Brown also takes Data Structures
