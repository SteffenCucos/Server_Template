from fastapi import Depends
from service.health_service import HealthService

from ...router import Router
from ...v1 import base_route

router = Router(
    prefix=base_route + "/health",
    tags=["health"]
)

@router.get("")
def status(
    health_service: HealthService = Depends(HealthService)
):
    # https://testfully.io/blog/api-health-check-monitoring/
    return {
        "running": True,
        "mongodb": health_service.mongo_health_check()
    }
