"""
Database Manager for Mobile Shop Management System
Uses SQLite for local data storage with Arabic support
"""

import sqlite3
import os
from datetime import datetime
from typing import List, Dict, Optional, Any

class DatabaseManager:
    def __init__(self, db_path: str = "mobile_shop.db"):
        """Initialize database manager with SQLite"""
        self.db_path = db_path
        self.connection = None
        
    def get_connection(self):
        """Get database connection with UTF-8 support for Arabic"""
        if self.connection is None:
            self.connection = sqlite3.connect(
                self.db_path,
                check_same_thread=False,
                isolation_level=None
            )
            self.connection.execute("PRAGMA foreign_keys = ON")
            # Enable UTF-8 support for Arabic text
            self.connection.execute("PRAGMA encoding = 'UTF-8'")
            self.connection.row_factory = sqlite3.Row
        return self.connection
    
    def initialize_database(self):
        """Create all necessary tables"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Products table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS products (
                id TEXT PRIMARY KEY,
                sku TEXT UNIQUE NOT NULL,
                name TEXT NOT NULL,
                description TEXT,
                category TEXT,
                brand TEXT,
                barcode TEXT,
                buy_price REAL NOT NULL,
                sale_price REAL NOT NULL,
                current_qty INTEGER DEFAULT 0,
                min_stock INTEGER DEFAULT 0,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Customers table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS customers (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                phone TEXT,
                email TEXT,
                address TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Sales table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sales (
                id TEXT PRIMARY KEY,
                customer_id TEXT,
                subtotal REAL NOT NULL,
                discount REAL DEFAULT 0,
                tax REAL DEFAULT 0,
                total REAL NOT NULL,
                payment_method TEXT DEFAULT 'cash',
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (customer_id) REFERENCES customers (id)
            )
        """)
        
        # Sale items table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS sale_items (
                id TEXT PRIMARY KEY,
                sale_id TEXT NOT NULL,
                product_id TEXT NOT NULL,
                qty INTEGER NOT NULL,
                unit_price REAL NOT NULL,
                discount REAL DEFAULT 0,
                total REAL NOT NULL,
                FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                FOREIGN KEY (product_id) REFERENCES products (id)
            )
        """)
        
        # Repair tickets table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS repair_tickets (
                id TEXT PRIMARY KEY,
                ticket_no TEXT UNIQUE NOT NULL,
                customer_name TEXT NOT NULL,
                customer_phone TEXT,
                device_brand TEXT NOT NULL,
                device_model TEXT NOT NULL,
                imei TEXT,
                issue_desc TEXT NOT NULL,
                accessories TEXT,
                est_cost REAL NOT NULL,
                deposit REAL DEFAULT 0,
                status TEXT DEFAULT 'pending',
                technician TEXT,
                date_due DATE,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Wallet transactions table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS wallet_transactions (
                id TEXT PRIMARY KEY,
                provider TEXT NOT NULL,
                type TEXT NOT NULL,
                amount REAL NOT NULL,
                customer_name TEXT,
                reference TEXT,
                notes TEXT,
                created_at DATETIME DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        conn.commit()
        self.create_sample_data()
    
    def create_sample_data(self):
        """Create sample data if tables are empty"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        # Check if products table is empty
        cursor.execute("SELECT COUNT(*) FROM products")
        if cursor.fetchone()[0] == 0:
            # Sample products
            products = [
                ("prod-1", "IPH14-CASE-001", "جراب iPhone 14", "جراب حماية لهاتف iPhone 14", "إكسسوارات", "Apple", "", 25.0, 45.0, 50, 5),
                ("prod-2", "CHRG-USB-C-001", "شاحن USB-C سريع", "شاحن USB-C بقوة 20 وات", "شواحن", "Generic", "", 35.0, 65.0, 30, 5),
                ("prod-3", "SCRN-IPH13-001", "شاشة iPhone 13", "شاشة LCD أصلية لهاتف iPhone 13", "قطع غيار", "Apple", "", 450.0, 750.0, 8, 2),
                ("prod-4", "HDPH-WRL-001", "سماعات لاسلكية", "سماعات بلوتوث عالية الجودة", "إكسسوارات", "Generic", "", 120.0, 200.0, 25, 3),
                ("prod-5", "BATT-SAM-A54", "بطارية Samsung A54", "بطارية أصلية لهاتف Samsung Galaxy A54", "قطع غيار", "Samsung", "", 85.0, 150.0, 12, 2)
            ]
            
            for product in products:
                cursor.execute("""
                    INSERT INTO products (id, sku, name, description, category, brand, barcode, buy_price, sale_price, current_qty, min_stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, product)
            
            # Sample customers
            customers = [
                ("cust-1", "أحمد محمد", "01012345678", "", "القاهرة، مصر"),
                ("cust-2", "فاطمة علي", "01098765432", "fatima@email.com", "الجيزة، مصر"),
                ("cust-3", "محمود حسن", "01155567890", "", "الإسكندرية، مصر")
            ]
            
            for customer in customers:
                cursor.execute("""
                    INSERT INTO customers (id, name, phone, email, address)
                    VALUES (?, ?, ?, ?, ?)
                """, customer)
            
            # Sample repair ticket
            cursor.execute("""
                INSERT INTO repair_tickets (id, ticket_no, customer_name, customer_phone, device_brand, device_model, 
                                          imei, issue_desc, accessories, est_cost, deposit, status, technician, date_due, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("repair-1", "R-2024-001", "علي أحمد", "01012345678", "iPhone", "iPhone 13", "123456789012345",
                  "كسر في الشاشة وتلف في زر الهوم", "شاحن، كابل USB", 800.0, 200.0, "in_progress", "محمد الفني", 
                  "2024-12-25", "يحتاج تغيير شاشة كاملة"))
            
            conn.commit()
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query and return results as list of dictionaries"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        rows = cursor.fetchall()
        return [dict(row) for row in rows]
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query and return affected rows"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        if params:
            cursor.execute(query, params)
        else:
            cursor.execute(query)
        
        conn.commit()
        return cursor.rowcount
    
    def close(self):
        """Close database connection"""
        if self.connection:
            self.connection.close()
            self.connection = None