from __future__ import annotations

import contextlib
import functools
import logging
from dataclasses import asdict, is_dataclass
from typing import AsyncIterator

from fastapi import Depends, Response
from fastapi_pagination.bases import AbstractPage
from sqlalchemy.ext.asyncio import (
    AsyncAttrs,
    AsyncConnection,
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)
from sqlalchemy.orm import DeclarativeBase, MappedAsDataclass
from sqlalchemy.orm.base import DEFAULT_STATE_ATTR

from server.common.exceptions import not_found
from server.common.fastapi import find_fastapi_param_name
from server.common.http import DataResponse

logger = logging.getLogger(__name__)


class Base(MappedAsDataclass, AsyncAttrs, DeclarativeBase):
    pass


class DatabaseSessionManager:
    def __init__(self):
        self._engine: AsyncEngine | None = None
        self._sessionmaker: async_sessionmaker[AsyncSession] | None = None

    def init(self, url: str, debug: bool = False):
        self._engine = create_async_engine(url, echo=debug)
        self._sessionmaker = async_sessionmaker(self._engine, expire_on_commit=False, future=True, class_=AsyncSession)

    async def close(self):
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        await self._engine.dispose()
        self._engine = None
        self._sessionmaker = None

    @contextlib.asynccontextmanager
    async def connect(self) -> AsyncIterator[AsyncConnection]:
        if self._engine is None:
            raise Exception("DatabaseSessionManager is not initialized")
        async with self._engine.begin() as connection:
            try:
                yield connection
            except Exception:
                await connection.rollback()
                raise

    @contextlib.asynccontextmanager
    async def session(self) -> AsyncIterator[AsyncSession]:
        if self._sessionmaker is None:
            raise Exception("DatabaseSessionManager is not initialized")
        session = self._sessionmaker()
        try:
            yield session
            await session.commit()
        except Exception:
            await session.rollback()
            raise
        finally:
            await session.close()

    # Used for testing
    async def create_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.create_all)

    async def drop_all(self, connection: AsyncConnection):
        await connection.run_sync(Base.metadata.drop_all)


session_manager = DatabaseSessionManager()


async def get_db() -> AsyncIterator[AsyncSession]:
    async with session_manager.session() as session:
        try:
            yield session
        finally:
            await session.close()


class DB(AsyncSession):
    def __new__(cls, db: AsyncSession = Depends(get_db)) -> AsyncSession:
        return db


def _dataclass_to_dict(data):
    if is_dataclass(data):
        return asdict(data)  # type: ignore
    return data


def transactional(handler):
    db_param_name = find_fastapi_param_name(handler, DB)

    @functools.wraps(handler)
    async def wrapped(*args, **kwargs):
        db: DB = kwargs[db_param_name]
        try:
            data = await handler(*args, **kwargs)
            await db.commit()
            data = _dataclass_to_dict(data)
            if hasattr(data, DEFAULT_STATE_ATTR):
                await db.refresh(data)
            if data is None:
                raise not_found("object not found")
            if isinstance(data, AbstractPage):
                data.data = [_dataclass_to_dict(item) for item in data.data]
                return data
            if isinstance(data, Response):
                return data
            return DataResponse(data=data)
        except:
            await db.rollback()
            raise

    return wrapped
