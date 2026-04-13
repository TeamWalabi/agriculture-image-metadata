"""
Metadata schema for agricultural vision datasets.

This module defines Pydantic models for structuring metadata of agricultural
datasets, including information about datasets, machines, sensors, fields,
plots, and images.
"""

import datetime
import uuid
from typing import Optional, List

from pydantic import Field

from metadata_vision.schemas.base import RDFModel
from metadata_vision.schemas.agent import AgentMetadata
from metadata_vision.schemas.images import ImageMetadata
from metadata_vision.schemas.field import FieldMetadata
from metadata_vision.schemas.platform import PlatformMetadata
from metadata_vision.utils.namespaces import AGIMAGE
from metadata_vision.generate_example_json import extract
from pydantic import field_validator
from metadata_vision.utils.file_system import get_strptime


class DatasetMetadata(RDFModel):
    """
    Metadata model for vision based datasets in agriculture.
    http://www.w3.org/ns/dcat#Dataset
    """

    rdf_type: str = "dcat:Dataset"

    # ---------------------
    # General dataset info
    # ---------------------
    title: str = Field(
        ...,
        description="Name of the dataset",
        json_schema_extra={
            "example": "Cucumber phenotyping dataset",
            "uri": "http://purl.org/dc/terms/title",
        },
    )

    ID: str = Field(
        str(uuid.uuid4()),
        description="unique ID of the dataset",
        json_schema_extra={
            "example": "7265f151-2ffe-4ab5-a3b7-47ec39ca8c40",
            "uri": "http://purl.org/dc/terms/identifier",
        },
    )

    description: str = Field(
        ...,
        description="General description of the dataset",
        json_schema_extra={
            "example": (
                "This dataset is recorded in a commercial cucumber greenhouse. "
                "Four classes are annotated: cucumbers, leaves, open flower and closed flower."
            ),
            "entity": "DatasetMetadata",
            "uri": "http://purl.org/dc/terms/description",
        },
    )

    accessURL: Optional[str] = Field(
        None,
        description="URL where the dataset can be found",
        json_schema_extra={
            "example": "https://example.org/datasets/cucumber-phenotyping",
            "uri": "http://www.w3.org/ns/dcat#accessURL",
            "property": "accessURL",
        },
    )

    version: Optional[str] = Field(
        None,
        description="Version number of the dataset",
        json_schema_extra={
            "example": "1",
            "uri": "http://www.w3.org/ns/dcat#version",
        },
    )

    # ---------------------
    # Dates
    # ---------------------
    issued: Optional[datetime.datetime | str] = Field(
        None,
        description="Date this dataset version was created or uploaded",
        json_schema_extra={
            "example": "20251014T093000Z",
            "uri": "http://purl.org/dc/terms/issued",
        },
    )
    modified: Optional[datetime.datetime | str] = Field(
        None,
        description="Date this dataset version was last modified YYYYMMDDTHHMMSSZ",
        json_schema_extra={
            "example": "20251014T093000Z",
            "uri": "http://purl.org/dc/terms/modified",
        },
    )

    startDate: Optional[datetime.datetime | str] = Field(
        None,
        description="Earliest date or timepoint in the dataset YYYYMMDDTHHMMSSZ",
        json_schema_extra={
            "example": "20251014T093000Z",
            "uri": "http://www.w3.org/ns/dcat#startDate",
        },
    )

    endDate: Optional[datetime.datetime | str] = Field(
        None,
        description="Latest date or timepoint in the dataset",
        json_schema_extra={
            "example": "20251014T093000Z",
            "uri": "http://www.w3.org/ns/dcat#endDate",
            "@type": "xsd:dateTime",
        },
    )

    # ---------------------
    # Identification & people
    # ---------------------
    identifier: str = Field(
        ...,
        description=(
            "Unique identifier of the dataset, preferably in the format projectnumber_datasetname"
        ),
        json_schema_extra={
            "example": "3742355900_agros2_komkommer",
            "uri": "http://purl.org/dc/terms/identifier",
        },
    )

    creator: AgentMetadata = Field(
        ...,
        json_schema_extra={
            "example": extract(AgentMetadata),
            "uri": "http://purl.org/dc/terms/creator",
            "cardinalityMax": "*",
        },
    )

    contributor: Optional[AgentMetadata | list[AgentMetadata]] = Field(
        None,
        description="Contributors to the dataset",
        json_schema_extra={
            "example": extract(AgentMetadata),
            "uri": "http://purl.org/dc/terms/contributor",
            "cardinalityMax": "*",
        },
    )

    # ---------------------
    # License
    # ---------------------

    license: Optional[str] = Field(
        None,
        description=(
            "Type of license (see https://creativecommons.org/share-your-work/cclicenses/)"
        ),
        json_schema_extra={
            "example": "CC BY-NC-SA",
            "uri": "http://purl.org/dc/terms/license",
        },
    )

    # ---------------------
    # Dataset statistics
    # ---------------------
    numberOfImages: int = Field(
        None,
        description="Total number of images in the dataset (auto-filled)",
        json_schema_extra={"example": -1, "uri": AGIMAGE + "numberOfImages"},
    )

    numberOfAnnotatedImages: int = Field(
        None,
        description="Total number of annotated images (auto-filled)",
        json_schema_extra={"example": -1, "uri": AGIMAGE + "numberOfAnnotatedImages"},
    )
    hasField: FieldMetadata | list[FieldMetadata] = Field(
        ..., json_schema_extra={"uri": AGIMAGE + "hasField"}
    )

    hasPlatform: PlatformMetadata | list[PlatformMetadata] = Field(
        ..., json_schema_extra={"uri": AGIMAGE + "hasPlatform"}
    )

    hasImage: Optional[ImageMetadata | List[ImageMetadata]] = Field(
        default=None, json_schema_extra={"uri": AGIMAGE + "hasImage"}
    )

    @field_validator("issued", "modified", "startDate", "endDate", mode="before")
    @classmethod
    def validate_image_timestamp(cls, v):
        return get_strptime(v)


if __name__ == "__main__":
    # Export all "id" fields from the dummy_package
    def extract_ids(obj, key="@id"):
        if isinstance(obj, dict):
            result = {}
            for k, v in obj.items():
                if isinstance(v, (dict, list)):
                    nested = extract_ids(v, key)
                    if nested:
                        result[k] = nested
                if key in k.lower():
                    result[k] = v
            return result
        elif isinstance(obj, list):
            return [extract_ids(item, key) for item in obj if extract_ids(item, key)]
        else:
            return None

    # schema = DatasetPackage.model_json_schema()
    # ids = extract_ids(schema)
    # print(json.dumps(ids, indent=4))
    # with open("ids.json", "w", encoding="utf-8") as f:
    #     json.dump(ids, f, indent=4)

    # ids = extract_ids(schema, "@tag")
    # print(json.dumps(ids, indent=4))
    # with open("tag.json", "w", encoding="utf-8") as f:
    #     json.dump(ids, f, indent=4)

    # a=dummy_package.to_jsonld()

    # print(json.dumps(dummy_package.to_jsonld(), indent=4))
    # with open("json_ld.json", "w", encoding="utf-8") as f:
    #     json.dump(dummy_package.to_jsonld(), f, indent=4)

    # with open("json.json", "w", encoding="utf-8") as f:
    #     json.dump(dummy_package.model_dump(), f, indent=4, default=str)


# metadata_vision/
# ├── __init__.py
# ├── schemas/                      # ← NEW: All Pydantic models
# │   ├── __init__.py
# │   ├── base.py                  # RDFModel base class
# │   ├── agent.py                 # AgentMetadata
# │   ├── camera.py                # CameraMetadata, DistortionModel
# │   ├── crop.py                  # CropMetadata, CropTiming
# │   ├── dataset.py               # DatasetMetadata
# │   ├── field.py                 # FieldMetadata
# │   ├── image.py                 # ImageMetadata
# │   ├── platform.py              # PlatformMetadata
# │   ├── plot.py                  # PlotMetadata
# │   ├── sensor.py                # SensorMetadata
# │   └── enums.py                 # SpectralBand, other enums
# ├── utils/                        # ← NEW: Utilities
# │   ├── __init__.py
# │   ├── namespaces.py            # All RDF namespaces (AGIMAGE, DCT, etc.)
# │   ├── rdf_helpers.py           # RDF-related utilities
# │   ├── type_mapping.py          # python_to_xsd(), unwrap_type()
# │   └── file_system.py           # Directory/file operations
# ├── ontology/
# │   ├── __init__.py
# │   ├── generator.py             # OWL ontology generation
# │   ├── shacl.py                 # SHACL shapes generation
# │   └── validator.py             # SHACL validation
# ├── main.py                       # Main entry point
# ├── unified_example.py            # Complete workflow
# └── generate_example_json.py      # JSON generation
