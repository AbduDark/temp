"""
Inventory Management Page for Desktop Application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt, QTimer
from PyQt6.QtGui import QFont
from uuid import uuid4

class InventoryPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Title
        title = QLabel("إدارة المخزون والمنتجات")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث في المنتجات...")
        self.search_input.textChanged.connect(self.filter_products)
        
        add_btn = QPushButton("إضافة منتج جديد")
        add_btn.clicked.connect(self.add_product)
        
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(add_btn)
        layout.addLayout(controls_layout)
        
        # Products table
        self.table = QTableWidget()
        self.table.setColumnCount(8)
        self.table.setHorizontalHeaderLabels([
            "العمليات", "المخزون", "سعر البيع", "سعر الشراء", 
            "الماركة", "الفئة", "اسم المنتج", "الكود"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
    def refresh_data(self):
        """Load products from database"""
        try:
            products = self.db_manager.execute_query("SELECT * FROM products ORDER BY name")
            self.populate_table(products)
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المنتجات: {e}")
    
    def populate_table(self, products):
        """Fill table with product data"""
        self.table.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Store product ID for reference
            self.table.setItem(row, 7, QTableWidgetItem(product['sku']))
            self.table.setItem(row, 6, QTableWidgetItem(product['name']))
            self.table.setItem(row, 5, QTableWidgetItem(product.get('category', '')))
            self.table.setItem(row, 4, QTableWidgetItem(product.get('brand', '')))
            self.table.setItem(row, 3, QTableWidgetItem(f"{product['buy_price']:.2f}"))
            self.table.setItem(row, 2, QTableWidgetItem(f"{product['sale_price']:.2f}"))
            self.table.setItem(row, 1, QTableWidgetItem(str(product['current_qty'])))
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            edit_btn = QPushButton("تحرير")
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            
            delete_btn = QPushButton("حذف")
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            delete_btn.setStyleSheet("background-color: #ef4444; color: white;")
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 0, actions_widget)
    
    def filter_products(self, text):
        """Filter products based on search text"""
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(1, self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def add_product(self):
        """Show add product dialog"""
        dialog = ProductDialog(self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def edit_product(self, product):
        """Show edit product dialog"""
        dialog = ProductDialog(self.db_manager, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_product(self, product):
        """Delete product with confirmation"""
        reply = QMessageBox.question(
            self, "تأكيد الحذف", 
            f"هل أنت متأكد من حذف المنتج '{product['name']}'؟"
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.execute_update(
                    "DELETE FROM products WHERE id = ?", 
                    (product['id'],)
                )
                self.refresh_data()
                QMessageBox.information(self, "نجح", "تم حذف المنتج بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المنتج: {e}")

class ProductDialog(QDialog):
    def __init__(self, db_manager, product=None):
        super().__init__()
        self.db_manager = db_manager
        self.product = product
        self.setup_ui()
        if product:
            self.load_product_data()
    
    def setup_ui(self):
        self.setWindowTitle("منتج جديد" if not self.product else "تحرير المنتج")
        self.setModal(True)
        self.resize(500, 400)
        
        layout = QFormLayout(self)
        
        # Form fields
        self.sku_input = QLineEdit()
        self.name_input = QLineEdit()
        self.description_input = QTextEdit()
        self.category_input = QLineEdit()
        self.brand_input = QLineEdit()
        self.barcode_input = QLineEdit()
        self.buy_price_input = QDoubleSpinBox()
        self.sale_price_input = QDoubleSpinBox()
        self.current_qty_input = QSpinBox()
        self.min_stock_input = QSpinBox()
        
        # Set ranges
        self.buy_price_input.setRange(0, 999999)
        self.sale_price_input.setRange(0, 999999)
        self.current_qty_input.setRange(0, 999999)
        self.min_stock_input.setRange(0, 999)
        
        # Add to form
        layout.addRow("الكود:", self.sku_input)
        layout.addRow("اسم المنتج:", self.name_input)
        layout.addRow("الوصف:", self.description_input)
        layout.addRow("الفئة:", self.category_input)
        layout.addRow("الماركة:", self.brand_input)
        layout.addRow("الباركود:", self.barcode_input)
        layout.addRow("سعر الشراء:", self.buy_price_input)
        layout.addRow("سعر البيع:", self.sale_price_input)
        layout.addRow("الكمية الحالية:", self.current_qty_input)
        layout.addRow("الحد الأدنى:", self.min_stock_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        
        save_btn.clicked.connect(self.save_product)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow(buttons_layout)
    
    def load_product_data(self):
        """Load existing product data into form"""
        if self.product:
            self.sku_input.setText(self.product['sku'])
            self.name_input.setText(self.product['name'])
            self.description_input.setText(self.product.get('description', ''))
            self.category_input.setText(self.product.get('category', ''))
            self.brand_input.setText(self.product.get('brand', ''))
            self.barcode_input.setText(self.product.get('barcode', ''))
            self.buy_price_input.setValue(self.product['buy_price'])
            self.sale_price_input.setValue(self.product['sale_price'])
            self.current_qty_input.setValue(self.product['current_qty'])
            self.min_stock_input.setValue(self.product['min_stock'])
    
    def save_product(self):
        """Save product to database"""
        if not self.name_input.text() or not self.sku_input.text():
            QMessageBox.warning(self, "تحذير", "يرجى ملء الحقول المطلوبة")
            return
        
        try:
            if self.product:
                # Update existing product
                self.db_manager.execute_update("""
                    UPDATE products SET 
                    sku=?, name=?, description=?, category=?, brand=?, 
                    barcode=?, buy_price=?, sale_price=?, current_qty=?, min_stock=?
                    WHERE id=?
                """, (
                    self.sku_input.text(),
                    self.name_input.text(),
                    self.description_input.toPlainText(),
                    self.category_input.text(),
                    self.brand_input.text(),
                    self.barcode_input.text(),
                    self.buy_price_input.value(),
                    self.sale_price_input.value(),
                    self.current_qty_input.value(),
                    self.min_stock_input.value(),
                    self.product['id']
                ))
            else:
                # Insert new product
                product_id = str(uuid4())
                self.db_manager.execute_update("""
                    INSERT INTO products 
                    (id, sku, name, description, category, brand, barcode, 
                     buy_price, sale_price, current_qty, min_stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_id,
                    self.sku_input.text(),
                    self.name_input.text(),
                    self.description_input.toPlainText(),
                    self.category_input.text(),
                    self.brand_input.text(),
                    self.barcode_input.text(),
                    self.buy_price_input.value(),
                    self.sale_price_input.value(),
                    self.current_qty_input.value(),
                    self.min_stock_input.value()
                ))
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المنتج: {e}")