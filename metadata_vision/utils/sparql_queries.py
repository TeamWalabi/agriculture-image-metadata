from typing import Optional, List
from rdflib import Graph


def query_find_all_images(g: Graph):
    query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    SELECT ?image ?imageTitle
    WHERE {
        ?image a agimage:Image ;
            <https://w3id.org/agri-image/imageName> ?imageTitle .
    }
    """
    print("\n📷 Query: Find all images")
    results = g.query(query)
    for row in results:
        print(f"   - {row.imageTitle}")
    return results


def query_find_all_fields(g: Graph):
    query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    SELECT ?field ?fieldName
    WHERE {
        ?field a agimage:Field ;
            <https://w3id.org/agri-image/fieldName> ?fieldName .
    }
    """
    print("\n🌾 Query: Find all fields")
    results = g.query(query)
    for row in results:
        print(f"   - {row.fieldName}")
    return results


def query_find_platforms(g: Graph):
    query = """
    PREFIX agimage: <https://w3id.org/agri-image/>
    SELECT ?platform ?platformName
    WHERE {
        ?platform a agimage:Platform ;
            <https://w3id.org/agri-image/platformName> ?platformName .
    }
    """
    print("\n🤖 Query: Find all platforms")
    results = g.query(query)
    for row in results:
        print(f"   - {row.platformName}")
    return results


def query_images_by_location_and_properties(
    g: Graph,
    image_number: Optional[int] = None,
    image_name: Optional[str] = None,
    cameraID: Optional[str] = None,
    field_id: Optional[str] = None,
    platform_id: Optional[str] = None,
    plot_id: Optional[str] = None,
    base_xyz_min: Optional[tuple] = None,
    base_xyz_max: Optional[tuple] = None,
) -> List:
    """
    Query images filtered by location (baseXYZ), image properties, and equipment IDs.

    Args:
        g: RDF graph to query
        image_number: Specific image number to filter (optional)
        image_name: Specific image name pattern to filter (optional)
        cameraID: Filter by camera serial number from EXIF (optional)
        field_id: Filter by field ID (optional)
        platform_id: Filter by platform ID (optional)
        plot_id: Filter by plot ID (optional)
        base_xyz_min: Tuple of (x_min, y_min, z_min) for location bounding box (optional)
        base_xyz_max: Tuple of (x_max, y_max, z_max) for location bounding box (optional)

    Returns:
        List of query results
    """
    filters = []
    optional_patterns = []

    # Filter by image number
    if image_number is not None:
        raise NotImplementedError
        filters.append(f"FILTER(?imageNumber = {image_number})")

    # Filter by image name (substring match)
    if image_name is not None:
        raise NotImplementedError
        filters.append(f'FILTER(CONTAINS(?imageName, "{image_name}"))')

    # Filter by camera serial number (EXIF)
    if cameraID is not None:
        optional_patterns.append(
            f'?image <https://exiftool.org/TagNames/EXIF.html#SerialNumber> "{cameraID}" .'
        )

    # Filter by field ID
    if field_id is not None:
        optional_patterns.append(f'?image <https://w3id.org/agri-image/fieldID> "{field_id}" .')

    # Filter by platform ID
    if platform_id is not None:
        optional_patterns.append(
            f'?image <https://w3id.org/agri-image/platformID> "{platform_id}" .'
        )

    # Filter by plot ID
    if plot_id is not None:
        optional_patterns.append(f'?image <https://w3id.org/agri-image/plotID> "{plot_id}" .')

    # Filter by location bounding box
    if base_xyz_min and base_xyz_max:
        x_min, y_min, z_min = base_xyz_min
        x_max, y_max, z_max = base_xyz_max
        filters.append(
            f"FILTER(?baseX >= {x_min} && ?baseX <= {x_max} && ?baseY >= {y_min} && ?baseY <= {y_max} && ?baseZ >= {z_min} && ?baseZ <= {z_max})"
        )

    filter_str = "\n        ".join(filters) if filters else ""
    optional_str = "\n        ".join(optional_patterns) if optional_patterns else ""

    query = f"""
    PREFIX agimage: <https://w3id.org/agri-image/>
    PREFIX exif: <http://www.w3.org/2003/12/exif/ns#>
    PREFIX rdf: <http://www.w3.org/1999/02/22-rdf-syntax-ns#>
    SELECT ?image ?imageName ?imageNumber ?baseX ?baseY ?baseZ
           ?serialNumber ?fieldID ?platformID ?plotID
    WHERE {{
        ?image a agimage:Image ;
            <https://w3id.org/agri-image/imageName> ?imageName .

        OPTIONAL {{ ?image <https://w3id.org/agri-image/imageNumber> ?imageNumber . }}
        OPTIONAL {{ ?image <http://www.w3.org/2003/12/exif/ns#SerialNumber> ?serialNumber . }}
        OPTIONAL {{ ?image <https://w3id.org/agri-image/fieldID> ?fieldID . }}
        OPTIONAL {{ ?image <https://w3id.org/agri-image/platformID> ?platformID . }}
        OPTIONAL {{ ?image <https://w3id.org/agri-image/plotID> ?plotID . }}

        OPTIONAL {{
            ?image <https://w3id.org/agri-image/baseXYZ> ?baseXYZList .
            ?baseXYZList rdf:first ?baseX ;
                         rdf:rest ?rest1 .
            ?rest1 rdf:first ?baseY ;
                   rdf:rest ?rest2 .
            ?rest2 rdf:first ?baseZ .
        }}

        {optional_str}
        {filter_str}
    }}
    ORDER BY ?imageName
    """

    print("\n📍 Query: Find images by location and properties")
    if image_number:
        print(f"   Filter: imageNumber = {image_number}")
    if image_name:
        print(f"   Filter: imageName contains '{image_name}'")
    if cameraID:
        print(f"   Filter: cameraSerialNumber = {cameraID}")
    if field_id:
        print(f"   Filter: fieldID = {field_id}")
    if platform_id:
        print(f"   Filter: platformID = {platform_id}")
    if plot_id:
        print(f"   Filter: plotID = {plot_id}")
    if base_xyz_min and base_xyz_max:
        print(
            f"   Filter: Location X[{base_xyz_min[0]}, {base_xyz_max[0]}], "
            f"Y[{base_xyz_min[1]}, {base_xyz_max[1]}], "
            f"Z[{base_xyz_min[2]}, {base_xyz_max[2]}]"
        )

    results = g.query(query)

    if not results:
        print("   ❌ No images found matching criteria")
        return []

    for row in results:
        location_str = f"({row.baseX}, {row.baseY}, {row.baseZ})" if row.baseX else "N/A"
        ids_str = f"[Serial: {row.serialNumber}, Field: {row.fieldID}, Platform: {row.platformID}, Plot: {row.plotID}]"
        print(f"   ✓ {row.imageName} (#{row.imageNumber}) @ {location_str} {ids_str}")

    return list(results)


# if __name__=="__main__":
#     # Find images from specific camera in specific field
#     from metadata_vision.ontology.generator import load_ontology_graph
#     g = load_ontology_graph(Path("metadata_vision") / "ontology" / "ontology.ttl")
#     query_images_by_location_and_properties(
#         g,
#         camera_id="4110037731",
#         field_id="field_001",
#         platform_id="demo_machine_1"
#     )

#     # Find images in location box from specific plot
#     query_images_in_location_box(
#         g,
#         x_min=0.0, x_max=10.0,
#         y_min=0.0, y_max=10.0,
#         z_min=0.0, z_max=5.0,
#         camera_id="4110037731",
#         plot_id="row_01"
#     )
