"""Graph module."""

from collections.abc import Callable, Iterable

from .edge import Edge
from .graph_exceptions import GraphException
from .metadata import Metadata
from .node import Node


class Graph[NodeValueT, EdgeValueT]:
    """Graph containing nodes and edges.

    The graph is responsible for maintaining node and edge uniqueness.
    Nodes and edges are indexed by their immutable identifiers.
    """

    def __init__(self) -> None:
        """Initialize an empty graph."""
        self._nodes_by_id: dict[str, Node[NodeValueT]] = {}
        self._edges_by_id: dict[str, Edge[NodeValueT, EdgeValueT]] = {}

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

        edge_ids_to_remove = [
            edge.edge_id
            for edge in self._edges_by_id.values()
            if node_id in (edge.node_start.node_id, edge.node_end.node_id)
        ]

        for edge_id in edge_ids_to_remove:
            del self._edges_by_id[edge_id]

        del self._nodes_by_id[node_id]
        return node

    def get_outgoing_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return outgoing edges for a node.

        For bidirectional edges, an edge connected to the node is considered
        outgoing even when the node is the edge end.

        Duplicate edges are removed from the result.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of outgoing edges.
        """
        self.get_node(node_id)

        outgoing_edges_by_id: dict[str, Edge[NodeValueT, EdgeValueT]] = {}

        for edge in self._edges_by_id.values():
            if edge.node_start.node_id == node_id:
                outgoing_edges_by_id[edge.edge_id] = edge
            elif edge.bidirectional and edge.node_end.node_id == node_id:
                outgoing_edges_by_id[edge.edge_id] = edge

        return list(outgoing_edges_by_id.values())

    def get_incoming_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return incoming edges for a node.

        For bidirectional edges, an edge connected to the node is considered
        incoming even when the node is the edge start.

        Duplicate edges are removed from the result.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of incoming edges.
        """
        self.get_node(node_id)

        incoming_edges_by_id: dict[str, Edge[NodeValueT, EdgeValueT]] = {}

        for edge in self._edges_by_id.values():
            if edge.node_end.node_id == node_id:
                incoming_edges_by_id[edge.edge_id] = edge
            elif edge.bidirectional and edge.node_start.node_id == node_id:
                incoming_edges_by_id[edge.edge_id] = edge

        return list(incoming_edges_by_id.values())

    def get_incident_edges(
        self,
        node_id: str,
    ) -> list[Edge[NodeValueT, EdgeValueT]]:
        """Return all edges connected to a node.

        Incident edges include both incoming and outgoing edges. Direction is not
        considered by this method.

        Duplicate edges are removed from the result.

        Args:
            node_id: Node identifier.

        Raises:
            GraphException: If the node does not exist in the graph.

        Returns:
            List of edges connected to the node.
        """
        self.get_node(node_id)

        incident_edges_by_id: dict[str, Edge[NodeValueT, EdgeValueT]] = {}

        for edge in self._edges_by_id.values():
            if node_id in (edge.node_start.node_id, edge.node_end.node_id):
                incident_edges_by_id[edge.edge_id] = edge

        return list(incident_edges_by_id.values())

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
