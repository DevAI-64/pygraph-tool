"""Graph exceptions module."""


class PyGraphToolException(Exception):
    """Base exception for pygraph-tool."""


class NodeException(PyGraphToolException):
    """Exception raised for node-related errors."""


class EdgeException(PyGraphToolException):
    """Exception raised for edge-related errors."""


class GraphException(PyGraphToolException):
    """Exception raised for graph-related errors."""
