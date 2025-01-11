import alembic.config
from src.util.logging import get_logger

logger = get_logger(__name__)


logger.info("Setting up lambda handler")

alembicArgs = [
    "--raiseerr",
    "upgrade",
    "head",
]


def handler(event, content)->None:
    logger.info("Starting Migration")
    alembic.config.main(argv=alembicArgs)
    logger.info("Migration Complete")


logger.info("Handler complete")

if __name__ == "__main__":
    handler(None, None)
