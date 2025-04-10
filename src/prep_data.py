import argparse
import os

import pandas as pd


def process_kaggle_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    extracted_df = df[["track_name", "lyrics"]]
    extracted_df.to_csv(output_file, index=False)
    print(f"Processed lyrics have been saved to {output_file}")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Process Kaggle lyrics data")
    parser.add_argument(
        "--input",
        type=str,
        default="../data/kaggle_data.csv",
        help="Path to the input Kaggle CSV file",
    )
    parser.add_argument(
        "--output",
        type=str,
        default="../data/cleaned_lyrics.csv",
        help="Path for the output CSV file",
    )

    args = parser.parse_args()
    process_kaggle_data(args.input, args.output)
