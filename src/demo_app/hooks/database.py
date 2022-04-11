"""This module exposes custom hooks used by the application
"""
from __future__ import annotations

import asyncio
import contextlib
import typing

from starlette.requests import Request
from structlog import get_logger

from demo_app.container import AppContainer
from demo_app.lib import EmployeeDatabase


@contextlib.asynccontextmanager
async def database_hook(
    container: AppContainer,
) -> typing.AsyncIterator[EmployeeDatabase]:
    """A hook providing a database instance in application state."""
    logger = get_logger().bind(logger="database-hook")
    logger.info(f"Opening database in {container.settings.database.path}")
    # Create new database instance using path from settings
    database = EmployeeDatabase(container.settings.database.path)
    # Attach database to application state
    container.app.state.database = database
    # Let the application run (I.E, signal startup complete)
    # The yielded value is not used by the application itself
    # So yielding the database is equivalent to yielding None when application is running
    # However, yielding a value helps writing unit tests.
    try:
        yield database
    # Always clean resources on application shutdown
    finally:
        logger.warning(f"Closing database in {container.settings.database.path}")


async def database_monitor(container: AppContainer) -> None:
    """A task to monitor database health (mocked since db is a file)"""
    logger = get_logger().bind(logger="database-monitor")
    # Access the database from the container
    db: EmployeeDatabase = container.app.state.database
    # Deploying application using docker containers is quite common nowadays
    # A useful trick when working with containers, it to exit the application if it is not healthy
    # It is then the responsability of the orchestrator (kubernetes / swarm / docker / ...) to create a new container
    # This example will check if the database dump is still present in the file system
    # If that's not the case, the application exits with an error message.
    while True:
        logger.debug("Checking connection to database...")
        if not db.path.exists():
            logger.error("Checking connection to database... ERROR")
            logger.critical(
                f"Checking connection to database... Exiting application due to critical error: Database dump not found ({db.path.as_posix()})"
            )
            container.exit_soon()
            return
        logger.info("Checking connection to database... OK")
        await asyncio.sleep(30)


def database(request: Request) -> EmployeeDatabase:
    """Access the employee database from a Starlette/FastAPI request"""
    return request.app.state.database  # type: ignore[no-any-return]
