# platform_and_sensors.py

from typing import Optional

from pydantic import Field, field_validator, model_validator
import sys

sys.path.append("")
from metadata_vision.schemas.sensor import SensorMetadata

from metadata_vision.old_code.generate_example_json import extract

import uuid
from metadata_vision.utils.namespaces import AGIMAGE
from metadata_vision.schemas.base import RDFModel


class PlatformMetadata(RDFModel):
    """
    Metadata model for machine/platform information.
    Attributes:
        PlatformID: Unique identifier or name of the Platform/platform.
        sensors: Optional list of camera sensors mounted on the Platform/platform.
    https://www.w3.org/TR/vocab-ssn/#SOSAPlatform
    """

    # rdf_type: str = "agimage:Platform"
    rdf_type: str = "sosa:Platform"

    # ---------------------
    # Image-specific fields
    # ---------------------
    platformName: str = Field(
        ...,
        description="Name of the Platform/platform",
        json_schema_extra={
            "example": "demo_platform1",
            "uri": AGIMAGE + "platformName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    platformID: Optional[str] = Field(
        None,
        description="Unique identifier for the Platform/platform based on PlatformName + uuid",
        json_schema_extra={
            "example": "demo_platform1_09cbf6ae-8dc1-43dc-96ef-4675b71039c3",
            # "@tag": "ex:PlatformId",
            "uri": AGIMAGE + "platformID",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )

    hasSensor: SensorMetadata | list[SensorMetadata] = Field(
        None,
        description="List of sensors hosted on the platform",
        json_schema_extra={
            "example": [extract(SensorMetadata)],
            "uri": "http://www.w3.org/ns/sosa/hosts",  # was AGIMAGE + "hasSensor"
            # "parent_uri": "http://www.w3.org/ns/sosa/hosts",
            "cardinalityMax": "*",
        },
    )

    @field_validator("hasSensor", mode="before")
    @classmethod
    def normalize_sensors_to_list(cls, v):
        """Ensure it is always a list."""
        if isinstance(v, list):
            return v
        return [v]

    @model_validator(mode="after")
    def set_id(self):
        if self.platformID is None:
            self.platformID = f"{self.platformName}_{uuid.uuid4()}"
        return self
