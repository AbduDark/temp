#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة إدارة المخزون - Inventory Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QSpinBox,
                              QDoubleSpinBox, QTextEdit, QFrame, QGroupBox,
                              QMessageBox, QDialog, QDialogButtonBox,
                              QTabWidget, QHeaderView, QAbstractItemView,
                              QProgressBar, QSplitter)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class ProductDialog(QDialog):
    """نافذة إضافة/تعديل منتج"""
    
    def __init__(self, parent=None, product=None, categories=None):
        super().__init__(parent)
        self.product = product
        self.categories = categories or []
        self.setup_ui()
        
        if product:
            self.load_product_data()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        title = "تعديل منتج" if self.product else "إضافة منتج جديد"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(500, 600)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # نموذج البيانات
        form_layout = QGridLayout()
        
        # اسم المنتج
        form_layout.addWidget(QLabel("اسم المنتج:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)
        
        # الباركود
        form_layout.addWidget(QLabel("الباركود:"), 1, 0)
        self.barcode_edit = QLineEdit()
        form_layout.addWidget(self.barcode_edit, 1, 1)
        
        # الفئة
        form_layout.addWidget(QLabel("الفئة:"), 2, 0)
        self.category_combo = QComboBox()
        self.category_combo.addItem("اختر الفئة", None)
        for category in self.categories:
            self.category_combo.addItem(category['name'], category['id'])
        form_layout.addWidget(self.category_combo, 2, 1)
        
        # سعر التكلفة
        form_layout.addWidget(QLabel("سعر التكلفة:"), 3, 0)
        self.cost_price_spin = QDoubleSpinBox()
        self.cost_price_spin.setMaximum(999999.99)
        self.cost_price_spin.setSuffix(" ر.س")
        form_layout.addWidget(self.cost_price_spin, 3, 1)
        
        # سعر البيع
        form_layout.addWidget(QLabel("سعر البيع:"), 4, 0)
        self.selling_price_spin = QDoubleSpinBox()
        self.selling_price_spin.setMaximum(999999.99)
        self.selling_price_spin.setSuffix(" ر.س")
        form_layout.addWidget(self.selling_price_spin, 4, 1)
        
        # الكمية في المخزون
        form_layout.addWidget(QLabel("الكمية في المخزون:"), 5, 0)
        self.quantity_spin = QSpinBox()
        self.quantity_spin.setMaximum(999999)
        form_layout.addWidget(self.quantity_spin, 5, 1)
        
        # الحد الأدنى للمخزون
        form_layout.addWidget(QLabel("الحد الأدنى للمخزون:"), 6, 0)
        self.min_stock_spin = QSpinBox()
        self.min_stock_spin.setMaximum(999)
        self.min_stock_spin.setValue(5)
        form_layout.addWidget(self.min_stock_spin, 6, 1)
        
        # الوصف
        form_layout.addWidget(QLabel("الوصف:"), 7, 0)
        self.description_edit = QTextEdit()
        self.description_edit.setMaximumHeight(100)
        form_layout.addWidget(self.description_edit, 7, 1)
        
        layout.addLayout(form_layout)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_product_data(self):
        """تحميل بيانات المنتج للتعديل"""
        if not self.product:
            return
        
        self.name_edit.setText(self.product['name'])
        self.barcode_edit.setText(self.product.get('barcode', ''))
        self.cost_price_spin.setValue(self.product.get('cost_price', 0))
        self.selling_price_spin.setValue(self.product['selling_price'])
        self.quantity_spin.setValue(self.product['quantity_in_stock'])
        self.min_stock_spin.setValue(self.product['minimum_stock'])
        self.description_edit.setPlainText(self.product.get('description', ''))
        
        # تحديد الفئة
        category_id = self.product.get('category_id')
        if category_id:
            for i in range(self.category_combo.count()):
                if self.category_combo.itemData(i) == category_id:
                    self.category_combo.setCurrentIndex(i)
                    break
    
    def accept_data(self):
        """التحقق من البيانات وقبولها"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم المنتج")
            return
        
        selling_price = self.selling_price_spin.value()
        if selling_price <= 0:
            QMessageBox.warning(self, "تحذير", "يجب إدخال سعر بيع صحيح")
            return
        
        category_id = self.category_combo.currentData()
        if not category_id:
            QMessageBox.warning(self, "تحذير", "يجب اختيار فئة المنتج")
            return
        
        self.accept()
    
    def get_product_data(self):
        """الحصول على بيانات المنتج"""
        return {
            'name': self.name_edit.text().strip(),
            'barcode': self.barcode_edit.text().strip(),
            'category_id': self.category_combo.currentData(),
            'cost_price': self.cost_price_spin.value(),
            'selling_price': self.selling_price_spin.value(),
            'quantity': self.quantity_spin.value(),
            'minimum_stock': self.min_stock_spin.value(),
            'description': self.description_edit.toPlainText().strip()
        }


class CategoryDialog(QDialog):
    """نافذة إضافة فئة جديدة"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle("إضافة فئة جديدة")
        self.setModal(True)
        self.setFixedSize(400, 200)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # نموذج البيانات
        form_layout = QGridLayout()
        
        # اسم الفئة
        form_layout.addWidget(QLabel("اسم الفئة:"), 0, 0)
        self.name_edit = QLineEdit()
        form_layout.addWidget(self.name_edit, 0, 1)
        
        # الوصف
        form_layout.addWidget(QLabel("الوصف:"), 1, 0)
        self.description_edit = QLineEdit()
        form_layout.addWidget(self.description_edit, 1, 1)
        
        layout.addLayout(form_layout)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def accept_data(self):
        """التحقق من البيانات وقبولها"""
        name = self.name_edit.text().strip()
        if not name:
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم الفئة")
            return
        
        self.accept()
    
    def get_category_data(self):
        """الحصول على بيانات الفئة"""
        return {
            'name': self.name_edit.text().strip(),
            'description': self.description_edit.text().strip()
        }


class StockAdjustmentDialog(QDialog):
    """نافذة تعديل المخزون"""
    
    def __init__(self, parent=None, product=None):
        super().__init__(parent)
        self.product = product
        self.setup_ui()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle(f"تعديل مخزون: {self.product['name']}")
        self.setModal(True)
        self.setFixedSize(400, 250)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # معلومات المنتج
        info_frame = QFrame()
        info_frame.setFrameStyle(QFrame.StyledPanel)
        info_layout = QGridLayout(info_frame)
        
        info_layout.addWidget(QLabel("المنتج:"), 0, 0)
        info_layout.addWidget(QLabel(self.product['name']), 0, 1)
        
        info_layout.addWidget(QLabel("المخزون الحالي:"), 1, 0)
        current_stock = QLabel(str(self.product['quantity_in_stock']))
        current_stock.setStyleSheet("font-weight: bold; color: #2c3e50;")
        info_layout.addWidget(current_stock, 1, 1)
        
        layout.addWidget(info_frame)
        
        # تعديل المخزون
        adjustment_layout = QGridLayout()
        
        adjustment_layout.addWidget(QLabel("الكمية الجديدة:"), 0, 0)
        self.new_quantity_spin = QSpinBox()
        self.new_quantity_spin.setMaximum(999999)
        self.new_quantity_spin.setValue(self.product['quantity_in_stock'])
        adjustment_layout.addWidget(self.new_quantity_spin, 0, 1)
        
        adjustment_layout.addWidget(QLabel("سبب التعديل:"), 1, 0)
        self.reason_edit = QLineEdit()
        self.reason_edit.setPlaceholderText("اختياري...")
        adjustment_layout.addWidget(self.reason_edit, 1, 1)
        
        layout.addLayout(adjustment_layout)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def get_adjustment_data(self):
        """الحصول على بيانات التعديل"""
        return {
            'new_quantity': self.new_quantity_spin.value(),
            'reason': self.reason_edit.text().strip()
        }


class InventoryWindow(QWidget):
    """نافذة إدارة المخزون"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
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
        
        # تبويب المنتجات
        products_tab = self.create_products_tab()
        self.tab_widget.addTab(products_tab, "المنتجات")
        
        # تبويب المخزون المنخفض
        low_stock_tab = self.create_low_stock_tab()
        self.tab_widget.addTab(low_stock_tab, "مخزون منخفض")
        
        # تبويب حركة المخزون
        movements_tab = self.create_movements_tab()
        self.tab_widget.addTab(movements_tab, "حركة المخزون")
        
        # تبويب الإحصائيات
        stats_tab = self.create_stats_tab()
        self.tab_widget.addTab(stats_tab, "الإحصائيات")
        
        layout.addWidget(self.tab_widget)
    
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
        
        # البحث
        search_label = QLabel("البحث:")
        layout.addWidget(search_label)
        
        self.search_edit = QLineEdit()
        self.search_edit.setPlaceholderText("ابحث عن منتج...")
        self.search_edit.textChanged.connect(self.search_products)
        layout.addWidget(self.search_edit)
        
        layout.addStretch()
        
        # أزرار العمل
        add_product_btn = QPushButton("إضافة منتج")
        add_product_btn.setStyleSheet("""
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
        add_product_btn.clicked.connect(self.add_product)
        layout.addWidget(add_product_btn)
        
        add_category_btn = QPushButton("إضافة فئة")
        add_category_btn.setStyleSheet("""
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
        add_category_btn.clicked.connect(self.add_category)
        layout.addWidget(add_category_btn)
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        layout.addWidget(refresh_btn)
        
        return toolbar
    
    def create_products_tab(self):
        """إنشاء تبويب المنتجات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # جدول المنتجات
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(8)
        self.products_table.setHorizontalHeaderLabels([
            "الاسم", "الفئة", "الباركود", "سعر التكلفة", 
            "سعر البيع", "المخزون", "الحد الأدنى", "العمليات"
        ])
        
        # تخصيص الجدول
        header = self.products_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.products_table)
        
        return tab
    
    def create_low_stock_tab(self):
        """إنشاء تبويب المخزون المنخفض"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # تنبيه
        warning_frame = QFrame()
        warning_frame.setStyleSheet("""
            QFrame {
                background-color: #f39c12;
                border-radius: 5px;
                padding: 10px;
                margin: 5px;
            }
            QLabel {
                color: white;
                font-weight: bold;
            }
        """)
        warning_layout = QHBoxLayout(warning_frame)
        warning_layout.addWidget(QLabel("⚠️ المنتجات التالية بحاجة إلى إعادة تعبئة المخزون"))
        layout.addWidget(warning_frame)
        
        # جدول المخزون المنخفض
        self.low_stock_table = QTableWidget()
        self.low_stock_table.setColumnCount(6)
        self.low_stock_table.setHorizontalHeaderLabels([
            "الاسم", "الفئة", "المخزون الحالي", "الحد الأدنى", "الحالة", "العمليات"
        ])
        
        header = self.low_stock_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.low_stock_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.low_stock_table)
        
        return tab
    
    def create_movements_tab(self):
        """إنشاء تبويب حركة المخزون"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # فلاتر
        filters_frame = QFrame()
        filters_frame.setFrameStyle(QFrame.StyledPanel)
        filters_layout = QHBoxLayout(filters_frame)
        
        filters_layout.addWidget(QLabel("المنتج:"))
        self.movement_product_combo = QComboBox()
        self.movement_product_combo.addItem("جميع المنتجات", None)
        filters_layout.addWidget(self.movement_product_combo)
        
        filters_layout.addWidget(QLabel("من تاريخ:"))
        self.movement_start_date = QLineEdit()
        self.movement_start_date.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addWidget(self.movement_start_date)
        
        filters_layout.addWidget(QLabel("إلى تاريخ:"))
        self.movement_end_date = QLineEdit()
        self.movement_end_date.setPlaceholderText("YYYY-MM-DD")
        filters_layout.addWidget(self.movement_end_date)
        
        filter_btn = QPushButton("فلترة")
        filter_btn.clicked.connect(self.filter_movements)
        filters_layout.addWidget(filter_btn)
        
        filters_layout.addStretch()
        
        layout.addWidget(filters_frame)
        
        # جدول حركة المخزون
        self.movements_table = QTableWidget()
        self.movements_table.setColumnCount(6)
        self.movements_table.setHorizontalHeaderLabels([
            "التاريخ", "المنتج", "النوع", "الكمية", "المرجع", "المستخدم"
        ])
        
        header = self.movements_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.movements_table.setAlternatingRowColors(True)
        
        layout.addWidget(self.movements_table)
        
        return tab
    
    def create_stats_tab(self):
        """إنشاء تبويب الإحصائيات"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        # إجمالي المنتجات
        self.total_products_card = self.create_stat_card(
            "إجمالي المنتجات", "0", "#3498db"
        )
        stats_layout.addWidget(self.total_products_card, 0, 0)
        
        # قيمة المخزون
        self.inventory_value_card = self.create_stat_card(
            "قيمة المخزون", "0 ر.س", "#27ae60"
        )
        stats_layout.addWidget(self.inventory_value_card, 0, 1)
        
        # منتجات منخفضة المخزون
        self.low_stock_count_card = self.create_stat_card(
            "مخزون منخفض", "0", "#e74c3c"
        )
        stats_layout.addWidget(self.low_stock_count_card, 1, 0)
        
        # منتجات نفدت
        self.out_of_stock_card = self.create_stat_card(
            "نفد من المخزون", "0", "#e67e22"
        )
        stats_layout.addWidget(self.out_of_stock_card, 1, 1)
        
        layout.addLayout(stats_layout)
        
        # أكثر المنتجات مبيعاً
        top_products_frame = QFrame()
        top_products_frame.setFrameStyle(QFrame.StyledPanel)
        top_products_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        top_layout = QVBoxLayout(top_products_frame)
        
        top_title = QLabel("أكثر المنتجات مبيعاً")
        top_title.setFont(QFont("Arial", 14, QFont.Bold))
        top_title.setStyleSheet("color: #2c3e50;")
        top_layout.addWidget(top_title)
        
        self.top_products_table = QTableWidget()
        self.top_products_table.setColumnCount(4)
        self.top_products_table.setHorizontalHeaderLabels([
            "المنتج", "الكمية المباعة", "إجمالي الإيراد", "متوسط السعر"
        ])
        
        header = self.top_products_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(0, QHeaderView.Stretch)
        
        self.top_products_table.setMaximumHeight(250)
        self.top_products_table.setAlternatingRowColors(True)
        
        top_layout.addWidget(self.top_products_table)
        
        layout.addWidget(top_products_frame)
        
        return tab
    
    def create_stat_card(self, title, value, color):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 20px;
                margin: 5px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(card)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)
        
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 18, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # حفظ مرجع للقيمة للتحديث لاحقاً
        card.value_label = value_label
        
        return card
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_products()
        self.load_low_stock_products()
        self.load_movements()
        self.load_stats()
        self.load_movement_filters()
    
    def load_products(self):
        """تحميل المنتجات"""
        try:
            products = self.main_window.inventory_service.get_all_products()
            self.display_products(products)
        except Exception as e:
            logger.error(f"خطأ في تحميل المنتجات: {str(e)}")
    
    def display_products(self, products):
        """عرض المنتجات في الجدول"""
        self.products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # الاسم
            self.products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # الفئة
            category_name = product.get('category_name', 'غير مصنف')
            self.products_table.setItem(row, 1, QTableWidgetItem(category_name))
            
            # الباركود
            barcode = product.get('barcode', '')
            self.products_table.setItem(row, 2, QTableWidgetItem(barcode))
            
            # سعر التكلفة
            cost_item = QTableWidgetItem(f"{product.get('cost_price', 0):.2f}")
            cost_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 3, cost_item)
            
            # سعر البيع
            price_item = QTableWidgetItem(f"{product['selling_price']:.2f}")
            price_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 4, price_item)
            
            # المخزون
            stock_item = QTableWidgetItem(str(product['quantity_in_stock']))
            stock_item.setTextAlignment(Qt.AlignCenter)
            
            # تلوين المخزون
            if product['quantity_in_stock'] == 0:
                stock_item.setBackground(QColor("#e74c3c"))
                stock_item.setForeground(QColor("white"))
            elif product['quantity_in_stock'] <= product['minimum_stock']:
                stock_item.setBackground(QColor("#f39c12"))
                stock_item.setForeground(QColor("white"))
            
            self.products_table.setItem(row, 5, stock_item)
            
            # الحد الأدنى
            min_item = QTableWidgetItem(str(product['minimum_stock']))
            min_item.setTextAlignment(Qt.AlignCenter)
            self.products_table.setItem(row, 6, min_item)
            
            # أزرار العمليات
            operations_widget = self.create_operations_widget(product)
            self.products_table.setCellWidget(row, 7, operations_widget)
    
    def create_operations_widget(self, product):
        """إنشاء أزرار العمليات للمنتج"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # زر التعديل
        edit_btn = QPushButton("تعديل")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_product(product))
        layout.addWidget(edit_btn)
        
        # زر تعديل المخزون
        stock_btn = QPushButton("مخزون")
        stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        stock_btn.clicked.connect(lambda: self.adjust_stock(product))
        layout.addWidget(stock_btn)
        
        return widget
    
    def load_low_stock_products(self):
        """تحميل المنتجات منخفضة المخزون"""
        try:
            products = self.main_window.inventory_service.get_low_stock_products()
            self.display_low_stock_products(products)
        except Exception as e:
            logger.error(f"خطأ في تحميل المنتجات منخفضة المخزون: {str(e)}")
    
    def display_low_stock_products(self, products):
        """عرض المنتجات منخفضة المخزون"""
        self.low_stock_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # الاسم
            self.low_stock_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            # الفئة
            category_name = product.get('category_name', 'غير مصنف')
            self.low_stock_table.setItem(row, 1, QTableWidgetItem(category_name))
            
            # المخزون الحالي
            current_item = QTableWidgetItem(str(product['quantity_in_stock']))
            current_item.setTextAlignment(Qt.AlignCenter)
            self.low_stock_table.setItem(row, 2, current_item)
            
            # الحد الأدنى
            min_item = QTableWidgetItem(str(product['minimum_stock']))
            min_item.setTextAlignment(Qt.AlignCenter)
            self.low_stock_table.setItem(row, 3, min_item)
            
            # الحالة
            if product['quantity_in_stock'] == 0:
                status = "نفد"
                color = "#e74c3c"
            else:
                status = "منخفض"
                color = "#f39c12"
            
            status_item = QTableWidgetItem(status)
            status_item.setTextAlignment(Qt.AlignCenter)
            status_item.setBackground(QColor(color))
            status_item.setForeground(QColor("white"))
            self.low_stock_table.setItem(row, 4, status_item)
            
            # العمليات
            operations_widget = self.create_low_stock_operations(product)
            self.low_stock_table.setCellWidget(row, 5, operations_widget)
    
    def create_low_stock_operations(self, product):
        """إنشاء أزرار العمليات للمخزون المنخفض"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        stock_btn = QPushButton("إعادة تعبئة")
        stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        stock_btn.clicked.connect(lambda: self.adjust_stock(product))
        layout.addWidget(stock_btn)
        
        return widget
    
    def load_movements(self):
        """تحميل حركة المخزون"""
        try:
            movements = self.main_window.inventory_service.get_stock_movements()
            self.display_movements(movements[:100])  # أحدث 100 حركة
        except Exception as e:
            logger.error(f"خطأ في تحميل حركة المخزون: {str(e)}")
    
    def display_movements(self, movements):
        """عرض حركة المخزون"""
        self.movements_table.setRowCount(len(movements))
        
        for row, movement in enumerate(movements):
            # التاريخ
            date_str = movement['created_at'][:16]  # YYYY-MM-DD HH:MM
            self.movements_table.setItem(row, 0, QTableWidgetItem(date_str))
            
            # المنتج
            product_name = movement.get('product_name', 'غير معروف')
            self.movements_table.setItem(row, 1, QTableWidgetItem(product_name))
            
            # النوع
            movement_type = "دخول" if movement['movement_type'] == 'in' else "خروج"
            type_item = QTableWidgetItem(movement_type)
            type_item.setTextAlignment(Qt.AlignCenter)
            
            if movement['movement_type'] == 'in':
                type_item.setBackground(QColor("#27ae60"))
            else:
                type_item.setBackground(QColor("#e74c3c"))
            
            type_item.setForeground(QColor("white"))
            self.movements_table.setItem(row, 2, type_item)
            
            # الكمية
            quantity_item = QTableWidgetItem(str(movement['quantity']))
            quantity_item.setTextAlignment(Qt.AlignCenter)
            self.movements_table.setItem(row, 3, quantity_item)
            
            # المرجع
            reference = movement.get('reference_type', '')
            self.movements_table.setItem(row, 4, QTableWidgetItem(reference))
            
            # المستخدم
            user_name = movement.get('user_name', 'النظام')
            self.movements_table.setItem(row, 5, QTableWidgetItem(user_name))
    
    def load_stats(self):
        """تحميل الإحصائيات"""
        try:
            # إحصائيات المخزون
            summary = self.main_window.inventory_service.get_inventory_summary()
            
            self.total_products_card.value_label.setText(str(summary.get('total_products', 0)))
            self.inventory_value_card.value_label.setText(f"{summary.get('total_selling_value', 0):.0f} ر.س")
            self.low_stock_count_card.value_label.setText(str(summary.get('low_stock_count', 0)))
            self.out_of_stock_card.value_label.setText(str(summary.get('out_of_stock_count', 0)))
            
            # أكثر المنتجات مبيعاً
            top_products = self.main_window.inventory_service.get_top_selling_products(limit=10)
            self.display_top_products(top_products)
            
        except Exception as e:
            logger.error(f"خطأ في تحميل الإحصائيات: {str(e)}")
    
    def display_top_products(self, products):
        """عرض أكثر المنتجات مبيعاً"""
        self.top_products_table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            self.top_products_table.setItem(row, 0, QTableWidgetItem(product['name']))
            
            sold_item = QTableWidgetItem(str(product.get('total_sold', 0)))
            sold_item.setTextAlignment(Qt.AlignCenter)
            self.top_products_table.setItem(row, 1, sold_item)
            
            revenue_item = QTableWidgetItem(f"{product.get('total_revenue', 0):.2f}")
            revenue_item.setTextAlignment(Qt.AlignCenter)
            self.top_products_table.setItem(row, 2, revenue_item)
            
            avg_price_item = QTableWidgetItem(f"{product.get('avg_price', 0):.2f}")
            avg_price_item.setTextAlignment(Qt.AlignCenter)
            self.top_products_table.setItem(row, 3, avg_price_item)
    
    def load_movement_filters(self):
        """تحميل مرشحات حركة المخزون"""
        try:
            products = self.main_window.inventory_service.get_all_products()
            self.movement_product_combo.clear()
            self.movement_product_combo.addItem("جميع المنتجات", None)
            
            for product in products:
                self.movement_product_combo.addItem(product['name'], product['id'])
                
        except Exception as e:
            logger.error(f"خطأ في تحميل مرشحات الحركة: {str(e)}")
    
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
    
    def filter_movements(self):
        """فلترة حركة المخزون"""
        try:
            product_id = self.movement_product_combo.currentData()
            start_date = self.movement_start_date.text().strip() or None
            end_date = self.movement_end_date.text().strip() or None
            
            movements = self.main_window.inventory_service.get_stock_movements(
                product_id, start_date, end_date
            )
            self.display_movements(movements)
            
        except Exception as e:
            logger.error(f"خطأ في فلترة الحركة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في فلترة البيانات:\n{str(e)}")
    
    def add_product(self):
        """إضافة منتج جديد"""
        try:
            categories = self.main_window.inventory_service.get_all_categories()
            dialog = ProductDialog(self, categories=categories)
            
            if dialog.exec() == QDialog.Accepted:
                product_data = dialog.get_product_data()
                
                product_id = self.main_window.inventory_service.create_product(**product_data)
                
                if product_id:
                    QMessageBox.information(self, "نجح", "تم إضافة المنتج بنجاح")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إضافة المنتج")
                    
        except Exception as e:
            logger.error(f"خطأ في إضافة المنتج: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إضافة المنتج:\n{str(e)}")
    
    def edit_product(self, product):
        """تعديل المنتج"""
        try:
            categories = self.main_window.inventory_service.get_all_categories()
            dialog = ProductDialog(self, product, categories)
            
            if dialog.exec() == QDialog.Accepted:
                product_data = dialog.get_product_data()
                
                success = self.main_window.inventory_service.update_product(
                    product['id'], **product_data
                )
                
                if success:
                    QMessageBox.information(self, "نجح", "تم تحديث المنتج بنجاح")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في تحديث المنتج")
                    
        except Exception as e:
            logger.error(f"خطأ في تعديل المنتج: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل المنتج:\n{str(e)}")
    
    def adjust_stock(self, product):
        """تعديل المخزون"""
        try:
            dialog = StockAdjustmentDialog(self, product)
            
            if dialog.exec() == QDialog.Accepted:
                adjustment_data = dialog.get_adjustment_data()
                
                success = self.main_window.inventory_service.adjust_stock(
                    product['id'], 
                    adjustment_data['new_quantity'],
                    adjustment_data['reason']
                )
                
                if success:
                    QMessageBox.information(self, "نجح", "تم تعديل المخزون بنجاح")
                    self.refresh_data()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في تعديل المخزون")
                    
        except Exception as e:
            logger.error(f"خطأ في تعديل المخزون: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في تعديل المخزون:\n{str(e)}")
    
    def add_category(self):
        """إضافة فئة جديدة"""
        try:
            dialog = CategoryDialog(self)
            
            if dialog.exec() == QDialog.Accepted:
                category_data = dialog.get_category_data()
                
                category_id = self.main_window.inventory_service.create_category(
                    category_data['name'], category_data['description']
                )
                
                if category_id:
                    QMessageBox.information(self, "نجح", "تم إضافة الفئة بنجاح")
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في إضافة الفئة")
                    
        except Exception as e:
            logger.error(f"خطأ في إضافة الفئة: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"حدث خطأ في إضافة الفئة:\n{str(e)}")
