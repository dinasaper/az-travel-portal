"""User management and auth for AZ Travel portal."""
import json
import os
import hashlib
import secrets
from datetime import datetime

USERS_FILE = os.path.join(os.path.dirname(__file__), "users.json")
AUDIT_FILE = os.path.join(os.path.dirname(__file__), "audit_log.json")

def load_users():
    if os.path.exists(USERS_FILE):
        with open(USERS_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return {}

def save_users(users):
    with open(USERS_FILE, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=2)

def hash_password(password):
    return hashlib.sha256(password.encode()).hexdigest()

def create_user(username, password, full_name="", role="viewer"):
    users = load_users()
    if username in users:
        return False, "User already exists"
    users[username] = {
        "password": hash_password(password),
        "full_name": full_name,
        "role": role,  # "admin" or "viewer"
        "created": datetime.now().isoformat(),
        "token": secrets.token_hex(32)
    }
    save_users(users)
    return True, users[username]["token"]

def verify_user(username, password):
    users = load_users()
    if username not in users:
        return None
    if users[username]["password"] != hash_password(password):
        return None
    # Generate new token
    token = secrets.token_hex(32)
    users[username]["token"] = token
    users[username]["last_login"] = datetime.now().isoformat()
    save_users(users)
    return {
        "username": username,
        "full_name": users[username].get("full_name", ""),
        "role": users[username]["role"],
        "token": token
    }

def get_user_by_token(token):
    users = load_users()
    for username, data in users.items():
        if data.get("token") == token:
            return {
                "username": username,
                "full_name": data.get("full_name", ""),
                "role": data["role"]
            }
    return None

def delete_user(username):
    users = load_users()
    if username in users:
        del users[username]
        save_users(users)
        return True
    return False

def list_users():
    users = load_users()
    return [{
        "username": u,
        "full_name": d.get("full_name", ""),
        "role": d["role"],
        "last_login": d.get("last_login", "Never")
    } for u, d in users.items()]

def log_audit(action, username, module="", details=""):
    logs = []
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
    logs.append({
        "timestamp": datetime.now().isoformat(),
        "action": action,
        "username": username,
        "module": module,
        "details": details
    })
    # Keep last 10000 entries
    if len(logs) > 10000:
        logs = logs[-10000:]
    with open(AUDIT_FILE, "w", encoding="utf-8") as f:
        json.dump(logs, f, ensure_ascii=False, indent=2)

def get_audit_logs(limit=500):
    if os.path.exists(AUDIT_FILE):
        with open(AUDIT_FILE, "r", encoding="utf-8") as f:
            logs = json.load(f)
        return logs[-limit:]
    return []

def init_default_users():
    """Create default admin if no users exist."""
    users = load_users()
    if not users:
        create_user("admin", "admin123", "System Admin", "admin")
        print("Default admin created: admin / admin123")

if __name__ == "__main__":
    init_default_users()
    print("Users:", list_users())
