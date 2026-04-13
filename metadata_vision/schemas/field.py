"""
Pydantic models for agricultural field and plot metadata.

Defines data structures for fields, plots crops, weather conditions,
and surface cover types used in agricultural image datasets.
"""

from typing import Optional
import uuid
from pydantic import Field, model_validator
from metadata_vision.generate_example_json import extract
from metadata_vision.schemas.plot import PlotMetadata

from metadata_vision.utils.namespaces import AGIMAGE
from metadata_vision.schemas.base import RDFModel


class FieldMetadata(RDFModel):
    """
    Metadata model for agricultural field information.
    Attributes:
        fieldID: Unique identifier for the field.
        plots: Optional list of plot metadata or single plot metadata within the field.
    """

    rdf_type: str = "agimage:Field"
    # rdf_type: str = "agimage:Plot"

    fieldName: str = Field(
        ...,
        description="Name of the field",
        json_schema_extra={
            "example": "field_001",
            #    "@tag": "ex:fieldName",
            # "uri": "http://purl.org/dc/terms/title",
            "uri": AGIMAGE + "fieldName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    fieldID: Optional[str] = Field(
        None,
        description="Unique identifier for the field based on field + uuid",
        json_schema_extra={
            "example": "field_001_5de48942-0c39-411f-8f4a-756b0c20f7bb",
            "@tag": "ex:fieldID",
            "uri": AGIMAGE + "fieldID",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )

    bbox: str = Field(
        ...,
        description="Field polygon as WKT literal (dcterms:Location) long, lat",
        json_schema_extra={
            "example": "POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
            "@tag": "dcat:bbox",
            "uri": AGIMAGE + "fieldBbox",
            "parent_uri": "https://www.w3.org/ns/dcat#bbox",
        },
    )

    hasPlot: Optional[PlotMetadata | list[PlotMetadata]] = Field(
        None,
        description="List of plots in the field",
        json_schema_extra={
            "example": extract(PlotMetadata),
            "uri": AGIMAGE + "hasPlot",
        },
    )


    @model_validator(mode="after")
    def set_id(self):
        if self.fieldID is None:
            self.fieldID = f"{self.fieldName}_{uuid.uuid4()}"
        return self
