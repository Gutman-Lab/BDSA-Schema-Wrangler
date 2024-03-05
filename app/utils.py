# Utility / helper functions used in various other files.
from pathlib import Path
import pandas as pd


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
                    "fileName": p.stem,
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
