from __future__ import annotations

import typing

import fastapi
from structlog import get_logger

from demo_app.hooks import database
from demo_app.lib import (
    EmployeeDatabase,
    EmployeeFormCreate,
    EmployeeFormUpdate,
    EmployeeInDB,
)

logger = get_logger()
router = fastapi.APIRouter(
    prefix="/employees",
    tags=["Employees"],
    default_response_class=fastapi.responses.JSONResponse,
)


@router.get(
    "/",
    summary="Return all the data corresponding to the employee.",
    status_code=200,
    response_model=typing.List[EmployeeInDB],
)
async def get_all_employee(
    db: EmployeeDatabase = fastapi.Depends(database),
    # logger: BoundLogger = fastapi.Depends(logger),
) -> typing.List[EmployeeInDB]:
    """Get all employees data."""
    values = db.values()
    # raise Exception("BOOM")
    logger.msg("Querying employees", count=len(values))
    return values


@router.get(
    "/lastnames",
    summary="Return all the lastnames of the employee",
    status_code=200,
    response_model=typing.List[str],
)
async def get_all_last_names(
    db: EmployeeDatabase = fastapi.Depends(database),
) -> typing.List[str]:
    """Get all the available employees lastnames."""
    return [employee.lastname for employee in db.values()]


@router.get(
    "/lastnames/{lastname}",
    summary="Return the data available the employee, given its lastnamme",
    status_code=200,
    response_model=EmployeeInDB,
)
async def get_employee_by_lastname(
    lastname: str, db: EmployeeDatabase = fastapi.Depends(database)
) -> EmployeeInDB:
    """Get all the available employees lastnames."""
    return db.find_one(lastname=lastname)


# Put and post endpoints to manipulate employee data
@router.post(
    "/",
    summary="Add a new employee to the file.",
    status_code=202,
    response_model=EmployeeInDB,
)
async def add_employee(
    employee: EmployeeFormCreate,
    db: EmployeeDatabase = fastapi.Depends(database),
) -> EmployeeInDB:
    """Add a new employee"""
    return db.create_one(employee=employee, save=True)


@router.put(
    "/{_id}",
    summary="Edits the data of an employee, given its lastname.",
    status_code=202,
    response_model=EmployeeInDB,
)
async def update_employee(
    _id: str,
    update_data: EmployeeFormUpdate,
    create: bool = fastapi.Query(False),
    db: EmployeeDatabase = fastapi.Depends(database),
) -> EmployeeInDB:
    """Edits the data of an employee, given its lastname."""
    return db.update_one({"id": _id}, update_data, create=create, save=True)


@router.delete(
    "/{_id}",
    summary="Delete the data of an employee.",
    status_code=204,
    response_model=None,
)
async def delete_employee(
    _id: str, db: EmployeeDatabase = fastapi.Depends(database)
) -> None:
    """Edits the data of an employee, given its lastname."""
    db.delete_one({"id": _id}, save=True)
    return None
