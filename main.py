#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام إدارة محل موبايلات - الملف الرئيسي
Mobile Shop Management System - Main Entry Point
"""

import sys
import os
from pathlib import Path
from PySide6.QtWidgets import QApplication, QMessageBox
from PySide6.QtCore import Qt, QTranslator
from PySide6.QtGui import QIcon

# إضافة مسار التطبيق إلى sys.path
app_path = Path(__file__).parent
sys.path.insert(0, str(app_path))

from app.models.database import DatabaseManager
from app.ui.login_dialog import LoginDialog
from app.ui.main_window import MainWindow
from app.utils.logger import setup_logger
from config.settings import APP_CONFIG

def setup_directories():
    """إنشاء المجلدات المطلوبة إذا لم تكن موجودة"""
    directories = [
        'data',
        'assets/icons',
        'reports/daily',
        'backup',
        'logs'
    ]
    
    for directory in directories:
        Path(directory).mkdir(parents=True, exist_ok=True)

def setup_database():
    """إعداد قاعدة البيانات الأولي"""
    try:
        db = DatabaseManager()
        db.initialize_database()
        return True
    except Exception as e:
        QMessageBox.critical(
            None,
            "خطأ في قاعدة البيانات",
            f"فشل في إعداد قاعدة البيانات:\n{str(e)}"
        )
        return False

def main():
    """الدالة الرئيسية لتشغيل التطبيق"""
    # إنشاء التطبيق
    app = QApplication(sys.argv)
    app.setApplicationName(APP_CONFIG['app_name'])
    app.setApplicationVersion(APP_CONFIG['version'])
    app.setOrganizationName(APP_CONFIG['organization'])
    
    # إعداد الترجمة العربية
    app.setLayoutDirection(Qt.RightToLeft)
    
    # إعداد أيقونة التطبيق
    icon_path = Path("assets/icons/app_icon.ico")
    if icon_path.exists():
        app.setWindowIcon(QIcon(str(icon_path)))
    
    # إعداد نظام التسجيل
    logger = setup_logger()
    logger.info("بدء تشغيل التطبيق")
    
    try:
        # إعداد المجلدات
        setup_directories()
        logger.info("تم إعداد المجلدات المطلوبة")
        
        # إعداد قاعدة البيانات
        if not setup_database():
            return 1
        logger.info("تم إعداد قاعدة البيانات")
        
        # عرض نافذة تسجيل الدخول
        login_dialog = LoginDialog()
        if login_dialog.exec() == LoginDialog.Accepted:
            # الحصول على بيانات المستخدم المسجل
            current_user = login_dialog.get_current_user()
            
            # عرض النافذة الرئيسية
            main_window = MainWindow(current_user)
            main_window.show()
            
            logger.info(f"تم تسجيل دخول المستخدم: {current_user['username']}")
            
            # تشغيل التطبيق
            return app.exec()
        else:
            logger.info("تم إلغاء تسجيل الدخول")
            return 0
            
    except Exception as e:
        logger.error(f"خطأ غير متوقع: {str(e)}")
        QMessageBox.critical(
            None,
            "خطأ",
            f"حدث خطأ غير متوقع:\n{str(e)}"
        )
        return 1

if __name__ == "__main__":
    sys.exit(main())
