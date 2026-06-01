# Chained queries

`pygraph-tool` provides chainable query helpers to make common graph operations more readable.

The entry point is `graph.query()`.

## Query nodes

```python
nodes = (
    graph.query()
    .nodes()
    .where(lambda node: node.node_id.startswith("n"))
    .to_list()
)
```

You can chain multiple predicates:

```python
nodes = (
    graph.query()
    .nodes()
    .where(lambda node: node.metadata.has_category("concept"))
    .where(lambda node: node.metadata.has_flag("active"))
    .to_list()
)
```

Each `where()` adds a condition. Conditions are combined by keeping only elements that match every predicate in the chain.

## Query nodes by metadata

```python
nodes = (
    graph.query()
    .nodes()
    .with_tag("python")
    .with_category("concept")
    .to_list()
)
```

Plural metadata helpers are also available:

```python
nodes = (
    graph.query()
    .nodes()
    .with_tags(["python", "graph"], match_all=False)
    .to_list()
)
```

Available node metadata helpers:

```python
.with_tag(...)
.with_category(...)
.with_layer(...)
.with_flag(...)
.with_tags(...)
.with_categories(...)
.with_layers(...)
.with_flags(...)
```

## Query edges

```python
edges = (
    graph.query()
    .edges()
    .where(lambda edge: edge.weight > 1.0)
    .to_list()
)
```

Edges can also be queried by metadata:

```python
edges = (
    graph.query()
    .edges()
    .with_tag("semantic")
    .with_category("relation")
    .to_list()
)
```

Available edge metadata helpers:

```python
.with_tag(...)
.with_category(...)
.with_layer(...)
.with_flag(...)
.with_tags(...)
.with_categories(...)
.with_layers(...)
.with_flags(...)
```

## Limit and inspect results

Node and edge query results provide simple helper methods.

```python
query = (
    graph.query()
    .nodes()
    .with_category("concept")
    .limit(10)
)

first_node = query.first()
count = query.count()
has_results = query.exists()
nodes_as_list = query.to_list()
nodes_as_tuple = query.to_tuple()
```

`first()` returns `None` when the result is empty.

```python
first_node = (
    graph.query()
    .nodes()
    .where(lambda node: node.node_id == "missing")
    .first()
)

print(first_node)
```

Output:

```text
None
```

## Start from a node

You can start from one node and continue with traversal-oriented methods.

```python
start_node = graph.query().from_node("n1").node()
```

If the node does not exist, a `GraphException` is raised.

## Retrieve neighbors

```python
neighbors = (
    graph.query()
    .from_node("n1")
    .neighbors(direction="both")
    .to_list()
)
```

Supported direction values are:

```text
outgoing
incoming
both
```

## Traverse reachable nodes

```python
reachable_nodes = (
    graph.query()
    .from_node("n1")
    .traverse(
        max_depth=2,
        direction="outgoing",
        include_start=True,
    )
    .to_list()
)
```

This returns a node query, so you can continue chaining node filters:

```python
active_context = (
    graph.query()
    .from_node("n1")
    .traverse(max_depth=2, direction="both", include_start=True)
    .where(lambda node: node.metadata.has_flag("active"))
    .to_list()
)
```

## Find a shortest path

```python
path = (
    graph.query()
    .from_node("n1")
    .shortest_path_to("n5", direction="outgoing")
    .to_list()
)
```

The shortest path is unweighted. Edge weights are ignored.

If no path exists, the result is empty.

## Query connected edges from a node

```python
outgoing_edges = (
    graph.query()
    .from_node("n1")
    .outgoing_edges()
    .to_list()
)

incoming_edges = (
    graph.query()
    .from_node("n1")
    .incoming_edges()
    .to_list()
)

incident_edges = (
    graph.query()
    .from_node("n1")
    .incident_edges()
    .to_list()
)
```

These methods return edge queries, so you can continue filtering edges:

```python
semantic_edges = (
    graph.query()
    .from_node("n1")
    .incident_edges()
    .with_tag("semantic")
    .to_list()
)
```

## Convert query results to a subgraph

Node query results can be converted to subgraphs:

```python
context_subgraph = (
    graph.query()
    .from_node("n1")
    .traverse(max_depth=2, direction="both", include_start=True)
    .to_subgraph()
)
```

You can also exclude edges:

```python
nodes_only_subgraph = (
    graph.query()
    .nodes()
    .with_category("concept")
    .to_subgraph(include_edges=False)
)
```

## No imports required

The fluent query helpers are always reached through `graph.query()`. The objects
they return are internal implementation details: you never import or construct
them yourself.

The only classes you import from `pygraph_tool` are `Graph`, `Node`, `Edge`,
`Metadata`, and the exception types.
