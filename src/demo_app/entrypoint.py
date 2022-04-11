"""This module exposes the container holding the application.

Routers and hooks are registered in this module.
"""
from __future__ import annotations

import pathlib
import typing

from fastapi import FastAPI

from demo_app.settings import AppSettings

from .container import AppContainer
from .hooks.database import database_hook, database_monitor
from .providers.logger import structured_logging_provider
from .providers.metrics import prometheus_metrics_provider
from .providers.tracing import openelemetry_traces_provider
from .routes import debug_router, employees_router


def create_container(
    settings: typing.Optional[AppSettings] = None,
    config_file: typing.Union[pathlib.Path, str, None] = None,
) -> AppContainer:
    """Application container factory.

    Modify this function to include new routers, new hooks or new providers.

    Returns:
        A new application container.
    """
    # Create an application container
    return AppContainer(
        # Config file can be either a file, a path or None
        config_file=config_file,
        # Settings must be an instance of AppSettings
        settings=settings or AppSettings(),
        routers=[
            # Router can be APIRouter instances
            employees_router,
            # Or functions. Function must either return None or an APIRouter instance
            lambda container: debug_router if container.settings.server.debug else None,
        ],
        # Hooks are coroutine functions which accept an application container and return an async context manager
        hooks=[database_hook],
        # Tasks are similar to hooks but can be created out of coroutines instead of async context managers
        # Tasks are simply cancelled on application exit. If you need a more sophisticated exit mechanism, use a hook.
        # Tasks can be accessed within endpoints. It is possible to get task status, stop task, start task, restart task.
        tasks=[database_monitor],
        # Providers are functions which accept an application container and return None
        providers=[
            prometheus_metrics_provider,
            openelemetry_traces_provider,
            structured_logging_provider,
        ],
    )


def create_app(settings: typing.Optional[AppSettings] = None) -> FastAPI:
    """Application instance factory"""
    # Container is accessible from application state:
    # app = create_app()
    # app.state.container
    return create_container(settings).app
