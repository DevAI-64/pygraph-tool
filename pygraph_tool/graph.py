"""Graph module."""

from __future__ import annotations

from collections import deque
from collections.abc import Callable, Iterable
from typing import Literal

from .edge import Edge
from .graph_exceptions import GraphException
from .metadata import Metadata
from .node import Node

Direction = Literal["outgoing", "incoming", "both"]


class Graph[NodeValueT, EdgeValueT]:
    """Graph containing nodes and edges.

    The graph is responsible for maintaining node and edge uniqueness.
    Nodes and edges are indexed by their immutable identifiers.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._nodes_by_id: dict[str, Node[NodeValueT]] = {}
        self._edges_by_id: dict[str, Edge[NodeValueT, EdgeValueT]] = {}
        self._outgoing_edge_ids_by_node_id: dict[str, dict[str, None]] = {}
        self._incoming_edge_ids_by_node_id: dict[str, dict[str, None]] = {}

    @property
    def nodes(self) -> tuple[Node[NodeValueT], ...]:
        """Return the graph nodes.

        Returns:
            Tuple containing the graph nodes.
        """
        return tuple(self._nodes_by_id.values())

    @property
    def edges(self) -> tuple[Edge[NodeValueT, EdgeValueT], ...]:
        """Return the graph edges.

        Returns:
            Tuple containing the graph edges.
        """
        return tuple(self._edges_by_id.values())

    def is_node(self, node_id: str) -> bool:
        """Return whether a node belongs to the graph.

        Args:
            node_id: Node identifier to check.

        Returns:
            True if the node exists, False otherwise.
        """
        return node_id in self._nodes_by_id

    def is_edge(self, edge_id: str) -> bool:
        """Return whether an edge belongs to the graph.

        Args:
            edge_id: Edge identifier to check.

        Returns:
            True if the edge exists, False otherwise.
        """
        return edge_id in self._edges_by_id

    def add_node(
        self,
        value: NodeValueT,
        node_id: str | None = None,
        metadata: Metadata | None = None,
    ) -> Node[NodeValueT]:
        """Add a node to the graph.

        If no identifier is provided, the node generates a UUID-based
        identifier automatically.

        Args:
            value: User-defined value stored in the node.
            node_id: Optional node identifier.
            metadata: Optional metadata associated with the node.

        Raises:
            GraphException: If a node with the same identifier already exists.

        Returns:
            The created node.
        """
        node = Node(value=value, node_id=node_id, metadata=metadata)

        if self.is_node(node.node_id):
            raise GraphException(f"The node '{node.node_id}' already exists.")

        self._nodes_by_id[node.node_id] = node
        self._outgoing_edge_ids_by_node_id[node.node_id] = {}
        self._incoming_edge_ids_by_node_id[node.node_id] = {}
        return node

    def add_edge(
        self,
        node_id_start: str,
        node_id_end: str,
        *,
        value: EdgeValueT | None = None,
        edge_id: str | None = None,
        weight: float = 1.0,
        bidirectional: bool = False,
        metadata: Metadata | None = None,
    ) -> Edge[NodeValueT, EdgeValueT]:
        """Add an edge to the graph.

        If no identifier is provided, the edge generates a UUID-based
        identifier automatically.

        Args:
            node_id_start: Starting node identifier.
            node_id_end: Ending node identifier.
            value: Optional user-defined value stored in the edge.
            edge_id: Optional edge identifier.
            weight: Numeric weight associated with the edge.
            bidirectional: Whether the edge should be interpreted as
                bidirectional.
            metadata: Optional metadata associated with the edge.

        Raises:
            GraphException: If one of the nodes does not exist in the graph.
            GraphException: If an edge with the same identifier already exists.

        Returns:
            The created edge.
        """
        node_start = self.get_node(node_id_start)
        node_end = self.get_node(node_id_end)

        edge = Edge(
            node_start=node_start,
            node_end=node_end,
            value=value,
            edge_id=edge_id,
            weight=weight,
            bidirectional=bidirectional,
            metadata=metadata,
        )

        if self.is_edge(edge.edge_id):
            raise GraphException(f"The edge '{edge.edge_id}' already exists.")

        self._edges_by_id[edge.edge_id] = edge
        self._register_edge_in_adjacency_indexes(edge)
        return edge

    def add_unidirectional_edge(
        self,
        node_id_start: str,
        node_id_end: str,
        *,
        value: EdgeValueT | None = None,
        edge_id: str | None = None,
        weight: float = 1.0,
        metadata: Metadata | None = None,
    ) -> Edge[NodeValueT, EdgeValueT]:
        """Add a unidirectional edge to the graph.

        Args:
            node_id_start: Starting node identifier.
            node_id_end: Ending node identifier.
            value: Optional user-defined value stored in the edge.
            edge_id: Optional edge identifier.
            weight: Numeric weight associated with the edge.
            metadata: Optional metadata associated with the edge.

        Returns:
            The created edge.
        """
        return self.add_edge(
            node_id_start=node_id_start,
            node_id_end=node_id_end,
            value=value,
            edge_id=edge_id,
            weight=weight,
            bidirectional=False,
            metadata=metadata,
        )

    def add_bidirectional_edge(
        self,
        node_id_start: str,
        node_id_end: str,
        *,
        value: EdgeValueT | None = None,
        edge_id: str | None = None,
        weight: float = 1.0,
        metadata: Metadata | None = None,
    ) -> Edge[NodeValueT, EdgeValueT]:
        """Add a bidirectional edge to the graph.

        Args:
            node_id_start: Starting node identifier.
            node_id_end: Ending node identifier.
            value: Optional user-defined value stored in the edge.
            edge_id: Optional edge identifier.
            weight: Numeric weight associated with the edge.
            metadata: Optional metadata associated with the edge.

        Returns:
            The created edge.
        """
        return self.add_edge(
            node_id_start=node_id_start,
            node_id_end=node_id_end,
            value=value,
            edge_id=edge_id,
            weight=weight,
            bidirectional=True,
            metadata=metadata,
        )

    def get_node(self, node_id: str) -> Node[NodeValueT]:
        """Return a node by identifier.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            The matching node.
        """
        try:
            return self._nodes_by_id[node_id]
        except KeyError as exception:
            raise GraphException(
                f"The node '{node_id}' does not exist in the graph."
            ) from exception

    def get_edge(self, edge_id: str) -> Edge[NodeValueT, EdgeValueT]:
        """Return an edge by identifier.

        Args:
            edge_id: Edge identifier.

        Raises:
            GraphException: If the edge does not exist in the graph.

        Returns:
            The matching edge.
        """
        try:
            return self._edges_by_id[edge_id]
        except KeyError as exception:
            raise GraphException(
                f"The edge '{edge_id}' does not exist in the graph."
            ) from exception

    def remove_edge(self, edge_id: str) -> Edge[NodeValueT, EdgeValueT]:
        """Remove an edge from the graph.

        Args:
            edge_id: Edge identifier.

        Raises:
            GraphException: If the edge does not exist in the graph.

        Returns:
            The removed edge.
        """
        edge = self.get_edge(edge_id)
        self._unregister_edge_from_adjacency_indexes(edge)
        del self._edges_by_id[edge_id]
        return edge

    def remove_node(self, node_id: str) -> Node[NodeValueT]:
        """Remove a node and all its connected edges from the graph.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            The removed node.
        """
        node = self.get_node(node_id)

        edge_ids_to_remove = [edge.edge_id for edge in self.get_incident_edges(node_id)]

        for edge_id in edge_ids_to_remove:
            self.remove_edge(edge_id)

        del self._outgoing_edge_ids_by_node_id[node_id]
        del self._incoming_edge_ids_by_node_id[node_id]
        del self._nodes_by_id[node_id]

        return node

    def get_outgoing_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return outgoing edges for a node.

        For bidirectional edges, an edge connected to the node is considered
        outgoing even when the node is the edge end.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of outgoing edges.
        """
        self.get_node(node_id)

        return [
            self._edges_by_id[edge_id]
            for edge_id in self._outgoing_edge_ids_by_node_id[node_id]
        ]

    def get_incoming_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return incoming edges for a node.

        For bidirectional edges, an edge connected to the node is considered
        incoming even when the node is the edge start.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of incoming edges.
        """
        self.get_node(node_id)

        return [
            self._edges_by_id[edge_id]
            for edge_id in self._incoming_edge_ids_by_node_id[node_id]
        ]

    def get_incident_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return all edges connected to a node.

        Incident edges include both incoming and outgoing edges.
        Direction is not considered by this method.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of edges connected to the node.
        """
        self.get_node(node_id)

        edge_ids = {
            **self._outgoing_edge_ids_by_node_id[node_id],
            **self._incoming_edge_ids_by_node_id[node_id],
        }

        return [self._edges_by_id[edge_id] for edge_id in edge_ids]

    def get_predecessors(self, node_id: str) -> list[Node[NodeValueT]]:
        """Return predecessor nodes for a node.

        For bidirectional edges, the opposite endpoint is also considered
        a predecessor.

        Duplicate nodes are removed from the result.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of predecessor nodes.
        """
        predecessors_by_id: dict[str, Node[NodeValueT]] = {}

        for edge in self.get_incoming_edges(node_id):
            if edge.node_end.node_id == node_id:
                predecessors_by_id[edge.node_start.node_id] = edge.node_start
            elif edge.bidirectional and edge.node_start.node_id == node_id:
                predecessors_by_id[edge.node_end.node_id] = edge.node_end

        return list(predecessors_by_id.values())

    def get_successors(self, node_id: str) -> list[Node[NodeValueT]]:
        """Return successor nodes for a node.

        For bidirectional edges, the opposite endpoint is also considered
        a successor.

        Duplicate nodes are removed from the result.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of successor nodes.
        """
        successors_by_id: dict[str, Node[NodeValueT]] = {}

        for edge in self.get_outgoing_edges(node_id):
            if edge.node_start.node_id == node_id:
                successors_by_id[edge.node_end.node_id] = edge.node_end
            elif edge.bidirectional and edge.node_end.node_id == node_id:
                successors_by_id[edge.node_start.node_id] = edge.node_start

        return list(successors_by_id.values())

    def get_neighbors(
        self,
        node_id: str,
        *,
        direction: Direction = "both",
    ) -> list[Node[NodeValueT]]:
        """Return neighbor nodes for a node.

        Args:
            node_id: Node identifier.
            direction: Neighbor direction to follow. Supported values are
                "outgoing", "incoming", and "both".

        Raises:
            GraphException: If the node does not exist.
            GraphException: If the direction is invalid.

        Returns:
            List of neighbor nodes.
        """
        if direction == "outgoing":
            return self.get_successors(node_id)

        if direction == "incoming":
            return self.get_predecessors(node_id)

        if direction == "both":
            neighbors_by_id: dict[str, Node[NodeValueT]] = {}

            for node in self.get_successors(node_id):
                neighbors_by_id[node.node_id] = node

            for node in self.get_predecessors(node_id):
                neighbors_by_id[node.node_id] = node

            return list(neighbors_by_id.values())

        raise GraphException(
            "Invalid direction. Expected 'outgoing', 'incoming', or 'both'."
        )

    def get_reachable_nodes(
        self,
        node_id: str,
        *,
        max_depth: int = 1,
        direction: Direction = "outgoing",
        include_start: bool = False,
    ) -> list[Node[NodeValueT]]:
        """Return nodes reachable from a start node up to a maximum depth.

        The traversal is breadth-first and unweighted.

        Args:
            node_id: Start node identifier.
            max_depth: Maximum traversal depth. Zero returns only the start node
                when include_start is True.
            direction: Edge direction to follow.
            include_start: Whether to include the start node in the result.

        Raises:
            GraphException: If the start node does not exist.
            GraphException: If max_depth is negative.

        Returns:
            List of reachable nodes.
        """
        if max_depth < 0:
            raise GraphException("max_depth must be greater than or equal to 0.")

        start_node = self.get_node(node_id)

        visited_node_ids = {node_id}
        reachable_nodes: list[Node[NodeValueT]] = []

        if include_start:
            reachable_nodes.append(start_node)

        queue: deque[tuple[str, int]] = deque([(node_id, 0)])

        while queue:
            current_node_id, current_depth = queue.popleft()

            if current_depth >= max_depth:
                continue

            for neighbor in self.get_neighbors(
                current_node_id,
                direction=direction,
            ):
                if neighbor.node_id in visited_node_ids:
                    continue

                visited_node_ids.add(neighbor.node_id)
                reachable_nodes.append(neighbor)
                queue.append((neighbor.node_id, current_depth + 1))

        return reachable_nodes

    def get_shortest_path(
        self,
        node_id_start: str,
        node_id_end: str,
        *,
        direction: Direction = "outgoing",
    ) -> list[Node[NodeValueT]] | None:
        """Return an unweighted shortest path between two nodes.

        The traversal is breadth-first and ignores edge weights.

        Args:
            node_id_start: Start node identifier.
            node_id_end: End node identifier.
            direction: Edge direction to follow.

        Raises:
            GraphException: If one of the nodes does not exist.

        Returns:
            The shortest path as a list of nodes, or None when no path exists.
        """
        self.get_node(node_id_start)
        self.get_node(node_id_end)

        if node_id_start == node_id_end:
            return [self.get_node(node_id_start)]

        visited_node_ids = {node_id_start}
        previous_node_id_by_node_id: dict[str, str | None] = {
            node_id_start: None,
        }

        queue: deque[str] = deque([node_id_start])

        while queue:
            current_node_id = queue.popleft()

            for neighbor in self.get_neighbors(
                current_node_id,
                direction=direction,
            ):
                if neighbor.node_id in visited_node_ids:
                    continue

                visited_node_ids.add(neighbor.node_id)
                previous_node_id_by_node_id[neighbor.node_id] = current_node_id

                if neighbor.node_id == node_id_end:
                    return self._build_node_path(
                        previous_node_id_by_node_id,
                        node_id_end,
                    )

                queue.append(neighbor.node_id)

        return None

    def _build_node_path(
        self,
        previous_node_id_by_node_id: dict[str, str | None],
        node_id_end: str,
    ) -> list[Node[NodeValueT]]:
        """Build a node path from a previous-node mapping."""
        path_node_ids: list[str] = []
        current_node_id: str | None = node_id_end

        while current_node_id is not None:
            path_node_ids.append(current_node_id)
            current_node_id = previous_node_id_by_node_id[current_node_id]

        path_node_ids.reverse()

        return [self.get_node(node_id) for node_id in path_node_ids]

    def filter_nodes(
        self,
        predicate: Callable[[Node[NodeValueT]], bool],
    ) -> list[Node[NodeValueT]]:
        """Return nodes matching a predicate.

        Args:
            predicate: Function used to select nodes.

        Returns:
            List of matching nodes.
        """
        return [node for node in self._nodes_by_id.values() if predicate(node)]

    def filter_edges(
        self,
        predicate: Callable[[Edge[NodeValueT, EdgeValueT]], bool],
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return edges matching a predicate.

        Args:
            predicate: Function used to select edges.

        Returns:
            List of matching edges.
        """
        return [edge for edge in self._edges_by_id.values() if predicate(edge)]

    def filter_nodes_by_metadata(
        self,
        *,
        tags: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        layers: Iterable[str] | None = None,
        flags: Iterable[str] | None = None,
        match_all: bool = True,
    ) -> list[Node[NodeValueT]]:
        """Return nodes matching metadata criteria.

        Args:
            tags: Optional tags to match.
            categories: Optional categories to match.
            layers: Optional layers to match.
            flags: Optional flags to match.
            match_all: If True, all provided values of each criterion must
                be present. If False, at least one provided value of each
                criterion must be present.

        Returns:
            List of nodes matching the metadata criteria.
        """
        return self.filter_nodes(
            lambda node: self._matches_metadata(
                metadata=node.metadata,
                tags=tags,
                categories=categories,
                layers=layers,
                flags=flags,
                match_all=match_all,
            )
        )

    def filter_edges_by_metadata(
        self,
        *,
        tags: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        layers: Iterable[str] | None = None,
        flags: Iterable[str] | None = None,
        match_all: bool = True,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return edges matching metadata criteria.

        Args:
            tags: Optional tags to match.
            categories: Optional categories to match.
            layers: Optional layers to match.
            flags: Optional flags to match.
            match_all: If True, all provided values of each criterion must
                be present. If False, at least one provided value of each
                criterion must be present.

        Returns:
            List of edges matching the metadata criteria.
        """
        return self.filter_edges(
            lambda edge: self._matches_metadata(
                metadata=edge.metadata,
                tags=tags,
                categories=categories,
                layers=layers,
                flags=flags,
                match_all=match_all,
            )
        )

    @staticmethod
    def _matches_metadata(
        metadata: Metadata,
        *,
        tags: Iterable[str] | None = None,
        categories: Iterable[str] | None = None,
        layers: Iterable[str] | None = None,
        flags: Iterable[str] | None = None,
        match_all: bool = True,
    ) -> bool:
        """Return whether metadata matches the provided criteria.

        Args:
            metadata: Metadata to inspect.
            tags: Optional tags to match.
            categories: Optional categories to match.
            layers: Optional layers to match.
            flags: Optional flags to match.
            match_all: If True, all expected values must be present within each
                provided criterion. If False, at least one expected value must be
                present within each provided criterion. Different criteria are
                always combined with AND.

        Returns:
            True if the metadata matches all provided criteria, False otherwise.
        """
        return (
            Graph._matches_values(metadata.tags, tags, match_all)
            and Graph._matches_values(metadata.categories, categories, match_all)
            and Graph._matches_values(metadata.layers, layers, match_all)
            and Graph._matches_values(metadata.flags, flags, match_all)
        )

    @staticmethod
    def _matches_values(
        existing_values: set[str],
        expected_values: Iterable[str] | None,
        match_all: bool,
    ) -> bool:
        """Return whether a set contains expected values.

        Args:
            existing_values: Existing metadata values.
            expected_values: Expected metadata values.
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

    def _register_edge_in_adjacency_indexes(
        self,
        edge: Edge[NodeValueT, EdgeValueT],
    ) -> None:
        """Register an edge in adjacency indexes."""
        start_id = edge.node_start.node_id
        end_id = edge.node_end.node_id

        self._outgoing_edge_ids_by_node_id[start_id][edge.edge_id] = None
        self._incoming_edge_ids_by_node_id[end_id][edge.edge_id] = None

        if edge.bidirectional:
            self._outgoing_edge_ids_by_node_id[end_id][edge.edge_id] = None
            self._incoming_edge_ids_by_node_id[start_id][edge.edge_id] = None

    def _unregister_edge_from_adjacency_indexes(
        self,
        edge: Edge[NodeValueT, EdgeValueT],
    ) -> None:
        """Unregister an edge from adjacency indexes."""
        start_id = edge.node_start.node_id
        end_id = edge.node_end.node_id

        self._outgoing_edge_ids_by_node_id[start_id].pop(edge.edge_id, None)
        self._incoming_edge_ids_by_node_id[end_id].pop(edge.edge_id, None)

        if edge.bidirectional:
            self._outgoing_edge_ids_by_node_id[end_id].pop(edge.edge_id, None)
            self._incoming_edge_ids_by_node_id[start_id].pop(edge.edge_id, None)

    def extract_subgraph(
        self,
        node_ids: Iterable[str],
        *,
        include_edges: bool = True,
    ) -> Graph[NodeValueT, EdgeValueT]:
        """Extract a subgraph containing selected nodes.

        Node and edge values are reused by reference. Metadata objects are copied.

        Args:
            node_ids: Node identifiers to include in the subgraph.
            include_edges: Whether to include edges whose two endpoints are part
                of the selected nodes.

        Raises:
            GraphException: If one of the node identifiers does not exist.

        Returns:
            A new graph containing the selected nodes and optional internal edges.
        """
        selected_node_ids = tuple(dict.fromkeys(node_ids))
        selected_node_id_set = set(selected_node_ids)

        subgraph: Graph[NodeValueT, EdgeValueT] = Graph()

        for node_id in selected_node_ids:
            node = self.get_node(node_id)
            subgraph.add_node(
                value=node.value,
                node_id=node.node_id,
                metadata=node.metadata.copy(),
            )

        if not include_edges:
            return subgraph

        for edge in self.edges:
            start_id = edge.node_start.node_id
            end_id = edge.node_end.node_id

            if start_id in selected_node_id_set and end_id in selected_node_id_set:
                subgraph.add_edge(
                    node_id_start=start_id,
                    node_id_end=end_id,
                    value=edge.value,
                    edge_id=edge.edge_id,
                    weight=edge.weight,
                    bidirectional=edge.bidirectional,
                    metadata=edge.metadata.copy(),
                )

        return subgraph
