from datetime import datetime
from typing import Generic, List, TypeVar

from fastapi import Request
from fastapi.params import Query
from fastapi_pagination.bases import AbstractPage, AbstractParams, RawParams
from pydantic import BaseModel, ConfigDict
from starlette.datastructures import Headers

DataT = TypeVar("DataT")
ActionT = TypeVar("ActionT")

DEFAULT_DATETIME_FORMAT = "%Y-%m-%dT%H:%M:%S.%fZ"


class DataResponse(BaseModel, Generic[DataT]):
    data: DataT

    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.strftime(DEFAULT_DATETIME_FORMAT)})


class PaginationData(BaseModel):
    total: int
    page: int
    size: int


class Params(BaseModel, AbstractParams):
    page: int = Query(1, ge=1, description="Page number")  # type: ignore
    size: int = Query(10, ge=1, le=100, description="Page size")  # type: ignore

    def to_raw_params(self) -> RawParams:
        return RawParams(
            limit=self.size,
            offset=self.size * (self.page - 1),
        )


class PageDataResponse(AbstractPage[DataT], Generic[DataT]):
    data: List[DataT]
    pagination: PaginationData

    model_config = ConfigDict(json_encoders={datetime: lambda dt: dt.strftime(DEFAULT_DATETIME_FORMAT)})

    @classmethod
    def create(
        cls,
        items: List[DataT],
        total: int,
        params: Params,
    ) -> "PageDataResponse[DataT]":
        return cls(data=items, pagination=PaginationData(total=total, page=params.page, size=params.size))


def set_request_header(request: Request, key: str, value: str):
    headers = dict(request.headers.items())
    headers[key] = value
    request._headers = Headers(headers)
    request.scope.update(headers=request.headers.raw)
