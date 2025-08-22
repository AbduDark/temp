
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
إعدادات التطبيق - Application Settings
"""

import os
from pathlib import Path

# مسار التطبيق الأساسي
BASE_DIR = Path(__file__).parent.parent

# إعدادات التطبيق الأساسية
APP_CONFIG = {
    'app_name': 'نظام إدارة محل الموبايلات',
    'version': '1.0.0',
    'organization': 'Mobile Shop Management',
    'author': 'Mobile Shop Team',
    'description': 'نظام شامل لإدارة محلات الموبايلات والاكسسوارات'
}

# إعدادات قاعدة البيانات
DATABASE_CONFIG = {
    'db_path': BASE_DIR / 'data' / 'mobile_shop.db',
    'backup_path': BASE_DIR / 'backup',
    'backup_retention_days': 30,
    'auto_backup_enabled': True,
    'auto_backup_interval_hours': 24
}

# إعدادات واجهة المستخدم
UI_CONFIG = {
    'theme': 'light',
    'language': 'ar',
    'font_family': 'Arial',
    'font_size': 10,
    'window_width': 1200,
    'window_height': 800,
    'sidebar_width': 250,
    'rtl_layout': True
}

# إعدادات النظام
SYSTEM_CONFIG = {
    'log_level': 'INFO',
    'log_max_size_mb': 10,
    'log_backup_count': 5,
    'session_timeout_minutes': 60,
    'max_login_attempts': 3,
    'password_min_length': 6
}

# إعدادات المحل الافتراضية
SHOP_DEFAULTS = {
    'name': 'محل الموبايلات',
    'address': 'الرياض، المملكة العربية السعودية',
    'phone': '+966-XX-XXX-XXXX',
    'email': 'info@mobileshop.com',
    'currency': 'SAR',
    'tax_rate': 15.0,
    'receipt_footer': 'شكراً لزيارتكم - نتطلع لخدمتكم مرة أخرى'
}

# إعدادات الطباعة
PRINT_CONFIG = {
    'receipt_width': 80,  # عدد الأحرف
    'auto_print': False,
    'printer_name': None,
    'paper_size': 'A4',
    'margin_top': 10,
    'margin_bottom': 10,
    'margin_left': 10,
    'margin_right': 10
}

# إعدادات التقارير
REPORTS_CONFIG = {
    'output_path': BASE_DIR / 'reports',
    'daily_reports_path': BASE_DIR / 'reports' / 'daily',
    'monthly_reports_path': BASE_DIR / 'reports' / 'monthly',
    'export_formats': ['PDF', 'Excel', 'CSV'],
    'auto_generate_daily': True,
    'report_retention_days': 365
}

# إعدادات الأمان
SECURITY_CONFIG = {
    'bcrypt_rounds': 12,
    'session_secret_key': os.urandom(32).hex(),
    'encryption_key': None,  # سيتم إنشاؤها عند الحاجة
    'audit_log_enabled': True,
    'backup_encryption': False
}

# مسارات الملفات والمجلدات
PATHS = {
    'data': BASE_DIR / 'data',
    'logs': BASE_DIR / 'logs',
    'assets': BASE_DIR / 'assets',
    'icons': BASE_DIR / 'assets' / 'icons',
    'reports': BASE_DIR / 'reports',
    'backup': BASE_DIR / 'backup',
    'temp': BASE_DIR / 'temp',
    'exports': BASE_DIR / 'exports'
}

# إعدادات قوائم المنتجات
PRODUCT_CONFIG = {
    'barcode_length': 13,
    'auto_generate_barcode': True,
    'low_stock_threshold': 5,
    'track_serial_numbers': True,
    'enable_batch_tracking': False,
    'price_decimal_places': 2
}

# إعدادات نقطة البيع
POS_CONFIG = {
    'auto_calculate_tax': True,
    'allow_discount': True,
    'max_discount_percent': 50.0,
    'require_customer_info': False,
    'print_receipt_auto': False,
    'cash_drawer_enabled': False,
    'barcode_scanner_enabled': True
}

# إعدادات الصيانة
REPAIR_CONFIG = {
    'ticket_number_prefix': 'RPR',
    'auto_generate_ticket_number': True,
    'default_warranty_days': 30,
    'sms_notifications': False,
    'email_notifications': False,
    'status_colors': {
        'pending': '#f39c12',
        'in_progress': '#3498db',
        'completed': '#27ae60',
        'delivered': '#2c3e50',
        'cancelled': '#e74c3c'
    }
}

# قوائم الخيارات
CHOICES = {
    'currencies': [
        ('SAR', 'الريال السعودي'),
        ('EGP', 'الجنيه المصري'),
        ('USD', 'الدولار الأمريكي'),
        ('EUR', 'اليورو')
    ],
    
    'user_roles': [
        ('Admin', 'مدير النظام'),
        ('Manager', 'مدير'),
        ('Cashier', 'كاشير'),
        ('Technician', 'فني صيانة'),
        ('Viewer', 'مشاهد')
    ],
    
    'payment_methods': [
        ('cash', 'نقدي'),
        ('card', 'بطاقة ائتمان'),
        ('transfer', 'تحويل بنكي'),
        ('installment', 'تقسيط')
    ],
    
    'repair_statuses': [
        ('pending', 'في الانتظار'),
        ('diagnosed', 'تم التشخيص'),
        ('parts_ordered', 'طلب قطع الغيار'),
        ('in_repair', 'قيد الإصلاح'),
        ('testing', 'قيد الاختبار'),
        ('completed', 'مكتمل'),
        ('ready_delivery', 'جاهز للتسليم'),
        ('delivered', 'تم التسليم'),
        ('cancelled', 'ملغي')
    ],
    
    'product_conditions': [
        ('new', 'جديد'),
        ('used_excellent', 'مستعمل ممتاز'),
        ('used_good', 'مستعمل جيد'),
        ('used_fair', 'مستعمل متوسط'),
        ('refurbished', 'مجدد')
    ]
}

# رسائل النظام
MESSAGES = {
    'success': {
        'save': 'تم الحفظ بنجاح',
        'update': 'تم التحديث بنجاح',
        'delete': 'تم الحذف بنجاح',
        'login': 'تم تسجيل الدخول بنجاح',
        'logout': 'تم تسجيل الخروج بنجاح'
    },
    
    'error': {
        'save': 'فشل في الحفظ',
        'update': 'فشل في التحديث',
        'delete': 'فشل في الحذف',
        'login': 'فشل في تسجيل الدخول',
        'connection': 'خطأ في الاتصال بقاعدة البيانات',
        'permission': 'ليس لديك صلاحية للوصول',
        'validation': 'خطأ في التحقق من البيانات'
    },
    
    'warning': {
        'unsaved_changes': 'يوجد تغييرات غير محفوظة. هل تريد المتابعة؟',
        'delete_confirm': 'هل أنت متأكد من الحذف؟',
        'low_stock': 'تنبيه: المخزون منخفض',
        'session_expire': 'انتهت صلاحية الجلسة. يرجى تسجيل الدخول مرة أخرى'
    }
}

# إعدادات التطوير
DEBUG_CONFIG = {
    'debug_mode': False,
    'show_sql_queries': False,
    'enable_profiling': False,
    'mock_data_enabled': False,
    'test_mode': False
}

def get_setting(key: str, default=None):
    """الحصول على إعداد من النظام"""
    # يمكن توسيع هذه الدالة لقراءة الإعدادات من قاعدة البيانات
    return default

def update_setting(key: str, value):
    """تحديث إعداد في النظام"""
    # يمكن توسيع هذه الدالة لحفظ الإعدادات في قاعدة البيانات
    pass

def create_required_directories():
    """إنشاء المجلدات المطلوبة"""
    for path in PATHS.values():
        if isinstance(path, Path):
            path.mkdir(parents=True, exist_ok=True)

# إنشاء المجلدات عند تحميل الوحدة
create_required_directories()
