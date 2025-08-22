#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
لوحة التحكم الرئيسية - Dashboard
"""

from PySide6.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QGridLayout,
                              QLabel, QPushButton, QFrame, QScrollArea,
                              QTableWidget, QTableWidgetItem, QProgressBar,
                              QMessageBox)
from PySide6.QtCore import Qt, QTimer
from PySide6.QtGui import QFont, QColor, QPalette
from datetime import datetime, date, timedelta
import logging

logger = logging.getLogger(__name__)


class DashboardWidget(QFrame):
    """ويدجت عنصر لوحة التحكم"""
    
    def __init__(self, title, value, icon="", color="#3498db"):
        super().__init__()
        self.setup_ui(title, value, icon, color)
    
    def setup_ui(self, title, value, icon, color):
        """إعداد واجهة العنصر"""
        self.setFrameStyle(QFrame.StyledPanel)
        self.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 10px;
                padding: 15px;
                margin: 5px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QVBoxLayout(self)
        layout.setContentsMargins(15, 15, 15, 15)
        
        # الأيقونة والعنوان
        header_layout = QHBoxLayout()
        
        if icon:
            icon_label = QLabel(icon)
            icon_label.setFont(QFont("Arial", 24))
            header_layout.addWidget(icon_label)
        
        title_label = QLabel(title)
        title_label.setFont(QFont("Arial", 12, QFont.Bold))
        header_layout.addWidget(title_label)
        header_layout.addStretch()
        
        layout.addLayout(header_layout)
        
        # القيمة
        self.value_label = QLabel(str(value))
        self.value_label.setFont(QFont("Arial", 20, QFont.Bold))
        self.value_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.value_label)
        
        layout.addStretch()
    
    def update_value(self, value):
        """تحديث القيمة"""
        self.value_label.setText(str(value))


class Dashboard(QWidget):
    """لوحة التحكم الرئيسية"""
    
    def __init__(self, main_window):
        super().__init__()
        self.main_window = main_window
        self.setup_ui()
        self.setup_refresh_timer()
    
    def setup_ui(self):
        """إعداد واجهة المستخدم"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(20)
        
        # عنوان اللوحة
        title_label = QLabel("لوحة التحكم")
        title_label.setFont(QFont("Arial", 24, QFont.Bold))
        title_label.setAlignment(Qt.AlignCenter)
        title_label.setStyleSheet("color: #2c3e50; margin-bottom: 20px;")
        layout.addWidget(title_label)
        
        # منطقة التمرير
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setStyleSheet("QScrollArea { border: none; }")
        
        scroll_widget = QWidget()
        scroll_layout = QVBoxLayout(scroll_widget)
        scroll_layout.setSpacing(20)
        
        # الإحصائيات السريعة
        self.setup_quick_stats(scroll_layout)
        
        # التنبيهات
        self.setup_alerts(scroll_layout)
        
        # الأنشطة الأخيرة
        self.setup_recent_activities(scroll_layout)
        
        # الأزرار السريعة
        self.setup_quick_actions(scroll_layout)
        
        scroll_area.setWidget(scroll_widget)
        layout.addWidget(scroll_area)
    
    def setup_quick_stats(self, layout):
        """إعداد الإحصائيات السريعة"""
        stats_frame = QFrame()
        stats_frame.setFrameStyle(QFrame.StyledPanel)
        stats_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        stats_layout = QVBoxLayout(stats_frame)
        
        # عنوان القسم
        stats_title = QLabel("الإحصائيات اليومية")
        stats_title.setFont(QFont("Arial", 16, QFont.Bold))
        stats_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        stats_layout.addWidget(stats_title)
        
        # شبكة الإحصائيات
        stats_grid = QGridLayout()
        
        # إنشاء عناصر الإحصائيات
        self.sales_widget = DashboardWidget("المبيعات اليوم", "0 ر.س", "💰", "#27ae60")
        self.transactions_widget = DashboardWidget("عدد المعاملات", "0", "🧾", "#3498db")
        self.repair_tickets_widget = DashboardWidget("تذاكر الصيانة", "0", "🔧", "#e67e22")
        self.low_stock_widget = DashboardWidget("مخزون منخفض", "0", "📦", "#e74c3c")
        
        # إضافة العناصر للشبكة
        stats_grid.addWidget(self.sales_widget, 0, 0)
        stats_grid.addWidget(self.transactions_widget, 0, 1)
        stats_grid.addWidget(self.repair_tickets_widget, 1, 0)
        stats_grid.addWidget(self.low_stock_widget, 1, 1)
        
        stats_layout.addLayout(stats_grid)
        layout.addWidget(stats_frame)
    
    def setup_alerts(self, layout):
        """إعداد التنبيهات"""
        alerts_frame = QFrame()
        alerts_frame.setFrameStyle(QFrame.StyledPanel)
        alerts_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        alerts_layout = QVBoxLayout(alerts_frame)
        
        # عنوان القسم
        alerts_title = QLabel("التنبيهات")
        alerts_title.setFont(QFont("Arial", 16, QFont.Bold))
        alerts_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        alerts_layout.addWidget(alerts_title)
        
        # منطقة التنبيهات
        self.alerts_container = QVBoxLayout()
        alerts_layout.addLayout(self.alerts_container)
        
        layout.addWidget(alerts_frame)
    
    def setup_recent_activities(self, layout):
        """إعداد الأنشطة الأخيرة"""
        activities_frame = QFrame()
        activities_frame.setFrameStyle(QFrame.StyledPanel)
        activities_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        activities_layout = QVBoxLayout(activities_frame)
        
        # عنوان القسم
        activities_title = QLabel("النشاط الأخير")
        activities_title.setFont(QFont("Arial", 16, QFont.Bold))
        activities_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        activities_layout.addWidget(activities_title)
        
        # جدول الأنشطة
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(3)
        self.activities_table.setHorizontalHeaderLabels(["الوقت", "النوع", "التفاصيل"])
        self.activities_table.horizontalHeader().setStretchLastSection(True)
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setMaximumHeight(200)
        
        activities_layout.addWidget(self.activities_table)
        layout.addWidget(activities_frame)
    
    def setup_quick_actions(self, layout):
        """إعداد الأزرار السريعة"""
        actions_frame = QFrame()
        actions_frame.setFrameStyle(QFrame.StyledPanel)
        actions_frame.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 10px;
                padding: 15px;
            }
        """)
        
        actions_layout = QVBoxLayout(actions_frame)
        
        # عنوان القسم
        actions_title = QLabel("إجراءات سريعة")
        actions_title.setFont(QFont("Arial", 16, QFont.Bold))
        actions_title.setStyleSheet("color: #2c3e50; margin-bottom: 10px;")
        actions_layout.addWidget(actions_title)
        
        # شبكة الأزرار
        buttons_grid = QGridLayout()
        
        # إنشاء الأزرار
        buttons = [
            ("فاتورة جديدة", self.main_window.show_pos, "#27ae60"),
            ("تذكرة صيانة", self.main_window.show_repair, "#e67e22"),
            ("إضافة منتج", self.add_product, "#3498db"),
            ("تقفيل يومي", self.main_window.show_daily_close, "#9b59b6")
        ]
        
        for i, (text, callback, color) in enumerate(buttons):
            button = QPushButton(text)
            button.setFont(QFont("Arial", 12, QFont.Bold))
            button.setStyleSheet(f"""
                QPushButton {{
                    background-color: {color};
                    color: white;
                    border: none;
                    border-radius: 8px;
                    padding: 15px;
                    font-weight: bold;
                }}
                QPushButton:hover {{
                    background-color: {self.darken_color(color)};
                }}
                QPushButton:pressed {{
                    background-color: {self.darken_color(color, 0.8)};
                }}
            """)
            button.clicked.connect(callback)
            
            row = i // 2
            col = i % 2
            buttons_grid.addWidget(button, row, col)
        
        actions_layout.addLayout(buttons_grid)
        layout.addWidget(actions_frame)
    
    def setup_refresh_timer(self):
        """إعداد مؤقت التحديث التلقائي"""
        self.refresh_timer = QTimer()
        self.refresh_timer.timeout.connect(self.refresh_data)
        self.refresh_timer.start(30000)  # تحديث كل 30 ثانية
    
    def darken_color(self, hex_color, factor=0.9):
        """تغميق اللون"""
        color = QColor(hex_color)
        return color.darker(int(100/factor)).name()
    
    def refresh_data(self):
        """تحديث بيانات اللوحة"""
        try:
            self.update_daily_stats()
            self.update_alerts()
            self.update_recent_activities()
        except Exception as e:
            logger.error(f"خطأ في تحديث بيانات اللوحة: {str(e)}")
    
    def update_daily_stats(self):
        """تحديث الإحصائيات اليومية"""
        try:
            today = date.today().isoformat()
            
            # إحصائيات المبيعات
            sales_summary = self.main_window.pos_service.get_daily_sales_summary(today)
            total_sales = sales_summary.get('total_amount', 0)
            total_transactions = sales_summary.get('total_transactions', 0)
            
            self.sales_widget.update_value(f"{total_sales:.0f} ر.س")
            self.transactions_widget.update_value(str(total_transactions))
            
            # إحصائيات الصيانة
            repair_summary = self.main_window.repair_service.get_repair_summary(today, today)
            open_tickets = repair_summary.get('received_tickets', 0) + repair_summary.get('in_progress_tickets', 0)
            
            self.repair_tickets_widget.update_value(str(open_tickets))
            
            # المخزون المنخفض
            low_stock = self.main_window.inventory_service.get_low_stock_products()
            self.low_stock_widget.update_value(str(len(low_stock)))
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الإحصائيات: {str(e)}")
    
    def update_alerts(self):
        """تحديث التنبيهات"""
        try:
            # مسح التنبيهات السابقة
            for i in reversed(range(self.alerts_container.count())):
                widget = self.alerts_container.itemAt(i).widget()
                if widget:
                    widget.setParent(None)
            
            alerts = []
            
            # تنبيهات المخزون المنخفض
            low_stock = self.main_window.inventory_service.get_low_stock_products()
            if low_stock:
                alerts.append({
                    'type': 'warning',
                    'message': f"يوجد {len(low_stock)} منتج بمخزون منخفض",
                    'action': self.main_window.show_inventory
                })
            
            # تنبيهات الصيانة المتأخرة
            today = date.today()
            week_ago = (today - timedelta(days=7)).isoformat()
            old_repairs = self.main_window.repair_service.get_repair_tickets(
                status='in_progress',
                start_date=week_ago,
                end_date=today.isoformat()
            )
            
            if old_repairs:
                alerts.append({
                    'type': 'error',
                    'message': f"يوجد {len(old_repairs)} تذكرة صيانة متأخرة (أكثر من أسبوع)",
                    'action': self.main_window.show_repair
                })
            
            # عرض التنبيهات
            if not alerts:
                no_alerts = QLabel("لا توجد تنبيهات")
                no_alerts.setStyleSheet("color: #27ae60; font-style: italic;")
                self.alerts_container.addWidget(no_alerts)
            else:
                for alert in alerts:
                    self.add_alert(alert)
                    
        except Exception as e:
            logger.error(f"خطأ في تحديث التنبيهات: {str(e)}")
    
    def add_alert(self, alert):
        """إضافة تنبيه"""
        alert_frame = QFrame()
        alert_frame.setFrameStyle(QFrame.StyledPanel)
        
        color = "#e74c3c" if alert['type'] == 'error' else "#f39c12"
        alert_frame.setStyleSheet(f"""
            QFrame {{
                background-color: {color};
                border-radius: 5px;
                padding: 10px;
                margin: 2px;
            }}
            QLabel {{
                color: white;
                border: none;
            }}
        """)
        
        layout = QHBoxLayout(alert_frame)
        
        # رمز التنبيه
        icon = "⚠️" if alert['type'] == 'warning' else "❌"
        icon_label = QLabel(icon)
        layout.addWidget(icon_label)
        
        # رسالة التنبيه
        message_label = QLabel(alert['message'])
        message_label.setFont(QFont("Arial", 10))
        layout.addWidget(message_label)
        
        layout.addStretch()
        
        # زر العمل
        if alert.get('action'):
            action_button = QPushButton("عرض")
            action_button.setStyleSheet("""
                QPushButton {
                    background-color: rgba(255, 255, 255, 0.2);
                    color: white;
                    border: 1px solid white;
                    border-radius: 3px;
                    padding: 5px 10px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: rgba(255, 255, 255, 0.3);
                }
            """)
            action_button.clicked.connect(alert['action'])
            layout.addWidget(action_button)
        
        self.alerts_container.addWidget(alert_frame)
    
    def update_recent_activities(self):
        """تحديث الأنشطة الأخيرة"""
        try:
            # الحصول على آخر الأنشطة
            activities = []
            
            # آخر المبيعات
            recent_sales = self.main_window.pos_service.get_recent_sales(5)
            for sale in recent_sales:
                activities.append({
                    'time': sale['created_at'],
                    'type': 'مبيعات',
                    'details': f"فاتورة #{sale['id']} - {sale['final_amount']:.0f} ر.س"
                })
            
            # آخر تذاكر الصيانة
            recent_repairs = self.main_window.repair_service.get_repair_tickets(limit=5)
            for repair in recent_repairs:
                activities.append({
                    'time': repair['received_date'],
                    'type': 'صيانة',
                    'details': f"تذكرة #{repair['id']} - {repair['device_info']}"
                })
            
            # ترتيب حسب الوقت
            activities.sort(key=lambda x: x['time'], reverse=True)
            activities = activities[:10]  # أحدث 10 أنشطة
            
            # تحديث الجدول
            self.activities_table.setRowCount(len(activities))
            
            for row, activity in enumerate(activities):
                # تنسيق الوقت
                try:
                    time_obj = datetime.fromisoformat(activity['time'].replace('Z', '+00:00'))
                    time_str = time_obj.strftime("%H:%M")
                except:
                    time_str = activity['time'][:10]
                
                self.activities_table.setItem(row, 0, QTableWidgetItem(time_str))
                self.activities_table.setItem(row, 1, QTableWidgetItem(activity['type']))
                self.activities_table.setItem(row, 2, QTableWidgetItem(activity['details']))
            
        except Exception as e:
            logger.error(f"خطأ في تحديث الأنشطة: {str(e)}")
    
    def add_product(self):
        """فتح نافذة إضافة منتج"""
        self.main_window.show_inventory()
        # يمكن إضافة كود لفتح نافذة إضافة منتج مباشرة
