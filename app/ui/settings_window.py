import sys
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QLabel, QPushButton, 
    QTabWidget, QTableWidget, QTableWidgetItem, QLineEdit, QFormLayout, 
    QMessageBox, QFileDialog, QHBoxLayout, QCheckBox, QDateEdit, QSpinBox, QComboBox, QScrollArea
)
from PySide6.QtGui import QFont, QIcon, QColor, QPixmap
from PySide6.QtCore import Qt, QDateTime, QDate, QTime, Slot, QSize, QDir, QFileInfo
from app.utils.logger import get_logger

logger = get_logger('settings')
from app.services.auth_service import AuthService
from app.services.inventory_service import InventoryService
from app.ui.inventory_window import InventoryWindow
from app.ui.repair_window import RepairWindow
from app.utils.pdf_generator import PDFGenerator
from app.utils.helpers import get_resource_path
from config.settings import Settings
import os

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("نظام إدارة محل الموبايلات")
        self.setWindowIcon(QIcon(get_resource_path("icons/main_icon.png")))
        self.setGeometry(100, 100, 1280, 720)
        self.setStyleSheet("background-color: #f8f9fa;")

        self.settings = Settings()
        self.auth_service = AuthService()
        self.inventory_service = InventoryService()
        
        self.pdf_generator = PDFGenerator()

        # تحميل معلومات المستخدم الحالي (يفترض أن يتم تحميلها بعد تسجيل الدخول)
        # self.current_user = {'username': 'Admin', 'role': 'Admin'} 
        self.current_user = None # سيتم تعيينها بعد تسجيل الدخول

        self.central_widget = QWidget()
        self.setCentralWidget(self.central_widget)
        self.main_layout = QHBoxLayout(self.central_widget)

        self.setup_left_menu()
        self.setup_main_content()

        self.show_login_window()

    def setup_left_menu(self):
        """إعداد القائمة اليسرى"""
        self.menu_widget = QWidget()
        self.menu_layout = QVBoxLayout(self.menu_widget)
        self.menu_layout.setContentsMargins(0, 0, 0, 0)
        self.menu_layout.setSpacing(0)
        self.menu_widget.setFixedWidth(220)
        self.menu_widget.setStyleSheet("""
            QWidget { background-color: #34495e; color: white; font-size: 14px; }
            QPushButton { 
                padding: 15px 20px; 
                text-align: right; 
                border: none; 
                font-weight: bold;
                background-color: #34495e;
            }
            QPushButton:hover { background-color: #4a637d; }
            QPushButton:pressed { background-color: #2c3e50; }
            .menu-icon { width: 24px; height: 24px; margin-left: 15px; margin-right: 10px;}
        """)

        # شعار التطبيق
        logo_label = QLabel()
        logo_pixmap = QPixmap(get_resource_path("icons/logo.png")).scaled(80, 80, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        logo_label.setPixmap(logo_pixmap)
        logo_label.setAlignment(Qt.AlignCenter)
        logo_label.setContentsMargins(0, 20, 0, 30)
        self.menu_layout.addWidget(logo_label)

        # أزرار القائمة
        self.btn_dashboard = QPushButton("لوحة التحكم")
        self.btn_dashboard.setIcon(QIcon(get_resource_path("icons/dashboard_icon.png")))
        self.btn_dashboard.setIconSize(QSize(24, 24))
        self.btn_dashboard.clicked.connect(lambda: self.show_content(self.dashboard_widget))

        self.btn_inventory = QPushButton("المخزون")
        self.btn_inventory.setIcon(QIcon(get_resource_path("icons/inventory_icon.png")))
        self.btn_inventory.setIconSize(QSize(24, 24))
        self.btn_inventory.clicked.connect(self.show_inventory_window)

        self.btn_sales = QPushButton("المبيعات")
        self.btn_sales.setIcon(QIcon(get_resource_path("icons/sales_icon.png")))
        self.btn_sales.setIconSize(QSize(24, 24))
        self.btn_sales.clicked.connect(self.show_sales_window)
        
        self.btn_maintenance = QPushButton("الصيانة")
        self.btn_maintenance.setIcon(QIcon(get_resource_path("icons/maintenance_icon.png")))
        self.btn_maintenance.setIconSize(QSize(24, 24))
        self.btn_maintenance.clicked.connect(self.show_maintenance_window)

        self.btn_reports = QPushButton("التقارير")
        self.btn_reports.setIcon(QIcon(get_resource_path("icons/reports_icon.png")))
        self.btn_reports.setIconSize(QSize(24, 24))
        self.btn_reports.clicked.connect(lambda: self.show_content(self.reports_widget))

        self.btn_settings = QPushButton("الإعدادات")
        self.btn_settings.setIcon(QIcon(get_resource_path("icons/settings_icon.png")))
        self.btn_settings.setIconSize(QSize(24, 24))
        self.btn_settings.clicked.connect(lambda: self.show_content(self.settings_widget))

        self.btn_users = QPushButton("إدارة المستخدمين")
        self.btn_users.setIcon(QIcon(get_resource_path("icons/users_icon.png")))
        self.btn_users.setIconSize(QSize(24, 24))
        self.btn_users.clicked.connect(self.open_user_management)

        self.btn_logout = QPushButton("تسجيل الخروج")
        self.btn_logout.setIcon(QIcon(get_resource_path("icons/logout_icon.png")))
        self.btn_logout.setIconSize(QSize(24, 24))
        self.btn_logout.clicked.connect(self.logout)

        self.menu_layout.addWidget(self.btn_dashboard)
        self.menu_layout.addWidget(self.btn_inventory)
        self.menu_layout.addWidget(self.btn_sales)
        self.menu_layout.addWidget(self.btn_maintenance)
        self.menu_layout.addWidget(self.btn_reports)
        self.menu_layout.addWidget(self.btn_settings)
        self.menu_layout.addWidget(self.btn_users)
        self.menu_layout.addStretch(1)
        self.menu_layout.addWidget(self.btn_logout)
        
        self.menu_layout.setAlignment(Qt.AlignTop)


        self.main_layout.addWidget(self.menu_widget)

    def setup_main_content(self):
        """إعداد المحتوى الرئيسي"""
        self.content_stack = QWidget()
        self.content_layout = QVBoxLayout(self.content_stack)
        self.content_layout.setContentsMargins(0, 0, 0, 0)
        self.content_layout.setSpacing(0)
        
        # محتوى لوحة التحكم
        self.dashboard_widget = QWidget()
        dashboard_layout = QVBoxLayout(self.dashboard_widget)
        dashboard_layout.setAlignment(Qt.AlignCenter)
        dashboard_layout.setContentsMargins(50, 50, 50, 50)
        dashboard_layout.setSpacing(30)

        welcome_label = QLabel("مرحباً بك في نظام إدارة محل الموبايلات")
        welcome_label.setFont(QFont("Segoe UI", 32, QFont.Bold))
        welcome_label.setAlignment(Qt.AlignCenter)
        welcome_label.setStyleSheet("color: #2c3e50;")
        dashboard_layout.addWidget(welcome_label)

        status_label = QLabel("تصفح الأقسام من القائمة اليسرى لإدارة أعمالك")
        status_label.setFont(QFont("Segoe UI", 16))
        status_label.setAlignment(Qt.AlignCenter)
        status_label.setStyleSheet("color: #555;")
        dashboard_layout.addWidget(status_label)
        
        # إضافة عناصر واجهة المستخدم للتقارير والإعدادات
        self.reports_widget = self.create_reports_window()
        self.settings_widget = self.create_settings_window()
        self.repair_window_instance = None # سنقوم بإنشاء مثيل عند الحاجة
        self.inventory_window_instance = None
        self.sales_window_instance = None

        self.main_layout.addWidget(self.content_stack)

    def create_reports_window(self):
        """إنشاء نافذة التقارير"""
        reports_window = QWidget()
        layout = QVBoxLayout(reports_window)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(20)

        # عنوان النافذة
        title_label = QLabel("التقارير")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 30px; 
            padding: 20px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #f1c40f, stop: 1 #f39c12);
            border-radius: 15px;
            border: 2px solid #e67e22;
        """)
        layout.addWidget(title_label)

        # خيارات التقرير
        report_options_layout = QFormLayout()
        report_options_layout.setContentsMargins(0, 0, 0, 20)
        report_options_layout.setSpacing(15)
        report_options_layout.addRow(QLabel("نوع التقرير:"))
        self.report_type_combo = QComboBox()
        self.report_type_combo.addItems(["تقرير المبيعات", "تقرير المخزون", "تقرير الصيانة", "تقرير الأرباح"])
        self.report_type_combo.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        report_options_layout.addRow(self.report_type_combo)

        report_options_layout.addRow(QLabel("من تاريخ:"))
        self.start_date_edit = QDateEdit()
        self.start_date_edit.setDate(QDate.currentDate().addMonths(-1))
        self.start_date_edit.setCalendarPopup(True)
        self.start_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.start_date_edit.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        report_options_layout.addRow(self.start_date_edit)

        report_options_layout.addRow(QLabel("إلى تاريخ:"))
        self.end_date_edit = QDateEdit()
        self.end_date_edit.setDate(QDate.currentDate())
        self.end_date_edit.setCalendarPopup(True)
        self.end_date_edit.setDisplayFormat("yyyy-MM-dd")
        self.end_date_edit.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        report_options_layout.addRow(self.end_date_edit)

        layout.addLayout(report_options_layout)

        # زر توليد التقرير
        generate_report_btn = QPushButton("توليد التقرير")
        generate_report_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
        generate_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; padding: 12px 25px; border-radius: 8px; border: none;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        generate_report_btn.clicked.connect(self.generate_report)
        layout.addWidget(generate_report_btn)

        # منطقة قابلة للتمرير لعرض تفاصيل التقرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("border: none;") # إزالة الحدود الافتراضية لمساحة التمرير

        self.report_content_widget = QWidget()
        self.report_content_layout = QVBoxLayout(self.report_content_widget)
        self.report_content_layout.setContentsMargins(0, 0, 0, 0)
        self.report_content_layout.setSpacing(15)
        self.report_content_layout.setAlignment(Qt.AlignTop) # محاذاة المحتوى للأعلى
        
        # رسالة أولية
        initial_message = QLabel("اختر نوع التقرير وحدد التواريخ ثم اضغط توليد.")
        initial_message.setFont(QFont("Segoe UI", 14))
        initial_message.setAlignment(Qt.AlignCenter)
        initial_message.setStyleSheet("color: #7f8c8d;")
        self.report_content_layout.addWidget(initial_message)
        
        scroll_area.setWidget(self.report_content_widget)
        layout.addWidget(scroll_area)

        return reports_window

    def create_settings_window(self):
        """إنشاء نافذة الإعدادات"""
        settings_window = QWidget()
        layout = QVBoxLayout(settings_window)
        layout.setContentsMargins(30, 30, 30, 30)
        layout.setSpacing(25)

        # عنوان الصفحة
        title_label = QLabel("إعدادات النظام")
        title_label.setFont(QFont("Segoe UI", 28, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            color: #2c3e50; 
            margin-bottom: 30px; 
            padding: 20px;
            background: qlineargradient(x1: 0, y1: 0, x2: 1, y2: 0,
                stop: 0 #ecf0f1, stop: 1 #bdc3c7);
            border-radius: 15px;
            border: 2px solid #bdc3c7;
        """)
        layout.addWidget(title_label)

        # التبويبات
        self.tab_widget = QTabWidget()
        self.tab_widget.setStyleSheet("""
            QTabWidget::pane {
                border: 2px solid #e9ecef;
                border-radius: 15px;
                background-color: white;
                padding: 25px;
            }
            QTabBar::tab {
                background-color: #ecf0f1;
                padding: 15px 25px;
                margin: 3px;
                border-radius: 10px;
                font-size: 14px;
                font-weight: bold;
                color: #2c3e50;
                min-width: 150px;
            }
            QTabBar::tab:selected {
                background-color: #3498db;
                color: white;
            }
            QTabBar::tab:hover {
                background-color: #bdc3c7;
            }
        """)

        # تبويب الإعدادات العامة
        general_tab = self.create_general_tab()
        self.tab_widget.addTab(general_tab, "الإعدادات العامة")

        # تبويب النسخ الاحتياطية
        backup_tab = self.create_backup_tab()
        self.tab_widget.addTab(backup_tab, "النسخ الاحتياطية")

        # تبويب إدارة المستخدمين (للمدير فقط)
        if hasattr(self.current_user, 'get') and self.current_user.get('role') == 'Admin':
            users_tab = self.create_users_tab()
            self.tab_widget.addTab(users_tab, "إدارة المستخدمين")

        layout.addWidget(self.tab_widget)

        return settings_window

    def create_general_tab(self):
        """إنشاء تبويب الإعدادات العامة"""
        general_tab = QWidget()
        layout = QFormLayout(general_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # اسم المحل
        self.store_name_input = QLineEdit()
        self.store_name_input.setPlaceholderText("أدخل اسم المحل")
        self.store_name_input.setText(self.settings.get_setting("store_name", ""))
        self.store_name_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("اسم المحل:", self.store_name_input)

        # عنوان المحل
        self.store_address_input = QLineEdit()
        self.store_address_input.setPlaceholderText("أدخل عنوان المحل")
        self.store_address_input.setText(self.settings.get_setting("store_address", ""))
        self.store_address_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("عنوان المحل:", self.store_address_input)

        # رقم الهاتف
        self.store_phone_input = QLineEdit()
        self.store_phone_input.setPlaceholderText("أدخل رقم هاتف المحل")
        self.store_phone_input.setText(self.settings.get_setting("store_phone", ""))
        self.store_phone_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("رقم الهاتف:", self.store_phone_input)

        # البريد الإلكتروني
        self.store_email_input = QLineEdit()
        self.store_email_input.setPlaceholderText("أدخل البريد الإلكتروني للمحل")
        self.store_email_input.setText(self.settings.get_setting("store_email", ""))
        self.store_email_input.setStyleSheet("padding: 10px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("البريد الإلكتروني:", self.store_email_input)

        # شعار المحل
        self.store_logo_path_label = QLabel("لم يتم اختيار شعار")
        self.store_logo_path_label.setToolTip("مسار الشعار الحالي")
        current_logo = self.settings.get_setting("store_logo", "")
        if current_logo:
            self.store_logo_path_label.setText(os.path.basename(current_logo))
        
        logo_select_btn = QPushButton("اختيار شعار")
        logo_select_btn.setStyleSheet("background-color: #3498db; color: white; padding: 8px 15px; border-radius: 5px; border: none;")
        logo_select_btn.clicked.connect(self.select_store_logo)
        
        logo_layout = QHBoxLayout()
        logo_layout.addWidget(self.store_logo_path_label)
        logo_layout.addWidget(logo_select_btn)
        layout.addRow("شعار المحل:", logo_layout.itemAt(0).widget()) # Add the label to the form layout

        # العملة
        self.currency_combo = QComboBox()
        self.currency_combo.addItems(["ريال سعودي (SAR)", "جنيه مصري (EGP)", "دولار أمريكي (USD)", "درهم إماراتي (AED)"])
        self.currency_combo.setCurrentText(self.settings.get_setting("currency", "ريال سعودي (SAR)"))
        self.currency_combo.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("العملة:", self.currency_combo)

        # لغة الواجهة
        self.language_combo = QComboBox()
        self.language_combo.addItems(["العربية", "English"])
        self.language_combo.setCurrentText(self.settings.get_setting("language", "العربية"))
        self.language_combo.setStyleSheet("padding: 8px; border-radius: 5px; border: 1px solid #ccc;")
        layout.addRow("لغة الواجهة:", self.language_combo)
        
        # خيارات الفوترة
        layout.addRow(QLabel("<b>خيارات الفوترة</b>"))
        
        self.show_store_info_on_invoice_check = QCheckBox()
        self.show_store_info_on_invoice_check.setChecked(self.settings.get_setting("show_store_info_on_invoice", True))
        layout.addRow("عرض معلومات المحل على الفاتورة:", self.show_store_info_on_invoice_check)

        self.show_store_logo_on_invoice_check = QCheckBox()
        self.show_store_logo_on_invoice_check.setChecked(self.settings.get_setting("show_store_logo_on_invoice", True))
        layout.addRow("عرض شعار المحل على الفاتورة:", self.show_store_logo_on_invoice_check)

        # زر حفظ الإعدادات
        save_button = QPushButton("حفظ الإعدادات")
        save_button.setFont(QFont("Segoe UI", 12, QFont.Bold))
        save_button.setStyleSheet("""
            QPushButton {
                background-color: #27ae60; color: white; padding: 12px 25px; border-radius: 8px; border: none;
            }
            QPushButton:hover { background-color: #229954; }
        """)
        save_button.clicked.connect(self.save_settings)
        layout.addRow("", save_button) # Add button to the last row

        return general_tab

    def create_backup_tab(self):
        """إنشاء تبويب النسخ الاحتياطية"""
        backup_tab = QWidget()
        layout = QVBoxLayout(backup_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # عنوان التبويب
        title_label = QLabel("إدارة النسخ الاحتياطية")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # أزرار العمليات
        operations_layout = QHBoxLayout()
        operations_layout.setSpacing(10)

        create_backup_btn = QPushButton("إنشاء نسخة احتياطية جديدة")
        create_backup_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        create_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #f39c12; color: white; padding: 10px 20px; border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #e67e22; }
        """)
        create_backup_btn.clicked.connect(self.create_backup)
        operations_layout.addWidget(create_backup_btn)

        restore_backup_btn = QPushButton("استعادة من ملف")
        restore_backup_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        restore_backup_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; color: white; padding: 10px 20px; border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #2980b9; }
        """)
        restore_backup_btn.clicked.connect(self.restore_backup)
        operations_layout.addWidget(restore_backup_btn)
        
        operations_layout.addStretch(1)
        layout.addLayout(operations_layout)

        # جدول النسخ الاحتياطية
        self.backups_table = QTableWidget()
        self.backups_table.setColumnCount(4)
        self.backups_table.setHorizontalHeaderLabels(["اسم النسخة", "التاريخ", "الحجم", "العمليات"])
        self.backups_table.setAlternatingRowColors(True)
        self.backups_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.backups_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.backups_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.backups_table.setFont(QFont("Segoe UI", 10))
        self.backups_table.horizontalHeader().setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.backups_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.backups_table.horizontalHeader().setStretchLastSection(True)
        self.backups_table.verticalHeader().setVisible(False)
        
        # تحديد عرض الأعمدة
        self.backups_table.setColumnWidth(0, 200) # اسم النسخة
        self.backups_table.setColumnWidth(1, 150) # التاريخ
        self.backups_table.setColumnWidth(2, 100) # الحجم
        self.backups_table.setColumnWidth(3, 150) # العمليات

        # إضافة مساحة قابلة للتمرير للجدول
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.backups_table)
        scroll_area.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        
        layout.addWidget(scroll_area)
        
        self.refresh_backups_list() # تحميل القائمة عند فتح التبويب

        return backup_tab

    def create_users_tab(self):
        """إنشاء تبويب إدارة المستخدمين"""
        users_tab = QWidget()
        layout = QVBoxLayout(users_tab)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # عنوان التبويب
        title_label = QLabel("إدارة المستخدمين")
        title_label.setFont(QFont("Segoe UI", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title_label)

        # زر إضافة مستخدم جديد
        add_user_btn = QPushButton("إضافة مستخدم جديد")
        add_user_btn.setFont(QFont("Segoe UI", 10, QFont.Bold))
        add_user_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; color: white; padding: 10px 20px; border-radius: 5px; border: none;
            }
            QPushButton:hover { background-color: #27ae60; }
        """)
        add_user_btn.clicked.connect(self.open_user_management)
        layout.addWidget(add_user_btn)

        # جدول المستخدمين
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(4)
        self.users_table.setHorizontalHeaderLabels(["اسم المستخدم", "البريد الإلكتروني", "الدور", "العمليات"])
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self.users_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.users_table.setFont(QFont("Segoe UI", 10))
        self.users_table.horizontalHeader().setFont(QFont("Segoe UI", 11, QFont.Bold))
        self.users_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
        self.users_table.horizontalHeader().setStretchLastSection(True)
        self.users_table.verticalHeader().setVisible(False)
        
        # تحديد عرض الأعمدة
        self.users_table.setColumnWidth(0, 150) # اسم المستخدم
        self.users_table.setColumnWidth(1, 200) # البريد الإلكتروني
        self.users_table.setColumnWidth(2, 120) # الدور
        self.users_table.setColumnWidth(3, 150) # العمليات

        # إضافة مساحة قابلة للتمرير للجدول
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self.users_table)
        scroll_area.setStyleSheet("border: 1px solid #ddd; border-radius: 5px;")
        
        layout.addWidget(scroll_area)

        # تحميل قائمة المستخدمين
        self.refresh_users_list()

        return users_tab

    def refresh_users_list(self):
        """تحديث قائمة المستخدمين"""
        try:
            users = self.auth_service.get_all_users()
            self.users_table.setRowCount(len(users))

            for row, user in enumerate(users):
                self.users_table.setItem(row, 0, QTableWidgetItem(user.get('username', '')))
                self.users_table.setItem(row, 1, QTableWidgetItem(user.get('email', '')))
                self.users_table.setItem(row, 2, QTableWidgetItem(user.get('role', '')))

                # أزرار العمليات
                operations_widget = self.create_user_operations(user)
                self.users_table.setCellWidget(row, 3, operations_widget)

        except Exception as e:
            logger.error(f"خطأ في تحميل قائمة المستخدمين: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل قائمة المستخدمين:\n{str(e)}")

    def create_user_operations(self, user):
        """إنشاء أزرار العمليات للمستخدم"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setSpacing(5)

        # زر تعديل
        edit_btn = QPushButton("تعديل")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f1c40f; color: white; border: none; border-radius: 3px; padding: 5px 10px; font-size: 10px;
            }
            QPushButton:hover { background-color: #f39c12; }
        """)
        edit_btn.clicked.connect(lambda: self.edit_user(user['id']))
        layout.addWidget(edit_btn)

        # زر حذف
        delete_btn = QPushButton("حذف")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c; color: white; border: none; border-radius: 3px; padding: 5px 10px; font-size: 10px;
            }
            QPushButton:hover { background-color: #c0392b; }
        """)
        delete_btn.clicked.connect(lambda: self.delete_user(user['id']))
        layout.addWidget(delete_btn)

        return widget

    def edit_user(self, user_id):
        """فتح نافذة تعديل المستخدم"""
        try:
            user_data = self.auth_service.get_user_by_id(user_id)
            if not user_data:
                QMessageBox.critical(self, "خطأ", "لم يتم العثور على بيانات المستخدم.")
                return

            # TODO: Implement user edit dialog
            QMessageBox.information(self, "قريباً", "ميزة تعديل المستخدم ستكون متاحة قريباً")
        except Exception as e:
            logger.error(f"خطأ في تعديل المستخدم (ID: {user_id}): {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في تعديل المستخدم:\n{str(e)}")

    def delete_user(self, user_id):
        """حذف مستخدم"""
        user_info = self.auth_service.get_user_by_id(user_id)
        username = user_info.get('username', f'ID: {user_id}') if user_info else f'ID: {user_id}'

        reply = QMessageBox.question(
            self, "تأكيد الحذف",
            f"هل أنت متأكد من حذف المستخدم '{username}'؟\n"
            "لا يمكن التراجع عن هذا الإجراء."
        )

        if reply == QMessageBox.Yes:
            try:
                success = self.auth_service.delete_user(user_id)
                if success:
                    QMessageBox.information(self, "نجاح", "تم حذف المستخدم بنجاح.")
                    self.refresh_users_list()
                else:
                    QMessageBox.critical(self, "خطأ", "فشل حذف المستخدم. قد يكون هذا المستخدم هو آخر مسؤول.")
            except Exception as e:
                logger.error(f"خطأ في حذف المستخدم (ID: {user_id}): {str(e)}")
                QMessageBox.critical(self, "خطأ", f"فشل في حذف المستخدم:\n{str(e)}")

    def select_store_logo(self):
        """اختيار شعار المحل"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختيار شعار المحل", "", "ملفات الصور (*.png *.jpg *.jpeg *.bmp);;جميع الملفات (*)"
        )
        if file_path:
            self.settings.set_setting("store_logo", file_path)
            self.store_logo_path_label.setText(os.path.basename(file_path))
            QMessageBox.information(self, "تم", "تم تحديد الشعار بنجاح.")

    def save_settings(self):
        """حفظ الإعدادات العامة"""
        try:
            self.settings.set_setting("store_name", self.store_name_input.text())
            self.settings.set_setting("store_address", self.store_address_input.text())
            self.settings.set_setting("store_phone", self.store_phone_input.text())
            self.settings.set_setting("store_email", self.store_email_input.text())
            self.settings.set_setting("currency", self.currency_combo.currentText())
            self.settings.set_setting("language", self.language_combo.currentText())
            self.settings.set_setting("show_store_info_on_invoice", self.show_store_info_on_invoice_check.isChecked())
            self.settings.set_setting("show_store_logo_on_invoice", self.show_store_logo_on_invoice_check.isChecked())
            
            # تطبيق اللغة إذا تغيرت (يتطلب إعادة تشغيل الواجهة أو التطبيق)
            if self.settings.get_setting("language", "العربية") != "العربية":
                QMessageBox.warning(self, "تنبيه", "تم تغيير لغة الواجهة. يرجى إعادة تشغيل التطبيق لتطبيق التغييرات.")

            QMessageBox.information(self, "نجاح", "تم حفظ الإعدادات بنجاح.")

        except Exception as e:
            logger.error(f"خطأ في حفظ الإعدادات: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في حفظ الإعدادات:\n{str(e)}")

    def generate_report(self):
        """توليد التقرير بناءً على الاختيارات"""
        report_type = self.report_type_combo.currentText()
        start_date = self.start_date_edit.date().toString("yyyy-MM-dd")
        end_date = self.end_date_edit.date().toString("yyyy-MM-dd")

        try:
            # مسح المحتوى القديم
            for i in reversed(range(self.report_content_layout.count())): 
                widget = self.report_content_layout.itemAt(i).widget()
                if widget is not None:
                    widget.deleteLater()

            report_title = f"تقرير {report_type} من {start_date} إلى {end_date}"
            
            # توليد بيانات التقرير
            report_data = []
            headers = []
            
            if report_type == "تقرير المبيعات":
                headers = ["معرف الفاتورة", "التاريخ", "العميل", "الإجمالي"]
                # TODO: Implement sales service integration
                report_data.append(["001", start_date, "عميل تجريبي", "100.00"])
            elif report_type == "تقرير المخزون":
                headers = ["معرف المنتج", "اسم المنتج", "الكمية", "سعر البيع"]
                inventory_data = self.inventory_service.get_all_products()
                for item in inventory_data:
                    report_data.append([
                        str(item.get('id', '')),
                        item.get('name', ''),
                        str(item.get('quantity', 0)),
                        f"{item.get('price', 0):.2f}"
                    ])
            elif report_type == "تقرير الصيانة":
                headers = ["معرف العميل", "اسم العميل", "الجهاز", "الحالة"]
                # TODO: Implement repair service integration
                report_data.append(["001", "عميل تجريبي", "iPhone 13", "قيد الصيانة"])
            elif report_type == "تقرير الأرباح":
                 headers = ["التاريخ", "الإجمالي"]
                 # TODO: Implement profit calculation
                 report_data.append([start_date, "500.00"])

            if not report_data:
                no_data_label = QLabel(f"لا توجد بيانات لعرضها لهذا التقرير في الفترة المحددة.")
                no_data_label.setFont(QFont("Segoe UI", 14))
                no_data_label.setAlignment(Qt.AlignCenter)
                no_data_label.setStyleSheet("color: #7f8c8d;")
                self.report_content_layout.addWidget(no_data_label)
                return

            # عرض البيانات في جدول داخل مساحة التمرير
            report_table = QTableWidget()
            report_table.setColumnCount(len(headers))
            report_table.setHorizontalHeaderLabels(headers)
            report_table.setRowCount(len(report_data))
            report_table.setAlternatingRowColors(True)
            report_table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
            report_table.setFont(QFont("Segoe UI", 10))
            report_table.horizontalHeader().setFont(QFont("Segoe UI", 11, QFont.Bold))
            report_table.horizontalHeader().setDefaultAlignment(Qt.AlignCenter)
            report_table.verticalHeader().setVisible(False)
            report_table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
            report_table.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)

            # ضبط عرض الأعمدة بشكل ديناميكي أو افتراضي
            for col, header in enumerate(headers):
                report_table.horizontalHeader().setSectionResizeMode(col, QTableWidget.ResizeMode.Interactive)
                if header in ["اسم المنتج", "اسم العميل", "الجهاز", "البريد الإلكتروني"]:
                    report_table.setColumnWidth(col, 200)
                elif header in ["التاريخ", "الدور"]:
                    report_table.setColumnWidth(col, 150)
                elif header in ["الإجمالي", "الصافي", "التكلفة", "الربح"]:
                     report_table.setColumnWidth(col, 120)
                else:
                    report_table.setColumnWidth(col, 100)

            for row, row_data in enumerate(report_data):
                for col, item_data in enumerate(row_data):
                    report_table.setItem(row, col, QTableWidgetItem(str(item_data)))

            self.report_content_layout.addWidget(report_table)

            # زر تصدير PDF
            export_pdf_btn = QPushButton(f"تصدير تقرير {report_type} إلى PDF")
            export_pdf_btn.setFont(QFont("Segoe UI", 12, QFont.Bold))
            export_pdf_btn.setStyleSheet("""
                QPushButton {
                    background-color: #9b59b6; color: white; padding: 12px 25px; border-radius: 8px; border: none;
                }
                QPushButton:hover { background-color: #8e44ad; }
            """)
            export_pdf_btn.clicked.connect(lambda: self.export_report_to_pdf(report_title, headers, report_data))
            self.report_content_layout.addWidget(export_pdf_btn, alignment=Qt.AlignCenter)

        except Exception as e:
            logger.error(f"خطأ في توليد التقرير: {str(e)}")
            error_label = QLabel(f"حدث خطأ أثناء توليد التقرير: {str(e)}")
            error_label.setFont(QFont("Segoe UI", 14))
            error_label.setAlignment(Qt.AlignCenter)
            error_label.setStyleSheet("color: red;")
            self.report_content_layout.addWidget(error_label)

    def export_report_to_pdf(self, title, headers, data):
        """تصدير التقرير الحالي إلى ملف PDF"""
        file_path, _ = QFileDialog.getSaveFileName(
            self, "حفظ التقرير كـ PDF", f"{title.replace(' ', '_')}.pdf", "ملفات PDF (*.pdf)"
        )

        if file_path:
            try:
                # جمع معلومات المحل من الإعدادات
                store_name = self.settings.get_setting("store_name", "اسم المحل")
                store_address = self.settings.get_setting("store_address", "عنوان المحل")
                store_phone = self.settings.get_setting("store_phone", "رقم الهاتف")
                store_email = self.settings.get_setting("store_email", "البريد الإلكتروني")
                store_logo = self.settings.get_setting("store_logo", None)
                show_logo = self.settings.get_setting("show_store_logo_on_invoice", True)
                show_info = self.settings.get_setting("show_store_info_on_invoice", True)

                # إعداد بيانات التقرير للمولد
                report_content = {
                    'title': title,
                    'headers': headers,
                    'data': data
                }
                
                # استدعاء مولد PDF
                success = self.pdf_generator.generate_report_pdf(
                    file_path, 
                    report_content, 
                    store_name, 
                    store_address, 
                    store_phone, 
                    store_email, 
                    store_logo if show_logo else None,
                    show_info
                )
                
                if success:
                    QMessageBox.information(self, "نجاح", f"تم تصدير التقرير بنجاح إلى:\n{file_path}")
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في تصدير التقرير إلى PDF.")

            except Exception as e:
                logger.error(f"خطأ في تصدير التقرير إلى PDF: {str(e)}")
                QMessageBox.critical(self, "خطأ", f"فشل في تصدير التقرير:\n{str(e)}")

    def create_repair_window(self):
        """إنشاء نافذة الصيانة"""
        if self.repair_window_instance is None:
            self.repair_window_instance = RepairWindow(self)
        return self.repair_window_instance

    def show_maintenance_window(self):
        """عرض نافذة الصيانة"""
        widget = self.create_repair_window()
        self.show_content(widget)
        self.update_menu_button_style(self.btn_maintenance)


    def show_inventory_window(self):
        """عرض نافذة المخزون"""
        if self.inventory_window_instance is None:
            self.inventory_window_instance = InventoryWindow(self)
        self.show_content(self.inventory_window_instance)
        self.update_menu_button_style(self.btn_inventory)
        
    def show_sales_window(self):
        """عرض نافذة المبيعات"""
        if self.sales_window_instance is None:
            self.sales_window_instance = SalesWindow(self)
        self.show_content(self.sales_window_instance)
        self.update_menu_button_style(self.btn_sales)

    def show_content(self, widget):
        """عرض الويدجت المحدد في منطقة المحتوى الرئيسي"""
        # إزالة أي ويدجت سابق
        for i in reversed(range(self.content_layout.count())):
            self.content_layout.itemAt(i).widget().deleteLater()
        
        self.content_layout.addWidget(widget)

    def update_menu_button_style(self, selected_button):
        """تحديث تنسيق أزرار القائمة لتحديد الزر النشط"""
        buttons = [
            self.btn_dashboard, self.btn_inventory, self.btn_sales, 
            self.btn_maintenance, self.btn_reports, self.btn_settings, self.btn_users
        ]
        for btn in buttons:
            if btn == selected_button:
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 15px 20px; 
                        text-align: right; 
                        border: none; 
                        font-weight: bold;
                        background-color: #2c3e50; 
                        color: #3498db;
                    }
                    QPushButton:hover { background-color: #4a637d; }
                    .menu-icon { width: 24px; height: 24px; margin-left: 15px; margin-right: 10px;}
                """)
            else:
                btn.setStyleSheet("""
                    QPushButton {
                        padding: 15px 20px; 
                        text-align: right; 
                        border: none; 
                        font-weight: bold;
                        background-color: #34495e; 
                        color: white;
                    }
                    QPushButton:hover { background-color: #4a637d; }
                    .menu-icon { width: 24px; height: 24px; margin-left: 15px; margin-right: 10px;}
                """)
                
    def show_login_window(self):
        """عرض نافذة تسجيل الدخول"""
        from app.ui.login_dialog import LoginDialog
        self.login_dialog = LoginDialog(self)
        if self.login_dialog.exec():
            # Handle successful login
            pass

    def on_login_success(self, user_data):
        """معالجة نجاح تسجيل الدخول"""
        self.current_user = user_data
        # تحديث القائمة بناءً على دور المستخدم
        self.toggle_admin_menu_items()
        
        # تحميل الإعدادات بعد تسجيل الدخول
        self.settings.load_settings()
        
        # عرض لوحة التحكم
        self.show_content(self.dashboard_widget)
        self.update_menu_button_style(self.btn_dashboard)
        
        # تحديث واجهة المستخدم بالبيانات المحملة
        self.refresh_backups_list()
        self.refresh_users_list()

    def toggle_admin_menu_items(self):
        """إظهار أو إخفاء عناصر القائمة الخاصة بالمسؤول"""
        is_admin = self.current_user and self.current_user.get('role') == 'Admin'
        
        # عرض أو إخفاء زر إدارة المستخدمين
        if is_admin:
            if self.btn_users not in self.menu_layout.findChildren(QPushButton):
                self.menu_layout.insertWidget(self.menu_layout.count() -1 , self.btn_users) # Insert before logout
        else:
            if self.btn_users in self.menu_layout.findChildren(QPushButton):
                self.btn_users.hide()
                
        # تحديث تبويب المستخدمين في الإعدادات
        if hasattr(self, 'settings_widget') and self.settings_widget:
            tab_bar = self.settings_widget.findChild(QTabWidget).tabBar()
            user_tab_index = -1
            for i in range(tab_bar.count()):
                if tab_bar.tabText(i) == "إدارة المستخدمين":
                    user_tab_index = i
                    break
            
            if is_admin:
                if user_tab_index == -1:
                    users_tab = self.create_users_tab()
                    self.settings_widget.findChild(QTabWidget).addTab(users_tab, "إدارة المستخدمين")
                else:
                    self.settings_widget.findChild(QTabWidget).setTabVisible(user_tab_index, True)
            else:
                if user_tab_index != -1:
                    self.settings_widget.findChild(QTabWidget).setTabVisible(user_tab_index, False)


    def logout(self):
        """تسجيل الخروج"""
        reply = QMessageBox.question(
            self, "تأكيد تسجيل الخروج",
            "هل أنت متأكد أنك تريد تسجيل الخروج؟"
        )
        if reply == QMessageBox.Yes:
            self.current_user = None
            # إغلاق جميع النوافذ الفرعية المفتوحة
            if self.repair_window_instance:
                self.repair_window_instance.close()
                self.repair_window_instance = None
            if self.inventory_window_instance:
                self.inventory_window_instance.close()
                self.inventory_window_instance = None
                
            # إظهار نافذة تسجيل الدخول مرة أخرى
            self.show_login_window()

    def open_user_management(self):
        """فتح نافذة إدارة المستخدمين"""
        if not self.current_user or self.current_user.get('role') != 'Admin':
            QMessageBox.warning(self, "صلاحيات محدودة", "ليس لديك صلاحيات كافية للوصول إلى هذه الميزة.")
            return
            
        # TODO: Implement user management dialog
        QMessageBox.information(self, "قريباً", "ميزة إدارة المستخدمين ستكون متاحة قريباً")
        
    def closeEvent(self, event):
        """معالجة حدث إغلاق النافذة الرئيسية"""
        # يمكنك إضافة كود هنا لحفظ الإعدادات أو القيام بأي إجراءات قبل الإغلاق
        # على سبيل المثال، حفظ الإعدادات تلقائيًا
        self.settings.save_settings() 
        event.accept()

# --- وظائف متعلقة بالنسخ الاحتياطي (من الكود الأصلي) ---

    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        try:
            from app.services.backup_service import BackupService
            backup_service = BackupService()

            backup_path = backup_service.create_backup()
            if backup_path:
                QMessageBox.information(
                    self, "نجح", 
                    f"تم إنشاء النسخة الاحتياطية بنجاح:\n{backup_path}"
                )
                self.refresh_backups_list()
            else:
                QMessageBox.critical(self, "خطأ", "فشل في إنشاء النسخة الاحتياطية")

        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
            QMessageBox.critical(self, "خطأ", f"فشل في إنشاء النسخة الاحتياطية:\n{str(e)}")

    def restore_backup(self):
        """استعادة نسخة احتياطية"""
        file_path, _ = QFileDialog.getOpenFileName(
            self, "اختر النسخة الاحتياطية", 
            "", "ملفات النسخ الاحتياطي (*.backup *.db)"
        )

        if file_path:
            reply = QMessageBox.question(
                self, "تأكيد",
                "تحذير: سيتم استبدال جميع البيانات الحالية بالنسخة الاحتياطية.\n"
                "هل أنت متأكد من المتابعة؟"
            )

            if reply == QMessageBox.Yes:
                try:
                    from app.services.backup_service import BackupService
                    backup_service = BackupService()

                    success = backup_service.restore_backup(file_path)
                    if success:
                        QMessageBox.information(
                            self, "نجح", 
                            "تم استعادة النسخة الاحتياطية بنجاح.\n"
                            "يرجى إعادة تشغيل التطبيق."
                        )
                        # ربما نحتاج لإعادة تشغيل التطبيق هنا أو إعلام المستخدم بذلك
                    else:
                        QMessageBox.critical(self, "خطأ", "فشل في استعادة النسخة الاحتياطية")

                except Exception as e:
                    logger.error(f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
                    QMessageBox.critical(self, "خطأ", f"فشل في استعادة النسخة الاحتياطية:\n{str(e)}")

    def refresh_backups_list(self):
        """تحديث قائمة النسخ الاحتياطية"""
        try:
            from app.services.backup_service import BackupService
            import os
            from datetime import datetime

            backup_service = BackupService()
            backup_dir = backup_service.backup_dir

            if not backup_dir.exists():
                self.backups_table.setRowCount(0)
                return

            backups = []
            for file_path in backup_dir.glob("*.backup"):
                try:
                    stat = file_path.stat()
                    backups.append({
                        'name': file_path.name,
                        'path': str(file_path),
                        'date': datetime.fromtimestamp(stat.st_mtime),
                        'size': stat.st_size
                    })
                except OSError:
                    # تخطي الملفات التي لا يمكن الوصول إليها
                    continue


            # ترتيب حسب التاريخ
            backups.sort(key=lambda x: x['date'], reverse=True)

            self.backups_table.setRowCount(len(backups))

            for row, backup in enumerate(backups):
                # اسم الملف
                self.backups_table.setItem(row, 0, QTableWidgetItem(backup['name']))

                # التاريخ
                date_str = backup['date'].strftime("%Y-%m-%d %H:%M")
                self.backups_table.setItem(row, 1, QTableWidgetItem(date_str))

                # الحجم
                size_mb = backup['size'] / (1024 * 1024)
                size_str = f"{size_mb:.2f} MB"
                self.backups_table.setItem(row, 2, QTableWidgetItem(size_str))

                # العمليات
                operations_widget = self.create_backup_operations(backup)
                self.backups_table.setCellWidget(row, 3, operations_widget)

        except Exception as e:
            logger.error(f"خطأ في تحديث قائمة النسخ الاحتياطية: {str(e)}")

    def create_backup_operations(self, backup):
        """إنشاء أزرار العمليات للنسخة الاحتياطية"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)

        # زر الاستعادة
        restore_btn = QPushButton("استعادة")
        restore_btn.setStyleSheet("""
            QPushButton {
                background-color: #e67e22;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #d35400;
            }
        """)
        restore_btn.clicked.connect(lambda: self.restore_specific_backup(backup['path']))
        layout.addWidget(restore_btn)

        # زر الحذف
        delete_btn = QPushButton("حذف")
        delete_btn.setStyleSheet("""
            QPushButton {
                background-color: #e74c3c;
                color: white;
                border: none;
                border-radius: 3px;
                padding: 5px 10px;
                font-size: 10px;
            }
            QPushButton:hover {
                background-color: #c0392b;
            }
        """)
        delete_btn.clicked.connect(lambda: self.delete_backup(backup['path']))
        layout.addWidget(delete_btn)

        return widget

    def restore_specific_backup(self, backup_path):
        """استعادة نسخة احتياطية محددة"""
        reply = QMessageBox.question(
            self, "تأكيد",
            f"هل أنت متأكد من استعادة النسخة الاحتياطية:\n{backup_path}؟"
        )

        if reply == QMessageBox.Yes:
            try:
                from app.services.backup_service import BackupService
                backup_service = BackupService()

                success = backup_service.restore_backup(backup_path)
                if success:
                    QMessageBox.information(
                        self, "نجح", 
                        "تم استعادة النسخة الاحتياطية بنجاح.\n"
                        "يرجى إعادة تشغيل التطبيق."
                    )
                else:
                    QMessageBox.critical(self, "خطأ", "فشل في استعادة النسخة الاحتياطية")

            except Exception as e:
                logger.error(f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
                QMessageBox.critical(self, "خطأ", f"فشل في استعادة النسخة الاحتياطية:\n{str(e)}")

    def delete_backup(self, backup_path):
        """حذف نسخة احتياطية"""
        reply = QMessageBox.question(
            self, "تأكيد",
            f"هل أنت متأكد من حذف النسخة الاحتياطية:\n{backup_path}؟"
        )

        if reply == QMessageBox.Yes:
            try:
                import os
                os.remove(backup_path)
                QMessageBox.information(self, "نجاح", "تم حذف النسخة الاحتياطية بنجاح")
                self.refresh_backups_list()

            except Exception as e:
                logger.error(f"خطأ في حذف النسخة الاحتياطية: {str(e)}")
                QMessageBox.critical(self, "خطأ", f"فشل في حذف النسخة الاحتياطية:\n{str(e)}")

    def cancel_changes(self):
        """إلغاء التغييرات"""
        reply = QMessageBox.question(
            self, "تأكيد",
            "هل أنت متأكد من إلغاء التغييرات؟"
        )

        if reply == QMessageBox.Yes:
            self.close()

if __name__ == '__main__':
    app = QApplication(sys.argv)
    
    # ضبط إعدادات التطبيق الأساسية (مثل لغة الواجهة)
    # يمكن تحسين ذلك بتحميل الإعدادات مبكرًا
    settings = Settings()
    language = settings.get_setting("language", "العربية")
    
    # قد تحتاج إلى منطق إضافي هنا لتعيين لغة Qt إذا لزم الأمر
    # مثال: app.setApplicationLocale(QLocale(language)) 

    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec())