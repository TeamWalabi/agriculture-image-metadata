from __future__ import annotations

from pathlib import Path
from typing import Any
import datetime
import warnings
from typing import Iterable, Sequence, Optional
import datetime

from rdflib import Graph, Namespace, RDF, RDFS, OWL, XSD, Literal
from typing import get_origin, get_args


def create_sensor_dir(root_folder, dataset_name, raw_data, field_id, plot_id, machine_id, cam_id, add_date_subfolder=False):
    """Create directory structure for sensor data."""
    # dataset_name / raw_data / field_id / plot_id / machine_id / cam_id / YYYYMMDD
    dir_path = Path(root_folder) / dataset_name / raw_data / field_id / plot_id / machine_id / cam_id 
    if add_date_subfolder:
        date_str  = datetime.datetime.now().strftime("%Y%m%d")
        dir_path = dir_path / date_str
    if not dir_path.exists():
        dir_path.mkdir(parents=True, exist_ok=True)
    return dir_path


def create_all_output_dirs(root_folder, metadata, raw_data="raw_data"):
    """Create all necessary directories based on metadata."""
    dataset_name = metadata.dataset.identifier

    created_dirs = {}
    for field in metadata.fields:
        for plot in field.plots:
            for machine in metadata.machines:
                for sensor in machine.sensors:
                    cam_id = sensor.camera_id
                    dir_path = create_sensor_dir(root_folder, dataset_name, raw_data, field.field_id, plot.plot_id, machine.machine_id, cam_id)
                    created_dirs[(plot.plot_id, machine.machine_id, cam_id)] = dir_path
    return created_dirs

def get_strftime(image_timestamp: datetime | str, bool_filename=False):
    "function to get convert datetime to string, use bool_file name to remove any : ."
    if isinstance(image_timestamp, datetime.datetime):
        # Format: ISO8601 with milliseconds -> YYYYMMDDTHHMMSSZmilliseconds
        if bool_filename: ## for file names you do not want to use .
            timestamp_str = image_timestamp.strftime("%Y%m%dT%H%M%S") + f"{image_timestamp.microsecond // 1000:03d}"+"Z"
        else:
            timestamp_str = image_timestamp.strftime("%Y-%m-%dT%H:%M:%S.") + f"{image_timestamp.microsecond // 1000:03d}"+"Z"
        # timestamp_str = image_timestamp.strftime("%Y-%m-%dT%H:%M:%SZ")# + f"{image_timestamp.microsecond // 1000:03d}"+"Z"
    else:
        timestamp_str = str(image_timestamp)
    return timestamp_str


def get_strptime(image_timestamp: str | datetime.datetime, from_filename=False):
    """
    Convert string to datetime
    args:
    image_timstamp: (str): "20250620150820111Z
    from_filename: (bool) if true will use "%Y%m%dT%H%M%SZ"
    """
    if isinstance(image_timestamp, datetime.datetime):
        return image_timestamp

    if from_filename:
        # YYYYMMDDTHHMMSSmillisecondsZ
        base, millis = image_timestamp[:-4], image_timestamp[-4:-1]
        fmt = "%Y%m%dT%H%M%SZ"
        return datetime.datetime.strptime(base, fmt).replace(microsecond=int(millis) * 1000)
    else:
        try:
            fmt = "%Y-%m-%dT%H:%M:%S.%fZ"
            return datetime.datetime.strptime(image_timestamp, fmt)
            # YYYY-MM-DD-THH:MM:SS.millisecondsZ
            indexi = image_timestamp.index(".")

            base, millis = image_timestamp[:-4], image_timestamp[-4:-1]
            return datetime.datetime.strptime(base, fmt).replace(microsecond=int(millis) * 1000)
        except:
            image_timestamp = image_timestamp[::-1].zfill(19)[::-1]
            base, millis = image_timestamp[:-3], image_timestamp[-3:]
            fmt = "%Y%m%dT%H%M%SZ"
            return datetime.datetime.strptime(base, fmt).replace(microsecond=int(millis) * 1000)

    # # if isinstance(image_timestamp, datetime):
    # #     return image_timestamp

    # index = image_timestamp.index("Z")+1

    # base, millis = image_timestamp[:index], image_timestamp[index:]
    # fmt = "%Y%m%dT%H%M%SZ"
    # return datetime.datetime.strptime(base, fmt).replace(microsecond=int(millis) * 1000)


def get_image_name(image_timestamp, camid, trigger_number, channel="rgb", extension=".png"):
    """Generate image name based on timestamp, camera ID, trigger number, and channel."""
    timestamp_str = get_strftime(image_timestamp)

    image_name = f"{timestamp_str}_camid{camid}_trigger{trigger_number:06d}_{channel.lower()}{extension}"
    return image_name



def _parse_metadata_timestamp(value: str | datetime) -> datetime:
    if isinstance(value, datetime):
        return value

    if value[-4].endswith("Z") and len(value) >= 19:
        base, millis = value[:-3], value[-3:]
        fmt = "%Y%m%dT%H%M%SZ"
        return datetime.strptime(base, fmt).replace(microsecond=int(millis) * 1000)

    return datetime.fromisoformat(value)
