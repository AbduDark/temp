"""
Enhanced Wallet Management Page for Mobile Shop Management System
Comprehensive digital wallet transactions management with modern UI
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

from ui.styles import ModernStyles
from ui.dialogs import WalletTransactionDialog
from ui.widgets import StatCard, TransactionCard

class WalletBalanceWidget(QFrame):
    """Wallet balance display widget for different providers"""
    
    def __init__(self, provider, provider_name, color, db_manager):
        super().__init__()
        self.provider = provider
        self.provider_name = provider_name
        self.color = color
        self.db_manager = db_manager
        self.balance = 0.0
        self.setup_ui()
        
    def setup_ui(self):
        """Setup balance widget UI"""
        self.setFixedHeight(160)
        self.setStyleSheet(f"""
            QFrame {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 {self.color}, stop:1 {self.color}cc);
                border-radius: 15px;
                padding: 20px;
            }}
        """)
        
        # Add shadow effect
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(15)
        shadow.setColor(QColor(0, 0, 0, 20))
        shadow.setOffset(0, 3)
        self.setGraphicsEffect(shadow)
        
        layout = QVBoxLayout(self)
        layout.setSpacing(10)
        
        # Header
        header_layout = QHBoxLayout()
        
        # Provider icon and name
        provider_icons = {
            'vodafone': '📱',
            'orange': '🍊', 
            'etisalat': '📶'
        }
        
        icon_label = QLabel(provider_icons.get(self.provider, '💳'))
        icon_label.setFont(QFont("Segoe UI Emoji", 24))
        icon_label.setStyleSheet("color: white;")
        
        name_label = QLabel(self.provider_name)
        name_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        name_label.setStyleSheet("color: white;")
        
        header_layout.addWidget(icon_label)
        header_layout.addWidget(name_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # Balance
        self.balance_label = QLabel("0.00 جنيه")
        self.balance_label.setFont(QFont("Tahoma", 22, QFont.Weight.Bold))
        self.balance_label.setStyleSheet("color: white; margin: 10px 0;")
        layout.addWidget(self.balance_label)
        
        # Statistics
        stats_layout = QHBoxLayout()
        
        self.transactions_today_label = QLabel("0 معاملة اليوم")
        self.transactions_today_label.setFont(QFont("Tahoma", 10))
        self.transactions_today_label.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        stats_layout.addWidget(self.transactions_today_label)
        stats_layout.addStretch()
        
        layout.addLayout(stats_layout)
        layout.addStretch()
        
    def update_balance(self):
        """Update balance and statistics"""
        try:
            # Get total balance
            balance_result = self.db_manager.execute_query("""
                SELECT COALESCE(SUM(amount), 0) as balance 
                FROM wallet_transactions 
                WHERE provider = ?
            """, (self.provider,))
            
            self.balance = balance_result[0]['balance'] if balance_result else 0.0
            self.balance_label.setText(f"{self.balance:.2f} جنيه")
            
            # Get today's transactions count
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = self.db_manager.execute_query("""
                SELECT COUNT(*) as count 
                FROM wallet_transactions 
                WHERE provider = ? AND DATE(created_at) = ?
            """, (self.provider, today))
            
            count = today_count[0]['count'] if today_count else 0
            self.transactions_today_label.setText(f"{count} معاملة اليوم")
            
        except Exception as e:
            print(f"Error updating balance for {self.provider}: {e}")

class WalletTransactionTable(QTableWidget):
    """Enhanced wallet transaction table"""
    
    transaction_selected = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.transactions_data = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup table UI"""
        self.setColumnCount(10)
        self.setHorizontalHeaderLabels([
            "الإجراءات", "المبلغ الصافي", "الرسوم", "المبلغ", "نوع الخدمة", 
            "نوع المعاملة", "المزود", "العميل", "الرقم المرجعي", "التاريخ"
        ])
        
        # Set column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.resizeSection(0, 100)  # Actions
        header.resizeSection(1, 120)  # Net amount
        header.resizeSection(2, 80)   # Fees
        header.resizeSection(3, 100)  # Amount
        header.resizeSection(4, 120)  # Service type
        header.resizeSection(5, 120)  # Transaction type
        header.resizeSection(6, 100)  # Provider
        header.resizeSection(7, 150)  # Customer
        header.resizeSection(8, 120)  # Reference
        header.resizeSection(9, 140)  # Date
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setStyleSheet(ModernStyles.get_table_style())
        
        # Connect signals
        self.itemSelectionChanged.connect(self.on_selection_changed)
        
    def populate_table(self, transactions):
        """Populate table with transactions data"""
        self.transactions_data = transactions
        self.setRowCount(len(transactions))
        
        # Provider display names
        provider_names = {
            'vodafone': 'فودافون كاش',
            'orange': 'أورانج كاش',
            'etisalat': 'اتصالات كاش'
        }
        
        # Transaction type display names
        type_names = {
            'receive': 'استقبال',
            'send': 'إرسال',
            'deposit': 'إيداع',
            'withdraw': 'سحب',
            'fees': 'رسوم',
            'transfer': 'تحويل',
            'payment': 'دفع',
            'refund': 'استرداد'
        }
        
        for row, transaction in enumerate(transactions):
            # Actions
            actions_widget = self.create_actions_widget(transaction)
            self.setCellWidget(row, 0, actions_widget)
            
            # Net amount
            net_amount = transaction.get('net_amount', transaction['amount'])
            net_item = QTableWidgetItem(f"{net_amount:.2f} جنيه")
            if net_amount > 0:
                net_item.setBackground(QColor(220, 252, 231))  # Green
                net_item.setForeground(QColor(5, 150, 105))
            else:
                net_item.setBackground(QColor(254, 226, 226))  # Red
                net_item.setForeground(QColor(153, 27, 27))
            self.setItem(row, 1, net_item)
            
            # Fees
            fees = transaction.get('fees', 0.0)
            self.setItem(row, 2, QTableWidgetItem(f"{fees:.2f}" if fees > 0 else "-"))
            
            # Amount
            amount_item = QTableWidgetItem(f"{transaction['amount']:.2f} جنيه")
            if transaction['amount'] > 0:
                amount_item.setForeground(QColor(5, 150, 105))
            else:
                amount_item.setForeground(QColor(153, 27, 27))
            self.setItem(row, 3, amount_item)
            
            # Service type
            service_type = transaction.get('service_type', '-')
            self.setItem(row, 4, QTableWidgetItem(service_type))
            
            # Transaction type
            trans_type = type_names.get(transaction['transaction_type'], transaction['transaction_type'])
            self.setItem(row, 5, QTableWidgetItem(trans_type))
            
            # Provider
            provider_name = provider_names.get(transaction['provider'], transaction['provider'])
            self.setItem(row, 6, QTableWidgetItem(provider_name))
            
            # Customer
            customer = transaction.get('customer_name', '') or transaction.get('customer_phone', '') or '-'
            self.setItem(row, 7, QTableWidgetItem(customer))
            
            # Reference
            reference = transaction.get('reference', '') or transaction.get('external_reference', '') or '-'
            self.setItem(row, 8, QTableWidgetItem(reference))
            
            # Date
            date_str = transaction['created_at'][:16] if transaction['created_at'] else '-'
            self.setItem(row, 9, QTableWidgetItem(date_str))
            
    def create_actions_widget(self, transaction):
        """Create actions widget for transaction row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # View details button
        details_btn = QPushButton("👁️")
        details_btn.setFixedSize(30, 25)
        details_btn.setToolTip("عرض التفاصيل")
        details_btn.setStyleSheet("""
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
        details_btn.clicked.connect(lambda: self.view_details(transaction))
        
        # Delete button (only for recent transactions)
        delete_btn = QPushButton("🗑️")
        delete_btn.setFixedSize(30, 25)
        delete_btn.setToolTip("حذف المعاملة")
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
        delete_btn.clicked.connect(lambda: self.delete_transaction(transaction))
        
        layout.addWidget(details_btn)
        layout.addWidget(delete_btn)
        
        return widget
        
    def view_details(self, transaction):
        """View transaction details"""
        self.transaction_selected.emit(transaction)
        
    def delete_transaction(self, transaction):
        """Delete transaction"""
        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف هذه المعاملة؟\nالمبلغ: {transaction['amount']:.2f} جنيه",
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
                        "DELETE FROM wallet_transactions WHERE id = ?",
                        (transaction['id'],)
                    )
                    QMessageBox.information(self, "نجح", "تم حذف المعاملة بنجاح")
                    # Refresh table
                    if hasattr(parent, 'refresh_transactions'):
                        parent.refresh_transactions()
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المعاملة: {str(e)}")
        
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.transactions_data):
            transaction = self.transactions_data[current_row]
            self.transaction_selected.emit(transaction)

class WalletPage(QWidget):
    """Enhanced wallet management page"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_transactions = []
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup wallet page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.setup_header(main_layout)
        
        # Balance cards section
        self.setup_balance_cards(main_layout)
        
        # Quick actions section
        self.setup_quick_actions(main_layout)
        
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
                    stop:0 #10b981, stop:1 #059669);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("💰 إدارة المحفظة الإلكترونية")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("إدارة معاملات فودافون كاش وأورانج كاش واتصالات كاش")
        subtitle.setFont(QFont("Tahoma", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Summary info
        self.summary_label = QLabel()
        self.summary_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
        self.summary_label.setStyleSheet("color: white;")
        self.summary_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addWidget(self.summary_label)
        
        parent_layout.addWidget(header_frame)
        
    def setup_balance_cards(self, parent_layout):
        """Setup balance cards for different providers"""
        cards_frame = QFrame()
        cards_layout = QGridLayout(cards_frame)
        cards_layout.setSpacing(20)
        
        # Provider configurations
        providers = [
            ('vodafone', 'فودافون كاش', '#e60000'),
            ('orange', 'أورانج كاش', '#ff6600'),
            ('etisalat', 'اتصالات كاش', '#0066cc')
        ]
        
        self.balance_widgets = {}
        
        for i, (provider, name, color) in enumerate(providers):
            balance_widget = WalletBalanceWidget(provider, name, color, self.db_manager)
            self.balance_widgets[provider] = balance_widget
            cards_layout.addWidget(balance_widget, 0, i)
        
        # Total balance card
        self.total_balance_card = StatCard("إجمالي الرصيد", "0.00 جنيه", "💳", "#6366f1")
        cards_layout.addWidget(self.total_balance_card, 0, 3)
        
        parent_layout.addWidget(cards_frame)
        
    def setup_quick_actions(self, parent_layout):
        """Setup quick actions section"""
        actions_frame = QFrame()
        actions_frame.setStyleSheet(ModernStyles.get_card_style())
        
        actions_layout = QVBoxLayout(actions_frame)
        actions_layout.setSpacing(15)
        
        # Header
        header = QLabel("⚡ الإجراءات السريعة")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        actions_layout.addWidget(header)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(15)
        
        # New transaction button
        new_transaction_btn = QPushButton("➕ معاملة جديدة")
        new_transaction_btn.setFixedHeight(50)
        new_transaction_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        new_transaction_btn.clicked.connect(self.add_transaction)
        
        # Quick receive button
        quick_receive_btn = QPushButton("📥 استقبال سريع")
        quick_receive_btn.setFixedHeight(50)
        quick_receive_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        quick_receive_btn.clicked.connect(self.quick_receive)
        
        # Quick send button
        quick_send_btn = QPushButton("📤 إرسال سريع")
        quick_send_btn.setFixedHeight(50)
        quick_send_btn.setStyleSheet("""
            QPushButton {
                background-color: #f59e0b;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #d97706;
            }
        """)
        quick_send_btn.clicked.connect(self.quick_send)
        
        # Balance check button
        balance_btn = QPushButton("💳 تحديث الأرصدة")
        balance_btn.setFixedHeight(50)
        balance_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 15px 25px;
                border-radius: 10px;
                font-weight: bold;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        balance_btn.clicked.connect(self.refresh_balances)
        
        buttons_layout.addWidget(new_transaction_btn)
        buttons_layout.addWidget(quick_receive_btn)
        buttons_layout.addWidget(quick_send_btn)
        buttons_layout.addWidget(balance_btn)
        buttons_layout.addStretch()
        
        actions_layout.addLayout(buttons_layout)
        parent_layout.addWidget(actions_frame)
        
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
        self.search_input.setPlaceholderText("البحث برقم المرجع، اسم العميل، أو رقم الهاتف...")
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.textChanged.connect(self.filter_transactions)
        
        # Provider filter
        provider_label = QLabel("📱 المزود:")
        provider_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.provider_filter = QComboBox()
        self.provider_filter.addItems([
            "جميع المزودين", "فودافون كاش", "أورانج كاش", "اتصالات كاش"
        ])
        self.provider_filter.setStyleSheet(ModernStyles.get_input_style())
        self.provider_filter.currentTextChanged.connect(self.filter_transactions)
        
        # Transaction type filter
        type_label = QLabel("💳 نوع المعاملة:")
        type_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.type_filter = QComboBox()
        self.type_filter.addItems([
            "جميع الأنواع", "استقبال", "إرسال", "إيداع", "سحب", "رسوم", "تحويل"
        ])
        self.type_filter.setStyleSheet(ModernStyles.get_input_style())
        self.type_filter.currentTextChanged.connect(self.filter_transactions)
        
        # Date range
        date_label = QLabel("📅 التاريخ:")
        date_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(ModernStyles.get_input_style())
        self.date_from.dateChanged.connect(self.filter_transactions)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(ModernStyles.get_input_style())
        self.date_to.dateChanged.connect(self.filter_transactions)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        refresh_btn.clicked.connect(self.refresh_data)
        
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_input, 2)
        filters_layout.addWidget(provider_label)
        filters_layout.addWidget(self.provider_filter, 1)
        filters_layout.addWidget(type_label)
        filters_layout.addWidget(self.type_filter, 1)
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(QLabel("إلى"))
        filters_layout.addWidget(self.date_to)
        filters_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(filters_frame)
        
    def setup_main_content(self, parent_layout):
        """Setup main content area"""
        # Create splitter for table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Transactions table
        table_frame = QFrame()
        table_frame.setStyleSheet(ModernStyles.get_card_style())
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_header = QLabel("📋 قائمة المعاملات")
        table_header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        table_header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        
        self.transactions_table = WalletTransactionTable()
        self.transactions_table.transaction_selected.connect(self.on_transaction_selected)
        
        table_layout.addWidget(table_header)
        table_layout.addWidget(self.transactions_table)
        
        # Transaction details panel
        self.details_frame = QFrame()
        self.details_frame.setStyleSheet(ModernStyles.get_card_style())
        self.details_frame.setFixedWidth(350)
        self.setup_details_panel()
        
        splitter.addWidget(table_frame)
        splitter.addWidget(self.details_frame)
        splitter.setSizes([800, 350])
        
        parent_layout.addWidget(splitter, 1)
        
    def setup_details_panel(self):
        """Setup transaction details panel"""
        layout = QVBoxLayout(self.details_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📄 تفاصيل المعاملة")
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
        default_label = QLabel("اختر معاملة من القائمة لعرض التفاصيل")
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_label.setStyleSheet("color: #9ca3af; font-style: italic; padding: 50px;")
        self.details_layout.addWidget(default_label)
        
        self.details_scroll.setWidget(self.details_widget)
        layout.addWidget(self.details_scroll, 1)
        
    def refresh_data(self):
        """Refresh all data"""
        try:
            # Refresh balances
            self.refresh_balances()
            
            # Refresh transactions
            self.refresh_transactions()
            
            # Update summary
            self.update_summary()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث البيانات: {str(e)}")
            
    def refresh_balances(self):
        """Refresh balance cards"""
        try:
            total_balance = 0.0
            
            for provider, widget in self.balance_widgets.items():
                widget.update_balance()
                total_balance += widget.balance
            
            self.total_balance_card.update_value(f"{total_balance:.2f} جنيه")
            
        except Exception as e:
            print(f"Error refreshing balances: {e}")
            
    def refresh_transactions(self):
        """Refresh transactions table"""
        try:
            transactions = self.db_manager.execute_query("""
                SELECT * FROM wallet_transactions 
                ORDER BY created_at DESC
                LIMIT 1000
            """)
            
            self.current_transactions = transactions
            self.transactions_table.populate_table(transactions)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المعاملات: {str(e)}")
            
    def update_summary(self):
        """Update summary information"""
        try:
            today = datetime.now().strftime("%Y-%m-%d")
            
            # Get today's statistics
            today_stats = self.db_manager.execute_query("""
                SELECT 
                    COUNT(*) as count,
                    COALESCE(SUM(ABS(amount)), 0) as volume
                FROM wallet_transactions 
                WHERE DATE(created_at) = ?
            """, (today,))
            
            if today_stats:
                stats = today_stats[0]
                self.summary_label.setText(
                    f"اليوم: {stats['count']} معاملة\n"
                    f"الحجم: {stats['volume']:.2f} جنيه"
                )
            
        except Exception as e:
            print(f"Error updating summary: {e}")
            
    def filter_transactions(self):
        """Filter transactions based on search and filters"""
        try:
            search_text = self.search_input.text().lower()
            provider = self.provider_filter.currentText()
            trans_type = self.type_filter.currentText()
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            
            # Provider mapping
            provider_map = {
                "فودافون كاش": "vodafone",
                "أورانج كاش": "orange", 
                "اتصالات كاش": "etisalat"
            }
            
            # Type mapping
            type_map = {
                "استقبال": "receive",
                "إرسال": "send",
                "إيداع": "deposit",
                "سحب": "withdraw",
                "رسوم": "fees",
                "تحويل": "transfer"
            }
            
            filtered_transactions = []
            
            for transaction in self.current_transactions:
                # Apply search filter
                if search_text:
                    if not (search_text in (transaction.get('reference', '') or '').lower() or 
                           search_text in (transaction.get('external_reference', '') or '').lower() or
                           search_text in (transaction.get('customer_name', '') or '').lower() or
                           search_text in (transaction.get('customer_phone', '') or '').lower()):
                        continue
                
                # Apply provider filter
                if provider != "جميع المزودين":
                    if transaction['provider'] != provider_map.get(provider, provider):
                        continue
                
                # Apply type filter
                if trans_type != "جميع الأنواع":
                    if transaction['transaction_type'] != type_map.get(trans_type, trans_type):
                        continue
                
                # Apply date filter
                if transaction['created_at']:
                    trans_date = transaction['created_at'][:10]
                    if not (date_from <= trans_date <= date_to):
                        continue
                
                filtered_transactions.append(transaction)
            
            self.transactions_table.populate_table(filtered_transactions)
            
        except Exception as e:
            print(f"Error filtering transactions: {e}")
            
    def on_transaction_selected(self, transaction):
        """Handle transaction selection"""
        try:
            # Clear existing details
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
            
            # Transaction icon based on type
            type_icons = {
                'receive': '📥',
                'send': '📤',
                'deposit': '💰',
                'withdraw': '🏧',
                'fees': '💳',
                'transfer': '🔄'
            }
            
            icon = type_icons.get(transaction['transaction_type'], '💳')
            
            # Transaction icon
            icon_label = QLabel(icon)
            icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            icon_label.setStyleSheet("""
                QLabel {
                    background-color: #f3f4f6;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 48px;
                }
            """)
            icon_label.setFixedHeight(120)
            self.details_layout.addWidget(icon_label)
            
            # Transaction amount
            amount_label = QLabel(f"{transaction['amount']:.2f} جنيه")
            amount_label.setFont(QFont("Tahoma", 18, QFont.Weight.Bold))
            if transaction['amount'] > 0:
                amount_label.setStyleSheet("color: #10b981;")
            else:
                amount_label.setStyleSheet("color: #ef4444;")
            amount_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            self.details_layout.addWidget(amount_label)
            
            # Transaction details
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
            
            # Provider
            provider_names = {
                'vodafone': 'فودافون كاش',
                'orange': 'أورانج كاش',
                'etisalat': 'اتصالات كاش'
            }
            provider_name = provider_names.get(transaction['provider'], transaction['provider'])
            details_layout.addRow("المزود:", QLabel(provider_name))
            
            # Transaction type
            type_names = {
                'receive': 'استقبال',
                'send': 'إرسال',
                'deposit': 'إيداع',
                'withdraw': 'سحب',
                'fees': 'رسوم',
                'transfer': 'تحويل'
            }
            type_name = type_names.get(transaction['transaction_type'], transaction['transaction_type'])
            details_layout.addRow("نوع المعاملة:", QLabel(type_name))
            
            # Service type
            if transaction.get('service_type'):
                details_layout.addRow("نوع الخدمة:", QLabel(transaction['service_type']))
            
            # Fees
            if transaction.get('fees') and transaction['fees'] > 0:
                details_layout.addRow("الرسوم:", QLabel(f"{transaction['fees']:.2f} جنيه"))
            
            # Net amount
            if transaction.get('net_amount'):
                details_layout.addRow("المبلغ الصافي:", QLabel(f"{transaction['net_amount']:.2f} جنيه"))
            
            # Customer info
            if transaction.get('customer_name'):
                details_layout.addRow("اسم العميل:", QLabel(transaction['customer_name']))
            if transaction.get('customer_phone'):
                details_layout.addRow("رقم الهاتف:", QLabel(transaction['customer_phone']))
            
            # Phone numbers
            if transaction.get('sender_number'):
                details_layout.addRow("رقم المرسل:", QLabel(transaction['sender_number']))
            if transaction.get('recipient_number'):
                details_layout.addRow("رقم المستقبل:", QLabel(transaction['recipient_number']))
            
            # References
            if transaction.get('reference'):
                details_layout.addRow("رقم المرجع:", QLabel(transaction['reference']))
            if transaction.get('external_reference'):
                details_layout.addRow("المرجع الخارجي:", QLabel(transaction['external_reference']))
            
            # Status
            status_label = QLabel(transaction.get('status', 'مكتملة'))
            if transaction.get('status') == 'completed':
                status_label.setStyleSheet("color: #10b981; font-weight: bold;")
            elif transaction.get('status') == 'pending':
                status_label.setStyleSheet("color: #f59e0b; font-weight: bold;")
            elif transaction.get('status') == 'failed':
                status_label.setStyleSheet("color: #ef4444; font-weight: bold;")
            details_layout.addRow("الحالة:", status_label)
            
            # Date
            details_layout.addRow("التاريخ:", QLabel(transaction['created_at'][:16]))
            
            # Cashier
            if transaction.get('cashier'):
                details_layout.addRow("الكاشير:", QLabel(transaction['cashier']))
            
            self.details_layout.addWidget(details_frame)
            
            # Notes
            if transaction.get('notes'):
                notes_frame = QFrame()
                notes_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f0fdf4;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                
                notes_layout = QVBoxLayout(notes_frame)
                
                notes_title = QLabel("ملاحظات:")
                notes_title.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                
                notes_text = QLabel(transaction['notes'])
                notes_text.setWordWrap(True)
                notes_text.setStyleSheet("color: #6b7280;")
                
                notes_layout.addWidget(notes_title)
                notes_layout.addWidget(notes_text)
                
                self.details_layout.addWidget(notes_frame)
            
            # Action buttons
            buttons_frame = QFrame()
            buttons_layout = QVBoxLayout(buttons_frame)
            buttons_layout.setSpacing(10)
            
            print_btn = QPushButton("🖨️ طباعة إيصال")
            print_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
            print_btn.clicked.connect(lambda: self.print_receipt(transaction))
            
            buttons_layout.addWidget(print_btn)
            
            self.details_layout.addWidget(buttons_frame)
            self.details_layout.addStretch()
            
        except Exception as e:
            print(f"Error displaying transaction details: {e}")
            
    def add_transaction(self):
        """Add new transaction"""
        dialog = WalletTransactionDialog(self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def quick_receive(self):
        """Quick receive transaction"""
        dialog = WalletTransactionDialog(self.db_manager, self, transaction_type='receive')
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def quick_send(self):
        """Quick send transaction"""
        dialog = WalletTransactionDialog(self.db_manager, self, transaction_type='send')
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def print_receipt(self, transaction):
        """Print transaction receipt"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة الطباعة قريباً")
