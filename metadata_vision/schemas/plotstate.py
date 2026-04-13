"""
Pydantic models for agricultural field and plot metadata.

Defines data structures for fields, plots crops, weather conditions,
and surface cover types used in agricultural image datasets.
"""

from typing import List, Optional
import uuid
from enum import Enum
import datetime
from pydantic import Field, field_validator, model_validator
from metadata_vision.old_code.generate_example_json import extract
from metadata_vision.schemas.crop import CropMetadata, CropHandling
from metadata_vision.utils.namespaces import AGIMAGE
from metadata_vision.utils.file_system import get_strptime
from metadata_vision.schemas.base import RDFModel


class WeatherConditions(str, Enum):
    """General description of the weather conditions."""

    SUNNY = "sunny"
    CLOUDY = "cloudy"
    DIFFUSE = "diffuse"
    RAINY = "rainy"


class ExternalConditions(str, Enum):
    """Relevant external conditions."""

    SOLAR_PANELS = "solar panels"
    SHADE_COVER = "shade cover"
    LED = "LED"

    @classmethod
    def validate(cls, value: str) -> str:
        """Accept enum values OR any string"""
        try:
            return cls(value).value
        except ValueError:
            # Not in enum, but accept it anyway
            return value


class SoilType(str, Enum):
    """soil taxonomy classification based on 'Soil Texture Triangle'.
    # https://serc.carleton.edu/details/images/343276.html
    This triangly classifies soil by using percentage clay, silt and sand.
    """

    CLAY = "clay"
    CLAY_LOAM = "clay"
    SILT = "silt"
    SILTY_CLAY = "silty clay"
    SILTY_CLAY_LOAM = "silty clay loam"
    SILT_LOAM = "silt loam"
    LOAM = "loam"
    LOAMY_SAND = "loamy sand"
    SAND = "sand"
    SANY_LOAM = "sand loam"
    SANDY_CLAY = "sandy clay"
    SANDY_CLAY_LOAM = "sandy clay loam"


class SurfaceLayer(str, Enum):
    """Non-crop surface cover visible in the images."""

    SHELLS = "shells"
    STRAW = "straw"
    BIO_FILM = "bio film"
    STONES = "stones"
    LOOSE_LEAVES = "loose leaves"

    ## greenhouse specific
    WHITE_CANVAS = "white canvas"
    BLACK_CANVAS = "black canvas"


class PlotStateMetadata(RDFModel):
    """
    Metadata model on plot level. Contains information about plotID location
    And related crops, weeds, soil type, weather conditions, external conditions and surface cover.
    """

    rdf_type: str = "agimage:PlotState"

    # ---------------------
    # PlotState-related fields
    # ---------------------
    stateName: str = Field(
        None,
        description="Name of the state of plot, used plotName_state_1",
        json_schema_extra={
            "example": "plot123_state_1",
            #    "@tag": "ex:plotID",
            "uri": AGIMAGE + "stateNae",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )
    stateID: Optional[str] = Field(
        None,
        description="Unique identifier for the state of the plot, used if timestamp changes",
        json_schema_extra={
            "example": "plot123_state_1",
            #    "@tag": "ex:plotID",
            "uri": AGIMAGE + "stateID",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )
    validFrom: Optional[datetime.datetime | str] = Field(
        None,
        description="ISO 8601 timestamp from which this plot state is valid",
        json_schema_extra={
            "example": "2024-01-15T10:30:00Z",
            "uri": AGIMAGE + "validFrom",
        },
    )

    validTo: Optional[datetime.datetime | str] = Field(
        None,
        description="ISO 8601 timestamp until which this plot state is valid",
        json_schema_extra={
            "example": "2024-01-16T10:30:00Z",
            "uri": AGIMAGE + "validTo",
        },
    )

    hasCrop: CropMetadata | List[CropMetadata] = Field(
        ...,
        description="List of crops planted in the plot",
        json_schema_extra={
            "example": extract(CropMetadata),
            "@tag": "ex:crops",
            "uri": AGIMAGE + "crop",
            "cardinalityMax": "*",
        },
    )

    hasWeed: Optional[CropMetadata | List[CropMetadata]] = Field(
        None,
        description="List of weeds present in the plot",
        json_schema_extra={
            "example": {"cropName": "dandelion", "cropCode": "TAROF"},
            "@tag": "ex:weeds",
            "uri": AGIMAGE + "weed",
            "parent_uri": AGIMAGE + "crop",
            "datatype": "agimage:crop",
            "cardinalityMax": "*",
        },
    )

    soilType: Optional[SoilType] = Field(
        None,
        description="Soil type based Soil Texture Triangle" \
        "https://serc.carleton.edu/details/images/343276.html",
        json_schema_extra={
            "example": SoilType.CLAY.name,  
            "uri": "https://aims.fao.org/aos/agrovoc/c_7156.html",
        },
    )

    ## should be derived automatically
    weatherConditions: Optional[WeatherConditions] = Field(
        None,
        description="General description of the weather conditions",
        json_schema_extra={
            "example": WeatherConditions.SUNNY.name,
            "uri": "https://dbpedia.org/page/Weather",
            "@tag": "ex:weatherConditions",
        },
    )

    # externalConditions: Optional[ExternalConditions] = Field(
    #     None,
    #     description="Relevant external conditions",
    #     json_schema_extra={
    #         "example": ExternalConditions.LED.name,
    #         "@tag": "ex:externalConditions",
    #     },
    # )

    surfaceLayer: Optional[list[SurfaceLayer]] = Field(
        None,
        description="Non-crop surface cover visible in the images, for example shells, straw",
        json_schema_extra={
            "example": [SurfaceLayer.SHELLS.name, SurfaceLayer.STRAW.name],
            "@tag": "ex:surfaceLayer",
            "uri": "http://purl.obolibrary.org/obo/ENVO_00010504",
        },
    )

    @field_validator("validFrom", "validTo", mode="before")
    @classmethod
    def validate_image_timestamp(cls, v):
        return get_strptime(v)

    @model_validator(mode="after")
    def set_id(self):
        if self.stateID is None:
            self.stateID = f"{self.stateName}_{uuid.uuid4()}"
        return self


if __name__ == "__main__":
    import json

    print(json.dumps(PlotStateMetadata.model_json_schema(), indent=4))

    # Create an example instance
    example = PlotStateMetadata(
        stateID="plot123_state1",
        bbox="POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
        crops=[
            CropMetadata(
                cropName="cucumber",
                cropCultivar="Hi Power",
                cropHandling=CropHandling.CROP_OBSERVATION,
                cropGrowthStageMin=60,
                cropGrowthStageMax=65,
            )
        ],
        weeds=[
            CropMetadata(
                cropName="dandelion",
                cropCultivar=None,
                cropHandling=None,
                cropGrowthStageMin=None,
                cropGrowthStageMax=None,
            )
        ],
        soil_type="clay loam",
        weather_conditions=WeatherConditions.SUNNY,
        external_conditions=ExternalConditions.LED,
        surface_cover=[SurfaceLayer.LOOSE_LEAVES, SurfaceLayer.WHITE_CANVAS],
    )

    print("\nExample instance:")
    print(example.model_dump_json(indent=2))
