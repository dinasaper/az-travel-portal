#!/usr/bin/env python3
"""Add 40 employees to AZ Travel Portal in bulk."""
import sys
import os
sys.path.insert(0, os.path.dirname(__file__))
from auth import create_user, load_users, list_users

# === قائمة الموظفين (اسم المستخدم، كلمة المرور، الاسم الكامل، الدور) ===
# الدور: admin = مدير (تعديل)، viewer = مشاهد فقط
# غيّر البيانات دي حسب موظفينك الحقيقيين

EMPLOYEES = [
    # Admins (المديرين)
    ("admin", "admin123", "System Admin", "admin"),
    ("ahmed.ali", "Az@2026Ah", "أحمد علي", "admin"),
    ("mohamed.hassan", "Az@2026Mo", "محمد حسن", "admin"),
    ("omar.farouk", "Az@2026Om", "عمر فاروق", "admin"),
    
    # Viewers (الموظفين العاديين)
    ("ali.mahmoud", "Az@2026Al", "علي محمود", "viewer"),
    ("hassan.ibrahim", "Az@2026Ha", "حسن ابراهيم", "viewer"),
    ("youssef.ahmed", "Az@2026Yo", "يوسف احمد", "viewer"),
    ("khaled.mostafa", "Az@2026Kh", "خالد مصطفى", "viewer"),
    ("amr.abdallah", "Az@2026Am", "عمرو عبدالله", "viewer"),
    ("tamer.ali", "Az@2026Ta", "تامر علي", "viewer"),
    ("mahmoud.farouk", "Az@2026Ma", "محمود فاروق", "viewer"),
    ("mostafa.hassan", "Az@2026Ms", "مصطفى حسن", "viewer"),
    ("ibrahim.ahmed", "Az@2026Ib", "ابراهيم احمد", "viewer"),
    ("hesham.ali", "Az@2026He", "هشام علي", "viewer"),
    ("wael.mostafa", "Az@2026Wa", "وائل مصطفى", "viewer"),
    ("ayman.hassan", "Az@2026Ay", "ايمن حسن", "viewer"),
    ("samir.ali", "Az@2026Sa", "سمير علي", "viewer"),
    ("reda.farouk", "Az@2026Re", "رضا فاروق", "viewer"),
    ("gamal.ahmed", "Az@2026Ga", "جمال احمد", "viewer"),
    ("adel.hassan", "Az@2026Ad", "عادل حسن", "viewer"),
    ("hatem.ali", "Az@2026Hat", "حاتم علي", "viewer"),
    ("sherif.mostafa", "Az@2026Sh", "شريف مصطفى", "viewer"),
    ("basem.hassan", "Az@2026Bas", "باسم حسن", "viewer"),
    ("nader.ali", "Az@2026Na", "نادر علي", "viewer"),
    ("islam.ahmed", "Az@2026Is", "اسلام احمد", "viewer"),
    ("ashraf.hassan", "Az@2026Ash", "اشرف حسن", "viewer"),
    ("walid.ali", "Az@2026Wal", "وليد علي", "viewer"),
    ("fady.mostafa", "Az@2026Fa", "فادي مصطفى", "viewer"),
    ("maged.hassan", "Az@2026Mag", "ماجد حسن", "viewer"),
    ("ramy.ali", "Az@2026Ra", "رامي علي", "viewer"),
    ("ehab.ahmed", "Az@2026Eh", "ايهاب احمد", "viewer"),
    ("saeed.hassan", "Az@2026Sae", "سعيد حسن", "viewer"),
    ("emad.ali", "Az@2026Em", "عماد علي", "viewer"),
    ("fathy.mostafa", "Az@2026Fath", "فتحي مصطفى", "viewer"),
    ("sayed.hassan", "Az@2026Sey", "سيد حسن", "viewer"),
    ("abdelrahman.ali", "Az@2026Abr", "عبدالرحمن علي", "viewer"),
    ("hany.ahmed", "Az@2026Han", "هاني احمد", "viewer"),
    ("mohsen.hassan", "Az@2026Moh", "محسن حسن", "viewer"),
    ("lotfy.ali", "Az@2026Lot", "لطفي علي", "viewer"),
    ("galal.mostafa", "Az@2026Gal", "جلال مصطفى", "viewer"),
    ("shawky.hassan", "Az@2026Shaw", "شوقى حسن", "viewer"),
]

def main():
    existing = load_users()
    added = 0
    skipped = 0
    errors = 0
    
    print("=" * 50)
    print("🚀 Adding employees to AZ Travel Portal")
    print("=" * 50)
    
    for username, password, full_name, role in EMPLOYEES:
        if username in existing:
            print(f"  ⏭️  {username} ({full_name}) - already exists, skipping")
            skipped += 1
            continue
        ok, result = create_user(username, password, full_name, role)
        if ok:
            icon = "⚙️" if role == "admin" else "👁️"
            print(f"  ✅ {icon} {username} ({full_name}) - {role}")
            added += 1
        else:
            print(f"  ❌ {username} - Error: {result}")
            errors += 1
    
    print("\n" + "=" * 50)
    print(f"📊 Summary:")
    print(f"   ✅ Added: {added}")
    print(f"   ⏭️  Skipped: {skipped}")
    print(f"   ❌ Errors: {errors}")
    print(f"   📋 Total users: {len(load_users())}")
    print("=" * 50)
    
    print("\n🔑 Login credentials (username / password):")
    print("-" * 50)
    for username, password, full_name, role in EMPLOYEES:
        icon = "⚙️" if role == "admin" else "👁️"
        print(f"  {icon} {username:20s} / {password:15s} | {full_name}")
    
    print("\n⚠️  IMPORTANT: Change passwords after first login!")
    print("   Share each user their own credentials privately.")

if __name__ == "__main__":
    main()
