# pygraph-tool

pygraph-tool is a module to create and manipulate graphs. Nodes can be all objects who you want and edges are oriented and valued at 1 by default. If you wish one graph not oriented, edges must be declared in one direction and then in the other.

## Getting started

### Import modules
Graph module:
```python
from pygraph_tool.graph import Graph
```
Exceptions module:
```python
from pygraph_tool.exceptions import (
    NodeException,
    EdgeException,
    GraphException
)
```
Others modules (optional):
```python
from pygraph_tool.node import Node
from pygraph_tool.edge import Edge
```

### Create new graph
The new graph is empty (No node and no edge).
```python
graph: Graph = Graph()
```

### Create new nodes in graph
Create new nodes n1, n2 and n3, three nodes of graph.
```python
graph.add_node("I'm n1", "n1")
graph.add_node("I'm n2", "n2")
graph.add_node("I'm n3", "n3")
```
If node already exists(same id), the `GraphException` is raise.
```python
try:
    graph.add_node("I'm n1 again", "n1")
except GraphException as error:
    pass  # or do something...
```
If an argument is `None`, the `NodeException` is raise.

### Create new unidirectional edge in graph
Create new edges e1 such as n1->n2 with weight = 1.5, 
e2 such as n3->n2 with weight by default = 1 and 
e3 such as n1->n3 with weight by default = 1
```python
graph.add_unidirectional_edge("n1", "n2", "e1", 1.5)
graph.add_unidirectional_edge("n3", "n2", "e2")
graph.add_unidirectional_edge("n1", "n3", "e3")
```
If edge already exists (same id), the `GraphException` is raise.
```python
try:
    graph.add_unidirectional_edge("n2", "n3", "e1")
except GraphException as error:
    pass  # or do something...
```
If an argument (except `weight` argument) is `None`, the `EdgeException` is raise.

### Create new bidirectional edge in graph
coming soon...

### Remove node
If node doesn't exist in graph, `GraphException` is raise.
```python
try:
    graph.remove_node("n2")
except GraphException as error:
    pass  # or do something...
```

### Remove edge
If edge doesn't exist in graph, `GraphException` is raise.
```python
try:
    graph.remove_edge("e3")
except GraphException as error:
    pass  # or do something...
```

### Visualize the graph (very simple representation)
Create function for display graph
```python
def displayGraph(graph: Graph) -> None:
    # display the graph's nodes
    for node in graph.nodes:
        print(f"{node.node_id}: {node.node_content}")

    # display the graph's edges
    for edge in graph.edges:
        message: str = (
            f"{edge.node_start.node_id} "
            f"--- {edge.edge_id} = {edge.weight} ---> "
            f"{edge.node_end.node_id}"
        )
        print(message)


# Display graph
displayGraph(graph)
```

## Author
If you have any questions or suggestions, please don't hesitate to contact me : <belaich.david@outlook.fr>.
