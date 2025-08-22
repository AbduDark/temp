
#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
دوال مساعدة - Helper Functions
"""

import re
import random
import string
from typing import Union

def format_currency(amount: Union[int, float], currency: str = "SAR") -> str:
    """تنسيق العملة"""
    try:
        if currency == "SAR":
            return f"{amount:,.2f} ر.س"
        elif currency == "EGP":
            return f"{amount:,.2f} ج.م"
        elif currency == "USD":
            return f"${amount:,.2f}"
        else:
            return f"{amount:,.2f} {currency}"
    except (ValueError, TypeError):
        return "0.00"

def validate_email(email: str) -> bool:
    """التحقق من صحة البريد الإلكتروني"""
    if not email:
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def generate_barcode(length: int = 12) -> str:
    """توليد باركود عشوائي"""
    # توليد رقم عشوائي بالطول المحدد
    digits = ''.join(random.choices(string.digits, k=length-1))
    
    # حساب رقم التحقق (checksum) للـ EAN-13
    if length == 13:
        checksum = 0
        for i, digit in enumerate(digits):
            if i % 2 == 0:
                checksum += int(digit)
            else:
                checksum += int(digit) * 3
        
        check_digit = (10 - (checksum % 10)) % 10
        return digits + str(check_digit)
    
    return digits + str(random.randint(0, 9))

def validate_phone(phone: str) -> bool:
    """التحقق من صحة رقم الهاتف"""
    if not phone:
        return False
    
    # إزالة المسافات والرموز
    clean_phone = re.sub(r'[^\d+]', '', phone)
    
    # التحقق من الأرقام السعودية والمصرية
    patterns = [
        r'^\+966[5-9]\d{8}$',  # السعودية
        r'^966[5-9]\d{8}$',    # السعودية بدون +
        r'^05[0-9]\d{7}$',     # السعودية محلي
        r'^\+20[1-9]\d{8,9}$', # مصر
        r'^20[1-9]\d{8,9}$',   # مصر بدون +
        r'^01[0-9]\d{8}$',     # مصر محلي
    ]
    
    return any(re.match(pattern, clean_phone) for pattern in patterns)

def format_file_size(size_bytes: int) -> str:
    """تنسيق حجم الملف"""
    if size_bytes == 0:
        return "0 بايت"
    
    size_names = ["بايت", "كيلوبايت", "ميجابايت", "جيجابايت"]
    i = 0
    size = float(size_bytes)
    
    while size >= 1024.0 and i < len(size_names) - 1:
        size /= 1024.0
        i += 1
    
    return f"{size:.1f} {size_names[i]}"

def sanitize_filename(filename: str) -> str:
    """تنظيف اسم الملف من الأحرف غير المسموحة"""
    # إزالة الأحرف غير المسموحة
    clean_name = re.sub(r'[<>:"/\\|?*]', '_', filename)
    
    # إزالة المسافات المتعددة
    clean_name = re.sub(r'\s+', ' ', clean_name).strip()
    
    # تحديد الطول الأقصى
    if len(clean_name) > 200:
        clean_name = clean_name[:200]
    
    return clean_name
