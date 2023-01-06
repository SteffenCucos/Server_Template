
import logging

from db.mongodb import client

logger = logging.getLogger(__name__)


class HealthService():
    def __init__(self):
        pass

    def mongo_health_check(self):
        try:
            client.server_info()
            return True
        except Exception as err:
            logger.error(err)
            return False
