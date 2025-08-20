"""
Modern Styles for Mobile Shop Management System
Beautiful and consistent styling across the application
"""

class ModernStyles:
    """Collection of modern styles for the application"""
    
    # Color palette
    PRIMARY_BLUE = "#3b82f6"
    PRIMARY_BLUE_HOVER = "#2563eb"
    PRIMARY_BLUE_DARK = "#1d4ed8"
    
    SUCCESS_GREEN = "#10b981"
    SUCCESS_GREEN_HOVER = "#059669"
    
    WARNING_ORANGE = "#f59e0b"
    WARNING_ORANGE_HOVER = "#d97706"
    
    DANGER_RED = "#ef4444"
    DANGER_RED_HOVER = "#dc2626"
    
    GRAY_50 = "#f9fafb"
    GRAY_100 = "#f3f4f6"
    GRAY_200 = "#e5e7eb"
    GRAY_300 = "#d1d5db"
    GRAY_400 = "#9ca3af"
    GRAY_500 = "#6b7280"
    GRAY_600 = "#4b5563"
    GRAY_700 = "#374151"
    GRAY_800 = "#1f2937"
    GRAY_900 = "#111827"
    
    @staticmethod
    def get_main_window_style():
        """Main window styling"""
        return """
            QMainWindow {
                background-color: #f8fafc;
                border: none;
            }
            
            QWidget {
                font-family: 'Segoe UI', 'Tahoma', sans-serif;
                font-size: 10pt;
            }
        """
    
    @staticmethod
    def get_sidebar_style():
        """Sidebar styling"""
        return f"""
            QFrame {{
                background-color: white;
                border: none;
                border-right: 1px solid {ModernStyles.GRAY_200};
            }}
        """
    
    @staticmethod
    def get_nav_button_style():
        """Navigation button default style"""
        return f"""
            QPushButton {{
                background-color: transparent;
                border: none;
                padding: 15px 20px;
                text-align: right;
                font-size: 13px;
                font-weight: 500;
                color: {ModernStyles.GRAY_600};
                border-radius: 12px;
                margin: 2px 8px;
                border-left: 3px solid transparent;
            }}
        """
    
    @staticmethod
    def get_hover_nav_button_style():
        """Navigation button hover style"""
        return f"""
            QPushButton {{
                background-color: {ModernStyles.GRAY_50};
                border: none;
                padding: 15px 20px;
                text-align: right;
                font-size: 13px;
                font-weight: 500;
                color: {ModernStyles.GRAY_700};
                border-radius: 12px;
                margin: 2px 8px;
                border-left: 3px solid {ModernStyles.PRIMARY_BLUE};
            }}
        """
    
    @staticmethod
    def get_active_nav_button_style():
        """Navigation button active style"""
        return f"""
            QPushButton {{
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernStyles.PRIMARY_BLUE}, stop:1 {ModernStyles.PRIMARY_BLUE_HOVER});
                border: none;
                padding: 15px 20px;
                text-align: right;
                font-size: 13px;
                font-weight: bold;
                color: white;
                border-radius: 12px;
                margin: 2px 8px;
                border-left: 3px solid {ModernStyles.PRIMARY_BLUE_DARK};
            }}
        """
    
    @staticmethod
    def get_card_style():
        """Card container style"""
        return f"""
            QFrame {{
                background-color: white;
                border: 1px solid {ModernStyles.GRAY_200};
                border-radius: 12px;
                padding: 20px;
            }}
        """
    
    @staticmethod
    def get_button_primary_style():
        """Primary button style"""
        return f"""
            QPushButton {{
                background-color: {ModernStyles.PRIMARY_BLUE};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernStyles.PRIMARY_BLUE_HOVER};
            }}
            QPushButton:pressed {{
                background-color: {ModernStyles.PRIMARY_BLUE_DARK};
            }}
            QPushButton:disabled {{
                background-color: {ModernStyles.GRAY_300};
                color: {ModernStyles.GRAY_500};
            }}
        """
    
    @staticmethod
    def get_button_success_style():
        """Success button style"""
        return f"""
            QPushButton {{
                background-color: {ModernStyles.SUCCESS_GREEN};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernStyles.SUCCESS_GREEN_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {ModernStyles.GRAY_300};
                color: {ModernStyles.GRAY_500};
            }}
        """
    
    @staticmethod
    def get_button_danger_style():
        """Danger button style"""
        return f"""
            QPushButton {{
                background-color: {ModernStyles.DANGER_RED};
                color: white;
                border: none;
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: bold;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernStyles.DANGER_RED_HOVER};
            }}
            QPushButton:disabled {{
                background-color: {ModernStyles.GRAY_300};
                color: {ModernStyles.GRAY_500};
            }}
        """
    
    @staticmethod
    def get_button_secondary_style():
        """Secondary button style"""
        return f"""
            QPushButton {{
                background-color: white;
                color: {ModernStyles.GRAY_700};
                border: 1px solid {ModernStyles.GRAY_300};
                padding: 12px 24px;
                border-radius: 8px;
                font-weight: 500;
                font-size: 12px;
            }}
            QPushButton:hover {{
                background-color: {ModernStyles.GRAY_50};
                border-color: {ModernStyles.GRAY_400};
            }}
            QPushButton:disabled {{
                background-color: {ModernStyles.GRAY_100};
                color: {ModernStyles.GRAY_400};
                border-color: {ModernStyles.GRAY_200};
            }}
        """
    
    @staticmethod
    def get_input_style():
        """Input field style"""
        return f"""
            QLineEdit, QTextEdit, QComboBox, QSpinBox, QDoubleSpinBox, QDateEdit {{
                background-color: white;
                border: 1px solid {ModernStyles.GRAY_300};
                border-radius: 6px;
                padding: 10px 12px;
                font-size: 12px;
                color: {ModernStyles.GRAY_800};
            }}
            QLineEdit:focus, QTextEdit:focus, QComboBox:focus, QSpinBox:focus, QDoubleSpinBox:focus, QDateEdit:focus {{
                border-color: {ModernStyles.PRIMARY_BLUE};
                outline: none;
            }}
            QLineEdit:disabled, QTextEdit:disabled, QComboBox:disabled, QSpinBox:disabled, QDoubleSpinBox:disabled, QDateEdit:disabled {{
                background-color: {ModernStyles.GRAY_100};
                color: {ModernStyles.GRAY_500};
                border-color: {ModernStyles.GRAY_200};
            }}
        """
    
    @staticmethod
    def get_table_style():
        """Table widget style"""
        return f"""
            QTableWidget {{
                background-color: white;
                border: 1px solid {ModernStyles.GRAY_200};
                border-radius: 8px;
                gridline-color: {ModernStyles.GRAY_200};
                font-size: 11px;
            }}
            QTableWidget::item {{
                padding: 8px 12px;
                border: none;
                border-bottom: 1px solid {ModernStyles.GRAY_100};
            }}
            QTableWidget::item:selected {{
                background-color: {ModernStyles.PRIMARY_BLUE};
                color: white;
            }}
            QTableWidget::item:alternate {{
                background-color: {ModernStyles.GRAY_50};
            }}
            QHeaderView::section {{
                background-color: {ModernStyles.GRAY_100};
                color: {ModernStyles.GRAY_700};
                padding: 12px 12px;
                border: none;
                border-bottom: 2px solid {ModernStyles.PRIMARY_BLUE};
                font-weight: bold;
                font-size: 11px;
            }}
        """
    
    @staticmethod
    def get_group_box_style():
        """Group box style"""
        return f"""
            QGroupBox {{
                font-weight: bold;
                font-size: 12px;
                color: {ModernStyles.GRAY_700};
                border: 1px solid {ModernStyles.GRAY_300};
                border-radius: 8px;
                margin-top: 12px;
                padding-top: 15px;
            }}
            QGroupBox::title {{
                subcontrol-origin: margin;
                left: 15px;
                padding: 0 8px 0 8px;
                background-color: white;
            }}
        """
    
    @staticmethod
    def get_tab_widget_style():
        """Tab widget style"""
        return f"""
            QTabWidget::pane {{
                border: 1px solid {ModernStyles.GRAY_200};
                border-radius: 8px;
                background-color: white;
                margin-top: -1px;
            }}
            QTabBar::tab {{
                background: {ModernStyles.GRAY_100};
                border: 1px solid {ModernStyles.GRAY_200};
                padding: 12px 20px;
                margin-right: 2px;
                border-top-left-radius: 8px;
                border-top-right-radius: 8px;
                font-weight: 500;
                color: {ModernStyles.GRAY_600};
            }}
            QTabBar::tab:selected {{
                background: {ModernStyles.PRIMARY_BLUE};
                color: white;
                border-color: {ModernStyles.PRIMARY_BLUE};
            }}
            QTabBar::tab:hover:!selected {{
                background: {ModernStyles.GRAY_200};
                color: {ModernStyles.GRAY_700};
            }}
        """
    
    @staticmethod
    def get_label_title_style():
        """Title label style"""
        return f"""
            QLabel {{
                color: {ModernStyles.GRAY_800};
                font-weight: bold;
                font-size: 16px;
                padding: 10px 0;
            }}
        """
    
    @staticmethod
    def get_label_subtitle_style():
        """Subtitle label style"""
        return f"""
            QLabel {{
                color: {ModernStyles.GRAY_600};
                font-weight: 500;
                font-size: 13px;
                padding: 5px 0;
            }}
        """
    
    @staticmethod
    def get_progress_bar_style():
        """Progress bar style"""
        return f"""
            QProgressBar {{
                border: none;
                border-radius: 6px;
                background-color: {ModernStyles.GRAY_200};
                height: 8px;
                text-align: center;
            }}
            QProgressBar::chunk {{
                border-radius: 6px;
                background: qlineargradient(x1:0, y1:0, x2:1, y2:0,
                    stop:0 {ModernStyles.PRIMARY_BLUE}, stop:1 {ModernStyles.PRIMARY_BLUE_HOVER});
            }}
        """
    
    @staticmethod
    def get_scroll_area_style():
        """Scroll area style"""
        return f"""
            QScrollArea {{
                border: none;
                background-color: transparent;
            }}
            QScrollBar:vertical {{
                background-color: {ModernStyles.GRAY_100};
                width: 12px;
                border-radius: 6px;
                margin: 0;
            }}
            QScrollBar::handle:vertical {{
                background-color: {ModernStyles.GRAY_400};
                border-radius: 6px;
                min-height: 20px;
                margin: 2px;
            }}
            QScrollBar::handle:vertical:hover {{
                background-color: {ModernStyles.GRAY_500};
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                border: none;
                background: none;
            }}
        """
