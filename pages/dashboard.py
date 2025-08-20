"""
Enhanced Dashboard Page for Mobile Shop Management System
Beautiful modern dashboard with comprehensive statistics and charts
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QScrollArea, QProgressBar, QTableWidget, QTableWidgetItem,
    QGraphicsDropShadowEffect, QSpacerItem, QSizePolicy
)
from PyQt6.QtCore import Qt, QTimer, QPropertyAnimation, QEasingCurve, pyqtSignal
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient
from datetime import datetime, timedelta
import calendar

from ui.styles import ModernStyles

class AnimatedStatCard(QFrame):
    """Animated statistics card with beautiful design"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title, value, icon, color="#3b82f6", trend=None, trend_value=None):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.trend = trend
        self.trend_value = trend_value
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        """Setup card UI"""
        self.setFixedHeight(140)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 16px;
                padding: 20px;
                border-left: 4px solid {self.color};
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
                transform: translateY(-2px);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setFixedSize(40, 40)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        icon_label.setStyleSheet(f"""
            QLabel {{
                background-color: {self.color}20;
                border-radius: 20px;
                color: {self.color};
            }}
        """)
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Tahoma", 11, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #6b7280; margin-left: 10px;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color}; margin: 8px 0;")
        
        # Trend
        trend_layout = QHBoxLayout()
        if self.trend and self.trend_value is not None:
            trend_icon = "📈" if self.trend == "up" else "📉" if self.trend == "down" else "➡️"
            trend_color = "#10b981" if self.trend == "up" else "#ef4444" if self.trend == "down" else "#6b7280"
            
            trend_icon_label = QLabel(trend_icon)
            trend_icon_label.setFont(QFont("Segoe UI Emoji", 12))
            
            trend_label = QLabel(f"{self.trend_value:+.1f}%" if isinstance(self.trend_value, (int, float)) else str(self.trend_value))
            trend_label.setStyleSheet(f"color: {trend_color}; font-size: 11px; font-weight: bold;")
            
            trend_layout.addWidget(trend_icon_label)
            trend_layout.addWidget(trend_label)
            trend_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addLayout(trend_layout)
        
    def setup_animation(self):
        """Setup hover animation"""
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)
        
    def update_value(self, new_value, trend=None, trend_value=None):
        """Update card value with animation"""
        self.value = new_value
        self.trend = trend
        self.trend_value = trend_value
        self.value_label.setText(str(new_value))

class QuickActionButton(QPushButton):
    """Quick action button with icon and description"""
    
    def __init__(self, title, description, icon, color="#3b82f6"):
        super().__init__()
        self.title = title
        self.description = description
        self.icon = icon
        self.color = color
        self.setup_ui()
        
    def setup_ui(self):
        """Setup button UI"""
        self.setFixedHeight(80)
        self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        self.setStyleSheet(f"""
            QPushButton {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 15px;
                text-align: right;
                border-left: 3px solid {self.color};
            }}
            QPushButton:hover {{
                background-color: {self.color}08;
                border-color: {self.color};
                transform: translateY(-1px);
            }}
            QPushButton:pressed {{
                background-color: {self.color}15;
            }}
        """)
        
        # Custom text with icon
        self.setText(f"{self.icon}  {self.title}\n{self.description}")
        self.setFont(QFont("Tahoma", 10, QFont.Weight.DemiBold))

class RecentActivityWidget(QFrame):
    """Recent activity display widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup widget UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📋 النشاط الأخير")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Activity list
        self.activity_layout = QVBoxLayout()
        layout.addLayout(self.activity_layout)
        
        layout.addStretch()
        
    def add_activity(self, icon, title, description, time_str, color="#6b7280"):
        """Add activity item"""
        activity_frame = QFrame()
        activity_frame.setStyleSheet(f"""
            QFrame {{
                background-color: #f9fafb;
                border: none;
                border-radius: 8px;
                padding: 10px;
                border-left: 3px solid {color};
            }}
        """)
        
        activity_layout = QHBoxLayout(activity_frame)
        activity_layout.setContentsMargins(12, 8, 12, 8)
        
        # Icon
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        icon_label.setFixedSize(30, 30)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Content
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #374151;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Tahoma", 9))
        desc_label.setStyleSheet("color: #6b7280;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        # Time
        time_label = QLabel(time_str)
        time_label.setFont(QFont("Tahoma", 8))
        time_label.setStyleSheet("color: #9ca3af;")
        time_label.setAlignment(Qt.AlignmentFlag.AlignTop)
        
        activity_layout.addWidget(icon_label)
        activity_layout.addLayout(content_layout, 1)
        activity_layout.addWidget(time_label)
        
        self.activity_layout.addWidget(activity_frame)
        
    def refresh_activities(self):
        """Refresh recent activities"""
        # Clear existing activities
        for i in reversed(range(self.activity_layout.count())):
            self.activity_layout.itemAt(i).widget().setParent(None)
        
        try:
            # Recent sales
            recent_sales = self.db_manager.execute_query("""
                SELECT * FROM sales 
                ORDER BY created_at DESC 
                LIMIT 3
            """)
            
            for sale in recent_sales:
                self.add_activity(
                    "💰", 
                    f"مبيعات بقيمة {sale['total']:.2f} جنيه",
                    f"العميل: {sale.get('customer_name', 'غير محدد')}",
                    sale['created_at'][:16],
                    "#10b981"
                )
            
            # Recent repairs
            recent_repairs = self.db_manager.execute_query("""
                SELECT * FROM repairs 
                ORDER BY created_at DESC 
                LIMIT 2
            """)
            
            for repair in recent_repairs:
                self.add_activity(
                    "🔧",
                    f"إصلاح {repair['device_type']} {repair['device_model']}",
                    f"العميل: {repair['customer_name']} - الحالة: {repair['status']}",
                    repair['created_at'][:16],
                    "#f59e0b"
                )
                
        except Exception as e:
            self.add_activity(
                "❌",
                "خطأ في تحميل البيانات",
                str(e),
                datetime.now().strftime("%Y-%m-%d %H:%M"),
                "#ef4444"
            )

class DashboardPage(QWidget):
    """Enhanced dashboard page with beautiful modern design"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.setup_auto_refresh()
        
    def setup_ui(self):
        """Setup dashboard UI"""
        # Main scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        scroll.setStyleSheet(ModernStyles.get_scroll_area_style())
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # Header section
        self.setup_header(main_layout)
        
        # Statistics cards
        self.setup_statistics_cards(main_layout)
        
        # Quick actions
        self.setup_quick_actions(main_layout)
        
        # Content sections
        content_layout = QHBoxLayout()
        content_layout.setSpacing(25)
        
        # Left column
        left_column = QVBoxLayout()
        self.setup_low_stock_alerts(left_column)
        self.setup_pending_repairs(left_column)
        
        # Right column  
        right_column = QVBoxLayout()
        self.setup_recent_activity(right_column)
        self.setup_daily_summary(right_column)
        
        left_widget = QWidget()
        left_widget.setLayout(left_column)
        right_widget = QWidget()
        right_widget.setLayout(right_column)
        
        content_layout.addWidget(left_widget, 1)
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addLayout(content_layout)
        
        scroll.setWidget(main_widget)
        
        # Main page layout
        page_layout = QVBoxLayout(self)
        page_layout.setContentsMargins(0, 0, 0, 0)
        page_layout.addWidget(scroll)
        
    def setup_header(self, parent_layout):
        """Setup dashboard header"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 20px;
                padding: 30px;
            }
        """)
        
        # Add shadow
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(20)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 5)
        header_frame.setGraphicsEffect(shadow)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Welcome text
        welcome_layout = QVBoxLayout()
        
        welcome_label = QLabel("مرحباً بك في نظام إدارة محل الموبايل")
        welcome_label.setFont(QFont("Tahoma", 24, QFont.Weight.Bold))
        welcome_label.setStyleSheet("color: white;")
        
        subtitle_label = QLabel("لوحة التحكم الشاملة - مراقبة الأداء والإحصائيات")
        subtitle_label.setFont(QFont("Tahoma", 13))
        subtitle_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        welcome_layout.addWidget(welcome_label)
        welcome_layout.addWidget(subtitle_label)
        
        # Date and time
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        self.datetime_label.setStyleSheet("color: white;")
        self.datetime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_datetime()
        
        header_layout.addLayout(welcome_layout, 1)
        header_layout.addWidget(self.datetime_label)
        
        parent_layout.addWidget(header_frame)
        
    def setup_statistics_cards(self, parent_layout):
        """Setup statistics cards"""
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Create stat cards
        self.sales_card = AnimatedStatCard("المبيعات اليومية", "0 جنيه", "💰", "#10b981")
        self.orders_card = AnimatedStatCard("عدد الفواتير", "0", "🧾", "#3b82f6")
        self.repairs_card = AnimatedStatCard("الإصلاحات النشطة", "0", "🔧", "#f59e0b")
        self.inventory_card = AnimatedStatCard("قيمة المخزون", "0 جنيه", "📦", "#8b5cf6")
        
        # Add click handlers
        self.sales_card.clicked.connect(lambda: self.navigate_to_page("sales"))
        self.orders_card.clicked.connect(lambda: self.navigate_to_page("sales"))
        self.repairs_card.clicked.connect(lambda: self.navigate_to_page("repairs"))
        self.inventory_card.clicked.connect(lambda: self.navigate_to_page("inventory"))
        
        stats_layout.addWidget(self.sales_card, 0, 0)
        stats_layout.addWidget(self.orders_card, 0, 1)
        stats_layout.addWidget(self.repairs_card, 0, 2)
        stats_layout.addWidget(self.inventory_card, 0, 3)
        
        parent_layout.addWidget(stats_frame)
        
    def setup_quick_actions(self, parent_layout):
        """Setup quick actions section"""
        actions_frame = QFrame()
        actions_frame.setStyleSheet(ModernStyles.get_card_style())
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        
        # Header
        header = QLabel("⚡ الإجراءات السريعة")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        actions_layout.addWidget(header)
        
        # Action buttons
        buttons_layout = QGridLayout()
        buttons_layout.setSpacing(15)
        
        # Create action buttons
        new_sale_btn = QuickActionButton("فاتورة جديدة", "إنشاء فاتورة مبيعات جديدة", "🛒", "#10b981")
        add_product_btn = QuickActionButton("إضافة منتج", "إضافة منتج جديد للمخزون", "📱", "#3b82f6")
        new_repair_btn = QuickActionButton("إصلاح جديد", "تسجيل طلب إصلاح جديد", "🔧", "#f59e0b")
        reports_btn = QuickActionButton("التقارير", "عرض التقارير والإحصائيات", "📊", "#8b5cf6")
        
        # Connect buttons
        new_sale_btn.clicked.connect(lambda: self.navigate_to_page("sales"))
        add_product_btn.clicked.connect(lambda: self.navigate_to_page("inventory"))
        new_repair_btn.clicked.connect(lambda: self.navigate_to_page("repairs"))
        reports_btn.clicked.connect(lambda: self.navigate_to_page("reports"))
        
        buttons_layout.addWidget(new_sale_btn, 0, 0)
        buttons_layout.addWidget(add_product_btn, 0, 1)
        buttons_layout.addWidget(new_repair_btn, 0, 2)
        buttons_layout.addWidget(reports_btn, 0, 3)
        
        actions_layout.addLayout(buttons_layout)
        parent_layout.addWidget(actions_frame)
        
    def setup_low_stock_alerts(self, parent_layout):
        """Setup low stock alerts"""
        alerts_frame = QFrame()
        alerts_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(alerts_frame)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("⚠️ تنبيهات المخزون المنخفض")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Alerts table
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(3)
        self.low_stock_table.setHorizontalHeaderLabels(["المنتج", "الكمية", "الحد الأدنى"])
        self.low_stock_table.horizontalHeader().setStretchLastSection(True)
        self.low_stock_table.setMaximumHeight(200)
        self.low_stock_table.setStyleSheet(ModernStyles.get_table_style())
        
        layout.addWidget(self.low_stock_table)
        parent_layout.addWidget(alerts_frame)
        
    def setup_pending_repairs(self, parent_layout):
        """Setup pending repairs section"""
        repairs_frame = QFrame()
        repairs_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(repairs_frame)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        header = QLabel("🔧 الإصلاحات المعلقة")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151;")
        
        view_all_btn = QPushButton("عرض الكل")
        view_all_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        view_all_btn.clicked.connect(lambda: self.navigate_to_page("repairs"))
        
        header_layout.addWidget(header)
        header_layout.addStretch()
        header_layout.addWidget(view_all_btn)
        
        layout.addLayout(header_layout)
        
        # Repairs list
        self.repairs_layout = QVBoxLayout()
        layout.addLayout(self.repairs_layout)
        
        parent_layout.addWidget(repairs_frame)
        
    def setup_recent_activity(self, parent_layout):
        """Setup recent activity section"""
        self.activity_widget = RecentActivityWidget(self.db_manager)
        parent_layout.addWidget(self.activity_widget)
        
    def setup_daily_summary(self, parent_layout):
        """Setup daily summary section"""
        summary_frame = QFrame()
        summary_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(summary_frame)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📈 ملخص اليوم")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Summary items
        self.summary_layout = QVBoxLayout()
        layout.addLayout(self.summary_layout)
        
        parent_layout.addWidget(summary_frame)
        
    def setup_auto_refresh(self):
        """Setup automatic data refresh"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # Refresh every 30 seconds
        
        # Initial data load
        self.refresh_data()
        
        # DateTime update timer
        self.datetime_timer = QTimer()
        self.datetime_timer.timeout.connect(self.update_datetime)
        self.datetime_timer.start(1000)  # Update every second
        
    def update_datetime(self):
        """Update date and time display"""
        now = datetime.now()
        date_str = now.strftime("%A, %d %B %Y")
        time_str = now.strftime("%I:%M:%S %p")
        self.datetime_label.setText(f"🕐 {time_str}\n📅 {date_str}")
        
    def refresh_data(self):
        """Refresh all dashboard data"""
        try:
            self.refresh_statistics()
            self.refresh_low_stock_alerts()
            self.refresh_pending_repairs()
            self.activity_widget.refresh_activities()
            self.refresh_daily_summary()
        except Exception as e:
            print(f"Error refreshing dashboard data: {e}")
            
    def refresh_statistics(self):
        """Refresh statistics cards"""
        try:
            # Get statistics from database
            stats = self.db_manager.get_statistics()
            
            # Update cards
            self.sales_card.update_value(f"{stats.get('sales_total_today', 0):.2f} جنيه")
            self.orders_card.update_value(str(stats.get('total_sales_today', 0)))
            self.repairs_card.update_value(str(stats.get('pending_repairs', 0) + stats.get('in_progress_repairs', 0)))
            self.inventory_card.update_value(f"{stats.get('inventory_value', 0):.2f} جنيه")
            
        except Exception as e:
            print(f"Error refreshing statistics: {e}")
            
    def refresh_low_stock_alerts(self):
        """Refresh low stock alerts"""
        try:
            low_stock = self.db_manager.execute_query("""
                SELECT name, current_qty, min_stock 
                FROM products 
                WHERE current_qty <= min_stock AND is_active = 1
                ORDER BY (current_qty - min_stock) ASC
                LIMIT 10
            """)
            
            self.low_stock_table.setRowCount(len(low_stock))
            
            for row, product in enumerate(low_stock):
                self.low_stock_table.setItem(row, 0, QTableWidgetItem(product['name']))
                self.low_stock_table.setItem(row, 1, QTableWidgetItem(str(product['current_qty'])))
                self.low_stock_table.setItem(row, 2, QTableWidgetItem(str(product['min_stock'])))
                
                # Color code based on severity
                if product['current_qty'] == 0:
                    for col in range(3):
                        item = self.low_stock_table.item(row, col)
                        if item:
                            item.setBackground(QColor(254, 202, 202))  # Red background
                elif product['current_qty'] <= product['min_stock'] / 2:
                    for col in range(3):
                        item = self.low_stock_table.item(row, col)
                        if item:
                            item.setBackground(QColor(253, 230, 138))  # Yellow background
                            
        except Exception as e:
            print(f"Error refreshing low stock alerts: {e}")
            
    def refresh_pending_repairs(self):
        """Refresh pending repairs"""
        try:
            # Clear existing repairs
            for i in reversed(range(self.repairs_layout.count())):
                self.repairs_layout.itemAt(i).widget().setParent(None)
            
            pending_repairs = self.db_manager.execute_query("""
                SELECT * FROM repairs 
                WHERE status IN ('في الانتظار', 'قيد الإصلاح')
                ORDER BY created_at DESC
                LIMIT 5
            """)
            
            for repair in pending_repairs:
                repair_frame = QFrame()
                repair_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f9fafb;
                        border: none;
                        border-radius: 8px;
                        padding: 12px;
                        border-left: 3px solid #f59e0b;
                    }
                """)
                
                repair_layout = QVBoxLayout(repair_frame)
                repair_layout.setSpacing(4)
                
                # Title
                title = QLabel(f"{repair['device_type']} {repair['device_model']} - {repair['customer_name']}")
                title.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                title.setStyleSheet("color: #374151;")
                
                # Details
                details = QLabel(f"الحالة: {repair['status']} | التكلفة: {repair['estimated_cost']:.2f} جنيه")
                details.setFont(QFont("Tahoma", 9))
                details.setStyleSheet("color: #6b7280;")
                
                repair_layout.addWidget(title)
                repair_layout.addWidget(details)
                
                self.repairs_layout.addWidget(repair_frame)
                
        except Exception as e:
            print(f"Error refreshing pending repairs: {e}")
            
    def refresh_daily_summary(self):
        """Refresh daily summary"""
        try:
            # Clear existing summary
            for i in reversed(range(self.summary_layout.count())):
                self.summary_layout.itemAt(i).widget().setParent(None)
            
            # Get daily statistics
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Daily sales summary
            sales_summary = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as sales_count,
                    COALESCE(SUM(total), 0) as sales_total,
                    COALESCE(AVG(total), 0) as avg_sale
                FROM sales 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            if sales_summary:
                summary = sales_summary[0]
                self.add_summary_item("💰", "المبيعات", f"{summary['sales_count']} فاتورة - {summary['sales_total']:.2f} جنيه")
                self.add_summary_item("📊", "متوسط الفاتورة", f"{summary['avg_sale']:.2f} جنيه")
            
            # Wallet transactions
            wallet_summary = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as trans_count,
                    COALESCE(SUM(ABS(amount)), 0) as trans_total
                FROM wallet_transactions 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            if wallet_summary:
                summary = wallet_summary[0]
                self.add_summary_item("💳", "معاملات المحفظة", f"{summary['trans_count']} معاملة - {summary['trans_total']:.2f} جنيه")
                
        except Exception as e:
            print(f"Error refreshing daily summary: {e}")
            
    def add_summary_item(self, icon, title, description):
        """Add summary item"""
        item_frame = QFrame()
        item_frame.setStyleSheet("""
            QFrame {
                background-color: #f3f4f6;
                border: none;
                border-radius: 6px;
                padding: 8px;
            }
        """)
        
        item_layout = QHBoxLayout(item_frame)
        item_layout.setContentsMargins(8, 6, 8, 6)
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        icon_label.setFixedSize(24, 24)
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        content_layout = QVBoxLayout()
        content_layout.setSpacing(2)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Tahoma", 9, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #374151;")
        
        desc_label = QLabel(description)
        desc_label.setFont(QFont("Tahoma", 8))
        desc_label.setStyleSheet("color: #6b7280;")
        
        content_layout.addWidget(title_label)
        content_layout.addWidget(desc_label)
        
        item_layout.addWidget(icon_label)
        item_layout.addLayout(content_layout, 1)
        
        self.summary_layout.addWidget(item_frame)
        
    def navigate_to_page(self, page_name):
        """Navigate to a specific page"""
        # This would be connected to the main window's navigation
        # For now, we'll just print the navigation request
        print(f"Navigate to: {page_name}")
        
        # In a real implementation, this would emit a signal or call parent method
        parent = self.parent()
        while parent and not hasattr(parent, 'navigate_to'):
            parent = parent.parent()
        if parent and hasattr(parent, 'navigate_to'):
            parent.navigate_to(page_name)
