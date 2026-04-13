import datetime
from agri_image_meta.schemas.camera import CameraMetadata, SpectralBand
from agri_image_meta.schemas.crop import CropMetadata, CropHandling
from agri_image_meta.schemas.plot import PlotMetadata
from agri_image_meta.schemas.field import FieldMetadata
from agri_image_meta.schemas.images import ImageMetadata
from agri_image_meta.schemas.platform import PlatformMetadata, SensorMetadata
from agri_image_meta.schemas.agent import AgentMetadata
from agri_image_meta.schemas.dataset import DatasetMetadata
from agri_image_meta.data.example_data import (
    create_dummy_data,
    dummy_camera,
    dummy_sensor,
    dummy_platform,
    dummy_crop,
    dummy_plot,
    dummy_field,
    dummy_field2,
    dummy_image,
    dummy_agent,
    dummy_contributor,
    dummy_dataset,
)

"""
Tests for the example_data module.

This module tests the create_dummy_data function and all exported dummy objects.
"""


class TestCreateDummyData:
    """Tests for the create_dummy_data function."""

    def test_create_dummy_data_returns_dict(self):
        """Test that create_dummy_data returns a dictionary."""
        data = create_dummy_data()
        assert isinstance(data, dict)

    def test_create_dummy_data_has_all_keys(self):
        """Test that create_dummy_data returns all required keys."""
        data = create_dummy_data()
        expected_keys = {
            "camera",
            "sensor",
            "platform",
            "crop",
            "plot",
            "plotstate",
            "field",
            "field2",
            "image",
            "agent",
            "contributor",
            "dataset",
        }
        assert set(data.keys()) == expected_keys

    def test_create_dummy_data_camera(self):
        """Test that create_dummy_data creates valid CameraMetadata."""
        data = create_dummy_data()
        camera = data["camera"]

        assert isinstance(camera, CameraMetadata)
        assert camera.cameraName == "camid050"
        assert camera.cameraID == "4110035082"
        assert camera.cameraModel == "IDS GV-5280FA-C-HQ Rev 1.2"
        assert camera.maxPixelX == 2464
        assert camera.maxPixelY == 2056
        assert camera.pixelSize == 4.39
        assert camera.focalLength == 6.0
        assert camera.subjectDistance == 400.0
        assert camera.spectralBand == SpectralBand.RGB

    def test_create_dummy_data_sensor(self):
        """Test that create_dummy_data creates valid SensorMetadata."""
        data = create_dummy_data()
        sensor = data["sensor"]
        print(sensor)

        assert isinstance(sensor, SensorMetadata)
        assert isinstance(sensor.hasCamera[0], CameraMetadata)
        assert sensor.hasCamera[0].cameraID == "4110035082"

    def test_create_dummy_data_platform(self):
        """Test that create_dummy_data creates valid PlatformMetadata."""
        data = create_dummy_data()
        platform = data["platform"]

        assert isinstance(platform, PlatformMetadata)
        assert platform.platformName == "demo_platform1"
        assert isinstance(platform.hasSensor[0], SensorMetadata)

    def test_create_dummy_data_crop(self):
        """Test that create_dummy_data creates valid CropMetadata."""
        data = create_dummy_data()
        crop = data["crop"]

        assert isinstance(crop, CropMetadata)
        assert crop.cropName == "cucumber"
        assert crop.cropCode == "CUMSA"
        assert crop.cropCultivar == "Hi Power"
        assert crop.cropHandling == CropHandling.CROP_OBSERVATION

    def test_create_dummy_data_plot(self):
        """Test that create_dummy_data creates valid PlotMetadata."""
        data = create_dummy_data()
        plot = data["plot"]

        assert isinstance(plot, PlotMetadata)
        assert plot.plotName == "plot123"
        assert isinstance(plot.hasPlotState, list)
        assert len(plot.hasPlotState[0].hasCrop) > 0
        assert isinstance(plot.hasPlotState[0].hasCrop[0], CropMetadata)

    def test_create_dummy_data_field(self):
        """Test that create_dummy_data creates valid FieldMetadata."""
        data = create_dummy_data()
        field = data["field"]

        assert isinstance(field, FieldMetadata)
        assert field.fieldName == "field_001"
        assert isinstance(field.hasPlot, PlotMetadata)

    def test_create_dummy_data_field2(self):
        """Test that create_dummy_data creates valid second FieldMetadata."""
        data = create_dummy_data()
        field2 = data["field2"]

        assert isinstance(field2, FieldMetadata)
        assert field2.fieldName == "field_002"
        assert isinstance(field2.hasPlot, PlotMetadata)

    def test_create_dummy_data_image(self):
        """Test that create_dummy_data creates valid ImageMetadata."""
        data = create_dummy_data()
        image = data["image"]

        assert isinstance(image, ImageMetadata)
        assert image.imageName == "20251014T093010Z857_camid9_trigger1000_rgb.png"
        assert isinstance(image.imageTimestamp, datetime.datetime)
        assert image.imageNumber == 1000
        assert image.imageXYZ == [1.0, 2.0, 2.5]
        assert image.imageQuaternionXYZW == [0.0, 0.0, 0.0, 1.0]
        assert image.baseXYZ == [0.0, 0.0, 0.0]
        assert image.baseQuaternionXYZW == [0.0, 0.0, 0.0, 1.0]

    def test_create_dummy_data_agent(self):
        """Test that create_dummy_data creates valid AgentMetadata."""
        data = create_dummy_data()
        agent = data["agent"]

        assert isinstance(agent, AgentMetadata)
        assert agent.name == "Jane Doe"

    def test_create_dummy_data_contributor(self):
        """Test that create_dummy_data creates valid contributor AgentMetadata."""
        data = create_dummy_data()
        contributor = data["contributor"]

        assert isinstance(contributor, AgentMetadata)
        assert contributor.name == "John Doe"

    def test_create_dummy_data_dataset(self):
        """Test that create_dummy_data creates valid DatasetMetadata."""
        data = create_dummy_data()
        dataset = data["dataset"]

        assert isinstance(dataset, DatasetMetadata)
        assert dataset.title == "Cucumber phenotyping dataset"
        assert dataset.identifier == "3742355900_agros2_komkommer"
        assert isinstance(dataset.creator, AgentMetadata)
        assert isinstance(dataset.contributor, AgentMetadata)
        assert dataset.version == "1.0"
        assert dataset.numberOfImages == 15000
        assert dataset.numberOfAnnotatedImages == 12500
        assert isinstance(dataset.hasField, list)
        assert len(dataset.hasField) == 2
        assert isinstance(dataset.hasPlatform, PlatformMetadata)
        assert isinstance(dataset.hasImage, ImageMetadata)


class TestDummyObjects:
    """Tests for the exported dummy objects."""

    def test_dummy_camera_is_valid(self):
        """Test that dummy_camera is a valid CameraMetadata instance."""
        assert isinstance(dummy_camera, CameraMetadata)
        assert dummy_camera.cameraName == "camid050"

    def test_dummy_sensor_is_valid(self):
        """Test that dummy_sensor is a valid SensorMetadata instance."""
        assert isinstance(dummy_sensor, SensorMetadata)
        assert isinstance(dummy_sensor.hasCamera[0], CameraMetadata)

    def test_dummy_platform_is_valid(self):
        """Test that dummy_platform is a valid PlatformMetadata instance."""
        assert isinstance(dummy_platform, PlatformMetadata)
        assert dummy_platform.platformName == "demo_platform1"

    def test_dummy_crop_is_valid(self):
        """Test that dummy_crop is a valid CropMetadata instance."""
        assert isinstance(dummy_crop, CropMetadata)
        assert dummy_crop.cropName == "cucumber"

    def test_dummy_plot_is_valid(self):
        """Test that dummy_plot is a valid PlotMetadata instance."""
        assert isinstance(dummy_plot, PlotMetadata)
        assert dummy_plot.plotName == "plot123"

    def test_dummy_field_is_valid(self):
        """Test that dummy_field is a valid FieldMetadata instance."""
        assert isinstance(dummy_field, FieldMetadata)
        assert dummy_field.fieldName == "field_001"

    def test_dummy_field2_is_valid(self):
        """Test that dummy_field2 is a valid FieldMetadata instance."""
        assert isinstance(dummy_field2, FieldMetadata)
        assert dummy_field2.fieldName == "field_002"

    def test_dummy_image_is_valid(self):
        """Test that dummy_image is a valid ImageMetadata instance."""
        assert isinstance(dummy_image, ImageMetadata)
        assert dummy_image.imageName == "20251014T093010Z857_camid9_trigger1000_rgb.png"

    def test_dummy_agent_is_valid(self):
        """Test that dummy_agent is a valid AgentMetadata instance."""
        assert isinstance(dummy_agent, AgentMetadata)
        assert dummy_agent.name == "Jane Doe"

    def test_dummy_contributor_is_valid(self):
        """Test that dummy_contributor is a valid AgentMetadata instance."""
        assert isinstance(dummy_contributor, AgentMetadata)
        assert dummy_contributor.name == "John Doe"

    def test_dummy_dataset_is_valid(self):
        """Test that dummy_dataset is a valid DatasetMetadata instance."""
        assert isinstance(dummy_dataset, DatasetMetadata)
        assert dummy_dataset.title == "Cucumber phenotyping dataset"

    def test_dummy_objects_consistency(self):
        """Test that all dummy objects are consistent with each other."""
        # Dataset should reference the fields, platform, and image
        assert dummy_dataset.hasField[0].fieldName == dummy_field.fieldName
        assert dummy_dataset.hasField[1].fieldName == dummy_field2.fieldName
        assert dummy_dataset.hasPlatform.platformName == dummy_platform.platformName
        assert dummy_dataset.hasImage.imageName == dummy_image.imageName

    def test_dummy_objects_are_singletons(self):
        """Test that dummy objects are singleton instances."""
        data = create_dummy_data()
        # Create new data and compare with exported objects
        assert dummy_camera.cameraID == data["camera"].cameraID
        assert dummy_platform.platformName == data["platform"].platformName
        assert dummy_dataset.identifier == data["dataset"].identifier
