
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة التقفيل اليومي - Daily Close Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QTextEdit,
                              QFrame, QGroupBox, QMessageBox, QScrollArea,
                              QDateEdit, QHeaderView, QAbstractItemView,
                              QProgressBar, QSplitter, QCheckBox)
from PySide6.QtCore import Qt, QDate, QTimer, QThread, Signal
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date
import logging

from app.utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class DailyCloseThread(QThread):
    """خيط التقفيل اليومي"""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, pos_service, repair_service, inventory_service, close_date):
        super().__init__()
        self.pos_service = pos_service
        self.repair_service = repair_service
        self.inventory_service = inventory_service
        self.close_date = close_date
    
    def run(self):
        """تشغيل التقفيل اليومي"""
        try:
            self.progress.emit(10)
            
            # جمع بيانات المبيعات
            sales_data = self.pos_service.get_daily_sales_summary(self.close_date)
            self.progress.emit(30)
            
            # جمع بيانات الصيانة
            repair_data = self.repair_service.get_repair_summary(self.close_date, self.close_date)
            self.progress.emit(50)
            
            # جمع بيانات المخزون
            inventory_data = self.inventory_service.get_inventory_summary()
            self.progress.emit(70)
            
            # جمع حركة المخزون
            stock_movements = self.inventory_service.get_stock_movements(
                None, self.close_date, self.close_date
            )
            self.progress.emit(90)
            
            # تجميع البيانات
            close_data = {
                'date': self.close_date,
                'sales': sales_data,
                'repair': repair_data,
                'inventory': inventory_data,
                'stock_movements': stock_movements,
                'timestamp': datetime.now().isoformat()
            }
            
            self.progress.emit(100)
            self.finished.emit(close_data)
            
        except Exception as e:
            self.error.emit(str(e))


class DailyCloseWindow(QWidget):
    """نافذة التقفيل اليومي"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pdf_generator = PDFGenerator()
        self.close_thread = None
        self.current_close_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)
        
        # عنوان الصفحة
        title_label = QLabel("التقفيل اليومي")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 30px; 
            padding: 20px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #e8f5e8, stop: 1 #c8e6c9);
            border-radius: 15px;
            border: 2px solid #4caf50;
        """)
        layout.addWidget(title_label)
        
        # شريط الأدوات
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("""
            QScrollArea { 
                border: none; 
                background-color: transparent;
            }
            QScrollBar:vertical {
                background-color: #ecf0f1;
                width: 12px;
                border-radius: 6px;
            }
            QScrollBar::handle:vertical {
                background-color: #bdc3c7;
                border-radius: 6px;
                min-height: 20px;
            }
        """)
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setContentsMargins(20, 20, 20, 20)
        scroll_layout.setSpacing(30)
        
        # ملخص اليوم
        self.setup_daily_summary(scroll_layout)
        
        # تفاصيل المبيعات
        self.setup_sales_details(scroll_layout)
        
        # تفاصيل الصيانة
        self.setup_repair_details(scroll_layout)
        
        # حركة المخزون
        self.setup_inventory_movements(scroll_layout)
        
        # إضافة مساحة في النهاية
        scroll_layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
        
        # شريط التقدم
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                text-align: center;
                padding: 2px;
                background-color: #ecf0f1;
                font-weight: bold;
            }
            QProgressBar::chunk {
                background-color: #4caf50;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)
    
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.NoFrame)
        toolbar.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 15px;
                padding: 25px;
                border: 2px solid #e9ecef;
                margin-bottom: 20px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        layout.setContentsMargins(25, 20, 25, 20)
        layout.setSpacing(20)
        
        # تاريخ التقفيل
        layout.addWidget(QLabel("تاريخ التقفيل:"))
        self.close_date = QDateEdit()
        self.close_date.setDate(QDate.currentDate())
        self.close_date.setCalendarPopup(True)
        self.close_date.setStyleSheet("""
            QDateEdit {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 14px;
                background-color: white;
                min-width: 150px;
            }
            QDateEdit:focus {
                border: 2px solid #4caf50;
            }
        """)
        layout.addWidget(self.close_date)
        
        layout.addStretch()
        
        # أزرار العمل
        generate_btn = QPushButton("إنتاج التقرير")
        generate_btn.setStyleSheet("""
            QPushButton {
                background-color: #4caf50;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
            QPushButton:pressed {
                background-color: #3d8b40;
            }
        """)
        generate_btn.clicked.connect(self.generate_close_report)
        layout.addWidget(generate_btn)
        
        self.close_day_btn = QPushButton("إقفال اليوم")
        self.close_day_btn.setStyleSheet("""
            QPushButton {
                background-color: #ff9800;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #e68900;
            }
            QPushButton:pressed {
                background-color: #cc7700;
            }
            QPushButton:disabled {
                background-color: #bdc3c7;
                color: #7f8c8d;
            }
        """)
        self.close_day_btn.clicked.connect(self.close_day)
        self.close_day_btn.setEnabled(False)
        layout.addWidget(self.close_day_btn)
        
        export_btn = QPushButton("تصدير PDF")
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196f3;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 25px;
                font-weight: bold;
                font-size: 14px;
                min-width: 120px;
            }
            QPushButton:hover {
                background-color: #1976d2;
            }
            QPushButton:pressed {
                background-color: #1565c0;
            }
        """)
        export_btn.clicked.connect(self.export_pdf)
        layout.addWidget(export_btn)
        
        return toolbar
    
    def setup_daily_summary(self, layout):
        """إعداد ملخص اليوم"""
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.NoFrame)
        summary_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 20px;
                padding: 30px;
                border: 2px solid #e9ecef;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        summary_layout.setContentsMargins(25, 25, 25, 25)
        summary_layout.setSpacing(25)
        
        # عنوان القسم
        summary_title = QLabel("ملخص اليوم")
        summary_title.setFont(QFont("Segoe UI", 20, QFont.Bold))
        summary_title.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 20px;
            padding: 15px;
            background-color: #e8f5e8;
            border-radius: 10px;
            border-left: 5px solid #4caf50;
        """)
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        stats_layout.setSpacing(20)
        
        self.sales_revenue_card = self.create_stat_card("إجمالي المبيعات", "0 ر.س", "#4caf50")
        stats_layout.addWidget(self.sales_revenue_card, 0, 0)
        
        self.transactions_count_card = self.create_stat_card("عدد المعاملات", "0", "#2196f3")
        stats_layout.addWidget(self.transactions_count_card, 0, 1)
        
        self.repair_revenue_card = self.create_stat_card("إيراد الصيانة", "0 ر.س", "#ff9800")
        stats_layout.addWidget(self.repair_revenue_card, 0, 2)
        
        self.total_revenue_card = self.create_stat_card("إجمالي الإيراد", "0 ر.س", "#9c27b0")
        stats_layout.addWidget(self.total_revenue_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
    
    def setup_sales_details(self, layout):
        """إعداد تفاصيل المبيعات"""
        sales_frame = QFrame()
        sales_frame.setFrameStyle(QFrame.NoFrame)
        sales_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 20px;
                padding: 30px;
                border: 2px solid #e9ecef;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        sales_layout = QVBoxLayout(sales_frame)
        sales_layout.setContentsMargins(25, 25, 25, 25)
        sales_layout.setSpacing(20)
        
        # عنوان القسم
        sales_title = QLabel("تفاصيل المبيعات")
        sales_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        sales_title.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 15px;
            padding: 12px;
            background-color: #e3f2fd;
            border-radius: 8px;
            border-left: 4px solid #2196f3;
        """)
        sales_layout.addWidget(sales_title)
        
        # جدول المبيعات
        self.sales_table = QTableWidget()
        self.sales_table.setColumnCount(6)
        self.sales_table.setHorizontalHeaderLabels([
            "رقم الفاتورة", "الوقت", "العميل", "إجمالي المبلغ", "طريقة الدفع", "الخصم"
        ])
        self.sales_table.setAlternatingRowColors(True)
        self.sales_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.sales_table.setMaximumHeight(300)
        
        # تخصيص الجدول
        header = self.sales_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        sales_layout.addWidget(self.sales_table)
        layout.addWidget(sales_frame)
    
    def setup_repair_details(self, layout):
        """إعداد تفاصيل الصيانة"""
        repair_frame = QFrame()
        repair_frame.setFrameStyle(QFrame.NoFrame)
        repair_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 20px;
                padding: 30px;
                border: 2px solid #e9ecef;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        repair_layout = QVBoxLayout(repair_frame)
        repair_layout.setContentsMargins(25, 25, 25, 25)
        repair_layout.setSpacing(20)
        
        # عنوان القسم
        repair_title = QLabel("تفاصيل الصيانة")
        repair_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        repair_title.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 15px;
            padding: 12px;
            background-color: #fff3e0;
            border-radius: 8px;
            border-left: 4px solid #ff9800;
        """)
        repair_layout.addWidget(repair_title)
        
        # جدول الصيانة
        self.repair_table = QTableWidget()
        self.repair_table.setColumnCount(5)
        self.repair_table.setHorizontalHeaderLabels([
            "رقم التذكرة", "العميل", "الجهاز", "الحالة", "التكلفة"
        ])
        self.repair_table.setAlternatingRowColors(True)
        self.repair_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.repair_table.setMaximumHeight(300)
        
        # تخصيص الجدول
        header = self.repair_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        repair_layout.addWidget(self.repair_table)
        layout.addWidget(repair_frame)
    
    def setup_inventory_movements(self, layout):
        """إعداد حركة المخزون"""
        inventory_frame = QFrame()
        inventory_frame.setFrameStyle(QFrame.NoFrame)
        inventory_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 20px;
                padding: 30px;
                border: 2px solid #e9ecef;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        inventory_layout = QVBoxLayout(inventory_frame)
        inventory_layout.setContentsMargins(25, 25, 25, 25)
        inventory_layout.setSpacing(20)
        
        # عنوان القسم
        inventory_title = QLabel("حركة المخزون")
        inventory_title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        inventory_title.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 15px;
            padding: 12px;
            background-color: #f3e5f5;
            border-radius: 8px;
            border-left: 4px solid #9c27b0;
        """)
        inventory_layout.addWidget(inventory_title)
        
        # جدول حركة المخزون
        self.inventory_table = QTableWidget()
        self.inventory_table.setColumnCount(5)
        self.inventory_table.setHorizontalHeaderLabels([
            "الوقت", "المنتج", "النوع", "الكمية", "المرجع"
        ])
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.inventory_table.setMaximumHeight(300)
        
        # تخصيص الجدول
        header = self.inventory_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        inventory_layout.addWidget(self.inventory_table)
        layout.addWidget(inventory_frame)
    
    def create_stat_card(self, title, value, color):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setFrameStyle(QFrame.NoFrame)
        card.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 {color}, stop: 1 {self.darken_color(color)});
                border-radius: 15px;
                padding: 25px;
                margin: 10px;
                border: 3px solid rgba(255, 255, 255, 0.2);
                min-height: 120px;
            }}
            QLabel {{
                color: white;
                border: none;
                background: transparent;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Segoe UI", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # حفظ مرجع للقيمة
        card.value_label = value_label
        
        return card
    
    def darken_color(self, hex_color):
        """تغميق اللون"""
        color = QColor(hex_color)
        return color.darker(120).name()
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.generate_close_report()
    
    def generate_close_report(self):
        """إنتاج تقرير التقفيل"""
        close_date = self.close_date.date().toString("yyyy-MM-dd")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.close_thread = DailyCloseThread(
            self.main_window.pos_service,
            self.main_window.repair_service,
            self.main_window.inventory_service,
            close_date
        )
        
        self.close_thread.finished.connect(self.on_report_finished)
        self.close_thread.error.connect(self.on_report_error)
        self.close_thread.progress.connect(self.progress_bar.setValue)
        
        self.close_thread.start()
    
    def on_report_finished(self, data):
        """عند انتهاء إنتاج التقرير"""
        self.progress_bar.setVisible(False)
        self.current_close_data = data
        
        self.display_close_data(data)
        self.close_day_btn.setEnabled(True)
    
    def on_report_error(self, error):
        """عند حدوث خطأ في إنتاج التقرير"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "خطأ", f"فشل في إنتاج تقرير التقفيل:\n{error}")
    
    def display_close_data(self, data):
        """عرض بيانات التقفيل"""
        try:
            sales_data = data.get('sales', {})
            repair_data = data.get('repair', {})
            
            # تحديث البطاقات
            sales_revenue = sales_data.get('total_amount', 0)
            repair_revenue = repair_data.get('total_revenue', 0)
            total_revenue = sales_revenue + repair_revenue
            
            self.sales_revenue_card.value_label.setText(f"{sales_revenue:.0f} ر.س")
            self.transactions_count_card.value_label.setText(str(sales_data.get('total_transactions', 0)))
            self.repair_revenue_card.value_label.setText(f"{repair_revenue:.0f} ر.س")
            self.total_revenue_card.value_label.setText(f"{total_revenue:.0f} ر.س")
            
            # عرض تفاصيل المبيعات
            self.display_sales_details(data)
            
            # عرض تفاصيل الصيانة
            self.display_repair_details(data)
            
            # عرض حركة المخزون
            self.display_inventory_movements(data)
            
        except Exception as e:
            logger.error(f"خطأ في عرض بيانات التقفيل: {str(e)}")
    
    def display_sales_details(self, data):
        """عرض تفاصيل المبيعات"""
        try:
            close_date = data['date']
            sales = self.main_window.pos_service.get_sales_by_date(close_date)
            
            self.sales_table.setRowCount(len(sales))
            
            for row, sale in enumerate(sales):
                self.sales_table.setItem(row, 0, QTableWidgetItem(str(sale['id'])))
                
                # تنسيق الوقت
                time_str = sale['created_at'][11:16] if len(sale['created_at']) > 16 else sale['created_at']
                self.sales_table.setItem(row, 1, QTableWidgetItem(time_str))
                
                customer = sale.get('customer_name', 'غير محدد')
                self.sales_table.setItem(row, 2, QTableWidgetItem(customer))
                
                amount_item = QTableWidgetItem(f"{sale['final_amount']:.2f}")
                amount_item.setTextAlignment(Qt.AlignCenter)
                self.sales_table.setItem(row, 3, amount_item)
                
                payment_method = self.main_window.pos_service.get_payment_method_name(sale['payment_method'])
                self.sales_table.setItem(row, 4, QTableWidgetItem(payment_method))
                
                discount_item = QTableWidgetItem(f"{sale.get('discount_amount', 0):.2f}")
                discount_item.setTextAlignment(Qt.AlignCenter)
                self.sales_table.setItem(row, 5, discount_item)
                
        except Exception as e:
            logger.error(f"خطأ في عرض تفاصيل المبيعات: {str(e)}")
    
    def display_repair_details(self, data):
        """عرض تفاصيل الصيانة"""
        try:
            close_date = data['date']
            repairs = self.main_window.repair_service.get_repair_tickets_by_date(close_date)
            
            self.repair_table.setRowCount(len(repairs))
            
            for row, repair in enumerate(repairs):
                self.repair_table.setItem(row, 0, QTableWidgetItem(str(repair['id'])))
                
                customer = repair.get('customer_name', 'غير محدد')
                self.repair_table.setItem(row, 1, QTableWidgetItem(customer))
                
                device = repair['device_info']
                self.repair_table.setItem(row, 2, QTableWidgetItem(device))
                
                status = self.main_window.repair_service.get_status_name(repair['status'])
                status_item = QTableWidgetItem(status)
                status_item.setTextAlignment(Qt.AlignCenter)
                self.repair_table.setItem(row, 3, status_item)
                
                cost = repair.get('final_cost') or repair.get('estimated_cost', 0)
                cost_item = QTableWidgetItem(f"{cost:.2f}")
                cost_item.setTextAlignment(Qt.AlignCenter)
                self.repair_table.setItem(row, 4, cost_item)
                
        except Exception as e:
            logger.error(f"خطأ في عرض تفاصيل الصيانة: {str(e)}")
    
    def display_inventory_movements(self, data):
        """عرض حركة المخزون"""
        try:
            movements = data.get('stock_movements', [])
            
            self.inventory_table.setRowCount(len(movements))
            
            for row, movement in enumerate(movements):
                # الوقت
                time_str = movement['created_at'][11:16] if len(movement['created_at']) > 16 else movement['created_at']
                self.inventory_table.setItem(row, 0, QTableWidgetItem(time_str))
                
                # المنتج
                product_name = movement.get('product_name', 'غير معروف')
                self.inventory_table.setItem(row, 1, QTableWidgetItem(product_name))
                
                # النوع
                movement_type = "دخول" if movement['movement_type'] == 'in' else "خروج"
                type_item = QTableWidgetItem(movement_type)
                type_item.setTextAlignment(Qt.AlignCenter)
                
                if movement['movement_type'] == 'in':
                    type_item.setBackground(QColor("#4caf50"))
                else:
                    type_item.setBackground(QColor("#f44336"))
                
                type_item.setForeground(QColor("white"))
                self.inventory_table.setItem(row, 2, type_item)
                
                # الكمية
                quantity_item = QTableWidgetItem(str(movement['quantity']))
                quantity_item.setTextAlignment(Qt.AlignCenter)
                self.inventory_table.setItem(row, 3, quantity_item)
                
                # المرجع
                reference = movement.get('reference_type', '')
                self.inventory_table.setItem(row, 4, QTableWidgetItem(reference))
                
        except Exception as e:
            logger.error(f"خطأ في عرض حركة المخزون: {str(e)}")
    
    def close_day(self):
        """إقفال اليوم"""
        if not self.current_close_data:
            QMessageBox.warning(self, "تحذير", "يجب إنتاج التقرير أولاً")
            return
        
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل أنت متأكد من إقفال اليوم؟\n"
            "لن يمكن تعديل البيانات بعد الإقفال.",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                # حفظ بيانات الإقفال
                close_date = self.current_close_data['date']
                success = self.main_window.pos_service.close_day(close_date, self.current_close_data)
                
                if success:
                    QMessageBox.information(
                        self, "نجح",
                        f"تم إقفال يوم {close_date} بنجاح"
                    )
                    self.close_day_btn.setEnabled(False)
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إقفال اليوم")
                    
            except Exception as e:
                logger.error(f"خطأ في إقفال اليوم: {str(e)}")
                QMessageBox.critical(self, "خطأ", f"حدث خطأ في إقفال اليوم:\n{str(e)}")
    
    def export_pdf(self):
        """تصدير التقرير إلى PDF"""
        if not self.current_close_data:
            QMessageBox.warning(self, "تحذير", "لا يوجد تقرير لتصديره")
            return
        
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            close_date = self.current_close_data['date']
            filename = f"daily_close_{close_date}_{timestamp}.pdf"
            filepath = f"reports/daily/{filename}"
            
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            import os
            os.makedirs("reports/daily", exist_ok=True)
            
            # إنتاج تقرير PDF
            success = self.pdf_generator.generate_daily_close_report(
                self.current_close_data, filepath
            )
            
            if success:
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ التقرير في:\n{filepath}"
                )
                
                # فتح الملف
                import subprocess
                import sys
                
                if sys.platform.startswith('win'):
                    os.startfile(filepath)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', filepath])
                else:
                    subprocess.run(['xdg-open', filepath])
                    
            else:
                QMessageBox.warning(
                    self, "تحذير",
                    "فشل في إنتاج ملف PDF للتقرير"
                )
                
        except Exception as e:
            logger.error(f"خطأ في تصدير PDF: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في تصدير التقرير:\n{str(e)}"
            )
