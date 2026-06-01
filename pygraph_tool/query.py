"""Fluent graph query module."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from typing import TYPE_CHECKING

from ._metadata_matching import matches_values
from ._types import Direction
from .edge import Edge
from .graph_exceptions import GraphException
from .node import Node

if TYPE_CHECKING:
    from .graph import Graph


class GraphQuery[NodeValueT, EdgeValueT]:
    """Entry point for fluent graph queries."""

    def __init__(self, graph: Graph[NodeValueT, EdgeValueT]) -> None:
        """Initialize a graph query.

        Args:
            graph: Source graph queried by this object.
        """
        self._graph = graph

    def nodes(self) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Return a query over all graph nodes.

        Returns:
            A node query initialized with all graph nodes.
        """
        return NodeQuery(self._graph, self._graph.nodes)

    def edges(self) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Return a query over all graph edges.

        Returns:
            An edge query initialized with all graph edges.
        """
        return EdgeQuery(self._graph, self._graph.edges)

    def from_node(
        self,
        node_id: str,
    ) -> NodeTraversalQuery[NodeValueT, EdgeValueT]:
        """Return a traversal query starting from a node.

        Args:
            node_id: Start node identifier.

        Raises:
            GraphException: If the node does not exist.

        Returns:
            A traversal query bound to the given start node.
        """
        self._graph.get_node(node_id)
        return NodeTraversalQuery(self._graph, node_id)


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
        self._graph = graph
        self._nodes = tuple(nodes)

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
            lambda node: matches_values(node.metadata.tags, tags, match_all)
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
            lambda node: matches_values(
                node.metadata.categories,
                categories,
                match_all,
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
            lambda node: matches_values(node.metadata.layers, layers, match_all)
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
            lambda node: matches_values(node.metadata.flags, flags, match_all)
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
        _validate_limit(limit)
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
        self._graph = graph
        self._edges = tuple(edges)

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
            lambda edge: matches_values(edge.metadata.tags, tags, match_all)
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
            lambda edge: matches_values(
                edge.metadata.categories,
                categories,
                match_all,
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
            lambda edge: matches_values(edge.metadata.layers, layers, match_all)
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
            lambda edge: matches_values(edge.metadata.flags, flags, match_all)
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
        _validate_limit(limit)
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


class NodeTraversalQuery[NodeValueT, EdgeValueT]:
    """Fluent traversal query starting from a node."""

    def __init__(
        self,
        graph: Graph[NodeValueT, EdgeValueT],
        node_id: str,
    ) -> None:
        """Initialize a traversal query.

        Args:
            graph: Source graph queried by this object.
            node_id: Start node identifier.
        """
        self._graph = graph
        self._node_id = node_id

    def node(self) -> Node[NodeValueT]:
        """Return the start node.

        Returns:
            Start node.
        """
        return self._graph.get_node(self._node_id)

    def neighbors(
        self,
        *,
        direction: Direction = "both",
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Return neighboring nodes as a node query.

        Args:
            direction: Neighbor direction to follow.

        Returns:
            A node query containing neighboring nodes.
        """
        return NodeQuery(
            self._graph,
            self._graph.get_neighbors(self._node_id, direction=direction),
        )

    def traverse(
        self,
        *,
        max_depth: int = 1,
        direction: Direction = "outgoing",
        include_start: bool = False,
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Return reachable nodes as a node query.

        Args:
            max_depth: Maximum traversal depth.
            direction: Edge direction to follow.
            include_start: Whether to include the start node.

        Returns:
            A node query containing reachable nodes.
        """
        return NodeQuery(
            self._graph,
            self._graph.get_reachable_nodes(
                self._node_id,
                max_depth=max_depth,
                direction=direction,
                include_start=include_start,
            ),
        )

    def shortest_path_to(
        self,
        node_id_end: str,
        *,
        direction: Direction = "outgoing",
    ) -> NodeQuery[NodeValueT, EdgeValueT]:
        """Return the shortest path to another node as a node query.

        Args:
            node_id_end: End node identifier.
            direction: Edge direction to follow.

        Returns:
            A node query containing the shortest path nodes, or an empty query
            when no path exists.
        """
        path = self._graph.get_shortest_path(
            self._node_id,
            node_id_end,
            direction=direction,
        )
        return NodeQuery(self._graph, path or [])

    def outgoing_edges(self) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Return outgoing edges from the start node.

        Returns:
            An edge query containing outgoing edges.
        """
        return EdgeQuery(self._graph, self._graph.get_outgoing_edges(self._node_id))

    def incoming_edges(self) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Return incoming edges to the start node.

        Returns:
            An edge query containing incoming edges.
        """
        return EdgeQuery(self._graph, self._graph.get_incoming_edges(self._node_id))

    def incident_edges(self) -> EdgeQuery[NodeValueT, EdgeValueT]:
        """Return incident edges connected to the start node.

        Returns:
            An edge query containing incident edges.
        """
        return EdgeQuery(self._graph, self._graph.get_incident_edges(self._node_id))


def _validate_limit(limit: int) -> None:
    """Validate a query limit."""
    if limit < 0:
        raise GraphException("limit must be greater than or equal to 0.")
