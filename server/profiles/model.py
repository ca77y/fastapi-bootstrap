from enum import Enum
from typing import Any, Generic, Type, TypeVar
from uuid import UUID

from pydantic import BaseModel
from sqlalchemy import ColumnElement, ForeignKey, Select, and_
from sqlalchemy.orm import Mapped, declared_attr, mapped_column, relationship

from server.common.database import DB, Base
from server.common.model import EntityMixin, TemporalMixin


class ProfileRole(str, Enum):
    USER = "user"
    ADMIN = "admin"


class Profile(TemporalMixin, EntityMixin, Base):
    __tablename__ = "profiles"

    name: Mapped[str] = mapped_column(nullable=False)
    role: Mapped[ProfileRole] = mapped_column(nullable=False, default=ProfileRole.USER)


ProfileRelatedT = TypeVar("ProfileRelatedT", bound="ProfileRelatedEntity")


class ProfileRelatedEntity(EntityMixin, Generic[ProfileRelatedT]):
    profile_id: Mapped[UUID] = mapped_column(ForeignKey("profiles.id"), nullable=False)

    @declared_attr
    def profile(cls) -> Mapped["Profile"]:
        return relationship("Profile", lazy="joined", init=False)

    @classmethod
    def list_query_for_profile(
        cls: Type[ProfileRelatedT],
        profile_id: UUID,
        filter: ColumnElement | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: ColumnElement | None = None,
    ) -> Select:
        if filter is None:
            profile_filter = cls.profile_id == profile_id
        else:
            profile_filter = and_(cls.profile_id == profile_id, filter)
        return cls.list_query(profile_filter, limit, offset, order_by)

    @classmethod
    async def list_for_profile(
        cls: Type[ProfileRelatedT], db: DB, profile_id: UUID, filter: Any = None
    ) -> list[ProfileRelatedT]:
        qs = cls.list_query_for_profile(profile_id, filter)
        res = await db.execute(qs)
        raw = res.unique().all()
        return [r[0] for r in raw]


class ProfileCreateData(BaseModel):
    name: str


class ProfileResponseData(BaseModel):
    id: UUID
    name: str
    role: ProfileRole
