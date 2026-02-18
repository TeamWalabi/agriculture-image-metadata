#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""
generate_complete.py
Run from the 'application-profile' directory.

Features:
- In-memory Excel normalization (no file is overwritten):
    * Fix 'agri-images' -> 'agri-image' in URIs
    * Remove/replace 'newont:' with your base prefix
    * Normalize class local-names to CamelCase (plot->Plot, sensor->Sensor, ...)
    * Map selected classes to authoritative vocabs:
        Dataset  -> dcat:Dataset
        Platform -> sosa:Platform
        Sensor   -> sosa:Sensor
- Generate OWL/RDF ontology (ontology.ttl)
- Generate SHACL shapes (shapes.ttl)
- Prefix compacting everywhere

USAGE (from within application-profile/):
    python3 generate_complete.py \
      --input application_profile.xlsx \
      --onto ontology.ttl \
      --shacl shapes.ttl \
      --base-ns https://w3id.org/agri-image/ \
      --base-prefix agimage \
      [--add-codelists]    # optional: build SKOS from allowedValues
      [--emit-external-class-blocks]   # optional: emit owl:Class for dcat/sosa
"""

import argparse
import math
import pandas as pd

# -------------------------------
# CLI
# -------------------------------
def parse_args():
    p = argparse.ArgumentParser(description="Normalize Excel (in-memory) and generate Ontology + SHACL.")
    p.add_argument("--input", "-i", default="application_profile.xlsx", help="Excel file in current dir")
    p.add_argument("--onto", "-o", default="ontology.ttl", help="Output ontology TTL")
    p.add_argument("--shacl", "-s", default="shapes.ttl", help="Output SHACL TTL")
    p.add_argument("--base-ns", default="https://w3id.org/agri-image/", help="Base namespace for your terms")
    p.add_argument("--base-prefix", default="agimage", help="Base prefix label")
    p.add_argument("--add-codelists", action="store_true", help="Emit SKOS from allowedValues in ontology")
    p.add_argument("--emit-external-class-blocks", action="store_true",
                   help="Also emit owl:Class blocks for mapped external classes (dcat/sosa)")
    return p.parse_args()

# -------------------------------
# Helpers
# -------------------------------
def is_nan(v):
    return v is None or (isinstance(v, float) and math.isnan(v))

def safe_literal(s):
    if s is None:
        return ""
    s = str(s)
    return s.replace('"', '\\"')

def build_prefix_map(base_ns: str, base_prefix: str):
    return {
        "owl":   "http://www.w3.org/2002/07/owl#",
        "rdf":   "http://www.w3.org/1999/02/22-rdf-syntax-ns#",
        "rdfs":  "http://www.w3.org/2000/01/rdf-schema#",
        "xsd":   "http://www.w3.org/2001/XMLSchema#",
        "skos":  "http://www.w3.org/2004/02/skos/core#",
        "dct":   "http://purl.org/dc/terms/",
        "dcat":  "http://www.w3.org/ns/dcat#",
        "foaf":  "http://xmlns.com/foaf/0.1/",
        "sosa":  "http://www.w3.org/ns/sosa/",
        "ssn":   "http://www.w3.org/ns/ssn/",
        "unit":  "https://qudt.org/vocab/unit/",
        "exif":  "https://exiftool.org/TagNames/EXIF.html#",
        base_prefix: base_ns.rstrip("/") + "/",
        # DO NOT include 'newont' on purpose, we normalize it away.
    }

def ttl_prefix_header(pmap: dict, base_ns: str) -> str:
    lines = []
    for pfx, ns in pmap.items():
        end = "" if ns.endswith(("#", "/")) else "/"
        lines.append(f"@prefix {pfx}: <{ns}{end}> .")
    lines.append(f"\n<{base_ns}> a owl:Ontology .\n")
    return "\n".join(lines) + "\n"

def compact_curie(value: str, prefix_map: dict) -> str:
    """ Compact absolute URIs to CURIEs. Keep CURIEs; fallback to <...>. """
    if value is None:
        return None
    v = str(value).strip()
    if not v:
        return v
    if ":" in v and not v.startswith(("http://", "https://")):
        # already a CURIE with a known prefix?
        pfx = v.split(":", 1)[0]
        if pfx in prefix_map:
            return v
        # unknown prefix -> map to base (handled later)
        return v

    if v.startswith("<") and v.endswith(">"):
        v = v[1:-1].strip()

    for pfx, ns in prefix_map.items():
        ns_eff = ns if ns.endswith(("#", "/")) else ns + "/"
        if v.startswith(ns_eff):
            local = v[len(ns_eff):]
            if not local:
                return f"<{v}>"
            return f"{pfx}:{local}"

    if v.startswith(("http://", "https://")):
        return f"<{v}>"
    return v

# Excel → authoritative class mapping
CLASS_MAP = {
    "Dataset":  "dcat:Dataset",
    "Platform": "sosa:Platform",
    "Sensor":   "sosa:Sensor",
}

# Normalize local class names to CamelCase
LOCAL_CLASS_NORMALIZATION = {
    "plot": "Plot",
    "crop": "Crop",
    "camera": "Camera",
    "sensor": "Sensor",
    "platform": "Platform",
    "image": "Image",
    "field": "Field",
    "dataset": "Dataset",
}

def normalize_local_class(local: str) -> str:
    if not local:
        return local
    if local in LOCAL_CLASS_NORMALIZATION:
        return LOCAL_CLASS_NORMALIZATION[local]
    # If it looks lowercase but not in map, capitalize first letter
    return local[:1].upper() + local[1:] if local[:1].islower() else local

def normalize_class_like(s: str, base_prefix: str, pmap: dict) -> str:
    """
    Normalize class-like strings from Excel:
      - 'newont:plot'  -> base_prefix:Plot
      - 'plot'         -> base_prefix:Plot
      - 'Plot'         -> base_prefix:Plot
      - 'Sensor'       -> sosa:Sensor (mapped)
      - absolute URIs  -> compact to CURIE
      - existing CURIE with unknown prefix -> remap to base
    """
    if not s:
        return None
    s = str(s).strip()

    # explicit external mapping
    if s in CLASS_MAP:
        return CLASS_MAP[s]

    # CURIE?
    if ":" in s and not s.startswith(("http://", "https://")):
        pfx, local = s.split(":", 1)
        local = normalize_local_class(local)
        if pfx in ("newont", base_prefix):
            return f"{base_prefix}:{local}"
        if pfx in pmap:
            return f"{pfx}:{local}"
        # unknown prefix -> remap to base
        return f"{base_prefix}:{local}"

    # Absolute URI
    if s.startswith(("http://", "https://")):
        return compact_curie(s, pmap)

    # Bare local class name
    local = normalize_local_class(s)
    if local in CLASS_MAP:
        return CLASS_MAP[local]
    return f"{base_prefix}:{local}"

def normalize_uri(value: str) -> str:
    """ Fix 'agri-images' -> 'agri-image' typos inside URIs. """
    if value is None:
        return value
    v = str(value)
    return v.replace("w3id.org/agri-images", "w3id.org/agri-image")

def parse_allowed_values(s):
    """Parse allowedValues from "['a','b']" or simple CSV "a,b,c" to list."""
    if not isinstance(s, str):
        return []
    txt = s.strip()
    if not txt:
        return []
    # Normalize common patterns
    txt = txt.replace("[", "").replace("]", "").replace("'", "")
    parts = [p.strip() for p in txt.split(",") if p.strip()]
    return parts

# -------------------------------
# EXCEL NORMALISATION
# -------------------------------
def load_and_normalize_excel(path: str, base_prefix: str, base_ns: str, pmap: dict) -> pd.DataFrame:
    df = pd.read_excel(path, engine="openpyxl")

    # Bulk string replace: 'agri-images' -> 'agri-image' in all string cells
    df = df.applymap(lambda v: normalize_uri(v) if isinstance(v, str) else v)

    # Normalize 'datatype' column (class-like for object properties, datatypes for datatype props)
    if "datatype" in df.columns:
        def _norm_dtype(row):
            dtype = row.get("datatype")
            ptype = str(row.get("type")).strip().lower() if not is_nan(row.get("type")) else ""
            if is_nan(dtype):
                return dtype
            val = str(dtype).strip()

            # For object properties, datatype stands for target CLASS
            if ptype == "object":
                return normalize_class_like(val, base_prefix, pmap)

            # For datatype properties, keep xsd/rdf/rdfs* compact; otherwise compact or leave
            if val.startswith(("xsd:", "rdf:", "rdfs:")):
                return val
            return compact_curie(val, pmap)

        df["datatype"] = df.apply(_norm_dtype, axis=1)

    # Normalize 'entity' names only for usage as domain classes later (domain will use mapping)
    if "entity" in df.columns:
        df["entity"] = df["entity"].apply(lambda e: normalize_local_class(str(e).strip()) if not is_nan(e) else e)

    # Normalize 'uri' (paths): fix typos + compact later during generation
    if "uri" in df.columns:
        df["uri"] = df["uri"].apply(lambda u: normalize_uri(u) if not is_nan(u) else u)

    # Clean allowedValues formatting
    if "allowedValues" in df.columns:
        df["allowedValues"] = df["allowedValues"].apply(lambda s: normalize_uri(s) if isinstance(s, str) else s)

    return df

# -------------------------------
# ONTOLOGY GENERATOR
# -------------------------------
def build_ontology(df: pd.DataFrame, onto_path: str, base_prefix: str, base_ns: str,
                   pmap: dict, add_codelists: bool, emit_external_class_blocks: bool):
    ttl = []
    ttl.append(ttl_prefix_header(pmap, base_ns))

    emitted_classes = set()
    entities = [str(e).strip() for e in df["entity"].dropna().unique()]

    # Emit classes ONLY for non-mapped entities (avoid duplicating dcat/sosa)
    for entity in entities:
        class_curie = normalize_class_like(entity, base_prefix, pmap)
        if entity in CLASS_MAP and not emit_external_class_blocks:
            continue
        if class_curie in emitted_classes:
            continue
        # Use only rdfs:label; avoid injecting property descriptions into class comments
        ttl.append(f"{class_curie} a owl:Class ;")
        ttl.append(f'    rdfs:label "{safe_literal(entity)}" ;')
        ttl.append("    .\n")
        emitted_classes.add(class_curie)

    # Properties
    for _, row in df.iterrows():
        entity = str(row.get("entity")).strip() if not is_nan(row.get("entity")) else ""
        if not entity:
            continue

        # Domain class (mapped)
        domain_curie = normalize_class_like(entity, base_prefix, pmap)

        # Property path
        raw_prop_uri = row.get("uri")
        if is_nan(raw_prop_uri) or not str(raw_prop_uri).strip():
            continue
        prop_curie = compact_curie(str(raw_prop_uri).strip(), pmap)

        label = None if is_nan(row.get("property")) else str(row.get("property")).strip()
        comment = None if is_nan(row.get("description")) else str(row.get("description")).strip()
        example = None if is_nan(row.get("example")) else row.get("example")

        ptype = str(row.get("type")).strip().lower() if not is_nan(row.get("type")) else ""
        dtype_raw = None if is_nan(row.get("datatype")) else str(row.get("datatype")).strip()

        if ptype == "object":
            range_curie = normalize_class_like(dtype_raw, base_prefix, pmap) if dtype_raw else None
            ttl.append(f"{prop_curie} a owl:ObjectProperty ;")
            ttl.append(f"    rdfs:domain {domain_curie} ;")
            if range_curie:
                ttl.append(f"    rdfs:range {range_curie} ;")
            if label:
                ttl.append(f'    rdfs:label "{safe_literal(label)}" ;')
            if comment:
                ttl.append(f'    rdfs:comment "{safe_literal(comment)}" ;')
            if example not in (None, ""):
                ttl.append(f'    rdfs:comment "Example: {safe_literal(example)}" ;')
            ttl.append("    .\n")

        elif ptype == "datatype":
            # Range is a datatype (xsd:* etc.) or URI
            range_term = None
            if dtype_raw:
                if dtype_raw.startswith(("xsd:", "rdf:", "rdfs:")):
                    range_term = dtype_raw
                else:
                    range_term = compact_curie(dtype_raw, pmap)

            ttl.append(f"{prop_curie} a owl:DatatypeProperty ;")
            ttl.append(f"    rdfs:domain {domain_curie} ;")
            if range_term:
                ttl.append(f"    rdfs:range {range_term} ;")
            if label:
                ttl.append(f'    rdfs:label "{safe_literal(label)}" ;')
            if comment:
                ttl.append(f'    rdfs:comment "{safe_literal(comment)}" ;')
            if example not in (None, ""):
                ttl.append(f'    rdfs:comment "Example: {safe_literal(example)}" ;')
            ttl.append("    .\n")

        # Optional: SKOS codelist per property
        if add_codelists and "allowedValues" in row and not is_nan(row["allowedValues"]) and label:
            vals = parse_allowed_values(str(row["allowedValues"]))
            if vals:
                scheme = f"{base_prefix}:{label}Scheme"
                ttl.append(f"{scheme} a skos:ConceptScheme ;")
                ttl.append(f'    skos:prefLabel "{safe_literal(label)} controlled vocabulary" .\n')
                for v in vals:
                    local = str(v).strip().replace(" ", "_").replace("/", "_").replace(":", "_").replace(",", "_")
                    cid = f"{base_prefix}:{label}_{local}"
                    ttl.append(f"{cid} a skos:Concept ;")
                    ttl.append(f"    skos:inScheme {scheme} ;")
                    ttl.append(f'    skos:prefLabel "{safe_literal(v)}" .\n')

    with open(onto_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ttl))

# -------------------------------
# SHACL GENERATOR
# -------------------------------
def build_shacl(df: pd.DataFrame, shacl_path: str, base_prefix: str, base_ns: str, pmap: dict):
    ttl = []
    # SHACL prefixes
    header = []
    for pfx, ns in {**pmap, **{"sh": "http://www.w3.org/ns/shacl#"}}.items():
        end = "" if ns.endswith(("#", "/")) else "/"
        header.append(f"@prefix {pfx}: <{ns}{end}> .")
    header.append("")
    ttl.append("\n".join(header))

    # One NodeShape per entity
    for entity in df["entity"].dropna().unique():
        en = str(entity).strip()
        if not en:
            continue
        target_class = normalize_class_like(en, base_prefix, pmap)
        shape_name = f"{base_prefix}:{en}Shape"
        ttl.append(f"{shape_name} a sh:NodeShape ;")
        ttl.append(f"    sh:targetClass {target_class} ;\n")

        subset = df[df["entity"] == en]
        for _, row in subset.iterrows():
            path_raw = row.get("uri")
            if is_nan(path_raw) or not str(path_raw).strip():
                continue
            path = compact_curie(str(path_raw).strip(), pmap)

            ptype = str(row.get("type")).strip().lower() if not is_nan(row.get("type")) else ""
            dtype_raw = None if is_nan(row.get("datatype")) else str(row.get("datatype")).strip()

            ttl.append("    sh:property [")
            ttl.append(f"        sh:path {path} ;")

            if ptype == "datatype":
                dtype = dtype_raw or ""
                if dtype.startswith(("xsd:", "rdf:", "rdfs:")):
                    ttl.append(f"        sh:datatype {dtype} ;")
                else:
                    ttl.append(f"        sh:datatype {compact_curie(dtype, pmap)} ;")
            elif ptype == "object":
                ttl.append(f"        sh:class {normalize_class_like(dtype_raw, base_prefix, pmap)} ;")
            else:
                # unknown, skip block cleanly
                ttl.pop()  # remove sh:property [
                ttl.pop()  # remove sh:path ...
                continue

            # cardinalities
            minc = row.get("cardinalityMin")
            maxc = row.get("cardinalityMax")
            try:
                if not is_nan(minc):
                    ttl.append(f"        sh:minCount {int(float(minc))} ;")
            except Exception:
                pass
            try:
                if not is_nan(maxc) and str(maxc).strip() != "*":
                    ttl.append(f"        sh:maxCount {int(float(maxc))} ;")
            except Exception:
                pass

            # description / example
            desc = None if is_nan(row.get("description")) else str(row.get("description")).strip()
            ex = None if is_nan(row.get("example")) else str(row.get("example")).strip()
            if desc:
                ttl.append(f'        sh:description "{safe_literal(desc)}" ;')
            if ex:
                ttl.append(f'        sh:example "{safe_literal(ex)}" ;')

            # allowed values -> sh:in
            allowed = None if is_nan(row.get("allowedValues")) else str(row.get("allowedValues")).strip()
            vals = parse_allowed_values(allowed) if allowed else []
            if vals:
                inlist = " ".join(f"\"{safe_literal(v)}\"" for v in vals)
                ttl.append(f"        sh:in ( {inlist} ) ;")

            ttl.append("    ] ;\n")

        ttl.append("    .\n")

    with open(shacl_path, "w", encoding="utf-8") as f:
        f.write("\n".join(ttl))

# -------------------------------
# MAIN
# -------------------------------
def main():
    args = parse_args()
    base_ns = args.base_ns.rstrip("/") + "/"
    pmap = build_prefix_map(base_ns, args.base_prefix)

    # 1) Load & normalize Excel in-memory
    df = load_and_normalize_excel(args.input, args.base_prefix, base_ns, pmap)

    # 2) Generate ontology (prefix-compacted, mapped classes, no duplicates)
    build_ontology(df, args.onto, args.base_prefix, base_ns, pmap,
                   add_codelists=args.add_codelists,
                   emit_external_class_blocks=args.emit_external_class_blocks)

    # 3) Generate SHACL shapes (prefix-compacted, mapped classes)
    build_shacl(df, args.shacl, args.base_prefix, base_ns, pmap)

    print("[OK] Normalization + Ontology + SHACL generated")
    print(f"[OK] Ontology: {args.onto}")
    print(f"[OK] SHACL:    {args.shacl}")
    print(f"[OK] Prefix:   {args.base_prefix}  Namespace: {base_ns}")

if __name__ == "__main__":
    main()
