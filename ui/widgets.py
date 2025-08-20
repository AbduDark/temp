"""
Enhanced UI Widgets for Mobile Shop Management System
Beautiful and reusable widget components with modern design
"""

from PyQt6.QtWidgets import *
from PyQt6.QtCore import Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, QTimer, QRect
from PyQt6.QtGui import QFont, QColor, QPainter, QPen, QBrush, QLinearGradient, QPixmap

from ui.styles import ModernStyles
from datetime import datetime
import math

class StatCard(QFrame):
    """Enhanced statistics card with modern design and animations"""
    
    clicked = pyqtSignal()
    
    def __init__(self, title, value, icon, color="#3b82f6", subtitle="", trend=None, clickable=True):
        super().__init__()
        self.title = title
        self.value = value
        self.icon = icon
        self.color = color
        self.subtitle = subtitle
        self.trend = trend
        self.clickable = clickable
        self.is_hovered = False
        self.setup_ui()
        self.setup_animation()
        
    def setup_ui(self):
        """Setup card UI with modern design"""
        self.setFixedHeight(140)
        if self.clickable:
            self.setCursor(Qt.CursorShape.PointingHandCursor)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 10))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        self.update_style()
        
        layout = QVBoxLayout(self)
        layout.setSpacing(12)
        layout.setContentsMargins(20, 16, 20, 16)
        
        # Header with icon and title
        header_layout = QHBoxLayout()
        
        # Icon container
        icon_container = QFrame()
        icon_container.setFixedSize(50, 50)
        icon_container.setStyleSheet(f"""
            QFrame {{
                background-color: {self.color}20;
                border-radius: 25px;
            }}
        """)
        
        icon_layout = QVBoxLayout(icon_container)
        icon_layout.setContentsMargins(0, 0, 0, 0)
        
        icon_label = QLabel(self.icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 20))
        icon_label.setStyleSheet(f"color: {self.color};")
        icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        icon_layout.addWidget(icon_label)
        
        # Title
        title_label = QLabel(self.title)
        title_label.setFont(QFont("Tahoma", 11, QFont.Weight.DemiBold))
        title_label.setStyleSheet("color: #6b7280;")
        title_label.setWordWrap(True)
        
        header_layout.addWidget(icon_container)
        header_layout.addWidget(title_label, 1)
        header_layout.addStretch()
        
        # Value
        self.value_label = QLabel(str(self.value))
        self.value_label.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        self.value_label.setStyleSheet(f"color: {self.color}; margin: 8px 0;")
        self.value_label.setWordWrap(True)
        
        # Bottom section with subtitle and trend
        bottom_layout = QHBoxLayout()
        
        if self.subtitle:
            subtitle_label = QLabel(self.subtitle)
            subtitle_label.setFont(QFont("Tahoma", 9))
            subtitle_label.setStyleSheet("color: #9ca3af;")
            subtitle_label.setWordWrap(True)
            bottom_layout.addWidget(subtitle_label)
        
        if self.trend:
            trend_container = QFrame()
            trend_layout = QHBoxLayout(trend_container)
            trend_layout.setContentsMargins(8, 4, 8, 4)
            trend_layout.setSpacing(4)
            
            # Trend icon
            if isinstance(self.trend, (int, float)):
                if self.trend > 0:
                    trend_icon = "📈"
                    trend_color = "#10b981"
                    trend_text = f"+{self.trend:.1f}%"
                elif self.trend < 0:
                    trend_icon = "📉"
                    trend_color = "#ef4444"
                    trend_text = f"{self.trend:.1f}%"
                else:
                    trend_icon = "➡️"
                    trend_color = "#6b7280"
                    trend_text = "0.0%"
            else:
                trend_icon = "📊"
                trend_color = "#6b7280"
                trend_text = str(self.trend)
            
            trend_icon_label = QLabel(trend_icon)
            trend_icon_label.setFont(QFont("Segoe UI Emoji", 10))
            
            trend_text_label = QLabel(trend_text)
            trend_text_label.setFont(QFont("Tahoma", 9, QFont.Weight.Bold))
            trend_text_label.setStyleSheet(f"color: {trend_color};")
            
            trend_container.setStyleSheet(f"""
                QFrame {{
                    background-color: {trend_color}15;
                    border-radius: 12px;
                }}
            """)
            
            trend_layout.addWidget(trend_icon_label)
            trend_layout.addWidget(trend_text_label)
            
            bottom_layout.addStretch()
            bottom_layout.addWidget(trend_container)
        
        layout.addLayout(header_layout)
        layout.addWidget(self.value_label)
        layout.addLayout(bottom_layout)
        
    def setup_animation(self):
        """Setup hover animations"""
        if not self.clickable:
            return
            
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(200)
        self.animation.setEasingCurve(QEasingCurve.Type.OutCubic)
        
    def update_style(self):
        """Update card style based on state"""
        if self.is_hovered and self.clickable:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid {self.color};
                    border-radius: 16px;
                    border-left: 4px solid {self.color};
                }}
            """)
        else:
            self.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 1px solid #e5e7eb;
                    border-radius: 16px;
                    border-left: 4px solid {self.color};
                }}
            """)
    
    def update_value(self, new_value, subtitle="", trend=None):
        """Update card value with animation effect"""
        self.value = new_value
        self.subtitle = subtitle
        self.trend = trend
        self.value_label.setText(str(new_value))
        
        # Simple fade animation
        self.value_label.setStyleSheet(f"color: {self.color}; margin: 8px 0; background-color: {self.color}10;")
        QTimer.singleShot(300, lambda: self.value_label.setStyleSheet(f"color: {self.color}; margin: 8px 0;"))
    
    def enterEvent(self, event):
        """Handle mouse enter"""
        if self.clickable:
            self.is_hovered = True
            self.update_style()
        super().enterEvent(event)
        
    def leaveEvent(self, event):
        """Handle mouse leave"""
        if self.clickable:
            self.is_hovered = False
            self.update_style()
        super().leaveEvent(event)
        
    def mousePressEvent(self, event):
        """Handle mouse press"""
        if self.clickable and event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit()
        super().mousePressEvent(event)

class ChartWidget(QFrame):
    """Simple chart widget for displaying data visualization"""
    
    def __init__(self, title="", chart_type="bar"):
        super().__init__()
        self.title = title
        self.chart_type = chart_type
        self.data = []
        self.labels = []
        self.colors = ["#3b82f6", "#10b981", "#f59e0b", "#ef4444", "#8b5cf6"]
        self.setup_ui()
        
    def setup_ui(self):
        """Setup chart UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        self.setMinimumHeight(300)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #374151; margin-bottom: 15px;")
            layout.addWidget(title_label)
        
        # Chart area
        self.chart_area = QFrame()
        self.chart_area.setMinimumHeight(250)
        layout.addWidget(self.chart_area, 1)
        
    def set_data(self, data, labels=None):
        """Set chart data"""
        self.data = data
        self.labels = labels or [f"Item {i+1}" for i in range(len(data))]
        self.update()
        
    def paintEvent(self, event):
        """Paint the chart"""
        super().paintEvent(event)
        
        if not self.data:
            return
            
        painter = QPainter(self)
        painter.setRenderHint(QPainter.RenderHint.Antialiasing)
        
        # Get chart area
        chart_rect = self.chart_area.geometry()
        chart_rect.adjust(20, 40, -20, -40)
        
        if self.chart_type == "bar":
            self.draw_bar_chart(painter, chart_rect)
        elif self.chart_type == "pie":
            self.draw_pie_chart(painter, chart_rect)
        elif self.chart_type == "line":
            self.draw_line_chart(painter, chart_rect)
            
    def draw_bar_chart(self, painter, rect):
        """Draw bar chart"""
        if not self.data:
            return
            
        max_value = max(self.data) if self.data else 1
        bar_width = rect.width() / len(self.data) - 10
        
        for i, value in enumerate(self.data):
            # Calculate bar height
            bar_height = (value / max_value) * rect.height()
            
            # Bar position
            x = rect.x() + i * (bar_width + 10)
            y = rect.y() + rect.height() - bar_height
            
            # Draw bar
            color = QColor(self.colors[i % len(self.colors)])
            painter.fillRect(int(x), int(y), int(bar_width), int(bar_height), color)
            
            # Draw value label
            painter.setPen(QPen(QColor("#374151")))
            painter.drawText(
                QRect(int(x), int(y - 20), int(bar_width), 15),
                Qt.AlignmentFlag.AlignCenter,
                str(value)
            )
            
            # Draw label
            if i < len(self.labels):
                painter.drawText(
                    QRect(int(x), int(rect.y() + rect.height() + 5), int(bar_width), 15),
                    Qt.AlignmentFlag.AlignCenter,
                    self.labels[i][:8] + "..." if len(self.labels[i]) > 8 else self.labels[i]
                )
    
    def draw_pie_chart(self, painter, rect):
        """Draw pie chart"""
        if not self.data:
            return
            
        total = sum(self.data)
        if total == 0:
            return
            
        center_x = rect.center().x()
        center_y = rect.center().y()
        radius = min(rect.width(), rect.height()) // 2 - 20
        
        start_angle = 0
        
        for i, value in enumerate(self.data):
            # Calculate span angle
            span_angle = int((value / total) * 360 * 16)  # Qt uses 1/16th degrees
            
            # Draw pie slice
            color = QColor(self.colors[i % len(self.colors)])
            painter.setBrush(QBrush(color))
            painter.setPen(QPen(QColor("white"), 2))
            
            painter.drawPie(
                center_x - radius, center_y - radius,
                radius * 2, radius * 2,
                start_angle, span_angle
            )
            
            start_angle += span_angle
    
    def draw_line_chart(self, painter, rect):
        """Draw line chart"""
        if len(self.data) < 2:
            return
            
        max_value = max(self.data)
        min_value = min(self.data)
        value_range = max_value - min_value if max_value != min_value else 1
        
        # Calculate points
        points = []
        for i, value in enumerate(self.data):
            x = rect.x() + (i / (len(self.data) - 1)) * rect.width()
            y = rect.y() + rect.height() - ((value - min_value) / value_range) * rect.height()
            points.append((int(x), int(y)))
        
        # Draw line
        painter.setPen(QPen(QColor(self.colors[0]), 3))
        for i in range(len(points) - 1):
            painter.drawLine(points[i][0], points[i][1], points[i + 1][0], points[i + 1][1])
        
        # Draw points
        painter.setBrush(QBrush(QColor(self.colors[0])))
        for x, y in points:
            painter.drawEllipse(x - 4, y - 4, 8, 8)

class ProductSearchWidget(QFrame):
    """Enhanced product search widget with auto-complete"""
    
    product_selected = pyqtSignal(dict)
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.products = []
        self.filtered_products = []
        self.setup_ui()
        self.load_products()
        
    def setup_ui(self):
        """Setup search widget UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        layout.setSpacing(10)
        
        # Search input
        search_layout = QHBoxLayout()
        
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 14))
        search_icon.setFixedSize(30, 30)
        search_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
        search_icon.setStyleSheet("""
            QLabel {
                background-color: #f3f4f6;
                border-radius: 15px;
                color: #6b7280;
            }
        """)
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.setPlaceholderText("البحث عن منتج بالاسم، الكود، أو الباركود...")
        self.search_input.textChanged.connect(self.filter_products)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addLayout(search_layout)
        
        # Results area
        self.results_scroll = QScrollArea()
        self.results_scroll.setWidgetResizable(True)
        self.results_scroll.setMaximumHeight(200)
        self.results_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAsNeeded)
        self.results_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarPolicy.ScrollBarAlwaysOff)
        self.results_scroll.setStyleSheet("""
            QScrollArea {
                border: 1px solid #e5e7eb;
                border-radius: 8px;
                background-color: white;
            }
        """)
        self.results_scroll.hide()
        
        self.results_widget = QWidget()
        self.results_layout = QVBoxLayout(self.results_widget)
        self.results_layout.setSpacing(2)
        self.results_layout.setContentsMargins(5, 5, 5, 5)
        
        self.results_scroll.setWidget(self.results_widget)
        layout.addWidget(self.results_scroll)
        
    def load_products(self):
        """Load products from database"""
        try:
            self.products = self.db_manager.execute_query("""
                SELECT * FROM products 
                WHERE is_active = 1 AND current_qty > 0
                ORDER BY name
            """)
        except Exception as e:
            print(f"Error loading products: {e}")
            self.products = []
    
    def filter_products(self, text):
        """Filter products based on search text"""
        if len(text) < 2:
            self.results_scroll.hide()
            return
        
        text = text.lower()
        self.filtered_products = []
        
        for product in self.products:
            if (text in product['name'].lower() or 
                text in product['sku'].lower() or 
                text in (product.get('barcode', '') or '').lower()):
                self.filtered_products.append(product)
        
        self.display_results()
    
    def display_results(self):
        """Display filtered results"""
        # Clear existing results
        for i in reversed(range(self.results_layout.count())):
            self.results_layout.itemAt(i).widget().setParent(None)
        
        if not self.filtered_products:
            self.results_scroll.hide()
            return
        
        # Add filtered products
        for product in self.filtered_products[:10]:  # Limit to 10 results
            result_item = self.create_result_item(product)
            self.results_layout.addWidget(result_item)
        
        self.results_layout.addStretch()
        self.results_scroll.show()
    
    def create_result_item(self, product):
        """Create result item widget"""
        item_frame = QFrame()
        item_frame.setCursor(Qt.CursorShape.PointingHandCursor)
        item_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border: none;
                border-radius: 4px;
                padding: 8px;
            }
            QFrame:hover {
                background-color: #f3f4f6;
            }
        """)
        
        layout = QHBoxLayout(item_frame)
        layout.setContentsMargins(8, 6, 8, 6)
        
        # Product info
        info_layout = QVBoxLayout()
        info_layout.setSpacing(2)
        
        name_label = QLabel(product['name'])
        name_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        name_label.setStyleSheet("color: #374151;")
        
        details_label = QLabel(f"الكود: {product['sku']} | السعر: {product['sale_price']:.2f} جنيه | متاح: {product['current_qty']}")
        details_label.setFont(QFont("Tahoma", 8))
        details_label.setStyleSheet("color: #6b7280;")
        
        info_layout.addWidget(name_label)
        info_layout.addWidget(details_label)
        
        # Stock indicator
        stock_indicator = QLabel("●")
        if product['current_qty'] == 0:
            stock_indicator.setStyleSheet("color: #ef4444; font-size: 12px;")
        elif product['current_qty'] <= product['min_stock']:
            stock_indicator.setStyleSheet("color: #f59e0b; font-size: 12px;")
        else:
            stock_indicator.setStyleSheet("color: #10b981; font-size: 12px;")
        
        layout.addLayout(info_layout, 1)
        layout.addWidget(stock_indicator)
        
        # Connect click event
        item_frame.mousePressEvent = lambda event: self.select_product(product) if event.button() == Qt.MouseButton.LeftButton else None
        
        return item_frame
    
    def select_product(self, product):
        """Select a product"""
        self.search_input.setText(product['name'])
        self.results_scroll.hide()
        self.product_selected.emit(product)

class TransactionCard(QFrame):
    """Transaction display card"""
    
    def __init__(self, transaction):
        super().__init__()
        self.transaction = transaction
        self.setup_ui()
        
    def setup_ui(self):
        """Setup card UI"""
        self.setStyleSheet("""
            QFrame {
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                padding: 15px;
                margin: 5px;
            }
            QFrame:hover {
                border-color: #3b82f6;
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Transaction icon based on type
        icons = {
            'receive': '📥',
            'send': '📤',
            'deposit': '💰',
            'withdraw': '🏧',
            'transfer': '🔄'
        }
        
        icon = icons.get(self.transaction.get('transaction_type', ''), '💳')
        icon_label = QLabel(icon)
        icon_label.setFont(QFont("Segoe UI Emoji", 16))
        
        # Amount
        amount = self.transaction.get('amount', 0)
        amount_label = QLabel(f"{amount:.2f} جنيه")
        amount_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        if amount >= 0:
            amount_label.setStyleSheet("color: #10b981;")
        else:
            amount_label.setStyleSheet("color: #ef4444;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(amount_label, 1)
        
        # Provider
        provider_names = {
            'vodafone': 'فودافون',
            'orange': 'أورانج',
            'etisalat': 'اتصالات'
        }
        provider = provider_names.get(self.transaction.get('provider', ''), self.transaction.get('provider', ''))
        provider_label = QLabel(provider)
        provider_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        provider_label.setStyleSheet("color: #6b7280;")
        
        header_layout.addWidget(provider_label)
        
        # Details
        details_layout = QVBoxLayout()
        details_layout.setSpacing(4)
        
        # Customer
        if self.transaction.get('customer_name'):
            customer_label = QLabel(f"العميل: {self.transaction['customer_name']}")
            customer_label.setFont(QFont("Tahoma", 9))
            customer_label.setStyleSheet("color: #374151;")
            details_layout.addWidget(customer_label)
        
        # Date
        date_str = self.transaction.get('created_at', '')[:16] if self.transaction.get('created_at') else ''
        date_label = QLabel(f"التاريخ: {date_str}")
        date_label.setFont(QFont("Tahoma", 8))
        date_label.setStyleSheet("color: #9ca3af;")
        details_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        layout.addLayout(details_layout)

class RepairCard(QFrame):
    """Repair status display card"""
    
    def __init__(self, repair):
        super().__init__()
        self.repair = repair
        self.setup_ui()
        
    def setup_ui(self):
        """Setup card UI"""
        # Status colors
        status_colors = {
            'في الانتظار': '#f59e0b',
            'قيد الإصلاح': '#3b82f6',
            'في انتظار قطع الغيار': '#ef4444',
            'مكتمل': '#10b981',
            'مسلم للعميل': '#059669',
            'ملغي': '#6b7280'
        }
        
        status = self.repair.get('status', 'في الانتظار')
        color = status_colors.get(status, '#6b7280')
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: white;
                border: 1px solid #e5e7eb;
                border-radius: 12px;
                border-left: 4px solid {color};
                padding: 15px;
                margin: 5px;
            }}
            QFrame:hover {{
                border-color: {color};
                box-shadow: 0 2px 8px rgba(0, 0, 0, 0.1);
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(8)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Device icon
        device_icon = QLabel("📱")
        device_icon.setFont(QFont("Segoe UI Emoji", 16))
        
        # Repair ID and device
        device_info = f"#{self.repair['id']} - {self.repair['device_type']}"
        if self.repair.get('device_model'):
            device_info += f" {self.repair['device_model']}"
        
        device_label = QLabel(device_info)
        device_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        device_label.setStyleSheet("color: #374151;")
        
        # Status
        status_label = QLabel(status)
        status_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        status_label.setStyleSheet(f"""
            background-color: {color}15;
            color: {color};
            padding: 4px 8px;
            border-radius: 4px;
        """)
        
        header_layout.addWidget(device_icon)
        header_layout.addWidget(device_label, 1)
        header_layout.addWidget(status_label)
        
        # Customer info
        customer_label = QLabel(f"العميل: {self.repair['customer_name']}")
        customer_label.setFont(QFont("Tahoma", 9))
        customer_label.setStyleSheet("color: #6b7280;")
        
        # Problem
        problem = self.repair.get('problem_description', '')
        if len(problem) > 60:
            problem = problem[:60] + "..."
        problem_label = QLabel(f"المشكلة: {problem}")
        problem_label.setFont(QFont("Tahoma", 9))
        problem_label.setStyleSheet("color: #6b7280;")
        problem_label.setWordWrap(True)
        
        # Cost and date
        info_layout = QHBoxLayout()
        
        cost = self.repair.get('estimated_cost', 0)
        cost_label = QLabel(f"التكلفة: {cost:.2f} جنيه")
        cost_label.setFont(QFont("Tahoma", 9, QFont.Weight.Bold))
        cost_label.setStyleSheet("color: #059669;")
        
        date_str = self.repair.get('created_at', '')[:10] if self.repair.get('created_at') else ''
        date_label = QLabel(date_str)
        date_label.setFont(QFont("Tahoma", 8))
        date_label.setStyleSheet("color: #9ca3af;")
        
        info_layout.addWidget(cost_label)
        info_layout.addStretch()
        info_layout.addWidget(date_label)
        
        layout.addLayout(header_layout)
        layout.addWidget(customer_label)
        layout.addWidget(problem_label)
        layout.addLayout(info_layout)

class SearchWidget(QFrame):
    """Generic search widget with filters"""
    
    search_changed = pyqtSignal(str)
    filter_changed = pyqtSignal(str, str)  # filter_type, value
    
    def __init__(self, placeholder="البحث...", filters=None):
        super().__init__()
        self.filters = filters or {}
        self.setup_ui(placeholder)
        
    def setup_ui(self, placeholder):
        """Setup search widget UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QHBoxLayout(self)
        layout.setSpacing(15)
        
        # Search input
        search_layout = QHBoxLayout()
        search_layout.setSpacing(8)
        
        search_icon = QLabel("🔍")
        search_icon.setFont(QFont("Segoe UI Emoji", 12))
        search_icon.setStyleSheet("color: #6b7280;")
        
        self.search_input = QLineEdit()
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.setPlaceholderText(placeholder)
        self.search_input.textChanged.connect(self.search_changed.emit)
        
        search_layout.addWidget(search_icon)
        search_layout.addWidget(self.search_input, 1)
        
        layout.addLayout(search_layout, 2)
        
        # Filters
        for filter_name, filter_options in self.filters.items():
            filter_label = QLabel(f"{filter_name}:")
            filter_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
            
            filter_combo = QComboBox()
            filter_combo.addItems(filter_options)
            filter_combo.setStyleSheet(ModernStyles.get_input_style())
            filter_combo.currentTextChanged.connect(
                lambda value, name=filter_name: self.filter_changed.emit(name, value)
            )
            
            layout.addWidget(filter_label)
            layout.addWidget(filter_combo, 1)

class FilterWidget(QFrame):
    """Advanced filter widget with multiple criteria"""
    
    filters_changed = pyqtSignal(dict)
    
    def __init__(self, filter_config=None):
        super().__init__()
        self.filter_config = filter_config or {}
        self.filter_widgets = {}
        self.setup_ui()
        
    def setup_ui(self):
        """Setup filter widget UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("🔧 المرشحات المتقدمة")
        header.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151;")
        layout.addWidget(header)
        
        # Filters
        filters_layout = QGridLayout()
        filters_layout.setSpacing(10)
        
        row = 0
        col = 0
        
        for filter_name, config in self.filter_config.items():
            filter_label = QLabel(f"{config.get('label', filter_name)}:")
            filter_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
            
            if config['type'] == 'combo':
                widget = QComboBox()
                widget.addItems(config['options'])
                widget.currentTextChanged.connect(self.on_filter_changed)
            elif config['type'] == 'date_range':
                widget = QFrame()
                date_layout = QHBoxLayout(widget)
                date_layout.setContentsMargins(0, 0, 0, 0)
                
                from_date = QDateEdit()
                from_date.setCalendarPopup(True)
                from_date.setStyleSheet(ModernStyles.get_input_style())
                
                to_date = QDateEdit()
                to_date.setCalendarPopup(True)
                to_date.setStyleSheet(ModernStyles.get_input_style())
                
                date_layout.addWidget(QLabel("من:"))
                date_layout.addWidget(from_date)
                date_layout.addWidget(QLabel("إلى:"))
                date_layout.addWidget(to_date)
                
                from_date.dateChanged.connect(self.on_filter_changed)
                to_date.dateChanged.connect(self.on_filter_changed)
                
            elif config['type'] == 'range':
                widget = QFrame()
                range_layout = QHBoxLayout(widget)
                range_layout.setContentsMargins(0, 0, 0, 0)
                
                min_spin = QDoubleSpinBox()
                min_spin.setRange(config.get('min', 0), config.get('max', 9999))
                min_spin.valueChanged.connect(self.on_filter_changed)
                
                max_spin = QDoubleSpinBox()
                max_spin.setRange(config.get('min', 0), config.get('max', 9999))
                max_spin.setValue(config.get('max', 9999))
                max_spin.valueChanged.connect(self.on_filter_changed)
                
                range_layout.addWidget(QLabel("من:"))
                range_layout.addWidget(min_spin)
                range_layout.addWidget(QLabel("إلى:"))
                range_layout.addWidget(max_spin)
                
            else:  # text
                widget = QLineEdit()
                widget.setStyleSheet(ModernStyles.get_input_style())
                widget.textChanged.connect(self.on_filter_changed)
            
            widget.setStyleSheet(ModernStyles.get_input_style())
            
            filters_layout.addWidget(filter_label, row, col * 2)
            filters_layout.addWidget(widget, row, col * 2 + 1)
            
            self.filter_widgets[filter_name] = widget
            
            col += 1
            if col >= 2:
                col = 0
                row += 1
        
        layout.addLayout(filters_layout)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        apply_btn = QPushButton("تطبيق المرشحات")
        apply_btn.setStyleSheet(ModernStyles.get_button_primary_style())
        apply_btn.clicked.connect(self.apply_filters)
        
        clear_btn = QPushButton("مسح الكل")
        clear_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        clear_btn.clicked.connect(self.clear_filters)
        
        buttons_layout.addWidget(apply_btn)
        buttons_layout.addWidget(clear_btn)
        buttons_layout.addStretch()
        
        layout.addLayout(buttons_layout)
        
    def on_filter_changed(self):
        """Handle filter change"""
        # Emit signal with current filter values
        self.apply_filters()
        
    def apply_filters(self):
        """Apply current filters"""
        filters = {}
        
        for filter_name, widget in self.filter_widgets.items():
            if isinstance(widget, QComboBox):
                filters[filter_name] = widget.currentText()
            elif isinstance(widget, QLineEdit):
                filters[filter_name] = widget.text()
            # Add other widget types as needed
                
        self.filters_changed.emit(filters)
        
    def clear_filters(self):
        """Clear all filters"""
        for widget in self.filter_widgets.values():
            if isinstance(widget, QComboBox):
                widget.setCurrentIndex(0)
            elif isinstance(widget, QLineEdit):
                widget.clear()
        
        self.apply_filters()

class ProgressWidget(QFrame):
    """Enhanced progress widget with animations"""
    
    def __init__(self, title="", total=100):
        super().__init__()
        self.title = title
        self.total = total
        self.current = 0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup progress widget UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        if self.title:
            title_label = QLabel(self.title)
            title_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
            title_label.setStyleSheet("color: #374151;")
            layout.addWidget(title_label)
        
        # Progress info
        self.info_layout = QHBoxLayout()
        
        self.progress_label = QLabel("0%")
        self.progress_label.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
        self.progress_label.setStyleSheet("color: #3b82f6;")
        
        self.status_label = QLabel(f"0 / {self.total}")
        self.status_label.setFont(QFont("Tahoma", 9))
        self.status_label.setStyleSheet("color: #6b7280;")
        
        self.info_layout.addWidget(self.progress_label)
        self.info_layout.addStretch()
        self.info_layout.addWidget(self.status_label)
        
        layout.addLayout(self.info_layout)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setMaximum(self.total)
        self.progress_bar.setValue(0)
        self.progress_bar.setStyleSheet(ModernStyles.get_progress_bar_style())
        self.progress_bar.setTextVisible(False)
        
        layout.addWidget(self.progress_bar)
        
    def set_progress(self, value):
        """Set progress value"""
        self.current = min(value, self.total)
        percentage = int((self.current / self.total) * 100) if self.total > 0 else 0
        
        self.progress_bar.setValue(self.current)
        self.progress_label.setText(f"{percentage}%")
        self.status_label.setText(f"{self.current} / {self.total}")
        
    def set_total(self, total):
        """Set total value"""
        self.total = total
        self.progress_bar.setMaximum(total)
        self.set_progress(self.current)
        
    def increment(self, value=1):
        """Increment progress by value"""
        self.set_progress(self.current + value)
        
    def reset(self):
        """Reset progress to 0"""
        self.set_progress(0)

class NotificationWidget(QFrame):
    """In-app notification widget"""
    
    dismissed = pyqtSignal()
    
    def __init__(self, message, message_type="info", timeout=5000):
        super().__init__()
        self.message = message
        self.message_type = message_type
        self.timeout = timeout
        self.setup_ui()
        
        if timeout > 0:
            QTimer.singleShot(timeout, self.dismiss)
        
    def setup_ui(self):
        """Setup notification UI"""
        # Colors based on message type
        colors = {
            "info": {"bg": "#dbeafe", "border": "#3b82f6", "text": "#1e40af"},
            "success": {"bg": "#dcfce7", "border": "#10b981", "text": "#065f46"},
            "warning": {"bg": "#fef3c7", "border": "#f59e0b", "text": "#92400e"},
            "error": {"bg": "#fee2e2", "border": "#ef4444", "text": "#991b1b"}
        }
        
        color_set = colors.get(self.message_type, colors["info"])
        
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color_set['bg']};
                border: 1px solid {color_set['border']};
                border-radius: 8px;
                padding: 12px;
                margin: 5px;
            }}
        """)
        
        layout = QHBoxLayout(self)
        layout.setSpacing(10)
        
        # Icon
        icons = {
            "info": "ℹ️",
            "success": "✅", 
            "warning": "⚠️",
            "error": "❌"
        }
        
        icon_label = QLabel(icons.get(self.message_type, "ℹ️"))
        icon_label.setFont(QFont("Segoe UI Emoji", 14))
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Tahoma", 10))
        message_label.setStyleSheet(f"color: {color_set['text']};")
        message_label.setWordWrap(True)
        
        # Close button
        close_btn = QPushButton("✕")
        close_btn.setFixedSize(20, 20)
        close_btn.setStyleSheet(f"""
            QPushButton {{
                background: transparent;
                border: none;
                color: {color_set['text']};
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {color_set['border']}20;
                border-radius: 10px;
            }}
        """)
        close_btn.clicked.connect(self.dismiss)
        
        layout.addWidget(icon_label)
        layout.addWidget(message_label, 1)
        layout.addWidget(close_btn)
        
    def dismiss(self):
        """Dismiss notification"""
        self.dismissed.emit()
        self.hide()
        self.deleteLater()

class LoadingWidget(QFrame):
    """Loading indicator widget"""
    
    def __init__(self, message="جاري التحميل..."):
        super().__init__()
        self.message = message
        self.angle = 0
        self.setup_ui()
        
        # Animation timer
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
    def setup_ui(self):
        """Setup loading widget UI"""
        self.setFixedSize(200, 100)
        self.setStyleSheet("""
            QFrame {
                background-color: rgba(255, 255, 255, 0.95);
                border: 1px solid #e5e7eb;
                border-radius: 12px;
            }
        """)
        
        layout = QVBoxLayout(self)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.setSpacing(15)
        
        # Spinner
        self.spinner_label = QLabel("⟳")
        self.spinner_label.setFont(QFont("Segoe UI Emoji", 24))
        self.spinner_label.setStyleSheet("color: #3b82f6;")
        self.spinner_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Message
        message_label = QLabel(self.message)
        message_label.setFont(QFont("Tahoma", 10))
        message_label.setStyleSheet("color: #6b7280;")
        message_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        layout.addWidget(self.spinner_label)
        layout.addWidget(message_label)
        
    def start(self):
        """Start loading animation"""
        self.timer.start(100)  # Rotate every 100ms
        self.show()
        
    def stop(self):
        """Stop loading animation"""
        self.timer.stop()
        self.hide()
        
    def rotate(self):
        """Rotate spinner"""
        self.angle = (self.angle + 30) % 360
        # Simple rotation effect by changing the spinner character
        spinners = ["⟳", "⟲", "⟳", "⟲"]
        self.spinner_label.setText(spinners[self.angle // 90])

class RatingWidget(QFrame):
    """Star rating widget"""
    
    rating_changed = pyqtSignal(int)
    
    def __init__(self, max_rating=5, current_rating=0):
        super().__init__()
        self.max_rating = max_rating
        self.current_rating = current_rating
        self.stars = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup rating widget UI"""
        layout = QHBoxLayout(self)
        layout.setSpacing(2)
        layout.setContentsMargins(0, 0, 0, 0)
        
        for i in range(self.max_rating):
            star_btn = QPushButton("⭐")
            star_btn.setFixedSize(25, 25)
            star_btn.setStyleSheet("""
                QPushButton {
                    background: transparent;
                    border: none;
                    font-size: 16px;
                }
                QPushButton:hover {
                    background-color: #fef3c7;
                    border-radius: 12px;
                }
            """)
            star_btn.clicked.connect(lambda checked, rating=i+1: self.set_rating(rating))
            
            self.stars.append(star_btn)
            layout.addWidget(star_btn)
            
        self.update_stars()
        
    def set_rating(self, rating):
        """Set current rating"""
        self.current_rating = max(0, min(rating, self.max_rating))
        self.update_stars()
        self.rating_changed.emit(self.current_rating)
        
    def update_stars(self):
        """Update star display"""
        for i, star in enumerate(self.stars):
            if i < self.current_rating:
                star.setText("⭐")
                star.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        font-size: 16px;
                        color: #f59e0b;
                    }
                    QPushButton:hover {
                        background-color: #fef3c7;
                        border-radius: 12px;
                    }
                """)
            else:
                star.setText("☆")
                star.setStyleSheet("""
                    QPushButton {
                        background: transparent;
                        border: none;
                        font-size: 16px;
                        color: #d1d5db;
                    }
                    QPushButton:hover {
                        background-color: #fef3c7;
                        border-radius: 12px;
                        color: #f59e0b;
                    }
                """)
