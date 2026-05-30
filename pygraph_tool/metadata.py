"""Metadata module."""

from dataclasses import dataclass, field


@dataclass(slots=True)
class Metadata:
    """Generic metadata associated with a graph element.

    Metadata stores graph-level annotations that can be used for filtering,
    categorization, layering, visualization, or application-specific hints.

    Attributes:
        tags: Free-form textual tags associated with the graph element.
        categories: Higher-level categories the graph element belongs to.
        layers: Logical graph layers the graph element belongs to.
        flags: Boolean-like textual markers describing graph-level states.
        properties: Additional user-defined metadata.
    """

    tags: set[str] = field(default_factory=set)
    categories: set[str] = field(default_factory=set)
    layers: set[str] = field(default_factory=set)
    flags: set[str] = field(default_factory=set)
    properties: dict[str, object] = field(default_factory=dict)

    def has_tag(self, tag: str) -> bool:
        """Return whether the metadata contains a tag.

        Args:
            tag: Tag to check.

        Returns:
            True if the tag exists, False otherwise.
        """
        return tag in self.tags

    def has_category(self, category: str) -> bool:
        """Return whether the metadata contains a category.

        Args:
            category: Category to check.

        Returns:
            True if the category exists, False otherwise.
        """
        return category in self.categories

    def has_layer(self, layer: str) -> bool:
        """Return whether the metadata contains a layer.

        Args:
            layer: Layer to check.

        Returns:
            True if the layer exists, False otherwise.
        """
        return layer in self.layers

    def has_flag(self, flag: str) -> bool:
        """Return whether the metadata contains a flag.

        Args:
            flag: Flag to check.

        Returns:
            True if the flag exists, False otherwise.
        """
        return flag in self.flags
