from datetime import datetime, date, time

from flask_login import UserMixin
from flask_sqlalchemy import SQLAlchemy
from werkzeug.security import generate_password_hash, check_password_hash

db = SQLAlchemy()


# USER

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



# COURSE

class Course(db.Model):
    __tablename__ = 'courses'

    id = db.Column(db.Integer, primary_key=True)
    course_code = db.Column(db.String(20), unique=True, nullable=False)
    course_name = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text)
    status = db.Column(db.String(20), default='active', nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    examinations = db.relationship('Examination', backref='course', lazy=True)



# EXAMINATION

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
# RUBRIC
class Rubric(db.Model):
    __tablename__ = 'rubrics'

    id = db.Column(db.Integer, primary_key=True)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    criterion_name = db.Column(db.String(200), nullable=False)
    max_marks = db.Column(db.Integer, nullable=False)
    weightage = db.Column(db.Float, default=1.0, nullable=False)
    description = db.Column(db.Text)

    evaluations = db.relationship('Evaluation', backref='rubric', lazy=True)

# EXAMINATION SLOT
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

# BOOKING
class Booking(db.Model):
    __tablename__ = 'bookings'
    id = db.Column(db.Integer, primary_key=True)
    student_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    slot_id = db.Column(db.Integer, db.ForeignKey('examination_slots.id'), nullable=False)
    booking_date = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    status = db.Column(db.String(20), default='booked', nullable=False)
    evaluations = db.relationship('Evaluation', backref='booking', lazy=True, cascade='all, delete-orphan')


# EVALUATION
class Evaluation(db.Model):
    __tablename__ = 'evaluations'
    id = db.Column(db.Integer, primary_key=True)
    booking_id = db.Column(db.Integer, db.ForeignKey('bookings.id'), nullable=False)
    rubric_id = db.Column(db.Integer, db.ForeignKey('rubrics.id'), nullable=False)
    marks_awarded = db.Column(db.Float, nullable=False)
    remarks = db.Column(db.Text)
    evaluated_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

# EXAMINER ASSIGNMENT
class ExaminerAssignment(db.Model):
    __tablename__ = 'examiner_assignments'

    id = db.Column(db.Integer, primary_key=True)
    examiner_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    examination_id = db.Column(db.Integer, db.ForeignKey('examinations.id'), nullable=False)
    assigned_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    __table_args__ = (
        db.UniqueConstraint('examiner_id', 'examination_id', name='uq_examiner_exam'),
    )
