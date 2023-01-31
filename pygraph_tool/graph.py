from typing import List, Any

from .node import Node
from .edge import Edge
from .graph_exceptions import NodeException, EdgeException, GraphException


class Graph:
    """Defines the class that creates and manipulates the graph."""

    def __init__(self) -> None:
        """Build the graph instance."""
        self._nodes: List[Node] = []
        self._edges: List[Edge] = []

    @property
    def nodes(self) -> List[Node]:
        """The graph's nodes."""
        return self._nodes

    @nodes.setter
    def nodes(self, nodes: List[Node]) -> None:
        self._nodes = nodes

    @property
    def edges(self) -> List[Edge]:
        """The graph's edges."""
        return self._edges

    @edges.setter
    def edges(self, edges: List[Edge]) -> None:
        self._edges = edges

    def is_node(self, node_id: str) -> bool:
        """Check if the node belongs to the graph.

        Args:
            node_id (str): The node's identifier to checked.

        Returns:
            bool: True if node belongs to the graph.
        """
        return any(node_id == node.node_id for node in self._nodes)

    def is_edge(self, edge_id: str) -> bool:
        """Check if the edge belongs to the graph.

        Args:
            edge_id (str): The edge's identifier to checked.

        Returns:
            bool: True if edge belongs to the graph.
        """
        return any(edge_id == edge.edge_id for edge in self._edges)

    def add_node(self, node_content: Any, node_id: str) -> None:
        """Add a node in the graph.

        Args:
            node_content (Any): The object contained in node.
            node_id (str): Node identifier.

        Raises:
            NodeException: If node identifier or node content are empty.
            GraphException: If node already exists in graph.
        """
        if not node_content:
            raise NodeException("The node must not be empty.")

        if not node_id:
            raise NodeException("The node identifier must be filled in.")

        if not self.is_node(node_id):
            self._nodes.append(Node(node_content, node_id))
        else:
            raise GraphException(f"The node '{node_id}' already exists.")

    def add_unidirectional_edge(
        self,
        node_id_start: str,
        node_id_end: str,
        edge_id: str,
        weight: float = 1.0,
    ) -> None:
        """Add an unidirecional edge in the graph.

        Args:
            node_id_start (str): Starting node identifier.
            node_id_end (str): Ending node identifier.
            edge_id (str): Edge identifier.
            weight (float, optional): The edge's weight. Defaults to 1.

        Raises:
            EdgeException: If starting or ending nodes are not specified. If
                edge id is not define.
            GraphException: If edge already exists in graph.
        """
        if not node_id_start:
            raise EdgeException("The starting node must be define.")

        if not node_id_end:
            raise EdgeException("The ending node must be define.")

        if not edge_id:
            raise EdgeException("The edge identifier must be filled in.")

        if not self.is_edge(edge_id):
            self._edges.append(
                Edge(
                    self.get_node(node_id_start),
                    self.get_node(node_id_end),
                    edge_id,
                    weight,
                )
            )
        else:
            raise GraphException(f"The edge '{edge_id}' already exists.")

    def add_bidirectional_edge(self) -> None:
        """Add a bidirectional edge in the graph.

        Raises:
            NotImplementedError: coming soon...
        """
        raise NotImplementedError("coming soon...")

    def get_node(self, node_id: str) -> Node:
        """Get node found in the graph.

        Args:
            node_id (str): Node identifier.

        Raises:
            GraphException: If node doesn't exist in graph.

        Returns:
            Node: The node found in the graph.
        """
        if not self.is_node(node_id):
            raise GraphException(f"The node {node_id} doesn't exist in graph.")

        return next(node for node in self._nodes if node.node_id == node_id)

    def get_edge(self, edge_id: str) -> Edge:
        """Get edge found in the graph.

        Args:
            edge_id (str): Edge identifier.

        Raises:
            GraphException: If edge doesn't exist in graph.

        Returns:
            Edge: The edge found in the graph.
        """
        if not self.is_edge(edge_id):
            raise GraphException(f"The edge {edge_id} doesn't exist in graph.")

        return next(edge for edge in self._edges if edge.edge_id == edge_id)

    def remove_edge(self, edge_id: str) -> None:
        """Remove edge found in graph.

        Args:
            edge_id (str): Edge identifier.
        """
        self._edges.remove(self.get_edge(edge_id))

    def remove_node(self, node_id: str) -> None:
        """Remove node found in graph.

        Args:
            node_id (str): Node identifier.
        """
        edges_to_remove: List[Edge] = [
            edge
            for edge in self._edges
            if edge.node_start.node_id == node_id
            or edge.node_end.node_id == node_id
        ]
        for edge in edges_to_remove:
            self._edges.remove(edge)
        self._nodes.remove(self.get_node(node_id))

    def get_predecessors(self, node_id: str) -> List[Node]:
        """Get predecessors nodes for a node.

        Args:
            node_id (str): Node identifier.

        Returns:
            List[Node]: Predecessors nodes for a node.
        """
        return [
            edge.node_start
            for edge in self._edges
            if edge.node_end.node_id == node_id
        ]

    def get_successors(self, node_id: str) -> List[Node]:
        """Get successors nodes for a node.

        Args:
            node_id (str): Node identifier.

        Returns:
            List[Node]: Successors nodes for a node.
        """
        return [
            edge.node_end
            for edge in self._edges
            if edge.node_start.node_id == node_id
        ]
