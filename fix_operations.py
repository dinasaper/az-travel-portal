#!/usr/bin/env python3
"""Convert operations Excel - fix column mapping."""
import openpyxl, json, os
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "static", "data")

def serialize(val):
    if val is None: return ""
    if isinstance(val, (datetime, date)): return val.strftime("%Y-%m-%d")
    if isinstance(val, float):
        if val == int(val): return int(val)
        return round(val, 2)
    return str(val).strip()

def convert_operations():
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "التشغيل.xlsx"), data_only=True, read_only=True)
    ws = wb["تشغيل "]
    rows = list(ws.iter_rows(values_only=True))
    
    # CORRECT header mapping based on Excel row 4 (index 3)
    headers = {
        0: "رقم السيارة (الأصالة)",
        1: "نوعها (الأصالة)",
        2: "رقم السيارة (الأصالة)2",
        3: "نوعها (الأصالة)2",
        4: "رقم السيارة (AZ)",
        5: "نوعها (AZ)",
        6: "الشركة",
        7: "اسم السائق",
        9: "النوع",
        10: "الكود",
        11: "كود التشغيلة",
        12: "كود التشغيلة2",
        13: "بداية التشغيلة",
        14: "نهاية التشغيلة",
        15: "رقم السيارة (التشغيلية)",
        16: "رقم السيارة (التشغيلية)2",
        17: "نوعها (التشغيلية)",
        18: "ب كم",
        19: "ن كم",
        20: "عدد الايام",
        21: "كم المستخدم",
        22: "كم المتاح",
        23: "كم الزيادة",
        24: "سعر اليوم",
        25: "فرق سعر اليوم",
        26: "سعر كم الزيادة",
        27: "فرق سعر كم الزيادة",
        28: "جملة التشغيلة",
        29: "3% خصم",
        30: "ض . م",
        31: "الاجمالي بعد الضريبة",
        32: "العموله",
        33: "فرق سعر",
        34: "فواتير بنزين",
        35: "اجر السائق",
        36: "ساعات اضافية",
        37: "بدل مبيت سائق",
        38: "الصافي",
        39: "رقم الفاتورة",
        40: "تاريخ الفاتورة",
        41: "اسم السائق2",
        42: "اسم العميل",
        43: "نوع العميل",
        44: "رقم التليفون",
        45: "رقم العقد",
        46: "ساعة الخروج",
        47: "ملاحظات",
        48: "خط السير",
        49: "داين",
        50: "رصيد",
        51: "الحالة",
        52: "تاريخ التصفية",
    }
    
    data = []
    for row in rows[4:]:  # Data starts at row 5 (index 4)
        record = {}
        has_data = False
        for col_idx, col_name in headers.items():
            val = serialize(row[col_idx] if col_idx < len(row) else "")
            record[col_name] = val
            if val: has_data = True
        if has_data:
            data.append(record)
    
    wb.close()
    
    # Remove empty columns
    all_cols = list(data[0].keys()) if data else []
    cols_with_data = set()
    for row in data:
        for col in all_cols:
            if row.get(col, ""):
                cols_with_data.add(col)
    
    filtered = []
    for row in data:
        filtered.append({k: v for k, v in row.items() if k in cols_with_data})
    
    out_path = os.path.join(OUT_DIR, "operations.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump(filtered, f, ensure_ascii=False)
    
    print(f"✅ operations: {len(filtered)} سجل, {len(cols_with_data)} عمود")
    print(f"الأعمدة: {list(cols_with_data)[:10]}...")

if __name__ == "__main__":
    convert_operations()
