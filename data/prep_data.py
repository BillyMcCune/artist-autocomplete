import os
import pandas as pd


def process_kaggle_data(input_file, output_file):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    lyrics = df["lyrics"].tolist()
    
    with open(output_file, 'w', encoding='utf-8') as f:
        for lyric in lyrics:
            f.write(f"{lyric}\n")
    
    print(f"Processed lyrics have been saved to {output_file}")


if __name__ == "__main__":
    input_file = "data/kaggle_data.csv"
    output_file = "data/cleaned_lyrics.txt"
    process_kaggle_data(input_file, output_file)
