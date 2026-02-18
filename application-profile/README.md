# Application profile

This folder contains the **application profile** for the Agriculture Image Metadata model.

- `application_profile.xlsx`: working spreadsheet (authoring format)
- `generate_shacl_ontology.py`: helper script to generate the ontology/shapes
- `shapes.ttl`: SHACL shapes (validation constraints) derived from the profile

## Notes

- Prefer referencing existing vocabularies first; only add minimal local extensions where needed (see `ontology-extension/`).
- When editing shapes in WebProtégé, SHACL shapes typically show up under **Individuals** (instances of `sh:NodeShape`).


