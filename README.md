# Agriculture Image Metadata

A Linked Data–based metadata model for agricultural image data.

This repository provides an **ontology** for image dataset in agricultural domains (greenhouse, open field, arable crops, horticulture, phenotyping).

The goal is to offer a **lightweight, interoperable, FAIR‑friendly** schema that leverages existing ontologies and codelists, while adding only minimal project‑specific extensions where necessary.

## Canonical namespace & hosting

- **Namespace**: `https://w3id.org/agri-image/`
- **Ontology**: `ontology/ontology.ttl` will be hosted at `https://w3id.org/agri-image`


## Repository structure

```text
## examples
├── examples 
│   ├── custom_dataset_example.py
│   ├── filtering_class_based.py
│   ├── filtering_query_based.py
│   ├── your_custom_dataset.json
│   └── your_custom_dataset.yaml
├── metadata_vision ## Package for loading etc
...
├── ontology
│   ├── dummy_dataset_output.json
│   ├── dummy_dataset_output.ttl
│   └── ontology.ttl
LICENSE
```

# Metadata Structure
The idea is to create a dataset that can consist of:
- fields: consisting of
    -  plots/rows
        - which have crops and weeds
        - properties of:
            - soilType
            - surfaceLayer
            - weatherConditions
Data is collected by a machine/platform
- platform: has sensors:
    - Camera: unique cam_id and properties
    - Lidar: *To be implemented in near future*
    - GPS: *To be implemented in near future*
- images: list of images which links to field, plot, platform and sensors


```python
# DatasetMetadata(RDFModel)
#     hasField: list[FieldMetadata] | FieldMetadata
    # hasPlot: PlotMetadata
    # plot.hasCrop: CropMetadata | list[CropMetadata]
    # plot.hasWeed: CropMetadata | list[CropMetadata]
    # platform: PlatformMetadata list[PlatformMetadata] 
    # platform.hasSensor: list[CameraMetadata] | CameraMetadata]
    # images: ImageMetadata | list[ImageMetadata]
```

## Install for deployment
```python
pip install .
```

## Folder structure for deployment
We recommend following folder structure:
```bash
dataset_name / raw_data / field_id / plot_id / platform_id / cam_id / optional[YYYYMMDD]
# although for some projects it make sense to use:
dataset_name / raw_data / field_id / plot_id / platform_id / YYYYMMDD / cam_id
## inside the folder cam_id you have
## XXX.png files and XXX.metadata.json files describing ImageMetadata
# to facilitate with the folder structure have a look at utils.file_system.py
```

This looks complicated but this make is ideal for:
- Timeseries
- Drone data with field and plots
- Multiple machines on a field.
- Machine is flexibile can be a:
    - harvesting robot
    - data platform
    - or in a greenhouse an device which has multiple camera's sensors

# Recreate ontology
To recreate the ontology:
```bash
python3 metadata_vision/create_ontology.py
```

## Commit / validating:
Install aditional packages
```bash

pip install -e .[test]
## validate if everything is working correctly with
pytest tests/
```

## License

This project is licensed under the **Creative Commons Attribution 4.0 International (CC BY 4.0)** license. See `LICENSE`.

You may use, modify, and distribute the contents as long as you provide attribution.

## Contributing

Suggestions and pull requests are welcome, especially for improving ontology mappings or adding reusable examples.

## Contact

- **Bart van Marrewijk & Joep Tummers**
- **Wageningen Research**
- **Email**: bart.vanmarrewijk@wur.nl
