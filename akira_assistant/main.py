#!/usr/bin/env python3
"""
Akira - AI Voice Assistant with Animated Anime Character
Main application entry point
"""

import sys
import os
from PyQt6.QtWidgets import QApplication
from PyQt6.QtCore import Qt
from akira_ui import AkiraMainWindow

def main():
    """Main application entry point"""
    # Enable high DPI scaling
    QApplication.setHighDpiScaleFactorRoundingPolicy(Qt.HighDpiScaleFactorRoundingPolicy.PassThrough)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_EnableHighDpiScaling, True)
    QApplication.setAttribute(Qt.ApplicationAttribute.AA_UseHighDpiPixmaps, True)
    
    app = QApplication(sys.argv)
    
    # Set application properties
    app.setApplicationName("Akira Assistant")
    app.setApplicationVersion("1.0")
    app.setOrganizationName("Akira AI")
    
    # Create and show main window
    window = AkiraMainWindow()
    window.show()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()