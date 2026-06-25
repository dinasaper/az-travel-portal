#!/usr/bin/env python3
"""Convert Excel to JSON - ALL COLUMNS, NO FILTERING."""
import openpyxl, json, os
from datetime import datetime, date

DATA_DIR = os.path.join(os.path.dirname(__file__), "data")
OUT_DIR = os.path.join(os.path.dirname(__file__), "static", "data")
os.makedirs(OUT_DIR, exist_ok=True)

def serialize(val):
    if val is None: return ""
    if isinstance(val, (datetime, date)): return val.strftime("%Y-%m-%d")
    if isinstance(val, float):
        if val == int(val): return int(val)
        return round(val, 2)
    return str(val).strip()

def extract_sheet(wb, sheet_name, header_row, data_start_row):
    """Extract ALL columns - no filtering."""
    if sheet_name not in wb.sheetnames: return []
    ws = wb[sheet_name]
    rows = list(ws.iter_rows(values_only=True))
    if len(rows) <= header_row: return []
    
    # Get ALL headers from header row - use column index if header is empty
    raw_headers = rows[header_row]
    headers = []
    for i, h in enumerate(raw_headers):
        if h and str(h).strip():
            headers.append(str(h).strip())
        else:
            headers.append(f"عمود_{i+1}")
    
    data = []
    for row in rows[data_start_row:]:
        record = {}
        has_data = False
        for i, h in enumerate(headers):
            val = serialize(row[i] if i < len(row) else "")
            record[h] = val
            if val: has_data = True
        if has_data:
            data.append(record)
    return data

def convert_all():
    results = {}

    # 1. المخزن الجديد
    print("📦 المخزن الجديد...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "المخزن_الجديد.xlsx"), data_only=True)
    results["inventory_items"] = extract_sheet(wb, "code", 3, 4)
    results["inventory_out"] = extract_sheet(wb, "منصرف(مبيعات)", 2, 3)
    results["inventory_in"] = extract_sheet(wb, "وارد ( مدخلات المخزن)", 2, 3)
    results["inventory_ledger"] = extract_sheet(wb, "دفترالاصناف", 3, 4)
    wb.close()

    # 2. صيانة 2026
    print("🔧 صيانة 2026...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "صيانة_2026.xlsx"), data_only=True)
    results["maintenance_codes"] = extract_sheet(wb, "كود", 3, 4)
    results["maintenance"] = extract_sheet(wb, "صيانة", 3, 4)
    wb.close()

    # 3. فواتير مبيعات الصاله
    print("🧾 فواتير مبيعات الصاله...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "فواتير_مبيعات_الصاله.xlsx"), data_only=True)
    results["sales_invoices"] = extract_sheet(wb, "مبيعات الاصاله 2026 ", 1, 2)
    wb.close()

    # 4. حسابات البنوك
    print("🏦 حسابات البنوك...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "حسابات_البنوك.xlsx"), data_only=True)
    results["bank_qnb_az"] = extract_sheet(wb, "حساب ايه زد بنك QNB", 1, 3)
    results["bank_qnb_asala"] = extract_sheet(wb, "حساب الاصالة بنك QNB", 1, 3)
    results["bank_treasury"] = extract_sheet(wb, "الخزنة", 2, 3)
    wb.close()

    # 5. وثائق اكسا
    print("🛡️ وثائق اكسا...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "وثائق_اكسا.xlsx"), data_only=True)
    results["insurance_axa"] = extract_sheet(wb, "وثائق اكسا للتأمين", 0, 1)
    wb.close()

    # 6. وثائق اورينت
    print("🛡️ وثائق اورينت...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "وثائق_اورينت.xlsx"), data_only=True)
    results["insurance_orient"] = extract_sheet(wb, "وثائق اورينت (2)", 0, 1)
    wb.close()

    # 7. التشغيل - MOST IMPORTANT - 71 columns!
    print("🚗 التشغيل (71 عمود)...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "التشغيل.xlsx"), data_only=True)
    results["operation_codes"] = extract_sheet(wb, "كود", 3, 4)
    results["operations"] = extract_sheet(wb, "تشغيل ", 3, 4)
    wb.close()

    # 8. الخزنة - 61-124 columns!
    print("💰 الخزنة (124 عمود)...")
    wb = openpyxl.load_workbook(os.path.join(DATA_DIR, "الخزنة.xlsx"), data_only=True)
    results["treasury_main"] = extract_sheet(wb, "العهد", 7, 8)
    results["treasury_salaf"] = extract_sheet(wb, "السلف", 3, 4)
    results["treasury_fuel"] = extract_sheet(wb, "عهد البنزين", 3, 4)
    results["treasury_maintenance"] = extract_sheet(wb, "عهدة صيانة", 4, 5)
    results["treasury_payments"] = extract_sheet(wb, "دفعات تحت الحساب", 2, 3)
    wb.close()

    # Save all
    for key, data in results.items():
        with open(os.path.join(OUT_DIR, f"{key}.json"), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        cols = len(data[0]) if data else 0
        print(f"  ✅ {key}: {len(data)} سجل, {cols} عمود")

    print("\n🎉 تم التحويل بنجاح!")

if __name__ == "__main__":
    convert_all()
