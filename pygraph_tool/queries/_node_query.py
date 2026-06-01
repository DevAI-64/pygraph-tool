"""Fluent query over graph nodes."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

from pygraph_tool.core.node import Node
from pygraph_tool.exceptions.graph_exceptions import GraphException

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph


class NodeQuery[NodeValueT, EdgeValueT]:
    """Fluent query over graph nodes."""

    def __init__(
        self,
        graph: Graph[NodeValueT, EdgeValueT],
        nodes: Iterable[Node[NodeValueT]],
    ) -> None:
        """Initialize a node query.

        Args:
            graph: Source graph queried by this object.
            nodes: Current node selection.
        """
        self._graph: Graph[NodeValueT, EdgeValueT] = graph
        self._nodes: tuple[Node[NodeValueT], ...] = tuple(nodes)

    def where(
        self,
        predicate: Callable[[Node[NodeValueT]], bool],
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes with a predicate.

        Args:
            predicate: Function used to keep or reject nodes.

        Returns:
            A new node query containing matching nodes.
        """
        return self._clone(node for node in self._nodes if predicate(node))

    def with_tag(self, tag: str) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes containing a metadata tag.

        Args:
            tag: Expected metadata tag.

        Returns:
            A new node query containing matching nodes.
        """
        return self.with_tags([tag])

    def with_category(self, category: str) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes containing a metadata category.

        Args:
            category: Expected metadata category.

        Returns:
            A new node query containing matching nodes.
        """
        return self.with_categories([category])

    def with_layer(self, layer: str) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes containing a metadata layer.

        Args:
            layer: Expected metadata layer.

        Returns:
            A new node query containing matching nodes.
        """
        return self.with_layers([layer])

    def with_flag(self, flag: str) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes containing a metadata flag.

        Args:
            flag: Expected metadata flag.

        Returns:
            A new node query containing matching nodes.
        """
        return self.with_flags([flag])

    def with_tags(
        self,
        tags: Iterable[str],
        *,
        match_all: bool = True,
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes by metadata tags.

        Args:
            tags: Expected metadata tags.
            match_all: Whether all expected tags must be present.

        Returns:
            A new node query containing matching nodes.
        """
        return self.where(
            lambda node: node.metadata.matches(tags=tags, match_all=match_all)
        )

    def with_categories(
        self,
        categories: Iterable[str],
        *,
        match_all: bool = True,
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes by metadata categories.

        Args:
            categories: Expected metadata categories.
            match_all: Whether all expected categories must be present.

        Returns:
            A new node query containing matching nodes.
        """
        return self.where(
            lambda node: node.metadata.matches(
                categories=categories, match_all=match_all
            )
        )

    def with_layers(
        self,
        layers: Iterable[str],
        *,
        match_all: bool = True,
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes by metadata layers.

        Args:
            layers: Expected metadata layers.
            match_all: Whether all expected layers must be present.

        Returns:
            A new node query containing matching nodes.
        """
        return self.where(
            lambda node: node.metadata.matches(layers=layers, match_all=match_all)
        )

    def with_flags(
        self,
        flags: Iterable[str],
        *,
        match_all: bool = True,
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Filter nodes by metadata flags.

        Args:
            flags: Expected metadata flags.
            match_all: Whether all expected flags must be present.

        Returns:
            A new node query containing matching nodes.
        """
        return self.where(
            lambda node: node.metadata.matches(flags=flags, match_all=match_all)
        )

    def limit(self, limit: int) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Limit the number of selected nodes.

        Args:
            limit: Maximum number of nodes to keep.

        Raises:
            GraphException: If limit is negative.

        Returns:
            A new node query containing at most limit nodes.
        """
        if limit < 0:
            raise GraphException("limit must be greater than or equal to 0.")
        return self._clone(self._nodes[:limit])

    def first(self) -> Node[NodeValueT] | None:
        """Return the first selected node.

        Returns:
            The first node, or None if the query is empty.
        """
        return self._nodes[0] if self._nodes else None

    def count(self) -> int:
        """Return the number of selected nodes.

        Returns:
            Number of selected nodes.
        """
        return len(self._nodes)

    def exists(self) -> bool:
        """Return whether the query contains at least one node.

        Returns:
            True if at least one node is selected, False otherwise.
        """
        return bool(self._nodes)

    def to_list(self) -> list[Node[NodeValueT]]:
        """Return selected nodes as a list.

        Returns:
            List of selected nodes.
        """
        return list(self._nodes)

    def to_tuple(self) -> tuple[Node[NodeValueT], ...]:
        """Return selected nodes as a tuple.

        Returns:
            Tuple of selected nodes.
        """
        return self._nodes

    def to_subgraph(
        self,
        *,
        include_edges: bool = True,
    ) -> Graph[NodeValueT, EdgeValueT]:
        """Return selected nodes as a subgraph.

        Args:
            include_edges: Whether to include edges whose endpoints are both
                part of the selected nodes.

        Returns:
            A subgraph containing selected nodes.
        """
        return self._graph.extract_subgraph(
            (node.node_id for node in self._nodes),
            include_edges=include_edges,
        )

    def _clone(
        self,
        nodes: Iterable[Node[NodeValueT]],
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Return a new node query with another node selection."""
        return NodeQuery(self._graph, nodes)
