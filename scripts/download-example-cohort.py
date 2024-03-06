from girder_client import GirderClient
from pathlib import Path
import pandas as pd


def girder_login(
    api_url: str, username: str | None = None, password: str | None = None
) -> GirderClient:
    """Login to Girder using the provided username and password.

    Args:
        api_url (str): The URL of the Girder server.
        username (str): The username to login with.
        password (str): The password to login with.

    Returns:
        GirderClient: A GirderClient object that is logged in.

    """
    interactive = False if all([username, password]) else True

    gc = GirderClient(apiUrl=api_url)
    gc.authenticate(username=username, password=password, interactive=interactive)

    return gc


def main():
    gc = GirderClient(apiUrl="https://megabrain.neurology.emory.edu/api/v1")
    gc.authenticate(interactive=True)

    # Selected WSIs to demo (3 SVS and 2 NDPI files).
    data = []

    wsi_ids = [
        "641bad66867536bb7a226a2c",
        "641bad67867536bb7a226a2e",
        "641bfd8f867536bb7a236b8e",
        "641bfb8d867536bb7a2366c6",
        "641bfb8f867536bb7a2366ca",
        "641bad67867536bb7a226a30",
    ]

    metadata = [
        {"caseID": "1-1", "regionName": "Amygdala", "stainID": "pTDP", "blockID": 1},
        {"caseID": "1-1", "regionName": "Hippocampus", "stainID": "aSyn", "blockID": 2},
        {"caseID": "1-2", "regionName": "Amygdala", "stainID": "H&E", "blockID": 1},
        {
            "caseID": "1-3",
            "regionName": "Left hippocampus",
            "stainID": "aBeta",
            "blockID": 3,
        },
        {
            "caseID": "1-4",
            "regionName": "Left Occipital",
            "stainID": "biels",
            "blockID": 7,
        },
        {
            "caseID": "1-5",
            "regionName": "Amygdala",
            "stainID": "H&E",
            "blockID": 1,
            "fileName": "E80-12.svs",
        },
    ]

    # Create directory to same images to.
    save_dir = Path("./app/sampleItemSet")
    save_dir.mkdir(exist_ok=True)

    print(f"Downloading {len(wsi_ids)} images...\n")
    for i, _id in enumerate(wsi_ids):
        # Add some dummy metadata
        print(f"Downloading image ({_id}) {i+1} of {len(wsi_ids)}...")
        item = gc.getItem(_id)
        item_name = item["name"]

        if i != 5:
            # Leave one without any metadata.
            meta = metadata[i]

            meta["fileName"] = item_name

            data.append(meta)

        # Check if file exists.
        save_fp = save_dir.joinpath(item_name)

        if item.get("largeImage", {}).get("fileId"):
            if not save_fp.is_file():
                gc.downloadFile(item["largeImage"]["fileId"], str(save_fp))
                print(f'   Downloaded image to "{str(save_fp)}".')
            else:
                print(f'   Image already exists at "{str(save_fp)}".')
        else:
            print("   Skipping file because large image file does not exist.")

    data.append(metadata[-1])
    df = pd.DataFrame(data)
    df.to_csv("./app/data.csv", index=False)


if __name__ == "__main__":
    main()
