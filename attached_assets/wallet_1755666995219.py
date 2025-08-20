"""
Wallet Management Page for Desktop Application
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QTableWidget, QTableWidgetItem,
    QLabel, QPushButton, QLineEdit, QComboBox, QFrame, QHeaderView,
    QMessageBox, QDialog, QFormLayout, QDoubleSpinBox, QTextEdit
)
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QFont
from uuid import uuid4

class WalletPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        title = QLabel("معاملات المحفظة الإلكترونية")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setAlignment(Qt.AlignmentFlag.AlignRight)
        layout.addWidget(title)
        
        # Balance cards
        self.setup_balance_cards(layout)
        
        # Controls
        controls_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث في المعاملات...")
        self.search_input.textChanged.connect(self.filter_transactions)
        
        add_btn = QPushButton("معاملة جديدة")
        add_btn.clicked.connect(self.add_transaction)
        
        controls_layout.addWidget(self.search_input)
        controls_layout.addWidget(add_btn)
        layout.addLayout(controls_layout)
        
        # Transactions table
        self.table = QTableWidget()
        self.table.setColumnCount(6)
        self.table.setHorizontalHeaderLabels([
            "العمليات", "المبلغ", "النوع", "المزود", "العميل", "التاريخ"
        ])
        
        header = self.table.horizontalHeader()
        header.setSectionResizeMode(QHeaderView.ResizeMode.Stretch)
        
        layout.addWidget(self.table)
        
    def setup_balance_cards(self, parent_layout):
        balances_frame = QFrame()
        balances_layout = QHBoxLayout(balances_frame)
        
        # Provider balances
        providers = [
            ("vodafone", "فودافون كاش", "#e60000"),
            ("orange", "أورانج كاش", "#ff6600"), 
            ("etisalat", "اتصالات كاش", "#0066cc")
        ]
        
        self.balance_labels = {}
        
        for provider_key, provider_name, color in providers:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{
                    background-color: white;
                    border: 2px solid {color};
                    border-radius: 8px;
                    padding: 15px;
                }}
            """)
            
            card_layout = QVBoxLayout(card)
            
            name_label = QLabel(provider_name)
            name_label.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
            name_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            name_label.setStyleSheet(f"color: {color};")
            
            balance_label = QLabel("0.00 جنيه")
            balance_label.setFont(QFont("Tahoma", 18, QFont.Weight.Bold))
            balance_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            card_layout.addWidget(name_label)
            card_layout.addWidget(balance_label)
            
            self.balance_labels[provider_key] = balance_label
            balances_layout.addWidget(card)
        
        parent_layout.addWidget(balances_frame)
        
    def refresh_data(self):
        try:
            # Update balances
            for provider in ["vodafone", "orange", "etisalat"]:
                balance_data = self.db_manager.execute_query("""
                    SELECT COALESCE(SUM(amount), 0) as balance 
                    FROM wallet_transactions 
                    WHERE provider = ?
                """, (provider,))
                
                balance = balance_data[0]['balance'] if balance_data else 0
                self.balance_labels[provider].setText(f"{balance:.2f} جنيه")
            
            # Load transactions
            transactions = self.db_manager.execute_query(
                "SELECT * FROM wallet_transactions ORDER BY created_at DESC"
            )
            self.populate_table(transactions)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المعاملات: {e}")
    
    def populate_table(self, transactions):
        self.table.setRowCount(len(transactions))
        
        type_labels = {
            "send": "إرسال",
            "receive": "استقبال",
            "deposit": "إيداع",
            "withdraw": "سحب",
            "fees": "رسوم"
        }
        
        provider_labels = {
            "vodafone": "فودافون",
            "orange": "أورانج",
            "etisalat": "اتصالات"
        }
        
        for row, transaction in enumerate(transactions):
            self.table.setItem(row, 5, QTableWidgetItem(transaction['created_at'][:10]))
            self.table.setItem(row, 4, QTableWidgetItem(transaction.get('customer_name', '')))
            self.table.setItem(row, 3, QTableWidgetItem(provider_labels.get(transaction['provider'], transaction['provider'])))
            self.table.setItem(row, 2, QTableWidgetItem(type_labels.get(transaction['type'], transaction['type'])))
            
            # Amount with color
            amount_item = QTableWidgetItem(f"{transaction['amount']:.2f} جنيه")
            if transaction['amount'] > 0:
                amount_item.setBackground(Qt.GlobalColor.lightGreen)
            else:
                amount_item.setBackground(Qt.GlobalColor.lightGray)
            self.table.setItem(row, 1, amount_item)
            
            # Action buttons
            actions_widget = QWidget()
            actions_layout = QHBoxLayout(actions_widget)
            
            delete_btn = QPushButton("حذف")
            delete_btn.clicked.connect(lambda checked, t=transaction: self.delete_transaction(t))
            delete_btn.setStyleSheet("background-color: #ef4444; color: white;")
            
            actions_layout.addWidget(delete_btn)
            self.table.setCellWidget(row, 0, actions_widget)
    
    def filter_transactions(self, text):
        for row in range(self.table.rowCount()):
            show_row = False
            for col in range(1, self.table.columnCount()):
                item = self.table.item(row, col)
                if item and text.lower() in item.text().lower():
                    show_row = True
                    break
            self.table.setRowHidden(row, not show_row)
    
    def add_transaction(self):
        dialog = WalletDialog(self.db_manager)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            self.refresh_data()
    
    def delete_transaction(self, transaction):
        reply = QMessageBox.question(
            self, "تأكيد الحذف", 
            "هل أنت متأكد من حذف هذه المعاملة؟"
        )
        if reply == QMessageBox.StandardButton.Yes:
            try:
                self.db_manager.execute_update(
                    "DELETE FROM wallet_transactions WHERE id = ?", 
                    (transaction['id'],)
                )
                self.refresh_data()
                QMessageBox.information(self, "نجح", "تم حذف المعاملة بنجاح")
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المعاملة: {e}")

class WalletDialog(QDialog):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
    
    def setup_ui(self):
        self.setWindowTitle("معاملة محفظة جديدة")
        self.setModal(True)
        self.resize(400, 300)
        
        layout = QFormLayout(self)
        
        # Form fields
        self.provider_input = QComboBox()
        self.provider_input.addItems([
            ("فودافون كاش", "vodafone"),
            ("أورانج كاش", "orange"),
            ("اتصالات كاش", "etisalat")
        ])
        
        self.type_input = QComboBox()
        self.type_input.addItems([
            ("استقبال", "receive"),
            ("إرسال", "send"),
            ("إيداع", "deposit"),
            ("سحب", "withdraw"),
            ("رسوم", "fees")
        ])
        
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0, 999999)
        self.amount_input.setDecimals(2)
        
        self.customer_name_input = QLineEdit()
        self.reference_input = QLineEdit()
        self.notes_input = QTextEdit()
        
        # Add to form
        layout.addRow("مقدم الخدمة:", self.provider_input)
        layout.addRow("نوع المعاملة:", self.type_input)
        layout.addRow("المبلغ:", self.amount_input)
        layout.addRow("اسم العميل:", self.customer_name_input)
        layout.addRow("رقم المرجع:", self.reference_input)
        layout.addRow("ملاحظات:", self.notes_input)
        
        # Buttons
        buttons_layout = QHBoxLayout()
        save_btn = QPushButton("حفظ")
        cancel_btn = QPushButton("إلغاء")
        
        save_btn.clicked.connect(self.save_transaction)
        cancel_btn.clicked.connect(self.reject)
        
        buttons_layout.addWidget(save_btn)
        buttons_layout.addWidget(cancel_btn)
        layout.addRow(buttons_layout)
    
    def save_transaction(self):
        if self.amount_input.value() == 0:
            QMessageBox.warning(self, "تحذير", "يرجى إدخال مبلغ صحيح")
            return
        
        try:
            # Adjust amount sign based on transaction type
            amount = self.amount_input.value()
            transaction_type = self.type_input.currentData()
            
            if transaction_type in ['send', 'withdraw', 'fees']:
                amount = -abs(amount)  # Make negative for outgoing
            else:
                amount = abs(amount)   # Make positive for incoming
            
            transaction_id = str(uuid4())
            self.db_manager.execute_update("""
                INSERT INTO wallet_transactions 
                (id, provider, type, amount, customer_name, reference, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (
                transaction_id,
                self.provider_input.currentData(),
                transaction_type,
                amount,
                self.customer_name_input.text(),
                self.reference_input.text(),
                self.notes_input.toPlainText()
            ))
            
            self.accept()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ المعاملة: {e}")