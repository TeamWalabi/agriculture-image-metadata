# Agriculture Image Metadata

A Linked Data–based metadata model for agricultural image data.

This repository provides an **application profile** and supporting resources for describing **images**, **observations**, and **contextual metadata** across agricultural domains (greenhouse, open field, arable crops, horticulture, phenotyping).

The goal is to offer a **lightweight, interoperable, FAIR‑friendly** schema that leverages existing ontologies and codelists, while adding only minimal project‑specific extensions where necessary.

## Objectives

- **Define consistent metadata** for agricultural image datasets.
- **Reference existing ontologies** (e.g., PROV‑O, SOSA/SSN, ENVO, schema.org) rather than duplicating concepts.
- **Structure metadata using Linked Data principles** with URIs, relationships, and reusable concepts.
- **Provide a clear hierarchy** connecting plants, observations, images, equipment, and context.
- **Support FAIR, reusable, traceable datasets** for research and machine‑learning workflows.
- **Allow lightweight project extensions** when no suitable ontology concept exists.

## Repository structure

```text
application-profile/
  metadata-profile.xlsx
  metadata-profile.ttl

ontology-extension/
  agriculture-image-extension.ttl

examples/
  example-image-metadata.jsonld
  example-image-metadata.ttl

docs/
  explanation.md
  vocabulary-links.md

LICENSE
```

## Ontologies & vocabularies used

This project does **not** create new codelists. It references established vocabularies such as:

- **PROV‑O** (provenance)
- **SOSA/SSN** (sensors, observations)
- **ENVO** (environment, locations)
- **schema.org** (general metadata)
- **External authoritative codelists** for varieties, growth stages, etc.

Missing concepts are added only as **minimal local extensions**.

## What this model describes

- **Image capture events**
- **Plant, plot, or object** being imaged
- **Locations** (greenhouse compartments, field sections, coordinates)
- **Camera, lens, and operator** identifiers
- **Experimental or observational context**
- Links to **external identifiers** (varieties, treatments, genotypes, etc.)

## Examples

See the `examples/` folder for JSON-LD and Turtle examples that show how an image and its context can be expressed.

## How to use

- Reuse the fields from the **application profile**.
- Represent metadata using **JSON-LD** or **RDF Turtle**.
- Refer to **external ontologies** wherever possible.
- Use terms from the **local extension** only if no external concept fits.
- Validate data using **SHACL** or the provided examples.

## License

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. See `LICENSE`.

You may use, modify, and distribute the contents as long as you provide attribution.

## Contributing

Suggestions and pull requests are welcome, especially for improving ontology mappings or adding reusable examples.

## Contact

- **Bart van Marrewijk & Joep Tummers**
- **Wageningen Research**
- **Email**: walabi.wser@wur.nl
