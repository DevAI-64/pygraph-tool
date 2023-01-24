# pygraph-tool

pygraph-tool is a module to create and manipulate graphs. Nodes can be all objects who you want and edges are oriented and valued at 1 by default. If you wish one graph not oriented, edges must be declared in one direction and then in the other.

## Getting started

```python
# import module
from pygraph_tool.graph import Graph

# Create function for display graph
def displayGraph(graph: Graph) -> None:
    # retrieve the list graph's nodes and edges
    nodes = graph.nodes
    edges = graph.edges

    # display the graph's nodes
    for node in nodes:
        print(f"{node.node_id}: {node.node_content}")

    # display the graph's edges
    for edge in edges:
        message: str = (
            f"{edge.node_start.node_id} "
            f"--- {edge.edge_id} = {edge.weight} ---> "
            f"{edge.node_end.node_id}"
        )
        print(message)

# create a new graph
graph: Graph = Graph

# create n1, n2 and n3, three nodes of graph
graph.addNode("I'm n1", "n1")
graph.addNode("I'm n2", "n2")
graph.addNode("I'm n3", "n3")

"""
create edge e1 such as n1->n2 with weight = 1.5,
edge e2 such as n3->n2 with weight by default = 1
and edge e3 such as n1->n3 with weight by default = 1
"""
graph.addEdge("n1", "n2", "e1", 1.5)
graph.addEdge("n3", "n2", "e2")
graph.addEdge("n1", "n3", "e3")

# Display graph
displayGraph(graph)
print()

# remove the node n2 and all edges binded to node n2
graph.removeNode("n2")

# Display graph
displayGraph(graph)
print()

# remove the edge e3
graph.removeEdge("e3")

# Display graph
displayGraph(graph)
```

## Author

If you have any questions or suggestions, please don't hesitate to contact me : <belaich.david@outlook.fr> .
