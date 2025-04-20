#!/usr/bin/env python3
import os
import pandas as pd


def split_genius_data(input_file, output_dir):
    print(f"Loading data from {input_file}...")
    df = pd.read_csv(input_file)
    total_rows = len(df)
    num_chunks = 10
    chunk_size = total_rows // num_chunks

    # Split and save each chunk
    for i in range(num_chunks):
        start = i * chunk_size
        end = total_rows if i == num_chunks - 1 else (i + 1) * chunk_size
        chunk_df = df.iloc[start:end]
        output_path = os.path.join(output_dir, f"genius_chunk_{i+1}.txt")
        print(f"Writing chunk {i+1} ({start}:{end}) to {output_path}...")
        with open(output_path, 'w', encoding='utf-8') as f:
            for lyric in chunk_df["lyrics"].tolist():
                f.write(f"{lyric}\n")

    print("Splitting complete.")


if __name__ == "__main__":
    input_file = "data/genius_dataset.csv"
    output_dir = "data/genius_lyrics"
    split_genius_data(input_file, output_dir) 