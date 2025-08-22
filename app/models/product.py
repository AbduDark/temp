#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المنتج والفئة - Product and Category Models
"""

from datetime import datetime
from typing import Dict, List, Optional
from .database import DatabaseManager

class Category:
    """فئة التصنيف"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def get_all_categories(self) -> List[Dict]:
        """الحصول على جميع الفئات"""
        try:
            result = self.db.execute_query(
                "SELECT * FROM categories ORDER BY name"
            )
            return [dict(row) for row in result]
        except Exception as e:
            print(f"خطأ في الحصول على الفئات: {str(e)}")
            return []
    
    def create_category(self, name: str, description: str = "") -> int:
        """إنشاء فئة جديدة"""
        try:
            return self.db.execute_insert(
                "INSERT INTO categories (name, description) VALUES (?, ?)",
                (name, description)
            )
        except Exception as e:
            print(f"خطأ في إنشاء الفئة: {str(e)}")
            return 0

class Product:
    """فئة المنتج"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def get_all_products(self) -> List[Dict]:
        """الحصول على جميع المنتجات"""
        try:
            result = self.db.execute_query("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
                ORDER BY p.name
            """)
            return [dict(row) for row in result]
        except Exception as e:
            print(f"خطأ في الحصول على المنتجات: {str(e)}")
            return []
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """الحصول على منتج بالمعرف"""
        try:
            result = self.db.execute_query("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.id = ? AND p.is_active = 1
            """, (product_id,))
            return dict(result[0]) if result else None
        except Exception as e:
            print(f"خطأ في الحصول على المنتج: {str(e)}")
            return None
    
    def search_products(self, search_term: str) -> List[Dict]:
        """البحث عن المنتجات"""
        try:
            search_pattern = f"%{search_term}%"
            result = self.db.execute_query("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE (p.name LIKE ? OR p.barcode LIKE ? OR p.model LIKE ?) 
                AND p.is_active = 1
                ORDER BY p.name
                LIMIT 50
            """, (search_pattern, search_pattern, search_pattern))
            
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"خطأ في البحث عن المنتجات: {str(e)}")
            return []
        """البحث عن المنتجات"""
        try:
            search_pattern = f"%{search_term}%"
            result = self.db.execute_query("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1 AND (
                    p.name LIKE ? OR 
                    p.barcode LIKE ? OR 
                    c.name LIKE ?
                )
                ORDER BY p.name
            """, (search_pattern, search_pattern, search_pattern))
            return [dict(row) for row in result]
        except Exception as e:
            print(f"خطأ في البحث عن المنتجات: {str(e)}")
            return []
    
    def create_product(self, name: str, category_id: int, selling_price: float,
                      cost_price: float = 0, barcode: str = "", 
                      quantity: int = 0, minimum_stock: int = 5,
                      description: str = "") -> int:
        """إنشاء منتج جديد"""
        try:
            product_id = self.db.execute_insert("""
                INSERT INTO products 
                (name, barcode, category_id, cost_price, selling_price, 
                 quantity_in_stock, minimum_stock, description)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, barcode, category_id, cost_price, selling_price,
                  quantity, minimum_stock, description))
            
            # تسجيل حركة مخزون إذا كانت الكمية أكبر من صفر
            if quantity > 0:
                self.add_stock_movement(product_id, 'in', quantity, cost_price, 
                                      'initial_stock', 'إضافة مخزون أولي')
            
            return product_id
            
        except Exception as e:
            print(f"خطأ في إنشاء المنتج: {str(e)}")
            return 0
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """تحديث بيانات المنتج"""
        try:
            update_fields = []
            params = []
            
            allowed_fields = ['name', 'barcode', 'category_id', 'cost_price', 
                            'selling_price', 'minimum_stock', 'description']
            
            for field, value in kwargs.items():
                if field in allowed_fields:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                params.append(product_id)
                
                query = f"UPDATE products SET {', '.join(update_fields)} WHERE id = ?"
                self.db.execute_update(query, tuple(params))
                return True
            
            return False
            
        except Exception as e:
            print(f"خطأ في تحديث المنتج: {str(e)}")
            return False
    
    def adjust_stock(self, product_id: int, new_quantity: int, reason: str = "",
                    user_id: int = None) -> bool:
        """تعديل المخزون يدوياً"""
        try:
            # الحصول على الكمية الحالية
            result = self.db.execute_query(
                "SELECT quantity_in_stock FROM products WHERE id = ?",
                (product_id,)
            )
            
            if not result:
                return False
            
            current_quantity = result[0]['quantity_in_stock']
            difference = new_quantity - current_quantity
            
            if difference != 0:
                # تحديث كمية المنتج
                self.db.execute_update(
                    "UPDATE products SET quantity_in_stock = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                    (new_quantity, product_id)
                )
                
                # تسجيل حركة المخزون
                movement_type = 'in' if difference > 0 else 'out'
                self.add_stock_movement(
                    product_id, movement_type, abs(difference), 
                    0, 'manual_adjustment', reason, user_id
                )
            
            return True
            
        except Exception as e:
            print(f"خطأ في تعديل المخزون: {str(e)}")
            return False
    
    def add_stock_movement(self, product_id: int, movement_type: str, 
                         quantity: int, cost_price: float = 0,
                         reference_type: str = "", notes: str = "",
                         user_id: int = None) -> int:
        """إضافة حركة مخزون"""
        try:
            return self.db.execute_insert("""
                INSERT INTO stock_movements 
                (product_id, movement_type, quantity, cost_price, 
                 reference_type, notes, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?)
            """, (product_id, movement_type, quantity, cost_price,
                  reference_type, notes, user_id))
        except Exception as e:
            print(f"خطأ في إضافة حركة المخزون: {str(e)}")
            return 0
    
    def get_low_stock_products(self) -> List[Dict]:
        """الحصول على المنتجات ذات المخزون المنخفض"""
        try:
            result = self.db.execute_query("""
                SELECT p.*, c.name as category_name 
                FROM products p 
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1 AND p.quantity_in_stock <= p.minimum_stock
                ORDER BY p.quantity_in_stock ASC
            """)
            return [dict(row) for row in result]
        except Exception as e:
            print(f"خطأ في الحصول على المنتجات منخفضة المخزون: {str(e)}")
            return []
    
    def get_stock_movements(self, product_id: int = None, 
                          start_date: str = None, end_date: str = None) -> List[Dict]:
        """الحصول على حركات المخزون"""
        try:
            query = """
                SELECT sm.*, p.name as product_name, u.full_name as user_name
                FROM stock_movements sm
                LEFT JOIN products p ON sm.product_id = p.id
                LEFT JOIN users u ON sm.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if product_id:
                query += " AND sm.product_id = ?"
                params.append(product_id)
            
            if start_date:
                query += " AND DATE(sm.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(sm.created_at) <= ?"
                params.append(end_date)
            
            query += " ORDER BY sm.created_at DESC"
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"خطأ في الحصول على حركات المخزون: {str(e)}")
            return []
