#!/usr/bin/env python3
"""
Source Target Manager - وظيفة إدارة المصدر والهدف
"""

from telethon import Button
from .base_module import BaseModule, TaskModule

class SourceTargetManager(BaseModule):
    """
    وظيفة إدارة المصدر والهدف للمهام
    تحتوي على جميع الأدوات اللازمة لتعيين وتغيير مصدر وهدف الرسائل
    """
    
    def __init__(self, client=None, logger=None):
        super().__init__(client, logger)
        self.module_name = "source_target_manager"
    
    async def show_menu(self, event):
        """عرض قائمة إدارة المصدر والهدف"""
        config = await self.get_current_config()
        
        try:
            source_chat = config.get('forwarding', 'source_chat', fallback='غير محدد')
            target_chat = config.get('forwarding', 'target_chat', fallback='غير محدد')
        except:
            source_chat = 'غير محدد'
            target_chat = 'غير محدد'
        
        message = (
            "📥📤 **إدارة المصدر والهدف**\n\n"
            f"📥 **المصدر الحالي:** `{source_chat}`\n"
            f"📤 **الهدف الحالي:** `{target_chat}`\n\n"
            "💡 **الوظائف المتاحة:**\n"
            "• تغيير مصدر الرسائل\n"
            "• تغيير هدف الرسائل\n"
            "• التحقق من صحة المعرفات\n"
            "• عرض تفاصيل القنوات\n\n"
            "🔧 **اختر العملية المطلوبة:**"
        )
        
        await self.show_info(event, message, self.get_menu_keyboard())
    
    def get_menu_keyboard(self) -> list:
        """الحصول على لوحة مفاتيح إدارة المصدر والهدف"""
        return [
            [Button.inline("📥 تغيير المصدر", b"set_source"),
             Button.inline("📤 تغيير الهدف", b"set_target")],
            [Button.inline("🔍 معلومات المصدر", b"source_info"),
             Button.inline("🔍 معلومات الهدف", b"target_info")],
            [Button.inline("✅ التحقق من الاتصال", b"verify_connection"),
             Button.inline("🔄 تبديل المصدر/الهدف", b"swap_source_target")],
            [Button.inline("📋 نسخ الإعدادات", b"copy_settings"),
             Button.inline("💾 حفظ النموذج", b"save_template")],
            self.get_back_button("settings")
        ]
    
    async def handle_callback(self, event, data: str) -> bool:
        """معالجة أحداث الضغط على الأزرار"""
        if data == "set_source":
            await self.prompt_source_chat(event)
            return True
        elif data == "set_target":
            await self.prompt_target_chat(event)
            return True
        elif data == "source_info":
            await self.show_source_info(event)
            return True
        elif data == "target_info":
            await self.show_target_info(event)
            return True
        elif data == "verify_connection":
            await self.verify_connection(event)
            return True
        elif data == "swap_source_target":
            await self.swap_source_target(event)
            return True
        elif data == "copy_settings":
            await self.copy_settings(event)
            return True
        elif data == "save_template":
            await self.save_template(event)
            return True
        return False
    
    async def handle_message(self, event) -> bool:
        """معالجة الرسائل النصية"""
        user_id = event.sender_id
        user_state = self.get_user_state(user_id)
        
        if not user_state:
            return False
        
        state = user_state.get('state')
        
        if state == "waiting_source":
            await self.process_source_input(event)
            return True
        elif state == "waiting_target":
            await self.process_target_input(event)
            return True
        
        return False
    
    async def prompt_source_chat(self, event):
        """طلب إدخال مصدر الرسائل"""
        message = (
            "📥 **تعيين مصدر الرسائل**\n\n"
            "🔹 **الطرق المقبولة:**\n"
            "• معرف القناة: `@channel_username`\n"
            "• رقم القناة: `-1001234567890`\n"
            "• اسم القناة: `اسم القناة`\n"
            "• رابط القناة: `https://t.me/channel_name`\n\n"
            "📝 **أرسل معرف المصدر الجديد:**"
        )
        
        self.set_user_state(event.sender_id, "waiting_source")
        await self.show_info(event, message, [
            [Button.inline("❌ إلغاء", b"source_target_manager")]
        ])
    
    async def prompt_target_chat(self, event):
        """طلب إدخال هدف الرسائل"""
        message = (
            "📤 **تعيين هدف الرسائل**\n\n"
            "🔹 **الطرق المقبولة:**\n"
            "• معرف القناة: `@channel_username`\n"
            "• رقم القناة: `-1001234567890`\n"
            "• اسم القناة: `اسم القناة`\n"
            "• رابط القناة: `https://t.me/channel_name`\n\n"
            "📝 **أرسل معرف الهدف الجديد:**"
        )
        
        self.set_user_state(event.sender_id, "waiting_target")
        await self.show_info(event, message, [
            [Button.inline("❌ إلغاء", b"source_target_manager")]
        ])
    
    async def process_source_input(self, event):
        """معالجة إدخال المصدر"""
        source_input = event.text.strip()
        
        # تنظيف المدخل
        source_chat = await self.clean_chat_input(source_input)
        
        # التحقق من صحة المدخل
        if await self.validate_chat_id(source_chat):
            success = await self.update_config('forwarding', 'source_chat', source_chat)
            if success:
                await self.show_success(event, f"تم تعيين المصدر بنجاح: `{source_chat}`")
                self.clear_user_state(event.sender_id)
                await self.show_menu(event)
            else:
                await self.show_error(event, "فشل في حفظ الإعدادات")
        else:
            await self.show_error(event, "معرف المصدر غير صحيح، يرجى المحاولة مرة أخرى")
    
    async def process_target_input(self, event):
        """معالجة إدخال الهدف"""
        target_input = event.text.strip()
        
        # تنظيف المدخل
        target_chat = await self.clean_chat_input(target_input)
        
        # التحقق من صحة المدخل
        if await self.validate_chat_id(target_chat):
            success = await self.update_config('forwarding', 'target_chat', target_chat)
            if success:
                await self.show_success(event, f"تم تعيين الهدف بنجاح: `{target_chat}`")
                self.clear_user_state(event.sender_id)
                await self.show_menu(event)
            else:
                await self.show_error(event, "فشل في حفظ الإعدادات")
        else:
            await self.show_error(event, "معرف الهدف غير صحيح، يرجى المحاولة مرة أخرى")
    
    async def clean_chat_input(self, chat_input: str) -> str:
        """تنظيف مدخل معرف القناة"""
        # إزالة الرابط وأخذ اسم المستخدم فقط
        if 't.me/' in chat_input:
            chat_input = chat_input.split('t.me/')[-1]
        
        # إزالة / إذا كانت موجودة في البداية
        if chat_input.startswith('/'):
            chat_input = chat_input[1:]
        
        # إضافة @ إذا لم تكن موجودة ولم يكن رقمًا
        if not chat_input.startswith('@') and not chat_input.startswith('-') and chat_input.isdigit() == False:
            chat_input = '@' + chat_input
        
        return chat_input.strip()
    
    async def validate_chat_id(self, chat_id: str) -> bool:
        """التحقق من صحة معرف القناة"""
        try:
            if not chat_id:
                return False
            
            # التحقق من أنماط معرفات القنوات المختلفة
            if chat_id.startswith('@') and len(chat_id) > 1:
                return True
            elif chat_id.startswith('-') and chat_id[1:].isdigit():
                return True
            elif chat_id.isdigit():
                return True
            else:
                return False
        except Exception:
            return False
    
    async def show_source_info(self, event):
        """عرض معلومات المصدر"""
        source_chat = await self.get_config_value('forwarding', 'source_chat', 'غير محدد')
        
        try:
            if self.client and source_chat != 'غير محدد':
                entity = await self.client.get_entity(source_chat)
                
                info_text = (
                    f"📥 **معلومات المصدر**\n\n"
                    f"🏷️ **الاسم:** {getattr(entity, 'title', getattr(entity, 'first_name', 'غير معروف'))}\n"
                    f"🆔 **المعرف:** `{entity.id}`\n"
                    f"👤 **اسم المستخدم:** @{getattr(entity, 'username', 'غير متاح')}\n"
                    f"📊 **النوع:** {'قناة' if getattr(entity, 'broadcast', False) else 'مجموعة'}\n"
                    f"👥 **عدد الأعضاء:** {getattr(entity, 'participants_count', 'غير متاح')}\n"
                )
            else:
                info_text = (
                    f"📥 **معلومات المصدر**\n\n"
                    f"🏷️ **المعرف المحفوظ:** `{source_chat}`\n"
                    "❗ **لا يمكن الحصول على معلومات إضافية**"
                )
        except Exception as e:
            info_text = (
                f"📥 **معلومات المصدر**\n\n"
                f"🏷️ **المعرف المحفوظ:** `{source_chat}`\n"
                f"❌ **خطأ:** {str(e)}"
            )
        
        await self.show_info(event, info_text, [
            [Button.inline("🔄 تحديث المعلومات", b"source_info")],
            self.get_back_button("source_target_manager")
        ])
    
    async def show_target_info(self, event):
        """عرض معلومات الهدف"""
        target_chat = await self.get_config_value('forwarding', 'target_chat', 'غير محدد')
        
        try:
            if self.client and target_chat != 'غير محدد':
                entity = await self.client.get_entity(target_chat)
                
                info_text = (
                    f"📤 **معلومات الهدف**\n\n"
                    f"🏷️ **الاسم:** {getattr(entity, 'title', getattr(entity, 'first_name', 'غير معروف'))}\n"
                    f"🆔 **المعرف:** `{entity.id}`\n"
                    f"👤 **اسم المستخدم:** @{getattr(entity, 'username', 'غير متاح')}\n"
                    f"📊 **النوع:** {'قناة' if getattr(entity, 'broadcast', False) else 'مجموعة'}\n"
                    f"👥 **عدد الأعضاء:** {getattr(entity, 'participants_count', 'غير متاح')}\n"
                )
            else:
                info_text = (
                    f"📤 **معلومات الهدف**\n\n"
                    f"🏷️ **المعرف المحفوظ:** `{target_chat}`\n"
                    "❗ **لا يمكن الحصول على معلومات إضافية**"
                )
        except Exception as e:
            info_text = (
                f"📤 **معلومات الهدف**\n\n"
                f"🏷️ **المعرف المحفوظ:** `{target_chat}`\n"
                f"❌ **خطأ:** {str(e)}"
            )
        
        await self.show_info(event, info_text, [
            [Button.inline("🔄 تحديث المعلومات", b"target_info")],
            self.get_back_button("source_target_manager")
        ])
    
    async def verify_connection(self, event):
        """التحقق من الاتصال بالمصدر والهدف"""
        source_chat = await self.get_config_value('forwarding', 'source_chat', '')
        target_chat = await self.get_config_value('forwarding', 'target_chat', '')
        
        source_status = "❌"
        target_status = "❌"
        
        try:
            if self.client and source_chat:
                await self.client.get_entity(source_chat)
                source_status = "✅"
        except Exception:
            pass
        
        try:
            if self.client and target_chat:
                await self.client.get_entity(target_chat)
                target_status = "✅"
        except Exception:
            pass
        
        message = (
            f"🔍 **حالة الاتصال**\n\n"
            f"📥 **المصدر:** {source_status} `{source_chat or 'غير محدد'}`\n"
            f"📤 **الهدف:** {target_status} `{target_chat or 'غير محدد'}`\n\n"
            f"{'✅ جميع الاتصالات سليمة' if source_status == '✅' and target_status == '✅' else '❌ يوجد مشاكل في الاتصال'}"
        )
        
        await self.show_info(event, message, [
            [Button.inline("🔄 إعادة فحص", b"verify_connection")],
            self.get_back_button("source_target_manager")
        ])
    
    async def swap_source_target(self, event):
        """تبديل المصدر والهدف"""
        source_chat = await self.get_config_value('forwarding', 'source_chat', '')
        target_chat = await self.get_config_value('forwarding', 'target_chat', '')
        
        if not source_chat or not target_chat:
            await self.show_error(event, "لا يمكن التبديل - المصدر أو الهدف غير محدد")
            return
        
        # تبديل القيم
        await self.update_config('forwarding', 'source_chat', target_chat)
        await self.update_config('forwarding', 'target_chat', source_chat)
        
        await self.show_success(event, "تم تبديل المصدر والهدف بنجاح")
        await self.show_menu(event)
    
    async def copy_settings(self, event):
        """نسخ الإعدادات للحافظة"""
        source_chat = await self.get_config_value('forwarding', 'source_chat', 'غير محدد')
        target_chat = await self.get_config_value('forwarding', 'target_chat', 'غير محدد')
        
        settings_text = (
            f"المصدر: {source_chat}\n"
            f"الهدف: {target_chat}"
        )
        
        message = (
            f"📋 **نسخ الإعدادات**\n\n"
            f"```\n{settings_text}\n```\n\n"
            "تم نسخ الإعدادات أعلاه"
        )
        
        await self.show_info(event, message)
    
    async def save_template(self, event):
        """حفظ نموذج الإعدادات"""
        source_chat = await self.get_config_value('forwarding', 'source_chat', '')
        target_chat = await self.get_config_value('forwarding', 'target_chat', '')
        
        if not source_chat or not target_chat:
            await self.show_error(event, "لا يمكن حفظ النموذج - المصدر أو الهدف غير محدد")
            return
        
        # حفظ النموذج في قسم منفصل
        template_name = f"template_{int(time.time())}"
        await self.update_config(template_name, 'source_chat', source_chat)
        await self.update_config(template_name, 'target_chat', target_chat)
        
        await self.show_success(event, f"تم حفظ النموذج: {template_name}")

class SourceTargetTaskManager(TaskModule):
    """
    إدارة المصدر والهدف للمهام المتعددة
    """
    
    def __init__(self, client=None, logger=None):
        super().__init__(client, logger)
        self.module_name = "source_target_task_manager"
    
    async def show_task_menu(self, event, task_id: str):
        """عرض قائمة إدارة المصدر والهدف لمهمة معينة"""
        source_chat = await self.get_task_config_value(task_id, 'source_chat', 'غير محدد')
        target_chat = await self.get_task_config_value(task_id, 'target_chat', 'غير محدد')
        
        message = (
            f"📥📤 **إدارة المصدر والهدف - المهمة: {task_id}**\n\n"
            f"📥 **المصدر:** `{source_chat}`\n"
            f"📤 **الهدف:** `{target_chat}`\n\n"
            "🔧 **اختر العملية:**"
        )
        
        keyboard = [
            [Button.inline("📥 تغيير المصدر", f"set_task_source_{task_id}".encode()),
             Button.inline("📤 تغيير الهدف", f"set_task_target_{task_id}".encode())],
            [Button.inline("🔍 معلومات المصدر", f"task_source_info_{task_id}".encode()),
             Button.inline("🔍 معلومات الهدف", f"task_target_info_{task_id}".encode())],
            [Button.inline("✅ التحقق من الاتصال", f"verify_task_connection_{task_id}".encode())],
            self.get_task_back_button(task_id)
        ]
        
        await self.show_info(event, message, keyboard)
    
    async def handle_task_callback(self, event, data: str, task_id: str) -> bool:
        """معالجة أحداث المهام"""
        if data.startswith("set_task_source_"):
            await self.prompt_task_source(event, task_id)
            return True
        elif data.startswith("set_task_target_"):
            await self.prompt_task_target(event, task_id)
            return True
        elif data.startswith("task_source_info_"):
            await self.show_task_source_info(event, task_id)
            return True
        elif data.startswith("task_target_info_"):
            await self.show_task_target_info(event, task_id)
            return True
        elif data.startswith("verify_task_connection_"):
            await self.verify_task_connection(event, task_id)
            return True
        return False
    
    async def prompt_task_source(self, event, task_id: str):
        """طلب إدخال مصدر المهمة"""
        message = (
            f"📥 **تعيين مصدر المهمة: {task_id}**\n\n"
            "📝 **أرسل معرف المصدر الجديد:**"
        )
        
        self.set_user_state(event.sender_id, f"waiting_task_source_{task_id}")
        await self.show_info(event, message, [
            [Button.inline("❌ إلغاء", f"edit_specific_{task_id}".encode())]
        ])
    
    async def prompt_task_target(self, event, task_id: str):
        """طلب إدخال هدف المهمة"""
        message = (
            f"📤 **تعيين هدف المهمة: {task_id}**\n\n"
            "📝 **أرسل معرف الهدف الجديد:**"
        )
        
        self.set_user_state(event.sender_id, f"waiting_task_target_{task_id}")
        await self.show_info(event, message, [
            [Button.inline("❌ إلغاء", f"edit_specific_{task_id}".encode())]
        ])
    
    async def process_task_source_input(self, event, task_id: str):
        """معالجة إدخال مصدر المهمة"""
        source_input = event.text.strip()
        source_chat = await self.clean_chat_input(source_input)
        
        if await self.validate_chat_id(source_chat):
            success = await self.update_task_config(task_id, 'source_chat', source_chat)
            if success:
                await self.show_success(event, f"تم تعيين مصدر المهمة {task_id}: `{source_chat}`")
                self.clear_user_state(event.sender_id)
            else:
                await self.show_error(event, "فشل في حفظ الإعدادات")
        else:
            await self.show_error(event, "معرف المصدر غير صحيح")
    
    async def process_task_target_input(self, event, task_id: str):
        """معالجة إدخال هدف المهمة"""
        target_input = event.text.strip()
        target_chat = await self.clean_chat_input(target_input)
        
        if await self.validate_chat_id(target_chat):
            success = await self.update_task_config(task_id, 'target_chat', target_chat)
            if success:
                await self.show_success(event, f"تم تعيين هدف المهمة {task_id}: `{target_chat}`")
                self.clear_user_state(event.sender_id)
            else:
                await self.show_error(event, "فشل في حفظ الإعدادات")
        else:
            await self.show_error(event, "معرف الهدف غير صحيح")
    
    # نفس الوظائف المساعدة من الفئة الأساسية
    async def clean_chat_input(self, chat_input: str) -> str:
        """تنظيف مدخل معرف القناة"""
        if 't.me/' in chat_input:
            chat_input = chat_input.split('t.me/')[-1]
        
        if chat_input.startswith('/'):
            chat_input = chat_input[1:]
        
        if not chat_input.startswith('@') and not chat_input.startswith('-') and chat_input.isdigit() == False:
            chat_input = '@' + chat_input
        
        return chat_input.strip()
    
    async def validate_chat_id(self, chat_id: str) -> bool:
        """التحقق من صحة معرف القناة"""
        try:
            if not chat_id:
                return False
            
            if chat_id.startswith('@') and len(chat_id) > 1:
                return True
            elif chat_id.startswith('-') and chat_id[1:].isdigit():
                return True
            elif chat_id.isdigit():
                return True
            else:
                return False
        except Exception:
            return False