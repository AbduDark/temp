"""
Enhanced Reports Page for Mobile Shop Management System
Comprehensive reporting and analytics with beautiful charts and visualizations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QHeaderView, QScrollArea, QProgressBar,
    QMessageBox, QDialog, QFormLayout, QGraphicsDropShadowEffect,
    QCheckBox, QGroupBox, QDateEdit, QTabWidget, QSplitter, QCalendarWidget
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon
from datetime import datetime, timedelta
import calendar

from ui.styles import ModernStyles
from ui.widgets import StatCard, ChartWidget

class ReportStatCard(QFrame):
    """Enhanced statistics card for reports"""
    
    def __init__(self, title, value, icon, color="#3b82f6", subtitle="", trend=None):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.subtitle = subtitle
        self.trend = trend
        self.setup_ui()
        
    def setup_ui(self):
        """Setup card UI"""
        self.setFixedHeight(120)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 15px;
                padding: 20px;
                border-left: 4px solid {self.color};
            }}
            QFrame:hover {{
                border: 1px solid {self.color};
                box-shadow: 0 4px 12px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(10)
        shadow.setColor(QColor(0, 0, 0, 8))
        shadow.setOffset(0, 2)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setStyleSheet(f"color: {self.color};")
        
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        title_label.setStyleSheet("color: #6b7280;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Tahoma", 18, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color};")
        
        # Subtitle and trend
        bottom_layout = QHBoxLayout()
        
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setFont(QFont("Tahoma", 8))
            subtitle_label.setStyleSheet("color: #9ca3af;")
            bottom_layout.addWidget(subtitle_label)
        
        if self.trend:
            trend_label = QLabel(self.trend)
            trend_label.setFont(QFont("Tahoma", 8, QFont.Weight.Bold))
            if "+" in self.trend:
                trend_label.setStyleSheet("color: #10b981;")
            elif "-" in self.trend:
                trend_label.setStyleSheet("color: #ef4444;")
            else:
                trend_label.setStyleSheet("color: #6b7280;")
            bottom_layout.addWidget(trend_label)
        
        bottom_layout.addStretch()
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addLayout(bottom_layout)
        
    def update_value(self, new_value, subtitle="", trend=None):
        """Update card value"""
        self.value = new_value
        self.value_label.setText(str(new_value))

class SalesReportWidget(QFrame):
    """Sales report widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup sales report UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("💰 تقرير المبيعات")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Top products table
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            "المنتج", "الكمية المباعة", "إجمالي المبيعات", "الربح"
        ])
        self.top_products_table.horizontalHeader().setStretchLastSection(True)
        self.top_products_table.setMaximumHeight(300)
        self.top_products_table.setStyleSheet(ModernStyles.get_table_style())
        
        layout.addWidget(self.top_products_table)
        
    def refresh_data(self, date_from, date_to):
        """Refresh sales report data"""
        try:
            # Get top selling products
            top_products = self.db_manager.execute_query("""
                SELECT 
                    si.product_name,
                    SUM(si.qty) as total_qty,
                    SUM(si.total) as total_sales,
                    SUM(si.profit) as total_profit
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
                GROUP BY si.product_id, si.product_name
                ORDER BY total_sales DESC
                LIMIT 10
            """, (date_from, date_to))
            
            self.top_products_table.setRowCount(len(top_products))
            
            for row, product in enumerate(top_products):
                self.top_products_table.setItem(row, 0, QTableWidgetItem(product['product_name']))
                self.top_products_table.setItem(row, 1, QTableWidgetItem(str(product['total_qty'])))
                self.top_products_table.setItem(row, 2, QTableWidgetItem(f"{product['total_sales']:.2f} جنيه"))
                self.top_products_table.setItem(row, 3, QTableWidgetItem(f"{product['total_profit']:.2f} جنيه"))
                
        except Exception as e:
            print(f"Error refreshing sales report: {e}")

class InventoryReportWidget(QFrame):
    """Inventory report widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup inventory report UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📦 تقرير المخزون")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Stock status table
        self.stock_table = QTableWidget()
        self.stock_table.setColumnCount(5)
        self.stock_table.setHorizontalHeaderLabels([
            "المنتج", "الكمية الحالية", "الحد الأدنى", "القيمة", "الحالة"
        ])
        self.stock_table.horizontalHeader().setStretchLastSection(True)
        self.stock_table.setMaximumHeight(300)
        self.stock_table.setStyleSheet(ModernStyles.get_table_style())
        
        layout.addWidget(self.stock_table)
        
    def refresh_data(self):
        """Refresh inventory report data"""
        try:
            # Get inventory status
            inventory = self.db_manager.execute_query("""
                SELECT 
                    name,
                    current_qty,
                    min_stock,
                    (current_qty * buy_price) as value,
                    CASE 
                        WHEN current_qty = 0 THEN 'نفاد المخزون'
                        WHEN current_qty <= min_stock THEN 'مخزون منخفض'
                        ELSE 'متوفر'
                    END as status
                FROM products 
                WHERE is_active = 1
                ORDER BY 
                    CASE 
                        WHEN current_qty = 0 THEN 1
                        WHEN current_qty <= min_stock THEN 2
                        ELSE 3
                    END, name
                LIMIT 20
            """)
            
            self.stock_table.setRowCount(len(inventory))
            
            for row, item in enumerate(inventory):
                self.stock_table.setItem(row, 0, QTableWidgetItem(item['name']))
                self.stock_table.setItem(row, 1, QTableWidgetItem(str(item['current_qty'])))
                self.stock_table.setItem(row, 2, QTableWidgetItem(str(item['min_stock'])))
                self.stock_table.setItem(row, 3, QTableWidgetItem(f"{item['value']:.2f} جنيه"))
                
                # Status with color coding
                status_item = QTableWidgetItem(item['status'])
                if item['status'] == 'نفاد المخزون':
                    status_item.setBackground(QColor(254, 226, 226))
                    status_item.setForeground(QColor(153, 27, 27))
                elif item['status'] == 'مخزون منخفض':
                    status_item.setBackground(QColor(254, 249, 195))
                    status_item.setForeground(QColor(146, 64, 14))
                else:
                    status_item.setBackground(QColor(220, 252, 231))
                    status_item.setForeground(QColor(5, 150, 105))
                
                self.stock_table.setItem(row, 4, status_item)
                
        except Exception as e:
            print(f"Error refreshing inventory report: {e}")

class FinancialReportWidget(QFrame):
    """Financial report widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup financial report UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📊 التقرير المالي")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Financial summary
        self.summary_layout = QVBoxLayout()
        layout.addLayout(self.summary_layout)
        
    def refresh_data(self, date_from, date_to):
        """Refresh financial report data"""
        try:
            # Clear existing summary
            for i in reversed(range(self.summary_layout.count())):
                self.summary_layout.itemAt(i).widget().setParent(None)
            
            # Get financial summary
            financial_data = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_sales,
                    COALESCE(SUM(subtotal), 0) as total_revenue,
                    COALESCE(SUM(discount), 0) as total_discounts,
                    COALESCE(SUM(total), 0) as net_revenue,
                    COALESCE(AVG(total), 0) as avg_sale
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (date_from, date_to))
            
            if financial_data:
                data = financial_data[0]
                
                # Create summary items
                summary_items = [
                    ("إجمالي الفواتير", str(data['total_sales']), "🧾"),
                    ("إجمالي الإيرادات", f"{data['total_revenue']:.2f} جنيه", "💰"),
                    ("إجمالي الخصومات", f"{data['total_discounts']:.2f} جنيه", "🏷️"),
                    ("صافي الإيرادات", f"{data['net_revenue']:.2f} جنيه", "💎"),
                    ("متوسط الفاتورة", f"{data['avg_sale']:.2f} جنيه", "📊")
                ]
                
                for title, value, icon in summary_items:
                    item_frame = QFrame()
                    item_frame.setStyleSheet("""
                        QFrame {
                            background-color: #f9fafb;
                            border: 1px solid #e5e7eb;
                            border-radius: 8px;
                            padding: 12px;
                            margin: 2px;
                        }
                    """)
                    
                    item_layout = QHBoxLayout(item_frame)
                    
                    icon_label = QLabel(icon)
                    icon_label.setFont(QFont("Segoe UI Emoji", 16))
                    icon_label.setFixedSize(30, 30)
                    icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
                    
                    text_layout = QVBoxLayout()
                    text_layout.setSpacing(2)
                    
                    title_label = QLabel(title)
                    title_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                    title_label.setStyleSheet("color: #374151;")
                    
                    value_label = QLabel(value)
                    value_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
                    value_label.setStyleSheet("color: #059669;")
                    
                    text_layout.addWidget(title_label)
                    text_layout.addWidget(value_label)
                    
                    item_layout.addWidget(icon_label)
                    item_layout.addLayout(text_layout, 1)
                    
                    self.summary_layout.addWidget(item_frame)
                    
            # Get profit analysis
            profit_data = self.db_manager.execute_query("""
                SELECT 
                    COALESCE(SUM(si.profit), 0) as total_profit,
                    COALESCE(SUM(si.total - si.profit), 0) as total_cost
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
            """, (date_from, date_to))
            
            if profit_data:
                profit = profit_data[0]
                
                profit_frame = QFrame()
                profit_frame.setStyleSheet("""
                    QFrame {
                        background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                            stop:0 #10b981, stop:1 #059669);
                        border-radius: 12px;
                        padding: 15px;
                        margin-top: 10px;
                    }
                """)
                
                profit_layout = QHBoxLayout(profit_frame)
                
                profit_info = QVBoxLayout()
                
                profit_title = QLabel("💎 تحليل الأرباح")
                profit_title.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
                profit_title.setStyleSheet("color: white;")
                
                profit_value = QLabel(f"إجمالي الأرباح: {profit['total_profit']:.2f} جنيه")
                profit_value.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
                profit_value.setStyleSheet("color: white;")
                
                cost_value = QLabel(f"إجمالي التكلفة: {profit['total_cost']:.2f} جنيه")
                cost_value.setFont(QFont("Tahoma", 10))
                cost_value.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
                
                profit_info.addWidget(profit_title)
                profit_info.addWidget(profit_value)
                profit_info.addWidget(cost_value)
                
                profit_layout.addLayout(profit_info)
                
                self.summary_layout.addWidget(profit_frame)
                
        except Exception as e:
            print(f"Error refreshing financial report: {e}")

class ReportsPage(QWidget):
    """Enhanced reports page with comprehensive analytics"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup reports page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.setup_header(main_layout)
        
        # Date range and filters section
        self.setup_filters(main_layout)
        
        # Overview statistics
        self.setup_overview_stats(main_layout)
        
        # Reports tabs
        self.setup_reports_tabs(main_layout)
        
    def setup_header(self, parent_layout):
        """Setup header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #8b5cf6, stop:1 #7c3aed);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("📊 التقارير والإحصائيات الشاملة")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("تحليلات متقدمة ورؤى شاملة لأداء المحل")
        subtitle.setFont(QFont("Tahoma", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Export buttons
        buttons_layout = QHBoxLayout()
        
        export_pdf_btn = QPushButton("📄 تصدير PDF")
        export_pdf_btn.setFixedHeight(45)
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_pdf)
        
        export_excel_btn = QPushButton("📊 تصدير Excel")
        export_excel_btn.setFixedHeight(45)
        export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        export_excel_btn.clicked.connect(self.export_excel)
        
        print_btn = QPushButton("🖨️ طباعة")
        print_btn.setFixedHeight(45)
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        print_btn.clicked.connect(self.print_report)
        
        buttons_layout.addWidget(export_pdf_btn)
        buttons_layout.addWidget(export_excel_btn)
        buttons_layout.addWidget(print_btn)
        buttons_layout.addStretch()
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(header_frame)
        
    def setup_filters(self, parent_layout):
        """Setup filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(ModernStyles.get_card_style())
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(20)
        
        # Quick date selections
        quick_dates_label = QLabel("📅 فترة سريعة:")
        quick_dates_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.quick_dates = QComboBox()
        self.quick_dates.addItems([
            "اليوم", "أمس", "آخر 7 أيام", "آخر 30 يوم", 
            "هذا الشهر", "الشهر الماضي", "آخر 3 شهور", "هذا العام", "مخصص"
        ])
        self.quick_dates.setStyleSheet(ModernStyles.get_input_style())
        self.quick_dates.currentTextChanged.connect(self.on_quick_date_changed)
        
        # Custom date range
        from_label = QLabel("من:")
        from_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(ModernStyles.get_input_style())
        self.date_from.dateChanged.connect(self.refresh_data)
        
        to_label = QLabel("إلى:")
        to_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(ModernStyles.get_input_style())
        self.date_to.dateChanged.connect(self.refresh_data)
        
        # Report type filter
        type_label = QLabel("📋 نوع التقرير:")
        type_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.report_type = QComboBox()
        self.report_type.addItems([
            "جميع التقارير", "المبيعات", "المخزون", "الإصلاحات", "المحفظة", "المالي"
        ])
        self.report_type.setStyleSheet(ModernStyles.get_input_style())
        self.report_type.currentTextChanged.connect(self.on_report_type_changed)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(ModernStyles.get_button_primary_style())
        refresh_btn.clicked.connect(self.refresh_data)
        
        filters_layout.addWidget(quick_dates_label)
        filters_layout.addWidget(self.quick_dates, 1)
        filters_layout.addWidget(from_label)
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(to_label)
        filters_layout.addWidget(self.date_to)
        filters_layout.addWidget(type_label)
        filters_layout.addWidget(self.report_type, 1)
        filters_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(filters_frame)
        
    def setup_overview_stats(self, parent_layout):
        """Setup overview statistics"""
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # Create stat cards
        self.revenue_card = ReportStatCard("إجمالي الإيرادات", "0 جنيه", "💰", "#10b981")
        self.sales_card = ReportStatCard("عدد المبيعات", "0", "🛒", "#3b82f6")
        self.profit_card = ReportStatCard("صافي الأرباح", "0 جنيه", "📈", "#8b5cf6")
        self.customers_card = ReportStatCard("العملاء الجدد", "0", "👥", "#f59e0b")
        
        stats_layout.addWidget(self.revenue_card, 0, 0)
        stats_layout.addWidget(self.sales_card, 0, 1)
        stats_layout.addWidget(self.profit_card, 0, 2)
        stats_layout.addWidget(self.customers_card, 0, 3)
        
        parent_layout.addWidget(stats_frame)
        
    def setup_reports_tabs(self, parent_layout):
        """Setup reports tabs"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet(ModernStyles.get_tab_widget_style())
        
        # Sales report tab
        self.sales_report = SalesReportWidget(self.db_manager)
        self.tabs.addTab(self.sales_report, "💰 تقرير المبيعات")
        
        # Inventory report tab
        self.inventory_report = InventoryReportWidget(self.db_manager)
        self.tabs.addTab(self.inventory_report, "📦 تقرير المخزون")
        
        # Financial report tab
        self.financial_report = FinancialReportWidget(self.db_manager)
        self.tabs.addTab(self.financial_report, "📊 التقرير المالي")
        
        # Repairs report tab
        self.setup_repairs_report_tab()
        
        # Wallet report tab
        self.setup_wallet_report_tab()
        
        parent_layout.addWidget(self.tabs, 1)
        
    def setup_repairs_report_tab(self):
        """Setup repairs report tab"""
        repairs_widget = QWidget()
        layout = QVBoxLayout(repairs_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("🔧 تقرير الإصلاحات")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Repairs status table
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(4)
        self.repairs_table.setHorizontalHeaderLabels([
            "الحالة", "العدد", "متوسط التكلفة", "إجمالي الإيرادات"
        ])
        self.repairs_table.horizontalHeader().setStretchLastSection(True)
        self.repairs_table.setStyleSheet(ModernStyles.get_table_style())
        
        layout.addWidget(self.repairs_table)
        
        self.tabs.addTab(repairs_widget, "🔧 تقرير الإصلاحات")
        
    def setup_wallet_report_tab(self):
        """Setup wallet report tab"""
        wallet_widget = QWidget()
        layout = QVBoxLayout(wallet_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("💳 تقرير المحفظة")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Wallet summary table
        self.wallet_table = QTableWidget()
        self.wallet_table.setColumnCount(5)
        self.wallet_table.setHorizontalHeaderLabels([
            "المزود", "عدد المعاملات", "إجمالي الحجم", "الرصيد الحالي", "الرسوم"
        ])
        self.wallet_table.horizontalHeader().setStretchLastSection(True)
        self.wallet_table.setStyleSheet(ModernStyles.get_table_style())
        
        layout.addWidget(self.wallet_table)
        
        self.tabs.addTab(wallet_widget, "💳 تقرير المحفظة")
        
    def on_quick_date_changed(self, text):
        """Handle quick date selection change"""
        today = QDate.currentDate()
        
        if text == "اليوم":
            self.date_from.setDate(today)
            self.date_to.setDate(today)
        elif text == "أمس":
            yesterday = today.addDays(-1)
            self.date_from.setDate(yesterday)
            self.date_to.setDate(yesterday)
        elif text == "آخر 7 أيام":
            self.date_from.setDate(today.addDays(-7))
            self.date_to.setDate(today)
        elif text == "آخر 30 يوم":
            self.date_from.setDate(today.addDays(-30))
            self.date_to.setDate(today)
        elif text == "هذا الشهر":
            first_day = QDate(today.year(), today.month(), 1)
            self.date_from.setDate(first_day)
            self.date_to.setDate(today)
        elif text == "الشهر الماضي":
            last_month = today.addMonths(-1)
            first_day = QDate(last_month.year(), last_month.month(), 1)
            last_day = first_day.addMonths(1).addDays(-1)
            self.date_from.setDate(first_day)
            self.date_to.setDate(last_day)
        elif text == "آخر 3 شهور":
            self.date_from.setDate(today.addMonths(-3))
            self.date_to.setDate(today)
        elif text == "هذا العام":
            first_day = QDate(today.year(), 1, 1)
            self.date_from.setDate(first_day)
            self.date_to.setDate(today)
        
        if text != "مخصص":
            self.refresh_data()
            
    def on_report_type_changed(self, text):
        """Handle report type change"""
        type_to_tab = {
            "المبيعات": 0,
            "المخزون": 1,
            "المالي": 2,
            "الإصلاحات": 3,
            "المحفظة": 4
        }
        
        if text in type_to_tab:
            self.tabs.setCurrentIndex(type_to_tab[text])
            
    def refresh_data(self):
        """Refresh all report data"""
        try:
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            
            # Refresh overview statistics
            self.refresh_overview_stats(date_from, date_to)
            
            # Refresh individual reports
            self.sales_report.refresh_data(date_from, date_to)
            self.inventory_report.refresh_data()
            self.financial_report.refresh_data(date_from, date_to)
            self.refresh_repairs_report(date_from, date_to)
            self.refresh_wallet_report(date_from, date_to)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث التقارير: {str(e)}")
            
    def refresh_overview_stats(self, date_from, date_to):
        """Refresh overview statistics"""
        try:
            # Sales statistics
            sales_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as total_sales,
                    COALESCE(SUM(total), 0) as total_revenue,
                    COALESCE(SUM(si.profit), 0) as total_profit
                FROM sales s
                LEFT JOIN sale_items si ON s.id = si.sale_id
                WHERE DATE(s.created_at) BETWEEN ? AND ?
            """, (date_from, date_to))
            
            if sales_stats:
                stats = sales_stats[0]
                self.revenue_card.update_value(f"{stats['total_revenue']:.2f} جنيه")
                self.sales_card.update_value(str(stats['total_sales']))
                self.profit_card.update_value(f"{stats['total_profit']:.2f} جنيه")
            
            # Customer statistics
            customers_stats = self.db_manager.execute_query("""
                SELECT COUNT(DISTINCT customer_id) as new_customers
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ?
                AND customer_id IS NOT NULL
            """, (date_from, date_to))
            
            if customers_stats:
                self.customers_card.update_value(str(customers_stats[0]['new_customers']))
                
        except Exception as e:
            print(f"Error refreshing overview stats: {e}")
            
    def refresh_repairs_report(self, date_from, date_to):
        """Refresh repairs report"""
        try:
            repairs_stats = self.db_manager.execute_query("""
                SELECT 
                    status,
                    COUNT(*) as count,
                    COALESCE(AVG(estimated_cost), 0) as avg_cost,
                    COALESCE(SUM(estimated_cost), 0) as total_revenue
                FROM repairs 
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY status
                ORDER BY count DESC
            """, (date_from, date_to))
            
            self.repairs_table.setRowCount(len(repairs_stats))
            
            for row, repair in enumerate(repairs_stats):
                self.repairs_table.setItem(row, 0, QTableWidgetItem(repair['status']))
                self.repairs_table.setItem(row, 1, QTableWidgetItem(str(repair['count'])))
                self.repairs_table.setItem(row, 2, QTableWidgetItem(f"{repair['avg_cost']:.2f} جنيه"))
                self.repairs_table.setItem(row, 3, QTableWidgetItem(f"{repair['total_revenue']:.2f} جنيه"))
                
        except Exception as e:
            print(f"Error refreshing repairs report: {e}")
            
    def refresh_wallet_report(self, date_from, date_to):
        """Refresh wallet report"""
        try:
            wallet_stats = self.db_manager.execute_query("""
                SELECT 
                    provider,
                    COUNT(*) as transaction_count,
                    COALESCE(SUM(ABS(amount)), 0) as total_volume,
                    COALESCE(SUM(fees), 0) as total_fees
                FROM wallet_transactions 
                WHERE DATE(created_at) BETWEEN ? AND ?
                GROUP BY provider
                ORDER BY total_volume DESC
            """, (date_from, date_to))
            
            # Get current balances
            current_balances = {}
            for provider in ['vodafone', 'orange', 'etisalat']:
                balance_result = self.db_manager.execute_query("""
                    SELECT COALESCE(SUM(amount), 0) as balance 
                    FROM wallet_transactions 
                    WHERE provider = ?
                """, (provider,))
                current_balances[provider] = balance_result[0]['balance'] if balance_result else 0.0
            
            self.wallet_table.setRowCount(len(wallet_stats))
            
            provider_names = {
                'vodafone': 'فودافون كاش',
                'orange': 'أورانج كاش',
                'etisalat': 'اتصالات كاش'
            }
            
            for row, wallet in enumerate(wallet_stats):
                provider_name = provider_names.get(wallet['provider'], wallet['provider'])
                current_balance = current_balances.get(wallet['provider'], 0.0)
                
                self.wallet_table.setItem(row, 0, QTableWidgetItem(provider_name))
                self.wallet_table.setItem(row, 1, QTableWidgetItem(str(wallet['transaction_count'])))
                self.wallet_table.setItem(row, 2, QTableWidgetItem(f"{wallet['total_volume']:.2f} جنيه"))
                self.wallet_table.setItem(row, 3, QTableWidgetItem(f"{current_balance:.2f} جنيه"))
                self.wallet_table.setItem(row, 4, QTableWidgetItem(f"{wallet['total_fees']:.2f} جنيه"))
                
        except Exception as e:
            print(f"Error refreshing wallet report: {e}")
            
    def export_pdf(self):
        """Export report to PDF"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة تصدير PDF قريباً")
        
    def export_excel(self):
        """Export report to Excel"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة تصدير Excel قريباً")
        
    def print_report(self):
        """Print report"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة الطباعة قريباً")
