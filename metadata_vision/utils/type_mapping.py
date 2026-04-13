from __future__ import annotations


from rdflib import XSD
from typing import get_origin, get_args


def unwrap_type(t):
    """Handle Optional, List, Union types"""
    origin = get_origin(t)
    if origin is list:
        return get_args(t)[0]
    if origin is None:
        return t
    args = get_args(t)
    if args:
        return args[0]
    return t


def python_to_xsd(t):
    """Map Python types to XSD types"""
    mapping = {
        str: XSD.string,
        int: XSD.integer,
        float: XSD.double,
        bool: XSD.boolean,
    }
    return mapping.get(t, XSD.string)
