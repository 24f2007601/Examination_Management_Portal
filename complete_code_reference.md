# Examination Management Portal — Complete Code Reference

All files listed in order. Study each one, then code it yourself.

---

## 1. `requirements.txt`

```txt
Flask==3.0.3
Flask-SQLAlchemy==3.1.1
Flask-Login==0.6.3
Werkzeug==3.0.4
```

---

## 2. `config.py`

```python
import os


class Config:
    """Application configuration loaded from environment variables with safe defaults."""

    SECRET_KEY = os.environ.get('SECRET_KEY', 'change-this-in-production')
    SQLALCHEMY_DATABASE_URI = os.environ.get(
        'DATABASE_URL', 'sqlite:///examination_portal.db'
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
```

---

## 3. `models.py`

```python
from datetime import datetime, date, time

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# ──────────────────────────────────────────────
# USER
# ──────────────────────────────────────────────
class User(UserMixin, db.Model):
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False, default='student')
    contact_details = db.Column(db.String(255))
    department = db.Column(db.String(120))
    is_active = db.Column(db.Boolean, default=True, nullable=False)
    is_approved = db.Column(db.Boolean, default=False, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    # Relationships
    slots = db.relationship('ExaminationSlot', backref='examiner', lazy=True,
                            foreign_keys='ExaminationSlot.examiner_id')
    bookings = db.relationship('Booking', backref='student', lazy=True,
                               foreign_keys='Booking.student_id')
    assignments = db.relationship('ExaminerAssignment', backref='examiner', lazy=True)

    def set_password(self, password):
        self.password_hash = generate_password_hash(password)

    def check_password(self, password):
        return check_password_hash(self.password_hash, password)


# ──────────────────────────────────────────────
# COURSE
# ──────────────────────────────────────────────
class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    examinations = db.relationship('Examination', backref='course', lazy=True)


# ──────────────────────────────────────────────
# EXAMINATION
# ──────────────────────────────────────────────
class Examination(db.Model):
    __tablename__ = 'examinations'

    id = db.Column(db.Integer, primary_key=True)
    course_id = db.Column(db.Integer, db.ForeignKey('courses.id'), nullable=False)
    exam_name = db.Column(db.String(200), nullable=False)
    exam_type = db.Column(db.String(50), nullable=False)  # viva, practical, project_demo, assessment
    duration_minutes = db.Column(db.Integer, nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)

    slot_creation_start = db.Column(db.DateTime, nullable=False)
    slot_creation_end = db.Column(db.DateTime, nullable=False)
    slot_booking_start = db.Column(db.DateTime, nullable=False)
    slot_booking_end = db.Column(db.DateTime, nullable=False)

    status = db.Column(db.String(20), default='draft', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    rubrics = db.relationship('Rubric', backref='examination', lazy=True,
                              cascade='all, delete-orphan')
    slots = db.relationship('ExaminationSlot', backref='examination', lazy=True,
                            cascade='all, delete-orphan')
    assignments = db.relationship('ExaminerAssignment', backref='examination', lazy=True,
                                  cascade='all, delete-orphan')

    def is_slot_creation_open(self):
        now = datetime.utcnow()
        return (self.status == 'slot_creation'
                and self.slot_creation_start <= now <= self.slot_creation_end)

    def is_booking_open(self):
        now = datetime.utcnow()
        return (self.status == 'booking_open'
                and self.slot_booking_start <= now <= self.slot_booking_end)


# ──────────────────────────────────────────────
# RUBRIC
# ──────────────────────────────────────────────
class Rubric(db.Model):
    __tablename__ = 'rubrics'

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    criterion_name = db.Column(db.String(200), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float, default=1.0, nullable=False)
    description = db.Column(db.Text)

    evaluations = db.relationship('Evaluation', backref='rubric', lazy=True)


# ──────────────────────────────────────────────
# EXAMINATION SLOT
# ──────────────────────────────────────────────
class ExaminationSlot(db.Model):
    __tablename__ = 'examination_slots'

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.Date, nullable=False)
    start_time = db.Column(db.Time, nullable=False)
    end_time = db.Column(db.Time, nullable=False)
    max_capacity = db.Column(db.Integer, nullable=False)
    available_seats = db.Column(db.Integer, nullable=False)
    status = db.Column(db.String(20), default='available', nullable=False)

    bookings = db.relationship('Booking', backref='slot', lazy=True)


# ──────────────────────────────────────────────
# BOOKING
# ──────────────────────────────────────────────
class Booking(db.Model):
    __tablename__ = 'bookings'

    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('examination_slots.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='booked', nullable=False)

    evaluations = db.relationship('Evaluation', backref='booking', lazy=True,
                                  cascade='all, delete-orphan')


# ──────────────────────────────────────────────
# EVALUATION
# ──────────────────────────────────────────────
class Evaluation(db.Model):
    __tablename__ = 'evaluations'

    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    marks_awarded = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)


# ──────────────────────────────────────────────
# EXAMINER ASSIGNMENT
# ──────────────────────────────────────────────
class ExaminerAssignment(db.Model):
    __tablename__ = 'examiner_assignments'

    id = db.Column(db.Integer, primary_key=True)
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('examiner_id', 'examination_id', name='uq_examiner_exam'),
    )
```

---

## 4. `app.py`

```python
from flask import Flask, redirect, url_for
from flask_login import LoginManager

from config import Config
from models import db, User


def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)

    # Initialize extensions
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)
    login_manager.login_view = 'auth.login'
    login_manager.login_message_category = 'info'

    @login_manager.user_loader
    def load_user(user_id):
        return User.query.get(int(user_id))

    # Register blueprints
    from routes.auth import auth_bp
    from routes.admin import admin_bp
    from routes.examiner import examiner_bp
    from routes.student import student_bp

    app.register_blueprint(auth_bp)
    app.register_blueprint(admin_bp, url_prefix='/admin')
    app.register_blueprint(examiner_bp, url_prefix='/examiner')
    app.register_blueprint(student_bp, url_prefix='/student')

    # Root route
    @app.route('/')
    def index():
        return redirect(url_for('auth.login'))

    # Create tables and seed admin
    with app.app_context():
        db.create_all()
        _seed_admin()

    return app


def _seed_admin():
    """Create the default admin account if it does not exist."""
    admin = User.query.filter_by(role='admin').first()
    if admin is None:
        admin = User(
            name='Admin',
            email='admin@emp.com',
            role='admin',
            is_approved=True,
            is_active=True,
        )
        admin.set_password('admin123')
        db.session.add(admin)
        db.session.commit()


if __name__ == '__main__':
    app = create_app()
    app.run(debug=True)
```

---

## 5. `routes/__init__.py`

```python
from functools import wraps

from flask import abort, flash, redirect, url_for
from flask_login import current_user


def role_required(*roles):
    """Restrict a view to users whose role is in *roles*."""
    def decorator(func):
        @wraps(func)
        def wrapper(*args, **kwargs):
            if not current_user.is_authenticated:
                flash('Please log in first.', 'warning')
                return redirect(url_for('auth.login'))
            if current_user.role not in roles:
                abort(403)
            return func(*args, **kwargs)
        return wrapper
    return decorator
```

---

## 6. `routes/auth.py`

```python
from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user

from models import db, User

auth_bp = Blueprint('auth', __name__)


@auth_bp.route('/login', methods=['GET', 'POST'])
def login():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')

        user = User.query.filter_by(email=email).first()

        if user is None or not user.check_password(password):
            flash('Invalid email or password.', 'danger')
            return redirect(url_for('auth.login'))

        if not user.is_active:
            flash('Your account has been deactivated. Contact admin.', 'danger')
            return redirect(url_for('auth.login'))

        if user.role == 'examiner' and not user.is_approved:
            flash('Your account is pending admin approval.', 'warning')
            return redirect(url_for('auth.login'))

        login_user(user)
        flash(f'Welcome, {user.name}!', 'success')
        return _redirect_by_role(user.role)

    return render_template('auth/login.html')


@auth_bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return _redirect_by_role(current_user.role)

    if request.method == 'POST':
        name = request.form.get('name', '').strip()
        email = request.form.get('email', '').strip()
        password = request.form.get('password', '')
        confirm = request.form.get('confirm_password', '')
        role = request.form.get('role', 'student')
        department = request.form.get('department', '').strip()
        contact = request.form.get('contact_details', '').strip()

        # Validation
        if not name or not email or not password:
            flash('All fields are required.', 'danger')
            return redirect(url_for('auth.register'))

        if password != confirm:
            flash('Passwords do not match.', 'danger')
            return redirect(url_for('auth.register'))

        if role not in ('student', 'examiner'):
            flash('Invalid role selected.', 'danger')
            return redirect(url_for('auth.register'))

        if User.query.filter_by(email=email).first():
            flash('Email already registered.', 'danger')
            return redirect(url_for('auth.register'))

        user = User(
            name=name,
            email=email,
            role=role,
            department=department,
            contact_details=contact,
            is_approved=(role == 'student'),  # students approved immediately
        )
        user.set_password(password)
        db.session.add(user)
        db.session.commit()

        if role == 'examiner':
            flash('Registration successful! Awaiting admin approval.', 'info')
        else:
            flash('Registration successful! Please log in.', 'success')

        return redirect(url_for('auth.login'))

    return render_template('auth/register.html')


@auth_bp.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('auth.login'))


def _redirect_by_role(role):
    """Send user to the correct dashboard based on role."""
    destinations = {
        'admin': 'admin.dashboard',
        'examiner': 'examiner.dashboard',
        'student': 'student.dashboard',
    }
    return redirect(url_for(destinations.get(role, 'auth.login')))
```

---

## 7. `routes/admin.py`

```python
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required

from models import (
    db, User, Course, Examination, Rubric,
    ExaminationSlot, Booking, ExaminerAssignment, Evaluation,
)
from routes import role_required

admin_bp = Blueprint('admin', __name__)


# ──────────────────────────────────────────────
# DASHBOARD
# ──────────────────────────────────────────────
@admin_bp.route('/dashboard')
@login_required
@role_required('admin')
def dashboard():
    stats = {
        'total_courses': Course.query.count(),
        'total_examinations': Examination.query.count(),
        'total_examiners': User.query.filter_by(role='examiner').count(),
        'total_students': User.query.filter_by(role='student').count(),
        'total_slots': ExaminationSlot.query.count(),
        'total_bookings': Booking.query.count(),
        'pending_examiners': User.query.filter_by(role='examiner', is_approved=False).count(),
    }
    return render_template('admin/dashboard.html', stats=stats)


# ──────────────────────────────────────────────
# COURSES
# ──────────────────────────────────────────────
@admin_bp.route('/courses')
@login_required
@role_required('admin')
def courses():
    all_courses = Course.query.order_by(Course.created_at.desc()).all()
    return render_template('admin/courses.html', courses=all_courses)


@admin_bp.route('/courses/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_course():
    if request.method == 'POST':
        code = request.form.get('course_code', '').strip()
        name = request.form.get('course_name', '').strip()
        desc = request.form.get('description', '').strip()

        if not code or not name:
            flash('Course code and name are required.', 'danger')
            return redirect(url_for('admin.create_course'))

        if Course.query.filter_by(course_code=code).first():
            flash('Course code already exists.', 'danger')
            return redirect(url_for('admin.create_course'))

        course = Course(course_code=code, course_name=name, description=desc)
        db.session.add(course)
        db.session.commit()
        flash('Course created successfully.', 'success')
        return redirect(url_for('admin.courses'))

    return render_template('admin/course_form.html', course=None)


@admin_bp.route('/courses/<int:course_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_course(course_id):
    course = Course.query.get_or_404(course_id)

    if request.method == 'POST':
        course.course_code = request.form.get('course_code', '').strip()
        course.course_name = request.form.get('course_name', '').strip()
        course.description = request.form.get('description', '').strip()
        course.status = request.form.get('status', 'active')
        db.session.commit()
        flash('Course updated.', 'success')
        return redirect(url_for('admin.courses'))

    return render_template('admin/course_form.html', course=course)


@admin_bp.route('/courses/<int:course_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_course(course_id):
    course = Course.query.get_or_404(course_id)
    course.status = 'inactive'
    db.session.commit()
    flash('Course deactivated.', 'success')
    return redirect(url_for('admin.courses'))


# ──────────────────────────────────────────────
# EXAMINATIONS
# ──────────────────────────────────────────────
@admin_bp.route('/examinations')
@login_required
@role_required('admin')
def examinations():
    all_exams = Examination.query.order_by(Examination.created_at.desc()).all()
    return render_template('admin/examinations.html', examinations=all_exams)


@admin_bp.route('/examinations/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_examination():
    if request.method == 'POST':
        exam = Examination(
            course_id=int(request.form['course_id']),
            exam_name=request.form['exam_name'].strip(),
            exam_type=request.form['exam_type'],
            duration_minutes=int(request.form['duration_minutes']),
            max_marks=int(request.form['max_marks']),
            slot_creation_start=datetime.strptime(request.form['slot_creation_start'], '%Y-%m-%dT%H:%M'),
            slot_creation_end=datetime.strptime(request.form['slot_creation_end'], '%Y-%m-%dT%H:%M'),
            slot_booking_start=datetime.strptime(request.form['slot_booking_start'], '%Y-%m-%dT%H:%M'),
            slot_booking_end=datetime.strptime(request.form['slot_booking_end'], '%Y-%m-%dT%H:%M'),
        )
        db.session.add(exam)
        db.session.commit()
        flash('Examination created.', 'success')
        return redirect(url_for('admin.examinations'))

    active_courses = Course.query.filter_by(status='active').all()
    return render_template('admin/exam_form.html', exam=None, courses=active_courses)


@admin_bp.route('/examinations/<int:exam_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_examination(exam_id):
    exam = Examination.query.get_or_404(exam_id)

    if request.method == 'POST':
        exam.exam_name = request.form['exam_name'].strip()
        exam.exam_type = request.form['exam_type']
        exam.duration_minutes = int(request.form['duration_minutes'])
        exam.max_marks = int(request.form['max_marks'])
        exam.slot_creation_start = datetime.strptime(request.form['slot_creation_start'], '%Y-%m-%dT%H:%M')
        exam.slot_creation_end = datetime.strptime(request.form['slot_creation_end'], '%Y-%m-%dT%H:%M')
        exam.slot_booking_start = datetime.strptime(request.form['slot_booking_start'], '%Y-%m-%dT%H:%M')
        exam.slot_booking_end = datetime.strptime(request.form['slot_booking_end'], '%Y-%m-%dT%H:%M')
        exam.status = request.form.get('status', exam.status)
        db.session.commit()
        flash('Examination updated.', 'success')
        return redirect(url_for('admin.examinations'))

    active_courses = Course.query.filter_by(status='active').all()
    return render_template('admin/exam_form.html', exam=exam, courses=active_courses)


@admin_bp.route('/examinations/<int:exam_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_examination(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    db.session.delete(exam)
    db.session.commit()
    flash('Examination deleted.', 'success')
    return redirect(url_for('admin.examinations'))


# ──────────────────────────────────────────────
# RUBRICS
# ──────────────────────────────────────────────
@admin_bp.route('/examinations/<int:exam_id>/rubrics')
@login_required
@role_required('admin')
def rubrics(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    return render_template('admin/rubrics.html', exam=exam, rubrics=exam.rubrics)


@admin_bp.route('/examinations/<int:exam_id>/rubrics/create', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def create_rubric(exam_id):
    exam = Examination.query.get_or_404(exam_id)

    if request.method == 'POST':
        rubric = Rubric(
            examination_id=exam_id,
            criterion_name=request.form['criterion_name'].strip(),
            max_marks=int(request.form['max_marks']),
            weightage=float(request.form.get('weightage', 1.0)),
            description=request.form.get('description', '').strip(),
        )
        db.session.add(rubric)
        db.session.commit()
        flash('Rubric criterion added.', 'success')
        return redirect(url_for('admin.rubrics', exam_id=exam_id))

    return render_template('admin/rubric_form.html', exam=exam, rubric=None)


@admin_bp.route('/rubrics/<int:rubric_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def edit_rubric(rubric_id):
    rubric = Rubric.query.get_or_404(rubric_id)

    if request.method == 'POST':
        rubric.criterion_name = request.form['criterion_name'].strip()
        rubric.max_marks = int(request.form['max_marks'])
        rubric.weightage = float(request.form.get('weightage', 1.0))
        rubric.description = request.form.get('description', '').strip()
        db.session.commit()
        flash('Rubric updated.', 'success')
        return redirect(url_for('admin.rubrics', exam_id=rubric.examination_id))

    return render_template('admin/rubric_form.html', exam=rubric.examination, rubric=rubric)


@admin_bp.route('/rubrics/<int:rubric_id>/delete', methods=['POST'])
@login_required
@role_required('admin')
def delete_rubric(rubric_id):
    rubric = Rubric.query.get_or_404(rubric_id)
    exam_id = rubric.examination_id
    db.session.delete(rubric)
    db.session.commit()
    flash('Rubric deleted.', 'success')
    return redirect(url_for('admin.rubrics', exam_id=exam_id))


# ──────────────────────────────────────────────
# EXAMINER MANAGEMENT
# ──────────────────────────────────────────────
@admin_bp.route('/examiners')
@login_required
@role_required('admin')
def examiners():
    all_examiners = User.query.filter_by(role='examiner').order_by(User.created_at.desc()).all()
    return render_template('admin/examiners.html', examiners=all_examiners)


@admin_bp.route('/examiners/<int:user_id>/approve', methods=['POST'])
@login_required
@role_required('admin')
def approve_examiner(user_id):
    user = User.query.get_or_404(user_id)
    user.is_approved = True
    db.session.commit()
    flash(f'{user.name} approved.', 'success')
    return redirect(url_for('admin.examiners'))


@admin_bp.route('/examiners/<int:user_id>/deactivate', methods=['POST'])
@login_required
@role_required('admin')
def deactivate_examiner(user_id):
    user = User.query.get_or_404(user_id)
    user.is_active = not user.is_active
    db.session.commit()
    status = 'activated' if user.is_active else 'deactivated'
    flash(f'{user.name} {status}.', 'success')
    return redirect(url_for('admin.examiners'))


@admin_bp.route('/examiners/assign', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def assign_examiner():
    if request.method == 'POST':
        examiner_id = int(request.form['examiner_id'])
        examination_id = int(request.form['examination_id'])

        existing = ExaminerAssignment.query.filter_by(
            examiner_id=examiner_id, examination_id=examination_id
        ).first()
        if existing:
            flash('Examiner already assigned to this examination.', 'warning')
        else:
            assignment = ExaminerAssignment(
                examiner_id=examiner_id, examination_id=examination_id
            )
            db.session.add(assignment)
            db.session.commit()
            flash('Examiner assigned successfully.', 'success')

        return redirect(url_for('admin.assign_examiner'))

    approved_examiners = User.query.filter_by(role='examiner', is_approved=True, is_active=True).all()
    all_exams = Examination.query.all()
    assignments = ExaminerAssignment.query.all()
    return render_template(
        'admin/assign_examiner.html',
        examiners=approved_examiners,
        examinations=all_exams,
        assignments=assignments,
    )


# ──────────────────────────────────────────────
# STUDENTS (view only)
# ──────────────────────────────────────────────
@admin_bp.route('/students')
@login_required
@role_required('admin')
def students():
    all_students = User.query.filter_by(role='student').order_by(User.created_at.desc()).all()
    return render_template('admin/students.html', students=all_students)


# ──────────────────────────────────────────────
# SLOTS & BOOKINGS
# ──────────────────────────────────────────────
@admin_bp.route('/slots')
@login_required
@role_required('admin')
def slots():
    all_slots = ExaminationSlot.query.order_by(ExaminationSlot.date.desc()).all()
    return render_template('admin/slots.html', slots=all_slots)


@admin_bp.route('/bookings')
@login_required
@role_required('admin')
def bookings():
    all_bookings = Booking.query.order_by(Booking.booking_date.desc()).all()
    return render_template('admin/bookings.html', bookings=all_bookings)


@admin_bp.route('/bookings/<int:booking_id>/reschedule', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reschedule_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    exam = booking.slot.examination

    if request.method == 'POST':
        new_slot_id = int(request.form['new_slot_id'])
        new_slot = ExaminationSlot.query.get_or_404(new_slot_id)

        if new_slot.available_seats <= 0:
            flash('Selected slot is full.', 'danger')
            return redirect(url_for('admin.reschedule_booking', booking_id=booking_id))

        # Free up old slot
        old_slot = booking.slot
        old_slot.available_seats += 1
        if old_slot.status == 'full':
            old_slot.status = 'available'

        # Move to new slot
        booking.slot_id = new_slot_id
        new_slot.available_seats -= 1
        if new_slot.available_seats == 0:
            new_slot.status = 'full'

        db.session.commit()
        flash('Booking rescheduled.', 'success')
        return redirect(url_for('admin.bookings'))

    available_slots = ExaminationSlot.query.filter(
        ExaminationSlot.examination_id == exam.id,
        ExaminationSlot.id != booking.slot_id,
        ExaminationSlot.status == 'available',
    ).all()
    return render_template('admin/reschedule.html', booking=booking, slots=available_slots)


@admin_bp.route('/slots/<int:slot_id>/reassign', methods=['GET', 'POST'])
@login_required
@role_required('admin')
def reassign_examiner(slot_id):
    slot = ExaminationSlot.query.get_or_404(slot_id)

    if request.method == 'POST':
        new_examiner_id = int(request.form['examiner_id'])
        slot.examiner_id = new_examiner_id
        db.session.commit()
        flash('Examiner reassigned.', 'success')
        return redirect(url_for('admin.slots'))

    approved_examiners = User.query.filter_by(role='examiner', is_approved=True, is_active=True).all()
    return render_template('admin/reassign.html', slot=slot, examiners=approved_examiners)


# ──────────────────────────────────────────────
# SEARCH
# ──────────────────────────────────────────────
@admin_bp.route('/search')
@login_required
@role_required('admin')
def search():
    query = request.args.get('q', '').strip()
    results = {'students': [], 'examiners': [], 'examinations': [], 'bookings': []}

    if query:
        like_pattern = f'%{query}%'
        results['students'] = User.query.filter(
            User.role == 'student',
            (User.name.ilike(like_pattern) | User.email.ilike(like_pattern))
        ).all()
        results['examiners'] = User.query.filter(
            User.role == 'examiner',
            (User.name.ilike(like_pattern) | User.email.ilike(like_pattern))
        ).all()
        results['examinations'] = Examination.query.filter(
            Examination.exam_name.ilike(like_pattern)
        ).all()
        results['bookings'] = Booking.query.join(User).filter(
            User.name.ilike(like_pattern)
        ).all()

    return render_template('admin/search.html', query=query, results=results)
```

---

## 8. `routes/examiner.py`

```python
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models import (
    db, Examination, ExaminationSlot, Booking, Rubric,
    Evaluation, ExaminerAssignment,
)
from routes import role_required

examiner_bp = Blueprint('examiner', __name__)


@examiner_bp.route('/dashboard')
@login_required
@role_required('examiner')
def dashboard():
    assignments = ExaminerAssignment.query.filter_by(examiner_id=current_user.id).all()
    my_slots = ExaminationSlot.query.filter_by(examiner_id=current_user.id).all()
    booked_count = Booking.query.join(ExaminationSlot).filter(
        ExaminationSlot.examiner_id == current_user.id,
        Booking.status == 'booked',
    ).count()
    pending_evals = Booking.query.join(ExaminationSlot).filter(
        ExaminationSlot.examiner_id == current_user.id,
        Booking.status == 'booked',
    ).outerjoin(Evaluation).filter(Evaluation.id.is_(None)).count()

    return render_template(
        'examiner/dashboard.html',
        assignments=assignments,
        my_slots=my_slots,
        booked_count=booked_count,
        pending_evals=pending_evals,
    )


@examiner_bp.route('/examinations')
@login_required
@role_required('examiner')
def assigned_examinations():
    assignments = ExaminerAssignment.query.filter_by(examiner_id=current_user.id).all()
    exams = [a.examination for a in assignments]
    return render_template('examiner/assigned_exams.html', examinations=exams)


@examiner_bp.route('/slots')
@login_required
@role_required('examiner')
def slots():
    my_slots = ExaminationSlot.query.filter_by(
        examiner_id=current_user.id
    ).order_by(ExaminationSlot.date.desc()).all()
    return render_template('examiner/slots.html', slots=my_slots)


@examiner_bp.route('/slots/create', methods=['GET', 'POST'])
@login_required
@role_required('examiner')
def create_slot():
    if request.method == 'POST':
        exam_id = int(request.form['examination_id'])
        exam = Examination.query.get_or_404(exam_id)

        if not exam.is_slot_creation_open():
            flash('Slot creation is not open for this examination.', 'danger')
            return redirect(url_for('examiner.slots'))

        # Verify examiner is assigned to this exam
        assignment = ExaminerAssignment.query.filter_by(
            examiner_id=current_user.id, examination_id=exam_id
        ).first()
        if not assignment:
            flash('You are not assigned to this examination.', 'danger')
            return redirect(url_for('examiner.slots'))

        slot_date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        capacity = int(request.form['max_capacity'])

        slot = ExaminationSlot(
            examination_id=exam_id,
            examiner_id=current_user.id,
            date=slot_date,
            start_time=start_time,
            end_time=end_time,
            max_capacity=capacity,
            available_seats=capacity,
        )
        db.session.add(slot)
        db.session.commit()
        flash('Slot created.', 'success')
        return redirect(url_for('examiner.slots'))

    # Get exams assigned to this examiner where slot creation is open
    assignments = ExaminerAssignment.query.filter_by(examiner_id=current_user.id).all()
    exams = [a.examination for a in assignments if a.examination.is_slot_creation_open()]
    return render_template('examiner/slot_form.html', slot=None, examinations=exams)


@examiner_bp.route('/slots/<int:slot_id>/edit', methods=['GET', 'POST'])
@login_required
@role_required('examiner')
def edit_slot(slot_id):
    slot = ExaminationSlot.query.get_or_404(slot_id)

    if slot.examiner_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('examiner.slots'))

    # Can only edit before booking starts
    exam = slot.examination
    if datetime.utcnow() >= exam.slot_booking_start:
        flash('Cannot edit slot after booking has started.', 'danger')
        return redirect(url_for('examiner.slots'))

    if request.method == 'POST':
        slot.date = datetime.strptime(request.form['date'], '%Y-%m-%d').date()
        slot.start_time = datetime.strptime(request.form['start_time'], '%H:%M').time()
        slot.end_time = datetime.strptime(request.form['end_time'], '%H:%M').time()
        slot.max_capacity = int(request.form['max_capacity'])
        slot.available_seats = slot.max_capacity  # reset since no bookings yet
        db.session.commit()
        flash('Slot updated.', 'success')
        return redirect(url_for('examiner.slots'))

    return render_template('examiner/slot_form.html', slot=slot, examinations=[exam])


@examiner_bp.route('/slots/<int:slot_id>/delete', methods=['POST'])
@login_required
@role_required('examiner')
def delete_slot(slot_id):
    slot = ExaminationSlot.query.get_or_404(slot_id)

    if slot.examiner_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('examiner.slots'))

    exam = slot.examination
    if datetime.utcnow() >= exam.slot_booking_start:
        flash('Cannot delete slot after booking has started.', 'danger')
        return redirect(url_for('examiner.slots'))

    db.session.delete(slot)
    db.session.commit()
    flash('Slot deleted.', 'success')
    return redirect(url_for('examiner.slots'))


@examiner_bp.route('/slots/<int:slot_id>/students')
@login_required
@role_required('examiner')
def booked_students(slot_id):
    slot = ExaminationSlot.query.get_or_404(slot_id)
    if slot.examiner_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('examiner.slots'))

    active_bookings = Booking.query.filter_by(slot_id=slot_id, status='booked').all()
    return render_template('examiner/booked_students.html', slot=slot, bookings=active_bookings)


@examiner_bp.route('/evaluate/<int:booking_id>', methods=['GET', 'POST'])
@login_required
@role_required('examiner')
def evaluate(booking_id):
    booking = Booking.query.get_or_404(booking_id)
    slot = booking.slot

    if slot.examiner_id != current_user.id:
        flash('You can only evaluate students in your own slots.', 'danger')
        return redirect(url_for('examiner.dashboard'))

    exam = slot.examination
    rubric_list = exam.rubrics

    if request.method == 'POST':
        # Delete old evaluations for this booking if re-evaluating
        Evaluation.query.filter_by(booking_id=booking_id).delete()

        for rubric in rubric_list:
            marks = float(request.form.get(f'marks_{rubric.id}', 0))
            remarks = request.form.get(f'remarks_{rubric.id}', '').strip()

            if marks > rubric.max_marks:
                flash(f'Marks for {rubric.criterion_name} cannot exceed {rubric.max_marks}.', 'danger')
                return redirect(url_for('examiner.evaluate', booking_id=booking_id))

            evaluation = Evaluation(
                booking_id=booking_id,
                rubric_id=rubric.id,
                marks_awarded=marks,
                remarks=remarks,
            )
            db.session.add(evaluation)

        booking.status = 'completed'
        db.session.commit()
        flash('Evaluation submitted.', 'success')
        return redirect(url_for('examiner.booked_students', slot_id=slot.id))

    existing_evals = {e.rubric_id: e for e in booking.evaluations}
    return render_template(
        'examiner/evaluate.html',
        booking=booking,
        rubrics=rubric_list,
        existing_evals=existing_evals,
    )
```

---

## 9. `routes/student.py`

```python
from datetime import datetime

from flask import Blueprint, render_template, redirect, url_for, flash, request
from flask_login import login_required, current_user

from models import db, Examination, ExaminationSlot, Booking, Evaluation

from routes import role_required

student_bp = Blueprint('student', __name__)


@student_bp.route('/dashboard')
@login_required
@role_required('student')
def dashboard():
    now = datetime.utcnow()

    # Exams with booking open
    available_exams = Examination.query.filter(
        Examination.status == 'booking_open',
        Examination.slot_booking_start <= now,
        Examination.slot_booking_end >= now,
    ).all()

    my_bookings = Booking.query.filter_by(
        student_id=current_user.id
    ).order_by(Booking.booking_date.desc()).all()

    upcoming = [b for b in my_bookings if b.status == 'booked']
    completed = [b for b in my_bookings if b.status == 'completed']

    return render_template(
        'student/dashboard.html',
        available_exams=available_exams,
        upcoming=upcoming,
        completed=completed,
    )


@student_bp.route('/examinations')
@login_required
@role_required('student')
def examinations():
    search_query = request.args.get('q', '').strip()
    exam_type = request.args.get('type', '')

    query = Examination.query.filter(Examination.status.in_(['booking_open', 'slot_creation', 'closed', 'completed']))

    if search_query:
        query = query.filter(Examination.exam_name.ilike(f'%{search_query}%'))
    if exam_type:
        query = query.filter(Examination.exam_type == exam_type)

    exams = query.order_by(Examination.created_at.desc()).all()
    return render_template('student/examinations.html', examinations=exams,
                           search_query=search_query, exam_type=exam_type)


@student_bp.route('/examinations/<int:exam_id>/slots')
@login_required
@role_required('student')
def available_slots(exam_id):
    exam = Examination.query.get_or_404(exam_id)
    slots = ExaminationSlot.query.filter_by(
        examination_id=exam_id, status='available'
    ).order_by(ExaminationSlot.date, ExaminationSlot.start_time).all()

    # Check if student already booked this exam
    existing_booking = Booking.query.join(ExaminationSlot).filter(
        Booking.student_id == current_user.id,
        ExaminationSlot.examination_id == exam_id,
        Booking.status != 'cancelled',
    ).first()

    return render_template(
        'student/available_slots.html',
        exam=exam,
        slots=slots,
        already_booked=existing_booking is not None,
    )


@student_bp.route('/book/<int:slot_id>', methods=['POST'])
@login_required
@role_required('student')
def book_slot(slot_id):
    slot = ExaminationSlot.query.get_or_404(slot_id)
    exam = slot.examination

    # Check booking window
    if not exam.is_booking_open():
        flash('Booking is not open for this examination.', 'danger')
        return redirect(url_for('student.examinations'))

    # Check duplicate
    existing = Booking.query.join(ExaminationSlot).filter(
        Booking.student_id == current_user.id,
        ExaminationSlot.examination_id == exam.id,
        Booking.status != 'cancelled',
    ).first()
    if existing:
        flash('You already have a booking for this examination.', 'warning')
        return redirect(url_for('student.available_slots', exam_id=exam.id))

    # Check availability
    if slot.available_seats <= 0:
        flash('This slot is full.', 'danger')
        return redirect(url_for('student.available_slots', exam_id=exam.id))

    # Create booking
    booking = Booking(student_id=current_user.id, slot_id=slot_id)
    slot.available_seats -= 1
    if slot.available_seats == 0:
        slot.status = 'full'

    db.session.add(booking)
    db.session.commit()
    flash('Slot booked successfully!', 'success')
    return redirect(url_for('student.my_bookings'))


@student_bp.route('/bookings')
@login_required
@role_required('student')
def my_bookings():
    all_bookings = Booking.query.filter_by(
        student_id=current_user.id
    ).order_by(Booking.booking_date.desc()).all()
    return render_template('student/my_bookings.html', bookings=all_bookings)


@student_bp.route('/bookings/<int:booking_id>/cancel', methods=['POST'])
@login_required
@role_required('student')
def cancel_booking(booking_id):
    booking = Booking.query.get_or_404(booking_id)

    if booking.student_id != current_user.id:
        flash('Unauthorized.', 'danger')
        return redirect(url_for('student.my_bookings'))

    if booking.status != 'booked':
        flash('This booking cannot be cancelled.', 'danger')
        return redirect(url_for('student.my_bookings'))

    # Check deadline
    exam = booking.slot.examination
    if datetime.utcnow() > exam.slot_booking_end:
        flash('Cancellation deadline has passed.', 'danger')
        return redirect(url_for('student.my_bookings'))

    booking.status = 'cancelled'
    slot = booking.slot
    slot.available_seats += 1
    if slot.status == 'full':
        slot.status = 'available'

    db.session.commit()
    flash('Booking cancelled.', 'success')
    return redirect(url_for('student.my_bookings'))


@student_bp.route('/results')
@login_required
@role_required('student')
def results():
    completed_bookings = Booking.query.filter_by(
        student_id=current_user.id, status='completed'
    ).all()

    results_data = []
    for booking in completed_bookings:
        evals = Evaluation.query.filter_by(booking_id=booking.id).all()
        total = sum(e.marks_awarded for e in evals)
        max_total = sum(e.rubric.max_marks for e in evals)
        results_data.append({
            'booking': booking,
            'evaluations': evals,
            'total_marks': total,
            'max_marks': max_total,
        })

    return render_template('student/results.html', results=results_data)


@student_bp.route('/profile', methods=['GET', 'POST'])
@login_required
@role_required('student')
def profile():
    if request.method == 'POST':
        current_user.name = request.form.get('name', '').strip()
        current_user.contact_details = request.form.get('contact_details', '').strip()
        current_user.department = request.form.get('department', '').strip()
        db.session.commit()
        flash('Profile updated.', 'success')
        return redirect(url_for('student.profile'))

    return render_template('student/profile.html')
```

---

## 10. `templates/base.html`

```html
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{% block title %}EMP{% endblock %}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/css/bootstrap.min.css" rel="stylesheet">
    <link href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.min.css" rel="stylesheet">
    <link rel="stylesheet" href="{{ url_for('static', filename='css/style.css') }}">
</head>
<body>

<nav class="navbar navbar-expand-lg navbar-dark bg-dark">
    <div class="container-fluid">
        <a class="navbar-brand" href="/">
            <i class="bi bi-mortarboard-fill"></i> EMP
        </a>
        <button class="navbar-toggler" type="button" data-bs-toggle="collapse" data-bs-target="#navContent">
            <span class="navbar-toggler-icon"></span>
        </button>
        <div class="collapse navbar-collapse" id="navContent">
            <ul class="navbar-nav me-auto">
                {% if current_user.is_authenticated %}

                    {# ── ADMIN NAV ── #}
                    {% if current_user.role == 'admin' %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.dashboard') }}">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.courses') }}">Courses</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.examinations') }}">Examinations</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.examiners') }}">Examiners</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.students') }}">Students</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.slots') }}">Slots</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.bookings') }}">Bookings</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('admin.search') }}">Search</a></li>

                    {# ── EXAMINER NAV ── #}
                    {% elif current_user.role == 'examiner' %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('examiner.dashboard') }}">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('examiner.assigned_examinations') }}">My Exams</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('examiner.slots') }}">My Slots</a></li>

                    {# ── STUDENT NAV ── #}
                    {% elif current_user.role == 'student' %}
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('student.dashboard') }}">Dashboard</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('student.examinations') }}">Examinations</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('student.my_bookings') }}">My Bookings</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('student.results') }}">Results</a></li>
                    <li class="nav-item"><a class="nav-link" href="{{ url_for('student.profile') }}">Profile</a></li>
                    {% endif %}

                {% endif %}
            </ul>
            <ul class="navbar-nav">
                {% if current_user.is_authenticated %}
                <li class="nav-item">
                    <span class="nav-link text-light">
                        <i class="bi bi-person-circle"></i> {{ current_user.name }} ({{ current_user.role }})
                    </span>
                </li>
                <li class="nav-item">
                    <a class="nav-link" href="{{ url_for('auth.logout') }}">Logout</a>
                </li>
                {% else %}
                <li class="nav-item"><a class="nav-link" href="{{ url_for('auth.login') }}">Login</a></li>
                <li class="nav-item"><a class="nav-link" href="{{ url_for('auth.register') }}">Register</a></li>
                {% endif %}
            </ul>
        </div>
    </div>
</nav>

<div class="container mt-4">
    {# Flash messages #}
    {% with messages = get_flashed_messages(with_categories=true) %}
        {% if messages %}
            {% for category, message in messages %}
            <div class="alert alert-{{ category }} alert-dismissible fade show" role="alert">
                {{ message }}
                <button type="button" class="btn-close" data-bs-dismiss="alert"></button>
            </div>
            {% endfor %}
        {% endif %}
    {% endwith %}

    {% block content %}{% endblock %}
</div>

<script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.3/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
```

---

## 11. `templates/auth/login.html`

```html
{% extends 'base.html' %}
{% block title %}Login — EMP{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-5">
        <div class="card shadow mt-5">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Login</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <button type="submit" class="btn btn-primary w-100">Login</button>
                </form>
                <p class="text-center mt-3">
                    Don't have an account? <a href="{{ url_for('auth.register') }}">Register</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 12. `templates/auth/register.html`

```html
{% extends 'base.html' %}
{% block title %}Register — EMP{% endblock %}

{% block content %}
<div class="row justify-content-center">
    <div class="col-md-6">
        <div class="card shadow mt-5">
            <div class="card-body">
                <h3 class="card-title text-center mb-4">Register</h3>
                <form method="POST">
                    <div class="mb-3">
                        <label for="name" class="form-label">Full Name</label>
                        <input type="text" class="form-control" id="name" name="name" required>
                    </div>
                    <div class="mb-3">
                        <label for="email" class="form-label">Email</label>
                        <input type="email" class="form-control" id="email" name="email" required>
                    </div>
                    <div class="mb-3">
                        <label for="role" class="form-label">Register as</label>
                        <select class="form-select" id="role" name="role" required>
                            <option value="student">Student</option>
                            <option value="examiner">Examiner</option>
                        </select>
                    </div>
                    <div class="mb-3">
                        <label for="department" class="form-label">Department</label>
                        <input type="text" class="form-control" id="department" name="department">
                    </div>
                    <div class="mb-3">
                        <label for="contact_details" class="form-label">Contact Details</label>
                        <input type="text" class="form-control" id="contact_details" name="contact_details">
                    </div>
                    <div class="mb-3">
                        <label for="password" class="form-label">Password</label>
                        <input type="password" class="form-control" id="password" name="password" required>
                    </div>
                    <div class="mb-3">
                        <label for="confirm_password" class="form-label">Confirm Password</label>
                        <input type="password" class="form-control" id="confirm_password" name="confirm_password" required>
                    </div>
                    <button type="submit" class="btn btn-success w-100">Register</button>
                </form>
                <p class="text-center mt-3">
                    Already have an account? <a href="{{ url_for('auth.login') }}">Login</a>
                </p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 13. `templates/admin/dashboard.html`

```html
{% extends 'base.html' %}
{% block title %}Admin Dashboard — EMP{% endblock %}

{% block content %}
<h2>Admin Dashboard</h2>
<div class="row mt-4">
    <div class="col-md-4 mb-3">
        <div class="card text-bg-primary">
            <div class="card-body">
                <h5 class="card-title">Courses</h5>
                <p class="display-6">{{ stats.total_courses }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-success">
            <div class="card-body">
                <h5 class="card-title">Examinations</h5>
                <p class="display-6">{{ stats.total_examinations }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-info">
            <div class="card-body">
                <h5 class="card-title">Examiners</h5>
                <p class="display-6">{{ stats.total_examiners }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-warning">
            <div class="card-body">
                <h5 class="card-title">Students</h5>
                <p class="display-6">{{ stats.total_students }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-secondary">
            <div class="card-body">
                <h5 class="card-title">Slots</h5>
                <p class="display-6">{{ stats.total_slots }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-dark">
            <div class="card-body">
                <h5 class="card-title">Bookings</h5>
                <p class="display-6">{{ stats.total_bookings }}</p>
            </div>
        </div>
    </div>
</div>

{% if stats.pending_examiners > 0 %}
<div class="alert alert-warning mt-3">
    <i class="bi bi-exclamation-triangle"></i>
    {{ stats.pending_examiners }} examiner(s) awaiting approval.
    <a href="{{ url_for('admin.examiners') }}">Review now</a>
</div>
{% endif %}
{% endblock %}
```

---

## 14. `templates/admin/courses.html`

```html
{% extends 'base.html' %}
{% block title %}Courses — EMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center">
    <h2>Courses</h2>
    <a href="{{ url_for('admin.create_course') }}" class="btn btn-primary">+ New Course</a>
</div>

<table class="table table-striped mt-3">
    <thead>
        <tr>
            <th>ID</th><th>Code</th><th>Name</th><th>Status</th><th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for course in courses %}
        <tr>
            <td>{{ course.id }}</td>
            <td>{{ course.course_code }}</td>
            <td>{{ course.course_name }}</td>
            <td>
                <span class="badge {{ 'bg-success' if course.status == 'active' else 'bg-secondary' }}">
                    {{ course.status }}
                </span>
            </td>
            <td>
                <a href="{{ url_for('admin.edit_course', course_id=course.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                <form method="POST" action="{{ url_for('admin.delete_course', course_id=course.id) }}" style="display:inline;">
                    <button type="submit" class="btn btn-sm btn-outline-danger"
                            onclick="return confirm('Deactivate this course?')">Deactivate</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 15. `templates/admin/course_form.html`

```html
{% extends 'base.html' %}
{% block title %}{{ 'Edit' if course else 'Create' }} Course — EMP{% endblock %}

{% block content %}
<h2>{{ 'Edit' if course else 'Create' }} Course</h2>
<form method="POST" class="mt-3" style="max-width: 600px;">
    <div class="mb-3">
        <label class="form-label">Course Code</label>
        <input type="text" class="form-control" name="course_code"
               value="{{ course.course_code if course else '' }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Course Name</label>
        <input type="text" class="form-control" name="course_name"
               value="{{ course.course_name if course else '' }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea class="form-control" name="description" rows="3">{{ course.description if course else '' }}</textarea>
    </div>
    {% if course %}
    <div class="mb-3">
        <label class="form-label">Status</label>
        <select class="form-select" name="status">
            <option value="active" {{ 'selected' if course.status == 'active' }}>Active</option>
            <option value="inactive" {{ 'selected' if course.status == 'inactive' }}>Inactive</option>
        </select>
    </div>
    {% endif %}
    <button type="submit" class="btn btn-success">{{ 'Update' if course else 'Create' }}</button>
    <a href="{{ url_for('admin.courses') }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 16. `templates/admin/examinations.html`

```html
{% extends 'base.html' %}
{% block title %}Examinations — EMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center">
    <h2>Examinations</h2>
    <a href="{{ url_for('admin.create_examination') }}" class="btn btn-primary">+ New Examination</a>
</div>

<table class="table table-striped mt-3">
    <thead>
        <tr>
            <th>ID</th><th>Name</th><th>Course</th><th>Type</th>
            <th>Max Marks</th><th>Status</th><th>Actions</th>
        </tr>
    </thead>
    <tbody>
        {% for exam in examinations %}
        <tr>
            <td>{{ exam.id }}</td>
            <td>{{ exam.exam_name }}</td>
            <td>{{ exam.course.course_name }}</td>
            <td>{{ exam.exam_type }}</td>
            <td>{{ exam.max_marks }}</td>
            <td><span class="badge bg-info">{{ exam.status }}</span></td>
            <td>
                <a href="{{ url_for('admin.edit_examination', exam_id=exam.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                <a href="{{ url_for('admin.rubrics', exam_id=exam.id) }}" class="btn btn-sm btn-outline-secondary">Rubrics</a>
                <form method="POST" action="{{ url_for('admin.delete_examination', exam_id=exam.id) }}" style="display:inline;">
                    <button type="submit" class="btn btn-sm btn-outline-danger"
                            onclick="return confirm('Delete this examination?')">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 17. `templates/admin/exam_form.html`

```html
{% extends 'base.html' %}
{% block title %}{{ 'Edit' if exam else 'Create' }} Examination — EMP{% endblock %}

{% block content %}
<h2>{{ 'Edit' if exam else 'Create' }} Examination</h2>
<form method="POST" class="mt-3" style="max-width: 700px;">
    <div class="mb-3">
        <label class="form-label">Course</label>
        <select class="form-select" name="course_id" required>
            {% for c in courses %}
            <option value="{{ c.id }}" {{ 'selected' if exam and exam.course_id == c.id }}>
                {{ c.course_code }} — {{ c.course_name }}
            </option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Examination Name</label>
        <input type="text" class="form-control" name="exam_name"
               value="{{ exam.exam_name if exam else '' }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Type</label>
        <select class="form-select" name="exam_type" required>
            {% for t in ['viva', 'practical', 'project_demo', 'assessment'] %}
            <option value="{{ t }}" {{ 'selected' if exam and exam.exam_type == t }}>{{ t | replace('_',' ') | title }}</option>
            {% endfor %}
        </select>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Duration (minutes)</label>
            <input type="number" class="form-control" name="duration_minutes"
                   value="{{ exam.duration_minutes if exam else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">Max Marks</label>
            <input type="number" class="form-control" name="max_marks"
                   value="{{ exam.max_marks if exam else '' }}" required>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Slot Creation Start</label>
            <input type="datetime-local" class="form-control" name="slot_creation_start"
                   value="{{ exam.slot_creation_start.strftime('%Y-%m-%dT%H:%M') if exam else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">Slot Creation End</label>
            <input type="datetime-local" class="form-control" name="slot_creation_end"
                   value="{{ exam.slot_creation_end.strftime('%Y-%m-%dT%H:%M') if exam else '' }}" required>
        </div>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Slot Booking Start</label>
            <input type="datetime-local" class="form-control" name="slot_booking_start"
                   value="{{ exam.slot_booking_start.strftime('%Y-%m-%dT%H:%M') if exam else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">Slot Booking End</label>
            <input type="datetime-local" class="form-control" name="slot_booking_end"
                   value="{{ exam.slot_booking_end.strftime('%Y-%m-%dT%H:%M') if exam else '' }}" required>
        </div>
    </div>
    {% if exam %}
    <div class="mb-3">
        <label class="form-label">Status</label>
        <select class="form-select" name="status">
            {% for s in ['draft', 'slot_creation', 'booking_open', 'closed', 'completed'] %}
            <option value="{{ s }}" {{ 'selected' if exam.status == s }}>{{ s | replace('_',' ') | title }}</option>
            {% endfor %}
        </select>
    </div>
    {% endif %}
    <button type="submit" class="btn btn-success">{{ 'Update' if exam else 'Create' }}</button>
    <a href="{{ url_for('admin.examinations') }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 18. `templates/admin/rubrics.html`

```html
{% extends 'base.html' %}
{% block title %}Rubrics — {{ exam.exam_name }} — EMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center">
    <h2>Rubrics — {{ exam.exam_name }}</h2>
    <a href="{{ url_for('admin.create_rubric', exam_id=exam.id) }}" class="btn btn-primary">+ Add Criterion</a>
</div>

<table class="table table-striped mt-3">
    <thead>
        <tr><th>Criterion</th><th>Max Marks</th><th>Weightage</th><th>Description</th><th>Actions</th></tr>
    </thead>
    <tbody>
        {% for r in rubrics %}
        <tr>
            <td>{{ r.criterion_name }}</td>
            <td>{{ r.max_marks }}</td>
            <td>{{ r.weightage }}</td>
            <td>{{ r.description or '—' }}</td>
            <td>
                <a href="{{ url_for('admin.edit_rubric', rubric_id=r.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                <form method="POST" action="{{ url_for('admin.delete_rubric', rubric_id=r.id) }}" style="display:inline;">
                    <button type="submit" class="btn btn-sm btn-outline-danger">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
<a href="{{ url_for('admin.examinations') }}" class="btn btn-secondary">Back</a>
{% endblock %}
```

---

## 19. `templates/admin/rubric_form.html`

```html
{% extends 'base.html' %}
{% block title %}{{ 'Edit' if rubric else 'Add' }} Rubric — EMP{% endblock %}

{% block content %}
<h2>{{ 'Edit' if rubric else 'Add' }} Rubric — {{ exam.exam_name }}</h2>
<form method="POST" class="mt-3" style="max-width: 600px;">
    <div class="mb-3">
        <label class="form-label">Criterion Name</label>
        <input type="text" class="form-control" name="criterion_name"
               value="{{ rubric.criterion_name if rubric else '' }}" required>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Max Marks</label>
            <input type="number" class="form-control" name="max_marks"
                   value="{{ rubric.max_marks if rubric else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">Weightage</label>
            <input type="number" step="0.1" class="form-control" name="weightage"
                   value="{{ rubric.weightage if rubric else '1.0' }}">
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">Description</label>
        <textarea class="form-control" name="description" rows="3">{{ rubric.description if rubric else '' }}</textarea>
    </div>
    <button type="submit" class="btn btn-success">{{ 'Update' if rubric else 'Add' }}</button>
    <a href="{{ url_for('admin.rubrics', exam_id=exam.id) }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 20. `templates/admin/examiners.html`

```html
{% extends 'base.html' %}
{% block title %}Examiners — EMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center">
    <h2>Examiners</h2>
    <a href="{{ url_for('admin.assign_examiner') }}" class="btn btn-outline-primary">Assign to Exam</a>
</div>

<table class="table table-striped mt-3">
    <thead>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Dept</th><th>Approved</th><th>Active</th><th>Actions</th></tr>
    </thead>
    <tbody>
        {% for e in examiners %}
        <tr>
            <td>{{ e.id }}</td>
            <td>{{ e.name }}</td>
            <td>{{ e.email }}</td>
            <td>{{ e.department or '—' }}</td>
            <td>{{ '✅' if e.is_approved else '❌' }}</td>
            <td>{{ '✅' if e.is_active else '❌' }}</td>
            <td>
                {% if not e.is_approved %}
                <form method="POST" action="{{ url_for('admin.approve_examiner', user_id=e.id) }}" style="display:inline;">
                    <button class="btn btn-sm btn-success">Approve</button>
                </form>
                {% endif %}
                <form method="POST" action="{{ url_for('admin.deactivate_examiner', user_id=e.id) }}" style="display:inline;">
                    <button class="btn btn-sm btn-outline-warning">
                        {{ 'Activate' if not e.is_active else 'Deactivate' }}
                    </button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 21. `templates/admin/assign_examiner.html`

```html
{% extends 'base.html' %}
{% block title %}Assign Examiner — EMP{% endblock %}

{% block content %}
<h2>Assign Examiner to Examination</h2>
<form method="POST" class="mt-3" style="max-width: 600px;">
    <div class="mb-3">
        <label class="form-label">Examiner</label>
        <select class="form-select" name="examiner_id" required>
            {% for e in examiners %}
            <option value="{{ e.id }}">{{ e.name }} ({{ e.email }})</option>
            {% endfor %}
        </select>
    </div>
    <div class="mb-3">
        <label class="form-label">Examination</label>
        <select class="form-select" name="examination_id" required>
            {% for ex in examinations %}
            <option value="{{ ex.id }}">{{ ex.exam_name }} — {{ ex.course.course_name }}</option>
            {% endfor %}
        </select>
    </div>
    <button type="submit" class="btn btn-primary">Assign</button>
</form>

<h4 class="mt-5">Current Assignments</h4>
<table class="table table-striped">
    <thead><tr><th>Examiner</th><th>Examination</th><th>Assigned</th></tr></thead>
    <tbody>
        {% for a in assignments %}
        <tr>
            <td>{{ a.examiner.name }}</td>
            <td>{{ a.examination.exam_name }}</td>
            <td>{{ a.assigned_at.strftime('%Y-%m-%d %H:%M') }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 22. `templates/admin/students.html`

```html
{% extends 'base.html' %}
{% block title %}Students — EMP{% endblock %}

{% block content %}
<h2>Students</h2>
<table class="table table-striped mt-3">
    <thead>
        <tr><th>ID</th><th>Name</th><th>Email</th><th>Department</th><th>Registered</th></tr>
    </thead>
    <tbody>
        {% for s in students %}
        <tr>
            <td>{{ s.id }}</td>
            <td>{{ s.name }}</td>
            <td>{{ s.email }}</td>
            <td>{{ s.department or '—' }}</td>
            <td>{{ s.created_at.strftime('%Y-%m-%d') }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 23. `templates/admin/slots.html`

```html
{% extends 'base.html' %}
{% block title %}All Slots — EMP{% endblock %}

{% block content %}
<h2>All Examination Slots</h2>
<table class="table table-striped mt-3">
    <thead>
        <tr><th>ID</th><th>Exam</th><th>Examiner</th><th>Date</th><th>Time</th><th>Capacity</th><th>Available</th><th>Status</th><th>Actions</th></tr>
    </thead>
    <tbody>
        {% for s in slots %}
        <tr>
            <td>{{ s.id }}</td>
            <td>{{ s.examination.exam_name }}</td>
            <td>{{ s.examiner.name }}</td>
            <td>{{ s.date }}</td>
            <td>{{ s.start_time }} – {{ s.end_time }}</td>
            <td>{{ s.max_capacity }}</td>
            <td>{{ s.available_seats }}</td>
            <td><span class="badge bg-info">{{ s.status }}</span></td>
            <td>
                <a href="{{ url_for('admin.reassign_examiner', slot_id=s.id) }}" class="btn btn-sm btn-outline-warning">Reassign</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 24. `templates/admin/bookings.html`

```html
{% extends 'base.html' %}
{% block title %}All Bookings — EMP{% endblock %}

{% block content %}
<h2>All Bookings</h2>
<table class="table table-striped mt-3">
    <thead>
        <tr><th>ID</th><th>Student</th><th>Exam</th><th>Slot Date</th><th>Examiner</th><th>Status</th><th>Actions</th></tr>
    </thead>
    <tbody>
        {% for b in bookings %}
        <tr>
            <td>{{ b.id }}</td>
            <td>{{ b.student.name }}</td>
            <td>{{ b.slot.examination.exam_name }}</td>
            <td>{{ b.slot.date }} {{ b.slot.start_time }}</td>
            <td>{{ b.slot.examiner.name }}</td>
            <td><span class="badge bg-info">{{ b.status }}</span></td>
            <td>
                {% if b.status == 'booked' %}
                <a href="{{ url_for('admin.reschedule_booking', booking_id=b.id) }}" class="btn btn-sm btn-outline-primary">Reschedule</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 25. `templates/admin/reschedule.html`

```html
{% extends 'base.html' %}
{% block title %}Reschedule Booking — EMP{% endblock %}

{% block content %}
<h2>Reschedule Booking #{{ booking.id }}</h2>
<p>Student: <strong>{{ booking.student.name }}</strong> | Current Slot: {{ booking.slot.date }} {{ booking.slot.start_time }}</p>
<form method="POST" class="mt-3" style="max-width: 600px;">
    <div class="mb-3">
        <label class="form-label">New Slot</label>
        <select class="form-select" name="new_slot_id" required>
            {% for s in slots %}
            <option value="{{ s.id }}">{{ s.date }} {{ s.start_time }}–{{ s.end_time }} ({{ s.available_seats }} seats) — {{ s.examiner.name }}</option>
            {% endfor %}
        </select>
    </div>
    <button type="submit" class="btn btn-primary">Reschedule</button>
    <a href="{{ url_for('admin.bookings') }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 26. `templates/admin/reassign.html`

```html
{% extends 'base.html' %}
{% block title %}Reassign Examiner — EMP{% endblock %}

{% block content %}
<h2>Reassign Examiner for Slot #{{ slot.id }}</h2>
<p>Exam: {{ slot.examination.exam_name }} | Current: {{ slot.examiner.name }}</p>
<form method="POST" class="mt-3" style="max-width: 600px;">
    <div class="mb-3">
        <label class="form-label">New Examiner</label>
        <select class="form-select" name="examiner_id" required>
            {% for e in examiners %}
            <option value="{{ e.id }}" {{ 'selected' if e.id == slot.examiner_id }}>{{ e.name }} ({{ e.email }})</option>
            {% endfor %}
        </select>
    </div>
    <button type="submit" class="btn btn-warning">Reassign</button>
    <a href="{{ url_for('admin.slots') }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 27. `templates/admin/search.html`

```html
{% extends 'base.html' %}
{% block title %}Search — EMP{% endblock %}

{% block content %}
<h2>Search</h2>
<form method="GET" class="mt-3">
    <div class="input-group" style="max-width: 500px;">
        <input type="text" class="form-control" name="q" value="{{ query }}" placeholder="Search by name, email, or ID...">
        <button class="btn btn-primary" type="submit">Search</button>
    </div>
</form>

{% if query %}
<div class="mt-4">
    <h4>Students ({{ results.students | length }})</h4>
    {% if results.students %}
    <table class="table table-sm"><thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
    <tbody>{% for s in results.students %}<tr><td>{{ s.id }}</td><td>{{ s.name }}</td><td>{{ s.email }}</td></tr>{% endfor %}</tbody></table>
    {% else %}<p class="text-muted">No students found.</p>{% endif %}

    <h4>Examiners ({{ results.examiners | length }})</h4>
    {% if results.examiners %}
    <table class="table table-sm"><thead><tr><th>ID</th><th>Name</th><th>Email</th></tr></thead>
    <tbody>{% for e in results.examiners %}<tr><td>{{ e.id }}</td><td>{{ e.name }}</td><td>{{ e.email }}</td></tr>{% endfor %}</tbody></table>
    {% else %}<p class="text-muted">No examiners found.</p>{% endif %}

    <h4>Examinations ({{ results.examinations | length }})</h4>
    {% if results.examinations %}
    <table class="table table-sm"><thead><tr><th>ID</th><th>Name</th><th>Type</th><th>Status</th></tr></thead>
    <tbody>{% for ex in results.examinations %}<tr><td>{{ ex.id }}</td><td>{{ ex.exam_name }}</td><td>{{ ex.exam_type }}</td><td>{{ ex.status }}</td></tr>{% endfor %}</tbody></table>
    {% else %}<p class="text-muted">No examinations found.</p>{% endif %}

    <h4>Bookings ({{ results.bookings | length }})</h4>
    {% if results.bookings %}
    <table class="table table-sm"><thead><tr><th>ID</th><th>Student</th><th>Exam</th><th>Status</th></tr></thead>
    <tbody>{% for b in results.bookings %}<tr><td>{{ b.id }}</td><td>{{ b.student.name }}</td><td>{{ b.slot.examination.exam_name }}</td><td>{{ b.status }}</td></tr>{% endfor %}</tbody></table>
    {% else %}<p class="text-muted">No bookings found.</p>{% endif %}
</div>
{% endif %}
{% endblock %}
```

---

## 28. `templates/examiner/dashboard.html`

```html
{% extends 'base.html' %}
{% block title %}Examiner Dashboard — EMP{% endblock %}

{% block content %}
<h2>Examiner Dashboard</h2>
<div class="row mt-4">
    <div class="col-md-3 mb-3">
        <div class="card text-bg-primary">
            <div class="card-body">
                <h6>Assigned Exams</h6>
                <p class="display-6">{{ assignments | length }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card text-bg-success">
            <div class="card-body">
                <h6>My Slots</h6>
                <p class="display-6">{{ my_slots | length }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card text-bg-info">
            <div class="card-body">
                <h6>Booked Students</h6>
                <p class="display-6">{{ booked_count }}</p>
            </div>
        </div>
    </div>
    <div class="col-md-3 mb-3">
        <div class="card text-bg-warning">
            <div class="card-body">
                <h6>Pending Evals</h6>
                <p class="display-6">{{ pending_evals }}</p>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

---

## 29. `templates/examiner/assigned_exams.html`

```html
{% extends 'base.html' %}
{% block title %}My Examinations — EMP{% endblock %}

{% block content %}
<h2>Assigned Examinations</h2>
<table class="table table-striped mt-3">
    <thead><tr><th>Exam</th><th>Course</th><th>Type</th><th>Status</th><th>Slot Creation Window</th></tr></thead>
    <tbody>
        {% for exam in examinations %}
        <tr>
            <td>{{ exam.exam_name }}</td>
            <td>{{ exam.course.course_name }}</td>
            <td>{{ exam.exam_type }}</td>
            <td><span class="badge bg-info">{{ exam.status }}</span></td>
            <td>{{ exam.slot_creation_start.strftime('%Y-%m-%d %H:%M') }} → {{ exam.slot_creation_end.strftime('%Y-%m-%d %H:%M') }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 30. `templates/examiner/slots.html`

```html
{% extends 'base.html' %}
{% block title %}My Slots — EMP{% endblock %}

{% block content %}
<div class="d-flex justify-content-between align-items-center">
    <h2>My Slots</h2>
    <a href="{{ url_for('examiner.create_slot') }}" class="btn btn-primary">+ Create Slot</a>
</div>

<table class="table table-striped mt-3">
    <thead><tr><th>Exam</th><th>Date</th><th>Time</th><th>Capacity</th><th>Available</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
        {% for s in slots %}
        <tr>
            <td>{{ s.examination.exam_name }}</td>
            <td>{{ s.date }}</td>
            <td>{{ s.start_time }} – {{ s.end_time }}</td>
            <td>{{ s.max_capacity }}</td>
            <td>{{ s.available_seats }}</td>
            <td><span class="badge bg-info">{{ s.status }}</span></td>
            <td>
                <a href="{{ url_for('examiner.booked_students', slot_id=s.id) }}" class="btn btn-sm btn-outline-info">Students</a>
                <a href="{{ url_for('examiner.edit_slot', slot_id=s.id) }}" class="btn btn-sm btn-outline-primary">Edit</a>
                <form method="POST" action="{{ url_for('examiner.delete_slot', slot_id=s.id) }}" style="display:inline;">
                    <button class="btn btn-sm btn-outline-danger">Delete</button>
                </form>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 31. `templates/examiner/slot_form.html`

```html
{% extends 'base.html' %}
{% block title %}{{ 'Edit' if slot else 'Create' }} Slot — EMP{% endblock %}

{% block content %}
<h2>{{ 'Edit' if slot else 'Create' }} Slot</h2>
<form method="POST" class="mt-3" style="max-width: 600px;">
    {% if not slot %}
    <div class="mb-3">
        <label class="form-label">Examination</label>
        <select class="form-select" name="examination_id" required>
            {% for exam in examinations %}
            <option value="{{ exam.id }}">{{ exam.exam_name }} — {{ exam.course.course_name }}</option>
            {% endfor %}
        </select>
    </div>
    {% endif %}
    <div class="mb-3">
        <label class="form-label">Date</label>
        <input type="date" class="form-control" name="date"
               value="{{ slot.date if slot else '' }}" required>
    </div>
    <div class="row">
        <div class="col-md-6 mb-3">
            <label class="form-label">Start Time</label>
            <input type="time" class="form-control" name="start_time"
                   value="{{ slot.start_time.strftime('%H:%M') if slot else '' }}" required>
        </div>
        <div class="col-md-6 mb-3">
            <label class="form-label">End Time</label>
            <input type="time" class="form-control" name="end_time"
                   value="{{ slot.end_time.strftime('%H:%M') if slot else '' }}" required>
        </div>
    </div>
    <div class="mb-3">
        <label class="form-label">Max Capacity</label>
        <input type="number" class="form-control" name="max_capacity"
               value="{{ slot.max_capacity if slot else '' }}" min="1" required>
    </div>
    <button type="submit" class="btn btn-success">{{ 'Update' if slot else 'Create' }}</button>
    <a href="{{ url_for('examiner.slots') }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 32. `templates/examiner/booked_students.html`

```html
{% extends 'base.html' %}
{% block title %}Booked Students — EMP{% endblock %}

{% block content %}
<h2>Booked Students — {{ slot.examination.exam_name }}</h2>
<p>Slot: {{ slot.date }} {{ slot.start_time }}–{{ slot.end_time }}</p>

<table class="table table-striped mt-3">
    <thead><tr><th>Student</th><th>Email</th><th>Booked On</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
        {% for b in bookings %}
        <tr>
            <td>{{ b.student.name }}</td>
            <td>{{ b.student.email }}</td>
            <td>{{ b.booking_date.strftime('%Y-%m-%d %H:%M') }}</td>
            <td><span class="badge bg-info">{{ b.status }}</span></td>
            <td>
                {% if b.status == 'booked' %}
                <a href="{{ url_for('examiner.evaluate', booking_id=b.id) }}" class="btn btn-sm btn-success">Evaluate</a>
                {% elif b.status == 'completed' %}
                <a href="{{ url_for('examiner.evaluate', booking_id=b.id) }}" class="btn btn-sm btn-outline-secondary">View/Edit</a>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
<a href="{{ url_for('examiner.slots') }}" class="btn btn-secondary">Back</a>
{% endblock %}
```

---

## 33. `templates/examiner/evaluate.html`

```html
{% extends 'base.html' %}
{% block title %}Evaluate — EMP{% endblock %}

{% block content %}
<h2>Evaluate: {{ booking.student.name }}</h2>
<p>Exam: {{ booking.slot.examination.exam_name }} | Slot: {{ booking.slot.date }} {{ booking.slot.start_time }}</p>

<form method="POST" class="mt-3" style="max-width: 700px;">
    <table class="table">
        <thead><tr><th>Criterion</th><th>Max</th><th>Score</th><th>Remarks</th></tr></thead>
        <tbody>
            {% for rubric in rubrics %}
            <tr>
                <td>{{ rubric.criterion_name }}<br><small class="text-muted">{{ rubric.description or '' }}</small></td>
                <td>{{ rubric.max_marks }}</td>
                <td>
                    <input type="number" class="form-control" name="marks_{{ rubric.id }}"
                           min="0" max="{{ rubric.max_marks }}" step="0.5"
                           value="{{ existing_evals[rubric.id].marks_awarded if rubric.id in existing_evals else '' }}" required>
                </td>
                <td>
                    <input type="text" class="form-control" name="remarks_{{ rubric.id }}"
                           value="{{ existing_evals[rubric.id].remarks if rubric.id in existing_evals else '' }}">
                </td>
            </tr>
            {% endfor %}
        </tbody>
    </table>
    <button type="submit" class="btn btn-success">Submit Evaluation</button>
    <a href="{{ url_for('examiner.booked_students', slot_id=booking.slot_id) }}" class="btn btn-secondary">Cancel</a>
</form>
{% endblock %}
```

---

## 34. `templates/student/dashboard.html`

```html
{% extends 'base.html' %}
{% block title %}Student Dashboard — EMP{% endblock %}

{% block content %}
<h2>Student Dashboard</h2>

<div class="row mt-4">
    <div class="col-md-4 mb-3">
        <div class="card text-bg-primary">
            <div class="card-body">
                <h6>Available Exams</h6>
                <p class="display-6">{{ available_exams | length }}</p>
                <a href="{{ url_for('student.examinations') }}" class="text-white">Browse →</a>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-success">
            <div class="card-body">
                <h6>Upcoming Bookings</h6>
                <p class="display-6">{{ upcoming | length }}</p>
                <a href="{{ url_for('student.my_bookings') }}" class="text-white">View →</a>
            </div>
        </div>
    </div>
    <div class="col-md-4 mb-3">
        <div class="card text-bg-info">
            <div class="card-body">
                <h6>Completed</h6>
                <p class="display-6">{{ completed | length }}</p>
                <a href="{{ url_for('student.results') }}" class="text-white">Results →</a>
            </div>
        </div>
    </div>
</div>

{% if upcoming %}
<h4 class="mt-4">Upcoming Examinations</h4>
<table class="table table-striped">
    <thead><tr><th>Exam</th><th>Date</th><th>Time</th><th>Examiner</th></tr></thead>
    <tbody>
        {% for b in upcoming %}
        <tr>
            <td>{{ b.slot.examination.exam_name }}</td>
            <td>{{ b.slot.date }}</td>
            <td>{{ b.slot.start_time }} – {{ b.slot.end_time }}</td>
            <td>{{ b.slot.examiner.name }}</td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endif %}
{% endblock %}
```

---

## 35. `templates/student/examinations.html`

```html
{% extends 'base.html' %}
{% block title %}Examinations — EMP{% endblock %}

{% block content %}
<h2>Examinations</h2>

<form method="GET" class="mt-3 mb-3">
    <div class="row g-2">
        <div class="col-md-6">
            <input type="text" class="form-control" name="q" value="{{ search_query }}" placeholder="Search by name...">
        </div>
        <div class="col-md-4">
            <select class="form-select" name="type">
                <option value="">All Types</option>
                {% for t in ['viva', 'practical', 'project_demo', 'assessment'] %}
                <option value="{{ t }}" {{ 'selected' if exam_type == t }}>{{ t | replace('_',' ') | title }}</option>
                {% endfor %}
            </select>
        </div>
        <div class="col-md-2">
            <button class="btn btn-primary w-100" type="submit">Filter</button>
        </div>
    </div>
</form>

<table class="table table-striped">
    <thead><tr><th>Exam</th><th>Course</th><th>Type</th><th>Max Marks</th><th>Status</th><th>Booking Window</th><th>Actions</th></tr></thead>
    <tbody>
        {% for exam in examinations %}
        <tr>
            <td>{{ exam.exam_name }}</td>
            <td>{{ exam.course.course_name }}</td>
            <td>{{ exam.exam_type }}</td>
            <td>{{ exam.max_marks }}</td>
            <td><span class="badge bg-info">{{ exam.status }}</span></td>
            <td>{{ exam.slot_booking_start.strftime('%m/%d %H:%M') }} → {{ exam.slot_booking_end.strftime('%m/%d %H:%M') }}</td>
            <td>
                <a href="{{ url_for('student.available_slots', exam_id=exam.id) }}" class="btn btn-sm btn-outline-primary">View Slots</a>
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 36. `templates/student/available_slots.html`

```html
{% extends 'base.html' %}
{% block title %}Available Slots — EMP{% endblock %}

{% block content %}
<h2>Available Slots — {{ exam.exam_name }}</h2>

{% if already_booked %}
<div class="alert alert-warning">You already have a booking for this examination.</div>
{% endif %}

<table class="table table-striped mt-3">
    <thead><tr><th>Date</th><th>Time</th><th>Examiner</th><th>Available Seats</th><th>Actions</th></tr></thead>
    <tbody>
        {% for s in slots %}
        <tr>
            <td>{{ s.date }}</td>
            <td>{{ s.start_time }} – {{ s.end_time }}</td>
            <td>{{ s.examiner.name }}</td>
            <td>{{ s.available_seats }} / {{ s.max_capacity }}</td>
            <td>
                {% if not already_booked and exam.is_booking_open() and s.available_seats > 0 %}
                <form method="POST" action="{{ url_for('student.book_slot', slot_id=s.id) }}">
                    <button class="btn btn-sm btn-success">Book</button>
                </form>
                {% elif s.available_seats == 0 %}
                <span class="badge bg-danger">Full</span>
                {% else %}
                <span class="text-muted">Unavailable</span>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
<a href="{{ url_for('student.examinations') }}" class="btn btn-secondary">Back</a>
{% endblock %}
```

---

## 37. `templates/student/my_bookings.html`

```html
{% extends 'base.html' %}
{% block title %}My Bookings — EMP{% endblock %}

{% block content %}
<h2>My Bookings</h2>
<table class="table table-striped mt-3">
    <thead><tr><th>Exam</th><th>Date</th><th>Time</th><th>Examiner</th><th>Booked On</th><th>Status</th><th>Actions</th></tr></thead>
    <tbody>
        {% for b in bookings %}
        <tr>
            <td>{{ b.slot.examination.exam_name }}</td>
            <td>{{ b.slot.date }}</td>
            <td>{{ b.slot.start_time }} – {{ b.slot.end_time }}</td>
            <td>{{ b.slot.examiner.name }}</td>
            <td>{{ b.booking_date.strftime('%Y-%m-%d') }}</td>
            <td>
                <span class="badge {{ 'bg-success' if b.status == 'booked' else 'bg-secondary' if b.status == 'cancelled' else 'bg-info' }}">
                    {{ b.status }}
                </span>
            </td>
            <td>
                {% if b.status == 'booked' %}
                <form method="POST" action="{{ url_for('student.cancel_booking', booking_id=b.id) }}" style="display:inline;">
                    <button class="btn btn-sm btn-outline-danger" onclick="return confirm('Cancel this booking?')">Cancel</button>
                </form>
                {% endif %}
            </td>
        </tr>
        {% endfor %}
    </tbody>
</table>
{% endblock %}
```

---

## 38. `templates/student/results.html`

```html
{% extends 'base.html' %}
{% block title %}Results — EMP{% endblock %}

{% block content %}
<h2>My Results</h2>

{% if not results %}
<p class="text-muted mt-3">No results published yet.</p>
{% endif %}

{% for r in results %}
<div class="card mt-3">
    <div class="card-header d-flex justify-content-between">
        <strong>{{ r.booking.slot.examination.exam_name }}</strong>
        <span>Total: {{ r.total_marks }} / {{ r.max_marks }}</span>
    </div>
    <div class="card-body">
        <table class="table table-sm">
            <thead><tr><th>Criterion</th><th>Score</th><th>Max</th><th>Remarks</th></tr></thead>
            <tbody>
                {% for e in r.evaluations %}
                <tr>
                    <td>{{ e.rubric.criterion_name }}</td>
                    <td>{{ e.marks_awarded }}</td>
                    <td>{{ e.rubric.max_marks }}</td>
                    <td>{{ e.remarks or '—' }}</td>
                </tr>
                {% endfor %}
            </tbody>
        </table>
    </div>
</div>
{% endfor %}
{% endblock %}
```

---

## 39. `templates/student/profile.html`

```html
{% extends 'base.html' %}
{% block title %}Profile — EMP{% endblock %}

{% block content %}
<h2>My Profile</h2>
<form method="POST" class="mt-3" style="max-width: 500px;">
    <div class="mb-3">
        <label class="form-label">Name</label>
        <input type="text" class="form-control" name="name" value="{{ current_user.name }}" required>
    </div>
    <div class="mb-3">
        <label class="form-label">Email</label>
        <input type="email" class="form-control" value="{{ current_user.email }}" disabled>
    </div>
    <div class="mb-3">
        <label class="form-label">Department</label>
        <input type="text" class="form-control" name="department" value="{{ current_user.department or '' }}">
    </div>
    <div class="mb-3">
        <label class="form-label">Contact Details</label>
        <input type="text" class="form-control" name="contact_details" value="{{ current_user.contact_details or '' }}">
    </div>
    <button type="submit" class="btn btn-success">Update</button>
</form>
{% endblock %}
```

---

## 40. `static/css/style.css`

```css
/* Custom overrides on top of Bootstrap */

body {
    background-color: #f8f9fa;
}

.card {
    border: none;
    border-radius: 0.75rem;
}

.card .display-6 {
    font-weight: 700;
}

.table th {
    white-space: nowrap;
}

.navbar-brand i {
    margin-right: 0.25rem;
}

.alert {
    border-radius: 0.5rem;
}
```

---

## Summary — File Count

| Location | Files |
|----------|-------|
| Root | `config.py`, `models.py`, `app.py`, `requirements.txt` |
| `routes/` | `__init__.py`, `auth.py`, `admin.py`, `examiner.py`, `student.py` |
| `templates/auth/` | `login.html`, `register.html` |
| `templates/admin/` | `dashboard.html`, `courses.html`, `course_form.html`, `examinations.html`, `exam_form.html`, `rubrics.html`, `rubric_form.html`, `examiners.html`, `assign_examiner.html`, `students.html`, `slots.html`, `bookings.html`, `reschedule.html`, `reassign.html`, `search.html` |
| `templates/examiner/` | `dashboard.html`, `assigned_exams.html`, `slots.html`, `slot_form.html`, `booked_students.html`, `evaluate.html` |
| `templates/student/` | `dashboard.html`, `examinations.html`, `available_slots.html`, `my_bookings.html`, `results.html`, `profile.html` |
| `static/css/` | `style.css` |

**Total: 40 files**

## How to Run

```bash
pip install -r requirements.txt
python app.py
```

Admin login: `admin@emp.com` / `admin123`
