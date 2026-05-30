"""Node module."""

from dataclasses import dataclass, field
from uuid import uuid4

from .graph_exceptions import NodeException
from .metadata import Metadata


@dataclass(slots=True, eq=False)
class Node[T]:
    """Graph node containing a user-defined value.

    A node represents a graph entity identified by a stable and immutable
    identifier. Its value is user-defined and can be updated after creation.

    If no identifier is provided, a UUID-based identifier is generated
    automatically.
    """

    _node_id: str = field(init=False, repr=False)
    value: T
    metadata: Metadata

    def __init__(
        self,
        value: T,
        node_id: str | None = None,
        metadata: Metadata | None = None,
    ) -> None:
        """Initialize a node.

        Args:
            value: User-defined value stored in the node.
            node_id: Optional unique node identifier. If omitted, a UUID-based
                identifier is generated automatically.
            metadata: Optional metadata associated with the node.

        Raises:
            NodeException: If the provided node identifier is empty.
        """
        if node_id is not None and not node_id.strip():
            raise NodeException("The node identifier must not be empty.")

        self._node_id = node_id if node_id is not None else str(uuid4())
        self.value = value
        self.metadata = metadata if metadata is not None else Metadata()

    @property
    def node_id(self) -> str:
        """Return the immutable node identifier."""
        return self._node_id

    def __eq__(self, other: object) -> bool:
        """Compare nodes by identifier.

        Args:
            other: Object to compare with this node.

        Returns:
            True if both nodes have the same identifier, False otherwise.
            NotImplemented when the other object is not a node.
        """
        if not isinstance(other, Node):
            return NotImplemented
        return self.node_id == other.node_id

    def __hash__(self) -> int:
        """Return the node hash based on its immutable identifier."""
        return hash(self.node_id)
