from pydantic_settings import BaseSettings, SettingsConfigDict
from sqlalchemy.ext.asyncio.engine import AsyncEngine
from sqlalchemy.orm import sessionmaker
from sqlmodel import SQLModel, create_engine
from sqlmodel.ext.asyncio.session import AsyncSession

from src.util.logging import get_logger

logger = get_logger(__name__)


async def create_db_and_tables():
    logger.warning("Running create db_and_tables. This is bad if running in prod")
    async with ENGINE.begin() as conn:
        # await conn.run_sync(SQLModel.metadata.drop_all)
        await conn.run_sync(SQLModel.metadata.create_all)


async def get_session() -> AsyncSession:
    async_session = sessionmaker(ENGINE, class_=AsyncSession, expire_on_commit=False)
    async with async_session() as session:
        yield session


class PG_Settings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="PG_")
    password: str = "password"
    database: str = "companion"
    user: str = "pguser"
    domain: str = "localhost"
    port: str = "5432"
    echo: bool = False
    ssl: bool = False


logger.info("Getting DB settings")
pg_settings: PG_Settings = PG_Settings()
logger.info(f"DB settings loaded as {pg_settings.model_dump_json()}")

DATABASE_URL = f"postgresql+asyncpg://{pg_settings.user}:{pg_settings.password}@{pg_settings.domain}:{pg_settings.port}/{pg_settings.database}"
MIGRATIONS_URL = f"postgresql://{pg_settings.user}:{pg_settings.password}@{pg_settings.domain}:{pg_settings.port}/{pg_settings.database}"
ENGINE = AsyncEngine(create_engine(url=DATABASE_URL, echo=pg_settings.echo, future=True))
logger.info(f"DB URL {DATABASE_URL}")
logger.info(f"migrations URL {MIGRATIONS_URL}")
