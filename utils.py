# Utility / helper functions used in various other files.
from pathlib import Path


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
                    "fileSize": int(p.stat().st_size / 1024),
                    "fileName": p.stem,
                }
            )

    return file_list
