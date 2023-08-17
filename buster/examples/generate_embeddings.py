import pandas as pd
from buster.documents_manager import DeepLakeDocumentsManager
import argparse

REQUIRED_COLUMNS = ["url", "title", "content", "source"]

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
        # initialize our vector store from scratch
        dm = DeepLakeDocumentsManager(vector_store_path=self.vector_store_path, overwrite=True, required_columns=REQUIRED_COLUMNS)
        # Generate the embeddings for our documents and store them to the deeplake store
        dm.add(df)
        # dm.add(df, csv_checkpoint="embeddings.csv")


def parse_args() -> argparse.Namespace:
    """
    Argument parser function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-v",
        "--vector_store_path",
        default="deeplake_store",
        help="vector store",
    )
    parser.add_argument(
        "-c",
        "--csv_path",
        default="stackoverflow.csv",
        help="contains df produced by create_chunks",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parsed_args = parse_args()
    generator = EmbeddingGenerator(parsed_args)
    generator.generate_embeddings()
