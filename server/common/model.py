import logging
from datetime import datetime
from typing import Dict, Generic, List, Tuple, Type, TypeVar
from uuid import UUID, uuid4

from sqlalchemy import ColumnElement, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import Mapped, MappedAsDataclass, mapped_column
from sqlalchemy.sql import Select, and_, select

from server.common.exceptions import not_found

EntityT = TypeVar("EntityT", bound="EntityMixin")
TemporalT = TypeVar("TemporalT", bound="TemporalMixin")
logger = logging.getLogger(__name__)


class EntityMixin(MappedAsDataclass, Generic[EntityT]):
    id: Mapped[UUID] = mapped_column(primary_key=True, default_factory=uuid4, init=False)

    @classmethod
    def get_query(cls: Type[EntityT], entity_id: UUID, filter: ColumnElement | None = None) -> Select[Tuple[EntityT]]:
        qs = select(cls)
        if filter is None:
            return qs.where(cls.id == entity_id)
        else:
            return qs.where(and_(cls.id == entity_id, filter))

    @classmethod
    async def get(
        cls: Type[EntityT], db: AsyncSession, entity_id: UUID, filter: ColumnElement | None = None
    ) -> EntityT:
        qs = cls.get_query(entity_id, filter)
        res = await db.execute(qs)
        obj = res.unique().scalar_one_or_none()
        if obj is None:
            raise not_found(f"Entity {cls.__name__} with id {entity_id} not found")
        return obj

    @classmethod
    async def find(cls: Type[EntityT], db: AsyncSession, *, filter: ColumnElement) -> EntityT | None:
        qs = select(cls).where(filter)
        res = await db.execute(qs)
        return res.unique().scalar_one_or_none()

    @classmethod
    async def find_or_create(cls: Type[EntityT], db: AsyncSession, *, filter: ColumnElement, defaults: Dict) -> EntityT:
        entity = await cls.find(db, filter=filter)
        if entity is None:
            entity = cls(**defaults)
            db.add(entity)
            await db.flush()
        return entity

    async def save(self, db: AsyncSession) -> None:
        db.add(self)
        await db.flush()

    @classmethod
    def list_query(
        cls: Type[EntityT],
        filter: ColumnElement | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: ColumnElement | None = None,
    ) -> Select[Tuple[EntityT]]:
        qs = select(cls)
        qs = qs if filter is None else qs.where(filter)
        qs = qs if limit is None else qs.limit(limit)
        qs = qs if offset is None else qs.offset(offset)
        qs = qs if order_by is None else qs.order_by(order_by)
        return qs

    @classmethod
    async def list(
        cls: Type[EntityT],
        db: AsyncSession,
        filter: ColumnElement | None = None,
        limit: int | None = None,
        offset: int | None = None,
        order_by: ColumnElement | None = None,
    ) -> list[EntityT]:
        qs = cls.list_query(filter, limit, offset, order_by)
        res = await db.execute(qs)
        raw = res.unique().all()
        return [r[0] for r in raw]

    @classmethod
    async def delete(cls: Type[EntityT], db: AsyncSession, entity_id: UUID) -> bool:
        qs = select(cls).where(cls.id == entity_id)
        res = await db.execute(qs)
        entity = res.scalar_one_or_none()
        if entity is None:
            return False
        else:
            await db.delete(entity)
            return True

    @classmethod
    async def exists_all(cls: Type[EntityT], db: AsyncSession, entity_ids: List[UUID]) -> bool:
        ids = set(entity_ids)
        query = select(func.count(cls.id)).where(cls.id.in_(ids))
        res = await db.execute(query)
        return res.scalar_one() == len(ids)

    @classmethod
    async def exists(cls: Type[EntityT], db: AsyncSession, criteria: ColumnElement) -> bool:
        query = select(func.count(cls.id)).where(criteria)
        res = await db.execute(query)
        return res.scalar_one() > 0


class TemporalMixin(MappedAsDataclass, Generic[TemporalT]):
    created_at: Mapped[datetime] = mapped_column(default_factory=datetime.utcnow, nullable=False, init=False)
    updated_at: Mapped[datetime] = mapped_column(
        default_factory=datetime.utcnow,
        nullable=False,
        onupdate=func.current_timestamp().op("AT TIME ZONE")("UTC"),
        init=False,
    )

    @classmethod
    async def find_by_created_at_day(cls: Type[TemporalT], db: AsyncSession, created_at: datetime) -> list[TemporalT]:
        start = created_at.replace(hour=0, minute=0, second=0, microsecond=0)
        end = created_at.replace(hour=23, minute=59, second=59, microsecond=999999)
        query = select(cls).where(cls.created_at.between(start, end))
        res = await db.execute(query)
        raw = res.unique().all()
        return [r[0] for r in raw]
