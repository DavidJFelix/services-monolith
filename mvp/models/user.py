#!/usr/bin/env python
from sqlalchemy import Boolean, Column, DateTime, String, text
from ..database import Base

from .uuid import UUID


class User(Base):
    __tablename__ = "users"

    id = Column(
            UUID,
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
            nullable=False,
    )
    name = Column(String, nullable=False)
    profile_image_url = Column(String, nullable=False)
    phone_number = Column(String, nullable=False)
    email = Column(String, nullable=False)
    created_at = Column(DateTime, nullable=False)
    updated_at = Column(DateTime, nullable=False)
    is_active = Column(Boolean, nullable=False)
