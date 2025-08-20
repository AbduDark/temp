"""
Enhanced Main Window for Mobile Shop Management System
PyQt6 implementation with beautiful modern UI and Arabic RTL support
"""

from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, 
    QStackedWidget, QFrame, QPushButton, QLabel,
    QMenuBar, QStatusBar, QSplitter, QScrollArea,
    QGraphicsDropShadowEffect, QApplication, QMessageBox
)
from PyQt6.QtCore import Qt, pyqtSignal, QSize, QTimer, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QIcon, QPixmap, QPalette, QColor, QPainter, QLinearGradient

from pages.dashboard import DashboardPage
from pages.inventory import InventoryPage
from pages.sales import SalesPage
from pages.repairs import RepairsPage
from pages.wallet import WalletPage
from pages.reports import ReportsPage
from ui.styles import ModernStyles

class AnimatedButton(QPushButton):
    """Custom animated button with hover effects"""
    
    def __init__(self, text, icon="", parent=None):
        super().__init__(text, parent)
        self.icon_text = icon
        self.is_hovered = False
        self.is_active = False
        self.setup_animation()
        
    def setup_animation(self):
        """Setup button animations"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.InOutCubic)
        
    def set_active(self, active):
        """Set button active state"""
        self.is_active = active
        self.update_style()
        
    def update_style(self):
        """Update button style based on state"""
        if self.is_active:
            self.setStyleSheet(ModernStyles.get_active_nav_button_style())
        elif self.is_hovered:
            self.setStyleSheet(ModernStyles.get_hover_nav_button_style())
        else:
            self.setStyleSheet(ModernStyles.get_nav_button_style())
    
    def enterEvent(self, event):
        """Handle mouse enter event"""
        self.is_hovered = True
        if not self.is_active:
            self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave event"""
        self.is_hovered = False
        if not self.is_active:
            self.update_style()
        super().leaveEvent(event)

class NotificationBar(QFrame):
    """Top notification bar for important messages"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
        self.hide()  # Hidden by default
        
    def setup_ui(self):
        """Setup notification bar UI"""
        self.setFixedHeight(40)
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #f56565, stop:1 #fc8181);
                border: none;
                border-radius: 0px;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 8, 20, 8)
        
        self.icon_label = QLabel("⚠️")
        self.icon_label.setStyleSheet("color: white; font-size: 16px;")
        
        self.message_label = QLabel()
        self.message_label.setStyleSheet("color: white; font-weight: bold; font-size: 12px;")
        
        self.close_button = QPushButton("✕")
        self.close_button.setFixedSize(24, 24)
        self.close_button.setStyleSheet("""
            QPushButton {
                background: transparent;
                color: white;
                border: 1px solid rgba(255,255,255,0.3);
                border-radius: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background: rgba(255,255,255,0.2);
            }
        """)
        self.close_button.clicked.connect(self.hide)
        
        layout.addWidget(self.icon_label)
        layout.addWidget(self.message_label, 1)
        layout.addWidget(self.close_button)
        
    def show_message(self, message, message_type="warning"):
        """Show notification message"""
        self.message_label.setText(message)
        
        if message_type == "error":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #f56565, stop:1 #fc8181);
                    border: none;
                }
            """)
            self.icon_label.setText("❌")
        elif message_type == "success":
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #48bb78, stop:1 #68d391);
                    border: none;
                }
            """)
            self.icon_label.setText("✅")
        else:  # warning
            self.setStyleSheet("""
                QFrame {
                    background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                        stop:0 #ed8936, stop:1 #f6ad55);
                    border: none;
                }
            """)
            self.icon_label.setText("⚠️")
        
        self.show()
        
        # Auto hide after 5 seconds
        QTimer.singleShot(5000, self.hide)

class ModernSidebar(QFrame):
    """Modern sidebar with beautiful design"""
    
    navigation_requested = pyqtSignal(str)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.nav_buttons = {}
        self.current_page = None
        self.setup_ui()
        
    def setup_ui(self):
        """Setup sidebar UI"""
        self.setFixedWidth(280)
        self.setStyleSheet(ModernStyles.get_sidebar_style())
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 30))
        shadow.setOffset(3, 0)
        self.setGraphicsEffect(shadow)
        
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Header section
        self.setup_header(main_layout)
        
        # Navigation section  
        self.setup_navigation(main_layout)
        
        # Footer section
        self.setup_footer(main_layout)
        
    def setup_header(self, parent_layout):
        """Setup sidebar header"""
        header_frame = QFrame()
        header_frame.setFixedHeight(120)
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border: none;
                border-radius: 0px;
            }
        """)
        
        header_layout = QVBoxLayout(header_frame)
        header_layout.setContentsMargins(20, 20, 20, 20)
        header_layout.setSpacing(8)
        
        # Logo
        logo_label = QLabel("🏪")
        logo_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        logo_label.setStyleSheet("font-size: 36px; color: white;")
        
        # Title
        title_label = QLabel("إدارة محل الموبايل")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        title_label.setStyleSheet("color: white;")
        
        # Subtitle
        subtitle_label = QLabel("نظام شامل ومتطور")
        subtitle_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        subtitle_label.setFont(QFont("Tahoma", 10))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.8);")
        
        header_layout.addWidget(logo_label)
        header_layout.addWidget(title_label)
        header_layout.addWidget(subtitle_label)
        
        parent_layout.addWidget(header_frame)
        
    def setup_navigation(self, parent_layout):
        """Setup navigation buttons"""
        nav_frame = QFrame()
        nav_layout = QVBoxLayout(nav_frame)
        nav_layout.setContentsMargins(15, 20, 15, 10)
        nav_layout.setSpacing(8)
        
        # Navigation items with modern icons
        nav_items = [
            ("dashboard", "الرئيسية", "🏠", "لوحة التحكم والإحصائيات"),
            ("inventory", "المخزون", "📦", "إدارة المنتجات والمخزون"),
            ("sales", "المبيعات", "🛒", "نظام نقاط البيع"),
            ("repairs", "الإصلاحات", "🔧", "إدارة طلبات الإصلاح"),
            ("wallet", "المحفظة", "💰", "معاملات المحفظة الإلكترونية"),
            ("reports", "التقارير", "📊", "التقارير والإحصائيات")
        ]
        
        for key, text, icon, tooltip in nav_items:
            btn = AnimatedButton(f"  {text}", icon)
            btn.setFixedHeight(60)
            btn.setToolTip(tooltip)
            btn.clicked.connect(lambda checked, k=key: self.navigate_to(k))
            btn.update_style()
            
            self.nav_buttons[key] = btn
            nav_layout.addWidget(btn)
        
        nav_layout.addStretch()
        parent_layout.addWidget(nav_frame, 1)
        
    def setup_footer(self, parent_layout):
        """Setup sidebar footer"""
        footer_frame = QFrame()
        footer_frame.setFixedHeight(80)
        footer_frame.setStyleSheet("""
            QFrame {
                background: rgba(0, 0, 0, 0.05);
                border: none;
                border-top: 1px solid rgba(0, 0, 0, 0.1);
            }
        """)
        
        footer_layout = QVBoxLayout(footer_frame)
        footer_layout.setContentsMargins(20, 15, 20, 15)
        footer_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        version_label = QLabel("الإصدار 2.0.0")
        version_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        version_label.setFont(QFont("Tahoma", 9))
        version_label.setStyleSheet("color: #718096;")
        
        copyright_label = QLabel("© 2024 Mobile Shop")
        copyright_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        copyright_label.setFont(QFont("Tahoma", 8))
        copyright_label.setStyleSheet("color: #a0aec0;")
        
        footer_layout.addWidget(version_label)
        footer_layout.addWidget(copyright_label)
        
        parent_layout.addWidget(footer_frame)
        
    def navigate_to(self, page_name):
        """Handle navigation"""
        # Update button states
        for key, btn in self.nav_buttons.items():
            btn.set_active(key == page_name)
        
        self.current_page = page_name
        self.navigation_requested.emit(page_name)

class MainWindow(QMainWindow):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_page = None
        self.setup_window()
        self.setup_ui()
        self.setup_status_updates()
        self.show_dashboard()
        
    def setup_window(self):
        """Setup main window properties"""
        self.setWindowTitle("نظام إدارة محل الموبايل - الإصدار المتطور")
        self.setMinimumSize(1400, 900)
        self.resize(1600, 1000)
        
        # Center window on screen
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
        
        # Apply modern styles
        self.setStyleSheet(ModernStyles.get_main_window_style())
        
    def setup_ui(self):
        """Setup the main user interface"""
        # Create central widget
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        # Main layout
        main_layout = QVBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Notification bar
        self.notification_bar = NotificationBar()
        main_layout.addWidget(self.notification_bar)
        
        # Content layout
        content_layout = QHBoxLayout()
        content_layout.setContentsMargins(0, 0, 0, 0)
        content_layout.setSpacing(0)
        
        # Create sidebar
        self.sidebar = ModernSidebar()
        self.sidebar.navigation_requested.connect(self.navigate_to)
        
        # Create content area
        self.setup_content_area()
        
        # Add to content layout
        content_layout.addWidget(self.sidebar)
        content_layout.addWidget(self.content_frame, 1)
        
        content_widget = QWidget()
        content_widget.setLayout(content_layout)
        main_layout.addWidget(content_widget, 1)
        
        # Setup status bar
        self.setup_status_bar()
        
    def setup_content_area(self):
        """Create and setup the main content area"""
        self.content_frame = QFrame()
        self.content_frame.setStyleSheet("""
            QFrame {
                background-color: #f8fafc;
                border: none;
            }
        """)
        
        content_layout = QVBoxLayout(self.content_frame)
        content_layout.setContentsMargins(0, 0, 0, 0)
        
        # Create stacked widget for pages
        self.stacked_widget = QStackedWidget()
        content_layout.addWidget(self.stacked_widget)
        
        # Initialize pages
        try:
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
                
        except Exception as e:
            self.show_error(f"فشل في تحميل الصفحات: {str(e)}")
    
    def setup_status_bar(self):
        """Setup enhanced status bar"""
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        
        self.status_bar.setStyleSheet("""
            QStatusBar {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #ffffff, stop:1 #f8fafc);
                border-top: 1px solid #e2e8f0;
                color: #4a5568;
                padding: 5px 15px;
                font-weight: 500;
            }
            QStatusBar::item {
                border: none;
            }
        """)
        
        # Add status widgets
        self.db_status_label = QLabel("🟢 قاعدة البيانات متصلة")
        self.db_status_label.setStyleSheet("color: #38a169; font-weight: bold;")
        
        self.time_label = QLabel()
        self.time_label.setStyleSheet("color: #718096;")
        
        self.user_label = QLabel("👤 المدير العام")
        self.user_label.setStyleSheet("color: #4a5568; font-weight: bold;")
        
        self.status_bar.addWidget(self.db_status_label)
        self.status_bar.addPermanentWidget(self.user_label)
        self.status_bar.addPermanentWidget(self.time_label)
        
        self.status_bar.showMessage("مرحباً بك في نظام إدارة محل الموبايل المتطور")
        
    def setup_status_updates(self):
        """Setup automatic status updates"""
        # Update time every second
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_time)
        self.time_timer.start(1000)
        
        # Check database status every 30 seconds
        self.db_timer = QTimer()
        self.db_timer.timeout.connect(self.check_database_status)
        self.db_timer.start(30000)
        
        # Initial updates
        self.update_time()
        self.check_database_status()
        
    def update_time(self):
        """Update time display"""
        from datetime import datetime
        current_time = datetime.now().strftime("%I:%M:%S %p")
        current_date = datetime.now().strftime("%A, %d %B %Y")
        self.time_label.setText(f"🕐 {current_time} - {current_date}")
        
    def check_database_status(self):
        """Check database connection status"""
        try:
            # Simple test query
            self.db_manager.execute_query("SELECT 1")
            self.db_status_label.setText("🟢 قاعدة البيانات متصلة")
            self.db_status_label.setStyleSheet("color: #38a169; font-weight: bold;")
        except:
            self.db_status_label.setText("🔴 خطأ في قاعدة البيانات")
            self.db_status_label.setStyleSheet("color: #e53e3e; font-weight: bold;")
    
    def navigate_to(self, page_name):
        """Navigate to a specific page with error handling"""
        try:
            if page_name in self.pages:
                # Show the selected page
                self.stacked_widget.setCurrentWidget(self.pages[page_name])
                self.current_page = page_name
                
                # Refresh the page data
                if hasattr(self.pages[page_name], 'refresh_data'):
                    self.pages[page_name].refresh_data()
                
                # Update status bar
                page_titles = {
                    'dashboard': 'لوحة التحكم الرئيسية - عرض الإحصائيات والتنبيهات',
                    'inventory': 'إدارة المخزون والمنتجات - إضافة وتعديل المنتجات',
                    'sales': 'نظام نقاط البيع - إنشاء فواتير المبيعات',
                    'repairs': 'إدارة طلبات الإصلاح - تتبع حالة الإصلاحات',
                    'wallet': 'معاملات المحفظة الإلكترونية - فودافون وأورانج واتصالات',
                    'reports': 'التقارير والإحصائيات الشاملة - تحليل الأداء'
                }
                self.status_bar.showMessage(page_titles.get(page_name, ""))
                
                # Show success notification for navigation
                if hasattr(self, 'notification_bar'):
                    page_names = {
                        'dashboard': 'الرئيسية',
                        'inventory': 'المخزون', 
                        'sales': 'المبيعات',
                        'repairs': 'الإصلاحات',
                        'wallet': 'المحفظة',
                        'reports': 'التقارير'
                    }
                    # Don't show notification for dashboard (initial load)
                    if page_name != 'dashboard' or self.current_page is not None:
                        self.notification_bar.show_message(
                            f"تم الانتقال إلى صفحة {page_names.get(page_name, page_name)}", 
                            "success"
                        )
                        
        except Exception as e:
            self.show_error(f"فشل في التنقل إلى الصفحة: {str(e)}")
    
    def show_dashboard(self):
        """Show the dashboard page by default"""
        self.navigate_to('dashboard')
        
    def show_notification(self, message, message_type="info"):
        """Show notification message"""
        if hasattr(self, 'notification_bar'):
            self.notification_bar.show_message(message, message_type)
            
    def show_error(self, message):
        """Show error message"""
        self.show_notification(message, "error")
        QMessageBox.critical(self, "خطأ", message)
        
    def show_success(self, message):
        """Show success message"""
        self.show_notification(message, "success")
        
    def refresh_current_page(self):
        """Refresh the currently active page"""
        if self.current_page and hasattr(self.pages[self.current_page], 'refresh_data'):
            try:
                self.pages[self.current_page].refresh_data()
                self.show_success("تم تحديث البيانات بنجاح")
            except Exception as e:
                self.show_error(f"فشل في تحديث البيانات: {str(e)}")
    
    def closeEvent(self, event):
        """Handle application close event"""
        reply = QMessageBox.question(
            self, 'تأكيد الإغلاق', 
            'هل أنت متأكد من إغلاق التطبيق؟',
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Close database connection
                if hasattr(self.db_manager, 'close'):
                    self.db_manager.close()
                
                # Stop timers
                if hasattr(self, 'time_timer'):
                    self.time_timer.stop()
                if hasattr(self, 'db_timer'):
                    self.db_timer.stop()
                    
                event.accept()
            except Exception as e:
                self.show_error(f"خطأ أثناء الإغلاق: {str(e)}")
                event.accept()  # Close anyway
        else:
            event.ignore()
