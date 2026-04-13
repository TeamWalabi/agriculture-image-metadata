from typing import List, Optional, Dict, Type, TypeVar
from pathlib import Path
import json
from pydantic import BaseModel

from metadata_vision.schemas.dataset import DatasetMetadata
from ruamel.yaml import YAML

T = TypeVar("T", bound=BaseModel)


def load_dataset(file_path: str | Path, mapping: Optional[Dict] = None) -> DatasetMetadata:
    """
    Load a complete DatasetMetadata from a unified JSON file.

    Expected JSON structure:
    {
        "dataset": {
            "title": "...",
            "identifier": "...",
            "creator": {...},
            "hasField": [...],
            "hasPlatform": {...},
            "hasImage": [...]
        }
    }

    Args:
        file_path: Path to unified dataset JSON or YAML file
        mapping: Optional ontology mapping dictionary to remap field names

    Returns:
        DatasetMetadata object
    """
    file_path = Path(file_path)

    if file_path.suffix.lower() == ".json":
        with open(file_path, "r") as f:
            data = json.load(f)
    elif file_path.suffix.lower() == ".yaml" or file_path.suffix.lower() == ".yml":
        with open(file_path, "r") as f:
            data = YAML().load(f)
    else:
        raise ValueError(f"Unsupported file format: {file_path.suffix}")

    dataset_data = data.get("dataset", data)

    if mapping:
        dataset_data = {mapping.get(k, k): v for k, v in dataset_data.items()}

    return DatasetMetadata(**dataset_data)


def load_metadata(
    list_of_paths: List[str], model_class: Type[T], mapping: Optional[Dict] = None
) -> List[T]:
    """
    Generic loader for any Pydantic metadata model from JSON or yaml filesfiles.

    Args:
        list_of_paths: List of paths to json or yaml metadata files
        model_class: Pydantic model class to instantiate: for example ImageMetadata
        mapping: Optional ontology mapping dictionary to remap field names

    Returns:
        List of instantiated model objects
    """
    instances = []
    for file_path in list_of_paths:
        if file_path.suffix.lower() == ".json":
            with open(file_path, "r") as f:
                data = json.load(f)
        elif file_path.suffix.lower() == ".yaml" or file_path.suffix.lower() == ".yml":
            with open(file_path, "r") as f:
                data = YAML().load(f)
        else:
            raise ValueError(f"Unsupported file format: {file_path.suffix}")

        if mapping:
            mapped_data = {mapping.get(k, k): v for k, v in data.items()}
        else:
            mapped_data = data
        mapped_data["imagePath"] = file_path
        instances.append(model_class(**mapped_data))
    return instances
