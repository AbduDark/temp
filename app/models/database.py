#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مدير قاعدة البيانات - Database Manager
"""

import sqlite3
import os
import bcrypt
from pathlib import Path
from datetime import datetime
from typing import Dict, List, Optional, Any
import logging

logger = logging.getLogger(__name__)

class DatabaseManager:
    """مدير قاعدة البيانات الرئيسي"""
    
    def __init__(self, db_path: str = "data/shop.db"):
        self.db_path = db_path
        self.ensure_db_directory()
    
    def ensure_db_directory(self):
        """التأكد من وجود مجلد قاعدة البيانات"""
        db_dir = Path(self.db_path).parent
        db_dir.mkdir(parents=True, exist_ok=True)
    
    def get_connection(self) -> sqlite3.Connection:
        """الحصول على اتصال بقاعدة البيانات"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row  # للحصول على النتائج كقاموس
        conn.execute("PRAGMA foreign_keys = ON")  # تفعيل المفاتيح الأجنبية
        return conn
    
    def initialize_database(self):
        """إنشاء جداول قاعدة البيانات والبيانات الأولية"""
        try:
            with self.get_connection() as conn:
                # إنشاء الجداول
                self._create_tables(conn)
                # إدراج البيانات الأولية
                self._insert_initial_data(conn)
                logger.info("تم إعداد قاعدة البيانات بنجاح")
        except Exception as e:
            logger.error(f"خطأ في إعداد قاعدة البيانات: {str(e)}")
            raise
    
    def _create_tables(self, conn: sqlite3.Connection):
        """إنشاء جداول قاعدة البيانات"""
        
        # جدول المستخدمين
        conn.execute('''
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username VARCHAR(50) UNIQUE NOT NULL,
                password_hash VARCHAR(128) NOT NULL,
                full_name VARCHAR(100) NOT NULL,
                role VARCHAR(20) NOT NULL DEFAULT 'Cashier',
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الفئات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS categories (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول الموردين
        conn.execute('''
            CREATE TABLE IF NOT EXISTS suppliers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100) NOT NULL,
                contact_person VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المنتجات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS products (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(200) NOT NULL,
                barcode VARCHAR(50),
                category_id INTEGER,
                cost_price DECIMAL(10,2) DEFAULT 0,
                selling_price DECIMAL(10,2) NOT NULL,
                quantity_in_stock INTEGER DEFAULT 0,
                minimum_stock INTEGER DEFAULT 5,
                description TEXT,
                is_active BOOLEAN DEFAULT 1,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (category_id) REFERENCES categories (id)
            )
        ''')
        
        # جدول حركة المخزون
        conn.execute('''
            CREATE TABLE IF NOT EXISTS stock_movements (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                product_id INTEGER NOT NULL,
                movement_type VARCHAR(20) NOT NULL,
                quantity INTEGER NOT NULL,
                cost_price DECIMAL(10,2),
                reference_id INTEGER,
                reference_type VARCHAR(50),
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (product_id) REFERENCES products (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول العملاء
        conn.execute('''
            CREATE TABLE IF NOT EXISTS customers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name VARCHAR(100),
                phone VARCHAR(20),
                email VARCHAR(100),
                address TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # جدول المبيعات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sales (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                total_amount DECIMAL(10,2) NOT NULL,
                discount_amount DECIMAL(10,2) DEFAULT 0,
                tax_amount DECIMAL(10,2) DEFAULT 0,
                final_amount DECIMAL(10,2) NOT NULL,
                payment_method VARCHAR(50) NOT NULL,
                status VARCHAR(20) DEFAULT 'completed',
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول عناصر المبيعات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS sale_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                discount_amount DECIMAL(10,2) DEFAULT 0,
                total_amount DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # جدول المشتريات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS purchases (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                supplier_id INTEGER,
                total_amount DECIMAL(10,2) NOT NULL,
                status VARCHAR(20) DEFAULT 'completed',
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (supplier_id) REFERENCES suppliers (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول عناصر المشتريات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS purchase_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                purchase_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_cost DECIMAL(10,2) NOT NULL,
                total_cost DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (purchase_id) REFERENCES purchases (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # جدول تذاكر الصيانة
        conn.execute('''
            CREATE TABLE IF NOT EXISTS repair_tickets (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                customer_id INTEGER,
                device_info VARCHAR(200) NOT NULL,
                imei VARCHAR(20),
                problem_description TEXT NOT NULL,
                repair_type VARCHAR(20) NOT NULL,
                estimated_cost DECIMAL(10,2),
                final_cost DECIMAL(10,2),
                status VARCHAR(20) DEFAULT 'received',
                technician_id INTEGER,
                received_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                completed_date TIMESTAMP,
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id),
                FOREIGN KEY (technician_id) REFERENCES users (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول قطع الغيار المستخدمة في الصيانة
        conn.execute('''
            CREATE TABLE IF NOT EXISTS repair_parts (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                repair_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_price DECIMAL(10,2) NOT NULL,
                FOREIGN KEY (repair_id) REFERENCES repair_tickets (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # جدول المرتجعات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS returns (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                sale_id INTEGER,
                total_amount DECIMAL(10,2) NOT NULL,
                reason TEXT,
                status VARCHAR(20) DEFAULT 'processed',
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (sale_id) REFERENCES sales (id),
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول عناصر المرتجعات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS return_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                return_id INTEGER NOT NULL,
                product_id INTEGER NOT NULL,
                quantity INTEGER NOT NULL,
                unit_price DECIMAL(10,2) NOT NULL,
                total_amount DECIMAL(10,2) NOT NULL,
                condition_status VARCHAR(50) DEFAULT 'good',
                FOREIGN KEY (return_id) REFERENCES returns (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        ''')
        
        # جدول التحويلات والرصيد
        conn.execute('''
            CREATE TABLE IF NOT EXISTS wallet_transfers (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                transfer_type VARCHAR(50) NOT NULL,
                wallet_type VARCHAR(50) NOT NULL,
                amount DECIMAL(10,2) NOT NULL,
                from_account VARCHAR(100),
                to_account VARCHAR(100),
                reference_number VARCHAR(100),
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول التقفيل اليومي
        conn.execute('''
            CREATE TABLE IF NOT EXISTS daily_closes (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                close_date DATE NOT NULL,
                cash_sales DECIMAL(10,2) DEFAULT 0,
                card_sales DECIMAL(10,2) DEFAULT 0,
                wallet_sales DECIMAL(10,2) DEFAULT 0,
                total_sales DECIMAL(10,2) DEFAULT 0,
                expenses DECIMAL(10,2) DEFAULT 0,
                purchases DECIMAL(10,2) DEFAULT 0,
                returns DECIMAL(10,2) DEFAULT 0,
                net_profit DECIMAL(10,2) DEFAULT 0,
                opening_balance DECIMAL(10,2) DEFAULT 0,
                closing_balance DECIMAL(10,2) DEFAULT 0,
                notes TEXT,
                user_id INTEGER,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول سجل النشاط
        conn.execute('''
            CREATE TABLE IF NOT EXISTS audit_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                action VARCHAR(100) NOT NULL,
                table_name VARCHAR(50),
                record_id INTEGER,
                old_values TEXT,
                new_values TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (id)
            )
        ''')
        
        # جدول الإعدادات
        conn.execute('''
            CREATE TABLE IF NOT EXISTS settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                key VARCHAR(100) UNIQUE NOT NULL,
                value TEXT,
                description TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
    
    def _insert_initial_data(self, conn: sqlite3.Connection):
        """إدراج البيانات الأولية"""
        
        # التحقق من وجود مستخدمين
        cursor = conn.execute("SELECT COUNT(*) FROM users")
        user_count = cursor.fetchone()[0]
        
        if user_count == 0:
            # إنشاء المستخدم الإداري الافتراضي
            password_hash = bcrypt.hashpw("admin123".encode('utf-8'), bcrypt.gensalt())
            conn.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', ("admin", password_hash.decode('utf-8'), "مدير النظام", "Admin"))
            
            # إنشاء مستخدم كاشير للتجربة
            cashier_password = bcrypt.hashpw("cashier123".encode('utf-8'), bcrypt.gensalt())
            conn.execute('''
                INSERT INTO users (username, password_hash, full_name, role)
                VALUES (?, ?, ?, ?)
            ''', ("cashier", cashier_password.decode('utf-8'), "كاشير", "Cashier"))
        
        # إدراج فئات المنتجات الأولية
        cursor = conn.execute("SELECT COUNT(*) FROM categories")
        category_count = cursor.fetchone()[0]
        
        if category_count == 0:
            categories = [
                ("شاشات", "شاشات الهواتف المحمولة"),
                ("جرابات", "جرابات وحافظات الهواتف"),
                ("سماعات", "سماعات الأذن السلكية واللاسلكية"),
                ("ايربودز", "سماعات البلوتوث اللاسلكية"),
                ("اكسسوارات", "اكسسوارات الهواتف المتنوعة"),
                ("شواحن", "شواحن الهواتف والكابلات"),
                ("وصلات", "كابلات USB ووصلات البيانات"),
                ("هواتف مستعملة", "هواتف محمولة مستعملة"),
                ("قطع غيار", "قطع غيار للصيانة")
            ]
            
            for name, desc in categories:
                conn.execute('''
                    INSERT INTO categories (name, description)
                    VALUES (?, ?)
                ''', (name, desc))
        
        # إدراج إعدادات النظام الأولية
        cursor = conn.execute("SELECT COUNT(*) FROM settings")
        settings_count = cursor.fetchone()[0]
        
        if settings_count == 0:
            settings = [
                ("shop_name", "محل الموبايلات", "اسم المحل"),
                ("shop_address", "الرياض، المملكة العربية السعودية", "عنوان المحل"),
                ("shop_phone", "+966-XX-XXX-XXXX", "هاتف المحل"),
                ("currency", "SAR", "العملة المستخدمة"),
                ("tax_rate", "15", "معدل الضريبة المضافة (%)"),
                ("receipt_footer", "شكراً لزيارتكم", "نص أسفل الفاتورة"),
                ("auto_backup", "1", "النسخ الاحتياطي التلقائي (1=مفعل, 0=معطل)")
            ]
            
            for key, value, desc in settings:
                conn.execute('''
                    INSERT INTO settings (key, value, description)
                    VALUES (?, ?, ?)
                ''', (key, value, desc))
        
        conn.commit()
    
    def execute_query(self, query: str, params: tuple = ()) -> List[sqlite3.Row]:
        """تنفيذ استعلام SELECT وإرجاع النتائج"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                return cursor.fetchall()
        except Exception as e:
            logger.error(f"خطأ في تنفيذ الاستعلام: {str(e)}")
            raise
    
    def execute_insert(self, query: str, params: tuple = ()) -> int:
        """تنفيذ استعلام INSERT وإرجاع معرف السجل الجديد"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.lastrowid
        except Exception as e:
            logger.error(f"خطأ في إدراج البيانات: {str(e)}")
            raise
    
    def execute_update(self, query: str, params: tuple = ()) -> int:
        """تنفيذ استعلام UPDATE وإرجاع عدد الصفوف المتأثرة"""
        try:
            with self.get_connection() as conn:
                cursor = conn.execute(query, params)
                conn.commit()
                return cursor.rowcount
        except Exception as e:
            logger.error(f"خطأ في تحديث البيانات: {str(e)}")
            raise
    
    def get_setting(self, key: str) -> Optional[str]:
        """الحصول على قيمة إعداد معين"""
        try:
            result = self.execute_query(
                "SELECT value FROM settings WHERE key = ?",
                (key,)
            )
            return result[0]['value'] if result else None
        except Exception as e:
            logger.error(f"خطأ في الحصول على الإعداد {key}: {str(e)}")
            return None
    
    def set_setting(self, key: str, value: str) -> bool:
        """تعديل قيمة إعداد معين"""
        try:
            updated = self.execute_update(
                "UPDATE settings SET value = ?, updated_at = CURRENT_TIMESTAMP WHERE key = ?",
                (value, key)
            )
            return updated > 0
        except Exception as e:
            logger.error(f"خطأ في تعديل الإعداد {key}: {str(e)}")
            return False
