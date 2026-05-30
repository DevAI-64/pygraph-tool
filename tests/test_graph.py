"""Tests for pygraph-tool."""

from collections.abc import Iterable
from math import inf, nan
from typing import Any
from uuid import UUID

import pytest

from pygraph_tool import Edge, Graph, GraphException, Metadata, Node, NodeException
from pygraph_tool.graph_exceptions import EdgeException


def _ids(items: Iterable[Node[Any]]) -> set[str]:
    """Return node identifiers from a node collection."""
    return {item.node_id for item in items}


def _edge_ids(items: Iterable[Edge[Any, Any]]) -> set[str]:
    """Return edge identifiers from an edge collection."""
    return {item.edge_id for item in items}


@pytest.fixture
def node_a() -> Node[str]:
    """Return a first test node."""
    return Node(value="A", node_id="a")


@pytest.fixture
def node_b() -> Node[str]:
    """Return a second test node."""
    return Node(value="B", node_id="b")


@pytest.fixture
def empty_graph() -> Graph[object, object]:
    """Return an empty graph."""
    return Graph()


@pytest.fixture
def graph_with_nodes() -> Graph[str, object]:
    """Return a graph containing three nodes."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_node(value="C", node_id="c")
    return graph


@pytest.fixture
def graph_with_edges() -> Graph[str, str]:
    """Return a graph containing three nodes and three edges."""
    graph: Graph[str, str] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_node(value="C", node_id="c")
    graph.add_unidirectional_edge(
        node_id_start="a",
        node_id_end="b",
        value="a-to-b",
        edge_id="ab",
    )
    graph.add_unidirectional_edge(
        node_id_start="c",
        node_id_end="b",
        value="c-to-b",
        edge_id="cb",
    )
    graph.add_bidirectional_edge(
        node_id_start="a",
        node_id_end="c",
        value="a-and-c",
        edge_id="ac",
    )
    return graph


def test_public_exports_are_importable() -> None:
    """Verify that the main public classes are importable from the package."""
    assert Graph is not None
    assert Node is not None
    assert Edge is not None
    assert Metadata is not None


def test_metadata_defaults_are_independent() -> None:
    """Verify that default metadata collections are not shared."""
    first = Metadata()
    second = Metadata()

    first.tags.add("python")
    first.categories.add("concept")
    first.layers.add("knowledge")
    first.flags.add("visible")
    first.properties["priority"] = 1

    assert second.tags == set()
    assert second.categories == set()
    assert second.layers == set()
    assert second.flags == set()
    assert second.properties == {}


def test_metadata_helpers_return_expected_membership() -> None:
    """Verify metadata membership helper methods."""
    metadata = Metadata(
        tags={"python"},
        categories={"concept"},
        layers={"knowledge"},
        flags={"visible"},
    )

    assert metadata.has_tag("python")
    assert not metadata.has_tag("java")
    assert metadata.has_category("concept")
    assert not metadata.has_category("document")
    assert metadata.has_layer("knowledge")
    assert not metadata.has_layer("ui")
    assert metadata.has_flag("visible")
    assert not metadata.has_flag("hidden")


def test_node_uses_provided_identifier() -> None:
    """Verify that a node keeps a provided identifier."""
    node = Node(value="content", node_id="node-1")

    assert node.node_id == "node-1"
    assert node.value == "content"


def test_node_generates_uuid_identifier_when_missing() -> None:
    """Verify that a node generates a UUID identifier when omitted."""
    node = Node(value="content")

    UUID(node.node_id)


def test_node_rejects_empty_identifier() -> None:
    """Verify that a node rejects an empty identifier."""
    with pytest.raises(NodeException):
        Node(value="content", node_id="")


def test_node_uses_default_metadata() -> None:
    """Verify that a node receives empty metadata by default."""
    node = Node(value="content", node_id="node-1")

    assert isinstance(node.metadata, Metadata)
    assert node.metadata.tags == set()


def test_node_uses_provided_metadata() -> None:
    """Verify that a node keeps provided metadata."""
    metadata = Metadata(tags={"important"})
    node = Node(value="content", node_id="node-1", metadata=metadata)

    assert node.metadata is metadata


def test_node_value_can_be_replaced() -> None:
    """Verify that a node value is mutable."""
    node = Node(value={"version": 1}, node_id="node-1")

    node.value = {"version": 2}

    assert node.value == {"version": 2}


def test_node_identifier_is_read_only() -> None:
    """Verify that the public node identifier cannot be reassigned."""
    node = Node(value="content", node_id="node-1")

    with pytest.raises(AttributeError):
        node.node_id = "node-2"  # type: ignore[misc]


def test_nodes_are_equal_by_identifier() -> None:
    """Verify that nodes are compared by identifier only."""
    first = Node(value="old", node_id="node-1")
    second = Node(value="new", node_id="node-1")
    third = Node(value="old", node_id="node-2")

    assert first == second
    assert first != third
    assert first != object()


def test_edge_uses_provided_identifier(node_a: Node[str], node_b: Node[str]) -> None:
    """Verify that an edge keeps a provided identifier."""
    edge: Edge[str, object] = Edge(
        node_start=node_a,
        node_end=node_b,
        edge_id="edge-1",
    )

    assert edge.edge_id == "edge-1"
    assert edge.node_start is node_a
    assert edge.node_end is node_b
    assert edge.weight == 1.0
    assert not edge.bidirectional


def test_edge_generates_uuid_identifier_when_missing(
    node_a: Node[str],
    node_b: Node[str],
) -> None:
    """Verify that an edge generates a UUID identifier when omitted."""
    edge: Edge[str, object] = Edge(node_start=node_a, node_end=node_b)

    UUID(edge.edge_id)


@pytest.mark.parametrize("edge_id", ["", "   "])
def test_edge_rejects_empty_or_blank_identifier(
    node_a: Node[str],
    node_b: Node[str],
    edge_id: str,
) -> None:
    """Verify that an edge rejects empty and blank identifiers."""
    with pytest.raises(EdgeException):
        Edge(node_start=node_a, node_end=node_b, edge_id=edge_id)


@pytest.mark.parametrize("weight", [inf, -inf, nan])
def test_edge_rejects_non_finite_weight(
    node_a: Node[str],
    node_b: Node[str],
    weight: float,
) -> None:
    """Verify that an edge rejects non-finite weights."""
    with pytest.raises(EdgeException):
        Edge(node_start=node_a, node_end=node_b, weight=weight)


def test_edge_accepts_value_metadata_weight_and_bidirectional_flag(
    node_a: Node[str],
    node_b: Node[str],
) -> None:
    """Verify edge value, metadata, weight, and bidirectional flag."""
    metadata = Metadata(tags={"relation"})
    edge: Edge[str, dict[str, str]] = Edge(
        node_start=node_a,
        node_end=node_b,
        value={"type": "supports"},
        edge_id="edge-1",
        weight=0.7,
        bidirectional=True,
        metadata=metadata,
    )

    assert edge.value == {"type": "supports"}
    assert edge.weight == 0.7
    assert edge.bidirectional
    assert edge.metadata is metadata


def test_edge_value_weight_and_metadata_can_change(
    node_a: Node[str],
    node_b: Node[str],
) -> None:
    """Verify that mutable edge fields can evolve without replacing the edge."""
    edge: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="old",
        edge_id="edge-1",
    )

    edge.value = "new"
    edge.weight = 2.5
    edge.metadata.tags.add("reviewed")

    assert edge.value == "new"
    assert edge.weight == 2.5
    assert edge.metadata.has_tag("reviewed")


def test_edge_structural_properties_are_read_only(
    node_a: Node[str],
    node_b: Node[str],
) -> None:
    """Verify that public structural edge properties cannot be reassigned."""
    edge: Edge[str, object] = Edge(
        node_start=node_a,
        node_end=node_b,
        edge_id="edge-1",
    )

    with pytest.raises(AttributeError):
        edge.edge_id = "edge-2"  # type: ignore[misc]
    with pytest.raises(AttributeError):
        edge.node_start = node_b  # type: ignore[misc]
    with pytest.raises(AttributeError):
        edge.node_end = node_a  # type: ignore[misc]
    with pytest.raises(AttributeError):
        edge.bidirectional = True  # type: ignore[misc]


def test_edges_are_equal_and_hashed_by_identifier(
    node_a: Node[str],
    node_b: Node[str],
) -> None:
    """Verify edge equality and hashing by identifier."""
    first: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="old",
        edge_id="edge-1",
    )
    second: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="new",
        edge_id="edge-1",
    )
    third: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="old",
        edge_id="edge-2",
    )

    assert first == second
    assert first != third
    assert first != object()
    assert len({first, second, third}) == 2


def test_graph_starts_empty(empty_graph: Graph[object, object]) -> None:
    """Verify that a graph starts without nodes or edges."""
    assert empty_graph.nodes == ()
    assert empty_graph.edges == ()


def test_graph_nodes_and_edges_properties_are_tuples(
    graph_with_edges: Graph[str, str],
) -> None:
    """Verify that graph collections are exposed as tuples."""
    assert isinstance(graph_with_edges.nodes, tuple)
    assert isinstance(graph_with_edges.edges, tuple)


def test_add_node_returns_and_stores_node(empty_graph: Graph[object, object]) -> None:
    """Verify that adding a node returns and stores it."""
    metadata = Metadata(tags={"tag"})
    node = empty_graph.add_node(
        value={"name": "Python"},
        node_id="python",
        metadata=metadata,
    )

    assert node.node_id == "python"
    assert node.value == {"name": "Python"}
    assert node.metadata is metadata
    assert empty_graph.is_node("python")
    assert empty_graph.get_node("python") is node


@pytest.mark.parametrize("value", [None, 0, False, "", [], {}])
def test_add_node_accepts_any_value(value: object) -> None:
    """Verify that graph nodes can store any user-defined value."""
    graph: Graph[object, object] = Graph()

    node = graph.add_node(value=value, node_id="node")

    assert node.value == value


def test_add_node_generates_unique_identifiers() -> None:
    """Verify that nodes added without identifiers receive unique UUIDs."""
    graph: Graph[str, object] = Graph()

    first = graph.add_node(value="first")
    second = graph.add_node(value="second")

    assert first.node_id != second.node_id
    UUID(first.node_id)
    UUID(second.node_id)


def test_add_node_rejects_duplicate_identifier(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that a graph rejects duplicate node identifiers."""
    with pytest.raises(GraphException):
        graph_with_nodes.add_node(value="duplicate", node_id="a")


def test_get_node_rejects_unknown_identifier(
    empty_graph: Graph[object, object],
) -> None:
    """Verify that getting an unknown node raises a graph exception."""
    with pytest.raises(GraphException):
        empty_graph.get_node("missing")


def test_add_unidirectional_edge_returns_and_stores_edge(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that adding a unidirectional edge returns and stores it."""
    edge = graph_with_nodes.add_unidirectional_edge(
        node_id_start="a",
        node_id_end="b",
        value="relation",
        edge_id="ab",
        weight=2.0,
        metadata=Metadata(tags={"dependency"}),
    )

    assert edge.edge_id == "ab"
    assert edge.value == "relation"
    assert edge.weight == 2.0
    assert edge.node_start.node_id == "a"
    assert edge.node_end.node_id == "b"
    assert not edge.bidirectional
    assert edge.metadata.has_tag("dependency")
    assert graph_with_nodes.is_edge("ab")
    assert graph_with_nodes.get_edge("ab") is edge


def test_add_bidirectional_edge_returns_bidirectional_edge(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that adding a bidirectional edge marks it as bidirectional."""
    edge = graph_with_nodes.add_bidirectional_edge(
        node_id_start="a",
        node_id_end="b",
        edge_id="ab",
    )

    assert edge.bidirectional
    assert graph_with_nodes.is_edge("ab")


def test_add_edge_generates_uuid_identifier_when_missing(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that an edge added without identifier receives a UUID."""
    edge = graph_with_nodes.add_edge(node_id_start="a", node_id_end="b")

    UUID(edge.edge_id)
    assert graph_with_nodes.get_edge(edge.edge_id) is edge


def test_add_edge_rejects_missing_start_node(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that adding an edge with an unknown start node fails."""
    with pytest.raises(GraphException):
        graph_with_nodes.add_edge(
            node_id_start="missing",
            node_id_end="b",
            edge_id="edge",
        )


def test_add_edge_rejects_missing_end_node(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that adding an edge with an unknown end node fails."""
    with pytest.raises(GraphException):
        graph_with_nodes.add_edge(
            node_id_start="a",
            node_id_end="missing",
            edge_id="edge",
        )


def test_add_edge_rejects_duplicate_identifier(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that a graph rejects duplicate edge identifiers."""
    graph_with_nodes.add_edge(node_id_start="a", node_id_end="b", edge_id="edge")

    with pytest.raises(GraphException):
        graph_with_nodes.add_edge(node_id_start="b", node_id_end="c", edge_id="edge")


def test_graph_allows_multiple_edges_between_same_nodes(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify that multiple edges can connect the same nodes if ids differ."""
    first = graph_with_nodes.add_edge(node_id_start="a", node_id_end="b", edge_id="e1")
    second = graph_with_nodes.add_edge(node_id_start="a", node_id_end="b", edge_id="e2")

    assert first.edge_id == "e1"
    assert second.edge_id == "e2"
    assert _edge_ids(graph_with_nodes.edges) == {"e1", "e2"}


def test_get_edge_rejects_unknown_identifier(
    empty_graph: Graph[object, object],
) -> None:
    """Verify that getting an unknown edge raises a graph exception."""
    with pytest.raises(GraphException):
        empty_graph.get_edge("missing")


def test_remove_edge_returns_and_removes_edge(
    graph_with_edges: Graph[str, str],
) -> None:
    """Verify that removing an edge returns and removes it."""
    removed = graph_with_edges.remove_edge("ab")

    assert removed.edge_id == "ab"
    assert not graph_with_edges.is_edge("ab")


def test_remove_edge_rejects_unknown_identifier(
    empty_graph: Graph[object, object],
) -> None:
    """Verify that removing an unknown edge raises a graph exception."""
    with pytest.raises(GraphException):
        empty_graph.remove_edge("missing")


def test_remove_node_returns_node_and_removes_incident_edges(
    graph_with_edges: Graph[str, str],
) -> None:
    """Verify that removing a node also removes all connected edges."""
    removed = graph_with_edges.remove_node("a")

    assert removed.node_id == "a"
    assert not graph_with_edges.is_node("a")
    assert not graph_with_edges.is_edge("ab")
    assert not graph_with_edges.is_edge("ac")
    assert graph_with_edges.is_edge("cb")


def test_remove_node_rejects_unknown_identifier(
    empty_graph: Graph[object, object],
) -> None:
    """Verify that removing an unknown node raises a graph exception."""
    with pytest.raises(GraphException):
        empty_graph.remove_node("missing")


def test_unidirectional_successors_and_predecessors() -> None:
    """Verify successors and predecessors for a unidirectional edge."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_unidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab")

    assert _ids(graph.get_successors("a")) == {"b"}
    assert graph.get_predecessors("a") == []
    assert graph.get_successors("b") == []
    assert _ids(graph.get_predecessors("b")) == {"a"}


def test_bidirectional_successors_and_predecessors() -> None:
    """Verify successors and predecessors for a bidirectional edge."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_bidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab")

    assert _ids(graph.get_successors("a")) == {"b"}
    assert _ids(graph.get_predecessors("a")) == {"b"}
    assert _ids(graph.get_successors("b")) == {"a"}
    assert _ids(graph.get_predecessors("b")) == {"a"}


def test_successors_and_predecessors_remove_duplicate_nodes() -> None:
    """Verify duplicate neighbor nodes are removed from traversal results."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_unidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab")
    graph.add_unidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab-2")
    graph.add_bidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab-bi")
    graph.add_unidirectional_edge(node_id_start="b", node_id_end="a", edge_id="ba")

    successors = graph.get_successors("a")
    predecessors = graph.get_predecessors("a")

    assert _ids(successors) == {"b"}
    assert len(successors) == 1
    assert _ids(predecessors) == {"b"}
    assert len(predecessors) == 1


def test_traversal_rejects_unknown_node(empty_graph: Graph[object, object]) -> None:
    """Verify traversal methods raise when the node does not exist."""
    with pytest.raises(GraphException):
        empty_graph.get_successors("missing")
    with pytest.raises(GraphException):
        empty_graph.get_predecessors("missing")
    with pytest.raises(GraphException):
        empty_graph.get_outgoing_edges("missing")
    with pytest.raises(GraphException):
        empty_graph.get_incoming_edges("missing")
    with pytest.raises(GraphException):
        empty_graph.get_incident_edges("missing")


def test_outgoing_incoming_and_incident_edges_with_unidirectional_edge() -> None:
    """Verify edge traversal for a unidirectional edge."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_unidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab")

    assert _edge_ids(graph.get_outgoing_edges("a")) == {"ab"}
    assert graph.get_incoming_edges("a") == []
    assert graph.get_outgoing_edges("b") == []
    assert _edge_ids(graph.get_incoming_edges("b")) == {"ab"}
    assert _edge_ids(graph.get_incident_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_incident_edges("b")) == {"ab"}


def test_outgoing_incoming_and_incident_edges_with_bidirectional_edge() -> None:
    """Verify edge traversal for a bidirectional edge."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_bidirectional_edge(node_id_start="a", node_id_end="b", edge_id="ab")

    assert _edge_ids(graph.get_outgoing_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_incoming_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_outgoing_edges("b")) == {"ab"}
    assert _edge_ids(graph.get_incoming_edges("b")) == {"ab"}
    assert _edge_ids(graph.get_incident_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_incident_edges("b")) == {"ab"}


def test_incident_edges_remove_duplicate_self_loop() -> None:
    """Verify self-loop edges are returned only once."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_edge(node_id_start="a", node_id_end="a", edge_id="aa")

    assert _edge_ids(graph.get_outgoing_edges("a")) == {"aa"}
    assert _edge_ids(graph.get_incoming_edges("a")) == {"aa"}
    assert _edge_ids(graph.get_incident_edges("a")) == {"aa"}
    assert _ids(graph.get_successors("a")) == {"a"}
    assert _ids(graph.get_predecessors("a")) == {"a"}


def test_filter_nodes_with_predicate(graph_with_nodes: Graph[str, object]) -> None:
    """Verify node filtering with a custom predicate."""
    nodes = graph_with_nodes.filter_nodes(lambda node: node.node_id in {"a", "c"})

    assert _ids(nodes) == {"a", "c"}


def test_filter_edges_with_predicate(graph_with_edges: Graph[str, str]) -> None:
    """Verify edge filtering with a custom predicate."""
    edges = graph_with_edges.filter_edges(lambda edge: edge.bidirectional)

    assert _edge_ids(edges) == {"ac"}


def test_filter_nodes_by_metadata_match_all() -> None:
    """Verify node metadata filtering with all expected values required."""
    graph: Graph[str, object] = Graph()
    graph.add_node(
        value="Python",
        node_id="python",
        metadata=Metadata(
            tags={"python", "oop"},
            categories={"concept"},
            layers={"knowledge", "training"},
            flags={"visible"},
        ),
    )
    graph.add_node(
        value="Java",
        node_id="java",
        metadata=Metadata(tags={"java", "oop"}, layers={"knowledge"}),
    )

    nodes = graph.filter_nodes_by_metadata(
        tags=["python", "oop"],
        layers=["knowledge"],
        match_all=True,
    )

    assert _ids(nodes) == {"python"}


def test_filter_nodes_by_metadata_match_any_within_each_criterion() -> None:
    """Verify metadata match_all=False applies within each criterion."""
    graph: Graph[str, object] = Graph()
    graph.add_node(
        value="Python",
        node_id="python",
        metadata=Metadata(tags={"python"}, layers={"knowledge"}),
    )
    graph.add_node(
        value="Java",
        node_id="java",
        metadata=Metadata(tags={"java"}, layers={"knowledge"}),
    )
    graph.add_node(
        value="Hidden Python",
        node_id="hidden-python",
        metadata=Metadata(tags={"python"}, layers={"archive"}),
    )

    nodes = graph.filter_nodes_by_metadata(
        tags=["python", "java"],
        layers=["knowledge"],
        match_all=False,
    )

    assert _ids(nodes) == {"python", "java"}


def test_filter_nodes_by_metadata_uses_categories_and_flags() -> None:
    """Verify metadata filtering by categories and flags."""
    graph: Graph[str, object] = Graph()
    graph.add_node(
        value="Visible concept",
        node_id="visible-concept",
        metadata=Metadata(categories={"concept"}, flags={"visible"}),
    )
    graph.add_node(
        value="Hidden concept",
        node_id="hidden-concept",
        metadata=Metadata(categories={"concept"}, flags={"hidden"}),
    )

    nodes = graph.filter_nodes_by_metadata(
        categories=["concept"],
        flags=["visible"],
    )

    assert _ids(nodes) == {"visible-concept"}


def test_filter_nodes_by_metadata_with_no_criteria_returns_all_nodes(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify empty node metadata criteria return all nodes."""
    nodes = graph_with_nodes.filter_nodes_by_metadata()

    assert _ids(nodes) == {"a", "b", "c"}


def test_filter_nodes_by_metadata_with_empty_iterable_returns_all_nodes(
    graph_with_nodes: Graph[str, object],
) -> None:
    """Verify empty metadata iterable criteria do not filter nodes."""
    nodes = graph_with_nodes.filter_nodes_by_metadata(tags=[])

    assert _ids(nodes) == {"a", "b", "c"}


def test_filter_edges_by_metadata() -> None:
    """Verify edge metadata filtering."""
    graph: Graph[str, object] = Graph()
    graph.add_node(value="A", node_id="a")
    graph.add_node(value="B", node_id="b")
    graph.add_node(value="C", node_id="c")
    graph.add_edge(
        node_id_start="a",
        node_id_end="b",
        edge_id="ab",
        metadata=Metadata(tags={"supports"}, layers={"knowledge"}),
    )
    graph.add_edge(
        node_id_start="a",
        node_id_end="c",
        edge_id="ac",
        metadata=Metadata(tags={"contradicts"}, layers={"knowledge"}),
    )

    edges = graph.filter_edges_by_metadata(
        tags=["supports"],
        layers=["knowledge"],
    )

    assert _edge_ids(edges) == {"ab"}


def test_filter_edges_by_metadata_with_no_criteria_returns_all_edges(
    graph_with_edges: Graph[str, str],
) -> None:
    """Verify empty edge metadata criteria return all edges."""
    edges = graph_with_edges.filter_edges_by_metadata()

    assert _edge_ids(edges) == {"ab", "cb", "ac"}


@pytest.mark.parametrize("node_id", ["", "   "])
def test_node_rejects_empty_or_blank_identifier(node_id: str) -> None:
    """Verify that a node rejects empty and blank identifiers."""
    with pytest.raises(NodeException):
        Node(value="content", node_id=node_id)
