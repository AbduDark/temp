#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة الإعدادات - Settings Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QSpinBox, QDoubleSpinBox, QTextEdit, QFrame, 
                              QGroupBox, QMessageBox, QTabWidget, QCheckBox,
                              QFileDialog, QTableWidget, QTableWidgetItem,
                              QHeaderView, QAbstractItemView, QDialog,
                              QDialogButtonBox)
from PySide6.QtCore import Qt, Signal
from PySide6.QtGui import QFont, QColor
import logging

logger = logging.getLogger(__name__)


class UserManagementDialog(QDialog):
    """نافذة إدارة المستخدمين"""
    
    def __init__(self, parent=None, auth_service=None):
        super().__init__(parent)
        self.auth_service = auth_service
        self.setup_ui()
        self.load_users()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        self.setWindowTitle("إدارة المستخدمين")
        self.setModal(True)
        self.setFixedSize(700, 500)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        # شريط الأدوات
        toolbar = QFrame()
        toolbar_layout = QHBoxLayout(toolbar)
        
        add_user_btn = QPushButton("إضافة مستخدم")
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 8px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        add_user_btn.clicked.connect(self.add_user)
        toolbar_layout.addWidget(add_user_btn)
        
        toolbar_layout.addStretch()
        
        refresh_btn = QPushButton("تحديث")
        refresh_btn.clicked.connect(self.load_users)
        toolbar_layout.addWidget(refresh_btn)
        
        layout.addWidget(toolbar)
        
        # جدول المستخدمين
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(6)
        self.users_table.setHorizontalHeaderLabels([
            "اسم المستخدم", "الاسم الكامل", "الدور", "الحالة", "تاريخ الإنشاء", "العمليات"
        ])
        
        header = self.users_table.horizontalHeader()
        header.setStretchLastSection(True)
        header.setSectionResizeMode(1, QHeaderView.Stretch)
        
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QAbstractItemView.SelectRows)
        
        layout.addWidget(self.users_table)
        
        # زر الإغلاق
        close_btn = QPushButton("إغلاق")
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
    
    def load_users(self):
        """تحميل المستخدمين"""
        try:
            users = self.auth_service.get_all_users()
            self.users_table.setRowCount(len(users))
            
            for row, user in enumerate(users):
                # اسم المستخدم
                self.users_table.setItem(row, 0, QTableWidgetItem(user['username']))
                
                # الاسم الكامل
                self.users_table.setItem(row, 1, QTableWidgetItem(user['full_name']))
                
                # الدور
                role_names = {
                    'Admin': 'مدير',
                    'Cashier': 'كاشير',
                    'Technician': 'فني'
                }
                role_name = role_names.get(user['role'], user['role'])
                self.users_table.setItem(row, 2, QTableWidgetItem(role_name))
                
                # الحالة
                status = "نشط" if user['is_active'] else "معطل"
                status_item = QTableWidgetItem(status)
                if user['is_active']:
                    status_item.setBackground(QColor("#27ae60"))
                else:
                    status_item.setBackground(QColor("#e74c3c"))
                status_item.setForeground(QColor("white"))
                self.users_table.setItem(row, 3, status_item)
                
                # تاريخ الإنشاء
                date_str = user['created_at'][:10]
                self.users_table.setItem(row, 4, QTableWidgetItem(date_str))
                
                # العمليات
                operations_widget = self.create_user_operations(user)
                self.users_table.setCellWidget(row, 5, operations_widget)
                
        except Exception as e:
            logger.error(f"خطأ في تحميل المستخدمين: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل المستخدمين:\n{str(e)}")
    
    def create_user_operations(self, user):
        """إنشاء أزرار العمليات للمستخدم"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # زر التعديل
        edit_btn = QPushButton("تعديل")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_user(user))
        layout.addWidget(edit_btn)
        
        # زر التعطيل/التفعيل
        toggle_btn = QPushButton("تعطيل" if user['is_active'] else "تفعيل")
        color = "#e74c3c" if user['is_active'] else "#27ae60"
        toggle_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }}
        """)
        toggle_btn.clicked.connect(lambda: self.toggle_user(user))
        layout.addWidget(toggle_btn)
        
        return widget
    
    def add_user(self):
        """إضافة مستخدم جديد"""
        dialog = UserDialog(self)
        if dialog.exec() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            
            success = self.auth_service.create_user(
                user_data['username'],
                user_data['password'],
                user_data['full_name'],
                user_data['role']
            )
            
            if success:
                QMessageBox.information(self, "نجح", "تم إضافة المستخدم بنجاح")
                self.load_users()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في إضافة المستخدم")
    
    def edit_user(self, user):
        """تعديل المستخدم"""
        dialog = UserDialog(self, user)
        if dialog.exec() == QDialog.Accepted:
            user_data = dialog.get_user_data()
            
            success = self.auth_service.update_user(user['id'], **user_data)
            
            if success:
                QMessageBox.information(self, "نجح", "تم تحديث المستخدم بنجاح")
                self.load_users()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في تحديث المستخدم")
    
    def toggle_user(self, user):
        """تفعيل/تعطيل المستخدم"""
        action = "تعطيل" if user['is_active'] else "تفعيل"
        reply = QMessageBox.question(
            self, "تأكيد",
            f"هل أنت متأكد من {action} المستخدم {user['full_name']}؟"
        )
        
        if reply == QMessageBox.Yes:
            success = self.auth_service.update_user(
                user['id'], is_active=not user['is_active']
            )
            
            if success:
                QMessageBox.information(self, "نجح", f"تم {action} المستخدم بنجاح")
                self.load_users()
            else:
                QMessageBox.critical(self, "خطأ", f"فشل في {action} المستخدم")


class UserDialog(QDialog):
    """نافذة إضافة/تعديل المستخدم"""
    
    def __init__(self, parent=None, user=None):
        super().__init__(parent)
        self.user = user
        self.setup_ui()
        
        if user:
            self.load_user_data()
    
    def setup_ui(self):
        """إعداد واجهة النافذة"""
        title = "تعديل مستخدم" if self.user else "إضافة مستخدم جديد"
        self.setWindowTitle(title)
        self.setModal(True)
        self.setFixedSize(400, 300)
        self.setLayoutDirection(Qt.RightToLeft)
        
        layout = QVBoxLayout(self)
        
        form_layout = QGridLayout()
        
        # اسم المستخدم
        form_layout.addWidget(QLabel("اسم المستخدم:"), 0, 0)
        self.username_edit = QLineEdit()
        self.username_edit.setEnabled(not self.user)  # لا يمكن تعديله
        form_layout.addWidget(self.username_edit, 0, 1)
        
        # الاسم الكامل
        form_layout.addWidget(QLabel("الاسم الكامل:"), 1, 0)
        self.full_name_edit = QLineEdit()
        form_layout.addWidget(self.full_name_edit, 1, 1)
        
        # كلمة المرور
        form_layout.addWidget(QLabel("كلمة المرور:"), 2, 0)
        self.password_edit = QLineEdit()
        self.password_edit.setEchoMode(QLineEdit.Password)
        if self.user:
            self.password_edit.setPlaceholderText("اتركها فارغة للاحتفاظ بكلمة المرور الحالية")
        form_layout.addWidget(self.password_edit, 2, 1)
        
        # الدور
        form_layout.addWidget(QLabel("الدور:"), 3, 0)
        self.role_combo = QComboBox()
        self.role_combo.addItem("مدير", "Admin")
        self.role_combo.addItem("كاشير", "Cashier")
        self.role_combo.addItem("فني", "Technician")
        form_layout.addWidget(self.role_combo, 3, 1)
        
        layout.addLayout(form_layout)
        
        # أزرار العمل
        buttons = QDialogButtonBox(
            QDialogButtonBox.Save | QDialogButtonBox.Cancel
        )
        buttons.button(QDialogButtonBox.Save).setText("حفظ")
        buttons.button(QDialogButtonBox.Cancel).setText("إلغاء")
        buttons.accepted.connect(self.accept_data)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
    
    def load_user_data(self):
        """تحميل بيانات المستخدم للتعديل"""
        if not self.user:
            return
        
        self.username_edit.setText(self.user['username'])
        self.full_name_edit.setText(self.user['full_name'])
        
        # تحديد الدور
        role = self.user['role']
        for i in range(self.role_combo.count()):
            if self.role_combo.itemData(i) == role:
                self.role_combo.setCurrentIndex(i)
                break
    
    def accept_data(self):
        """التحقق من البيانات وقبولها"""
        username = self.username_edit.text().strip()
        full_name = self.full_name_edit.text().strip()
        password = self.password_edit.text()
        
        if not username:
            QMessageBox.warning(self, "تحذير", "يجب إدخال اسم المستخدم")
            return
        
        if not full_name:
            QMessageBox.warning(self, "تحذير", "يجب إدخال الاسم الكامل")
            return
        
        if not self.user and not password:
            QMessageBox.warning(self, "تحذير", "يجب إدخال كلمة المرور للمستخدم الجديد")
            return
        
        self.accept()
    
    def get_user_data(self):
        """الحصول على بيانات المستخدم"""
        data = {
            'username': self.username_edit.text().strip(),
            'full_name': self.full_name_edit.text().strip(),
            'role': self.role_combo.currentData()
        }
        
        # إضافة كلمة المرور إذا تم إدخالها
        password = self.password_edit.text()
        if password:
            data['password'] = password
        
        return data


class SettingsWindow(QWidget):
    """نافذة الإعدادات"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(10, 10, 10, 10)
        
        # عنوان القسم
        title_label = QLabel("الإعدادات")
        title_label.setFont(QFont("Arial", 20, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # التبويبات
        self.tab_widget = QTabWidget()
        
        # إعدادات المحل
        shop_tab = self.create_shop_settings_tab()
        self.tab_widget.addTab(shop_tab, "إعدادات المحل")
        
        # إعدادات النظام
        system_tab = self.create_system_settings_tab()
        self.tab_widget.addTab(system_tab, "إعدادات النظام")
        
        # إدارة المستخدمين (للمدير فقط)
        if self.main_window.current_user['role'] == 'Admin':
            users_tab = self.create_users_tab()
            self.tab_widget.addTab(users_tab, "إدارة المستخدمين")
        
        # النسخ الاحتياطي
        backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(backup_tab, "النسخ الاحتياطي")
        
        layout.addWidget(self.tab_widget)
        
        # أزرار الحفظ والإلغاء
        buttons_layout = QHBoxLayout()
        buttons_layout.addStretch()
        
        save_btn = QPushButton("حفظ الإعدادات")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #27ae60;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #229954;
            }
        """)
        save_btn.clicked.connect(self.save_settings)
        buttons_layout.addWidget(save_btn)
        
        cancel_btn = QPushButton("إلغاء")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #95a5a6;
                color: white;
                border: none;
                border-radius: 5px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7f8c8d;
            }
        """)
        cancel_btn.clicked.connect(self.cancel_changes)
        buttons_layout.addWidget(cancel_btn)
        
        layout.addLayout(buttons_layout)
    
    def create_shop_settings_tab(self):
        """إنشاء تبويب إعدادات المحل"""
        tab = QWidget()
        layout = QVBoxLayout(tab)
        
        # معلومات المحل
        shop_group = QGroupBox("معلومات المحل")
        shop_layout = QGridLayout(shop_group)
        
        shop_layout.addWidget(QLabel("اسم المحل:"), 0, 0)
        self.shop_name_edit = QLineEdit()
        shop_layout.addWidget(self.shop_name_edit, 0, 1)
        
        shop_layout.addWidget(QLabel("العنوان:"), 1, 0)
        self.shop_address_edit = QTextEdit()
        self.shop_address_edit.setMaximumHeight(80)
        shop_layout.addWidget(self.shop_address_edit, 1, 1)
        
        shop_layout.addWidget(QLabel("رقم الهاتف:"), 2, 0)
        self.shop_phone_edit = QLineEdit()
        shop_layout.addWidget(self.shop_phone_edit, 2, 1)
        
        shop_layout.addWidget(QLabel("البريد الإلكتروني:"), 3, 0)
        self.shop_email_edit = QLineEdit()
        shop_layout.addWidget(self.shop_email_edit, 3, 1)
        
        layout.addWidget(shop_group)
        
        # الإعدادات المالية
        financial_group = QGroupBox("الإعدادات المالية")
        financial_layout = QGridLayout(financial_group)
        
        financial_layout.addWidget(QLabel("العملة:"), 0, 0)
        self.currency_combo = QComboBox()
        self.currency_combo.addItem("الريال السعودي (SAR)", "SAR")
        self.currency_combo.addItem("الجنيه المصري (EGP)", "EGP")
        self.currency_combo.addItem("الدولار الأمريكي (USD)", "USD")
        financial_layout.addWidget(self.currency_combo, 0, 1)
        
        financial_layout.addWidget(QLabel("معدل الضريبة (%):"), 1, 0)
        self.tax_rate_spin = QDoubleSpinBox()
        self.tax_rate_spin.setMaximum(100.0)
        self.tax_rate_spin.setDecimals(2)
        self.tax_rate_spin.setSuffix("%")
        financial_layout.addWidget(self.tax_rate_spin, 1, 1)
        
        layout.addWidget(financial_group)
        
        # إعدادات الطباعة
        print_group = QGroupBox("إعدادات الطباعة")
        print_layout = QGridLayout(print_group)
        
        print_layout.addWidget(QLabel("نص أسفل الفاتورة:"), 0, 0)
        self.receipt_footer_edit = QLineEdit()
        print_layout.addWidget(self.receipt_footer_edit, 0, 1)
        
        print_layout.addWidget(QLabel("طباعة تلقائية:"), 1, 0)
        self.auto_print_checkbox = QCheckBox("تفعيل الطباعة# thoughts
المطلوب هو إكمال نظام إدارة محل الموبايلات المطور بـ Python و PySide6. لدي بالفعل الملفات الأساسية للنظام وأحتاج لإكمال الملفات الناقصة التي تشمل:

1. نوافذ المستخدم المتبقية (الصيانة، التقارير، الإعدادات، التقفيل اليومي)
2. مولد ملفات PDF للفواتير والتقارير
3. نظام التسجيل (Logger)
4. ملف الإعدادات
5. مساعدات عامة
6. اختبارات أساسية
7. دليل المستخدم وملفات البناء

سأقوم بتطوير كل ملف بشكل كامل ووظيفي مع التركيز على:
- واجهات مستخدم عربية بتخطيط من اليمين لليسار
- تكامل كامل مع الخدمات الموجودة
- معالجة الأخطاء المناسبة
- تصميم حديث ومتسق
- وظائف حقيقية وليس مجرد نماذج أولية

# useful_guidelines_from_blueprints


# directory_structure
```json
[
    {"path": "app/ui/repair_window.py", "status": "new"},
    {"path": "app/ui/reports_window.py", "status": "new"},
    {"path": "app/ui/settings_window.py", "status": "new"},
    {"path": "app/ui/daily_close_window.py", "status": "new"},
    {"path": "app/utils/__init__.py", "status": "new"},
    {"path": "app/utils/pdf_generator.py", "status": "new"},
    {"path": "app/utils/logger.py", "status": "new"},
    {"path": "app/utils/helpers.py", "status": "new"},
    {"path": "config/settings.py", "status": "new"},
    {"path": "assets/icons/.gitkeep", "status": "new"},
    {"path": "data/.gitkeep", "status": "new"},
    {"path": "reports/daily/.gitkeep", "status": "new"},
    {"path": "backup/.gitkeep", "status": "new"},
    {"path": "tests/__init__.py", "status": "new"},
    {"path": "tests/test_pos.py", "status": "new"},
    {"path": "tests/test_inventory.py", "status": "new"},
    {"path": "README.md", "status": "new"},
    {"path": "build_win.bat", "status": "new"}
]
