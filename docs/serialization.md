# Serialization guide

This guide shows how to serialize and deserialize a graph with `pygraph-tool`.

`pygraph-tool` can convert a graph into a standard Python dictionary, and
optionally into JSON. It relies only on the standard library: there is no extra
dependency, no `pickle`, and no specialized graph format. The goal is to import
and export graphs, not to provide a database or a persistence layer.

## Overview

Serialization is organized in layers:

- `to_dict()` / `from_dict()` convert a graph to and from a plain Python
  dictionary.
- `to_json()` / `from_json()` convert a graph to and from a JSON string.
- `save_json()` / `load_json()` write and read a JSON file.

Node and edge identifiers, values, weights, directions, and metadata are
preserved, so a round trip rebuilds an equivalent graph.

## Convert a graph to a dictionary

```python
from pygraph_tool import Graph, Metadata

graph: Graph[str, str] = Graph()
graph.add_node(value="Idle", node_id="idle", metadata=Metadata(categories={"state"}))
graph.add_node(value="Running", node_id="running")
graph.add_unidirectional_edge(
    node_id_start="idle",
    node_id_end="running",
    edge_id="start",
    value="START",
    metadata=Metadata(categories={"transition"}),
)

data = graph.to_dict()
```

The dictionary uses only standard Python containers:

```python
{
    "schema_version": "1.0",
    "nodes": [
        {"id": "idle", "value": "Idle", "metadata": {"categories": ["state"]}},
        {"id": "running", "value": "Running"},
    ],
    "edges": [
        {
            "id": "start",
            "source": "idle",
            "target": "running",
            "value": "START",
            "weight": 1.0,
            "bidirectional": False,
            "metadata": {"categories": ["transition"]},
        }
    ],
}
```

Notes:

- Nodes and edges are emitted in insertion order.
- Metadata sets (`tags`, `categories`, `layers`, `flags`) are exported as
  sorted lists, which keeps the output deterministic.
- Empty metadata is omitted to keep the output compact.

## Rebuild a graph from a dictionary

```python
restored = Graph.from_dict(data)
```

`from_dict()` returns a `Graph[Any, Any]` because value types cannot be inferred
from serialized data. Identifiers, weights, directions, and metadata are
restored, and the adjacency indexes are rebuilt automatically.

## JSON strings

```python
text = graph.to_json(indent=2)
restored = Graph.from_json(text)
```

`to_json()` accepts `indent` and `sort_keys`, which are passed to the standard
JSON encoder.

## JSON files

```python
graph.save_json("graph.json")
restored = Graph.load_json("graph.json")
```

Files are written and read as UTF-8. `save_json()` uses `indent=2` by default to
produce a human-readable file.

## Values that are not JSON-compatible

By default, node and edge values are written as-is. Standard values such as
strings, numbers, booleans, `None`, lists, and dictionaries are supported
directly. The same applies to `Metadata.properties`, which must contain
JSON-compatible values.

If a value is not JSON-serializable, `to_json()` raises a
`SerializationException`. To handle richer values, provide conversion hooks:

```python
from datetime import datetime

graph: Graph[datetime, str] = Graph()
graph.add_node(value=datetime(2026, 6, 1, 12, 30), node_id="event")

text = graph.to_json(serialize_node_value=lambda value: value.isoformat())

restored = Graph.from_json(
    text,
    deserialize_node_value=datetime.fromisoformat,
)
```

The available hooks are:

- `serialize_node_value` and `serialize_edge_value` on `to_dict()`, `to_json()`,
  and `save_json()`.
- `deserialize_node_value` and `deserialize_edge_value` on `from_dict()`,
  `from_json()`, and `load_json()`.

## Error handling

Serialization and deserialization errors raise `SerializationException`:

```python
from pygraph_tool import Graph, SerializationException

try:
    Graph.from_json("{not valid json")
except SerializationException as error:
    print(error)
```

A `SerializationException` is raised when the JSON is invalid, when the data is
malformed (missing keys, wrong types, unsupported `schema_version`), when the
data is inconsistent (an edge referencing an unknown node, a duplicate
identifier), or when a value is not JSON-serializable and no hook converts it.
