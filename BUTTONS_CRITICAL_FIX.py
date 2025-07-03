#!/usr/bin/env python3
"""
🔧 إصلاح شامل للأزرار المفقودة
Critical Buttons Fix Script
"""

import re

def add_missing_handlers():
    """إضافة المعالجات المفقودة"""
    
    missing_handlers = """
            # ===== إصلاح شامل للمعالجات المفقودة =====
            
            # معالجات إضافية لأوضاع فلتر اللغة
            elif data.startswith("set_language_filter_mode_"):
                parts = data.replace("set_language_filter_mode_", "").split("_")
                task_id = "_".join(parts[:-1])
                mode = parts[-1]
                await self.set_language_filter_mode(event, task_id, mode)
            
            # معالجات إضافية لفلتر المستخدمين
            elif data.startswith("set_user_filter_mode_"):
                parts = data.replace("set_user_filter_mode_", "").split("_")
                task_id = "_".join(parts[:-1])
                mode = parts[-1]
                await self.set_user_filter_mode(event, task_id, mode)
            
            # معالجات إضافية لحد الأحرف
            elif data.startswith("set_task_char_min_limit_"):
                task_id = data.replace("set_task_char_min_limit_", "")
                await self.set_task_char_min_limit(event, task_id)
            elif data.startswith("set_task_char_max_limit_"):
                task_id = data.replace("set_task_char_max_limit_", "")
                await self.set_task_char_max_limit(event, task_id)
            elif data.startswith("reset_task_char_limits_"):
                task_id = data.replace("reset_task_char_limits_", "")
                await self.reset_task_char_limits(event, task_id)
            
            # معالجات إضافية لفلتر التكرار
            elif data.startswith("set_duplicate_similarity_"):
                task_id = data.replace("set_duplicate_similarity_", "")
                await self.set_duplicate_similarity(event, task_id)
            elif data.startswith("set_duplicate_check_period_"):
                task_id = data.replace("set_duplicate_check_period_", "")
                await self.set_duplicate_check_period(event, task_id)
            elif data.startswith("clear_duplicate_history_"):
                task_id = data.replace("clear_duplicate_history_", "")
                await self.clear_duplicate_history(event, task_id)
            
            # معالجات إضافية للأزرار الشفافة
            elif data.startswith("toggle_task_inline_buttons_"):
                task_id = data.replace("toggle_task_inline_buttons_", "")
                await self.toggle_task_inline_buttons(event, task_id)
            elif data.startswith("toggle_task_reply_buttons_"):
                task_id = data.replace("toggle_task_reply_buttons_", "")
                await self.toggle_task_reply_buttons(event, task_id)
            
            # معالجات إضافية لتنسيق الرسائل
            elif data.startswith("set_task_message_format_"):
                parts = data.replace("set_task_message_format_", "").split("_")
                task_id = "_".join(parts[:-1])
                format_type = parts[-1]
                await self.set_task_message_format(event, task_id, format_type)
            
            # معالجات إضافية للتأخير
            elif data.startswith("set_message_delay_value_"):
                task_id = data.replace("set_message_delay_value_", "")
                await self.set_message_delay_value(event, task_id)
            elif data.startswith("set_forward_delay_value_"):
                task_id = data.replace("set_forward_delay_value_", "")
                await self.set_forward_delay_value(event, task_id)
            elif data.startswith("reset_task_message_delay_"):
                task_id = data.replace("reset_task_message_delay_", "")
                await self.reset_task_message_delay(event, task_id)
            elif data.startswith("reset_task_forward_delay_"):
                task_id = data.replace("reset_task_forward_delay_", "")
                await self.reset_task_forward_delay(event, task_id)
            
            # معالجات إضافية لنوع التوجيه
            elif data.startswith("set_task_forwarding_type_"):
                parts = data.replace("set_task_forwarding_type_", "").split("_")
                task_id = "_".join(parts[:-1])
                forward_type = parts[-1]
                await self.set_task_forwarding_type(event, task_id, forward_type)
            elif data.startswith("prompt_set_admin_chat_"):
                task_id = data.replace("prompt_set_admin_chat_", "")
                await self.prompt_set_admin_chat(event, task_id)
            
            # ===== نهاية إصلاح المعالجات المفقودة ====="""
    
    return missing_handlers

def fix_callback_patterns():
    """إصلاح أنماط المعالجات في callback_handler"""
    
    print("🔧 بدء إصلاح أنماط المعالجات...")
    
    try:
        # قراءة الملف
        with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # الإصلاحات المطلوبة
        fixes = [
            # إصلاح أنماط أزرار فلتر اللغة
            ('elif data.startswith("set_language_mode_"):', 'elif data.startswith("set_language_mode_") or data.startswith("set_language_filter_mode_"):'),
            
            # إصلاح أنماط أزرار فلتر المستخدمين  
            ('elif data.startswith("set_user_filter_mode_"):', 'elif data.startswith("set_user_filter_mode_") or data.startswith("set_user_mode_"):'),
            
            # إصلاح أنماط أزرار حد الأحرف
            ('elif data.startswith("set_min_chars_"):', 'elif data.startswith("set_min_chars_") or data.startswith("set_task_char_min_limit_"):'),
            ('elif data.startswith("set_max_chars_"):', 'elif data.startswith("set_max_chars_") or data.startswith("set_task_char_max_limit_"):'),
            ('elif data.startswith("reset_char_limits_"):', 'elif data.startswith("reset_char_limits_") or data.startswith("reset_task_char_limits_"):'),
            
            # إصلاح أنماط أزرار فلتر التكرار
            ('elif data.startswith("set_similarity_"):', 'elif data.startswith("set_similarity_") or data.startswith("set_duplicate_similarity_"):'),
            ('elif data.startswith("set_check_period_"):', 'elif data.startswith("set_check_period_") or data.startswith("set_duplicate_check_period_"):'),
            ('elif data.startswith("clear_message_history_"):', 'elif data.startswith("clear_message_history_") or data.startswith("clear_duplicate_history_"):'),
            
            # إصلاح أنماط أزرار الأزرار الشفافة
            ('elif data.startswith("toggle_inline_buttons_"):', 'elif data.startswith("toggle_inline_buttons_") or data.startswith("toggle_task_inline_buttons_"):'),
            ('elif data.startswith("toggle_reply_buttons_"):', 'elif data.startswith("toggle_reply_buttons_") or data.startswith("toggle_task_reply_buttons_"):'),
        ]
        
        # تطبيق الإصلاحات
        fixed_count = 0
        for old_pattern, new_pattern in fixes:
            if old_pattern in content:
                content = content.replace(old_pattern, new_pattern)
                fixed_count += 1
                print(f"✅ تم إصلاح: {old_pattern}")
        
        # إضافة المعالجات المفقودة قبل نهاية callback_handler
        missing_handlers = add_missing_handlers()
        
        # البحث عن نقطة الإدراج (قبل نهاية callback_handler)
        insertion_point = content.find("# Advanced settings callbacks")
        if insertion_point != -1:
            content = content[:insertion_point] + missing_handlers + "\n            " + content[insertion_point:]
            print("✅ تم إضافة المعالجات المفقودة")
            fixed_count += 1
        
        # حفظ الملف المُحدث
        with open('modern_control_bot.py', 'w', encoding='utf-8') as f:
            f.write(content)
        
        print(f"\n🎉 تم إنجاز الإصلاح!")
        print(f"📊 إجمالي الإصلاحات: {fixed_count}")
        
        return True
        
    except Exception as e:
        print(f"❌ خطأ في الإصلاح: {e}")
        return False

def verify_fixes():
    """التحقق من صحة الإصلاحات"""
    
    print("\n🔍 التحقق من صحة الإصلاحات...")
    
    try:
        with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
            content = f.read()
        
        # قائمة الأنماط المطلوب التحقق منها
        required_patterns = [
            "toggle_task_language_filter_",
            "toggle_task_link_filter_", 
            "toggle_task_forwarded_filter_",
            "toggle_task_char_limit_",
            "toggle_task_user_filter_",
            "toggle_task_transparent_buttons_",
            "toggle_task_duplicate_filter_",
            "toggle_task_message_formatting_",
            "toggle_task_link_preview_",
            "set_language_filter_mode_",
            "set_user_filter_mode_",
            "set_task_char_min_limit_",
            "set_duplicate_similarity_",
            "toggle_task_inline_buttons_",
        ]
        
        verified_count = 0
        for pattern in required_patterns:
            if pattern in content:
                verified_count += 1
                print(f"✅ تم التحقق: {pattern}")
            else:
                print(f"❌ مفقود: {pattern}")
        
        success_rate = (verified_count / len(required_patterns)) * 100
        print(f"\n📊 نسبة نجاح التحقق: {success_rate:.1f}%")
        
        return success_rate >= 90
        
    except Exception as e:
        print(f"❌ خطأ في التحقق: {e}")
        return False

def main():
    """الدالة الرئيسية"""
    
    print("🔧 إصلاح شامل للأزرار المفقودة")
    print("=" * 50)
    
    # تطبيق الإصلاحات
    if fix_callback_patterns():
        print("✅ تم تطبيق الإصلاحات بنجاح")
        
        # التحقق من صحة الإصلاحات
        if verify_fixes():
            print("🎉 جميع الإصلاحات تم تطبيقها بنجاح!")
            return 0
        else:
            print("⚠️ بعض الإصلاحات قد لا تكون مكتملة")
            return 1
    else:
        print("❌ فشل في تطبيق الإصلاحات")
        return 1

if __name__ == "__main__":
    exit(main())