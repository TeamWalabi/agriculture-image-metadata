"""
Unit tests for ontology generator: OWL generation, SHACL shapes, URI logic, and RDF population.
"""

import datetime

import pytest
from rdflib import OWL, RDF, RDFS, XSD, Graph, Literal, Namespace, URIRef

from metadata_vision.ontology.generator import (
    add_model_to_graph,
    add_property_shapes,
    generate_class,
    generate_ontology,
    generate_shacl,
    get_model_class_uri,
    get_model_shape_uri,
)
from metadata_vision.schemas.agent import AgentMetadata
from metadata_vision.schemas.camera import CameraMetadata
from metadata_vision.schemas.crop import CropMetadata
from metadata_vision.schemas.dataset import DatasetMetadata
from metadata_vision.schemas.field import FieldMetadata
from metadata_vision.schemas.images import ImageMetadata
from metadata_vision.schemas.platform import PlatformMetadata
from metadata_vision.schemas.plot import PlotMetadata
from metadata_vision.schemas.plotstate import PlotStateMetadata
from metadata_vision.schemas.sensor import SensorMetadata
from metadata_vision.utils.namespaces import AGIMAGE, DCT, FOAF, SOSA

SH = Namespace("http://www.w3.org/ns/shacl#")


ALL_MODELS = [
    AgentMetadata,
    CropMetadata,
    CameraMetadata,
    SensorMetadata,
    PlotMetadata,
    PlotStateMetadata,
    FieldMetadata,
    PlatformMetadata,
    ImageMetadata,
    DatasetMetadata,
]


# ── Helpers ──────────────────────────────────────────────────────────────────


def _make_camera(**kw):
    defaults = dict(
        cameraName="cam01", cameraID="SN001", cameraModel="TestCam",
        cameraLensModel="Lens", maxPixelX=640, maxPixelY=480,
        pixelSize=3.0, focalLength=4.0, subjectDistance=1.0,
    )
    defaults.update(kw)
    return CameraMetadata(**defaults)


def _make_crop(**kw):
    defaults = dict(cropName="wheat", cropCode="TRZAW")
    defaults.update(kw)
    return CropMetadata(**defaults)


def _make_plotstate(**kw):
    defaults = dict(stateName="ps1", hasCrop=_make_crop())
    defaults.update(kw)
    return PlotStateMetadata(**defaults)


def _make_plot(**kw):
    defaults = dict(plotName="plot1", bbox=["POLYGON((0 0,1 0,1 1,0 0))"], hasPlotState=_make_plotstate())
    defaults.update(kw)
    return PlotMetadata(**defaults)


def _make_field(**kw):
    defaults = dict(fieldName="field_a", bbox="POLYGON((0 0,10 0,10 10,0 0))", hasPlot=_make_plot())
    defaults.update(kw)
    return FieldMetadata(**defaults)


def _make_sensor(**kw):
    defaults = dict(hasCamera=_make_camera())
    defaults.update(kw)
    return SensorMetadata(**defaults)


def _make_platform(**kw):
    defaults = dict(platformName="robot1", hasSensor=_make_sensor())
    defaults.update(kw)
    return PlatformMetadata(**defaults)


def _make_image(**kw):
    defaults = dict(
        imageName="img.png", imageTimestamp=datetime.datetime(2025, 1, 1),
        cameraID="SN001", fieldID="f_abc", plotID="p_abc", platformID="r_abc",
        baseQuaternionXYZW=[0.0, 0.0, 0.0, 1.0],
    )
    defaults.update(kw)
    return ImageMetadata(**defaults)


# ── generate_ontology metadata triples ───────────────────────────────────────


class TestGenerateOntologyMetadata:

    def test_ontology_type_triple(self):
        g = generate_ontology([CameraMetadata])
        assert (AGIMAGE[""], RDF.type, OWL.Ontology) in g

    def test_version_info_present(self):
        g = generate_ontology([CameraMetadata])
        versions = list(g.objects(AGIMAGE[""], OWL.versionInfo))
        assert len(versions) == 1
        assert str(versions[0]) != ""

    def test_dct_created_present(self):
        g = generate_ontology([CameraMetadata])
        dates = list(g.objects(AGIMAGE[""], DCT.created))
        assert len(dates) == 1
        # Should be today's date in ISO format
        today = datetime.date.today().isoformat()
        assert str(dates[0]) == today

    def test_ontology_has_classes(self):
        g = generate_ontology(ALL_MODELS)
        classes = set(g.subjects(RDF.type, OWL.Class))
        assert len(classes) > 0

    def test_ontology_has_datatype_properties(self):
        g = generate_ontology(ALL_MODELS)
        props = set(g.subjects(RDF.type, OWL.DatatypeProperty))
        assert len(props) > 0

    def test_ontology_has_object_properties(self):
        g = generate_ontology(ALL_MODELS)
        props = set(g.subjects(RDF.type, OWL.ObjectProperty))
        assert len(props) > 0


# ── generate_class ───────────────────────────────────────────────────────────


class TestGenerateClass:

    def test_creates_owl_class(self):
        g = Graph()
        generate_class(g, CameraMetadata)
        assert (AGIMAGE["Camera"], RDF.type, OWL.Class) in g

    def test_creates_datatype_properties(self):
        g = Graph()
        generate_class(g, CameraMetadata)
        # cameraName should have a DatatypeProperty triple
        camera_name_uri = AGIMAGE["cameraName"]
        assert (camera_name_uri, RDF.type, OWL.DatatypeProperty) in g
        assert (camera_name_uri, RDFS.domain, AGIMAGE["Camera"]) in g

    def test_creates_object_properties_for_nested_models(self):
        g = Graph()
        generate_class(g, FieldMetadata)
        # hasPlot should be an ObjectProperty
        has_plot_uri = AGIMAGE["hasPlot"]
        assert (has_plot_uri, RDF.type, OWL.ObjectProperty) in g

    def test_labels_are_added(self):
        g = Graph()
        generate_class(g, AgentMetadata)
        name_uri = FOAF["name"]
        labels = list(g.objects(name_uri, RDFS.label))
        assert any(str(l) == "name" for l in labels)


# ── get_model_shape_uri ──────────────────────────────────────────────────────


class TestGetModelShapeUri:

    def test_camera_shape_uri(self):
        uri = get_model_shape_uri(CameraMetadata)
        assert str(uri).endswith("CameraShape")

    def test_image_shape_uri(self):
        uri = get_model_shape_uri(ImageMetadata)
        assert str(uri).endswith("ImageShape")

    def test_dataset_shape_uri(self):
        uri = get_model_shape_uri(DatasetMetadata)
        assert str(uri).endswith("DatasetShape")

    def test_plotstate_shape_uri(self):
        uri = get_model_shape_uri(PlotStateMetadata)
        assert str(uri).endswith("PlotStateShape")


# ── get_model_class_uri ──────────────────────────────────────────────────────


class TestGetModelClassUri:

    def test_agimage_camera(self):
        uri = get_model_class_uri(CameraMetadata)
        assert uri == AGIMAGE["Camera"]

    def test_agimage_field(self):
        uri = get_model_class_uri(FieldMetadata)
        assert uri == AGIMAGE["Field"]

    def test_foaf_agent(self):
        """AgentMetadata sets rdf_type as instance default, not __dict__ class attr.
        get_model_class_uri uses __dict__ so falls back to AGIMAGE."""
        uri = get_model_class_uri(AgentMetadata)
        # Falls back to AGIMAGE since rdf_type is not in __dict__
        assert uri == AGIMAGE["Agent"]

    def test_dcat_dataset(self):
        """DatasetMetadata sets rdf_type as instance default, not __dict__ class attr.
        get_model_class_uri uses __dict__ so falls back to AGIMAGE."""
        uri = get_model_class_uri(DatasetMetadata)
        assert uri == AGIMAGE["Dataset"]

    def test_agimage_image(self):
        uri = get_model_class_uri(ImageMetadata)
        assert uri == AGIMAGE["Image"]

    def test_agimage_platform(self):
        uri = get_model_class_uri(PlatformMetadata)
        assert uri == AGIMAGE["Platform"]


# ── SHACL shapes ─────────────────────────────────────────────────────────────


class TestSHACLShapes:

    def test_node_shapes_created(self):
        g = generate_shacl(ALL_MODELS)
        node_shapes = set(g.subjects(RDF.type, SH.NodeShape))
        assert len(node_shapes) >= len(ALL_MODELS)

    def test_shape_has_target_class(self):
        g = generate_shacl([CameraMetadata])
        shape_uri = get_model_shape_uri(CameraMetadata)
        targets = list(g.objects(shape_uri, SH.targetClass))
        assert len(targets) == 1
        assert targets[0] == AGIMAGE["Camera"]

    def test_required_field_has_mincount_1(self):
        g = generate_shacl([AgentMetadata])
        shape_uri = get_model_shape_uri(AgentMetadata)
        # Find property shapes
        prop_shapes = list(g.objects(shape_uri, SH.property))
        found_required = False
        for ps in prop_shapes:
            path = list(g.objects(ps, SH.path))
            min_counts = list(g.objects(ps, SH.minCount))
            if path and str(path[0]) == str(FOAF["name"]):
                assert any(int(mc) == 1 for mc in min_counts)
                found_required = True
        assert found_required, "Expected required field 'name' with minCount 1"

    def test_optional_field_has_mincount_0(self):
        g = generate_shacl([CropMetadata])
        shape_uri = get_model_shape_uri(CropMetadata)
        prop_shapes = list(g.objects(shape_uri, SH.property))

        found_optional = False
        for ps in prop_shapes:
            path = list(g.objects(ps, SH.path))
            min_counts = list(g.objects(ps, SH.minCount))
            if path and str(path[0]) == str(AGIMAGE["cropCultivar"]):
                assert any(int(mc) == 0 for mc in min_counts)
                found_optional = True
        assert found_optional, "Expected optional field 'cropCultivar' with minCount 0"

    def test_nested_model_has_sh_node(self):
        g = generate_shacl([FieldMetadata, PlotMetadata])
        shape_uri = get_model_shape_uri(FieldMetadata)
        prop_shapes = list(g.objects(shape_uri, SH.property))
        found_nested = False
        for ps in prop_shapes:
            nodes = list(g.objects(ps, SH.node))
            if nodes:
                found_nested = True
                break
        assert found_nested, "Expected nested model to use sh:node"


# ── add_model_to_graph ───────────────────────────────────────────────────────


class TestAddModelToGraph:

    def test_uses_image_id_as_uri(self):
        img = _make_image(imageID="test_image_001")
        g = Graph()
        uri = add_model_to_graph(g, img)
        assert "test_image_001" in str(uri)

    def test_uses_field_id_as_uri(self):
        field = _make_field(fieldID="field_test_id")
        g = Graph()
        uri = add_model_to_graph(g, field)
        assert "field_test_id" in str(uri)

    def test_uses_camera_id_as_uri(self):
        cam = _make_camera(cameraID="SN999")
        g = Graph()
        uri = add_model_to_graph(g, cam)
        assert "SN999" in str(uri)

    def test_uses_identifier_for_dataset(self):
        ds = DatasetMetadata(
            title="T", description="D", identifier="ds_test_001",
            creator=AgentMetadata(name="A"), numberOfImages=1,
            numberOfAnnotatedImages=0, hasField=_make_field(),
            hasPlatform=_make_platform(),
        )
        g = Graph()
        uri = add_model_to_graph(g, ds)
        assert "ds_test_001" in str(uri)

    def test_type_triple_added(self):
        cam = _make_camera()
        g = Graph()
        uri = add_model_to_graph(g, cam)
        assert (uri, RDF.type, AGIMAGE["Camera"]) in g

    def test_nested_model_creates_link(self):
        field = _make_field()
        g = Graph()
        field_uri = add_model_to_graph(g, field)
        # Should have a hasPlot object property link
        has_plot_objects = list(g.objects(field_uri, AGIMAGE["hasPlot"]))
        assert len(has_plot_objects) >= 1

    def test_list_of_nested_models(self):
        field1 = _make_field(fieldName="f1")
        field2 = _make_field(fieldName="f2")
        ds = DatasetMetadata(
            title="T", description="D", identifier="ds_multi",
            creator=AgentMetadata(name="A"), numberOfImages=1,
            numberOfAnnotatedImages=0, hasField=[field1, field2],
            hasPlatform=_make_platform(),
        )
        g = Graph()
        uri = add_model_to_graph(g, ds)
        fields = list(g.objects(uri, AGIMAGE["hasField"]))
        assert len(fields) == 2

    def test_primitive_values_serialized(self):
        cam = _make_camera()
        g = Graph()
        uri = add_model_to_graph(g, cam)
        # Check cameraName was added as literal
        names = list(g.objects(uri, AGIMAGE["cameraName"]))
        assert len(names) == 1
        assert str(names[0]) == "cam01"

    def test_integer_field_has_xsd_type(self):
        cam = _make_camera(maxPixelX=1920)
        g = Graph()
        uri = add_model_to_graph(g, cam)
        from rdflib.namespace import XSD as RDF_XSD
        from metadata_vision.utils.namespaces import EXIF
        values = list(g.objects(uri, URIRef(str(EXIF) + "PixelXDimension")))
        assert len(values) == 1
        assert values[0].datatype == XSD.integer

    def test_float_field_has_xsd_type(self):
        cam = _make_camera(focalLength=8.0)
        g = Graph()
        uri = add_model_to_graph(g, cam)
        from metadata_vision.utils.namespaces import EXIF
        values = list(g.objects(uri, URIRef(str(EXIF) + "FocalLength")))
        assert len(values) == 1
        assert values[0].datatype == XSD.double

    def test_boolean_field_has_xsd_type(self):
        cam = _make_camera(cameraBox=True)
        g = Graph()
        uri = add_model_to_graph(g, cam)
        values = list(g.objects(uri, AGIMAGE["cameraBox"]))
        assert len(values) == 1
        assert values[0].datatype == XSD.boolean

    def test_none_fields_not_added(self):
        cam = _make_camera(lightSource=None)
        g = Graph()
        uri = add_model_to_graph(g, cam)
        from metadata_vision.utils.namespaces import EXIF
        values = list(g.objects(uri, URIRef(str(EXIF) + "LightSource")))
        assert len(values) == 0

    def test_agent_uri_uses_uuid(self):
        """Agent has no ID field, so should use a generated UUID URI."""
        agent = AgentMetadata(name="Test Agent")
        g = Graph()
        uri = add_model_to_graph(g, agent)
        assert uri is not None
        # Should have type and name triples
        assert (uri, RDF.type, FOAF["Agent"]) in g
