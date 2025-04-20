#!/usr/bin/env python3
import os
import sys

#add the src directory to path
current_dir = os.path.dirname(os.path.abspath(__file__))
src_dir = os.path.join(current_dir, "src")
sys.path.append(current_dir)

#import and run the GUI
import src.userView as userView

if __name__ == "__main__":
    userView.main() 