import sqlite3
from datetime import datetime, date

# Create connection to database
conn = sqlite3.connect('school.db')
cursor = conn.cursor()

# Create tables
tables_sql = [
    """
    CREATE TABLE IF NOT EXISTS departments (
        department_id INTEGER PRIMARY KEY AUTOINCREMENT,
        department_name TEXT NOT NULL,
        department_head TEXT,
        budget REAL,
        created_date DATE
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS teachers (
        teacher_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        email TEXT UNIQUE,
        phone TEXT,
        department_id INTEGER,
        hire_date DATE,
        salary REAL,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS classes (
        class_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_name TEXT NOT NULL,
        grade_level INTEGER,
        teacher_id INTEGER,
        department_id INTEGER,
        max_students INTEGER,
        room_number TEXT,
        schedule_time TEXT,
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id),
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS students (
        student_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        date_of_birth DATE,
        gender TEXT,
        email TEXT UNIQUE,
        phone TEXT,
        address TEXT,
        enrollment_date DATE,
        class_id INTEGER,
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS subjects (
        subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        subject_name TEXT NOT NULL,
        subject_code TEXT UNIQUE,
        credits INTEGER,
        department_id INTEGER,
        description TEXT,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS class_subjects (
        class_subject_id INTEGER PRIMARY KEY AUTOINCREMENT,
        class_id INTEGER,
        subject_id INTEGER,
        teacher_id INTEGER,
        FOREIGN KEY (class_id) REFERENCES classes(class_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (teacher_id) REFERENCES teachers(teacher_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS grades (
        grade_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        subject_id INTEGER,
        class_id INTEGER,
        exam_type TEXT,
        score REAL,
        grade_letter TEXT,
        date_recorded DATE,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS attendance (
        attendance_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        class_id INTEGER,
        date DATE,
        status TEXT,
        remarks TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS parents (
        parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        first_name TEXT NOT NULL,
        last_name TEXT NOT NULL,
        relationship TEXT,
        phone TEXT,
        email TEXT,
        address TEXT,
        occupation TEXT
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS student_parents (
        student_parent_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        parent_id INTEGER,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (parent_id) REFERENCES parents(parent_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS exams (
        exam_id INTEGER PRIMARY KEY AUTOINCREMENT,
        exam_name TEXT NOT NULL,
        subject_id INTEGER,
        class_id INTEGER,
        exam_date DATE,
        duration INTEGER,
        max_marks REAL,
        exam_type TEXT,
        FOREIGN KEY (subject_id) REFERENCES subjects(subject_id),
        FOREIGN KEY (class_id) REFERENCES classes(class_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS fees (
        fee_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        fee_type TEXT,
        amount REAL,
        due_date DATE,
        paid_date DATE,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS events (
        event_id INTEGER PRIMARY KEY AUTOINCREMENT,
        event_name TEXT NOT NULL,
        event_date DATE,
        event_time TEXT,
        location TEXT,
        organizer TEXT,
        description TEXT,
        department_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS library (
        book_id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        author TEXT,
        isbn TEXT UNIQUE,
        publication_year INTEGER,
        genre TEXT,
        available_copies INTEGER,
        total_copies INTEGER,
        department_id INTEGER,
        FOREIGN KEY (department_id) REFERENCES departments(department_id)
    )
    """,
    
    """
    CREATE TABLE IF NOT EXISTS student_books (
        borrow_id INTEGER PRIMARY KEY AUTOINCREMENT,
        student_id INTEGER,
        book_id INTEGER,
        borrow_date DATE,
        due_date DATE,
        return_date DATE,
        status TEXT,
        FOREIGN KEY (student_id) REFERENCES students(student_id),
        FOREIGN KEY (book_id) REFERENCES library(book_id)
    )
    """
]

# Execute table creation
for sql in tables_sql:
    cursor.execute(sql)

# Insert sample data into departments
departments_data = [
    ('Mathematics', 'Dr. Sarah Johnson', 50000.00, '2020-09-01'),
    ('Science', 'Dr. Michael Chen', 75000.00, '2020-09-01'),
    ('English', 'Dr. Emily Davis', 45000.00, '2020-09-01'),
    ('History', 'Dr. Robert Wilson', 40000.00, '2020-09-01'),
    ('Computer Science', 'Dr. Lisa Anderson', 60000.00, '2020-09-01'),
    ('Arts', 'Dr. James Parker', 35000.00, '2020-09-01'),
    ('Physical Education', 'Dr. Maria Rodriguez', 30000.00, '2020-09-01'),
    ('Foreign Languages', 'Dr. Thomas Kim', 42000.00, '2020-09-01')
]

cursor.executemany('''
    INSERT INTO departments (department_name, department_head, budget, created_date) 
    VALUES (?, ?, ?, ?)
''', departments_data)

# Insert sample data into teachers
teachers_data = [
    ('John', 'Smith', 'john.smith@school.edu', '555-0101', 1, '2021-08-15', 55000.00),
    ('Maria', 'Garcia', 'maria.garcia@school.edu', '555-0102', 2, '2020-08-20', 58000.00),
    ('David', 'Brown', 'david.brown@school.edu', '555-0103', 3, '2019-08-25', 52000.00),
    ('Lisa', 'Wilson', 'lisa.wilson@school.edu', '555-0104', 4, '2021-08-10', 54000.00),
    ('Robert', 'Taylor', 'robert.taylor@school.edu', '555-0105', 5, '2022-08-12', 60000.00),
    ('Jennifer', 'Anderson', 'jennifer.anderson@school.edu', '555-0106', 6, '2020-08-18', 48000.00),
    ('Michael', 'Thomas', 'michael.thomas@school.edu', '555-0107', 7, '2018-08-30', 45000.00),
    ('Sarah', 'Jackson', 'sarah.jackson@school.edu', '555-0108', 8, '2021-08-22', 50000.00),
    ('Kevin', 'White', 'kevin.white@school.edu', '555-0109', 1, '2022-08-15', 53000.00),
    ('Amanda', 'Harris', 'amanda.harris@school.edu', '555-0110', 2, '2019-08-28', 56000.00)
]

cursor.executemany('''
    INSERT INTO teachers (first_name, last_name, email, phone, department_id, hire_date, salary) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', teachers_data)

# Insert sample data into classes
classes_data = [
    ('Grade 9A', 9, 1, 1, 30, 'R101', '08:00-09:00'),
    ('Grade 9B', 9, 9, 1, 30, 'R102', '09:00-10:00'),
    ('Grade 10A', 10, 2, 2, 28, 'R201', '10:00-11:00'),
    ('Grade 10B', 10, 10, 2, 28, 'R202', '11:00-12:00'),
    ('Grade 11A', 11, 3, 3, 25, 'R301', '13:00-14:00'),
    ('Grade 11B', 11, 4, 4, 25, 'R302', '14:00-15:00'),
    ('Grade 12A', 12, 5, 5, 22, 'R401', '15:00-16:00'),
    ('Grade 12B', 12, 6, 6, 22, 'R402', '16:00-17:00'),
    ('PE Class', 9, 7, 7, 40, 'Gym', '07:00-08:00'),
    ('French 101', 10, 8, 8, 20, 'R501', '12:00-13:00')
]

cursor.executemany('''
    INSERT INTO classes (class_name, grade_level, teacher_id, department_id, max_students, room_number, schedule_time) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', classes_data)

# Insert sample data into students
students_data = [
    ('Emma', 'Johnson', '2007-03-15', 'Female', 'emma.johnson@student.school.edu', '555-0201', '123 Main St', '2023-09-01', 1),
    ('Noah', 'Smith', '2007-07-22', 'Male', 'noah.smith@student.school.edu', '555-0202', '456 Oak Ave', '2023-09-01', 1),
    ('Olivia', 'Williams', '2007-11-08', 'Female', 'olivia.williams@student.school.edu', '555-0203', '789 Pine Rd', '2023-09-01', 1),
    ('Liam', 'Brown', '2007-01-30', 'Male', 'liam.brown@student.school.edu', '555-0204', '321 Elm St', '2023-09-01', 2),
    ('Ava', 'Jones', '2007-05-12', 'Female', 'ava.jones@student.school.edu', '555-0205', '654 Maple Dr', '2023-09-01', 2),
    ('Lucas', 'Garcia', '2007-09-25', 'Male', 'lucas.garcia@student.school.edu', '555-0206', '987 Cedar Ln', '2023-09-01', 3),
    ('Mia', 'Miller', '2007-12-03', 'Female', 'mia.miller@student.school.edu', '555-0207', '147 Birch St', '2023-09-01', 3),
    ('Ethan', 'Davis', '2007-04-18', 'Male', 'ethan.davis@student.school.edu', '555-0208', '258 Spruce Ave', '2023-09-01', 4),
    ('Isabella', 'Rodriguez', '2007-08-30', 'Female', 'isabella.rodriguez@student.school.edu', '555-0209', '369 Willow Dr', '2023-09-01', 4),
    ('James', 'Martinez', '2007-02-14', 'Male', 'james.martinez@student.school.edu', '555-0210', '741 Poplar Rd', '2023-09-01', 5)
]

cursor.executemany('''
    INSERT INTO students (first_name, last_name, date_of_birth, gender, email, phone, address, enrollment_date, class_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
''', students_data)

# Insert sample data into subjects
subjects_data = [
    ('Algebra', 'MATH101', 3, 1, 'Basic algebra concepts'),
    ('Geometry', 'MATH102', 3, 1, 'Geometric principles and theorems'),
    ('Biology', 'SCI101', 4, 2, 'Introduction to biological sciences'),
    ('Chemistry', 'SCI102', 4, 2, 'Basic chemical principles'),
    ('English Literature', 'ENG101', 3, 3, 'Study of classic literature'),
    ('Creative Writing', 'ENG102', 2, 3, 'Developing writing skills'),
    ('World History', 'HIST101', 3, 4, 'Global historical events'),
    ('Programming Fundamentals', 'CS101', 4, 5, 'Introduction to programming'),
    ('Digital Art', 'ART101', 2, 6, 'Digital art creation techniques'),
    ('Physical Fitness', 'PE101', 1, 7, 'Physical fitness and health')
]

cursor.executemany('''
    INSERT INTO subjects (subject_name, subject_code, credits, department_id, description) 
    VALUES (?, ?, ?, ?, ?)
''', subjects_data)

# Insert sample data into class_subjects
class_subjects_data = [
    (1, 1, 1), (1, 2, 1), (2, 1, 9), (2, 2, 9),
    (3, 3, 2), (3, 4, 2), (4, 3, 10), (4, 4, 10),
    (5, 5, 3), (5, 6, 3), (6, 7, 4), (6, 5, 3),
    (7, 8, 5), (7, 5, 3), (8, 9, 6), (8, 6, 3),
    (9, 10, 7), (10, 5, 8)
]

cursor.executemany('''
    INSERT INTO class_subjects (class_id, subject_id, teacher_id) 
    VALUES (?, ?, ?)
''', class_subjects_data)

# Insert sample data into grades
grades_data = [
    (1, 1, 1, 'Midterm', 85.5, 'B', '2023-10-15'),
    (1, 2, 1, 'Midterm', 92.0, 'A-', '2023-10-16'),
    (2, 1, 1, 'Midterm', 78.0, 'C+', '2023-10-15'),
    (2, 2, 1, 'Midterm', 88.5, 'B+', '2023-10-16'),
    (3, 3, 2, 'Midterm', 91.0, 'A-', '2023-10-17'),
    (3, 4, 2, 'Midterm', 87.5, 'B+', '2023-10-18'),
    (4, 3, 2, 'Midterm', 76.0, 'C+', '2023-10-17'),
    (4, 4, 2, 'Midterm', 82.5, 'B-', '2023-10-18'),
    (5, 5, 3, 'Midterm', 89.0, 'B+', '2023-10-19'),
    (5, 6, 3, 'Midterm', 94.0, 'A', '2023-10-20')
]

cursor.executemany('''
    INSERT INTO grades (student_id, subject_id, class_id, exam_type, score, grade_letter, date_recorded) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', grades_data)

# Insert sample data into attendance
attendance_data = [
    (1, 1, '2023-10-01', 'Present', 'Good'),
    (2, 1, '2023-10-01', 'Present', 'Good'),
    (3, 1, '2023-10-01', 'Absent', 'Sick'),
    (4, 2, '2023-10-01', 'Present', 'Good'),
    (5, 2, '2023-10-01', 'Late', '15 minutes late'),
    (6, 3, '2023-10-01', 'Present', 'Good'),
    (7, 3, '2023-10-01', 'Present', 'Good'),
    (8, 4, '2023-10-01', 'Absent', 'Family emergency'),
    (9, 4, '2023-10-01', 'Present', 'Good'),
    (10, 5, '2023-10-01', 'Present', 'Good')
]

cursor.executemany('''
    INSERT INTO attendance (student_id, class_id, date, status, remarks) 
    VALUES (?, ?, ?, ?, ?)
''', attendance_data)

# Insert sample data into parents
parents_data = [
    ('Robert', 'Johnson', 'Father', '555-0301', 'robert.johnson@email.com', '123 Main St', 'Engineer'),
    ('Jennifer', 'Johnson', 'Mother', '555-0302', 'jennifer.johnson@email.com', '123 Main St', 'Teacher'),
    ('Michael', 'Smith', 'Father', '555-0303', 'michael.smith@email.com', '456 Oak Ave', 'Doctor'),
    ('Sarah', 'Smith', 'Mother', '555-0304', 'sarah.smith@email.com', '456 Oak Ave', 'Nurse'),
    ('David', 'Williams', 'Father', '555-0305', 'david.williams@email.com', '789 Pine Rd', 'Lawyer'),
    ('Lisa', 'Brown', 'Mother', '555-0306', 'lisa.brown@email.com', '321 Elm St', 'Accountant'),
    ('Carlos', 'Garcia', 'Father', '555-0307', 'carlos.garcia@email.com', '987 Cedar Ln', 'Chef'),
    ('Maria', 'Garcia', 'Mother', '555-0308', 'maria.garcia@email.com', '987 Cedar Ln', 'Artist'),
    ('Thomas', 'Miller', 'Father', '555-0309', 'thomas.miller@email.com', '147 Birch St', 'Architect'),
    ('Anna', 'Miller', 'Mother', '555-0310', 'anna.miller@email.com', '147 Birch St', 'Designer')
]

cursor.executemany('''
    INSERT INTO parents (first_name, last_name, relationship, phone, email, address, occupation) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', parents_data)

# Insert sample data into student_parents
student_parents_data = [
    (1, 1), (1, 2), (2, 3), (2, 4), (3, 5),
    (4, 6), (5, 7), (6, 8), (7, 9), (8, 10)
]

cursor.executemany('''
    INSERT INTO student_parents (student_id, parent_id) 
    VALUES (?, ?)
''', student_parents_data)

# Insert sample data into exams
exams_data = [
    ('Algebra Midterm', 1, 1, '2023-10-15', 90, 100.0, 'Midterm'),
    ('Geometry Midterm', 2, 1, '2023-10-16', 90, 100.0, 'Midterm'),
    ('Biology Midterm', 3, 3, '2023-10-17', 90, 100.0, 'Midterm'),
    ('Chemistry Midterm', 4, 3, '2023-10-18', 90, 100.0, 'Midterm'),
    ('English Literature Midterm', 5, 5, '2023-10-19', 90, 100.0, 'Midterm'),
    ('World History Midterm', 7, 6, '2023-10-20', 90, 100.0, 'Midterm'),
    ('Programming Final', 8, 7, '2023-12-15', 120, 100.0, 'Final'),
    ('Digital Art Project', 9, 8, '2023-12-16', 180, 100.0, 'Project'),
    ('Physical Fitness Test', 10, 9, '2023-12-17', 60, 100.0, 'Test'),
    ('French Oral Exam', 5, 10, '2023-12-18', 45, 100.0, 'Oral')
]

cursor.executemany('''
    INSERT INTO exams (exam_name, subject_id, class_id, exam_date, duration, max_marks, exam_type) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', exams_data)

# Insert sample data into fees
fees_data = [
    (1, 'Tuition', 5000.00, '2023-09-01', '2023-08-15', 'Paid'),
    (2, 'Tuition', 5000.00, '2023-09-01', '2023-08-20', 'Paid'),
    (3, 'Tuition', 5000.00, '2023-09-01', None, 'Pending'),
    (4, 'Tuition', 5000.00, '2023-09-01', '2023-08-25', 'Paid'),
    (5, 'Tuition', 5000.00, '2023-09-01', None, 'Pending'),
    (6, 'Tuition', 5000.00, '2023-09-01', '2023-08-30', 'Paid'),
    (7, 'Tuition', 5000.00, '2023-09-01', None, 'Pending'),
    (8, 'Tuition', 5000.00, '2023-09-01', '2023-09-01', 'Paid'),
    (9, 'Tuition', 5000.00, '2023-09-01', None, 'Pending'),
    (10, 'Tuition', 5000.00, '2023-09-01', '2023-08-28', 'Paid')
]

cursor.executemany('''
    INSERT INTO fees (student_id, fee_type, amount, due_date, paid_date, status) 
    VALUES (?, ?, ?, ?, ?, ?)
''', fees_data)

# Insert sample data into events
events_data = [
    ('Science Fair', '2023-11-15', '10:00', 'Main Hall', 'Dr. Michael Chen', 'Annual science exhibition', 2),
    ('Literary Festival', '2023-12-01', '09:00', 'Library', 'Dr. Emily Davis', 'Poetry and book reading', 3),
    ('Sports Day', '2023-10-25', '08:00', 'Playground', 'Dr. Maria Rodriguez', 'Inter-class sports competition', 7),
    ('Art Exhibition', '2023-11-30', '14:00', 'Art Room', 'Dr. James Parker', 'Student artwork display', 6),
    ('Parent-Teacher Meeting', '2023-10-20', '16:00', 'Classrooms', 'Principal', 'Regular parent-teacher conference', 1),
    ('Career Counseling', '2023-11-10', '13:00', 'Counseling Room', 'Career Advisor', 'Guidance for Grade 12 students', 5),
    ('Mathematics Olympiad', '2023-12-05', '09:00', 'Math Lab', 'Dr. Sarah Johnson', 'Inter-school math competition', 1),
    ('Cultural Program', '2023-12-20', '18:00', 'Auditorium', 'Dr. Thomas Kim', 'Annual cultural celebration', 8),
    ('Graduation Ceremony', '2024-06-15', '10:00', 'Auditorium', 'Principal', 'Grade 12 graduation', 1),
    ('Science Workshop', '2023-11-20', '11:00', 'Science Lab', 'Dr. Michael Chen', 'Hands-on science experiments', 2)
]

cursor.executemany('''
    INSERT INTO events (event_name, event_date, event_time, location, organizer, description, department_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?)
''', events_data)

# Insert sample data into library
library_data = [
    ('To Kill a Mockingbird', 'Harper Lee', '978-0-06-112008-4', 1960, 'Fiction', 3, 5, 3),
    ('The Great Gatsby', 'F. Scott Fitzgerald', '978-0-7432-7356-5', 1925, 'Fiction', 2, 4, 3),
    ('1984', 'George Orwell', '978-0-452-28423-4', 1949, 'Dystopian', 4, 6, 3),
    ('Pride and Prejudice', 'Jane Austen', '978-0-14-143951-8', 1813, 'Romance', 3, 5, 3),
    ('The Catcher in the Rye', 'J.D. Salinger', '978-0-316-76948-0', 1951, 'Fiction', 2, 3, 3),
    ('Lord of the Flies', 'William Golding', '978-0-571-05686-2', 1954, 'Fiction', 3, 4, 3),
    ('Animal Farm', 'George Orwell', '978-0-452-28424-1', 1945, 'Political Satire', 5, 7, 3),
    ('Brave New World', 'Aldous Huxley', '978-0-06-085052-4', 1932, 'Dystopian', 2, 3, 3),
    ('Of Mice and Men', 'John Steinbeck', '978-0-14-017739-8', 1937, 'Fiction', 4, 5, 3),
    ('The Lord of the Rings', 'J.R.R. Tolkien', '978-0-544-00341-5', 1954, 'Fantasy', 1, 3, 3)
]

cursor.executemany('''
    INSERT INTO library (title, author, isbn, publication_year, genre, available_copies, total_copies, department_id) 
    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
''', library_data)

# Insert sample data into student_books
student_books_data = [
    (1, 1, '2023-10-01', '2023-10-29', None, 'Borrowed'),
    (2, 2, '2023-10-02', '2023-10-30', '2023-10-15', 'Returned'),
    (3, 3, '2023-10-03', '2023-10-31', None, 'Borrowed'),
    (4, 4, '2023-10-04', '2023-11-01', None, 'Borrowed'),
    (5, 5, '2023-10-05', '2023-11-02', '2023-10-20', 'Returned'),
    (6, 6, '2023-10-06', '2023-11-03', None, 'Borrowed'),
    (7, 7, '2023-10-07', '2023-11-04', None, 'Borrowed'),
    (8, 8, '2023-10-08', '2023-11-05', '2023-10-25', 'Returned'),
    (9, 9, '2023-10-09', '2023-11-06', None, 'Borrowed'),
    (10, 10, '2023-10-10', '2023-11-07', None, 'Borrowed')
]

cursor.executemany('''
    INSERT INTO student_books (student_id, book_id, borrow_date, due_date, return_date, status) 
    VALUES (?, ?, ?, ?, ?, ?)
''', student_books_data)

# Commit changes and close connection
conn.commit()
conn.close()

print("School database created successfully with 15 tables and sample data!")