"""
Improved Dashboard Page with better UI and functionality
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton, 
    QFrame, QScrollArea, QTimer, QGroupBox, QMessageBox, QProgressBar
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QIcon, QPalette, QColor, QPixmap, QPainter
from datetime import datetime, timedelta
import math

class ModernStatCard(QFrame):
    """Modern styled statistics card with gradient background"""
    
    def __init__(self, title, value, icon, primary_color, secondary_color):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.primary_color = primary_color
        self.secondary_color = secondary_color
        self.setup_ui()
        
    def setup_ui(self):
        """Setup the modern card UI"""
        self.setFixedSize(280, 140)
        layout = QVBoxLayout(self)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(15)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setFixedSize(50, 50)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.secondary_color};
                border-radius: 25px;
                color: {self.primary_color};
                border: 2px solid {self.primary_color};
            }}
        """)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #64748b;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter)
        
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        header_layout.addWidget(icon_label)
        
        # Value
        self.value_label = QLabel(self.value)
        self.value_label.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.primary_color};")
        self.value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addStretch()
        
        # Modern card styling with gradient effect
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 white, stop:1 {self.secondary_color});
                border: 2px solid {self.primary_color.replace('#', 'rgba(').replace(')', ', 0.2)')}20;
                border-radius: 16px;
                border-left: 4px solid {self.primary_color};
            }}
            QFrame:hover {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.secondary_color}, stop:1 white);
                transform: translateY(-2px);
                border-color: {self.primary_color};
            }}
        """)
        
    def update_value(self, new_value):
        """Update the card value"""
        self.value_label.setText(new_value)

class ModernActionButton(QPushButton):
    """Modern styled action button with hover effects"""
    
    def __init__(self, text, icon, color, description=""):
        super().__init__()
        self.setText(f"{icon}  {text}")
        self.description = description
        self.color = color
        self.setup_style()
        
    def setup_style(self):
        """Setup modern button styling"""
        self.setFixedHeight(70)
        self.setFont(QFont("Tahoma", 13, QFont.Weight.Bold))
        self.setStyleSheet(f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.color}, stop:1 {self.darken_color(self.color, 0.1)});
                color: white;
                border: none;
                border-radius: 12px;
                padding: 15px 25px;
                text-align: center;
            }}
            QPushButton:hover {{
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 {self.lighten_color(self.color, 0.1)}, stop:1 {self.color});
                transform: translateY(-3px);
            }}
            QPushButton:pressed {{
                background: {self.darken_color(self.color, 0.2)};
                transform: translateY(0px);
            }}
        """)
        
    def darken_color(self, color, amount):
        """Darken a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(max(0, int(c * (1 - amount))) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"
        
    def lighten_color(self, color, amount):
        """Lighten a hex color"""
        color = color.lstrip('#')
        rgb = tuple(int(color[i:i+2], 16) for i in (0, 2, 4))
        rgb = tuple(min(255, int(c + (255 - c) * amount)) for c in rgb)
        return f"#{rgb[0]:02x}{rgb[1]:02x}{rgb[2]:02x}"

class AlertBanner(QFrame):
    """Modern alert banner"""
    
    def __init__(self, message, alert_type="info", dismissible=True):
        super().__init__()
        self.alert_type = alert_type
        self.setup_ui(message, dismissible)
        
    def setup_ui(self, message, dismissible):
        """Setup alert banner UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        
        # Alert icon
        icons = {
            "warning": "⚠️",
            "error": "🚨", 
            "info": "💡",
            "success": "✅"
        }
        
        colors = {
            "warning": ("#f59e0b", "#fef3c7", "#92400e"),
            "error": ("#ef4444", "#fee2e2", "#b91c1c"),
            "info": ("#3b82f6", "#dbeafe", "#1d4ed8"), 
            "success": ("#10b981", "#d1fae5", "#047857")
        }
        
        bg_color, border_color, text_color = colors.get(self.alert_type, colors["info"])
        
        icon_label = QLabel(icons.get(self.alert_type, "💡"))
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Tahoma", 11))
        message_label.setWordWrap(True)
        message_label.setStyleSheet(f"color: {text_color};")
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        if dismissible:
            close_btn = QPushButton("×")
            close_btn.setFixedSize(25, 25)
            close_btn.clicked.connect(self.hide)
            close_btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {text_color};
                    color: white;
                    border: none;
                    border-radius: 12px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {bg_color};
                }}
            """)
            layout.addWidget(close_btn)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {border_color};
                border: 2px solid {bg_color};
                border-radius: 10px;
                border-right: 6px solid {bg_color};
            }}
        """)

class ImprovedDashboardPage(QWidget):
    """Improved dashboard with modern UI and enhanced functionality"""
    
    # Signals for navigation
    navigate_to_sales = pyqtSignal()
    navigate_to_inventory = pyqtSignal()
    navigate_to_repairs = pyqtSignal()
    navigate_to_wallet = pyqtSignal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.stat_cards = {}
        self.setup_ui()
        self.setup_auto_refresh()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup the improved dashboard UI"""
        # Main scroll area for better mobile-like experience
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(40, 40, 40, 40)
        main_layout.setSpacing(30)
        
        # Header section
        self.setup_header(main_layout)
        
        # Statistics cards
        self.setup_modern_stats(main_layout)
        
        # Quick actions
        self.setup_modern_actions(main_layout)
        
        # Alerts section
        self.setup_modern_alerts(main_layout)
        
        # Recent activity (optional)
        self.setup_recent_activity(main_layout)
        
        scroll.setWidget(main_widget)
        
        # Main page layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
    def setup_header(self, parent_layout):
        """Setup modern header"""
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        # Welcome message
        welcome_label = QLabel("مرحباً بك في نظام إدارة المحل")
        welcome_label.setFont(QFont("Tahoma", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: #1e293b;")
        
        # Date and time
        datetime_label = QLabel(datetime.now().strftime("%Y/%m/%d - %H:%M"))
        datetime_label.setFont(QFont("Tahoma", 14))
        datetime_label.setStyleSheet("color: #64748b;")
        datetime_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        
        header_layout.addWidget(welcome_label)
        header_layout.addStretch()
        header_layout.addWidget(datetime_label)
        
        parent_layout.addWidget(header_frame)
        
    def setup_modern_stats(self, parent_layout):
        """Setup modern statistics cards"""
        stats_group = QGroupBox("إحصائيات اليوم")
        stats_group.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        stats_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px 10px;
                margin: 10px 0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        
        stats_layout = QGridLayout(stats_group)
        stats_layout.setContentsMargins(30, 40, 30, 30)
        stats_layout.setSpacing(25)
        
        # Create modern stat cards
        cards_config = [
            ("مبيعات اليوم", "0 جنيه", "💰", "#10b981", "#d1fae5"),
            ("عدد الطلبات", "0", "🛒", "#3b82f6", "#dbeafe"),
            ("إصلاحات جديدة", "0", "🔧", "#f59e0b", "#fef3c7"),
            ("نقص مخزون", "0", "📦", "#ef4444", "#fee2e2")
        ]
        
        for i, (title, value, icon, primary, secondary) in enumerate(cards_config):
            card = ModernStatCard(title, value, icon, primary, secondary)
            row, col = i // 2, i % 2
            stats_layout.addWidget(card, row, col)
            
            # Store cards for updates
            card_keys = ['sales', 'orders', 'repairs', 'low_stock']
            self.stat_cards[card_keys[i]] = card
        
        parent_layout.addWidget(stats_group)
        
    def setup_modern_actions(self, parent_layout):
        """Setup modern quick actions"""
        actions_group = QGroupBox("إجراءات سريعة")
        actions_group.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px 10px;
                margin: 10px 0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        
        actions_layout = QGridLayout(actions_group)
        actions_layout.setContentsMargins(30, 40, 30, 30)
        actions_layout.setSpacing(20)
        
        # Modern action buttons with proper connections
        actions_config = [
            ("فاتورة جديدة", "🧾", "#10b981", "إنشاء فاتورة مبيعات جديدة", self.navigate_to_sales.emit),
            ("إضافة منتج", "📦", "#3b82f6", "إضافة منتج جديد للمخزون", self.navigate_to_inventory.emit),
            ("طلب إصلاح", "🔧", "#f59e0b", "تسجيل طلب إصلاح جديد", self.navigate_to_repairs.emit),
            ("معاملة محفظة", "💳", "#8b5cf6", "تسجيل معاملة محفظة إلكترونية", self.navigate_to_wallet.emit)
        ]
        
        for i, (text, icon, color, desc, handler) in enumerate(actions_config):
            btn = ModernActionButton(text, icon, color, desc)
            btn.clicked.connect(handler)
            row, col = i // 2, i % 2
            actions_layout.addWidget(btn, row, col)
        
        parent_layout.addWidget(actions_group)
        
    def setup_modern_alerts(self, parent_layout):
        """Setup modern alerts section"""
        alerts_group = QGroupBox("التنبيهات والإشعارات")
        alerts_group.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        alerts_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px 10px;
                margin: 10px 0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        
        self.alerts_layout = QVBoxLayout(alerts_group)
        self.alerts_layout.setContentsMargins(30, 40, 30, 30)
        self.alerts_layout.setSpacing(15)
        
        # Placeholder
        no_alerts = QLabel("لا توجد تنبيهات حالياً")
        no_alerts.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_alerts.setStyleSheet("color: #94a3b8; font-size: 16px; padding: 30px;")
        self.alerts_layout.addWidget(no_alerts)
        
        parent_layout.addWidget(alerts_group)
        
    def setup_recent_activity(self, parent_layout):
        """Setup recent activity section"""
        activity_group = QGroupBox("النشاط الأخير")
        activity_group.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        activity_group.setStyleSheet("""
            QGroupBox {
                font-size: 18px;
                font-weight: bold;
                color: #374151;
                border: 2px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px 10px;
                margin: 10px 0;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top right;
                padding: 0 10px;
                background-color: white;
            }
        """)
        
        activity_layout = QVBoxLayout(activity_group)
        activity_layout.setContentsMargins(30, 40, 30, 30)
        
        # Recent activity items (placeholder)
        activities = [
            ("تم إنشاء فاتورة مبيعات #1001", "منذ ساعة واحدة", "success"),
            ("تم إضافة منتج جديد: جراب ايفون", "منذ ساعتين", "info"),
            ("تحذير: نقص مخزون في منتج الشواحن", "منذ 3 ساعات", "warning")
        ]
        
        for activity, time_ago, activity_type in activities:
            item_frame = QFrame()
            item_layout = QHBoxLayout(item_frame)
            item_layout.setContentsMargins(15, 10, 15, 10)
            
            activity_label = QLabel(activity)
            activity_label.setFont(QFont("Tahoma", 11))
            
            time_label = QLabel(time_ago)
            time_label.setFont(QFont("Tahoma", 9))
            time_label.setStyleSheet("color: #64748b;")
            
            item_layout.addWidget(activity_label)
            item_layout.addStretch()
            item_layout.addWidget(time_label)
            
            # Activity type styling
            colors = {
                "success": "#d1fae5",
                "info": "#dbeafe", 
                "warning": "#fef3c7"
            }
            
            item_frame.setStyleSheet(f"""
                QFrame {{
                    background-color: {colors.get(activity_type, '#f8fafc')};
                    border-radius: 8px;
                    border-right: 4px solid {
                        '#10b981' if activity_type == 'success' 
                        else '#3b82f6' if activity_type == 'info'
                        else '#f59e0b'
                    };
                    margin: 2px 0;
                }}
            """)
            
            activity_layout.addWidget(item_frame)
        
        parent_layout.addWidget(activity_group)
        
    def setup_auto_refresh(self):
        """Setup automatic refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # 30 seconds
        
    def refresh_data(self):
        """Refresh dashboard data"""
        try:
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Today's sales
            sales_query = """
                SELECT COALESCE(SUM(total), 0) as total_sales, COUNT(*) as order_count
                FROM sales 
                WHERE DATE(created_at) = ?
            """
            sales_data = self.db_manager.execute_query(sales_query, (today,))
            
            total_sales = sales_data[0]['total_sales'] if sales_data else 0
            order_count = sales_data[0]['order_count'] if sales_data else 0
            
            # Pending repairs
            repairs_query = """
                SELECT COUNT(*) as pending_repairs 
                FROM repair_tickets 
                WHERE status IN ('pending', 'in_progress')
            """
            repairs_data = self.db_manager.execute_query(repairs_query)
            pending_repairs = repairs_data[0]['pending_repairs'] if repairs_data else 0
            
            # Low stock products
            low_stock_query = """
                SELECT COUNT(*) as low_stock_count 
                FROM products 
                WHERE current_qty <= min_stock
            """
            low_stock_data = self.db_manager.execute_query(low_stock_query)
            low_stock_count = low_stock_data[0]['low_stock_count'] if low_stock_data else 0
            
            # Update cards
            self.stat_cards['sales'].update_value(f"{total_sales:.0f} جنيه")
            self.stat_cards['orders'].update_value(str(order_count))
            self.stat_cards['repairs'].update_value(str(pending_repairs))
            self.stat_cards['low_stock'].update_value(str(low_stock_count))
            
            # Update alerts
            self.update_alerts(low_stock_count, pending_repairs)
            
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
    
    def update_alerts(self, low_stock_count, pending_repairs):
        """Update alerts section"""
        # Clear existing alerts
        for i in reversed(range(self.alerts_layout.count())):
            child = self.alerts_layout.itemAt(i).widget()
            if child:
                child.setParent(None)
        
        alerts_added = 0
        
        # Low stock alert
        if low_stock_count > 0:
            alert = AlertBanner(
                f"تحذير: يوجد {low_stock_count} منتج بمخزون منخفض",
                "warning"
            )
            self.alerts_layout.addWidget(alert)
            alerts_added += 1
        
        # Pending repairs alert
        if pending_repairs > 0:
            alert = AlertBanner(
                f"يوجد {pending_repairs} طلب إصلاح في الانتظار",
                "info"
            )
            self.alerts_layout.addWidget(alert)
            alerts_added += 1
        
        # No alerts message
        if alerts_added == 0:
            no_alerts = QLabel("لا توجد تنبيهات حالياً ✅")
            no_alerts.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_alerts.setStyleSheet("color: #10b981; font-size: 16px; padding: 30px; font-weight: bold;")
            self.alerts_layout.addWidget(no_alerts)