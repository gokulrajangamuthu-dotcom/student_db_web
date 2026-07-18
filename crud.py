"""
crud.py
All Create, Read, Update, Delete operations for the
Student Database Management System.
"""

from mysql.connector import Error
from db import get_connection


# ---------------------------------------------------------------
# STUDENT CRUD
# ---------------------------------------------------------------

def create_student(name, dob, gender, email, phone, dept_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO students (name, dob, gender, email, phone, dept_id)
            VALUES (%s, %s, %s, %s, %s, %s)
        """
        cursor.execute(query, (name, dob, gender, email, phone, dept_id))
        conn.commit()
        print(f"[OK] Student '{name}' added with ID {cursor.lastrowid}.")
    except Error as e:
        print(f"[ERROR] Could not add student: {e}")
    finally:
        cursor.close()
        conn.close()


def get_all_students():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.student_id, s.name, s.dob, s.gender, s.email, s.phone,
                   d.dept_name
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            ORDER BY s.student_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"[ERROR] Could not fetch students: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def get_student_by_id(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.student_id, s.name, s.dob, s.gender, s.email, s.phone,
                   d.dept_name, s.dept_id
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            WHERE s.student_id = %s
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchone()
    except Error as e:
        print(f"[ERROR] Could not fetch student: {e}")
        return None
    finally:
        cursor.close()
        conn.close()


def update_student(student_id, name=None, dob=None, gender=None, email=None, phone=None, dept_id=None):
    """
    Only updates fields that are provided (not None).
    """
    fields = []
    values = []

    if name is not None:
        fields.append("name = %s")
        values.append(name)
    if dob is not None:
        fields.append("dob = %s")
        values.append(dob)
    if gender is not None:
        fields.append("gender = %s")
        values.append(gender)
    if email is not None:
        fields.append("email = %s")
        values.append(email)
    if phone is not None:
        fields.append("phone = %s")
        values.append(phone)
    if dept_id is not None:
        fields.append("dept_id = %s")
        values.append(dept_id)

    if not fields:
        print("[INFO] Nothing to update.")
        return

    values.append(student_id)
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = f"UPDATE students SET {', '.join(fields)} WHERE student_id = %s"
        cursor.execute(query, tuple(values))
        conn.commit()
        if cursor.rowcount:
            print(f"[OK] Student ID {student_id} updated.")
        else:
            print(f"[INFO] No student found with ID {student_id}.")
    except Error as e:
        print(f"[ERROR] Could not update student: {e}")
    finally:
        cursor.close()
        conn.close()


def delete_student(student_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM students WHERE student_id = %s", (student_id,))
        conn.commit()
        if cursor.rowcount:
            print(f"[OK] Student ID {student_id} deleted.")
        else:
            print(f"[INFO] No student found with ID {student_id}.")
    except Error as e:
        print(f"[ERROR] Could not delete student: {e}")
    finally:
        cursor.close()
        conn.close()


def search_students_by_name(keyword):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT s.student_id, s.name, s.email, d.dept_name
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            WHERE s.name LIKE %s
        """
        cursor.execute(query, (f"%{keyword}%",))
        return cursor.fetchall()
    except Error as e:
        print(f"[ERROR] Could not search students: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# ATTENDANCE
# ---------------------------------------------------------------

def get_enrolled_students_for_course(course_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT DISTINCT s.student_id, s.name
            FROM students s
            JOIN enrollments e ON s.student_id = e.student_id
            WHERE e.course_id = %s
            ORDER BY s.name
        """
        cursor.execute(query, (course_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_attendance_for_course_date(course_id, attendance_date):
    """Returns a dict: {student_id: status} for a given course + date."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT student_id, status FROM attendance
            WHERE course_id = %s AND attendance_date = %s
        """
        cursor.execute(query, (course_id, attendance_date))
        rows = cursor.fetchall()
        return {str(r["student_id"]): r["status"] for r in rows}
    finally:
        cursor.close()
        conn.close()


def save_attendance(course_id, attendance_date, records):
    """
    records: list of (student_id, status) tuples.
    Inserts new attendance rows, or updates status if that
    student/course/date combination already exists.
    """
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO attendance (student_id, course_id, attendance_date, status)
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE status = VALUES(status)
        """
        for student_id, status in records:
            cursor.execute(query, (student_id, course_id, attendance_date, status))
        conn.commit()
        print(f"[OK] Attendance saved for {len(records)} student(s).")
    except Error as e:
        print(f"[ERROR] Could not save attendance: {e}")
    finally:
        cursor.close()
        conn.close()


def get_attendance_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT a.attendance_id, c.course_name, a.attendance_date, a.status
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = %s
            ORDER BY a.attendance_date DESC
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def get_attendance_summary_for_student(student_id):
    """Per-course totals + present count, used to compute attendance %."""
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT c.course_name,
                   COUNT(*) AS total_classes,
                   SUM(CASE WHEN a.status = 'Present' THEN 1 ELSE 0 END) AS present_count
            FROM attendance a
            JOIN courses c ON a.course_id = c.course_id
            WHERE a.student_id = %s
            GROUP BY c.course_name
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# DASHBOARD STATS
# ---------------------------------------------------------------

def count_students():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM students")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def count_courses():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM courses")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def count_enrollments():
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("SELECT COUNT(*) FROM enrollments")
        return cursor.fetchone()[0]
    finally:
        cursor.close()
        conn.close()


def students_by_department():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT COALESCE(d.dept_name, 'Unassigned') AS dept_name, COUNT(s.student_id) AS total
            FROM students s
            LEFT JOIN departments d ON s.dept_id = d.dept_id
            GROUP BY d.dept_name
            ORDER BY total DESC
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


def students_by_gender():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT COALESCE(gender, 'Not specified') AS gender, COUNT(*) AS total
            FROM students
            GROUP BY gender
        """
        cursor.execute(query)
        return cursor.fetchall()
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# DEPARTMENT (lookup/support)
# ---------------------------------------------------------------

def get_all_departments():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        cursor.execute("SELECT * FROM departments ORDER BY dept_id")
        return cursor.fetchall()
    except Error as e:
        print(f"[ERROR] Could not fetch departments: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# COURSE (lookup/support)
# ---------------------------------------------------------------

def get_all_courses():
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT c.course_id, c.course_name, c.credits, d.dept_name
            FROM courses c
            LEFT JOIN departments d ON c.dept_id = d.dept_id
            ORDER BY c.course_id
        """
        cursor.execute(query)
        return cursor.fetchall()
    except Error as e:
        print(f"[ERROR] Could not fetch courses: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


# ---------------------------------------------------------------
# ENROLLMENT CRUD
# ---------------------------------------------------------------

def enroll_student(student_id, course_id, semester, grade=None):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        query = """
            INSERT INTO enrollments (student_id, course_id, semester, grade)
            VALUES (%s, %s, %s, %s)
        """
        cursor.execute(query, (student_id, course_id, semester, grade))
        conn.commit()
        print(f"[OK] Enrollment created (ID {cursor.lastrowid}).")
    except Error as e:
        print(f"[ERROR] Could not enroll student: {e}")
    finally:
        cursor.close()
        conn.close()


def get_enrollments_for_student(student_id):
    conn = get_connection()
    cursor = conn.cursor(dictionary=True)
    try:
        query = """
            SELECT e.enrollment_id, c.course_name, e.semester, e.grade
            FROM enrollments e
            JOIN courses c ON e.course_id = c.course_id
            WHERE e.student_id = %s
        """
        cursor.execute(query, (student_id,))
        return cursor.fetchall()
    except Error as e:
        print(f"[ERROR] Could not fetch enrollments: {e}")
        return []
    finally:
        cursor.close()
        conn.close()


def update_grade(enrollment_id, grade):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute(
            "UPDATE enrollments SET grade = %s WHERE enrollment_id = %s",
            (grade, enrollment_id)
        )
        conn.commit()
        if cursor.rowcount:
            print(f"[OK] Grade updated for enrollment ID {enrollment_id}.")
        else:
            print(f"[INFO] No enrollment found with ID {enrollment_id}.")
    except Error as e:
        print(f"[ERROR] Could not update grade: {e}")
    finally:
        cursor.close()
        conn.close()


def delete_enrollment(enrollment_id):
    conn = get_connection()
    cursor = conn.cursor()
    try:
        cursor.execute("DELETE FROM enrollments WHERE enrollment_id = %s", (enrollment_id,))
        conn.commit()
        if cursor.rowcount:
            print(f"[OK] Enrollment ID {enrollment_id} deleted.")
        else:
            print(f"[INFO] No enrollment found with ID {enrollment_id}.")
    except Error as e:
        print(f"[ERROR] Could not delete enrollment: {e}")
    finally:
        cursor.close()
        conn.close()
