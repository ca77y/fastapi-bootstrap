from uuid import UUID

from pydantic import BaseModel
from sqlalchemy.dialects.postgresql import TEXT
from sqlalchemy.orm import Mapped, mapped_column

from server.common.database import Base
from server.common.model import EntityMixin, TemporalMixin
from server.profiles.model import ProfileRelatedEntity, ProfileResponseData


class Article(ProfileRelatedEntity, TemporalMixin, EntityMixin, Base):
    __tablename__ = "articles"

    title: Mapped[str] = mapped_column(nullable=False)
    content: Mapped[str] = mapped_column(type_=TEXT, nullable=False)


class ArticleResponseData(BaseModel):
    id: UUID
    title: str
    profile: ProfileResponseData


class ArticleCreateData(BaseModel):
    profile_id: UUID
    title: str
    content: str
