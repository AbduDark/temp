#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة إدارة المخزون - Inventory Service
"""

from typing import Dict, List, Optional, Tuple
from app.models.database import DatabaseManager
from app.models.product import Product, Category
import logging

logger = logging.getLogger(__name__)

class InventoryService:
    """خدمة إدارة المخزون"""
    
    def __init__(self, auth_service=None):
        self.db = DatabaseManager()
        self.product_model = Product(self.db)
        self.category_model = Category(self.db)
        self.auth_service = auth_service
    
    def get_all_products(self) -> List[Dict]:
        """الحصول على جميع المنتجات"""
        return self.product_model.get_all_products()
    
    def get_product_by_id(self, product_id: int) -> Optional[Dict]:
        """الحصول على منتج بالمعرف"""
        return self.product_model.get_product_by_id(product_id)
    
    def search_products(self, search_term: str) -> List[Dict]:
        """البحث عن المنتجات"""
        return self.product_model.search_products(search_term)
    
    def create_product(self, name: str, category_id: int, selling_price: float,
                      cost_price: float = 0, barcode: str = "", 
                      quantity: int = 0, minimum_stock: int = 5,
                      description: str = "") -> int:
        """إنشاء منتج جديد"""
        if self.auth_service and not self.auth_service.has_permission('manage_products'):
            return 0
        
        try:
            product_id = self.product_model.create_product(
                name, category_id, selling_price, cost_price,
                barcode, quantity, minimum_stock, description
            )
            
            if product_id and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'create_product', 
                        'products', product_id, f"إنشاء منتج جديد: {name}"
                    )
            
            return product_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء المنتج: {str(e)}")
            return 0
    
    def update_product(self, product_id: int, **kwargs) -> bool:
        """تحديث بيانات المنتج"""
        if self.auth_service and not self.auth_service.has_permission('manage_products'):
            return False
        
        try:
            success = self.product_model.update_product(product_id, **kwargs)
            
            if success and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'update_product', 
                        'products', product_id, f"تحديث بيانات المنتج"
                    )
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث المنتج: {str(e)}")
            return False
    
    def adjust_stock(self, product_id: int, new_quantity: int, 
                    reason: str = "") -> bool:
        """تعديل المخزون يدوياً"""
        if self.auth_service and not self.auth_service.has_permission('update_stock'):
            return False
        
        try:
            user_id = None
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    user_id = current_user['id']
            
            success = self.product_model.adjust_stock(
                product_id, new_quantity, reason, user_id
            )
            
            if success and self.auth_service:
                self.auth_service.log_user_activity(
                    user_id, 'adjust_stock', 'products', 
                    product_id, f"تعديل المخزون: {reason}"
                )
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تعديل المخزون: {str(e)}")
            return False
    
    def get_low_stock_products(self) -> List[Dict]:
        """الحصول على المنتجات ذات المخزون المنخفض"""
        return self.product_model.get_low_stock_products()
    
    def get_stock_movements(self, product_id: int = None, 
                          start_date: str = None, end_date: str = None) -> List[Dict]:
        """الحصول على حركات المخزون"""
        return self.product_model.get_stock_movements(product_id, start_date, end_date)
    
    def get_all_categories(self) -> List[Dict]:
        """الحصول على جميع الفئات"""
        return self.category_model.get_all_categories()
    
    def create_category(self, name: str, description: str = "") -> int:
        """إنشاء فئة جديدة"""
        if self.auth_service and not self.auth_service.has_permission('manage_categories'):
            return 0
        
        try:
            category_id = self.category_model.create_category(name, description)
            
            if category_id and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'create_category', 
                        'categories', category_id, f"إنشاء فئة جديدة: {name}"
                    )
            
            return category_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء الفئة: {str(e)}")
            return 0
    
    def get_inventory_summary(self) -> Dict:
        """الحصول على ملخص المخزون"""
        try:
            # إجمالي المنتجات
            total_products = self.db.execute_query(
                "SELECT COUNT(*) as count FROM products WHERE is_active = 1"
            )
            
            # إجمالي قيمة المخزون
            inventory_value = self.db.execute_query("""
                SELECT 
                    SUM(quantity_in_stock * cost_price) as total_cost_value,
                    SUM(quantity_in_stock * selling_price) as total_selling_value
                FROM products WHERE is_active = 1
            """)
            
            # المنتجات منخفضة المخزون
            low_stock_count = self.db.execute_query("""
                SELECT COUNT(*) as count FROM products 
                WHERE is_active = 1 AND quantity_in_stock <= minimum_stock
            """)
            
            # المنتجات نفدت من المخزون
            out_of_stock_count = self.db.execute_query("""
                SELECT COUNT(*) as count FROM products 
                WHERE is_active = 1 AND quantity_in_stock = 0
            """)
            
            return {
                'total_products': total_products[0]['count'] if total_products else 0,
                'total_cost_value': inventory_value[0]['total_cost_value'] if inventory_value and inventory_value[0]['total_cost_value'] else 0,
                'total_selling_value': inventory_value[0]['total_selling_value'] if inventory_value and inventory_value[0]['total_selling_value'] else 0,
                'low_stock_count': low_stock_count[0]['count'] if low_stock_count else 0,
                'out_of_stock_count': out_of_stock_count[0]['count'] if out_of_stock_count else 0
            }
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على ملخص المخزون: {str(e)}")
            return {}
    
    def get_top_selling_products(self, start_date: str = None, 
                               end_date: str = None, limit: int = 10) -> List[Dict]:
        """الحصول على أكثر المنتجات مبيعاً"""
        try:
            query = """
                SELECT p.name, p.selling_price, SUM(si.quantity) as total_sold,
                       SUM(si.total_amount) as total_revenue
                FROM products p
                INNER JOIN sale_items si ON p.id = si.product_id
                INNER JOIN sales s ON si.sale_id = s.id
                WHERE s.status = 'completed'
            """
            params = []
            
            if start_date:
                query += " AND DATE(s.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(s.created_at) <= ?"
                params.append(end_date)
            
            query += """
                GROUP BY p.id, p.name, p.selling_price
                ORDER BY total_sold DESC
                LIMIT ?
            """
            params.append(limit)
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على أكثر المنتجات مبيعاً: {str(e)}")
            return []
    
    def bulk_update_prices(self, updates: List[Dict]) -> bool:
        """تحديث الأسعار بالجملة"""
        if self.auth_service and not self.auth_service.has_permission('manage_products'):
            return False
        
        try:
            user_id = None
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    user_id = current_user['id']
            
            for update in updates:
                product_id = update.get('product_id')
                new_price = update.get('new_price')
                price_type = update.get('price_type', 'selling')  # selling or cost
                
                if product_id and new_price is not None:
                    field = 'selling_price' if price_type == 'selling' else 'cost_price'
                    
                    self.db.execute_update(
                        f"UPDATE products SET {field} = ?, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                        (new_price, product_id)
                    )
                    
                    if self.auth_service:
                        self.auth_service.log_user_activity(
                            user_id, 'bulk_update_prices', 'products', 
                            product_id, f"تحديث سعر {price_type}: {new_price}"
                        )
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في التحديث الجماعي للأسعار: {str(e)}")
            return False
