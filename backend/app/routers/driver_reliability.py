
from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    Path
)

from app.routers.driver_listing import (
    require_verified_student
)

from app.schemas.driver_reliability import (
    DriverReliabilityResponse
)

from app.services.driver_reliability import (
    get_driver_reliability
)


router = APIRouter(
    prefix="/drivers",
    tags=["Driver Reliability"]
)


@router.get(
    "/{driver_id}/reliability",
    response_model=DriverReliabilityResponse
)
def retrieve_driver_reliability(
    driver_id: int = Path(gt=0),
    is_verified_student: bool = Depends(
        require_verified_student
    )
):
    """
    Retrieve available reliability information
    for a driver.
    """

    if not is_verified_student:
        raise HTTPException(
            status_code=403,
            detail=(
                "Only verified FAST students "
                "can view driver reliability information."
            )
        )

    return get_driver_reliability(driver_id)
