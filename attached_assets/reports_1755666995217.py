
"""
Reports Page for Mobile Shop Management System
صفحة التقارير الشاملة لنظام إدارة محل الموبايل
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QComboBox, QDateEdit,
    QGroupBox, QScrollArea, QHeaderView, QTabWidget, QProgressBar,
    QLineEdit, QSpinBox, QTextEdit, QMessageBox
)
from PyQt6.QtCore import Qt, QDate, QTimer, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QPainter, QColor
from datetime import datetime, timedelta
import calendar

class StatCard(QFrame):
    """بطاقة إحصائيات محسنة"""
    def __init__(self, title, value, icon, color="#3b82f6", change=None):
        super().__init__()
        self.setup_ui(title, value, icon, color, change)
        
    def setup_ui(self, title, value, icon, color, change):
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Tahoma", 12))
        title_label.setStyleSheet("color: #6b7280;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Value
        value_label = QLabel(str(value))
        value_label.setFont(QFont("Tahoma", 24, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        layout.addWidget(value_label)
        
        # Change indicator
        if change is not None:
            change_label = QLabel(f"{change:+.1f}%" if isinstance(change, (int, float)) else str(change))
            change_color = "#10b981" if (isinstance(change, (int, float)) and change >= 0) else "#ef4444"
            change_label.setStyleSheet(f"color: {change_color}; font-size: 12px;")
            layout.addWidget(change_label)

class ReportsPage(QWidget):
    """صفحة التقارير الشاملة"""
    
    # إشارات للتنقل
    navigate_to_sales = pyqtSignal()
    navigate_to_inventory = pyqtSignal()
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_period = "today"
        self.stats_data = {}
        self.setup_ui()
        self.setup_auto_refresh()
        self.refresh_data()

    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        # منطقة التمرير الرئيسية
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(25)
        
        # العنوان الرئيسي
        self.setup_header(main_layout)
        
        # فلاتر التقارير
        self.setup_filters(main_layout)
        
        # الإحصائيات الرئيسية
        self.setup_main_stats(main_layout)
        
        # التبويبات
        self.setup_tabs(main_layout)
        
        scroll.setWidget(main_widget)
        
        # التخطيط الرئيسي
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.addWidget(scroll)

    def setup_header(self, parent_layout):
        """إعداد العنوان الرئيسي"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 30px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # العنوان
        title = QLabel("📊 التقارير والإحصائيات الشاملة")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        # التاريخ والوقت
        datetime_label = QLabel(datetime.now().strftime("%A, %d %B %Y - %I:%M %p"))
        datetime_label.setFont(QFont("Tahoma", 12))
        datetime_label.setStyleSheet("color: #e0e7ff;")
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(datetime_label)
        
        parent_layout.addWidget(header_frame)

    def setup_filters(self, parent_layout):
        """إعداد فلاتر التقارير"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        
        filters_layout = QHBoxLayout(filters_frame)
        
        # فترة التقرير
        period_label = QLabel("📅 فترة التقرير:")
        period_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        
        self.period_combo = QComboBox()
        self.period_combo.addItems([
            "اليوم", "أمس", "آخر 7 أيام", "آخر 30 يوم", 
            "هذا الشهر", "الشهر الماضي", "آخر 3 شهور", "هذا العام"
        ])
        self.period_combo.currentTextChanged.connect(self.on_period_changed)
        
        # التاريخ المخصص
        custom_label = QLabel("📆 من:")
        self.from_date = QDateEdit()
        self.from_date.setDate(QDate.currentDate().addDays(-30))
        self.from_date.setCalendarPopup(True)
        
        to_label = QLabel("إلى:")
        self.to_date = QDateEdit()
        self.to_date.setDate(QDate.currentDate())
        self.to_date.setCalendarPopup(True)
        
        # زر التحديث
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 8px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        filters_layout.addWidget(period_label)
        filters_layout.addWidget(self.period_combo)
        filters_layout.addSpacing(20)
        filters_layout.addWidget(custom_label)
        filters_layout.addWidget(self.from_date)
        filters_layout.addWidget(to_label)
        filters_layout.addWidget(self.to_date)
        filters_layout.addStretch()
        filters_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(filters_frame)

    def setup_main_stats(self, parent_layout):
        """إعداد الإحصائيات الرئيسية"""
        stats_frame = QFrame()
        stats_layout = QGridLayout(stats_frame)
        stats_layout.setSpacing(20)
        
        # بطاقات الإحصائيات
        self.sales_card = StatCard("المبيعات", "0 جنيه", "💰", "#10b981")
        self.profit_card = StatCard("الأرباح", "0 جنيه", "📈", "#3b82f6")
        self.orders_card = StatCard("عدد الفواتير", "0", "🧾", "#8b5cf6")
        self.customers_card = StatCard("العملاء", "0", "👥", "#f59e0b")
        
        stats_layout.addWidget(self.sales_card, 0, 0)
        stats_layout.addWidget(self.profit_card, 0, 1)
        stats_layout.addWidget(self.orders_card, 0, 2)
        stats_layout.addWidget(self.customers_card, 0, 3)
        
        # إحصائيات إضافية
        self.products_card = StatCard("المنتجات", "0", "📱", "#ef4444")
        self.low_stock_card = StatCard("نقص المخزون", "0", "⚠️", "#f97316")
        self.repairs_card = StatCard("الإصلاحات", "0", "🔧", "#06b6d4")
        self.avg_sale_card = StatCard("متوسط الفاتورة", "0 جنيه", "💳", "#84cc16")
        
        stats_layout.addWidget(self.products_card, 1, 0)
        stats_layout.addWidget(self.low_stock_card, 1, 1)
        stats_layout.addWidget(self.repairs_card, 1, 2)
        stats_layout.addWidget(self.avg_sale_card, 1, 3)
        
        parent_layout.addWidget(stats_frame)

    def setup_tabs(self, parent_layout):
        """إعداد التبويبات"""
        self.tabs = QTabWidget()
        self.tabs.setStyleSheet("""
            QTabWidget::pane {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            }
            QTabBar::tab {
                background: #f8fafc;
                border: 1px solid #e5e7eb;
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
            }
            QTabBar::tab:selected {
                background: #3b82f6;
                color: white;
            }
        """)
        
        # تقارير المبيعات
        self.setup_sales_report_tab()
        
        # تقارير المخزون
        self.setup_inventory_report_tab()
        
        # تقارير العملاء
        self.setup_customers_report_tab()
        
        # التقارير المالية
        self.setup_financial_report_tab()
        
        parent_layout.addWidget(self.tabs)

    def setup_sales_report_tab(self):
        """تبويب تقارير المبيعات"""
        sales_widget = QWidget()
        layout = QVBoxLayout(sales_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # أفضل المنتجات مبيعاً
        top_products_group = QGroupBox("🏆 أفضل المنتجات مبيعاً")
        top_products_layout = QVBoxLayout(top_products_group)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(5)
        self.top_products_table.setHorizontalHeaderLabels([
            "المرتبة", "اسم المنتج", "الكمية المباعة", "إجمالي المبيعات", "النسبة المئوية"
        ])
        self.top_products_table.horizontalHeader().setStretchLastSection(True)
        top_products_layout.addWidget(self.top_products_table)
        
        layout.addWidget(top_products_group)
        
        # المبيعات اليومية
        daily_sales_group = QGroupBox("📅 المبيعات اليومية")
        daily_sales_layout = QVBoxLayout(daily_sales_group)
        
        self.daily_sales_table = QTableWidget()
        self.daily_sales_table.setColumnCount(4)
        self.daily_sales_table.setHorizontalHeaderLabels([
            "التاريخ", "عدد الفواتير", "إجمالي المبيعات", "متوسط الفاتورة"
        ])
        self.daily_sales_table.horizontalHeader().setStretchLastSection(True)
        daily_sales_layout.addWidget(self.daily_sales_table)
        
        layout.addWidget(daily_sales_group)
        
        self.tabs.addTab(sales_widget, "💰 تقارير المبيعات")

    def setup_inventory_report_tab(self):
        """تبويب تقارير المخزون"""
        inventory_widget = QWidget()
        layout = QVBoxLayout(inventory_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # حالة المخزون
        stock_status_group = QGroupBox("📊 حالة المخزون")
        stock_status_layout = QVBoxLayout(stock_status_group)
        
        self.stock_status_table = QTableWidget()
        self.stock_status_table.setColumnCount(6)
        self.stock_status_table.setHorizontalHeaderLabels([
            "اسم المنتج", "الكمية الحالية", "الحد الأدنى", "الحالة", "القيمة", "آخر تحديث"
        ])
        self.stock_status_table.horizontalHeader().setStretchLastSection(True)
        stock_status_layout.addWidget(self.stock_status_table)
        
        layout.addWidget(stock_status_group)
        
        # المنتجات الأكثر حركة
        fast_moving_group = QGroupBox("🚀 المنتجات الأكثر حركة")
        fast_moving_layout = QVBoxLayout(fast_moving_group)
        
        self.fast_moving_table = QTableWidget()
        self.fast_moving_table.setColumnCount(4)
        self.fast_moving_table.setHorizontalHeaderLabels([
            "اسم المنتج", "إجمالي المبيعات", "معدل الدوران", "التقييم"
        ])
        self.fast_moving_table.horizontalHeader().setStretchLastSection(True)
        fast_moving_layout.addWidget(self.fast_moving_table)
        
        layout.addWidget(fast_moving_group)
        
        self.tabs.addTab(inventory_widget, "📦 تقارير المخزون")

    def setup_customers_report_tab(self):
        """تبويب تقارير العملاء"""
        customers_widget = QWidget()
        layout = QVBoxLayout(customers_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # أفضل العملاء
        top_customers_group = QGroupBox("👑 أفضل العملاء")
        top_customers_layout = QVBoxLayout(top_customers_group)
        
        self.top_customers_table = QTableWidget()
        self.top_customers_table.setColumnCount(5)
        self.top_customers_table.setHorizontalHeaderLabels([
            "اسم العميل", "عدد المشتريات", "إجمالي المبلغ", "متوسط الشراء", "آخر شراء"
        ])
        self.top_customers_table.horizontalHeader().setStretchLastSection(True)
        top_customers_layout.addWidget(self.top_customers_table)
        
        layout.addWidget(top_customers_group)
        
        # إحصائيات العملاء
        customer_stats_group = QGroupBox("📈 إحصائيات العملاء")
        customer_stats_layout = QGridLayout(customer_stats_group)
        
        # بطاقات إحصائيات العملاء
        self.new_customers_card = StatCard("عملاء جدد", "0", "👤", "#10b981")
        self.returning_customers_card = StatCard("عملاء عائدون", "0", "🔄", "#3b82f6")
        self.avg_customer_value_card = StatCard("متوسط قيمة العميل", "0 جنيه", "💎", "#8b5cf6")
        
        customer_stats_layout.addWidget(self.new_customers_card, 0, 0)
        customer_stats_layout.addWidget(self.returning_customers_card, 0, 1)
        customer_stats_layout.addWidget(self.avg_customer_value_card, 0, 2)
        
        layout.addWidget(customer_stats_group)
        
        self.tabs.addTab(customers_widget, "👥 تقارير العملاء")

    def setup_financial_report_tab(self):
        """تبويب التقارير المالية"""
        financial_widget = QWidget()
        layout = QVBoxLayout(financial_widget)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # ملخص مالي
        financial_summary_group = QGroupBox("💰 الملخص المالي")
        financial_summary_layout = QGridLayout(financial_summary_group)
        
        self.revenue_card = StatCard("الإيرادات", "0 جنيه", "💵", "#10b981")
        self.costs_card = StatCard("التكاليف", "0 جنيه", "💸", "#ef4444")
        self.net_profit_card = StatCard("صافي الربح", "0 جنيه", "💰", "#3b82f6")
        self.profit_margin_card = StatCard("هامش الربح", "0%", "📊", "#8b5cf6")
        
        financial_summary_layout.addWidget(self.revenue_card, 0, 0)
        financial_summary_layout.addWidget(self.costs_card, 0, 1)
        financial_summary_layout.addWidget(self.net_profit_card, 1, 0)
        financial_summary_layout.addWidget(self.profit_margin_card, 1, 1)
        
        layout.addWidget(financial_summary_group)
        
        # طرق الدفع
        payment_methods_group = QGroupBox("💳 طرق الدفع")
        payment_methods_layout = QVBoxLayout(payment_methods_group)
        
        self.payment_methods_table = QTableWidget()
        self.payment_methods_table.setColumnCount(4)
        self.payment_methods_table.setHorizontalHeaderLabels([
            "طريقة الدفع", "عدد المعاملات", "المبلغ", "النسبة المئوية"
        ])
        self.payment_methods_table.horizontalHeader().setStretchLastSection(True)
        payment_methods_layout.addWidget(self.payment_methods_table)
        
        layout.addWidget(payment_methods_group)
        
        self.tabs.addTab(financial_widget, "💰 التقارير المالية")

    def setup_auto_refresh(self):
        """إعداد التحديث التلقائي"""
        self.auto_refresh_timer = QTimer()
        self.auto_refresh_timer.timeout.connect(self.refresh_data)
        self.auto_refresh_timer.start(60000)  # كل دقيقة

    def on_period_changed(self, period_text):
        """عند تغيير فترة التقرير"""
        period_map = {
            "اليوم": "today",
            "أمس": "yesterday", 
            "آخر 7 أيام": "week",
            "آخر 30 يوم": "month",
            "هذا الشهر": "this_month",
            "الشهر الماضي": "last_month",
            "آخر 3 شهور": "quarter",
            "هذا العام": "year"
        }
        self.current_period = period_map.get(period_text, "today")
        self.refresh_data()

    def get_date_range(self):
        """الحصول على نطاق التاريخ"""
        today = datetime.now().date()
        
        if self.current_period == "today":
            return today, today
        elif self.current_period == "yesterday":
            yesterday = today - timedelta(days=1)
            return yesterday, yesterday
        elif self.current_period == "week":
            return today - timedelta(days=7), today
        elif self.current_period == "month":
            return today - timedelta(days=30), today
        elif self.current_period == "this_month":
            return today.replace(day=1), today
        elif self.current_period == "last_month":
            first_day_last_month = (today.replace(day=1) - timedelta(days=1)).replace(day=1)
            last_day_last_month = today.replace(day=1) - timedelta(days=1)
            return first_day_last_month, last_day_last_month
        elif self.current_period == "quarter":
            return today - timedelta(days=90), today
        elif self.current_period == "year":
            return today.replace(month=1, day=1), today
        else:
            return self.from_date.date().toPython(), self.to_date.date().toPython()

    def refresh_data(self):
        """تحديث البيانات"""
        try:
            start_date, end_date = self.get_date_range()
            
            # تحديث الإحصائيات الرئيسية
            self.update_main_stats(start_date, end_date)
            
            # تحديث تقارير المبيعات
            self.update_sales_reports(start_date, end_date)
            
            # تحديث تقارير المخزون
            self.update_inventory_reports()
            
            # تحديث تقارير العملاء
            self.update_customers_reports(start_date, end_date)
            
            # تحديث التقارير المالية
            self.update_financial_reports(start_date, end_date)
            
        except Exception as e:
            QMessageBox.warning(self, "خطأ", f"فشل في تحديث التقارير: {str(e)}")

    def update_main_stats(self, start_date, end_date):
        """تحديث الإحصائيات الرئيسية"""
        # المبيعات
        sales_data = self.db_manager.execute_query("""
            SELECT COALESCE(SUM(total), 0) as total_sales,
                   COUNT(*) as order_count,
                   COALESCE(AVG(total), 0) as avg_order
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        """, (start_date.isoformat(), end_date.isoformat()))
        
        if sales_data:
            total_sales, order_count, avg_order = sales_data[0]
            self.sales_card.findChild(QLabel).setText(f"{total_sales:,.0f} جنيه")
            self.orders_card.findChild(QLabel).setText(str(order_count))
            self.avg_sale_card.findChild(QLabel).setText(f"{avg_order:,.0f} جنيه")
        
        # المنتجات
        products_data = self.db_manager.execute_query("""
            SELECT COUNT(*) as total_products,
                   COUNT(CASE WHEN current_qty <= min_qty THEN 1 END) as low_stock
            FROM products
        """)
        
        if products_data:
            total_products, low_stock = products_data[0]
            self.products_card.findChild(QLabel).setText(str(total_products))
            self.low_stock_card.findChild(QLabel).setText(str(low_stock))
        
        # العملاء
        customers_data = self.db_manager.execute_query("""
            SELECT COUNT(DISTINCT customer_name) as unique_customers
            FROM sales 
            WHERE DATE(sale_date) BETWEEN ? AND ?
        """, (start_date.isoformat(), end_date.isoformat()))
        
        if customers_data:
            unique_customers = customers_data[0][0]
            self.customers_card.findChild(QLabel).setText(str(unique_customers))

    def update_sales_reports(self, start_date, end_date):
        """تحديث تقارير المبيعات"""
        # أفضل المنتجات مبيعاً
        top_products_data = self.db_manager.execute_query("""
            SELECT p.name, 
                   SUM(si.qty) as total_qty,
                   SUM(si.total) as total_sales,
                   (SUM(si.total) * 100.0 / (SELECT SUM(total) FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?)) as percentage
            FROM sale_items si
            JOIN sales s ON si.sale_id = s.id
            JOIN products p ON si.product_id = p.id
            WHERE DATE(s.sale_date) BETWEEN ? AND ?
            GROUP BY p.id, p.name
            ORDER BY total_sales DESC
            LIMIT 10
        """, (start_date.isoformat(), end_date.isoformat(), start_date.isoformat(), end_date.isoformat()))
        
        self.populate_table(self.top_products_table, top_products_data, add_rank=True)
        
        # المبيعات اليومية
        daily_sales_data = self.db_manager.execute_query("""
            SELECT DATE(sale_date) as sale_date,
                   COUNT(*) as order_count,
                   SUM(total) as total_sales,
                   AVG(total) as avg_order
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY DATE(sale_date)
            ORDER BY sale_date DESC
        """, (start_date.isoformat(), end_date.isoformat()))
        
        self.populate_table(self.daily_sales_table, daily_sales_data)

    def update_inventory_reports(self):
        """تحديث تقارير المخزون"""
        # حالة المخزون
        stock_data = self.db_manager.execute_query("""
            SELECT name, current_qty, min_qty,
                   CASE 
                       WHEN current_qty <= 0 THEN 'نفد'
                       WHEN current_qty <= min_qty THEN 'منخفض'
                       ELSE 'متوفر'
                   END as status,
                   (current_qty * cost_price) as value,
                   updated_at
            FROM products
            ORDER BY current_qty ASC
        """)
        
        self.populate_table(self.stock_status_table, stock_data)

    def update_customers_reports(self, start_date, end_date):
        """تحديث تقارير العملاء"""
        # أفضل العملاء
        top_customers_data = self.db_manager.execute_query("""
            SELECT customer_name,
                   COUNT(*) as purchase_count,
                   SUM(total) as total_amount,
                   AVG(total) as avg_purchase,
                   MAX(sale_date) as last_purchase
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY customer_name
            ORDER BY total_amount DESC
            LIMIT 10
        """, (start_date.isoformat(), end_date.isoformat()))
        
        self.populate_table(self.top_customers_table, top_customers_data)

    def update_financial_reports(self, start_date, end_date):
        """تحديث التقارير المالية"""
        # طرق الدفع
        payment_methods_data = self.db_manager.execute_query("""
            SELECT payment_method,
                   COUNT(*) as transaction_count,
                   SUM(total) as total_amount,
                   (SUM(total) * 100.0 / (SELECT SUM(total) FROM sales WHERE DATE(sale_date) BETWEEN ? AND ?)) as percentage
            FROM sales
            WHERE DATE(sale_date) BETWEEN ? AND ?
            GROUP BY payment_method
            ORDER BY total_amount DESC
        """, (start_date.isoformat(), end_date.isoformat(), start_date.isoformat(), end_date.isoformat()))
        
        self.populate_table(self.payment_methods_table, payment_methods_data)

    def populate_table(self, table, data, add_rank=False):
        """ملء الجدول بالبيانات"""
        if not data:
            table.setRowCount(0)
            return
        
        table.setRowCount(len(data))
        
        for row, record in enumerate(data):
            col_offset = 0
            
            # إضافة رقم الترتيب
            if add_rank:
                rank_item = QTableWidgetItem(str(row + 1))
                rank_item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, 0, rank_item)
                col_offset = 1
            
            # إضافة باقي البيانات
            for col, value in enumerate(record):
                if value is not None:
                    if isinstance(value, float):
                        text = f"{value:,.2f}"
                    elif isinstance(value, int) and col > 0:
                        text = f"{value:,}"
                    else:
                        text = str(value)
                else:
                    text = "-"
                
                item = QTableWidgetItem(text)
                item.setTextAlignment(Qt.AlignmentFlag.AlignCenter)
                table.setItem(row, col + col_offset, item)
        
        # تخصيص حجم الأعمدة
        table.resizeColumnsToContents()
