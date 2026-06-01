"""Edge module."""

from dataclasses import dataclass, field
from math import isfinite
from uuid import uuid4

from pygraph_tool.exceptions.graph_exceptions import EdgeException

from .metadata import Metadata
from .node import Node


@dataclass(slots=True, eq=False, init=False)
class Edge[NodeValueT, EdgeValueT]:
    """Graph edge connecting two nodes.

    An edge represents a relationship between two nodes. It has a stable and
    immutable identifier, optional user-defined value, optional metadata, and
    a mutable weight.

    If no identifier is provided, a UUID-based identifier is generated
    automatically.

    Attributes:
        value: Optional user-defined value stored in the edge.
        weight: Numeric weight associated with the edge.
        metadata: Generic metadata associated with the edge.
    """

    _edge_id: str = field(init=False, repr=False)
    _node_start: Node[NodeValueT] = field(init=False, repr=False)
    _node_end: Node[NodeValueT] = field(init=False, repr=False)
    _bidirectional: bool = field(init=False, repr=False)
    _weight: float = field(init=False, repr=False)

    value: EdgeValueT | None
    metadata: Metadata

    def __init__(
        self,
        node_start: Node[NodeValueT],
        node_end: Node[NodeValueT],
        *,
        value: EdgeValueT | None = None,
        edge_id: str | None = None,
        weight: float = 1.0,
        bidirectional: bool = False,
        metadata: Metadata | None = None,
    ) -> None:
        """Initialize an edge.

        Args:
            node_start: Node where the edge starts.
            node_end: Node where the edge ends.
            value: Optional user-defined value stored in the edge.
            edge_id: Optional unique edge identifier. If omitted, a UUID-based
                identifier is generated automatically.
            weight: Numeric weight associated with the edge.
            bidirectional: Whether the edge should be interpreted as
                bidirectional.
            metadata: Optional metadata associated with the edge.

        Raises:
            EdgeException: If the edge identifier is empty.
            EdgeException: If the weight is not finite.
        """
        if edge_id is not None and not edge_id.strip():
            raise EdgeException("The edge identifier must not be empty.")

        if not isfinite(weight):
            raise EdgeException("The edge weight must be finite.")

        self._edge_id = edge_id if edge_id is not None else str(uuid4())
        self._node_start = node_start
        self._node_end = node_end
        self._bidirectional = bidirectional

        self.value = value
        self.weight = weight
        self.metadata = metadata if metadata is not None else Metadata()

    @property
    def edge_id(self) -> str:
        """Return the immutable edge identifier."""
        return self._edge_id

    @property
    def node_start(self) -> Node[NodeValueT]:
        """Return the node where the edge starts."""
        return self._node_start

    @property
    def node_end(self) -> Node[NodeValueT]:
        """Return the node where the edge ends."""
        return self._node_end

    @property
    def weight(self) -> float:
        """Return the edge weight."""
        return self._weight

    @weight.setter
    def weight(self, value: float) -> None:
        """Set the edge weight.

        Raises:
            EdgeException: If the weight is not finite.
        """
        if not isfinite(value):
            raise EdgeException("The edge weight must be finite.")
        self._weight = value

    @property
    def bidirectional(self) -> bool:
        """Return whether the edge is bidirectional."""
        return self._bidirectional

    def __eq__(self, other: object) -> bool:
        """Compare edges by identifier.

        Args:
            other: Object to compare with this edge.

        Returns:
            True if both edges have the same identifier, False otherwise.
            NotImplemented when the other object is not an edge.
        """
        if not isinstance(other, Edge):
            return NotImplemented
        return self.edge_id == other.edge_id

    def __hash__(self) -> int:
        """Return the edge hash based on its immutable identifier."""
        return hash(self.edge_id)
