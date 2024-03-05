from girder_client import GirderClient
from pathlib import Path
from tqdm import tqdm


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
    wsi_ids = [
        "641bfde6867536bb7a236c5e",
        "641bfe20867536bb7a236ce4",
        "641bfd8f867536bb7a236b8e",
        "641bfb8d867536bb7a2366c6",
        "641bfb8f867536bb7a2366ca",
    ]

    # Create directory to same images to.
    save_dir = Path("./app/sampleItemSet")
    save_dir.mkdir(exist_ok=True)

    print(f"Downloading {len(wsi_ids)} images...\n")
    for i, _id in enumerate(wsi_ids):
        print(f"Downloading image ({_id}) {i+1} of {len(wsi_ids)}...")
        item = gc.getItem(_id)
        item_name = item["name"]

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


if __name__ == "__main__":
    main()
