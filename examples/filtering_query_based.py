"""
Example script to load a dataset and filter based on on queries
"""
from pathlib import Path


if __name__=="__main__":
    from metadata_vision.utils.dataset_loading import load_dataset, load_metadata
    from metadata_vision.schemas.images import ImageMetadata
    from metadata_vision.ontology.generator import load_ontology_graph, add_model_to_graph
    from metadata_vision.utils import sparql_queries
    from rdflib import Namespace, Literal
    from decimal import Decimal

    # 2. load ontology
    g = load_ontology_graph(Path("metadata_vision") / "ontology" / "ontology.ttl")

    ## 1. load dataset
    dataset  = load_dataset("examples/agros.json")

    mapping = {
        "image_name": "imageName",
        "image_timestamp": "imageTimestamp",
        "camera_id": "cameraID",
        "machine_id": "platformID",
        "field_id": "fieldID",
        "plot_id": "plotID",
        "exposure_time_s": "exposureTime",
        "image_number": "imageNumber",
        "image_xyz": "imageXYZ",
        "image_quaternion_xyzw": "imageQuaternionXYZW",
        "image_gnss": "imageGNSS",
        "base_xyz": "baseXYZ",
        "base_quaternion_xyzw": "baseQuaternionXYZW",
        "base_gnss": "baseGNSS"
    }

    main_folder = Path("/media/agro/PhDBart2/3742355900_agros2_komkommer/raw_data/field_001/row_01/20260226_demo_platform1/")

    list_of_paths = main_folder.rglob("*metadata.json")
    images_dataset = load_metadata(list_of_paths, model_class=ImageMetadata, mapping=mapping)
    dataset.hasImage = images_dataset

    add_model_to_graph(g, dataset)

    # g.serialize(destination="graph.ttl", format="ttl")
    # g = load_ontology_graph("graph.ttl")


    # sparql_queries.query_find_all_images(g)
    # sparql_queries.query_find_all_fields(g)
    # sparql_queries.query_find_platforms(g)
    sparql_queries.query_images_by_location_and_properties(
        g,
        # image_number="003167",
        # cameraID="0101",# 0101
        field_id="field_001",
        # platform_id="demo_platform1"
    )


    



