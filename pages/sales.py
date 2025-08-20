"""
Enhanced Sales/POS Page for Mobile Shop Management System
Modern point of sale system with comprehensive features
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QHeaderView, QScrollArea, QProgressBar,
    QMessageBox, QDialog, QFormLayout, QGraphicsDropShadowEffect,
    QCheckBox, QGroupBox, QDateEdit, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon
from datetime import datetime, timedelta
from uuid import uuid4
import json

from ui.styles import ModernStyles
from ui.dialogs import CustomerSelectionDialog, PaymentDialog
from ui.widgets import StatCard, ProductSearchWidget

class SaleItemWidget(QFrame):
    """Individual sale item widget"""
    
    item_removed = pyqtSignal(dict)
    item_updated = pyqtSignal(dict)
    
    def __init__(self, product, quantity=1):
        super().__init__()
        self.product = product
        self.quantity = quantity
        self.setup_ui()
        
    def setup_ui(self):
        """Setup item widget UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                padding: 10px;
                margin: 2px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
            }
        """)
        
        layout = QHBoxLayout(self)
        layout.setContentsMargins(12, 8, 12, 8)
        layout.setSpacing(10)
        
        # Product info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(4)
        
        name_label = QLabel(self.product['name'])
        name_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #1f2937;")
        
        sku_label = QLabel(f"الكود: {self.product['sku']}")
        sku_label.setFont(QFont("Tahoma", 9))
        sku_label.setStyleSheet("color: #6b7280;")
        
        price_label = QLabel(f"السعر: {self.product['sale_price']:.2f} جنيه")
        price_label.setFont(QFont("Tahoma", 9))
        price_label.setStyleSheet("color: #059669; font-weight: bold;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(sku_label)
        info_layout.addWidget(price_label)
        
        # Quantity controls
        qty_layout = QVBoxLayout()
        qty_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        qty_label = QLabel("الكمية:")
        qty_label.setFont(QFont("Tahoma", 9))
        qty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.qty_spinbox = QSpinBox()
        self.qty_spinbox.setMinimum(1)
        self.qty_spinbox.setMaximum(self.product['current_qty'])
        self.qty_spinbox.setValue(self.quantity)
        self.qty_spinbox.setStyleSheet(ModernStyles.get_input_style())
        self.qty_spinbox.valueChanged.connect(self.update_quantity)
        
        qty_layout.addWidget(qty_label)
        qty_layout.addWidget(self.qty_spinbox)
        
        # Total price
        total_layout = QVBoxLayout()
        total_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        total_label = QLabel("الإجمالي:")
        total_label.setFont(QFont("Tahoma", 9))
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        self.total_label = QLabel(f"{self.get_total():.2f} جنيه")
        self.total_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #059669;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(self.total_label)
        
        # Remove button
        remove_btn = QPushButton("🗑️")
        remove_btn.setFixedSize(40, 40)
        remove_btn.setToolTip("إزالة من السلة")
        remove_btn.setStyleSheet("""
            QPushButton {
                background-color: #fef2f2;
                border: 1px solid #fecaca;
                border-radius: 20px;
                font-size: 16px;
                color: #dc2626;
            }
            QPushButton:hover {
                background-color: #fee2e2;
                border-color: #fca5a5;
            }
        """)
        remove_btn.clicked.connect(self.remove_item)
        
        layout.addLayout(info_layout, 3)
        layout.addLayout(qty_layout, 1)
        layout.addLayout(total_layout, 1)
        layout.addWidget(remove_btn)
        
    def get_total(self):
        """Get item total price"""
        return self.quantity * self.product['sale_price']
        
    def update_quantity(self, new_qty):
        """Update item quantity"""
        self.quantity = new_qty
        self.total_label.setText(f"{self.get_total():.2f} جنيه")
        self.item_updated.emit(self.get_item_data())
        
    def remove_item(self):
        """Remove item from cart"""
        self.item_removed.emit(self.get_item_data())
        
    def get_item_data(self):
        """Get item data"""
        return {
            'product': self.product,
            'quantity': self.quantity,
            'unit_price': self.product['sale_price'],
            'total': self.get_total()
        }

class SalesCartWidget(QFrame):
    """Sales cart widget"""
    
    cart_updated = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.cart_items = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup cart UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(15)
        
        # Header
        header_layout = QHBoxLayout()
        
        title = QLabel("🛒 سلة المشتريات")
        title.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        title.setStyleSheet("color: #374151;")
        
        self.items_count_label = QLabel("0 منتج")
        self.items_count_label.setFont(QFont("Tahoma", 10))
        self.items_count_label.setStyleSheet("color: #6b7280;")
        
        clear_btn = QPushButton("🗑️ مسح الكل")
        clear_btn.setStyleSheet(ModernStyles.get_button_danger_style())
        clear_btn.clicked.connect(self.clear_cart)
        
        header_layout.addWidget(title)
        header_layout.addWidget(self.items_count_label)
        header_layout.addStretch()
        header_layout.addWidget(clear_btn)
        
        layout.addLayout(header_layout)
        
        # Items scroll area
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_area.setStyleSheet("""
            QScrollArea {
                border: none;
                background-color: #f9fafb;
                border-radius: 8px;
            }
        """)
        
        self.items_widget = QWidget()
        self.items_layout = QVBoxLayout(self.items_widget)
        self.items_layout.setSpacing(5)
        self.items_layout.addStretch()
        
        self.scroll_area.setWidget(self.items_widget)
        layout.addWidget(self.scroll_area, 1)
        
        # Empty state
        self.empty_label = QLabel("السلة فارغة\nابدأ بإضافة المنتجات")
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("""
            QLabel {
                color: #9ca3af;
                font-size: 14px;
                padding: 50px;
                background-color: #f9fafb;
                border-radius: 8px;
                border: 2px dashed #d1d5db;
            }
        """)
        layout.addWidget(self.empty_label)
        
        self.update_empty_state()
        
    def add_product(self, product, quantity=1):
        """Add product to cart"""
        # Check if product already exists
        for i, item_widget in enumerate(self.get_item_widgets()):
            if item_widget.product['id'] == product['id']:
                # Update existing item
                new_qty = item_widget.quantity + quantity
                if new_qty <= product['current_qty']:
                    item_widget.qty_spinbox.setValue(new_qty)
                else:
                    QMessageBox.warning(self, "تحذير", f"الكمية المطلوبة غير متوفرة\nالمتاح: {product['current_qty']}")
                return
        
        # Add new item
        if quantity <= product['current_qty']:
            item_widget = SaleItemWidget(product, quantity)
            item_widget.item_removed.connect(self.remove_item)
            item_widget.item_updated.connect(lambda: self.cart_updated.emit())
            
            # Insert before stretch
            self.items_layout.insertWidget(self.items_layout.count() - 1, item_widget)
            self.update_cart()
        else:
            QMessageBox.warning(self, "تحذير", f"الكمية المطلوبة غير متوفرة\nالمتاح: {product['current_qty']}")
            
    def remove_item(self, item_data):
        """Remove item from cart"""
        for widget in self.get_item_widgets():
            if widget.product['id'] == item_data['product']['id']:
                widget.setParent(None)
                break
        self.update_cart()
        
    def clear_cart(self):
        """Clear all items from cart"""
        if self.cart_items:
            reply = QMessageBox.question(
                self, "تأكيد", "هل أنت متأكد من مسح جميع المنتجات من السلة؟"
            )
            if reply == QMessageBox.StandardButton.Yes:
                for widget in self.get_item_widgets():
                    widget.setParent(None)
                self.update_cart()
                
    def get_item_widgets(self):
        """Get all item widgets"""
        widgets = []
        for i in range(self.items_layout.count() - 1):  # Exclude stretch
            widget = self.items_layout.itemAt(i).widget()
            if isinstance(widget, SaleItemWidget):
                widgets.append(widget)
        return widgets
        
    def update_cart(self):
        """Update cart data and UI"""
        self.cart_items = []
        for widget in self.get_item_widgets():
            self.cart_items.append(widget.get_item_data())
        
        self.items_count_label.setText(f"{len(self.cart_items)} منتج")
        self.update_empty_state()
        self.cart_updated.emit()
        
    def update_empty_state(self):
        """Update empty state visibility"""
        has_items = len(self.get_item_widgets()) > 0
        self.scroll_area.setVisible(has_items)
        self.empty_label.setVisible(not has_items)
        
    def get_cart_total(self):
        """Get total cart value"""
        return sum(item['total'] for item in self.cart_items)
        
    def get_cart_count(self):
        """Get total items count"""
        return sum(item['quantity'] for item in self.cart_items)

class SalesTotalsWidget(QFrame):
    """Sales totals display widget"""
    
    checkout_clicked = pyqtSignal()
    
    def __init__(self):
        super().__init__()
        self.subtotal = 0.0
        self.discount = 0.0
        self.tax = 0.0
        self.total = 0.0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup totals UI"""
        self.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                    stop:0 #667eea, stop:1 #764ba2);
                border-radius: 15px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Title
        title = QLabel("💰 إجمالي الفاتورة")
        title.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Totals
        totals_layout = QFormLayout()
        totals_layout.setSpacing(10)
        
        # Subtotal
        self.subtotal_label = QLabel("0.00 جنيه")
        self.subtotal_label.setFont(QFont("Tahoma", 12))
        self.subtotal_label.setStyleSheet("color: white;")
        totals_layout.addRow("المجموع الفرعي:", self.subtotal_label)
        
        # Discount
        discount_layout = QHBoxLayout()
        self.discount_input = QDoubleSpinBox()
        self.discount_input.setRange(0, 100)
        self.discount_input.setSuffix("%")
        self.discount_input.setStyleSheet("""
            QDoubleSpinBox {
                background-color: white;
                border: none;
                border-radius: 4px;
                padding: 5px;
                font-weight: bold;
            }
        """)
        self.discount_input.valueChanged.connect(self.update_totals)
        
        self.discount_label = QLabel("0.00 جنيه")
        self.discount_label.setFont(QFont("Tahoma", 10))
        self.discount_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        discount_layout.addWidget(self.discount_input)
        discount_layout.addWidget(self.discount_label)
        totals_layout.addRow("الخصم:", discount_layout)
        
        # Tax (removed as requested)
        # self.tax_label = QLabel("0.00 جنيه")
        # self.tax_label.setFont(QFont("Tahoma", 12))
        # self.tax_label.setStyleSheet("color: white;")
        # totals_layout.addRow("الضريبة:", self.tax_label)
        
        # Total
        self.total_label = QLabel("0.00 جنيه")
        self.total_label.setFont(QFont("Tahoma", 18, QFont.Weight.Bold))
        self.total_label.setStyleSheet("color: #fbbf24; text-shadow: 0 1px 2px rgba(0,0,0,0.1);")
        totals_layout.addRow("الإجمالي النهائي:", self.total_label)
        
        layout.addLayout(totals_layout)
        
        # Checkout button
        self.checkout_btn = QPushButton("💳 إتمام البيع")
        self.checkout_btn.setFixedHeight(50)
        self.checkout_btn.setEnabled(False)
        self.checkout_btn.setStyleSheet("""
            QPushButton {
                background-color: #fbbf24;
                color: #1f2937;
                border: none;
                border-radius: 10px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover:enabled {
                background-color: #f59e0b;
            }
            QPushButton:disabled {
                background-color: rgba(255, 255, 255, 0.3);
                color: rgba(255, 255, 255, 0.6);
            }
        """)
        self.checkout_btn.clicked.connect(self.checkout_clicked.emit)
        
        layout.addWidget(self.checkout_btn)
        
    def update_totals(self, subtotal=None):
        """Update totals display"""
        if subtotal is not None:
            self.subtotal = subtotal
            
        # Calculate discount
        discount_percentage = self.discount_input.value()
        self.discount = self.subtotal * (discount_percentage / 100)
        
        # Calculate tax (removed)
        self.tax = 0.0
        
        # Calculate total
        self.total = self.subtotal - self.discount + self.tax
        
        # Update labels
        self.subtotal_label.setText(f"{self.subtotal:.2f} جنيه")
        self.discount_label.setText(f"{self.discount:.2f} جنيه")
        # self.tax_label.setText(f"{self.tax:.2f} جنيه")
        self.total_label.setText(f"{self.total:.2f} جنيه")
        
        # Enable/disable checkout button
        self.checkout_btn.setEnabled(self.total > 0)
        
    def get_totals_data(self):
        """Get totals data"""
        return {
            'subtotal': self.subtotal,
            'discount': self.discount,
            'discount_percentage': self.discount_input.value(),
            'tax': self.tax,
            'total': self.total
        }

class SalesPage(QWidget):
    """Enhanced sales/POS page"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.selected_customer = None
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup sales page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.setup_header(main_layout)
        
        # Main content
        content_layout = QHBoxLayout()
        content_layout.setSpacing(20)
        
        # Left side - Product selection and search
        left_widget = QWidget()
        left_layout = QVBoxLayout(left_widget)
        left_layout.setSpacing(15)
        
        self.setup_product_search(left_layout)
        self.setup_product_grid(left_layout)
        
        # Right side - Cart and totals
        right_widget = QWidget()
        right_layout = QVBoxLayout(right_widget)
        right_layout.setSpacing(15)
        
        self.setup_customer_section(right_layout)
        self.setup_cart(right_layout)
        self.setup_totals(right_layout)
        
        left_widget.setMinimumWidth(600)
        right_widget.setFixedWidth(400)
        
        content_layout.addWidget(left_widget, 2)
        content_layout.addWidget(right_widget, 1)
        
        main_layout.addLayout(content_layout, 1)
        
    def setup_header(self, parent_layout):
        """Setup header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("🛒 نظام نقاط البيع")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("نظام بيع حديث وسهل الاستخدام")
        subtitle.setFont(QFont("Tahoma", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Date and time
        self.datetime_label = QLabel()
        self.datetime_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        self.datetime_label.setStyleSheet("color: white;")
        self.datetime_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Update time
        self.time_timer = QTimer()
        self.time_timer.timeout.connect(self.update_datetime)
        self.time_timer.start(1000)
        self.update_datetime()
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addWidget(self.datetime_label)
        
        parent_layout.addWidget(header_frame)
        
    def setup_customer_section(self, parent_layout):
        """Setup customer selection section"""
        customer_frame = QFrame()
        customer_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(customer_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        title = QLabel("👤 العميل")
        title.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #374151;")
        
        select_btn = QPushButton("اختيار عميل")
        select_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        select_btn.clicked.connect(self.select_customer)
        
        header_layout.addWidget(title)
        header_layout.addStretch()
        header_layout.addWidget(select_btn)
        
        layout.addLayout(header_layout)
        
        # Customer info
        self.customer_info_label = QLabel("عميل نقدي (بدون تسجيل)")
        self.customer_info_label.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                padding: 10px;
                border-radius: 6px;
                color: #6b7280;
            }
        """)
        layout.addWidget(self.customer_info_label)
        
        parent_layout.addWidget(customer_frame)
        
    def setup_product_search(self, parent_layout):
        """Setup product search section"""
        search_frame = QFrame()
        search_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(search_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("🔍 البحث عن المنتجات")
        title.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #374151;")
        layout.addWidget(title)
        
        # Search input
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("ابحث بالاسم، الكود، أو امسح الباركود...")
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.textChanged.connect(self.filter_products)
        self.search_input.returnPressed.connect(self.quick_add_product)
        
        # Category filter
        self.category_filter = QComboBox()
        self.category_filter.setStyleSheet(ModernStyles.get_input_style())
        self.category_filter.currentTextChanged.connect(self.filter_products)
        
        search_layout.addWidget(self.search_input, 3)
        search_layout.addWidget(self.category_filter, 1)
        
        layout.addLayout(search_layout)
        
        parent_layout.addWidget(search_frame)
        
    def setup_product_grid(self, parent_layout):
        """Setup product grid section"""
        products_frame = QFrame()
        products_frame.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(products_frame)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Title
        title = QLabel("📱 المنتجات المتاحة")
        title.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        title.setStyleSheet("color: #374151;")
        layout.addWidget(title)
        
        # Products scroll area
        self.products_scroll = QScrollArea()
        self.products_scroll.setWidgetResizable(True)
        self.products_scroll.setStyleSheet(ModernStyles.get_scroll_area_style())
        
        self.products_widget = QWidget()
        self.products_layout = QGridLayout(self.products_widget)
        self.products_layout.setSpacing(10)
        
        self.products_scroll.setWidget(self.products_widget)
        layout.addWidget(self.products_scroll, 1)
        
        parent_layout.addWidget(products_frame, 1)
        
    def setup_cart(self, parent_layout):
        """Setup shopping cart"""
        self.cart_widget = SalesCartWidget()
        self.cart_widget.cart_updated.connect(self.update_totals)
        parent_layout.addWidget(self.cart_widget, 1)
        
    def setup_totals(self, parent_layout):
        """Setup totals section"""
        self.totals_widget = SalesTotalsWidget()
        self.totals_widget.checkout_clicked.connect(self.checkout)
        parent_layout.addWidget(self.totals_widget)
        
    def update_datetime(self):
        """Update date and time display"""
        now = datetime.now()
        date_str = now.strftime("%Y-%m-%d")
        time_str = now.strftime("%H:%M:%S")
        self.datetime_label.setText(f"📅 {date_str}\n🕐 {time_str}")
        
    def refresh_data(self):
        """Refresh page data"""
        self.load_products()
        self.load_categories()
        
    def load_products(self):
        """Load available products"""
        try:
            products = self.db_manager.execute_query("""
                SELECT * FROM products 
                WHERE is_active = 1 AND current_qty > 0
                ORDER BY name
            """)
            
            self.all_products = products
            self.display_products(products)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المنتجات: {str(e)}")
            
    def load_categories(self):
        """Load product categories"""
        try:
            categories = self.db_manager.execute_query("""
                SELECT DISTINCT category FROM products 
                WHERE is_active = 1 AND category IS NOT NULL AND category != ''
                ORDER BY category
            """)
            
            self.category_filter.clear()
            self.category_filter.addItem("جميع الفئات")
            for cat in categories:
                self.category_filter.addItem(cat['category'])
                
        except Exception as e:
            print(f"Error loading categories: {e}")
            
    def display_products(self, products):
        """Display products in grid"""
        # Clear existing products
        for i in reversed(range(self.products_layout.count())):
            self.products_layout.itemAt(i).widget().setParent(None)
        
        # Add products
        for i, product in enumerate(products[:20]):  # Limit to 20 for performance
            product_btn = self.create_product_button(product)
            row = i // 4
            col = i % 4
            self.products_layout.addWidget(product_btn, row, col)
            
    def create_product_button(self, product):
        """Create product selection button"""
        btn = QPushButton()
        btn.setFixedSize(140, 120)
        btn.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Create product info layout
        widget = QWidget()
        layout = QVBoxLayout(widget)
        layout.setContentsMargins(8, 8, 8, 8)
        layout.setSpacing(4)
        
        # Product image placeholder
        image_label = QLabel("📱")
        image_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        image_label.setStyleSheet("font-size: 32px;")
        
        # Product name
        name_label = QLabel(product['name'])
        name_label.setFont(QFont("Tahoma", 8, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #1f2937;")
        name_label.setWordWrap(True)
        name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Price
        price_label = QLabel(f"{product['sale_price']:.2f} جنيه")
        price_label.setFont(QFont("Tahoma", 9, QFont.Weight.Bold))
        price_label.setStyleSheet("color: #059669;")
        price_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Stock
        stock_label = QLabel(f"المتاح: {product['current_qty']}")
        stock_label.setFont(QFont("Tahoma", 7))
        stock_label.setStyleSheet("color: #6b7280;")
        stock_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(image_label)
        layout.addWidget(name_label)
        layout.addWidget(price_label)
        layout.addWidget(stock_label)
        
        # Set widget as button layout
        btn.setStyleSheet("""
            QPushButton {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 10px;
                padding: 5px;
            }
            QPushButton:hover {
                border-color: #3b82f6;
                background-color: #f8fafc;
                transform: translateY(-2px);
            }
            QPushButton:pressed {
                background-color: #e5e7eb;
                transform: translateY(0px);
            }
        """)
        
        # Set the product text
        btn.setText(f"{product['name']}\n{product['sale_price']:.2f} جنيه\nمتاح: {product['current_qty']}")
        btn.setFont(QFont("Tahoma", 8))
        
        # Connect click event
        btn.clicked.connect(lambda: self.add_to_cart(product))
        
        return btn
        
    def filter_products(self):
        """Filter products based on search and category"""
        search_text = self.search_input.text().lower()
        category = self.category_filter.currentText()
        
        filtered_products = []
        
        for product in self.all_products:
            # Apply search filter
            if search_text:
                if not (search_text in product['name'].lower() or 
                       search_text in product['sku'].lower() or
                       search_text in (product.get('barcode', '') or '').lower()):
                    continue
            
            # Apply category filter
            if category != "جميع الفئات":
                if product['category'] != category:
                    continue
            
            filtered_products.append(product)
        
        self.display_products(filtered_products)
        
    def quick_add_product(self):
        """Quick add product by search/barcode"""
        search_text = self.search_input.text().strip()
        if not search_text:
            return
            
        # Find exact match by SKU or barcode
        for product in self.all_products:
            if (product['sku'].lower() == search_text.lower() or 
                (product.get('barcode') and product['barcode'].lower() == search_text.lower())):
                self.add_to_cart(product)
                self.search_input.clear()
                return
        
        QMessageBox.information(self, "غير موجود", "لم يتم العثور على منتج بهذا الكود")
        
    def add_to_cart(self, product):
        """Add product to cart"""
        self.cart_widget.add_product(product)
        
    def update_totals(self):
        """Update totals display"""
        cart_total = self.cart_widget.get_cart_total()
        self.totals_widget.update_totals(cart_total)
        
    def select_customer(self):
        """Select customer for sale"""
        dialog = CustomerSelectionDialog(self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.selected_customer = dialog.get_selected_customer()
            if self.selected_customer:
                self.customer_info_label.setText(
                    f"👤 {self.selected_customer['name']}\n"
                    f"📞 {self.selected_customer['phone']}"
                )
                self.customer_info_label.setStyleSheet("""
                    QLabel {
                        background-color: #ecfdf5;
                        border: 1px solid #10b981;
                        padding: 10px;
                        border-radius: 6px;
                        color: #064e3b;
                    }
                """)
            else:
                self.customer_info_label.setText("عميل نقدي (بدون تسجيل)")
                self.customer_info_label.setStyleSheet("""
                    QLabel {
                        background-color: #f3f4f6;
                        padding: 10px;
                        border-radius: 6px;
                        color: #6b7280;
                    }
                """)
                
    def checkout(self):
        """Process checkout"""
        if not self.cart_widget.cart_items:
            QMessageBox.warning(self, "تحذير", "السلة فارغة!")
            return
            
        # Get totals
        totals_data = self.totals_widget.get_totals_data()
        
        # Show payment dialog
        dialog = PaymentDialog(totals_data, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            payment_data = dialog.get_payment_data()
            self.process_sale(totals_data, payment_data)
            
    def process_sale(self, totals_data, payment_data):
        """Process the sale transaction"""
        try:
            # Generate sale ID and number
            sale_id = str(uuid4())
            sale_number = f"S-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000:04d}"
            
            # Create sale record
            self.db_manager.execute_update("""
                INSERT INTO sales (
                    id, sale_number, customer_id, customer_name, customer_phone,
                    subtotal, discount, discount_percentage, tax, total,
                    paid_amount, change_amount, payment_method, payment_status,
                    notes, cashier
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                sale_id, sale_number,
                self.selected_customer['id'] if self.selected_customer else None,
                self.selected_customer['name'] if self.selected_customer else "عميل نقدي",
                self.selected_customer['phone'] if self.selected_customer else "",
                totals_data['subtotal'], totals_data['discount'], totals_data['discount_percentage'],
                totals_data['tax'], totals_data['total'],
                payment_data['paid_amount'], payment_data['change_amount'],
                payment_data['payment_method'], "paid",
                payment_data.get('notes', ''), "الكاشير"
            ))
            
            # Create sale items
            for item in self.cart_widget.cart_items:
                item_id = str(uuid4())
                product = item['product']
                
                self.db_manager.execute_update("""
                    INSERT INTO sale_items (
                        id, sale_id, product_id, product_name, product_sku,
                        qty, unit_price, discount, total, cost_price, profit
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    item_id, sale_id, product['id'], product['name'], product['sku'],
                    item['quantity'], item['unit_price'], 0, item['total'],
                    product['buy_price'], (item['unit_price'] - product['buy_price']) * item['quantity']
                ))
                
                # Update product quantity
                self.db_manager.execute_update("""
                    UPDATE products SET current_qty = current_qty - ? WHERE id = ?
                """, (item['quantity'], product['id']))
                
                # Log inventory movement
                movement_id = str(uuid4())
                self.db_manager.execute_update("""
                    INSERT INTO inventory_movements (
                        id, product_id, movement_type, quantity, cost_per_unit,
                        total_cost, reference_id, reference_type, notes, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    movement_id, product['id'], "sale", -item['quantity'], product['buy_price'],
                    product['buy_price'] * item['quantity'], sale_id, "sale",
                    f"مبيعات - فاتورة رقم {sale_number}", "الكاشير"
                ))
            
            # Show success message
            QMessageBox.information(
                self, "نجح", 
                f"تم إتمام البيع بنجاح!\n"
                f"رقم الفاتورة: {sale_number}\n"
                f"الإجمالي: {totals_data['total']:.2f} جنيه\n"
                f"المدفوع: {payment_data['paid_amount']:.2f} جنيه\n"
                f"الباقي: {payment_data['change_amount']:.2f} جنيه"
            )
            
            # Clear cart and reset
            self.cart_widget.clear_cart()
            self.selected_customer = None
            self.customer_info_label.setText("عميل نقدي (بدون تسجيل)")
            self.customer_info_label.setStyleSheet("""
                QLabel {
                    background-color: #f3f4f6;
                    padding: 10px;
                    border-radius: 6px;
                    color: #6b7280;
                }
            """)
            self.totals_widget.discount_input.setValue(0)
            
            # Refresh products (to update quantities)
            self.load_products()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في معالجة البيع: {str(e)}")
