#!/usr/bin/env python3
import os
import sys
import argparse
from src.application.model.parser.parser import process_file, get_available_files
from src.application.model.model import MarkovModel


def main():
    parser = argparse.ArgumentParser(description='Artist Autocomplete - Generate lyrics using Markov chains')
    

    parser.add_argument('--input', '-i', help='Path to lyrics file or directory')
    parser.add_argument('--list-files', '-l', action='store_true', help='List available lyrics files')
    
    parser.add_argument('--order', '-o', type=int, default=2, help='Order of the Markov model (default: 2)')
    parser.add_argument('--save-model', '-s', help='Save trained model to file')
    parser.add_argument('--load-model', '-m', help='Load trained model from file')
    
    parser.add_argument('--lines', '-n', type=int, default=5, help='Number of lines to generate (default: 5)')
    parser.add_argument('--max-length', type=int, default=30, help='Maximum line length in words (default: 30)')
    parser.add_argument('--temperature', '-t', type=float, default=1.0, 
                        help='Temperature for generation (higher = more random, default: 1.0)')
    parser.add_argument('--seed', help='Seed words to start generation')
    
    args = parser.parse_args()
    
    # List available files
    if args.list_files:
        data_dir = args.input if args.input else os.path.join('..', 'data')
        files = get_available_files(data_dir)
        if files:
            print(f"Available files in {data_dir}:")
            for i, file in enumerate(files, 1):
                print(f"{i}. {os.path.basename(file)}")
        else:
            print(f"No lyrics files found in {data_dir}")
        return
    
    # Create or load model
    model = None
    
    if args.load_model:
        if os.path.exists(args.load_model):
            try:
                model = MarkovModel.load(args.load_model)
                print(f"Model loaded successfully from {args.load_model}")
            except Exception as e:
                print(f"Error loading model: {e}")
                return
        else:
            print(f"Model file not found: {args.load_model}")
            return
    
    # Train model if input file provided
    if args.input and not model:
        if os.path.isfile(args.input):
            print(f"Processing file: {args.input}")
            lyrics = process_file(args.input)
            
            if not lyrics:
                print(f"No lyrics found in {args.input}")
                return
                
            print(f"Training model with order {args.order}...")
            model = MarkovModel(order=args.order)
            model.train(lyrics)
            
        elif os.path.isdir(args.input):
            # Train on all files in directory
            files = get_available_files(args.input)
            if not files:
                print(f"No lyrics files found in {args.input}")
                return
                
            print(f"Training model on {len(files)} files from {args.input}...")
            all_lyrics = []
            for file in files:
                print(f"Processing {os.path.basename(file)}...")
                lyrics = process_file(file)
                if lyrics:
                    all_lyrics.extend(lyrics)
            
            if not all_lyrics:
                print("No lyrics extracted from files")
                return
                
            print(f"Training model with order {args.order}...")
            model = MarkovModel(order=args.order)
            model.train(all_lyrics)
        else:
            print(f"Input path not found: {args.input}")
            return
    
    # Save model if requested
    if args.save_model and model:
        try:
            model.save(args.save_model)
            print(f"Model saved to {args.save_model}")
        except Exception as e:
            print(f"Error saving model: {e}")
    
    # Generate lyrics
    if model:
        print("\nGenerated lyrics:")
        print("=" * 40)
        
        lines = model.generate(
            num_lines=args.lines,
            max_length=args.max_length,
            temperature=args.temperature,
            seed=args.seed
        )
        
        for line in lines:
            print(line)
        
        print("=" * 40)
    else:
        print("No model available. Please provide an input file or load a model.")
        parser.print_help()


if __name__ == "__main__":
    main() 