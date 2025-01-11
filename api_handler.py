from mangum import Mangum

from src.main import app
from src.util.logging import get_logger

logger = get_logger(__name__)


logger.info("Setting up lambda handler")


handler = Mangum(app, lifespan="off")

logger.info("lambda handler configured")
