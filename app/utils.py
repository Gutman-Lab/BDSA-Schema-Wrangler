# Utility / helper functions used in various other files.
from pathlib import Path
import pandas as pd
import cv2 as cv
import numpy as np
import large_image
from pathlib import Path
from time import sleep


def get_files_with_size(root_directory: str) -> list[dict]:
    """Get list of files with their sizes in a directory.

    Args:
        root_directory (str): The root directory to search for files.

    Returns:
        list[dict]: A list of dictionaries, each containing the file path, file size, and file name.

    """
    file_list = []

    path = Path(root_directory)

    for p in path.rglob("*"):
        if p.is_file():
            file_list.append(
                {
                    "filePath": str(p),
                    "fileSize": round(float(p.stat().st_size / (1024**3)), 2),
                    "fileName": p.name,
                }
            )

    return file_list


def get_csv_files(root_dir: str) -> list[dict]:
    """Get a list of CSV file names under a directory, and return the number of
    rows in each file.

    Args:
        root_dir (str): The root directory to search for CSV files.

    Returns:
        list[dict]: A list of dictionaries, each containing the file name and the
        number of rows in the file.

    """
    csv_dir_path = Path(root_dir)

    file_names = []

    for fp in csv_dir_path.glob("*.csv"):

        file_names.append({"fileName": fp.name, "fileLength": len(pd.read_csv(fp))})

    return file_names


def imwrite(fp: str, img: np.ndarray, grayscale: bool = False):
    """Write image to file.

    Args:
        fp: Filepath to save image.
        img: Image to save.
        grayscale: True to save image as a grayscale image, otherwise it is
            saved as an RGB image.

    """
    if grayscale:
        cv.imwrite(fp, img)
    else:
        cv.imwrite(fp, cv.cvtColor(img, cv.COLOR_RGB2BGR))


def deidentify_image(fp: str, save_fp: str):
    """De-identify an image and save it locally."""
    # Skip if output file is saved.
    if Path(save_fp).is_file():
        return

    # Read the large image tilesource.
    ts = large_image.open(fp)

    img = ts.getThumbnail(format=large_image.constants.TILE_FORMAT_NUMPY)[0]

    # sleep(120)
    imwrite(save_fp, img)
