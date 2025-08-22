#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة نقاط البيع - POS Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QSpinBox,
                              QDoubleSpinBox, QTextEdit, QFrame, QGroupBox,
                              QMessageBox, QDialog, QDialogButtonBox,
                              QCompleter, QHeaderView, QAbstractItemView)
from PySide6.QtCore import Qt, QStringListModel, Signal
from PySide6.QtGui import QFont, QDoubleValidator, QIntValidator , QColor
from datetime import datetime
import logging

from app.utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class CustomerDialog(QDialog):
    """نافذة بيانات العميل"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.customer_data = {}
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle("بيانات العميل")
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # حقول البيانات
        form_layout = QGridLayout()
        
        # الاسم
        form_layout.addWidget(QLabel("الاسم:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)
        
        # الهاتف
        form_layout.addWidget(QLabel("رقم الهاتف:"), 1, 0)
        self.phone_edit = QLineEdit()
        form_layout.addWidget(self.phone_edit, 1, 1)
        
        # البريد الإلكتروني
        form_layout.addWidget(QLabel("البريد الإلكتروني:"), 2, 0)
        self.email_edit = QLineEdit()
        form_layout.addWidget(self.email_edit, 2, 1)
        
        # العنوان
        form_layout.addWidget(QLabel("العنوان:"), 3, 0)
        self.address_edit = QTextEdit()
        self.address_edit.setMaximumHeight(80)
        form_layout.addWidget(self.address_edit, 3, 1)
        
        layout.addLayout(form_layout)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Ok | QDialogButtonBox.Cancel
        )
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept_data(self):
        """قبول البيانات"""
        self.customer_data = {
            'name': self.name_edit.text().strip(),
            'phone': self.phone_edit.text().strip(),
            'email': self.email_edit.text().strip(),
            'address': self.address_edit.toPlainText().strip()
        }
        self.accept()
    
    def get_customer_data(self):
        """الحصول على بيانات العميل"""
        return self.customer_data


class POSWindow(QWidget):
    """نافذة نقاط البيع"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.cart_items = []
        self.current_customer = None
        self.pdf_generator = PDFGenerator()
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QHBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(10)
        
        # الجانب الأيسر - البحث والمنتجات
        left_panel = self.create_left_panel()
        layout.addWidget(left_panel, 1)
        
        # الجانب الأيمن - السلة والدفع
        right_panel = self.create_right_panel()
        layout.addWidget(right_panel, 1)
    
    def create_left_panel(self):
        """إنشاء اللوحة اليسرى"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.NoFrame)
        panel.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1: 0, y1: 0, x2: 0, y2: 1,
                    stop: 0 #ffffff, stop: 1 #f8f9fa);
                border-radius: 20px;
                padding: 25px;
                border: 2px solid #e9ecef;
                box-shadow: 0 6px 12px rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(25, 25, 25, 25)
        layout.setSpacing(20)
        
        # عنوان القسم
        title = QLabel("البحث عن المنتجات")
        title.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 20px;
            padding: 15px;
            background-color: #ecf0f1;
            border-radius: 10px;
            border-left: 5px solid #3498db;
        """)
        layout.addWidget(title)
        
        # شريط البحث
        search_layout = QHBoxLayout()
        search_layout.setSpacing(15)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ابحث بالاسم أو الباركود...")
        self.search_edit.setStyleSheet("""
            QLineEdit {
                padding: 12px 15px;
                border: 2px solid #bdc3c7;
                border-radius: 10px;
                font-size: 14px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 2px solid #3498db;
                background-color: #f8f9fa;
            }
        """)
        self.search_edit.textChanged.connect(self.search_products)
        search_layout.addWidget(self.search_edit)
        
        search_button = QPushButton("بحث")
        search_button.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 10px;
                padding: 12px 20px;
                font-weight: bold;
                font-size: 14px;
                min-width: 80px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
            QPushButton:pressed {
                background-color: #1f4e79;
            }
        """)
        search_button.clicked.connect(self.search_products)
        search_layout.addWidget(search_button)
        
        layout.addLayout(search_layout)
        
        # جدول المنتجات
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(5)
        self.products_table.setHorizontalHeaderLabels([
            "الاسم", "الفئة", "السعر", "المخزون", "إضافة"
        ])
        
        # تخصيص الجدول
        header = self.products_table.horizontalHeader()
        header.setStretchLastSection(False)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        header.setSectionResizeMode(1, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(2, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(3, QHeaderView.ResizeToContents)
        header.setSectionResizeMode(4, QHeaderView.ResizeToContents)
        
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        self.products_table.setAlternatingRowColors(True)
        layout.addWidget(self.products_table)
        
        return panel
    
    def create_right_panel(self):
        """إنشاء اللوحة اليمنى"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 10px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # عنوان القسم
        title = QLabel("السلة والدفع")
        title.setFont(QFont("Arial", 16, QFont.Bold))
        title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        layout.addWidget(title)
        
        # معلومات العميل
        customer_group = QGroupBox("معلومات العميل")
        customer_layout = QHBoxLayout(customer_group)
        
        self.customer_label = QLabel("لا يوجد عميل محدد")
        customer_layout.addWidget(self.customer_label)
        
        customer_button = QPushButton("اختيار عميل")
        customer_button.clicked.connect(self.select_customer)
        customer_layout.addWidget(customer_button)
        
        layout.addWidget(customer_group)
        
        # جدول السلة
        self.cart_table = QTableWidget()
        self.cart_table.setColumnCount(6)
        self.cart_table.setHorizontalHeaderLabels([
            "المنتج", "السعر", "الكمية", "المجموع", "حذف", ""
        ])
        
        # تخصيص جدول السلة
        cart_header = self.cart_table.horizontalHeader()
        cart_header.setStretchLastSection(True)
        cart_header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.cart_table.setAlternatingRowColors(True)
        layout.addWidget(self.cart_table)
        
        # ملخص الفاتورة
        summary_group = QGroupBox("ملخص الفاتورة")
        summary_layout = QGridLayout(summary_group)
        
        # المجموع الفرعي
        summary_layout.addWidget(QLabel("المجموع الفرعي:"), 0, 0)
        self.subtotal_label = QLabel("0.00 ر.س")
        self.subtotal_label.setAlignment(Qt.AlignLeft)
        summary_layout.addWidget(self.subtotal_label, 0, 1)
        
        # الخصم
        summary_layout.addWidget(QLabel("الخصم:"), 1, 0)
        self.discount_spin = QDoubleSpinBox()
        self.discount_spin.setMaximum(9999.99)
        self.discount_spin.setSuffix(" ر.س")
        self.discount_spin.valueChanged.connect(self.calculate_total)
        summary_layout.addWidget(self.discount_spin, 1, 1)
        
        # الضريبة
        summary_layout.addWidget(QLabel("الضريبة:"), 2, 0)
        self.tax_label = QLabel("0.00 ر.س")
        self.tax_label.setAlignment(Qt.AlignLeft)
        summary_layout.addWidget(self.tax_label, 2, 1)
        
        # المجموع النهائي
        summary_layout.addWidget(QLabel("المجموع النهائي:"), 3, 0)
        self.total_label = QLabel("0.00 ر.س")
        self.total_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.total_label.setStyleSheet("color: #27ae60;")
        self.total_label.setAlignment(Qt.AlignLeft)
        summary_layout.addWidget(self.total_label, 3, 1)
        
        layout.addWidget(summary_group)
        
        # طريقة الدفع
        payment_group = QGroupBox("طريقة الدفع")
        payment_layout = QVBoxLayout(payment_group)
        
        self.payment_combo = QComboBox()
        payment_methods = self.main_window.pos_service.get_payment_methods()
        for method in payment_methods:
            self.payment_combo.addItem(
                self.main_window.pos_service.get_payment_method_name(method),
                method
            )
        payment_layout.addWidget(self.payment_combo)
        
        layout.addWidget(payment_group)
        
        # ملاحظات
        notes_group = QGroupBox("ملاحظات")
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setMaximumHeight(80)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        
        clear_button = QPushButton("مسح الكل")
        clear_button.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        clear_button.clicked.connect(self.clear_cart)
        buttons_layout.addWidget(clear_button)
        
        self.complete_button = QPushButton("إتمام البيع")
        self.complete_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        self.complete_button.clicked.connect(self.complete_sale)
        self.complete_button.setEnabled(False)
        buttons_layout.addWidget(self.complete_button)
        
        layout.addLayout(buttons_layout)
        
        return panel
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_products()
        self.clear_cart()
    
    def load_products(self):
        """تحميل المنتجات"""
        try:
            products = self.main_window.inventory_service.get_all_products()
            self.display_products(products)
        except Exception as e:
            logger.error(f"خطأ في تحميل المنتجات: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المنتجات:\n{str(e)}")
    
    def display_products(self, products):
        """عرض المنتجات في الجدول"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # الاسم
            self.products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # الفئة
            category_name = product.get('category_name', 'غير مصنف')
            self.products_table.setItem(row, 1, QTableWidgetItem(category_name))
            
            # السعر
            price_item = QTableWidgetItem(f"{product['selling_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 2, price_item)
            
            # المخزون
            stock_item = QTableWidgetItem(str(product['quantity_in_stock']))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # تلوين المخزون حسب الحالة
            if product['quantity_in_stock'] == 0:
                stock_item.setBackground(QColor("#e74c3c"))
                stock_item.setForeground(QColor("white"))
            elif product['quantity_in_stock'] <= product['minimum_stock']:
                stock_item.setBackground(QColor("#f39c12"))
                stock_item.setForeground(QColor("white"))
            
            self.products_table.setItem(row, 3, stock_item)
            
            # زر الإضافة
            add_button = QPushButton("إضافة")
            add_button.setEnabled(product['quantity_in_stock'] > 0)
            add_button.clicked.connect(
                lambda checked, p=product: self.add_to_cart(p)
            )
            self.products_table.setCellWidget(row, 4, add_button)
    
    def search_products(self):
        """البحث عن المنتجات"""
        search_term = self.search_edit.text().strip()
        
        if not search_term:
            self.load_products()
            return
        
        try:
            products = self.main_window.inventory_service.search_products(search_term)
            self.display_products(products)
        except Exception as e:
            logger.error(f"خطأ في البحث: {str(e)}")
    
    def add_to_cart(self, product):
        """إضافة منتج للسلة"""
        # التحقق من وجود المنتج في السلة
        for item in self.cart_items:
            if item['product_id'] == product['id']:
                if item['quantity'] < product['quantity_in_stock']:
                    item['quantity'] += 1
                    self.update_cart_display()
                    return
                else:
                    QMessageBox.warning(
                        self, "تحذير",
                        "الكمية المطلوبة تتجاوز المخزون المتاح"
                    )
                    return
        
        # إضافة منتج جديد للسلة
        cart_item = {
            'product_id': product['id'],
            'name': product['name'],
            'price': product['selling_price'],
            'quantity': 1,
            'max_quantity': product['quantity_in_stock']
        }
        
        self.cart_items.append(cart_item)
        self.update_cart_display()
    
    def update_cart_display(self):
        """تحديث عرض السلة"""
        self.cart_table.setRowCount(len(self.cart_items))
        
        for row, item in enumerate(self.cart_items):
            # اسم المنتج
            self.cart_table.setItem(row, 0, QTableWidgetItem(item['name']))
            
            # السعر
            price_item = QTableWidgetItem(f"{item['price']:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 1, price_item)
            
            # الكمية
            quantity_spin = QSpinBox()
            quantity_spin.setMinimum(1)
            quantity_spin.setMaximum(item['max_quantity'])
            quantity_spin.setValue(item['quantity'])
            quantity_spin.valueChanged.connect(
                lambda value, r=row: self.update_quantity(r, value)
            )
            self.cart_table.setCellWidget(row, 2, quantity_spin)
            
            # المجموع
            total = item['price'] * item['quantity']
            total_item = QTableWidgetItem(f"{total:.2f}")
            total_item.setTextAlignment(Qt.AlignCenter)
            self.cart_table.setItem(row, 3, total_item)
            
            # زر الحذف
            delete_button = QPushButton("حذف")
            delete_button.setStyleSheet("""
                QPushButton {
                    background-color: #e74c3c;
                    color: white;
                    border: none;
                    border-radius: 3px;
                    padding: 5px;
                }
                QPushButton:hover {
                    background-color: #c0392b;
                }
            """)
            delete_button.clicked.connect(
                lambda checked, r=row: self.remove_from_cart(r)
            )
            self.cart_table.setCellWidget(row, 4, delete_button)
        
        self.calculate_total()
    
    def update_quantity(self, row, quantity):
        """تحديث كمية المنتج"""
        if row < len(self.cart_items):
            self.cart_items[row]['quantity'] = quantity
            self.update_cart_display()
    
    def remove_from_cart(self, row):
        """حذف منتج من السلة"""
        if row < len(self.cart_items):
            del self.cart_items[row]
            self.update_cart_display()
    
    def calculate_total(self):
        """حساب الإجمالي"""
        if not self.cart_items:
            self.subtotal_label.setText("0.00 ر.س")
            self.tax_label.setText("0.00 ر.س")
            self.total_label.setText("0.00 ر.س")
            self.complete_button.setEnabled(False)
            return
        
        # حساب المجموع الفرعي
        subtotal = sum(item['price'] * item['quantity'] for item in self.cart_items)
        
        # الخصم
        discount = self.discount_spin.value()
        
        # حساب الضريبة
        taxable_amount = subtotal - discount
        tax_rate = float(self.main_window.db.get_setting('tax_rate') or 0) / 100
        tax_amount = taxable_amount * tax_rate
        
        # المجموع النهائي
        total = taxable_amount + tax_amount
        
        # تحديث العرض
        self.subtotal_label.setText(f"{subtotal:.2f} ر.س")
        self.tax_label.setText(f"{tax_amount:.2f} ر.س")
        self.total_label.setText(f"{total:.2f} ر.س")
        
        # تفعيل زر الإتمام
        self.complete_button.setEnabled(total > 0)
    
    def select_customer(self):
        """اختيار العميل"""
        dialog = CustomerDialog(self)
        if dialog.exec() == QDialog.Accepted:
            customer_data = dialog.get_customer_data()
            if customer_data['name'] or customer_data['phone']:
                self.current_customer = customer_data
                display_text = customer_data['name'] or customer_data['phone']
                self.customer_label.setText(f"العميل: {display_text}")
            else:
                self.current_customer = None
                self.customer_label.setText("لا يوجد عميل محدد")
    
    def clear_cart(self):
        """مسح السلة"""
        self.cart_items.clear()
        self.current_customer = None
        self.customer_label.setText("لا يوجد عميل محدد")
        self.discount_spin.setValue(0)
        self.notes_edit.clear()
        self.update_cart_display()
    
    def complete_sale(self):
        """إتمام البيع"""
        if not self.cart_items:
            QMessageBox.warning(self, "تحذير", "السلة فارغة")
            return
        
        try:
            # إعداد بيانات الفاتورة
            items = []
            for cart_item in self.cart_items:
                items.append({
                    'product_id': cart_item['product_id'],
                    'quantity': cart_item['quantity'],
                    'price': cart_item['price']
                })
            
            payment_method = self.payment_combo.currentData()
            discount_amount = self.discount_spin.value()
            notes = self.notes_edit.toPlainText().strip()
            
            # إنشاء الفاتورة
            sale = self.main_window.pos_service.create_sale(
                items=items,
                payment_method=payment_method,
                customer_info=self.current_customer,
                discount_amount=discount_amount,
                notes=notes
            )
            
            if sale:
                QMessageBox.information(
                    self, "نجح",
                    f"تم إنشاء الفاتورة بنجاح\nرقم الفاتورة: {sale['id']}"
                )
                
                # عرض خيارات الطباعة
                reply = QMessageBox.question(
                    self, "طباعة الفاتورة",
                    "هل تريد طباعة الفاتورة؟",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    self.print_invoice(sale)
                
                # مسح السلة
                self.clear_cart()
                
                # تحديث المنتجات
                self.load_products()
                
            else:
                QMessageBox.critical(
                    self, "خطأ",
                    "فشل في إنشاء الفاتورة"
                )
                
        except Exception as e:
            logger.error(f"خطأ في إتمام البيع: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في إتمام البيع:\n{str(e)}"
            )
    
    def print_invoice(self, sale):
        """طباعة الفاتورة"""
        try:
            # إنشاء ملف PDF
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"invoice_{sale['id']}_{timestamp}.pdf"
            filepath = f"reports/daily/{filename}"
            
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            import os
            os.makedirs("reports/daily", exist_ok=True)
            
            # إنتاج الفاتورة
            success = self.pdf_generator.generate_invoice(sale, filepath)
            
            if success:
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ الفاتورة في:\n{filepath}"
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
                    "فشل في إنتاج ملف PDF للفاتورة"
                )
                
        except Exception as e:
            logger.error(f"خطأ في طباعة الفاتورة: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في طباعة الفاتورة:\n{str(e)}"
            )
