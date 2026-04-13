"""
Example for metadata for sensors like cameras
"""

from enum import Enum
from typing import List, Optional

from pydantic import Field, field_validator
import sys

sys.path.append("")
from agri_image_meta.generate_example_json import extract
from agri_image_meta.schemas.base import RDFModel
from agri_image_meta.utils.namespaces import AGIMAGE, EXIF
# better -> https://exiftool.org/TagNames/EXIF.html
# https://exiv2.org/tags.html

## online
# https://www.w3.org/2003/12/exif/
#


class SpectralBand(str, Enum):
    """Spectral band captured by the camera."""

    ## name is lower case for consistency
    RGB = "rgb"
    NIR = "nir"
    MONO = "mono"
    THERMAL = "thermal"
    MULTISPECTRAL = "multispectral"  ## multi or hyperspectral

    ## for 3D camera's you might want to specifiy stereo
    DEPTH = "depth"  ## multi or hyperspectral


class LightSource(Enum):
    """Light source types based on EXIF specification.
    https://exiftool.org/TagNames/EXIF.html#LightSource
    """

    UNKNOWN = 0
    DAYLIGHT = 1
    FLUORESCENT = 2
    TUNGSTEN = 3
    FLASH = 4
    FINE_WEATHER = 9
    CLOUDY = 10
    SHADE = 11
    DAYLIGHT_FLUORESCENT = 12
    DAY_WHITE_FLUORESCENT = 13
    COOL_WHITE_FLUORESCENT = 14
    WHITE_FLUORESCENT = 15
    WARM_WHITE_FLUORESCENT = 16
    STANDARD_LIGHT_A = 17
    STANDARD_LIGHT_B = 18
    STANDARD_LIGHT_C = 19
    D55 = 20
    D65 = 21
    D75 = 22
    D50 = 23
    ISO_STUDIO_TUNGSTEN = 24
    OTHER = 255


class DistortionModelName(str, Enum):
    """Distortion model names for camera calibration."""

    RADIAL = "radial"
    TANGENTIAL = "tangential"
    FISHEYE = "fisheye"
    THIN_PRISM = "thin_prism"
    BROWN_CONRADY = "brown_conrady"


class DistortionModel(RDFModel):
    """Distortion model with name and optional model string."""

    rdf_type: str = "agimage:distortionModel"

    name: DistortionModelName = Field(
        ...,
        description="Name/type of the distortion model",
        json_schema_extra={
            "uri": AGIMAGE + "distortionModelName",
            "example": DistortionModelName.BROWN_CONRADY.name,
        },
    )
    coefficients: Optional[list[float]] = Field(
        None,
        description="list of coefficients",
        json_schema_extra={
            "uri": AGIMAGE + "distortionModelCoefficients",
            "example": [0.0, 0.0, 0.0, 0.0, 0.0],
        },
    )


class CameraMetadata(RDFModel):
    """
    Metadata model for camera/sensor-related information.
    """

    rdf_type: str = "agimage:Camera"
    # rdf_type: str = "sosa:Sensor"

    cameraName: str = Field(
        ...,
        description="Simple identifier for the camera",
        json_schema_extra={
            "example": "0010",
            # "uri": "http://purl.org/dc/terms/title",
            "uri": AGIMAGE + "cameraName",
            "parent_uri": "http://purl.org/dc/terms/title",
        },
    )

    cameraID: str = Field(
        ...,
        description="Unique ID/serial number of the camera",
        json_schema_extra={
            "example": "4110035082",
            # "@id": "http://ns.adobe.com/exif/1.0/SerialNumber",
            "uri": EXIF + "SerialNumber",
            # "@tag": "Exif.Image.SerialNumber",
        },
    )

    cameraModel: str = Field(
        ...,
        description="Manufacture and camera type",
        json_schema_extra={
            "example": "IDS GV-5280FA-C-HQ Rev 1.2",  ## IDS example
            # "@id": "http://ns.adobe.com/exif/1.0/Model",
            "uri": EXIF + "Model",
            "@tag": "Exif.Image.Model",
            "@owl": "exif:model\n\t"
            "a owl:DatatypeProperty ;\n\t"
            "rdfs:domain ex:Camera ;\n\t"
            "rdfs:range xsd:string .",
        },
    )

    cameraLensModel: str = Field(
        ...,
        description="Model name/number of the lens",
        json_schema_extra={
            "example": "IDS 6mm 1:2.8 C2/3",
            "uri": EXIF + "LensModel",
            "@tag": "Exif.Image.LensModel",
            "@owl": "exif:PixelXDimension\n\t"
            "a owl:DatatypeProperty ;\n\t"
            "rdfs:domain ex:Camera ;\n\t"
            "rdfs:range xsd:integer .",
        },
    )

    # Not exactly the same as EXIF because of Max pixel instead of actual image reosl
    maxPixelX: int = Field(
        ...,
        description="Maximum number of pixels of sensor in X (horizontal) direction, "
        "NOT actual image size (downscaling/binning)",
        json_schema_extra={
            "example": 2464,
            "uri": EXIF + "PixelXDimension",
            "@tag": "Exif.Image.PixelXDimension",
        },
    )

    maxPixelY: int = Field(
        ...,
        description="Maximum number of pixels of sensor in Y (vertical) direction,"
        "NOT actual image size (downscaling/binning)",
        json_schema_extra={
            "example": 2056,
            "uri": EXIF + "PixelYDimension",
            "@tag": "Exif.Image.PixelYDimension",
        },
    )

    pixelSize: float = Field(
        ...,
        description="Pixel size of sensor in [um]",
        json_schema_extra={
            "example": 3.45,
            "uri": AGIMAGE + "pixelSize",
            # "uri": EXIF+"FocalLength",
            "unit": "http://qudt.org/vocab/unit/MicroM",
            "@owl": "ex:pixelSize\n\t"
            "a owl:DatatypeProperty ;\n\t"
            "rdfs:domain ex:Camera ;\n\t"
            "rdfs:range xsd:decimal ;\n\t"
            "qudt:unit unit:MicroM .",
        },
    )

    # Optics
    focalLength: float = Field(
        ...,
        description="Focal length of the lens in [mm]",
        json_schema_extra={
            "example": 6.0,
            # "@id": "http://ns.adobe.com/exif/1.0/FocalLength",
            "uri": EXIF + "FocalLength",
            "@tag": "Exif.Photo.FocalLength",
            "unit": "http://qudt.org/vocab/unit/MilliM",
        },
    )

    subjectDistance: float = Field(
        ...,
        # meters because of Exif standard
        description="Distance from camera to subject in meters [m]",
        json_schema_extra={
            "example": 400.0,
            # "@id": "http://ns.adobe.com/exif/1.0/SubjectDistance",
            "uri": EXIF + "SubjectDistance",
            "@tag": "Exif.Image.SubjectDistance",
            "unit": "https://qudt.org/vocab/unit/M",
        },
    )

    # Image properties
    spectralBand: SpectralBand = Field(
        SpectralBand.RGB,
        description="Spectral band captured by the camera (e.g., RGB, BGR, NIR, Thermal)",
        json_schema_extra={
            "example": SpectralBand.RGB.name,
            # "@tag": "ex.spectralBand",
            "uri": "http://sweetontology.net/propOrdinal/SpectralBand",
        },
    )

    cameraBox: Optional[bool] = Field(
        None,
        # meters because of Exif standard
        description="Is the product shielded with a camera box [True, False]",
        json_schema_extra={
            "example": True,
            "uri": AGIMAGE + "cameraBox",
            # "@tag": "Exif.Image.SubjectDistance",
        },
    )

    lightSource: Optional[LightSource] = Field(
        None,
        # meters because of Exif standard
        description="Indicates the Lightsource in agreement with EXIF standaard",
        json_schema_extra={
            "example": LightSource.FLASH.name,
            "@tag": "Exif.Image.LightSource",
            "uri": EXIF + "LightSource",
        },
    )

    lightModel: Optional[str] = Field(
        None,
        # meters because of Exif standard
        description="If additional light is used, indicate model",
        json_schema_extra={
            "example": "Luxalight LF-24-5700K-24.2X16-PU",
            "uri": AGIMAGE + "lightModel",
            # "uri": EXIF+"Model"
        },
    )

    def model_dump(self, **kwargs):
        data = super().model_dump(**kwargs)
        # if "spectral_band" in data and isinstance(data["spectral_band"], Enum):
        #     data["spectral_band"] = self.spectral_band.name
        return data

    # Calibration
    intrinsics: Optional[List[List[float]]] = Field(
        default=None,
        description="3x3 camera Matrix K=[[fx, s, cx],[0, fy, cy],[0,0,1]],"
        "corresponding with images recorded NOT MaxPixelX",
        json_schema_extra={
            "@id": "https://docs.opencv.org/4.x/d9/intrind0c/group__calib3d.html",
            "uri": AGIMAGE + "intrinsics",
        },
    )

    hasDistortionModel: Optional[DistortionModel] = Field(
        default=None,
        description="Distortion model used. OPENCV uses dist_coeffs =[k1,k2,p1,p2,k3,k4,k5,k6],"
        "with k4 , k5, k6 optional. K123 = radial distortion, p12 tangetial distortion, "
        "k456 higher order radial distortion coefficicients for complex distortion",
        json_schema_extra={
            "@id": "https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html",
            "uri": AGIMAGE + "hasDistortionModel",
            "example": extract(DistortionModel),
        },
    )

    # distortionCoefficients: Optional[List[float]] = Field(
    #     default=None,
    #     description="Distortion coefficients corresponding to the distortion model," \
    #     "opencv: 4 to 8 coefficients"
    #     "[k1, k2, p1, p2, k3, k4, k5, k6]",
    #     json_schema_extra={
    #         "@id": "https://docs.opencv.org/4.x/d9/d0c/group__calib3d.html"
    #     },
    # )

    # --------------------
    # Validators
    # --------------------
    @field_validator("intrinsics")
    @classmethod
    def validate_intrinsics(cls, v):
        """ "Validate intrinsics as 3x3 matrix"""
        if v is None:
            return v
        if len(v) != 3 or any(len(row) != 3 for row in v):
            raise ValueError("cameraIntrinsics must be a 3x3 matrix")
        return v

    # @field_validator("distortionCoefficients")
    # @classmethod
    # def validate_distortion(cls, v, info: ValidationInfo):
    #     """"Validate distortion coefficients"""
    #     if v is None:
    #         return v

    #     model = info.data.get("distortionModel")
    #     if model == "OPENCV":
    #         if not 4 <= len(v) <= 8:
    #             raise ValueError("OPENCV distortion expects 4–8 coefficients")
    #     return v


def get_value_by_cameraName(camera_list: List[CameraMetadata], cameraName: str, field_name: str):
    """
    Utility function to get a specific field value from a list of CameraMetadata
    based on the cameraID.

    Args:
        camera_list (List[CameraMetadata]): List of CameraMetadata instances.
        cameraID (str): The cameraID to search for.
        field_name (str): The field name whose value is to be retrieved.

    Returns:
        The value of the specified field for the matching cameraID, or None if not found.
    """
    for camera in camera_list:
        if camera.cameraName == cameraName:
            return getattr(camera, field_name, None)
    return None


if __name__ == "__main__":
    # print(json.dumps(CameraMetadata.model_json_schema(), indent=2))

    # Export fields with @owl annotation
    print("\n--- Fields with @owl annotation ---")
    schema = CameraMetadata.model_json_schema()

    for field_name, field_info in schema.get("properties", {}).items():
        if "@owl" in field_info:
            print(f"\n{field_name}:")
            print(field_info["@owl"])
    # Create a dummy example
    dummy_camera = CameraMetadata(
        cameraName="camid050",
        cameraID="4110035082",
        cameraModel="IDS GV-5280FA-C-HQ Rev 1.2",
        cameraLensModel="IDS 6mm 1:2.8 C2/3",
        maxPixelX=2464,
        maxPixelY=2056,
        pixelSize=4.39,
        focalLength=6.0,
        subjectDistance=400.0,
        spectralBand=SpectralBand.RGB,
        # intrinsics=None,
        # distortionModel=None,
        # distortionCoefficients=None
    )
    a = [dummy_camera]
    print(get_value_by_cameraName(a, "camid050", "spectralBand"))

    # print("Camera Metadata Example:")
    # print(f"Camera ID: {dummy_camera.cameraID}")
    # print(f"Model: {dummy_camera.camera_model}")
    # print(f"Resolution: {dummy_camera.max_pixel_x}x{dummy_camera.max_pixel_y}")
    # print(f"Focal Length: {dummy_camera.focal_length_mm}mm")
    # print(f"\nCamera Matrix:\n{dummy_camera.intrinsics}")
    # print(f"\nDistortion Coefficients:\n{dummy_camera.distortion_coefficients}")
