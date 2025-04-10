# Artist Autocomplete

This project extracts title and lyrics data from CSV files for the artist autocomplete feature.

## Environment Setup

### Option 1: Using pip (recommended for most users)

1. Clone the repo:
   ```bash
   git clone https://github.com/yourusername/artist-autocomplete.git
   cd artist-autocomplete
   ```

2. Create a virtual environment:
   ```bash
   python -m venv venv
   ```

3. Activate the virtual environment:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

5. Run the data preparation script (only if data file has been modified - no need to run otherwise):

   ```bash
   cd src
   python prep_data.py

## Requirements
- Dependencies listed in requirements.txt