#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج الصيانة - Repair Model
"""

from datetime import datetime
from typing import Dict, List, Optional
from .database import DatabaseManager

class RepairTicket:
    """فئة تذكرة الصيانة"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def create_ticket(self, customer_id: Optional[int], device_info: str,
                     problem_description: str, repair_type: str,
                     estimated_cost: float = 0, imei: str = "",
                     technician_id: int = None, notes: str = "",
                     user_id: int = None) -> Optional[int]:
        """إنشاء تذكرة صيانة جديدة"""
        try:
            ticket_id = self.db.execute_insert("""
                INSERT INTO repair_tickets 
                (customer_id, device_info, imei, problem_description, 
                 repair_type, estimated_cost, technician_id, notes, user_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (customer_id, device_info, imei, problem_description,
                  repair_type, estimated_cost, technician_id, notes, user_id))
            
            return ticket_id
            
        except Exception as e:
            print(f"خطأ في إنشاء تذكرة الصيانة: {str(e)}")
            return None
    
    def get_ticket_by_id(self, ticket_id: int) -> Optional[Dict]:
        """الحصول على تذكرة صيانة بالمعرف"""
        try:
            result = self.db.execute_query("""
                SELECT rt.*, 
                       c.name as customer_name, c.phone as customer_phone,
                       t.full_name as technician_name,
                       u.full_name as created_by
                FROM repair_tickets rt
                LEFT JOIN customers c ON rt.customer_id = c.id
                LEFT JOIN users t ON rt.technician_id = t.id
                LEFT JOIN users u ON rt.user_id = u.id
                WHERE rt.id = ?
            """, (ticket_id,))
            
            if not result:
                return None
            
            ticket = dict(result[0])
            
            # الحصول على قطع الغيار المستخدمة
            parts_result = self.db.execute_query("""
                SELECT rp.*, p.name as product_name
                FROM repair_parts rp
                LEFT JOIN products p ON rp.product_id = p.id
                WHERE rp.repair_id = ?
            """, (ticket_id,))
            
            ticket['parts_used'] = [dict(row) for row in parts_result]
            
            return ticket
            
        except Exception as e:
            print(f"خطأ في الحصول على تذكرة الصيانة: {str(e)}")
            return None
    
    def get_tickets_list(self, status: str = None, technician_id: int = None,
                        start_date: str = None, end_date: str = None,
                        limit: int = 100) -> List[Dict]:
        """الحصول على قائمة تذاكر الصيانة"""
        try:
            query = """
                SELECT rt.*, 
                       c.name as customer_name, c.phone as customer_phone,
                       t.full_name as technician_name
                FROM repair_tickets rt
                LEFT JOIN customers c ON rt.customer_id = c.id
                LEFT JOIN users t ON rt.technician_id = t.id
                WHERE 1=1
            """
            params = []
            
            if status:
                query += " AND rt.status = ?"
                params.append(status)
            
            if technician_id:
                query += " AND rt.technician_id = ?"
                params.append(technician_id)
            
            if start_date:
                query += " AND DATE(rt.received_date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(rt.received_date) <= ?"
                params.append(end_date)
            
            query += " ORDER BY rt.received_date DESC LIMIT ?"
            params.append(limit)
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"خطأ في الحصول على قائمة التذاكر: {str(e)}")
            return []
    
    def update_ticket_status(self, ticket_id: int, status: str,
                           final_cost: float = None, completed_date: str = None,
                           notes: str = "", user_id: int = None) -> bool:
        """تحديث حالة التذكرة"""
        try:
            update_fields = ["status = ?", "updated_at = CURRENT_TIMESTAMP"]
            params = [status]
            
            if final_cost is not None:
                update_fields.append("final_cost = ?")
                params.append(final_cost)
            
            if completed_date:
                update_fields.append("completed_date = ?")
                params.append(completed_date)
            elif status == 'completed':
                update_fields.append("completed_date = CURRENT_TIMESTAMP")
            
            if notes:
                update_fields.append("notes = ?")
                params.append(notes)
            
            params.append(ticket_id)
            
            query = f"UPDATE repair_tickets SET {', '.join(update_fields)} WHERE id = ?"
            
            rows_affected = self.db.execute_update(query, tuple(params))
            return rows_affected > 0
            
        except Exception as e:
            print(f"خطأ في تحديث حالة التذكرة: {str(e)}")
            return False
    
    def add_repair_part(self, ticket_id: int, product_id: int, 
                       quantity: int, unit_price: float) -> bool:
        """إضافة قطعة غيار للتذكرة"""
        try:
            total_price = quantity * unit_price
            
            # إضافة قطعة الغيار
            self.db.execute_insert("""
                INSERT INTO repair_parts 
                (repair_id, product_id, quantity, unit_price, total_price)
                VALUES (?, ?, ?, ?, ?)
            """, (ticket_id, product_id, quantity, unit_price, total_price))
            
            # تحديث المخزون
            self.db.execute_update("""
                UPDATE products 
                SET quantity_in_stock = quantity_in_stock - ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quantity, product_id))
            
            # تسجيل حركة المخزون
            self.db.execute_insert("""
                INSERT INTO stock_movements 
                (product_id, movement_type, quantity, reference_id, 
                 reference_type, notes)
                VALUES (?, ?, ?, ?, ?, ?)
            """, (product_id, 'out', quantity, ticket_id,
                  'repair', f'استخدام في الصيانة - تذكرة #{ticket_id}'))
            
            return True
            
        except Exception as e:
            print(f"خطأ في إضافة قطعة الغيار: {str(e)}")
            return False
    
    def remove_repair_part(self, part_id: int) -> bool:
        """إزالة قطعة غيار من التذكرة"""
        try:
            # الحصول على بيانات قطعة الغيار
            result = self.db.execute_query(
                "SELECT product_id, quantity FROM repair_parts WHERE id = ?",
                (part_id,)
            )
            
            if not result:
                return False
            
            product_id = result[0]['product_id']
            quantity = result[0]['quantity']
            
            # حذف قطعة الغيار
            self.db.execute_update(
                "DELETE FROM repair_parts WHERE id = ?", (part_id,)
            )
            
            # إعادة القطعة للمخزون
            self.db.execute_update("""
                UPDATE products 
                SET quantity_in_stock = quantity_in_stock + ?,
                    updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (quantity, product_id))
            
            # تسجيل حركة المخزون
            self.db.execute_insert("""
                INSERT INTO stock_movements 
                (product_id, movement_type, quantity, reference_type, notes)
                VALUES (?, ?, ?, ?, ?)
            """, (product_id, 'in', quantity, 'repair_return',
                  f'إعادة قطعة غيار من الصيانة'))
            
            return True
            
        except Exception as e:
            print(f"خطأ في إزالة قطعة الغيار: {str(e)}")
            return False
    
    def get_technician_stats(self, technician_id: int, 
                           start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على إحصائيات الفني"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tickets,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tickets,
                    AVG(CASE 
                        WHEN completed_date IS NOT NULL AND received_date IS NOT NULL 
                        THEN julianday(completed_date) - julianday(received_date) 
                        END) as avg_completion_days
                FROM repair_tickets 
                WHERE technician_id = ?
            """
            params = [technician_id]
            
            if start_date:
                query += " AND DATE(received_date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(received_date) <= ?"
                params.append(end_date)
            
            result = self.db.execute_query(query, tuple(params))
            
            if result:
                stats = dict(result[0])
                # تحويل متوسط الأيام إلى رقم صحيح
                if stats['avg_completion_days']:
                    stats['avg_completion_days'] = round(stats['avg_completion_days'])
                return stats
            else:
                return {
                    'total_tickets': 0,
                    'completed_tickets': 0,
                    'in_progress_tickets': 0,
                    'avg_completion_days': 0
                }
                
        except Exception as e:
            print(f"خطأ في الحصول على إحصائيات الفني: {str(e)}")
            return {}
    
    def get_repair_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على ملخص الصيانة"""
        try:
            query = """
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'received' THEN 1 END) as received_tickets,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tickets,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tickets,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_tickets,
                    SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as total_revenue
                FROM repair_tickets
                WHERE 1=1
            """
            params = []
            
            if start_date:
                query += " AND DATE(received_date) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(received_date) <= ?"
                params.append(end_date)
            
            result = self.db.execute_query(query, tuple(params))
            
            if result:
                return dict(result[0])
            else:
                return {
                    'total_tickets': 0,
                    'received_tickets': 0,
                    'in_progress_tickets': 0,
                    'completed_tickets': 0,
                    'delivered_tickets': 0,
                    'total_revenue': 0
                }
                
        except Exception as e:
            print(f"خطأ في الحصول على ملخص الصيانة: {str(e)}")
            return {}
