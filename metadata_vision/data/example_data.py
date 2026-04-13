"""
Sample/dummy data for testing and examples.

This module provides realistic example metadata instances for all metadata classes.
"""

import datetime
from metadata_vision.schemas.images import ImageMetadata
from metadata_vision.schemas.field import FieldMetadata
from metadata_vision.schemas.plot import PlotMetadata
from metadata_vision.schemas.plotstate import PlotStateMetadata, WeatherConditions, SurfaceLayer
from metadata_vision.schemas.camera import CameraMetadata, SpectralBand
from metadata_vision.schemas.crop import CropMetadata, CropHandling, CropTiming, CropTimingType
from metadata_vision.schemas.platform import PlatformMetadata, SensorMetadata
from metadata_vision.schemas.agent import AgentMetadata
from metadata_vision.schemas.dataset import DatasetMetadata


def create_dummy_data():
    """
    Create and return all dummy metadata instances.

    Returns:
        dict: Dictionary containing all dummy objects
    """

    # Create camera
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
    )

    # Create sensor with camera
    dummy_sensor = SensorMetadata(hasCamera=dummy_camera)

    # Create platform with sensor
    dummy_platform = PlatformMetadata(
        platformName="demo_platform1",
        platformID="demo_platform1_65b8590f-463b-4b40-8ab1-cb6984d49035",  # hardcode for unneccesary git changes
        hasSensor=dummy_sensor,
    )

    # Create crop
    dummy_crop = CropMetadata(
        cropName="cucumber",
        cropCode="CUMSA",
        cropCultivar="Hi Power",
        cropHandling=CropHandling.CROP_OBSERVATION,
        cropGrowthStageMin=65,
        cropGrowthStageMax=85,
        cropTiming=CropTiming(
            type=CropTimingType.PLANTING_DATE, date=datetime.datetime(2026, 1, 10)
        ),
    )

    plotName = "plot123"
    dummy_plotstate = PlotStateMetadata(
        stateName=plotName + "_state_1",
        stateID=plotName + "_state_1_12345678-c9fb-4cf7-8766-c28077b2c035",
        validFrom=datetime.datetime(2026, 8, 18),
        validTo=datetime.datetime(2026, 8, 20),
        hasCrop=[dummy_crop],
        soilType=None,  # SoilType.CLAY,
        weatherConditions=WeatherConditions.SUNNY,
        surfaceLayer=[SurfaceLayer.WHITE_CANVAS, SurfaceLayer.LOOSE_LEAVES],
    )

    # Create plot with crop
    dummy_plot = PlotMetadata(
        plotName=plotName,
        plotID="plot123_7415bf0b-c9fb-4cf7-8766-c28077b2c035",  # hardcode for unneccesary git changes
        bbox=["POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))"],
        hasPlotState=[dummy_plotstate],
    )

    # Create fields
    dummy_field = FieldMetadata(
        fieldName="field_001",
        fieldID="field_001_d35cce35-513d-4902-b392-1657c0d8a64d",  # hardcode for unneccesary git changes
        bbox="POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
        hasPlot=dummy_plot,
    )

    dummy_field2 = FieldMetadata(
        fieldName="field_002",
        fieldID="field_002_362f6026-28a0-4bc0-b8b5-a3ef9c81ca7e",  # hardcode for unneccesary git changes
        bbox="POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
        hasPlot=dummy_plot,
    )

    # Create image
    dummy_image = ImageMetadata(
        imageName="20251014T093010Z857_camid9_trigger1000_rgb.png",
        imageTimestamp=datetime.datetime(2025, 10, 14, 9, 30, 10, 857000),
        cameraID=dummy_camera.cameraID,
        fieldID=dummy_field.fieldID,
        plotID=dummy_plot.plotID,
        platformID=dummy_platform.platformID,
        imageNumber=1000,
        imageXYZ=[1.0, 2.0, 2.5],
        imageQuaternionXYZW=[0.0, 0.0, 0.0, 1.0],
        baseXYZ=[0.0, 0.0, 0.0],
        baseQuaternionXYZW=[0.0, 0.0, 0.0, 1.0],
    )

    # Create agent
    dummy_agent = AgentMetadata(name="Jane Doe")
    dummy_contributor = AgentMetadata(name="John Doe")

    # Create dataset
    dummy_dataset = DatasetMetadata(
        title="Cucumber phenotyping dataset",
        description=(
            "This dataset is recorded in a commercial cucumber greenhouse. "
            "Four classes are annotated: cucumbers, leaves, open flower and closed flower."
        ),
        identifier="3742355900_agros2_komkommer",
        creator=dummy_agent,
        contributor=dummy_contributor,
        accessURL="https://example.org/datasets/cucumber-phenotyping",
        version="1.0",
        issued=datetime.datetime(2025, 10, 14, 9, 30, 0),
        modified=datetime.datetime(2025, 10, 14, 9, 30, 0),
        startDate=datetime.datetime(2025, 10, 14, 9, 30, 0),
        endDate=datetime.datetime(2025, 10, 14, 17, 30, 0),
        license="CC BY-NC-SA",
        numberOfImages=15000,
        numberOfAnnotatedImages=12500,
        hasField=[dummy_field, dummy_field2],
        hasPlatform=dummy_platform,
        hasImage=dummy_image,
    )

    return {
        "camera": dummy_camera,
        "sensor": dummy_sensor,
        "platform": dummy_platform,
        "crop": dummy_crop,
        "plot": dummy_plot,
        "plotstate": dummy_plotstate,
        "field": dummy_field,
        "field2": dummy_field2,
        "image": dummy_image,
        "agent": dummy_agent,
        "contributor": dummy_contributor,
        "dataset": dummy_dataset,
    }


# Create singleton instances
_data = create_dummy_data()

# Export individual objects for convenience
dummy_camera = _data["camera"]
dummy_sensor = _data["sensor"]
dummy_platform = _data["platform"]
dummy_crop = _data["crop"]
dummy_plot = _data["plot"]
dummy_plotstate = _data["plotstate"]
dummy_field = _data["field"]
dummy_field2 = _data["field2"]
dummy_image = _data["image"]
dummy_agent = _data["agent"]
dummy_contributor = _data["contributor"]
dummy_dataset = _data["dataset"]

__all__ = [
    "create_dummy_data",
    "dummy_camera",
    "dummy_sensor",
    "dummy_platform",
    "dummy_crop",
    "dummy_plot",
    "dummy_plotstate",
    "dummy_field",
    "dummy_field2",
    "dummy_image",
    "dummy_agent",
    "dummy_contributor",
    "dummy_dataset",
]
