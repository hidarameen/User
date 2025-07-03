#!/usr/bin/env python3
"""
Base Module - الفئة الأساسية لجميع وظائف البوت
"""

import configparser
import logging
from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from telethon import Button

class BaseModule(ABC):
    """
    الفئة الأساسية لجميع وظائف البوت
    تحتوي على الوظائف المشتركة والواجهات المطلوبة
    """
    
    def __init__(self, client=None, logger=None):
        self.client = client
        self.logger = logger or logging.getLogger(self.__class__.__name__)
        self.config_file = 'config.ini'
        self.user_states = {}
        
    async def get_current_config(self) -> configparser.ConfigParser:
        """الحصول على الإعدادات الحالية"""
        config = configparser.ConfigParser()
        try:
            config.read(self.config_file, encoding='utf-8')
        except Exception as e:
            self.logger.error(f"خطأ في قراءة الإعدادات: {e}")
            # إنشاء إعدادات افتراضية
            config.add_section('forwarding')
        return config
    
    async def update_config(self, section: str, key: str, value: str) -> bool:
        """تحديث إعداد معين"""
        try:
            config = await self.get_current_config()
            if not config.has_section(section):
                config.add_section(section)
            config.set(section, key, str(value))
            
            with open(self.config_file, 'w', encoding='utf-8') as configfile:
                config.write(configfile)
            
            self.logger.info(f"تم تحديث الإعداد: {section}.{key} = {value}")
            return True
        except Exception as e:
            self.logger.error(f"خطأ في تحديث الإعداد: {e}")
            return False
    
    async def get_config_value(self, section: str, key: str, fallback: Any = None) -> Any:
        """الحصول على قيمة إعداد معين"""
        try:
            config = await self.get_current_config()
            return config.get(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    async def get_config_boolean(self, section: str, key: str, fallback: bool = False) -> bool:
        """الحصول على قيمة منطقية من الإعدادات"""
        try:
            config = await self.get_current_config()
            return config.getboolean(section, key, fallback=fallback)
        except Exception:
            return fallback
    
    async def get_config_list(self, section: str, key: str, fallback: list = None) -> list:
        """الحصول على قائمة من الإعدادات"""
        if fallback is None:
            fallback = []
        try:
            value = await self.get_config_value(section, key, '')
            if value:
                return [item.strip() for item in value.split(',') if item.strip()]
            return fallback
        except Exception:
            return fallback
    
    async def set_config_list(self, section: str, key: str, value_list: list) -> bool:
        """حفظ قائمة في الإعدادات"""
        try:
            value = ','.join(str(item) for item in value_list)
            return await self.update_config(section, key, value)
        except Exception as e:
            self.logger.error(f"خطأ في حفظ القائمة: {e}")
            return False
    
    def get_status_emoji(self, enabled: bool) -> str:
        """الحصول على رمز الحالة"""
        return "✅" if enabled else "❌"
    
    def get_back_button(self, callback_data: str = "main_menu") -> list:
        """الحصول على زر العودة"""
        return [Button.inline("🔙 العودة", callback_data.encode())]
    
    def set_user_state(self, user_id: int, state: str, data: Dict = None):
        """تعيين حالة المستخدم"""
        if data is None:
            data = {}
        self.user_states[user_id] = {'state': state, 'data': data}
    
    def get_user_state(self, user_id: int) -> Optional[Dict]:
        """الحصول على حالة المستخدم"""
        return self.user_states.get(user_id)
    
    def clear_user_state(self, user_id: int):
        """مسح حالة المستخدم"""
        if user_id in self.user_states:
            del self.user_states[user_id]
    
    async def is_admin(self, user_id: int) -> bool:
        """التحقق من صلاحيات المدير"""
        try:
            admin_id = await self.get_config_value('bot', 'admin_user_id', '')
            return str(user_id) == str(admin_id)
        except Exception:
            return False
    
    @abstractmethod
    async def show_menu(self, event) -> None:
        """عرض قائمة الوظيفة - يجب تنفيذها في كل وظيفة"""
        pass
    
    @abstractmethod
    def get_menu_keyboard(self) -> list:
        """الحصول على لوحة مفاتيح القائمة - يجب تنفيذها في كل وظيفة"""
        pass
    
    @abstractmethod
    async def handle_callback(self, event, data: str) -> bool:
        """معالجة أحداث الضغط على الأزرار - يجب تنفيذها في كل وظيفة"""
        pass
    
    @abstractmethod
    async def handle_message(self, event) -> bool:
        """معالجة الرسائل النصية - يجب تنفيذها في كل وظيفة"""
        pass
    
    async def show_error(self, event, message: str):
        """عرض رسالة خطأ"""
        try:
            await event.edit(f"❌ خطأ: {message}", buttons=self.get_back_button())
        except Exception:
            await event.respond(f"❌ خطأ: {message}", buttons=self.get_back_button())
    
    async def show_success(self, event, message: str):
        """عرض رسالة نجاح"""
        try:
            await event.edit(f"✅ {message}", buttons=self.get_back_button())
        except Exception:
            await event.respond(f"✅ {message}", buttons=self.get_back_button())
    
    async def show_info(self, event, message: str, buttons: list = None):
        """عرض رسالة معلومات"""
        if buttons is None:
            buttons = self.get_back_button()
        try:
            await event.edit(message, buttons=buttons)
        except Exception:
            await event.respond(message, buttons=buttons)

class TaskModule(BaseModule):
    """
    فئة أساسية للوظائف المتعلقة بالمهام المتعددة
    """
    
    def __init__(self, client=None, logger=None):
        super().__init__(client, logger)
        self.task_prefix = 'task_'
    
    async def get_task_config_value(self, task_id: str, key: str, fallback: Any = None) -> Any:
        """الحصول على قيمة إعداد خاص بمهمة معينة"""
        return await self.get_config_value(f'{self.task_prefix}{task_id}', key, fallback)
    
    async def update_task_config(self, task_id: str, key: str, value: str) -> bool:
        """تحديث إعداد خاص بمهمة معينة"""
        return await self.update_config(f'{self.task_prefix}{task_id}', key, value)
    
    async def get_task_config_boolean(self, task_id: str, key: str, fallback: bool = False) -> bool:
        """الحصول على قيمة منطقية خاصة بمهمة معينة"""
        return await self.get_config_boolean(f'{self.task_prefix}{task_id}', key, fallback)
    
    async def get_task_config_list(self, task_id: str, key: str, fallback: list = None) -> list:
        """الحصول على قائمة خاصة بمهمة معينة"""
        return await self.get_config_list(f'{self.task_prefix}{task_id}', key, fallback)
    
    async def set_task_config_list(self, task_id: str, key: str, value_list: list) -> bool:
        """حفظ قائمة خاصة بمهمة معينة"""
        return await self.set_config_list(f'{self.task_prefix}{task_id}', key, value_list)
    
    def get_task_back_button(self, task_id: str) -> list:
        """الحصول على زر العودة لقائمة المهمة"""
        return [Button.inline("🔙 العودة", f"edit_specific_{task_id}".encode())]
    
    async def get_all_tasks(self) -> list:
        """الحصول على جميع المهام"""
        try:
            config = await self.get_current_config()
            tasks = []
            for section in config.sections():
                if section.startswith(self.task_prefix):
                    task_id = section.replace(self.task_prefix, '')
                    tasks.append(task_id)
            return tasks
        except Exception as e:
            self.logger.error(f"خطأ في الحصول على المهام: {e}")
            return []