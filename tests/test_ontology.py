"""
Test suite for ontology generation, dataset creation, RDF graph population, and SPARQL queries.
"""

import pytest
from rdflib import Graph

from metadata_vision.schemas.images import ImageMetadata
from metadata_vision.schemas.field import FieldMetadata, PlotMetadata
from metadata_vision.schemas.camera import CameraMetadata
from metadata_vision.schemas.crop import CropMetadata
from metadata_vision.schemas.platform import PlatformMetadata
from metadata_vision.schemas.dataset import DatasetMetadata
from metadata_vision.ontology.generator import (
    generate_ontology,
    generate_shacl,
    add_model_to_graph,
)
from metadata_vision.utils.sparql_queries import (
    query_find_all_images,
    query_find_all_fields,
    query_find_platforms,
    # query_images_by_location_and_properties,
    # query_images_in_location_box,
)
from metadata_vision.data.example_data import (
    dummy_dataset,
)


class TestOntologyGeneration:
    """Tests for OWL ontology generation from Pydantic models."""

    def test_generate_ontology(self):
        """Test generating an OWL ontology from Pydantic models."""
        models = [
            ImageMetadata,
            CameraMetadata,
            PlatformMetadata,
            FieldMetadata,
            PlotMetadata,
            CropMetadata,
            DatasetMetadata,
        ]

        g = generate_ontology(models)

        assert len(g) > 0
        assert g is not None

        # Check that ontology contains classes
        query = """
        PREFIX owl: <http://www.w3.org/2002/07/owl#>
        SELECT (COUNT(?class) as ?count) WHERE {
            ?class a owl:Class .
        }
        """
        results = list(g.query(query))
        assert int(results[0][0]) > 0


class TestSHACLShapesGeneration:
    """Tests for SHACL shapes generation from Pydantic models."""

    def test_generate_shacl_shapes(self):
        """Test generating SHACL shapes from Pydantic models."""
        models = [
            ImageMetadata,
            CameraMetadata,
            PlatformMetadata,
            FieldMetadata,
            PlotMetadata,
            CropMetadata,
            DatasetMetadata,
        ]

        g = generate_shacl(models)

        assert len(g) > 0
        assert g is not None

        # Check that shapes contain NodeShapes
        query = """
        PREFIX sh: <http://www.w3.org/ns/shacl#>
        SELECT (COUNT(?shape) as ?count) WHERE {
            ?shape a sh:NodeShape .
        }
        """
        results = list(g.query(query))
        assert int(results[0][0]) > 0


class TestRDFGraphPopulation:
    """Tests for adding Pydantic models to RDF graphs."""

    @pytest.fixture
    def sample_dataset(self):
        """Create a sample dataset with nested metadata."""

        return dummy_dataset

    def test_add_model_to_graph(self, sample_dataset):
        """Test adding a model to an RDF graph."""
        g = Graph()

        uri = add_model_to_graph(g, sample_dataset)

        assert uri is not None
        assert len(g) > 0


class TestSPARQLQueries:
    """Tests for SPARQL query functions."""

    @pytest.fixture
    def populated_graph(self):
        """Create and populate an RDF graph with sample data."""
        g = Graph()
        add_model_to_graph(g, dummy_dataset)
        return g

    def test_query_find_all_images(self, populated_graph):
        """Test finding all images in the graph."""
        query_find_all_images(populated_graph)

        # Verify query returns results
        query = """
        PREFIX agimage: <https://w3id.org/agri-image/>
        SELECT ?image WHERE {
            ?image a agimage:Image .
        }
        """
        results = list(populated_graph.query(query))
        assert len(results) == 1

    def test_query_find_all_fields(self, populated_graph):
        """Test finding all fields in the graph."""
        query_find_all_fields(populated_graph)

        query = """
        PREFIX agimage: <https://w3id.org/agri-image/>
        SELECT ?field WHERE {
            ?field a agimage:Field .
        }
        """
        results = list(populated_graph.query(query))
        assert len(results) > 0

    def test_query_find_platforms(self, populated_graph):
        """Test finding all platforms in the graph."""
        query_find_platforms(populated_graph)

        query = """
        PREFIX agimage: <https://w3id.org/agri-image/>
        SELECT ?platform WHERE {
            ?platform a agimage:Platform .
        }
        """
        results = list(populated_graph.query(query))
        assert len(results) > 0


class TestCompleteWorkflow:
    """Integration tests for complete ontology and data workflow."""

    def test_complete_workflow(self):
        """Test the complete workflow: generate ontology, populate graph, and query."""
        # Step 1: Generate ontology
        models = [
            ImageMetadata,
            CameraMetadata,
            PlatformMetadata,
            FieldMetadata,
            PlotMetadata,
            CropMetadata,
            DatasetMetadata,
        ]
        ontology_graph = generate_ontology(models)
        assert len(ontology_graph) > 0

        # Step 2: Generate SHACL shapes
        shapes_graph = generate_shacl(models)
        assert len(shapes_graph) > 0

        # Step 3: Create sample data
        dataset = dummy_dataset

        # Step 4: Populate RDF graph
        data_graph = Graph()
        add_model_to_graph(data_graph, dataset)
        assert len(data_graph) > 0

        # # Step 5: Query the data
        # results = query_images_by_location_and_properties(data_graph, field_ids=["field_001"])
        # assert len(results) >= 1

        # Step 6: Verify data exists
        query = """
        PREFIX agimage: <https://w3id.org/agri-image/>
        SELECT ?image ?imageName WHERE {
            ?image a agimage:Image ;
                <https://w3id.org/agri-image/imageName> ?imageName .
        }
        """
        query_results = list(data_graph.query(query))
        assert len(query_results) == 1
        assert "20251014T093010Z857_camid9_trigger1000_rgb.png" in str(query_results[0][1])
