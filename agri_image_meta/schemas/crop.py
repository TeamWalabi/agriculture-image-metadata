"""Crop/weed related metadata representing crop-related metadata,
including crop handling operations, growth stages, and cultivar information.
It uses the AgroconnectCL291 classification for crop operations and BBCH scale"""

from typing import List, Optional
from enum import Enum
import datetime
from pydantic import Field, field_validator
from agri_image_meta.generate_example_json import extract
from agri_image_meta.schemas.base import RDFModel
from agri_image_meta.utils.namespaces import AGIMAGE
from agri_image_meta.utils.file_system import get_strptime


class CropHandling(str, Enum):
    """Activity related to the dataset. Based on AgroconnectCL291 level1."""

    ## based on AgroconnectCL291 level1
    PROFILE_IMPROVEMENT = "Profile Improvement"
    TILLAGE = "Tillage"
    PLANTING = "Planting"
    CROP_PROTECTION = "Crop Protection"
    CROP_CONDITIONING = "Crop conditioning"
    FERTILIZING = "Fertilizing"
    PRODUCT_HANDLING = "Product handling"
    STORAGE = "Storage"
    SOIL_SAMPLING = "Soil Sampling"
    CROP_OBSERVATION = "Crop observation"
    FIELD_WATERWAY_MAINTENANCE = "Field&Waterway maintencance"
    REPAIR_AND_MAINTENANCE = "repair and maintenance"
    ADMINISTRATION = "Administration"


class CropTimingType(str, Enum):
    ## based on https://agrovoc.fao.org/browse/agrovoc/en/page/c_7779
    FLOWERING_TIME = "flowering_time"
    HARVESTING_DATE = "harvesting_date"
    PLANTING_DATE = "planting_date"
    SOWING_DATE = "sowing_date"
    SYNCHRONIZATION = "synchronization"
    TRANSPLANTING_DATE = "transplanting_date"
    TREATMENT_DATE = "treatment_date"


class CropTiming(RDFModel):
    rdf_type: str = "agimage:CropTiming"

    type: CropTimingType = Field(
        ...,
        description="Type of crop timing event",
        json_schema_extra={
            "example": CropTimingType.PLANTING_DATE.name,
            "@tag": "ex:cropTimingType",
            "uri": "https://agrovoc.fao.org/browse/agrovoc/en/page/c_7779",
        },
    )
    date: Optional[datetime.datetime | str] = Field(
        None,
        description="Date of the crop timing event",
        json_schema_extra={
            "example": "20251014T093000Z",
            "@tag": "ex:cropTimingDate",
            "uri": "http://www.w3.org/TR/xmlschema11-2/#dateTime",
        },
    )

    @field_validator("date", mode="before")
    @classmethod
    def validate_image_timestamp(cls, v):
        return get_strptime(v)


class CropMetadata(RDFModel):
    """
    Metadata model for crop-related information.
    """

    rdf_type: str = "agimage:Crop"

    # ---------------------
    # Crop-related fields
    # ---------------------
    cropName: str = Field(
        ...,
        description="Name of the crop, please search in following database: https://gd.eppo.int/",
        json_schema_extra={
            "example": "cucumber",
            "@tag": "ex:cropName",
            "uri": AGIMAGE + "cropName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    cropCode: str = Field(
        ...,
        description="Code of the crop (e.g. EPPO code from https://gd.eppo.int/taxon/)",
        json_schema_extra={
            "example": "CUMSA",
            "@tag": "ex:cropCode",
            "uri": "https://gd.eppo.int/taxon/",
        },
    )

    cropCultivar: Optional[str | List[str]] = Field(
        None,
        description="Variety of the crop; Have a look at and download the list https://ec.europa.eu/food/plant-variety-portal/#. Cucuber example has Hi power variety",
        json_schema_extra={
            "example": ["Hi power"],
            "@tag": "ex:cropCultivar",
            "controlledVocabulary": "https://ec.europa.eu/food/plant-variety-portal/#",
            "uri": "https://w3id.org/agri-image/cropCultivar",
        },
    )

    cropHandling: Optional[CropHandling] = Field(
        None,
        description="Activity related to the dataset. Choose from predefined crop operations "
        "based on AgroconnectCL291 level1",
        json_schema_extra={
            "example": CropHandling.CROP_OBSERVATION.name,
            "@tag": "ex:cropHandling",
            "controlledVocabulary": "AgroconnectCL291",
            "uri": "https://w3id.org/agri-image/cropHandling",
        },
    )

    cropGrowthStageMin: Optional[int] = Field(
        None,
        description="BBCH minimum growth stage of the main crop (0-100)",
        json_schema_extra={
            "example": "60",
            "@tag": "ex:growthStageMin",
            "uri": "https://opendata.inrae.fr/ppd-def#GrowthStage",
        },
    )

    cropGrowthStageMax: Optional[int] = Field(
        None,
        description="BBCH maximum growth stage of the main crop (0-100)",
        json_schema_extra={
            "example": "65",
            "@tag": "ex:growthStageMax",
            "uri": "https://opendata.inrae.fr/ppd-def#GrowthStage",
        },
    )

    cropTiming: Optional[CropTiming | List[CropTiming]] = Field(
        None,
        description="List of crop timing events (e.g., planting, harvesting, flowering, etc.)",
        json_schema_extra={
            "example": extract(CropTiming),
            "@tag": "ex:cropTiming",
            "uri": "https://agrovoc.fao.org/browse/agrovoc/en/page/c_7779",
            "cardinalityMax": "*",
        },
    )

    # cropEPPO: str = Field(
    #     ...,
    #     description="Add crop EPPO code (https://gd.eppo.int/taxon)",
    #     json_schema_extra={
    #         "example": "CUMSA",
    #         "@tag": "ex:cropEPPO"}
    # )

    # datasetPurpose: Optional[str] = Field(
    #     None,
    #     description="Is this dataset about the plant itself or its product?",
    #     example="productCrop",
    #     json_schema_extra={"@tag": "ex:datasetPurpose"}
    # )

    # cropProductionPurpose: Optional[str] = Field(
    #     None,
    #     description="Production purpose of the crop (e.g., consumption, starch)",
    #     example="NA",
    #     json_schema_extra={"@tag": "ex:cropPurpose"}
    # )


if __name__ == "__main__":
    # Generate and print the JSON schema for CropMetadata
    print(CropMetadata.model_json_schema())
