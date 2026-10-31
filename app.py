from flask import Flask, request, jsonify
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-fig-pure-api"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT,
    email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT,
    father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT,
    kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT,
    api_key TEXT)''')
    # Auto-update old PWANI to FIG
    conn.execute("UPDATE users SET project='FIG' WHERE project='PWANI' OR project IS NULL OR project=''")
    
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("FIG/001", "Admin User", "FIG", "Oct 2026", "admin@lonma.com", generate_password_hash("admin123"), "Admin", "0700000000",
         "N/A", "N/A", "22400966", "23601476", "42107914", "111041990", "", "", "", "lonma_api_key_12345"))
    conn.commit(); conn.close()
init_db()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY,Authorization')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS')
    return r

def need_key(f):
    @wraps(f)
    def d(*a,**k):
        if request.method=='OPTIONS': return '',200
        key=request.headers.get("X-API-KEY") or request.args.get("api_key") or request.headers.get("Authorization")
        if key and key.startswith("Bearer "): key=key.replace("Bearer ","")
        if not key: return jsonify({"error":"API key required. Use header X-API-KEY: lonma_api_key_12345"}),401
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone(); conn.close()
        if not u: return jsonify({"error":"Invalid API key"}),401
        return f(*a,**k)
    return d

@app.route("/")
def root():
    return jsonify({
        "service": "LONMA FIG WELFARE API",
        "status": "LIVE",
        "version": "Pure API v6 - FIG",
        "base_url": "https://lonma-orbit-24qw.onrender.com",
        "master_api_key": "lonma_api_key_12345",
        "project": "FIG",
        "endpoints": {
            "GET /": "This info",
            "GET /api/health": "Health check",
            "GET /api/members": "Get all FIG members",
            "POST /api/register": "Register FIG member",
            "POST /api/login": "Login"
        }
    })

@app.route("/api/health")
def health(): return jsonify({"status":"ok","project":"FIG WELFARE","db":"connected"})

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    conn=get_db(); users=conn.execute("SELECT * FROM users WHERE project='FIG' OR project='PWANI' ORDER BY id DESC").fetchall(); conn.close()
    data=[]
    for u in users:
        data.append({
            "id": u["id"], "staff_no": u["staff_no"], "full_names": u["full_names"],
            "project": "FIG", "month_year_joined": u["month_year_joined"],
            "email": u["email"], "phone": u["phone"], "role": u["role"],
            "parents_ids": {"father_id": u["father_id"], "mother_id": u["mother_id"]},
            "guardian_id": u["guardian_id"], "spouse_id": u["spouse_id"],
            "kids_birth_certificates": {"kid1": u["kid1"], "kid2": u["kid2"], "kid3": u["kid3"], "kid4": u["kid4"], "kid5": u["kid5"]},
        })
    return jsonify({"total": len(data), "project": "FIG", "members": data})

@app.route("/api/register", methods=["POST","OPTIONS"])
def register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d: return jsonify({"error":"Send JSON body"}),400
    if not d.get("email") or not d.get("password"): return jsonify({"error":"email and password required"}),400
    try:
        key=f"lonma_{secrets.token_hex(16)}"
        conn=get_db()
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d.get("staff_no",f"FIG/{secrets.token_hex(2).upper()}"), d.get("full_names",d.get("name","")), "FIG", d.get("month_year_joined",""),
         d.get("email"), generate_password_hash(d.get("password")), d.get("role","Member"), d.get("phone",""),
         d.get("father_id",""), d.get("mother_id",""), d.get("guardian_id",""), d.get("spouse_id",""),
         d.get("kid1",""), d.get("kid2",""), d.get("kid3",""), d.get("kid4",""), d.get("kid5",""), key))
        conn.commit()
        u=conn.execute("SELECT id, staff_no, full_names, email, role, project, api_key FROM users WHERE email=?",(d["email"],)).fetchone()
        conn.close()
        return jsonify({"message":"FIG member registered","member":dict(u)}),201
    except Exception as e:
        return jsonify({"error":str(e)}),400

@app.route("/api/login", methods=["POST","OPTIONS"])
def login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d: return jsonify({"error":"Send JSON"}),400
    conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); conn.close()
    if not u or not check_password_hash(u["password"], d.get("password","")):
        return jsonify({"error":"Invalid email or password"}),401
    return jsonify({"message":"Login success","project":"FIG","member":{"id":u["id"],"full_names":u["full_names"],"email":u["email"],"role":u["role"],"api_key":u["api_key"]}})

@app.route("/api/members/<int:id>", methods=["PUT","DELETE","OPTIONS"])
@need_key
def modify(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    if request.method=="DELETE":
        conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close()
        return jsonify({"message":f"FIG Member {id} deleted"})
    d=request.get_json(silent=True)
    allowed=["staff_no","full_names","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]
    fields=[]; vals=[]
    for k in allowed:
        if k in d: fields.append(f"{k}=?"); vals.append(d[k])
    fields.append("project=?"); vals.append("FIG")
    vals.append(id)
    conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", vals); conn.commit(); conn.close()
    return jsonify({"message":"Updated to FIG","id":id})

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    conn=get_db()
    total=conn.execute("SELECT COUNT(*) FROM users WHERE project='FIG' OR project='PWANI'").fetchone()[0]
    conn.close()
    return jsonify({"project":"FIG","total_members":total})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
