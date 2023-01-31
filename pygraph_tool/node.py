from typing import Any


class Node:
    """Defines the class that creates and manipulates the nodes of the graph.

    Attributes:
        node_content (Any): The object contained in node.
        node_id (str): Node identifier.
    """

    def __init__(self, node_content: Any, node_id: str) -> None:
        """Build the node instance.

        Args:
            node_content (Any): The object contained in node.
            node_id (str): Node identifier.
        """
        self._node_content: Any = node_content
        self._node_id: str = node_id

    @property
    def node_content(self) -> Any:
        """The object contained in node."""
        return self._node_content

    @node_content.setter
    def node_content(self, node_content: Any) -> None:
        self._node_content = node_content

    @property
    def node_id(self) -> str:
        """Node identifier."""
        return self._node_id

    @node_id.setter
    def node_id(self, node_id: str) -> None:
        self._node_id = node_id
