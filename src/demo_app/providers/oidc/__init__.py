from __future__ import annotations

from typing import List

import fastapi
from starlette.requests import Request
from starlette.status import HTTP_403_FORBIDDEN

from demo_app.container import AppContainer
from demo_app.providers.oidc.errors import NotAllowedError

from .provider import OIDCAuth, OIDCAuthProvider
from .models import UserClaims

current_user = OIDCAuth()


def get_user(roles: List[str] = []):
    async def _get_current_user_with_roles(
        user: UserClaims = fastapi.Security(current_user),
    ) -> UserClaims:
        if not roles:
            return user
        try:
            user.check_roles(roles)
        except NotAllowedError:
            raise fastapi.HTTPException(
                status_code=HTTP_403_FORBIDDEN,
                detail="Not allowed",
                headers={"WWW-Authenticate": "Bearer"},
            )
        return user

    return fastapi.Depends(_get_current_user_with_roles)


def oidc_provider(container: AppContainer) -> None:
    if container.settings.oidc.enabled:
        # Set client ID on swagger UI
        container.app.swagger_ui_init_oauth[
            "clientId"
        ] = container.settings.oidc.client_id
    # Create oidc provider
    oidc = OIDCAuthProvider(
        issuer_url=container.settings.oidc.issuer_url,
        enabled=container.settings.oidc.enabled,
        algorithms=container.settings.oidc.algorithms,
    )
    if oidc.enabled:
        OIDCAuth.update_model(oidc)
    # Attach oidc provider to app
    container.app.state.oidc = oidc


__all__ = ["oidc_provider", "current_user", "get_user"]
