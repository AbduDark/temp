#!/usr/bin/env python3
"""
Mobile Shop Management System - Desktop Application
Built with PyQt6 and Arabic RTL support
"""

import sys
import os
from PyQt6.QtWidgets import QApplication, QSplashScreen, QLabel
from PyQt6.QtCore import Qt, QTimer, QThread, pyqtSignal
from PyQt6.QtGui import QIcon, QFont, QPixmap, QPainter, QColor

# Add current directory to path for imports
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from ui.main_window import MainWindow
from utils.database import DatabaseManager

class DatabaseInitThread(QThread):
    """Thread for initializing database to avoid blocking UI"""
    finished = pyqtSignal()
    error = pyqtSignal(str)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
    
    def run(self):
        try:
            self.db_manager.initialize_database()
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))

class MobileShopApp(QApplication):
    def __init__(self, argv):
        super().__init__(argv)
        
        # Set application properties
        self.setApplicationName("نظام إدارة محل الموبايل")
        self.setApplicationVersion("2.0.0")
        self.setOrganizationName("Mobile Shop Management")
        self.setOrganizationDomain("mobileshop.local")
        
        # Set RTL layout for Arabic support
        self.setLayoutDirection(Qt.LayoutDirection.RightToLeft)
        
        # Set default font for Arabic text
        font = QFont("Segoe UI", 10)
        font.setStyleStrategy(QFont.StyleStrategy.PreferAntialias)
        self.setFont(font)
        
        # Apply global styles
        self.setStyleSheet(self.get_global_styles())
        
        # Initialize components
        self.db_manager = None
        self.main_window = None
        self.splash = None
        
    def get_global_styles(self):
        """Global application styles"""
        return """
            QApplication {
                font-family: 'Segoe UI', 'Tahoma', sans-serif;
                font-size: 10pt;
            }
            
            QWidget {
                color: #2d3748;
                background-color: #f7fafc;
            }
            
            QMessageBox {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            
            QMessageBox QLabel {
                color: #2d3748;
                font-size: 12pt;
                padding: 10px;
            }
            
            QMessageBox QPushButton {
                background-color: #3182ce;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 6px;
                font-weight: bold;
                min-width: 80px;
            }
            
            QMessageBox QPushButton:hover {
                background-color: #2c5aa0;
            }
        """
    
    def show_splash(self):
        """Show splash screen during initialization"""
        # Create splash screen
        splash_pixmap = QPixmap(400, 300)
        splash_pixmap.fill(QColor(59, 130, 246))
        
        painter = QPainter(splash_pixmap)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Draw logo
        painter.setPen(QColor(255, 255, 255))
        painter.setFont(QFont("Segoe UI", 48, QFont.Weight.Bold))
        painter.drawText(splash_pixmap.rect(), Qt.AlignmentFlag.AlignCenter, "🏪")
        
        # Draw title
        painter.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        painter.drawText(50, 200, "نظام إدارة محل الموبايل")
        
        # Draw version
        painter.setFont(QFont("Tahoma", 12))
        painter.drawText(50, 220, "الإصدار 2.0.0")
        
        # Draw loading text
        painter.drawText(50, 260, "جاري التحميل...")
        
        painter.end()
        
        self.splash = QSplashScreen(splash_pixmap)
        self.splash.setWindowFlags(Qt.WindowType.SplashScreen | Qt.WindowType.FramelessWindowHint)
        self.splash.show()
        
        # Process events to show splash
        self.processEvents()
    
    def initialize_database(self):
        """Initialize database in background thread"""
        self.db_manager = DatabaseManager()
        
        # Create and start database initialization thread
        self.db_thread = DatabaseInitThread(self.db_manager)
        self.db_thread.finished.connect(self.on_db_initialized)
        self.db_thread.error.connect(self.on_db_error)
        self.db_thread.start()
    
    def on_db_initialized(self):
        """Called when database initialization is complete"""
        if self.splash:
            self.splash.showMessage("إنشاء النافذة الرئيسية...", 
                                   Qt.AlignmentFlag.AlignBottom | Qt.AlignmentFlag.AlignCenter,
                                   QColor(255, 255, 255))
        
        # Create main window
        self.main_window = MainWindow(self.db_manager)
        
        # Show main window after a brief delay
        QTimer.singleShot(1000, self.show_main_window)
    
    def on_db_error(self, error_msg):
        """Called when database initialization fails"""
        if self.splash:
            self.splash.close()
        
        from PyQt6.QtWidgets import QMessageBox
        QMessageBox.critical(None, "خطأ في قاعدة البيانات", 
                           f"فشل في تهيئة قاعدة البيانات:\n{error_msg}")
        self.quit()
    
    def show_main_window(self):
        """Show the main application window"""
        if self.splash:
            self.splash.close()
        
        if self.main_window:
            self.main_window.show()
            self.main_window.raise_()
            self.main_window.activateWindow()

def main():
    """Main entry point for the application"""
    # Enable high DPI support
    os.environ["QT_ENABLE_HIGHDPI_SCALING"] = "1"
    os.environ["QT_SCALE_FACTOR_ROUNDING_POLICY"] = "RoundPreferFloor"
    
    # Create application instance
    app = MobileShopApp(sys.argv)
    
    # Show splash screen
    app.show_splash()
    
    # Initialize database
    app.initialize_database()
    
    # Start event loop
    sys.exit(app.exec())

if __name__ == "__main__":
    main()
