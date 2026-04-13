"""
Example script to load a set of images and apply some class based filtering
"""

import json
from pathlib import Path
from agri_image_meta.schemas.images import ImageMetadata
from agri_image_meta.utils.file_system import get_strptime
import numpy as np
from typing import Iterable, Sequence, Optional
import datetime

import shutil


class ImageMetadataIterator:
    def __init__(self, images: Sequence[ImageMetadata]):
        self._images = images
        self._index = 0

    def __iter__(self):
        self._index = 0
        return self

    def __next__(self):
        if self._index >= len(self._images):
            raise StopIteration
        img = self._images[self._index]
        self._index += 1
        return img

    def __len__(self):
        return len(self._images)

    def reset(self):
        self._index = 0

    def filter(self, **kwargs) -> "ImageMetadataIterator":
        filtered = filter_image_metadata(self._images, **kwargs)
        self._images = filtered
        self._index = 0

    def get_lowest_image_number(self) -> Optional[int]:
        if not self._images:
            return None
        return min(img.imageNumber for img in self._images)

    def get_highest_image_number(self) -> Optional[int]:
        if not self._images:
            return None
        return max(img.imageNumber for img in self._images)

    def get_lowest_image_timestamp(self) -> Optional[str]:
        if not self._images:
            return None
        return min(img.imageTimestamp for img in self._images)

    def get_highest_image_timestamp(self) -> Optional[str]:
        if not self._images:
            return None
        return max(img.imageTimestamp for img in self._images)

    def get_lowest_base_xyz(self, axis=0) -> Optional[list]:
        if not self._images:
            return None
        return min(img.baseXYZ[axis] for img in self._images)

    def get_highest_base_xyz(self, axis=0) -> Optional[list]:
        if not self._images:
            return None
        return max(img.baseXYZ[axis] for img in self._images)

    def get_by_trigger_number(self, image_number) -> Optional[list]:
        if not self._images:
            return None
        matches = [img for img in self._images if img.imageNumber == image_number]
        return sorted(matches, key=lambda img: img.cameraID)

    def get_unique_trigger_numbers(self) -> list:
        if not self._images:
            return []
        return sorted(set(img.imageNumber for img in self._images))

    def write_to_nerfstudio(
        self,
        intrinsics: dict,
        distortion: dict,
        image_dir: Path,
        h=4000,
        w=6000,
        output_dir: Path = Path(),
    ):
        applied_transform = np.zeros((3, 4), dtype=float)
        applied_transform[:3, :3] = np.eye(3)

        dummy_dict = {
            "camera_model": "OPENCV",  # OPENCV_FISHEYE
            "orientation_override": "none",
            "ply_file_path": None,
            "frames": [],
            # "applied_transform": applied_transform
        }
        frame_dummy_dict = {
            "h": h,
            "w": w,
            "file_path": "images/frame_00013.jpg",
            "fl_x": 8040.868955733327,
            "fl_y": 8040.868955733327,
            "cx": 2871.297397247967,
            "cy": 1945.1464830148566,
            "k1": 0.0312,  # first radial distortion parameter, used by [OPENCV, OPENCV_FISHEYE]
            "k2": 0.0051,  # second radial distortion parameter, used by [OPENCV, OPENCV_FISHEYE]
            "k3": 0.0006,  # third radial distortion parameter, used by [OPENCV_FISHEYE]
            "k4": 0.0001,  # fourth radial distortion parameter, used by [OPENCV_FISHEYE]
            "p1": -6.47e-5,  # first tangential distortion parameter, used by [OPENCV]
            "p2": -1.37e-7,  # second tangential distortion parameter, used by [OPENCV]
            "transform_matrix": [
                [0.710919248029843, -0.6504965031692165, -0.26729781545179904, -18.60046131462555],
                [0.5525689096894804, 0.7517714188488636, -0.35987127399466795, -21.85140183746417],
                [0.4350418633019832, 0.10813895304925038, 0.8938929152913959, 59.52254831852292],
                [0.0, 0.0, 0.0, 1.0],
            ],
            # "mask_path": "mask/0012_0_12.png"
        }
        frames = []
        for tmp in self._images:
            tmp_frame = frame_dummy_dict.copy()
            tmp_intrinsic = intrinsics[tmp.cameraID]
            tmp_frame["fl_x"] = tmp_intrinsic[0][0]
            tmp_frame["cx"] = tmp_intrinsic[0][2]
            tmp_frame["fl_y"] = tmp_intrinsic[1][1]
            tmp_frame["cy"] = tmp_intrinsic[1][2]

            tmp_distortion = distortion[tmp.cameraID]
            tmp_frame["k1"] = tmp_distortion[0]
            tmp_frame["k2"] = tmp_distortion[1]
            tmp_frame["k3"] = tmp_distortion[2]
            tmp_frame["k4"] = 0.0
            tmp_frame["p1"] = tmp_distortion[3] if len(tmp_distortion) > 3 else 0.0
            tmp_frame["p2"] = tmp_distortion[4] if len(tmp_distortion) > 4 else 0.0

            t = np.divide(tmp.baseXYZ, 1000) + tmp.imageXYZ
            import scipy

            R = scipy.spatial.transform.Rotation.from_quat(tmp.imageQuaternionXYZW).as_matrix()
            tf = np.array(tmp_frame["transform_matrix"])
            tf[:3, :3] = R
            tf[:3, 3] = t
            tmp_frame["transform_matrix"] = tf.tolist()

            tmp_frame["file_path"] = "images/" + tmp.imageName
            frames.append(tmp_frame)

        dummy_dict["frames"] = frames

        # nerfstudio output
        nerf_folder = output_dir / "images_nerfstudio"
        if not nerf_folder.exists():
            nerf_folder.mkdir()
        images_0 = nerf_folder / "images"
        if not images_0.exists():
            images_0.mkdir()

        images_4_folder = nerf_folder / "images_4"
        if not images_4_folder.exists():
            images_4_folder.mkdir()
        for img in self._images:
            img_path = image_dir / img.cameraID / img.imageName
            dst_path = images_0 / img.imageName
            if not dst_path.exists():
                shutil.copy(img_path, dst=dst_path)

            # image = cv2.imread(str(img_path))
            # resized = cv2.resize(image, (int(image.shape[1] * 0.25), int(image.shape[0] * 0.25)))
            # cv2.imwrite(str(images_4_folder / img.imageName), resized)

        with open(nerf_folder / "transforms.json", "w") as f:
            json.dump(dummy_dict, f, indent=2)


def filter_image_metadata(
    images: Iterable[ImageMetadata],
    *,
    camera_ids: Optional[np.ndarray[int]] = None,
    field_ids: Optional[Sequence[str]] = None,
    image_numbers: Optional[np.ndarray[int]] = None,
    earliest: Optional[datetime] = None,
    latest: Optional[datetime] = None,
) -> list[ImageMetadata]:
    if earliest and latest and earliest > latest:
        raise ValueError("earliest must be before latest")

    camera_set = set(camera_ids) if camera_ids else None
    field_set = set(field_ids) if field_ids else None

    def matches(img: ImageMetadata) -> bool:
        if camera_set and img.cameraID not in camera_set:
            return False
        if field_set and img.fieldID not in field_set:
            return False
        if image_numbers is not None and img.imageNumber not in image_numbers:
            return False

        timestamp = get_strptime(img.imageTimestamp)

        if earliest and timestamp < earliest:
            return False
        if latest and timestamp > latest:
            return False
        return True

    return [img for img in images if matches(img)]


if __name__ == "__main__":
    main_folder = Path(
        "/media/agro/PhDBart2/3742355900_agros2_komkommer/raw_data/field_001/row_01/demo_platform1/"
    )
    main_folder = Path(
        "/media/agro/PhDBart2/3742355900_agros2_komkommer/raw_data/field_001/row_01/20260226_demo_platform1/"
    )

    list_of_paths = main_folder.rglob("*metadata.json")
    from agri_image_meta.utils.dataset_loading import load_metadata
    from agri_image_meta.schemas.images import ImageMetadata

    mapping = {
        "image_name": "imageName",
        "image_timestamp": "imageTimestamp",
        "camera_id": "cameraID",
        "machine_id": "platformID",
        "field_id": "fieldID",
        "plot_id": "plotID",
        "exposure_time_s": "exposureTime",
        "image_number": "imageNumber",
        "image_xyz": "imageXYZ",
        "image_quaternion_xyzw": "imageQuaternionXYZW",
        "image_gnss": "imageGNSS",
        "base_xyz": "baseXYZ",
        "base_quaternion_xyzw": "baseQuaternionXYZW",
        "base_gnss": "baseGNSS",
    }

    images_dataset = load_metadata(list_of_paths, model_class=ImageMetadata, mapping=mapping)
    obj = ImageMetadataIterator(images_dataset)

    # obj.filter(image_numbers=np.arange(1603,1642))

    print("highest", obj.get_highest_image_number())
    print("lowest", obj.get_lowest_image_number())

    print("highest", obj.get_highest_base_xyz())
    print("lowest", obj.get_lowest_base_xyz())
