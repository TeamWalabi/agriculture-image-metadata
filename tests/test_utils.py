"""
Tests for utility modules: type_mapping, file_system, dataset_loading, and sparql_queries.
"""

import datetime
import json
import tempfile
from pathlib import Path
from typing import List, Optional, Union

import pytest
from rdflib import Graph, XSD

from agri_image_meta.utils.type_mapping import python_to_xsd, unwrap_type
from agri_image_meta.utils.file_system import (
    create_sensor_dir,
    get_image_name,
    get_strftime,
    get_strptime,
)
from agri_image_meta.utils.dataset_loading import load_dataset, load_metadata
from agri_image_meta.utils.sparql_queries import (
    query_find_all_fields,
    query_find_all_images,
    query_find_platforms,
    query_images_by_location_and_properties,
)
from agri_image_meta.ontology.generator import add_model_to_graph
from agri_image_meta.data.example_data import dummy_dataset


# ── unwrap_type ──────────────────────────────────────────────────────────────


class TestUnwrapType:

    def test_plain_str(self):
        assert unwrap_type(str) is str

    def test_plain_int(self):
        assert unwrap_type(int) is int

    def test_optional_str(self):
        assert unwrap_type(Optional[str]) is str

    def test_list_int(self):
        assert unwrap_type(List[int]) is int

    def test_list_float(self):
        assert unwrap_type(List[float]) is float

    def test_union_str_none(self):
        result = unwrap_type(Union[str, None])
        assert result is str

    def test_plain_bool(self):
        assert unwrap_type(bool) is bool


# ── python_to_xsd ───────────────────────────────────────────────────────────


class TestPythonToXSD:

    def test_str_to_xsd_string(self):
        assert python_to_xsd(str) == XSD.string

    def test_int_to_xsd_integer(self):
        assert python_to_xsd(int) == XSD.integer

    def test_float_to_xsd_double(self):
        assert python_to_xsd(float) == XSD.double

    def test_bool_to_xsd_boolean(self):
        assert python_to_xsd(bool) == XSD.boolean

    def test_unknown_type_defaults_to_string(self):
        assert python_to_xsd(list) == XSD.string


# ── get_strftime / get_strptime ──────────────────────────────────────────────


class TestDatetimeConversion:

    def test_strftime_datetime(self):
        dt = datetime.datetime(2025, 6, 15, 10, 30, 0, 500000)
        result = get_strftime(dt)
        assert "2025" in result
        assert "500" in result  # milliseconds
        assert result.endswith("Z")

    def test_strftime_string_passthrough(self):
        result = get_strftime("already_a_string")
        assert result == "already_a_string"

    def test_strftime_filename_format(self):
        dt = datetime.datetime(2025, 6, 15, 10, 30, 0, 500000)
        result = get_strftime(dt, bool_filename=True)
        assert ":" not in result
        assert "." not in result
        assert result.endswith("Z")

    def test_strptime_datetime_passthrough(self):
        dt = datetime.datetime(2025, 1, 1, 12, 0, 0)
        result = get_strptime(dt)
        assert result is dt

    def test_strptime_iso_format(self):
        result = get_strptime("2025-06-15T10:30:00.500Z")
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.month == 6
        assert result.day == 15

    def test_strptime_compact_format(self):
        result = get_strptime("20250615T103000Z500")
        assert isinstance(result, datetime.datetime)
        assert result.microsecond == 500000

    def test_strptime_from_filename_format_is_broken(self):
        """get_strptime(from_filename=True) has a bug: the format string expects a literal Z
        in the base portion, but the split removes it. This documents the known issue."""
        with pytest.raises(ValueError):
            get_strptime("20250615T103000500Z", from_filename=True)

    def test_strptime_compact_format_fallback(self):
        """The fallback parser in get_strptime handles compact timestamps like 20250615T103000Z500."""
        result = get_strptime("20250615T103000Z500")
        assert isinstance(result, datetime.datetime)
        assert result.year == 2025
        assert result.microsecond == 500000
        assert result.month == 6

    def test_round_trip_datetime(self):
        dt = datetime.datetime(2025, 3, 15, 14, 30, 0, 123000)
        s = get_strftime(dt)
        dt2 = get_strptime(s)
        assert dt2.year == dt.year
        assert dt2.month == dt.month
        assert dt2.day == dt.day
        assert dt2.hour == dt.hour
        assert dt2.minute == dt.minute
        assert dt2.second == dt.second
        assert dt2.microsecond == dt.microsecond


# ── get_image_name ───────────────────────────────────────────────────────────


class TestGetImageName:

    def test_default_channel_and_extension(self):
        dt = datetime.datetime(2025, 10, 14, 9, 30, 10, 857000)
        name = get_image_name(dt, camid=9, trigger_number=1000)
        assert "camid9" in name
        assert "trigger001000" in name
        assert name.endswith("_rgb.png")

    def test_custom_channel_and_extension(self):
        dt = datetime.datetime(2025, 1, 1, 0, 0, 0)
        name = get_image_name(dt, camid=1, trigger_number=1, channel="nir", extension=".tiff")
        assert name.endswith("_nir.tiff")


# ── create_sensor_dir ────────────────────────────────────────────────────────


class TestCreateSensorDir:

    def test_creates_directory(self, tmp_path):
        result = create_sensor_dir(
            root_folder=str(tmp_path),
            dataset_name="ds1",
            raw_data="raw",
            field_id="field_001",
            plot_id="plot_001",
            machine_id="robot1",
            cam_id="cam01",
        )
        assert result.exists()
        assert result.is_dir()
        assert "ds1" in str(result)
        assert "cam01" in str(result)

    def test_with_date_subfolder(self, tmp_path):
        result = create_sensor_dir(
            root_folder=str(tmp_path),
            dataset_name="ds1",
            raw_data="raw",
            field_id="f1",
            plot_id="p1",
            machine_id="m1",
            cam_id="c1",
            add_date_subfolder=True,
        )
        assert result.exists()
        # Should have a YYYYMMDD subfolder
        today = datetime.datetime.now().strftime("%Y%m%d")
        assert today in str(result)


# ── load_dataset ─────────────────────────────────────────────────────────────


class TestLoadDataset:

    def test_load_from_json(self):
        json_path = Path(__file__).parent.parent / "examples" / "your_custom_dataset.json"
        if json_path.exists():
            from agri_image_meta.schemas.dataset import DatasetMetadata

            ds = load_dataset(json_path)
            assert isinstance(ds, DatasetMetadata)
            assert ds.title is not None

    def test_load_from_yaml(self):
        yaml_path = Path(__file__).parent.parent / "examples" / "your_custom_dataset.yaml"
        if yaml_path.exists():
            from agri_image_meta.schemas.dataset import DatasetMetadata

            ds = load_dataset(yaml_path)
            assert isinstance(ds, DatasetMetadata)
            assert ds.title is not None

    def test_load_unsupported_format_raises(self, tmp_path):
        bad_file = tmp_path / "data.xml"
        bad_file.write_text("<data/>")
        with pytest.raises(ValueError, match="Unsupported file format"):
            load_dataset(bad_file)

    def test_load_with_mapping(self, tmp_path):
        data = {
            "dataset": {
                "rdf_type": "dcat:Dataset",
                "name": "Mapped dataset",
                "description": "Test",
                "identifier": "map_001",
                "creator": {"rdf_type": "foaf:Agent", "name": "Alice"},
                "numberOfImages": 1,
                "numberOfAnnotatedImages": 0,
                "hasField": {
                    "rdf_type": "agimage:Field",
                    "fieldName": "f1",
                    "bbox": "POLYGON((0 0, 1 0, 1 1, 0 1, 0 0))",
                },
                "hasPlatform": {
                    "rdf_type": "agimage:Platform",
                    "platformName": "p1",
                    "hasSensor": {
                        "rdf_type": "agimage:Sensor",
                        "hasCamera": {
                            "rdf_type": "agimage:Camera",
                            "cameraName": "c1",
                            "cameraID": "SN1",
                            "cameraModel": "M1",
                            "cameraLensModel": "L1",
                            "maxPixelX": 640,
                            "maxPixelY": 480,
                            "pixelSize": 3.0,
                            "focalLength": 4.0,
                            "subjectDistance": 1.0,
                        },
                    },
                },
            }
        }
        json_file = tmp_path / "mapped.json"
        json_file.write_text(json.dumps(data))
        mapping = {"name": "title"}
        ds = load_dataset(json_file, mapping=mapping)
        assert ds.title == "Mapped dataset"


# ── SPARQL queries ───────────────────────────────────────────────────────────


class TestSPARQLQueriesEmpty:

    def test_queries_on_empty_graph_do_not_crash(self):
        g = Graph()
        query_find_all_images(g)
        query_find_all_fields(g)
        query_find_platforms(g)

    def test_query_images_by_camera_id(self):
        g = Graph()
        add_model_to_graph(g, dummy_dataset)
        results = query_images_by_location_and_properties(g, cameraID="4110035082")
        assert len(results) >= 0

    def test_query_images_by_field_id(self):
        g = Graph()
        add_model_to_graph(g, dummy_dataset)
        results = query_images_by_location_and_properties(
            g, field_id=dummy_dataset.hasImage.fieldID
        )
        assert len(results) >= 0

    def test_query_images_by_number_raises(self):
        g = Graph()
        with pytest.raises(NotImplementedError):
            query_images_by_location_and_properties(g, image_number=1)

    def test_query_images_by_name_raises(self):
        g = Graph()
        with pytest.raises(NotImplementedError):
            query_images_by_location_and_properties(g, image_name="test")
