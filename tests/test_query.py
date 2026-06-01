"""Tests for fluent graph queries."""

from typing import Any

import pytest

from pygraph_tool import Graph, GraphException, Metadata, Node


def _node_ids(nodes: list[Node[Any]]) -> list[str]:
    return [node.node_id for node in nodes]


def _build_query_graph() -> Graph[str, str]:
    graph: Graph[str, str] = Graph()

    graph.add_node(
        "Python",
        node_id="python",
        metadata=Metadata(
            tags={"python", "language"},
            categories={"concept"},
            layers={"knowledge"},
            flags={"active"},
        ),
    )
    graph.add_node(
        "Graph",
        node_id="graph",
        metadata=Metadata(
            tags={"graph", "data-structure"},
            categories={"concept"},
            layers={"knowledge"},
        ),
    )
    graph.add_node(
        "Archive",
        node_id="archive",
        metadata=Metadata(
            tags={"old"},
            categories={"archive"},
            layers={"archive"},
            flags={"inactive"},
        ),
    )
    graph.add_node(
        "Agent",
        node_id="agent",
        metadata=Metadata(
            tags={"ai"},
            categories={"concept"},
            layers={"runtime"},
            flags={"active"},
        ),
    )

    graph.add_unidirectional_edge(
        "python",
        "graph",
        edge_id="python-graph",
        value="uses",
        weight=0.9,
        metadata=Metadata(
            tags={"semantic"},
            categories={"relation"},
            layers={"knowledge"},
        ),
    )
    graph.add_unidirectional_edge(
        "graph",
        "agent",
        edge_id="graph-agent",
        value="supports",
        weight=0.8,
        metadata=Metadata(
            tags={"semantic", "ai"},
            categories={"relation"},
            layers={"runtime"},
        ),
    )
    graph.add_unidirectional_edge(
        "archive",
        "python",
        edge_id="archive-python",
        value="mentions",
        weight=0.2,
        metadata=Metadata(
            tags={"archive"},
            categories={"relation"},
            layers={"archive"},
        ),
    )

    return graph


def test_graph_query_returns_all_nodes() -> None:
    graph = _build_query_graph()

    nodes = graph.query().nodes().to_list()

    assert _node_ids(nodes) == ["python", "graph", "archive", "agent"]


def test_node_query_filters_with_predicates() -> None:
    graph = _build_query_graph()

    nodes = (
        graph.query().nodes().where(lambda node: node.node_id.startswith("a")).to_list()
    )

    assert _node_ids(nodes) == ["archive", "agent"]


def test_node_query_chains_multiple_filters() -> None:
    graph = _build_query_graph()

    nodes = (
        graph.query()
        .nodes()
        .where(lambda node: node.metadata.has_category("concept"))
        .where(lambda node: node.metadata.has_flag("active"))
        .to_list()
    )

    assert _node_ids(nodes) == ["python", "agent"]


def test_node_query_metadata_helpers() -> None:
    graph = _build_query_graph()

    nodes = graph.query().nodes().with_category("concept").with_flag("active").to_list()

    assert _node_ids(nodes) == ["python", "agent"]


def test_node_query_plural_metadata_helpers_with_match_any() -> None:
    graph = _build_query_graph()

    nodes = graph.query().nodes().with_tags(["python", "ai"], match_all=False).to_list()

    assert _node_ids(nodes) == ["python", "agent"]


def test_node_query_limit_first_count_exists_and_tuple() -> None:
    graph = _build_query_graph()

    query = graph.query().nodes().with_category("concept").limit(2)

    first_node = query.first()

    assert query.count() == 2
    assert query.exists()
    assert first_node is not None
    assert first_node.node_id == "python"
    assert [node.node_id for node in query.to_tuple()] == ["python", "graph"]


def test_node_query_negative_limit_raises_exception() -> None:
    graph = _build_query_graph()

    with pytest.raises(GraphException):
        graph.query().nodes().limit(-1)


def test_node_query_to_subgraph() -> None:
    graph = _build_query_graph()

    subgraph = graph.query().nodes().with_category("concept").to_subgraph()

    assert {node.node_id for node in subgraph.nodes} == {
        "python",
        "graph",
        "agent",
    }
    assert {edge.edge_id for edge in subgraph.edges} == {
        "python-graph",
        "graph-agent",
    }


def test_node_query_to_subgraph_without_edges() -> None:
    graph = _build_query_graph()

    subgraph = (
        graph.query().nodes().with_category("concept").to_subgraph(include_edges=False)
    )

    assert {node.node_id for node in subgraph.nodes} == {
        "python",
        "graph",
        "agent",
    }
    assert subgraph.edges == ()


def test_graph_query_returns_all_edges() -> None:
    graph = _build_query_graph()

    edges = graph.query().edges().to_list()

    assert [edge.edge_id for edge in edges] == [
        "python-graph",
        "graph-agent",
        "archive-python",
    ]


def test_edge_query_filters_with_predicates() -> None:
    graph = _build_query_graph()

    edges = graph.query().edges().where(lambda edge: edge.weight >= 0.8).to_list()

    assert [edge.edge_id for edge in edges] == ["python-graph", "graph-agent"]


def test_edge_query_metadata_helpers() -> None:
    graph = _build_query_graph()

    edges = (
        graph.query().edges().with_tag("semantic").with_category("relation").to_list()
    )

    assert [edge.edge_id for edge in edges] == ["python-graph", "graph-agent"]


def test_edge_query_plural_metadata_helpers_with_match_any() -> None:
    graph = _build_query_graph()

    edges = (
        graph.query()
        .edges()
        .with_layers(["knowledge", "runtime"], match_all=False)
        .to_list()
    )

    assert [edge.edge_id for edge in edges] == ["python-graph", "graph-agent"]


def test_edge_query_limit_first_count_exists_and_tuple() -> None:
    graph = _build_query_graph()

    query = graph.query().edges().with_category("relation").limit(1)

    first_edge = query.first()

    assert query.count() == 1
    assert query.exists()
    assert first_edge is not None
    assert first_edge.edge_id == "python-graph"
    assert [edge.edge_id for edge in query.to_tuple()] == ["python-graph"]


def test_edge_query_negative_limit_raises_exception() -> None:
    graph = _build_query_graph()

    with pytest.raises(GraphException):
        graph.query().edges().limit(-1)


def test_from_node_rejects_unknown_node() -> None:
    graph = _build_query_graph()

    with pytest.raises(GraphException):
        graph.query().from_node("missing")


def test_from_node_returns_start_node() -> None:
    graph = _build_query_graph()

    node = graph.query().from_node("python").node()

    assert node.node_id == "python"


def test_traversal_query_neighbors() -> None:
    graph = _build_query_graph()

    neighbors = graph.query().from_node("graph").neighbors(direction="both").to_list()

    assert _node_ids(neighbors) == ["agent", "python"]


def test_traversal_query_traverse_to_subgraph() -> None:
    graph = _build_query_graph()

    subgraph = (
        graph.query()
        .from_node("python")
        .traverse(max_depth=2, direction="outgoing", include_start=True)
        .to_subgraph()
    )

    assert {node.node_id for node in subgraph.nodes} == {
        "python",
        "graph",
        "agent",
    }
    assert {edge.edge_id for edge in subgraph.edges} == {
        "python-graph",
        "graph-agent",
    }


def test_traversal_query_shortest_path_to() -> None:
    graph = _build_query_graph()

    path = graph.query().from_node("python").shortest_path_to("agent").to_list()

    assert _node_ids(path) == ["python", "graph", "agent"]


def test_traversal_query_shortest_path_to_returns_empty_query_when_no_path() -> None:
    graph = _build_query_graph()

    path = graph.query().from_node("agent").shortest_path_to("archive").to_list()

    assert path == []


def test_traversal_query_edges() -> None:
    graph = _build_query_graph()

    outgoing_edges = graph.query().from_node("graph").outgoing_edges().to_list()
    incoming_edges = graph.query().from_node("graph").incoming_edges().to_list()
    incident_edges = graph.query().from_node("graph").incident_edges().to_list()

    assert [edge.edge_id for edge in outgoing_edges] == ["graph-agent"]
    assert [edge.edge_id for edge in incoming_edges] == ["python-graph"]
    assert {edge.edge_id for edge in incident_edges} == {
        "python-graph",
        "graph-agent",
    }


def test_node_query_singular_metadata_helpers() -> None:
    graph = _build_query_graph()

    tagged_nodes = graph.query().nodes().with_tag("python").to_list()
    layered_nodes = graph.query().nodes().with_layer("knowledge").to_list()

    assert _node_ids(tagged_nodes) == ["python"]
    assert _node_ids(layered_nodes) == ["python", "graph"]


def test_edge_query_singular_metadata_helpers() -> None:
    graph = _build_query_graph()

    categorized_edges = graph.query().edges().with_category("relation").to_list()
    layered_edges = graph.query().edges().with_layer("runtime").to_list()
    flagged_edges = graph.query().edges().with_flag("missing").to_list()

    assert [edge.edge_id for edge in categorized_edges] == [
        "python-graph",
        "graph-agent",
        "archive-python",
    ]
    assert [edge.edge_id for edge in layered_edges] == ["graph-agent"]
    assert flagged_edges == []


def test_empty_node_metadata_filter_returns_all_nodes() -> None:
    graph = _build_query_graph()

    nodes = graph.query().nodes().with_tags([]).to_list()

    assert _node_ids(nodes) == ["python", "graph", "archive", "agent"]


def test_empty_edge_metadata_filter_returns_all_edges() -> None:
    graph = _build_query_graph()

    edges = graph.query().edges().with_tags([]).to_list()

    assert [edge.edge_id for edge in edges] == [
        "python-graph",
        "graph-agent",
        "archive-python",
    ]


def test_empty_node_query_result_helpers() -> None:
    graph = _build_query_graph()

    query = graph.query().nodes().where(lambda node: node.node_id == "missing")

    assert query.first() is None
    assert query.count() == 0
    assert not query.exists()
    assert query.to_list() == []
    assert query.to_tuple() == ()


def test_empty_edge_query_result_helpers() -> None:
    graph = _build_query_graph()

    query = graph.query().edges().where(lambda edge: edge.edge_id == "missing")

    assert query.first() is None
    assert query.count() == 0
    assert not query.exists()
    assert query.to_list() == []
    assert query.to_tuple() == ()
