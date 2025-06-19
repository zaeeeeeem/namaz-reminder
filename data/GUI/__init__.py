"""Package containing all GUI view components."""
from .dashboard import DashboardView
from .settings import SettingsView
from .calendar import CalendarView
from .chatbot import ChatbotView
from .notification import show_notification_popup

__all__ = [
    'DashboardView',
    'SettingsView',
    'CalendarView',
    'ChatbotView',
    'show_notification_popup'
]