#!/usr/bin/env python3
"""
سكريبت تخصيص White-Label لمشروع حقيبة الرياضة
الاستخدام: python customize.py <client_config.json>
"""
import json, sys, os, re, shutil
from pathlib import Path

def load_config(config_file):
    with open(config_file, 'r', encoding='utf-8') as f:
        return json.load(f)

def update_brand_ts(config, project_path):
    """تحديث ملف brand.ts بالإعدادات الجديدة"""
    brand_file = Path(project_path) / "client/src/config/brand.ts"
    
    replacements = {
        'name: "حقيبة الرياضة"': f'name: "{config["name"]}"',
        'nameEn: "Sports Bag"': f'nameEn: "{config.get("nameEn", config["name"])}"',
        'tagline: "المتجر الأول في سوريا للأحذية الرياضية والكاجوال"': f'tagline: "{config.get("tagline", "")}"',
        'shortName: "حقيبة الرياضة"': f'shortName: "{config["name"]}"',
        f'industry: "retail_sports"': f'industry: "{config.get("industry", "general")}"',
        'country: "سوريا"': f'country: "{config.get("country", "سوريا")}"',
        'city: "إدلب"': f'city: "{config.get("city", "")}"',
        'foundedYear: "2022"': f'foundedYear: "{config.get("foundedYear", "2024")}"',
    }
    
    content = brand_file.read_text(encoding='utf-8')
    for old, new in replacements.items():
        content = content.replace(old, new)
    
    # تحديث الوحدات (modules)
    if "modules" in config:
        for module, enabled in config["modules"].items():
            content = re.sub(
                rf'({module}: )(true|false)',
                rf'\g<1>{str(enabled).lower()}',
                content
            )
    
    # تحديث تركيز لوحة التحكم
    if "dashboard_focus" in config:
        content = content.replace(
            'primaryFocus: "sales"',
            f'primaryFocus: "{config["dashboard_focus"]}"'
        )
    
    brand_file.write_text(content, encoding='utf-8')
    print(f"✅ تم تحديث brand.ts")

def update_manifest(config, project_path):
    """تحديث manifest.json"""
    manifest_file = Path(project_path) / "client/public/manifest.json"
    manifest = json.loads(manifest_file.read_text(encoding='utf-8'))
    
    manifest["name"] = f'{config["name"]} | {config.get("nameEn", "")}'
    manifest["short_name"] = config["name"]
    manifest["description"] = config.get("tagline", "")
    manifest["theme_color"] = config.get("primary_color", "#22c55e")
    
    manifest_file.write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding='utf-8')
    print(f"✅ تم تحديث manifest.json")

def update_index_html(config, project_path):
    """تحديث index.html"""
    html_file = Path(project_path) / "client/index.html"
    content = html_file.read_text(encoding='utf-8')
    
    # تحديث العنوان
    content = re.sub(r'<title>.*?</title>', f'<title>{config["name"]}</title>', content)
    
    # تحديث theme-color
    if "primary_color" in config:
        content = re.sub(
            r'<meta name="theme-color" content="[^"]*"',
            f'<meta name="theme-color" content="{config["primary_color"]}"',
            content
        )
    
    html_file.write_text(content, encoding='utf-8')
    print(f"✅ تم تحديث index.html")

def generate_report(config, project_path):
    """إنشاء تقرير التخصيص"""
    report = f"""
# تقرير تخصيص White-Label
## العميل: {config['name']}
## التاريخ: {__import__('datetime').datetime.now().strftime('%Y-%m-%d %H:%M')}

### الإعدادات المطبّقة:
- **اسم الشركة**: {config['name']}
- **المدينة**: {config.get('city', '-')}
- **القطاع**: {config.get('industry', 'general')}
- **اللون الرئيسي**: {config.get('primary_color', '#22c55e')}

### الوحدات المفعّلة:
{chr(10).join([f"- {'✅' if v else '❌'} {k}" for k, v in config.get('modules', {}).items()])}

### الملفات المُعدَّلة:
- client/src/config/brand.ts
- client/public/manifest.json
- client/index.html
"""
    report_path = Path(project_path) / f"CUSTOMIZATION_REPORT_{config['name']}.md"
    report_path.write_text(report, encoding='utf-8')
    print(f"✅ تقرير التخصيص: {report_path}")

def main():
    if len(sys.argv) < 3:
        print("الاستخدام: python customize.py <client_config.json> <project_path>")
        sys.exit(1)
    
    config = load_config(sys.argv[1])
    project_path = sys.argv[2]
    
    print(f"\n🚀 بدء تخصيص المشروع لـ: {config['name']}\n")
    
    update_brand_ts(config, project_path)
    update_manifest(config, project_path)
    update_index_html(config, project_path)
    generate_report(config, project_path)
    
    print(f"\n✅ اكتمل التخصيص! المشروع جاهز لـ: {config['name']}")

if __name__ == "__main__":
    main()
