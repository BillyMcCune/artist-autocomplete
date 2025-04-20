#!/usr/bin/env python3
import os
import sys

# Add project root (contains "src/") to Python path
current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, current_dir)

# Import and launch the GUI
import src.application.view.userView as userView

if __name__ == "__main__":
    userView.main()