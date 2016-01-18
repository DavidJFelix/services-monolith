#!/usr/bin/env python
from sqlalchemy import Column, ForeignKey, String, text
from sqlalchemy.orm import relationship
from ..database import Base

from .uuid import UUID


class OAuthClaim(Base):
    __tablename__ = "oauth_claims"

    id = Column(
            UUID,
            primary_key=True,
            server_default=text("uuid_generate_v4()"),
            nullable=False,
    )
    oauth_provider_id = Column(UUID, ForeignKey('oauth_providers.id'))
    oauth_provider_uid = Column(String, nullable=False)
    user_id = Column(UUID, ForeignKey('users.id'), nullable=False)

    user = relationship('User', back_populates='oauth_claims')
    oauth_provider = relationship(
            'OAuthProvider',
            back_populates='oauth_claims'
    )
