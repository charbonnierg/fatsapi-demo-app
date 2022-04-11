"""This module provides error handlers to use within FastAPI application."""
from __future__ import annotations

from typing import Any, Callable, Coroutine, Dict, Type, Union

import fastapi
from starlette.requests import Request
from starlette.responses import Response

from .lib.errors import EmployeeNotFoundError


async def employee_not_found_to_404(
    request: Request, exception: EmployeeNotFoundError
) -> Response:
    """Catch KeyError to return meaningful 404 responses"""
    return fastapi.responses.JSONResponse(
        status_code=404, content={"details": "Employee not found"}
    )


ERROR_HANDLERS: Dict[
    Union[int, Type[Exception]], Callable[[Request, Any], Coroutine[Any, Any, Response]]
] = {EmployeeNotFoundError: employee_not_found_to_404}
