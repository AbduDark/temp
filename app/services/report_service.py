#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
خدمة التقارير - Reports Service
"""

from typing import Dict, List, Optional
from datetime import datetime, date, timedelta
from app.models.database import DatabaseManager
import logging

logger = logging.getLogger(__name__)

class ReportService:
    """خدمة إنتاج التقارير"""
    
    def __init__(self, auth_service=None):
        self.db = DatabaseManager()
        self.auth_service = auth_service
    
    def get_sales_report(self, start_date: str, end_date: str, 
                        group_by: str = 'day') -> Dict:
        """تقرير المبيعات"""
        try:
            # إجمالي المبيعات
            total_result = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_transactions,
                    SUM(final_amount) as total_sales,
                    SUM(discount_amount) as total_discounts,
                    SUM(tax_amount) as total_tax,
                    AVG(final_amount) as avg_transaction
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ? 
                AND status = 'completed'
            """, (start_date, end_date))
            
            # المبيعات حسب وسيلة الدفع
            payment_result = self.db.execute_query("""
                SELECT 
                    payment_method,
                    COUNT(*) as transaction_count,
                    SUM(final_amount) as total_amount
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ? 
                AND status = 'completed'
                GROUP BY payment_method
                ORDER BY total_amount DESC
            """, (start_date, end_date))
            
            # المبيعات اليومية/الشهرية
            if group_by == 'day':
                period_query = "DATE(created_at)"
                period_format = "%Y-%m-%d"
            elif group_by == 'month':
                period_query = "strftime('%Y-%m', created_at)"
                period_format = "%Y-%m"
            else:
                period_query = "DATE(created_at)"
                period_format = "%Y-%m-%d"
            
            period_result = self.db.execute_query(f"""
                SELECT 
                    {period_query} as period,
                    COUNT(*) as transactions,
                    SUM(final_amount) as total_sales,
                    SUM(discount_amount) as discounts
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ? 
                AND status = 'completed'
                GROUP BY {period_query}
                ORDER BY period
            """, (start_date, end_date))
            
            # أفضل المنتجات مبيعاً
            top_products = self.db.execute_query("""
                SELECT 
                    p.name,
                    SUM(si.quantity) as total_sold,
                    SUM(si.total_amount) as total_revenue,
                    AVG(si.unit_price) as avg_price
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_id = p.id
                WHERE DATE(s.created_at) BETWEEN ? AND ? 
                AND s.status = 'completed'
                GROUP BY p.id, p.name
                ORDER BY total_sold DESC
                LIMIT 10
            """, (start_date, end_date))
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'summary': dict(total_result[0]) if total_result else {},
                'by_payment_method': [dict(row) for row in payment_result],
                'by_period': [dict(row) for row in period_result],
                'top_products': [dict(row) for row in top_products]
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير المبيعات: {str(e)}")
            return {}
    
    def get_inventory_report(self) -> Dict:
        """تقرير المخزون"""
        try:
            # ملخص المخزون
            summary = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_products,
                    SUM(quantity_in_stock) as total_quantity,
                    SUM(quantity_in_stock * cost_price) as total_cost_value,
                    SUM(quantity_in_stock * selling_price) as total_selling_value,
                    COUNT(CASE WHEN quantity_in_stock <= minimum_stock THEN 1 END) as low_stock_count,
                    COUNT(CASE WHEN quantity_in_stock = 0 THEN 1 END) as out_of_stock_count
                FROM products 
                WHERE is_active = 1
            """)
            
            # المنتجات منخفضة المخزون
            low_stock = self.db.execute_query("""
                SELECT 
                    p.name,
                    p.quantity_in_stock,
                    p.minimum_stock,
                    c.name as category_name,
                    p.selling_price
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1 
                AND p.quantity_in_stock <= p.minimum_stock
                ORDER BY p.quantity_in_stock ASC
            """)
            
            # المخزون حسب الفئة
            by_category = self.db.execute_query("""
                SELECT 
                    COALESCE(c.name, 'غير مصنف') as category_name,
                    COUNT(p.id) as product_count,
                    SUM(p.quantity_in_stock) as total_quantity,
                    SUM(p.quantity_in_stock * p.cost_price) as total_cost_value,
                    SUM(p.quantity_in_stock * p.selling_price) as total_selling_value
                FROM products p
                LEFT JOIN categories c ON p.category_id = c.id
                WHERE p.is_active = 1
                GROUP BY c.id, c.name
                ORDER BY total_selling_value DESC
            """)
            
            # أعلى قيمة مخزون
            highest_value = self.db.execute_query("""
                SELECT 
                    p.name,
                    p.quantity_in_stock,
                    p.cost_price,
                    p.selling_price,
                    (p.quantity_in_stock * p.selling_price) as total_value
                FROM products p
                WHERE p.is_active = 1 
                AND p.quantity_in_stock > 0
                ORDER BY total_value DESC
                LIMIT 10
            """)
            
            return {
                'summary': dict(summary[0]) if summary else {},
                'low_stock_products': [dict(row) for row in low_stock],
                'by_category': [dict(row) for row in by_category],
                'highest_value_products': [dict(row) for row in highest_value]
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير المخزون: {str(e)}")
            return {}
    
    def get_repair_report(self, start_date: str, end_date: str) -> Dict:
        """تقرير الصيانة"""
        try:
            # ملخص الصيانة
            summary = self.db.execute_query("""
                SELECT 
                    COUNT(*) as total_tickets,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as completed_tickets,
                    COUNT(CASE WHEN status = 'in_progress' THEN 1 END) as in_progress_tickets,
                    COUNT(CASE WHEN status = 'delivered' THEN 1 END) as delivered_tickets,
                    SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as total_revenue,
                    AVG(CASE 
                        WHEN completed_date IS NOT NULL AND received_date IS NOT NULL 
                        THEN julianday(completed_date) - julianday(received_date) 
                        END) as avg_completion_days
                FROM repair_tickets 
                WHERE DATE(received_date) BETWEEN ? AND ?
            """, (start_date, end_date))
            
            # الصيانة حسب النوع
            by_type = self.db.execute_query("""
                SELECT 
                    repair_type,
                    COUNT(*) as ticket_count,
                    SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as total_revenue,
                    AVG(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as avg_cost
                FROM repair_tickets 
                WHERE DATE(received_date) BETWEEN ? AND ?
                GROUP BY repair_type
            """, (start_date, end_date))
            
            # أداء الفنيين
            technician_performance = self.db.execute_query("""
                SELECT 
                    u.full_name as technician_name,
                    COUNT(rt.id) as total_tickets,
                    COUNT(CASE WHEN rt.status = 'completed' THEN 1 END) as completed_tickets,
                    SUM(CASE WHEN rt.final_cost IS NOT NULL THEN rt.final_cost ELSE rt.estimated_cost END) as total_revenue,
                    AVG(CASE 
                        WHEN rt.completed_date IS NOT NULL AND rt.received_date IS NOT NULL 
                        THEN julianday(rt.completed_date) - julianday(rt.received_date) 
                        END) as avg_completion_days
                FROM repair_tickets rt
                LEFT JOIN users u ON rt.technician_id = u.id
                WHERE DATE(rt.received_date) BETWEEN ? AND ?
                AND rt.technician_id IS NOT NULL
                GROUP BY rt.technician_id, u.full_name
                ORDER BY completed_tickets DESC
            """, (start_date, end_date))
            
            # الصيانة اليومية
            daily_repairs = self.db.execute_query("""
                SELECT 
                    DATE(received_date) as date,
                    COUNT(*) as tickets_received,
                    COUNT(CASE WHEN status = 'completed' THEN 1 END) as tickets_completed,
                    SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as daily_revenue
                FROM repair_tickets 
                WHERE DATE(received_date) BETWEEN ? AND ?
                GROUP BY DATE(received_date)
                ORDER BY date
            """, (start_date, end_date))
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'summary': dict(summary[0]) if summary else {},
                'by_type': [dict(row) for row in by_type],
                'technician_performance': [dict(row) for row in technician_performance],
                'daily_summary': [dict(row) for row in daily_repairs]
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير الصيانة: {str(e)}")
            return {}
    
    def get_profit_loss_report(self, start_date: str, end_date: str) -> Dict:
        """تقرير الربح والخسارة"""
        try:
            # إيرادات المبيعات
            sales_revenue = self.db.execute_query("""
                SELECT 
                    SUM(final_amount) as total_sales,
                    SUM(tax_amount) as total_tax,
                    SUM(discount_amount) as total_discounts
                FROM sales 
                WHERE DATE(created_at) BETWEEN ? AND ? 
                AND status = 'completed'
            """, (start_date, end_date))
            
            # تكلفة البضاعة المباعة
            cost_of_goods = self.db.execute_query("""
                SELECT 
                    SUM(si.quantity * p.cost_price) as total_cogs
                FROM sale_items si
                JOIN sales s ON si.sale_id = s.id
                JOIN products p ON si.product_id = p.id
                WHERE DATE(s.created_at) BETWEEN ? AND ? 
                AND s.status = 'completed'
            """, (start_date, end_date))
            
            # إيرادات الصيانة
            repair_revenue = self.db.execute_query("""
                SELECT 
                    SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END) as total_repair_revenue
                FROM repair_tickets 
                WHERE DATE(received_date) BETWEEN ? AND ?
                AND status IN ('completed', 'delivered')
            """, (start_date, end_date))
            
            # المرتجعات
            returns_data = self.db.execute_query("""
                SELECT 
                    SUM(total_amount) as total_returns
                FROM returns 
                WHERE DATE(created_at) BETWEEN ? AND ?
            """, (start_date, end_date))
            
            # حساب الأرباح
            sales_total = sales_revenue[0]['total_sales'] if sales_revenue and sales_revenue[0]['total_sales'] else 0
            cogs_total = cost_of_goods[0]['total_cogs'] if cost_of_goods and cost_of_goods[0]['total_cogs'] else 0
            repair_total = repair_revenue[0]['total_repair_revenue'] if repair_revenue and repair_revenue[0]['total_repair_revenue'] else 0
            returns_total = returns_data[0]['total_returns'] if returns_data and returns_data[0]['total_returns'] else 0
            
            gross_profit = sales_total - cogs_total
            total_revenue = sales_total + repair_total - returns_total
            net_profit = gross_profit + repair_total - returns_total
            
            # هامش الربح
            gross_margin = (gross_profit / sales_total * 100) if sales_total > 0 else 0
            net_margin = (net_profit / total_revenue * 100) if total_revenue > 0 else 0
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'revenue': {
                    'sales_revenue': sales_total,
                    'repair_revenue': repair_total,
                    'total_revenue': total_revenue,
                    'returns': returns_total
                },
                'costs': {
                    'cost_of_goods_sold': cogs_total
                },
                'profit': {
                    'gross_profit': gross_profit,
                    'net_profit': net_profit,
                    'gross_margin': round(gross_margin, 2),
                    'net_margin': round(net_margin, 2)
                }
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير الربح والخسارة: {str(e)}")
            return {}
    
    def get_customer_report(self, start_date: str, end_date: str) -> Dict:
        """تقرير العملاء"""
        try:
            # أفضل العملاء
            top_customers = self.db.execute_query("""
                SELECT 
                    c.name,
                    c.phone,
                    COUNT(s.id) as total_purchases,
                    SUM(s.final_amount) as total_spent,
                    AVG(s.final_amount) as avg_purchase,
                    MAX(s.created_at) as last_purchase
                FROM customers c
                JOIN sales s ON c.id = s.customer_id
                WHERE DATE(s.created_at) BETWEEN ? AND ? 
                AND s.status = 'completed'
                GROUP BY c.id, c.name, c.phone
                ORDER BY total_spent DESC
                LIMIT 20
            """, (start_date, end_date))
            
            # عملاء الصيانة
            repair_customers = self.db.execute_query("""
                SELECT 
                    c.name,
                    c.phone,
                    COUNT(rt.id) as total_repairs,
                    SUM(CASE WHEN rt.final_cost IS NOT NULL THEN rt.final_cost ELSE rt.estimated_cost END) as total_repair_cost,
                    AVG(CASE WHEN rt.final_cost IS NOT NULL THEN rt.final_cost ELSE rt.estimated_cost END) as avg_repair_cost
                FROM customers c
                JOIN repair_tickets rt ON c.id = rt.customer_id
                WHERE DATE(rt.received_date) BETWEEN ? AND ?
                GROUP BY c.id, c.name, c.phone
                ORDER BY total_repair_cost DESC
                LIMIT 20
            """, (start_date, end_date))
            
            # إحصائيات عامة
            customer_stats = self.db.execute_query("""
                SELECT 
                    COUNT(DISTINCT c.id) as total_customers,
                    COUNT(DISTINCT CASE WHEN s.id IS NOT NULL THEN c.id END) as purchasing_customers,
                    COUNT(DISTINCT CASE WHEN rt.id IS NOT NULL THEN c.id END) as repair_customers
                FROM customers c
                LEFT JOIN sales s ON c.id = s.customer_id AND DATE(s.created_at) BETWEEN ? AND ?
                LEFT JOIN repair_tickets rt ON c.id = rt.customer_id AND DATE(rt.received_date) BETWEEN ? AND ?
            """, (start_date, end_date, start_date, end_date))
            
            return {
                'period': {'start': start_date, 'end': end_date},
                'statistics': dict(customer_stats[0]) if customer_stats else {},
                'top_customers': [dict(row) for row in top_customers],
                'repair_customers': [dict(row) for row in repair_customers]
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير العملاء: {str(e)}")
            return {}
    
    def get_daily_close_report(self, date: str) -> Dict:
        """تقرير التقفيل اليومي"""
        try:
            # البحث عن تقفيل موجود
            existing_close = self.db.execute_query("""
                SELECT * FROM daily_closes WHERE close_date = ?
            """, (date,))
            
            if existing_close:
                return dict(existing_close[0])
            
            # حساب البيانات للتقفيل الجديد
            sales_summary = self.db.execute_query("""
                SELECT 
                    SUM(CASE WHEN payment_method = 'cash' THEN final_amount ELSE 0 END) as cash_sales,
                    SUM(CASE WHEN payment_method = 'card' THEN final_amount ELSE 0 END) as card_sales,
                    SUM(CASE WHEN payment_method IN ('vodafone_cash', 'etisalat_wallet', 'we_pay', 'insta_pay') 
                        THEN final_amount ELSE 0 END) as wallet_sales,
                    SUM(final_amount) as total_sales
                FROM sales 
                WHERE DATE(created_at) = ? AND status = 'completed'
            """, (date,))
            
            returns_total = self.db.execute_query("""
                SELECT COALESCE(SUM(total_amount), 0) as total_returns
                FROM returns 
                WHERE DATE(created_at) = ?
            """, (date,))
            
            repair_revenue = self.db.execute_query("""
                SELECT COALESCE(SUM(CASE WHEN final_cost IS NOT NULL THEN final_cost ELSE estimated_cost END), 0) as repair_revenue
                FROM repair_tickets 
                WHERE DATE(received_date) = ? AND status IN ('completed', 'delivered')
            """, (date,))
            
            # إعداد البيانات
            sales_data = dict(sales_summary[0]) if sales_summary else {}
            returns_amount = returns_total[0]['total_returns'] if returns_total else 0
            repair_amount = repair_revenue[0]['repair_revenue'] if repair_revenue else 0
            
            cash_sales = sales_data.get('cash_sales', 0) or 0
            card_sales = sales_data.get('card_sales', 0) or 0
            wallet_sales = sales_data.get('wallet_sales', 0) or 0
            total_sales = sales_data.get('total_sales', 0) or 0
            
            net_sales = total_sales - returns_amount
            total_revenue = net_sales + repair_amount
            
            return {
                'close_date': date,
                'cash_sales': cash_sales,
                'card_sales': card_sales,
                'wallet_sales': wallet_sales,
                'total_sales': total_sales,
                'returns': returns_amount,
                'repair_revenue': repair_amount,
                'net_sales': net_sales,
                'total_revenue': total_revenue,
                'expenses': 0,  # يتم إدخالها يدوياً
                'net_profit': total_revenue,  # سيتم تعديلها بعد إدخال المصروفات
                'opening_balance': 0,  # يتم إدخالها يدوياً
                'closing_balance': 0   # يتم حسابها
            }
            
        except Exception as e:
            logger.error(f"خطأ في تقرير التقفيل اليومي: {str(e)}")
            return {}
    
    def save_daily_close(self, close_data: Dict) -> bool:
        """حفظ بيانات التقفيل اليومي"""
        try:
            # التحقق من وجود تقفيل لنفس التاريخ
            existing = self.db.execute_query(
                "SELECT id FROM daily_closes WHERE close_date = ?",
                (close_data['close_date'],)
            )
            
            user_id = None
            if self.auth_service:
                current_user = self.auth_service.get_current_user()
                if current_user:
                    user_id = current_user['id']
            
            if existing:
                # تحديث التقفيل الموجود
                self.db.execute_update("""
                    UPDATE daily_closes SET
                        cash_sales = ?, card_sales = ?, wallet_sales = ?,
                        total_sales = ?, expenses = ?, purchases = ?,
                        returns = ?, net_profit = ?, opening_balance = ?,
                        closing_balance = ?, notes = ?, user_id = ?
                    WHERE close_date = ?
                """, (
                    close_data.get('cash_sales', 0),
                    close_data.get('card_sales', 0),
                    close_data.get('wallet_sales', 0),
                    close_data.get('total_sales', 0),
                    close_data.get('expenses', 0),
                    close_data.get('purchases', 0),
                    close_data.get('returns', 0),
                    close_data.get('net_profit', 0),
                    close_data.get('opening_balance', 0),
                    close_data.get('closing_balance', 0),
                    close_data.get('notes', ''),
                    user_id,
                    close_data['close_date']
                ))
            else:
                # إنشاء تقفيل جديد
                self.db.execute_insert("""
                    INSERT INTO daily_closes (
                        close_date, cash_sales, card_sales, wallet_sales,
                        total_sales, expenses, purchases, returns, net_profit,
                        opening_balance, closing_balance, notes, user_id
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, (
                    close_data['close_date'],
                    close_data.get('cash_sales', 0),
                    close_data.get('card_sales', 0),
                    close_data.get('wallet_sales', 0),
                    close_data.get('total_sales', 0),
                    close_data.get('expenses', 0),
                    close_data.get('purchases', 0),
                    close_data.get('returns', 0),
                    close_data.get('net_profit', 0),
                    close_data.get('opening_balance', 0),
                    close_data.get('closing_balance', 0),
                    close_data.get('notes', ''),
                    user_id
                ))
            
            return True
            
        except Exception as e:
            logger.error(f"خطأ في حفظ التقفيل اليومي: {str(e)}")
            return False
