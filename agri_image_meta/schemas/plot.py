"""
Pydantic models for agricultural field and plot metadata.

Defines data structures for fields, plots crops, weather conditions,
and surface cover types used in agricultural image datasets.
"""

from typing import List, Optional
import uuid
from pydantic import Field, model_validator
from agri_image_meta.schemas.plotstate import PlotStateMetadata

from agri_image_meta.utils.namespaces import AGIMAGE
from agri_image_meta.schemas.base import RDFModel


class PlotMetadata(RDFModel):
    """
    Metadata model on plot level. Contains information about plotID location
    And related crops, weeds, soil type, weather conditions, external conditions and surface cover.
    """

    rdf_type: str = "agimage:Plot"

    # ---------------------
    # Plot-related fields
    # ---------------------
    plotName: str = Field(
        ...,
        description="Plot or Greenhouse identifier",
        json_schema_extra={
            "example": "plot123",
            "@tag": "ex:plotName",
            "uri": AGIMAGE + "plotName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    plotID: Optional[str] = Field(
        None,
        description="Unique identifier for the maplot based on plot + uuid",
        json_schema_extra={
            "example": "plot123_448aadb7-b07d-498d-9301-2240533d849a",
            #    "@tag": "ex:plotID",
            "uri": AGIMAGE + "plotID",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )

    bbox: List[str] = Field(
        ...,
        description="Plot polygon as WKT literal (dcterms:Location)",
        json_schema_extra={
            "example": [
                "POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))"
            ],
            "@tag": "dcat:bbox",
            "uri": AGIMAGE + "plotBbox",
            "parent_uri": "https://www.w3.org/ns/dcat#bbox",
            # "uri": "https://www.w3.org/ns/dcat#bbox",
            # "datatype": "rdf:List",
        },
    )
    hasPlotState: PlotStateMetadata | list[PlotStateMetadata] = Field(
        ...,
        description="Defining the state of the plot, so crops/weed growth stage," \
        "environmental conditions at certain timestamp",
        json_schema_extra={
            "example": [
                "POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))"
            ],
            "uri": AGIMAGE + "hasPlotState",
        },
    )

    @model_validator(mode="after")
    def set_id(self):
        if self.plotID is None:
            self.plotID = f"{self.plotName}_{uuid.uuid4()}"
        return self


if __name__ == "__main__":
    import json

    print(json.dumps(PlotMetadata.model_json_schema(), indent=4))

    # Create an example instance
    example = PlotMetadata(
        plotName="plot123",
        bbox="POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
        # hasPlotState=None
    )

    print("\nExample instance:")
    print(example.model_dump_json(indent=2))
