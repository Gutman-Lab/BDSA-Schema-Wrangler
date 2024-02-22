"""Create a metadata CSV file for the Emory's ADRC DSA collection."""

from girder_client import GirderClient
from pathlib import Path
import pandas as pd


def main():
    # Load environment variables from .env
    gc = GirderClient(apiUrl="https://megabrain.neurology.emory.edu/api/v1")
    print('Authenticate girder client for "https://megabrain.neurology.emory.edu"\n')
    gc.authenticate(interactive=True)

    # Get data from all items (images) from the Emory ADRC collection.
    metadata = []

    for item in gc.get(
        "resource/641ba814867536bb7a225533/items?type=collection&limit=0"
    ):
        # Grab the associated metadata for each item.
        np_schema = item.get("meta", {}).get("npSchema", {})

        metadata.append(
            [
                item["name"],
                np_schema.get("caseID", ""),
                np_schema.get("stainID", ""),
                np_schema.get("regionName", ""),
                np_schema.get("blockID", ""),
            ]
        )

    # Format as dataframe and save to CSV.
    df = pd.DataFrame(
        metadata, columns=["fileName", "caseID", "stainID", "regionName", "blockID"]
    )
    df = df.sort_values(by="fileName")

    Path("metadata").mkdir(exist_ok=True)
    df.to_csv("metadata/emory-sample.csv", index=False)

    print(df.head())


if __name__ == "__main__":
    main()
