import pytest

from pygraph_tool.graph import Graph
from pygraph_tool.graph_exceptions import (
    EdgeException, GraphException, NodeException
)
from pygraph_tool.node import Node
from pygraph_tool.edge import Edge


@pytest.fixture
def graph() -> Graph:
    return Graph()


@pytest.fixture
def graph_with_nodes_and_edges() -> Graph:
    graph: Graph = Graph()
    graph.add_node("content", "node_1")
    graph.add_node("content", "node_2")
    graph.add_node("content", "node_3")
    graph.add_unidirectional_edge("node_1", "node_2", "edge_1")
    graph.add_unidirectional_edge("node_1", "node_3", "edge_3")
    graph.add_unidirectional_edge("node_2", "node_3", "edge_2")
    return graph


class TestGraphIsNode:
    def test_is_node(self, graph: Graph):
        node_id: str = "n1"
        graph.add_node(node_content="content", node_id=node_id)
        assert graph.is_node(node_id=node_id)

    def test_is_not_node(self, graph: Graph):
        assert not graph.is_node(node_id="n1")


class TestGraphIsEdge:
    def test_is_edge(self, graph_with_nodes_and_edges: Graph):
        assert graph_with_nodes_and_edges.is_edge(edge_id="edge_1")

    def test_is_not_edge(self, graph: Graph):
        assert not graph.is_edge(edge_id="e1")


class TestGraphAddNode:
    def test_add_node_without_content(self, graph: Graph):
        with pytest.raises(NodeException):
            graph.add_node(None, "node_id")

    def test_add_node_without_node_id(self, graph: Graph):
        with pytest.raises(NodeException):
            graph.add_node("content", "")

    def test_add_node_existing(self, graph_with_nodes_and_edges: Graph):
        with pytest.raises(GraphException):
            graph_with_nodes_and_edges.add_node("toto", "node_1")

    def test_add_node(self, graph_with_nodes_and_edges: Graph):
        assert graph_with_nodes_and_edges.is_node("node_1")


class TestGraphAddUnidirectionalEdge:
    def test_add_edge_without_node_id_start(self, graph: Graph):
        with pytest.raises(EdgeException):
            graph.add_unidirectional_edge("", "node_id_end", "edge_id")

    def test_add_edge_without_node_id_end(self, graph: Graph):
        with pytest.raises(EdgeException):
            graph.add_unidirectional_edge("node_id_start", "", "edge_id")

    def test_add_edge_without_id(self, graph: Graph):
        with pytest.raises(EdgeException):
            graph.add_unidirectional_edge("node_id_start", "node_id_end", "")

    def test_add_edge_existing(self, graph_with_nodes_and_edges: Graph):
        with pytest.raises(GraphException):
            graph_with_nodes_and_edges.add_unidirectional_edge(
                "node_1", "node_2", "edge_1"
            )

    def test_add_edge_without_node_exist(self, graph: Graph):
        graph.add_node("content", "node_1")
        with pytest.raises(GraphException):
            graph.add_unidirectional_edge("node_1", "node_2", "edge_1")

    def test_add_edge(self, graph_with_nodes_and_edges: Graph):
        assert graph_with_nodes_and_edges.is_edge("edge_1")


class TestGraphGetNode:
    def test_get_node_dont_exist(self, graph: Graph):
        with pytest.raises(GraphException):
            graph.get_node("toto")

    def test_get_node(self, graph_with_nodes_and_edges: Graph):
        assert isinstance(
            graph_with_nodes_and_edges.get_node("node_1"), Node
        )


class TestGraphGetEdge:
    def test_get_edge_dont_exist(self, graph: Graph):
        with pytest.raises(GraphException):
            graph.get_edge("toto")

    def test_get_edge(self, graph_with_nodes_and_edges: Graph):
        assert isinstance(
            graph_with_nodes_and_edges.get_edge("edge_1"), Edge
        )


class TestGraphRemoveEdge:
    def test_remove_edge_dont_exist(self, graph: Graph):
        with pytest.raises(GraphException):
            graph.remove_edge("toto")

    def test_remove_edge(self, graph_with_nodes_and_edges: Graph):
        graph_with_nodes_and_edges.remove_edge("edge_1")
        assert not graph_with_nodes_and_edges.is_edge("edge_1")


class TestGraphRemoveNode:
    def test_remove_node_dont_exist(self, graph: Graph):
        with pytest.raises(GraphException):
            graph.remove_node("toto")

    def test_remove_node(self, graph_with_nodes_and_edges: Graph):
        graph_with_nodes_and_edges.remove_node("node_1")
        assert (
            not graph_with_nodes_and_edges.is_edge("edge_1") and
            not graph_with_nodes_and_edges.is_node("node_1") and
            graph_with_nodes_and_edges.is_node("node_2")
        )


class TestGraphGetPredecessors:
    def test_get_predecessors_node_dont_exist(self, graph: Graph):
        assert graph.get_predecessors("toto") == []

    def test_get_predecessors(self, graph_with_nodes_and_edges: Graph):
        assert (
            [
                node.node_id
                for node in graph_with_nodes_and_edges.get_predecessors(
                    "node_3"
                )
            ] == ["node_1", "node_2"]
        )

    def test_get_predecessors_without_predecessor(
        self, graph_with_nodes_and_edges: Graph
    ):
        assert (
            [
                node.node_id
                for node in graph_with_nodes_and_edges.get_predecessors(
                    "node_1"
                )
            ] == []
        )

    
class TestGraphGetSuccessors:
    def test_get_successors_node_dont_exist(self, graph: Graph):
        assert graph.get_successors("toto") == []

    def test_get_successors(self, graph_with_nodes_and_edges: Graph):
        assert (
            [
                node.node_id
                for node in graph_with_nodes_and_edges.get_successors(
                    "node_1"
                )
            ] == ["node_2", "node_3"]
        )

    def test_get_successors_without_successor(
        self, graph_with_nodes_and_edges: Graph
    ):
        assert (
            [
                node.node_id
                for node in graph_with_nodes_and_edges.get_successors(
                    "node_3"
                )
            ] == []
        )
