# Usage guide

This guide shows the main features of `pygraph-tool`.

`pygraph-tool` is designed for local, in-memory graph manipulation with Python objects. It can be used for finite state machines, dependency graphs, workflow graphs, object relationship graphs, graph-based simulations, educational examples, or any project that needs a simple graph structure in Python.

## Import modules

`pygraph-tool` exposes only a few classes. You only import these:

```python
from pygraph_tool import Edge, Graph, Metadata, Node
```

And the exceptions:

```python
from pygraph_tool import (
    PyGraphToolException,
    GraphException,
    NodeException,
    EdgeException,
    SerializationException,
)
```

The fluent query helpers are used through `graph.query()` (see the
[chained queries guide](query.md)). They return internal objects that you never
import or construct yourself, which keeps the library simple.

## Create a graph

A new graph starts empty.

```python
graph = Graph()
```

You can optionally type your graph values:

```python
graph: Graph[str, str] = Graph()
```

The first type parameter represents node values. The second type parameter represents edge values.

## Add nodes

A node stores a user-defined value. The value can be any Python object.

```python
graph.add_node(value="Idle", node_id="idle")
graph.add_node(value="Running", node_id="running")
graph.add_node(value="Finished", node_id="finished")
```

If no `node_id` is provided, a UUID-based identifier is generated automatically:

```python
node = graph.add_node(value="Generated id node")

print(node.node_id)
```

The created node is returned by `add_node()`:

```python
node = graph.add_node(value={"name": "Task A"}, node_id="task-a")

print(node.node_id)
print(node.value)
```

If a node with the same identifier already exists, a `GraphException` is raised:

```python
try:
    graph.add_node(value="Duplicate idle state", node_id="idle")
except GraphException as error:
    print(error)
```

## Add metadata to nodes

Metadata can be used for tags, categories, layers, flags, or custom properties.

```python
metadata = Metadata(
    tags={"initial"},
    categories={"state"},
    layers={"runtime"},
    flags={"active"},
    properties={"priority": 1},
)

graph.add_node(
    value="Idle",
    node_id="idle",
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
    node_id_start="idle",
    node_id_end="running",
    edge_id="start",
    value="START",
    weight=1.0,
)

graph.add_unidirectional_edge(
    node_id_start="running",
    node_id_end="finished",
    edge_id="complete",
    value="COMPLETE",
)

graph.add_unidirectional_edge(
    node_id_start="finished",
    node_id_end="idle",
    edge_id="reset",
    value="RESET",
)
```

This creates:

```text
idle -> running
running -> finished
finished -> idle
```

If no `edge_id` is provided, a UUID-based identifier is generated automatically:

```python
edge = graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
)

print(edge.edge_id)
```

If an edge with the same identifier already exists, a `GraphException` is raised:

```python
try:
    graph.add_unidirectional_edge(
        node_id_start="idle",
        node_id_end="running",
        edge_id="start",
    )
except GraphException as error:
    print(error)
```

## Add bidirectional edges

A bidirectional edge connects two nodes in both directions.

```python
graph.add_bidirectional_edge(
    node_id_start="task-a",
    node_id_end="task-b",
    edge_id="related-tasks",
)
```

This creates a logical bidirectional relationship:

```text
task-a <-> task-b
```

A bidirectional edge is considered both incoming and outgoing for each of its connected nodes.

## Add values to edges

Edges can store user-defined values.

This is useful when an edge represents a meaningful relationship, such as a transition, a dependency, a workflow step, or a weighted connection.

```python
edge = graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
    edge_id="start-transition",
    value={
        "event": "START",
        "description": "Start the process",
    },
)

print(edge.value)
```

Edge values can be updated without removing the edge:

```python
edge.value = {
    "event": "START",
    "description": "Start the process immediately",
}
```

## Add metadata to edges

Edges can also have metadata.

```python
edge_metadata = Metadata(
    tags={"transition", "validated"},
    categories={"workflow"},
    layers={"runtime"},
)

graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
    edge_id="validated-start",
    value="START",
    metadata=edge_metadata,
)
```

## Access nodes and edges

```python
node = graph.get_node("idle")
edge = graph.get_edge("start")

print(node.value)
print(edge.weight)
```

You can check whether a node or edge exists:

```python
print(graph.is_node("idle"))
print(graph.is_edge("start"))
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
successors = graph.get_successors("idle")

for node in successors:
    print(node.node_id)
```

For bidirectional edges, the opposite endpoint is considered a successor.

### Predecessors

Predecessors are nodes that point to a given node.

```python
predecessors = graph.get_predecessors("running")

for node in predecessors:
    print(node.node_id)
```

For bidirectional edges, the opposite endpoint is considered a predecessor.

## Retrieve neighbors

Neighbors are nodes directly connected to a given node.

By default, both incoming and outgoing directions are considered:

```python
neighbors = graph.get_neighbors("running")

for node in neighbors:
    print(node.node_id)
```

You can restrict the direction:

```python
successors = graph.get_neighbors("running", direction="outgoing")
predecessors = graph.get_neighbors("running", direction="incoming")
all_neighbors = graph.get_neighbors("running", direction="both")
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
    node_id="idle",
    max_depth=2,
    direction="outgoing",
)

for node in reachable_nodes:
    print(node.node_id)
```

You can include the start node in the result:

```python
reachable_nodes = graph.get_reachable_nodes(
    node_id="idle",
    max_depth=2,
    direction="outgoing",
    include_start=True,
)
```

You can also traverse in both directions:

```python
reachable_nodes = graph.get_reachable_nodes(
    node_id="running",
    max_depth=2,
    direction="both",
)
```

This is useful when extracting a local context around a node.

## Find shortest paths

You can find an unweighted shortest path between two nodes.

```python
path = graph.get_shortest_path(
    node_id_start="idle",
    node_id_end="finished",
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
    node_id_start="finished",
    node_id_end="idle",
    direction="both",
)
```

If the start and end nodes are the same, the returned path contains only that node:

```python
path = graph.get_shortest_path("idle", "idle")

if path is not None:
    print([node.node_id for node in path])
```

Output:

```text
['idle']
```

## Retrieve connected edges

### Outgoing edges

Outgoing edges start from the given node.

```python
outgoing_edges = graph.get_outgoing_edges("idle")

for edge in outgoing_edges:
    print(edge.edge_id)
```

For bidirectional edges, an edge connected to the node is considered outgoing even when the node is the edge end.

### Incoming edges

Incoming edges end at the given node.

```python
incoming_edges = graph.get_incoming_edges("running")

for edge in incoming_edges:
    print(edge.edge_id)
```

For bidirectional edges, an edge connected to the node is considered incoming even when the node is the edge start.

### Incident edges

Incident edges are all edges connected to a node, regardless of direction.

```python
incident_edges = graph.get_incident_edges("running")

for edge in incident_edges:
    print(edge.edge_id)
```

## Extract subgraphs

You can create a new graph from a selected set of node identifiers.

```python
subgraph = graph.extract_subgraph(["idle", "running"])
```

By default, edges are included only when both their start and end nodes are part of the selected nodes.

```python
print([node.node_id for node in subgraph.nodes])
print([edge.edge_id for edge in subgraph.edges])
```

You can extract nodes without edges:

```python
subgraph = graph.extract_subgraph(
    ["idle", "running", "finished"],
    include_edges=False,
)
```

Subgraph extraction reuses node and edge values by reference, but metadata objects are copied.

This means:

* The selected node values are the same Python objects as in the original graph.
* The selected edge values are the same Python objects as in the original graph.
* Metadata collections are copied to avoid accidental metadata mutation across graphs.

A common pattern is to combine reachability traversal and subgraph extraction:

```python
context_nodes = graph.get_reachable_nodes(
    node_id="idle",
    max_depth=2,
    direction="outgoing",
    include_start=True,
)

context_subgraph = graph.extract_subgraph(
    node.node_id for node in context_nodes
)
```

## Filter nodes and edges

The direct filtering methods remain available for simple use cases or when you do not need chained operations.

### Filter with predicates

You can filter nodes with any custom predicate:

```python
nodes = graph.filter_nodes(
    lambda node: node.node_id.startswith("task-")
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
from dataclasses import dataclass


@dataclass
class Task:
    name: str
    priority: int


task_graph: Graph[Task, str] = Graph()

task_graph.add_node(
    node_id="task-a",
    value=Task(name="Task A", priority=1),
)

task_graph.add_node(
    node_id="task-b",
    value=Task(name="Task B", priority=3),
)

high_priority_tasks = task_graph.filter_nodes(
    lambda node: node.value.priority > 1
)
```

### Filter by metadata

You can filter nodes by tags, categories, layers, and flags:

```python
nodes = graph.filter_nodes_by_metadata(
    categories=["state"],
    layers=["runtime"],
)
```

By default, all expected values within each criterion must be present.

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["initial", "visible"],
    match_all=True,
)
```

Use `match_all=False` to require at least one value within each criterion:

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["initial", "final"],
    match_all=False,
)
```

Different criteria are always combined with `AND`.

For example:

```python
nodes = graph.filter_nodes_by_metadata(
    tags=["initial", "final"],
    categories=["state"],
    match_all=False,
)
```

This means:

```text
(tags contains "initial" OR "final")
AND
(categories contains "state")
```

Edges can be filtered the same way:

```python
edges = graph.filter_edges_by_metadata(
    tags=["transition"],
    categories=["workflow"],
)
```

## Chained queries

`pygraph-tool` provides chainable query helpers to make common graph operations more readable.

### Query nodes

```python
states = (
    graph.query()
    .nodes()
    .with_category("state")
    .to_list()
)
```

You can chain multiple predicates:

```python
active_states = (
    graph.query()
    .nodes()
    .where(lambda node: node.metadata.has_category("state"))
    .where(lambda node: node.metadata.has_flag("active"))
    .to_list()
)
```

### Query edges

```python
transitions = (
    graph.query()
    .edges()
    .with_category("workflow")
    .to_list()
)
```

You can also filter edges with predicates:

```python
important_edges = (
    graph.query()
    .edges()
    .where(lambda edge: edge.weight > 1.0)
    .to_list()
)
```

### Start from a node

You can start from one node and continue with traversal-oriented methods.

```python
start_node = graph.query().from_node("idle").node()
```

Retrieve neighbors:

```python
neighbors = (
    graph.query()
    .from_node("running")
    .neighbors(direction="both")
    .to_list()
)
```

Traverse reachable nodes:

```python
reachable_states = (
    graph.query()
    .from_node("idle")
    .traverse(
        max_depth=2,
        direction="outgoing",
        include_start=True,
    )
    .to_list()
)
```

Find an unweighted shortest path:

```python
path = (
    graph.query()
    .from_node("idle")
    .shortest_path_to("finished")
    .to_list()
)
```

If no path exists, the result is empty.

### Convert query results to a subgraph

Node query results can be converted to subgraphs:

```python
state_subgraph = (
    graph.query()
    .from_node("idle")
    .traverse(max_depth=2, direction="outgoing", include_start=True)
    .to_subgraph()
)
```

You can also exclude edges:

```python
nodes_only_subgraph = (
    graph.query()
    .nodes()
    .with_category("state")
    .to_subgraph(include_edges=False)
)
```

## Serialize and import/export graphs

A graph can be converted to a standard Python dictionary, to JSON, or to a JSON
file, and rebuilt from any of these.

```python
data = graph.to_dict()
restored = Graph.from_dict(data)

text = graph.to_json(indent=2)
restored = Graph.from_json(text)

graph.save_json("graph.json")
restored = Graph.load_json("graph.json")
```

Identifiers, values, weights, directions, and metadata are preserved across a
round trip. Values that are not JSON-compatible can be handled with optional
conversion hooks.

See the [serialization guide](serialization.md) for the format, the hooks, and
the error handling details.

## Remove edges

```python
removed_edge = graph.remove_edge("reset")

print(removed_edge.edge_id)
```

If the edge does not exist, a `GraphException` is raised.

Removing an edge updates the graph internal adjacency indexes.

## Remove nodes

Removing a node also removes all edges connected to it.

```python
removed_node = graph.remove_node("finished")

print(removed_node.node_id)
```

If the node does not exist, a `GraphException` is raised.

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

## Example: finite state machine

Because nodes and edges can store Python values, `pygraph-tool` can be used to model simple finite state machines.

```python
from dataclasses import dataclass

from pygraph_tool import Graph, Metadata


@dataclass
class State:
    name: str
    is_final: bool = False


@dataclass
class Transition:
    event: str


graph: Graph[State, Transition] = Graph()

graph.add_node(
    node_id="idle",
    value=State(name="Idle"),
    metadata=Metadata(categories={"state"}, flags={"initial"}),
)

graph.add_node(
    node_id="running",
    value=State(name="Running"),
    metadata=Metadata(categories={"state"}),
)

graph.add_node(
    node_id="finished",
    value=State(name="Finished", is_final=True),
    metadata=Metadata(categories={"state"}, flags={"final"}),
)

graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
    edge_id="start",
    value=Transition(event="START"),
    metadata=Metadata(categories={"transition"}),
)

graph.add_unidirectional_edge(
    node_id_start="running",
    node_id_end="finished",
    edge_id="complete",
    value=Transition(event="COMPLETE"),
    metadata=Metadata(categories={"transition"}),
)
```

You can then retrieve reachable states:

```python
reachable_states = graph.get_reachable_nodes(
    node_id="idle",
    max_depth=2,
    direction="outgoing",
    include_start=True,
)

print([state.node_id for state in reachable_states])
```

Or extract a local subgraph:

```python
state_graph = (
    graph.query()
    .from_node("idle")
    .traverse(max_depth=2, direction="outgoing", include_start=True)
    .to_subgraph()
)
```

## Error handling

`pygraph-tool` exposes dedicated exceptions:

```python
from pygraph_tool import (
    EdgeException,
    GraphException,
    NodeException,
    SerializationException,
)
```

Typical cases:

* `NodeException`: invalid node creation
* `EdgeException`: invalid edge creation
* `GraphException`: invalid graph operation, such as duplicate identifiers or missing nodes/edges
* `SerializationException`: invalid or inconsistent serialized data

Example:

```python
try:
    graph.get_node("missing-node")
except GraphException as error:
    print(error)
```
