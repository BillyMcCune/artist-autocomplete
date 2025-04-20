#!/usr/bin/env python3
import os
import re
import glob
import pandas as pd

def clean_text(text):
    """
    Clean the input text by removing special characters, 
    extra whitespace, and standardizing formatting.
    
    Args:
        text (str): Text to clean
        
    Returns:
        str: Cleaned text
    """
    # Remove special characters
    text = re.sub(r'[^\w\s\']', ' ', text)
    
    # Normalize whitespace
    text = re.sub(r'\s+', ' ', text)
    
    # Remove leading/trailing whitespace
    text = text.strip()
    
    # Convert to lowercase
    text = text.lower()
    
    return text

def process_file(file_path):
    """
    Process a lyrics file and return a list of cleaned sentences.
    
    Args:
        file_path (str): Path to the lyrics file
        
    Returns:
        list: List of cleaned sentences
    """
    try:
        if file_path.endswith('.csv'):
            # Read CSV file
            df = pd.read_csv(file_path)
            
            # Check for 'lyrics' column
            if 'lyrics' in df.columns:
                lyrics_text = ' '.join(df['lyrics'].dropna().astype(str))
            else:
                # Try to find a column that might contain lyrics
                text_columns = [col for col in df.columns if df[col].dtype == 'object']
                if text_columns:
                    lyrics_text = ' '.join(df[text_columns[0]].dropna().astype(str))
                else:
                    raise ValueError(f"Could not find lyrics column in {file_path}")
        else:
            # Read as text file
            with open(file_path, 'r', encoding='utf-8') as f:
                lyrics_text = f.read()
        
        # Split into sentences (by newlines and punctuation)
        sentences = re.split(r'[.!?;\n]', lyrics_text)
        
        # Clean each sentence
        cleaned_sentences = [clean_text(sentence) for sentence in sentences if len(clean_text(sentence)) > 0]
        
        print(f"Processed {file_path}: {len(cleaned_sentences)} sentences extracted")
        return cleaned_sentences
    
    except Exception as e:
        print(f"Error processing {file_path}: {str(e)}")
        return []

def get_available_files(directory='../data', extensions=None):
    """
    Get a list of lyrics files in the specified directory.
    
    Args:
        directory (str): Directory to search
        extensions (list): List of file extensions to include (default: ['.txt', '.csv'])
        
    Returns:
        list: List of file paths
    """
    if extensions is None:
        extensions = ['.txt', '.csv']
    
    files = []
    for ext in extensions:
        pattern = os.path.join(directory, f'*{ext}')
        files.extend(glob.glob(pattern))
    
    return sorted(files)

if __name__ == "__main__":
    # Test the parser
    import sys
    
    if len(sys.argv) > 1:
        test_file = sys.argv[1]
        sentences = process_file(test_file)
        print(f"First 5 sentences:")
        for i, sentence in enumerate(sentences[:5]):
            print(f"{i+1}. {sentence}")
    else:
        print("Please provide a file path to test the parser.")
        print("Available files:")
        files = get_available_files()
        for file in files:
            print(f"- {file}")
