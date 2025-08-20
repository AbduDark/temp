"""
Improved Inventory Management Page with CRUD operations
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QSpinBox, QDoubleSpinBox,
    QTextEdit, QGroupBox, QScrollArea, QTabWidget, QGridLayout
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QColor
from uuid import uuid4
from datetime import datetime

class AddProductDialog(QDialog):
    """Enhanced dialog for adding/editing products"""
    
    def __init__(self, db_manager, product=None, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.product = product
        self.is_editing = product is not None
        self.setup_ui()
        if self.is_editing:
            self.populate_fields()
        
    def setup_ui(self):
        """Setup the enhanced product dialog"""
        self.setWindowTitle("تعديل منتج" if self.is_editing else "إضافة منتج جديد")
        self.setModal(True)
        self.resize(500, 600)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header_label = QLabel("تعديل المنتج" if self.is_editing else "إضافة منتج جديد")
        header_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header_label.setStyleSheet("color: #1e293b; margin-bottom: 10px;")
        layout.addWidget(header_label)
        
        # Form in a scroll area
        scroll = QScrollArea()
        form_widget = QWidget()
        form_layout = QFormLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Product details
        self.sku_input = QLineEdit()
        self.sku_input.setPlaceholderText("مثال: IPH14-CASE-001")
        
        self.name_input = QLineEdit()
        self.name_input.setPlaceholderText("اسم المنتج")
        
        self.description_input = QTextEdit()
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("وصف المنتج (اختياري)")
        
        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)
        categories = ["جرابات", "شواحن", "شاشات", "سماعات", "بطاريات", "كابلات", "اكسسوارات"]
        self.category_combo.addItems(categories)
        
        self.brand_input = QLineEdit()
        self.brand_input.setPlaceholderText("الماركة")
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setPlaceholderText("الباركود (اختياري)")
        
        # Pricing
        self.cost_input = QDoubleSpinBox()
        self.cost_input.setRange(0.0, 999999.99)
        self.cost_input.setDecimals(2)
        self.cost_input.setSuffix(" جنيه")
        
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setRange(0.0, 999999.99)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setSuffix(" جنيه")
        
        # Stock
        self.current_qty_input = QSpinBox()
        self.current_qty_input.setRange(0, 999999)
        
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 999999)
        self.min_stock_input.setValue(5)  # Default minimum stock
        
        # Add fields to form
        form_layout.addRow("كود المنتج *:", self.sku_input)
        form_layout.addRow("اسم المنتج *:", self.name_input)
        form_layout.addRow("الوصف:", self.description_input)
        form_layout.addRow("الفئة:", self.category_combo)
        form_layout.addRow("الماركة:", self.brand_input)
        form_layout.addRow("الباركود:", self.barcode_input)
        form_layout.addRow("تكلفة الشراء:", self.cost_input)
        form_layout.addRow("سعر البيع *:", self.sale_price_input)
        form_layout.addRow("الكمية الحالية:", self.current_qty_input)
        form_layout.addRow("الحد الأدنى للمخزون:", self.min_stock_input)
        
        # Style form inputs
        self.style_inputs()
        
        scroll.setWidget(form_widget)
        scroll.setWidgetResizable(True)
        layout.addWidget(scroll)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("حفظ" if not self.is_editing else "تحديث")
        save_btn.setFixedHeight(45)
        save_btn.clicked.connect(self.save_product)
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setFixedHeight(45)
        cancel_btn.clicked.connect(self.reject)
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #6b7280;
                color: white;
                border: none;
                border-radius: 8px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #4b5563;
            }
        """)
        
        button_layout.addWidget(cancel_btn)
        button_layout.addWidget(save_btn)
        layout.addLayout(button_layout)
        
    def style_inputs(self):
        """Apply styling to form inputs"""
        input_style = """
            QLineEdit, QSpinBox, QDoubleSpinBox, QComboBox, QTextEdit {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 8px 12px;
                font-size: 12px;
                background-color: white;
            }
            QLineEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus, QComboBox:focus, QTextEdit:focus {
                border-color: #3b82f6;
            }
        """
        
        for widget in [self.sku_input, self.name_input, self.description_input, 
                      self.category_combo, self.brand_input, self.barcode_input,
                      self.cost_input, self.sale_price_input, self.current_qty_input, self.min_stock_input]:
            widget.setStyleSheet(input_style)
        
    def populate_fields(self):
        """Populate form fields when editing"""
        if self.product:
            self.sku_input.setText(self.product.get('sku', ''))
            self.name_input.setText(self.product.get('name', ''))
            self.description_input.setText(self.product.get('description', ''))
            
            # Set category
            category = self.product.get('category', '')
            index = self.category_combo.findText(category)
            if index >= 0:
                self.category_combo.setCurrentIndex(index)
            else:
                self.category_combo.setEditText(category)
                
            self.brand_input.setText(self.product.get('brand', ''))
            self.barcode_input.setText(self.product.get('barcode', ''))
            self.cost_input.setValue(float(self.product.get('cost_price', 0)))
            self.sale_price_input.setValue(float(self.product.get('sale_price', 0)))
            self.current_qty_input.setValue(int(self.product.get('current_qty', 0)))
            self.min_stock_input.setValue(int(self.product.get('min_stock', 5)))
        
    def save_product(self):
        """Save or update product"""
        # Validation
        if not self.sku_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال كود المنتج")
            return
            
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المنتج")
            return
            
        if self.sale_price_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال سعر بيع صحيح")
            return
        
        try:
            product_data = {
                'sku': self.sku_input.text().strip(),
                'name': self.name_input.text().strip(),
                'description': self.description_input.toPlainText().strip(),
                'category': self.category_combo.currentText().strip(),
                'brand': self.brand_input.text().strip(),
                'barcode': self.barcode_input.text().strip(),
                'cost_price': self.cost_input.value(),
                'sale_price': self.sale_price_input.value(),
                'current_qty': self.current_qty_input.value(),
                'min_stock': self.min_stock_input.value(),
                'updated_at': datetime.now().isoformat()
            }
            
            if self.is_editing:
                # Update existing product
                product_data['id'] = self.product['id']
                self.db_manager.execute_update("""
                    UPDATE products SET 
                        sku=?, name=?, description=?, category=?, brand=?, barcode=?,
                        cost_price=?, sale_price=?, current_qty=?, min_stock=?, updated_at=?
                    WHERE id=?
                """, (
                    product_data['sku'], product_data['name'], product_data['description'],
                    product_data['category'], product_data['brand'], product_data['barcode'],
                    product_data['cost_price'], product_data['sale_price'],
                    product_data['current_qty'], product_data['min_stock'],
                    product_data['updated_at'], product_data['id']
                ))
                QMessageBox.information(self, "نجح", "تم تحديث المنتج بنجاح")
            else:
                # Add new product
                product_data['id'] = str(uuid4())
                product_data['created_at'] = datetime.now().isoformat()
                self.db_manager.execute_update("""
                    INSERT INTO products 
                    (id, sku, name, description, category, brand, barcode, cost_price, 
                     sale_price, current_qty, min_stock, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    product_data['id'], product_data['sku'], product_data['name'],
                    product_data['description'], product_data['category'], product_data['brand'],
                    product_data['barcode'], product_data['cost_price'], product_data['sale_price'],
                    product_data['current_qty'], product_data['min_stock'],
                    product_data['created_at'], product_data['updated_at']
                ))
                QMessageBox.information(self, "نجح", "تم إضافة المنتج بنجاح")
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المنتج: {e}")

class ImprovedInventoryPage(QWidget):
    """Enhanced inventory management page with full CRUD operations"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.products = []
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup enhanced inventory UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)
        
        # Header
        header_frame = QFrame()
        header_layout = QHBoxLayout(header_frame)
        
        title = QLabel("إدارة المخزون")
        title.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        title.setStyleSheet("color: #1e293b;")
        
        # Add product button
        add_btn = QPushButton("🆕 إضافة منتج جديد")
        add_btn.setFixedHeight(45)
        add_btn.clicked.connect(self.add_product)
        add_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 12px 20px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        layout.addWidget(header_frame)
        
        # Search and filters
        self.setup_search_section(layout)
        
        # Products table
        self.setup_products_table(layout)
        
        # Statistics
        self.setup_stats_section(layout)
        
    def setup_search_section(self, parent_layout):
        """Setup search and filter section"""
        search_frame = QFrame()
        search_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 15px;
            }
        """)
        search_layout = QHBoxLayout(search_frame)
        
        # Search input
        search_label = QLabel("البحث:")
        search_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث بالاسم، الكود، أو الباركود...")
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.setStyleSheet("""
            QLineEdit {
                border: 2px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                background-color: #f9fafb;
            }
            QLineEdit:focus {
                border-color: #3b82f6;
                background-color: white;
            }
        """)
        
        # Category filter
        category_label = QLabel("الفئة:")
        category_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        
        self.category_filter = QComboBox()
        self.category_filter.addItem("جميع الفئات")
        self.category_filter.currentTextChanged.connect(self.filter_products)
        
        # Stock filter
        stock_label = QLabel("المخزون:")
        stock_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        
        self.stock_filter = QComboBox()
        self.stock_filter.addItems(["الكل", "متوفر", "نقص", "نفد"])
        self.stock_filter.currentTextChanged.connect(self.filter_products)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.clicked.connect(self.refresh_data)
        refresh_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 15px;
                font-size: 12px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        
        search_layout.addWidget(search_label)
        search_layout.addWidget(self.search_input, 2)
        search_layout.addWidget(category_label)
        search_layout.addWidget(self.category_filter)
        search_layout.addWidget(stock_label)
        search_layout.addWidget(self.stock_filter)
        search_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(search_frame)
        
    def setup_products_table(self, parent_layout):
        """Setup enhanced products table"""
        table_frame = QFrame()
        table_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 10px;
            }
        """)
        table_layout = QVBoxLayout(table_frame)
        
        self.products_table = QTableWidget()
        self.products_table.setColumnCount(9)
        self.products_table.setHorizontalHeaderLabels([
            "إجراءات", "الحالة", "الحد الأدنى", "الكمية", "السعر", 
            "الفئة", "الباركود", "الاسم", "الكود"
        ])
        
        # Table styling
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: none;
                gridline-color: #e5e7eb;
                background-color: white;
                alternate-background-color: #f9fafb;
            }
            QHeaderView::section {
                background-color: #f3f4f6;
                padding: 12px 8px;
                font-size: 12px;
                font-weight: bold;
                border: 1px solid #e5e7eb;
            }
            QTableWidget::item {
                padding: 10px 8px;
                border-bottom: 1px solid #f3f4f6;
            }
            QTableWidget::item:selected {
                background-color: #dbeafe;
                color: #1e40af;
            }
        """)
        
        # Header resize
        header = self.products_table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Interactive)
        header.setSectionResizeMode(7, QHeaderView.ResizeMode.Stretch)  # Name column
        
        table_layout.addWidget(self.products_table)
        parent_layout.addWidget(table_frame)
        
    def setup_stats_section(self, parent_layout):
        """Setup statistics section"""
        stats_frame = QFrame()
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 20px;
            }
        """)
        stats_layout = QHBoxLayout(stats_frame)
        
        # Stats cards
        self.total_products_label = QLabel("0")
        self.low_stock_label = QLabel("0")
        self.out_stock_label = QLabel("0")
        self.total_value_label = QLabel("0 جنيه")
        
        stats_config = [
            ("إجمالي المنتجات", self.total_products_label, "#3b82f6"),
            ("نقص مخزون", self.low_stock_label, "#f59e0b"),
            ("نفد المخزون", self.out_stock_label, "#ef4444"),
            ("قيمة المخزون", self.total_value_label, "#10b981")
        ]
        
        for title, label, color in stats_config:
            card = self.create_stat_card(title, label, color)
            stats_layout.addWidget(card)
        
        parent_layout.addWidget(stats_frame)
        
    def create_stat_card(self, title, value_label, color):
        """Create a statistics card"""
        card = QFrame()
        card.setFixedHeight(80)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color}10;
                border: 2px solid {color}30;
                border-radius: 10px;
                border-left: 4px solid {color};
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setContentsMargins(15, 10, 15, 10)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Tahoma", 11))
        title_label.setStyleSheet("color: #64748b;")
        title_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        value_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        value_label.setStyleSheet(f"color: {color};")
        value_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(title_label)
        layout.addWidget(value_label)
        
        return card
        
    def add_product(self):
        """Open add product dialog"""
        dialog = AddProductDialog(self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def edit_product(self, product):
        """Open edit product dialog"""
        dialog = AddProductDialog(self.db_manager, product)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
            
    def delete_product(self, product):
        """Delete product with confirmation"""
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف المنتج: {product['name']}؟\n"
            "لا يمكن التراجع عن هذا الإجراء.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.execute_update("DELETE FROM products WHERE id = ?", (product['id'],))
                QMessageBox.information(self, "نجح", "تم حذف المنتج بنجاح")
                self.refresh_data()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المنتج: {e}")
    
    def filter_products(self):
        """Filter products based on search and filters"""
        search_text = self.search_input.text().lower()
        selected_category = self.category_filter.currentText()
        selected_stock = self.stock_filter.currentText()
        
        for row in range(self.products_table.rowCount()):
            show_row = True
            
            # Get product data from table
            sku = self.products_table.item(row, 8).text().lower() if self.products_table.item(row, 8) else ""
            name = self.products_table.item(row, 7).text().lower() if self.products_table.item(row, 7) else ""
            category = self.products_table.item(row, 5).text() if self.products_table.item(row, 5) else ""
            qty = int(self.products_table.item(row, 4).text()) if self.products_table.item(row, 4) else 0
            min_stock = int(self.products_table.item(row, 3).text()) if self.products_table.item(row, 3) else 0
            
            # Search filter
            if search_text and not (search_text in name or search_text in sku):
                show_row = False
            
            # Category filter
            if selected_category != "جميع الفئات" and category != selected_category:
                show_row = False
                
            # Stock filter
            if selected_stock != "الكل":
                if selected_stock == "نفد" and qty > 0:
                    show_row = False
                elif selected_stock == "نقص" and (qty == 0 or qty > min_stock):
                    show_row = False
                elif selected_stock == "متوفر" and qty <= min_stock:
                    show_row = False
            
            self.products_table.setRowHidden(row, not show_row)
    
    def refresh_data(self):
        """Refresh products data"""
        try:
            self.products = self.db_manager.execute_query("SELECT * FROM products ORDER BY name")
            self.populate_table()
            self.update_categories_filter()
            self.update_statistics()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل البيانات: {e}")
    
    def populate_table(self):
        """Populate products table"""
        self.products_table.setRowCount(len(self.products))
        
        for row, product in enumerate(self.products):
            # Basic data
            self.products_table.setItem(row, 8, QTableWidgetItem(product.get('sku', '')))
            self.products_table.setItem(row, 7, QTableWidgetItem(product.get('name', '')))
            self.products_table.setItem(row, 6, QTableWidgetItem(product.get('barcode', '')))
            self.products_table.setItem(row, 5, QTableWidgetItem(product.get('category', '')))
            self.products_table.setItem(row, 4, QTableWidgetItem(f"{product.get('sale_price', 0):.2f} جنيه"))
            self.products_table.setItem(row, 3, QTableWidgetItem(str(product.get('current_qty', 0))))
            self.products_table.setItem(row, 2, QTableWidgetItem(str(product.get('min_stock', 0))))
            
            # Status
            qty = product.get('current_qty', 0)
            min_stock = product.get('min_stock', 0)
            
            if qty == 0:
                status = "نفد"
                status_color = QColor("#fee2e2")
            elif qty <= min_stock:
                status = "نقص"
                status_color = QColor("#fef3c7")
            else:
                status = "متوفر"
                status_color = QColor("#d1fae5")
            
            status_item = QTableWidgetItem(status)
            status_item.setBackground(status_color)
            self.products_table.setItem(row, 1, status_item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            actions_layout.setContentsMargins(5, 2, 5, 2)
            actions_layout.setSpacing(5)
            
            edit_btn = QPushButton("✏️")
            edit_btn.setFixedSize(30, 30)
            edit_btn.clicked.connect(lambda checked, p=product: self.edit_product(p))
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #3b82f6;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #2563eb;
                }
            """)
            
            delete_btn = QPushButton("🗑️")
            delete_btn.setFixedSize(30, 30)
            delete_btn.clicked.connect(lambda checked, p=product: self.delete_product(p))
            delete_btn.setStyleSheet("""
                QPushButton {
                    background-color: #ef4444;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    font-size: 14px;
                }
                QPushButton:hover {
                    background-color: #dc2626;
                }
            """)
            
            actions_layout.addWidget(edit_btn)
            actions_layout.addWidget(delete_btn)
            actions_layout.addStretch()
            
            self.products_table.setCellWidget(row, 0, actions_widget)
    
    def update_categories_filter(self):
        """Update categories filter dropdown"""
        current_categories = set(p.get('category', '') for p in self.products if p.get('category'))
        
        self.category_filter.clear()
        self.category_filter.addItem("جميع الفئات")
        self.category_filter.addItems(sorted(current_categories))
    
    def update_statistics(self):
        """Update statistics cards"""
        total_products = len(self.products)
        low_stock = sum(1 for p in self.products if p.get('current_qty', 0) <= p.get('min_stock', 0) and p.get('current_qty', 0) > 0)
        out_of_stock = sum(1 for p in self.products if p.get('current_qty', 0) == 0)
        total_value = sum(p.get('current_qty', 0) * p.get('cost_price', 0) for p in self.products)
        
        self.total_products_label.setText(str(total_products))
        self.low_stock_label.setText(str(low_stock))
        self.out_stock_label.setText(str(out_of_stock))
        self.total_value_label.setText(f"{total_value:.2f} جنيه")