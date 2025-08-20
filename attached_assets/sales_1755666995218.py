"""
Sales/POS Page for Desktop Application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from uuid import uuid4
from datetime import datetime

class SalesPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("نظام نقاط البيع")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)
        
        # Quick sale button
        new_sale_btn = QPushButton("فاتورة جديدة")
        new_sale_btn.setFixedHeight(50)
        new_sale_btn.clicked.connect(self.new_sale)
        new_sale_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                font-size: 16px;
                font-weight: bold;
                border-radius: 8px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        layout.addWidget(new_sale_btn)
        
        layout.addStretch()
        
    def new_sale(self):
        dialog = SaleDialog(self.db_manager)
        dialog.exec()
    
    def refresh_data(self):
        pass

class SaleDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.sale_items = []
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        self.setWindowTitle("فاتورة جديدة")
        self.setModal(True)
        self.resize(800, 600)
        
        layout = QVBoxLayout(self)
        
        # Product search
        search_layout = QHBoxLayout()
        search_label = QLabel("البحث عن منتج:")
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث بالاسم أو الكود...")
        self.search_input.textChanged.connect(self.search_products)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input)
        layout.addLayout(search_layout)
        
        # Products list
        self.products_combo = QComboBox()
        self.products_combo.currentTextChanged.connect(self.product_selected)
        layout.addWidget(self.products_combo)
        
        # Sale items table
        self.items_table = QTableWidget()
        self.items_table.setColumnCount(5)
        self.items_table.setHorizontalHeaderLabels([
            "حذف", "الإجمالي", "الكمية", "السعر", "المنتج"
        ])
        layout.addWidget(self.items_table)
        
        # Totals
        totals_frame = QFrame()
        totals_layout = QFormLayout(totals_frame)
        
        self.subtotal_label = QLabel("0.00 جنيه")
        self.tax_label = QLabel("0.00 جنيه")
        self.total_label = QLabel("0.00 جنيه")
        
        totals_layout.addRow("المجموع الفرعي:", self.subtotal_label)
        totals_layout.addRow("الضريبة (14%):", self.tax_label)
        totals_layout.addRow("الإجمالي:", self.total_label)
        
        layout.addWidget(totals_frame)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        complete_btn = QPushButton("إتمام البيع")
        cancel_btn = QPushButton("إلغاء")
        
        complete_btn.clicked.connect(self.complete_sale)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(complete_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addLayout(buttons_layout)
        
    def load_products(self):
        self.products = self.db_manager.execute_query(
            "SELECT * FROM products WHERE current_qty > 0"
        )
        self.refresh_products_combo()
        
    def refresh_products_combo(self):
        self.products_combo.clear()
        self.products_combo.addItem("اختر منتج...")
        for product in self.products:
            self.products_combo.addItem(f"{product['name']} - {product['sku']}", product)
            
    def search_products(self, text):
        self.products_combo.clear()
        self.products_combo.addItem("اختر منتج...")
        
        for product in self.products:
            if (text.lower() in product['name'].lower() or 
                text.lower() in product['sku'].lower()):
                self.products_combo.addItem(f"{product['name']} - {product['sku']}", product)
                
    def product_selected(self):
        if self.products_combo.currentIndex() > 0:
            product = self.products_combo.currentData()
            if product:
                self.add_sale_item(product)
                self.products_combo.setCurrentIndex(0)
                
    def add_sale_item(self, product):
        # Check if product already in list
        for i, item in enumerate(self.sale_items):
            if item['product_id'] == product['id']:
                self.sale_items[i]['qty'] += 1
                self.refresh_items_table()
                return
                
        # Add new item
        self.sale_items.append({
            'product_id': product['id'],
            'product': product,
            'qty': 1,
            'price': product['sale_price']
        })
        self.refresh_items_table()
        
    def refresh_items_table(self):
        self.items_table.setRowCount(len(self.sale_items))
        
        for row, item in enumerate(self.sale_items):
            self.items_table.setItem(row, 4, QTableWidgetItem(item['product']['name']))
            self.items_table.setItem(row, 3, QTableWidgetItem(f"{item['price']:.2f}"))
            
            # Quantity spinbox
            qty_spin = QSpinBox()
            qty_spin.setMinimum(1)
            qty_spin.setMaximum(item['product']['current_qty'])
            qty_spin.setValue(item['qty'])
            qty_spin.valueChanged.connect(lambda val, r=row: self.update_qty(r, val))
            self.items_table.setCellWidget(row, 2, qty_spin)
            
            # Total
            total = item['qty'] * item['price']
            self.items_table.setItem(row, 1, QTableWidgetItem(f"{total:.2f}"))
            
            # Delete button
            del_btn = QPushButton("حذف")
            del_btn.clicked.connect(lambda checked, r=row: self.remove_item(r))
            del_btn.setStyleSheet("background-color: #ef4444; color: white;")
            self.items_table.setCellWidget(row, 0, del_btn)
            
        self.update_totals()
        
    def update_qty(self, row, qty):
        self.sale_items[row]['qty'] = qty
        self.refresh_items_table()
        
    def remove_item(self, row):
        del self.sale_items[row]
        self.refresh_items_table()
        
    def update_totals(self):
        subtotal = sum(item['qty'] * item['price'] for item in self.sale_items)
        tax = 0.0  # Removed tax
        total = subtotal
        
        self.subtotal_label.setText(f"{subtotal:.2f} جنيه")
        self.tax_label.setText("0.00 جنيه")
        self.total_label.setText(f"{total:.2f} جنيه")
        
    def complete_sale(self):
        if not self.sale_items:
            QMessageBox.warning(self, "تحذير", "يرجى إضافة منتجات للفاتورة")
            return
            
        try:
            # Calculate totals - No tax
            subtotal = sum(item['qty'] * item['price'] for item in self.sale_items)
            tax = 0.0  # Removed tax
            total = subtotal
            
            # Insert sale
            sale_id = str(uuid4())
            self.db_manager.execute_update("""
                INSERT INTO sales (id, subtotal, tax, total, payment_method)
                VALUES (?, ?, ?, ?, ?)
            """, (sale_id, subtotal, tax, total, 'cash'))
            
            # Insert sale items
            for item in self.sale_items:
                item_id = str(uuid4())
                self.db_manager.execute_update("""
                    INSERT INTO sale_items (id, sale_id, product_id, qty, unit_price, total)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (
                    item_id, sale_id, item['product_id'], 
                    item['qty'], item['price'], 
                    item['qty'] * item['price']
                ))
                
                # Update product quantity
                self.db_manager.execute_update("""
                    UPDATE products SET current_qty = current_qty - ? WHERE id = ?
                """, (item['qty'], item['product_id']))
            
            QMessageBox.information(self, "نجح", f"تم إتمام البيع بنجاح\nالمبلغ الإجمالي: {total:.2f} جنيه")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إتمام البيع: {e}")