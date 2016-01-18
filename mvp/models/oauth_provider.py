#!/usr/bin/env python
from sqlalchemy import Column, String, text
from ..database import Base

from .uuid import UUID


class OAuthProvider(Base):
    __tablename__ = "oauth_providers"

    id = Column(
            UUID,
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
            nullable=False,
    )
    name = Column(
            String,
            primary_key=True,
            nullable=False
    )
