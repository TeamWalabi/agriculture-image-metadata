from __future__ import annotations



from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal


AGIMAGE = Namespace("https://w3id.org/agri-image/")
DCT = Namespace("http://purl.org/dc/terms/")
SKOS = Namespace("http://www.w3.org/2004/02/skos/core#")
DCAT = Namespace("http://www.w3.org/ns/dcat#")
FOAF = Namespace("http://xmlns.com/foaf/0.1/")
SOSA = Namespace("http://www.w3.org/ns/sosa/")
SSN = Namespace("http://www.w3.org/ns/ssn/")
UNIT = Namespace("https://qudt.org/vocab/unit/")
EXIF = Namespace("https://exiftool.org/TagNames/EXIF.html#")
SH = Namespace("http://www.w3.org/ns/shacl#")

JSONLD_CONTEXT = {
    "dct": str(DCT),
    "dcat": str(DCAT),
    "sosa": str(SOSA),
    "ssn": str(SSN),
    "agimage": str(AGIMAGE),
    "exif": str(EXIF),
    "foaf": str(FOAF),
    "skos": str(SKOS),
    "unit": str(UNIT),
    "sh": str(SH),
}