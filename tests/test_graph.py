"""Additional tests covering constructors, metadata helpers, and edge cases."""

from math import inf, nan
from typing import Any, cast
from uuid import UUID

import pytest

from pygraph_tool import Edge, Graph, GraphException, Metadata, Node, NodeException
from pygraph_tool.exceptions.graph_exceptions import EdgeException


def _node_ids(nodes: list[Node[Any]]) -> list[str]:
    """Return node identifiers in order."""
    return [node.node_id for node in nodes]


def _edge_ids(edges: list[Edge[Any, Any]]) -> set[str]:
    """Return edge identifiers."""
    return {edge.edge_id for edge in edges}


def test_metadata_membership_helpers_return_true_and_false() -> None:
    metadata = Metadata(
        tags={"python"},
        categories={"concept"},
        layers={"knowledge"},
        flags={"visible"},
    )

    assert metadata.has_tag("python")
    assert not metadata.has_tag("java")
    assert metadata.has_category("concept")
    assert not metadata.has_category("relation")
    assert metadata.has_layer("knowledge")
    assert not metadata.has_layer("archive")
    assert metadata.has_flag("visible")
    assert not metadata.has_flag("hidden")


def test_node_rejects_blank_identifier_and_compares_non_node() -> None:
    with pytest.raises(NodeException):
        Node(value="content", node_id="   ")

    node = Node(value="content", node_id="node")

    assert node != object()
    assert hash(node) == hash("node")


def test_edge_rejects_blank_identifier_and_non_finite_weight() -> None:
    node_a = Node(value="A", node_id="a")
    node_b = Node(value="B", node_id="b")

    with pytest.raises(EdgeException):
        Edge(node_start=node_a, node_end=node_b, edge_id="   ")

    for weight in [inf, -inf, nan]:
        with pytest.raises(EdgeException):
            Edge(node_start=node_a, node_end=node_b, weight=weight)


def test_edge_compares_by_identifier_and_hashes_identifier() -> None:
    node_a = Node(value="A", node_id="a")
    node_b = Node(value="B", node_id="b")

    first: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="old",
        edge_id="edge",
    )
    second: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="new",
        edge_id="edge",
    )
    third: Edge[str, str] = Edge(
        node_start=node_a,
        node_end=node_b,
        value="other",
        edge_id="other-edge",
    )

    assert first == second
    assert first != third
    assert first != object()
    assert hash(first) == hash("edge")
    assert len({first, second, third}) == 2


def test_graph_rejects_duplicate_node_and_duplicate_edge() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")

    with pytest.raises(GraphException):
        graph.add_node("A again", node_id="a")

    graph.add_unidirectional_edge("a", "b", edge_id="ab")

    with pytest.raises(GraphException):
        graph.add_unidirectional_edge("a", "b", edge_id="ab")


def test_graph_rejects_unknown_edge_lookup_and_removal() -> None:
    graph: Graph[str, str] = Graph()

    with pytest.raises(GraphException):
        graph.get_edge("missing")

    with pytest.raises(GraphException):
        graph.remove_edge("missing")


def test_graph_rejects_unknown_node_removal_and_traversal() -> None:
    graph: Graph[str, str] = Graph()

    with pytest.raises(GraphException):
        graph.remove_node("missing")

    with pytest.raises(GraphException):
        graph.get_outgoing_edges("missing")

    with pytest.raises(GraphException):
        graph.get_incoming_edges("missing")

    with pytest.raises(GraphException):
        graph.get_incident_edges("missing")


def test_graph_add_edge_rejects_missing_nodes() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")

    with pytest.raises(GraphException):
        graph.add_unidirectional_edge("missing", "a", edge_id="ma")

    with pytest.raises(GraphException):
        graph.add_unidirectional_edge("a", "missing", edge_id="am")


def test_graph_generated_identifiers_are_valid_uuids() -> None:
    graph: Graph[str, str] = Graph()
    node_a = graph.add_node("A")
    node_b = graph.add_node("B")
    edge = graph.add_unidirectional_edge(node_a.node_id, node_b.node_id)

    UUID(node_a.node_id)
    UUID(node_b.node_id)
    UUID(edge.edge_id)


def test_graph_neighbors_and_direction_errors() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")
    graph.add_node("C", node_id="c")
    graph.add_unidirectional_edge("a", "b", edge_id="ab")
    graph.add_unidirectional_edge("c", "a", edge_id="ca")

    assert _node_ids(graph.get_neighbors("a", direction="outgoing")) == ["b"]
    assert _node_ids(graph.get_neighbors("a", direction="incoming")) == ["c"]
    assert set(_node_ids(graph.get_neighbors("a", direction="both"))) == {"b", "c"}

    with pytest.raises(GraphException):
        graph.get_neighbors("a", direction=cast(Any, "sideways"))


def test_graph_reachable_nodes_edge_cases_and_cycles() -> None:
    graph: Graph[str, str] = Graph()
    for node_id in ["a", "b", "c"]:
        graph.add_node(node_id.upper(), node_id=node_id)

    graph.add_unidirectional_edge("a", "b", edge_id="ab")
    graph.add_unidirectional_edge("b", "c", edge_id="bc")
    graph.add_unidirectional_edge("c", "a", edge_id="ca")

    assert graph.get_reachable_nodes("a", max_depth=0) == []
    assert _node_ids(
        graph.get_reachable_nodes("a", max_depth=0, include_start=True)
    ) == ["a"]
    assert _node_ids(graph.get_reachable_nodes("a", max_depth=5)) == ["b", "c"]
    assert _node_ids(
        graph.get_reachable_nodes("c", max_depth=2, direction="incoming")
    ) == [
        "b",
        "a",
    ]

    with pytest.raises(GraphException):
        graph.get_reachable_nodes("a", max_depth=-1)

    with pytest.raises(GraphException):
        graph.get_reachable_nodes("missing")


def test_graph_shortest_path_edge_cases() -> None:
    graph: Graph[str, str] = Graph()
    for node_id in ["a", "b", "c", "d", "x"]:
        graph.add_node(node_id.upper(), node_id=node_id)

    graph.add_unidirectional_edge("a", "b", edge_id="ab")
    graph.add_unidirectional_edge("b", "a", edge_id="ba")
    graph.add_unidirectional_edge("b", "c", edge_id="bc")
    graph.add_unidirectional_edge("c", "d", edge_id="cd")

    same_node_path = graph.get_shortest_path("a", "a")
    assert same_node_path is not None
    assert _node_ids(same_node_path) == ["a"]

    path = graph.get_shortest_path("a", "d")
    assert path is not None
    assert _node_ids(path) == ["a", "b", "c", "d"]

    assert graph.get_shortest_path("a", "x") is None

    with pytest.raises(GraphException):
        graph.get_shortest_path("missing", "a")

    with pytest.raises(GraphException):
        graph.get_shortest_path("a", "missing")


def test_graph_bidirectional_edges_update_indexes_and_traversal() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")
    graph.add_bidirectional_edge("a", "b", edge_id="ab")

    assert _node_ids(graph.get_successors("a")) == ["b"]
    assert _node_ids(graph.get_predecessors("a")) == ["b"]
    assert _node_ids(graph.get_successors("b")) == ["a"]
    assert _node_ids(graph.get_predecessors("b")) == ["a"]
    assert _edge_ids(graph.get_outgoing_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_incoming_edges("a")) == {"ab"}
    assert _edge_ids(graph.get_outgoing_edges("b")) == {"ab"}
    assert _edge_ids(graph.get_incoming_edges("b")) == {"ab"}

    graph.remove_edge("ab")

    assert graph.get_outgoing_edges("a") == []
    assert graph.get_incoming_edges("a") == []
    assert graph.get_outgoing_edges("b") == []
    assert graph.get_incoming_edges("b") == []


def test_graph_remove_node_removes_incident_edges_from_indexes() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")
    graph.add_node("C", node_id="c")
    graph.add_unidirectional_edge("a", "b", edge_id="ab")
    graph.add_unidirectional_edge("b", "c", edge_id="bc")
    graph.add_bidirectional_edge("a", "c", edge_id="ac")

    graph.remove_node("b")

    assert not graph.is_node("b")
    assert not graph.is_edge("ab")
    assert not graph.is_edge("bc")
    assert graph.is_edge("ac")
    assert graph.get_outgoing_edges("a") == [graph.get_edge("ac")]
    assert graph.get_incoming_edges("c") == [graph.get_edge("ac")]


def test_graph_filter_predicates_and_metadata_matching() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node(
        "Python",
        node_id="python",
        metadata=Metadata(
            tags={"python", "oop"}, categories={"concept"}, layers={"knowledge"}
        ),
    )
    graph.add_node(
        "Java",
        node_id="java",
        metadata=Metadata(
            tags={"java", "oop"}, categories={"concept"}, layers={"knowledge"}
        ),
    )
    graph.add_node(
        "Archive",
        node_id="archive",
        metadata=Metadata(tags={"python"}, categories={"concept"}, layers={"archive"}),
    )
    graph.add_unidirectional_edge(
        "python",
        "java",
        edge_id="py-java",
        metadata=Metadata(
            tags={"semantic"}, categories={"relation"}, layers={"knowledge"}
        ),
    )
    graph.add_unidirectional_edge(
        "archive",
        "python",
        edge_id="archive-python",
        metadata=Metadata(
            tags={"archive"}, categories={"relation"}, layers={"archive"}
        ),
    )

    assert _node_ids(graph.filter_nodes(lambda node: node.node_id.startswith("p"))) == [
        "python"
    ]
    assert _edge_ids(
        graph.filter_edges(lambda edge: edge.edge_id.startswith("py"))
    ) == {"py-java"}
    assert _node_ids(
        graph.filter_nodes_by_metadata(
            tags=["python", "java"], layers=["knowledge"], match_all=False
        )
    ) == ["python", "java"]
    assert _node_ids(graph.filter_nodes_by_metadata(tags=[])) == [
        "python",
        "java",
        "archive",
    ]
    assert _edge_ids(
        graph.filter_edges_by_metadata(tags=["semantic"], categories=["relation"])
    ) == {"py-java"}
    assert _edge_ids(graph.filter_edges_by_metadata()) == {"py-java", "archive-python"}


def test_graph_extract_subgraph_edge_cases_and_metadata_copy() -> None:
    graph: Graph[dict[str, str], dict[str, str]] = Graph()
    node_value = {"name": "A"}
    edge_value = {"type": "RELATES_TO"}

    graph.add_node(node_value, node_id="a", metadata=Metadata(tags={"node"}))
    graph.add_node({"name": "B"}, node_id="b")
    graph.add_node({"name": "C"}, node_id="c")
    graph.add_unidirectional_edge(
        "a",
        "b",
        value=edge_value,
        edge_id="ab",
        metadata=Metadata(tags={"edge"}),
    )
    graph.add_unidirectional_edge("b", "c", edge_id="bc")

    subgraph_without_edges = graph.extract_subgraph(["a", "b"], include_edges=False)
    assert {node.node_id for node in subgraph_without_edges.nodes} == {"a", "b"}
    assert subgraph_without_edges.edges == ()

    subgraph = graph.extract_subgraph(["a", "b"])
    assert {node.node_id for node in subgraph.nodes} == {"a", "b"}
    assert _edge_ids(list(subgraph.edges)) == {"ab"}
    assert subgraph.get_node("a").value is node_value
    assert subgraph.get_edge("ab").value is edge_value
    assert subgraph.get_node("a").metadata is not graph.get_node("a").metadata
    assert subgraph.get_edge("ab").metadata is not graph.get_edge("ab").metadata

    subgraph.get_node("a").metadata.tags.add("subgraph")
    subgraph.get_edge("ab").metadata.tags.add("subgraph")

    assert graph.get_node("a").metadata.tags == {"node"}
    assert graph.get_edge("ab").metadata.tags == {"edge"}

    with pytest.raises(GraphException):
        graph.extract_subgraph(["a", "missing"])


def test_node_compares_by_identifier() -> None:
    first = Node(value="first", node_id="node")
    second = Node(value="second", node_id="node")
    third = Node(value="third", node_id="other-node")

    assert first == second
    assert first != third
    assert len({first, second, third}) == 2


def test_get_opposite_node_raises_when_node_is_not_connected_to_edge() -> None:
    graph: Graph[str, str] = Graph()

    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")

    edge = graph.add_unidirectional_edge("a", "b", edge_id="ab")

    with pytest.raises(GraphException):
        graph._get_opposite_node(edge, "missing")


def test_edge_weight_rejects_non_finite_value_after_creation() -> None:
    graph: Graph[str, str] = Graph()
    graph.add_node("A", node_id="a")
    graph.add_node("B", node_id="b")

    edge = graph.add_edge("a", "b")

    with pytest.raises(EdgeException):
        edge.weight = float("nan")


def test_public_library_is_intentionally_limited() -> None:
    import pygraph_tool

    assert set(pygraph_tool.__all__) == {
        "Edge",
        "Graph",
        "Metadata",
        "Node",
        "EdgeException",
        "GraphException",
        "NodeException",
        "PyGraphToolException",
        "SerializationException",
    }
