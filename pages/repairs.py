"""
Enhanced Repairs Management Page for Mobile Shop Management System
Comprehensive repair tracking and management with modern UI
"""

from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QGridLayout, QLabel, QPushButton,
    QFrame, QTableWidget, QTableWidgetItem, QLineEdit, QComboBox, QSpinBox,
    QDoubleSpinBox, QTextEdit, QHeaderView, QScrollArea, QProgressBar,
    QMessageBox, QDialog, QFormLayout, QGraphicsDropShadowEffect,
    QCheckBox, QGroupBox, QDateEdit, QTabWidget, QSplitter
)
from PyQt6.QtCore import Qt, QTimer, pyqtSignal, QDate, QPropertyAnimation, QEasingCurve
from PyQt6.QtGui import QFont, QColor, QPixmap, QPainter, QIcon
from datetime import datetime, timedelta
from uuid import uuid4

from ui.styles import ModernStyles
from ui.dialogs import AddRepairDialog, EditRepairDialog, RepairStatusDialog
from ui.widgets import StatCard, RepairCard

class RepairStatsWidget(QFrame):
    """Repair statistics display widget"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.setup_ui()
        
    def setup_ui(self):
        """Setup statistics UI"""
        self.setStyleSheet(ModernStyles.get_card_style())
        
        layout = QGridLayout(self)
        layout.setSpacing(20)
        layout.setContentsMargins(20, 20, 20, 20)
        
        # Statistics cards
        self.total_repairs_card = StatCard("إجمالي الإصلاحات", "0", "🔧", "#3b82f6")
        self.pending_repairs_card = StatCard("في الانتظار", "0", "⏳", "#f59e0b")
        self.in_progress_card = StatCard("قيد الإصلاح", "0", "🔄", "#8b5cf6")
        self.completed_card = StatCard("مكتملة", "0", "✅", "#10b981")
        
        layout.addWidget(self.total_repairs_card, 0, 0)
        layout.addWidget(self.pending_repairs_card, 0, 1)
        layout.addWidget(self.in_progress_card, 0, 2)
        layout.addWidget(self.completed_card, 0, 3)
        
    def update_statistics(self):
        """Update repair statistics"""
        try:
            # Total repairs
            total_repairs = self.db_manager.execute_query("""
                SELECT COUNT(*) as count FROM repairs
            """)[0]['count']
            
            # Status-wise counts
            status_counts = self.db_manager.execute_query("""
                SELECT 
                    status,
                    COUNT(*) as count
                FROM repairs 
                GROUP BY status
            """)
            
            # Initialize counts
            pending_count = 0
            in_progress_count = 0
            completed_count = 0
            
            for status in status_counts:
                if status['status'] == 'في الانتظار':
                    pending_count = status['count']
                elif status['status'] == 'قيد الإصلاح':
                    in_progress_count = status['count']
                elif status['status'] in ['مكتمل', 'مسلم للعميل']:
                    completed_count += status['count']
            
            # Update cards
            self.total_repairs_card.update_value(str(total_repairs))
            self.pending_repairs_card.update_value(str(pending_count))
            self.in_progress_card.update_value(str(in_progress_count))
            self.completed_card.update_value(str(completed_count))
            
        except Exception as e:
            print(f"Error updating repair statistics: {e}")

class RepairTableWidget(QTableWidget):
    """Enhanced repair table with advanced features"""
    
    repair_selected = pyqtSignal(dict)
    repair_double_clicked = pyqtSignal(dict)
    
    def __init__(self):
        super().__init__()
        self.repairs_data = []
        self.setup_ui()
        
    def setup_ui(self):
        """Setup table UI"""
        self.setColumnCount(12)
        self.setHorizontalHeaderLabels([
            "الإجراءات", "الحالة", "الأولوية", "التاريخ المتوقع", "التكلفة", 
            "نوع الإصلاح", "المشكلة", "الجهاز", "رقم الهاتف", "اسم العميل", "رقم الإصلاح", "ID"
        ])
        
        # Hide ID column
        self.setColumnHidden(11, True)
        
        # Set column widths
        header = self.horizontalHeader()
        header.setStretchLastSection(False)
        header.resizeSection(0, 120)  # Actions
        header.resizeSection(1, 100)  # Status
        header.resizeSection(2, 80)   # Priority
        header.resizeSection(3, 120)  # Date
        header.resizeSection(4, 100)  # Cost
        header.resizeSection(5, 120)  # Repair type
        header.resizeSection(6, 200)  # Problem
        header.resizeSection(7, 150)  # Device
        header.resizeSection(8, 120)  # Phone
        header.resizeSection(9, 150)  # Customer
        header.resizeSection(10, 120) # Repair ID
        
        # Table properties
        self.setAlternatingRowColors(True)
        self.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self.setSelectionMode(QTableWidget.SelectionMode.SingleSelection)
        self.setStyleSheet(ModernStyles.get_table_style())
        
        # Connect signals
        self.itemSelectionChanged.connect(self.on_selection_changed)
        self.itemDoubleClicked.connect(self.on_double_click)
        
    def populate_table(self, repairs):
        """Populate table with repairs data"""
        self.repairs_data = repairs
        self.setRowCount(len(repairs))
        
        for row, repair in enumerate(repairs):
            # Actions column
            actions_widget = self.create_actions_widget(repair)
            self.setCellWidget(row, 0, actions_widget)
            
            # Status column with color coding
            status_widget = self.create_status_widget(repair)
            self.setCellWidget(row, 1, status_widget)
            
            # Priority column with color coding
            priority_item = QTableWidgetItem(repair['priority'])
            if repair['priority'] == 'طارئ':
                priority_item.setBackground(QColor(254, 226, 226))  # Red
                priority_item.setForeground(QColor(153, 27, 27))
            elif repair['priority'] == 'مستعجل':
                priority_item.setBackground(QColor(254, 249, 195))  # Yellow
                priority_item.setForeground(QColor(146, 64, 14))
            self.setItem(row, 2, priority_item)
            
            # Expected delivery date
            expected_date = ""
            if repair['receive_date'] and repair['estimated_days']:
                try:
                    receive_date = datetime.strptime(repair['receive_date'], '%Y-%m-%d')
                    expected_date = (receive_date + timedelta(days=repair['estimated_days'])).strftime('%Y-%m-%d')
                except:
                    expected_date = "غير محدد"
            self.setItem(row, 3, QTableWidgetItem(expected_date))
            
            # Cost
            cost_str = f"{repair['estimated_cost']:.2f}"
            if repair['actual_cost'] and repair['actual_cost'] > 0:
                cost_str = f"{repair['actual_cost']:.2f}"
            self.setItem(row, 4, QTableWidgetItem(cost_str))
            
            # Repair type
            self.setItem(row, 5, QTableWidgetItem(repair['repair_type'] or ''))
            
            # Problem description (truncated)
            problem = repair['problem_description'] or ''
            if len(problem) > 50:
                problem = problem[:50] + "..."
            self.setItem(row, 6, QTableWidgetItem(problem))
            
            # Device info
            device_info = f"{repair['device_type']} {repair['device_model'] or ''}".strip()
            self.setItem(row, 7, QTableWidgetItem(device_info))
            
            # Customer phone
            self.setItem(row, 8, QTableWidgetItem(repair['customer_phone'] or ''))
            
            # Customer name
            name_item = QTableWidgetItem(repair['customer_name'])
            name_item.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
            self.setItem(row, 9, name_item)
            
            # Repair ID
            self.setItem(row, 10, QTableWidgetItem(str(repair['id'])))
            
            # Hidden ID
            self.setItem(row, 11, QTableWidgetItem(str(repair['id'])))
            
    def create_actions_widget(self, repair):
        """Create actions widget for repair row"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 2, 5, 2)
        layout.setSpacing(5)
        
        # Edit button
        edit_btn = QPushButton("✏️")
        edit_btn.setFixedSize(30, 25)
        edit_btn.setToolTip("تعديل الإصلاح")
        edit_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        edit_btn.clicked.connect(lambda: self.edit_repair(repair))
        
        # Status button
        status_btn = QPushButton("🔄")
        status_btn.setFixedSize(30, 25)
        status_btn.setToolTip("تحديث الحالة")
        status_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        status_btn.clicked.connect(lambda: self.update_status(repair))
        
        # Print button
        print_btn = QPushButton("🖨️")
        print_btn.setFixedSize(30, 25)
        print_btn.setToolTip("طباعة")
        print_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 12px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        print_btn.clicked.connect(lambda: self.print_repair(repair))
        
        layout.addWidget(edit_btn)
        layout.addWidget(status_btn)
        layout.addWidget(print_btn)
        
        return widget
        
    def create_status_widget(self, repair):
        """Create status indicator widget"""
        widget = QWidget()
        layout = QHBoxLayout(widget)
        layout.setContentsMargins(5, 5, 5, 5)
        layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        
        # Status indicator with color
        status_colors = {
            'في الانتظار': '#f59e0b',
            'قيد الإصلاح': '#8b5cf6',
            'في انتظار قطع الغيار': '#ef4444',
            'مكتمل': '#10b981',
            'مسلم للعميل': '#059669',
            'ملغي': '#6b7280'
        }
        
        color = status_colors.get(repair['status'], '#6b7280')
        
        indicator = QLabel("●")
        indicator.setStyleSheet(f"color: {color}; font-size: 16px;")
        indicator.setToolTip(repair['status'])
        
        status_label = QLabel(repair['status'])
        status_label.setStyleSheet(f"color: {color}; font-weight: bold; font-size: 10px;")
        
        layout.addWidget(indicator)
        layout.addWidget(status_label)
        return widget
        
    def edit_repair(self, repair):
        """Edit repair"""
        self.repair_double_clicked.emit(repair)
        
    def update_status(self, repair):
        """Update repair status"""
        parent = self.parent()
        while parent and not hasattr(parent, 'db_manager'):
            parent = parent.parent()
        
        if parent and hasattr(parent, 'db_manager'):
            dialog = RepairStatusDialog(repair, parent.db_manager, self)
            if dialog.exec() == dialog.DialogCode.Accepted:
                if hasattr(parent, 'refresh_repairs'):
                    parent.refresh_repairs()
        
    def print_repair(self, repair):
        """Print repair receipt"""
        QMessageBox.information(self, "طباعة", "سيتم تطوير وظيفة الطباعة قريباً")
        
    def on_selection_changed(self):
        """Handle selection change"""
        current_row = self.currentRow()
        if current_row >= 0 and current_row < len(self.repairs_data):
            repair = self.repairs_data[current_row]
            self.repair_selected.emit(repair)
            
    def on_double_click(self, item):
        """Handle double click"""
        row = item.row()
        if row >= 0 and row < len(self.repairs_data):
            repair = self.repairs_data[row]
            self.repair_double_clicked.emit(repair)

class RepairsPage(QWidget):
    """Enhanced repairs management page"""
    
    def __init__(self, db_manager):
        super().__init__()
        self.db_manager = db_manager
        self.current_repairs = []
        self.setup_ui()
        self.refresh_data()
        
    def setup_ui(self):
        """Setup repairs page UI"""
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # Header section
        self.setup_header(main_layout)
        
        # Statistics section
        self.stats_widget = RepairStatsWidget(self.db_manager)
        main_layout.addWidget(self.stats_widget)
        
        # Search and filters section
        self.setup_search_filters(main_layout)
        
        # Main content (table and details)
        self.setup_main_content(main_layout)
        
    def setup_header(self, parent_layout):
        """Setup header section"""
        header_frame = QFrame()
        header_frame.setStyleSheet("""
            QFrame {
                background: qlineargradient(x1:0, y1:0, x2:1, y2:1,
                    stop:0 #f59e0b, stop:1 #d97706);
                border-radius: 15px;
                padding: 25px;
            }
        """)
        
        header_layout = QHBoxLayout(header_frame)
        
        # Title
        title_layout = QVBoxLayout()
        title = QLabel("🔧 إدارة طلبات الإصلاح")
        title.setFont(QFont("Tahoma", 20, QFont.Weight.Bold))
        title.setStyleSheet("color: white;")
        
        subtitle = QLabel("تتبع وإدارة جميع طلبات الإصلاح بكفاءة عالية")
        subtitle.setFont(QFont("Tahoma", 12))
        subtitle.setStyleSheet("color: rgba(255, 255, 255, 0.9);")
        
        title_layout.addWidget(title)
        title_layout.addWidget(subtitle)
        
        # Action buttons
        buttons_layout = QHBoxLayout()
        
        add_repair_btn = QPushButton("➕ إصلاح جديد")
        add_repair_btn.setFixedHeight(45)
        add_repair_btn.setStyleSheet("""
            QPushButton {
                background-color: #10b981;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #059669;
            }
        """)
        add_repair_btn.clicked.connect(self.add_repair)
        
        complete_batch_btn = QPushButton("✅ إكمال دفعة")
        complete_batch_btn.setFixedHeight(45)
        complete_batch_btn.setStyleSheet("""
            QPushButton {
                background-color: #3b82f6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #2563eb;
            }
        """)
        complete_batch_btn.clicked.connect(self.complete_batch)
        
        print_report_btn = QPushButton("📄 تقرير")
        print_report_btn.setFixedHeight(45)
        print_report_btn.setStyleSheet("""
            QPushButton {
                background-color: #8b5cf6;
                color: white;
                border: none;
                padding: 12px 20px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #7c3aed;
            }
        """)
        print_report_btn.clicked.connect(self.print_report)
        
        buttons_layout.addWidget(add_repair_btn)
        buttons_layout.addWidget(complete_batch_btn)
        buttons_layout.addWidget(print_report_btn)
        buttons_layout.addStretch()
        
        header_layout.addLayout(title_layout, 1)
        header_layout.addLayout(buttons_layout)
        
        parent_layout.addWidget(header_frame)
        
    def setup_search_filters(self, parent_layout):
        """Setup search and filters section"""
        filters_frame = QFrame()
        filters_frame.setStyleSheet(ModernStyles.get_card_style())
        
        filters_layout = QHBoxLayout(filters_frame)
        filters_layout.setSpacing(15)
        
        # Search
        search_label = QLabel("🔍 البحث:")
        search_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("البحث برقم الإصلاح، اسم العميل، أو رقم الهاتف...")
        self.search_input.setStyleSheet(ModernStyles.get_input_style())
        self.search_input.textChanged.connect(self.filter_repairs)
        
        # Status filter
        status_label = QLabel("📊 الحالة:")
        status_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.status_filter = QComboBox()
        self.status_filter.addItems([
            "جميع الحالات", "في الانتظار", "قيد الإصلاح", 
            "في انتظار قطع الغيار", "مكتمل", "مسلم للعميل", "ملغي"
        ])
        self.status_filter.setStyleSheet(ModernStyles.get_input_style())
        self.status_filter.currentTextChanged.connect(self.filter_repairs)
        
        # Priority filter
        priority_label = QLabel("⚡ الأولوية:")
        priority_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.priority_filter = QComboBox()
        self.priority_filter.addItems(["جميع الأولويات", "عادي", "مستعجل", "طارئ"])
        self.priority_filter.setStyleSheet(ModernStyles.get_input_style())
        self.priority_filter.currentTextChanged.connect(self.filter_repairs)
        
        # Date range
        date_label = QLabel("📅 التاريخ:")
        date_label.setFont(QFont("Tahoma", 11, QFont.Weight.Bold))
        
        self.date_from = QDateEdit()
        self.date_from.setDate(QDate.currentDate().addDays(-30))
        self.date_from.setCalendarPopup(True)
        self.date_from.setStyleSheet(ModernStyles.get_input_style())
        self.date_from.dateChanged.connect(self.filter_repairs)
        
        self.date_to = QDateEdit()
        self.date_to.setDate(QDate.currentDate())
        self.date_to.setCalendarPopup(True)
        self.date_to.setStyleSheet(ModernStyles.get_input_style())
        self.date_to.dateChanged.connect(self.filter_repairs)
        
        # Refresh button
        refresh_btn = QPushButton("🔄 تحديث")
        refresh_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
        refresh_btn.clicked.connect(self.refresh_data)
        
        filters_layout.addWidget(search_label)
        filters_layout.addWidget(self.search_input, 2)
        filters_layout.addWidget(status_label)
        filters_layout.addWidget(self.status_filter, 1)
        filters_layout.addWidget(priority_label)
        filters_layout.addWidget(self.priority_filter, 1)
        filters_layout.addWidget(date_label)
        filters_layout.addWidget(self.date_from)
        filters_layout.addWidget(QLabel("إلى"))
        filters_layout.addWidget(self.date_to)
        filters_layout.addWidget(refresh_btn)
        
        parent_layout.addWidget(filters_frame)
        
    def setup_main_content(self, parent_layout):
        """Setup main content area"""
        # Create splitter for table and details
        splitter = QSplitter(Qt.Orientation.Horizontal)
        
        # Repairs table
        table_frame = QFrame()
        table_frame.setStyleSheet(ModernStyles.get_card_style())
        
        table_layout = QVBoxLayout(table_frame)
        table_layout.setContentsMargins(15, 15, 15, 15)
        
        table_header = QLabel("📋 قائمة الإصلاحات")
        table_header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        table_header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        
        self.repairs_table = RepairTableWidget()
        self.repairs_table.repair_selected.connect(self.on_repair_selected)
        self.repairs_table.repair_double_clicked.connect(self.edit_repair)
        
        table_layout.addWidget(table_header)
        table_layout.addWidget(self.repairs_table)
        
        # Repair details panel
        self.details_frame = QFrame()
        self.details_frame.setStyleSheet(ModernStyles.get_card_style())
        self.details_frame.setFixedWidth(350)
        self.setup_details_panel()
        
        splitter.addWidget(table_frame)
        splitter.addWidget(self.details_frame)
        splitter.setSizes([800, 350])
        
        parent_layout.addWidget(splitter, 1)
        
    def setup_details_panel(self):
        """Setup repair details panel"""
        layout = QVBoxLayout(self.details_frame)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)
        
        # Header
        header = QLabel("📄 تفاصيل الإصلاح")
        header.setFont(QFont("Tahoma", 14, QFont.Weight.Bold))
        header.setStyleSheet("color: #374151; margin-bottom: 10px;")
        layout.addWidget(header)
        
        # Details area
        self.details_scroll = QScrollArea()
        self.details_scroll.setWidgetResizable(True)
        self.details_scroll.setStyleSheet("""
            QScrollArea {
                border: none;
                background: transparent;
            }
        """)
        
        self.details_widget = QWidget()
        self.details_layout = QVBoxLayout(self.details_widget)
        self.details_layout.setSpacing(10)
        
        # Default message
        default_label = QLabel("اختر إصلاحاً من القائمة لعرض التفاصيل")
        default_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        default_label.setStyleSheet("color: #9ca3af; font-style: italic; padding: 50px;")
        self.details_layout.addWidget(default_label)
        
        self.details_scroll.setWidget(self.details_widget)
        layout.addWidget(self.details_scroll, 1)
        
    def refresh_data(self):
        """Refresh all data"""
        try:
            # Refresh statistics
            self.stats_widget.update_statistics()
            
            # Refresh repairs
            self.refresh_repairs()
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحديث البيانات: {str(e)}")
            
    def refresh_repairs(self):
        """Refresh repairs table"""
        try:
            repairs = self.db_manager.execute_query("""
                SELECT * FROM repairs 
                ORDER BY created_at DESC
            """)
            
            self.current_repairs = repairs
            self.repairs_table.populate_table(repairs)
            
        except Exception as e:
            QMessageBox.critical(self, "خطأ", f"فشل في تحميل الإصلاحات: {str(e)}")
            
    def filter_repairs(self):
        """Filter repairs based on search and filters"""
        try:
            search_text = self.search_input.text().lower()
            status = self.status_filter.currentText()
            priority = self.priority_filter.currentText()
            date_from = self.date_from.date().toString("yyyy-MM-dd")
            date_to = self.date_to.date().toString("yyyy-MM-dd")
            
            filtered_repairs = []
            
            for repair in self.current_repairs:
                # Apply search filter
                if search_text:
                    if not (search_text in str(repair['id']).lower() or 
                           search_text in repair['customer_name'].lower() or
                           search_text in (repair['customer_phone'] or '').lower() or
                           search_text in (repair['device_type'] or '').lower()):
                        continue
                
                # Apply status filter
                if status != "جميع الحالات":
                    if repair['status'] != status:
                        continue
                
                # Apply priority filter
                if priority != "جميع الأولويات":
                    if repair['priority'] != priority:
                        continue
                
                # Apply date filter
                if repair['receive_date']:
                    if not (date_from <= repair['receive_date'] <= date_to):
                        continue
                
                filtered_repairs.append(repair)
            
            self.repairs_table.populate_table(filtered_repairs)
            
        except Exception as e:
            print(f"Error filtering repairs: {e}")
            
    def on_repair_selected(self, repair):
        """Handle repair selection"""
        try:
            # Clear existing details
            for i in reversed(range(self.details_layout.count())):
                self.details_layout.itemAt(i).widget().setParent(None)
            
            # Device icon
            device_icon = "📱" if "iphone" in repair['device_type'].lower() else "📱"
            
            # Device label
            device_label = QLabel(device_icon)
            device_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            device_label.setStyleSheet("""
                QLabel {
                    background-color: #f3f4f6;
                    border-radius: 8px;
                    padding: 20px;
                    font-size: 48px;
                }
            """)
            device_label.setFixedHeight(120)
            self.details_layout.addWidget(device_label)
            
            # Repair ID and status
            id_status_layout = QHBoxLayout()
            
            id_label = QLabel(f"#{repair['id']}")
            id_label.setFont(QFont("Tahoma", 16, QFont.Weight.Bold))
            id_label.setStyleSheet("color: #1f2937;")
            
            status_label = QLabel(repair['status'])
            status_label.setFont(QFont("Tahoma", 12, QFont.Weight.Bold))
            status_colors = {
                'في الانتظار': '#f59e0b',
                'قيد الإصلاح': '#8b5cf6',
                'في انتظار قطع الغيار': '#ef4444',
                'مكتمل': '#10b981',
                'مسلم للعميل': '#059669',
                'ملغي': '#6b7280'
            }
            color = status_colors.get(repair['status'], '#6b7280')
            status_label.setStyleSheet(f"color: {color}; background-color: {color}20; padding: 4px 8px; border-radius: 4px;")
            
            id_status_layout.addWidget(id_label)
            id_status_layout.addStretch()
            id_status_layout.addWidget(status_label)
            
            self.details_layout.addLayout(id_status_layout)
            
            # Customer info
            customer_frame = QFrame()
            customer_frame.setStyleSheet("""
                QFrame {
                    background-color: #f9fafb;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            customer_layout = QFormLayout(customer_frame)
            customer_layout.setSpacing(8)
            
            customer_layout.addRow("العميل:", QLabel(repair['customer_name']))
            if repair['customer_phone']:
                customer_layout.addRow("الهاتف:", QLabel(repair['customer_phone']))
            if repair['customer_email']:
                customer_layout.addRow("البريد:", QLabel(repair['customer_email']))
            
            self.details_layout.addWidget(customer_frame)
            
            # Device info
            device_frame = QFrame()
            device_frame.setStyleSheet("""
                QFrame {
                    background-color: #f0f9ff;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            device_layout = QFormLayout(device_frame)
            device_layout.setSpacing(8)
            
            device_layout.addRow("نوع الجهاز:", QLabel(repair['device_type']))
            if repair['device_model']:
                device_layout.addRow("الموديل:", QLabel(repair['device_model']))
            if repair['device_serial']:
                device_layout.addRow("الرقم التسلسلي:", QLabel(repair['device_serial']))
            if repair['device_color']:
                device_layout.addRow("اللون:", QLabel(repair['device_color']))
            
            self.details_layout.addWidget(device_frame)
            
            # Repair details
            repair_frame = QFrame()
            repair_frame.setStyleSheet("""
                QFrame {
                    background-color: #fef7ff;
                    border-radius: 8px;
                    padding: 15px;
                }
            """)
            
            repair_layout = QFormLayout(repair_frame)
            repair_layout.setSpacing(8)
            
            if repair['repair_type']:
                repair_layout.addRow("نوع الإصلاح:", QLabel(repair['repair_type']))
            
            repair_layout.addRow("الأولوية:", QLabel(repair['priority']))
            
            if repair['estimated_cost']:
                repair_layout.addRow("التكلفة المتوقعة:", QLabel(f"{repair['estimated_cost']:.2f} جنيه"))
            
            if repair['actual_cost'] and repair['actual_cost'] > 0:
                repair_layout.addRow("التكلفة الفعلية:", QLabel(f"{repair['actual_cost']:.2f} جنيه"))
            
            if repair['estimated_days']:
                repair_layout.addRow("المدة المتوقعة:", QLabel(f"{repair['estimated_days']} يوم"))
            
            if repair['receive_date']:
                repair_layout.addRow("تاريخ الاستلام:", QLabel(repair['receive_date']))
            
            if repair['delivery_date']:
                repair_layout.addRow("تاريخ التسليم:", QLabel(repair['delivery_date']))
            
            self.details_layout.addWidget(repair_frame)
            
            # Problem description
            if repair['problem_description']:
                problem_frame = QFrame()
                problem_frame.setStyleSheet("""
                    QFrame {
                        background-color: #fef2f2;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                
                problem_layout = QVBoxLayout(problem_frame)
                
                problem_title = QLabel("وصف المشكلة:")
                problem_title.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                
                problem_text = QLabel(repair['problem_description'])
                problem_text.setWordWrap(True)
                problem_text.setStyleSheet("color: #6b7280;")
                
                problem_layout.addWidget(problem_title)
                problem_layout.addWidget(problem_text)
                
                self.details_layout.addWidget(problem_frame)
            
            # Notes
            if repair['notes']:
                notes_frame = QFrame()
                notes_frame.setStyleSheet("""
                    QFrame {
                        background-color: #f0fdf4;
                        border-radius: 8px;
                        padding: 15px;
                    }
                """)
                
                notes_layout = QVBoxLayout(notes_frame)
                
                notes_title = QLabel("ملاحظات:")
                notes_title.setFont(QFont("Tahoma", 10, QFont.Weight.Bold))
                
                notes_text = QLabel(repair['notes'])
                notes_text.setWordWrap(True)
                notes_text.setStyleSheet("color: #6b7280;")
                
                notes_layout.addWidget(notes_title)
                notes_layout.addWidget(notes_text)
                
                self.details_layout.addWidget(notes_frame)
            
            # Action buttons
            buttons_frame = QFrame()
            buttons_layout = QVBoxLayout(buttons_frame)
            buttons_layout.setSpacing(10)
            
            edit_btn = QPushButton("✏️ تعديل الإصلاح")
            edit_btn.setStyleSheet(ModernStyles.get_button_primary_style())
            edit_btn.clicked.connect(lambda: self.edit_repair(repair))
            
            status_btn = QPushButton("🔄 تحديث الحالة")
            status_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
            status_btn.clicked.connect(lambda: self.update_status(repair))
            
            print_btn = QPushButton("🖨️ طباعة إيصال")
            print_btn.setStyleSheet(ModernStyles.get_button_secondary_style())
            print_btn.clicked.connect(lambda: self.print_receipt(repair))
            
            buttons_layout.addWidget(edit_btn)
            buttons_layout.addWidget(status_btn)
            buttons_layout.addWidget(print_btn)
            
            self.details_layout.addWidget(buttons_frame)
            self.details_layout.addStretch()
            
        except Exception as e:
            print(f"Error displaying repair details: {e}")
            
    def add_repair(self):
        """Add new repair"""
        dialog = AddRepairDialog(self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def edit_repair(self, repair):
        """Edit existing repair"""
        dialog = EditRepairDialog(repair, self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def update_status(self, repair):
        """Update repair status"""
        dialog = RepairStatusDialog(repair, self.db_manager, self)
        if dialog.exec() == dialog.DialogCode.Accepted:
            self.refresh_data()
            
    def complete_batch(self):
        """Complete batch of repairs"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة إكمال الدفعة قريباً")
        
    def print_report(self):
        """Print repairs report"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة التقارير قريباً")
        
    def print_receipt(self, repair):
        """Print repair receipt"""
        QMessageBox.information(self, "قريباً", "سيتم تطوير وظيفة الطباعة قريباً")
