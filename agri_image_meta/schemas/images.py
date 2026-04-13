"""Pydantic model for image metadata captured by cameras on machines/platforms.
This module defines the ImageMetadata class which stores essential information about
captured images including timestamp, camera/machine identifiers, position, and orientation
data in both camera-relative and global reference frames."""

import json
import uuid
import datetime
from pathlib import Path
from pydantic import Field, field_validator, model_validator
from typing import Optional, List
from agri_image_meta.utils.file_system import get_strptime
from agri_image_meta.utils.namespaces import AGIMAGE, EXIF
from agri_image_meta.schemas.base import RDFModel


class ImageMetadata(RDFModel):
    """
    Basic metadata for every image captured
    """

    rdf_type: str = "agimage:Image"

    # ---------------------
    # Image-specific fields
    # ---------------------
    imageName: str = Field(
        ...,
        description="Name of the image, follow the format: timestamp_camid_trigger_channel.png",
        json_schema_extra={
            "example": "20251014T093010Z857_camid9_trigger1000_rgb.png",
            "@tag": "ex:imageName",
            "uri": AGIMAGE + "imageName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    imagePath: Optional[str | Path] = Field(
        None,
        description="Full path of the image",
        json_schema_extra={
            "example": "/home/user001/datataset/20251014T093010Z857_camid9_trigger1000_rgb.png",
            "@tag": "ex:imageName",
            "uri": AGIMAGE + "imagePath",
            "parent_uri": "http://purl.org/dc/terms/identifier",
            # https://www.semanticdesktop.org/ontologies/2007/03/22/nfo/
        },
    )

    imageID: Optional[str] = Field(
        None,
        description="Unique identifier for the image based on image + uuid",
        json_schema_extra={
            "example": "20251014T093010Z857_camid9_trigger1000_rgb.png_0acbbe89-3058-4f62-a731-3fd3b42cfa04",
            "@tag": "ex:imageID",
            "uri": AGIMAGE + "imageID",
            "parent_uri": "http://purl.org/dc/terms/identifier",
        },
    )

    imageTimestamp: datetime.datetime | str = Field(
        ...,
        description="ISO-8601 timestamp of image (YYYYMMDDTHHMMSSZmilliseconds 20250917T134658Z)",
        json_schema_extra={
            "example": datetime.datetime(2025, 10, 14, 9, 30, 10, 857000),
            "uri": "http://www.w3.org/TR/xmlschema11-2/#dateTime",
        },
    )

    @field_validator("imageTimestamp", mode="before")
    @classmethod
    def validate_image_timestamp(cls, v):
        return get_strptime(v)

    # @classmethod
    # def convert_datetime_to_string(cls, v):
    #     """Datetime to string"""
    #     if isinstance(v, datetime.datetime):
    #         # Format: ISO8601 with milliseconds -> YYYYMMDDTHHMMSSZmilliseconds
    #         return v.strftime("%Y%m%dT%H%M%SZ") + str(v.microsecond // 1000)
    #     return v

    cameraID: str = Field(
        ...,
        description="Unique ID/serial number of the camera",
        json_schema_extra={
            "example": "4110035082",
            "uri": EXIF + "SerialNumber",
        },
    )

    fieldID: str = Field(
        ...,
        description="Identifier of the field where the image was captured",
        json_schema_extra={
            "example": "field_001_5de48942-0c39-411f-8f4a-756b0c20f7bb",
            "@tag": "ex:fieldID",
            "uri": AGIMAGE + "fieldID",
            # "uri": "http://purl.org/dc/terms/title",
        },
    )
    plotID: str = Field(
        ...,
        description="Identifier of the plot where the image was captured",
        json_schema_extra={
            "example": "plot123_448aadb7-b07d-498d-9301-2240533d849a",
            "@tag": "ex:plotID",
            "uri": AGIMAGE + "plotID",
        },
    )

    platformID: str = Field(
        ...,
        description="Identifier of the machine/platform that captured the image",
        json_schema_extra={
            "example": "demo_platform1_09cbf6ae-8dc1-43dc-96ef-4675b71039c3",
            "@tag": "ex:platformID",
            "uri": AGIMAGE + "platformID",
        },
    )

    exposureTime: Optional[float] = Field(
        None,
        description="Exposure time in seconds (Exif is also seconds)",
        json_schema_extra={
            "example": 0.01,
            "@tag": "Exif.Image.ExposureTime",
            "uri": "https://exiftool.org/TagNames/EXIF.html#ExposureTime",
            "unit": "https://qudt.org/vocab/unit/SEC",
        },
    )

    imageNumber: Optional[int] = Field(
        None,
        description="Image number, Exif.Image.ImageNumber",
        json_schema_extra={
            "example": 1000,
            "@tag": "Exif.Image.ImageNumber",
            "uri": "https://exiftool.org/TagNames/EXIF.html#ImageNumber",
        },
    )

    imageXYZ: Optional[List[float]] = Field(
        None,
        description="Camera location XYZ coordinates in meters relative to platform base",
        json_schema_extra={
            "example": [0.0, 0.0, 2.5],
            "@tag": "ex:imageXYZ",
            "uri": "http://purl.org/dc/terms/Location",
            # "uri": "https://w3id.org/agri-image/cameraLocation",
            "unit": "https://qudt.org/vocab/unit/M",
            "rdf_list": True,
        },
    )

    imageQuaternionXYZW: Optional[List[float]] = Field(
        None,
        description="Camera orientation as quaternion [x, y, z, w], relative to base "
        "assumes OPENCV camera coord. system",
        json_schema_extra={
            "example": [0.0, 0.0, 0.0, 1.0],
            "@tag": "ex:imageQuaternionXYZW",
            "uri": "https://dbpedia.org/page/Quaternion",
            # "uri": "https://w3id.org/agri-image/cameraOrientation",
            "rdf_list": True,
        },
    )

    imageGNSS: Optional[str] = Field(
        None,
        description="NMEA string (e.g., NMEA-GGA/GSV, NMEA-2000) of camera position",
        json_schema_extra={
            "@tag": "ex:imageGNSS",
            "example": "$GPGGA,172814.0,3723.46587704,N,12202.26957864,W,2,6,1.2,18.893,M,-25.669,M,2.0 0031*4F",
            "uri": "http://dbpedia.org/resource/NMEA_0183",
        },
    )

    ## Machine base info
    baseXYZ: Optional[List[float]] = Field(
        None,
        description="Platform base location XYZ coordinates in meters (global reference frame)",
        json_schema_extra={
            "example": [0.0, 0.0, 0.0],
            "@tag": "ex:baseXYZ",
            "uri": "http://purl.org/dc/terms/Location",
            # "uri": "https://w3id.org/agri-image/platformLocation",
            "unit": "https://qudt.org/vocab/unit/M",
            "rdf_list": True,
        },
    )
    baseQuaternionXYZW: List[float] = Field(
        ...,
        description="Machine base orientation as quaternion [x, y, z, w]  (global reference frame)",
        json_schema_extra={
            "example": [0.0, 0.0, 0.0, 1.0],
            "@tag": "ex:baseQuaternionXYZW",
            # "uri": "https://dbpedia.org/page/Quaternion",
            "uri": "https://w3id.org/agri-image/platformOrientation",
            "rdf_list": True,
        },
    )

    baseGNSS: Optional[str] = Field(
        None,
        description="NMEA string (e.g., NMEA-GGA/GSV, NMEA-2000) of machine base position",
        json_schema_extra={
            "@tag": "ex:baseGNSS",
            "example": "$GPGGA,172814.0,3723.46587704,N,12202.26957864,W,2,6,1.2,18.893,M,-25.669,M,2.0 0031*4F",
            "uri": "http://dbpedia.org/resource/NMEA_0183",
        },
    )

    @model_validator(mode="after")
    def set_id(self):
        if self.imageID is None:
            self.imageID = f"{self.imageName}_{uuid.uuid4()}"
        return self


if __name__ == "__main__":
    # Generate and print the JSON schema for ImageMetadata
    import json

    print(json.dumps(ImageMetadata.model_json_schema(), indent=4))
    dummy_image = ImageMetadata(
        imageName="20251014T093010Z857_camid9_trigger1000_rgb.png",
        imageTimestamp=datetime.datetime(2025, 10, 14, 9, 30, 10, 857000),
        cameraID="4110035082",
        fieldID="field_001_5de48942-0c39-411f-8f4a-756b0c20f7bb",
        plotID="plot123_448aadb7-b07d-498d-9301-2240533d849a",
        platformID="demo_platform1_09cbf6ae-8dc1-43dc-96ef-4675b71039c3",
        exposureTime=None,
        imageNumber=1000,
        imageXYZ=[1.0, 2.0, 2.5],
        imageQuaternionXYZW=[0.0, 0.0, 0.0, 1.0],
        imageGNSS="$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
        baseXYZ=[0.0, 0.0, 0.0],
        baseQuaternionXYZW=[0.0, 0.0, 0.0, 1.0],
        baseGNSS="$GPGGA,123519,4807.038,N,01131.000,E,1,08,0.9,545.4,M,46.9,M,,*47",
    )

    ##################### load image metadata and filter:
    # main_folder = Path(r"W:\PROJECTS\VisionRoboticsData\GARdata\new_format\3742355900_agros2_komkommer\datasets\raw_data\metadata_test\0107")
    # file_paths = main_folder.rglob("*metadata.json")
    # load_image_metadata_files(file_paths)
