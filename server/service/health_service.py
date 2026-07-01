import logging

from db.connection import DatabaseSettings
from db.repository import MappingSerializer
from db.repository_creation import create_repository

logger = logging.getLogger(__name__)


class HealthService:
    def database_health_check(self) -> bool:
        repository = None
        try:
            repository = create_repository(
                settings=DatabaseSettings.from_env(),
                resource_name="health",
                serializer=MappingSerializer(),
            )
            repository.list(limit=1)
            return True
        except Exception as err:
            logger.error(err)
            return False
        finally:
            if repository is not None:
                repository.close()
