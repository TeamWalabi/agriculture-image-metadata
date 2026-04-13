"""Ontology generation and validation module."""

from .generator import (
    generate_class,
    generate_ontology,
    generate_shacl,
    get_model_shape_uri,
    get_model_class_uri,
    add_property_shapes,
    add_model_to_graph,
)

__all__ = [
    "generate_class",
    "generate_ontology",
    "generate_shacl",
    "get_model_shape_uri",
    "get_model_class_uri",
    "add_property_shapes",
    "add_model_to_graph",
]
