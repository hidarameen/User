#!/usr/bin/env python3
"""
نظام تسجيل محسن للبوت مع ألوان ورصد شامل للأحداث
Enhanced logging system with colors and comprehensive event monitoring
"""

import logging
import datetime
import os
import sys
import threading
from typing import Optional, Dict, Any
import json

class ColoredFormatter(logging.Formatter):
    """مُنسق السجلات مع الألوان"""
    
    # رموز الألوان ANSI
    COLORS = {
        'DEBUG': '\033[36m',      # سماوي
        'INFO': '\033[32m',       # أخضر  
        'WARNING': '\033[33m',    # أصفر
        'ERROR': '\033[31m',      # أحمر
        'CRITICAL': '\033[35m',   # بنفسجي
        'EVENT': '\033[94m',      # أزرق فاتح
        'USER': '\033[92m',       # أخضر فاتح
        'BUTTON': '\033[96m',     # سماوي فاتح
        'TASK': '\033[93m',       # أصفر فاتح
        'RESET': '\033[0m'        # إعادة تعيين
    }
    
    # رموز الأحداث
    ICONS = {
        'DEBUG': '🔍',
        'INFO': 'ℹ️',
        'WARNING': '⚠️',
        'ERROR': '❌',
        'CRITICAL': '🔥',
        'EVENT': '⚡',
        'USER': '👤',
        'BUTTON': '🔘',
        'TASK': '📋',
        'SUCCESS': '✅'
    }
    
    def format(self, record):
        # إضافة اللون حسب نوع السجل
        level_name = record.levelname
        color = self.COLORS.get(level_name, self.COLORS['RESET'])
        icon = self.ICONS.get(level_name, '📝')
        
        # تنسيق الوقت
        timestamp = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # تنسيق اسم المصدر
        name = record.name.split('.')[-1] if '.' in record.name else record.name
        
        # تنسيق الرسالة
        message = record.getMessage()
        
        # إضافة معلومات إضافية إذا كانت متوفرة
        extra_info = ""
        if hasattr(record, 'user_id'):
            extra_info += f" [User:{record.user_id}]"
        if hasattr(record, 'event_type'):
            extra_info += f" [{record.event_type}]"
        if hasattr(record, 'task_id'):
            extra_info += f" [Task:{record.task_id}]"
        
        # تجميع السجل النهائي
        formatted = f"{color}{icon} {timestamp} [{level_name:8}] {name:15} | {message}{extra_info}{self.COLORS['RESET']}"
        
        return formatted

class EventLogger:
    """فئة تسجيل الأحداث المحسنة"""
    
    def __init__(self, name: str = "BotLogger"):
        self.logger = logging.getLogger(name)
        self.setup_logger()
        
        # إحصائيات السجلات
        self.stats = {
            'total_events': 0,
            'errors': 0,
            'warnings': 0,
            'user_actions': 0,
            'button_clicks': 0,
            'task_operations': 0
        }
        
        # قفل للعمليات المتزامنة
        self.lock = threading.Lock()
    
    def setup_logger(self):
        """إعداد نظام التسجيل"""
        # إزالة المعالجات السابقة
        for handler in self.logger.handlers[:]:
            self.logger.removeHandler(handler)
        
        # تعيين مستوى التسجيل
        self.logger.setLevel(logging.DEBUG)
        
        # معالج وحدة التحكم (الترمينال)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.DEBUG)
        console_handler.setFormatter(ColoredFormatter())
        
        # معالج الملف
        file_handler = logging.FileHandler(
            'bot_comprehensive.log', 
            mode='a', 
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_formatter = logging.Formatter(
            '%(asctime)s [%(levelname)s] %(name)s | %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        file_handler.setFormatter(file_formatter)
        
        # إضافة المعالجات
        self.logger.addHandler(console_handler)
        self.logger.addHandler(file_handler)
        
        # منع تكرار السجلات
        self.logger.propagate = False
    
    def _update_stats(self, event_type: str):
        """تحديث إحصائيات السجلات"""
        with self.lock:
            self.stats['total_events'] += 1
            if event_type in self.stats:
                self.stats[event_type] += 1
    
    def info(self, message: str, **kwargs):
        """تسجيل معلومة عامة"""
        self._update_stats('info')
        self.logger.info(message, extra=kwargs)
    
    def debug(self, message: str, **kwargs):
        """تسجيل معلومة تطوير"""
        self._update_stats('debug')
        self.logger.debug(message, extra=kwargs)
    
    def warning(self, message: str, **kwargs):
        """تسجيل تحذير"""
        self._update_stats('warnings')
        self.logger.warning(message, extra=kwargs)
    
    def error(self, message: str, **kwargs):
        """تسجيل خطأ"""
        self._update_stats('errors')
        self.logger.error(message, extra=kwargs)
    
    def critical(self, message: str, **kwargs):
        """تسجيل خطأ حرج"""
        self._update_stats('errors')
        self.logger.critical(message, extra=kwargs)
    
    def event(self, message: str, **kwargs):
        """تسجيل حدث مهم"""
        # إنشاء سجل مخصص للأحداث
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO, 
            "", 0, message, (), None
        )
        record.levelname = 'EVENT'
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
        self._update_stats('events')
    
    def user_action(self, action: str, user_id: str, details: str = "", **kwargs):
        """تسجيل إجراء المستخدم"""
        message = f"User Action: {action}"
        if details:
            message += f" - {details}"
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO,
            "", 0, message, (), None
        )
        record.levelname = 'USER'
        record.user_id = user_id
        record.event_type = 'user_action'
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
        self._update_stats('user_actions')
    
    def button_click(self, button_data: str, user_id: str, details: str = "", **kwargs):
        """تسجيل ضغط زر"""
        message = f"Button Clicked: {button_data}"
        if details:
            message += f" - {details}"
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO,
            "", 0, message, (), None
        )
        record.levelname = 'BUTTON'
        record.user_id = user_id
        record.event_type = 'button_click'
        record.button_data = button_data
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
        self._update_stats('button_clicks')
    
    def task_operation(self, operation: str, task_id: str, details: str = "", **kwargs):
        """تسجيل عملية مهمة"""
        message = f"Task {operation}: {task_id}"
        if details:
            message += f" - {details}"
        
        record = self.logger.makeRecord(
            self.logger.name, logging.INFO,
            "", 0, message, (), None
        )
        record.levelname = 'TASK'
        record.task_id = task_id
        record.event_type = 'task_operation'
        record.operation = operation
        
        for key, value in kwargs.items():
            setattr(record, key, value)
        
        self.logger.handle(record)
        self._update_stats('task_operations')
    
    def bot_response(self, response_type: str, user_id: str, message: str, **kwargs):
        """تسجيل استجابة البوت"""
        full_message = f"Bot Response [{response_type}]: {message}"
        
        self.event(full_message, 
                  user_id=user_id, 
                  event_type='bot_response',
                  response_type=response_type,
                  **kwargs)
    
    def config_change(self, setting: str, old_value: Any, new_value: Any, user_id: str, **kwargs):
        """تسجيل تغيير إعداد"""
        message = f"Config Changed: {setting} | {old_value} → {new_value}"
        
        self.event(message,
                  user_id=user_id,
                  event_type='config_change',
                  setting=setting,
                  old_value=str(old_value),
                  new_value=str(new_value),
                  **kwargs)
    
    def get_stats(self) -> Dict[str, int]:
        """الحصول على إحصائيات السجلات"""
        with self.lock:
            return self.stats.copy()
    
    def reset_stats(self):
        """إعادة تعيين الإحصائيات"""
        with self.lock:
            for key in self.stats:
                self.stats[key] = 0
    
    def export_logs(self, filename: str = None) -> str:
        """تصدير السجلات"""
        if not filename:
            timestamp = datetime.datetime.now().strftime('%Y%m%d_%H%M%S')
            filename = f"bot_logs_export_{timestamp}.json"
        
        export_data = {
            'export_time': datetime.datetime.now().isoformat(),
            'stats': self.get_stats(),
            'log_file': 'bot_comprehensive.log'
        }
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(export_data, f, indent=2, ensure_ascii=False)
        
        self.info(f"Logs exported to: {filename}")
        return filename

# إنشاء مثيل السجل العام
enhanced_logger = EventLogger("ModernBot")

# وظائف مساعدة للاستخدام السريع
def log_info(message: str, **kwargs):
    enhanced_logger.info(message, **kwargs)

def log_debug(message: str, **kwargs):
    enhanced_logger.debug(message, **kwargs)

def log_warning(message: str, **kwargs):
    enhanced_logger.warning(message, **kwargs)

def log_error(message: str, **kwargs):
    enhanced_logger.error(message, **kwargs)

def log_event(message: str, **kwargs):
    enhanced_logger.event(message, **kwargs)

def log_user_action(action: str, user_id: str, details: str = "", **kwargs):
    enhanced_logger.user_action(action, user_id, details, **kwargs)

def log_button_click(button_data: str, user_id: str, details: str = "", **kwargs):
    enhanced_logger.button_click(button_data, user_id, details, **kwargs)

def log_task_operation(operation: str, task_id: str, details: str = "", **kwargs):
    enhanced_logger.task_operation(operation, task_id, details, **kwargs)

def log_bot_response(response_type: str, user_id: str, message: str, **kwargs):
    enhanced_logger.bot_response(response_type, user_id, message, **kwargs)

def log_config_change(setting: str, old_value: Any, new_value: Any, user_id: str, **kwargs):
    enhanced_logger.config_change(setting, old_value, new_value, user_id, **kwargs)

# تسجيل بداية تشغيل النظام
if __name__ != "__main__":
    enhanced_logger.event("📊 Enhanced logging system initialized", 
                         event_type='system_start')