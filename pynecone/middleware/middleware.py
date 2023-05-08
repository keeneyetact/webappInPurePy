"""Base Pynecone middleware."""
from __future__ import annotations

from abc import ABC
from typing import TYPE_CHECKING, Optional

from pynecone.base import Base
from pynecone.event import Event
from pynecone.state import State, StateUpdate

if TYPE_CHECKING:
    from pynecone.app import App


class Middleware(Base, ABC):
    """Middleware to preprocess and postprocess requests."""

    async def preprocess(
        self, app: App, state: State, event: Event
    ) -> Optional[StateUpdate]:
        """Preprocess the event.

        Args:
            app: The app.
            state: The client state.
            event: The event to preprocess.

        Returns:
            An optional state update to return.
        """
        return None

    async def postprocess(
        self, app: App, state: State, event: Event, update: StateUpdate
    ) -> StateUpdate:
        """Postprocess the event.

        Args:
            app: The app.
            state: The client state.
            event: The event to postprocess.
            update: The current state update.

        Returns:
            An optional state to return.
        """
        return update
