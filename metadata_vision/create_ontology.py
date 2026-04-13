"""
Unified example: Generate ontology + create instances + demonstrate usage + validate with SHACL

This example combines functionality from chatgpt.py and example_with_ontology.py:
1. Generates SHACL shapes file from Pydantic models
2. Generates OWL ontology from Pydantic models on-the-fly
3. Creates instances of metadata classes
4. Adds them to an RDF graph
5. Validates RDF graph against SHACL shapes
6. Performs SPARQL queries
7. Serializes results
"""
import json

from rdflib import Graph, Namespace
from pathlib import Path
from pyshacl import validate

from metadata_vision.schemas.images import ImageMetadata
from metadata_vision.schemas.field import FieldMetadata
from metadata_vision.schemas.plot import PlotMetadata
from metadata_vision.schemas.plotstate import PlotStateMetadata
from metadata_vision.schemas.camera import CameraMetadata
from metadata_vision.schemas.crop import CropMetadata
from metadata_vision.schemas.platform import PlatformMetadata
from metadata_vision.schemas.sensor import SensorMetadata
from metadata_vision.schemas.agent import AgentMetadata
from metadata_vision.schemas.dataset import DatasetMetadata
from metadata_vision.ontology import (
    generate_ontology,
    generate_shacl,
    add_model_to_graph,
)
from metadata_vision.data import (
    dummy_camera,
    # dummy_sensor,
    dummy_platform,
    # dummy_crop,
    dummy_plot,
    dummy_field,
    dummy_field2,
    dummy_image,
    dummy_agent,
    # dummy_contributor,
    dummy_dataset,
)


if __name__=="__main__":
    output_dir = Path(__file__).parent / "ontology"
    output_dir.mkdir(exist_ok=True)

    # -----------------------
    # 1. Generate SHACL shapes
    # -----------------------
    print("=" * 70)
    print("STEP 1: GENERATING SHACL SHAPES FILE")
    print("=" * 70)

    models_for_shapes = [
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

    shapes_graph = generate_shacl(models_for_shapes)
    print(f"✓ Generated {len(shapes_graph)} shape triples")
    print(f"✓ Shapes file saved to: shapes.ttl")
    shapes_graph.serialize("shapes.ttl", format="turtle")
    print()

    # -----------------------
    # 2. Generate ontology
    # -----------------------
    print("=" * 70)
    print("STEP 2: GENERATING ONTOLOGY")
    print("=" * 70)

    # g = generate_ontology([
    #     DatasetMetadata,
    #     FieldMetadata,
    #     CropMetadata,
    #     PlatformMetadata,
    #     SensorMetadata,
    #     CameraMetadata,
    #     ImageMetadata,
    # ])
    g = generate_ontology(models_for_shapes)

    print(f"✓ Generated ontology with {len(g)} triples")
    ontology_output = output_dir / "ontology.ttl"
    g.serialize(ontology_output, format="turtle")
    print(f"✓ Ontology saved to: {ontology_output}")

    print()

    # -----------------------
    # 3. Create metadata instances
    # -----------------------
    print("=" * 70)
    print("STEP 3: CREATING METADATA INSTANCES")
    print("=" * 70)
    
    print(f"✓ Created camera: {dummy_camera.cameraName} ({dummy_camera.cameraID})")
    print(f"✓ Created sensor with camera")
    print(f"✓ Created platform: {dummy_platform.platformName} ({dummy_platform.platformID})")
    print(f"✓ Created plot: {dummy_plot.plotName} ({dummy_plot.plotID})")
    print(f"✓ Created field: {dummy_field.fieldName} ({dummy_field.fieldID})")
    print(f"✓ Created field: {dummy_field2.fieldName} ({dummy_field2.fieldID})")
    print(f"✓ Created image: {dummy_image.imageName} ({dummy_image.imageID})")
    print(f"✓ Created agent: {dummy_agent.name}")
    print(f"✓ Created dataset: {dummy_dataset.title}")
    print()

    # -----------------------
    # 4. Add metadata to graph
    # -----------------------
    print("="*70)
    print("STEP 4: ADDING METADATA TO RDF GRAPH")
    print("=" * 70)

    # add_model_to_graph(g, dummy_platform)
    # add_model_to_graph(g, dummy_field)
    # add_model_to_graph(g, dummy_field2)
    # add_model_to_graph(g, dummy_plot)
    # add_model_to_graph(g, dummy_image)
    add_model_to_graph(g, dummy_dataset)

    print(f"✓ Added all metadata to graph")
    print(f"✓ Total triples in graph: {len(g)}")
    print()

    # -----------------------
    # 5. Validate with SHACL
    # -----------------------
    print("="*70)
    print("STEP 5: VALIDATING WITH SHACL")
    print("="*70)

    try:

        is_valid, report_graph, report_text = validate(g, shacl_graph=shapes_graph)
        
        if is_valid:
            print("✅ SHACL Validation PASSED!")
            print("   All data conforms to defined shapes and constraints.")
        else:
            print("❌ SHACL Validation FAILED:")
            print(report_text)
    except ImportError:
        print("⚠️  pySHACL not installed. Install with: pip install pyshacl")
        print("   Skipping SHACL validation...")
    except Exception as e:
        print(f"⚠️  SHACL validation error: {e}")

    print()

    # -----------------------
    # 6. SPARQL queries
    # -----------------------
    print("="*70)
    print("STEP 6: SPARQL QUERIES")
    print("=" * 70)

    from metadata_vision.utils.sparql_queries import query_find_all_fields, query_find_all_images, query_find_platforms
    query_find_all_images(g)
    query_find_all_fields(g)
    query_find_platforms(g)
    print()

    # -----------------------
    # 7. Serialize to files
    # -----------------------
    print("="*70)
    print("STEP 7: SERIALIZING OUTPUT")
    print("=" * 70)

    # Save RDF graph as Turtle
    shapes_path = output_dir / "shapes.ttl"
    ontology_path = output_dir / "testing.ttl"
    graph_path = output_dir / "unified_output.ttl"
    json_path = output_dir / "unified_output.json"

    shapes_graph.serialize(shapes_path, format="turtle")
    print(f"✓ Serialized to: {shapes_path}")

    g.serialize(graph_path, format="turtle")
    print(f"✓ Serialized to: {graph_path}")

    # Save metadata as JSON
    output_json = {
        "dataset": dummy_dataset.model_dump(),
    }
    with open(json_path, "w") as f:
        json.dump(output_json, f, indent=2, default=str)
    print(f"✓ Serialized to: {json_path}")

    # Load the unified_output.json file
    with open(json_path, "r") as f:
        loaded_data = json.load(f)
    
    loaded_dataset = DatasetMetadata(**loaded_data["dataset"])
    
    print()
    print("=" * 70)
    print("✅ UNIFIED EXAMPLE COMPLETE!")
    print("=" * 70)
    print("\nGenerated files:")
    print(f"  📄 {shapes_path}          (SHACL shapes for validation)")
    print(f"  📄 {ontology_path}         (Generated OWL ontology)")
    print(f"  🔗 {graph_path}  (RDF graph with instances)")
    print(f"  📋 {json_path} (Metadata as JSON)")
