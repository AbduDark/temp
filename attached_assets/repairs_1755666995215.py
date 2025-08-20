
"""
Repairs Management Page for Mobile Shop Management System
"""

from PyQt6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                           QTableWidget, QTableWidgetItem, QPushButton, 
                           QLineEdit, QComboBox, QTextEdit, QFormLayout,
                           QDialog, QDialogButtonBox, QMessageBox, QDateEdit,
                           QGroupBox, QGridLayout, QSpinBox, QDoubleSpinBox)
from PyQt6.QtCore import Qt, QDate, pyqtSignal
from PyQt6.QtGui import QFont, QPixmap, QIcon
import sqlite3
from datetime import datetime

class AddRepairDialog(QDialog):
    def __init__(self, db_manager, parent=None):
        super().__init__(parent)
        self.db_manager = db_manager
        self.setWindowTitle("إضافة إصلاح جديد")
        self.setModal(True)
        self.resize(500, 600)
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        # Customer Information Group
        customer_group = QGroupBox("معلومات العميل")
        customer_layout = QFormLayout()

        self.customer_name = QLineEdit()
        self.customer_phone = QLineEdit()
        self.customer_email = QLineEdit()

        customer_layout.addRow("اسم العميل:", self.customer_name)
        customer_layout.addRow("رقم الهاتف:", self.customer_phone)
        customer_layout.addRow("البريد الإلكتروني:", self.customer_email)
        customer_group.setLayout(customer_layout)

        # Device Information Group
        device_group = QGroupBox("معلومات الجهاز")
        device_layout = QFormLayout()

        self.device_type = QComboBox()
        self.device_type.addItems(["iPhone", "Samsung", "Huawei", "Xiaomi", "Oppo", "Vivo", "أخرى"])
        
        self.device_model = QLineEdit()
        self.device_serial = QLineEdit()
        self.device_color = QLineEdit()

        device_layout.addRow("نوع الجهاز:", self.device_type)
        device_layout.addRow("موديل الجهاز:", self.device_model)
        device_layout.addRow("الرقم التسلسلي:", self.device_serial)
        device_layout.addRow("لون الجهاز:", self.device_color)
        device_group.setLayout(device_layout)

        # Repair Information Group
        repair_group = QGroupBox("معلومات الإصلاح")
        repair_layout = QFormLayout()

        self.problem_description = QTextEdit()
        self.problem_description.setMaximumHeight(100)
        
        self.repair_type = QComboBox()
        self.repair_type.addItems([
            "إصلاح شاشة", "تغيير بطارية", "إصلاح مكبر صوت", 
            "إصلاح مايكروفون", "إصلاح كاميرا", "إصلاح شحن",
            "تحديث سوفتوير", "فك تشفير", "أخرى"
        ])

        self.priority = QComboBox()
        self.priority.addItems(["عادي", "مستعجل", "طارئ"])

        self.estimated_cost = QDoubleSpinBox()
        self.estimated_cost.setRange(0, 99999)
        self.estimated_cost.setSuffix(" ريال")

        self.estimated_days = QSpinBox()
        self.estimated_days.setRange(1, 30)
        self.estimated_days.setSuffix(" يوم")

        self.receive_date = QDateEdit()
        self.receive_date.setDate(QDate.currentDate())
        self.receive_date.setCalendarPopup(True)

        repair_layout.addRow("وصف المشكلة:", self.problem_description)
        repair_layout.addRow("نوع الإصلاح:", self.repair_type)
        repair_layout.addRow("الأولوية:", self.priority)
        repair_layout.addRow("التكلفة المتوقعة:", self.estimated_cost)
        repair_layout.addRow("المدة المتوقعة:", self.estimated_days)
        repair_layout.addRow("تاريخ الاستلام:", self.receive_date)
        repair_group.setLayout(repair_layout)

        # Buttons
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(customer_group)
        layout.addWidget(device_group)
        layout.addWidget(repair_group)
        layout.addWidget(button_box)

    def get_repair_data(self):
        return {
            'customer_name': self.customer_name.text(),
            'customer_phone': self.customer_phone.text(),
            'customer_email': self.customer_email.text(),
            'device_type': self.device_type.currentText(),
            'device_model': self.device_model.text(),
            'device_serial': self.device_serial.text(),
            'device_color': self.device_color.text(),
            'problem_description': self.problem_description.toPlainText(),
            'repair_type': self.repair_type.currentText(),
            'priority': self.priority.currentText(),
            'estimated_cost': self.estimated_cost.value(),
            'estimated_days': self.estimated_days.value(),
            'receive_date': self.receive_date.date().toString("yyyy-MM-dd"),
            'status': 'في الانتظار'
        }

class UpdateStatusDialog(QDialog):
    def __init__(self, current_status, parent=None):
        super().__init__(parent)
        self.setWindowTitle("تحديث حالة الإصلاح")
        self.setModal(True)
        self.resize(300, 200)
        self.current_status = current_status
        self.setup_ui()

    def setup_ui(self):
        layout = QVBoxLayout(self)

        self.status_combo = QComboBox()
        self.status_combo.addItems([
            "في الانتظار", "قيد الإصلاح", "في انتظار قطع الغيار",
            "مكتمل", "مسلم للعميل", "ملغي"
        ])
        self.status_combo.setCurrentText(self.current_status)

        self.notes = QTextEdit()
        self.notes.setPlaceholderText("ملاحظات إضافية...")
        self.notes.setMaximumHeight(100)

        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(self.accept)
        button_box.rejected.connect(self.reject)

        layout.addWidget(QLabel("الحالة الجديدة:"))
        layout.addWidget(self.status_combo)
        layout.addWidget(QLabel("ملاحظات:"))
        layout.addWidget(self.notes)
        layout.addWidget(button_box)

    def get_update_data(self):
        return {
            'status': self.status_combo.currentText(),
            'notes': self.notes.toPlainText()
        }

class RepairsPage(QWidget):
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        self.setup_database()
        self.load_repairs()

    def setup_database(self):
        """Create repairs table if it doesn't exist"""
        try:
            cursor = self.db_manager.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS repairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT,
                    customer_email TEXT,
                    device_type TEXT NOT NULL,
                    device_model TEXT,
                    device_serial TEXT,
                    device_color TEXT,
                    problem_description TEXT,
                    repair_type TEXT,
                    priority TEXT DEFAULT 'عادي',
                    estimated_cost REAL DEFAULT 0,
                    actual_cost REAL DEFAULT 0,
                    estimated_days INTEGER DEFAULT 1,
                    receive_date TEXT,
                    delivery_date TEXT,
                    status TEXT DEFAULT 'في الانتظار',
                    notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            ''')
            self.db_manager.commit()
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في إنشاء جدول الإصلاحات: {str(e)}")

    def setup_ui(self):
        """Setup the repairs user interface"""
        layout = QVBoxLayout(self)

        # Header
        header = QLabel("🔧 إدارة الإصلاحات")
        header.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
        header.setAlignment(Qt.AlignmentFlag.AlignCenter)
        header.setStyleSheet("color: #1f2937; margin: 20px;")
        layout.addWidget(header)

        # Search and Filter Section
        search_layout = QHBoxLayout()
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث برقم الإصلاح، اسم العميل، أو رقم الهاتف...")
        self.search_input.textChanged.connect(self.filter_repairs)
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "جميع الحالات", "في الانتظار", "قيد الإصلاح", 
            "في انتظار قطع الغيار", "مكتمل", "مسلم للعميل", "ملغي"
        ])
        self.status_filter.currentTextChanged.connect(self.filter_repairs)

        search_layout.addWidget(QLabel("البحث:"))
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(QLabel("تصفية الحالة:"))
        search_layout.addWidget(self.status_filter)
        layout.addLayout(search_layout)

        # Buttons Section
        buttons_layout = QHBoxLayout()
        
        self.add_repair_btn = QPushButton("➕ إضافة إصلاح جديد")
        self.add_repair_btn.clicked.connect(self.add_repair)
        self.add_repair_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)

        self.update_status_btn = QPushButton("🔄 تحديث الحالة")
        self.update_status_btn.clicked.connect(self.update_repair_status)
        self.update_status_btn.setEnabled(False)

        self.complete_repair_btn = QPushButton("✅ إكمال الإصلاح")
        self.complete_repair_btn.clicked.connect(self.complete_repair)
        self.complete_repair_btn.setEnabled(False)

        self.delete_repair_btn = QPushButton("🗑️ حذف")
        self.delete_repair_btn.clicked.connect(self.delete_repair)
        self.delete_repair_btn.setEnabled(False)
        self.delete_repair_btn.setStyleSheet("""
            QPushButton {
                background-color: #ef4444;
                color: white;
                border: none;
                padding: 10px 20px;
                border-radius: 5px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #dc2626;
            }
        """)

        self.refresh_btn = QPushButton("🔄 تحديث")
        self.refresh_btn.clicked.connect(self.load_repairs)

        buttons_layout.addWidget(self.add_repair_btn)
        buttons_layout.addWidget(self.update_status_btn)
        buttons_layout.addWidget(self.complete_repair_btn)
        buttons_layout.addWidget(self.delete_repair_btn)
        buttons_layout.addStretch()
        buttons_layout.addWidget(self.refresh_btn)
        layout.addLayout(buttons_layout)

        # Repairs Table
        self.repairs_table = QTableWidget()
        self.repairs_table.setColumnCount(12)
        self.repairs_table.setHorizontalHeaderLabels([
            "رقم الإصلاح", "اسم العميل", "رقم الهاتف", "نوع الجهاز",
            "موديل الجهاز", "نوع الإصلاح", "الأولوية", "التكلفة المتوقعة",
            "تاريخ الاستلام", "المدة المتوقعة", "الحالة", "ملاحظات"
        ])
        self.repairs_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.repairs_table.setAlternatingRowColors(True)
        self.repairs_table.itemSelectionChanged.connect(self.on_selection_changed)
        
        # Set column widths
        header = self.repairs_table.horizontalHeader()
        header.setStretchLastSection(True)
        for i in range(self.repairs_table.columnCount()):
            header.resizeSection(i, 120)

        layout.addWidget(self.repairs_table)

        # Statistics Section
        stats_layout = QHBoxLayout()
        
        self.stats_pending = QLabel("في الانتظار: 0")
        self.stats_in_progress = QLabel("قيد الإصلاح: 0")
        self.stats_completed = QLabel("مكتمل: 0")
        self.stats_delivered = QLabel("مسلم: 0")

        for label in [self.stats_pending, self.stats_in_progress, self.stats_completed, self.stats_delivered]:
            label.setStyleSheet("""
                QLabel {
                    background-color: #f3f4f6;
                    padding: 10px;
                    border-radius: 5px;
                    font-weight: bold;
                }
            """)

        stats_layout.addWidget(self.stats_pending)
        stats_layout.addWidget(self.stats_in_progress)
        stats_layout.addWidget(self.stats_completed)
        stats_layout.addWidget(self.stats_delivered)
        stats_layout.addStretch()

        layout.addLayout(stats_layout)

    def load_repairs(self):
        """Load repairs data from database"""
        try:
            cursor = self.db_manager.cursor()
            cursor.execute('''
                SELECT id, customer_name, customer_phone, device_type, device_model,
                       repair_type, priority, estimated_cost, receive_date,
                       estimated_days, status, notes
                FROM repairs 
                ORDER BY id DESC
            ''')
            
            repairs = cursor.fetchall()
            self.repairs_table.setRowCount(len(repairs))
            
            for row, repair in enumerate(repairs):
                for col, value in enumerate(repair):
                    item = QTableWidgetItem(str(value) if value else "")
                    
                    # Color code based on status
                    if col == 10:  # Status column
                        if value == "في الانتظار":
                            item.setBackground(Qt.GlobalColor.yellow)
                        elif value == "قيد الإصلاح":
                            item.setBackground(Qt.GlobalColor.cyan)
                        elif value == "مكتمل":
                            item.setBackground(Qt.GlobalColor.green)
                        elif value == "مسلم للعميل":
                            item.setBackground(Qt.GlobalColor.lightGray)
                        elif value == "ملغي":
                            item.setBackground(Qt.GlobalColor.red)
                    
                    # Color code based on priority
                    if col == 6:  # Priority column
                        if value == "طارئ":
                            item.setBackground(Qt.GlobalColor.red)
                        elif value == "مستعجل":
                            item.setBackground(Qt.GlobalColor.yellow)
                    
                    self.repairs_table.setItem(row, col, item)
            
            self.update_statistics()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل بيانات الإصلاحات: {str(e)}")

    def update_statistics(self):
        """Update repair statistics"""
        try:
            cursor = self.db_manager.cursor()
            
            # Count by status
            cursor.execute("SELECT status, COUNT(*) FROM repairs GROUP BY status")
            stats = dict(cursor.fetchall())
            
            self.stats_pending.setText(f"في الانتظار: {stats.get('في الانتظار', 0)}")
            self.stats_in_progress.setText(f"قيد الإصلاح: {stats.get('قيد الإصلاح', 0)}")
            self.stats_completed.setText(f"مكتمل: {stats.get('مكتمل', 0)}")
            self.stats_delivered.setText(f"مسلم: {stats.get('مسلم للعميل', 0)}")
            
        except Exception as e:
            print(f"Error updating statistics: {e}")

    def filter_repairs(self):
        """Filter repairs based on search and status"""
        search_text = self.search_input.text().lower()
        status_filter = self.status_filter.currentText()
        
        for row in range(self.repairs_table.rowCount()):
            show_row = True
            
            # Search filter
            if search_text:
                found = False
                for col in range(self.repairs_table.columnCount()):
                    item = self.repairs_table.item(row, col)
                    if item and search_text in item.text().lower():
                        found = True
                        break
                if not found:
                    show_row = False
            
            # Status filter
            if status_filter != "جميع الحالات":
                status_item = self.repairs_table.item(row, 10)  # Status column
                if not status_item or status_item.text() != status_filter:
                    show_row = False
            
            self.repairs_table.setRowHidden(row, not show_row)

    def on_selection_changed(self):
        """Handle table selection changes"""
        selected = len(self.repairs_table.selectedItems()) > 0
        self.update_status_btn.setEnabled(selected)
        self.complete_repair_btn.setEnabled(selected)
        self.delete_repair_btn.setEnabled(selected)

    def add_repair(self):
        """Add new repair"""
        dialog = AddRepairDialog(self.db_manager, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            repair_data = dialog.get_repair_data()
            
            try:
                cursor = self.db_manager.cursor()
                cursor.execute('''
                    INSERT INTO repairs (
                        customer_name, customer_phone, customer_email,
                        device_type, device_model, device_serial, device_color,
                        problem_description, repair_type, priority,
                        estimated_cost, estimated_days, receive_date, status
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                ''', (
                    repair_data['customer_name'], repair_data['customer_phone'],
                    repair_data['customer_email'], repair_data['device_type'],
                    repair_data['device_model'], repair_data['device_serial'],
                    repair_data['device_color'], repair_data['problem_description'],
                    repair_data['repair_type'], repair_data['priority'],
                    repair_data['estimated_cost'], repair_data['estimated_days'],
                    repair_data['receive_date'], repair_data['status']
                ))
                
                self.db_manager.commit()
                self.load_repairs()
                QMessageBox.information(self, "نجح", "تم إضافة الإصلاح بنجاح!")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في إضافة الإصلاح: {str(e)}")

    def update_repair_status(self):
        """Update repair status"""
        current_row = self.repairs_table.currentRow()
        if current_row < 0:
            return
        
        repair_id = self.repairs_table.item(current_row, 0).text()
        current_status = self.repairs_table.item(current_row, 10).text()
        
        dialog = UpdateStatusDialog(current_status, self)
        if dialog.exec() == QDialog.DialogCode.Accepted:
            update_data = dialog.get_update_data()
            
            try:
                cursor = self.db_manager.cursor()
                cursor.execute('''
                    UPDATE repairs 
                    SET status = ?, notes = ?
                    WHERE id = ?
                ''', (update_data['status'], update_data['notes'], repair_id))
                
                self.db_manager.commit()
                self.load_repairs()
                QMessageBox.information(self, "نجح", "تم تحديث حالة الإصلاح بنجاح!")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في تحديث الحالة: {str(e)}")

    def complete_repair(self):
        """Mark repair as completed"""
        current_row = self.repairs_table.currentRow()
        if current_row < 0:
            return
        
        repair_id = self.repairs_table.item(current_row, 0).text()
        
        reply = QMessageBox.question(
            self, "تأكيد", 
            "هل أنت متأكد من أن الإصلاح مكتمل؟",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_manager.cursor()
                cursor.execute('''
                    UPDATE repairs 
                    SET status = 'مكتمل', delivery_date = ?
                    WHERE id = ?
                ''', (datetime.now().strftime("%Y-%m-%d"), repair_id))
                
                self.db_manager.commit()
                self.load_repairs()
                QMessageBox.information(self, "نجح", "تم إكمال الإصلاح بنجاح!")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في إكمال الإصلاح: {str(e)}")

    def delete_repair(self):
        """Delete selected repair"""
        current_row = self.repairs_table.currentRow()
        if current_row < 0:
            return
        
        repair_id = self.repairs_table.item(current_row, 0).text()
        customer_name = self.repairs_table.item(current_row, 1).text()
        
        reply = QMessageBox.question(
            self, "تأكيد الحذف", 
            f"هل أنت متأكد من حذف إصلاح العميل: {customer_name}؟\nهذا الإجراء لا يمكن التراجع عنه.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            try:
                cursor = self.db_manager.cursor()
                cursor.execute("DELETE FROM repairs WHERE id = ?", (repair_id,))
                self.db_manager.commit()
                self.load_repairs()
                QMessageBox.information(self, "نجح", "تم حذف الإصلاح بنجاح!")
                
            except Exception as e:
                QMessageBox.critical(self, "خطأ", f"فشل في حذف الإصلاح: {str(e)}")

    def refresh_data(self):
        """Refresh repairs data"""
        self.load_repairs()
