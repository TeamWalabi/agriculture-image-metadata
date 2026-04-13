# platform_and_sensors.py


from pydantic import Field, field_validator
import sys

sys.path.append("")
from agri_image_meta.schemas.base import RDFModel
from agri_image_meta.schemas.camera import CameraMetadata
from agri_image_meta.generate_example_json import extract

from agri_image_meta.utils.namespaces import AGIMAGE


class SensorMetadata(RDFModel):
    """
    Metadata model for sensors/cameras mounted on a platform.
    https://www.w3.org/TR/vocab-ssn/#SOSASensor
    """

    # rdf_type: str = "agimage:Sensor"
    rdf_type: str = "sosa:Sensor"


    hasCamera: CameraMetadata | list[CameraMetadata] = Field(
        None,
        description="List of cameras associated with this sensor",
        json_schema_extra={
            "example": [extract(CameraMetadata)],
            "uri": AGIMAGE + "hasCamera",
            "cardinalityMax": "*",
        },
    )

    # ##TODO implement Lidar
    # hasLidar: LidarMetadata | list[LidarMetadata] = Field(
    #     None,
    #     description="List of cameras associated with this sensor",
    #     json_schema_extra={
    #         "example": [extract(LidarMetadata)],
    #         "uri": AGIMAGE+"hasLidar",
    #     },
    # )
    # ##TODO implement Lidar
    # hasGPS: GPSMetadata | list[GPSMetadata] = Field(
    #     None,
    #     description="List of cameras associated with this sensor",
    #     json_schema_extra={
    #         "example": [extract(GPSMetadata)],
    #         "uri": AGIMAGE+"hasGPS",
    #     },
    # )

    @field_validator("hasCamera", mode="before")
    @classmethod
    def normalize_cameras_to_list(cls, v):
        """Ensure it is always a list."""
        if isinstance(v, list):
            return v
        return [v]
