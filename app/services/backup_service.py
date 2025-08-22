#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة النسخ الاحتياطي - Backup Service
"""

import os
import shutil
import zipfile
import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
from app.models.database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class BackupService:
    """خدمة النسخ الاحتياطي والاستعادة"""
    
    def __init__(self, auth_service=None):
        self.db = DatabaseManager()
        self.auth_service = auth_service
        self.backup_dir = Path("backup")
        self.backup_dir.mkdir(exist_ok=True)
    
    def create_backup(self, backup_name: str = None, include_reports: bool = True) -> Optional[str]:
        """إنشاء نسخة احتياطية"""
        try:
            if not backup_name:
                timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
                backup_name = f"backup_{timestamp}"
            
            backup_path = self.backup_dir / f"{backup_name}.zip"
            
            with zipfile.ZipFile(backup_path, 'w', zipfile.ZIP_DEFLATED) as zipf:
                # نسخ قاعدة البيانات
                db_path = Path(self.db.db_path)
                if db_path.exists():
                    zipf.write(db_path, "data/shop.db")
                
                # نسخ ملفات التقارير إذا طُلب ذلك
                if include_reports:
                    reports_dir = Path("reports")
                    if reports_dir.exists():
                        for report_file in reports_dir.rglob("*"):
                            if report_file.is_file():
                                zipf.write(report_file, report_file)
                
                # نسخ الإعدادات والأصول
                assets_dir = Path("assets")
                if assets_dir.exists():
                    for asset_file in assets_dir.rglob("*"):
                        if asset_file.is_file():
                            zipf.write(asset_file, asset_file)
                
                # إضافة معلومات النسخة الاحتياطية
                backup_info = {
                    'created_at': datetime.now().isoformat(),
                    'version': '1.0.0',
                    'includes_reports': include_reports
                }
                
                if self.auth_service:
                    current_user = self.auth_service.get_current_user()
                    if current_user:
                        backup_info['created_by'] = current_user['username']
                
                import json
                zipf.writestr("backup_info.json", json.dumps(backup_info, indent=2))
            
            # تسجيل النشاط
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'create_backup', None, None,
                        f"إنشاء نسخة احتياطية: {backup_name}"
                    )
            
            logger.info(f"تم إنشاء النسخة الاحتياطية: {backup_path}")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"خطأ في إنشاء النسخة الاحتياطية: {str(e)}")
            return None
    
    def restore_backup(self, backup_path: str, restore_reports: bool = True) -> bool:
        """استعادة نسخة احتياطية"""
        try:
            backup_file = Path(backup_path)
            if not backup_file.exists():
                raise FileNotFoundError("ملف النسخة الاحتياطية غير موجود")
            
            # إنشاء نسخة احتياطية من البيانات الحالية قبل الاستعادة
            current_backup = self.create_backup("pre_restore_backup")
            if not current_backup:
                logger.warning("فشل في إنشاء نسخة احتياطية من البيانات الحالية")
            
            with zipfile.ZipFile(backup_file, 'r') as zipf:
                # قراءة معلومات النسخة الاحتياطية
                try:
                    backup_info_str = zipf.read("backup_info.json").decode('utf-8')
                    import json
                    backup_info = json.loads(backup_info_str)
                    logger.info(f"استعادة النسخة الاحتياطية المنشأة في: {backup_info.get('created_at')}")
                except Exception:
                    logger.warning("لا يمكن قراءة معلومات النسخة الاحتياطية")
                
                # استعادة قاعدة البيانات
                try:
                    # إغلاق جميع اتصالات قاعدة البيانات
                    db_content = zipf.read("data/shop.db")
                    
                    # إنشاء مجلد البيانات إذا لم يكن موجوداً
                    Path("data").mkdir(exist_ok=True)
                    
                    # كتابة قاعدة البيانات الجديدة
                    with open(self.db.db_path, 'wb') as f:
                        f.write(db_content)
                    
                    logger.info("تم استعادة قاعدة البيانات")
                    
                except KeyError:
                    raise Exception("ملف قاعدة البيانات غير موجود في النسخة الاحتياطية")
                
                # استعادة التقارير
                if restore_reports:
                    reports_files = [f for f in zipf.namelist() if f.startswith("reports/")]
                    for report_file in reports_files:
                        zipf.extract(report_file, ".")
                    
                    if reports_files:
                        logger.info(f"تم استعادة {len(reports_files)} ملف تقرير")
                
                # استعادة الأصول
                assets_files = [f for f in zipf.namelist() if f.startswith("assets/")]
                for asset_file in assets_files:
                    zipf.extract(asset_file, ".")
                
                if assets_files:
                    logger.info(f"تم استعادة {len(assets_files)} ملف أصول")
            
            # تسجيل النشاط
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    self.auth_service.log_user_activity(
                        current_user['id'], 'restore_backup', None, None,
                        f"استعادة نسخة احتياطية من: {backup_file.name}"
                    )
            
            logger.info(f"تم استعادة النسخة الاحتياطية بنجاح من: {backup_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في استعادة النسخة الاحتياطية: {str(e)}")
            return False
    
    def get_backup_list(self) -> List[Dict]:
        """الحصول على قائمة النسخ الاحتياطية"""
        try:
            backups = []
            
            for backup_file in self.backup_dir.glob("*.zip"):
                try:
                    backup_info = {
                        'name': backup_file.stem,
                        'file_path': str(backup_file),
                        'size': backup_file.stat().st_size,
                        'created_at': datetime.fromtimestamp(backup_file.stat().st_mtime).isoformat()
                    }
                    
                    # محاولة قراءة معلومات إضافية من ملف النسخة الاحتياطية
                    try:
                        with zipfile.ZipFile(backup_file, 'r') as zipf:
                            if "backup_info.json" in zipf.namelist():
                                import json
                                info_str = zipf.read("backup_info.json").decode('utf-8')
                                extra_info = json.loads(info_str)
                                backup_info.update(extra_info)
                    except Exception:
                        pass  # تجاهل الأخطاء في قراءة المعلومات الإضافية
                    
                    backups.append(backup_info)
                    
                except Exception as e:
                    logger.warning(f"خطأ في قراءة معلومات النسخة الاحتياطية {backup_file}: {str(e)}")
            
            # ترتيب حسب تاريخ الإنشاء (الأحدث أولاً)
            backups.sort(key=lambda x: x['created_at'], reverse=True)
            
            return backups
            
        except Exception as e:
            logger.error(f"خطأ في الحصول على قائمة النسخ الاحتياطية: {str(e)}")
            return []
    
    def delete_backup(self, backup_path: str) -> bool:
        """حذف نسخة احتياطية"""
        try:
            backup_file = Path(backup_path)
            if backup_file.exists():
                backup_file.unlink()
                
                # تسجيل النشاط
                if self.auth_service:
                    current_user = self.auth_service.get_current_user()
                    if current_user:
                        self.auth_service.log_user_activity(
                            current_user['id'], 'delete_backup', None, None,
                            f"حذف نسخة احتياطية: {backup_file.name}"
                        )
                
                logger.info(f"تم حذف النسخة الاحتياطية: {backup_path}")
                return True
            else:
                logger.warning(f"النسخة الاحتياطية غير موجودة: {backup_path}")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في حذف النسخة الاحتياطية: {str(e)}")
            return False
    
    def auto_backup(self) -> bool:
        """النسخ الاحتياطي التلقائي"""
        try:
            # التحقق من تفعيل النسخ التلقائي
            auto_backup_enabled = self.db.get_setting('auto_backup')
            if auto_backup_enabled != '1':
                return True  # النسخ التلقائي معطل
            
            # التحقق من وجود نسخة احتياطية لليوم الحالي
            today = datetime.now().strftime("%Y%m%d")
            existing_backup = None
            
            for backup_file in self.backup_dir.glob(f"auto_backup_{today}_*.zip"):
                existing_backup = backup_file
                break
            
            if existing_backup:
                logger.info(f"النسخة الاحتياطية التلقائية موجودة لليوم: {existing_backup}")
                return True
            
            # إنشاء نسخة احتياطية تلقائية
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            backup_name = f"auto_backup_{timestamp}"
            
            backup_path = self.create_backup(backup_name, include_reports=False)
            
            if backup_path:
                logger.info(f"تم إنشاء النسخة الاحتياطية التلقائية: {backup_path}")
                
                # حذف النسخ التلقائية القديمة (الاحتفاظ بآخر 7 نسخ)
                self._cleanup_old_auto_backups()
                
                return True
            else:
                logger.error("فشل في إنشاء النسخة الاحتياطية التلقائية")
                return False
                
        except Exception as e:
            logger.error(f"خطأ في النسخ الاحتياطي التلقائي: {str(e)}")
            return False
    
    def _cleanup_old_auto_backups(self, keep_count: int = 7):
        """حذف النسخ التلقائية القديمة"""
        try:
            auto_backups = []
            
            for backup_file in self.backup_dir.glob("auto_backup_*.zip"):
                auto_backups.append({
                    'file': backup_file,
                    'mtime': backup_file.stat().st_mtime
                })
            
            # ترتيب حسب تاريخ التعديل (الأقدم أولاً)
            auto_backups.sort(key=lambda x: x['mtime'])
            
            # حذف النسخ الزائدة
            while len(auto_backups) > keep_count:
                old_backup = auto_backups.pop(0)
                old_backup['file'].unlink()
                logger.info(f"تم حذف النسخة الاحتياطية القديمة: {old_backup['file'].name}")
                
        except Exception as e:
            logger.error(f"خطأ في حذف النسخ القديمة: {str(e)}")
    
    def export_data(self, export_type: str, start_date: str = None, 
                   end_date: str = None) -> Optional[str]:
        """تصدير البيانات بصيغ مختلفة"""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            export_dir = Path("backup") / "exports"
            export_dir.mkdir(exist_ok=True)
            
            if export_type == 'csv':
                return self._export_to_csv(export_dir, timestamp, start_date, end_date)
            elif export_type == 'sql':
                return self._export_to_sql(export_dir, timestamp)
            else:
                raise ValueError(f"نوع التصدير غير مدعوم: {export_type}")
                
        except Exception as e:
            logger.error(f"خطأ في تصدير البيانات: {str(e)}")
            return None
    
    def _export_to_csv(self, export_dir: Path, timestamp: str, 
                      start_date: str = None, end_date: str = None) -> str:
        """تصدير البيانات إلى ملفات CSV"""
        import csv
        
        export_file = export_dir / f"data_export_{timestamp}.zip"
        
        with zipfile.ZipFile(export_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
            # تصدير المبيعات
            sales_query = "SELECT * FROM sales"
            params = []
            
            if start_date and end_date:
                sales_query += " WHERE DATE(created_at) BETWEEN ? AND ?"
                params = [start_date, end_date]
            
            sales_data = self.db.execute_query(sales_query, tuple(params))
            
            if sales_data:
                sales_csv = "sales.csv"
                with zipf.open(sales_csv, 'w') as csvfile:
                    import io
                    text_stream = io.TextIOWrapper(csvfile, encoding='utf-8')
                    writer = csv.DictWriter(text_stream, fieldnames=sales_data[0].keys())
                    writer.writeheader()
                    for row in sales_data:
                        writer.writerow(dict(row))
                    text_stream.detach()
            
            # تصدير المنتجات
            products_data = self.db.execute_query("SELECT * FROM products")
            if products_data:
                products_csv = "products.csv"
                with zipf.open(products_csv, 'w') as csvfile:
                    import io
                    text_stream = io.TextIOWrapper(csvfile, encoding='utf-8')
                    writer = csv.DictWriter(text_stream, fieldnames=products_data[0].keys())
                    writer.writeheader()
                    for row in products_data:
                        writer.writerow(dict(row))
                    text_stream.detach()
        
        return str(export_file)
    
    def _export_to_sql(self, export_dir: Path, timestamp: str) -> str:
        """تصدير البيانات إلى ملف SQL"""
        export_file = export_dir / f"database_dump_{timestamp}.sql"
        
        with sqlite3.connect(self.db.db_path) as conn:
            with open(export_file, 'w', encoding='utf-8') as f:
                for line in conn.iterdump():
                    f.write('%s\n' % line)
        
        return str(export_file)
