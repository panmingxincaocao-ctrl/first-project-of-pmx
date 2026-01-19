from datetime import datetime

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, Text
from sqlalchemy.orm import relationship

from .database import Base


class Role(Base):
    __tablename__ = "roles"

    id = Column(Integer, primary_key=True)
    name = Column(String(32), unique=True, nullable=False)
    description = Column(String(255), nullable=False)

    users = relationship("User", back_populates="role")


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True)
    name = Column(String(80), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    password_hash = Column(String(255), nullable=False)
    role_id = Column(Integer, ForeignKey("roles.id"), nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    role = relationship("Role", back_populates="users")
    courses = relationship("Course", back_populates="teacher")
    enrollments = relationship("Enrollment", back_populates="student")
    progresses = relationship("StudyProgress", back_populates="student")


class Course(Base):
    __tablename__ = "courses"

    id = Column(Integer, primary_key=True)
    title = Column(String(120), nullable=False)
    description = Column(Text, nullable=False)
    teacher_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    status = Column(String(32), default="draft")
    created_at = Column(DateTime, default=datetime.utcnow)

    teacher = relationship("User", back_populates="courses")
    chapters = relationship("CourseChapter", back_populates="course", cascade="all, delete-orphan")
    enrollments = relationship("Enrollment", back_populates="course")


class CourseChapter(Base):
    __tablename__ = "course_chapters"

    id = Column(Integer, primary_key=True)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    title = Column(String(120), nullable=False)
    order_index = Column(Integer, nullable=False)

    course = relationship("Course", back_populates="chapters")
    ppts = relationship("PptResource", back_populates="chapter", cascade="all, delete-orphan")
    videos = relationship("VideoResource", back_populates="chapter", cascade="all, delete-orphan")


class PptResource(Base):
    __tablename__ = "ppt_resources"

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("course_chapters.id"), nullable=False)
    file_name = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    page_count = Column(Integer, default=0)
    editable = Column(Boolean, default=False)

    chapter = relationship("CourseChapter", back_populates="ppts")


class VideoResource(Base):
    __tablename__ = "video_resources"

    id = Column(Integer, primary_key=True)
    chapter_id = Column(Integer, ForeignKey("course_chapters.id"), nullable=False)
    title = Column(String(255), nullable=False)
    file_path = Column(String(255), nullable=False)
    duration_seconds = Column(Integer, default=0)

    chapter = relationship("CourseChapter", back_populates="videos")


class Enrollment(Base):
    __tablename__ = "enrollments"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    enrolled_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="enrollments")
    course = relationship("Course", back_populates="enrollments")


class StudyProgress(Base):
    __tablename__ = "study_progress"

    id = Column(Integer, primary_key=True)
    student_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    course_id = Column(Integer, ForeignKey("courses.id"), nullable=False)
    ppt_id = Column(Integer, ForeignKey("ppt_resources.id"), nullable=True)
    video_id = Column(Integer, ForeignKey("video_resources.id"), nullable=True)
    current_page = Column(Integer, default=0)
    watched_seconds = Column(Integer, default=0)
    updated_at = Column(DateTime, default=datetime.utcnow)

    student = relationship("User", back_populates="progresses")
