"""
Ontology generation module for automatic OWL ontology and SHACL shapes generation
from Pydantic models.
"""

import inspect
import uuid
from datetime import date
from rdflib import Graph, Namespace, RDF, RDFS, OWL, URIRef, Literal, BNode
from pydantic import BaseModel

from metadata_vision import __version__
from metadata_vision.utils.namespaces import (
    AGIMAGE, SH, DCT, FOAF, SOSA, EXIF, XSD
)
from metadata_vision.utils.type_mapping import unwrap_type, python_to_xsd


def load_ontology_graph(ontology_file_path: str) -> Graph:
    """
    Load an ontology file (TTL, RDF/XML, N-Triples, etc.) as an RDF graph.
    
    Args:
        ontology_file_path (str): Path to the ontology file
        
    Returns:
        Graph: RDF graph containing the loaded ontology
    """
    g = Graph()
    
    # Bind namespaces for readability
    g.bind("agimage", AGIMAGE)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)
    
    # Parse the file (format is auto-detected from file extension)
    g.parse(ontology_file_path, format=None)
    
    print(f"✓ Loaded ontology from: {ontology_file_path}")
    print(f"  Total triples: {len(g)}")
    
    return g


# =============================================================================
# OWL ONTOLOGY GENERATION
# =============================================================================

def generate_class(g, model):
    """
    Generate OWL class definition from Pydantic model.
    
    Args:
        g (Graph): RDF graph to add triples to
        model: Pydantic model class
    """
    class_name = model.__name__.replace("Metadata", "")
    class_uri = AGIMAGE[class_name]

    g.add((class_uri, RDF.type, OWL.Class))

    for field_name, field in model.model_fields.items():
        extra = field.json_schema_extra or {}
        uri = extra.get("uri")

        if not uri:
            continue

        prop = URIRef(uri)
        field_type = unwrap_type(field.annotation)

        # Object property (nested BaseModel)
        if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            range_class = AGIMAGE[field_type.__name__.replace("Metadata", "")]
            g.add((prop, RDF.type, OWL.ObjectProperty))
            g.add((prop, RDFS.domain, class_uri))
            g.add((prop, RDFS.range, range_class))
            generate_class(g, field_type)
        
        # Datatype property
        else:
            g.add((prop, RDF.type, OWL.DatatypeProperty))
            g.add((prop, RDFS.domain, class_uri))
            g.add((prop, RDFS.range, python_to_xsd(field_type)))

        g.add((prop, RDFS.label, Literal(field_name)))
        if field.description:
            g.add((prop, RDFS.comment, Literal(field.description)))


def generate_ontology(root_models):
    """
    Generate complete OWL ontology from a list of Pydantic models.
    
    Args:
        root_models (list): List of Pydantic model classes
        
    Returns:
        Graph: RDF graph containing the generated OWL ontology
    """
    g = Graph()

    g.bind("agimage", AGIMAGE)
    g.bind("owl", OWL)
    g.bind("rdfs", RDFS)
    g.bind("xsd", XSD)

    g.bind("dct", DCT)

    g.add((AGIMAGE[""], RDF.type, OWL.Ontology))
    g.add((AGIMAGE[""], OWL.versionInfo, Literal(__version__)))
    g.add((AGIMAGE[""], DCT.created, Literal(date.today().isoformat(), datatype=XSD.date)))

    for model in root_models:
        generate_class(g, model)

    return g


# =============================================================================
# SHACL SHAPES GENERATION
# =============================================================================

def get_model_shape_uri(model_class):
    """
    Generate shape URI for a model class.
    
    Args:
        model_class: Pydantic model class
        
    Returns:
        URIRef: Shape URI (e.g., agimage:ImageShape)
    """
    class_name = model_class.__name__.replace("Metadata", "")
    return AGIMAGE[f"{class_name}Shape"]


def get_model_class_uri(model_class):
    """
    Generate RDF class URI for a model class.
    
    Maps Pydantic model's rdf_type field to proper RDF namespace URIs.
    Handles special cases (dcat:Dataset, foaf:Agent, sosa:Sensor, etc.)
    
    Args:
        model_class: Pydantic model class
        
    Returns:
        URIRef: RDF class URI
    """
    rdf_type = model_class.__dict__.get("rdf_type", None)
    
    if rdf_type and ":" in rdf_type:
        prefix, local = rdf_type.split(":", 1)
        if prefix == "agimage":
            return AGIMAGE[local]
        elif prefix == "dcat":
            from rdflib import Namespace as NS
            DCAT = NS("http://www.w3.org/ns/dcat#")
            return DCAT[local]
        elif prefix == "foaf":
            return FOAF[local]
        elif prefix == "sosa":
            return SOSA[local]
    
    class_name = model_class.__name__.replace("Metadata", "")
    return AGIMAGE[class_name]


def add_property_shapes(g, model_class, shape_uri):
    """
    Add sh:property shapes for each field in the model.
    
    Creates SHACL property shapes with constraints (minCount, datatype, nested shapes).
    
    Args:
        g (Graph): RDF graph to add shapes to
        model_class: Pydantic model class
        shape_uri (URIRef): NodeShape URI for this model
    """
    
    for field_name, field in model_class.model_fields.items():
        if field_name == "rdf_type":
            continue
        
        extra = field.json_schema_extra or {}
        field_uri = extra.get("uri")
        
        if not field_uri:
            continue
        
        # Create property shape
        prop_shape = BNode()
        g.add((shape_uri, SH.property, prop_shape))
        g.add((prop_shape, SH.path, URIRef(field_uri)))
        
        # Get field type
        field_type = unwrap_type(field.annotation)
        
        # Check if required (minCount)
        is_required = field.is_required()
        if is_required:
            g.add((prop_shape, SH.minCount, Literal(1)))
        else:
            g.add((prop_shape, SH.minCount, Literal(0)))
        
        # Check if it's a nested BaseModel (object property)
        if inspect.isclass(field_type) and issubclass(field_type, BaseModel):
            # Reference the shape for the nested model
            nested_shape_uri = get_model_shape_uri(field_type)
            g.add((prop_shape, SH.node, nested_shape_uri))
        else:
            # It's a datatype property
            xsd_type = python_to_xsd(field_type)
            g.add((prop_shape, SH.datatype, xsd_type))


def generate_shacl(models_to_shape):
    """
    Generate SHACL shapes for a list of models.
    
    Creates NodeShapes and property constraints for each model.
    
    Args:
        models_to_shape (list): List of Pydantic model classes
        
    Returns:
        Graph: RDF graph containing SHACL shapes
    """
    g = Graph()
    
    # Bind namespaces
    g.bind("sh", SH)
    g.bind("agimage", AGIMAGE)
    g.bind("dct", DCT)
    g.bind("foaf", FOAF)
    g.bind("sosa", SOSA)
    g.bind("exif", EXIF)
    g.bind("xsd", XSD)
    g.bind("rdfs", RDFS)
    
    # Generate shapes for each model
    for model_class in models_to_shape:
        shape_uri = get_model_shape_uri(model_class)
        class_uri = get_model_class_uri(model_class)
        
        # Define NodeShape
        g.add((shape_uri, RDF.type, SH.NodeShape))
        g.add((shape_uri, SH.targetClass, class_uri))
        g.add((shape_uri, SH.name, Literal(f"{model_class.__name__.replace('Metadata', '')} shape")))
        
        if model_class.__doc__:
            g.add((shape_uri, SH.description, Literal(model_class.__doc__.strip())))
        
        # Add property constraints
        add_property_shapes(g, model_class, shape_uri)
    
    return g


# =============================================================================
# RDF GRAPH POPULATION
# =============================================================================
def add_model_to_graph(g: Graph, model: BaseModel):
    """
    Automatically add all fields of a Pydantic model to an RDF graph.
    
    Recursively adds nested BaseModel instances and creates proper RDF relationships.
    
    Args:
        g (Graph): RDF graph to add triples to
        model (BaseModel): Pydantic model instance
        
    Returns:
        URIRef: URI of the added resource
    """
    # Get namespace and class name from rdf_type
    if hasattr(model, 'rdf_type'):
        prefix, model_class_name = model.rdf_type.split(":")
        if prefix == "agimage":
            ns = AGIMAGE
        elif prefix == "dcat":
            from rdflib import Namespace as NS
            ns = NS("http://www.w3.org/ns/dcat#")
        elif prefix == "foaf":
            ns = FOAF
        else:
            ns = AGIMAGE
    else:
        ns = AGIMAGE
        model_class_name = model.__class__.__name__
    
    # Generate URI based on available ID fields
    uri = None
    if hasattr(model, "imageID") and model.imageID:
        uri = ns[model.imageID]
    elif hasattr(model, "fieldID") and model.fieldID:
        uri = ns[model.fieldID]
    elif hasattr(model, "plotID") and model.plotID:
        uri = ns[model.plotID]
    elif hasattr(model, "platformID") and model.platformID:
        uri = ns[model.platformID]
    elif hasattr(model, "cameraID") and model.cameraID:
        uri = ns[model.cameraID]
    elif hasattr(model, "identifier") and model.identifier:
        uri = ns[model.identifier]
    else:
        uri = ns[str(uuid.uuid4())]
    
    # Add type triple
    g.add((uri, RDF.type, ns[model_class_name]))
    
    # Iterate over actual model fields (not dumped dict)
    for field_name, field_info in model.model_fields.items():
        if field_name == 'rdf_type':
            continue
        
        # Get the actual value from the model instance
        value = getattr(model, field_name, None)
        
        if value is None:
            continue
        
        # Get the URI for this property from json_schema_extra
        extra = field_info.json_schema_extra if isinstance(field_info.json_schema_extra, dict) else {}
        prop_uri_str = extra.get("uri")
        
        if not prop_uri_str:
            continue
        
        prop_uri = URIRef(prop_uri_str) if prop_uri_str.startswith(("http", "https")) else AGIMAGE[prop_uri_str]
        
        # Handle nested BaseModel instances (recursively add them)
        if isinstance(value, BaseModel):
            nested_uri = add_model_to_graph(g, value)
            g.add((uri, prop_uri, nested_uri))
        
        # Handle list of BaseModel instances
        elif isinstance(value, list) and value and isinstance(value[0], BaseModel):
            for nested_model in value:
                nested_uri = add_model_to_graph(g, nested_model)
                g.add((uri, prop_uri, nested_uri))
        
        # Handle primitive types and lists of primitives
        elif isinstance(value, list):
            for item in value:
                g.add((uri, prop_uri, Literal(item)))
        elif isinstance(value, bool):
            g.add((uri, prop_uri, Literal(value, datatype=XSD.boolean)))
        elif isinstance(value, int):
            g.add((uri, prop_uri, Literal(value, datatype=XSD.integer)))
        elif isinstance(value, float):
            g.add((uri, prop_uri, Literal(value, datatype=XSD.double)))
        else:
            g.add((uri, prop_uri, Literal(str(value))))
    
    return uri