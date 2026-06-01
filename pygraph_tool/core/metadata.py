"""Metadata module."""

from __future__ import annotations

from collections.abc import Iterable
from dataclasses import dataclass, field


@dataclass(slots=True)
class Metadata:
    """Generic metadata associated with a graph element.

    Metadata stores graph-level annotations that can be used for filtering,
    categorization, layering, visualization, or application-specific hints.

    Attributes:
        tags: Free-form textual tags associated with the graph element.
        categories: Higher-level categories the graph element belongs to.
        layers: Logical graph layers the graph element belongs to.
        flags: Boolean-like textual markers describing graph-level states.
        properties: Additional user-defined metadata.
    """

    tags: set[str] = field(default_factory=set)
    categories: set[str] = field(default_factory=set)
    layers: set[str] = field(default_factory=set)
    flags: set[str] = field(default_factory=set)
    properties: dict[str, object] = field(default_factory=dict)

    def has_tag(self, tag: str) -> bool:
        """Return whether the metadata contains a tag.

        Args:
            tag: Tag to check.

        Returns:
            True if the tag exists, False otherwise.
        """
        return tag in self.tags

    def has_category(self, category: str) -> bool:
        """Return whether the metadata contains a category.

        Args:
            category: Category to check.

        Returns:
            True if the category exists, False otherwise.
        """
        return category in self.categories

    def has_layer(self, layer: str) -> bool:
        """Return whether the metadata contains a layer.

        Args:
            layer: Layer to check.

        Returns:
            True if the layer exists, False otherwise.
        """
        return layer in self.layers

    def has_flag(self, flag: str) -> bool:
        """Return whether the metadata contains a flag.

        Args:
            flag: Flag to check.

        Returns:
            True if the flag exists, False otherwise.
        """
        return flag in self.flags

    def matches(
        self,
        *,
        tags: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        layers: Iterable[str] | None = None,
        flags: Iterable[str] | None = None,
        match_all: bool = True,
    ) -> bool:
        """Return whether the metadata matches the provided criteria.

        Different criteria are combined with ``AND``. Within each criterion,
        values are matched according to ``match_all``.

        Args:
            tags: Optional tags to match.
            categories: Optional categories to match.
            layers: Optional layers to match.
            flags: Optional flags to match.
            match_all: If True, all expected values within each provided
                criterion must be present. If False, at least one expected
                value within each provided criterion must be present.

        Returns:
            True if the metadata matches all provided criteria, False otherwise.
        """
        return (
            self._matches_values(self.tags, tags, match_all)
            and self._matches_values(self.categories, categories, match_all)
            and self._matches_values(self.layers, layers, match_all)
            and self._matches_values(self.flags, flags, match_all)
        )

    @staticmethod
    def _matches_values(
        existing_values: set[str],
        expected_values: Iterable[str] | None,
        match_all: bool,
    ) -> bool:
        """Return whether existing values match expected values.

        Args:
            existing_values: Existing metadata values.
            expected_values: Expected metadata values. If None or empty, the
                criterion is ignored and returns True.
            match_all: If True, all expected values must be present. If False,
                at least one expected value must be present.

        Returns:
            True if the values match, False otherwise.
        """
        if expected_values is None:
            return True

        expected_values_set = set(expected_values)

        if not expected_values_set:
            return True

        if match_all:
            return expected_values_set.issubset(existing_values)

        return bool(existing_values.intersection(expected_values_set))

    def copy(self) -> Metadata:
        """Return a shallow copy of the metadata.

        Returns:
            A new metadata instance with copied collections.
        """
        return Metadata(
            tags=set(self.tags),
            categories=set(self.categories),
            layers=set(self.layers),
            flags=set(self.flags),
            properties=dict(self.properties),
        )
