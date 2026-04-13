"""
Metadata schema for agricultural vision datasets.

This module defines Pydantic models for structuring metadata of agricultural
datasets, including information about datasets, machines, sensors, fields,
plots, and images.
"""

from pydantic import Field
import sys

sys.path.append("")

from metadata_vision.schemas.base import RDFModel
from metadata_vision.utils.namespaces import FOAF


class AgentMetadata(RDFModel):
    rdf_type: str = "foaf:Agent"

    name: str = Field(..., json_schema_extra={"example": "Jane Doe", "uri": FOAF + "name"})
