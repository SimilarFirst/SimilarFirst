#!/usr/bin/env python3
"""
Akira - AI Voice Assistant with Animated Anime Character
Main application entry point
"""

import tkinter as tk
from tkinter import ttk
import sys
import os
from akira_ui import AkiraMainWindow

def main():
    """Main application entry point"""
    # Create main window
    root = tk.Tk()
    
    # Set window properties
    root.title("Akira - AI Assistant")
    root.geometry("800x600")
    root.resizable(True, True)
    
    # Create application
    app = AkiraMainWindow(root)
    
    # Start main loop
    root.mainloop()

if __name__ == "__main__":
    main()