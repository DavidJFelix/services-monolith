#!/usr/bin/env python
from sqlalchemy import Column, DateTime, ForeignKey, String, text
from sqlalchemy.orm import relationship
from ..database import Base

from .uuid import UUID


class BearerToken(Base):
    __tablename__ = "bearer_tokens"

    id = Column(
            UUID,
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
            nullable=False,
    )
    token = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, nullable=False)

    user = relationship('User', back_populates='addresses')
