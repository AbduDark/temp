#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
نموذج المستخدم - User Model
"""

import bcrypt
from datetime import datetime
from typing import Dict, List, Optional
from .database import DatabaseManager

class User:
    """فئة المستخدم"""
    
    def __init__(self, db: DatabaseManager = None):
        self.db = db if db else DatabaseManager()
    
    def authenticate(self, username: str, password: str) -> Optional[Dict]:
        """تسجيل دخول المستخدم"""
        try:
            result = self.db.execute_query(
                """SELECT id, username, password_hash, full_name, role, is_active 
                   FROM users WHERE username = ? AND is_active = 1""",
                (username,)
            )
            
            if result:
                user = dict(result[0])
                stored_hash = user['password_hash']
                
                # التحقق من كلمة المرور
                if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                    # إزالة كلمة المرور من النتيجة
                    del user['password_hash']
                    return user
            
            return None
            
        except Exception as e:
            print(f"خطأ في المصادقة: {str(e)}")
            return None
    
    def create_user(self, username: str, password: str, full_name: str, 
                   role: str = "Cashier") -> bool:
        """إنشاء مستخدم جديد"""
        try:
            # تشفير كلمة المرور
            password_hash = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
            
            self.db.execute_insert(
                """INSERT INTO users (username, password_hash, full_name, role)
                   VALUES (?, ?, ?, ?)""",
                (username, password_hash.decode('utf-8'), full_name, role)
            )
            return True
            
        except Exception as e:
            print(f"خطأ في إنشاء المستخدم: {str(e)}")
            return False
    
    def get_all_users(self) -> List[Dict]:
        """الحصول على جميع المستخدمين"""
        try:
            result = self.db.execute_query(
                """SELECT id, username, full_name, role, is_active, created_at
                   FROM users ORDER BY created_at DESC"""
            )
            return [dict(row) for row in result]
            
        except Exception as e:
            print(f"خطأ في الحصول على المستخدمين: {str(e)}")
            return []
    
    def update_user(self, user_id: int, **kwargs) -> bool:
        """تحديث بيانات المستخدم"""
        try:
            update_fields = []
            params = []
            
            for field, value in kwargs.items():
                if field == 'password':
                    # تشفير كلمة المرور الجديدة
                    password_hash = bcrypt.hashpw(value.encode('utf-8'), bcrypt.gensalt())
                    update_fields.append("password_hash = ?")
                    params.append(password_hash.decode('utf-8'))
                elif field in ['username', 'full_name', 'role', 'is_active']:
                    update_fields.append(f"{field} = ?")
                    params.append(value)
            
            if update_fields:
                update_fields.append("updated_at = CURRENT_TIMESTAMP")
                params.append(user_id)
                
                query = f"UPDATE users SET {', '.join(update_fields)} WHERE id = ?"
                self.db.execute_update(query, tuple(params))
                return True
            
            return False
            
        except Exception as e:
            print(f"خطأ في تحديث المستخدم: {str(e)}")
            return False
    
    def delete_user(self, user_id: int) -> bool:
        """حذف المستخدم (تعطيل)"""
        try:
            self.db.execute_update(
                "UPDATE users SET is_active = 0, updated_at = CURRENT_TIMESTAMP WHERE id = ?",
                (user_id,)
            )
            return True
            
        except Exception as e:
            print(f"خطأ في حذف المستخدم: {str(e)}")
            return False
    
    def get_user_by_id(self, user_id: int) -> Optional[Dict]:
        """الحصول على مستخدم بالمعرف"""
        try:
            result = self.db.execute_query(
                """SELECT id, username, full_name, role, is_active, created_at
                   FROM users WHERE id = ?""",
                (user_id,)
            )
            return dict(result[0]) if result else None
            
        except Exception as e:
            print(f"خطأ في الحصول على المستخدم: {str(e)}")
            return None
