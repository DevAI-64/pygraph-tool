"""Internal graph-to-dictionary and graph-to-JSON serialization.

Defines :class:`GraphSerializer`, used by :class:`pygraph_tool.Graph` to export
a graph to standard Python containers or JSON text. It relies only on the Python
standard library and avoids formats such as ``pickle`` so that serialized data
stays explicit and portable.
"""

from __future__ import annotations

import json
from collections.abc import Callable
from typing import TYPE_CHECKING, Any

from pygraph_tool.exceptions.graph_exceptions import SerializationException

from ._metadata_serializer import MetadataSerializer

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph

SCHEMA_VERSION = "1.0"
"""Version of the serialized graph format produced by this module."""


class GraphSerializer:
    """Serialize graphs to standard Python containers or JSON text."""

    def __init__(
        self,
        *,
        serialize_node_value: Callable[[Any], Any] | None = None,
        serialize_edge_value: Callable[[Any], Any] | None = None,
    ) -> None:
        """Initialize a graph serializer.

        Args:
            serialize_node_value: Optional callable converting node values into
                JSON-compatible objects.
            serialize_edge_value: Optional callable converting edge values into
                JSON-compatible objects.
        """
        self._serialize_node_value = serialize_node_value
        self._serialize_edge_value = serialize_edge_value

    def to_dict(self, graph: Graph[Any, Any]) -> dict[str, Any]:
        """Convert a graph to a JSON-compatible dictionary.

        Nodes and edges are emitted in insertion order. Node and edge values are
        included as-is unless a serialization hook converts them.

        Args:
            graph: Graph to convert.

        Returns:
            A dictionary describing the graph.
        """
        return {
            "schema_version": SCHEMA_VERSION,
            "nodes": [self._node_to_dict(node) for node in graph.nodes],
            "edges": [self._edge_to_dict(edge) for edge in graph.edges],
        }

    def to_json(
        self,
        graph: Graph[Any, Any],
        *,
        indent: int | None = None,
        sort_keys: bool = False,
    ) -> str:
        """Serialize a graph to a JSON string.

        Args:
            graph: Graph to serialize.
            indent: Optional indentation passed to the JSON encoder.
            sort_keys: Whether to sort dictionary keys in the JSON output.

        Raises:
            SerializationException: If a value is not JSON-serializable and no
                matching hook converts it.

        Returns:
            The JSON representation of the graph.
        """
        try:
            return json.dumps(
                self.to_dict(graph),
                indent=indent,
                sort_keys=sort_keys,
                ensure_ascii=False,
                allow_nan=False,
            )
        except (TypeError, ValueError) as exception:
            raise SerializationException(
                "The graph contains a value that is not JSON-serializable. "
                "Provide a serialize_node_value or serialize_edge_value hook "
                "to convert it."
            ) from exception

    def _node_to_dict(self, node: Any) -> dict[str, Any]:
        """Convert a node to a serialized dictionary."""
        node_dict: dict[str, Any] = {
            "id": node.node_id,
            "value": self._apply_hook(self._serialize_node_value, node.value),
        }
        metadata: dict[str, Any] = MetadataSerializer.to_dict(node.metadata)
        if metadata:
            node_dict["metadata"] = metadata
        return node_dict

    def _edge_to_dict(self, edge: Any) -> dict[str, Any]:
        """Convert an edge to a serialized dictionary."""
        edge_dict: dict[str, Any] = {
            "id": edge.edge_id,
            "source": edge.node_start.node_id,
            "target": edge.node_end.node_id,
            "value": self._apply_hook(self._serialize_edge_value, edge.value),
            "weight": edge.weight,
            "bidirectional": edge.bidirectional,
        }
        metadata: dict[str, Any] = MetadataSerializer.to_dict(edge.metadata)
        if metadata:
            edge_dict["metadata"] = metadata
        return edge_dict

    @staticmethod
    def _apply_hook(hook: Callable[[Any], Any] | None, value: Any) -> Any:
        """Apply an optional serialization hook to a value."""
        return hook(value) if hook is not None else value
