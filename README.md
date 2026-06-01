# pygraph-tool

`pygraph-tool` is a lightweight Python library to create, manipulate, traverse and filter object-oriented graphs.

It provides simple and explicit Python classes and methods for working with nodes and edges. Nodes and edges have stable identifiers, can store user-defined Python values, and can be annotated with metadata for filtering, categorization, layering or application-specific usage.

The library is designed for developers who need a small, readable, in-memory graph toolkit that can be used in many kinds of Python projects.

## Why pygraph-tool?

`pygraph-tool` focuses on local graph manipulation with Python objects.

It is useful when you want to:

- create graphs in memory,
- store rich Python values in nodes and edges,
- model directed or bidirectional relationships,
- traverse graph structures,
- retrieve neighbors, predecessors and successors,
- extract local subgraphs,
- filter graph elements by predicate or metadata,
- write readable chained queries,
- prototype graph-based systems without adding a heavy dependency.

`pygraph-tool` is not a graph database. It does not provide persistence, transactions, clustering, query optimization or server features. It focuses on local, in-memory graph manipulation with Python objects.

## Installation

Install from PyPI:

```bash
pip install pygraph-tool
```

With `uv`:

```bash
uv add pygraph-tool
```

## Quick example

This example models a very small finite state machine.

```python
from pygraph_tool import Graph, Metadata

graph: Graph[str, str] = Graph()

graph.add_node(
    value="Idle",
    node_id="idle",
    metadata=Metadata(categories={"state"}),
)

graph.add_node(
    value="Running",
    node_id="running",
    metadata=Metadata(categories={"state"}),
)

graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
    edge_id="start",
    value="START",
    metadata=Metadata(categories={"transition"}),
)

successors = graph.get_successors("idle")

print([node.node_id for node in successors])
```

Output:

```text
['running']
```

## Chained queries

`pygraph-tool` also provides chainable query helpers for more readable graph operations.

```python
states = (
    graph.query()
    .nodes()
    .with_category("state")
    .to_list()
)
```

You can start from a node and traverse the graph:

```python
reachable_states = (
    graph.query()
    .from_node("idle")
    .traverse(max_depth=2, direction="outgoing", include_start=True)
    .to_list()
)
```

You can also query edges:

```python
transitions = (
    graph.query()
    .edges()
    .with_category("transition")
    .to_list()
)
```

## Main features

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
- Incoming, outgoing and incident edge retrieval
- Subgraph extraction from selected nodes
- Chainable local query interface
- Generic filtering with predicates
- Metadata-based filtering
- Dedicated exceptions for graph, node and edge errors
- Type information through `py.typed`

## Use cases

`pygraph-tool` can be used for many graph-based needs, including:

- finite state machines,
- dependency graphs,
- workflow graphs,
- object relationship graphs,
- concept maps,
- knowledge graphs,
- graph-based simulations,
- educational examples,
- local graph-based prototypes,
- in-memory graph manipulation.

The library intentionally stays general-purpose. More specialized systems can be built on top of it without making the core package specific to one domain.

## Documentation

More detailed documentation is available in the `docs/` directory:

- [Usage guide](https://github.com/DevAI-64/pygraph-tool/blob/main/docs/usage.md)
- [Chained queries](https://github.com/DevAI-64/pygraph-tool/blob/main/docs/query.md)
- [Development guide](https://github.com/DevAI-64/pygraph-tool/blob/main/docs/development.md)
- [Release guide](https://github.com/DevAI-64/pygraph-tool/blob/main/docs/release.md)

## Public classes

Main classes:

```python
from pygraph_tool import Edge, Graph, Metadata, Node
```

Query helper classes, mainly useful for type hints and advanced usage:

```python
from pygraph_tool import EdgeQuery, GraphQuery, NodeQuery, NodeTraversalQuery
```

Exceptions:

```python
from pygraph_tool import EdgeException, GraphException, NodeException
```

## Common methods

Create graph elements:

```python
graph.add_node(...)
graph.add_unidirectional_edge(...)
graph.add_bidirectional_edge(...)
```

Retrieve graph elements:

```python
graph.get_node(...)
graph.get_edge(...)
graph.is_node(...)
graph.is_edge(...)
```

Traverse the graph:

```python
graph.get_successors(...)
graph.get_predecessors(...)
graph.get_neighbors(...)
graph.get_reachable_nodes(...)
graph.get_shortest_path(...)
```

Retrieve connected edges:

```python
graph.get_outgoing_edges(...)
graph.get_incoming_edges(...)
graph.get_incident_edges(...)
```

Filter graph elements:

```python
graph.filter_nodes(...)
graph.filter_edges(...)
graph.filter_nodes_by_metadata(...)
graph.filter_edges_by_metadata(...)
```

Extract subgraphs:

```python
graph.extract_subgraph(...)
```

Use chained queries:

```python
graph.query().nodes()
graph.query().edges()
graph.query().from_node(...)
```

## Development

Install development dependencies:

```bash
uv sync --dev
```

Run the main checks:

```bash
uv run ruff format .
uv run ruff check .
uv run mypy pygraph_tool
uv run coverage run --branch -m pytest
uv run coverage report -m
```

More details are available in the [development guide](https://github.com/DevAI-64/pygraph-tool/blob/main/docs/development.md).

## Contributing

Contributions are welcome. Please read [CONTRIBUTING.md](https://github.com/DevAI-64/pygraph-tool/blob/main/CONTRIBUTING.md) before opening an issue or a pull request.

## Security

If you need to report a security issue, please read [SECURITY.md](https://github.com/DevAI-64/pygraph-tool/blob/main/SECURITY.md).

## Versioning

`pygraph-tool` follows semantic versioning.

Given a version number `MAJOR.MINOR.PATCH`:

- `MAJOR` changes may introduce breaking changes.
- `MINOR` changes add functionality in a backward-compatible way.
- `PATCH` changes fix bugs in a backward-compatible way.

## Roadmap

Potential future improvements:

- JSON serialization
- Optional local storage helpers
- Public indexing system
- Weighted shortest path search
- Mermaid export
- Graph visualization helpers
- Import and export helpers
- Additional graph traversal utilities

## License

This project is licensed under the terms of the MIT License.

## Author

Created and maintained by David BEL AICH.

For questions or suggestions, please contact: [belaich.david@outlook.fr](mailto:belaich.david@outlook.fr).
