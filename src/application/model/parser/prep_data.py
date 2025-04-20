import argparse
import os
import re
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


def generate_lyrics(models, model, seed_text=None, count=5, max_length=50):
    """
    Generate multiple lyrics samples using back‑off across model orders.

    Args:
        models (dict[int, MarkovModel]): dict of trained MarkovModel instances
        model (MarkovModel): the primary model (of the chosen order)
        seed_text (str, optional): text to prime the generator
        count (int): how many samples to generate
        max_length (int): max tokens per sample

    Returns:
        list[str]: generated lyric strings
    """
    results = []
    if seed_text:
        seed_words = re.findall(r'\b\w+\b|[.!?,]', seed_text.lower())
    else:
        seed_words = None

    for _ in range(count):
        sample = model.generate_with_backoff(models, seed_words, max_length)
        results.append(sample)

    return results