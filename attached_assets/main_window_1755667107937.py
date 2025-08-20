"""
Main Window for Mobile Shop Management System
PyQt6 implementation with Arabic RTL support
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QFrame, QPushButton, QLabel,
    QMenuBar, QStatusBar, QSplitter, QScrollArea
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor

from .pages.dashboard import DashboardPage
from .pages.inventory import InventoryPage
from .pages.sales import SalesPage
from .pages.repairs import RepairsPage
from .pages.wallet import WalletPage
from .pages.reports import ReportsPage

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_page = None
        
        self.setup_ui()
        self.setup_styles()
        self.show_dashboard()
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Window properties
        self.setWindowTitle("نظام إدارة محل الموبايل")
        self.setMinimumSize(1200, 800)
        self.resize(1400, 900)
        
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create sidebar
        self.setup_sidebar()
        
        # Create content area
        self.setup_content_area()
        
        # Add to main layout
        main_layout.addWidget(self.sidebar_frame, 0)
        main_layout.addWidget(self.content_frame, 1)
        
        # Setup status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("مرحباً بك في نظام إدارة محل الموبايل")
        
    def setup_sidebar(self):
        """Create and setup the sidebar navigation"""
        self.sidebar_frame = QFrame()
        self.sidebar_frame.setFixedWidth(280)
        self.sidebar_frame.setFrameStyle(QFrame.Shape.Box)
        
        sidebar_layout = QVBoxLayout(self.sidebar_frame)
        sidebar_layout.setContentsMargins(0, 0, 0, 0)
        sidebar_layout.setSpacing(0)
        
        # Logo/Header
        header_widget = QWidget()
        header_widget.setFixedHeight(80)
        header_layout = QVBoxLayout(header_widget)
        header_layout.setContentsMargins(20, 10, 20, 10)
        
        logo_label = QLabel("🏪")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 32px;")
        
        title_label = QLabel("إدارة محل الموبايل")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        
        # Navigation buttons
        nav_widget = QWidget()
        nav_layout = QVBoxLayout(nav_widget)
        nav_layout.setContentsMargins(10, 20, 10, 10)
        nav_layout.setSpacing(5)
        
        # Navigation menu items
        self.nav_buttons = {}
        nav_items = [
            ("dashboard", "الرئيسية", "🏠"),
            ("inventory", "المخزون", "📦"),
            ("sales", "المبيعات", "🛒"),
            ("repairs", "الإصلاحات", "🔧"),
            ("wallet", "المحفظة", "💰"),
            ("reports", "التقارير", "📊")
        ]
        
        for key, text, icon in nav_items:
            btn = QPushButton(f"{icon}  {text}")
            btn.setFixedHeight(50)
            btn.setCheckable(True)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            self.nav_buttons[key] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        
        sidebar_layout.addWidget(header_widget)
        sidebar_layout.addWidget(nav_widget, 1)
        
    def setup_content_area(self):
        """Create and setup the main content area"""
        self.content_frame = QFrame()
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Initialize pages
        self.pages = {
            'dashboard': DashboardPage(self.db_manager),
            'inventory': InventoryPage(self.db_manager),
            'sales': SalesPage(self.db_manager),
            'repairs': RepairsPage(self.db_manager),
            'wallet': WalletPage(self.db_manager),
            'reports': ReportsPage(self.db_manager)
        }
        
        # Add pages to stacked widget
        for page_name, page_widget in self.pages.items():
            self.stacked_widget.addWidget(page_widget)
    
    def setup_styles(self):
        """Apply custom styles to the interface"""
        self.setStyleSheet("""
            QMainWindow {
                background-color: #f8fafc;
            }
            
            QFrame {
                border: none;
            }
            
            /* Sidebar styles */
            QFrame[objectName="sidebar_frame"] {
                background-color: #ffffff;
                border-right: 1px solid #e2e8f0;
            }
            
            /* Navigation button styles */
            QPushButton {
                background-color: transparent;
                border: none;
                padding: 12px 20px;
                text-align: right;
                font-size: 14px;
                font-weight: 500;
                color: #475569;
                border-radius: 8px;
                margin: 2px 5px;
            }
            
            QPushButton:hover {
                background-color: #f1f5f9;
                color: #334155;
            }
            
            QPushButton:checked {
                background-color: #3b82f6;
                color: white;
            }
            
            QPushButton:checked:hover {
                background-color: #2563eb;
            }
            
            /* Status bar */
            QStatusBar {
                background-color: #ffffff;
                border-top: 1px solid #e2e8f0;
                color: #64748b;
                padding: 5px 15px;
            }
            
            /* Content area */
            QFrame[objectName="content_frame"] {
                background-color: #f8fafc;
            }
        """)
        
        # Set object names for styling
        self.sidebar_frame.setObjectName("sidebar_frame")
        self.content_frame.setObjectName("content_frame")
    
    def navigate_to(self, page_name):
        """Navigate to a specific page"""
        if page_name in self.pages:
            # Update button states
            for key, btn in self.nav_buttons.items():
                btn.setChecked(key == page_name)
            
            # Show the selected page
            self.stacked_widget.setCurrentWidget(self.pages[page_name])
            self.current_page = page_name
            
            # Refresh the page data
            if hasattr(self.pages[page_name], 'refresh_data'):
                self.pages[page_name].refresh_data()
            
            # Update status bar
            page_titles = {
                'dashboard': 'لوحة التحكم الرئيسية',
                'inventory': 'إدارة المخزون والمنتجات',
                'sales': 'نظام نقاط البيع',
                'repairs': 'إدارة طلبات الإصلاح',
                'wallet': 'معاملات المحفظة الإلكترونية',
                'reports': 'التقارير والإحصائيات'
            }
            self.status_bar.showMessage(page_titles.get(page_name, ""))
    
    def show_dashboard(self):
        """Show the dashboard page by default"""
        self.navigate_to('dashboard')
    
    def refresh_current_page(self):
        """Refresh the currently active page"""
        if self.current_page and hasattr(self.pages[self.current_page], 'refresh_data'):
            self.pages[self.current_page].refresh_data()
    
    def closeEvent(self, event):
        """Handle application close event"""
        # Close database connection
        if hasattr(self.db_manager, 'close'):
            self.db_manager.close()
        event.accept()