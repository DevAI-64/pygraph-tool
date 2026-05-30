# pygraph-tool

`pygraph-tool` is a lightweight Python library to create and manipulate graphs.

It provides a simple object-oriented API for working with nodes and edges. Nodes and edges have stable identifiers, can store user-defined values, and can be annotated with metadata for filtering, categorization, layering, or application-specific usage.

## Features

* Directed and bidirectional edges
* Automatic UUID-based identifiers when no id is provided
* User-defined values on nodes and edges
* Mutable node and edge values
* Optional metadata on nodes and edges
* Fast lookup by node and edge identifiers
* Successor and predecessor traversal
* Incoming, outgoing, and incident edge retrieval
* Generic filtering with predicates
* Metadata-based filtering

## Installation

Once published on PyPI:

```bash
pip install pygraph-tool
```

With `uv`:

```bash
uv add pygraph-tool
```

## Getting started

### Import modules

```python
from pygraph_tool import Graph
```

You can also import the main public classes:

```python
from pygraph_tool import Edge, Metadata, Node
```

And the exceptions:

```python
from pygraph_tool import EdgeException, GraphException, NodeException
```

## Create a graph

A new graph starts empty.

```python
graph = Graph()
```

## Add nodes

A node stores a user-defined value. The value can be any Python object.

```python
graph.add_node(value="I'm n1", node_id="n1")
graph.add_node(value="I'm n2", node_id="n2")
graph.add_node(value="I'm n3", node_id="n3")
```

If no `node_id` is provided, a UUID-based identifier is generated automatically:

```python
node = graph.add_node(value="Generated id node")

print(node.node_id)
```

The created node is returned by `add_node()`:

```python
node = graph.add_node(value={"name": "Python"}, node_id="python")

print(node.node_id)
print(node.value)
```

If a node with the same identifier already exists, a `GraphException` is raised:

```python
try:
    graph.add_node(value="I'm n1 again", node_id="n1")
except GraphException as error:
    print(error)
```

## Add metadata to nodes

Metadata can be used for tags, categories, layers, flags, or custom properties.

```python
metadata = Metadata(
    tags={"python", "graph"},
    categories={"concept"},
    layers={"knowledge_base"},
    flags={"visible"},
    properties={"priority": 1},
)

graph.add_node(
    value="Python graph concept",
    node_id="python-graph",
    metadata=metadata,
)
```

## Add unidirectional edges

A unidirectional edge connects a start node to an end node.

```python
graph.add_unidirectional_edge(
    node_id_start="n1",
    node_id_end="n2",
    edge_id="e1",
    weight=1.5,
)

graph.add_unidirectional_edge(
    node_id_start="n3",
    node_id_end="n2",
    edge_id="e2",
)

graph.add_unidirectional_edge(
    node_id_start="n1",
    node_id_end="n3",
    edge_id="e3",
)
```

This creates:

```text
n1 -> n2
n3 -> n2
n1 -> n3
```

If no `edge_id` is provided, a UUID-based identifier is generated automatically:

```python
edge = graph.add_unidirectional_edge(
    node_id_start="n1",
    node_id_end="n2",
)

print(edge.edge_id)
```

If an edge with the same identifier already exists, a `GraphException` is raised:

```python
try:
    graph.add_unidirectional_edge(
        node_id_start="n2",
        node_id_end="n3",
        edge_id="e1",
    )
except GraphException as error:
    print(error)
```

## Add bidirectional edges

A bidirectional edge connects two nodes in both directions.

```python
graph.add_bidirectional_edge(
    node_id_start="n2",
    node_id_end="n3",
    edge_id="e4",
)
```

This creates a logical bidirectional relationship:

```text
n2 <-> n3
```

A bidirectional edge is considered both incoming and outgoing for each of its connected nodes.

## Add values to edges

Edges can also store user-defined values.

This is useful when an edge represents a meaningful relationship, such as a dependency, a semantic link, a knowledge relation, or a similarity score.

```python
edge = graph.add_unidirectional_edge(
    node_id_start="n1",
    node_id_end="n2",
    edge_id="relation-1",
    value={
        "type": "supports",
        "confidence": 0.85,
    },
)

print(edge.value)
```

Edge values can be updated without removing the edge:

```python
edge.value = {
    "type": "supports",
    "confidence": 0.95,
}
```

## Add metadata to edges

```python
edge_metadata = Metadata(
    tags={"semantic", "verified"},
    categories={"relation"},
    layers={"knowledge_base"},
)

graph.add_unidirectional_edge(
    node_id_start="n1",
    node_id_end="n2",
    edge_id="semantic-link",
    value="supports",
    metadata=edge_metadata,
)
```

## Access nodes and edges

```python
node = graph.get_node("n1")
edge = graph.get_edge("e1")

print(node.value)
print(edge.weight)
```

You can check whether a node or edge exists:

```python
print(graph.is_node("n1"))
print(graph.is_edge("e1"))
```

## Traverse the graph

### Successors

Successors are nodes reachable from a given node.

```python
successors = graph.get_successors("n1")

for node in successors:
    print(node.node_id)
```

### Predecessors

Predecessors are nodes that point to a given node.

```python
predecessors = graph.get_predecessors("n2")

for node in predecessors:
    print(node.node_id)
```

For bidirectional edges, the opposite endpoint is considered both a successor and a predecessor.

## Retrieve connected edges

### Outgoing edges

```python
outgoing_edges = graph.get_outgoing_edges("n1")

for edge in outgoing_edges:
    print(edge.edge_id)
```

### Incoming edges

```python
incoming_edges = graph.get_incoming_edges("n2")

for edge in incoming_edges:
    print(edge.edge_id)
```

### Incident edges

Incident edges are all edges connected to a node, regardless of direction.

```python
incident_edges = graph.get_incident_edges("n2")

for edge in incident_edges:
    print(edge.edge_id)
```

## Filter nodes and edges

### Filter with predicates

You can filter nodes with any custom predicate:

```python
nodes = graph.filter_nodes(
    lambda node: node.node_id.startswith("n")
)
```

You can also filter edges:

```python
edges = graph.filter_edges(
    lambda edge: edge.weight > 1.0
)
```

### Filter by metadata

You can filter nodes by tags, categories, layers, and flags:

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["python"],
    layers=["knowledge_base"],
)
```

By default, all expected values within each criterion must be present.

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["python", "graph"],
    match_all=True,
)
```

Use `match_all=False` to require at least one value within each criterion:

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["python", "java"],
    match_all=False,
)
```

Different criteria are always combined with `AND`.

For example:

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["python", "java"],
    layers=["knowledge_base"],
    match_all=False,
)
```

This means:

```text
(tags contains "python" OR "java")
AND
(layers contains "knowledge_base")
```

Edges can be filtered the same way:

```python
edges = graph.filter_edges_by_metadata(
    tags=["semantic"],
    categories=["relation"],
)
```

## Remove edges

```python
removed_edge = graph.remove_edge("e3")

print(removed_edge.edge_id)
```

If the edge does not exist, a `GraphException` is raised.

```python
try:
    graph.remove_edge("unknown-edge")
except GraphException as error:
    print(error)
```

## Remove nodes

Removing a node also removes all edges connected to it.

```python
removed_node = graph.remove_node("n2")

print(removed_node.node_id)
```

If the node does not exist, a `GraphException` is raised.

```python
try:
    graph.remove_node("unknown-node")
except GraphException as error:
    print(error)
```

## Display a graph

Here is a simple display helper:

```python
def display_graph(graph: Graph) -> None:
    """Display a simple text representation of a graph."""
    print("Nodes:")
    for node in graph.nodes:
        print(f"- {node.node_id}: {node.value}")

    print("Edges:")
    for edge in graph.edges:
        arrow = "<->" if edge.bidirectional else "->"
        print(
            f"- {edge.node_start.node_id} "
            f"{arrow} "
            f"{edge.node_end.node_id} "
            f"({edge.edge_id}, weight={edge.weight}, value={edge.value})"
        )


display_graph(graph)
```

## Error handling

`pygraph-tool` exposes dedicated exceptions:

```python
from pygraph_tool import EdgeException, GraphException, NodeException
```

Typical cases:

* `NodeException`: invalid node creation
* `EdgeException`: invalid edge creation
* `GraphException`: invalid graph operation, such as duplicate identifiers or missing nodes/edges

Example:

```python
try:
    graph.get_node("missing-node")
except GraphException as error:
    print(error)
```

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run tests:

```bash
uv run pytest
```

Run tests with coverage:

```bash
uv run coverage run -m pytest
uv run coverage report
```

Run linting and formatting:

```bash
uv run ruff check .
uv run ruff format .
```

Run type checking:

```bash
uv run mypy pygraph_tool
```

Build the package:

```bash
uv build --no-sources
```

## Author

Created and maintained by David BEL AICH.

For questions or suggestions, please contact: [belaich.david@outlook.fr](mailto:belaich.david@outlook.fr).
