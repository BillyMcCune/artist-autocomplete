# src/userView.py
#!/usr/bin/env python3
import tkinter as tk
import os
from tkinter import scrolledtext, messagebox, ttk
from src.application.model.model import MarkovModel
from src.application.model.parser.parser import process_file
from src.application.model.parser.prep_data import generate_lyrics

# locate the data/ folder next to this script
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
FOLDER_PATH = os.path.abspath(os.path.join(
    SCRIPT_DIR, "..", "..", "..", "data"
))


def get_lyric_files():
    try:
        if os.path.isdir(FOLDER_PATH):
            return [f for f in os.listdir(FOLDER_PATH)
                    if os.path.isfile(os.path.join(FOLDER_PATH, f))]
        else:
            raise FileNotFoundError
    except Exception:
        return []


def main():
    files = get_lyric_files() or ["No files found"]

    root = tk.Tk()
    root.title("Artist Autocomplete – Lyrics Generator")
    root.minsize(600, 500)

    main_frame = ttk.Frame(root, padding="10")
    main_frame.pack(fill=tk.BOTH, expand=True)

    input_frame = ttk.LabelFrame(main_frame, text="Parameters", padding="10")
    input_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0,5))

    # File picker
    ttk.Label(input_frame, text="Lyrics file:")
    file_var = tk.StringVar(value=files[0])
    ttk.Combobox(input_frame, textvariable=file_var, values=files, width=30)
    file_var.get()  # ensure default
    ttk.Combobox(input_frame, textvariable=file_var, values=files, width=30).grid(row=0, column=1)

    # Seed text
    ttk.Label(input_frame, text="Seed text (optional):").grid(row=1, column=0)
    seed_input = ttk.Entry(input_frame, width=30)
    seed_input.grid(row=1, column=1)

    # Number of samples
    ttk.Label(input_frame, text="Number of samples:").grid(row=2, column=0)
    samples_input = ttk.Entry(input_frame, width=10)
    samples_input.insert(0, "5")
    samples_input.grid(row=2, column=1)

    # Max length
    ttk.Label(input_frame, text="Max length per sample:").grid(row=3, column=0)
    length_input = ttk.Entry(input_frame, width=10)
    length_input.insert(0, "50")
    length_input.grid(row=3, column=1)

    # Markov order
    ttk.Label(input_frame, text="Markov chain order:").grid(row=4, column=0)
    order_input = ttk.Entry(input_frame, width=10)
    order_input.insert(0, "2")
    order_input.grid(row=4, column=1)

    status_var = tk.StringVar(value="Ready")
    ttk.Label(root, textvariable=status_var, relief=tk.SUNKEN, anchor=tk.W).pack(side=tk.BOTTOM, fill=tk.X)

    # Results pane
    results_frame = ttk.Frame(main_frame)
    results_frame.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
    ttk.Label(results_frame, text="Generated Lyrics:").pack(anchor=tk.W)
    result_text = scrolledtext.ScrolledText(results_frame, height=20, width=50, wrap=tk.WORD)
    result_text.insert(tk.END, "Your lyrics will appear here…")
    result_text.config(state=tk.DISABLED)
    result_text.pack(fill=tk.BOTH, expand=True)

    def on_generate():
        selected = file_var.get()
        seed = seed_input.get().strip() or None
        try:
            count = int(samples_input.get())
            max_length = int(length_input.get())
            order = int(order_input.get())
            if not (1 <= count <= 20):
                raise ValueError("Samples must be between 1 and 20")
            if not (10 <= max_length <= 200):
                raise ValueError("Max length must be between 10 and 200")
            if not (1 <= order <= 5):
                raise ValueError("Order must be between 1 and 5")

            path = os.path.join(FOLDER_PATH, selected)
            status_var.set("Reading & training models...")
            root.update_idletasks()

            sentences = process_file(path)
            if not sentences:
                raise ValueError("No usable content in the selected file.")

            # Train orders 1–5 for back‑off
            models = {}
            for o in range(1, 6):
                m = MarkovModel(order=o)
                m.train(sentences)
                models[o] = m

            primary = models[order]
            status_var.set("Generating lyrics…")
            root.update_idletasks()

            samples = generate_lyrics(
                models,
                primary,
                seed_text=seed,
                count=count,
                max_length=max_length
            )

            # Display
            result_text.config(state=tk.NORMAL)
            result_text.delete("1.0", tk.END)
            result_text.insert(tk.END, "\n\n".join(samples))
            result_text.config(state=tk.DISABLED)
            status_var.set(f"Done: {len(samples)} samples generated.")

        except Exception as e:
            messagebox.showerror("Error", str(e))
            status_var.set(f"Error: {e}")

    ttk.Button(input_frame, text="Generate Lyrics", command=on_generate).grid(row=5, column=0, columnspan=2, pady=10)

    root.mainloop()