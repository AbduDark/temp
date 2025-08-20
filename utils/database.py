"""
Enhanced Database Manager for Mobile Shop Management System
Uses SQLite with comprehensive error handling and data validation
"""

import sqlite3
import os
import shutil
from datetime import datetime, timedelta
from typing import List, Dict, Optional, Any, Union
import logging
import json

class DatabaseManager:
    def __init__(self, db_path: str = "mobile_shop.db"):
        """Initialize database manager with enhanced features"""
        self.db_path = db_path
        self.connection = None
        self.setup_logging()
        
    def setup_logging(self):
        """Setup logging for database operations"""
        logging.basicConfig(
            level=logging.INFO,
            format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            handlers=[
                logging.FileHandler('database.log', encoding='utf-8'),
                logging.StreamHandler()
            ]
        )
        self.logger = logging.getLogger('DatabaseManager')
        
    def get_connection(self):
        """Get database connection with enhanced configuration"""
        if self.connection is None:
            try:
                self.connection = sqlite3.connect(
                    self.db_path,
                    check_same_thread=False,
                    timeout=30.0
                )
                
                # Enable foreign keys and other pragmas
                self.connection.execute("PRAGMA foreign_keys = ON")
                self.connection.execute("PRAGMA encoding = 'UTF-8'")
                self.connection.execute("PRAGMA journal_mode = WAL")
                self.connection.execute("PRAGMA synchronous = NORMAL")
                self.connection.execute("PRAGMA cache_size = 10000")
                self.connection.execute("PRAGMA temp_store = MEMORY")
                
                # Custom row factory for better data access
                self.connection.row_factory = sqlite3.Row
                
                self.logger.info("Database connection established successfully")
                
            except Exception as e:
                self.logger.error(f"Failed to establish database connection: {e}")
                raise
                
        return self.connection
    
    def backup_database(self, backup_path: str = None) -> str:
        """Create a backup of the database"""
        if backup_path is None:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_path = f"backup_mobile_shop_{timestamp}.db"
        
        try:
            if os.path.exists(self.db_path):
                shutil.copy2(self.db_path, backup_path)
                self.logger.info(f"Database backup created: {backup_path}")
                return backup_path
            else:
                raise FileNotFoundError("Database file not found")
        except Exception as e:
            self.logger.error(f"Failed to create database backup: {e}")
            raise
    
    def initialize_database(self):
        """Create all necessary tables with enhanced schema"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Products table with enhanced fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS products (
                    id TEXT PRIMARY KEY,
                    sku TEXT UNIQUE NOT NULL,
                    name TEXT NOT NULL,
                    name_en TEXT,
                    description TEXT,
                    category TEXT NOT NULL,
                    subcategory TEXT,
                    brand TEXT,
                    barcode TEXT,
                    buy_price REAL NOT NULL DEFAULT 0,
                    sale_price REAL NOT NULL DEFAULT 0,
                    current_qty INTEGER DEFAULT 0,
                    min_stock INTEGER DEFAULT 0,
                    max_stock INTEGER DEFAULT 100,
                    location TEXT,
                    supplier TEXT,
                    warranty_months INTEGER DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    tax_rate REAL DEFAULT 0,
                    profit_margin REAL DEFAULT 0,
                    last_updated DATETIME DEFAULT CURRENT_TIMESTAMP,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Customers table with enhanced fields
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS customers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    city TEXT,
                    notes TEXT,
                    customer_type TEXT DEFAULT 'regular',
                    discount_percentage REAL DEFAULT 0,
                    credit_limit REAL DEFAULT 0,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Sales table with enhanced tracking
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS sales (
                    id TEXT PRIMARY KEY,
                    sale_number TEXT UNIQUE NOT NULL,
                    customer_id TEXT,
                    customer_name TEXT,
                    customer_phone TEXT,
                    subtotal REAL NOT NULL DEFAULT 0,
                    discount REAL DEFAULT 0,
                    discount_percentage REAL DEFAULT 0,
                    tax REAL DEFAULT 0,
                    total REAL NOT NULL DEFAULT 0,
                    paid_amount REAL DEFAULT 0,
                    change_amount REAL DEFAULT 0,
                    payment_method TEXT DEFAULT 'cash',
                    payment_status TEXT DEFAULT 'paid',
                    notes TEXT,
                    cashier TEXT,
                    is_refunded BOOLEAN DEFAULT 0,
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
                    product_name TEXT NOT NULL,
                    product_sku TEXT,
                    qty INTEGER NOT NULL,
                    unit_price REAL NOT NULL,
                    discount REAL DEFAULT 0,
                    total REAL NOT NULL,
                    cost_price REAL DEFAULT 0,
                    profit REAL DEFAULT 0,
                    FOREIGN KEY (sale_id) REFERENCES sales (id) ON DELETE CASCADE,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Enhanced repairs table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repairs (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    customer_name TEXT NOT NULL,
                    customer_phone TEXT,
                    customer_email TEXT,
                    device_type TEXT NOT NULL,
                    device_model TEXT,
                    device_serial TEXT,
                    device_color TEXT,
                    device_password TEXT,
                    problem_description TEXT,
                    repair_type TEXT,
                    priority TEXT DEFAULT 'عادي',
                    estimated_cost REAL DEFAULT 0,
                    actual_cost REAL DEFAULT 0,
                    parts_cost REAL DEFAULT 0,
                    labor_cost REAL DEFAULT 0,
                    estimated_days INTEGER DEFAULT 1,
                    actual_days INTEGER DEFAULT 0,
                    receive_date TEXT,
                    delivery_date TEXT,
                    status TEXT DEFAULT 'في الانتظار',
                    technician TEXT,
                    accessories TEXT,
                    backup_created BOOLEAN DEFAULT 0,
                    data_recovered BOOLEAN DEFAULT 0,
                    warranty_days INTEGER DEFAULT 0,
                    notes TEXT,
                    internal_notes TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Repair status history
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS repair_status_history (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    repair_id INTEGER NOT NULL,
                    old_status TEXT,
                    new_status TEXT NOT NULL,
                    notes TEXT,
                    changed_by TEXT,
                    changed_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (repair_id) REFERENCES repairs (id) ON DELETE CASCADE
                )
            """)
            
            # Enhanced wallet transactions
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS wallet_transactions (
                    id TEXT PRIMARY KEY,
                    transaction_number TEXT UNIQUE NOT NULL,
                    provider TEXT NOT NULL,
                    service_type TEXT,
                    transaction_type TEXT NOT NULL,
                    amount REAL NOT NULL,
                    fees REAL DEFAULT 0,
                    net_amount REAL,
                    customer_name TEXT,
                    customer_phone TEXT,
                    recipient_number TEXT,
                    sender_number TEXT,
                    reference TEXT,
                    external_reference TEXT,
                    status TEXT DEFAULT 'completed',
                    notes TEXT,
                    cashier TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Inventory movements
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS inventory_movements (
                    id TEXT PRIMARY KEY,
                    product_id TEXT NOT NULL,
                    movement_type TEXT NOT NULL,
                    quantity INTEGER NOT NULL,
                    cost_per_unit REAL,
                    total_cost REAL,
                    reference_id TEXT,
                    reference_type TEXT,
                    notes TEXT,
                    created_by TEXT,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (product_id) REFERENCES products (id)
                )
            """)
            
            # Suppliers table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS suppliers (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    contact_person TEXT,
                    phone TEXT,
                    email TEXT,
                    address TEXT,
                    tax_number TEXT,
                    payment_terms TEXT,
                    notes TEXT,
                    is_active BOOLEAN DEFAULT 1,
                    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Settings table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS settings (
                    key TEXT PRIMARY KEY,
                    value TEXT NOT NULL,
                    description TEXT,
                    category TEXT DEFAULT 'general',
                    updated_at DATETIME DEFAULT CURRENT_TIMESTAMP
                )
            """)
            
            # Create indexes for better performance
            self.create_indexes(cursor)
            
            # Create triggers
            self.create_triggers(cursor)
            
            conn.commit()
            self.logger.info("Database schema created successfully")
            
            # Insert default settings and sample data
            self.insert_default_settings()
            self.create_sample_data()
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Failed to initialize database: {e}")
            raise
    
    def create_indexes(self, cursor):
        """Create database indexes for better performance"""
        indexes = [
            "CREATE INDEX IF NOT EXISTS idx_products_sku ON products(sku)",
            "CREATE INDEX IF NOT EXISTS idx_products_category ON products(category)",
            "CREATE INDEX IF NOT EXISTS idx_products_brand ON products(brand)",
            "CREATE INDEX IF NOT EXISTS idx_sales_date ON sales(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_sales_customer ON sales(customer_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_sale ON sale_items(sale_id)",
            "CREATE INDEX IF NOT EXISTS idx_sale_items_product ON sale_items(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_repairs_status ON repairs(status)",
            "CREATE INDEX IF NOT EXISTS idx_repairs_customer ON repairs(customer_phone)",
            "CREATE INDEX IF NOT EXISTS idx_wallet_provider ON wallet_transactions(provider)",
            "CREATE INDEX IF NOT EXISTS idx_wallet_date ON wallet_transactions(created_at)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_product ON inventory_movements(product_id)",
            "CREATE INDEX IF NOT EXISTS idx_inventory_date ON inventory_movements(created_at)"
        ]
        
        for index_sql in indexes:
            try:
                cursor.execute(index_sql)
            except Exception as e:
                self.logger.warning(f"Failed to create index: {e}")
    
    def create_triggers(self, cursor):
        """Create database triggers for data integrity"""
        triggers = [
            # Update product quantity on sale
            """
            CREATE TRIGGER IF NOT EXISTS update_product_qty_on_sale
            AFTER INSERT ON sale_items
            BEGIN
                UPDATE products 
                SET current_qty = current_qty - NEW.qty,
                    last_updated = CURRENT_TIMESTAMP
                WHERE id = NEW.product_id;
            END
            """,
            
            # Update timestamps
            """
            CREATE TRIGGER IF NOT EXISTS update_product_timestamp
            AFTER UPDATE ON products
            BEGIN
                UPDATE products 
                SET last_updated = CURRENT_TIMESTAMP 
                WHERE id = NEW.id;
            END
            """,
            
            # Calculate profit on sale items
            """
            CREATE TRIGGER IF NOT EXISTS calculate_profit_on_sale
            AFTER INSERT ON sale_items
            BEGIN
                UPDATE sale_items 
                SET profit = (NEW.unit_price - NEW.cost_price) * NEW.qty
                WHERE id = NEW.id;
            END
            """,
            
            # Log repair status changes
            """
            CREATE TRIGGER IF NOT EXISTS log_repair_status_change
            AFTER UPDATE ON repairs
            WHEN OLD.status != NEW.status
            BEGIN
                INSERT INTO repair_status_history 
                (repair_id, old_status, new_status, notes, changed_at)
                VALUES (NEW.id, OLD.status, NEW.status, 'Status changed automatically', CURRENT_TIMESTAMP);
            END
            """
        ]
        
        for trigger_sql in triggers:
            try:
                cursor.execute(trigger_sql)
            except Exception as e:
                self.logger.warning(f"Failed to create trigger: {e}")
    
    def insert_default_settings(self):
        """Insert default application settings"""
        default_settings = [
            ('shop_name', 'محل الموبايل', 'اسم المحل'),
            ('shop_address', 'العنوان غير محدد', 'عنوان المحل'),
            ('shop_phone', '01000000000', 'رقم هاتف المحل'),
            ('tax_rate', '0.14', 'معدل الضريبة'),
            ('currency', 'جنيه', 'العملة المستخدمة'),
            ('receipt_footer', 'شكراً لزيارتكم', 'تذييل الفاتورة'),
            ('low_stock_threshold', '5', 'حد التنبيه للمخزون المنخفض'),
            ('backup_frequency', '7', 'تكرار النسخ الاحتياطي بالأيام'),
            ('last_backup', '', 'تاريخ آخر نسخة احتياطية'),
            ('auto_generate_sku', '1', 'توليد كود المنتج تلقائياً'),
            ('default_warranty', '6', 'فترة الضمان الافتراضية بالشهور')
        ]
        
        try:
            for key, value, description in default_settings:
                self.execute_update(
                    "INSERT OR IGNORE INTO settings (key, value, description) VALUES (?, ?, ?)",
                    (key, value, description)
                )
            self.logger.info("Default settings inserted successfully")
        except Exception as e:
            self.logger.error(f"Failed to insert default settings: {e}")
    
    def create_sample_data(self):
        """Create comprehensive sample data"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            # Check if data already exists
            cursor.execute("SELECT COUNT(*) FROM products")
            if cursor.fetchone()[0] > 0:
                return
            
            # Sample categories and brands
            categories = ['اكسسوارات', 'قطع غيار', 'شواحن', 'سماعات', 'جرابات']
            brands = ['Apple', 'Samsung', 'Huawei', 'Xiaomi', 'Oppo', 'Vivo', 'Generic']
            
            # Sample products with realistic data
            products = [
                # iPhone Accessories
                ("prod-001", "IPH14-CASE-BLK", "جراب iPhone 14 أسود", "جراب حماية سيليكون لهاتف iPhone 14", 
                 "جرابات", "iPhone", "Apple", "", 25.0, 45.0, 50, 5, 100),
                ("prod-002", "IPH14-CASE-CLR", "جراب iPhone 14 شفاف", "جراب حماية شفاف لهاتف iPhone 14", 
                 "جرابات", "iPhone", "Apple", "", 20.0, 35.0, 30, 5, 100),
                ("prod-003", "IPH-CHRG-20W", "شاحن iPhone 20W", "شاحن سريع أصلي لهواتف iPhone", 
                 "شواحن", "شواحن", "Apple", "", 120.0, 200.0, 25, 3, 50),
                
                # Samsung Accessories  
                ("prod-004", "SAM-A54-SCRN", "شاشة Samsung A54", "شاشة LCD أصلية لهاتف Samsung Galaxy A54", 
                 "قطع غيار", "Samsung", "Samsung", "", 300.0, 500.0, 8, 2, 20),
                ("prod-005", "SAM-A54-BATT", "بطارية Samsung A54", "بطارية أصلية لهاتف Samsung Galaxy A54", 
                 "قطع غيار", "Samsung", "Samsung", "", 85.0, 150.0, 12, 2, 30),
                
                # Generic Accessories
                ("prod-006", "USB-C-FAST", "كابل USB-C سريع", "كابل USB-C للشحن السريع ونقل البيانات", 
                 "شواحن", "كابلات", "Generic", "", 15.0, 30.0, 100, 10, 200),
                ("prod-007", "POWER-BANK-10K", "باور بانك 10000mAh", "بطارية محمولة بقوة 10000 مللي أمبير", 
                 "اكسسوارات", "باور بانك", "Generic", "", 80.0, 150.0, 20, 3, 50),
                ("prod-008", "HDPH-WIRED", "سماعات سلكية", "سماعات أذن سلكية عالية الجودة", 
                 "سماعات", "سماعات", "Generic", "", 25.0, 50.0, 40, 5, 100),
                ("prod-009", "HDPH-BT", "سماعات بلوتوث", "سماعات لاسلكية بتقنية البلوتوث", 
                 "سماعات", "سماعات", "Generic", "", 120.0, 250.0, 15, 2, 40),
                
                # Phone accessories
                ("prod-010", "PHONE-STAND", "حامل موبايل", "حامل موبايل قابل للتعديل للمكتب والسيارة", 
                 "اكسسوارات", "حوامل", "Generic", "", 30.0, 60.0, 25, 3, 50),
                ("prod-011", "CAR-CHRG", "شاحن سيارة", "شاحن سيارة سريع بمنفذين USB", 
                 "شواحن", "شواحن", "Generic", "", 35.0, 70.0, 30, 3, 60),
                ("prod-012", "SCRN-PROT", "واقي شاشة", "واقي شاشة زجاجي مقاوم للكسر", 
                 "اكسسوارات", "واقيات", "Generic", "", 10.0, 25.0, 80, 10, 150),
                
                # Repair parts
                ("prod-013", "IPH13-SCRN", "شاشة iPhone 13", "شاشة OLED أصلية لهاتف iPhone 13", 
                 "قطع غيار", "iPhone", "Apple", "", 450.0, 750.0, 5, 1, 15),
                ("prod-014", "IPH12-BATT", "بطارية iPhone 12", "بطارية أصلية لهاتف iPhone 12", 
                 "قطع غيار", "iPhone", "Apple", "", 150.0, 280.0, 8, 2, 20),
                ("prod-015", "AND-TOOLS", "أدوات فك الموبايل", "طقم أدوات احترافي لفك وإصلاح الهواتف", 
                 "اكسسوارات", "أدوات", "Generic", "", 60.0, 120.0, 10, 2, 25)
            ]
            
            for product in products:
                cursor.execute("""
                    INSERT INTO products (id, sku, name, description, category, subcategory, brand, barcode, 
                                        buy_price, sale_price, current_qty, min_stock, max_stock)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, product)
            
            # Sample customers
            customers = [
                ("cust-001", "أحمد محمد علي", "01012345678", "ahmed@email.com", "شارع التحرير، القاهرة", "القاهرة", "", "vip", 5.0),
                ("cust-002", "فاطمة حسن", "01098765432", "", "شارع الهرم، الجيزة", "الجيزة", "", "regular", 0.0),
                ("cust-003", "محمود السيد", "01155567890", "mahmoud@email.com", "كورنيش النيل، الإسكندرية", "الإسكندرية", "", "regular", 0.0),
                ("cust-004", "نور أحمد", "01234567890", "", "شارع الجامعة، المنصورة", "المنصورة", "", "regular", 0.0),
                ("cust-005", "يوسف محمد", "01987654321", "youssef@email.com", "شارع الكورنيش، أسوان", "أسوان", "", "wholesale", 10.0)
            ]
            
            for customer in customers:
                cursor.execute("""
                    INSERT INTO customers (id, name, phone, email, address, city, notes, customer_type, discount_percentage)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, customer)
            
            # Sample suppliers
            suppliers = [
                ("supp-001", "شركة الهواتف المتقدمة", "أحمد المدير", "01000111222", "supplier1@email.com", "القاهرة الجديدة"),
                ("supp-002", "مؤسسة الاكسسوارات الحديثة", "سارة المبيعات", "01000333444", "", "الإسكندرية"),
                ("supp-003", "معرض قطع الغيار الأصلية", "محمد التاجر", "01000555666", "parts@email.com", "الجيزة")
            ]
            
            for supplier in suppliers:
                cursor.execute("""
                    INSERT INTO suppliers (id, name, contact_person, phone, email, address)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, supplier)
            
            # Sample repair ticket
            cursor.execute("""
                INSERT INTO repairs (customer_name, customer_phone, customer_email, device_type, device_model, 
                                   device_serial, device_color, problem_description, repair_type, priority, 
                                   estimated_cost, estimated_days, receive_date, status, accessories, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, ("علي أحمد محمد", "01012345678", "", "iPhone", "iPhone 13 Pro", "123456789012345", "أزرق",
                  "كسر في الشاشة مع عدم استجابة اللمس في المنطقة اليمنى", "إصلاح شاشة", "مستعجل", 
                  800.0, 2, datetime.now().strftime("%Y-%m-%d"), "قيد الإصلاح", "شاحن، سماعات، جراب", 
                  "تم اختبار الجهاز وتحديد المشكلة، في انتظار قطعة الغيار"))
            
            # Sample wallet transactions
            wallet_transactions = [
                ("trans-001", "WT-2024-001", "vodafone", "cash", "receive", 500.0, 0.0, 500.0, "أحمد محمد", "01012345678", "", "", "", "", "completed"),
                ("trans-002", "WT-2024-002", "orange", "transfer", "send", -200.0, 5.0, -195.0, "فاطمة حسن", "01098765432", "01234567890", "", "", "", "completed"),
                ("trans-003", "WT-2024-003", "etisalat", "cash", "receive", 300.0, 0.0, 300.0, "محمود السيد", "01155567890", "", "", "", "", "completed")
            ]
            
            for transaction in wallet_transactions:
                cursor.execute("""
                    INSERT INTO wallet_transactions (id, transaction_number, provider, service_type, transaction_type, 
                                                   amount, fees, net_amount, customer_name, customer_phone, 
                                                   recipient_number, sender_number, reference, external_reference, status)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, transaction)
            
            conn.commit()
            self.logger.info("Sample data created successfully")
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Failed to create sample data: {e}")
            raise
    
    def execute_query(self, query: str, params: tuple = None) -> List[Dict[str, Any]]:
        """Execute SELECT query with enhanced error handling"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            rows = cursor.fetchall()
            result = [dict(row) for row in rows]
            
            self.logger.debug(f"Query executed successfully: {len(result)} rows returned")
            return result
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            raise
    
    def execute_update(self, query: str, params: tuple = None) -> int:
        """Execute INSERT/UPDATE/DELETE query with enhanced error handling"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            if params:
                cursor.execute(query, params)
            else:
                cursor.execute(query)
            
            affected_rows = cursor.rowcount
            conn.commit()
            
            self.logger.debug(f"Update executed successfully: {affected_rows} rows affected")
            return affected_rows
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Update execution failed: {e}")
            raise
    
    def execute_transaction(self, queries: List[tuple]) -> bool:
        """Execute multiple queries in a transaction"""
        conn = self.get_connection()
        cursor = conn.cursor()
        
        try:
            cursor.execute("BEGIN TRANSACTION")
            
            for query, params in queries:
                if params:
                    cursor.execute(query, params)
                else:
                    cursor.execute(query)
            
            conn.commit()
            self.logger.info(f"Transaction executed successfully: {len(queries)} queries")
            return True
            
        except Exception as e:
            conn.rollback()
            self.logger.error(f"Transaction failed: {e}")
            raise
    
    def get_setting(self, key: str, default_value: str = "") -> str:
        """Get a setting value"""
        try:
            result = self.execute_query("SELECT value FROM settings WHERE key = ?", (key,))
            return result[0]['value'] if result else default_value
        except:
            return default_value
    
    def set_setting(self, key: str, value: str, description: str = "") -> bool:
        """Set a setting value"""
        try:
            self.execute_update("""
                INSERT OR REPLACE INTO settings (key, value, description, updated_at) 
                VALUES (?, ?, ?, CURRENT_TIMESTAMP)
            """, (key, value, description))
            return True
        except:
            return False
    
    def get_statistics(self) -> Dict[str, Any]:
        """Get comprehensive database statistics"""
        try:
            stats = {}
            
            # Products statistics
            products_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(current_qty) as total_inventory,
                    SUM(CASE WHEN current_qty <= min_stock THEN 1 ELSE 0 END) as low_stock_count,
                    SUM(current_qty * buy_price) as inventory_value
                FROM products WHERE is_active = 1
            """)[0]
            stats.update(products_stats)
            
            # Sales statistics
            today = datetime.now().strftime("%Y-%m-%d")
            sales_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as total_sales_today,
                    COALESCE(SUM(total), 0) as sales_total_today
                FROM sales 
                WHERE DATE(created_at) = ?
            """, (today,))[0]
            stats.update(sales_stats)
            
            # Monthly sales
            month_start = datetime.now().replace(day=1).strftime("%Y-%m-%d")
            monthly_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as total_sales_month,
                    COALESCE(SUM(total), 0) as sales_total_month
                FROM sales 
                WHERE DATE(created_at) >= ?
            """, (month_start,))[0]
            stats.update(monthly_stats)
            
            # Repairs statistics
            repairs_stats = self.execute_query("""
                SELECT 
                    COUNT(*) as total_repairs,
                    SUM(CASE WHEN status = 'في الانتظار' THEN 1 ELSE 0 END) as pending_repairs,
                    SUM(CASE WHEN status = 'قيد الإصلاح' THEN 1 ELSE 0 END) as in_progress_repairs,
                    SUM(CASE WHEN status = 'مكتمل' THEN 1 ELSE 0 END) as completed_repairs
                FROM repairs
            """)[0]
            stats.update(repairs_stats)
            
            # Wallet statistics
            wallet_stats = self.execute_query("""
                SELECT 
                    provider,
                    SUM(amount) as balance
                FROM wallet_transactions 
                GROUP BY provider
            """)
            
            for wallet in wallet_stats:
                stats[f"{wallet['provider']}_balance"] = wallet['balance']
            
            return stats
            
        except Exception as e:
            self.logger.error(f"Failed to get statistics: {e}")
            return {}
    
    def cleanup_old_data(self, days: int = 365):
        """Clean up old data to maintain database performance"""
        try:
            cutoff_date = (datetime.now() - timedelta(days=days)).strftime("%Y-%m-%d")
            
            # Archive old sales (you might want to export before deleting)
            old_sales = self.execute_query("""
                SELECT COUNT(*) as count FROM sales 
                WHERE DATE(created_at) < ? AND payment_status = 'paid'
            """, (cutoff_date,))[0]
            
            if old_sales['count'] > 0:
                self.logger.info(f"Found {old_sales['count']} old sales records to archive")
                # Here you could export to backup before deletion
                
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to cleanup old data: {e}")
            return False
    
    def optimize_database(self):
        """Optimize database performance"""
        try:
            conn = self.get_connection()
            cursor = conn.cursor()
            
            # Run VACUUM to reclaim space
            cursor.execute("VACUUM")
            
            # Analyze to update statistics
            cursor.execute("ANALYZE")
            
            # Reindex
            cursor.execute("REINDEX")
            
            conn.commit()
            self.logger.info("Database optimization completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Database optimization failed: {e}")
            return False
    
    def close(self):
        """Close database connection properly"""
        if self.connection:
            try:
                self.connection.close()
                self.connection = None
                self.logger.info("Database connection closed successfully")
            except Exception as e:
                self.logger.error(f"Error closing database connection: {e}")
