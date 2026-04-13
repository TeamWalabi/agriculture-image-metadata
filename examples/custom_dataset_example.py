"""
Sample to create your own custom_dataset yaml file
"""

import datetime
import json
from ruamel.yaml import YAML
from agri_image_meta.schemas.images import ImageMetadata
from agri_image_meta.schemas.field import FieldMetadata
from agri_image_meta.schemas.plot import PlotMetadata
from agri_image_meta.schemas.plotstate import (
    PlotStateMetadata,
    WeatherConditions,
    SurfaceLayer,
    SoilType,
)
from agri_image_meta.schemas.camera import CameraMetadata, SpectralBand
from agri_image_meta.schemas.crop import CropMetadata, CropHandling
from agri_image_meta.schemas.platform import PlatformMetadata, SensorMetadata
from agri_image_meta.schemas.agent import AgentMetadata
from agri_image_meta.schemas.dataset import DatasetMetadata
from agri_image_meta.utils.dataset_loading import load_dataset


# Create camera
dummy_camera = CameraMetadata(
    cameraName="camid050",
    cameraID="4110035082",
    cameraModel="IDS GV-5280FA-C-HQ Rev 1.2",
    cameraLensModel="IDS,12M23-C0628,6mm,2/3",
    maxPixelX=2464,
    maxPixelY=2056,
    pixelSize=3.45,
    focalLength=6.0,
    subjectDistance=400.0,
    spectralBand=SpectralBand.RGB,
)

# Create sensor with camera
dummy_sensor = SensorMetadata(hasCamera=dummy_camera)

# Create platform with sensor
dummy_platform = PlatformMetadata(platformName="demo_platform_1", hasSensor=dummy_sensor)

# Create crop
dummy_crop = CropMetadata(
    cropName="cucumber",
    cropCode="CUMSA",
    cropCultivar="Hi Power",
    cropHandling=CropHandling.CROP_OBSERVATION,
    cropGrowthStageMin=65,
    cropGrowthStageMax=85,
    # cropTiming=
)
plotName = "plot123"
dummy_plotstate = PlotStateMetadata(
    stateName=plotName + "_state_1",
    validFrom=datetime.datetime(2026, 8, 18),
    validTo=datetime.datetime(2026, 8, 20),
    hasCrop=[dummy_crop],
    hasWeed=None,
    soilType=SoilType.CLAY,
    weatherConditions=WeatherConditions.SUNNY,
    surfaceLayer=[SurfaceLayer.WHITE_CANVAS, SurfaceLayer.LOOSE_LEAVES],
)

# Create plot with crop
dummy_plot = PlotMetadata(
    plotName=plotName,
    bbox=["POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))"],
    hasPlotState=[dummy_plotstate],
)

# Create fields
dummy_field = FieldMetadata(
    fieldName="field_001",
    bbox="POLYGON((3.053 47.975, 7.24 47.975, 7.24 53.504, 3.053 53.504, 3.053 47.975))",
    hasPlot=dummy_plot,
)

dummy_field2 = FieldMetadata(
    fieldName="field_002",
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
    numberOfImages=-1,
    numberOfAnnotatedImages=-1,
    hasField=[dummy_field, dummy_field2],
    hasPlatform=dummy_platform,
    hasImage=dummy_image,
)

# Save dataset to JSON
with open("examples/your_custom_dataset.json", "w") as f:
    json.dump(dummy_dataset.model_dump(), f, indent=4, default=str)

# Save dataset to YAML
with open("examples/your_custom_dataset.yaml", "w") as f:
    YAML().dump(dummy_dataset.model_dump(), f)


loaded_from_json = load_dataset("examples/your_custom_dataset.json")
loaded_from_yaml = load_dataset("examples/your_custom_dataset.yaml")

print("\nComparing loaded objects with original...")
if loaded_from_json.title != dummy_dataset.title:
    raise ValueError("JSON loaded dataset title does not match original")
if loaded_from_yaml.title != dummy_dataset.title:
    raise ValueError("YAML loaded dataset title does not match original")
print("✓ All validations passed!")
