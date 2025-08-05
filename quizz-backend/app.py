import os
from datetime import datetime, timedelta
from functools import wraps

from celery_init import celery_init_app
from flask import Flask, jsonify, request, send_from_directory
from flask_cors import CORS
from flask_jwt_extended import (
    JWTManager,
    create_access_token,
    get_jwt_identity,
    jwt_required,
)
from flask_mail import Mail
from flask_security import Security, SQLAlchemyUserDatastore, hash_password
from flask_sqlalchemy import SQLAlchemy
from models import (
    Chapter,
    Question,
    Quiz,
    Result,
    Role,
    Score,
    Subject,
    User,
    UserResponse,
    db,
)
from redis import StrictRedis
from tasks import csv_report

app = Flask(__name__)
app.config["SECRET_KEY"] = "your_secure_secret_key_here"
app.config["SQLALCHEMY_DATABASE_URI"] = "sqlite:///quizz.db"
app.config["SECURITY_PASSWORD_SALT"] = "your_password_salt"
app.config["JWT_SECRET_KEY"] = "jwt-secret-string"  
app.config["JWT_ACCESS_TOKEN_EXPIRES"] = timedelta(hours=12)
app.config["EXPORTS_FOLDER"] = "exports"


app.config["SECURITY_PASSWORD_HASH"] = "bcrypt"
app.config["SECURITY_EMAIL_VALIDATOR_ARGS"] = {"check_deliverability": False}

app.config["WTF_CSRF_ENABLED"] = False
app.config["SECURITY_CSRF_PROTECT_MECHANISMS"] = []
app.config["SECURITY_CSRF_IGNORE_UNAUTH_ENDPOINTS"] = True
app.config["WTF_CSRF_COOKIE_NAME"] = None
app.config["WTF_CSRF_TIME_LIMIT"] = None
app.config["WTF_CSRF_SSL_STRICT"] = False
app.config["SECURITY_CSRF_HEADER"] = None
app.config["MAIL_SERVER"] = "localhost"
app.config["MAIL_PORT"] = 1025
app.config["MAIL_USE_TLS"] = False
app.config["MAIL_USE_SSL"] = False
app.config["MAIL_DEFAULT_SENDER"] = "admin@quizz.com"

CORS(app)
db.init_app(app)

user_datastore = SQLAlchemyUserDatastore(db, User, Role)
security = Security(app, user_datastore)

jwt = JWTManager(app)

celery = celery_init_app(app)
celery.autodiscover_tasks()

mail = Mail(app)

redis_client = StrictRedis.from_url("redis://localhost:6379/0", decode_responses=True)


# ------------------- Database Initialization ---------------------
def init_database():
    """Initialize database with tables and default admin user"""
    with app.app_context():
        try:
            # Create all tables
            db.create_all()

            # Create admin role if it doesn't exist
            admin_role = Role.query.filter_by(name="admin").first()
            if not admin_role:
                admin_role = Role(name="admin", description="Administrator")
                db.session.add(admin_role)
                db.session.commit()
                print("Created admin role")

            # Create admin user if it doesn't exist
            admin_user = User.query.filter_by(email="admin@quizz.com").first()
            if not admin_user:
                admin_user = user_datastore.create_user(
                    email="admin@quizz.com",
                    password=hash_password("adminpass"),
                    fs_uniquifier=str(datetime.utcnow().timestamp()),
                    fullname="Admin User",
                    name_search_term="admin user",
                    dob=datetime.utcnow().date(),
                    gender="Other",
                    country="India",
                    qualification="N/A",
                    active=True,
                )

                # Add admin role to user
                admin_role = Role.query.filter_by(name="admin").first()
                if admin_role:
                    admin_user.roles.append(admin_role)

                db.session.commit()
                print("Created admin user: admin@quizz.com / adminpass")

            print("Database initialization completed successfully")

        except Exception as e:
            print(f"Error initializing database: {e}")
            db.session.rollback()
            raise


# ------------------- Admin Required Decorator ---------------------
def admin_required(f):
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = get_jwt_identity()
        # Convert back to int for database query
        current_user = User.query.get(int(current_user_id))

        if not current_user or "admin" not in [
            role.name for role in current_user.roles
        ]:
            return jsonify({"message": "Admin access required"}), 403

        return f(current_user, *args, **kwargs)

    return decorated_function


# ------------------- Authentication Routes ---------------------
@app.route("/register", methods=["POST"])
def register():
    data = request.get_json()

    if not data:
        return jsonify({"message": "No data provided"}), 400

    required_fields = [
        "email",
        "password",
        "fullname",
        "dob",
        "gender",
        "country",
        "qualification",
    ]

    # Check for missing fields
    missing = [
        field for field in required_fields if field not in data or not data[field]
    ]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    # Basic email format check
    if "@" not in data["email"] or "." not in data["email"]:
        return jsonify({"message": "Invalid email format"}), 400

    # Check if email already exists
    if User.query.filter_by(email=data["email"]).first():
        return jsonify({"message": "Email already exists"}), 400

    try:
        new_user = user_datastore.create_user(
            email=data["email"],
            password=hash_password(data["password"]),
            fs_uniquifier=str(datetime.utcnow().timestamp()),
            fullname=data["fullname"],
            name_search_term=data["fullname"].lower(),
            dob=datetime.strptime(data["dob"], "%Y-%m-%d").date(),
            gender=data["gender"],
            country=data["country"],
            qualification=data["qualification"],
            active=True,
        )
        db.session.commit()
        return jsonify({"message": "User registered successfully"}), 201

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": "Invalid date format. Use YYYY-MM-DD"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Registration failed", "error": str(e)}), 500


@app.route("/login_main", methods=["POST"])
def login():
    data = request.get_json()

    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"message": "Email and password required"}), 400

    try:
        user = User.query.filter_by(email=data["email"]).first()

        if user and user.verify_and_update_password(data["password"]):
            token = create_access_token(identity=str(user.id))
            return jsonify({"token": token}), 200
        else:
            return jsonify({"message": "Invalid credentials"}), 401

    except Exception as e:
        return jsonify({"message": "Login failed", "error": str(e)}), 500


@app.route("/me", methods=["GET"])
@jwt_required()
def get_me():
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return jsonify({"message": "User not found"}), 404

        return (
            jsonify(
                {
                    "id": current_user.id,
                    "email": current_user.email,
                    "fullname": current_user.fullname,
                    "roles": [r.name for r in current_user.roles],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error fetching user data", "error": str(e)}), 500


# ------------------- User Functionalities ---------------------
@app.route("/subjects", methods=["GET"])
@jwt_required()
def get_subjects():
    try:
        subjects = Subject.query.all()
        return (
            jsonify(
                [
                    {"id": s.id, "name": s.name, "description": s.description}
                    for s in subjects
                ]
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error fetching subjects", "error": str(e)}), 500


@app.route("/quizzes/<int:subject_id>", methods=["GET"])
@jwt_required()
def get_quizzes_by_subject(subject_id):
    try:
        quizzes = Quiz.query.filter_by(subjectid=subject_id).all()
        return (
            jsonify(
                [
                    {
                        "id": q.id,
                        "chapterid": q.chapterid,
                        "subjectid": q.subjectid,
                        "date_of_quiz": q.date_of_quiz.strftime("%Y-%m-%d"),
                        "duration_of_quiz": str(q.duration_of_quiz),
                        "remarks": q.remarks,
                    }
                    for q in quizzes
                ]
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error fetching quizzes", "error": str(e)}), 500


@app.route("/quiz/<int:quiz_id>/questions", methods=["GET"])
@jwt_required()
def get_quiz_questions(quiz_id):
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404

        questions = Question.query.filter_by(quiz_id=quiz_id).all()
        return (
            jsonify(
                {
                    "duration_of_quiz": quiz.duration_of_quiz.total_seconds(),
                    "questions": [
                        {
                            "id": q.id,
                            "question_statement": q.question_statement,
                            "option1": q.option1,
                            "option2": q.option2,
                            "option3": q.option3,
                            "option4": q.option4,
                        }
                        for q in questions
                    ],
                }
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error fetching questions", "error": str(e)}), 500


@app.route("/quiz/<int:quiz_id>/submit", methods=["POST"])
@jwt_required()
def submit_quiz(quiz_id):
    try:
        current_user_id = get_jwt_identity()
        current_user = User.query.get(current_user_id)

        if not current_user:
            return jsonify({"message": "User not found"}), 404

        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        questions = Question.query.filter_by(quiz_id=quiz_id).all()

        if not questions:
            return jsonify({"message": "Quiz not found or has no questions"}), 404

        correct, wrong, unattempted = 0, 0, 0

        for q in questions:
            selected = data.get(str(q.id))
            if selected is None:
                unattempted += 1
                option_selected = -1
            elif int(selected) == q.correct_option_id:
                correct += 1
                option_selected = int(selected)
            else:
                wrong += 1
                option_selected = int(selected)

            response = UserResponse(
                user_id=current_user.id,
                quiz_id=quiz_id,
                question_id=q.id,
                option_selected=option_selected,
            )
            db.session.add(response)

        total_questions = len(questions)
        score = (correct * 100) / total_questions if total_questions > 0 else 0

        result = Result(
            user_id=current_user.id,
            quiz_id=quiz_id,
            score=score,
            correct_answers=correct,
            total_questions=total_questions,
        )
        db.session.add(result)

        score_entry = Score(
            quiz_id=quiz_id,
            user_id=current_user.id,
            correct=correct,
            wrong=wrong,
            unattempted=unattempted,
            total_score=int(score),
            status="completed",
        )
        db.session.add(score_entry)
        db.session.commit()

        return jsonify({"message": "Quiz submitted successfully", "score": score}), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify({"message": "Invalid data format", "error": str(e)}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error submitting quiz", "error": str(e)}), 500


from datetime import datetime

from flask import jsonify


@app.route("/quiz/<int:quiz_id>", methods=["GET"])
@jwt_required()
def get_quiz(quiz_id):
    try:
        quiz = Quiz.query.get(quiz_id)
        if not quiz:
            return jsonify({"message": "Quiz not found"}), 404

        # ✅ Validate date (only allow today's quiz)
        today = datetime.now().date()
        quiz_date = (
            quiz.date_of_quiz.date()
            if hasattr(quiz.date_of_quiz, "date")
            else quiz.date_of_quiz
        )

        if quiz_date != today:
            return jsonify(
                {
                    "message": "You can only attempt the quiz on its scheduled date.",
                    "status": "restricted",
                }
            ), 403

        # ✅ Return quiz details if valid
        questions = [
            {
                "id": q.id,
                "question": q.question_statement,
                "options": [q.option1, q.option2, q.option3, q.option4],
            }
            for q in quiz.questions
        ]

        return jsonify(
            {
                "id": quiz.id,
                "name": quiz.remarks,
                "date": str(quiz.date_of_quiz),
                "duration": quiz.duration_of_quiz.total_seconds(),
                "questions": questions,
            }
        ), 200

    except Exception as e:
        return jsonify({"message": "Error loading quiz", "error": str(e)}), 500


@app.route("/results", methods=["GET"])
@jwt_required()
def get_results():
    try:
        current_user_id = get_jwt_identity()
        results = Result.query.filter_by(user_id=current_user_id).all()
        return (
            jsonify(
                [
                    {
                        "quiz_id": r.quiz_id,
                        "score": r.score,
                        "correct_answers": r.correct_answers,
                        "total_questions": r.total_questions,
                        "attempted_on": (
                            r.attempted_on.strftime("%Y-%m-%d %H:%M:%S")
                            if r.attempted_on
                            else None
                        ),
                    }
                    for r in results
                ]
            ),
            200,
        )
    except Exception as e:
        return jsonify({"message": "Error fetching results", "error": str(e)}), 500


# ------------------- Admin CRUD ---------------------


@app.route("/admin/subject", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def manage_subject(current_user):
    try:
        if request.method == "GET":
            # Retrieve all subjects
            subjects = Subject.query.all()
            return jsonify(
                [
                    {
                        "id": subject.id,
                        "name": subject.name,
                        "description": subject.description,
                    }
                    for subject in subjects
                ]
            ), 200

        elif request.method == "POST":
            # Create a new subject
            data = request.get_json()
            name = data.get("name")
            description = data.get("description")

            if not name:
                return jsonify({"error": "Subject name is required"}), 400

            existing = Subject.query.filter_by(name=name).first()
            if existing:
                return jsonify({"error": "Subject already exists"}), 409

            new_subject = Subject(name=name, description=description)
            db.session.add(new_subject)
            db.session.commit()
            return jsonify({"message": "Subject created successfully"}), 201

        elif request.method == "PUT":
            # Update an existing subject
            data = request.get_json()
            subject_id = data.get("id")
            name = data.get("name")
            description = data.get("description")

            subject = Subject.query.get(subject_id)
            if not subject:
                return jsonify({"error": "Subject not found"}), 404

            if name:
                subject.name = name
            if description:
                subject.description = description

            db.session.commit()
            return jsonify({"message": "Subject updated successfully"}), 200

        elif request.method == "DELETE":
            # Delete a subject
            data = request.get_json()
            subject_id = data.get("id")

            subject = Subject.query.get(subject_id)
            if not subject:
                return jsonify({"error": "Subject not found"}), 404

            db.session.delete(subject)
            db.session.commit()
            return jsonify({"message": "Subject deleted successfully"}), 200

    except Exception as e:
        return jsonify({"error": str(e)}), 500


@app.route("/admin/chapter", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def manage_chapter(current_user):
    try:
        if request.method == "GET":
            chapters = Chapter.query.all()
            return jsonify(
                [
                    {
                        "id": chapter.id,
                        "name": chapter.name,
                        "description": chapter.description,
                        "subjectid": chapter.subjectid,
                    }
                    for chapter in chapters
                ]
            ), 200

        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        if request.method == "POST":
            required_fields = ["name", "subjectid"]
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return jsonify(
                    {"message": f"Missing fields: {', '.join(missing)}"}
                ), 400

            chapter = Chapter(
                name=data["name"],
                name_search_term=data["name"].lower(),
                description=data["description"],
                subjectid=data["subjectid"],
            )
            db.session.add(chapter)

        elif request.method == "PUT":
            if not data.get("id"):
                return jsonify({"message": "ID is required for update"}), 400

            chapter = Chapter.query.get(data["id"])
            if not chapter:
                return jsonify({"message": "Chapter not found"}), 404

            chapter.name = data.get("name", chapter.name)
            chapter.name_search_term = data.get("name", chapter.name).lower()
            chapter.description = data.get("description", chapter.description)

        elif request.method == "DELETE":
            if not data.get("id"):
                return jsonify({"message": "ID is required for deletion"}), 400

            chapter = Chapter.query.get(data["id"])
            if not chapter:
                return jsonify({"message": "Chapter not found"}), 404

            db.session.delete(chapter)

        db.session.commit()
        return jsonify({"message": "Chapter operation successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error managing chapter", "error": str(e)}), 500


@app.route("/admin/quiz", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def manage_quiz(current_user):
    try:
        if request.method == "GET":
            quizzes = Quiz.query.all()
            result = []
            for quiz in quizzes:
                chapter = Chapter.query.get(quiz.chapterid)
                subject = Subject.query.get(quiz.subjectid)
                result.append(
                    {
                        "id": quiz.id,
                        "chapterid": quiz.chapterid,
                        "chapter_name": chapter.name if chapter else None,
                        "subjectid": quiz.subjectid,
                        "subject_name": subject.name if subject else None,
                        "date_of_quiz": quiz.date_of_quiz.strftime("%Y-%m-%d"),
                        "duration_of_quiz": int(
                            quiz.duration_of_quiz.total_seconds() / 60
                        ),
                        "remarks": quiz.remarks,
                    }
                )
            return jsonify(result), 200

        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        if request.method == "POST":
            required_fields = [
                "chapterid",
                "subjectid",
                "date_of_quiz",
                "duration_of_quiz",
            ]
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return jsonify(
                    {"message": f"Missing fields: {', '.join(missing)}"}
                ), 400

            chapter = Chapter.query.get(data["chapterid"])
            subject = Subject.query.get(data["subjectid"])
            if not chapter or not subject:
                return jsonify({"message": "Chapter or Subject not found"}), 404

            quiz = Quiz(
                chapterid=data["chapterid"],
                chapter_name_search_term=chapter.name.lower(),
                subjectid=data["subjectid"],
                subject_name_search_term=subject.name.lower(),
                date_of_quiz=datetime.strptime(data["date_of_quiz"], "%Y-%m-%d").date(),
                duration_of_quiz=timedelta(minutes=int(data["duration_of_quiz"])),
                remarks=data.get("remarks", ""),
            )
            db.session.add(quiz)

        elif request.method == "PUT":
            if not data.get("id"):
                return jsonify({"message": "ID is required for update"}), 400

            quiz = Quiz.query.get(data["id"])
            if not quiz:
                return jsonify({"message": "Quiz not found"}), 404

            quiz.remarks = data.get("remarks", quiz.remarks)
            if data.get("date_of_quiz"):
                quiz.date_of_quiz = datetime.strptime(
                    data["date_of_quiz"], "%Y-%m-%d"
                ).date()
            if data.get("duration_of_quiz"):
                quiz.duration_of_quiz = timedelta(minutes=int(data["duration_of_quiz"]))

        elif request.method == "DELETE":
            if not data.get("id"):
                return jsonify({"message": "ID is required for deletion"}), 400

            quiz = Quiz.query.get(data["id"])
            if not quiz:
                return jsonify({"message": "Quiz not found"}), 404

            db.session.delete(quiz)

        db.session.commit()
        return jsonify({"message": "Quiz operation successful"}), 200

    except ValueError as e:
        db.session.rollback()
        return jsonify(
            {"message": "Invalid date or duration format", "error": str(e)}
        ), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error managing quiz", "error": str(e)}), 500


@app.route("/admin/question", methods=["GET", "POST", "PUT", "DELETE"])
@admin_required
def manage_question(current_user):
    try:
        if request.method == "GET":
            quiz_id = request.args.get("quiz_id")
            if not quiz_id:
                return jsonify({"message": "quiz_id is required in query params"}), 400

            questions = Question.query.filter_by(quiz_id=quiz_id).all()
            result = []
            for q in questions:
                result.append(
                    {
                        "id": q.id,
                        "quiz_id": q.quiz_id,
                        "question_statement": q.question_statement,
                        "option1": q.option1,
                        "option2": q.option2,
                        "option3": q.option3,
                        "option4": q.option4,
                        "correct_option_id": q.correct_option_id,
                    }
                )
            return jsonify(result), 200

        data = request.get_json()
        if not data:
            return jsonify({"message": "No data provided"}), 400

        if request.method == "POST":
            required_fields = [
                "quiz_id",
                "question_statement",
                "option1",
                "option2",
                "option3",
                "option4",
                "correct_option_id",
            ]
            missing = [field for field in required_fields if not data.get(field)]
            if missing:
                return jsonify(
                    {"message": f"Missing fields: {', '.join(missing)}"}
                ), 400

            question = Question(
                quiz_id=data["quiz_id"],
                question_statement=data["question_statement"],
                question_search_term=data["question_statement"].lower(),
                option1=data["option1"],
                option2=data["option2"],
                option3=data["option3"],
                option4=data["option4"],
                correct_option_id=data["correct_option_id"],
            )
            db.session.add(question)

        elif request.method == "PUT":
            if not data.get("id"):
                return jsonify({"message": "ID is required for update"}), 400

            question = Question.query.get(data["id"])
            if not question:
                return jsonify({"message": "Question not found"}), 404

            question.question_statement = data.get(
                "question_statement", question.question_statement
            )
            question.question_search_term = data.get(
                "question_statement", question.question_statement
            ).lower()
            question.option1 = data.get("option1", question.option1)
            question.option2 = data.get("option2", question.option2)
            question.option3 = data.get("option3", question.option3)
            question.option4 = data.get("option4", question.option4)
            question.correct_option_id = data.get(
                "correct_option_id", question.correct_option_id
            )

        elif request.method == "DELETE":
            if not data.get("id"):
                return jsonify({"message": "ID is required for deletion"}), 400

            question = Question.query.get(data["id"])
            if not question:
                return jsonify({"message": "Question not found"}), 404

            db.session.delete(question)

        db.session.commit()
        return jsonify({"message": "Question operation successful"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Error managing question", "error": str(e)}), 500


@app.route("/admin/summary")
def admin_summary():
    subjects_count = Subject.query.count()
    quizzes_count = Quiz.query.count()
    users_count = User.query.count()
    return jsonify(
        {"subjects": subjects_count, "quizzes": quizzes_count, "users": users_count}
    )


@app.route("/admin/chart-data", methods=["GET"])
@admin_required
def admin_chart_data(current_user):
    try:
        # Top 5 quizzes by attempts
        quiz_stats = (
            db.session.query(Quiz.id, Quiz.remarks, db.func.count(Result.id))
            .join(Result, Result.quiz_id == Quiz.id)
            .group_by(Quiz.id)
            .order_by(db.func.count(Result.id).desc())
            .limit(5)
            .all()
        )

        quizzes = [
            {"quiz_name": q[1] or f"Quiz {q[0]}", "attempts": q[2]} for q in quiz_stats
        ]

        # Score distribution
        score_ranges = [0, 0, 0, 0]  # 0-30, 30-60, 60-90, 90-100
        results = Result.query.with_entities(Result.score).all()
        for r in results:
            if r.score < 30:
                score_ranges[0] += 1
            elif r.score < 60:
                score_ranges[1] += 1
            elif r.score < 90:
                score_ranges[2] += 1
            else:
                score_ranges[3] += 1

        return jsonify({"quizData": quizzes, "scoreData": score_ranges}), 200
    except Exception as e:
        return jsonify({"message": "Error fetching chart data", "error": str(e)}), 500


@app.route("/admin/users", methods=["GET"])
@jwt_required()
def get_all_users():
    current_user_id = get_jwt_identity()
    current_user = User.query.get(int(current_user_id))

    # Ensure only admin
    if not current_user or "admin" not in [role.name for role in current_user.roles]:
        return jsonify({"error": "Access denied"}), 403

    users = User.query.all()
    return jsonify(
        [
            {
                "id": u.id,
                "username": u.email,
                "fullname": u.fullname,
                "email": u.email,
            }
            for u in users
        ]
    )


@app.route("/admin/search", methods=["GET"])
@jwt_required()
def admin_search():
    # Ensure only admin can search
    current_user = get_jwt_identity()
    user = User.query.filter_by(id=current_user).first()
    if "admin" not in [role.name for role in user.roles]:
        return jsonify({"error": "Access denied"}), 403

    query = request.args.get("q", "").strip()
    if not query:
        return jsonify({"users": [], "quizzes": [], "subjects": []})

    # Perform case-insensitive search
    users = User.query.filter(User.fullname.ilike(f"%{query}%")).all()

    quizzes = Quiz.query.filter(Quiz.remarks.ilike(f"%{query}%")).all()
    subjects = Subject.query.filter(Subject.name.ilike(f"%{query}%")).all()
    chapters = Chapter.query.filter(Chapter.name.ilike(f"%{query}%")).all()

    return jsonify(
        {
            "users": [
                {"id": u.id, "username": u.email, "fullname": u.fullname} for u in users
            ],
            "quizzes": [{"id": q.id, "name": q.remarks} for q in quizzes],
            "subjects": [{"id": s.id, "name": s.name} for s in subjects],
            "chapters": [{"id": c.id, "name": c.name} for c in chapters],
        }
    )


# ------------------- CSV Export Routes ---------------------
@app.route("/admin/export-users-csv", methods=["POST"])
@admin_required
def export_users_csv(current_user):
    task = csv_report.delay()
    return jsonify({"task_id": task.id})


@app.route("/download/<task_id>")
def download(task_id):
    task = celery.AsyncResult(task_id)
    if task.state == "SUCCESS":
        file_path_in_container = task.result["url"]
        filename = os.path.basename(file_path_in_container)
        return send_from_directory(
            app.config["EXPORTS_FOLDER"], filename, as_attachment=True
        )
    elif task.state == "FAILURE":
        return jsonify({"status": "FAILURE", "message": str(task.info)})
    else:
        return jsonify({"status": task.state})


# ------------------- Error Handlers ---------------------
@app.errorhandler(404)
def not_found(error):
    return jsonify({"message": "Resource not found"}), 404


@app.errorhandler(500)
def internal_error(error):
    db.session.rollback()
    return jsonify({"message": "Internal server error"}), 500


init_database()

if __name__ == "__main__":
    app.run(debug=True)
