from .node import Node


class Edge:
    """Defines the class that creates and manipulates the edges of the graph.

    Attributes:
        node_start (Node): Node which begins the edge.
        node_end (Node): Node which terminates the edge.
        edge_id (str): Edge identifier.
        weight (float, optional): The edge's weight. Defaults to 1.
        bidirectional (bool, optional): If the edge is undirected.
            Defaults to False.
    """

    def __init__(
        self,
        node_start: Node,
        node_end: Node,
        edge_id: str,
        weight: float = 1.0,
        bidirectional: bool = False,
    ) -> None:
        """Build the edge instance.

        Args:
            node_start (Node): Node which begins the edge.
            node_end (Node): Node which terminates the edge.
            edge_id (str): Edge identifier.
            weight (float, optional): The edge's weight. Defaults to 1.
            bidirectional (bool, optional): If the edge is undirected.
                Defaults to False.
        """
        self._node_start: Node = node_start
        self._node_end: Node = node_end
        self._edge_id: str = edge_id
        self._weight: float = weight
        self._bidirectional: bool = bidirectional

    @property
    def node_start(self) -> Node:
        """Node which begins the edge."""
        return self._node_start

    @node_start.setter
    def node_start(self, node_start: Node) -> None:
        self._node_start = node_start

    @property
    def node_end(self) -> Node:
        """Node which terminates the edge."""
        return self._node_end

    @node_end.setter
    def node_end(self, node_end: Node) -> None:
        self._node_end = node_end

    @property
    def edge_id(self) -> str:
        """Edge identifier."""
        return self._edge_id

    @edge_id.setter
    def edge_id(self, edge_id: str) -> None:
        self._edge_id = edge_id

    @property
    def weight(self) -> float:
        """The edge's weight."""
        return self._weight

    @weight.setter
    def weight(self, weight: float) -> None:
        self._weight = weight

    @property
    def bidirectional(self) -> bool:
        """If the edge is undirected."""
        return self._bidirectional

    @bidirectional.setter
    def bidirectional(self, bidirectional: bool) -> None:
        self._bidirectional = bidirectional
