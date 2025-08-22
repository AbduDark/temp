#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة المصادقة - Authentication Service
"""

from typing import Dict, List, Optional
from app.models.database import DatabaseManager
from app.models.user import User
import logging

logger = logging.getLogger(__name__)

class AuthService:
    """خدمة المصادقة وإدارة المستخدمين"""
    
    def __init__(self):
        self.db = DatabaseManager()
        self.user_model = User(self.db)
        self._current_user = None
    
    def login(self, username: str, password: str) -> Optional[Dict]:
        """تسجيل دخول المستخدم"""
        try:
            user = self.user_model.authenticate(username, password)
            if user:
                self._current_user = user
                self.log_user_activity(user['id'], 'login', 'users', user['id'])
                logger.info(f"تم تسجيل دخول المستخدم: {username}")
            return user
        except Exception as e:
            logger.error(f"خطأ في تسجيل الدخول: {str(e)}")
            return None
    
    def logout(self):
        """تسجيل خروج المستخدم"""
        if self._current_user:
            self.log_user_activity(
                self._current_user['id'], 'logout', 
                'users', self._current_user['id']
            )
            logger.info(f"تم تسجيل خروج المستخدم: {self._current_user['username']}")
            self._current_user = None
    
    def get_current_user(self) -> Optional[Dict]:
        """الحصول على المستخدم الحالي"""
        return self._current_user
    
    def has_permission(self, permission: str) -> bool:
        """التحقق من صلاحية المستخدم"""
        if not self._current_user:
            return False
        
        role = self._current_user['role']
        
        # صلاحيات المدير الكاملة
        if role == 'Admin':
            return True
        
        # صلاحيات الكاشير
        if role == 'Cashier':
            cashier_permissions = [
                'create_sale', 'view_sales', 'create_return',
                'view_products', 'update_stock', 'create_customer',
                'view_reports_basic'
            ]
            return permission in cashier_permissions
        
        # صلاحيات الفني
        if role == 'Technician':
            technician_permissions = [
                'create_repair', 'update_repair', 'view_repairs',
                'view_products', 'use_parts'
            ]
            return permission in technician_permissions
        
        return False
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str = "Cashier") -> bool:
        """إنشاء مستخدم جديد"""
        if not self.has_permission('manage_users'):
            return False
        
        try:
            success = self.user_model.create_user(username, password, full_name, role)
            if success:
                self.log_user_activity(
                    self._current_user['id'], 'create_user', 
                    'users', None, f"إنشاء مستخدم جديد: {username}"
                )
            return success
        except Exception as e:
            logger.error(f"خطأ في إنشاء المستخدم: {str(e)}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        if not self.has_permission('manage_users'):
            return []
        
        return self.user_model.get_all_users()
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """تحديث بيانات المستخدم"""
        if not self.has_permission('manage_users'):
            return False
        
        try:
            success = self.user_model.update_user(user_id, **kwargs)
            if success:
                self.log_user_activity(
                    self._current_user['id'], 'update_user', 
                    'users', user_id, f"تحديث بيانات المستخدم"
                )
            return success
        except Exception as e:
            logger.error(f"خطأ في تحديث المستخدم: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """حذف المستخدم (تعطيل)"""
        if not self.has_permission('manage_users'):
            return False
        
        # منع حذف نفسه
        if self._current_user and user_id == self._current_user['id']:
            return False
        
        try:
            success = self.user_model.delete_user(user_id)
            if success:
                self.log_user_activity(
                    self._current_user['id'], 'delete_user', 
                    'users', user_id, f"تعطيل المستخدم"
                )
            return success
        except Exception as e:
            logger.error(f"خطأ في حذف المستخدم: {str(e)}")
            return False
    
    def log_user_activity(self, user_id: int, action: str, table_name: str = None,
                         record_id: int = None, notes: str = None):
        """تسجيل نشاط المستخدم"""
        try:
            self.db.execute_insert("""
                INSERT INTO audit_logs (user_id, action, table_name, record_id, new_values)
                VALUES (?, ?, ?, ?, ?)
            """, (user_id, action, table_name, record_id, notes))
        except Exception as e:
            logger.error(f"خطأ في تسجيل نشاط المستخدم: {str(e)}")
    
    def get_user_activity_log(self, user_id: int = None, 
                            start_date: str = None, end_date: str = None,
                            limit: int = 100) -> List[Dict]:
        """الحصول على سجل نشاط المستخدمين"""
        if not self.has_permission('view_audit_log'):
            return []
        
        try:
            query = """
                SELECT al.*, u.full_name as user_name, u.username
                FROM audit_logs al
                LEFT JOIN users u ON al.user_id = u.id
                WHERE 1=1
            """
            params = []
            
            if user_id:
                query += " AND al.user_id = ?"
                params.append(user_id)
            
            if start_date:
                query += " AND DATE(al.created_at) >= ?"
                params.append(start_date)
            
            if end_date:
                query += " AND DATE(al.created_at) <= ?"
                params.append(end_date)
            
            query += " ORDER BY al.created_at DESC LIMIT ?"
            params.append(limit)
            
            result = self.db.execute_query(query, tuple(params))
            return [dict(row) for row in result]
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على سجل النشاط: {str(e)}")
            return []
