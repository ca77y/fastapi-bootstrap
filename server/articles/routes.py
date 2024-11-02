from fastapi import APIRouter, Depends
from fastapi_pagination.bases import AbstractPage
from fastapi_pagination.ext.sqlalchemy import paginate

from server.articles.model import Article, ArticleCreateData, ArticleResponseData
from server.common.database import DB, transactional
from server.common.exceptions import not_found
from server.common.http import DataResponse, PageDataResponse, Params
from server.common.logging import LoggingRoute
from server.common.queue import JobName, ProcessJobData, enqueue
from server.profiles.model import Profile

router = APIRouter(route_class=LoggingRoute)


@router.get("", response_model=PageDataResponse[ArticleResponseData])
@transactional
async def list_articles(params: Params = Depends(), db: DB = Depends()) -> AbstractPage[Article]:
    return await paginate(
        db,
        Article.list_query(order_by=Article.updated_at.desc()),
        params,
    )


@router.post("", response_model=DataResponse[ArticleResponseData])
@transactional
async def create_article(data: ArticleCreateData, db: DB = Depends()) -> Article:
    exists = await Profile.exists(db, Profile.id == data.profile_id)
    if not exists:
        raise not_found(f"Profile {data.profile_id} not found")
    article = Article(title=data.title, content=data.content, profile_id=data.profile_id)
    await article.save(db)
    await enqueue(JobName.process_article_job, ProcessJobData(article_id=article.id))
    await article.awaitable_attrs.profile
    return article
