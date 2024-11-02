from fastapi import APIRouter, Depends
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.sqlalchemy import paginate

from server.common.database import DB, transactional
from server.common.http import DataResponse, PageDataResponse, Params
from server.common.logging import LoggingRoute
from server.profiles.model import Profile, ProfileCreateData, ProfileResponseData

router = APIRouter(route_class=LoggingRoute)


@router.get("", response_model=PageDataResponse[ProfileResponseData])
@transactional
async def list_profiles(params: Params = Depends(), db: DB = Depends()) -> AbstractPage[Profile]:
    return await paginate(
        db,
        Profile.list_query(order_by=Profile.name.asc()),
        params,
    )


@router.post("", response_model=DataResponse[ProfileResponseData])
@transactional
async def create_profile(data: ProfileCreateData, db: DB = Depends()) -> Profile:
    profile = Profile(name=data.name)
    await profile.save(db)
    return profile
