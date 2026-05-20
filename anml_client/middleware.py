"""HTTP middleware chain for request/response processing."""

from __future__ import annotations

from collections.abc import Awaitable, Callable
from dataclasses import dataclass, field

import httpx


# Middleware function type: takes request, next handler, returns response
MiddlewareFunc = Callable[
    [httpx.Request, Callable[[httpx.Request], Awaitable[httpx.Response]]],
    Awaitable[httpx.Response],
]


@dataclass
class MiddlewareChain:
    """Chain of middleware functions for HTTP request processing."""

    _middlewares: list[MiddlewareFunc] = field(default_factory=list)

    def add(self, middleware: MiddlewareFunc) -> "MiddlewareChain":
        """Add a middleware to the chain.

        Args:
            middleware: The middleware function to add.

        Returns:
            Self for chaining.
        """
        self._middlewares.append(middleware)
        return self

    async def execute(
        self,
        request: httpx.Request,
        send: Callable[[httpx.Request], Awaitable[httpx.Response]],
    ) -> httpx.Response:
        """Execute the middleware chain.

        Args:
            request: The HTTP request.
            send: The final send function.

        Returns:
            The HTTP response after passing through all middleware.
        """
        if not self._middlewares:
            return await send(request)

        async def build_chain(
            index: int,
        ) -> Callable[[httpx.Request], Awaitable[httpx.Response]]:
            if index >= len(self._middlewares):
                return send

            middleware = self._middlewares[index]

            async def next_handler(req: httpx.Request) -> httpx.Response:
                next_fn = await build_chain(index + 1)
                return await next_fn(req)

            async def handler(req: httpx.Request) -> httpx.Response:
                return await middleware(req, next_handler)

            return handler

        handler = await build_chain(0)
        return await handler(request)


async def logging_middleware(
    request: httpx.Request,
    next_handler: Callable[[httpx.Request], Awaitable[httpx.Response]],
) -> httpx.Response:
    """Example middleware that could log requests/responses.

    Args:
        request: The HTTP request.
        next_handler: The next handler in the chain.

    Returns:
        The HTTP response.
    """
    response = await next_handler(request)
    return response


async def user_agent_middleware(
    user_agent: str,
) -> MiddlewareFunc:
    """Create a middleware that sets the User-Agent header.

    Args:
        user_agent: The User-Agent string to set.

    Returns:
        A middleware function.
    """

    async def middleware(
        request: httpx.Request,
        next_handler: Callable[[httpx.Request], Awaitable[httpx.Response]],
    ) -> httpx.Response:
        request.headers["user-agent"] = user_agent
        return await next_handler(request)

    return middleware
