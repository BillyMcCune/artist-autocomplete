import tkinter as tk
import os
import sys
from tkinter import scrolledtext, messagebox, ttk
from model import MarkovModel
from parser import process_file

# Determine the absolute path of the directory where this script resides.
script_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path for the 'data' folder relative to the script.
folder_path = os.path.join(script_dir, "..", "data")
folder_path = os.path.abspath(folder_path)  # Normalize the path

print("Data folder path:", folder_path)  

def get_lyric_files():
    """Get all available lyric files from the data directory"""
    try:
        if os.path.exists(folder_path):
            files = [f for f in os.listdir(folder_path) if os.path.isfile(os.path.join(folder_path, f))]
        else:
            raise FileNotFoundError(f"Folder '{folder_path}' does not exist")
    except Exception as e:
        print("Error reading folder:", e)
        files = []  

    if not files:
        files = ["No files found"]
    
    return files

def main():
    """Main function to create and run the GUI"""
    # Get available files
    files = get_lyric_files()
    
    # Create GUI
    root = tk.Tk()
    root.title("Artist Autocomplete - Lyrics Generator")
    root.minsize(600, 500)

    # Create main frame
    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    # Input frame (left side)
    input_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
    input_frame.pack(side=tk.LEFT, fill=tk.BOTH, expand=False, padx=(0, 5))

    # File selection
    ttk.Label(input_frame, text="Select lyrics file:").grid(row=0, column=0, sticky=tk.W, pady=2)
    file_var = tk.StringVar(root)
    file_var.set(files[0])
    file_dropdown = ttk.Combobox(input_frame, textvariable=file_var, values=files, width=30)
    file_dropdown.grid(row=0, column=1, sticky=tk.W, pady=2)

    # Seed text
    ttk.Label(input_frame, text="Seed text (optional):").grid(row=1, column=0, sticky=tk.W, pady=2)
    seed_input = ttk.Entry(input_frame, width=30)
    seed_input.grid(row=1, column=1, sticky=tk.W, pady=2)

    # Number of lines
    ttk.Label(input_frame, text="Number of lines:").grid(row=2, column=0, sticky=tk.W, pady=2)
    lines_input = ttk.Entry(input_frame, width=10)
    lines_input.insert(0, "5")
    lines_input.grid(row=2, column=1, sticky=tk.W, pady=2)

    # Temperature
    ttk.Label(input_frame, text="Temperature:").grid(row=3, column=0, sticky=tk.W, pady=2)
    temp_input = ttk.Entry(input_frame, width=10)
    temp_input.insert(0, "1.0")
    temp_input.grid(row=3, column=1, sticky=tk.W, pady=2)

    # Order
    ttk.Label(input_frame, text="Markov chain order:").grid(row=4, column=0, sticky=tk.W, pady=2)
    order_input = ttk.Entry(input_frame, width=10)
    order_input.insert(0, "2")
    order_input.grid(row=4, column=1, sticky=tk.W, pady=2)

    # Results frame (right side)
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)

    # Generated lyrics
    ttk.Label(results_frame, text="Generated Lyrics:").pack(anchor=tk.W)
    result_text = scrolledtext.ScrolledText(results_frame, height=15, width=40, wrap=tk.WORD)
    result_text.pack(fill=tk.BOTH, expand=True)
    result_text.insert(tk.END, "Generated lyrics will appear here")
    result_text.config(state=tk.DISABLED)
    
    # Status bar
    status_var = tk.StringVar()
    status_var.set("Ready")
    status_bar = ttk.Label(input_frame, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W)
    status_bar.grid(row=6, column=0, columnspan=2, sticky=tk.W+tk.E, pady=(5, 0))
    
    def generate_lyrics():
        """Generate lyrics using the selected file and parameters."""
        selected_file = file_var.get()
        seed_text = seed_input.get()
        
        try:
            # Get number of lines and temperature
            num_lines = int(lines_input.get())
            temp = float(temp_input.get())
            order = int(order_input.get())
            
            # Validate parameters
            if num_lines <= 0 or num_lines > 50:
                raise ValueError("Number of lines must be between 1 and 50")
            if temp <= 0:
                raise ValueError("Temperature must be greater than 0")
            if order <= 0 or order > 5:
                raise ValueError("Order must be between 1 and 5")
            
            # Path to the selected file
            file_path = os.path.join(folder_path, selected_file)
            
            # Update status
            status_var.set("Processing file and training model...")
            root.update_idletasks()
            
            # Process file and train model
            sentences = process_file(file_path)
            if not sentences:
                raise ValueError(f"No usable content found in {selected_file}")
            
            model = MarkovModel(order=order)
            model.train(sentences)
            
            # Update status
            status_var.set("Generating lyrics...")
            root.update_idletasks()
            
            # Generate lyrics
            lyrics = model.generate(
                num_lines=num_lines,
                max_length=30,
                temperature=temp,
                seed=seed_text if seed_text else None
            )
            
            # Display results
            result_text.config(state=tk.NORMAL)
            result_text.delete(1.0, tk.END)
            result_text.insert(tk.END, "\n".join(lyrics))
            result_text.config(state=tk.DISABLED)
        
            
            # Update status
            status_var.set(f"Successfully generated {len(lyrics)} lines of lyrics")
            
        except ValueError as e:
            messagebox.showerror("Input Error", str(e))
            status_var.set(f"Error: {str(e)}")
        except Exception as e:
            messagebox.showerror("Generation Error", f"An error occurred: {str(e)}")
            status_var.set(f"Error: {str(e)}")

    # Generate button
    generate_button = ttk.Button(input_frame, text="Generate Lyrics", command=generate_lyrics)
    generate_button.grid(row=5, column=0, columnspan=2, pady=(20, 5))

    # Check for file selection changes to update artist info
    def on_file_select(*args):
        selected_file = file_var.get()
        file_path = os.path.join(folder_path, selected_file)

    file_var.trace("w", on_file_select)
    
    # Initialize with first file's artist info if available
    if files[0] != "No files found":
        file_path = os.path.join(folder_path, files[0])

    # Start the main loop
    root.mainloop()

if __name__ == "__main__":
    main()
