"""
Script to generate example yaml/json files
"""
import types
from pathlib import Path
from typing import Any, Dict, List, Optional, Union, get_args, get_origin

import json
from pydantic import BaseModel
from ruamel.yaml import YAML
from ruamel.yaml.comments import CommentedMap

def placeholder(ann):
    """Return a dummy value that passes validation for annotation *ann*."""
    origin = get_origin(ann) or ann
    if origin in (list, List):
        value = []
    elif origin in (dict, Dict):
        value = {}
    elif isinstance(origin, type) and issubclass(origin, Path):
        value = "."
    elif origin in (str, Optional[str]):
        value = ""
    elif origin in (int, Optional[int]):
        value = 0
    elif origin in (float, Optional[float]):
        value = 0.0
    elif origin in (bool, Optional[bool]):
        value = False
    else:
        value = None
    return value

def unwrap_optional(ann):
    if get_origin(ann) is Union and type(None) in get_args(ann):
        return next(a for a in get_args(ann) if not isinstance(a, type(None)))
    return ann

def extract(model: type[BaseModel]) -> Dict[str, Any]:
    data: Dict[str, Any] = {}
    for name, field in model.model_fields.items():
        if name == "rdf_type":
            continue
        ann = unwrap_optional(field.annotation)

        # Use example **unless it is None**
        if (
            isinstance(field.json_schema_extra, dict)
            and "example" in field.json_schema_extra
            and field.json_schema_extra["example"] is not None
        ):
            value = field.json_schema_extra["example"]

        # Nested Pydantic model(s)
        elif isinstance(ann, type) and issubclass(ann, BaseModel):
            value = extract(ann)
        elif (
            get_origin(ann) in (list, List)
            and get_args(ann)
            and isinstance(get_args(ann)[0], type)
            and issubclass(get_args(ann)[0], BaseModel)
        ):
            value = [extract(get_args(ann)[0])]
        else:
            value = placeholder(ann)

        data[name] = value
    return data

def generate_example(
    config_class: type[BaseModel],
    output_path: Path,
    to_disk_comments: bool = True,
    to_disk: bool = True,
) -> Dict:
    """Write a YAML file that instantiates `config_class` without errors."""

    example_data = extract(config_class)

    if to_disk_comments:
        save_dict_with_comments(config_class, example_data, output_path)
    elif to_disk:
        write_config_to_file(example_data, output_path)
    return example_data


def write_config_to_file(example_data: dict, output_path: Path) -> None:
    """Write the example data to a  or json depending on suffix file."""
    if output_path.suffix == ".json":
        with open(output_path, "w", encoding="utf-8") as fh:
            json.dump(example_data, fh, indent=2)
    else:
        with open(output_path, "w", encoding="utf-8") as fh:
            YAML().dump(example_data, fh)


def save_dict_with_comments(
    model_class: type[BaseModel], example_data: dict, output_path: Path
) -> None:
    """
    Save a dictionary as YAML, adding field descriptions as comments.
    """
    yaml = YAML()
    yaml.indent(mapping=2, sequence=4, offset=2)
    commented = CommentedMap()
    commented = lookp_loop(model_class, example_data, commented)
    with open(output_path, "w", encoding="utf-8") as fh:
        yaml.dump(commented, fh)


def lookp_loop(
    model_class: type[Any], example_data: dict, commented: CommentedMap
) -> CommentedMap:
    """
    Recursively process the model class and example data to add comments.
    """
    for name, value in example_data.items():
        commented[name] = value
        # solution for optional subclasses
        if (
            get_origin(model_class) is Union
            or get_origin(model_class) is types.UnionType
        ):
            args = [a for a in get_args(model_class) if not isinstance(a, type(None))]
            model_class = args[0] if args else model_class

        # Get the field description from the model class, if available
        field = model_class.model_fields.get(name)
        if field and field.description:
            commented.yaml_add_eol_comment(key=name, comment=field.description)
        elif isinstance(value, list) and value:
            # If the value is a list with items, process each item
            if isinstance(value[0], dict):
                ann = unwrap_optional(field.annotation)
                if get_origin(ann) in (list, List) and get_args(ann):
                    item_type = get_args(ann)[0]
                    commented[name] = [
                        lookp_loop(item_type, item, CommentedMap()) for item in value
                    ]
            # elif isinstance(value[0], list):
            #     # Handle nested lists recursively
            #     ann = unwrap_optional(field.annotation)
            #     if get_origin(ann) in (list, List) and get_args(ann):
            #         # This is a list of lists - process recursively
            #         print(value)
            #         commented[name] = value  # For now, keep as-is or implement deeper nesting logic
        elif isinstance(value, dict):
            # If the value is a dict, recursively process it
            commented[name] = lookp_loop(field.annotation, value, CommentedMap())
    return commented


if __name__ == "__main__":
    from metadata_vision.main import DatasetPackage

    ### save as yaml
    generate_example(
        DatasetPackage,
        Path(__file__).parent.parent / "example_config.yaml",
        to_disk_comments=False,
    )

    # with open(Path(__file__).parent.parent / "example_config_model_schema.yaml","w") as f:
    #     json.dump(DatasetPackage.model_json_schema(), f, indent=4)


    generate_example(
        DatasetPackage,
        Path(__file__).parent.parent / "example_config_comments.yaml",
        to_disk_comments=True,
    )

    ## save as json
    # generate_example(
    #     DatasetPackage,
    #     Path(__file__).parent / "example_config.json",
    #     to_disk_comments=False,
    # )
