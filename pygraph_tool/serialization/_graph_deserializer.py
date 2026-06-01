"""Internal dictionary-to-graph and JSON-to-graph deserialization.

Defines :class:`GraphDeserializer`, used by :class:`pygraph_tool.Graph` to
rebuild a graph from standard Python containers or JSON text. It relies only on
the Python standard library, validates its input, and raises
:class:`pygraph_tool.SerializationException` on malformed or inconsistent data.
"""

from __future__ import annotations

import json
from collections.abc import Callable, Mapping
from typing import TYPE_CHECKING, Any

from pygraph_tool.core.metadata import Metadata
from pygraph_tool.exceptions.graph_exceptions import (
    PyGraphToolException,
    SerializationException,
)

from ._metadata_serializer import MetadataSerializer

if TYPE_CHECKING:
    from pygraph_tool.core.graph import Graph

SCHEMA_VERSION = "1.0"
"""Version of the serialized graph format produced by this module."""


class GraphDeserializer:
    """Deserialize graph data from dictionaries or JSON text."""

    def __init__(
        self,
        *,
        deserialize_node_value: Callable[[Any], Any] | None = None,
        deserialize_edge_value: Callable[[Any], Any] | None = None,
    ) -> None:
        """Initialize a graph deserializer.

        Args:
            deserialize_node_value: Optional callable converting stored node
                values back into their in-memory form.
            deserialize_edge_value: Optional callable converting stored edge
                values back into their in-memory form.
        """
        self._deserialize_node_value = deserialize_node_value
        self._deserialize_edge_value = deserialize_edge_value

    def populate_graph(self, graph: Graph[Any, Any], data: Any) -> None:
        """Populate an empty graph from serialized graph data.

        All nodes are added before edges so that edge endpoints exist before
        relationships are restored. Graph model errors are re-raised as
        :class:`SerializationException`.

        Args:
            graph: Empty graph to populate.
            data: Serialized graph mapping.

        Raises:
            SerializationException: If the data is malformed or inconsistent.
        """
        if not isinstance(data, Mapping):
            raise SerializationException("The serialized graph must be a mapping.")

        self._validate_schema_version(data)

        for node_data in self._sequence_field(data, "nodes"):
            self._add_node(graph, node_data)

        for edge_data in self._sequence_field(data, "edges"):
            self._add_edge(graph, edge_data)

    @classmethod
    def parse_json(cls, text: str) -> Any:
        """Parse JSON text into a Python object.

        Args:
            text: JSON text to parse.

        Raises:
            SerializationException: If the text is not valid JSON.

        Returns:
            The parsed Python object.
        """
        try:
            return json.loads(text)
        except json.JSONDecodeError as exception:
            raise SerializationException(
                "The graph JSON text is invalid."
            ) from exception

    @staticmethod
    def _validate_schema_version(data: Mapping[str, Any]) -> None:
        """Validate that the data declares a supported schema version."""
        version: Any = data.get("schema_version")
        if version != SCHEMA_VERSION:
            raise SerializationException(
                f"Unsupported or missing 'schema_version'. Expected '{SCHEMA_VERSION}'."
            )

    @staticmethod
    def _sequence_field(data: Mapping[str, Any], key: str) -> list[Any]:
        """Return a list field from serialized graph data."""
        value: Any = data.get(key, [])
        if not isinstance(value, list):
            raise SerializationException(f"The '{key}' field must be a list.")
        return value

    def _add_node(self, graph: Graph[Any, Any], node_data: Any) -> None:
        """Add one serialized node to the graph."""
        if not isinstance(node_data, Mapping):
            raise SerializationException("Each node must be a mapping.")

        node_id = self._require_str(node_data, "id", "node")
        value = self._apply_hook(self._deserialize_node_value, node_data.get("value"))
        metadata = self._metadata_field(node_data)

        try:
            graph.add_node(value=value, node_id=node_id, metadata=metadata)
        except PyGraphToolException as exception:
            raise SerializationException(str(exception)) from exception

    def _add_edge(self, graph: Graph[Any, Any], edge_data: Any) -> None:
        """Add one serialized edge to the graph."""
        if not isinstance(edge_data, Mapping):
            raise SerializationException("Each edge must be a mapping.")

        edge_id = self._require_str(edge_data, "id", "edge")
        source = self._require_str(edge_data, "source", "edge")
        target = self._require_str(edge_data, "target", "edge")
        value = self._apply_hook(self._deserialize_edge_value, edge_data.get("value"))
        metadata = self._metadata_field(edge_data)

        try:
            graph.add_edge(
                node_id_start=source,
                node_id_end=target,
                value=value,
                edge_id=edge_id,
                weight=self._weight_field(edge_data),
                bidirectional=self._bool_field(edge_data, "bidirectional"),
                metadata=metadata,
            )
        except PyGraphToolException as exception:
            raise SerializationException(str(exception)) from exception

    @staticmethod
    def _apply_hook(hook: Callable[[Any], Any] | None, value: Any) -> Any:
        """Apply an optional deserialization hook to a value."""
        return hook(value) if hook is not None else value

    @staticmethod
    def _metadata_field(data: Mapping[str, Any]) -> Metadata:
        """Build metadata from an optional serialized metadata field."""
        metadata_data: Any = data.get("metadata")
        if metadata_data is None:
            return Metadata()
        if not isinstance(metadata_data, Mapping):
            raise SerializationException("The 'metadata' field must be a mapping.")
        return MetadataSerializer.from_dict(metadata_data)

    @staticmethod
    def _require_str(data: Mapping[str, Any], key: str, context: str) -> str:
        """Return a required string field from serialized data."""
        if key not in data:
            raise SerializationException(f"Missing key '{key}' in {context}.")
        value: Any = data[key]
        if not isinstance(value, str):
            raise SerializationException(f"The '{key}' of {context} must be a string.")
        return value

    @staticmethod
    def _weight_field(edge_data: Mapping[str, Any]) -> float:
        """Return an edge weight from serialized edge data."""
        value: Any = edge_data.get("weight", 1.0)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            raise SerializationException("The edge 'weight' must be a number.")
        return float(value)

    @staticmethod
    def _bool_field(edge_data: Mapping[str, Any], key: str) -> bool:
        """Return a boolean edge field from serialized edge data."""
        value: Any = edge_data.get(key, False)
        if not isinstance(value, bool):
            raise SerializationException(f"The edge '{key}' must be a boolean.")
        return value
