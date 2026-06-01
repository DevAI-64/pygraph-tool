"""Internal serialization of :class:`pygraph_tool.Metadata` instances.

Defines :class:`MetadataSerializer`, which converts metadata to and from
JSON-compatible dictionaries. Metadata sets are exported as sorted lists to
produce deterministic output.
"""

from __future__ import annotations

from collections.abc import Mapping
from typing import Any

from pygraph_tool.core.metadata import Metadata
from pygraph_tool.exceptions.graph_exceptions import SerializationException


class MetadataSerializer:
    """Serialize and deserialize :class:`Metadata` instances."""

    @classmethod
    def to_dict(cls, metadata: Metadata) -> dict[str, Any]:
        """Convert metadata to a JSON-compatible dictionary.

        Empty collections are omitted to keep the output compact. Metadata sets
        are exported as sorted lists to produce deterministic output.

        Args:
            metadata: Metadata to convert.

        Returns:
            A dictionary containing only non-empty metadata fields.
        """
        result: dict[str, Any] = {}

        if metadata.tags:
            result["tags"] = sorted(metadata.tags)
        if metadata.categories:
            result["categories"] = sorted(metadata.categories)
        if metadata.layers:
            result["layers"] = sorted(metadata.layers)
        if metadata.flags:
            result["flags"] = sorted(metadata.flags)
        if metadata.properties:
            result["properties"] = dict(metadata.properties)

        return result

    @classmethod
    def from_dict(cls, data: Mapping[str, Any]) -> Metadata:
        """Build metadata from a serialized dictionary.

        Missing fields default to empty collections.

        Args:
            data: Mapping containing serialized metadata fields.

        Raises:
            SerializationException: If a metadata field has an invalid type.

        Returns:
            A new metadata instance.
        """
        return Metadata(
            tags=cls._string_set(data, "tags"),
            categories=cls._string_set(data, "categories"),
            layers=cls._string_set(data, "layers"),
            flags=cls._string_set(data, "flags"),
            properties=cls._properties(data),
        )

    @staticmethod
    def _string_set(data: Mapping[str, Any], key: str) -> set[str]:
        """Return a set of strings from an optional list field.

        Args:
            data: Serialized metadata mapping.
            key: Field name to read.

        Raises:
            SerializationException: If the field is not a list of strings.

        Returns:
            A set containing the field values, or an empty set when missing.
        """
        if key not in data:
            return set()

        value: Any = data[key]

        if not isinstance(value, list) or any(
            not isinstance(item, str) for item in value
        ):
            raise SerializationException(
                f"The metadata field '{key}' must be a list of strings."
            )

        return set(value)

    @staticmethod
    def _properties(data: Mapping[str, Any]) -> dict[str, object]:
        """Return metadata properties from an optional mapping field.

        Args:
            data: Serialized metadata mapping.

        Raises:
            SerializationException: If the properties field is not a mapping.

        Returns:
            Metadata properties as a plain dictionary.
        """
        if "properties" not in data:
            return {}

        value: Any = data["properties"]

        if not isinstance(value, Mapping):
            raise SerializationException(
                "The metadata field 'properties' must be a mapping."
            )

        return dict(value)
