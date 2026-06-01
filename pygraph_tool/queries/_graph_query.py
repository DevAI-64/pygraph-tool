"""Fluent query entry point bound to a graph."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygraph_tool.queries._edge_query import EdgeQuery
from pygraph_tool.queries._node_query import NodeQuery
from pygraph_tool.queries._node_traversal_query import NodeTraversalQuery

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph


class GraphQuery[NodeValueT, EdgeValueT]:
    """Entry point for fluent graph queries."""

    def __init__(self, graph: Graph[NodeValueT, EdgeValueT]) -> None:
        """Initialize a graph query.

        Args:
            graph: Source graph queried by this object.
        """
        self._graph: Graph[NodeValueT, EdgeValueT] = graph

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
