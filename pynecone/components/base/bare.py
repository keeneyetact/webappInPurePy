"""A bare component."""
from __future__ import annotations

from typing import Any

from pynecone.components.component import Component
from pynecone.components.tags import Tag
from pynecone.components.tags.tagless import Tagless
from pynecone.var import Var


class Bare(Component):
    """A component with no tag."""

    contents: Var[str]

    @classmethod
    def create(cls, contents: Any) -> Component:
        """Create a Bare component, with no tag.

        Args:
            contents: The contents of the component.

        Returns:
            The component.
        """
        return cls(contents=str(contents))  # type: ignore

    def _render(self) -> Tag:
        contents = str(self.contents)
        if self.state is not None:
            check = f"{{{self.state.get_name()}"
            contents = str(self.contents).replace(check, f"${check}")
        return Tagless(contents=contents)
