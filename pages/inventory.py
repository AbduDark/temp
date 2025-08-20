"""
Enhanced Inventory Management Page for Mobile Shop Management System
Comprehensive product and stock management with beautiful modern UI
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QHeaderView, QScrollArea, QProgressBar,
    QMessageBox, QFileDialog, QGraphicsDropShadowEffect, QCheckBox,
    QGroupBox, QFormLayout, QDateEdit, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QThread, pyqtSignal as Signal
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon
from datetime import datetime, timedelta
from uuid import uuid4
import csv
import json

from ui.styles import ModernStyles
from ui.dialogs import AddProductDialog, EditProductDialog, ImportProductsDialog
from ui.widgets import SearchWidget, FilterWidget, StatCard

class InventoryStatsWidget(QFrame):
    """Inventory statistics display widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup statistics UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QGridLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Statistics cards
        self.total_products_card = StatCard("إجمالي المنتجات", "0", "📱", "#3b82f6")
        self.total_value_card = StatCard("قيمة المخزون", "0 جنيه", "💰", "#10b981")
        self.low_stock_card = StatCard("نقص المخزون", "0", "⚠️", "#f59e0b")
        self.out_stock_card = StatCard("نفاد المخزون", "0", "❌", "#ef4444")
        
        layout.addWidget(self.total_products_card, 0, 0)
        layout.addWidget(self.total_value_card, 0, 1)
        layout.addWidget(self.low_stock_card, 0, 2)
        layout.addWidget(self.out_stock_card, 0, 3)
        
    def update_statistics(self):
        """Update inventory statistics"""
        try:
            # Total products
            total_products = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM products WHERE is_active = 1
            """)[0]['count']
            
            # Total inventory value
            total_value = self.db_manager.execute_query("""
                SELECT COALESCE(SUM(current_qty * buy_price), 0) as value 
                FROM products WHERE is_active = 1
            """)[0]['value']
            
            # Low stock count
            low_stock = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM products 
                WHERE current_qty <= min_stock AND current_qty > 0 AND is_active = 1
            """)[0]['count']
            
            # Out of stock count
            out_stock = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM products 
                WHERE current_qty = 0 AND is_active = 1
            """)[0]['count']
            
            # Update cards
            self.total_products_card.update_value(str(total_products))
            self.total_value_card.update_value(f"{total_value:.2f} جنيه")
            self.low_stock_card.update_value(str(low_stock))
            self.out_stock_card.update_value(str(out_stock))
            
        except Exception as e:
            print(f"Error updating inventory statistics: {e}")

class ProductTableWidget(QTableWidget):
    """Enhanced product table with advanced features"""
    
    product_selected = pyqtSignal(dict)
    product_double_clicked = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.products_data = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup table UI"""
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels([
            "الإجراءات", "الحالة", "الربح %", "قيمة المخزون", "الكمية الحالية", 
            "سعر البيع", "سعر الشراء", "الفئة", "الماركة", "اسم المنتج", "الكود", "ID"
        ])
        
        # Hide ID column
        self.setColumnHidden(11, True)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.resizeSection(0, 120)  # Actions
        header.resizeSection(1, 80)   # Status
        header.resizeSection(2, 80)   # Profit
        header.resizeSection(3, 120)  # Value
        header.resizeSection(4, 100)  # Quantity
        header.resizeSection(5, 100)  # Sale price
        header.resizeSection(6, 100)  # Buy price
        header.resizeSection(7, 100)  # Category
        header.resizeSection(8, 100)  # Brand
        header.resizeSection(9, 200)  # Name
        header.resizeSection(10, 120) # SKU
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setStyleSheet(ModernStyles.get_table_style())
        
        # Connect signals
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemDoubleClicked.connect(self.on_double_click)
        
    def populate_table(self, products):
        """Populate table with products data"""
        self.products_data = products
        self.setRowCount(len(products))
        
        for row, product in enumerate(products):
            # Actions column (buttons)
            actions_widget = self.create_actions_widget(product)
            self.setCellWidget(row, 0, actions_widget)
            
            # Status column (indicator)
            status_widget = self.create_status_widget(product)
            self.setCellWidget(row, 1, status_widget)
            
            # Profit percentage
            profit_margin = ((product['sale_price'] - product['buy_price']) / product['buy_price'] * 100) if product['buy_price'] > 0 else 0
            profit_item = QTableWidgetItem(f"{profit_margin:.1f}%")
            if profit_margin >= 30:
                profit_item.setBackground(QColor(220, 252, 231))  # Green
            elif profit_margin >= 15:
                profit_item.setBackground(QColor(254, 249, 195))  # Yellow
            else:
                profit_item.setBackground(QColor(254, 226, 226))  # Red
            self.setItem(row, 2, profit_item)
            
            # Inventory value
            inventory_value = product['current_qty'] * product['buy_price']
            self.setItem(row, 3, QTableWidgetItem(f"{inventory_value:.2f}"))
            
            # Current quantity
            qty_item = QTableWidgetItem(str(product['current_qty']))
            if product['current_qty'] == 0:
                qty_item.setBackground(QColor(254, 226, 226))  # Red
            elif product['current_qty'] <= product['min_stock']:
                qty_item.setBackground(QColor(254, 249, 195))  # Yellow
            self.setItem(row, 4, qty_item)
            
            # Sale price
            self.setItem(row, 5, QTableWidgetItem(f"{product['sale_price']:.2f}"))
            
            # Buy price
            self.setItem(row, 6, QTableWidgetItem(f"{product['buy_price']:.2f}"))
            
            # Category
            self.setItem(row, 7, QTableWidgetItem(product['category'] or ''))
            
            # Brand
            self.setItem(row, 8, QTableWidgetItem(product['brand'] or ''))
            
            # Product name
            name_item = QTableWidgetItem(product['name'])
            name_item.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
            self.setItem(row, 9, name_item)
            
            # SKU
            self.setItem(row, 10, QTableWidgetItem(product['sku']))
            
            # Hidden ID
            self.setItem(row, 11, QTableWidgetItem(product['id']))
            
    def create_actions_widget(self, product):
        """Create actions widget for product row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 25)
        edit_btn.setToolTip("تعديل المنتج")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_product(product))
        
        # Delete button
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 25)
        delete_btn.setToolTip("حذف المنتج")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_product(product))
        
        # Stock button
        stock_btn = QPushButton("📦")
        stock_btn.setFixedSize(30, 25)
        stock_btn.setToolTip("إدارة المخزون")
        stock_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        stock_btn.clicked.connect(lambda: self.manage_stock(product))
        
        layout.addWidget(edit_btn)
        layout.addWidget(delete_btn)
        layout.addWidget(stock_btn)
        
        return widget
        
    def create_status_widget(self, product):
        """Create status indicator widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        if product['current_qty'] == 0:
            indicator = QLabel("●")
            indicator.setStyleSheet("color: #ef4444; font-size: 16px;")
            indicator.setToolTip("نفاد المخزون")
        elif product['current_qty'] <= product['min_stock']:
            indicator = QLabel("●")
            indicator.setStyleSheet("color: #f59e0b; font-size: 16px;")
            indicator.setToolTip("مخزون منخفض")
        else:
            indicator = QLabel("●")
            indicator.setStyleSheet("color: #10b981; font-size: 16px;")
            indicator.setToolTip("مخزون متوفر")
        
        layout.addWidget(indicator)
        return widget
        
    def edit_product(self, product):
        """Edit product"""
        # This will be handled by the parent widget
        self.product_double_clicked.emit(product)
        
    def delete_product(self, product):
        """Delete product"""
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف المنتج '{product['name']}'؟\nسيتم حذف جميع البيانات المرتبطة بهذا المنتج.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                # Get database manager from parent
                parent = self.parent()
                while parent and not hasattr(parent, 'db_manager'):
                    parent = parent.parent()
                
                if parent and hasattr(parent, 'db_manager'):
                    parent.db_manager.execute_update(
                        "UPDATE products SET is_active = 0 WHERE id = ?",
                        (product['id'],)
                    )
                    QMessageBox.information(self, "نجح", "تم حذف المنتج بنجاح")
                    # Refresh table
                    if hasattr(parent, 'refresh_products'):
                        parent.refresh_products()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المنتج: {str(e)}")
        
    def manage_stock(self, product):
        """Manage product stock"""
        from ui.dialogs import StockManagementDialog
        
        parent = self.parent()
        while parent and not hasattr(parent, 'db_manager'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'db_manager'):
            dialog = StockManagementDialog(product, parent.db_manager, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                if hasattr(parent, 'refresh_products'):
                    parent.refresh_products()
        
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.products_data):
            product = self.products_data[current_row]
            self.product_selected.emit(product)
            
    def on_double_click(self, item):
        """Handle double click"""
        row = item.row()
        if row >= 0 and row < len(self.products_data):
            product = self.products_data[row]
            self.product_double_clicked.emit(product)

class InventoryPage(QWidget):
    """Enhanced inventory management page"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_products = []
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup inventory page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.setup_header(main_layout)
        
        # Statistics section
        self.stats_widget = InventoryStatsWidget(self.db_manager)
        main_layout.addWidget(self.stats_widget)
        
        # Search and filters section
        self.setup_search_filters(main_layout)
        
        # Main content (table and details)
        self.setup_main_content(main_layout)
        
    def setup_header(self, parent_layout):
        """Setup header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #4c51bf, stop:1 #667eea);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("📦 إدارة المخزون والمنتجات")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("إدارة شاملة للمنتجات والمخزون مع تتبع الكميات والأسعار")
        subtitle.setFont(QFont("Tahoma", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        add_product_btn = QPushButton("➕ إضافة منتج")
        add_product_btn.setFixedHeight(45)
        add_product_btn.setStyleSheet("""
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
        add_product_btn.clicked.connect(self.add_product)
        
        import_btn = QPushButton("📁 استيراد")
        import_btn.setFixedHeight(45)
        import_btn.setStyleSheet("""
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
        import_btn.clicked.connect(self.import_products)
        
        export_btn = QPushButton("📤 تصدير")
        export_btn.setFixedHeight(45)
        export_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        export_btn.clicked.connect(self.export_products)
        
        buttons_layout.addWidget(add_product_btn)
        buttons_layout.addWidget(import_btn)
        buttons_layout.addWidget(export_btn)
        buttons_layout.addStretch()
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(header_frame)
        
    def setup_search_filters(self, parent_layout):
        """Setup search and filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(ModernStyles.get_card_style())
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)
        
        # Search
        search_label = QLabel("🔍 البحث:")
        search_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث بالاسم، الكود، أو الماركة...")
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.textChanged.connect(self.filter_products)
        
        # Category filter
        category_label = QLabel("📂 الفئة:")
        category_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.category_filter = QComboBox()
        self.category_filter.setStyleSheet(ModernStyles.get_input_style())
        self.category_filter.currentTextChanged.connect(self.filter_products)
        
        # Brand filter
        brand_label = QLabel("🏷️ الماركة:")
        brand_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.brand_filter = QComboBox()
        self.brand_filter.setStyleSheet(ModernStyles.get_input_style())
        self.brand_filter.currentTextChanged.connect(self.filter_products)
        
        # Stock status filter
        status_label = QLabel("📊 حالة المخزون:")
        status_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "جميع المنتجات", "متوفر", "مخزون منخفض", "نفاد المخزون"
        ])
        self.status_filter.setStyleSheet(ModernStyles.get_input_style())
        self.status_filter.currentTextChanged.connect(self.filter_products)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        refresh_btn.clicked.connect(self.refresh_data)
        
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_input, 2)
        filters_layout.addWidget(category_label)
        filters_layout.addWidget(self.category_filter, 1)
        filters_layout.addWidget(brand_label)
        filters_layout.addWidget(self.brand_filter, 1)
        filters_layout.addWidget(status_label)
        filters_layout.addWidget(self.status_filter, 1)
        filters_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(filters_frame)
        
    def setup_main_content(self, parent_layout):
        """Setup main content area"""
        # Create splitter for table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Products table
        table_frame = QFrame()
        table_frame.setStyleSheet(ModernStyles.get_card_style())
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_header = QLabel("📋 قائمة المنتجات")
        table_header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        table_header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        
        self.products_table = ProductTableWidget()
        self.products_table.product_selected.connect(self.on_product_selected)
        self.products_table.product_double_clicked.connect(self.edit_product)
        
        table_layout.addWidget(table_header)
        table_layout.addWidget(self.products_table)
        
        # Product details panel
        self.details_frame = QFrame()
        self.details_frame.setStyleSheet(ModernStyles.get_card_style())
        self.details_frame.setFixedWidth(350)
        self.setup_details_panel()
        
        splitter.addWidget(table_frame)
        splitter.addWidget(self.details_frame)
        splitter.setSizes([800, 350])
        
        parent_layout.addWidget(splitter, 1)
        
    def setup_details_panel(self):
        """Setup product details panel"""
        layout = QVBoxLayout(self.details_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📄 تفاصيل المنتج")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Details area
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setSpacing(10)
        
        # Default message
        default_label = QLabel("اختر منتجاً من القائمة لعرض التفاصيل")
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_label.setStyleSheet("color: #9ca3af; font-style: italic; padding: 50px;")
        self.details_layout.addWidget(default_label)
        
        self.details_scroll.setWidget(self.details_widget)
        layout.addWidget(self.details_scroll, 1)
        
    def refresh_data(self):
        """Refresh all data"""
        try:
            # Refresh statistics
            self.stats_widget.update_statistics()
            
            # Refresh products
            self.refresh_products()
            
            # Refresh filters
            self.refresh_filters()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث البيانات: {str(e)}")
            
    def refresh_products(self):
        """Refresh products table"""
        try:
            products = self.db_manager.execute_query("""
                SELECT * FROM products 
                WHERE is_active = 1 
                ORDER BY created_at DESC
            """)
            
            self.current_products = products
            self.products_table.populate_table(products)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المنتجات: {str(e)}")
            
    def refresh_filters(self):
        """Refresh filter options"""
        try:
            # Get categories
            categories = self.db_manager.execute_query("""
                SELECT DISTINCT category FROM products 
                WHERE is_active = 1 AND category IS NOT NULL AND category != ''
                ORDER BY category
            """)
            
            self.category_filter.clear()
            self.category_filter.addItem("جميع الفئات")
            for cat in categories:
                self.category_filter.addItem(cat['category'])
            
            # Get brands
            brands = self.db_manager.execute_query("""
                SELECT DISTINCT brand FROM products 
                WHERE is_active = 1 AND brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """)
            
            self.brand_filter.clear()
            self.brand_filter.addItem("جميع الماركات")
            for brand in brands:
                self.brand_filter.addItem(brand['brand'])
                
        except Exception as e:
            print(f"Error refreshing filters: {e}")
            
    def filter_products(self):
        """Filter products based on search and filters"""
        try:
            search_text = self.search_input.text().lower()
            category = self.category_filter.currentText()
            brand = self.brand_filter.currentText()
            status = self.status_filter.currentText()
            
            filtered_products = []
            
            for product in self.current_products:
                # Apply search filter
                if search_text:
                    if not (search_text in product['name'].lower() or 
                           search_text in product['sku'].lower() or
                           search_text in (product['brand'] or '').lower()):
                        continue
                
                # Apply category filter
                if category != "جميع الفئات":
                    if product['category'] != category:
                        continue
                
                # Apply brand filter
                if brand != "جميع الماركات":
                    if product['brand'] != brand:
                        continue
                
                # Apply status filter
                if status != "جميع المنتجات":
                    if status == "متوفر" and product['current_qty'] <= product['min_stock']:
                        continue
                    elif status == "مخزون منخفض" and not (0 < product['current_qty'] <= product['min_stock']):
                        continue
                    elif status == "نفاد المخزون" and product['current_qty'] != 0:
                        continue
                
                filtered_products.append(product)
            
            self.products_table.populate_table(filtered_products)
            
        except Exception as e:
            print(f"Error filtering products: {e}")
            
    def on_product_selected(self, product):
        """Handle product selection"""
        try:
            # Clear existing details
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
            
            # Product image placeholder
            image_label = QLabel("📱")
            image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            image_label.setStyleSheet("""
                QLabel {
                    background-color: #f3f4f6;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 48px;
                }
            """)
            image_label.setFixedHeight(120)
            self.details_layout.addWidget(image_label)
            
            # Product name
            name_label = QLabel(product['name'])
            name_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
            name_label.setStyleSheet("color: #1f2937; margin: 10px 0;")
            name_label.setWordWrap(True)
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_layout.addWidget(name_label)
            
            # Details grid
            details_frame = QFrame()
            details_frame.setStyleSheet("""
                QFrame {
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            details_layout = QFormLayout(details_frame)
            details_layout.setSpacing(8)
            
            # Add details
            details_layout.addRow("الكود:", QLabel(product['sku']))
            details_layout.addRow("الفئة:", QLabel(product['category'] or 'غير محدد'))
            details_layout.addRow("الماركة:", QLabel(product['brand'] or 'غير محدد'))
            details_layout.addRow("سعر الشراء:", QLabel(f"{product['buy_price']:.2f} جنيه"))
            details_layout.addRow("سعر البيع:", QLabel(f"{product['sale_price']:.2f} جنيه"))
            
            # Profit calculation
            profit = product['sale_price'] - product['buy_price']
            profit_percentage = (profit / product['buy_price'] * 100) if product['buy_price'] > 0 else 0
            profit_label = QLabel(f"{profit:.2f} جنيه ({profit_percentage:.1f}%)")
            if profit_percentage >= 30:
                profit_label.setStyleSheet("color: #10b981; font-weight: bold;")
            elif profit_percentage >= 15:
                profit_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            else:
                profit_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            details_layout.addRow("الربح:", profit_label)
            
            # Stock info
            stock_label = QLabel(f"{product['current_qty']} / {product['min_stock']}")
            if product['current_qty'] == 0:
                stock_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            elif product['current_qty'] <= product['min_stock']:
                stock_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            else:
                stock_label.setStyleSheet("color: #10b981; font-weight: bold;")
            details_layout.addRow("المخزون / الحد الأدنى:", stock_label)
            
            # Inventory value
            inventory_value = product['current_qty'] * product['buy_price']
            details_layout.addRow("قيمة المخزون:", QLabel(f"{inventory_value:.2f} جنيه"))
            
            # Description
            if product.get('description'):
                desc_label = QLabel(product['description'])
                desc_label.setWordWrap(True)
                desc_label.setStyleSheet("color: #6b7280; margin-top: 10px;")
                details_layout.addRow("الوصف:", desc_label)
            
            self.details_layout.addWidget(details_frame)
            
            # Action buttons
            buttons_frame = QFrame()
            buttons_layout = QVBoxLayout(buttons_frame)
            buttons_layout.setSpacing(10)
            
            edit_btn = QPushButton("✏️ تعديل المنتج")
            edit_btn.setStyleSheet(ModernStyles.get_button_primary_style())
            edit_btn.clicked.connect(lambda: self.edit_product(product))
            
            stock_btn = QPushButton("📦 إدارة المخزون")
            stock_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
            stock_btn.clicked.connect(lambda: self.manage_stock(product))
            
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(stock_btn)
            
            self.details_layout.addWidget(buttons_frame)
            self.details_layout.addStretch()
            
        except Exception as e:
            print(f"Error displaying product details: {e}")
            
    def add_product(self):
        """Add new product"""
        dialog = AddProductDialog(self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def edit_product(self, product):
        """Edit existing product"""
        dialog = EditProductDialog(product, self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def manage_stock(self, product):
        """Manage product stock"""
        from ui.dialogs import StockManagementDialog
        
        dialog = StockManagementDialog(product, self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def import_products(self):
        """Import products from file"""
        dialog = ImportProductsDialog(self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def export_products(self):
        """Export products to file"""
        try:
            file_path, _ = QFileDialog.getSaveFileName(
                self, "تصدير المنتجات", 
                f"products_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv",
                "CSV files (*.csv)"
            )
            
            if file_path:
                products = self.db_manager.execute_query("""
                    SELECT * FROM products WHERE is_active = 1 ORDER BY name
                """)
                
                with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                    fieldnames = [
                        'sku', 'name', 'description', 'category', 'brand', 
                        'buy_price', 'sale_price', 'current_qty', 'min_stock'
                    ]
                    writer = csv.DictWriter(csvfile, fieldnames=fieldnames)
                    
                    writer.writeheader()
                    for product in products:
                        writer.writerow({
                            'sku': product['sku'],
                            'name': product['name'],
                            'description': product.get('description', ''),
                            'category': product.get('category', ''),
                            'brand': product.get('brand', ''),
                            'buy_price': product['buy_price'],
                            'sale_price': product['sale_price'],
                            'current_qty': product['current_qty'],
                            'min_stock': product['min_stock']
                        })
                
                QMessageBox.information(self, "نجح", f"تم تصدير {len(products)} منتج بنجاح")
                
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تصدير المنتجات: {str(e)}")
