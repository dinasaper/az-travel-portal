"""AZ Travel Portal - Flask Backend."""
import os
import json
from flask import Flask, request, jsonify, send_from_directory, send_file
from auth import verify_user, get_user_by_token, create_user, delete_user, list_users, log_audit, get_audit_logs, init_default_users

app = Flask(__name__, static_folder="static", static_url_path="/static")

DATA_DIR = os.path.join(os.path.dirname(__file__), "static", "data")

# Protected modules (require edit password / admin role)
PROTECTED_EDIT = {"operations", "treasury_main", "treasury_salaf", "treasury_fuel",
                  "treasury_maintenance", "treasury_payments", "bank_qnb_az",
                  "bank_qnb_asala", "bank_treasury"}

# All data modules with their display names
MODULES = {
    "inventory_items": {"ar": "دليل الأصناف", "en": "Inventory Items", "icon": "📦", "protected": False},
    "inventory_out": {"ar": "منصرف (مبيعات)", "en": "Inventory Out", "icon": "📤", "protected": False},
    "inventory_in": {"ar": "وارد (مدخلات المخزن)", "en": "Inventory In", "icon": "📥", "protected": False},
    "inventory_ledger": {"ar": "دفتر الأصناف", "en": "Item Ledger", "icon": "📒", "protected": False},
    "maintenance": {"ar": "الصيانة", "en": "Maintenance", "icon": "🔧", "protected": False},
    "sales_invoices": {"ar": "فواتير مبيعات الصاله", "en": "Sales Invoices", "icon": "🧾", "protected": False},
    "insurance_axa": {"ar": "وثائق تأمين أكسا", "en": "AXA Insurance", "icon": "🛡️", "protected": False},
    "insurance_orient": {"ar": "وثائق تأمين أورينت", "en": "Orient Insurance", "icon": "🛡️", "protected": False},
    "operations": {"ar": "التشغيل", "en": "Operations", "icon": "🚗", "protected": True},
    "treasury_main": {"ar": "الخزنة - العهد", "en": "Treasury - Main", "icon": "💰", "protected": True},
    "treasury_salaf": {"ar": "السلف", "en": "Advances", "icon": "💵", "protected": True},
    "treasury_fuel": {"ar": "عهد البنزين", "en": "Fuel Account", "icon": "⛽", "protected": True},
    "treasury_maintenance": {"ar": "عهدة صيانة", "en": "Maintenance Account", "icon": "🔩", "protected": True},
    "treasury_payments": {"ar": "دفعات تحت الحساب", "en": "Advance Payments", "icon": "💳", "protected": True},
    "bank_qnb_az": {"ar": "حساب AZ بنك QNB", "en": "AZ QNB Account", "icon": "🏦", "protected": True},
    "bank_qnb_asala": {"ar": "حساب الأصالة بنك QNB", "en": "Asala QNB Account", "icon": "🏦", "protected": True},
    "bank_treasury": {"ar": "الخزنة (بنوك)", "en": "Bank Treasury", "icon": "🏛️", "protected": True},
}

def get_token_user():
    """Extract user from Authorization header."""
    auth = request.headers.get("Authorization", "")
    if auth.startswith("Bearer "):
        token = auth[7:]
        return get_user_by_token(token)
    return None

@app.route("/")
def index():
    return send_file("index.html")

@app.route("/api/login", methods=["POST"])
def login():
    data = request.json
    user = verify_user(data.get("username", ""), data.get("password", ""))
    if user:
        log_audit("login", user["username"])
        return jsonify({"ok": True, "user": user})
    return jsonify({"ok": False, "error": "Invalid credentials"}), 401

@app.route("/api/me")
def me():
    user = get_token_user()
    if user:
        return jsonify({"ok": True, "user": user})
    return jsonify({"ok": False}), 401

@app.route("/api/modules")
def modules():
    return jsonify(MODULES)

@app.route("/api/data/<module_name>")
def get_data(module_name):
    user = get_token_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    if module_name not in MODULES:
        return jsonify({"error": "Module not found"}), 404

    json_path = os.path.join(DATA_DIR, f"{module_name}.json")
    if not os.path.exists(json_path):
        return jsonify({"data": [], "total": 0})

    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    # Pagination
    page = int(request.args.get("page", 1))
    per_page = int(request.args.get("per_page", 50))
    search = request.args.get("search", "").strip()
    sort_col = request.args.get("sort", "")
    sort_dir = request.args.get("sort_dir", "asc")

    # Search filter
    if search:
        search_lower = search.lower()
        data = [r for r in data if any(search_lower in str(v).lower() for v in r.values())]

    # Sort
    if sort_col and sort_col in (data[0] if data else {}):
        try:
            data.sort(key=lambda x: float(x.get(sort_col, 0) or 0), reverse=(sort_dir == "desc"))
        except (ValueError, TypeError):
            data.sort(key=lambda x: str(x.get(sort_col, "")), reverse=(sort_dir == "desc"))

    total = len(data)
    start = (page - 1) * per_page
    end = start + per_page

    log_audit("view", user["username"], module_name, f"page={page}")

    return jsonify({
        "data": data[start:end],
        "total": total,
        "page": page,
        "per_page": per_page,
        "pages": (total + per_page - 1) // per_page
    })

@app.route("/api/data/<module_name>/all")
def get_all_data(module_name):
    """Get all data for charts/stats (no pagination)."""
    user = get_token_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if module_name not in MODULES:
        return jsonify({"error": "Module not found"}), 404
    json_path = os.path.join(DATA_DIR, f"{module_name}.json")
    if not os.path.exists(json_path):
        return jsonify({"data": []})
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    return jsonify({"data": data})

@app.route("/api/data/<module_name>/add", methods=["POST"])
def add_record(module_name):
    user = get_token_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    if module_name not in MODULES:
        return jsonify({"error": "Module not found"}), 404

    record = request.json
    json_path = os.path.join(DATA_DIR, f"{module_name}.json")
    data = []
    if os.path.exists(json_path):
        with open(json_path, "r", encoding="utf-8") as f:
            data = json.load(f)
    data.append(record)
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False)

    log_audit("add", user["username"], module_name, json.dumps(record, ensure_ascii=False)[:200])
    return jsonify({"ok": True, "total": len(data)})

@app.route("/api/data/<module_name>/delete", methods=["POST"])
def delete_record(module_name):
    user = get_token_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401
    if user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403

    idx = request.json.get("index", -1)
    json_path = os.path.join(DATA_DIR, f"{module_name}.json")
    if not os.path.exists(json_path):
        return jsonify({"error": "Not found"}), 404
    with open(json_path, "r", encoding="utf-8") as f:
        data = json.load(f)
    if 0 <= idx < len(data):
        removed = data.pop(idx)
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False)
        log_audit("delete", user["username"], module_name, json.dumps(removed, ensure_ascii=False)[:200])
        return jsonify({"ok": True})
    return jsonify({"error": "Invalid index"}), 400

# User management (admin only)
@app.route("/api/users", methods=["GET"])
def get_users():
    user = get_token_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    return jsonify({"users": list_users()})

@app.route("/api/users/add", methods=["POST"])
def add_user():
    user = get_token_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    data = request.json
    ok, result = create_user(
        data["username"], data["password"],
        data.get("full_name", ""), data.get("role", "viewer")
    )
    if ok:
        log_audit("create_user", user["username"], "users", data["username"])
        return jsonify({"ok": True})
    return jsonify({"error": result}), 400

@app.route("/api/users/delete", methods=["POST"])
def del_user():
    user = get_token_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    username = request.json.get("username")
    if username == "admin":
        return jsonify({"error": "Cannot delete admin"}), 400
    if delete_user(username):
        log_audit("delete_user", user["username"], "users", username)
        return jsonify({"ok": True})
    return jsonify({"error": "User not found"}), 404

@app.route("/api/audit")
def audit_logs():
    user = get_token_user()
    if not user or user["role"] != "admin":
        return jsonify({"error": "Admin access required"}), 403
    limit = int(request.args.get("limit", 200))
    return jsonify({"logs": get_audit_logs(limit)})

@app.route("/api/stats")
def stats():
    user = get_token_user()
    if not user:
        return jsonify({"error": "Unauthorized"}), 401

    result = {}
    for mod in MODULES:
        json_path = os.path.join(DATA_DIR, f"{mod}.json")
        if os.path.exists(json_path):
            with open(json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
            result[mod] = len(data)
        else:
            result[mod] = 0
    return jsonify(result)

if __name__ == "__main__":
    init_default_users()
    app.run(host="0.0.0.0", port=5000, debug=False)
