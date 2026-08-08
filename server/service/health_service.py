import logging

from db import DatabaseSettings, MappingSerializer
from db.repository.factory import create_repository

logger = logging.getLogger(__name__)


class HealthService:
    async def database_health_check(self) -> bool:
        repository = None
        try:
            repository = create_repository(
                settings=DatabaseSettings.from_env(),
                resource_name="health",
                serializer=MappingSerializer(),
            )
            await repository.list(limit=1)
            return True
        except Exception as err:
            logger.error(err)
            return False
        finally:
            if repository is not None:
                await repository.close()
