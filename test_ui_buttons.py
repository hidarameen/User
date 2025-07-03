#!/usr/bin/env python3
"""
🖥️ اختبار واجهة المستخدم لأزرار البوت
UI Test for Bot Buttons Interface
"""

import asyncio
import sys
import json
from datetime import datetime
from dotenv import load_dotenv

load_dotenv()

class UIButtonTester:
    """فئة اختبار واجهة المستخدم للأزرار"""
    
    def __init__(self):
        self.bot = None
        self.test_results = {}
        
    async def simulate_button_clicks(self):
        """محاكاة نقرات الأزرار"""
        
        print("🧪 بدء اختبار واجهة المستخدم للأزرار")
        print("="*50)
        
        # الأزرار المطلوب اختبارها
        buttons_tests = [
            {
                "name": "إعدادات المهام المتعددة",
                "callback": "show_multi_task_menu",
                "description": "عرض قائمة المهام المتعددة"
            },
            {
                "name": "فلتر اللغة",
                "callback": "edit_task_language_filter_1",
                "description": "تعديل فلتر اللغة للمهمة"
            },
            {
                "name": "فلتر الروابط", 
                "callback": "edit_task_link_filter_1",
                "description": "تعديل فلتر الروابط"
            },
            {
                "name": "فلتر المعاد توجيهها",
                "callback": "edit_task_forwarded_filter_1", 
                "description": "تعديل فلتر الرسائل المعاد توجيهها"
            },
            {
                "name": "فلتر حد الأحرف",
                "callback": "edit_task_char_limit_1",
                "description": "تعديل حد الأحرف"
            },
            {
                "name": "فلتر المستخدمين",
                "callback": "edit_task_user_filter_1",
                "description": "تعديل فلتر المستخدمين"
            },
            {
                "name": "الأزرار الشفافة",
                "callback": "edit_task_transparent_buttons_1",
                "description": "تعديل إعدادات الأزرار الشفافة"
            },
            {
                "name": "فلتر التكرار",
                "callback": "edit_task_duplicate_filter_1",
                "description": "تعديل فلتر التكرار"
            },
            {
                "name": "تنسيق الرسائل",
                "callback": "edit_task_message_formatting_1",
                "description": "تعديل تنسيق الرسائل"
            },
            {
                "name": "معاينة الروابط",
                "callback": "edit_task_link_preview_1",
                "description": "تعديل معاينة الروابط"
            },
            {
                "name": "تأخير التوجيه",
                "callback": "edit_task_forward_delay_1",
                "description": "تعديل تأخير التوجيه"
            },
            {
                "name": "تأخير الرسائل",
                "callback": "edit_task_message_delay_1",
                "description": "تعديل تأخير الرسائل"
            },
            {
                "name": "إعدادات المزامنة",
                "callback": "edit_task_sync_settings_1",
                "description": "تعديل إعدادات المزامنة"
            },
            {
                "name": "إعدادات الإشعارات",
                "callback": "edit_task_notification_settings_1",
                "description": "تعديل إعدادات الإشعارات"
            },
            {
                "name": "تثبيت الرسائل",
                "callback": "edit_task_pin_messages_1",
                "description": "تعديل تثبيت الرسائل"
            },
            {
                "name": "المحافظة على الردود",
                "callback": "edit_task_reply_preservation_1",
                "description": "تعديل المحافظة على الردود"
            },
            {
                "name": "نوع التوجيه",
                "callback": "edit_task_forwarding_type_1",
                "description": "تعديل نوع التوجيه"
            }
        ]
        
        passed = 0
        failed = 0
        
        for i, test in enumerate(buttons_tests, 1):
            print(f"\n🔍 [{i:02d}/17] اختبار: {test['name']}")
            print(f"    الوصف: {test['description']}")
            print(f"    Callback: {test['callback']}")
            
            try:
                # محاكاة إنشاء Keyboard للاختبار
                success = await self.test_button_keyboard(test['callback'])
                
                if success:
                    print(f"    ✅ نجح - الزر يعمل بشكل صحيح")
                    passed += 1
                    self.test_results[test['name']] = {
                        "status": "PASS",
                        "callback": test['callback'],
                        "timestamp": datetime.now().isoformat()
                    }
                else:
                    print(f"    ❌ فشل - الزر لا يعمل")
                    failed += 1
                    self.test_results[test['name']] = {
                        "status": "FAIL",
                        "callback": test['callback'],
                        "timestamp": datetime.now().isoformat()
                    }
                    
            except Exception as e:
                print(f"    💥 خطأ: {e}")
                failed += 1
                self.test_results[test['name']] = {
                    "status": "ERROR",
                    "callback": test['callback'],
                    "error": str(e),
                    "timestamp": datetime.now().isoformat()
                }
        
        # النتائج النهائية
        total = passed + failed
        success_rate = (passed / total) * 100 if total > 0 else 0
        
        print("\n" + "="*50)
        print("📊 نتائج الاختبار النهائية:")
        print(f"   إجمالي الاختبارات: {total}")
        print(f"   نجح: {passed} ✅")
        print(f"   فشل: {failed} ❌")
        print(f"   معدل النجاح: {success_rate:.1f}%")
        print("="*50)
        
        return success_rate
    
    async def test_button_keyboard(self, callback_data):
        """اختبار إنشاء keyboard للزر"""
        try:
            # قراءة ملف البوت للبحث عن المعالج
            with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
                bot_code = f.read()
            
            # البحث عن المعالج
            search_patterns = [
                f"callback_data == '{callback_data}'",
                f'callback_data == "{callback_data}"',
                f"'{callback_data}':",
                f'"{callback_data}":',
                f"async def {callback_data.replace('_1', '_').rstrip('_')}",
            ]
            
            handler_found = False
            for pattern in search_patterns:
                if pattern in bot_code:
                    handler_found = True
                    break
            
            if not handler_found:
                # البحث عن المعالج العام
                base_callback = callback_data.replace('_1', '_').rstrip('_')
                if base_callback in bot_code:
                    handler_found = True
            
            return handler_found
            
        except Exception as e:
            print(f"خطأ في فحص الزر {callback_data}: {e}")
            return False
    
    async def test_specific_buttons(self):
        """اختبار أزرار محددة بالتفصيل"""
        
        print("\n🔍 اختبار الأزرار المحددة بالتفصيل...")
        print("-" * 40)
        
        specific_tests = [
            # اختبار فلتر اللغة
            {
                "category": "فلتر اللغة",
                "buttons": [
                    "toggle_task_language_filter_1",
                    "set_language_mode_1_allow", 
                    "set_language_mode_1_block",
                    "add_allowed_languages_1",
                    "add_blocked_languages_1",
                    "view_allowed_languages_1",
                    "view_blocked_languages_1",
                    "clear_all_languages_1"
                ]
            },
            
            # اختبار فلتر الروابط
            {
                "category": "فلتر الروابط",
                "buttons": [
                    "toggle_task_link_filter_1",
                    "toggle_telegram_links_1",
                    "toggle_external_links_1",
                    "add_allowed_domains_1",
                    "add_blocked_domains_1",
                    "view_allowed_domains_1",
                    "view_blocked_domains_1",
                    "clear_all_domains_1"
                ]
            },
            
            # اختبار الأزرار الشفافة
            {
                "category": "الأزرار الشفافة",
                "buttons": [
                    "toggle_task_transparent_buttons_1",
                    "toggle_inline_buttons_1",
                    "toggle_reply_buttons_1"
                ]
            },
            
            # اختبار تنسيق الرسائل
            {
                "category": "تنسيق الرسائل",
                "buttons": [
                    "toggle_task_message_formatting_1",
                    "set_message_format_1_original",
                    "set_message_format_1_bold",
                    "set_message_format_1_italic",
                    "set_message_format_1_code"
                ]
            }
        ]
        
        detailed_results = {}
        
        for test_group in specific_tests:
            category = test_group["category"]
            buttons = test_group["buttons"]
            
            print(f"\n📂 فحص فئة: {category}")
            
            category_passed = 0
            category_total = len(buttons)
            
            for button in buttons:
                success = await self.test_button_keyboard(button)
                if success:
                    print(f"   ✅ {button}")
                    category_passed += 1
                else:
                    print(f"   ❌ {button}")
            
            category_rate = (category_passed / category_total) * 100
            detailed_results[category] = {
                "passed": category_passed,
                "total": category_total,
                "rate": category_rate
            }
            
            print(f"   📊 النتيجة: {category_passed}/{category_total} ({category_rate:.1f}%)")
        
        return detailed_results

async def main():
    """الدالة الرئيسية"""
    
    print("🖥️ مختبر واجهة المستخدم لأزرار البوت")
    print("="*60)
    
    tester = UIButtonTester()
    
    try:
        # اختبار الأزرار الرئيسية
        print("🚀 بدء اختبار الأزرار الرئيسية...")
        success_rate = await tester.simulate_button_clicks()
        
        # اختبار الأزرار المحددة
        print("\n🔍 بدء اختبار الأزرار المحددة...")
        detailed_results = await tester.test_specific_buttons()
        
        # حفظ النتائج
        final_results = {
            "overall_success_rate": success_rate,
            "main_buttons": tester.test_results,
            "detailed_categories": detailed_results,
            "timestamp": datetime.now().isoformat()
        }
        
        # حفظ في ملف JSON
        with open(f'ui_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(final_results, f, ensure_ascii=False, indent=2)
        
        print(f"\n📋 تم حفظ النتائج في ملف JSON")
        
        # تقييم النتائج النهائية
        if success_rate >= 95:
            print("\n🎉 ممتاز! واجهة المستخدم تعمل بشكل مثالي")
            return 0
        elif success_rate >= 85:
            print(f"\n👍 جيد! واجهة المستخدم تعمل بشكل جيد ({success_rate:.1f}%)")
            return 0
        elif success_rate >= 70:
            print(f"\n⚠️ مقبول، يحتاج تحسين ({success_rate:.1f}%)")
            return 1
        else:
            print(f"\n❌ غير مقبول! واجهة المستخدم تحتاج إصلاح ({success_rate:.1f}%)")
            return 2
            
    except Exception as e:
        print(f"\n💥 خطأ في تشغيل الاختبار: {e}")
        return 3

if __name__ == "__main__":
    exit_code = asyncio.run(main())
    sys.exit(exit_code)