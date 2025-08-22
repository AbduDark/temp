#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة نقاط البيع - POS Service
"""

from typing import Dict, List, Optional, Tuple
from decimal import Decimal, ROUND_HALF_UP
from app.models.database import DatabaseManager
from app.models.sale import Sale, Customer
import logging

logger = logging.getLogger(__name__)

class POSService:
    """خدمة نقاط البيع"""
    
    def __init__(self, auth_service=None):
        self.db = DatabaseManager()
        self.sale_model = Sale(self.db)
        self.customer_model = Customer(self.db)
        self.auth_service = auth_service
    
    def create_sale(self, items: List[Dict], payment_method: str,
                   customer_info: Dict = None, discount_amount: float = 0,
                   notes: str = "") -> Optional[Dict]:
        """إنشاء فاتورة مبيعات"""
        if self.auth_service and not self.auth_service.has_permission('create_sale'):
            return None
        
        try:
            # التحقق من صحة البيانات
            if not items:
                raise ValueError("لا يمكن إنشاء فاتورة بدون عناصر")
            
            # التحقق من توفر المخزون
            for item in items:
                product = self._get_product_info(item['product_id'])
                if not product:
                    raise ValueError(f"المنتج غير موجود: {item['product_id']}")
                
                if product['quantity_in_stock'] < item['quantity']:
                    raise ValueError(f"المخزون غير كافٍ للمنتج: {product['name']}")
            
            # إنشاء/الحصول على معرف العميل
            customer_id = None
            if customer_info and (customer_info.get('name') or customer_info.get('phone')):
                customer_id = self.customer_model.get_or_create_customer(**customer_info)
            
            # الحصول على معرف المستخدم
            user_id = None
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    user_id = current_user['id']
            
            # إنشاء الفاتورة
            sale_id = self.sale_model.create_sale(
                customer_id, items, payment_method, 
                discount_amount, notes, user_id
            )
            
            if sale_id:
                # تسجيل النشاط
                if self.auth_service:
                    self.auth_service.log_user_activity(
                        user_id, 'create_sale', 'sales', sale_id,
                        f"إنشاء فاتورة مبيعات - المبلغ: {self._calculate_final_amount(items, discount_amount)}"
                    )
                
                # إرجاع بيانات الفاتورة
                return self.get_sale_by_id(sale_id)
            
            return None
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء فاتورة المبيعات: {str(e)}")
            return None
    
    def get_sale_by_id(self, sale_id: int) -> Optional[Dict]:
        """الحصول على فاتورة مبيعات بالمعرف"""
        return self.sale_model.get_sale_by_id(sale_id)
    
    def search_sales(self, search_term: str = "", start_date: str = None,
                    end_date: str = None, payment_method: str = None,
                    limit: int = 100) -> List[Dict]:
        """البحث عن المبيعات"""
        try:
            query = """
                SELECT s.*, c.name as customer_name, c.phone as customer_phone,
                       u.full_name as user_name
                FROM sales s
                LEFT JOIN customers c ON s.customer_id = c.id
                LEFT JOIN users u ON s.user_id = u.id
                WHERE s.status = 'completed'
            """
            params = []
            
            if search_term:
                query += """ AND (
                    c.name LIKE ? OR 
                    c.phone LIKE ? OR 
                    s.id = ? OR
                    s.notes LIKE ?
                )"""
                search_pattern = f"%{search_term}%"
                params.extend([search_pattern, search_pattern, search_term, search_pattern])
            
            if start_date:
                query += " AND DATE(s.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(s.created_at) <= ?"
                params.append(end_date)
            
            if payment_method:
                query += " AND s.payment_method = ?"
                params.append(payment_method)
            
            query += " ORDER BY s.created_at DESC LIMIT ?"
            params.append(limit)
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن المبيعات: {str(e)}")
            return []
    
    def create_return(self, sale_id: int, return_items: List[Dict],
                     reason: str = "") -> Optional[int]:
        """إنشاء مرتجع"""
        if self.auth_service and not self.auth_service.has_permission('create_return'):
            return None
        
        try:
            # التحقق من صحة الفاتورة
            sale = self.sale_model.get_sale_by_id(sale_id)
            if not sale:
                raise ValueError("الفاتورة غير موجودة")
            
            # التحقق من صحة عناصر المرتجع
            for return_item in return_items:
                # البحث عن العنصر في الفاتورة الأصلية
                original_item = None
                for item in sale['items']:
                    if item['product_id'] == return_item['product_id']:
                        original_item = item
                        break
                
                if not original_item:
                    raise ValueError(f"المنتج غير موجود في الفاتورة الأصلية")
                
                if return_item['quantity'] > original_item['quantity']:
                    raise ValueError(f"كمية المرتجع أكبر من الكمية الأصلية")
            
            # الحصول على معرف المستخدم
            user_id = None
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    user_id = current_user['id']
            
            # إنشاء المرتجع
            return_id = self.sale_model.create_return(
                sale_id, return_items, reason, user_id
            )
            
            if return_id and self.auth_service:
                total_return = sum(item['quantity'] * item['unit_price'] for item in return_items)
                self.auth_service.log_user_activity(
                    user_id, 'create_return', 'returns', return_id,
                    f"إنشاء مرتجع - المبلغ: {total_return}"
                )
            
            return return_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المرتجع: {str(e)}")
            return None
    
    def get_daily_sales_summary(self, date: str) -> Dict:
        """الحصول على ملخص مبيعات اليوم"""
        return self.sale_model.get_daily_sales_summary(date)
    
    def get_payment_methods(self) -> List[str]:
        """الحصول على وسائل الدفع المتاحة"""
        return [
            'cash',           # نقد
            'card',           # بطاقة
            'vodafone_cash',  # فودافون كاش
            'etisalat_wallet', # اتصالات محفظة
            'we_pay',         # WePay
            'insta_pay',      # InstaPay
            'points'          # نقاط داخلية
        ]
    
    def get_payment_method_name(self, method: str) -> str:
        """الحصول على اسم وسيلة الدفع بالعربية"""
        names = {
            'cash': 'نقد',
            'card': 'بطاقة',
            'vodafone_cash': 'فودافون كاش',
            'etisalat_wallet': 'اتصالات محفظة',
            'we_pay': 'WePay',
            'insta_pay': 'InstaPay',
            'points': 'نقاط داخلية'
        }
        return names.get(method, method)
    
    def calculate_sale_total(self, items: List[Dict], discount_amount: float = 0) -> Dict:
        """حساب إجمالي الفاتورة"""
        try:
            subtotal = sum(item['quantity'] * item['price'] for item in items)
            
            # حساب الضريبة
            tax_rate = float(self.db.get_setting('tax_rate') or 0) / 100
            tax_amount = (subtotal - discount_amount) * tax_rate
            
            # المبلغ النهائي
            final_amount = subtotal - discount_amount + tax_amount
            
            return {
                'subtotal': round(subtotal, 2),
                'discount_amount': round(discount_amount, 2),
                'tax_rate': tax_rate * 100,
                'tax_amount': round(tax_amount, 2),
                'final_amount': round(final_amount, 2)
            }
            
        except Exception as e:
            logger.error(f"خطأ في حساب إجمالي الفاتورة: {str(e)}")
            return {}
    
    def _get_product_info(self, product_id: int) -> Optional[Dict]:
        """الحصول على معلومات المنتج"""
        try:
            result = self.db.execute_query("""
                SELECT id, name, selling_price, quantity_in_stock, is_active
                FROM products WHERE id = ? AND is_active = 1
            """, (product_id,))
            
            return dict(result[0]) if result else None
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على معلومات المنتج: {str(e)}")
            return None
    
    def _calculate_final_amount(self, items: List[Dict], discount_amount: float = 0) -> float:
        """حساب المبلغ النهائي"""
        subtotal = sum(item['quantity'] * item['price'] for item in items)
        tax_rate = float(self.db.get_setting('tax_rate') or 0) / 100
        tax_amount = (subtotal - discount_amount) * tax_rate
        return round(subtotal - discount_amount + tax_amount, 2)
    
    def search_customers(self, search_term: str) -> List[Dict]:
        """البحث عن العملاء"""
        return self.customer_model.search_customers(search_term)
    
    def get_recent_sales(self, limit: int = 10) -> List[Dict]:
        """الحصول على المبيعات الأخيرة"""
        return self.sale_model.get_sales_list(limit=limit)
    
    def void_sale(self, sale_id: int, reason: str = "") -> bool:
        """إلغاء فاتورة مبيعات"""
        if self.auth_service and not self.auth_service.has_permission('void_sale'):
            return False
        
        try:
            # الحصول على بيانات الفاتورة
            sale = self.sale_model.get_sale_by_id(sale_id)
            if not sale or sale['status'] != 'completed':
                return False
            
            # إرجاع المخزون
            for item in sale['items']:
                self.db.execute_update("""
                    UPDATE products 
                    SET quantity_in_stock = quantity_in_stock + ?,
                        updated_at = CURRENT_TIMESTAMP
                    WHERE id = ?
                """, (item['quantity'], item['product_id']))
                
                # تسجيل حركة المخزون
                self.db.execute_insert("""
                    INSERT INTO stock_movements 
                    (product_id, movement_type, quantity, reference_id, 
                     reference_type, notes)
                    VALUES (?, ?, ?, ?, ?, ?)
                """, (item['product_id'], 'in', item['quantity'], sale_id,
                      'sale_void', f'إلغاء فاتورة #{sale_id}: {reason}'))
            
            # تغيير حالة الفاتورة
            self.db.execute_update(
                "UPDATE sales SET status = 'void', notes = ? WHERE id = ?",
                (f"ملغاة: {reason}", sale_id)
            )
            
            # تسجيل النشاط
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'void_sale', 'sales', sale_id,
                        f"إلغاء فاتورة مبيعات: {reason}"
                    )
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إلغاء الفاتورة: {str(e)}")
            return False
