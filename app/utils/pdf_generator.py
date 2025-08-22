#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
مولد ملفات PDF - PDF Generator
"""

import os
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional
import logging

try:
    from reportlab.lib import colors
    from reportlab.lib.pagesizes import letter, A4
    from reportlab.lib.units import inch, cm
    from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
    from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer, Image
    from reportlab.platypus.flowables import HRFlowable
    from reportlab.pdfgen import canvas
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
except ImportError:
    # إذا لم تكن مكتبة reportlab متوفرة، استخدم مولد PDF بديل
    SimpleDocTemplate = None

logger = logging.getLogger(__name__)


class PDFGenerator:
    """مولد ملفات PDF للفواتير والتقارير"""
    
    def __init__(self):
        self.setup_fonts()
        self.setup_styles()
    
    def setup_fonts(self):
        """إعداد الخطوط العربية"""
        try:
            # محاولة تحميل خط عربي إذا كان متوفراً
            font_path = "assets/fonts/NotoSansArabic-Regular.ttf"
            if os.path.exists(font_path):
                pdfmetrics.registerFont(TTFont('Arabic', font_path))
                self.arabic_font = 'Arabic'
            else:
                # استخدام خط افتراضي
                self.arabic_font = 'Helvetica'
        except Exception:
            self.arabic_font = 'Helvetica'
    
    def setup_styles(self):
        """إعداد أنماط النصوص"""
        if not SimpleDocTemplate:
            return
            
        self.styles = getSampleStyleSheet()
        
        # نمط العنوان الرئيسي
        self.title_style = ParagraphStyle(
            'CustomTitle',
            parent=self.styles['Heading1'],
            fontName=self.arabic_font,
            fontSize=18,
            spaceAfter=20,
            alignment=1,  # محاذاة وسط
            textColor=colors.HexColor('#2c3e50')
        )
        
        # نمط العنوان الفرعي
        self.subtitle_style = ParagraphStyle(
            'CustomSubtitle',
            parent=self.styles['Heading2'],
            fontName=self.arabic_font,
            fontSize=14,
            spaceAfter=12,
            alignment=1,
            textColor=colors.HexColor('#34495e')
        )
        
        # نمط النص العادي
        self.normal_style = ParagraphStyle(
            'CustomNormal',
            parent=self.styles['Normal'],
            fontName=self.arabic_font,
            fontSize=10,
            spaceAfter=6,
            alignment=2,  # محاذاة يمين للعربية
            textColor=colors.HexColor('#2c3e50')
        )
        
        # نمط النص الصغير
        self.small_style = ParagraphStyle(
            'CustomSmall',
            parent=self.styles['Normal'],
            fontName=self.arabic_font,
            fontSize=8,
            spaceAfter=4,
            alignment=2,
            textColor=colors.HexColor('#7f8c8d')
        )
    
    def generate_invoice(self, sale_data: Dict, output_path: str) -> bool:
        """إنتاج فاتورة مبيعات"""
        if not SimpleDocTemplate:
            return self._generate_simple_invoice(sale_data, output_path)
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # عنوان الفاتورة
            story.append(Paragraph("فاتورة مبيعات", self.title_style))
            story.append(Spacer(1, 20))
            
            # معلومات الفاتورة والعميل
            invoice_info = [
                ['رقم الفاتورة:', str(sale_data['id'])],
                ['تاريخ الفاتورة:', sale_data['created_at'][:16]],
                ['وسيلة الدفع:', self._get_payment_method_name(sale_data.get('payment_method', ''))],
            ]
            
            if sale_data.get('customer_name'):
                invoice_info.extend([
                    ['اسم العميل:', sale_data['customer_name']],
                    ['هاتف العميل:', sale_data.get('customer_phone', 'غير محدد')]
                ])
            
            info_table = Table(invoice_info, colWidths=[4*cm, 6*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # جدول العناصر
            items_data = [['المنتج', 'الكمية', 'سعر الوحدة', 'المجموع']]
            
            for item in sale_data.get('items', []):
                items_data.append([
                    item.get('product_name', 'غير محدد'),
                    str(item['quantity']),
                    f"{item['unit_price']:.2f} ر.س",
                    f"{item['total_amount']:.2f} ر.س"
                ])
            
            items_table = Table(items_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
            items_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('FONTSIZE', (0, 0), (-1, 0), 12),
                ('FONTNAME', (0, 0), (-1, 0), self.arabic_font),
            ]))
            
            story.append(items_table)
            story.append(Spacer(1, 20))
            
            # جدول الإجماليات
            totals_data = [
                ['المجموع الفرعي:', f"{sale_data['total_amount']:.2f} ر.س"],
                ['الخصم:', f"{sale_data.get('discount_amount', 0):.2f} ر.س"],
                ['الضريبة:', f"{sale_data.get('tax_amount', 0):.2f} ر.س"],
                ['المجموع النهائي:', f"{sale_data['final_amount']:.2f} ر.س"],
            ]
            
            totals_table = Table(totals_data, colWidths=[4*cm, 4*cm])
            totals_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
                ('FONTNAME', (0, -1), (-1, -1), self.arabic_font),
            ]))
            
            story.append(totals_table)
            
            # الملاحظات
            if sale_data.get('notes'):
                story.append(Spacer(1, 20))
                story.append(Paragraph("ملاحظات:", self.subtitle_style))
                story.append(Paragraph(sale_data['notes'], self.normal_style))
            
            # نص الختام
            story.append(Spacer(1, 30))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
            story.append(Spacer(1, 10))
            story.append(Paragraph("شكراً لزيارتكم ونتطلع لخدمتكم مرة أخرى", self.normal_style))
            
            # بناء الوثيقة
            doc.build(story)
            
            logger.info(f"تم إنتاج فاتورة PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج فاتورة PDF: {str(e)}")
            return False
    
    def generate_repair_ticket(self, ticket_data: Dict, output_path: str) -> bool:
        """إنتاج تذكرة صيانة"""
        if not SimpleDocTemplate:
            return self._generate_simple_repair_ticket(ticket_data, output_path)
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # عنوان التذكرة
            story.append(Paragraph("تذكرة صيانة", self.title_style))
            story.append(Spacer(1, 20))
            
            # معلومات التذكرة
            ticket_info = [
                ['رقم التذكرة:', str(ticket_data['id'])],
                ['تاريخ الاستلام:', ticket_data['received_date'][:16]],
                ['نوع الصيانة:', self._get_repair_type_name(ticket_data.get('repair_type', ''))],
                ['الحالة:', self._get_repair_status_name(ticket_data.get('status', ''))],
            ]
            
            if ticket_data.get('customer_name'):
                ticket_info.extend([
                    ['اسم العميل:', ticket_data['customer_name']],
                    ['هاتف العميل:', ticket_data.get('customer_phone', 'غير محدد')]
                ])
            
            ticket_info.extend([
                ['معلومات الجهاز:', ticket_data.get('device_info', 'غير محدد')],
                ['رقم IMEI:', ticket_data.get('imei', 'غير محدد')]
            ])
            
            if ticket_data.get('technician_name'):
                ticket_info.append(['الفني المسؤول:', ticket_data['technician_name']])
            
            info_table = Table(ticket_info, colWidths=[4*cm, 8*cm])
            info_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 10),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ]))
            
            story.append(info_table)
            story.append(Spacer(1, 20))
            
            # وصف المشكلة
            story.append(Paragraph("وصف المشكلة:", self.subtitle_style))
            story.append(Paragraph(ticket_data.get('problem_description', ''), self.normal_style))
            story.append(Spacer(1, 15))
            
            # قطع الغيار المستخدمة
            if ticket_data.get('parts_used'):
                story.append(Paragraph("قطع الغيار المستخدمة:", self.subtitle_style))
                
                parts_data = [['القطعة', 'الكمية', 'السعر', 'المجموع']]
                
                for part in ticket_data['parts_used']:
                    parts_data.append([
                        part.get('product_name', 'غير محدد'),
                        str(part['quantity']),
                        f"{part['unit_price']:.2f} ر.س",
                        f"{part['total_price']:.2f} ر.س"
                    ])
                
                parts_table = Table(parts_data, colWidths=[6*cm, 2*cm, 3*cm, 3*cm])
                parts_table.setStyle(TableStyle([
                    ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                    ('FONTSIZE', (0, 0), (-1, -1), 10),
                    ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
                    ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                    ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                    ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#e67e22')),
                    ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                    ('FONTSIZE', (0, 0), (-1, 0), 12),
                ]))
                
                story.append(parts_table)
                story.append(Spacer(1, 15))
            
            # التكاليف
            cost_data = [
                ['التكلفة المقدرة:', f"{ticket_data.get('estimated_cost', 0):.2f} ر.س"],
                ['التكلفة النهائية:', f"{ticket_data.get('final_cost', 0):.2f} ر.س"],
            ]
            
            cost_table = Table(cost_data, colWidths=[4*cm, 4*cm])
            cost_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'LEFT'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (0, -1), colors.HexColor('#ecf0f1')),
            ]))
            
            story.append(cost_table)
            
            # الملاحظات
            if ticket_data.get('notes'):
                story.append(Spacer(1, 20))
                story.append(Paragraph("ملاحظات:", self.subtitle_style))
                story.append(Paragraph(ticket_data['notes'], self.normal_style))
            
            # نص الختام
            story.append(Spacer(1, 30))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
            story.append(Spacer(1, 10))
            story.append(Paragraph("نضمن جودة الخدمة وقطع الغيار المستخدمة", self.normal_style))
            
            # بناء الوثيقة
            doc.build(story)
            
            logger.info(f"تم إنتاج تذكرة صيانة PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج تذكرة صيانة PDF: {str(e)}")
            return False
    
    def generate_daily_close_report(self, close_data: Dict, output_path: str) -> bool:
        """إنتاج تقرير التقفيل اليومي"""
        if not SimpleDocTemplate:
            return self._generate_simple_daily_close(close_data, output_path)
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # عنوان التقرير
            story.append(Paragraph("تقرير التقفيل اليومي", self.title_style))
            story.append(Paragraph(f"تاريخ التقفيل: {close_data['close_date']}", self.subtitle_style))
            story.append(Spacer(1, 20))
            
            # ملخص المبيعات
            story.append(Paragraph("ملخص المبيعات", self.subtitle_style))
            
            sales_data = [
                ['نوع المبيعات', 'المبلغ'],
                ['مبيعات نقدية', f"{close_data.get('cash_sales', 0):.2f} ر.س"],
                ['مبيعات البطاقات', f"{close_data.get('card_sales', 0):.2f} ر.س"],
                ['المحافظ الإلكترونية', f"{close_data.get('wallet_sales', 0):.2f} ر.س"],
                ['إجمالي المبيعات', f"{close_data.get('total_sales', 0):.2f} ر.س"],
            ]
            
            if close_data.get('repair_revenue'):
                sales_data.append(['إيراد الصيانة', f"{close_data['repair_revenue']:.2f} ر.س"])
            
            if close_data.get('returns'):
                sales_data.append(['المرتجعات', f"{close_data['returns']:.2f} ر.س"])
            
            sales_data.append(['صافي الإيراد', f"{close_data.get('total_revenue', 0):.2f} ر.س"])
            
            sales_table = Table(sales_data, colWidths=[6*cm, 4*cm])
            sales_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#3498db')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
            ]))
            
            story.append(sales_table)
            story.append(Spacer(1, 20))
            
            # المصروفات والأرصدة
            story.append(Paragraph("المصروفات والأرصدة", self.subtitle_style))
            
            expenses_data = [
                ['البيان', 'المبلغ'],
                ['المصروفات اليومية', f"{close_data.get('expenses', 0):.2f} ر.س"],
                ['المشتريات', f"{close_data.get('purchases', 0):.2f} ر.س"],
                ['رصيد أول اليوم', f"{close_data.get('opening_balance', 0):.2f} ر.س"],
                ['رصيد آخر اليوم', f"{close_data.get('closing_balance', 0):.2f} ر.س"],
                ['صافي الربح', f"{close_data.get('net_profit', 0):.2f} ر.س"],
            ]
            
            expenses_table = Table(expenses_data, colWidths=[6*cm, 4*cm])
            expenses_table.setStyle(TableStyle([
                ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
                ('FONTSIZE', (0, 0), (-1, -1), 11),
                ('ALIGN', (0, 0), (0, -1), 'RIGHT'),
                ('ALIGN', (1, 0), (1, -1), 'CENTER'),
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
                ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
                ('BACKGROUND', (0, -1), (-1, -1), colors.HexColor('#e74c3c') if close_data.get('net_profit', 0) < 0 else colors.HexColor('#27ae60')),
                ('TEXTCOLOR', (0, -1), (-1, -1), colors.whitesmoke),
                ('FONTSIZE', (0, -1), (-1, -1), 12),
            ]))
            
            story.append(expenses_table)
            
            # الملاحظات
            if close_data.get('notes'):
                story.append(Spacer(1, 20))
                story.append(Paragraph("ملاحظات:", self.subtitle_style))
                story.append(Paragraph(close_data['notes'], self.normal_style))
            
            # تاريخ الإنتاج
            story.append(Spacer(1, 30))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"تم إنتاج التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.small_style))
            
            # بناء الوثيقة
            doc.build(story)
            
            logger.info(f"تم إنتاج تقرير التقفيل اليومي PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج تقرير التقفيل اليومي PDF: {str(e)}")
            return False
    
    def generate_report(self, report_data: Dict, report_type: str, output_path: str) -> bool:
        """إنتاج تقرير عام"""
        if not SimpleDocTemplate:
            return self._generate_simple_report(report_data, report_type, output_path)
        
        try:
            doc = SimpleDocTemplate(
                output_path,
                pagesize=A4,
                rightMargin=2*cm,
                leftMargin=2*cm,
                topMargin=2*cm,
                bottomMargin=2*cm
            )
            
            story = []
            
            # عنوان التقرير
            report_titles = {
                'sales': 'تقرير المبيعات',
                'inventory': 'تقرير المخزون',
                'repair': 'تقرير الصيانة',
                'profit_loss': 'تقرير الربح والخسارة',
                'customer': 'تقرير العملاء'
            }
            
            title = report_titles.get(report_type, 'تقرير')
            story.append(Paragraph(title, self.title_style))
            
            # فترة التقرير
            if report_data.get('period'):
                period = report_data['period']
                period_text = f"من {period.get('start', '')} إلى {period.get('end', '')}"
                story.append(Paragraph(period_text, self.subtitle_style))
            
            story.append(Spacer(1, 20))
            
            # محتوى التقرير حسب النوع
            if report_type == 'sales':
                self._add_sales_report_content(story, report_data)
            elif report_type == 'inventory':
                self._add_inventory_report_content(story, report_data)
            elif report_type == 'repair':
                self._add_repair_report_content(story, report_data)
            elif report_type == 'profit_loss':
                self._add_profit_loss_report_content(story, report_data)
            elif report_type == 'customer':
                self._add_customer_report_content(story, report_data)
            
            # تاريخ الإنتاج
            story.append(Spacer(1, 30))
            story.append(HRFlowable(width="100%", thickness=1, color=colors.HexColor('#bdc3c7')))
            story.append(Spacer(1, 10))
            story.append(Paragraph(f"تم إنتاج التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}", self.small_style))
            
            # بناء الوثيقة
            doc.build(story)
            
            logger.info(f"تم إنتاج {title} PDF: {output_path}")
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج التقرير PDF: {str(e)}")
            return False
    
    def _add_sales_report_content(self, story, data):
        """إضافة محتوى تقرير المبيعات"""
        summary = data.get('summary', {})
        
        # الملخص
        summary_data = [
            ['البيان', 'القيمة'],
            ['إجمالي المعاملات', str(summary.get('total_transactions', 0))],
            ['إجمالي المبيعات', f"{summary.get('total_sales', 0):.2f} ر.س"],
            ['إجمالي الخصومات', f"{summary.get('total_discounts', 0):.2f} ر.س"],
            ['إجمالي الضرائب', f"{summary.get('total_tax', 0):.2f} ر.س"],
            ['متوسط المعاملة', f"{summary.get('avg_transaction', 0):.2f} ر.س"],
        ]
        
        summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
        summary_table.setStyle(self._get_table_style())
        story.append(summary_table)
        story.append(Spacer(1, 20))
        
        # أفضل المنتجات
        if data.get('top_products'):
            story.append(Paragraph("أكثر المنتجات مبيعاً", self.subtitle_style))
            
            products_data = [['المنتج', 'الكمية', 'الإيراد']]
            for product in data['top_products'][:10]:
                products_data.append([
                    product['name'],
                    str(product.get('total_sold', 0)),
                    f"{product.get('total_revenue', 0):.2f} ر.س"
                ])
            
            products_table = Table(products_data, colWidths=[6*cm, 2*cm, 4*cm])
            products_table.setStyle(self._get_table_style())
            story.append(products_table)
    
    def _add_inventory_report_content(self, story, data):
        """إضافة محتوى تقرير المخزون"""
        summary = data.get('summary', {})
        
        # الملخص
        summary_data = [
            ['البيان', 'القيمة'],
            ['إجمالي المنتجات', str(summary.get('total_products', 0))],
            ['إجمالي الكمية', str(summary.get('total_quantity', 0))],
            ['قيمة التكلفة', f"{summary.get('total_cost_value', 0):.2f} ر.س"],
            ['قيمة البيع', f"{summary.get('total_selling_value', 0):.2f} ر.س"],
            ['مخزون منخفض', str(summary.get('low_stock_count', 0))],
            ['نفد من المخزون', str(summary.get('out_of_stock_count', 0))],
        ]
        
        summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
        summary_table.setStyle(self._get_table_style())
        story.append(summary_table)
    
    def _add_repair_report_content(self, story, data):
        """إضافة محتوى تقرير الصيانة"""
        summary = data.get('summary', {})
        
        # الملخص
        summary_data = [
            ['البيان', 'القيمة'],
            ['إجمالي التذاكر', str(summary.get('total_tickets', 0))],
            ['المكتملة', str(summary.get('completed_tickets', 0))],
            ['قيد العمل', str(summary.get('in_progress_tickets', 0))],
            ['المسلمة', str(summary.get('delivered_tickets', 0))],
            ['إجمالي الإيراد', f"{summary.get('total_revenue', 0):.2f} ر.س"],
        ]
        
        summary_table = Table(summary_data, colWidths=[6*cm, 4*cm])
        summary_table.setStyle(self._get_table_style())
        story.append(summary_table)
    
    def _add_profit_loss_report_content(self, story, data):
        """إضافة محتوى تقرير الربح والخسارة"""
        revenue = data.get('revenue', {})
        costs = data.get('costs', {})
        profit = data.get('profit', {})
        
        # الإيرادات
        story.append(Paragraph("الإيرادات", self.subtitle_style))
        revenue_data = [
            ['البيان', 'المبلغ'],
            ['إيرادات المبيعات', f"{revenue.get('sales_revenue', 0):.2f} ر.س"],
            ['إيرادات الصيانة', f"{revenue.get('repair_revenue', 0):.2f} ر.س"],
            ['إجمالي الإيرادات', f"{revenue.get('total_revenue', 0):.2f} ر.س"],
        ]
        
        revenue_table = Table(revenue_data, colWidths=[6*cm, 4*cm])
        revenue_table.setStyle(self._get_table_style())
        story.append(revenue_table)
        story.append(Spacer(1, 15))
        
        # التكاليف
        story.append(Paragraph("التكاليف", self.subtitle_style))
        costs_data = [
            ['البيان', 'المبلغ'],
            ['تكلفة البضاعة المباعة', f"{costs.get('cost_of_goods_sold', 0):.2f} ر.س"],
            ['المرتجعات', f"{revenue.get('returns', 0):.2f} ر.س"],
        ]
        
        costs_table = Table(costs_data, colWidths=[6*cm, 4*cm])
        costs_table.setStyle(self._get_table_style())
        story.append(costs_table)
        story.append(Spacer(1, 15))
        
        # الأرباح
        story.append(Paragraph("الأرباح", self.subtitle_style))
        profit_data = [
            ['البيان', 'المبلغ', 'النسبة'],
            ['الربح الإجمالي', f"{profit.get('gross_profit', 0):.2f} ر.س", f"{profit.get('gross_margin', 0):.1f}%"],
            ['صافي الربح', f"{profit.get('net_profit', 0):.2f} ر.س", f"{profit.get('net_margin', 0):.1f}%"],
        ]
        
        profit_table = Table(profit_data, colWidths=[4*cm, 4*cm, 2*cm])
        profit_table.setStyle(self._get_table_style())
        story.append(profit_table)
    
    def _add_customer_report_content(self, story, data):
        """إضافة محتوى تقرير العملاء"""
        statistics = data.get('statistics', {})
        
        # الإحصائيات
        stats_data = [
            ['البيان', 'القيمة'],
            ['إجمالي العملاء', str(statistics.get('total_customers', 0))],
            ['عملاء المبيعات', str(statistics.get('purchasing_customers', 0))],
            ['عملاء الصيانة', str(statistics.get('repair_customers', 0))],
        ]
        
        stats_table = Table(stats_data, colWidths=[6*cm, 4*cm])
        stats_table.setStyle(self._get_table_style())
        story.append(stats_table)
        story.append(Spacer(1, 20))
        
        # أفضل العملاء
        if data.get('top_customers'):
            story.append(Paragraph("أفضل العملاء", self.subtitle_style))
            
            customers_data = [['العميل', 'المشتريات', 'إجمالي الإنفاق']]
            for customer in data['top_customers'][:10]:
                customers_data.append([
                    customer.get('name', 'غير محدد'),
                    str(customer.get('total_purchases', 0)),
                    f"{customer.get('total_spent', 0):.2f} ر.س"
                ])
            
            customers_table = Table(customers_data, colWidths=[6*cm, 2*cm, 4*cm])
            customers_table.setStyle(self._get_table_style())
            story.append(customers_table)
    
    def _get_table_style(self):
        """الحصول على نمط الجداول الافتراضي"""
        return TableStyle([
            ('FONTNAME', (0, 0), (-1, -1), self.arabic_font),
            ('FONTSIZE', (0, 0), (-1, -1), 10),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
            ('GRID', (0, 0), (-1, -1), 1, colors.HexColor('#bdc3c7')),
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor('#34495e')),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
            ('FONTSIZE', (0, 0), (-1, 0), 11),
        ])
    
    def _get_payment_method_name(self, method: str) -> str:
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
    
    def _get_repair_type_name(self, repair_type: str) -> str:
        """الحصول على اسم نوع الصيانة بالعربية"""
        names = {
            'hardware': 'هاردوير',
            'software': 'سوفتوير'
        }
        return names.get(repair_type, repair_type)
    
    def _get_repair_status_name(self, status: str) -> str:
        """الحصول على اسم حالة الصيانة بالعربية"""
        names = {
            'received': 'مستلمة',
            'in_progress': 'قيد العمل',
            'waiting_parts': 'انتظار قطع غيار',
            'completed': 'مكتملة',
            'delivered': 'مسلمة',
            'cancelled': 'ملغاة'
        }
        return names.get(status, status)
    
    # مولدات بديلة للحالات التي لا تتوفر فيها مكتبة reportlab
    
    def _generate_simple_invoice(self, sale_data: Dict, output_path: str) -> bool:
        """إنتاج فاتورة نصية بسيطة"""
        try:
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("فاتورة مبيعات\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"رقم الفاتورة: {sale_data['id']}\n")
                f.write(f"التاريخ: {sale_data['created_at'][:16]}\n")
                f.write(f"وسيلة الدفع: {self._get_payment_method_name(sale_data.get('payment_method', ''))}\n")
                
                if sale_data.get('customer_name'):
                    f.write(f"العميل: {sale_data['customer_name']}\n")
                    if sale_data.get('customer_phone'):
                        f.write(f"الهاتف: {sale_data['customer_phone']}\n")
                
                f.write("\n" + "-" * 50 + "\n")
                f.write("العناصر:\n")
                f.write("-" * 50 + "\n")
                
                for item in sale_data.get('items', []):
                    f.write(f"{item.get('product_name', 'غير محدد')} x {item['quantity']} = {item['total_amount']:.2f} ر.س\n")
                
                f.write("-" * 50 + "\n")
                f.write(f"المجموع الفرعي: {sale_data['total_amount']:.2f} ر.س\n")
                f.write(f"الخصم: {sale_data.get('discount_amount', 0):.2f} ر.س\n")
                f.write(f"الضريبة: {sale_data.get('tax_amount', 0):.2f} ر.س\n")
                f.write(f"المجموع النهائي: {sale_data['final_amount']:.2f} ر.س\n")
                
                if sale_data.get('notes'):
                    f.write(f"\nملاحظات: {sale_data['notes']}\n")
                
                f.write("\nشكراً لزيارتكم\n")
                
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج الفاتورة النصية: {str(e)}")
            return False
    
    def _generate_simple_repair_ticket(self, ticket_data: Dict, output_path: str) -> bool:
        """إنتاج تذكرة صيانة نصية بسيطة"""
        try:
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("تذكرة صيانة\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"رقم التذكرة: {ticket_data['id']}\n")
                f.write(f"تاريخ الاستلام: {ticket_data['received_date'][:16]}\n")
                f.write(f"نوع الصيانة: {self._get_repair_type_name(ticket_data.get('repair_type', ''))}\n")
                f.write(f"الحالة: {self._get_repair_status_name(ticket_data.get('status', ''))}\n")
                
                if ticket_data.get('customer_name'):
                    f.write(f"العميل: {ticket_data['customer_name']}\n")
                    if ticket_data.get('customer_phone'):
                        f.write(f"الهاتف: {ticket_data['customer_phone']}\n")
                
                f.write(f"الجهاز: {ticket_data.get('device_info', 'غير محدد')}\n")
                if ticket_data.get('imei'):
                    f.write(f"IMEI: {ticket_data['imei']}\n")
                
                f.write(f"\nوصف المشكلة:\n{ticket_data.get('problem_description', '')}\n")
                
                f.write(f"\nالتكلفة المقدرة: {ticket_data.get('estimated_cost', 0):.2f} ر.س\n")
                f.write(f"التكلفة النهائية: {ticket_data.get('final_cost', 0):.2f} ر.س\n")
                
                if ticket_data.get('notes'):
                    f.write(f"\nملاحظات: {ticket_data['notes']}\n")
                
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج تذكرة الصيانة النصية: {str(e)}")
            return False
    
    def _generate_simple_daily_close(self, close_data: Dict, output_path: str) -> bool:
        """إنتاج تقرير تقفيل يومي نصي بسيط"""
        try:
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write("تقرير التقفيل اليومي\n")
                f.write("=" * 50 + "\n\n")
                
                f.write(f"تاريخ التقفيل: {close_data['close_date']}\n\n")
                
                f.write("ملخص المبيعات:\n")
                f.write("-" * 30 + "\n")
                f.write(f"مبيعات نقدية: {close_data.get('cash_sales', 0):.2f} ر.س\n")
                f.write(f"مبيعات البطاقات: {close_data.get('card_sales', 0):.2f} ر.س\n")
                f.write(f"المحافظ الإلكترونية: {close_data.get('wallet_sales', 0):.2f} ر.س\n")
                f.write(f"إجمالي المبيعات: {close_data.get('total_sales', 0):.2f} ر.س\n")
                
                if close_data.get('repair_revenue'):
                    f.write(f"إيراد الصيانة: {close_data['repair_revenue']:.2f} ر.س\n")
                
                if close_data.get('returns'):
                    f.write(f"المرتجعات: {close_data['returns']:.2f} ر.س\n")
                
                f.write(f"\nصافي الإيراد: {close_data.get('total_revenue', 0):.2f} ر.س\n")
                
                f.write("\nالمصروفات والأرصدة:\n")
                f.write("-" * 30 + "\n")
                f.write(f"المصروفات: {close_data.get('expenses', 0):.2f} ر.س\n")
                f.write(f"المشتريات: {close_data.get('purchases', 0):.2f} ر.س\n")
                f.write(f"رصيد أول اليوم: {close_data.get('opening_balance', 0):.2f} ر.س\n")
                f.write(f"رصيد آخر اليوم: {close_data.get('closing_balance', 0):.2f} ر.س\n")
                f.write(f"صافي الربح: {close_data.get('net_profit', 0):.2f} ر.س\n")
                
                if close_data.get('notes'):
                    f.write(f"\nملاحظات: {close_data['notes']}\n")
                
                f.write(f"\nتم إنتاج التقرير في: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج تقرير التقفيل النصي: {str(e)}")
            return False
    
    def _generate_simple_report(self, report_data: Dict, report_type: str, output_path: str) -> bool:
        """إنتاج تقرير نصي بسيط"""
        try:
            report_titles = {
                'sales': 'تقرير المبيعات',
                'inventory': 'تقرير المخزون',
                'repair': 'تقرير الصيانة',
                'profit_loss': 'تقرير الربح والخسارة',
                'customer': 'تقرير العملاء'
            }
            
            title = report_titles.get(report_type, 'تقرير')
            
            with open(output_path.replace('.pdf', '.txt'), 'w', encoding='utf-8') as f:
                f.write("=" * 50 + "\n")
                f.write(f"{title}\n")
                f.write("=" * 50 + "\n\n")
                
                if report_data.get('period'):
                    period = report_data['period']
                    f.write(f"الفترة: من {period.get('start', '')} إلى {period.get('end', '')}\n\n")
                
                # كتابة محتوى مبسط للتقرير
                f.write("بيانات التقرير:\n")
                f.write("-" * 30 + "\n")
                f.write(f"نوع التقرير: {title}\n")
                f.write(f"تاريخ الإنتاج: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
                
                # إضافة ملخص بسيط
                if 'summary' in report_data:
                    summary = report_data['summary']
                    f.write("\nالملخص:\n")
                    for key, value in summary.items():
                        f.write(f"{key}: {value}\n")
                
            return True
            
        except Exception as e:
            logger.error(f"خطأ في إنتاج التقرير النصي: {str(e)}")
            return False
