"""
Enhanced Dialogs for Mobile Shop Management System
Comprehensive dialog components with modern UI and Arabic RTL support
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, QDate, pyqtSignal, QThread, QTimer
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon
from datetime import datetime, timedelta
from uuid import uuid4
import csv
import json
import os

from ui.styles import ModernStyles

class AddProductDialog(QDialog):
    """Dialog for adding new product"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إضافة منتج جديد")
        self.setModal(True)
        self.resize(600, 700)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("➕ إضافة منتج جديد")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll area for form
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Basic Information Group
        basic_group = QGroupBox("المعلومات الأساسية")
        basic_group.setStyleSheet(ModernStyles.get_group_box_style())
        basic_layout = QFormLayout(basic_group)
        basic_layout.setSpacing(10)
        
        self.sku_input = QLineEdit()
        self.sku_input.setStyleSheet(ModernStyles.get_input_style())
        self.sku_input.setPlaceholderText("سيتم توليده تلقائياً إذا ترك فارغاً")
        
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(ModernStyles.get_input_style())
        self.name_input.setPlaceholderText("أدخل اسم المنتج")
        
        self.description_input = QTextEdit()
        self.description_input.setStyleSheet(ModernStyles.get_input_style())
        self.description_input.setMaximumHeight(80)
        self.description_input.setPlaceholderText("وصف المنتج (اختياري)")
        
        basic_layout.addRow("الكود (SKU):", self.sku_input)
        basic_layout.addRow("اسم المنتج *:", self.name_input)
        basic_layout.addRow("الوصف:", self.description_input)
        
        # Category and Brand Group
        category_group = QGroupBox("التصنيف والماركة")
        category_group.setStyleSheet(ModernStyles.get_group_box_style())
        category_layout = QFormLayout(category_group)
        category_layout.setSpacing(10)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.setStyleSheet(ModernStyles.get_input_style())
        self.load_categories()
        
        self.subcategory_input = QComboBox()
        self.subcategory_input.setEditable(True)
        self.subcategory_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.brand_input = QComboBox()
        self.brand_input.setEditable(True)
        self.brand_input.setStyleSheet(ModernStyles.get_input_style())
        self.load_brands()
        
        self.barcode_input = QLineEdit()
        self.barcode_input.setStyleSheet(ModernStyles.get_input_style())
        self.barcode_input.setPlaceholderText("الباركود (اختياري)")
        
        category_layout.addRow("الفئة *:", self.category_input)
        category_layout.addRow("الفئة الفرعية:", self.subcategory_input)
        category_layout.addRow("الماركة:", self.brand_input)
        category_layout.addRow("الباركود:", self.barcode_input)
        
        # Pricing Group
        pricing_group = QGroupBox("الأسعار")
        pricing_group.setStyleSheet(ModernStyles.get_group_box_style())
        pricing_layout = QFormLayout(pricing_group)
        pricing_layout.setSpacing(10)
        
        self.buy_price_input = QDoubleSpinBox()
        self.buy_price_input.setRange(0, 999999)
        self.buy_price_input.setDecimals(2)
        self.buy_price_input.setSuffix(" جنيه")
        self.buy_price_input.setStyleSheet(ModernStyles.get_input_style())
        self.buy_price_input.valueChanged.connect(self.calculate_profit_margin)
        
        self.sale_price_input = QDoubleSpinBox()
        self.sale_price_input.setRange(0, 999999)
        self.sale_price_input.setDecimals(2)
        self.sale_price_input.setSuffix(" جنيه")
        self.sale_price_input.setStyleSheet(ModernStyles.get_input_style())
        self.sale_price_input.valueChanged.connect(self.calculate_profit_margin)
        
        self.profit_margin_label = QLabel("0%")
        self.profit_margin_label.setStyleSheet("color: #059669; font-weight: bold;")
        
        self.tax_rate_input = QDoubleSpinBox()
        self.tax_rate_input.setRange(0, 100)
        self.tax_rate_input.setDecimals(2)
        self.tax_rate_input.setSuffix(" %")
        self.tax_rate_input.setValue(14.0)
        self.tax_rate_input.setStyleSheet(ModernStyles.get_input_style())
        
        pricing_layout.addRow("سعر الشراء *:", self.buy_price_input)
        pricing_layout.addRow("سعر البيع *:", self.sale_price_input)
        pricing_layout.addRow("هامش الربح:", self.profit_margin_label)
        pricing_layout.addRow("معدل الضريبة:", self.tax_rate_input)
        
        # Inventory Group
        inventory_group = QGroupBox("إدارة المخزون")
        inventory_group.setStyleSheet(ModernStyles.get_group_box_style())
        inventory_layout = QFormLayout(inventory_group)
        inventory_layout.setSpacing(10)
        
        self.initial_qty_input = QSpinBox()
        self.initial_qty_input.setRange(0, 999999)
        self.initial_qty_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.min_stock_input = QSpinBox()
        self.min_stock_input.setRange(0, 999999)
        self.min_stock_input.setValue(5)
        self.min_stock_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.max_stock_input = QSpinBox()
        self.max_stock_input.setRange(0, 999999)
        self.max_stock_input.setValue(100)
        self.max_stock_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.location_input = QLineEdit()
        self.location_input.setStyleSheet(ModernStyles.get_input_style())
        self.location_input.setPlaceholderText("موقع المنتج في المخزن")
        
        inventory_layout.addRow("الكمية الأولية:", self.initial_qty_input)
        inventory_layout.addRow("الحد الأدنى *:", self.min_stock_input)
        inventory_layout.addRow("الحد الأقصى:", self.max_stock_input)
        inventory_layout.addRow("الموقع:", self.location_input)
        
        # Additional Information Group
        additional_group = QGroupBox("معلومات إضافية")
        additional_group.setStyleSheet(ModernStyles.get_group_box_style())
        additional_layout = QFormLayout(additional_group)
        additional_layout.setSpacing(10)
        
        self.supplier_input = QComboBox()
        self.supplier_input.setEditable(True)
        self.supplier_input.setStyleSheet(ModernStyles.get_input_style())
        self.load_suppliers()
        
        self.warranty_input = QSpinBox()
        self.warranty_input.setRange(0, 120)
        self.warranty_input.setValue(6)
        self.warranty_input.setSuffix(" شهر")
        self.warranty_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.is_active_checkbox = QCheckBox("المنتج نشط")
        self.is_active_checkbox.setChecked(True)
        self.is_active_checkbox.setStyleSheet("font-weight: bold;")
        
        additional_layout.addRow("المورد:", self.supplier_input)
        additional_layout.addRow("فترة الضمان:", self.warranty_input)
        additional_layout.addRow("", self.is_active_checkbox)
        
        # Add all groups to form
        form_layout.addWidget(basic_group)
        form_layout.addWidget(category_group)
        form_layout.addWidget(pricing_group)
        form_layout.addWidget(inventory_group)
        form_layout.addWidget(additional_group)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.save_product)
        buttons.rejected.connect(self.reject)
        
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
    def load_categories(self):
        """Load existing categories"""
        try:
            categories = self.db_manager.execute_query("""
                SELECT DISTINCT category FROM products 
                WHERE is_active = 1 AND category IS NOT NULL AND category != ''
                ORDER BY category
            """)
            
            self.category_input.clear()
            self.category_input.addItem("")
            for cat in categories:
                self.category_input.addItem(cat['category'])
        except:
            pass
            
    def load_brands(self):
        """Load existing brands"""
        try:
            brands = self.db_manager.execute_query("""
                SELECT DISTINCT brand FROM products 
                WHERE is_active = 1 AND brand IS NOT NULL AND brand != ''
                ORDER BY brand
            """)
            
            self.brand_input.clear()
            self.brand_input.addItem("")
            for brand in brands:
                self.brand_input.addItem(brand['brand'])
        except:
            pass
            
    def load_suppliers(self):
        """Load existing suppliers"""
        try:
            suppliers = self.db_manager.execute_query("""
                SELECT name FROM suppliers 
                WHERE is_active = 1
                ORDER BY name
            """)
            
            self.supplier_input.clear()
            self.supplier_input.addItem("")
            for supplier in suppliers:
                self.supplier_input.addItem(supplier['name'])
        except:
            pass
            
    def calculate_profit_margin(self):
        """Calculate and display profit margin"""
        buy_price = self.buy_price_input.value()
        sale_price = self.sale_price_input.value()
        
        if buy_price > 0:
            profit_margin = ((sale_price - buy_price) / buy_price) * 100
            self.profit_margin_label.setText(f"{profit_margin:.1f}%")
            
            if profit_margin >= 30:
                self.profit_margin_label.setStyleSheet("color: #059669; font-weight: bold;")
            elif profit_margin >= 15:
                self.profit_margin_label.setStyleSheet("color: #d97706; font-weight: bold;")
            else:
                self.profit_margin_label.setStyleSheet("color: #dc2626; font-weight: bold;")
        else:
            self.profit_margin_label.setText("0%")
            
    def validate_input(self):
        """Validate form input"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم المنتج")
            return False
            
        if not self.category_input.currentText().strip():
            QMessageBox.warning(self, "خطأ", "يرجى اختيار فئة المنتج")
            return False
            
        if self.buy_price_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال سعر شراء صحيح")
            return False
            
        if self.sale_price_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال سعر بيع صحيح")
            return False
            
        if self.min_stock_input.value() < 0:
            QMessageBox.warning(self, "خطأ", "الحد الأدنى للمخزون لا يمكن أن يكون سالباً")
            return False
            
        return True
        
    def save_product(self):
        """Save new product"""
        if not self.validate_input():
            return
            
        try:
            # Generate SKU if not provided
            sku = self.sku_input.text().strip()
            if not sku:
                sku = f"PRD-{int(datetime.now().timestamp())}"
                
            # Check if SKU already exists
            existing = self.db_manager.execute_query(
                "SELECT id FROM products WHERE sku = ?", (sku,)
            )
            if existing:
                QMessageBox.warning(self, "خطأ", "كود المنتج موجود بالفعل")
                return
            
            product_id = str(uuid4())
            
            # Calculate profit margin
            buy_price = self.buy_price_input.value()
            sale_price = self.sale_price_input.value()
            profit_margin = ((sale_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
            
            self.db_manager.execute_update("""
                INSERT INTO products (
                    id, sku, name, description, category, subcategory, brand, barcode,
                    buy_price, sale_price, current_qty, min_stock, max_stock, location,
                    supplier, warranty_months, is_active, tax_rate, profit_margin
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                product_id, sku, self.name_input.text().strip(),
                self.description_input.toPlainText().strip(),
                self.category_input.currentText().strip(),
                self.subcategory_input.currentText().strip(),
                self.brand_input.currentText().strip(),
                self.barcode_input.text().strip(),
                buy_price, sale_price,
                self.initial_qty_input.value(),
                self.min_stock_input.value(),
                self.max_stock_input.value(),
                self.location_input.text().strip(),
                self.supplier_input.currentText().strip(),
                self.warranty_input.value(),
                self.is_active_checkbox.isChecked(),
                self.tax_rate_input.value(),
                profit_margin
            ))
            
            # Log initial inventory movement if quantity > 0
            if self.initial_qty_input.value() > 0:
                movement_id = str(uuid4())
                self.db_manager.execute_update("""
                    INSERT INTO inventory_movements (
                        id, product_id, movement_type, quantity, cost_per_unit,
                        total_cost, reference_type, notes, created_by
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    movement_id, product_id, "initial_stock", 
                    self.initial_qty_input.value(), buy_price,
                    self.initial_qty_input.value() * buy_price,
                    "product_creation", "مخزون أولي عند إنشاء المنتج", "النظام"
                ))
            
            QMessageBox.information(self, "نجح", "تم إضافة المنتج بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المنتج: {str(e)}")

class EditProductDialog(AddProductDialog):
    """Dialog for editing existing product"""
    
    def __init__(self, product, db_manager, parent=None):
        self.product = product
        super().__init__(db_manager, parent)
        self.setWindowTitle("تعديل المنتج")
        self.load_product_data()
        
    def setup_ui(self):
        """Setup dialog UI"""
        super().setup_ui()
        
        # Change header
        header = self.findChild(QLabel)
        if header:
            header.setText("✏️ تعديل المنتج")
            
        # Change save button text
        buttons = self.findChild(QDialogButtonBox)
        if buttons:
            save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
            if save_btn:
                save_btn.setText("حفظ التغييرات")
        
    def load_product_data(self):
        """Load product data into form"""
        try:
            self.sku_input.setText(self.product['sku'])
            self.sku_input.setReadOnly(True)  # SKU shouldn't be changed
            
            self.name_input.setText(self.product['name'])
            self.description_input.setPlainText(self.product.get('description', ''))
            
            # Set category
            if self.product.get('category'):
                index = self.category_input.findText(self.product['category'])
                if index >= 0:
                    self.category_input.setCurrentIndex(index)
                else:
                    self.category_input.setCurrentText(self.product['category'])
                    
            # Set subcategory
            if self.product.get('subcategory'):
                self.subcategory_input.setCurrentText(self.product['subcategory'])
                
            # Set brand
            if self.product.get('brand'):
                index = self.brand_input.findText(self.product['brand'])
                if index >= 0:
                    self.brand_input.setCurrentIndex(index)
                else:
                    self.brand_input.setCurrentText(self.product['brand'])
                    
            self.barcode_input.setText(self.product.get('barcode', ''))
            
            self.buy_price_input.setValue(self.product['buy_price'])
            self.sale_price_input.setValue(self.product['sale_price'])
            self.tax_rate_input.setValue(self.product.get('tax_rate', 14.0))
            
            # Inventory fields - don't change current_qty here
            self.initial_qty_input.setValue(self.product['current_qty'])
            self.initial_qty_input.setEnabled(False)  # Current qty managed elsewhere
            self.initial_qty_input.setToolTip("استخدم إدارة المخزون لتعديل الكمية")
            
            self.min_stock_input.setValue(self.product['min_stock'])
            self.max_stock_input.setValue(self.product.get('max_stock', 100))
            self.location_input.setText(self.product.get('location', ''))
            
            # Set supplier
            if self.product.get('supplier'):
                self.supplier_input.setCurrentText(self.product['supplier'])
                
            self.warranty_input.setValue(self.product.get('warranty_months', 6))
            self.is_active_checkbox.setChecked(self.product.get('is_active', True))
            
            # Calculate profit margin
            self.calculate_profit_margin()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات المنتج: {str(e)}")
            
    def save_product(self):
        """Update existing product"""
        if not self.validate_input():
            return
            
        try:
            # Calculate profit margin
            buy_price = self.buy_price_input.value()
            sale_price = self.sale_price_input.value()
            profit_margin = ((sale_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
            
            self.db_manager.execute_update("""
                UPDATE products SET
                    name = ?, description = ?, category = ?, subcategory = ?, brand = ?, barcode = ?,
                    buy_price = ?, sale_price = ?, min_stock = ?, max_stock = ?, location = ?,
                    supplier = ?, warranty_months = ?, is_active = ?, tax_rate = ?, profit_margin = ?,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (
                self.name_input.text().strip(),
                self.description_input.toPlainText().strip(),
                self.category_input.currentText().strip(),
                self.subcategory_input.currentText().strip(),
                self.brand_input.currentText().strip(),
                self.barcode_input.text().strip(),
                buy_price, sale_price,
                self.min_stock_input.value(),
                self.max_stock_input.value(),
                self.location_input.text().strip(),
                self.supplier_input.currentText().strip(),
                self.warranty_input.value(),
                self.is_active_checkbox.isChecked(),
                self.tax_rate_input.value(),
                profit_margin,
                self.product['id']
            ))
            
            QMessageBox.information(self, "نجح", "تم تحديث المنتج بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث المنتج: {str(e)}")

class StockManagementDialog(QDialog):
    """Dialog for managing product stock"""
    
    def __init__(self, product, db_manager, parent=None):
        super().__init__(parent)
        self.product = product
        self.db_manager = db_manager
        self.setWindowTitle(f"إدارة مخزون - {product['name']}")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"📦 إدارة مخزون - {self.product['name']}")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Current stock info
        info_frame = QFrame()
        info_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        info_layout = QFormLayout(info_frame)
        info_layout.addRow("الكمية الحالية:", QLabel(f"{self.product['current_qty']} قطعة"))
        info_layout.addRow("الحد الأدنى:", QLabel(f"{self.product['min_stock']} قطعة"))
        info_layout.addRow("سعر الشراء:", QLabel(f"{self.product['buy_price']:.2f} جنيه"))
        
        layout.addWidget(info_frame)
        
        # Stock adjustment form
        adjustment_group = QGroupBox("تعديل المخزون")
        adjustment_group.setStyleSheet(ModernStyles.get_group_box_style())
        adjustment_layout = QFormLayout(adjustment_group)
        
        self.movement_type = QComboBox()
        self.movement_type.addItems([
            ("إضافة مخزون", "stock_in"),
            ("خصم مخزون", "stock_out"),
            ("تصحيح مخزون", "adjustment"),
            ("إتلاف مخزون", "damage"),
            ("إرجاع للمورد", "return_to_supplier")
        ])
        self.movement_type.setStyleSheet(ModernStyles.get_input_style())
        
        self.quantity_input = QSpinBox()
        self.quantity_input.setRange(1, 99999)
        self.quantity_input.setStyleSheet(ModernStyles.get_input_style())
        self.quantity_input.valueChanged.connect(self.calculate_totals)
        
        self.cost_per_unit_input = QDoubleSpinBox()
        self.cost_per_unit_input.setRange(0, 999999)
        self.cost_per_unit_input.setDecimals(2)
        self.cost_per_unit_input.setValue(self.product['buy_price'])
        self.cost_per_unit_input.setSuffix(" جنيه")
        self.cost_per_unit_input.setStyleSheet(ModernStyles.get_input_style())
        self.cost_per_unit_input.valueChanged.connect(self.calculate_totals)
        
        self.total_cost_label = QLabel("0.00 جنيه")
        self.total_cost_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
        
        self.reference_input = QLineEdit()
        self.reference_input.setStyleSheet(ModernStyles.get_input_style())
        self.reference_input.setPlaceholderText("رقم الفاتورة أو المرجع")
        
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(ModernStyles.get_input_style())
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("ملاحظات...")
        
        adjustment_layout.addRow("نوع الحركة:", self.movement_type)
        adjustment_layout.addRow("الكمية:", self.quantity_input)
        adjustment_layout.addRow("التكلفة للقطعة:", self.cost_per_unit_input)
        adjustment_layout.addRow("إجمالي التكلفة:", self.total_cost_label)
        adjustment_layout.addRow("رقم المرجع:", self.reference_input)
        adjustment_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addWidget(adjustment_group)
        
        # New stock preview
        self.preview_label = QLabel()
        self.preview_label.setStyleSheet("""
            QLabel {
                background-color: #fef3c7;
                border: 1px solid #f59e0b;
                border-radius: 6px;
                padding: 10px;
                font-weight: bold;
                text-align: center;
            }
        """)
        self.preview_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.update_preview()
        layout.addWidget(self.preview_label)
        
        # Connect signals
        self.movement_type.currentTextChanged.connect(self.update_preview)
        self.quantity_input.valueChanged.connect(self.update_preview)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("تطبيق التغيير")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.apply_stock_change)
        buttons.rejected.connect(self.reject)
        
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
    def calculate_totals(self):
        """Calculate total cost"""
        quantity = self.quantity_input.value()
        cost_per_unit = self.cost_per_unit_input.value()
        total_cost = quantity * cost_per_unit
        self.total_cost_label.setText(f"{total_cost:.2f} جنيه")
        
    def update_preview(self):
        """Update new stock preview"""
        current_qty = self.product['current_qty']
        quantity = self.quantity_input.value()
        movement_type = self.movement_type.currentData()
        
        if movement_type in ['stock_in', 'adjustment']:
            new_qty = current_qty + quantity
        else:  # stock_out, damage, return_to_supplier
            new_qty = current_qty - quantity
            
        if new_qty < 0:
            self.preview_label.setText(f"⚠️ تحذير: الكمية الجديدة ستكون سالبة ({new_qty})")
            self.preview_label.setStyleSheet("""
                QLabel {
                    background-color: #fef2f2;
                    border: 1px solid #ef4444;
                    border-radius: 6px;
                    padding: 10px;
                    font-weight: bold;
                    color: #dc2626;
                    text-align: center;
                }
            """)
        else:
            self.preview_label.setText(f"الكمية الجديدة: {new_qty} قطعة")
            if new_qty <= self.product['min_stock']:
                self.preview_label.setStyleSheet("""
                    QLabel {
                        background-color: #fef3c7;
                        border: 1px solid #f59e0b;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                        color: #92400e;
                        text-align: center;
                    }
                """)
            else:
                self.preview_label.setStyleSheet("""
                    QLabel {
                        background-color: #dcfce7;
                        border: 1px solid #16a34a;
                        border-radius: 6px;
                        padding: 10px;
                        font-weight: bold;
                        color: #15803d;
                        text-align: center;
                    }
                """)
                
    def apply_stock_change(self):
        """Apply stock change"""
        try:
            current_qty = self.product['current_qty']
            quantity = self.quantity_input.value()
            movement_type_data = self.movement_type.currentData()
            
            # Calculate new quantity
            if movement_type_data in ['stock_in', 'adjustment']:
                new_qty = current_qty + quantity
                movement_qty = quantity
            else:  # stock_out, damage, return_to_supplier
                new_qty = current_qty - quantity
                movement_qty = -quantity
                
            if new_qty < 0:
                reply = QMessageBox.question(
                    self, "تحذير",
                    "الكمية الجديدة ستكون سالبة. هل تريد المتابعة؟",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
                )
                if reply == QMessageBox.StandardButton.No:
                    return
            
            # Update product quantity
            self.db_manager.execute_update("""
                UPDATE products SET current_qty = ?, last_updated = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (new_qty, self.product['id']))
            
            # Log inventory movement
            movement_id = str(uuid4())
            self.db_manager.execute_update("""
                INSERT INTO inventory_movements (
                    id, product_id, movement_type, quantity, cost_per_unit,
                    total_cost, reference_id, reference_type, notes, created_by
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                movement_id, self.product['id'], movement_type_data,
                movement_qty, self.cost_per_unit_input.value(),
                abs(movement_qty) * self.cost_per_unit_input.value(),
                self.reference_input.text().strip(),
                "manual_adjustment",
                self.notes_input.toPlainText().strip(),
                "المدير"
            ))
            
            QMessageBox.information(self, "نجح", "تم تطبيق التغيير بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تطبيق التغيير: {str(e)}")

class ImportProductsDialog(QDialog):
    """Dialog for importing products from CSV file"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("استيراد المنتجات")
        self.setModal(True)
        self.resize(700, 500)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("📁 استيراد المنتجات من ملف CSV")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # File selection
        file_frame = QFrame()
        file_frame.setStyleSheet(ModernStyles.get_card_style())
        file_layout = QHBoxLayout(file_frame)
        
        self.file_path_input = QLineEdit()
        self.file_path_input.setStyleSheet(ModernStyles.get_input_style())
        self.file_path_input.setPlaceholderText("اختر ملف CSV...")
        self.file_path_input.setReadOnly(True)
        
        browse_btn = QPushButton("تصفح")
        browse_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        browse_btn.clicked.connect(self.browse_file)
        
        file_layout.addWidget(QLabel("ملف CSV:"))
        file_layout.addWidget(self.file_path_input, 1)
        file_layout.addWidget(browse_btn)
        
        layout.addWidget(file_frame)
        
        # Preview table
        self.preview_table = QTableWidget()
        self.preview_table.setStyleSheet(ModernStyles.get_table_style())
        self.preview_table.setMaximumHeight(200)
        layout.addWidget(QLabel("معاينة البيانات:"))
        layout.addWidget(self.preview_table)
        
        # Import options
        options_frame = QFrame()
        options_frame.setStyleSheet(ModernStyles.get_card_style())
        options_layout = QFormLayout(options_frame)
        
        self.skip_first_row = QCheckBox("تخطي الصف الأول (العناوين)")
        self.skip_first_row.setChecked(True)
        
        self.update_existing = QCheckBox("تحديث المنتجات الموجودة")
        self.update_existing.setChecked(True)
        
        options_layout.addRow("", self.skip_first_row)
        options_layout.addRow("", self.update_existing)
        
        layout.addWidget(options_frame)
        
        # Progress
        self.progress_bar = QProgressBar()
        self.progress_bar.setVisible(False)
        layout.addWidget(self.progress_bar)
        
        self.status_label = QLabel("")
        self.status_label.setStyleSheet("color: #059669; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("استيراد")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        buttons.accepted.connect(self.import_products)
        buttons.rejected.connect(self.reject)
        
        import_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        import_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        self.buttons = buttons
        layout.addWidget(buttons)
        
    def browse_file(self):
        """Browse for CSV file"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر ملف CSV", "", "CSV files (*.csv)"
        )
        
        if file_path:
            self.file_path_input.setText(file_path)
            self.load_preview(file_path)
            
    def load_preview(self, file_path):
        """Load file preview"""
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                
            if not rows:
                QMessageBox.warning(self, "خطأ", "الملف فارغ")
                return
                
            # Setup preview table
            self.preview_table.setRowCount(min(5, len(rows)))
            self.preview_table.setColumnCount(len(rows[0]))
            
            # Set headers
            headers = ['الكود', 'الاسم', 'الوصف', 'الفئة', 'الماركة', 'سعر الشراء', 'سعر البيع', 'الكمية', 'الحد الأدنى']
            self.preview_table.setHorizontalHeaderLabels(headers[:len(rows[0])])
            
            # Fill preview data
            for i, row in enumerate(rows[:5]):
                for j, cell in enumerate(row):
                    self.preview_table.setItem(i, j, QTableWidgetItem(str(cell)))
                    
            self.preview_table.resizeColumnsToContents()
            self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.status_label.setText(f"جاهز لاستيراد {len(rows)} صف")
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في قراءة الملف: {str(e)}")
            
    def import_products(self):
        """Import products from CSV"""
        if not self.file_path_input.text():
            QMessageBox.warning(self, "تحذير", "يرجى اختيار ملف CSV")
            return
            
        try:
            with open(self.file_path_input.text(), 'r', encoding='utf-8') as file:
                csv_reader = csv.reader(file)
                rows = list(csv_reader)
                
            if self.skip_first_row.isChecked() and rows:
                rows = rows[1:]
                
            self.progress_bar.setVisible(True)
            self.progress_bar.setMaximum(len(rows))
            
            imported_count = 0
            updated_count = 0
            error_count = 0
            
            for i, row in enumerate(rows):
                self.progress_bar.setValue(i + 1)
                self.status_label.setText(f"معالجة الصف {i + 1} من {len(rows)}")
                
                try:
                    if len(row) < 6:  # Minimum required columns
                        error_count += 1
                        continue
                        
                    sku = row[0].strip() if len(row) > 0 else f"IMP-{int(datetime.now().timestamp())}-{i}"
                    name = row[1].strip() if len(row) > 1 else ""
                    description = row[2].strip() if len(row) > 2 else ""
                    category = row[3].strip() if len(row) > 3 else ""
                    brand = row[4].strip() if len(row) > 4 else ""
                    
                    try:
                        buy_price = float(row[5]) if len(row) > 5 and row[5].strip() else 0
                        sale_price = float(row[6]) if len(row) > 6 and row[6].strip() else 0
                        quantity = int(row[7]) if len(row) > 7 and row[7].strip() else 0
                        min_stock = int(row[8]) if len(row) > 8 and row[8].strip() else 5
                    except ValueError:
                        error_count += 1
                        continue
                        
                    if not name or buy_price <= 0 or sale_price <= 0:
                        error_count += 1
                        continue
                        
                    # Check if product exists
                    existing = self.db_manager.execute_query(
                        "SELECT id FROM products WHERE sku = ?", (sku,)
                    )
                    
                    if existing and self.update_existing.isChecked():
                        # Update existing product
                        self.db_manager.execute_update("""
                            UPDATE products SET
                                name = ?, description = ?, category = ?, brand = ?,
                                buy_price = ?, sale_price = ?, min_stock = ?,
                                last_updated = CURRENT_TIMESTAMP
                            WHERE sku = ?
                        """, (name, description, category, brand, buy_price, sale_price, min_stock, sku))
                        updated_count += 1
                        
                    elif not existing:
                        # Insert new product
                        product_id = str(uuid4())
                        profit_margin = ((sale_price - buy_price) / buy_price * 100) if buy_price > 0 else 0
                        
                        self.db_manager.execute_update("""
                            INSERT INTO products (
                                id, sku, name, description, category, brand,
                                buy_price, sale_price, current_qty, min_stock, profit_margin, is_active
                            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                        """, (product_id, sku, name, description, category, brand, 
                             buy_price, sale_price, quantity, min_stock, profit_margin, True))
                        
                        # Log initial inventory
                        if quantity > 0:
                            movement_id = str(uuid4())
                            self.db_manager.execute_update("""
                                INSERT INTO inventory_movements (
                                    id, product_id, movement_type, quantity, cost_per_unit,
                                    total_cost, reference_type, notes, created_by
                                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                            """, (movement_id, product_id, "import", quantity, buy_price,
                                 quantity * buy_price, "csv_import", "استيراد من ملف CSV", "النظام"))
                        
                        imported_count += 1
                        
                except Exception as e:
                    error_count += 1
                    print(f"Error processing row {i}: {e}")
                    
            self.progress_bar.setVisible(False)
            
            message = f"تم الانتهاء من الاستيراد:\n"
            message += f"منتجات جديدة: {imported_count}\n"
            message += f"منتجات محدثة: {updated_count}\n"
            if error_count > 0:
                message += f"أخطاء: {error_count}"
                
            QMessageBox.information(self, "اكتمل الاستيراد", message)
            self.accept()
            
        except Exception as e:
            self.progress_bar.setVisible(False)
            QMessageBox.critical(self, "خطأ", f"فشل في استيراد المنتجات: {str(e)}")

class AddRepairDialog(QDialog):
    """Dialog for adding new repair"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إضافة إصلاح جديد")
        self.setModal(True)
        self.resize(600, 800)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("🔧 إضافة إصلاح جديد")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Scroll area
        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setStyleSheet("QScrollArea { border: none; }")
        
        form_widget = QWidget()
        form_layout = QVBoxLayout(form_widget)
        form_layout.setSpacing(15)
        
        # Customer Information
        customer_group = QGroupBox("معلومات العميل")
        customer_group.setStyleSheet(ModernStyles.get_group_box_style())
        customer_layout = QFormLayout(customer_group)
        
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setStyleSheet(ModernStyles.get_input_style())
        self.customer_name_input.setPlaceholderText("اسم العميل")
        
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setStyleSheet(ModernStyles.get_input_style())
        self.customer_phone_input.setPlaceholderText("01xxxxxxxxx")
        
        self.customer_email_input = QLineEdit()
        self.customer_email_input.setStyleSheet(ModernStyles.get_input_style())
        self.customer_email_input.setPlaceholderText("email@example.com")
        
        customer_layout.addRow("اسم العميل *:", self.customer_name_input)
        customer_layout.addRow("رقم الهاتف:", self.customer_phone_input)
        customer_layout.addRow("البريد الإلكتروني:", self.customer_email_input)
        
        # Device Information
        device_group = QGroupBox("معلومات الجهاز")
        device_group.setStyleSheet(ModernStyles.get_group_box_style())
        device_layout = QFormLayout(device_group)
        
        self.device_type_input = QComboBox()
        self.device_type_input.setEditable(True)
        self.device_type_input.addItems([
            "iPhone", "Samsung", "Huawei", "Xiaomi", "Oppo", "Vivo", 
            "Realme", "OnePlus", "Google Pixel", "Nokia", "أخرى"
        ])
        self.device_type_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.device_model_input = QLineEdit()
        self.device_model_input.setStyleSheet(ModernStyles.get_input_style())
        self.device_model_input.setPlaceholderText("iPhone 13 Pro")
        
        self.device_serial_input = QLineEdit()
        self.device_serial_input.setStyleSheet(ModernStyles.get_input_style())
        self.device_serial_input.setPlaceholderText("الرقم التسلسلي أو IMEI")
        
        self.device_color_input = QLineEdit()
        self.device_color_input.setStyleSheet(ModernStyles.get_input_style())
        self.device_color_input.setPlaceholderText("أبيض، أسود، ذهبي...")
        
        self.device_password_input = QLineEdit()
        self.device_password_input.setStyleSheet(ModernStyles.get_input_style())
        self.device_password_input.setPlaceholderText("كلمة مرور الجهاز (اختياري)")
        self.device_password_input.setEchoMode(QLineEdit.EchoMode.Password)
        
        device_layout.addRow("نوع الجهاز *:", self.device_type_input)
        device_layout.addRow("موديل الجهاز:", self.device_model_input)
        device_layout.addRow("الرقم التسلسلي:", self.device_serial_input)
        device_layout.addRow("لون الجهاز:", self.device_color_input)
        device_layout.addRow("كلمة المرور:", self.device_password_input)
        
        # Repair Information
        repair_group = QGroupBox("معلومات الإصلاح")
        repair_group.setStyleSheet(ModernStyles.get_group_box_style())
        repair_layout = QFormLayout(repair_group)
        
        self.problem_description_input = QTextEdit()
        self.problem_description_input.setStyleSheet(ModernStyles.get_input_style())
        self.problem_description_input.setMaximumHeight(100)
        self.problem_description_input.setPlaceholderText("وصف تفصيلي للمشكلة...")
        
        self.repair_type_input = QComboBox()
        self.repair_type_input.setEditable(True)
        self.repair_type_input.addItems([
            "إصلاح شاشة", "تغيير بطارية", "إصلاح مكبر صوت", 
            "إصلاح مايكروفون", "إصلاح كاميرا", "إصلاح شحن",
            "تحديث سوفتوير", "فك تشفير", "إصلاح زر الهوم",
            "إصلاح مستشعر البصمة", "تنظيف داخلي", "أخرى"
        ])
        self.repair_type_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.priority_input = QComboBox()
        self.priority_input.addItems(["عادي", "مستعجل", "طارئ"])
        self.priority_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.estimated_cost_input = QDoubleSpinBox()
        self.estimated_cost_input.setRange(0, 99999)
        self.estimated_cost_input.setSuffix(" جنيه")
        self.estimated_cost_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.parts_cost_input = QDoubleSpinBox()
        self.parts_cost_input.setRange(0, 99999)
        self.parts_cost_input.setSuffix(" جنيه")
        self.parts_cost_input.setStyleSheet(ModernStyles.get_input_style())
        self.parts_cost_input.valueChanged.connect(self.calculate_total_cost)
        
        self.labor_cost_input = QDoubleSpinBox()
        self.labor_cost_input.setRange(0, 99999)
        self.labor_cost_input.setSuffix(" جنيه")
        self.labor_cost_input.setStyleSheet(ModernStyles.get_input_style())
        self.labor_cost_input.valueChanged.connect(self.calculate_total_cost)
        
        self.estimated_days_input = QSpinBox()
        self.estimated_days_input.setRange(1, 30)
        self.estimated_days_input.setValue(3)
        self.estimated_days_input.setSuffix(" يوم")
        self.estimated_days_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.receive_date_input = QDateEdit()
        self.receive_date_input.setDate(QDate.currentDate())
        self.receive_date_input.setCalendarPopup(True)
        self.receive_date_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.warranty_days_input = QSpinBox()
        self.warranty_days_input.setRange(0, 365)
        self.warranty_days_input.setValue(30)
        self.warranty_days_input.setSuffix(" يوم")
        self.warranty_days_input.setStyleSheet(ModernStyles.get_input_style())
        
        repair_layout.addRow("وصف المشكلة *:", self.problem_description_input)
        repair_layout.addRow("نوع الإصلاح:", self.repair_type_input)
        repair_layout.addRow("الأولوية:", self.priority_input)
        repair_layout.addRow("تكلفة قطع الغيار:", self.parts_cost_input)
        repair_layout.addRow("تكلفة العمالة:", self.labor_cost_input)
        repair_layout.addRow("التكلفة الإجمالية:", self.estimated_cost_input)
        repair_layout.addRow("المدة المتوقعة:", self.estimated_days_input)
        repair_layout.addRow("تاريخ الاستلام:", self.receive_date_input)
        repair_layout.addRow("مدة الضمان:", self.warranty_days_input)
        
        # Additional Information
        additional_group = QGroupBox("معلومات إضافية")
        additional_group.setStyleSheet(ModernStyles.get_group_box_style())
        additional_layout = QFormLayout(additional_group)
        
        self.accessories_input = QTextEdit()
        self.accessories_input.setStyleSheet(ModernStyles.get_input_style())
        self.accessories_input.setMaximumHeight(60)
        self.accessories_input.setPlaceholderText("شاحن، سماعات، جراب...")
        
        self.technician_input = QComboBox()
        self.technician_input.setEditable(True)
        self.technician_input.addItems(["أحمد الفني", "محمد المختص", "علي المهندس"])
        self.technician_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.backup_created_checkbox = QCheckBox("تم إنشاء نسخة احتياطية")
        self.data_recovery_checkbox = QCheckBox("مطلوب استعادة بيانات")
        
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(ModernStyles.get_input_style())
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("ملاحظات إضافية...")
        
        additional_layout.addRow("الإكسسوارات المرفقة:", self.accessories_input)
        additional_layout.addRow("الفني المسؤول:", self.technician_input)
        additional_layout.addRow("", self.backup_created_checkbox)
        additional_layout.addRow("", self.data_recovery_checkbox)
        additional_layout.addRow("ملاحظات:", self.notes_input)
        
        # Add groups to form
        form_layout.addWidget(customer_group)
        form_layout.addWidget(device_group)
        form_layout.addWidget(repair_group)
        form_layout.addWidget(additional_group)
        
        scroll.setWidget(form_widget)
        layout.addWidget(scroll)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ الإصلاح")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.save_repair)
        buttons.rejected.connect(self.reject)
        
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
    def calculate_total_cost(self):
        """Calculate total estimated cost"""
        parts_cost = self.parts_cost_input.value()
        labor_cost = self.labor_cost_input.value()
        total_cost = parts_cost + labor_cost
        self.estimated_cost_input.setValue(total_cost)
        
    def validate_input(self):
        """Validate form input"""
        if not self.customer_name_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم العميل")
            return False
            
        if not self.device_type_input.currentText().strip():
            QMessageBox.warning(self, "خطأ", "يرجى تحديد نوع الجهاز")
            return False
            
        if not self.problem_description_input.toPlainText().strip():
            QMessageBox.warning(self, "خطأ", "يرجى وصف المشكلة")
            return False
            
        return True
        
    def save_repair(self):
        """Save new repair"""
        if not self.validate_input():
            return
            
        try:
            self.db_manager.execute_update("""
                INSERT INTO repairs (
                    customer_name, customer_phone, customer_email,
                    device_type, device_model, device_serial, device_color, device_password,
                    problem_description, repair_type, priority,
                    estimated_cost, parts_cost, labor_cost, estimated_days,
                    receive_date, status, technician, accessories,
                    backup_created, data_recovered, warranty_days, notes
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                self.customer_name_input.text().strip(),
                self.customer_phone_input.text().strip(),
                self.customer_email_input.text().strip(),
                self.device_type_input.currentText().strip(),
                self.device_model_input.text().strip(),
                self.device_serial_input.text().strip(),
                self.device_color_input.text().strip(),
                self.device_password_input.text().strip(),
                self.problem_description_input.toPlainText().strip(),
                self.repair_type_input.currentText().strip(),
                self.priority_input.currentText(),
                self.estimated_cost_input.value(),
                self.parts_cost_input.value(),
                self.labor_cost_input.value(),
                self.estimated_days_input.value(),
                self.receive_date_input.date().toString("yyyy-MM-dd"),
                'في الانتظار',
                self.technician_input.currentText().strip(),
                self.accessories_input.toPlainText().strip(),
                self.backup_created_checkbox.isChecked(),
                self.data_recovery_checkbox.isChecked(),
                self.warranty_days_input.value(),
                self.notes_input.toPlainText().strip()
            ))
            
            QMessageBox.information(self, "نجح", "تم إضافة طلب الإصلاح بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الإصلاح: {str(e)}")

class EditRepairDialog(AddRepairDialog):
    """Dialog for editing existing repair"""
    
    def __init__(self, repair, db_manager, parent=None):
        self.repair = repair
        super().__init__(db_manager, parent)
        self.setWindowTitle(f"تعديل الإصلاح - #{repair['id']}")
        self.load_repair_data()
        
    def setup_ui(self):
        """Setup dialog UI"""
        super().setup_ui()
        
        # Change header
        header = self.findChild(QLabel)
        if header:
            header.setText(f"✏️ تعديل الإصلاح - #{self.repair['id']}")
            
        # Change save button text
        buttons = self.findChild(QDialogButtonBox)
        if buttons:
            save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
            if save_btn:
                save_btn.setText("حفظ التغييرات")
        
    def load_repair_data(self):
        """Load repair data into form"""
        try:
            # Customer info
            self.customer_name_input.setText(self.repair['customer_name'])
            self.customer_phone_input.setText(self.repair.get('customer_phone', ''))
            self.customer_email_input.setText(self.repair.get('customer_email', ''))
            
            # Device info
            self.device_type_input.setCurrentText(self.repair['device_type'])
            self.device_model_input.setText(self.repair.get('device_model', ''))
            self.device_serial_input.setText(self.repair.get('device_serial', ''))
            self.device_color_input.setText(self.repair.get('device_color', ''))
            self.device_password_input.setText(self.repair.get('device_password', ''))
            
            # Repair info
            self.problem_description_input.setPlainText(self.repair.get('problem_description', ''))
            self.repair_type_input.setCurrentText(self.repair.get('repair_type', ''))
            self.priority_input.setCurrentText(self.repair.get('priority', 'عادي'))
            
            self.estimated_cost_input.setValue(self.repair.get('estimated_cost', 0))
            self.parts_cost_input.setValue(self.repair.get('parts_cost', 0))
            self.labor_cost_input.setValue(self.repair.get('labor_cost', 0))
            self.estimated_days_input.setValue(self.repair.get('estimated_days', 1))
            self.warranty_days_input.setValue(self.repair.get('warranty_days', 30))
            
            if self.repair.get('receive_date'):
                self.receive_date_input.setDate(QDate.fromString(self.repair['receive_date'], "yyyy-MM-dd"))
            
            # Additional info
            self.accessories_input.setPlainText(self.repair.get('accessories', ''))
            self.technician_input.setCurrentText(self.repair.get('technician', ''))
            self.backup_created_checkbox.setChecked(self.repair.get('backup_created', False))
            self.data_recovery_checkbox.setChecked(self.repair.get('data_recovered', False))
            self.notes_input.setPlainText(self.repair.get('notes', ''))
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الإصلاح: {str(e)}")
            
    def save_repair(self):
        """Update existing repair"""
        if not self.validate_input():
            return
            
        try:
            self.db_manager.execute_update("""
                UPDATE repairs SET
                    customer_name = ?, customer_phone = ?, customer_email = ?,
                    device_type = ?, device_model = ?, device_serial = ?, device_color = ?, device_password = ?,
                    problem_description = ?, repair_type = ?, priority = ?,
                    estimated_cost = ?, parts_cost = ?, labor_cost = ?, estimated_days = ?,
                    receive_date = ?, technician = ?, accessories = ?,
                    backup_created = ?, data_recovered = ?, warranty_days = ?, notes = ?
                WHERE id = ?
            """, (
                self.customer_name_input.text().strip(),
                self.customer_phone_input.text().strip(),
                self.customer_email_input.text().strip(),
                self.device_type_input.currentText().strip(),
                self.device_model_input.text().strip(),
                self.device_serial_input.text().strip(),
                self.device_color_input.text().strip(),
                self.device_password_input.text().strip(),
                self.problem_description_input.toPlainText().strip(),
                self.repair_type_input.currentText().strip(),
                self.priority_input.currentText(),
                self.estimated_cost_input.value(),
                self.parts_cost_input.value(),
                self.labor_cost_input.value(),
                self.estimated_days_input.value(),
                self.receive_date_input.date().toString("yyyy-MM-dd"),
                self.technician_input.currentText().strip(),
                self.accessories_input.toPlainText().strip(),
                self.backup_created_checkbox.isChecked(),
                self.data_recovery_checkbox.isChecked(),
                self.warranty_days_input.value(),
                self.notes_input.toPlainText().strip(),
                self.repair['id']
            ))
            
            QMessageBox.information(self, "نجح", "تم تحديث الإصلاح بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث الإصلاح: {str(e)}")

class RepairStatusDialog(QDialog):
    """Dialog for updating repair status"""
    
    def __init__(self, repair, db_manager, parent=None):
        super().__init__(parent)
        self.repair = repair
        self.db_manager = db_manager
        self.setWindowTitle(f"تحديث حالة الإصلاح - #{repair['id']}")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel(f"🔄 تحديث حالة الإصلاح - #{self.repair['id']}")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Current status
        current_frame = QFrame()
        current_frame.setStyleSheet("""
            QFrame {
                background-color: #f0f9ff;
                border: 1px solid #0ea5e9;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        current_layout = QFormLayout(current_frame)
        current_layout.addRow("الحالة الحالية:", QLabel(self.repair['status']))
        current_layout.addRow("العميل:", QLabel(self.repair['customer_name']))
        current_layout.addRow("الجهاز:", QLabel(f"{self.repair['device_type']} {self.repair.get('device_model', '')}"))
        layout.addWidget(current_frame)
        
        # New status form
        form_group = QGroupBox("الحالة الجديدة")
        form_group.setStyleSheet(ModernStyles.get_group_box_style())
        form_layout = QFormLayout(form_group)
        
        self.new_status_input = QComboBox()
        self.new_status_input.addItems([
            "في الانتظار", "قيد الإصلاح", "في انتظار قطع الغيار",
            "مكتمل", "مسلم للعميل", "ملغي"
        ])
        self.new_status_input.setCurrentText(self.repair['status'])
        self.new_status_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.actual_cost_input = QDoubleSpinBox()
        self.actual_cost_input.setRange(0, 99999)
        self.actual_cost_input.setValue(self.repair.get('actual_cost', self.repair.get('estimated_cost', 0)))
        self.actual_cost_input.setSuffix(" جنيه")
        self.actual_cost_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.delivery_date_input = QDateEdit()
        self.delivery_date_input.setDate(QDate.currentDate())
        self.delivery_date_input.setCalendarPopup(True)
        self.delivery_date_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(ModernStyles.get_input_style())
        self.notes_input.setMaximumHeight(100)
        self.notes_input.setPlaceholderText("ملاحظات حول تحديث الحالة...")
        
        form_layout.addRow("الحالة الجديدة:", self.new_status_input)
        form_layout.addRow("التكلفة الفعلية:", self.actual_cost_input)
        form_layout.addRow("تاريخ التسليم:", self.delivery_date_input)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addWidget(form_group)
        
        # Show delivery date only for completed status
        self.new_status_input.currentTextChanged.connect(self.on_status_changed)
        self.on_status_changed()
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("تحديث الحالة")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.update_status)
        buttons.rejected.connect(self.reject)
        
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
    def on_status_changed(self):
        """Handle status change"""
        status = self.new_status_input.currentText()
        
        # Show delivery date field only for completed statuses
        show_delivery = status in ['مكتمل', 'مسلم للعميل']
        
        # Find the delivery date row and show/hide it
        form_layout = self.delivery_date_input.parent().layout()
        for i in range(form_layout.rowCount()):
            item = form_layout.itemAt(i, QFormLayout.ItemRole.LabelRole)
            if item and item.widget() and item.widget().text() == "تاريخ التسليم:":
                item.widget().setVisible(show_delivery)
                form_layout.itemAt(i, QFormLayout.ItemRole.FieldRole).widget().setVisible(show_delivery)
                break
        
    def update_status(self):
        """Update repair status"""
        try:
            new_status = self.new_status_input.currentText()
            actual_cost = self.actual_cost_input.value()
            delivery_date = self.delivery_date_input.date().toString("yyyy-MM-dd") if new_status in ['مكتمل', 'مسلم للعميل'] else None
            notes = self.notes_input.toPlainText().strip()
            
            # Update repair
            self.db_manager.execute_update("""
                UPDATE repairs SET
                    status = ?, actual_cost = ?, delivery_date = ?, notes = ?
                WHERE id = ?
            """, (new_status, actual_cost, delivery_date, notes, self.repair['id']))
            
            # Log status change in history
            self.db_manager.execute_update("""
                INSERT INTO repair_status_history (
                    repair_id, old_status, new_status, notes, changed_by
                ) VALUES (?, ?, ?, ?, ?)
            """, (self.repair['id'], self.repair['status'], new_status, notes, "المدير"))
            
            QMessageBox.information(self, "نجح", "تم تحديث حالة الإصلاح بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث الحالة: {str(e)}")

class CustomerSelectionDialog(QDialog):
    """Dialog for selecting customer"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.selected_customer = None
        self.setWindowTitle("اختيار العميل")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        self.load_customers()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("👤 اختيار العميل")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Search
        search_layout = QHBoxLayout()
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.setPlaceholderText("البحث بالاسم أو رقم الهاتف...")
        self.search_input.textChanged.connect(self.search_customers)
        
        add_customer_btn = QPushButton("➕ عميل جديد")
        add_customer_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        add_customer_btn.clicked.connect(self.add_new_customer)
        
        search_layout.addWidget(QLabel("البحث:"))
        search_layout.addWidget(self.search_input, 1)
        search_layout.addWidget(add_customer_btn)
        layout.addLayout(search_layout)
        
        # Customers table
        self.customers_table = QTableWidget()
        self.customers_table.setColumnCount(4)
        self.customers_table.setHorizontalHeaderLabels(["الاسم", "الهاتف", "البريد الإلكتروني", "النوع"])
        self.customers_table.horizontalHeader().setStretchLastSection(True)
        self.customers_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.customers_table.setStyleSheet(ModernStyles.get_table_style())
        self.customers_table.itemDoubleClicked.connect(self.on_customer_selected)
        layout.addWidget(self.customers_table)
        
        # Quick options
        quick_layout = QHBoxLayout()
        
        cash_customer_btn = QPushButton("💰 عميل نقدي")
        cash_customer_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        cash_customer_btn.clicked.connect(self.select_cash_customer)
        
        quick_layout.addWidget(cash_customer_btn)
        quick_layout.addStretch()
        
        layout.addLayout(quick_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("اختيار")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(False)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        
        self.buttons = buttons
        layout.addWidget(buttons)
        
    def load_customers(self):
        """Load customers"""
        try:
            customers = self.db_manager.execute_query("""
                SELECT * FROM customers WHERE is_active = 1 ORDER BY name
            """)
            
            self.populate_table(customers)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل العملاء: {str(e)}")
            
    def populate_table(self, customers):
        """Populate customers table"""
        self.customers_data = customers
        self.customers_table.setRowCount(len(customers))
        
        for row, customer in enumerate(customers):
            self.customers_table.setItem(row, 0, QTableWidgetItem(customer['name']))
            self.customers_table.setItem(row, 1, QTableWidgetItem(customer.get('phone', '')))
            self.customers_table.setItem(row, 2, QTableWidgetItem(customer.get('email', '')))
            self.customers_table.setItem(row, 3, QTableWidgetItem(customer.get('customer_type', 'عادي')))
            
    def search_customers(self, text):
        """Search customers"""
        try:
            if text.strip():
                customers = self.db_manager.execute_query("""
                    SELECT * FROM customers 
                    WHERE is_active = 1 AND (name LIKE ? OR phone LIKE ?) 
                    ORDER BY name
                """, (f"%{text}%", f"%{text}%"))
            else:
                customers = self.db_manager.execute_query("""
                    SELECT * FROM customers WHERE is_active = 1 ORDER BY name
                """)
                
            self.populate_table(customers)
            
        except Exception as e:
            print(f"Error searching customers: {e}")
            
    def on_customer_selected(self):
        """Handle customer selection"""
        current_row = self.customers_table.currentRow()
        if current_row >= 0:
            self.selected_customer = self.customers_data[current_row]
            self.buttons.button(QDialogButtonBox.StandardButton.Ok).setEnabled(True)
            self.accept()
            
    def select_cash_customer(self):
        """Select cash customer"""
        self.selected_customer = None
        self.accept()
        
    def add_new_customer(self):
        """Add new customer"""
        dialog = AddCustomerDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.load_customers()
            
    def get_selected_customer(self):
        """Get selected customer"""
        return self.selected_customer

class AddCustomerDialog(QDialog):
    """Dialog for adding new customer"""
    
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إضافة عميل جديد")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("👤 إضافة عميل جديد")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Form
        form_layout = QFormLayout()
        
        self.name_input = QLineEdit()
        self.name_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.phone_input = QLineEdit()
        self.phone_input.setStyleSheet(ModernStyles.get_input_style())
        self.phone_input.setPlaceholderText("01xxxxxxxxx")
        
        self.email_input = QLineEdit()
        self.email_input.setStyleSheet(ModernStyles.get_input_style())
        self.email_input.setPlaceholderText("email@example.com")
        
        self.address_input = QTextEdit()
        self.address_input.setStyleSheet(ModernStyles.get_input_style())
        self.address_input.setMaximumHeight(80)
        
        self.customer_type_input = QComboBox()
        self.customer_type_input.addItems(["عادي", "مميز", "جملة"])
        self.customer_type_input.setStyleSheet(ModernStyles.get_input_style())
        
        form_layout.addRow("اسم العميل *:", self.name_input)
        form_layout.addRow("رقم الهاتف:", self.phone_input)
        form_layout.addRow("البريد الإلكتروني:", self.email_input)
        form_layout.addRow("العنوان:", self.address_input)
        form_layout.addRow("نوع العميل:", self.customer_type_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.save_customer)
        buttons.rejected.connect(self.reject)
        
        layout.addWidget(buttons)
        
    def save_customer(self):
        """Save new customer"""
        if not self.name_input.text().strip():
            QMessageBox.warning(self, "خطأ", "يرجى إدخال اسم العميل")
            return
            
        try:
            customer_id = str(uuid4())
            self.db_manager.execute_update("""
                INSERT INTO customers (id, name, phone, email, address, customer_type)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (
                customer_id, self.name_input.text().strip(),
                self.phone_input.text().strip(),
                self.email_input.text().strip(),
                self.address_input.toPlainText().strip(),
                self.customer_type_input.currentText()
            ))
            
            QMessageBox.information(self, "نجح", "تم إضافة العميل بنجاح")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ العميل: {str(e)}")

class PaymentDialog(QDialog):
    """Dialog for payment processing"""
    
    def __init__(self, totals_data, parent=None):
        super().__init__(parent)
        self.totals_data = totals_data
        self.setWindowTitle("معالجة الدفع")
        self.setModal(True)
        self.resize(400, 300)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("💳 معالجة الدفع")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Total amount display
        total_frame = QFrame()
        total_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 10px;
                padding: 20px;
            }
        """)
        total_layout = QVBoxLayout(total_frame)
        
        total_label = QLabel("المبلغ الإجمالي")
        total_label.setFont(QFont("Tahoma", 12))
        total_label.setStyleSheet("color: white;")
        total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        amount_label = QLabel(f"{self.totals_data['total']:.2f} جنيه")
        amount_label.setFont(QFont("Tahoma", 24, QFont.Weight.Bold))
        amount_label.setStyleSheet("color: white;")
        amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        total_layout.addWidget(total_label)
        total_layout.addWidget(amount_label)
        
        layout.addWidget(total_frame)
        
        # Payment form
        form_layout = QFormLayout()
        
        self.payment_method_input = QComboBox()
        self.payment_method_input.addItems(["نقدي", "بطاقة ائتمان", "تحويل بنكي", "محفظة إلكترونية"])
        self.payment_method_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.paid_amount_input = QDoubleSpinBox()
        self.paid_amount_input.setRange(0, 999999)
        self.paid_amount_input.setDecimals(2)
        self.paid_amount_input.setValue(self.totals_data['total'])
        self.paid_amount_input.setSuffix(" جنيه")
        self.paid_amount_input.setStyleSheet(ModernStyles.get_input_style())
        self.paid_amount_input.valueChanged.connect(self.calculate_change)
        
        self.change_label = QLabel("0.00 جنيه")
        self.change_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
        
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(ModernStyles.get_input_style())
        self.notes_input.setMaximumHeight(60)
        self.notes_input.setPlaceholderText("ملاحظات الدفع...")
        
        form_layout.addRow("طريقة الدفع:", self.payment_method_input)
        form_layout.addRow("المبلغ المدفوع:", self.paid_amount_input)
        form_layout.addRow("الباقي:", self.change_label)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Ok).setText("إتمام الدفع")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.process_payment)
        buttons.rejected.connect(self.reject)
        
        pay_btn = buttons.button(QDialogButtonBox.StandardButton.Ok)
        pay_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
        # Initial calculation
        self.calculate_change()
        
    def calculate_change(self):
        """Calculate change amount"""
        paid = self.paid_amount_input.value()
        total = self.totals_data['total']
        change = paid - total
        
        self.change_label.setText(f"{change:.2f} جنيه")
        
        if change < 0:
            self.change_label.setStyleSheet("color: #dc2626; font-weight: bold; font-size: 14px;")
        else:
            self.change_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
            
    def process_payment(self):
        """Process payment"""
        paid_amount = self.paid_amount_input.value()
        total_amount = self.totals_data['total']
        
        if paid_amount < total_amount:
            reply = QMessageBox.question(
                self, "تأكيد",
                f"المبلغ المدفوع أقل من الإجمالي بـ {total_amount - paid_amount:.2f} جنيه.\nهل تريد المتابعة؟"
            )
            if reply == QMessageBox.StandardButton.No:
                return
                
        self.accept()
        
    def get_payment_data(self):
        """Get payment data"""
        return {
            'payment_method': self.payment_method_input.currentText(),
            'paid_amount': self.paid_amount_input.value(),
            'change_amount': self.paid_amount_input.value() - self.totals_data['total'],
            'notes': self.notes_input.toPlainText().strip()
        }

class WalletTransactionDialog(QDialog):
    """Dialog for wallet transaction"""
    
    def __init__(self, db_manager, parent=None, transaction_type=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.transaction_type = transaction_type
        self.setWindowTitle("معاملة محفظة جديدة")
        self.setModal(True)
        self.resize(500, 400)
        self.setup_ui()
        
    def setup_ui(self):
        """Setup dialog UI"""
        layout = QVBoxLayout(self)
        layout.setSpacing(20)
        
        # Header
        header = QLabel("💰 معاملة محفظة جديدة")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setStyleSheet("color: #1f2937; margin-bottom: 10px;")
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(header)
        
        # Form
        form_layout = QFormLayout()
        
        self.provider_input = QComboBox()
        self.provider_input.addItem("فودافون كاش", "vodafone")
        self.provider_input.addItem("أورانج كاش", "orange")
        self.provider_input.addItem("اتصالات كاش", "etisalat")
        self.provider_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.transaction_type_input = QComboBox()
        self.transaction_type_input.addItem("استقبال", "receive")
        self.transaction_type_input.addItem("إرسال", "send")
        self.transaction_type_input.addItem("إيداع", "deposit")
        self.transaction_type_input.addItem("سحب", "withdraw")
        self.transaction_type_input.addItem("رسوم", "fees")
        self.transaction_type_input.addItem("تحويل", "transfer")
        self.transaction_type_input.setStyleSheet(ModernStyles.get_input_style())
        self.transaction_type_input.currentTextChanged.connect(self.on_type_changed)
        
        # Set default transaction type if provided
        if self.transaction_type:
            type_index = self.transaction_type_input.findData(self.transaction_type)
            if type_index >= 0:
                self.transaction_type_input.setCurrentIndex(type_index)
        
        self.service_type_input = QComboBox()
        self.service_type_input.setEditable(True)
        self.service_type_input.addItems(["نقدي", "تحويل", "دفع فواتير", "شحن رصيد"])
        self.service_type_input.setStyleSheet(ModernStyles.get_input_style())
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999)
        self.amount_input.setDecimals(2)
        self.amount_input.setSuffix(" جنيه")
        self.amount_input.setStyleSheet(ModernStyles.get_input_style())
        self.amount_input.valueChanged.connect(self.calculate_net_amount)
        
        self.fees_input = QDoubleSpinBox()
        self.fees_input.setRange(0, 999999)
        self.fees_input.setDecimals(2)
        self.fees_input.setSuffix(" جنيه")
        self.fees_input.setStyleSheet(ModernStyles.get_input_style())
        self.fees_input.valueChanged.connect(self.calculate_net_amount)
        
        self.net_amount_label = QLabel("0.00 جنيه")
        self.net_amount_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
        
        self.customer_name_input = QLineEdit()
        self.customer_name_input.setStyleSheet(ModernStyles.get_input_style())
        self.customer_name_input.setPlaceholderText("اسم العميل")
        
        self.customer_phone_input = QLineEdit()
        self.customer_phone_input.setStyleSheet(ModernStyles.get_input_style())
        self.customer_phone_input.setPlaceholderText("01xxxxxxxxx")
        
        self.sender_number_input = QLineEdit()
        self.sender_number_input.setStyleSheet(ModernStyles.get_input_style())
        self.sender_number_input.setPlaceholderText("رقم المرسل")
        
        self.recipient_number_input = QLineEdit()
        self.recipient_number_input.setStyleSheet(ModernStyles.get_input_style())
        self.recipient_number_input.setPlaceholderText("رقم المستقبل")
        
        self.reference_input = QLineEdit()
        self.reference_input.setStyleSheet(ModernStyles.get_input_style())
        self.reference_input.setPlaceholderText("رقم المرجع")
        
        self.external_reference_input = QLineEdit()
        self.external_reference_input.setStyleSheet(ModernStyles.get_input_style())
        self.external_reference_input.setPlaceholderText("المرجع الخارجي")
        
        self.notes_input = QTextEdit()
        self.notes_input.setStyleSheet(ModernStyles.get_input_style())
        self.notes_input.setMaximumHeight(80)
        self.notes_input.setPlaceholderText("ملاحظات...")
        
        form_layout.addRow("مقدم الخدمة *:", self.provider_input)
        form_layout.addRow("نوع المعاملة *:", self.transaction_type_input)
        form_layout.addRow("نوع الخدمة:", self.service_type_input)
        form_layout.addRow("المبلغ *:", self.amount_input)
        form_layout.addRow("الرسوم:", self.fees_input)
        form_layout.addRow("المبلغ الصافي:", self.net_amount_label)
        form_layout.addRow("اسم العميل:", self.customer_name_input)
        form_layout.addRow("رقم العميل:", self.customer_phone_input)
        form_layout.addRow("رقم المرسل:", self.sender_number_input)
        form_layout.addRow("رقم المستقبل:", self.recipient_number_input)
        form_layout.addRow("رقم المرجع:", self.reference_input)
        form_layout.addRow("المرجع الخارجي:", self.external_reference_input)
        form_layout.addRow("ملاحظات:", self.notes_input)
        
        layout.addLayout(form_layout)
        
        # Buttons
        buttons = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Save | QDialogButtonBox.StandardButton.Cancel
        )
        buttons.button(QDialogButtonBox.StandardButton.Save).setText("حفظ المعاملة")
        buttons.button(QDialogButtonBox.StandardButton.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.save_transaction)
        buttons.rejected.connect(self.reject)
        
        save_btn = buttons.button(QDialogButtonBox.StandardButton.Save)
        save_btn.setStyleSheet(ModernStyles.get_button_success_style())
        
        cancel_btn = buttons.button(QDialogButtonBox.StandardButton.Cancel)
        cancel_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        
        layout.addWidget(buttons)
        
        # Initial setup
        self.on_type_changed()
        self.calculate_net_amount()
        
    def on_type_changed(self):
        """Handle transaction type change"""
        trans_type = self.transaction_type_input.currentData()
        
        # Show/hide relevant fields based on transaction type
        if trans_type in ['send', 'transfer']:
            self.sender_number_input.setVisible(True)
            self.recipient_number_input.setVisible(True)
        else:
            self.sender_number_input.setVisible(False)
            self.recipient_number_input.setVisible(False)
            
    def calculate_net_amount(self):
        """Calculate net amount"""
        amount = self.amount_input.value()
        fees = self.fees_input.value()
        trans_type = self.transaction_type_input.currentData()
        
        if trans_type in ['send', 'withdraw', 'fees']:
            net_amount = -(amount + fees)
        else:
            net_amount = amount - fees
            
        self.net_amount_label.setText(f"{net_amount:.2f} جنيه")
        
        if net_amount >= 0:
            self.net_amount_label.setStyleSheet("color: #059669; font-weight: bold; font-size: 14px;")
        else:
            self.net_amount_label.setStyleSheet("color: #dc2626; font-weight: bold; font-size: 14px;")
            
    def validate_input(self):
        """Validate form input"""
        if self.amount_input.value() <= 0:
            QMessageBox.warning(self, "خطأ", "يرجى إدخال مبلغ صحيح")
            return False
            
        trans_type = self.transaction_type_input.currentData()
        if trans_type in ['send', 'transfer']:
            if not self.recipient_number_input.text().strip():
                QMessageBox.warning(self, "خطأ", "يرجى إدخال رقم المستقبل")
                return False
                
        return True
        
    def save_transaction(self):
        """Save wallet transaction"""
        if not self.validate_input():
            return
            
        try:
            trans_type = self.transaction_type_input.currentData()
            amount = self.amount_input.value()
            fees = self.fees_input.value()
            
            # Calculate net amount and actual amount to store
            if trans_type in ['send', 'withdraw', 'fees']:
                actual_amount = -(amount + fees)
                net_amount = actual_amount
            else:
                actual_amount = amount
                net_amount = amount - fees
            
            # Generate transaction ID and number
            transaction_id = str(uuid4())
            transaction_number = f"WT-{datetime.now().strftime('%Y%m%d')}-{int(datetime.now().timestamp()) % 10000:04d}"
            
            self.db_manager.execute_update("""
                INSERT INTO wallet_transactions (
                    id, transaction_number, provider, service_type, transaction_type,
                    amount, fees, net_amount, customer_name, customer_phone,
                    sender_number, recipient_number, reference, external_reference,
                    status, notes, cashier
                ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id, transaction_number,
                self.provider_input.currentData(),
                self.service_type_input.currentText().strip(),
                trans_type, actual_amount, fees, net_amount,
                self.customer_name_input.text().strip(),
                self.customer_phone_input.text().strip(),
                self.sender_number_input.text().strip(),
                self.recipient_number_input.text().strip(),
                self.reference_input.text().strip(),
                self.external_reference_input.text().strip(),
                'completed',
                self.notes_input.toPlainText().strip(),
                'الكاشير'
            ))
            
            QMessageBox.information(self, "نجح", f"تم حفظ المعاملة بنجاح\nرقم المعاملة: {transaction_number}")
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المعاملة: {str(e)}")
