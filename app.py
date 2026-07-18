"""
app.py
Flask web application for the Student Database Management System.
Reuses the same crud.py logic as the CLI version.
"""

import os
from functools import wraps
from flask import Flask, render_template, request, redirect, url_for, flash, session
from werkzeug.security import generate_password_hash, check_password_hash
import crud

app = Flask(__name__)
app.secret_key = os.environ.get("SECRET_KEY", "dev-secret-change-in-production")

# ---------------------------------------------------------------
# ADMIN LOGIN
# ---------------------------------------------------------------
# Change these via environment variables when deploying.
ADMIN_USERNAME = os.environ.get("ADMIN_USERNAME", "admin")
ADMIN_PASSWORD_HASH = generate_password_hash(os.environ.get("ADMIN_PASSWORD", "admin123"))


def login_required(view):
    @wraps(view)
    def wrapped(*args, **kwargs):
        if not session.get("logged_in"):
            return redirect(url_for("login", next=request.path))
        return view(*args, **kwargs)
    return wrapped


@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        username = request.form.get("username", "").strip()
        password = request.form.get("password", "")
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD_HASH, password):
            session["logged_in"] = True
            session["username"] = username
            flash("Welcome back!", "success")
            next_url = request.args.get("next") or url_for("dashboard")
            return redirect(next_url)
        flash("Invalid username or password.", "error")
    return render_template("login.html")


@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out.", "success")
    return redirect(url_for("login"))


# ---------------------------------------------------------------
# DASHBOARD
# ---------------------------------------------------------------

@app.route("/dashboard")
@login_required
def dashboard():
    stats = {
        "total_students": crud.count_students(),
        "total_courses": crud.count_courses(),
        "total_enrollments": crud.count_enrollments(),
        "by_department": crud.students_by_department(),
        "by_gender": crud.students_by_gender(),
    }
    return render_template("dashboard.html", stats=stats)


# ---------------------------------------------------------------
# DASHBOARD / STUDENTS
# ---------------------------------------------------------------

@app.route("/")
@login_required
def index():
    search = request.args.get("q", "").strip()
    if search:
        students = crud.search_students_by_name(search)
    else:
        students = crud.get_all_students()
    return render_template("index.html", students=students, search=search)


@app.route("/students/add", methods=["GET", "POST"])
@login_required
def add_student():
    departments = crud.get_all_departments()
    if request.method == "POST":
        name = request.form.get("name", "").strip()
        dob = request.form.get("dob") or None
        gender = request.form.get("gender") or None
        email = request.form.get("email", "").strip()
        phone = request.form.get("phone", "").strip()
        dept_id = request.form.get("dept_id") or None

        if not name:
            flash("Name is required.", "error")
            return render_template("student_form.html", departments=departments, student=None)

        crud.create_student(name, dob, gender, email, phone, dept_id)
        flash(f"Student '{name}' added.", "success")
        return redirect(url_for("index"))

    return render_template("student_form.html", departments=departments, student=None)


@app.route("/students/<int:student_id>")
@login_required
def view_student(student_id):
    student = crud.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))
    enrollments = crud.get_enrollments_for_student(student_id)
    attendance_summary = crud.get_attendance_summary_for_student(student_id)
    return render_template("student_detail.html", student=student, enrollments=enrollments, attendance_summary=attendance_summary)


@app.route("/students/<int:student_id>/edit", methods=["GET", "POST"])
@login_required
def edit_student(student_id):
    student = crud.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    departments = crud.get_all_departments()

    if request.method == "POST":
        name = request.form.get("name", "").strip() or None
        dob = request.form.get("dob") or None
        gender = request.form.get("gender") or None
        email = request.form.get("email", "").strip() or None
        phone = request.form.get("phone", "").strip() or None
        dept_id = request.form.get("dept_id") or None

        crud.update_student(student_id, name, dob, gender, email, phone, dept_id)
        flash("Student updated.", "success")
        return redirect(url_for("view_student", student_id=student_id))

    return render_template("student_form.html", departments=departments, student=student)


@app.route("/students/<int:student_id>/delete", methods=["POST"])
@login_required
def delete_student(student_id):
    crud.delete_student(student_id)
    flash("Student deleted.", "success")
    return redirect(url_for("index"))


# ---------------------------------------------------------------
# ATTENDANCE
# ---------------------------------------------------------------

@app.route("/attendance")
@login_required
def attendance_home():
    all_courses = crud.get_all_courses()
    course_id = request.args.get("course_id")
    date = request.args.get("date")
    roster = None
    existing = {}

    if course_id and date:
        roster = crud.get_enrolled_students_for_course(course_id)
        existing = crud.get_attendance_for_course_date(course_id, date)

    return render_template(
        "attendance.html",
        courses=all_courses,
        course_id=course_id,
        date=date,
        roster=roster,
        existing=existing,
    )


@app.route("/attendance/save", methods=["POST"])
@login_required
def save_attendance_route():
    course_id = request.form.get("course_id")
    date = request.form.get("date")
    student_ids = request.form.getlist("student_id")

    records = []
    for sid in student_ids:
        status = request.form.get(f"status_{sid}", "Present")
        records.append((sid, status))

    crud.save_attendance(course_id, date, records)
    flash(f"Attendance saved for {len(records)} student(s).", "success")
    return redirect(url_for("attendance_home", course_id=course_id, date=date))


# ---------------------------------------------------------------
# COURSES / ENROLLMENTS
# ---------------------------------------------------------------

@app.route("/courses")
@login_required
def courses():
    all_courses = crud.get_all_courses()
    return render_template("courses.html", courses=all_courses)


@app.route("/students/<int:student_id>/enroll", methods=["GET", "POST"])
@login_required
def enroll(student_id):
    student = crud.get_student_by_id(student_id)
    if not student:
        flash("Student not found.", "error")
        return redirect(url_for("index"))

    all_courses = crud.get_all_courses()

    if request.method == "POST":
        course_id = request.form.get("course_id")
        semester = request.form.get("semester", "").strip()
        crud.enroll_student(student_id, course_id, semester)
        flash("Enrollment added.", "success")
        return redirect(url_for("view_student", student_id=student_id))

    return render_template("enroll_form.html", student=student, courses=all_courses)


@app.route("/enrollments/<int:enrollment_id>/grade", methods=["POST"])
@login_required
def update_grade(enrollment_id):
    grade = request.form.get("grade", "").strip()
    student_id = request.form.get("student_id")
    crud.update_grade(enrollment_id, grade)
    flash("Grade updated.", "success")
    return redirect(url_for("view_student", student_id=student_id))


@app.route("/enrollments/<int:enrollment_id>/delete", methods=["POST"])
@login_required
def delete_enrollment(enrollment_id):
    student_id = request.form.get("student_id")
    crud.delete_enrollment(enrollment_id)
    flash("Enrollment removed.", "success")
    return redirect(url_for("view_student", student_id=student_id))


if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=True)
