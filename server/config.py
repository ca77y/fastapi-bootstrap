from pydantic import BaseModel, PostgresDsn
from pydantic_settings import BaseSettings, SettingsConfigDict


class Task(BaseModel):
    job_max_tries: int = 5


class Datastores(BaseModel):
    redis_url: str = "redis://localhost:6379"
    database_url: PostgresDsn = "postgresql://postgres:postgres@localhost:5432/example"  # type: ignore

    @property
    def sqlalchemy_database_url(self):
        return (
            str(self.database_url)
            .replace("postgres://", "postgresql+asyncpg://")
            .replace("postgresql://", "postgresql+asyncpg://")
        )


class GlobalSettings(BaseSettings):
    environment: str = "local"
    debug: bool = False
    datastores: Datastores = Datastores()
    task: Task = Task()

    model_config = SettingsConfigDict(env_file=".env", extra="ignore", env_nested_delimiter="__")

    def is_local(self) -> bool:
        return self.environment == "local"

    def is_dev(self) -> bool:
        return self.environment in ["local", "test", "dev"]


settings = GlobalSettings()
