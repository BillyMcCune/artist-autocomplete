# Artist Autocomplete

A Python application that generates song lyrics in the style of your favorite artists using Markov chain text generation.

## Features

- Train on individual lyrics files or entire directories
- Support for various file formats (TXT, CSV, JSON)
- Customizable Markov chain order
- Adjustable generation parameters (seed text, temperature, length)
- Save and load trained models
- GUI interface for easy lyrics generation

## Installation

1. Clone this repository:
```bash
git clone https://github.com/yourusername/artist-autocomplete.git
cd artist-autocomplete
```

2. Make the script executable:
```bash
chmod +x artist_autocomplete.py
chmod +x run_gui.py
```

## Usage

### GUI Interface

The easiest way to use Artist Autocomplete is through the GUI:

```bash
./run_gui.py
```

This will open a user interface where you can:
- Select any lyrics file from the data directory
- Set parameters like number of lines, temperature, and Markov chain order
- Add optional seed text to start the generation
- View the generated lyrics and artist information in a clean interface

### Command Line Interface

### List Lyric Files

List all supported lyric files in the data directory:

```bash
./artist_autocomplete.py list
```

Specify a different directory:

```bash
./artist_autocomplete.py list --dir path/to/lyrics
```

### Train a Model

Train a model on a single file:

```bash
./artist_autocomplete.py train --input data/sample_lyrics.txt
```

Train on a directory of files:

```bash
./artist_autocomplete.py train --input data/ --order 3 --save model.pkl
```

Options:
- `--input`, `-i`: Input file or directory (required)
- `--order`, `-o`: Order of the Markov model (default: 2)
- `--save`, `-s`: Save model to file

### Generate Lyrics

Generate lyrics using a saved model:

```bash
./artist_autocomplete.py generate --model model.pkl --lines 10
```

Generate lyrics by training on the fly:

```bash
./artist_autocomplete.py generate --input data/sample_lyrics.txt --seed "I want to" --temp 0.8
```

Options:
- `--model`, `-m`: Load a saved model
- `--input`, `-i`: Input file or directory (if not loading a model)
- `--order`, `-o`: Order of the Markov model (default: 2)
- `--lines`, `-l`: Number of lines to generate (default: 5)
- `--seed`: Seed text to start generation
- `--temp`, `-t`: Temperature for randomness (default: 1.0)

## How It Works

Artist Autocomplete uses Markov chains to learn the patterns in an artist's lyrics and generate new text based on those patterns. The "order" parameter determines how many previous words are considered when predicting the next word.

- Lower order (1-2): More random, less coherent
- Higher order (3+): More coherent, but may copy longer phrases from the original

The "temperature" parameter controls randomness in generation:
- Lower values (<1.0): More predictable, favors common patterns
- Higher values (>1.0): More random, less predictable

## License

This project is licensed under the MIT License - see the LICENSE file for details.