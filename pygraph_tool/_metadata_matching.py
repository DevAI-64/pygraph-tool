"""Metadata matching helpers."""

from collections.abc import Iterable

from .metadata import Metadata


def matches_metadata(
    metadata: Metadata,
    *,
    tags: Iterable[str] | None = None,
    categories: Iterable[str] | None = None,
    layers: Iterable[str] | None = None,
    flags: Iterable[str] | None = None,
    match_all: bool = True,
) -> bool:
    """Return whether metadata matches the provided criteria.

    Args:
        metadata: Metadata to inspect.
        tags: Optional tags to match.
        categories: Optional categories to match.
        layers: Optional layers to match.
        flags: Optional flags to match.
        match_all: If True, all expected values must be present within each
            provided criterion. If False, at least one expected value must be
            present within each provided criterion.

    Returns:
        True if the metadata matches all provided criteria, False otherwise.
    """
    return (
        matches_values(metadata.tags, tags, match_all)
        and matches_values(metadata.categories, categories, match_all)
        and matches_values(metadata.layers, layers, match_all)
        and matches_values(metadata.flags, flags, match_all)
    )


def matches_values(
    existing_values: set[str],
    expected_values: Iterable[str] | None,
    match_all: bool,
) -> bool:
    """Return whether a set contains expected values.

    Args:
        existing_values: Existing metadata values.
        expected_values: Expected metadata values.
        match_all: If True, all expected values must be present. If False,
            at least one expected value must be present.

    Returns:
        True if the values match, False otherwise.
    """
    if expected_values is None:
        return True

    expected_values_set = set(expected_values)

    if not expected_values_set:
        return True

    if match_all:
        return expected_values_set.issubset(existing_values)

    return bool(existing_values.intersection(expected_values_set))
