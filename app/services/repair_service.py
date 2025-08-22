#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة الصيانة - Repair Service
"""

from typing import Dict, List, Optional
from datetime import datetime, date
from app.models.database import DatabaseManager
from app.models.repair import RepairTicket
from app.models.sale import Customer
import logging

logger = logging.getLogger(__name__)

class RepairService:
    """خدمة إدارة الصيانة"""
    
    def __init__(self, auth_service=None):
        self.db = DatabaseManager()
        self.repair_model = RepairTicket(self.db)
        self.customer_model = Customer(self.db)
        self.auth_service = auth_service
    
    def create_repair_ticket(self, customer_info: Dict, device_info: str,
                           problem_description: str, repair_type: str,
                           estimated_cost: float = 0, imei: str = "",
                           technician_id: int = None, notes: str = "") -> Optional[int]:
        """إنشاء تذكرة صيانة جديدة"""
        if self.auth_service and not self.auth_service.has_permission('create_repair'):
            return None
        
        try:
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
            
            # إنشاء التذكرة
            ticket_id = self.repair_model.create_ticket(
                customer_id, device_info, problem_description, repair_type,
                estimated_cost, imei, technician_id, notes, user_id
            )
            
            if ticket_id and self.auth_service:
                self.auth_service.log_user_activity(
                    user_id, 'create_repair', 'repair_tickets', ticket_id,
                    f"إنشاء تذكرة صيانة: {device_info}"
                )
            
            return ticket_id
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء تذكرة الصيانة: {str(e)}")
            return None
    
    def get_repair_ticket(self, ticket_id: int) -> Optional[Dict]:
        """الحصول على تذكرة صيانة بالمعرف"""
        return self.repair_model.get_ticket_by_id(ticket_id)
    
    def get_repair_tickets(self, status: str = None, technician_id: int = None,
                         start_date: str = None, end_date: str = None,
                         limit: int = 100) -> List[Dict]:
        """الحصول على قائمة تذاكر الصيانة"""
        return self.repair_model.get_tickets_list(
            status, technician_id, start_date, end_date, limit
        )
    
    def update_ticket_status(self, ticket_id: int, status: str,
                           final_cost: float = None, notes: str = "") -> bool:
        """تحديث حالة التذكرة"""
        if self.auth_service and not self.auth_service.has_permission('update_repair'):
            return False
        
        try:
            completed_date = None
            if status == 'completed':
                completed_date = datetime.now().isoformat()
            
            success = self.repair_model.update_ticket_status(
                ticket_id, status, final_cost, completed_date, notes
            )
            
            if success and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'update_repair_status', 
                        'repair_tickets', ticket_id,
                        f"تحديث حالة التذكرة إلى: {self.get_status_name(status)}"
                    )
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في تحديث حالة التذكرة: {str(e)}")
            return False
    
    def add_repair_part(self, ticket_id: int, product_id: int, 
                       quantity: int, unit_price: float) -> bool:
        """إضافة قطعة غيار للتذكرة"""
        if self.auth_service and not self.auth_service.has_permission('use_parts'):
            return False
        
        try:
            # التحقق من توفر المخزون
            result = self.db.execute_query(
                "SELECT quantity_in_stock, name FROM products WHERE id = ? AND is_active = 1",
                (product_id,)
            )
            
            if not result:
                raise ValueError("قطعة الغيار غير موجودة")
            
            product = dict(result[0])
            if product['quantity_in_stock'] < quantity:
                raise ValueError(f"المخزون غير كافٍ لقطعة الغيار: {product['name']}")
            
            success = self.repair_model.add_repair_part(
                ticket_id, product_id, quantity, unit_price
            )
            
            if success and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'add_repair_part', 
                        'repair_parts', None,
                        f"إضافة قطعة غيار للتذكرة #{ticket_id}: {product['name']}"
                    )
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إضافة قطعة الغيار: {str(e)}")
            return False
    
    def remove_repair_part(self, part_id: int) -> bool:
        """إزالة قطعة غيار من التذكرة"""
        if self.auth_service and not self.auth_service.has_permission('use_parts'):
            return False
        
        try:
            success = self.repair_model.remove_repair_part(part_id)
            
            if success and self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'remove_repair_part', 
                        'repair_parts', part_id,
                        f"إزالة قطعة غيار من الصيانة"
                    )
            
            return success
            
        except Exception as e:
            logger.error(f"خطأ في إزالة قطعة الغيار: {str(e)}")
            return False
    
    def search_repair_tickets(self, search_term: str) -> List[Dict]:
        """البحث عن تذاكر الصيانة"""
        try:
            search_pattern = f"%{search_term}%"
            result = self.db.execute_query("""
                SELECT rt.*, 
                       c.name as customer_name, c.phone as customer_phone,
                       t.full_name as technician_name
                FROM repair_tickets rt
                LEFT JOIN customers c ON rt.customer_id = c.id
                LEFT JOIN users t ON rt.technician_id = t.id
                WHERE (
                    rt.id = ? OR
                    rt.device_info LIKE ? OR
                    rt.imei LIKE ? OR
                    c.name LIKE ? OR
                    c.phone LIKE ?
                )
                ORDER BY rt.received_date DESC
                LIMIT 50
            """, (search_term, search_pattern, search_pattern, 
                  search_pattern, search_pattern))
            
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن تذاكر الصيانة: {str(e)}")
            return []
            
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في البحث عن تذاكر الصيانة: {str(e)}")
            return []
    
    def get_technician_workload(self, technician_id: int) -> Dict:
        """الحصول على عبء عمل الفني"""
        try:
            result = self.db.execute_query("""
                SELECT 
                    COUNT(CASE WHEN status = 'received' THEN 1 END) as received_count,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_count,
                    COUNT(CASE WHEN status = 'waiting_parts' THEN 1 END) as waiting_parts_count,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_today_count
                FROM repair_tickets 
                WHERE technician_id = ? 
                AND (status NOT IN ('delivered', 'cancelled') OR DATE(updated_at) = DATE('now'))
            """, (technician_id,))
            
            if result:
                return dict(result[0])
            else:
                return {
                    'received_count': 0,
                    'in_progress_count': 0,
                    'waiting_parts_count': 0,
                    'completed_today_count': 0
                }
                
        except Exception as e:
            logger.error(f"خطأ في الحصول على عبء عمل الفني: {str(e)}")
            return {}
    
    def get_repair_summary(self, start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على ملخص الصيانة"""
        return self.repair_model.get_repair_summary(start_date, end_date)
    
    def get_technician_stats(self, technician_id: int, 
                           start_date: str = None, end_date: str = None) -> Dict:
        """الحصول على إحصائيات الفني"""
        return self.repair_model.get_technician_stats(technician_id, start_date, end_date)
    
    def get_repair_types(self) -> List[str]:
        """الحصول على أنواع الصيانة"""
        return ['hardware', 'software']
    
    def get_repair_type_name(self, repair_type: str) -> str:
        """الحصول على اسم نوع الصيانة بالعربية"""
        names = {
            'hardware': 'هاردوير',
            'software': 'سوفتوير'
        }
        return names.get(repair_type, repair_type)
    
    def get_repair_statuses(self) -> List[str]:
        """الحصول على حالات الصيانة"""
        return ['received', 'in_progress', 'waiting_parts', 'completed', 'delivered', 'cancelled']
    
    def get_status_name(self, status: str) -> str:
        """الحصول على اسم الحالة بالعربية"""
        names = {
            'received': 'مستلمة',
            'in_progress': 'قيد العمل',
            'waiting_parts': 'انتظار قطع غيار',
            'completed': 'مكتملة',
            'delivered': 'مسلمة',
            'cancelled': 'ملغاة'
        }
        return names.get(status, status)
    
    def get_technicians(self) -> List[Dict]:
        """الحصول على قائمة الفنيين"""
        try:
            result = self.db.execute_query("""
                SELECT id, username, full_name
                FROM users 
                WHERE role IN ('Technician', 'Admin') AND is_active = 1
                ORDER BY full_name
            """)
            
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة الفنيين: {str(e)}")
            return []
    
    def calculate_repair_cost(self, ticket_id: int) -> float:
        """حساب تكلفة الصيانة الإجمالية"""
        try:
            # الحصول على التكلفة المقدرة
            ticket = self.repair_model.get_ticket_by_id(ticket_id)
            if not ticket:
                return 0
            
            estimated_cost = ticket.get('estimated_cost', 0) or 0
            
            # إضافة تكلفة قطع الغيار
            parts_cost = sum(part['total_price'] for part in ticket.get('parts_used', []))
            
            return estimated_cost + parts_cost
            
        except Exception as e:
            logger.error(f"خطأ في حساب تكلفة الصيانة: {str(e)}")
            return 0
