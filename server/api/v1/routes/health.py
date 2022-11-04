from fastapi import Depends

from ...v1 import base_route
from ...router import Router

from service.health_service import HealthService

router = Router(
    prefix=base_route + "/health",
    tags=["health"]
)


@router.get("")
def status(
    healthService: HealthService = Depends(HealthService)
):
    # https://testfully.io/blog/api-health-check-monitoring/
    return {
        "running": True,
        "mongodb": healthService.mongo_health_check()
    }
