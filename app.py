from flask import Flask, request, jsonify
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
import json

app = Flask(__name__)
app.config['JSON_SORT_KEYS'] = False
app.config['JSONIFY_PRETTYPRINT_REGULAR'] = True
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT,
    email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT,
    father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT,
    kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT,
    api_key TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    
    # Migrate PWANI -> FIG
    try:
        conn.execute("UPDATE users SET project='FIG' WHERE project='PWANI' OR project='pwani'")
    except: pass
    
    # Create admin if not exists
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("FIG/001", "Admin User", "FIG", "Oct 2026", "admin@lonma.com", 
         generate_password_hash("admin123"), "Admin", "0700000000",
         "FATHER_ID_001", "MOTHER_ID_001", "22400966", "23601476", 
         "42107914", "111041990", "", "", "", "lonma_api_key_12345"))
    
    conn.commit()
    conn.close()

init_db()

# CORS + Security Headers
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY,Authorization')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS')
    r.headers.add('Content-Type','application/json')
    return r

# API Key Guard
def need_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        key = request.headers.get("X-API-KEY") or request.args.get("api_key") or request.headers.get("Authorization")
        if key and key.startswith("Bearer "):
            key = key.replace("Bearer ","")
        if not key:
            return jsonify({"error": "API key required", "how_to": "Use header X-API-KEY: lonma_api_key_12345"}), 401
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE api_key=?", (key,)).fetchone()
        conn.close()
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated

# Fix favicon 404 spam
@app.route("/favicon.ico")
def favicon():
    return "", 204

# ROOT - Pure FIG API Info
@app.route("/", methods=["GET"])
def root():
    return jsonify({
        "service": "LONMA FIG WELFARE API",
        "status": "LIVE",
        "version": "Pure API v7 - FINAL - FIG",
        "project": "FIG",
        "base_url": "https://lonma-orbit-24qw.onrender.com",
        "master_api_key": "lonma_api_key_12345",
        "endpoints": {
            "GET /": "This info",
            "GET /api/health": "Health check",
            "GET /api/members": "Get all FIG members (needs API key)",
            "GET /api/members/<id>": "Get one member",
            "POST /api/register": "Register FIG member (WELFARE_DATA fields)",
            "POST /api/login": "Login",
            "PUT /api/members/<id>": "Update member",
            "DELETE /api/members/<id>": "Delete member",
            "GET /api/stats": "FIG stats"
        },
        "welfare_fields": {
            "staff_no": "FIG/001",
            "full_names": "John Doe",
            "project": "FIG",
            "month_year_joined": "Oct 2026",
            "email": "john@lonma.com",
            "phone": "0700000000",
            "father_id": "ID Number",
            "mother_id": "ID Number",
            "guardian_id": "22400966",
            "spouse_id": "23601476",
            "kids": ["42107914","111041990","kid3","kid4","kid5"]
        }
    })

@app.route("/api/health", methods=["GET"])
def health():
    conn = get_db()
    try:
        count = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        conn.close()
        return jsonify({"status": "ok", "project": "FIG", "db": "connected", "total_members": count})
    except Exception as e:
        return jsonify({"status": "error", "error": str(e)}), 500

@app.route("/api/members", methods=["GET", "OPTIONS"])
@need_key
def get_members():
    if request.method == 'OPTIONS':
        return '', 200
    conn = get_db()
    users = conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
    conn.close()
    members = []
    for u in users:
        members.append({
            "id": u["id"],
            "staff_no": u["staff_no"],
            "full_names": u["full_names"],
            "project": u["project"],
            "month_year_joined": u["month_year_joined"],
            "email": u["email"],
            "phone": u["phone"],
            "role": u["role"],
            "family_ids": {
                "father_id": u["father_id"],
                "mother_id": u["mother_id"],
                "guardian_id": u["guardian_id"],
                "spouse_id": u["spouse_id"]
            },
            "kids_birth_certificates": {
                "kid1": u["kid1"],
                "kid2": u["kid2"],
                "kid3": u["kid3"],
                "kid4": u["kid4"],
                "kid5": u["kid5"]
            },
            "created_at": u["created_at"]
        })
    return jsonify({"project": "FIG", "total": len(members), "members": members})

@app.route("/api/members/<int:member_id>", methods=["GET", "OPTIONS"])
@need_key
def get_one(member_id):
    if request.method == 'OPTIONS':
        return '', 200
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE id=?", (member_id,)).fetchone()
    conn.close()
    if not u:
        return jsonify({"error": "Member not found"}), 404
    return jsonify({
        "id": u["id"], "staff_no": u["staff_no"], "full_names": u["full_names"],
        "project": "FIG", "email": u["email"], "phone": u["phone"],
        "father_id": u["father_id"], "mother_id": u["mother_id"],
        "guardian_id": u["guardian_id"], "spouse_id": u["spouse_id"],
        "kids": [u["kid1"], u["kid2"], u["kid3"], u["kid4"], u["kid5"]]
    })

@app.route("/api/register", methods=["POST", "OPTIONS"])
def register():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Send JSON body", "example": {"full_names":"John Doe","email":"john@lonma.com","password":"1234","father_id":"123","mother_id":"456"}}), 400
    if not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password required"}), 400
    try:
        api_key = f"lonma_{secrets.token_hex(16)}"
        conn = get_db()
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (
            data.get("staff_no", f"FIG/{secrets.token_hex(2).upper()}"),
            data.get("full_names", data.get("name","")),
            "FIG",
            data.get("month_year_joined",""),
            data.get("email"),
            generate_password_hash(data.get("password")),
            data.get("role","Member"),
            data.get("phone",""),
            data.get("father_id",""),
            data.get("mother_id",""),
            data.get("guardian_id",""),
            data.get("spouse_id",""),
            data.get("kid1",""),
            data.get("kid2",""),
            data.get("kid3",""),
            data.get("kid4",""),
            data.get("kid5",""),
            api_key
        ))
        conn.commit()
        user = conn.execute("SELECT id, staff_no, full_names, email, project, api_key FROM users WHERE email=?", (data["email"],)).fetchone()
        conn.close()
        return jsonify({"message": "FIG member registered successfully", "member": dict(user)}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400

@app.route("/api/login", methods=["POST", "OPTIONS"])
def login():
    if request.method == 'OPTIONS':
        return '', 200
    data = request.get_json(silent=True)
    if not data or not data.get("email"):
        return jsonify({"error": "Send JSON with email and password"}), 400
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE email=?", (data.get("email"),)).fetchone()
    conn.close()
    if not user or not check_password_hash(user["password"], data.get("password","")):
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify({
        "message": "Login success",
        "project": "FIG",
        "member": {
            "id": user["id"],
            "full_names": user["full_names"],
            "email": user["email"],
            "staff_no": user["staff_no"],
            "role": user["role"],
            "api_key": user["api_key"]
        }
    })

@app.route("/api/members/<int:member_id>", methods=["PUT", "DELETE", "OPTIONS"])
@need_key
def modify_member(member_id):
    if request.method == 'OPTIONS':
        return '', 200
    conn = get_db()
    if request.method == "DELETE":
        conn.execute("DELETE FROM users WHERE id=?", (member_id,))
        conn.commit()
        conn.close()
        return jsonify({"message": f"FIG Member {member_id} deleted"})

    data = request.get_json(silent=True)
    if not data:
        return jsonify({"error": "Send JSON"}), 400
    allowed = ["staff_no","full_names","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]
    fields = []
    vals = []
    for k in allowed:
        if k in data:
            fields.append(f"{k}=?")
            vals.append(data[k])
    if not fields:
        return jsonify({"error": "No fields to update"}), 400
    fields.append("project=?")
    vals.append("FIG")
    vals.append(member_id)
    conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", vals)
    conn.commit()
    conn.close()
    return jsonify({"message": "FIG member updated", "id": member_id})

@app.route("/api/stats", methods=["GET", "OPTIONS"])
@need_key
def stats():
    if request.method == 'OPTIONS':
        return '', 200
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    admins = conn.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
    conn.close()
    return jsonify({"project": "FIG", "total_members": total, "admins": admins, "members": total-admins})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
