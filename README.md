# pygraph-tool

`pygraph-tool` is a lightweight Python library to create and manipulate object-oriented graphs.

It provides a simple and explicit API for working with nodes and edges. Nodes and edges have stable identifiers, can store user-defined Python values, and can be annotated with metadata for filtering, categorization, layering, or application-specific usage.

The library is designed for developers who need a small, readable, in-memory graph toolkit without requiring a graph database server.

## Features

- Directed and bidirectional edges
- Automatic UUID-based identifiers when no id is provided
- User-defined values on nodes and edges
- Mutable node and edge values
- Optional metadata on nodes and edges
- Fast lookup by node and edge identifiers
- Successor and predecessor traversal
- Neighbor retrieval by direction
- Reachability traversal with maximum depth
- Unweighted shortest path search
- Incoming, outgoing, and incident edge retrieval
- Subgraph extraction from selected nodes
- Generic filtering with predicates
- Metadata-based filtering
- Dedicated exceptions for graph, node, and edge errors

## Use cases

`pygraph-tool` can be used for:

- Knowledge graphs
- Dependency graphs
- Workflow graphs
- Concept maps
- Graph-based prototypes
- In-memory graph manipulation
- Educational examples
- AI agent memory experiments
- Object graphs with rich Python values

It is not intended to replace a full graph database such as Neo4j. Instead, it focuses on lightweight local graph manipulation with Python objects.

## Installation

Install from PyPI:

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

Metadata can also be copied safely:

```python
metadata_copy = metadata.copy()
```

This is useful when extracting subgraphs or duplicating graph elements without sharing the same metadata collections.

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

Edges can also have metadata.

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

You can also access all nodes and edges:

```python
for node in graph.nodes:
    print(node.node_id, node.value)

for edge in graph.edges:
    print(edge.edge_id, edge.node_start.node_id, edge.node_end.node_id)
```

## Traverse the graph

### Successors

Successors are nodes reachable from a given node by following outgoing edges.

```python
successors = graph.get_successors("n1")

for node in successors:
    print(node.node_id)
```

For bidirectional edges, the opposite endpoint is considered a successor.

### Predecessors

Predecessors are nodes that point to a given node.

```python
predecessors = graph.get_predecessors("n2")

for node in predecessors:
    print(node.node_id)
```

For bidirectional edges, the opposite endpoint is considered a predecessor.

## Retrieve neighbors

Neighbors are nodes directly connected to a given node.

By default, both incoming and outgoing directions are considered:

```python
neighbors = graph.get_neighbors("n1")

for node in neighbors:
    print(node.node_id)
```

You can restrict the direction:

```python
successors = graph.get_neighbors("n1", direction="outgoing")
predecessors = graph.get_neighbors("n1", direction="incoming")
all_neighbors = graph.get_neighbors("n1", direction="both")
```

Supported direction values are:

```text
outgoing
incoming
both
```

## Retrieve reachable nodes

You can retrieve all nodes reachable from a start node up to a maximum depth.

```python
reachable_nodes = graph.get_reachable_nodes(
    node_id="n1",
    max_depth=2,
    direction="outgoing",
)

for node in reachable_nodes:
    print(node.node_id)
```

You can include the start node in the result:

```python
reachable_nodes = graph.get_reachable_nodes(
    node_id="n1",
    max_depth=2,
    direction="outgoing",
    include_start=True,
)
```

You can also traverse in both directions:

```python
reachable_nodes = graph.get_reachable_nodes(
    node_id="n1",
    max_depth=2,
    direction="both",
)
```

This is useful when extracting a local context around a node.

For example:

```python
context_nodes = graph.get_reachable_nodes(
    node_id="python",
    max_depth=2,
    direction="both",
    include_start=True,
)
```

## Find shortest paths

You can find an unweighted shortest path between two nodes.

```python
path = graph.get_shortest_path(
    node_id_start="n1",
    node_id_end="n3",
)

if path is not None:
    print([node.node_id for node in path])
else:
    print("No path found.")
```

The shortest path search is breadth-first and does not take edge weights into account.

You can also control the traversal direction:

```python
path = graph.get_shortest_path(
    node_id_start="n1",
    node_id_end="n3",
    direction="both",
)
```

If the start and end nodes are the same, the returned path contains only that node:

```python
path = graph.get_shortest_path("n1", "n1")

print([node.node_id for node in path])
```

Output:

```text
['n1']
```

## Retrieve connected edges

### Outgoing edges

Outgoing edges start from the given node.

```python
outgoing_edges = graph.get_outgoing_edges("n1")

for edge in outgoing_edges:
    print(edge.edge_id)
```

For bidirectional edges, an edge connected to the node is considered outgoing even when the node is the edge end.

### Incoming edges

Incoming edges end at the given node.

```python
incoming_edges = graph.get_incoming_edges("n2")

for edge in incoming_edges:
    print(edge.edge_id)
```

For bidirectional edges, an edge connected to the node is considered incoming even when the node is the edge start.

### Incident edges

Incident edges are all edges connected to a node, regardless of direction.

```python
incident_edges = graph.get_incident_edges("n2")

for edge in incident_edges:
    print(edge.edge_id)
```

## Extract subgraphs

You can create a new graph from a selected set of node identifiers.

```python
subgraph = graph.extract_subgraph(["n1", "n2", "n3"])
```

By default, edges are included only when both their start and end nodes are part of the selected nodes.

```python
print([node.node_id for node in subgraph.nodes])
print([edge.edge_id for edge in subgraph.edges])
```

You can extract nodes without edges:

```python
subgraph = graph.extract_subgraph(
    ["n1", "n2", "n3"],
    include_edges=False,
)
```

Subgraph extraction reuses node and edge values by reference, but metadata objects are copied.

This means:

- The selected node values are the same Python objects as in the original graph.
- The selected edge values are the same Python objects as in the original graph.
- Metadata collections are copied to avoid accidental metadata mutation across graphs.

A common pattern is to combine reachability traversal and subgraph extraction:

```python
context_nodes = graph.get_reachable_nodes(
    node_id="n1",
    max_depth=2,
    direction="both",
    include_start=True,
)

context_subgraph = graph.extract_subgraph(
    node.node_id for node in context_nodes
)
```

This is useful for building local graph contexts.

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

Since node and edge values can be any Python object, predicates can inspect custom attributes.

```python
nodes = graph.filter_nodes(
    lambda node: hasattr(node.value, "confidence")
    and node.value.confidence > 0.8
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

Removing an edge updates the graph internal adjacency indexes.

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

Removing a node updates the graph internal adjacency indexes and removes all incident edges.

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

Example output:

```text
Nodes:
- n1: I'm n1
- n2: I'm n2
- n3: I'm n3

Edges:
- n1 -> n2 (e1, weight=1.5, value=None)
- n3 -> n2 (e2, weight=1.0, value=None)
- n1 -> n3 (e3, weight=1.0, value=None)
```

## Example: knowledge graph

Because nodes and edges can store Python values, `pygraph-tool` can be used to build simple knowledge graphs.

```python
from dataclasses import dataclass

from pygraph_tool import Graph, Metadata


@dataclass
class Concept:
    name: str
    definition: str
    confidence: float


@dataclass
class Relation:
    relation_type: str
    confidence: float


graph: Graph[Concept, Relation] = Graph()

graph.add_node(
    node_id="concept:tree",
    value=Concept(
        name="tree",
        definition="A perennial plant with a trunk and branches.",
        confidence=0.95,
    ),
    metadata=Metadata(tags={"biology"}, categories={"concept"}),
)

graph.add_node(
    node_id="concept:leaf",
    value=Concept(
        name="leaf",
        definition="A plant organ often involved in photosynthesis.",
        confidence=0.9,
    ),
    metadata=Metadata(tags={"biology"}, categories={"concept"}),
)

graph.add_unidirectional_edge(
    node_id_start="concept:tree",
    node_id_end="concept:leaf",
    edge_id="tree-has-leaf",
    value=Relation(
        relation_type="HAS_PART",
        confidence=0.92,
    ),
    metadata=Metadata(tags={"semantic"}, categories={"relation"}),
)
```

You can then extract a local context around a concept:

```python
context_nodes = graph.get_reachable_nodes(
    node_id="concept:tree",
    max_depth=2,
    direction="both",
    include_start=True,
)

context_graph = graph.extract_subgraph(
    node.node_id for node in context_nodes
)
```

## Error handling

`pygraph-tool` exposes dedicated exceptions:

```python
from pygraph_tool import EdgeException, GraphException, NodeException
```

Typical cases:

- `NodeException`: invalid node creation
- `EdgeException`: invalid edge creation
- `GraphException`: invalid graph operation, such as duplicate identifiers or missing nodes/edges

Example:

```python
try:
    graph.get_node("missing-node")
except GraphException as error:
    print(error)
```

## API overview

Main classes:

```python
from pygraph_tool import Edge, Graph, Metadata, Node
```

Main exceptions:

```python
from pygraph_tool import EdgeException, GraphException, NodeException
```

Common graph methods:

```python
graph.add_node(...)
graph.add_unidirectional_edge(...)
graph.add_bidirectional_edge(...)

graph.get_node(...)
graph.get_edge(...)

graph.is_node(...)
graph.is_edge(...)

graph.get_successors(...)
graph.get_predecessors(...)
graph.get_neighbors(...)
graph.get_reachable_nodes(...)
graph.get_shortest_path(...)

graph.get_outgoing_edges(...)
graph.get_incoming_edges(...)
graph.get_incident_edges(...)

graph.extract_subgraph(...)

graph.filter_nodes(...)
graph.filter_edges(...)
graph.filter_nodes_by_metadata(...)
graph.filter_edges_by_metadata(...)

graph.remove_edge(...)
graph.remove_node(...)
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

Run linting:

```bash
uv run ruff check .
```

Run formatting:

```bash
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

## Release checklist

Before publishing a new version:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy pygraph_tool
uv run coverage run -m pytest
uv run coverage report
uv build --no-sources
```

Then update:

- `pyproject.toml`
- `CHANGELOG.md`
- `README.md`

Create a Git tag:

```bash
git tag v1.1.0
git push origin v1.1.0
```

Publish to PyPI:

```bash
uv publish
```

## Versioning

`pygraph-tool` follows semantic versioning.

Given a version number `MAJOR.MINOR.PATCH`:

- `MAJOR` changes may introduce breaking changes.
- `MINOR` changes add functionality in a backward-compatible way.
- `PATCH` changes fix bugs in a backward-compatible way.

## Roadmap

Potential future improvements:

- Fluent query API
- JSON serialization
- SQLite storage backend
- Public indexing API
- Weighted shortest path search
- Mermaid export
- Graph visualization helpers
- Optional Neo4j adapter
- AI memory-oriented extension package

## Author

Created and maintained by David BEL AICH.

For questions or suggestions, please contact: [belaich.david@outlook.fr](mailto:belaich.david@outlook.fr).