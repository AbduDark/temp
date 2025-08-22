#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة التقارير - Reports Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QTabWidget,
                              QTextEdit, QFrame, QGroupBox, QMessageBox,
                              QDateEdit, QHeaderView, QAbstractItemView,
                              QProgressBar, QFileDialog ,QScrollArea)
from PySide6.QtCore import Qt, QDate, QThread, Signal
from PySide6.QtGui import QFont, QColor 
from datetime import datetime, date, timedelta
import json
import csv
import logging

from app.utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class ReportGeneratorThread(QThread):
    """خيط لإنتاج التقارير في الخلفية"""
    
    finished = Signal(dict)
    error = Signal(str)
    progress = Signal(int)
    
    def __init__(self, report_service, report_type, start_date, end_date):
        super().__init__()
        self.report_service = report_service
        self.report_type = report_type
        self.start_date = start_date
        self.end_date = end_date
    
    def run(self):
        """تشغيل إنتاج التقرير"""
        try:
            self.progress.emit(10)
            
            if self.report_type == 'sales':
                data = self.report_service.get_sales_report(self.start_date, self.end_date)
            elif self.report_type == 'inventory':
                data = self.report_service.get_inventory_report()
            elif self.report_type == 'repair':
                data = self.report_service.get_repair_report(self.start_date, self.end_date)
            elif self.report_type == 'profit_loss':
                data = self.report_service.get_profit_loss_report(self.start_date, self.end_date)
            elif self.report_type == 'customer':
                data = self.report_service.get_customer_report(self.start_date, self.end_date)
            else:
                raise ValueError(f"نوع تقرير غير مدعوم: {self.report_type}")
            
            self.progress.emit(100)
            self.finished.emit(data)
            
        except Exception as e:
            self.error.emit(str(e))


class ReportsWindow(QWidget):
    """نافذة التقارير"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pdf_generator = PDFGenerator()
        self.current_report_data = None
        self.report_thread = None
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # شريط الأدوات
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # التبويبات
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e9ecef;
                border-radius: 15px;
                background-color: white;
                padding: 20px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 12px 20px;
                margin: 2px;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                min-width: 120px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)
        
        # تبويب المبيعات
        sales_tab = self.create_sales_tab()
        self.tab_widget.addTab(sales_tab, "تقارير المبيعات")
        
        # تبويب المخزون
        inventory_tab = self.create_inventory_tab()
        self.tab_widget.addTab(inventory_tab, "تقارير المخزون")
        
        # تبويب الصيانة
        repair_tab = self.create_repair_tab()
        self.tab_widget.addTab(repair_tab, "تقارير الصيانة")
        
        # تبويب الربح والخسارة
        profit_loss_tab = self.create_profit_loss_tab()
        self.tab_widget.addTab(profit_loss_tab, "الربح والخسارة")
        
        # تبويب العملاء
        customer_tab = self.create_customer_tab()
        self.tab_widget.addTab(customer_tab, "تقارير العملاء")
        
        layout.addWidget(self.tab_widget)
        
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
            }
            QProgressBar::chunk {
                background-color: #3498db;
                border-radius: 8px;
            }
        """)
        layout.addWidget(self.progress_bar)
    
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        
        # إعدادات التقرير العامة
        layout.addWidget(QLabel("من تاريخ:"))
        self.global_start_date = QDateEdit()
        self.global_start_date.setDate(QDate.currentDate().addDays(-30))
        self.global_start_date.setCalendarPopup(True)
        layout.addWidget(self.global_start_date)
        
        layout.addWidget(QLabel("إلى تاريخ:"))
        self.global_end_date = QDateEdit()
        self.global_end_date.setDate(QDate.currentDate())
        self.global_end_date.setCalendarPopup(True)
        layout.addWidget(self.global_end_date)
        
        layout.addStretch()
        
        # أزرار التصدير
        export_pdf_btn = QPushButton("تصدير PDF")
        export_pdf_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        export_pdf_btn.clicked.connect(self.export_pdf)
        layout.addWidget(export_pdf_btn)
        
        export_excel_btn = QPushButton("تصدير Excel")
        export_excel_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        export_excel_btn.clicked.connect(self.export_excel)
        layout.addWidget(export_excel_btn)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        return toolbar
    
    def create_sales_tab(self):
        """إنشاء تبويب تقارير المبيعات"""
        tab = QWidget()
        main_layout = QVBoxLayout(tab)
        main_layout.setContentsMargins(10, 10, 10, 10)
        
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
        layout = QVBoxLayout(scroll_widget)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(25)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.NoFrame)
        settings_frame.setStyleSheet("""
            QFrame {
                background-color: #f8f9fa;
                border-radius: 15px;
                padding: 20px;
                border: 2px solid #e9ecef;
            }
        """)
        settings_layout = QHBoxLayout(settings_frame)
        settings_layout.setContentsMargins(20, 15, 20, 15)
        settings_layout.setSpacing(20)
        
        settings_layout.addWidget(QLabel("تجميع حسب:"))
        self.sales_group_combo = QComboBox()
        self.sales_group_combo.addItem("يوم", "day")
        self.sales_group_combo.addItem("شهر", "month")
        settings_layout.addWidget(self.sales_group_combo)
        
        generate_sales_btn = QPushButton("إنتاج التقرير")
        generate_sales_btn.clicked.connect(self.generate_sales_report)
        settings_layout.addWidget(generate_sales_btn)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # ملخص المبيعات
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("ملخص المبيعات")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        self.sales_total_card = self.create_stat_card("إجمالي المبيعات", "0 ر.س", "#27ae60")
        stats_layout.addWidget(self.sales_total_card, 0, 0)
        
        self.sales_transactions_card = self.create_stat_card("عدد المعاملات", "0", "#3498db")
        stats_layout.addWidget(self.sales_transactions_card, 0, 1)
        
        self.sales_avg_card = self.create_stat_card("متوسط المعاملة", "0 ر.س", "#9b59b6")
        stats_layout.addWidget(self.sales_avg_card, 0, 2)
        
        self.sales_discount_card = self.create_stat_card("إجمالي الخصومات", "0 ر.س", "#e67e22")
        stats_layout.addWidget(self.sales_discount_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # جدول تفاصيل المبيعات
        self.sales_details_table = QTableWidget()
        self.sales_details_table.setAlternatingRowColors(True)
        layout.addWidget(self.sales_details_table)
        
        # إضافة مساحة في النهاية
        layout.addStretch()
        
        scroll_area.setWidget(scroll_widget)
        main_layout.addWidget(scroll_area)
        
        return tab
    
    def create_inventory_tab(self):
        """إنشاء تبويب تقارير المخزون"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QHBoxLayout(settings_frame)
        
        generate_inventory_btn = QPushButton("إنتاج تقرير المخزون")
        generate_inventory_btn.clicked.connect(self.generate_inventory_report)
        settings_layout.addWidget(generate_inventory_btn)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # ملخص المخزون
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("ملخص المخزون")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        self.inventory_products_card = self.create_stat_card("إجمالي المنتجات", "0", "#3498db")
        stats_layout.addWidget(self.inventory_products_card, 0, 0)
        
        self.inventory_value_card = self.create_stat_card("قيمة المخزون", "0 ر.س", "#27ae60")
        stats_layout.addWidget(self.inventory_value_card, 0, 1)
        
        self.inventory_low_stock_card = self.create_stat_card("مخزون منخفض", "0", "#e74c3c")
        stats_layout.addWidget(self.inventory_low_stock_card, 0, 2)
        
        self.inventory_out_stock_card = self.create_stat_card("نفد من المخزون", "0", "#e67e22")
        stats_layout.addWidget(self.inventory_out_stock_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # جدول تفاصيل المخزون
        self.inventory_details_table = QTableWidget()
        self.inventory_details_table.setAlternatingRowColors(True)
        layout.addWidget(self.inventory_details_table)
        
        return tab
    
    def create_repair_tab(self):
        """إنشاء تبويب تقارير الصيانة"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QHBoxLayout(settings_frame)
        
        generate_repair_btn = QPushButton("إنتاج تقرير الصيانة")
        generate_repair_btn.clicked.connect(self.generate_repair_report)
        settings_layout.addWidget(generate_repair_btn)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # ملخص الصيانة
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("ملخص الصيانة")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        self.repair_total_card = self.create_stat_card("إجمالي التذاكر", "0", "#3498db")
        stats_layout.addWidget(self.repair_total_card, 0, 0)
        
        self.repair_completed_card = self.create_stat_card("المكتملة", "0", "#27ae60")
        stats_layout.addWidget(self.repair_completed_card, 0, 1)
        
        self.repair_pending_card = self.create_stat_card("قيد العمل", "0", "#f39c12")
        stats_layout.addWidget(self.repair_pending_card, 0, 2)
        
        self.repair_revenue_card = self.create_stat_card("إيراد الصيانة", "0 ر.س", "#9b59b6")
        stats_layout.addWidget(self.repair_revenue_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # جدول تفاصيل الصيانة
        self.repair_details_table = QTableWidget()
        self.repair_details_table.setAlternatingRowColors(True)
        layout.addWidget(self.repair_details_table)
        
        return tab
    
    def create_profit_loss_tab(self):
        """إنشاء تبويب الربح والخسارة"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QHBoxLayout(settings_frame)
        
        generate_pl_btn = QPushButton("إنتاج تقرير الربح والخسارة")
        generate_pl_btn.clicked.connect(self.generate_profit_loss_report)
        settings_layout.addWidget(generate_pl_btn)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # ملخص الربح والخسارة
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("الربح والخسارة")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        self.pl_revenue_card = self.create_stat_card("إجمالي الإيراد", "0 ر.س", "#3498db")
        stats_layout.addWidget(self.pl_revenue_card, 0, 0)
        
        self.pl_costs_card = self.create_stat_card("التكاليف", "0 ر.س", "#e74c3c")
        stats_layout.addWidget(self.pl_costs_card, 0, 1)
        
        self.pl_gross_profit_card = self.create_stat_card("الربح الإجمالي", "0 ر.س", "#27ae60")
        stats_layout.addWidget(self.pl_gross_profit_card, 0, 2)
        
        self.pl_net_profit_card = self.create_stat_card("صافي الربح", "0 ر.س", "#9b59b6")
        stats_layout.addWidget(self.pl_net_profit_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # تفاصيل الربح والخسارة
        self.pl_details = QTextEdit()
        self.pl_details.setReadOnly(True)
        self.pl_details.setMaximumHeight(300)
        layout.addWidget(self.pl_details)
        
        return tab
    
    def create_customer_tab(self):
        """إنشاء تبويب تقارير العملاء"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QHBoxLayout(settings_frame)
        
        generate_customer_btn = QPushButton("إنتاج تقرير العملاء")
        generate_customer_btn.clicked.connect(self.generate_customer_report)
        settings_layout.addWidget(generate_customer_btn)
        
        settings_layout.addStretch()
        
        layout.addWidget(settings_frame)
        
        # ملخص العملاء
        summary_frame = QFrame()
        summary_frame.setFrameStyle(QFrame.StyledPanel)
        summary_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("إحصائيات العملاء")
        summary_title.setFont(QFont("Arial", 14, QFont.Bold))
        summary_title.setStyleSheet("color: #2c3e50;")
        summary_layout.addWidget(summary_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        self.customer_total_card = self.create_stat_card("إجمالي العملاء", "0", "#3498db")
        stats_layout.addWidget(self.customer_total_card, 0, 0)
        
        self.customer_purchasing_card = self.create_stat_card("عملاء المبيعات", "0", "#27ae60")
        stats_layout.addWidget(self.customer_purchasing_card, 0, 1)
        
        self.customer_repair_card = self.create_stat_card("عملاء الصيانة", "0", "#e67e22")
        stats_layout.addWidget(self.customer_repair_card, 0, 2)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # جدول أفضل العملاء
        self.customer_details_table = QTableWidget()
        self.customer_details_table.setAlternatingRowColors(True)
        layout.addWidget(self.customer_details_table)
        
        return tab
    
    def create_stat_card(self, title, value, color):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                min-height: 80px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 16, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # حفظ مرجع للقيمة
        card.value_label = value_label
        
        return card
    
    def refresh_data(self):
        """تحديث البيانات"""
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # المبيعات
            self.generate_sales_report()
        elif current_tab == 1:  # المخزون
            self.generate_inventory_report()
        elif current_tab == 2:  # الصيانة
            self.generate_repair_report()
        elif current_tab == 3:  # الربح والخسارة
            self.generate_profit_loss_report()
        elif current_tab == 4:  # العملاء
            self.generate_customer_report()
    
    def start_report_generation(self, report_type):
        """بدء إنتاج التقرير في خيط منفصل"""
        start_date = self.global_start_date.date().toString("yyyy-MM-dd")
        end_date = self.global_end_date.date().toString("yyyy-MM-dd")
        
        self.progress_bar.setVisible(True)
        self.progress_bar.setValue(0)
        
        self.report_thread = ReportGeneratorThread(
            self.main_window.report_service,
            report_type,
            start_date,
            end_date
        )
        
        self.report_thread.finished.connect(self.on_report_finished)
        self.report_thread.error.connect(self.on_report_error)
        self.report_thread.progress.connect(self.progress_bar.setValue)
        
        self.report_thread.start()
    
    def on_report_finished(self, data):
        """عند انتهاء إنتاج التقرير"""
        self.progress_bar.setVisible(False)
        self.current_report_data = data
        
        current_tab = self.tab_widget.currentIndex()
        
        if current_tab == 0:  # المبيعات
            self.display_sales_report(data)
        elif current_tab == 1:  # المخزون
            self.display_inventory_report(data)
        elif current_tab == 2:  # الصيانة
            self.display_repair_report(data)
        elif current_tab == 3:  # الربح والخسارة
            self.display_profit_loss_report(data)
        elif current_tab == 4:  # العملاء
            self.display_customer_report(data)
    
    def on_report_error(self, error):
        """عند حدوث خطأ في إنتاج التقرير"""
        self.progress_bar.setVisible(False)
        QMessageBox.critical(self, "خطأ", f"فشل في إنتاج التقرير:\n{error}")
    
    def generate_sales_report(self):
        """إنتاج تقرير المبيعات"""
        self.start_report_generation('sales')
    
    def display_sales_report(self, data):
        """عرض تقرير المبيعات"""
        summary = data.get('summary', {})
        
        # تحديث البطاقات
        self.sales_total_card.value_label.setText(f"{summary.get('total_sales', 0):.0f} ر.س")
        self.sales_transactions_card.value_label.setText(str(summary.get('total_transactions', 0)))
        self.sales_avg_card.value_label.setText(f"{summary.get('avg_transaction', 0):.0f} ر.س")
        self.sales_discount_card.value_label.setText(f"{summary.get('total_discounts', 0):.0f} ر.س")
        
        # عرض أفضل المنتجات
        top_products = data.get('top_products', [])
        self.sales_details_table.setColumnCount(4)
        self.sales_details_table.setHorizontalHeaderLabels([
            "المنتج", "الكمية المباعة", "إجمالي الإيراد", "متوسط السعر"
        ])
        self.sales_details_table.setRowCount(len(top_products))
        
        for row, product in enumerate(top_products):
            self.sales_details_table.setItem(row, 0, QTableWidgetItem(product['name']))
            self.sales_details_table.setItem(row, 1, QTableWidgetItem(str(product.get('total_sold', 0))))
            self.sales_details_table.setItem(row, 2, QTableWidgetItem(f"{product.get('total_revenue', 0):.2f}"))
            self.sales_details_table.setItem(row, 3, QTableWidgetItem(f"{product.get('avg_price', 0):.2f}"))
        
        # تخصيص الجدول
        header = self.sales_details_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def generate_inventory_report(self):
        """إنتاج تقرير المخزون"""
        self.start_report_generation('inventory')
    
    def display_inventory_report(self, data):
        """عرض تقرير المخزون"""
        summary = data.get('summary', {})
        
        # تحديث البطاقات
        self.inventory_products_card.value_label.setText(str(summary.get('total_products', 0)))
        self.inventory_value_card.value_label.setText(f"{summary.get('total_selling_value', 0):.0f} ر.س")
        self.inventory_low_stock_card.value_label.setText(str(summary.get('low_stock_count', 0)))
        self.inventory_out_stock_card.value_label.setText(str(summary.get('out_of_stock_count', 0)))
        
        # عرض المخزون حسب الفئة
        by_category = data.get('by_category', [])
        self.inventory_details_table.setColumnCount(5)
        self.inventory_details_table.setHorizontalHeaderLabels([
            "الفئة", "عدد المنتجات", "الكمية الإجمالية", "قيمة التكلفة", "قيمة البيع"
        ])
        self.inventory_details_table.setRowCount(len(by_category))
        
        for row, category in enumerate(by_category):
            self.inventory_details_table.setItem(row, 0, QTableWidgetItem(category['category_name']))
            self.inventory_details_table.setItem(row, 1, QTableWidgetItem(str(category.get('product_count', 0))))
            self.inventory_details_table.setItem(row, 2, QTableWidgetItem(str(category.get('total_quantity', 0))))
            self.inventory_details_table.setItem(row, 3, QTableWidgetItem(f"{category.get('total_cost_value', 0):.2f}"))
            self.inventory_details_table.setItem(row, 4, QTableWidgetItem(f"{category.get('total_selling_value', 0):.2f}"))
        
        # تخصيص الجدول
        header = self.inventory_details_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def generate_repair_report(self):
        """إنتاج تقرير الصيانة"""
        self.start_report_generation('repair')
    
    def display_repair_report(self, data):
        """عرض تقرير الصيانة"""
        summary = data.get('summary', {})
        
        # تحديث البطاقات
        self.repair_total_card.value_label.setText(str(summary.get('total_tickets', 0)))
        self.repair_completed_card.value_label.setText(str(summary.get('completed_tickets', 0)))
        self.repair_pending_card.value_label.setText(str(summary.get('in_progress_tickets', 0)))
        self.repair_revenue_card.value_label.setText(f"{summary.get('total_revenue', 0):.0f} ر.س")
        
        # عرض أداء الفنيين
        technician_performance = data.get('technician_performance', [])
        self.repair_details_table.setColumnCount(5)
        self.repair_details_table.setHorizontalHeaderLabels([
            "الفني", "إجمالي التذاكر", "المكتملة", "الإيراد", "متوسط الإنجاز (أيام)"
        ])
        self.repair_details_table.setRowCount(len(technician_performance))
        
        for row, tech in enumerate(technician_performance):
            self.repair_details_table.setItem(row, 0, QTableWidgetItem(tech['technician_name']))
            self.repair_details_table.setItem(row, 1, QTableWidgetItem(str(tech.get('total_tickets', 0))))
            self.repair_details_table.setItem(row, 2, QTableWidgetItem(str(tech.get('completed_tickets', 0))))
            self.repair_details_table.setItem(row, 3, QTableWidgetItem(f"{tech.get('total_revenue', 0):.2f}"))
            self.repair_details_table.setItem(row, 4, QTableWidgetItem(f"{tech.get('avg_completion_days', 0):.1f}"))
        
        # تخصيص الجدول
        header = self.repair_details_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def generate_profit_loss_report(self):
        """إنتاج تقرير الربح والخسارة"""
        self.start_report_generation('profit_loss')
    
    def display_profit_loss_report(self, data):
        """عرض تقرير الربح والخسارة"""
        revenue = data.get('revenue', {})
        costs = data.get('costs', {})
        profit = data.get('profit', {})
        
        # تحديث البطاقات
        self.pl_revenue_card.value_label.setText(f"{revenue.get('total_revenue', 0):.0f} ر.س")
        self.pl_costs_card.value_label.setText(f"{costs.get('cost_of_goods_sold', 0):.0f} ر.س")
        self.pl_gross_profit_card.value_label.setText(f"{profit.get('gross_profit', 0):.0f} ر.س")
        self.pl_net_profit_card.value_label.setText(f"{profit.get('net_profit', 0):.0f} ر.س")
        
        # تفاصيل الربح والخسارة
        details_text = f"""
تقرير الربح والخسارة
من {data.get('period', {}).get('start', '')} إلى {data.get('period', {}).get('end', '')}

الإيرادات:
- إيرادات المبيعات: {revenue.get('sales_revenue', 0):.2f} ر.س
- إيرادات الصيانة: {revenue.get('repair_revenue', 0):.2f} ر.س
- إجمالي الإيرادات: {revenue.get('total_revenue', 0):.2f} ر.س

المرتجعات: {revenue.get('returns', 0):.2f} ر.س

التكاليف:
- تكلفة البضاعة المباعة: {costs.get('cost_of_goods_sold', 0):.2f} ر.س

الأرباح:
- الربح الإجمالي: {profit.get('gross_profit', 0):.2f} ر.س
- صافي الربح: {profit.get('net_profit', 0):.2f} ر.س
- هامش الربح الإجمالي: {profit.get('gross_margin', 0):.1f}%
- هامش صافي الربح: {profit.get('net_margin', 0):.1f}%
        """.strip()
        
        self.pl_details.setText(details_text)
    
    def generate_customer_report(self):
        """إنتاج تقرير العملاء"""
        self.start_report_generation('customer')
    
    def display_customer_report(self, data):
        """عرض تقرير العملاء"""
        statistics = data.get('statistics', {})
        
        # تحديث البطاقات
        self.customer_total_card.value_label.setText(str(statistics.get('total_customers', 0)))
        self.customer_purchasing_card.value_label.setText(str(statistics.get('purchasing_customers', 0)))
        self.customer_repair_card.value_label.setText(str(statistics.get('repair_customers', 0)))
        
        # عرض أفضل العملاء
        top_customers = data.get('top_customers', [])
        self.customer_details_table.setColumnCount(5)
        self.customer_details_table.setHorizontalHeaderLabels([
            "العميل", "الهاتف", "عدد المشتريات", "إجمالي الإنفاق", "متوسط المشتريات"
        ])
        self.customer_details_table.setRowCount(len(top_customers))
        
        for row, customer in enumerate(top_customers):
            self.customer_details_table.setItem(row, 0, QTableWidgetItem(customer.get('name', 'غير محدد')))
            self.customer_details_table.setItem(row, 1, QTableWidgetItem(customer.get('phone', 'غير محدد')))
            self.customer_details_table.setItem(row, 2, QTableWidgetItem(str(customer.get('total_purchases', 0))))
            self.customer_details_table.setItem(row, 3, QTableWidgetItem(f"{customer.get('total_spent', 0):.2f}"))
            self.customer_details_table.setItem(row, 4, QTableWidgetItem(f"{customer.get('avg_purchase', 0):.2f}"))
        
        # تخصيص الجدول
        header = self.customer_details_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
    
    def export_pdf(self):
        """تصدير التقرير إلى PDF"""
        if not self.current_report_data:
            QMessageBox.warning(self, "تحذير", "لا يوجد تقرير لتصديره")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ التقرير", 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf",
                "ملفات PDF (*.pdf)"
            )
            
            if file_path:
                current_tab = self.tab_widget.currentIndex()
                report_type = ['sales', 'inventory', 'repair', 'profit_loss', 'customer'][current_tab]
                
                success = self.pdf_generator.generate_report(
                    self.current_report_data, 
                    report_type, 
                    file_path
                )
                
                if success:
                    QMessageBox.information(
                        self, "نجح",
                        f"تم حفظ التقرير في:\n{file_path}"
                    )
                    
                    # فتح الملف
                    import subprocess
                    import sys
                    import os
                    
                    if sys.platform.startswith('win'):
                        os.startfile(file_path)
                    elif sys.platform.startswith('darwin'):
                        subprocess.run(['open', file_path])
                    else:
                        subprocess.run(['xdg-open', file_path])
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في تصدير التقرير")
                    
        except Exception as e:
            logger.error(f"خطأ في تصدير PDF: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في التصدير:\n{str(e)}")
    
    def export_excel(self):
        """تصدير التقرير إلى Excel"""
        if not self.current_report_data:
            QMessageBox.warning(self, "تحذير", "لا يوجد تقرير لتصديره")
            return
        
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "حفظ التقرير", 
                f"report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "ملفات CSV (*.csv)"
            )
            
            if file_path:
                current_tab = self.tab_widget.currentIndex()
                
                # تحديد الجدول المناسب
                if current_tab == 0:  # المبيعات
                    table = self.sales_details_table
                elif current_tab == 1:  # المخزون
                    table = self.inventory_details_table
                elif current_tab == 2:  # الصيانة
                    table = self.repair_details_table
                elif current_tab == 4:  # العملاء
                    table = self.customer_details_table
                else:
                    QMessageBox.warning(self, "تحذير", "هذا التقرير لا يدعم التصدير إلى Excel")
                    return
                
                # تصدير البيانات
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    writer = csv.writer(csvfile)
                    
                    # كتابة العناوين
                    headers = []
                    for col in range(table.columnCount()):
                        headers.append(table.horizontalHeaderItem(col).text())
                    writer.writerow(headers)
                    
                    # كتابة البيانات
                    for row in range(table.rowCount()):
                        row_data = []
                        for col in range(table.columnCount()):
                            item = table.item(row, col)
                            row_data.append(item.text() if item else '')
                        writer.writerow(row_data)
                
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ التقرير في:\n{file_path}"
                )
                
        except Exception as e:
            logger.error(f"خطأ في تصدير Excel: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في التصدير:\n{str(e)}")
