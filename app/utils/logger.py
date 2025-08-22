#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نظام التسجيل - Logging System
"""

import logging
import logging.handlers
import os
from pathlib import Path
from datetime import datetime
from typing import Optional


def setup_logger(
    name: str = 'mobile_shop_app',
    log_file: Optional[str] = None,
    level: int = logging.INFO,
    max_bytes: int = 10*1024*1024,  # 10MB
    backup_count: int = 5
) -> logging.Logger:
    """
    إعداد نظام التسجيل الرئيسي
    
    Args:
        name: اسم المسجل
        log_file: مسار ملف السجل (افتراضي: logs/app.log)
        level: مستوى التسجيل
        max_bytes: الحد الأقصى لحجم ملف السجل
        backup_count: عدد ملفات النسخ الاحتياطية
    
    Returns:
        مسجل الأحداث المكون
    """
    
    # إنشاء مجلد السجلات إذا لم يكن موجوداً
    logs_dir = Path("logs")
    logs_dir.mkdir(exist_ok=True)
    
    # تحديد مسار ملف السجل
    if log_file is None:
        log_file = logs_dir / "app.log"
    
    # إنشاء المسجل
    logger = logging.getLogger(name)
    logger.setLevel(level)
    
    # تجنب إضافة معالجات متعددة
    if logger.handlers:
        return logger
    
    # إنشاء تنسيق السجلات
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # معالج الملف مع التدوير
    file_handler = logging.handlers.RotatingFileHandler(
        log_file,
        maxBytes=max_bytes,
        backupCount=backup_count,
        encoding='utf-8'
    )
    file_handler.setLevel(level)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # معالج وحدة التحكم
    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.WARNING)  # فقط التحذيرات والأخطاء
    console_formatter = logging.Formatter(
        fmt='%(levelname)s: %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    logger.addHandler(console_handler)
    
    # تسجيل بداية التشغيل
    logger.info("تم تشغيل نظام التسجيل")
    logger.info(f"ملف السجل: {log_file}")
    
    return logger


def get_logger(name: str) -> logging.Logger:
    """
    الحصول على مسجل فرعي
    
    Args:
        name: اسم المسجل الفرعي
    
    Returns:
        المسجل الفرعي
    """
    return logging.getLogger(f'mobile_shop_app.{name}')


def setup_database_logger() -> logging.Logger:
    """إعداد مسجل قاعدة البيانات"""
    db_logger = get_logger('database')
    
    # إضافة معالج منفصل لقاعدة البيانات إذا أردنا
    logs_dir = Path("logs")
    db_log_file = logs_dir / "database.log"
    
    # تجنب إضافة معالجات متعددة
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
               and h.baseFilename == str(db_log_file.absolute()) 
               for h in db_logger.handlers):
        
        db_handler = logging.handlers.RotatingFileHandler(
            db_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=3,
            encoding='utf-8'
        )
        
        db_formatter = logging.Formatter(
            fmt='%(asctime)s - DB - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        db_handler.setFormatter(db_formatter)
        db_handler.setLevel(logging.DEBUG)
        db_logger.addHandler(db_handler)
    
    return db_logger


def setup_error_logger() -> logging.Logger:
    """إعداد مسجل الأخطاء"""
    error_logger = get_logger('errors')
    
    logs_dir = Path("logs")
    error_log_file = logs_dir / "errors.log"
    
    # تجنب إضافة معالجات متعددة
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
               and h.baseFilename == str(error_log_file.absolute()) 
               for h in error_logger.handlers):
        
        error_handler = logging.handlers.RotatingFileHandler(
            error_log_file,
            maxBytes=10*1024*1024,  # 10MB
            backupCount=5,
            encoding='utf-8'
        )
        
        error_formatter = logging.Formatter(
            fmt='%(asctime)s - ERROR - %(name)s - %(funcName)s:%(lineno)d - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        error_handler.setFormatter(error_formatter)
        error_handler.setLevel(logging.ERROR)
        error_logger.addHandler(error_handler)
    
    return error_logger


def setup_audit_logger() -> logging.Logger:
    """إعداد مسجل المراجعة"""
    audit_logger = get_logger('audit')
    
    logs_dir = Path("logs")
    audit_log_file = logs_dir / "audit.log"
    
    # تجنب إضافة معالجات متعددة
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
               and h.baseFilename == str(audit_log_file.absolute()) 
               for h in audit_logger.handlers):
        
        audit_handler = logging.handlers.RotatingFileHandler(
            audit_log_file,
            maxBytes=20*1024*1024,  # 20MB
            backupCount=10,
            encoding='utf-8'
        )
        
        audit_formatter = logging.Formatter(
            fmt='%(asctime)s - AUDIT - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        audit_handler.setFormatter(audit_formatter)
        audit_handler.setLevel(logging.INFO)
        audit_logger.addHandler(audit_handler)
    
    return audit_logger


def log_user_activity(user_id: int, action: str, details: str = ""):
    """
    تسجيل نشاط المستخدم
    
    Args:
        user_id: معرف المستخدم
        action: الإجراء المنفذ
        details: تفاصيل إضافية
    """
    audit_logger = setup_audit_logger()
    audit_logger.info(f"المستخدم {user_id} - {action} - {details}")


def log_database_operation(operation: str, table: str, record_id: Optional[int] = None):
    """
    تسجيل عملية قاعدة البيانات
    
    Args:
        operation: نوع العملية (INSERT, UPDATE, DELETE, SELECT)
        table: اسم الجدول
        record_id: معرف السجل (اختياري)
    """
    db_logger = setup_database_logger()
    record_info = f" - السجل: {record_id}" if record_id else ""
    db_logger.debug(f"عملية {operation} على جدول {table}{record_info}")


def log_error(error: Exception, context: str = ""):
    """
    تسجيل خطأ مع تفاصيل السياق
    
    Args:
        error: الاستثناء المراد تسجيله
        context: سياق حدوث الخطأ
    """
    error_logger = setup_error_logger()
    context_info = f" - السياق: {context}" if context else ""
    error_logger.error(f"{type(error).__name__}: {str(error)}{context_info}", exc_info=True)


def log_security_event(event: str, user_id: Optional[int] = None, ip_address: str = ""):
    """
    تسجيل حدث أمني
    
    Args:
        event: وصف الحدث الأمني
        user_id: معرف المستخدم (إذا كان متاحاً)
        ip_address: عنوان IP (إذا كان متاحاً)
    """
    security_logger = get_logger('security')
    
    # إعداد معالج الأمان إذا لم يكن موجوداً
    logs_dir = Path("logs")
    security_log_file = logs_dir / "security.log"
    
    if not any(isinstance(h, logging.handlers.RotatingFileHandler) 
               and h.baseFilename == str(security_log_file.absolute()) 
               for h in security_logger.handlers):
        
        security_handler = logging.handlers.RotatingFileHandler(
            security_log_file,
            maxBytes=5*1024*1024,  # 5MB
            backupCount=10,
            encoding='utf-8'
        )
        
        security_formatter = logging.Formatter(
            fmt='%(asctime)s - SECURITY - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        security_handler.setFormatter(security_formatter)
        security_handler.setLevel(logging.WARNING)
        security_logger.addHandler(security_handler)
    
    user_info = f" - المستخدم: {user_id}" if user_id else ""
    ip_info = f" - IP: {ip_address}" if ip_address else ""
    security_logger.warning(f"{event}{user_info}{ip_info}")


def cleanup_old_logs(days_to_keep: int = 30):
    """
    تنظيف السجلات القديمة
    
    Args:
        days_to_keep: عدد الأيام للاحتفاظ بالسجلات
    """
    logger = get_logger('maintenance')
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return
        
        cutoff_date = datetime.now().timestamp() - (days_to_keep * 24 * 60 * 60)
        deleted_count = 0
        
        for log_file in logs_dir.iterdir():
            if log_file.is_file() and log_file.suffix == '.log':
                # فحص ملفات النسخ الاحتياطية للسجلات
                if '.' in log_file.stem and log_file.stem.split('.')[-1].isdigit():
                    if log_file.stat().st_mtime < cutoff_date:
                        log_file.unlink()
                        deleted_count += 1
        
        if deleted_count > 0:
            logger.info(f"تم حذف {deleted_count} ملف سجل قديم")
        
    except Exception as e:
        logger.error(f"خطأ في تنظيف السجلات القديمة: {str(e)}")


def get_log_stats() -> dict:
    """
    الحصول على إحصائيات السجلات
    
    Returns:
        قاموس يحتوي على إحصائيات الملفات
    """
    stats = {
        'total_files': 0,
        'total_size_mb': 0,
        'files': []
    }
    
    try:
        logs_dir = Path("logs")
        if not logs_dir.exists():
            return stats
        
        for log_file in logs_dir.iterdir():
            if log_file.is_file() and log_file.suffix == '.log':
                size = log_file.stat().st_size
                stats['total_files'] += 1
                stats['total_size_mb'] += size / (1024 * 1024)
                
                stats['files'].append({
                    'name': log_file.name,
                    'size_mb': round(size / (1024 * 1024), 2),
                    'modified': datetime.fromtimestamp(log_file.stat().st_mtime).isoformat()
                })
        
        stats['total_size_mb'] = round(stats['total_size_mb'], 2)
        stats['files'].sort(key=lambda x: x['modified'], reverse=True)
        
    except Exception as e:
        logger = get_logger('maintenance')
        logger.error(f"خطأ في الحصول على إحصائيات السجلات: {str(e)}")
    
    return stats


# إعداد المسجلات الافتراضية
_main_logger = None

def initialize_logging():
    """تهيئة نظام التسجيل الافتراضي"""
    global _main_logger
    if _main_logger is None:
        _main_logger = setup_logger()
        setup_database_logger()
        setup_error_logger()
        setup_audit_logger()
        
        # تسجيل بداية تشغيل التطبيق
        _main_logger.info("=" * 50)
        _main_logger.info("بداية تشغيل نظام إدارة محل الموبايلات")
        _main_logger.info("=" * 50)
    
    return _main_logger


def shutdown_logging():
    """إغلاق نظام التسجيل"""
    if _main_logger:
        _main_logger.info("=" * 50)
        _main_logger.info("إنهاء تشغيل نظام إدارة محل الموبايلات")
        _main_logger.info("=" * 50)
        
        # إغلاق جميع المعالجات
        for handler in _main_logger.handlers[:]:
            handler.close()
            _main_logger.removeHandler(handler)
