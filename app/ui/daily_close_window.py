#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نافذة التقفيل اليومي - Daily Close Window
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QLineEdit, QComboBox,
                              QTableWidget, QTableWidgetItem, QSpinBox,
                              QDoubleSpinBox, QTextEdit, QFrame, QGroupBox,
                              QMessageBox, QDateEdit, QHeaderView, QCheckBox,
                              QScrollArea, QSplitter, QFileDialog)
from PySide6.QtCore import Qt, QDate, QTimer
from PySide6.QtGui import QFont, QColor, QPixmap
from datetime import datetime, date
import os
import logging

from app.utils.pdf_generator import PDFGenerator

logger = logging.getLogger(__name__)


class DailyCloseWindow(QWidget):
    """نافذة التقفيل اليومي"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.pdf_generator = PDFGenerator()
        self.current_close_data = None
        self.setup_ui()
        
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # عنوان الصفحة
        title_label = QLabel("التقفيل اليومي")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("""
            QLabel {
                color: #2c3e50;
                padding: 15px;
                background-color: #ecf0f1;
                border-radius: 10px;
                margin-bottom: 20px;
            }
        """)
        layout.addWidget(title_label)
        
        # شريط الأدوات
        toolbar = self.create_toolbar()
        layout.addWidget(toolbar)
        
        # المحتوى الرئيسي
        main_content = QSplitter(Qt.Horizontal)
        
        # الجانب الأيسر - ملخص التقفيل
        left_panel = self.create_summary_panel()
        main_content.addWidget(left_panel)
        
        # الجانب الأيمن - التفاصيل والإجراءات
        right_panel = self.create_details_panel()
        main_content.addWidget(right_panel)
        
        # تحديد نسب التقسيم
        main_content.setSizes([400, 300])
        
        layout.addWidget(main_content)
        
        # شريط الحالة
        status_bar = self.create_status_bar()
        layout.addWidget(status_bar)
    
    def create_toolbar(self):
        """إنشاء شريط الأدوات"""
        toolbar = QFrame()
        toolbar.setFrameStyle(QFrame.StyledPanel)
        toolbar.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
                margin-bottom: 10px;
            }
        """)
        
        layout = QHBoxLayout(toolbar)
        
        # تاريخ التقفيل
        layout.addWidget(QLabel("تاريخ التقفيل:"))
        self.close_date = QDateEdit()
        self.close_date.setDate(QDate.currentDate())
        self.close_date.setCalendarPopup(True)
        self.close_date.setStyleSheet("""
            QDateEdit {
                font-size: 12px;
                padding: 8px;
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                background-color: white;
                min-width: 120px;
            }
            QDateEdit:focus {
                border-color: #3498db;
            }
        """)
        self.close_date.dateChanged.connect(self.load_close_data)
        layout.addWidget(self.close_date)
        
        layout.addStretch()
        
        # أزرار العمل
        load_btn = QPushButton("تحميل البيانات")
        load_btn.setStyleSheet(self.get_button_style("#3498db"))
        load_btn.clicked.connect(self.load_close_data)
        layout.addWidget(load_btn)
        
        save_btn = QPushButton("حفظ التقفيل")
        save_btn.setStyleSheet(self.get_button_style("#27ae60"))
        save_btn.clicked.connect(self.save_close)
        layout.addWidget(save_btn)
        
        export_btn = QPushButton("تصدير PDF")
        export_btn.setStyleSheet(self.get_button_style("#e74c3c"))
        export_btn.clicked.connect(self.export_pdf)
        layout.addWidget(export_btn)
        
        return toolbar
    
    def create_summary_panel(self):
        """إنشاء لوحة الملخص"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # عنوان القسم
        section_title = QLabel("ملخص اليوم المالي")
        section_title.setFont(QFont("Arial", 16, QFont.Bold))
        section_title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(section_title)
        
        # بطاقات الإحصائيات
        stats_layout = QGridLayout()
        
        # المبيعات النقدية
        self.cash_sales_card = self.create_stat_card("مبيعات نقدية", "0.00 ر.س", "#27ae60", "💰")
        stats_layout.addWidget(self.cash_sales_card, 0, 0)
        
        # مبيعات البطاقات
        self.card_sales_card = self.create_stat_card("مبيعات البطاقات", "0.00 ر.س", "#3498db", "💳")
        stats_layout.addWidget(self.card_sales_card, 0, 1)
        
        # مبيعات المحافظ الإلكترونية
        self.wallet_sales_card = self.create_stat_card("المحافظ الإلكترونية", "0.00 ر.س", "#9b59b6", "📱")
        stats_layout.addWidget(self.wallet_sales_card, 1, 0)
        
        # إجمالي المبيعات
        self.total_sales_card = self.create_stat_card("إجمالي المبيعات", "0.00 ر.س", "#2c3e50", "📊")
        stats_layout.addWidget(self.total_sales_card, 1, 1)
        
        # إيراد الصيانة
        self.repair_revenue_card = self.create_stat_card("إيراد الصيانة", "0.00 ر.س", "#e67e22", "🔧")
        stats_layout.addWidget(self.repair_revenue_card, 2, 0)
        
        # المرتجعات
        self.returns_card = self.create_stat_card("المرتجعات", "0.00 ر.س", "#e74c3c", "↩️")
        stats_layout.addWidget(self.returns_card, 2, 1)
        
        layout.addLayout(stats_layout)
        
        # صافي الإيراد
        net_frame = QFrame()
        net_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                            stop:0 #27ae60, stop:1 #2ecc71);
                border-radius: 10px;
                padding: 20px;
                margin-top: 15px;
            }
        """)
        net_layout = QVBoxLayout(net_frame)
        
        net_title = QLabel("صافي الإيراد")
        net_title.setFont(QFont("Arial", 14, QFont.Bold))
        net_title.setStyleSheet("color: white;")
        net_title.setAlignment(Qt.AlignCenter)
        net_layout.addWidget(net_title)
        
        self.net_revenue_label = QLabel("0.00 ر.س")
        self.net_revenue_label.setFont(QFont("Arial", 24, QFont.Bold))
        self.net_revenue_label.setStyleSheet("color: white;")
        self.net_revenue_label.setAlignment(Qt.AlignCenter)
        net_layout.addWidget(self.net_revenue_label)
        
        layout.addWidget(net_frame)
        
        return panel
    
    def create_details_panel(self):
        """إنشاء لوحة التفاصيل"""
        panel = QFrame()
        panel.setFrameStyle(QFrame.StyledPanel)
        panel.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 20px;
            }
        """)
        
        layout = QVBoxLayout(panel)
        
        # المصروفات والتعديلات
        expenses_group = QGroupBox("المصروفات والتعديلات")
        expenses_group.setFont(QFont("Arial", 12, QFont.Bold))
        expenses_layout = QGridLayout(expenses_group)
        
        # المصروفات اليومية
        expenses_layout.addWidget(QLabel("المصروفات اليومية:"), 0, 0)
        self.expenses_spin = QDoubleSpinBox()
        self.expenses_spin.setMaximum(999999.99)
        self.expenses_spin.setSuffix(" ر.س")
        self.expenses_spin.valueChanged.connect(self.calculate_totals)
        expenses_layout.addWidget(self.expenses_spin, 0, 1)
        
        # المشتريات
        expenses_layout.addWidget(QLabel("المشتريات:"), 1, 0)
        self.purchases_spin = QDoubleSpinBox()
        self.purchases_spin.setMaximum(999999.99)
        self.purchases_spin.setSuffix(" ر.س")
        self.purchases_spin.valueChanged.connect(self.calculate_totals)
        expenses_layout.addWidget(self.purchases_spin, 1, 1)
        
        # رصيد أول اليوم
        expenses_layout.addWidget(QLabel("رصيد أول اليوم:"), 2, 0)
        self.opening_balance_spin = QDoubleSpinBox()
        self.opening_balance_spin.setMaximum(999999.99)
        self.opening_balance_spin.setSuffix(" ر.س")
        self.opening_balance_spin.valueChanged.connect(self.calculate_totals)
        expenses_layout.addWidget(self.opening_balance_spin, 2, 1)
        
        layout.addWidget(expenses_group)
        
        # النتائج المحاسبية
        results_group = QGroupBox("النتائج المحاسبية")
        results_group.setFont(QFont("Arial", 12, QFont.Bold))
        results_layout = QGridLayout(results_group)
        
        # صافي الربح
        results_layout.addWidget(QLabel("صافي الربح:"), 0, 0)
        self.net_profit_label = QLabel("0.00 ر.س")
        self.net_profit_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.net_profit_label.setStyleSheet("color: #27ae60;")
        results_layout.addWidget(self.net_profit_label, 0, 1)
        
        # رصيد آخر اليوم
        results_layout.addWidget(QLabel("رصيد آخر اليوم:"), 1, 0)
        self.closing_balance_label = QLabel("0.00 ر.س")
        self.closing_balance_label.setFont(QFont("Arial", 12, QFont.Bold))
        self.closing_balance_label.setStyleSheet("color: #2c3e50;")
        results_layout.addWidget(self.closing_balance_label, 1, 1)
        
        layout.addWidget(results_group)
        
        # الملاحظات
        notes_group = QGroupBox("ملاحظات التقفيل")
        notes_group.setFont(QFont("Arial", 12, QFont.Bold))
        notes_layout = QVBoxLayout(notes_group)
        
        self.notes_edit = QTextEdit()
        self.notes_edit.setPlaceholderText("أدخل أي ملاحظات إضافية للتقفيل...")
        self.notes_edit.setMaximumHeight(100)
        self.notes_edit.setStyleSheet("""
            QTextEdit {
                border: 2px solid #bdc3c7;
                border-radius: 5px;
                padding: 10px;
                font-size: 11px;
            }
            QTextEdit:focus {
                border-color: #3498db;
            }
        """)
        notes_layout.addWidget(self.notes_edit)
        
        layout.addWidget(notes_group)
        
        # رفع المرفقات
        attachments_group = QGroupBox("المرفقات")
        attachments_group.setFont(QFont("Arial", 12, QFont.Bold))
        attachments_layout = QVBoxLayout(attachments_group)
        
        upload_btn = QPushButton("رفع صور الإيصالات")
        upload_btn.setStyleSheet(self.get_button_style("#9b59b6"))
        upload_btn.clicked.connect(self.upload_attachments)
        attachments_layout.addWidget(upload_btn)
        
        self.attachments_list = QLabel("لا توجد مرفقات")
        self.attachments_list.setStyleSheet("color: #7f8c8d; font-style: italic;")
        attachments_layout.addWidget(self.attachments_list)
        
        layout.addWidget(attachments_group)
        
        layout.addStretch()
        
        return panel
    
    def create_stat_card(self, title, value, color, icon=""):
        """إنشاء بطاقة إحصائية"""
        card = QFrame()
        card.setFrameStyle(QFrame.StyledPanel)
        card.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
                min-height: 80px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(card)
        layout.setSpacing(5)
        
        # العنوان مع الأيقونة
        header_layout = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 16))
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 10, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # القيمة
        value_label = QLabel(value)
        value_label.setFont(QFont("Arial", 14, QFont.Bold))
        value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(value_label)
        
        # حفظ مرجع للقيمة للتحديث لاحقاً
        card.value_label = value_label
        
        return card
    
    def create_status_bar(self):
        """إنشاء شريط الحالة"""
        status_bar = QFrame()
        status_bar.setFrameStyle(QFrame.StyledPanel)
        status_bar.setStyleSheet("""
            QFrame {
                background-color: #34495e;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        
        layout = QHBoxLayout(status_bar)
        
        self.status_label = QLabel("جاهز")
        self.status_label.setStyleSheet("color: white; font-weight: bold;")
        layout.addWidget(self.status_label)
        
        layout.addStretch()
        
        # معلومات آخر حفظ
        self.last_save_label = QLabel("")
        self.last_save_label.setStyleSheet("color: #bdc3c7;")
        layout.addWidget(self.last_save_label)
        
        return status_bar
    
    def get_button_style(self, color):
        """الحصول على نمط الأزرار"""
        return f"""
            QPushButton {{
                background-color: {color};
                color: white;
                border: none;
                border-radius: 8px;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 12px;
                min-width: 100px;
            }}
            QPushButton:hover {{
                background-color: {self.darken_color(color)};
            }}
            QPushButton:pressed {{
                background-color: {self.darken_color(color, 0.8)};
            }}
        """
    
    def darken_color(self, hex_color, factor=0.9):
        """تغميق اللون"""
        color = QColor(hex_color)
        return color.darker(int(100/factor)).name()
    
    def refresh_data(self):
        """تحديث البيانات"""
        self.load_close_data()
    
    def load_close_data(self):
        """تحميل بيانات التقفيل"""
        try:
            selected_date = self.close_date.date().toString("yyyy-MM-dd")
            self.status_label.setText(f"جاري تحميل بيانات {selected_date}...")
            
            # الحصول على بيانات التقفيل من الخدمة
            close_data = self.main_window.report_service.get_daily_close_report(selected_date)
            
            if close_data:
                self.current_close_data = close_data
                self.display_close_data(close_data)
                self.status_label.setText(f"تم تحميل بيانات {selected_date}")
            else:
                self.clear_display()
                self.status_label.setText(f"لا توجد بيانات للتاريخ {selected_date}")
                
        except Exception as e:
            logger.error(f"خطأ في تحميل بيانات التقفيل: {str(e)}")
            QMessageBox.critical(
                self, "خطأ", 
                f"فشل في تحميل بيانات التقفيل:\n{str(e)}"
            )
            self.status_label.setText("خطأ في التحميل")
    
    def display_close_data(self, data):
        """عرض بيانات التقفيل"""
        # تحديث البطاقات
        self.cash_sales_card.value_label.setText(f"{data.get('cash_sales', 0):.2f} ر.س")
        self.card_sales_card.value_label.setText(f"{data.get('card_sales', 0):.2f} ر.س")
        self.wallet_sales_card.value_label.setText(f"{data.get('wallet_sales', 0):.2f} ر.س")
        self.total_sales_card.value_label.setText(f"{data.get('total_sales', 0):.2f} ر.س")
        self.repair_revenue_card.value_label.setText(f"{data.get('repair_revenue', 0):.2f} ر.س")
        self.returns_card.value_label.setText(f"{data.get('returns', 0):.2f} ر.س")
        
        # تحديث صافي الإيراد
        net_revenue = data.get('total_revenue', 0)
        self.net_revenue_label.setText(f"{net_revenue:.2f} ر.س")
        
        # تحديث المدخلات
        self.expenses_spin.setValue(data.get('expenses', 0))
        self.purchases_spin.setValue(data.get('purchases', 0))
        self.opening_balance_spin.setValue(data.get('opening_balance', 0))
        
        # تحديث الملاحظات
        self.notes_edit.setPlainText(data.get('notes', ''))
        
        # حساب الإجماليات
        self.calculate_totals()
    
    def clear_display(self):
        """مسح العرض"""
        # مسح البطاقات
        cards = [
            self.cash_sales_card, self.card_sales_card, self.wallet_sales_card,
            self.total_sales_card, self.repair_revenue_card, self.returns_card
        ]
        
        for card in cards:
            card.value_label.setText("0.00 ر.س")
        
        self.net_revenue_label.setText("0.00 ر.س")
        
        # مسح المدخلات
        self.expenses_spin.setValue(0)
        self.purchases_spin.setValue(0)
        self.opening_balance_spin.setValue(0)
        self.notes_edit.clear()
        
        # مسح النتائج
        self.net_profit_label.setText("0.00 ر.س")
        self.closing_balance_label.setText("0.00 ر.س")
        
        self.current_close_data = None
    
    def calculate_totals(self):
        """حساب الإجماليات"""
        if not self.current_close_data:
            return
        
        try:
            # الإيرادات
            total_revenue = self.current_close_data.get('total_revenue', 0)
            
            # المصروفات
            expenses = self.expenses_spin.value()
            purchases = self.purchases_spin.value()
            returns = self.current_close_data.get('returns', 0)
            
            # صافي الربح
            net_profit = total_revenue - expenses - purchases - returns
            
            # الأرصدة
            opening_balance = self.opening_balance_spin.value()
            closing_balance = opening_balance + net_profit
            
            # تحديث العرض
            self.net_profit_label.setText(f"{net_profit:.2f} ر.س")
            self.closing_balance_label.setText(f"{closing_balance:.2f} ر.س")
            
            # تلوين صافي الربح
            if net_profit >= 0:
                self.net_profit_label.setStyleSheet("color: #27ae60; font-weight: bold;")
            else:
                self.net_profit_label.setStyleSheet("color: #e74c3c; font-weight: bold;")
                
        except Exception as e:
            logger.error(f"خطأ في حساب الإجماليات: {str(e)}")
    
    def save_close(self):
        """حفظ التقفيل"""
        if not self.current_close_data:
            QMessageBox.warning(
                self, "تحذير",
                "لا توجد بيانات للحفظ. يرجى تحميل البيانات أولاً."
            )
            return
        
        try:
            # إعداد بيانات الحفظ
            close_date = self.close_date.date().toString("yyyy-MM-dd")
            
            save_data = {
                'close_date': close_date,
                'cash_sales': self.current_close_data.get('cash_sales', 0),
                'card_sales': self.current_close_data.get('card_sales', 0),
                'wallet_sales': self.current_close_data.get('wallet_sales', 0),
                'total_sales': self.current_close_data.get('total_sales', 0),
                'expenses': self.expenses_spin.value(),
                'purchases': self.purchases_spin.value(),
                'returns': self.current_close_data.get('returns', 0),
                'net_profit': float(self.net_profit_label.text().replace(' ر.س', '')),
                'opening_balance': self.opening_balance_spin.value(),
                'closing_balance': float(self.closing_balance_label.text().replace(' ر.س', '')),
                'notes': self.notes_edit.toPlainText().strip()
            }
            
            # حفظ البيانات
            success = self.main_window.report_service.save_daily_close(save_data)
            
            if success:
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ تقفيل يوم {close_date} بنجاح"
                )
                
                # تحديث شريط الحالة
                now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                self.last_save_label.setText(f"آخر حفظ: {now}")
                self.status_label.setText("تم الحفظ بنجاح")
                
            else:
                QMessageBox.critical(
                    self, "خطأ",
                    "فشل في حفظ بيانات التقفيل"
                )
                
        except Exception as e:
            logger.error(f"خطأ في حفظ التقفيل: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في حفظ التقفيل:\n{str(e)}"
            )
    
    def export_pdf(self):
        """تصدير التقفيل إلى PDF"""
        if not self.current_close_data:
            QMessageBox.warning(
                self, "تحذير",
                "لا توجد بيانات للتصدير. يرجى تحميل البيانات أولاً."
            )
            return
        
        try:
            close_date = self.close_date.date().toString("yyyy-MM-dd")
            timestamp = datetime.now().strftime("%H%M%S")
            filename = f"daily_close_{close_date}_{timestamp}.pdf"
            filepath = f"reports/daily/{filename}"
            
            # إنشاء مجلد التقارير إذا لم يكن موجوداً
            os.makedirs("reports/daily", exist_ok=True)
            
            # إعداد بيانات التقرير
            report_data = {
                'close_date': close_date,
                'cash_sales': self.current_close_data.get('cash_sales', 0),
                'card_sales': self.current_close_data.get('card_sales', 0),
                'wallet_sales': self.current_close_data.get('wallet_sales', 0),
                'total_sales': self.current_close_data.get('total_sales', 0),
                'repair_revenue': self.current_close_data.get('repair_revenue', 0),
                'returns': self.current_close_data.get('returns', 0),
                'total_revenue': self.current_close_data.get('total_revenue', 0),
                'expenses': self.expenses_spin.value(),
                'purchases': self.purchases_spin.value(),
                'net_profit': float(self.net_profit_label.text().replace(' ر.س', '')),
                'opening_balance': self.opening_balance_spin.value(),
                'closing_balance': float(self.closing_balance_label.text().replace(' ر.س', '')),
                'notes': self.notes_edit.toPlainText().strip()
            }
            
            # إنتاج تقرير PDF
            success = self.pdf_generator.generate_daily_close_report(report_data, filepath)
            
            if success:
                QMessageBox.information(
                    self, "نجح",
                    f"تم حفظ تقرير التقفيل في:\n{filepath}"
                )
                
                # فتح الملف
                import subprocess
                import sys
                
                if sys.platform.startswith('win'):
                    os.startfile(filepath)
                elif sys.platform.startswith('darwin'):
                    subprocess.run(['open', filepath])
                else:
                    subprocess.run(['xdg-open', filepath])
                    
                self.status_label.setText("تم تصدير التقرير")
                
            else:
                QMessageBox.critical(
                    self, "خطأ",
                    "فشل في إنتاج تقرير PDF"
                )
                
        except Exception as e:
            logger.error(f"خطأ في تصدير PDF: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في التصدير:\n{str(e)}"
            )
    
    def upload_attachments(self):
        """رفع المرفقات"""
        try:
            file_dialog = QFileDialog()
            files, _ = file_dialog.getOpenFileNames(
                self,
                "اختيار صور الإيصالات",
                "",
                "صور (*.png *.jpg *.jpeg *.gif *.bmp);;جميع الملفات (*)"
            )
            
            if files:
                # إنشاء مجلد المرفقات
                attachments_dir = "reports/daily/attachments"
                os.makedirs(attachments_dir, exist_ok=True)
                
                uploaded_files = []
                close_date = self.close_date.date().toString("yyyy-MM-dd")
                
                for file_path in files:
                    # نسخ الملف إلى مجلد المرفقات
                    import shutil
                    filename = os.path.basename(file_path)
                    new_filename = f"{close_date}_{filename}"
                    new_path = os.path.join(attachments_dir, new_filename)
                    
                    shutil.copy2(file_path, new_path)
                    uploaded_files.append(new_filename)
                
                # تحديث قائمة المرفقات
                if uploaded_files:
                    files_text = "\n".join([f"• {f}" for f in uploaded_files])
                    self.attachments_list.setText(files_text)
                    self.attachments_list.setStyleSheet("color: #27ae60;")
                    
                    QMessageBox.information(
                        self, "نجح",
                        f"تم رفع {len(uploaded_files)} ملف بنجاح"
                    )
                    
                    self.status_label.setText(f"تم رفع {len(uploaded_files)} مرفق")
                
        except Exception as e:
            logger.error(f"خطأ في رفع المرفقات: {str(e)}")
            QMessageBox.critical(
                self, "خطأ",
                f"حدث خطأ في رفع المرفقات:\n{str(e)}"
            )
