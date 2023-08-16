import argparse
from buster.docparser import get_all_documents
from buster.parser import SphinxParser


class ChunkManager:
    """
    Class to generate chunks for buster
    """

    def __init__(self, config):
        self.class_name = "ChunkManager"
        self.config = config
        # Parser to use, you can create one by inheriting from buster.parser.Parser
        self.parser = SphinxParser
        self.docs_dir = config.docs_dir
        self.base_url = config.base_url
        self.source = config.source
        self.output_csv = config.output_csv

    def create_chunks(self):
        # Create the chunks, returns a DataFrame
        documents_df = get_all_documents(self.docs_dir, self.base_url, self.parser)

        # The source column is used to easily filter/update the documents.
        # We could have mila-docs, slack-threads, office-hours, ...
        documents_df["source"] = self.source

        if self.config.filter:
            print(f"Choosing only 10 rows of the df as demo")
            documents_df = documents_df[:10]
        # Save the chunks
        documents_df.to_csv(self.output_csv, index=False)

        return


def parse_args() -> argparse.Namespace:
    """
    Argument parser function
    """
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "-d",
        "--docs_dir",
        default="",
        help="",
    )
    parser.add_argument(
        "-b",
        "--base_url",
        default="",
        help="",
    )
    parser.add_argument(
        "-o",
        "--output_csv",
        default="",
        help="",
    )
    parser.add_argument(
        "-s",
        "--source",
        default="",
        help="",
    )
    parser.add_argument(
        "-f",
        "--filter",
        action='store_true',
        help="",
    )

    args = parser.parse_args()
    return args


if __name__ == "__main__":
    parsed_args = parse_args()
    generator = ChunkManager(parsed_args)
    generator.create_chunks()
