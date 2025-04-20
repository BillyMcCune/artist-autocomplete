#!/usr/bin/env python3
import json
import random
import pickle
import os
import numpy as np
from collections import defaultdict


class MarkovModel:
    """
    A Markov chain model for generating lyrics.
    """
    
    def __init__(self, order=2):
        """
        Initialize a Markov model with specified order.
        
        Args:
            order (int): The order of the Markov model (number of words in state)
        """
        self.order = order
        self.model = defaultdict(list)
        self.start_states = []
        
    def train(self, sentences):
        """
        Train the model on a list of sentences.
        
        Args:
            sentences (list): List of sentences to train on
        """
        for sentence in sentences:
            words = sentence.split()
            
            # Skip sentences that are too short
            if len(words) <= self.order:
                continue
                
            # Add starting state
            start_state = tuple(words[:self.order])
            self.start_states.append(start_state)
            
            # Train model
            for i in range(len(words) - self.order):
                state = tuple(words[i:i+self.order])
                next_word = words[i+self.order]
                self.model[state].append(next_word)
                
        # Report training statistics
        print(f"Trained model with order {self.order}")
        print(f"Number of states: {len(self.model)}")
        print(f"Number of start states: {len(self.start_states)}")
    
    def generate(self, num_lines=5, max_length=50, temperature=1.0, seed=None):
        """
        Generate lyrics.
        
        Args:
            num_lines (int): Number of lines to generate
            max_length (int): Maximum line length in words
            temperature (float): Randomness factor (higher = more random)
            seed (list or str): Optional starting words
            
        Returns:
            list: List of generated lines
        """
        if not self.model:
            raise ValueError("Model not trained. Please train the model first.")
            
        lines = []
        
        for _ in range(num_lines):
            line = self._generate_line(max_length, temperature, seed)
            lines.append(line)
            # Reset seed after first line
            seed = None
            
        return lines
    
    def _generate_line(self, max_length, temperature, seed=None):
        """
        Generate a single line.
        
        Args:
            max_length (int): Maximum line length in words
            temperature (float): Randomness factor
            seed (list or str): Optional starting words
            
        Returns:
            str: Generated line
        """
        # Process seed if provided
        if seed:
            if isinstance(seed, str):
                seed_words = seed.lower().split()
            else:
                seed_words = [word.lower() for word in seed]
                
            # Use seed words if possible
            if len(seed_words) >= self.order:
                current_state = tuple(seed_words[-self.order:])
                line = list(seed_words)
            else:
                # Pad seed words if needed
                random_state = random.choice(self.start_states)
                padded_words = list(random_state[:self.order-len(seed_words)]) + seed_words
                current_state = tuple(padded_words)
                line = list(padded_words)
        else:
            # Start with a random state
            if not self.start_states:
                # Fallback to a random model state if no start states
                current_state = random.choice(list(self.model.keys()))
            else:
                current_state = random.choice(self.start_states)
            line = list(current_state)
        
        # Generate the line
        for _ in range(max_length - len(line)):
            if current_state not in self.model:
                break
                
            next_words = self.model[current_state]
            
            if temperature != 1.0:
                # Apply temperature scaling by sampling with probabilities
                word_counts = {}
                for word in next_words:
                    if word in word_counts:
                        word_counts[word] += 1
                    else:
                        word_counts[word] = 1
                
                words = list(word_counts.keys())
                counts = np.array(list(word_counts.values()))
                probabilities = counts ** (1.0 / temperature)
                probabilities = probabilities / probabilities.sum()
                
                next_word = np.random.choice(words, p=probabilities)
            else:
                next_word = random.choice(next_words)
                
            line.append(next_word)
            
            # Update state
            current_state = tuple(line[-self.order:])
            
        return ' '.join(line)
    
    def save(self, file_path):
        """
        Save the model to a file.
        
        Args:
            file_path (str): Path to save the model
        """
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        with open(file_path, 'wb') as f:
            pickle.dump({
                'order': self.order,
                'model': dict(self.model),  # Convert defaultdict to dict for serialization
                'start_states': self.start_states
            }, f)
        
        print(f"Model saved to {file_path}")
    
    @classmethod
    def load(cls, file_path):
        """
        Load a model from a file.
        
        Args:
            file_path (str): Path to the model file
            
        Returns:
            MarkovModel: Loaded model
        """
        with open(file_path, 'rb') as f:
            data = pickle.load(f)
        
        model = cls(order=data['order'])
        model.model = defaultdict(list, data['model'])
        model.start_states = data['start_states']
        
        print(f"Loaded model from {file_path}")
        print(f"Order: {model.order}")
        print(f"Number of states: {len(model.model)}")
        
        return model


if __name__ == "__main__":
    # Test the model
    from parser import process_file
    import sys
    
    if len(sys.argv) > 1:
        file_path = sys.argv[1]
        sentences = process_file(file_path)
        
        if sentences:
            model = MarkovModel(order=2)
            model.train(sentences)
            
            print("\nGenerating sample lyrics:")
            lines = model.generate(num_lines=5, max_length=20)
            for i, line in enumerate(lines):
                print(f"{i+1}. {line}")
                
            # Test with seed
            seed = "love is"
            print(f"\nGenerating with seed '{seed}':")
            lines = model.generate(num_lines=3, seed=seed)
            for i, line in enumerate(lines):
                print(f"{i+1}. {line}")
    else:
        print("Please provide a file path to test the model.")
