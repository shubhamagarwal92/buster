import pandas as pd
from buster.documents_manager import DeepLakeDocumentsManager
import argparse


class EmbeddingGenerator:
    """
    Class to generate embeddings
    """

    def __init__(self, config):
        self.class_name = "EmbeddingGenerator"
        self.config = config
        self.csv_path = config.csv_path
        self.vector_store_path = config.vector_store_path

    def generate_embeddings(self):
        # Read the csv
        df = pd.read_csv(self.csv_path)
        # Generate the embeddings for our documents and store them in a deeplake format
        dm = DeepLakeDocumentsManager(vector_store_path=self.vector_store_path, overwrite=True)
        dm.add(df)


def parse_args() -> argparse.Namespace:
    """
    Argument parser function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--vector_store_path",
        default="",
        help="",
    )
    parser.add_argument(
        "-c",
        "--csv_path",
        default="",
        help="",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parsed_args = parse_args()
    generator = EmbeddingGenerator(parsed_args)
    generator.generate_embeddings()
