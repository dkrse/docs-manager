from sqlalchemy import Column, Integer, String, Boolean, DateTime, ForeignKey, Text
from sqlalchemy.orm import relationship, deferred
from datetime import datetime, timezone
from app.database import Base


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String(100), unique=True, nullable=False, index=True)
    hashed_password = Column(String(255), nullable=False)
    is_admin = Column(Boolean, default=False)
    must_change_password = Column(Boolean, default=False)
    created_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))

    documents = relationship("Document", back_populates="uploader")
    settings = relationship("UserSettings", back_populates="user", uselist=False)


class UserSettings(Base):
    __tablename__ = "user_settings"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    page_size = Column(Integer, default=20)
    default_sort = Column(String(20), default="random")
    hidden_hashtags = Column(Text, default="")
    theme = Column(String(10), default="light")
    show_edit = Column(Boolean, default=True)
    show_download = Column(Boolean, default=True)
    show_delete = Column(Boolean, default=True)
    show_line_numbers = Column(Boolean, default=False)

    user = relationship("User", back_populates="settings")


class Document(Base):
    __tablename__ = "documents"

    id = Column(Integer, primary_key=True, index=True)
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_extension = Column(String(10), nullable=False, default=".pdf")
    file_path = Column(String(500), nullable=False)
    thumbnail_path = Column(String(500), nullable=True)
    thumbnail_page = Column(Integer, default=1)
    category = Column(String(100), default="")
    hashtags = Column(Text, default="")
    description = Column(Text, default="")
    notes = Column(Text, default="")
    is_private = Column(Boolean, default=False)
    uploaded_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    uploaded_at = Column(DateTime, default=lambda: datetime.now(timezone.utc))
    updated_at = Column(DateTime, default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    file_size = Column(Integer, default=0)
    document_date = Column(DateTime, nullable=True)
    content_hash = Column(String(64), nullable=False, index=True)
    content = deferred(Column(Text, default=""))
    share_token = Column(String(64), nullable=True, unique=True, index=True)

    uploader = relationship("User", back_populates="documents")
    favorites = relationship("Favorite", back_populates="document", cascade="all, delete-orphan")


class Favorite(Base):
    __tablename__ = "favorites"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    document_id = Column(Integer, ForeignKey("documents.id"), nullable=False)

    user = relationship("User")
    document = relationship("Document", back_populates="favorites")
