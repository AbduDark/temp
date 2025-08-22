#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة تسجيل الدخول - Login Dialog
"""

from PySide6.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, 
                              QLineEdit, QPushButton, QFrame, QMessageBox,
                              QCheckBox, QApplication)
from PySide6.QtCore import Qt, QPropertyAnimation, QEasingCurve, QRect
from PySide6.QtGui import QFont, QPixmap, QIcon

from app.services.auth_service import AuthService


class LoginDialog(QDialog):
    """نافذة تسجيل الدخول"""
    
    def __init__(self):
        super().__init__()
        self.auth_service = AuthService()
        self.current_user = None
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        self.setWindowTitle("تسجيل الدخول - نظام إدارة محل الموبايلات")
        self.setFixedSize(400, 500)
        self.setWindowFlags(Qt.Dialog | Qt.WindowCloseButtonHint)
        self.setLayoutDirection(Qt.RightToLeft)
        
        # التصميم الرئيسي
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(30, 30, 30, 30)
        main_layout.setSpacing(20)
        
        # إطار تسجيل الدخول
        login_frame = QFrame()
        login_frame.setObjectName("loginFrame")
        frame_layout = QVBoxLayout(login_frame)
        frame_layout.setContentsMargins(30, 30, 30, 30)
        frame_layout.setSpacing(20)
        
        # شعار/عنوان التطبيق
        title_label = QLabel("نظام إدارة محل الموبايلات")
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setObjectName("titleLabel")
        frame_layout.addWidget(title_label)
        
        # أيقونة المستخدم
        user_icon_label = QLabel("👤")
        user_icon_label.setAlignment(Qt.AlignCenter)
        user_icon_label.setObjectName("userIcon")
        frame_layout.addWidget(user_icon_label)
        
        # حقل اسم المستخدم
        username_layout = QVBoxLayout()
        username_label = QLabel("اسم المستخدم:")
        username_label.setObjectName("fieldLabel")
        self.username_edit = QLineEdit()
        self.username_edit.setPlaceholderText("أدخل اسم المستخدم")
        self.username_edit.setObjectName("inputField")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_edit)
        frame_layout.addLayout(username_layout)
        
        # حقل كلمة المرور
        password_layout = QVBoxLayout()
        password_label = QLabel("كلمة المرور:")
        password_label.setObjectName("fieldLabel")
        self.password_edit = QLineEdit()
        self.password_edit.setPlaceholderText("أدخل كلمة المرور")
        self.password_edit.setEchoMode(QLineEdit.Password)
        self.password_edit.setObjectName("inputField")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_edit)
        frame_layout.addLayout(password_layout)
        
        # خيار تذكرني
        self.remember_checkbox = QCheckBox("تذكرني")
        self.remember_checkbox.setObjectName("rememberCheckbox")
        frame_layout.addWidget(self.remember_checkbox)
        
        # أزرار العمل
        buttons_layout = QHBoxLayout()
        
        self.login_button = QPushButton("تسجيل الدخول")
        self.login_button.setObjectName("loginButton")
        self.login_button.clicked.connect(self.login)
        
        self.cancel_button = QPushButton("إلغاء")
        self.cancel_button.setObjectName("cancelButton")
        self.cancel_button.clicked.connect(self.reject)
        
        buttons_layout.addWidget(self.login_button)
        buttons_layout.addWidget(self.cancel_button)
        frame_layout.addLayout(buttons_layout)
        
        # معلومات تجريبية
        info_layout = QVBoxLayout()
        info_label = QLabel("بيانات تجريبية:")
        info_label.setObjectName("infoLabel")
        
        admin_info = QLabel("المدير: admin / admin123")
        admin_info.setObjectName("credentialInfo")
        
        cashier_info = QLabel("الكاشير: cashier / cashier123")
        cashier_info.setObjectName("credentialInfo")
        
        info_layout.addWidget(info_label)
        info_layout.addWidget(admin_info)
        info_layout.addWidget(cashier_info)
        frame_layout.addLayout(info_layout)
        
        main_layout.addWidget(login_frame)
        
        # تطبيق الستايل
        self.setup_style()
        
        # ربط Enter بتسجيل الدخول
        self.username_edit.returnPressed.connect(self.password_edit.setFocus)
        self.password_edit.returnPressed.connect(self.login)
        
        # التركيز على حقل اسم المستخدم
        self.username_edit.setFocus()
    
    def setup_style(self):
        """إعداد نمط النافذة"""
        style = """
        QDialog {
            background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                        stop:0 #667eea, stop:1 #764ba2);
        }
        
        #loginFrame {
            background-color: rgba(255, 255, 255, 0.95);
            border-radius: 15px;
            border: 2px solid rgba(255, 255, 255, 0.8);
        }
        
        #titleLabel {
            font-size: 24px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 10px;
        }
        
        #userIcon {
            font-size: 48px;
            color: #3498db;
            margin-bottom: 10px;
        }
        
        #fieldLabel {
            font-size: 14px;
            font-weight: bold;
            color: #2c3e50;
            margin-bottom: 5px;
        }
        
        #inputField {
            font-size: 14px;
            padding: 12px;
            border: 2px solid #bdc3c7;
            border-radius: 8px;
            background-color: white;
            selection-background-color: #3498db;
        }
        
        #inputField:focus {
            border-color: #3498db;
            outline: none;
        }
        
        #rememberCheckbox {
            font-size: 12px;
            color: #34495e;
            margin: 10px 0;
        }
        
        #loginButton {
            background-color: #3498db;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            min-width: 120px;
        }
        
        #loginButton:hover {
            background-color: #2980b9;
        }
        
        #loginButton:pressed {
            background-color: #21618c;
        }
        
        #cancelButton {
            background-color: #95a5a6;
            color: white;
            font-size: 16px;
            font-weight: bold;
            padding: 12px 30px;
            border: none;
            border-radius: 8px;
            min-width: 120px;
        }
        
        #cancelButton:hover {
            background-color: #7f8c8d;
        }
        
        #infoLabel {
            font-size: 12px;
            font-weight: bold;
            color: #e74c3c;
            margin-top: 20px;
        }
        
        #credentialInfo {
            font-size: 11px;
            color: #7f8c8d;
            background-color: #ecf0f1;
            padding: 5px;
            border-radius: 4px;
            margin: 2px 0;
        }
        """
        
        self.setStyleSheet(style)
    
    def login(self):
        """محاولة تسجيل الدخول"""
        username = self.username_edit.text().strip()
        password = self.password_edit.text()
        
        if not username or not password:
            QMessageBox.warning(
                self, "بيانات ناقصة",
                "يرجى إدخال اسم المستخدم وكلمة المرور"
            )
            return
        
        # تعطيل الأزرار أثناء المعالجة
        self.login_button.setEnabled(False)
        self.login_button.setText("جاري التحقق...")
        
        # محاولة تسجيل الدخول
        user = self.auth_service.login(username, password)
        
        if user:
            self.current_user = user
            QMessageBox.information(
                self, "نجح تسجيل الدخول",
                f"مرحباً {user['full_name']}"
            )
            self.accept()
        else:
            QMessageBox.critical(
                self, "فشل تسجيل الدخول",
                "اسم المستخدم أو كلمة المرور غير صحيحة"
            )
            # إعادة تفعيل الأزرار
            self.login_button.setEnabled(True)
            self.login_button.setText("تسجيل الدخول")
            
            # مسح كلمة المرور
            self.password_edit.clear()
            self.password_edit.setFocus()
    
    def get_current_user(self):
        """الحصول على بيانات المستخدم المسجل"""
        return self.current_user
    
    def keyPressEvent(self, event):
        """التعامل مع ضغط المفاتيح"""
        if event.key() == Qt.Key_Escape:
            self.reject()
        else:
            super().keyPressEvent(event)
