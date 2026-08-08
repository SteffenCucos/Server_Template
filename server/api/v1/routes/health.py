from fastapi import Depends
from service.health_service import HealthService

from ...router import Router
from ...v1 import base_route

router = Router(
    prefix=base_route + "/health",
    tags=["health"],
)


@router.get("")
async def status(
    health_service: HealthService = Depends(HealthService),
):
    return {
        "running": True,
        "database": await health_service.database_health_check(),
    }
