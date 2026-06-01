"""Fluent traversal query starting from a graph node."""

from __future__ import annotations

from typing import TYPE_CHECKING

from pygraph_tool._types import Direction
from pygraph_tool.core.node import Node
from pygraph_tool.queries._edge_query import EdgeQuery
from pygraph_tool.queries._node_query import NodeQuery

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph


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
        self._graph: Graph[NodeValueT, EdgeValueT] = graph
        self._node_id: str = node_id

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
        path: list[Node[NodeValueT]] | None = self._graph.get_shortest_path(
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
