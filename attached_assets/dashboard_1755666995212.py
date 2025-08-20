"""
Dashboard Page for Mobile Shop Management System
Shows overview statistics and alerts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
    QLabel, QFrame, QScrollArea, QListWidget, QListWidgetItem,
    QPushButton, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont, QPalette, QColor
from datetime import datetime, timedelta

class StatCard(QFrame):
    """Custom widget for displaying statistics"""
    
    def __init__(self, title, value, icon, color="#3b82f6"):
        super().__init__()
        self.setup_ui(title, value, icon, color)
        
    def setup_ui(self, title, value, icon, color):
        """Setup the stat card UI"""
        self.setFixedHeight(120)
        self.setFrameStyle(QFrame.Shape.Box)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 15, 20, 15)
        layout.setSpacing(5)
        
        # Icon and value row
        top_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setStyleSheet(f"font-size: 24px; color: {color};")
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label = QLabel(str(value))
        value_label.setAlignment(Qt.AlignmentFlag.AlignLeft)
        value_label.setFont(QFont("Tahoma", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        
        top_layout.addWidget(icon_label)
        top_layout.addStretch()
        top_layout.addWidget(value_label)
        
        # Title
        title_label = QLabel(title)
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        title_label.setFont(QFont("Tahoma", 12))
        title_label.setStyleSheet("color: #64748b;")
        
        layout.addLayout(top_layout)
        layout.addWidget(title_label)
        
        # Styling - Fixed CSS without box-shadow
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
            }
            QFrame:hover {
                border-color: #cbd5e1;
                background-color: #f8fafc;
            }
        """)

class AlertItem(QFrame):
    """Custom widget for displaying alerts"""
    
    def __init__(self, message, alert_type="info"):
        super().__init__()
        self.setup_ui(message, alert_type)
        
    def setup_ui(self, message, alert_type):
        """Setup the alert item UI"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(15, 10, 15, 10)
        
        # Icon based on alert type
        icons = {
            "warning": "⚠️",
            "error": "❌", 
            "info": "ℹ️",
            "success": "✅"
        }
        
        colors = {
            "warning": "#f59e0b",
            "error": "#ef4444",
            "info": "#3b82f6", 
            "success": "#10b981"
        }
        
        icon_label = QLabel(icons.get(alert_type, "ℹ️"))
        icon_label.setStyleSheet("font-size: 16px;")
        
        message_label = QLabel(message)
        message_label.setFont(QFont("Tahoma", 10))
        message_label.setWordWrap(True)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        
        # Styling
        bg_colors = {
            "warning": "#fef3c7",
            "error": "#fee2e2",
            "info": "#dbeafe",
            "success": "#d1fae5"
        }
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {bg_colors.get(alert_type, "#dbeafe")};
                border: 1px solid {colors.get(alert_type, "#3b82f6")};
                border-radius: 6px;
                margin: 2px 0;
            }}
        """)

class DashboardPage(QWidget):
    """Main dashboard page showing business overview"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.setup_auto_refresh()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # Page title
        title_label = QLabel("لوحة التحكم الرئيسية")
        title_label.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        title_label.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(title_label)
        
        # Statistics cards
        self.setup_stats_section(layout)
        
        # Alerts and notifications
        self.setup_alerts_section(layout)
        
        # Quick actions
        self.setup_quick_actions(layout)
        
        layout.addStretch()
        
    def setup_stats_section(self, parent_layout):
        """Setup the statistics cards section"""
        stats_label = QLabel("إحصائيات اليوم")
        stats_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        stats_label.setStyleSheet("color: #374151; margin-bottom: 15px;")
        parent_layout.addWidget(stats_label)
        
        # Stats grid
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        # Create stat cards (will be updated with real data)
        self.stat_cards = {
            'sales': StatCard("مبيعات اليوم", "0 جنيه", "💰", "#10b981"),
            'orders': StatCard("عدد الطلبات", "0", "🛒", "#3b82f6"),
            'repairs': StatCard("إصلاحات جديدة", "0", "🔧", "#f59e0b"),
            'low_stock': StatCard("نقص مخزون", "0", "📦", "#ef4444")
        }
        
        # Add to grid (2x2)
        stats_layout.addWidget(self.stat_cards['sales'], 0, 0)
        stats_layout.addWidget(self.stat_cards['orders'], 0, 1)
        stats_layout.addWidget(self.stat_cards['repairs'], 1, 0)
        stats_layout.addWidget(self.stat_cards['low_stock'], 1, 1)
        
        parent_layout.addLayout(stats_layout)
        
    def setup_alerts_section(self, parent_layout):
        """Setup the alerts and notifications section"""
        alerts_label = QLabel("التنبيهات والإشعارات")
        alerts_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        alerts_label.setStyleSheet("color: #374151; margin: 20px 0 15px 0;")
        parent_layout.addWidget(alerts_label)
        
        # Alerts container
        alerts_frame = QFrame()
        alerts_frame.setMaximumHeight(200)
        alerts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e2e8f0;
                border-radius: 8px;
                padding: 10px;
            }
        """)
        
        self.alerts_layout = QVBoxLayout(alerts_frame)
        self.alerts_layout.setContentsMargins(10, 10, 10, 10)
        self.alerts_layout.setSpacing(5)
        
        # Placeholder message
        no_alerts_label = QLabel("لا توجد تنبيهات حالياً")
        no_alerts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        no_alerts_label.setStyleSheet("color: #94a3b8; font-size: 14px; padding: 20px;")
        self.alerts_layout.addWidget(no_alerts_label)
        
        parent_layout.addWidget(alerts_frame)
        
    def setup_quick_actions(self, parent_layout):
        """Setup quick action buttons"""
        actions_label = QLabel("إجراءات سريعة")
        actions_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        actions_label.setStyleSheet("color: #374151; margin: 20px 0 15px 0;")
        parent_layout.addWidget(actions_label)
        
        # Actions layout
        actions_layout = QHBoxLayout()
        actions_layout.setSpacing(15)
        
        # Quick action buttons
        buttons = [
            ("فاتورة جديدة", "🧾", "#10b981"),
            ("إضافة منتج", "📦", "#3b82f6"),
            ("طلب إصلاح", "🔧", "#f59e0b"),
            ("معاملة محفظة", "💳", "#8b5cf6")
        ]
        
        self.action_buttons = {}
        for i, (text, icon, color) in enumerate(buttons):
            btn = QPushButton(f"{icon}  {text}")
            btn.setFixedHeight(50)
            btn.setFont(QFont("Tahoma", 12))
            btn.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 12px 20px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: rgba(59, 130, 246, 0.8);
                }}
                QPushButton:pressed {{
                    background-color: rgba(59, 130, 246, 0.6);
                }}
            """)
            
            # Connect button actions
            if i == 0:  # فاتورة جديدة
                btn.clicked.connect(lambda: self.show_message("سيتم فتح صفحة المبيعات"))
            elif i == 1:  # إضافة منتج
                btn.clicked.connect(lambda: self.show_message("سيتم فتح صفحة المخزون"))
            elif i == 2:  # طلب إصلاح
                btn.clicked.connect(lambda: self.show_message("سيتم فتح صفحة الإصلاحات"))
            elif i == 3:  # معاملة محفظة
                btn.clicked.connect(lambda: self.show_message("سيتم فتح صفحة المحفظة"))
                
            self.action_buttons[text] = btn
            actions_layout.addWidget(btn)
        
        parent_layout.addLayout(actions_layout)
        
    def show_message(self, message):
        """Show information message"""
        QMessageBox.information(self, "معلومات", message)
        
    def setup_auto_refresh(self):
        """Setup automatic data refresh timer"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
    def refresh_data(self):
        """Refresh dashboard data from database"""
        try:
            # Get today's date
            today = datetime.now().strftime('%Y-%m-%d')
            
            # Today's sales
            sales_query = """
                SELECT COALESCE(SUM(total), 0) as total_sales, COUNT(*) as order_count
                FROM sales 
                WHERE DATE(created_at) = ?
            """
            sales_data = self.db_manager.execute_query(sales_query, (today,))
            
            if sales_data:
                total_sales = sales_data[0]['total_sales']
                order_count = sales_data[0]['order_count']
            else:
                total_sales = 0
                order_count = 0
            
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
            
            # Update stat cards
            self.update_stat_card('sales', f"{total_sales:.0f} جنيه")
            self.update_stat_card('orders', str(order_count))
            self.update_stat_card('repairs', str(pending_repairs))
            self.update_stat_card('low_stock', str(low_stock_count))
            
            # Update alerts
            self.update_alerts(low_stock_count, pending_repairs)
            
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
    
    def update_stat_card(self, card_key, new_value):
        """Update a specific stat card value"""
        if card_key in self.stat_cards:
            # Find the value label and update it
            card = self.stat_cards[card_key]
            layout = card.layout()
            if layout:
                top_layout = layout.itemAt(0).layout()
                if top_layout and top_layout.count() >= 3:
                    value_label = top_layout.itemAt(2).widget()
                    if isinstance(value_label, QLabel):
                        value_label.setText(new_value)
    
    def update_alerts(self, low_stock_count, pending_repairs):
        """Update the alerts section with current issues"""
        # Clear existing alerts
        for i in reversed(range(self.alerts_layout.count())):
            child = self.alerts_layout.itemAt(i).widget()
            if child:
                child.deleteLater()
        
        alerts_added = False
        
        # Low stock alert
        if low_stock_count > 0:
            alert = AlertItem(f"يوجد {low_stock_count} منتج بحاجة لإعادة تعبئة المخزون", "warning")
            self.alerts_layout.addWidget(alert)
            alerts_added = True
        
        # Pending repairs alert
        if pending_repairs > 0:
            alert = AlertItem(f"يوجد {pending_repairs} طلب إصلاح في الانتظار", "info")
            self.alerts_layout.addWidget(alert)
            alerts_added = True
        
        # Add welcome message if no alerts
        if not alerts_added:
            no_alerts_label = QLabel("جميع العمليات تسير بسلاسة! ✨")
            no_alerts_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            no_alerts_label.setStyleSheet("color: #10b981; font-size: 14px; padding: 20px;")
            self.alerts_layout.addWidget(no_alerts_label)
        
        self.alerts_layout.addStretch()
    
    def darken_color(self, hex_color, factor=0.1):
        """Darken a hex color by a given factor"""
        # Remove # if present
        hex_color = hex_color.lstrip('#')
        
        # Convert to RGB
        rgb = tuple(int(hex_color[i:i+2], 16) for i in (0, 2, 4))
        
        # Darken
        darkened = tuple(int(c * (1 - factor)) for c in rgb)
        
        # Convert back to hex
        return f"#{''.join(f'{c:02x}' for c in darkened)}"