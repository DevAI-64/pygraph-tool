"""Fluent query over graph edges."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

from pygraph_tool.core.edge import Edge
from pygraph_tool.exceptions.graph_exceptions import GraphException

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph


class EdgeQuery[NodeValueT, EdgeValueT]:
    """Fluent query over graph edges."""

    def __init__(
        self,
        graph: Graph[NodeValueT, EdgeValueT],
        edges: Iterable[Edge[NodeValueT, EdgeValueT]],
    ) -> None:
        """Initialize an edge query.

        Args:
            graph: Source graph queried by this object.
            edges: Current edge selection.
        """
        self._graph: Graph[NodeValueT, EdgeValueT] = graph
        self._edges: tuple[Edge[NodeValueT, EdgeValueT], ...] = tuple(edges)

    def where(
        self,
        predicate: Callable[[Edge[NodeValueT, EdgeValueT]], bool],
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges with a predicate.

        Args:
            predicate: Function used to keep or reject edges.

        Returns:
            A new edge query containing matching edges.
        """
        return self._clone(edge for edge in self._edges if predicate(edge))

    def with_tag(self, tag: str) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges containing a metadata tag.

        Args:
            tag: Expected metadata tag.

        Returns:
            A new edge query containing matching edges.
        """
        return self.with_tags([tag])

    def with_category(self, category: str) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges containing a metadata category.

        Args:
            category: Expected metadata category.

        Returns:
            A new edge query containing matching edges.
        """
        return self.with_categories([category])

    def with_layer(self, layer: str) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges containing a metadata layer.

        Args:
            layer: Expected metadata layer.

        Returns:
            A new edge query containing matching edges.
        """
        return self.with_layers([layer])

    def with_flag(self, flag: str) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges containing a metadata flag.

        Args:
            flag: Expected metadata flag.

        Returns:
            A new edge query containing matching edges.
        """
        return self.with_flags([flag])

    def with_tags(
        self,
        tags: Iterable[str],
        *,
        match_all: bool = True,
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges by metadata tags.

        Args:
            tags: Expected metadata tags.
            match_all: Whether all expected tags must be present.

        Returns:
            A new edge query containing matching edges.
        """
        return self.where(
            lambda edge: edge.metadata.matches(tags=tags, match_all=match_all)
        )

    def with_categories(
        self,
        categories: Iterable[str],
        *,
        match_all: bool = True,
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges by metadata categories.

        Args:
            categories: Expected metadata categories.
            match_all: Whether all expected categories must be present.

        Returns:
            A new edge query containing matching edges.
        """
        return self.where(
            lambda edge: edge.metadata.matches(
                categories=categories, match_all=match_all
            )
        )

    def with_layers(
        self,
        layers: Iterable[str],
        *,
        match_all: bool = True,
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges by metadata layers.

        Args:
            layers: Expected metadata layers.
            match_all: Whether all expected layers must be present.

        Returns:
            A new edge query containing matching edges.
        """
        return self.where(
            lambda edge: edge.metadata.matches(layers=layers, match_all=match_all)
        )

    def with_flags(
        self,
        flags: Iterable[str],
        *,
        match_all: bool = True,
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Filter edges by metadata flags.

        Args:
            flags: Expected metadata flags.
            match_all: Whether all expected flags must be present.

        Returns:
            A new edge query containing matching edges.
        """
        return self.where(
            lambda edge: edge.metadata.matches(flags=flags, match_all=match_all)
        )

    def limit(self, limit: int) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Limit the number of selected edges.

        Args:
            limit: Maximum number of edges to keep.

        Raises:
            GraphException: If limit is negative.

        Returns:
            A new edge query containing at most limit edges.
        """
        if limit < 0:
            raise GraphException("limit must be greater than or equal to 0.")
        return self._clone(self._edges[:limit])

    def first(self) -> Edge[NodeValueT, EdgeValueT] | None:
        """Return the first selected edge.

        Returns:
            The first edge, or None if the query is empty.
        """
        return self._edges[0] if self._edges else None

    def count(self) -> int:
        """Return the number of selected edges.

        Returns:
            Number of selected edges.
        """
        return len(self._edges)

    def exists(self) -> bool:
        """Return whether the query contains at least one edge.

        Returns:
            True if at least one edge is selected, False otherwise.
        """
        return bool(self._edges)

    def to_list(self) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return selected edges as a list.

        Returns:
            List of selected edges.
        """
        return list(self._edges)

    def to_tuple(self) -> tuple[Edge[NodeValueT, EdgeValueT], ...]:
        """Return selected edges as a tuple.

        Returns:
            Tuple of selected edges.
        """
        return self._edges

    def _clone(
        self,
        edges: Iterable[Edge[NodeValueT, EdgeValueT]],
    ) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Return a new edge query with another edge selection."""
        return EdgeQuery(self._graph, edges)
