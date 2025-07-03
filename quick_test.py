#!/usr/bin/env python3
"""
⚡ اختبار سريع للوحة التحكم
Quick Control Panel Test
"""

import asyncio
import sys
from datetime import datetime

def test_button_exists(button_name, code_content):
    """فحص سريع لوجود الزر في الكود"""
    patterns = [
        f"async def {button_name}",
        f"'{button_name}':",
        f'"{button_name}":',
        f"callback_data='{button_name}'",
        f'callback_data="{button_name}"',
        button_name.replace('_1', '_').rstrip('_')
    ]
    
    for pattern in patterns:
        if pattern in code_content:
            return True
    return False

def main():
    """الدالة الرئيسية للاختبار السريع"""
    print("⚡ اختبار سريع للوحة التحكم الشفافة")
    print("=" * 50)
    
    try:
        # قراءة ملف البوت
        with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
            bot_code = f.read()
        
        # الأزرار الحرجة للاختبار
        critical_buttons = [
            "show_multi_task_menu",
            "edit_task_language_filter_",
            "edit_task_link_filter_", 
            "edit_task_transparent_buttons_",
            "edit_task_forwarding_type_",
            "toggle_task_language_filter",
            "toggle_task_link_filter",
            "toggle_task_transparent_buttons",
            "set_task_forwarding_type"
        ]
        
        passed = 0
        total = len(critical_buttons)
        
        print(f"🧪 فحص {total} أزرار حرجة...")
        print("-" * 30)
        
        for button in critical_buttons:
            exists = test_button_exists(button, bot_code)
            status = "✅" if exists else "❌"
            print(f"{status} {button}")
            if exists:
                passed += 1
        
        success_rate = (passed / total) * 100
        
        print("-" * 30)
        print(f"📊 النتائج:")
        print(f"   نجح: {passed}/{total}")
        print(f"   معدل النجاح: {success_rate:.1f}%")
        
        if success_rate == 100:
            print("\n🎉 ممتاز! جميع الأزرار الحرجة موجودة")
            return 0
        elif success_rate >= 80:
            print(f"\n👍 جيد! معظم الأزرار موجودة ({success_rate:.1f}%)")
            return 0
        else:
            print(f"\n⚠️ تحذير! بعض الأزرار مفقودة ({success_rate:.1f}%)")
            return 1
            
    except FileNotFoundError:
        print("❌ لم يتم العثور على ملف modern_control_bot.py")
        return 2
    except Exception as e:
        print(f"💥 خطأ: {e}")
        return 3

if __name__ == "__main__":
    exit_code = main()
    print(f"\nتم إنجاز الاختبار في {datetime.now().strftime('%H:%M:%S')}")
    sys.exit(exit_code)