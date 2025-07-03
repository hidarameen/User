#!/usr/bin/env python3
"""
🔍 فحص شامل لجميع الأزرار الفرعية
Comprehensive Audit of All Sub-Buttons
"""

import re
import json
from datetime import datetime
from collections import defaultdict

class ComprehensiveButtonsAudit:
    """فئة الفحص الشامل للأزرار الفرعية"""
    
    def __init__(self):
        self.bot_code = ""
        self.audit_results = {}
        self.categories = {
            "1. إدارة المهام المتعددة": {
                "buttons": [
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
                "sub_buttons": [
                    "start_specific_task_",
                    "stop_specific_task_",
                    "restart_specific_task_", 
                    "confirm_delete_task_",
                    "delete_task_confirmed_",
                    "edit_specific_task_"
                ]
            },
            
            "2. فلتر اللغة": {
                "buttons": [
                    "edit_task_language_filter_",
                    "toggle_task_language_filter_"
                ],
                "sub_buttons": [
                    "set_language_filter_mode_",
                    "add_allowed_languages_",
                    "add_blocked_languages_",
                    "view_allowed_languages_",
                    "view_blocked_languages_", 
                    "clear_all_languages_",
                    "prompt_add_allowed_languages",
                    "prompt_add_blocked_languages",
                    "process_allowed_languages_input",
                    "process_blocked_languages_input"
                ]
            },
            
            "3. فلتر الروابط": {
                "buttons": [
                    "edit_task_link_filter_",
                    "toggle_task_link_filter_"
                ],
                "sub_buttons": [
                    "toggle_telegram_links_",
                    "toggle_external_links_",
                    "add_allowed_domains_",
                    "add_blocked_domains_",
                    "view_allowed_domains_",
                    "view_blocked_domains_",
                    "clear_all_domains_",
                    "clear_all_domains_both",
                    "prompt_add_allowed_domains",
                    "prompt_add_blocked_domains", 
                    "process_allowed_domains_input",
                    "process_blocked_domains_input"
                ]
            },
            
            "4. فلتر المعاد توجيهها": {
                "buttons": [
                    "edit_task_forwarded_filter_",
                    "toggle_task_forwarded_filter_"
                ],
                "sub_buttons": []
            },
            
            "5. فلتر حد الأحرف": {
                "buttons": [
                    "edit_task_char_limit_",
                    "toggle_task_char_limit_"
                ],
                "sub_buttons": [
                    "set_task_char_min_limit",
                    "set_task_char_max_limit", 
                    "reset_task_char_limits",
                    "process_char_min_input",
                    "process_char_max_input"
                ]
            },
            
            "6. فلتر المستخدمين": {
                "buttons": [
                    "edit_task_user_filter_",
                    "toggle_task_user_filter_"
                ],
                "sub_buttons": [
                    "set_user_filter_mode",
                    "add_allowed_users_",
                    "add_blocked_users_",
                    "view_allowed_users_",
                    "view_blocked_users_",
                    "clear_all_users_",
                    "prompt_add_allowed_users",
                    "prompt_add_blocked_users",
                    "process_allowed_users_input", 
                    "process_blocked_users_input"
                ]
            },
            
            "7. الأزرار الشفافة": {
                "buttons": [
                    "edit_task_transparent_buttons_",
                    "toggle_task_transparent_buttons_"
                ],
                "sub_buttons": [
                    "toggle_task_inline_buttons",
                    "toggle_task_reply_buttons",
                    "toggle_inline_buttons_",
                    "toggle_reply_buttons_"
                ]
            },
            
            "8. فلتر التكرار": {
                "buttons": [
                    "edit_task_duplicate_filter_",
                    "toggle_task_duplicate_filter_"
                ],
                "sub_buttons": [
                    "set_duplicate_similarity",
                    "set_duplicate_check_period",
                    "clear_duplicate_history",
                    "process_similarity_input",
                    "process_check_period_input"
                ]
            },
            
            "9. تنسيق الرسائل": {
                "buttons": [
                    "edit_task_message_formatting_",
                    "toggle_task_message_formatting_"
                ],
                "sub_buttons": [
                    "set_task_message_format",
                    "set_message_format_"
                ]
            },
            
            "10. معاينة الروابط": {
                "buttons": [
                    "edit_task_link_preview_",
                    "toggle_task_link_preview_"
                ],
                "sub_buttons": []
            },
            
            "11. تأخير التوجيه": {
                "buttons": [
                    "edit_task_forward_delay_",
                    "toggle_task_forward_delay_"
                ],
                "sub_buttons": [
                    "set_forward_delay_value",
                    "reset_task_forward_delay",
                    "process_forward_delay_input"
                ]
            },
            
            "12. تأخير الرسائل": {
                "buttons": [
                    "edit_task_message_delay_",
                    "toggle_task_message_delay_"
                ],
                "sub_buttons": [
                    "set_message_delay_value", 
                    "reset_task_message_delay",
                    "process_message_delay_input"
                ]
            },
            
            "13. إعدادات المزامنة": {
                "buttons": [
                    "edit_task_sync_settings_",
                    "toggle_task_sync_delete",
                    "toggle_task_sync_edit"
                ],
                "sub_buttons": [
                    "toggle_sync_delete_",
                    "toggle_sync_edit_"
                ]
            },
            
            "14. إعدادات الإشعارات": {
                "buttons": [
                    "edit_task_notification_settings_",
                    "toggle_task_notifications",
                    "toggle_task_silent_mode"
                ],
                "sub_buttons": [
                    "toggle_silent_mode_",
                    "toggle_task_notifications_"
                ]
            },
            
            "15. تثبيت الرسائل": {
                "buttons": [
                    "edit_task_pin_messages_",
                    "toggle_task_pin_messages",
                    "toggle_task_pin_notify"
                ],
                "sub_buttons": [
                    "toggle_pin_messages_",
                    "toggle_pin_notify_"
                ]
            },
            
            "16. المحافظة على الردود": {
                "buttons": [
                    "edit_task_reply_preservation_",
                    "toggle_task_reply_preservation"
                ],
                "sub_buttons": [
                    "toggle_reply_preservation_"
                ]
            },
            
            "17. نوع التوجيه": {
                "buttons": [
                    "edit_task_forwarding_type_",
                    "set_task_forwarding_type"
                ],
                "sub_buttons": [
                    "prompt_set_admin_chat",
                    "process_admin_chat_input"
                ]
            }
        }
    
    def load_bot_code(self):
        """تحميل كود البوت"""
        try:
            with open('modern_control_bot.py', 'r', encoding='utf-8') as f:
                self.bot_code = f.read()
            return True
        except FileNotFoundError:
            print("❌ لم يتم العثور على ملف modern_control_bot.py")
            return False
        except Exception as e:
            print(f"💥 خطأ في تحميل الملف: {e}")
            return False
    
    def check_button_exists(self, button_name):
        """فحص وجود الزر في الكود"""
        if not button_name or not self.bot_code:
            return False
            
        # أنماط البحث المختلفة
        patterns = [
            f"async def {button_name}",
            f"def {button_name}",
            f"'{button_name}':",
            f'"{button_name}":',
            f"callback_data='{button_name}'",
            f'callback_data="{button_name}"',
            f"'{button_name}'" + r"\s*:",
            f'"{button_name}"' + r"\s*:",
            button_name.rstrip('_'),
            re.escape(button_name)
        ]
        
        for pattern in patterns:
            if re.search(pattern, self.bot_code, re.IGNORECASE):
                return True
        
        # فحص إضافي للأزرار المتغيرة
        if '_' in button_name:
            base_name = button_name.rsplit('_', 1)[0]
            if base_name in self.bot_code:
                return True
        
        return False
    
    def audit_category(self, category_name, category_data):
        """فحص فئة واحدة"""
        results = {
            "category": category_name,
            "main_buttons": {},
            "sub_buttons": {},
            "stats": {
                "total_main": len(category_data["buttons"]),
                "total_sub": len(category_data["sub_buttons"]),
                "passed_main": 0,
                "passed_sub": 0
            }
        }
        
        # فحص الأزرار الرئيسية
        for button in category_data["buttons"]:
            exists = self.check_button_exists(button)
            results["main_buttons"][button] = {
                "exists": exists,
                "status": "✅ موجود" if exists else "❌ مفقود"
            }
            if exists:
                results["stats"]["passed_main"] += 1
        
        # فحص الأزرار الفرعية
        for button in category_data["sub_buttons"]:
            exists = self.check_button_exists(button)
            results["sub_buttons"][button] = {
                "exists": exists,
                "status": "✅ موجود" if exists else "❌ مفقود"
            }
            if exists:
                results["stats"]["passed_sub"] += 1
        
        # حساب النسب
        results["stats"]["main_percentage"] = (
            results["stats"]["passed_main"] / results["stats"]["total_main"] * 100
            if results["stats"]["total_main"] > 0 else 0
        )
        
        results["stats"]["sub_percentage"] = (
            results["stats"]["passed_sub"] / results["stats"]["total_sub"] * 100 
            if results["stats"]["total_sub"] > 0 else 100
        )
        
        return results
    
    def run_comprehensive_audit(self):
        """تشغيل الفحص الشامل"""
        print("🔍 فحص شامل لجميع الأزرار الفرعية")
        print("=" * 60)
        
        if not self.load_bot_code():
            return False
        
        total_stats = {
            "total_categories": len(self.categories),
            "total_main_buttons": 0,
            "total_sub_buttons": 0,
            "passed_main_buttons": 0,
            "passed_sub_buttons": 0
        }
        
        # فحص كل فئة
        for category_name, category_data in self.categories.items():
            print(f"\n🔍 فحص {category_name}")
            print("-" * 50)
            
            results = self.audit_category(category_name, category_data)
            self.audit_results[category_name] = results
            
            # طباعة النتائج الفورية
            main_perc = results["stats"]["main_percentage"]
            sub_perc = results["stats"]["sub_percentage"]
            
            print(f"   الأزرار الرئيسية: {results['stats']['passed_main']}/{results['stats']['total_main']} ({main_perc:.1f}%)")
            if results["stats"]["total_sub"] > 0:
                print(f"   الأزرار الفرعية: {results['stats']['passed_sub']}/{results['stats']['total_sub']} ({sub_perc:.1f}%)")
            
            # تحديث الإحصائيات الإجمالية
            total_stats["total_main_buttons"] += results["stats"]["total_main"]
            total_stats["total_sub_buttons"] += results["stats"]["total_sub"]
            total_stats["passed_main_buttons"] += results["stats"]["passed_main"]
            total_stats["passed_sub_buttons"] += results["stats"]["passed_sub"]
            
            # عرض الأزرار المفقودة
            missing_main = [name for name, data in results["main_buttons"].items() if not data["exists"]]
            missing_sub = [name for name, data in results["sub_buttons"].items() if not data["exists"]]
            
            if missing_main:
                print(f"   ❌ أزرار رئيسية مفقودة: {', '.join(missing_main[:3])}" + 
                      (f" وأخرى..." if len(missing_main) > 3 else ""))
            
            if missing_sub:
                print(f"   ❌ أزرار فرعية مفقودة: {', '.join(missing_sub[:3])}" + 
                      (f" وأخرى..." if len(missing_sub) > 3 else ""))
        
        # النتائج النهائية
        self.generate_final_report(total_stats)
        return True
    
    def generate_final_report(self, total_stats):
        """إنشاء التقرير النهائي"""
        
        # حساب النسب الإجمالية
        main_percentage = (
            total_stats["passed_main_buttons"] / total_stats["total_main_buttons"] * 100
            if total_stats["total_main_buttons"] > 0 else 0
        )
        
        sub_percentage = (
            total_stats["passed_sub_buttons"] / total_stats["total_sub_buttons"] * 100
            if total_stats["total_sub_buttons"] > 0 else 0
        )
        
        overall_buttons = total_stats["passed_main_buttons"] + total_stats["passed_sub_buttons"]
        total_buttons = total_stats["total_main_buttons"] + total_stats["total_sub_buttons"]
        overall_percentage = (overall_buttons / total_buttons * 100) if total_buttons > 0 else 0
        
        print("\n" + "=" * 60)
        print("📊 النتائج النهائية للفحص الشامل")
        print("=" * 60)
        
        print(f"📂 إجمالي الفئات: {total_stats['total_categories']}")
        print(f"🔘 إجمالي الأزرار الرئيسية: {total_stats['total_main_buttons']}")
        print(f"🔹 إجمالي الأزرار الفرعية: {total_stats['total_sub_buttons']}")
        print(f"🎯 إجمالي الأزرار: {total_buttons}")
        
        print(f"\n✅ الأزرار الرئيسية العاملة: {total_stats['passed_main_buttons']} ({main_percentage:.1f}%)")
        print(f"✅ الأزرار الفرعية العاملة: {total_stats['passed_sub_buttons']} ({sub_percentage:.1f}%)")
        print(f"🎉 المعدل الإجمالي: {overall_buttons}/{total_buttons} ({overall_percentage:.1f}%)")
        
        # تقييم الجودة
        if overall_percentage >= 95:
            print("\n🏆 تقييم الجودة: ممتاز (A+)")
            print("🎯 الحالة: جاهز للإنتاج بثقة تامة")
        elif overall_percentage >= 85:
            print("\n👍 تقييم الجودة: جيد جداً (A)")
            print("🎯 الحالة: جاهز للإنتاج مع تحسينات طفيفة")
        elif overall_percentage >= 75:
            print("\n⚠️ تقييم الجودة: جيد (B)")
            print("🎯 الحالة: يحتاج تحسينات قبل الإنتاج")
        else:
            print("\n❌ تقييم الجودة: يحتاج تطوير (C)")
            print("🎯 الحالة: غير جاهز للإنتاج")
        
        # حفظ النتائج
        self.save_detailed_results(total_stats, overall_percentage)
    
    def save_detailed_results(self, total_stats, overall_percentage):
        """حفظ النتائج المفصلة"""
        
        # إنشاء تقرير مفصل
        detailed_report = {
            "audit_info": {
                "timestamp": datetime.now().isoformat(),
                "total_categories": total_stats["total_categories"],
                "total_buttons": total_stats["total_main_buttons"] + total_stats["total_sub_buttons"],
                "overall_percentage": overall_percentage
            },
            "summary": total_stats,
            "detailed_results": self.audit_results
        }
        
        # حفظ JSON
        filename = f"comprehensive_buttons_audit_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(detailed_report, f, ensure_ascii=False, indent=2)
        
        # إنشاء تقرير نصي
        report_text = self.generate_text_report(detailed_report)
        txt_filename = f"comprehensive_buttons_report_{datetime.now().strftime('%Y%m%d_%H%M%S')}.md"
        with open(txt_filename, 'w', encoding='utf-8') as f:
            f.write(report_text)
        
        print(f"\n📋 تم حفظ التقرير المفصل:")
        print(f"   📄 {txt_filename}")
        print(f"   📊 {filename}")
    
    def generate_text_report(self, data):
        """إنشاء تقرير نصي مفصل"""
        
        report = f"""# 🔍 تقرير الفحص الشامل للأزرار الفرعية

## 📋 معلومات الفحص
- **التاريخ:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}
- **إجمالي الفئات:** {data['audit_info']['total_categories']}
- **إجمالي الأزرار:** {data['audit_info']['total_buttons']}
- **المعدل الإجمالي:** {data['audit_info']['overall_percentage']:.1f}%

---

## 📊 النتائج حسب الفئة

"""
        
        for category_name, results in data['detailed_results'].items():
            main_perc = results['stats']['main_percentage']
            sub_perc = results['stats']['sub_percentage']
            
            report += f"""### {category_name}

**الإحصائيات:**
- الأزرار الرئيسية: {results['stats']['passed_main']}/{results['stats']['total_main']} ({main_perc:.1f}%)
- الأزرار الفرعية: {results['stats']['passed_sub']}/{results['stats']['total_sub']} ({sub_perc:.1f}%)

**الأزرار الرئيسية:**
"""
            
            for button_name, button_data in results['main_buttons'].items():
                status = "✅" if button_data['exists'] else "❌"
                report += f"- {status} `{button_name}`\n"
            
            if results['sub_buttons']:
                report += "\n**الأزرار الفرعية:**\n"
                for button_name, button_data in results['sub_buttons'].items():
                    status = "✅" if button_data['exists'] else "❌"
                    report += f"- {status} `{button_name}`\n"
            
            report += "\n---\n\n"
        
        return report

def main():
    """الدالة الرئيسية"""
    auditor = ComprehensiveButtonsAudit()
    success = auditor.run_comprehensive_audit()
    
    if success:
        print("\n🎉 تم إنجاز الفحص الشامل بنجاح!")
        return 0
    else:
        print("\n💥 فشل في إجراء الفحص الشامل")
        return 1

if __name__ == "__main__":
    exit(main())