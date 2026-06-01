"""Tests covering graph serialization and deserialization."""

from datetime import datetime
from pathlib import Path
from typing import Any

import pytest

from pygraph_tool import Graph, Metadata, Node, SerializationException


def _node_ids(nodes: tuple[Node[Any], ...] | list[Node[Any]]) -> list[str]:
    """Return node identifiers in order."""
    return [node.node_id for node in nodes]


def _build_sample_graph() -> Graph[str, str]:
    """Return a small graph exercising metadata, weights, and directions."""
    graph: Graph[str, str] = Graph()
    graph.add_node(
        value="Idle",
        node_id="idle",
        metadata=Metadata(
            tags={"start"},
            categories={"state"},
            layers={"core"},
            flags={"initial"},
            properties={"x": 1, "y": [1, 2, 3]},
        ),
    )
    graph.add_node(value="Running", node_id="running")
    graph.add_unidirectional_edge(
        node_id_start="idle",
        node_id_end="running",
        edge_id="start",
        value="START",
        weight=2.0,
        metadata=Metadata(categories={"transition"}),
    )
    graph.add_bidirectional_edge(
        node_id_start="running",
        node_id_end="idle",
        edge_id="loop",
    )
    return graph


def test_to_dict_and_from_dict_round_trip_on_empty_graph() -> None:
    graph: Graph[str, str] = Graph()

    data = graph.to_dict()

    assert data == {"schema_version": "1.0", "nodes": [], "edges": []}

    restored = Graph.from_dict(data)

    assert restored.nodes == ()
    assert restored.edges == ()


def test_to_dict_includes_schema_version() -> None:
    assert Graph().to_dict()["schema_version"] == "1.0"


def test_round_trip_preserves_nodes_edges_and_metadata() -> None:
    restored = Graph.from_dict(_build_sample_graph().to_dict())

    assert _node_ids(restored.nodes) == ["idle", "running"]
    assert {edge.edge_id for edge in restored.edges} == {"start", "loop"}

    idle = restored.get_node("idle")
    assert idle.value == "Idle"
    assert idle.metadata.tags == {"start"}
    assert idle.metadata.categories == {"state"}
    assert idle.metadata.layers == {"core"}
    assert idle.metadata.flags == {"initial"}
    assert idle.metadata.properties == {"x": 1, "y": [1, 2, 3]}

    start = restored.get_edge("start")
    assert start.value == "START"
    assert start.weight == 2.0
    assert start.bidirectional is False
    assert start.node_start.node_id == "idle"
    assert start.node_end.node_id == "running"
    assert start.metadata.categories == {"transition"}

    loop = restored.get_edge("loop")
    assert loop.value is None
    assert loop.weight == 1.0
    assert loop.bidirectional is True


def test_round_trip_rebuilds_adjacency_indexes() -> None:
    restored = Graph.from_dict(_build_sample_graph().to_dict())

    assert _node_ids(restored.get_successors("idle")) == ["running"]
    assert {node.node_id for node in restored.get_neighbors("idle")} == {"running"}
    assert {edge.edge_id for edge in restored.get_incident_edges("idle")} == {
        "start",
        "loop",
    }


def test_metadata_sets_are_serialized_as_sorted_lists() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node(value="n", node_id="n", metadata=Metadata(tags={"c", "a", "b"}))

    data = graph.to_dict()

    assert data["nodes"][0]["metadata"]["tags"] == ["a", "b", "c"]


def test_empty_metadata_is_omitted_from_output() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node(value="n", node_id="n")
    graph.add_node(value="m", node_id="m")
    graph.add_unidirectional_edge("n", "m", edge_id="e")

    data = graph.to_dict()

    assert "metadata" not in data["nodes"][0]
    assert "metadata" not in data["edges"][0]


def test_to_json_and_from_json_round_trip() -> None:
    text = _build_sample_graph().to_json(indent=2, sort_keys=True)

    assert isinstance(text, str)

    restored = Graph.from_json(text)

    assert _node_ids(restored.nodes) == ["idle", "running"]
    assert {edge.edge_id for edge in restored.edges} == {"start", "loop"}
    assert restored.get_edge("start").weight == 2.0


def test_save_json_and_load_json_round_trip(tmp_path: Path) -> None:
    graph = _build_sample_graph()
    path = tmp_path / "graph.json"

    graph.save_json(path)

    assert path.exists()
    assert path.read_text(encoding="utf-8").startswith("{\n")

    restored = Graph.load_json(path)

    assert _node_ids(restored.nodes) == ["idle", "running"]
    assert restored.get_edge("start").weight == 2.0


def test_save_json_and_load_json_accept_string_paths(tmp_path: Path) -> None:
    path = tmp_path / "graph.json"

    _build_sample_graph().save_json(str(path))
    restored = Graph.load_json(str(path))

    assert _node_ids(restored.nodes) == ["idle", "running"]


def test_from_dict_applies_value_hooks() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}],
        "edges": [],
    }

    restored = Graph.from_dict(data, deserialize_node_value=lambda value: value + 41)

    assert restored.get_node("a").value == 42


def test_to_json_raises_on_non_serializable_value_without_hook() -> None:
    graph: Graph[datetime, str] = Graph()
    graph.add_node(value=datetime(2026, 6, 1), node_id="n")

    with pytest.raises(SerializationException):
        graph.to_json()


def test_from_dict_allows_missing_node_and_edge_lists() -> None:
    restored = Graph.from_dict({"schema_version": "1.0"})

    assert restored.nodes == ()
    assert restored.edges == ()


def test_from_dict_applies_defaults_for_optional_fields() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a"}, {"id": "b"}],
        "edges": [{"id": "e", "source": "a", "target": "b"}],
    }

    restored = Graph.from_dict(data)

    assert restored.get_node("a").value is None
    edge = restored.get_edge("e")
    assert edge.weight == 1.0
    assert edge.bidirectional is False


def test_from_dict_rejects_non_mapping() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict(["not", "a", "mapping"])  # type: ignore[arg-type]


def test_from_dict_rejects_unsupported_schema_version() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "999", "nodes": [], "edges": []})


def test_from_dict_rejects_missing_schema_version() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"nodes": [], "edges": []})


def test_from_dict_rejects_non_list_nodes() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "1.0", "nodes": {}, "edges": []})


def test_from_dict_rejects_non_list_edges() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "1.0", "nodes": [], "edges": {}})


def test_from_dict_rejects_non_mapping_node() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "1.0", "nodes": ["bad"], "edges": []})


def test_from_dict_rejects_node_without_id() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "1.0", "nodes": [{"value": 1}], "edges": []})


def test_from_dict_rejects_non_string_node_id() -> None:
    with pytest.raises(SerializationException):
        Graph.from_dict({"schema_version": "1.0", "nodes": [{"id": 5}], "edges": []})


def test_from_dict_rejects_blank_node_id() -> None:
    data = {"schema_version": "1.0", "nodes": [{"id": "   ", "value": 1}], "edges": []}

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_duplicate_node_id() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "n", "value": 1}, {"id": "n", "value": 2}],
        "edges": [],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_mapping_edge() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}],
        "edges": ["bad"],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_edge_without_source() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}],
        "edges": [{"id": "e", "target": "a"}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_edge_with_unknown_node() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}],
        "edges": [{"id": "e", "source": "a", "target": "missing"}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_duplicate_edge_id() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        "edges": [
            {"id": "e", "source": "a", "target": "b"},
            {"id": "e", "source": "b", "target": "a"},
        ],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_numeric_weight() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        "edges": [{"id": "e", "source": "a", "target": "b", "weight": "heavy"}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_boolean_weight() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        "edges": [{"id": "e", "source": "a", "target": "b", "weight": True}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_finite_weight() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        "edges": [{"id": "e", "source": "a", "target": "b", "weight": float("inf")}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_boolean_bidirectional() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1}, {"id": "b", "value": 2}],
        "edges": [{"id": "e", "source": "a", "target": "b", "bidirectional": "yes"}],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_mapping_metadata() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1, "metadata": []}],
        "edges": [],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_list_metadata_field() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1, "metadata": {"tags": "single"}}],
        "edges": [],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_dict_rejects_non_mapping_properties() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [{"id": "a", "value": 1, "metadata": {"properties": [1, 2]}}],
        "edges": [],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_from_json_rejects_invalid_json() -> None:
    with pytest.raises(SerializationException):
        Graph.from_json("{not valid json")


def test_from_dict_rejects_non_string_metadata_item() -> None:
    data = {
        "schema_version": "1.0",
        "nodes": [
            {
                "id": "a",
                "value": 1,
                "metadata": {"tags": [1]},
            }
        ],
        "edges": [],
    }

    with pytest.raises(SerializationException):
        Graph.from_dict(data)


def test_to_json_rejects_nan_values() -> None:
    graph: Graph[float, str] = Graph()
    graph.add_node(float("nan"), node_id="n")

    with pytest.raises(SerializationException):
        graph.to_json()
