#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
النافذة الرئيسية للتطبيق - Main Window
"""

import os
from PySide6.QtWidgets import (QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                              QStackedWidget, QMenuBar, QStatusBar, QLabel,
                              QToolBar, QPushButton, QMessageBox, QSplitter)
from PySide6.QtCore import Qt, QTimer, QSize
from PySide6.QtGui import QAction, QIcon, QFont

from .dashboard import Dashboard
from .pos_window import POSWindow
from .inventory_window import InventoryWindow
from .repair_window import RepairWindow
from .reports_window import ReportsWindow
from .settings_window import SettingsWindow
from .daily_close_window import DailyCloseWindow

from app.services.auth_service import AuthService
from app.services.inventory_service import InventoryService
from app.services.pos_service import POSService
from app.services.repair_service import RepairService
from app.services.report_service import ReportService
from app.services.backup_service import BackupService


class MainWindow(QMainWindow):
    """النافذة الرئيسية للتطبيق"""
    
    def __init__(self, current_user):
        super().__init__()
        self.current_user = current_user
        self.setup_services()
        self.setup_ui()
        self.setup_timer()
        
    def setup_services(self):
        """إعداد الخدمات"""
        self.auth_service = AuthService()
        self.auth_service._current_user = self.current_user
        
        self.inventory_service = InventoryService(self.auth_service)
        self.pos_service = POSService(self.auth_service)
        self.repair_service = RepairService(self.auth_service)
        self.report_service = ReportService(self.auth_service)
        self.backup_service = BackupService(self.auth_service)
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("نظام إدارة محل الموبايلات")
        self.setMinimumSize(1200, 800)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # إعداد القوائم
        self.setup_menubar()
        
        # إعداد شريط الأدوات
        self.setup_toolbar()
        
        # إعداد المحتوى الرئيسي
        self.setup_main_content()
        
        # إعداد شريط الحالة
        self.setup_statusbar()
        
        # تطبيق الستايل
        self.setup_style()
    
    def setup_menubar(self):
        """إعداد شريط القوائم"""
        menubar = self.menuBar()
        menubar.setLayoutDirection(Qt.RightToLeft)
        
        # قائمة الملف
        file_menu = menubar.addMenu("ملف")
        
        # نسخة احتياطية
        backup_action = QAction("إنشاء نسخة احتياطية", self)
        backup_action.triggered.connect(self.create_backup)
        file_menu.addAction(backup_action)
        
        # استعادة نسخة احتياطية
        restore_action = QAction("استعادة نسخة احتياطية", self)
        restore_action.triggered.connect(self.restore_backup)
        file_menu.addAction(restore_action)
        
        file_menu.addSeparator()
        
        # خروج
        exit_action = QAction("خروج", self)
        exit_action.triggered.connect(self.close)
        file_menu.addAction(exit_action)
        
        # قائمة النظام
        system_menu = menubar.addMenu("النظام")
        
        # إعدادات
        settings_action = QAction("الإعدادات", self)
        settings_action.triggered.connect(self.show_settings)
        system_menu.addAction(settings_action)
        
        # إدارة المستخدمين (للمدير فقط)
        if self.current_user['role'] == 'Admin':
            users_action = QAction("إدارة المستخدمين", self)
            users_action.triggered.connect(self.show_user_management)
            system_menu.addAction(users_action)
        
        # قائمة المساعدة
        help_menu = menubar.addMenu("مساعدة")
        
        about_action = QAction("حول النظام", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
    
    def setup_toolbar(self):
        """إعداد شريط الأدوات"""
        toolbar = QToolBar("الأدوات الرئيسية")
        toolbar.setLayoutDirection(Qt.RightToLeft)
        toolbar.setToolButtonStyle(Qt.ToolButtonTextBesideIcon)
        toolbar.setIconSize(QSize(32, 32))
        self.addToolBar(toolbar)
        
        # أزرار التنقل السريع
        buttons = [
            ("لوحة التحكم", "dashboard", self.show_dashboard),
            ("نقطة البيع", "pos", self.show_pos),
            ("المخزون", "inventory", self.show_inventory),
            ("الصيانة", "repair", self.show_repair),
            ("التقارير", "reports", self.show_reports),
            ("التقفيل اليومي", "daily_close", self.show_daily_close)
        ]
        
        for text, icon_name, callback in buttons:
            action = QAction(text, self)
            
            # محاولة تحميل الأيقونة
            icon_path = f"assets/icons/{icon_name}.png"
            if os.path.exists(icon_path):
                action.setIcon(QIcon(icon_path))
            
            action.triggered.connect(callback)
            toolbar.addAction(action)
            
            # فاصل بعد كل زر
            if text != "التقفيل اليومي":
                toolbar.addSeparator()
    
    def setup_main_content(self):
        """إعداد المحتوى الرئيسي"""
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QHBoxLayout(central_widget)
        layout.setContentsMargins(5, 5, 5, 5)
        
        # إنشاء المحتوى المكدس
        self.stacked_widget = QStackedWidget()
        
        # إنشاء الصفحات
        self.dashboard = Dashboard(self)
        self.pos_window = POSWindow(self)
        self.inventory_window = InventoryWindow(self)
        self.repair_window = RepairWindow(self)
        self.reports_window = ReportsWindow(self)
        self.settings_window = SettingsWindow(self)
        self.daily_close_window = DailyCloseWindow(self)
        
        # إضافة الصفحات للمكدس
        self.stacked_widget.addWidget(self.dashboard)
        self.stacked_widget.addWidget(self.pos_window)
        self.stacked_widget.addWidget(self.inventory_window)
        self.stacked_widget.addWidget(self.repair_window)
        self.stacked_widget.addWidget(self.reports_window)
        self.stacked_widget.addWidget(self.settings_window)
        self.stacked_widget.addWidget(self.daily_close_window)
        
        layout.addWidget(self.stacked_widget)
        
        # عرض لوحة التحكم بشكل افتراضي
        self.show_dashboard()
    
    def setup_statusbar(self):
        """إعداد شريط الحالة"""
        statusbar = self.statusBar()
        statusbar.setLayoutDirection(Qt.RightToLeft)
        
        # معلومات المستخدم
        self.user_label = QLabel(f"المستخدم: {self.current_user['full_name']} ({self.current_user['role']})")
        statusbar.addPermanentWidget(self.user_label)
        
        # الوقت الحالي
        self.time_label = QLabel()
        statusbar.addPermanentWidget(self.time_label)
        
        # حالة الاتصال
        self.connection_label = QLabel("متصل")
        statusbar.addPermanentWidget(self.connection_label)
    
    def setup_style(self):
        """إعداد نمط التطبيق"""
        style = """
        QMainWindow {
            background-color: #f5f5f5;
        }
        
        QMenuBar {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            padding: 4px;
        }
        
        QMenuBar::item {
            background-color: transparent;
            padding: 4px 8px;
            margin: 2px;
            border-radius: 4px;
        }
        
        QMenuBar::item:selected {
            background-color: #3498db;
        }
        
        QToolBar {
            background-color: #34495e;
            border: none;
            spacing: 3px;
            padding: 5px;
        }
        
        QToolBar QToolButton {
            background-color: #34495e;
            color: white;
            border: none;
            padding: 8px;
            margin: 2px;
            border-radius: 6px;
            font-weight: bold;
        }
        
        QToolBar QToolButton:hover {
            background-color: #3498db;
        }
        
        QToolBar QToolButton:pressed {
            background-color: #2980b9;
        }
        
        QStatusBar {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
        }
        
        QStatusBar QLabel {
            color: white;
            margin: 0 10px;
        }
        """
        
        self.setStyleSheet(style)
    
    def setup_timer(self):
        """إعداد مؤقت تحديث الوقت"""
        self.timer = QTimer()
        self.timer.timeout.connect(self.update_time)
        self.timer.start(1000)  # تحديث كل ثانية
        self.update_time()
    
    def update_time(self):
        """تحديث عرض الوقت"""
        from datetime import datetime
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.time_label.setText(f"الوقت: {current_time}")
    
    # وظائف التنقل
    def show_dashboard(self):
        """عرض لوحة التحكم"""
        self.stacked_widget.setCurrentWidget(self.dashboard)
        self.dashboard.refresh_data()
        
    def show_pos(self):
        """عرض نقطة البيع"""
        if self.auth_service.has_permission('create_sale'):
            self.stacked_widget.setCurrentWidget(self.pos_window)
            self.pos_window.refresh_data()
        else:
            self.show_permission_denied()
    
    def show_inventory(self):
        """عرض إدارة المخزون"""
        if self.auth_service.has_permission('view_products'):
            self.stacked_widget.setCurrentWidget(self.inventory_window)
            self.inventory_window.refresh_data()
        else:
            self.show_permission_denied()
    
    def show_repair(self):
        """عرض إدارة الصيانة"""
        if self.auth_service.has_permission('view_repairs'):
            self.stacked_widget.setCurrentWidget(self.repair_window)
            self.repair_window.refresh_data()
        else:
            self.show_permission_denied()
    
    def show_reports(self):
        """عرض التقارير"""
        if self.auth_service.has_permission('view_reports_basic'):
            self.stacked_widget.setCurrentWidget(self.reports_window)
            self.reports_window.refresh_data()
        else:
            self.show_permission_denied()
    
    def show_daily_close(self):
        """عرض التقفيل اليومي"""
        if self.auth_service.has_permission('daily_close'):
            self.stacked_widget.setCurrentWidget(self.daily_close_window)
            self.daily_close_window.refresh_data()
        else:
            self.show_permission_denied()
    
    def show_settings(self):
        """عرض الإعدادات"""
        self.stacked_widget.setCurrentWidget(self.settings_window)
        self.settings_window.refresh_data()
    
    def show_permission_denied(self):
        """عرض رسالة عدم وجود صلاحية"""
        QMessageBox.warning(
            self, "غير مصرح", 
            "ليس لديك صلاحية للوصول إلى هذه الميزة"
        )
    
    # وظائف النسخ الاحتياطي
    def create_backup(self):
        """إنشاء نسخة احتياطية"""
        try:
            backup_path = self.backup_service.create_backup()
            if backup_path:
                QMessageBox.information(
                    self, "نجح", 
                    f"تم إنشاء النسخة الاحتياطية بنجاح:\n{backup_path}"
                )
            else:
                QMessageBox.critical(
                    self, "خطأ", 
                    "فشل في إنشاء النسخة الاحتياطية"
                )
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", 
                f"حدث خطأ في إنشاء النسخة الاحتياطية:\n{str(e)}"
            )
    
    def restore_backup(self):
        """استعادة نسخة احتياطية"""
        from PySide6.QtWidgets import QFileDialog
        
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, "اختر ملف النسخة الاحتياطية", 
                "backup", "ملفات النسخ الاحتياطية (*.zip)"
            )
            
            if file_path:
                reply = QMessageBox.question(
                    self, "تأكيد", 
                    "هل أنت متأكد من استعادة هذه النسخة الاحتياطية؟\n"
                    "سيتم استبدال البيانات الحالية.",
                    QMessageBox.Yes | QMessageBox.No
                )
                
                if reply == QMessageBox.Yes:
                    success = self.backup_service.restore_backup(file_path)
                    if success:
                        QMessageBox.information(
                            self, "نجح", 
                            "تم استعادة النسخة الاحتياطية بنجاح.\n"
                            "سيتم إعادة تشغيل التطبيق."
                        )
                        # إعادة تشغيل التطبيق
                        import sys
                        import subprocess
                        subprocess.Popen([sys.executable] + sys.argv)
                        self.close()
                    else:
                        QMessageBox.critical(
                            self, "خطأ", 
                            "فشل في استعادة النسخة الاحتياطية"
                        )
        except Exception as e:
            QMessageBox.critical(
                self, "خطأ", 
                f"حدث خطأ في استعادة النسخة الاحتياطية:\n{str(e)}"
            )
    
    def show_user_management(self):
        """عرض إدارة المستخدمين"""
        # سيتم تنفيذها لاحقاً كنافذة منفصلة
        QMessageBox.information(
            self, "قريباً", 
            "ميزة إدارة المستخدمين ستكون متاحة قريباً"
        )
    
    def show_about(self):
        """عرض معلومات حول النظام"""
        QMessageBox.about(
            self, "حول النظام",
            "نظام إدارة محل الموبايلات\n"
            "الإصدار 1.0.0\n\n"
            "نظام شامل لإدارة المبيعات والمخزون والصيانة\n"
            "في محلات الهواتف المحمولة"
        )
    
    def closeEvent(self, event):
        """التعامل مع إغلاق النافذة"""
        reply = QMessageBox.question(
            self, "تأكيد الخروج",
            "هل أنت متأكد من الخروج من النظام؟",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            # تسجيل خروج المستخدم
            self.auth_service.logout()
            
            # إجراء نسخة احتياطية تلقائية
            try:
                self.backup_service.auto_backup()
            except Exception:
                pass  # تجاهل أخطاء النسخ الاحتياطي عند الخروج
            
            event.accept()
        else:
            event.ignore()
