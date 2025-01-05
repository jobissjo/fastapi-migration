import logging

logging.basicConfig(
    level=logging.INFO,
    format='%(levelname)s - %(name)s  - %(message)s - %(asctime)s'
)

logger = logging.getLogger(__name__)
