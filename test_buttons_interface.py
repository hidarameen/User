#!/usr/bin/env python3
"""
🧪 اختبار شامل لأزرار لوحة التحكم الشفافة
Comprehensive Test for Transparent Control Panel Buttons
"""

import asyncio
import logging
import os
import sys
from datetime import datetime
from dotenv import load_dotenv

# تحميل المتغيرات البيئية
load_dotenv()

# إعداد السجلات
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('button_test.log'),
        logging.StreamHandler(sys.stdout)
    ]
)
logger = logging.getLogger(__name__)

class ButtonTestInterface:
    """فئة لاختبار واجهة أزرار لوحة التحكم"""
    
    def __init__(self):
        self.test_results = {}
        self.failed_tests = []
        self.passed_tests = []
        self.total_buttons = 0
        self.tested_buttons = 0
        
        # قائمة جميع الأزرار المطلوب فحصها
        self.buttons_to_test = {
            "main_menu": [
                "show_settings_menu",
                "show_advanced_settings", 
                "show_bot_status",
                "show_stats_dashboard",
                "show_quick_settings",
                "show_quick_setup",
                "save_and_exit"
            ],
            
            "task_management": [
                "show_multi_task_menu",
                "view_tasks",
                "show_task_stats",
                "prompt_add_task",
                "prompt_start_task",
                "prompt_stop_task",
                "prompt_restart_task",
                "prompt_delete_task",
                "prompt_edit_task"
            ],
            
            "language_filter": [
                "toggle_task_language_filter_",
                "set_language_mode_*_allow",
                "set_language_mode_*_block", 
                "add_allowed_languages_",
                "add_blocked_languages_",
                "view_allowed_languages_",
                "view_blocked_languages_",
                "clear_all_languages_"
            ],
            
            "link_filter": [
                "toggle_task_link_filter_",
                "toggle_telegram_links_",
                "toggle_external_links_",
                "add_allowed_domains_",
                "add_blocked_domains_",
                "view_allowed_domains_",
                "view_blocked_domains_",
                "clear_all_domains_"
            ],
            
            "forwarded_filter": [
                "toggle_task_forwarded_filter_"
            ],
            
            "char_limit": [
                "toggle_task_char_limit_",
                "set_min_chars_",
                "set_max_chars_",
                "reset_char_limits_"
            ],
            
            "user_filter": [
                "toggle_task_user_filter_",
                "set_user_filter_mode_*_allow",
                "set_user_filter_mode_*_block",
                "add_allowed_users_",
                "add_blocked_users_",
                "view_allowed_users_",
                "view_blocked_users_",
                "clear_all_users_"
            ],
            
            "transparent_buttons": [
                "toggle_task_transparent_buttons_",
                "toggle_inline_buttons_",
                "toggle_reply_buttons_"
            ],
            
            "duplicate_filter": [
                "toggle_task_duplicate_filter_",
                "set_check_period_",
                "set_similarity_",
                "clear_message_history_"
            ],
            
            "message_formatting": [
                "toggle_task_message_formatting_",
                "set_message_format_*_original",
                "set_message_format_*_regular",
                "set_message_format_*_bold",
                "set_message_format_*_italic",
                "set_message_format_*_underline",
                "set_message_format_*_strikethrough",
                "set_message_format_*_spoiler",
                "set_message_format_*_code",
                "set_message_format_*_pre",
                "set_message_format_*_blockquote",
                "set_message_format_*_expandable_blockquote"
            ],
            
            "link_preview": [
                "toggle_task_link_preview_"
            ],
            
            "forward_delay": [
                "toggle_task_forward_delay_",
                "set_forward_delay_",
                "reset_forward_delay_"
            ],
            
            "message_delay": [
                "toggle_task_message_delay_",
                "set_message_delay_",
                "reset_message_delay_"
            ],
            
            "sync_settings": [
                "toggle_sync_delete_",
                "toggle_sync_edit_"
            ],
            
            "notification_settings": [
                "toggle_silent_mode_",
                "toggle_task_notifications_"
            ],
            
            "pin_messages": [
                "toggle_pin_messages_",
                "toggle_pin_notify_"
            ],
            
            "reply_preservation": [
                "toggle_reply_preservation_"
            ],
            
            "forwarding_type": [
                "set_forwarding_type_*_forward",
                "set_forwarding_type_*_copy",
                "set_forwarding_type_*_manual",
                "set_forwarding_type_*_auto",
                "set_admin_chat_"
            ]
        }
    
    async def initialize_bot(self):
        """تهيئة البوت للاختبار"""
        try:
            from modern_control_bot import ModernControlBot
            self.bot = ModernControlBot()
            await self.bot.start()
            logger.info("✅ تم تهيئة البوت بنجاح")
            return True
        except Exception as e:
            logger.error(f"❌ فشل في تهيئة البوت: {e}")
            return False
    
    async def test_button_handler(self, button_name, category):
        """اختبار معالج زر واحد"""
        try:
            # البحث عن المعالج في الكود
            handler_found = await self.check_handler_exists(button_name)
            
            if handler_found:
                self.test_results[f"{category}.{button_name}"] = {
                    "status": "PASS",
                    "message": "المعالج موجود ومربوط بشكل صحيح",
                    "timestamp": datetime.now().isoformat()
                }
                self.passed_tests.append(f"{category}.{button_name}")
                logger.info(f"✅ {button_name}: PASS")
            else:
                self.test_results[f"{category}.{button_name}"] = {
                    "status": "FAIL", 
                    "message": "المعالج غير موجود أو غير مربوط",
                    "timestamp": datetime.now().isoformat()
                }
                self.failed_tests.append(f"{category}.{button_name}")
                logger.error(f"❌ {button_name}: FAIL")
                
        except Exception as e:
            self.test_results[f"{category}.{button_name}"] = {
                "status": "ERROR",
                "message": f"خطأ في الاختبار: {str(e)}",
                "timestamp": datetime.now().isoformat()
            }
            self.failed_tests.append(f"{category}.{button_name}")
            logger.error(f"💥 {button_name}: ERROR - {e}")
    
    async def check_handler_exists(self, button_name):
        """فحص وجود معالج الزر في الكود"""
        try:
            # قراءة ملف البوت
            with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
                bot_code = f.read()
            
            # البحث عن اسم المعالج
            handler_patterns = [
                f"async def {button_name}",
                f"'{button_name}':",
                f'"{button_name}":',
                f"callback_data='{button_name}'",
                f'callback_data="{button_name}"'
            ]
            
            for pattern in handler_patterns:
                if pattern in bot_code:
                    return True
            
            # فحص الأنماط البديلة للأزرار المتغيرة
            if "*" in button_name:
                base_pattern = button_name.replace("*", "")
                return base_pattern in bot_code
                
            return False
            
        except Exception as e:
            logger.error(f"خطأ في فحص المعالج {button_name}: {e}")
            return False
    
    async def run_comprehensive_test(self):
        """تشغيل اختبار شامل لجميع الأزرار"""
        logger.info("🚀 بدء الاختبار الشامل لأزرار لوحة التحكم")
        logger.info("=" * 60)
        
        start_time = datetime.now()
        
        # حساب العدد الإجمالي للأزرار
        for category, buttons in self.buttons_to_test.items():
            self.total_buttons += len(buttons)
        
        logger.info(f"📊 إجمالي الأزرار المطلوب فحصها: {self.total_buttons}")
        logger.info("=" * 60)
        
        # اختبار كل فئة
        for category, buttons in self.buttons_to_test.items():
            logger.info(f"\n🔍 فحص فئة: {category}")
            logger.info("-" * 40)
            
            for button in buttons:
                await self.test_button_handler(button, category)
                self.tested_buttons += 1
                
                # تقرير التقدم
                progress = (self.tested_buttons / self.total_buttons) * 100
                logger.info(f"التقدم: {progress:.1f}% ({self.tested_buttons}/{self.total_buttons})")
        
        end_time = datetime.now()
        duration = end_time - start_time
        
        # إنشاء التقرير النهائي
        await self.generate_final_report(start_time, end_time, duration)
    
    async def generate_final_report(self, start_time, end_time, duration):
        """إنشاء تقرير نهائي مفصل"""
        
        passed_count = len(self.passed_tests)
        failed_count = len(self.failed_tests)
        success_rate = (passed_count / self.total_buttons) * 100 if self.total_buttons > 0 else 0
        
        report = f"""
{'='*80}
🧪 تقرير الاختبار الشامل لأزرار لوحة التحكم الشفافة
{'='*80}

⏰ معلومات الاختبار:
   بداية الاختبار: {start_time.strftime('%Y-%m-%d %H:%M:%S')}
   نهاية الاختبار: {end_time.strftime('%Y-%m-%d %H:%M:%S')}
   المدة الإجمالية: {duration.total_seconds():.2f} ثانية

📊 النتائج الإجمالية:
   إجمالي الأزرار: {self.total_buttons}
   اختبارات ناجحة: {passed_count} ✅
   اختبارات فاشلة: {failed_count} ❌
   معدل النجاح: {success_rate:.2f}%

{'='*80}
"""

        # إضافة تفاصيل الأزرار الفاشلة
        if self.failed_tests:
            report += "\n❌ الأزرار الفاشلة:\n"
            report += "-" * 40 + "\n"
            for failed_test in self.failed_tests:
                test_data = self.test_results.get(failed_test, {})
                report += f"   🔸 {failed_test}\n"
                report += f"      السبب: {test_data.get('message', 'غير محدد')}\n\n"
        
        # إضافة ملخص حسب الفئة
        report += "\n📋 ملخص حسب الفئة:\n"
        report += "-" * 40 + "\n"
        
        for category, buttons in self.buttons_to_test.items():
            category_passed = 0
            category_total = len(buttons)
            
            for button in buttons:
                test_key = f"{category}.{button}"
                if test_key in self.passed_tests:
                    category_passed += 1
            
            category_rate = (category_passed / category_total) * 100 if category_total > 0 else 0
            status_icon = "✅" if category_rate == 100 else "⚠️" if category_rate >= 80 else "❌"
            
            report += f"   {status_icon} {category}: {category_passed}/{category_total} ({category_rate:.1f}%)\n"
        
        # إضافة توصيات
        report += "\n💡 التوصيات:\n"
        report += "-" * 40 + "\n"
        
        if success_rate == 100:
            report += "   🎉 ممتاز! جميع الأزرار تعمل بشكل صحيح\n"
            report += "   ✅ لوحة التحكم جاهزة للإنتاج\n"
        elif success_rate >= 90:
            report += "   👍 جيد جداً! معظم الأزرار تعمل بشكل صحيح\n"
            report += "   🔧 يُنصح بإصلاح الأزرار الفاشلة قبل الإنتاج\n"
        elif success_rate >= 80:
            report += "   ⚠️ مقبول، لكن يحتاج تحسين\n"
            report += "   🛠️ إصلاح الأزرار الفاشلة مطلوب\n"
        else:
            report += "   ❌ غير مقبول! عدد كبير من الأزرار لا تعمل\n"
            report += "   🚨 مراجعة شاملة مطلوبة قبل الإنتاج\n"
        
        report += "\n" + "="*80 + "\n"
        
        # طباعة التقرير
        print(report)
        
        # حفظ التقرير في ملف
        with open(f'button_test_report_{datetime.now().strftime("%Y%m%d_%H%M%S")}.txt', 'w', encoding='utf-8') as f:
            f.write(report)
        
        # حفظ النتائج التفصيلية في JSON
        import json
        detailed_results = {
            "test_info": {
                "start_time": start_time.isoformat(),
                "end_time": end_time.isoformat(),
                "duration_seconds": duration.total_seconds(),
                "total_buttons": self.total_buttons,
                "passed_count": passed_count,
                "failed_count": failed_count,
                "success_rate": success_rate
            },
            "results": self.test_results,
            "passed_tests": self.passed_tests,
            "failed_tests": self.failed_tests
        }
        
        with open(f'button_test_results_{datetime.now().strftime("%Y%m%d_%H%M%S")}.json', 'w', encoding='utf-8') as f:
            json.dump(detailed_results, f, ensure_ascii=False, indent=2)
        
        logger.info(f"📋 تم حفظ التقرير المفصل")
        return success_rate

async def main():
    """الدالة الرئيسية"""
    print("🧪 مختبر أزرار لوحة التحكم الشفافة")
    print("="*60)
    
    # إنشاء مثيل الاختبار
    tester = ButtonTestInterface()
    
    try:
        # تشغيل الاختبار الشامل
        success_rate = await tester.run_comprehensive_test()
        
        # تقييم النتائج
        if success_rate == 100:
            print("\n🎉 نجح الاختبار بنسبة 100%! جميع الأزرار تعمل بشكل مثالي")
            sys.exit(0)
        elif success_rate >= 90:
            print(f"\n👍 نجح الاختبار بنسبة {success_rate:.1f}% - ممتاز!")
            sys.exit(0)
        elif success_rate >= 80:
            print(f"\n⚠️ نجح الاختبار بنسبة {success_rate:.1f}% - يحتاج تحسين")
            sys.exit(1)
        else:
            print(f"\n❌ فشل الاختبار! نسبة النجاح: {success_rate:.1f}%")
            sys.exit(2)
            
    except KeyboardInterrupt:
        print("\n⏹️ تم إيقاف الاختبار بواسطة المستخدم")
        sys.exit(1)
    except Exception as e:
        print(f"\n💥 خطأ في تشغيل الاختبار: {e}")
        sys.exit(3)

if __name__ == "__main__":
    asyncio.run(main())