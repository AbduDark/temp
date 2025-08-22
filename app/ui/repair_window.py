#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إدارة الصيانة - Repair Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QSpinBox,
                              QDoubleSpinBox, QTextEdit, QFrame, QGroupBox,
                              QMessageBox, QDialog, QDialogButtonBox,
                              QTabWidget, QHeaderView, QAbstractItemView,
                              QDateEdit, QSplitter, QProgressBar)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor
from datetime import datetime, date
import logging

from app.utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class RepairTicketDialog(QDialog):
    """نافذة إنشاء/تعديل تذكرة صيانة"""
    
    def __init__(self, parent=None, ticket=None, technicians=None):
        super().__init__(parent)
        self.ticket = ticket
        self.technicians = technicians or []
        self.setup_ui()
        
        if ticket:
            self.load_ticket_data()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        title = "تعديل تذكرة صيانة" if self.ticket else "تذكرة صيانة جديدة"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(600, 700)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # معلومات العميل
        customer_group = QGroupBox("معلومات العميل")
        customer_layout = QGridLayout(customer_group)
        
        customer_layout.addWidget(QLabel("اسم العميل:"), 0, 0)
        self.customer_name_edit = QLineEdit()
        customer_layout.addWidget(self.customer_name_edit, 0, 1)
        
        customer_layout.addWidget(QLabel("رقم الهاتف:"), 1, 0)
        self.customer_phone_edit = QLineEdit()
        customer_layout.addWidget(self.customer_phone_edit, 1, 1)
        
        customer_layout.addWidget(QLabel("البريد الإلكتروني:"), 2, 0)
        self.customer_email_edit = QLineEdit()
        customer_layout.addWidget(self.customer_email_edit, 2, 1)
        
        layout.addWidget(customer_group)
        
        # معلومات الجهاز
        device_group = QGroupBox("معلومات الجهاز")
        device_layout = QGridLayout(device_group)
        
        device_layout.addWidget(QLabel("معلومات الجهاز:"), 0, 0)
        self.device_info_edit = QLineEdit()
        self.device_info_edit.setPlaceholderText("مثال: iPhone 13 Pro - أبيض")
        device_layout.addWidget(self.device_info_edit, 0, 1)
        
        device_layout.addWidget(QLabel("رقم IMEI:"), 1, 0)
        self.imei_edit = QLineEdit()
        device_layout.addWidget(self.imei_edit, 1, 1)
        
        layout.addWidget(device_group)
        
        # معلومات الصيانة
        repair_group = QGroupBox("معلومات الصيانة")
        repair_layout = QGridLayout(repair_group)
        
        repair_layout.addWidget(QLabel("نوع الصيانة:"), 0, 0)
        self.repair_type_combo = QComboBox()
        self.repair_type_combo.addItem("هاردوير", "hardware")
        self.repair_type_combo.addItem("سوفتوير", "software")
        repair_layout.addWidget(self.repair_type_combo, 0, 1)
        
        repair_layout.addWidget(QLabel("وصف المشكلة:"), 1, 0)
        self.problem_edit = QTextEdit()
        self.problem_edit.setMaximumHeight(100)
        repair_layout.addWidget(self.problem_edit, 1, 1)
        
        repair_layout.addWidget(QLabel("التكلفة المقدرة:"), 2, 0)
        self.estimated_cost_spin = QDoubleSpinBox()
        self.estimated_cost_spin.setMaximum(99999.99)
        self.estimated_cost_spin.setSuffix(" ر.س")
        repair_layout.addWidget(self.estimated_cost_spin, 2, 1)
        
        repair_layout.addWidget(QLabel("الفني المسؤول:"), 3, 0)
        self.technician_combo = QComboBox()
        self.technician_combo.addItem("اختر الفني", None)
        for tech in self.technicians:
            self.technician_combo.addItem(tech['full_name'], tech['id'])
        repair_layout.addWidget(self.technician_combo, 3, 1)
        
        repair_layout.addWidget(QLabel("ملاحظات:"), 4, 0)
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        repair_layout.addWidget(self.notes_edit, 4, 1)
        
        layout.addWidget(repair_group)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_ticket_data(self):
        """تحميل بيانات التذكرة للتعديل"""
        if not self.ticket:
            return
        
        # معلومات العميل
        self.customer_name_edit.setText(self.ticket.get('customer_name', ''))
        self.customer_phone_edit.setText(self.ticket.get('customer_phone', ''))
        
        # معلومات الجهاز
        self.device_info_edit.setText(self.ticket['device_info'])
        self.imei_edit.setText(self.ticket.get('imei', ''))
        
        # معلومات الصيانة
        repair_type = self.ticket['repair_type']
        for i in range(self.repair_type_combo.count()):
            if self.repair_type_combo.itemData(i) == repair_type:
                self.repair_type_combo.setCurrentIndex(i)
                break
        
        self.problem_edit.setPlainText(self.ticket['problem_description'])
        self.estimated_cost_spin.setValue(self.ticket.get('estimated_cost', 0))
        self.notes_edit.setPlainText(self.ticket.get('notes', ''))
        
        # الفني المسؤول
        technician_id = self.ticket.get('technician_id')
        if technician_id:
            for i in range(self.technician_combo.count()):
                if self.technician_combo.itemData(i) == technician_id:
                    self.technician_combo.setCurrentIndex(i)
                    break
    
    def accept_data(self):
        """التحقق من البيانات وقبولها"""
        device_info = self.device_info_edit.text().strip()
        if not device_info:
            QMessageBox.warning(self, "تحذير", "يجب إدخال معلومات الجهاز")
            return
        
        problem = self.problem_edit.toPlainText().strip()
        if not problem:
            QMessageBox.warning(self, "تحذير", "يجب وصف المشكلة")
            return
        
        self.accept()
    
    def get_ticket_data(self):
        """الحصول على بيانات التذكرة"""
        return {
            'customer_info': {
                'name': self.customer_name_edit.text().strip(),
                'phone': self.customer_phone_edit.text().strip(),
                'email': self.customer_email_edit.text().strip()
            },
            'device_info': self.device_info_edit.text().strip(),
            'imei': self.imei_edit.text().strip(),
            'repair_type': self.repair_type_combo.currentData(),
            'problem_description': self.problem_edit.toPlainText().strip(),
            'estimated_cost': self.estimated_cost_spin.value(),
            'technician_id': self.technician_combo.currentData(),
            'notes': self.notes_edit.toPlainText().strip()
        }


class AddPartDialog(QDialog):
    """نافذة إضافة قطعة غيار"""
    
    def __init__(self, parent=None, products=None):
        super().__init__(parent)
        self.products = products or []
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle("إضافة قطعة غيار")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        form_layout = QGridLayout()
        
        # قطعة الغيار
        form_layout.addWidget(QLabel("قطعة الغيار:"), 0, 0)
        self.product_combo = QComboBox()
        self.product_combo.addItem("اختر قطعة الغيار", None)
        for product in self.products:
            if product['quantity_in_stock'] > 0:
                self.product_combo.addItem(
                    f"{product['name']} (متوفر: {product['quantity_in_stock']})",
                    product
                )
        form_layout.addWidget(self.product_combo, 0, 1)
        
        # الكمية
        form_layout.addWidget(QLabel("الكمية:"), 1, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMinimum(1)
        self.quantity_spin.setMaximum(999)
        form_layout.addWidget(self.quantity_spin, 1, 1)
        
        # السعر
        form_layout.addWidget(QLabel("سعر الوحدة:"), 2, 0)
        self.price_spin = QDoubleSpinBox()
        self.price_spin.setMaximum(9999.99)
        self.price_spin.setSuffix(" ر.س")
        form_layout.addWidget(self.price_spin, 2, 1)
        
        layout.addLayout(form_layout)
        
        # ربط إشارات
        self.product_combo.currentTextChanged.connect(self.update_price)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("إضافة")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def update_price(self):
        """تحديث السعر عند اختيار المنتج"""
        product = self.product_combo.currentData()
        if product:
            self.price_spin.setValue(product['selling_price'])
            self.quantity_spin.setMaximum(product['quantity_in_stock'])
    
    def accept_data(self):
        """التحقق من البيانات وقبولها"""
        product = self.product_combo.currentData()
        if not product:
            QMessageBox.warning(self, "تحذير", "يجب اختيار قطعة الغيار")
            return
        
        if self.quantity_spin.value() > product['quantity_in_stock']:
            QMessageBox.warning(self, "تحذير", "الكمية المطلوبة أكبر من المتوفر")
            return
        
        self.accept()
    
    def get_part_data(self):
        """الحصول على بيانات قطعة الغيار"""
        product = self.product_combo.currentData()
        return {
            'product_id': product['id'],
            'quantity': self.quantity_spin.value(),
            'unit_price': self.price_spin.value()
        }


class RepairWindow(QWidget):
    """نافذة إدارة الصيانة"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pdf_generator = PDFGenerator()
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # شريط الأدوات
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # التبويبات
        self.tab_widget = QTabWidget()
        
        # تبويب التذاكر
        tickets_tab = self.create_tickets_tab()
        self.tab_widget.addTab(tickets_tab, "تذاكر الصيانة")
        
        # تبويب إحصائيات الفنيين
        technicians_tab = self.create_technicians_tab()
        self.tab_widget.addTab(technicians_tab, "الفنيون")
        
        # تبويب التقارير
        reports_tab = self.create_reports_tab()
        self.tab_widget.addTab(reports_tab, "التقارير")
        
        layout.addWidget(self.tab_widget)
    
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
        
        # البحث
        search_label = QLabel("البحث:")
        search_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        search_label.setStyleSheet("color: #2c3e50; margin-right: 10px;")
        layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ابحث برقم التذكرة أو اسم العميل أو IMEI...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 14px;
                background-color: white;
                min-width: 300px;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.search_edit.textChanged.connect(self.search_tickets)
        layout.addWidget(self.search_edit)
        
        # فلتر الحالة
        layout.addWidget(QLabel("الحالة:"))
        self.status_filter = QComboBox()
        self.status_filter.addItem("جميع الحالات", None)
        statuses = self.main_window.repair_service.get_repair_statuses()
        for status in statuses:
            status_name = self.main_window.repair_service.get_status_name(status)
            self.status_filter.addItem(status_name, status)
        self.status_filter.currentTextChanged.connect(self.filter_tickets)
        layout.addWidget(self.status_filter)
        
        layout.addStretch()
        
        # أزرار العمل
        new_ticket_btn = QPushButton("تذكرة جديدة")
        new_ticket_btn.setStyleSheet("""
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
        new_ticket_btn.clicked.connect(self.new_ticket)
        layout.addWidget(new_ticket_btn)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        return toolbar
    
    def create_tickets_tab(self):
        """إنشاء تبويب التذاكر"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # جدول التذاكر
        self.tickets_table = QTableWidget()
        self.tickets_table.setColumnCount(9)
        self.tickets_table.setHorizontalHeaderLabels([
            "رقم التذكرة", "العميل", "الجهاز", "النوع", "الحالة", 
            "الفني", "التاريخ", "التكلفة", "العمليات"
        ])
        
        # تخصيص الجدول
        header = self.tickets_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        header.setSectionResizeMode(2, QHeaderView.Stretch)
        
        self.tickets_table.setAlternatingRowColors(True)
        self.tickets_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.tickets_table)
        
        return tab
    
    def create_technicians_tab(self):
        """إنشاء تبويب الفنيين"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # فترة التقرير
        period_frame = QFrame()
        period_frame.setFrameStyle(QFrame.StyledPanel)
        period_layout = QHBoxLayout(period_frame)
        
        period_layout.addWidget(QLabel("من تاريخ:"))
        self.tech_start_date = QDateEdit()
        self.tech_start_date.setDate(QDate.currentDate().addDays(-30))
        self.tech_start_date.setCalendarPopup(True)
        period_layout.addWidget(self.tech_start_date)
        
        period_layout.addWidget(QLabel("إلى تاريخ:"))
        self.tech_end_date = QDateEdit()
        self.tech_end_date.setDate(QDate.currentDate())
        self.tech_end_date.setCalendarPopup(True)
        period_layout.addWidget(self.tech_end_date)
        
        update_stats_btn = QPushButton("تحديث الإحصائيات")
        update_stats_btn.clicked.connect(self.update_technician_stats)
        period_layout.addWidget(update_stats_btn)
        
        period_layout.addStretch()
        
        layout.addWidget(period_frame)
        
        # جدول إحصائيات الفنيين
        self.technicians_table = QTableWidget()
        self.technicians_table.setColumnCount(6)
        self.technicians_table.setHorizontalHeaderLabels([
            "الفني", "إجمالي التذاكر", "المكتملة", "قيد العمل", 
            "متوسط الإنجاز (أيام)", "التحميل الحالي"
        ])
        
        header = self.technicians_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.technicians_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.technicians_table)
        
        return tab
    
    def create_reports_tab(self):
        """إنشاء تبويب التقارير"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # إعدادات التقرير
        settings_frame = QFrame()
        settings_frame.setFrameStyle(QFrame.StyledPanel)
        settings_layout = QGridLayout(settings_frame)
        
        settings_layout.addWidget(QLabel("من تاريخ:"), 0, 0)
        self.report_start_date = QDateEdit()
        self.report_start_date.setDate(QDate.currentDate().addDays(-30))
        self.report_start_date.setCalendarPopup(True)
        settings_layout.addWidget(self.report_start_date, 0, 1)
        
        settings_layout.addWidget(QLabel("إلى تاريخ:"), 0, 2)
        self.report_end_date = QDateEdit()
        self.report_end_date.setDate(QDate.currentDate())
        self.report_end_date.setCalendarPopup(True)
        settings_layout.addWidget(self.report_end_date, 0, 3)
        
        generate_report_btn = QPushButton("إنتاج التقرير")
        generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        generate_report_btn.clicked.connect(self.generate_report)
        settings_layout.addWidget(generate_report_btn, 0, 4)
        
        layout.addWidget(settings_frame)
        
        # ملخص التقرير
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
        
        self.total_tickets_card = self.create_stat_card("إجمالي التذاكر", "0", "#3498db")
        stats_layout.addWidget(self.total_tickets_card, 0, 0)
        
        self.completed_tickets_card = self.create_stat_card("المكتملة", "0", "#27ae60")
        stats_layout.addWidget(self.completed_tickets_card, 0, 1)
        
        self.pending_tickets_card = self.create_stat_card("قيد العمل", "0", "#f39c12")
        stats_layout.addWidget(self.pending_tickets_card, 0, 2)
        
        self.revenue_card = self.create_stat_card("الإيراد", "0 ر.س", "#9b59b6")
        stats_layout.addWidget(self.revenue_card, 0, 3)
        
        summary_layout.addLayout(stats_layout)
        layout.addWidget(summary_frame)
        
        # تفاصيل التقرير
        self.report_details = QTextEdit()
        self.report_details.setReadOnly(True)
        self.report_details.setMaximumHeight(200)
        layout.addWidget(self.report_details)
        
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
        self.load_tickets()
        self.update_technician_stats()
        self.generate_report()
    
    def load_tickets(self):
        """تحميل التذاكر"""
        try:
            tickets = self.main_window.repair_service.get_repair_tickets(limit=100)
            self.display_tickets(tickets)
        except Exception as e:
            logger.error(f"خطأ في تحميل التذاكر: {str(e)}")
    
    def display_tickets(self, tickets):
        """عرض التذاكر في الجدول"""
        self.tickets_table.setRowCount(len(tickets))
        
        for row, ticket in enumerate(tickets):
            # رقم التذكرة
            id_item = QTableWidgetItem(str(ticket['id']))
            id_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 0, id_item)
            
            # العميل
            customer_name = ticket.get('customer_name', 'غير محدد')
            self.tickets_table.setItem(row, 1, QTableWidgetItem(customer_name))
            
            # الجهاز
            self.tickets_table.setItem(row, 2, QTableWidgetItem(ticket['device_info']))
            
            # النوع
            repair_type = self.main_window.repair_service.get_repair_type_name(ticket['repair_type'])
            type_item = QTableWidgetItem(repair_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 3, type_item)
            
            # الحالة
            status_name = self.main_window.repair_service.get_status_name(ticket['status'])
            status_item = QTableWidgetItem(status_name)
            status_item.setTextAlignment(Qt.AlignCenter)
            
            # تلوين الحالة
            status_colors = {
                'received': '#3498db',
                'in_progress': '#f39c12',
                'waiting_parts': '#e67e22',
                'completed': '#27ae60',
                'delivered': '#2c3e50',
                'cancelled': '#e74c3c'
            }
            
            color = status_colors.get(ticket['status'], '#95a5a6')
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor("white"))
            
            self.tickets_table.setItem(row, 4, status_item)
            
            # الفني
            technician_name = ticket.get('technician_name', 'غير محدد')
            self.tickets_table.setItem(row, 5, QTableWidgetItem(technician_name))
            
            # التاريخ
            date_str = ticket['received_date'][:10]  # YYYY-MM-DD
            date_item = QTableWidgetItem(date_str)
            date_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 6, date_item)
            
            # التكلفة
            cost = ticket.get('final_cost') or ticket.get('estimated_cost', 0)
            cost_item = QTableWidgetItem(f"{cost:.2f}")
            cost_item.setTextAlignment(Qt.AlignCenter)
            self.tickets_table.setItem(row, 7, cost_item)
            
            # أزرار العمليات
            operations_widget = self.create_ticket_operations(ticket)
            self.tickets_table.setCellWidget(row, 8, operations_widget)
    
    def create_ticket_operations(self, ticket):
        """إنشاء أزرار العمليات للتذكرة"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # زر التفاصيل
        details_btn = QPushButton("تفاصيل")
        details_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        details_btn.clicked.connect(lambda: self.view_ticket_details(ticket))
        layout.addWidget(details_btn)
        
        # زر تحديث الحالة
        if ticket['status'] not in ['delivered', 'cancelled']:
            status_btn = QPushButton("حالة")
            status_btn.setStyleSheet("""
                QPushButton {
                    background-color: #e67e22;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px 8px;
                    font-size: 10px;
                }
                QPushButton:hover {
                    background-color: #d35400;
                }
            """)
            status_btn.clicked.connect(lambda: self.update_ticket_status(ticket))
            layout.addWidget(status_btn)
        
        # زر الطباعة
        print_btn = QPushButton("طباعة")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 8px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_ticket(ticket))
        layout.addWidget(print_btn)
        
        return widget
    
    def search_tickets(self):
        """البحث عن التذاكر"""
        search_term = self.search_edit.text().strip()
        
        if not search_term:
            self.load_tickets()
            return
        
        try:
            tickets = self.main_window.repair_service.search_repair_tickets(search_term)
            self.display_tickets(tickets)
        except Exception as e:
            logger.error(f"خطأ في البحث: {str(e)}")
    
    def filter_tickets(self):
        """فلترة التذاكر حسب الحالة"""
        status = self.status_filter.currentData()
        
        try:
            tickets = self.main_window.repair_service.get_repair_tickets(
                status=status, limit=100
            )
            self.display_tickets(tickets)
        except Exception as e:
            logger.error(f"خطأ في الفلترة: {str(e)}")
    
    def new_ticket(self):
        """إنشاء تذكرة جديدة"""
        try:
            technicians = self.main_window.repair_service.get_technicians()
            dialog = RepairTicketDialog(self, technicians=technicians)
            
            if dialog.exec() == QDialog.Accepted:
                ticket_data = dialog.get_ticket_data()
                
                ticket_id = self.main_window.repair_service.create_repair_ticket(
                    customer_info=ticket_data['customer_info'],
                    device_info=ticket_data['device_info'],
                    problem_description=ticket_data['problem_description'],
                    repair_type=ticket_data['repair_type'],
                    estimated_cost=ticket_data['estimated_cost'],
                    imei=ticket_data['imei'],
                    technician_id=ticket_data['technician_id'],
                    notes=ticket_data['notes']
                )
                
                if ticket_id:
                    QMessageBox.information(
                        self, "نجح", 
                        f"تم إنشاء التذكرة بنجاح\nرقم التذكرة: {ticket_id}"
                    )
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إنشاء التذكرة")
                    
        except Exception as e:
            logger.error(f"خطأ في إنشاء التذكرة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إنشاء التذكرة:\n{str(e)}")
    
    def view_ticket_details(self, ticket):
        """عرض تفاصيل التذكرة"""
        try:
            # الحصول على التفاصيل الكاملة
            full_ticket = self.main_window.repair_service.get_repair_ticket(ticket['id'])
            
            if not full_ticket:
                QMessageBox.warning(self, "تحذير", "لم يتم العثور على التذكرة")
                return
            
            # إنشاء نافذة التفاصيل
            details_dialog = QDialog(self)
            details_dialog.setWindowTitle(f"تذكرة صيانة #{ticket['id']}")
            details_dialog.setModal(True)
            details_dialog.setFixedSize(600, 500)
            details_dialog.setLayoutDirection(Qt.RightToLeft)
            
            layout = QVBoxLayout(details_dialog)
            
            # معلومات التذكرة
            info_text = f"""
معلومات التذكرة:
رقم التذكرة: {full_ticket['id']}
العميل: {full_ticket.get('customer_name', 'غير محدد')}
هاتف العميل: {full_ticket.get('customer_phone', 'غير محدد')}
الجهاز: {full_ticket['device_info']}
IMEI: {full_ticket.get('imei', 'غير محدد')}
نوع الصيانة: {self.main_window.repair_service.get_repair_type_name(full_ticket['repair_type'])}
الحالة: {self.main_window.repair_service.get_status_name(full_ticket['status'])}
الفني: {full_ticket.get('technician_name', 'غير محدد')}
تاريخ الاستلام: {full_ticket['received_date'][:16]}
التكلفة المقدرة: {full_ticket.get('estimated_cost', 0):.2f} ر.س
التكلفة النهائية: {full_ticket.get('final_cost', 0):.2f} ر.س

وصف المشكلة:
{full_ticket['problem_description']}

ملاحظات:
{full_ticket.get('notes', 'لا توجد ملاحظات')}
            """.strip()
            
            info_label = QLabel(info_text)
            info_label.setWordWrap(True)
            info_label.setStyleSheet("""
                QLabel {
                    background-color: #f8f9fa;
                    padding: 15px;
                    border-radius: 5px;
                    font-family: monospace;
                }
            """)
            layout.addWidget(info_label)
            
            # قطع الغيار المستخدمة
            if full_ticket.get('parts_used'):
                parts_label = QLabel("قطع الغيار المستخدمة:")
                parts_label.setFont(QFont("Arial", 12, QFont.Bold))
                layout.addWidget(parts_label)
                
                parts_table = QTableWidget()
                parts_table.setColumnCount(4)
                parts_table.setHorizontalHeaderLabels(["القطعة", "الكمية", "السعر", "المجموع"])
                parts_table.setRowCount(len(full_ticket['parts_used']))
                
                for row, part in enumerate(full_ticket['parts_used']):
                    parts_table.setItem(row, 0, QTableWidgetItem(part.get('product_name', '')))
                    parts_table.setItem(row, 1, QTableWidgetItem(str(part['quantity'])))
                    parts_table.setItem(row, 2, QTableWidgetItem(f"{part['unit_price']:.2f}"))
                    parts_table.setItem(row, 3, QTableWidgetItem(f"{part['total_price']:.2f}"))
                
                parts_table.setMaximumHeight(150)
                layout.addWidget(parts_table)
            
            # أزرار العمل
            buttons_layout = QHBoxLayout()
            
            # زر إضافة قطعة غيار
            if full_ticket['status'] in ['received', 'in_progress', 'waiting_parts']:
                add_part_btn = QPushButton("إضافة قطعة غيار")
                add_part_btn.clicked.connect(lambda: self.add_part_to_ticket(full_ticket['id']))
                buttons_layout.addWidget(add_part_btn)
            
            # زر تحديث الحالة
            if full_ticket['status'] not in ['delivered', 'cancelled']:
                update_status_btn = QPushButton("تحديث الحالة")
                update_status_btn.clicked.connect(lambda: self.update_ticket_status(full_ticket))
                buttons_layout.addWidget(update_status_btn)
            
            # زر الطباعة
            print_btn = QPushButton("طباعة")
            print_btn.clicked.connect(lambda: self.print_ticket(full_ticket))
            buttons_layout.addWidget(print_btn)
            
            # زر الإغلاق
            close_btn = QPushButton("إغلاق")
            close_btn.clicked.connect(details_dialog.close)
            buttons_layout.addWidget(close_btn)
            
            layout.addLayout(buttons_layout)
            
            details_dialog.exec()
            
        except Exception as e:
            logger.error(f"خطأ في عرض تفاصيل التذكرة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في عرض التفاصيل:\n{str(e)}")
    
    def update_ticket_status(self, ticket):
        """تحديث حالة التذكرة"""
        try:
            # إنشاء نافذة تحديث الحالة
            dialog = QDialog(self)
            dialog.setWindowTitle(f"تحديث حالة التذكرة #{ticket['id']}")
            dialog.setModal(True)
            dialog.setFixedSize(400, 300)
            dialog.setLayoutDirection(Qt.RightToLeft)
            
            layout = QVBoxLayout(dialog)
            
            form_layout = QGridLayout()
            
            # الحالة الجديدة
            form_layout.addWidget(QLabel("الحالة الجديدة:"), 0, 0)
            status_combo = QComboBox()
            statuses = self.main_window.repair_service.get_repair_statuses()
            for status in statuses:
                if status != ticket['status']:  # لا نعرض الحالة الحالية
                    status_name = self.main_window.repair_service.get_status_name(status)
                    status_combo.addItem(status_name, status)
            form_layout.addWidget(status_combo, 0, 1)
            
            # التكلفة النهائية
            form_layout.addWidget(QLabel("التكلفة النهائية:"), 1, 0)
            final_cost_spin = QDoubleSpinBox()
            final_cost_spin.setMaximum(99999.99)
            final_cost_spin.setSuffix(" ر.س")
            final_cost_spin.setValue(ticket.get('final_cost') or ticket.get('estimated_cost', 0))
            form_layout.addWidget(final_cost_spin, 1, 1)
            
            # ملاحظات
            form_layout.addWidget(QLabel("ملاحظات:"), 2, 0)
            notes_edit = QTextEdit()
            notes_edit.setMaximumHeight(80)
            form_layout.addWidget(notes_edit, 2, 1)
            
            layout.addLayout(form_layout)
            
            # أزرار العمل
            buttons = QDialogButtonBox(
                QDialogButtonBox.Save | QDialogButtonBox.Cancel
            )
            buttons.button(QDialogButtonBox.Save).setText("حفظ")
            buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)
            
            if dialog.exec() == QDialog.Accepted:
                new_status = status_combo.currentData()
                final_cost = final_cost_spin.value()
                notes = notes_edit.toPlainText().strip()
                
                success = self.main_window.repair_service.update_ticket_status(
                    ticket['id'], new_status, final_cost, notes
                )
                
                if success:
                    QMessageBox.information(self, "نجح", "تم تحديث حالة التذكرة بنجاح")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في تحديث حالة التذكرة")
                    
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة التذكرة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تحديث الحالة:\n{str(e)}")
    
    def add_part_to_ticket(self, ticket_id):
        """إضافة قطعة غيار للتذكرة"""
        try:
            products = self.main_window.inventory_service.get_all_products()
            # فلترة المنتجات لإظهار قطع الغيار فقط
            spare_parts = [p for p in products if 'قطع غيار' in p.get('category_name', '')]
            
            if not spare_parts:
                spare_parts = products  # إذا لم توجد فئة قطع غيار، اعرض جميع المنتجات
            
            dialog = AddPartDialog(self, spare_parts)
            
            if dialog.exec() == QDialog.Accepted:
                part_data = dialog.get_part_data()
                
                success = self.main_window.repair_service.add_repair_part(
                    ticket_id,
                    part_data['product_id'],
                    part_data['quantity'],
                    part_data['unit_price']
                )
                
                if success:
                    QMessageBox.information(self, "نجح", "تم إضافة قطعة الغيار بنجاح")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إضافة قطعة الغيار")
                    
        except Exception as e:
            logger.error(f"خطأ في إضافة قطعة الغيار: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إضافة قطعة الغيار:\n{str(e)}")
    
    def print_ticket(self, ticket):
        """طباعة التذكرة"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"repair_ticket_{ticket['id']}_{timestamp}.pdf"
            filepath = f"reports/daily/{filename}"
            
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            import os
            os.makedirs("reports/daily", exist_ok=True)
            
            # إنتاج تذكرة PDF
            success = self.pdf_generator.generate_repair_ticket(ticket, filepath)
            
            if success:
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ التذكرة في:\n{filepath}"
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
                    "فشل في إنتاج ملف PDF للتذكرة"
                )
                
        except Exception as e:
            logger.error(f"خطأ في طباعة التذكرة: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في طباعة التذكرة:\n{str(e)}"
            )
    
    def update_technician_stats(self):
        """تحديث إحصائيات الفنيين"""
        try:
            start_date = self.tech_start_date.date().toString("yyyy-MM-dd")
            end_date = self.tech_end_date.date().toString("yyyy-MM-dd")
            
            technicians = self.main_window.repair_service.get_technicians()
            self.technicians_table.setRowCount(len(technicians))
            
            for row, tech in enumerate(technicians):
                # اسم الفني
                self.technicians_table.setItem(row, 0, QTableWidgetItem(tech['full_name']))
                
                # إحصائيات الفني
                stats = self.main_window.repair_service.get_technician_stats(
                    tech['id'], start_date, end_date
                )
                
                # إجمالي التذاكر
                total_item = QTableWidgetItem(str(stats.get('total_tickets', 0)))
                total_item.setTextAlignment(Qt.AlignCenter)
                self.technicians_table.setItem(row, 1, total_item)
                
                # المكتملة
                completed_item = QTableWidgetItem(str(stats.get('completed_tickets', 0)))
                completed_item.setTextAlignment(Qt.AlignCenter)
                self.technicians_table.setItem(row, 2, completed_item)
                
                # قيد العمل
                workload = self.main_window.repair_service.get_technician_workload(tech['id'])
                in_progress = workload.get('in_progress_count', 0) + workload.get('received_count', 0)
                progress_item = QTableWidgetItem(str(in_progress))
                progress_item.setTextAlignment(Qt.AlignCenter)
                self.technicians_table.setItem(row, 3, progress_item)
                
                # متوسط الإنجاز
                avg_days = stats.get('avg_completion_days', 0) or 0
                avg_item = QTableWidgetItem(f"{avg_days:.1f}")
                avg_item.setTextAlignment(Qt.AlignCenter)
                self.technicians_table.setItem(row, 4, avg_item)
                
                # التحميل الحالي
                workload_widget = self.create_workload_widget(workload)
                self.technicians_table.setCellWidget(row, 5, workload_widget)
                
        except Exception as e:
            logger.error(f"خطأ في تحديث إحصائيات الفنيين: {str(e)}")
    
    def create_workload_widget(self, workload):
        """إنشاء ويدجت عبء العمل"""
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # شريط التقدم
        progress = QProgressBar()
        total_load = (workload.get('received_count', 0) + 
                     workload.get('in_progress_count', 0) + 
                     workload.get('waiting_parts_count', 0))
        
        # تحديد الحد الأقصى (افتراضياً 10 تذاكر)
        max_load = 10
        progress.setMaximum(max_load)
        progress.setValue(min(total_load, max_load))
        
        # تلوين حسب العبء
        if total_load <= 3:
            color = "#27ae60"  # أخضر - عبء قليل
        elif total_load <= 7:
            color = "#f39c12"  # برتقالي - عبء متوسط
        else:
            color = "#e74c3c"  # أحمر - عبء عالي
        
        progress.setStyleSheet(f"""
            QProgressBar {{
                border: 1px solid #ccc;
                border-radius: 3px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                background-color: {color};
            }}
        """)
        
        layout.addWidget(progress)
        
        # نص التفاصيل
        details = QLabel(f"{total_load} تذكرة")
        details.setAlignment(Qt.AlignCenter)
        details.setFont(QFont("Arial", 9))
        layout.addWidget(details)
        
        return widget
    
    def generate_report(self):
        """إنتاج تقرير الصيانة"""
        try:
            start_date = self.report_start_date.date().toString("yyyy-MM-dd")
            end_date = self.report_end_date.date().toString("yyyy-MM-dd")
            
            # الحصول على بيانات التقرير
            report_data = self.main_window.report_service.get_repair_report(start_date, end_date)
            
            # تحديث البطاقات
            summary = report_data.get('summary', {})
            self.total_tickets_card.value_label.setText(str(summary.get('total_tickets', 0)))
            self.completed_tickets_card.value_label.setText(str(summary.get('completed_tickets', 0)))
            self.pending_tickets_card.value_label.setText(str(summary.get('in_progress_tickets', 0)))
            
            revenue = summary.get('total_revenue', 0)
            self.revenue_card.value_label.setText(f"{revenue:.0f} ر.س")
            
            # تحديث تفاصيل التقرير
            details_text = f"""
تقرير الصيانة من {start_date} إلى {end_date}

الملخص العام:
- إجمالي التذاكر: {summary.get('total_tickets', 0)}
- التذاكر المكتملة: {summary.get('completed_tickets', 0)}
- التذاكر قيد العمل: {summary.get('in_progress_tickets', 0)}
- التذاكر المسلمة: {summary.get('delivered_tickets', 0)}
- إجمالي الإيراد: {summary.get('total_revenue', 0):.2f} ر.س
- متوسط مدة الإنجاز: {summary.get('avg_completion_days', 0):.1f} يوم

الصيانة حسب النوع:
"""
            
            for type_data in report_data.get('by_type', []):
                repair_type = self.main_window.repair_service.get_repair_type_name(type_data['repair_type'])
                details_text += f"- {repair_type}: {type_data['ticket_count']} تذكرة، إيراد: {type_data.get('total_revenue', 0):.2f} ر.س\n"
            
            details_text += "\nأداء الفنيين:\n"
            for tech_data in report_data.get('technician_performance', []):
                details_text += f"- {tech_data['technician_name']}: {tech_data['total_tickets']} تذكرة، مكتمل: {tech_data['completed_tickets']}\n"
            
            self.report_details.setText(details_text.strip())
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج التقرير: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إنتاج التقرير:\n{str(e)}")
