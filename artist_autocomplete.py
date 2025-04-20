#!/usr/bin/env python3
import os
import sys
import random
import json
import csv
import argparse
import pickle
from collections import defaultdict
from pathlib import Path

class MarkovModel:
    def __init__(self, order=2):
        self.order = order
        self.model = defaultdict(list)
        self.start_words = []
    
    def train(self, text):
        """Train the model on the given text."""
        words = text.split()
        if len(words) <= self.order:
            return
        
        # Track starting sequences
        self.start_words.append(tuple(words[:self.order]))
        
        # Build the Markov chain
        for i in range(len(words) - self.order):
            key = tuple(words[i:i+self.order])
            value = words[i+self.order]
            self.model[key].append(value)
    
    def generate(self, seed=None, num_lines=5, temperature=1.0):
        """Generate text using the trained model."""
        if not self.model:
            return "Error: Model not trained"
        
        # Initialize with seed or random start
        if seed:
            seed_words = seed.split()
            if len(seed_words) >= self.order:
                current = tuple(seed_words[-self.order:])
            else:
                # Pad seed with start words if needed
                if self.start_words:
                    random_start = random.choice(self.start_words)
                    current = random_start[:self.order-len(seed_words)] + tuple(seed_words)
                else:
                    current = tuple(random.choice(list(self.model.keys())))
            output = list(current)
        else:
            # Choose random start
            if self.start_words:
                current = random.choice(self.start_words)
            else:
                current = random.choice(list(self.model.keys()))
            output = list(current)
        
        # Generate lines
        line_count = 1
        line_length = 0
        max_length = 100  # Safety to prevent infinite loops
        
        while line_count <= num_lines and len(output) < max_length:
            # If no next words, break
            if current not in self.model:
                break
            
            next_words = self.model[current]
            
            # Apply temperature
            if temperature != 1.0:
                # When temperature is lower, make common options more likely
                # When temperature is higher, make all options more equally likely
                if temperature < 1.0:
                    # Count frequencies
                    word_counts = {}
                    for word in next_words:
                        if word in word_counts:
                            word_counts[word] += 1
                        else:
                            word_counts[word] = 1
                    
                    # Create a weighted list based on counts and temperature
                    weighted_words = []
                    for word, count in word_counts.items():
                        # Higher counts get more weight when temperature is low
                        weight = int(count ** (1/temperature))
                        weighted_words.extend([word] * weight)
                    
                    next_word = random.choice(weighted_words) if weighted_words else random.choice(next_words)
                else:
                    # For higher temperatures, introduce more randomness
                    unique_words = list(set(next_words))
                    next_word = random.choice(unique_words)
            else:
                # Normal temperature (1.0)
                next_word = random.choice(next_words)
            
            output.append(next_word)
            
            # Update current sequence
            current = tuple(output[-self.order:])
            
            # Count lines
            line_length += 1
            if next_word.endswith(('.', '!', '?', ',')) or line_length > 10:
                line_length = 0
                if next_word.endswith(('.', '!', '?')):
                    line_count += 1
        
        return " ".join(output)
    
    def save(self, filename):
        """Save the trained model to a file."""
        with open(filename, 'wb') as f:
            pickle.dump((self.model, self.start_words, self.order), f)
        return f"Model saved to {filename}"
    
    @classmethod
    def load(cls, filename):
        """Load a trained model from a file."""
        with open(filename, 'rb') as f:
            model_data, start_words, order = pickle.load(f)
        
        loaded_model = cls(order)
        loaded_model.model = model_data
        loaded_model.start_words = start_words
        return loaded_model


def read_lyrics_file(file_path):
    """Read lyrics from different file formats."""
    file_path = Path(file_path)
    extension = file_path.suffix.lower()
    
    try:
        if extension == '.txt':
            with open(file_path, 'r', encoding='utf-8') as f:
                return f.read()
        
        elif extension == '.csv':
            lyrics = []
            with open(file_path, 'r', encoding='utf-8') as f:
                reader = csv.reader(f)
                header = next(reader, None)  # Skip header if exists
                
                lyric_col = 0  # Default to first column
                # Try to find a lyrics column
                if header:
                    for i, col in enumerate(header):
                        if 'lyric' in col.lower():
                            lyric_col = i
                            break
                
                for row in reader:
                    if len(row) > lyric_col:
                        lyrics.append(row[lyric_col])
            
            return "\n".join(lyrics)
        
        elif extension == '.json':
            with open(file_path, 'r', encoding='utf-8') as f:
                data = json.load(f)
                
                # Try to extract lyrics from common JSON structures
                if isinstance(data, list):
                    # If it's a list of objects, try to find lyrics fields
                    lyrics = []
                    for item in data:
                        if isinstance(item, dict):
                            for key, value in item.items():
                                if 'lyric' in key.lower() and isinstance(value, str):
                                    lyrics.append(value)
                                    break
                    if lyrics:
                        return "\n".join(lyrics)
                
                elif isinstance(data, dict):
                    # If it's a dictionary, look for lyrics fields
                    lyrics = []
                    # Try direct lookup
                    for key in ['lyrics', 'lyric', 'text', 'content']:
                        if key in data and isinstance(data[key], str):
                            return data[key]
                    
                    # Try nested lookup
                    for key, value in data.items():
                        if isinstance(value, dict):
                            for subkey, subvalue in value.items():
                                if 'lyric' in subkey.lower() and isinstance(subvalue, str):
                                    lyrics.append(subvalue)
                        elif isinstance(value, list) and len(value) > 0 and isinstance(value[0], dict):
                            for item in value:
                                for subkey, subvalue in item.items():
                                    if 'lyric' in subkey.lower() and isinstance(subvalue, str):
                                        lyrics.append(subvalue)
                    
                    if lyrics:
                        return "\n".join(lyrics)
                    
                # Fallback: convert the whole JSON to string
                return json.dumps(data)
        
        else:
            return f"Unsupported file format: {extension}"
    
    except Exception as e:
        return f"Error reading file {file_path}: {str(e)}"


def process_directory(directory_path, model):
    """Process all supported files in a directory."""
    processed = 0
    directory = Path(directory_path)
    
    for ext in ['.txt', '.csv', '.json']:
        for file_path in directory.glob(f'*{ext}'):
            lyrics = read_lyrics_file(file_path)
            if not lyrics.startswith("Error") and not lyrics.startswith("Unsupported"):
                model.train(lyrics)
                processed += 1
    
    return processed


def list_lyric_files(directory_path=None):
    """List all supported lyric files in the given directory."""
    if directory_path is None:
        directory_path = 'data'
    
    directory = Path(directory_path)
    if not directory.exists() or not directory.is_dir():
        return f"Directory not found: {directory_path}"
    
    files = []
    for ext in ['.txt', '.csv', '.json']:
        for file_path in directory.glob(f'*{ext}'):
            files.append(str(file_path))
    
    if not files:
        return f"No supported lyric files found in {directory_path}"
    
    return "\n".join(files)


def main():
    parser = argparse.ArgumentParser(description="Artist Autocomplete - Generate lyrics based on an artist's style using Markov chains")
    
    # Command options
    subparsers = parser.add_subparsers(dest='command', help='Commands')
    
    # List files command
    list_parser = subparsers.add_parser('list', help='List available lyric files')
    list_parser.add_argument('--dir', '-d', help='Directory to search for lyric files', default='data')
    
    # Train command
    train_parser = subparsers.add_parser('train', help='Train a new model')
    train_parser.add_argument('--input', '-i', help='Input file or directory with lyrics', required=True)
    train_parser.add_argument('--order', '-o', help='Order of the Markov model (default: 2)', type=int, default=2)
    train_parser.add_argument('--save', '-s', help='Save model to file', default=None)
    
    # Generate command
    gen_parser = subparsers.add_parser('generate', help='Generate lyrics using a trained model')
    gen_parser.add_argument('--model', '-m', help='Load a saved model', default=None)
    gen_parser.add_argument('--input', '-i', help='Input file or directory with lyrics (if not loading a model)', default=None)
    gen_parser.add_argument('--order', '-o', help='Order of the Markov model (default: 2)', type=int, default=2)
    gen_parser.add_argument('--lines', '-l', help='Number of lines to generate (default: 5)', type=int, default=5)
    gen_parser.add_argument('--seed', help='Seed text to start generation', default=None)
    gen_parser.add_argument('--temp', '-t', help='Temperature for randomness (default: 1.0)', type=float, default=1.0)
    
    # Parse arguments
    args = parser.parse_args()
    
    # Handle commands
    if args.command == 'list':
        print(list_lyric_files(args.dir))
    
    elif args.command == 'train':
        model = MarkovModel(order=args.order)
        input_path = Path(args.input)
        
        if input_path.is_dir():
            processed = process_directory(input_path, model)
            print(f"Processed {processed} files from directory {input_path}")
        else:
            lyrics = read_lyrics_file(input_path)
            if lyrics.startswith("Error") or lyrics.startswith("Unsupported"):
                print(lyrics)
                return
            model.train(lyrics)
            print(f"Model trained on {input_path}")
        
        if args.save:
            print(model.save(args.save))
    
    elif args.command == 'generate':
        # Load model or train a new one
        if args.model:
            try:
                model = MarkovModel.load(args.model)
                print(f"Model loaded from {args.model}")
            except Exception as e:
                print(f"Error loading model: {str(e)}")
                return
        elif args.input:
            model = MarkovModel(order=args.order)
            input_path = Path(args.input)
            
            if input_path.is_dir():
                processed = process_directory(input_path, model)
                print(f"Processed {processed} files from directory {input_path}")
            else:
                lyrics = read_lyrics_file(input_path)
                if lyrics.startswith("Error") or lyrics.startswith("Unsupported"):
                    print(lyrics)
                    return
                model.train(lyrics)
                print(f"Model trained on {input_path}")
        else:
            print("Error: Either --model or --input must be specified")
            return
        
        # Generate lyrics
        generated = model.generate(
            seed=args.seed,
            num_lines=args.lines,
            temperature=args.temp
        )
        
        print("\nGenerated Lyrics:")
        print("-----------------")
        print(generated)
    
    else:
        parser.print_help()


if __name__ == "__main__":
    main() 