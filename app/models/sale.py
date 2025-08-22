#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المبيعات - Sales Model
"""

from datetime import datetime
from typing import Dict, List, Optional, Tuple
from .database import DatabaseManager

class Sale:
    """فئة المبيعات"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def create_sale(self, customer_id: Optional[int], items: List[Dict],
                   payment_method: str, discount_amount: float = 0,
                   notes: str = "", user_id: int = None) -> Optional[int]:
        """إنشاء فاتورة مبيعات"""
        try:
            # حساب إجمالي المبلغ
            total_amount = sum(item['quantity'] * item['price'] for item in items)
            
            # حساب الضريبة
            tax_rate = float(self.db.get_setting('tax_rate') or 0) / 100
            tax_amount = (total_amount - discount_amount) * tax_rate
            
            # المبلغ النهائي
            final_amount = total_amount - discount_amount + tax_amount
            
            # إنشاء فاتورة المبيعات
            sale_id = self.db.execute_insert("""
                INSERT INTO sales 
                (customer_id, total_amount, discount_amount, tax_amount, 
                 final_amount, payment_method, notes, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, total_amount, discount_amount, tax_amount,
                  final_amount, payment_method, notes, user_id))
            
            if not sale_id:
                return None
            
            # إضافة عناصر الفاتورة
            for item in items:
                item_total = item['quantity'] * item['price']
                
                # إضافة عنصر الفاتورة
                self.db.execute_insert("""
                    INSERT INTO sale_items 
                    (sale_id, product_id, quantity, unit_price, total_amount)
                    VALUES (?, ?, ?, ?, ?)
                """, (sale_id, item['product_id'], item['quantity'],
                      item['price'], item_total))
                
                # تحديث المخزون
                self._update_product_stock(item['product_id'], -item['quantity'])
                
                # تسجيل حركة المخزون
                self._add_stock_movement(
                    item['product_id'], 'out', item['quantity'],
                    sale_id, 'sale', user_id
                )
            
            return sale_id
            
        except Exception as e:
            print(f"خطأ في إنشاء فاتورة المبيعات: {str(e)}")
            return None
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Dict]:
        """الحصول على فاتورة مبيعات بالمعرف"""
        try:
            # الحصول على بيانات الفاتورة
            result = self.db.execute_query("""
                SELECT s.*, c.name as customer_name, c.phone as customer_phone,
                       u.full_name as user_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.id = ?
            """, (sale_id,))
            
            if not result:
                return None
            
            sale = dict(result[0])
            
            # الحصول على عناصر الفاتورة
            items_result = self.db.execute_query("""
                SELECT si.*, p.name as product_name
                FROM sale_items si
                LEFT JOIN products p ON si.product_id = p.id
                WHERE si.sale_id = ?
            """, (sale_id,))
            
            sale['items'] = [dict(row) for row in items_result]
            
            return sale
            
        except Exception as e:
            print(f"خطأ في الحصول على فاتورة المبيعات: {str(e)}")
            return None
    
    def get_sales_list(self, start_date: str = None, end_date: str = None,
                      customer_id: int = None, limit: int = 100) -> List[Dict]:
        """الحصول على قائمة المبيعات"""
        try:
            query = """
                SELECT s.*, c.name as customer_name, u.full_name as user_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.status = 'completed'
            """
            params = []
            
            if start_date:
                query += " AND DATE(s.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(s.created_at) <= ?"
                params.append(end_date)
            
            if customer_id:
                query += " AND s.customer_id = ?"
                params.append(customer_id)
            
            query += " ORDER BY s.created_at DESC LIMIT ?"
            params.append(limit)
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"خطأ في الحصول على قائمة المبيعات: {str(e)}")
            return []
    
    def get_daily_sales_summary(self, date: str) -> Dict:
        """الحصول على ملخص مبيعات اليوم"""
        try:
            result = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(final_amount) as total_amount,
                    SUM(CASE WHEN payment_method = 'cash' THEN final_amount ELSE 0 END) as cash_sales,
                    SUM(CASE WHEN payment_method = 'card' THEN final_amount ELSE 0 END) as card_sales,
                    SUM(CASE WHEN payment_method LIKE '%wallet%' THEN final_amount ELSE 0 END) as wallet_sales
                FROM sales 
                WHERE DATE(created_at) = ? AND status = 'completed'
            """, (date,))
            
            if result:
                return dict(result[0])
            else:
                return {
                    'total_transactions': 0,
                    'total_amount': 0,
                    'cash_sales': 0,
                    'card_sales': 0,
                    'wallet_sales': 0
                }
                
        except Exception as e:
            print(f"خطأ في الحصول على ملخص المبيعات: {str(e)}")
            return {}
    
    def create_return(self, sale_id: int, return_items: List[Dict],
                     reason: str = "", user_id: int = None) -> Optional[int]:
        """إنشاء مرتجع"""
        try:
            # حساب إجمالي المرتجع
            total_return_amount = sum(
                item['quantity'] * item['unit_price'] 
                for item in return_items
            )
            
            # إنشاء المرتجع
            return_id = self.db.execute_insert("""
                INSERT INTO returns (sale_id, total_amount, reason, user_id)
                VALUES (?, ?, ?, ?)
            """, (sale_id, total_return_amount, reason, user_id))
            
            if not return_id:
                return None
            
            # إضافة عناصر المرتجع
            for item in return_items:
                # إضافة عنصر المرتجع
                self.db.execute_insert("""
                    INSERT INTO return_items 
                    (return_id, product_id, quantity, unit_price, total_amount, condition_status)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (return_id, item['product_id'], item['quantity'],
                      item['unit_price'], item['quantity'] * item['unit_price'],
                      item.get('condition_status', 'good')))
                
                # إعادة المنتج للمخزون إذا كان بحالة جيدة
                if item.get('condition_status', 'good') == 'good':
                    self._update_product_stock(item['product_id'], item['quantity'])
                    
                    # تسجيل حركة المخزون
                    self._add_stock_movement(
                        item['product_id'], 'in', item['quantity'],
                        return_id, 'return', user_id
                    )
            
            return return_id
            
        except Exception as e:
            print(f"خطأ في إنشاء المرتجع: {str(e)}")
            return None
    
    def _update_product_stock(self, product_id: int, quantity_change: int):
        """تحديث مخزون المنتج"""
        self.db.execute_update("""
            UPDATE products 
            SET quantity_in_stock = quantity_in_stock + ?,
                updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (quantity_change, product_id))
    
    def _add_stock_movement(self, product_id: int, movement_type: str, 
                          quantity: int, reference_id: int, 
                          reference_type: str, user_id: int):
        """إضافة حركة مخزون"""
        self.db.execute_insert("""
            INSERT INTO stock_movements 
            (product_id, movement_type, quantity, reference_id, 
             reference_type, user_id)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (product_id, movement_type, quantity, reference_id,
              reference_type, user_id))


class Customer:
    """فئة العميل"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def get_or_create_customer(self, name: str = None, phone: str = None,
                             email: str = None, address: str = None) -> Optional[int]:
        """الحصول على العميل أو إنشاء جديد"""
        try:
            # البحث عن العميل بالهاتف أولاً
            if phone:
                result = self.db.execute_query(
                    "SELECT id FROM customers WHERE phone = ?", (phone,)
                )
                if result:
                    return result[0]['id']
            
            # إنشاء عميل جديد
            if name or phone:
                return self.db.execute_insert("""
                    INSERT INTO customers (name, phone, email, address)
                    VALUES (?, ?, ?, ?)
                """, (name, phone, email, address))
            
            return None
            
        except Exception as e:
            from app.utils.logger import get_logger
            logger = get_logger('customer')
            logger.error(f"خطأ في الحصول على أو إنشاء العميل: {str(e)}")
            return None
               