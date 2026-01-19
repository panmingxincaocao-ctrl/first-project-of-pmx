from datetime import datetime

from flask import Flask, jsonify, request
from itsdangerous import BadSignature, SignatureExpired, URLSafeTimedSerializer
from werkzeug.security import check_password_hash, generate_password_hash

from .config import SECRET_KEY
from .database import Base, SessionLocal, engine
from .models import (Course, CourseChapter, Enrollment, PptResource, Role,
                     StudyProgress, User, VideoResource)

app = Flask(__name__)
serializer = URLSafeTimedSerializer(SECRET_KEY)

Base.metadata.create_all(bind=engine)
with SessionLocal() as session:
    if session.query(Role).count() == 0:
        session.add_all(
            [
                Role(name="admin", description="系统管理员"),
                Role(name="teacher", description="教师"),
                Role(name="student", description="学生"),
            ]
        )
        session.commit()


def create_token(user: User):
    payload = {"user_id": user.id, "role": user.role.name}
    return serializer.dumps(payload)


def verify_token(token: str):
    try:
        return serializer.loads(token, max_age=60 * 60 * 8)
    except (BadSignature, SignatureExpired):
        return None


def get_current_user(session):
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return None
    payload = verify_token(auth.replace("Bearer ", "", 1))
    if not payload:
        return None
    return session.get(User, payload["user_id"])


@app.post("/api/auth/register")
def register():
    data = request.json or {}
    required = {"name", "email", "password", "role"}
    if not required.issubset(data):
        return jsonify({"error": "缺少必填字段"}), 400
    with SessionLocal() as session:
        if session.query(User).filter_by(email=data["email"]).first():
            return jsonify({"error": "邮箱已存在"}), 400
        role = session.query(Role).filter_by(name=data["role"]).first()
        if not role:
            return jsonify({"error": "角色不存在"}), 400
        user = User(
            name=data["name"],
            email=data["email"],
            password_hash=generate_password_hash(data["password"]),
            role=role,
        )
        session.add(user)
        session.commit()
        return jsonify({"id": user.id, "role": role.name})


@app.post("/api/auth/login")
def login():
    data = request.json or {}
    with SessionLocal() as session:
        user = session.query(User).filter_by(email=data.get("email")).first()
        if not user or not check_password_hash(user.password_hash, data.get("password", "")):
            return jsonify({"error": "账号或密码错误"}), 401
        return jsonify({"token": create_token(user), "role": user.role.name})


@app.get("/api/courses")
def list_courses():
    with SessionLocal() as session:
        courses = session.query(Course).all()
        return jsonify(
            [
                {
                    "id": course.id,
                    "title": course.title,
                    "description": course.description,
                    "teacher": course.teacher.name,
                    "status": course.status,
                }
                for course in courses
            ]
        )


@app.post("/api/courses")
def create_course():
    data = request.json or {}
    with SessionLocal() as session:
        user = get_current_user(session)
        if not user or user.role.name != "teacher":
            return jsonify({"error": "仅教师可创建课程"}), 403
        course = Course(
            title=data.get("title", ""),
            description=data.get("description", ""),
            teacher=user,
            status="pending",
        )
        session.add(course)
        session.commit()
        return jsonify({"id": course.id, "status": course.status})


@app.post("/api/courses/<int:course_id>/chapters")
def add_chapter(course_id):
    data = request.json or {}
    with SessionLocal() as session:
        user = get_current_user(session)
        course = session.get(Course, course_id)
        if not course:
            return jsonify({"error": "课程不存在"}), 404
        if not user or course.teacher_id != user.id:
            return jsonify({"error": "无权限"}), 403
        chapter = CourseChapter(
            course=course,
            title=data.get("title", ""),
            order_index=data.get("order_index", 1),
        )
        session.add(chapter)
        session.commit()
        return jsonify({"id": chapter.id})


@app.post("/api/chapters/<int:chapter_id>/ppt")
def upload_ppt(chapter_id):
    data = request.json or {}
    with SessionLocal() as session:
        user = get_current_user(session)
        chapter = session.get(CourseChapter, chapter_id)
        if not chapter:
            return jsonify({"error": "章节不存在"}), 404
        if not user or chapter.course.teacher_id != user.id:
            return jsonify({"error": "无权限"}), 403
        ppt = PptResource(
            chapter=chapter,
            file_name=data.get("file_name", ""),
            file_path=data.get("file_path", ""),
            page_count=data.get("page_count", 0),
            editable=bool(data.get("editable", False)),
        )
        session.add(ppt)
        session.commit()
        return jsonify({"id": ppt.id})


@app.post("/api/chapters/<int:chapter_id>/video")
def upload_video(chapter_id):
    data = request.json or {}
    with SessionLocal() as session:
        user = get_current_user(session)
        chapter = session.get(CourseChapter, chapter_id)
        if not chapter:
            return jsonify({"error": "章节不存在"}), 404
        if not user or chapter.course.teacher_id != user.id:
            return jsonify({"error": "无权限"}), 403
        video = VideoResource(
            chapter=chapter,
            title=data.get("title", ""),
            file_path=data.get("file_path", ""),
            duration_seconds=data.get("duration_seconds", 0),
        )
        session.add(video)
        session.commit()
        return jsonify({"id": video.id})


@app.post("/api/courses/<int:course_id>/enroll")
def enroll(course_id):
    with SessionLocal() as session:
        user = get_current_user(session)
        if not user or user.role.name != "student":
            return jsonify({"error": "仅学生可报名"}), 403
        course = session.get(Course, course_id)
        if not course:
            return jsonify({"error": "课程不存在"}), 404
        enrollment = Enrollment(student=user, course=course)
        session.add(enrollment)
        session.commit()
        return jsonify({"enrolled_at": enrollment.enrolled_at.isoformat()})


@app.post("/api/progress")
def update_progress():
    data = request.json or {}
    with SessionLocal() as session:
        user = get_current_user(session)
        if not user or user.role.name != "student":
            return jsonify({"error": "仅学生可记录进度"}), 403
        progress = StudyProgress(
            student=user,
            course_id=data.get("course_id"),
            ppt_id=data.get("ppt_id"),
            video_id=data.get("video_id"),
            current_page=data.get("current_page", 0),
            watched_seconds=data.get("watched_seconds", 0),
            updated_at=datetime.utcnow(),
        )
        session.add(progress)
        session.commit()
        return jsonify({"id": progress.id})


@app.get("/api/progress")
def list_progress():
    with SessionLocal() as session:
        user = get_current_user(session)
        if not user or user.role.name != "student":
            return jsonify({"error": "仅学生可查看"}), 403
        progresses = session.query(StudyProgress).filter_by(student_id=user.id).all()
        return jsonify(
            [
                {
                    "course_id": progress.course_id,
                    "ppt_id": progress.ppt_id,
                    "video_id": progress.video_id,
                    "current_page": progress.current_page,
                    "watched_seconds": progress.watched_seconds,
                    "updated_at": progress.updated_at.isoformat(),
                }
                for progress in progresses
            ]
        )


@app.get("/api/health")
def health():
    return jsonify({"status": "ok"})


if __name__ == "__main__":
    app.run(host="0.0.0.0", port=8000)
