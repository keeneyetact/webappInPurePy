"""Logging middleware."""
from __future__ import annotations

from typing import TYPE_CHECKING

from pynecone.event import Event
from pynecone.middleware.middleware import Middleware
from pynecone.state import State, StateUpdate

if TYPE_CHECKING:
    from pynecone.app import App


class LoggingMiddleware(Middleware):
    """Middleware to log requests and responses."""

    async def preprocess(self, app: App, state: State, event: Event):
        """Preprocess the event.

        Args:
            app: The app to apply the middleware to.
            state: The client state.
            event: The event to preprocess.
        """
        print(f"Event {event}")

    async def postprocess(
        self, app: App, state: State, event: Event, update: StateUpdate
    ):
        """Postprocess the event.

        Args:
            app: The app to apply the middleware to.
            state: The client state.
            event: The event to postprocess.
            update: The current state update.
        """
        print(f"Update {update}")
