# Changelog

All notable changes to this project will be documented in this file.

This project follows [Semantic Versioning](https://semver.org/).

## [1.1.0] - 2026-05-31

### Added

- Added adjacency indexes to improve outgoing, incoming, and incident edge lookups.
- Added `Graph.get_neighbors()` to retrieve neighboring nodes by direction.
- Added `Graph.get_reachable_nodes()` for breadth-first traversal up to a maximum depth.
- Added `Graph.get_shortest_path()` for unweighted shortest path search.
- Added `Graph.extract_subgraph()` to create a graph from a selected set of nodes.
- Added `Metadata.copy()` to safely duplicate metadata collections.

### Changed

- Updated graph edge lookup internals to rely on adjacency indexes.
- Improved traversal performance for graph navigation methods.
- Preserved existing public API behavior while improving internal storage.

### Fixed

- Ensured adjacency indexes remain consistent when removing edges.
- Ensured adjacency indexes remain consistent when removing nodes and their connected edges.
- Ensured subgraph extraction copies metadata instead of sharing metadata instances.

### Tests

- Added traversal tests for neighbors, reachable nodes, and shortest paths.
- Added subgraph extraction tests.
- Added metadata copy tests.
- Improved coverage around edge and node removal with adjacency indexes.

## [1.0.0] - 2026-05-30

### Added

* Added automatic UUID-based identifiers for nodes when no `node_id` is provided.
* Added automatic UUID-based identifiers for edges when no `edge_id` is provided.
* Added generic user-defined `value` support for nodes.
* Added generic user-defined `value` support for edges.
* Added `Metadata` support for nodes and edges.
* Added metadata fields:

  * `tags`
  * `categories`
  * `layers`
  * `flags`
  * `properties`
* Added bidirectional edge support.
* Added `Graph.add_edge()` as a generic edge creation method.
* Added `Graph.add_unidirectional_edge()` helper.
* Added `Graph.add_bidirectional_edge()` helper.
* Added edge traversal methods:

  * `get_outgoing_edges(node_id)`
  * `get_incoming_edges(node_id)`
  * `get_incident_edges(node_id)`
* Added node traversal methods with duplicate removal:

  * `get_successors(node_id)`
  * `get_predecessors(node_id)`
* Added generic filtering methods:

  * `filter_nodes(predicate)`
  * `filter_edges(predicate)`
* Added metadata-based filtering methods:

  * `filter_nodes_by_metadata(...)`
  * `filter_edges_by_metadata(...)`
* Added support for multiple edges between the same pair of nodes when edge identifiers are distinct.
* Added public package exports for core classes and exceptions.

### Changed

* Reworked the internal graph storage from lists to dictionaries indexed by identifiers.
* Improved node lookup performance by using internal node id indexing.
* Improved edge lookup performance by using internal edge id indexing.
* Changed `Graph.add_node()` to return the created `Node`.
* Changed edge creation methods to return the created `Edge`.
* Changed graph node and edge collections to be exposed as read-only tuples.
* Changed node identity semantics to rely on immutable `node_id`.
* Changed edge identity semantics to rely on immutable `edge_id`.
* Updated successors and predecessors traversal to correctly handle bidirectional edges.
* Updated traversal methods to remove duplicate returned nodes or edges.
* Updated the package configuration to use `uv` and a modern `pyproject.toml` workflow.
* Updated the README to reflect the new public API.

### Removed

* Removed mutable public setters for graph node and edge collections.
* Removed the previous placeholder behavior for bidirectional edges.
* Removed the old `node_content` API in favor of the generic `value` attribute.

### Fixed

* Fixed node content handling so falsy values such as `0`, `False`, empty strings, empty lists, and empty dictionaries can be stored as valid node values.
* Fixed bidirectional edge traversal behavior.
* Fixed duplicate neighbor results in predecessor and successor lookups.
* Fixed duplicate edge results in incoming, outgoing, and incident edge lookups.

### Development

* Added an expanded test suite covering nodes, edges, metadata, graph operations, traversal, filtering, and duplicate handling.
* Added type-checking-oriented tests and annotations for generic graph components.
* Added coverage-oriented tests for the public API.
