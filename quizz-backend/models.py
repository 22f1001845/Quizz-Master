from datetime import datetime, timedelta, timezone

from flask_security import RoleMixin, UserMixin
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()
IST = timezone(timedelta(hours=5, minutes=30))

# ------------------- Association Tables -------------------

# User <-> Role
user_roles = db.Table(
    "user_roles",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("role_id", db.Integer, db.ForeignKey("role.id"), primary_key=True),
)

# User <-> Saved Quizzes
saved_quizzes = db.Table(
    "saved_quizzes",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("quiz_id", db.Integer, db.ForeignKey("quiz.id"), primary_key=True),
)

# User <-> Enrolled Subjects
enrolled_subjects = db.Table(
    "enrolled_subjects",
    db.Column("user_id", db.Integer, db.ForeignKey("user.id"), primary_key=True),
    db.Column("subject_id", db.Integer, db.ForeignKey("subject.id"), primary_key=True),
)


# ------------------- Role Table -------------------
class Role(db.Model, RoleMixin):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), unique=True, nullable=True)
    description = db.Column(db.String(255))


# ------------------- User Table -------------------
class User(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    email = db.Column(db.String(255), unique=True, nullable=True)
    password = db.Column(db.String(255), nullable=True)
    fs_uniquifier = db.Column(db.String(255), unique=True, nullable=True)
    active = db.Column(db.Boolean, default=True)

    fullname = db.Column(db.String(100), nullable=True)
    name_search_term = db.Column(db.String(255), nullable=True)

    dob = db.Column(db.Date, nullable=True)
    gender = db.Column(db.String(50), nullable=True)
    country = db.Column(db.String(100), nullable=True)
    qualification = db.Column(db.String(255), nullable=True)

    roles = db.relationship("Role", secondary=user_roles, backref="users")
    saved_quizzes = db.relationship(
        "Quiz", secondary=saved_quizzes, backref="saved_by_users"
    )
    enrolled_subjects = db.relationship(
        "Subject", secondary=enrolled_subjects, backref="enrolled_users"
    )

    responses = db.relationship(
        "UserResponse", backref="user", cascade="all, delete-orphan"
    )
    scores = db.relationship("Score", backref="user", cascade="all, delete-orphan")
    results = db.relationship("Result", backref="user", cascade="all, delete-orphan")


# ------------------- Subject Table -------------------
class Subject(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    name_search_term = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text, default="")

    chapters = db.relationship(
        "Chapter", backref="subject", cascade="all, delete-orphan"
    )
    quizzes = db.relationship("Quiz", backref="subject", cascade="all, delete-orphan")


# ------------------- Chapter Table -------------------
class Chapter(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(255), nullable=True)
    name_search_term = db.Column(db.String(255), nullable=True)
    description = db.Column(db.Text)

    subjectid = db.Column(
        db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), nullable=True
    )
    quizzes = db.relationship("Quiz", backref="chapter", cascade="all, delete-orphan")


# ------------------- Quiz Table -------------------
class Quiz(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    chapterid = db.Column(
        db.Integer, db.ForeignKey("chapter.id", ondelete="CASCADE"), nullable=True
    )
    chapter_name_search_term = db.Column(db.String(255), nullable=True)

    subjectid = db.Column(
        db.Integer, db.ForeignKey("subject.id", ondelete="CASCADE"), nullable=True
    )
    subject_name_search_term = db.Column(db.String(255), nullable=True)

    date_of_quiz = db.Column(db.Date, nullable=True)
    duration_of_quiz = db.Column(db.Interval, nullable=True)
    remarks = db.Column(db.Text, default="")

    questions = db.relationship(
        "Question", backref="quiz", cascade="all, delete-orphan"
    )
    responses = db.relationship(
        "UserResponse", backref="quiz", cascade="all, delete-orphan"
    )
    scores = db.relationship("Score", backref="quiz", cascade="all, delete-orphan")
    results = db.relationship("Result", backref="quiz", cascade="all, delete-orphan")


# ------------------- Question Table -------------------
class Question(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=True
    )

    question_statement = db.Column(db.Text, nullable=True)
    question_search_term = db.Column(db.Text, nullable=True)

    option1 = db.Column(db.String(255), nullable=True)
    option2 = db.Column(db.String(255), nullable=True)
    option3 = db.Column(db.String(255), nullable=True)
    option4 = db.Column(db.String(255), nullable=True)
    correct_option_id = db.Column(db.Integer, nullable=True)

    responses = db.relationship(
        "UserResponse", backref="question", cascade="all, delete-orphan"
    )


# ------------------- UserResponse Table -------------------
class UserResponse(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=True
    )
    question_id = db.Column(
        db.Integer, db.ForeignKey("question.id", ondelete="CASCADE"), nullable=True
    )

    option_selected = db.Column(db.Integer, nullable=True)


# ------------------- Score Table -------------------
class Score(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=True
    )
    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )

    timestamp_of_attempt = db.Column(db.DateTime, default=lambda: datetime.now(IST))
    correct = db.Column(db.Integer, nullable=True)
    wrong = db.Column(db.Integer, nullable=True)
    unattempted = db.Column(db.Integer, nullable=True)
    total_score = db.Column(db.Integer, nullable=True)
    status = db.Column(db.String(50), nullable=True)


# ------------------- Result Table -------------------
class Result(db.Model):
    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer, db.ForeignKey("user.id", ondelete="CASCADE"), nullable=True
    )
    quiz_id = db.Column(
        db.Integer, db.ForeignKey("quiz.id", ondelete="CASCADE"), nullable=True
    )

    score = db.Column(db.Float, nullable=True)
    correct_answers = db.Column(db.Integer, nullable=True)
    total_questions = db.Column(db.Integer, nullable=True)
    attempted_on = db.Column(db.DateTime, default=lambda: datetime.now(IST))
