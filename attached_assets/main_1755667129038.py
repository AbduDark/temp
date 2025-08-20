#!/usr/bin/env python3
"""
Mobile Shop Management System - Desktop Application
Built with PyQt6 and Arabic RTL support
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon, QFont

# Add the desktop_app directory to the path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.database import DatabaseManager

class MobileShopApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        self.setApplicationName("إدارة محل الموبايل")
        self.setApplicationVersion("1.0.0")
        self.setOrganizationName("Mobile Shop Management")
        
        # Set RTL layout for Arabic support
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Set default font for Arabic text
        font = QFont("Tahoma", 10)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)
        
        # Initialize database
        self.db_manager = DatabaseManager()
        self.db_manager.initialize_database()
        
        # Create main window
        self.main_window = MainWindow(self.db_manager)
        
    def show_main_window(self):
        """Show the main application window"""
        self.main_window.show()
        self.main_window.raise_()
        self.main_window.activateWindow()

def main():
    """Main entry point for the application"""
    # Enable high DPI support (PyQt6 handles this automatically)
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
    
    # Create application instance
    app = MobileShopApp(sys.argv)
    
    # Show main window
    app.show_main_window()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()