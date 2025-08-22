"""
واجهات المستخدم - User Interface
"""

from .main_window import MainWindow
from .login_dialog import LoginDialog
from .dashboard import Dashboard
from .pos_window import POSWindow
from .inventory_window import InventoryWindow
from .repair_window import RepairWindow
from .reports_window import ReportsWindow
from .settings_window import SettingsWindow
from .daily_close_window import DailyCloseWindow

__all__ = [
    'MainWindow',
    'LoginDialog',
    'Dashboard',
    'POSWindow',
    'InventoryWindow',
    'RepairWindow',
    'ReportsWindow',
    'SettingsWindow',
    'DailyCloseWindow'
]
