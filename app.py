from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
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
    try: conn.execute("UPDATE users SET project='FIG' WHERE project='PWANI'")
    except: pass
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
        if not key: return jsonify({"error":"API key required"}),401
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone(); conn.close()
        if not u: return jsonify({"error":"Invalid key"}),401
        return f(*a,**k)
    return d

@app.route("/favicon.ico")
def favicon(): return "",204

# PRETTY LANDING PAGE FOR SHARING
@app.route("/", methods=["GET"])
def root():
    html = """
    <!DOCTYPE html>
    <html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
    <title>LONMA FIG WELFARE API</title>
    <style>
    body{font-family:system-ui,-apple-system,sans-serif;background:#0f172a;color:#e2e8f0;margin:0;padding:20px}
    .card{max-width:800px;margin:20px auto;background:#1e293b;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,.3)}
    h1{color:#38bdf8;margin:0 0 10px;font-size:28px} .live{color:#4ade80;font-weight:bold}
    .badge{background:#334155;padding:4px 10px;border-radius:20px;font-size:12px;display:inline-block;margin:4px}
    .endpoint{background:#0f172a;padding:12px;border-radius:8px;margin:8px 0;font-family:monospace;font-size:13px;border-left:4px solid #38bdf8}
    a{color:#38bdf8;text-decoration:none} .btn{background:#38bdf8;color:#0f172a;padding:10px 18px;border-radius:8px;display:inline-block;font-weight:bold;margin-top:10px}
    </style></head><body>
    <div class="card">
        <h1>🚀 LONMA FIG WELFARE API</h1>
        <p><span class="live">● LIVE</span> Pure API v8 - FINAL - FIG</p>
        <p><b>Base URL:</b> https://lonma-orbit-24qw.onrender.com</p>
        <p><b>Master Key:</b> <span class="badge">lonma_api_key_12345</span> <span class="badge">Project: FIG</span></p>
        <a class="btn" href="/api/health">Check Health</a> <a class="btn" style="background:#4ade80" href="/api/members?api_key=lonma_api_key_12345">View Members JSON</a>
        <h3 style="margin-top:30px">📋 Endpoints</h3>
        <div class="endpoint">GET /api/health → Health check</div>
        <div class="endpoint">GET /api/members?api_key=KEY → Get all FIG members</div>
        <div class="endpoint">POST /api/register → Register {full_names,email,password,father_id,mother_id,guardian_id,spouse_id,kid1..kid5}</div>
        <div class="endpoint">POST /api/login → {email,password}</div>
        <div class="endpoint">PUT /api/members/1?api_key=KEY → Update</div>
        <div class="endpoint">DELETE /api/members/1?api_key=KEY → Delete</div>
        <div class="endpoint">GET /api/stats?api_key=KEY → FIG stats</div>
        <h3>🎯 WELFARE_DATA Fields</h3>
        <p>staff_no, full_names, project=FIG, month_year_joined, email, phone, father_id, mother_id, guardian_id, spouse_id, kid1-kid5 birth certs</p>
        <p style="color:#94a3b8;font-size:12px;margin-top:20px">Deployed on Render • FIG Project • Changed from PWANI • 2026</p>
    </div></body></html>
    """
    return render_template_string(html)

@app.route("/api")
def api_info():
    return jsonify({"service":"LONMA FIG WELFARE API","status":"LIVE","version":"Pure API v8 FINAL FIG","project":"FIG","base_url":"https://lonma-orbit-24qw.onrender.com","master_api_key":"lonma_api_key_12345","endpoints":["GET /api/health","GET /api/members","POST /api/register","POST /api/login","PUT /api/members/<id>","DELETE /api/members/<id>","GET /api/stats"]})

@app.route("/api/health")
def health():
    conn=get_db(); c=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"status":"ok","project":"FIG","total":c})

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    if request.method=='OPTIONS': return '',200
    conn=get_db(); users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); conn.close()
    data=[{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"project":u["project"],"month_year_joined":u["month_year_joined"],"email":u["email"],"phone":u["phone"],"role":u["role"],"family":{"father_id":u["father_id"],"mother_id":u["mother_id"],"guardian_id":u["guardian_id"],"spouse_id":u["spouse_id"]},"kids":{"kid1":u["kid1"],"kid2":u["kid2"],"kid3":u["kid3"],"kid4":u["kid4"],"kid5":u["kid5"]}} for u in users]
    return jsonify({"project":"FIG","total":len(data),"members":data})

@app.route("/api/register", methods=["POST","OPTIONS"])
def register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"email,password required"}),400
    try:
        key=f"lonma_{secrets.token_hex(16)}"; conn=get_db()
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (d.get("staff_no",f"FIG/{secrets.token_hex(2).upper()}"),d.get("full_names",""),"FIG",d.get("month_year_joined",""),d["email"],generate_password_hash(d["password"]),d.get("role","Member"),d.get("phone",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),key))
        conn.commit(); u=conn.execute("SELECT id,staff_no,full_names,email,project,api_key FROM users WHERE email=?",(d["email"],)).fetchone(); conn.close()
        return jsonify({"message":"FIG member registered","member":dict(u)}),201
    except Exception as e: return jsonify({"error":str(e)}),400

@app.route("/api/login", methods=["POST","OPTIONS"])
def login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True); conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); conn.close()
    if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
    return jsonify({"message":"Login success","project":"FIG","member":{"id":u["id"],"full_names":u["full_names"],"email":u["email"],"api_key":u["api_key"]}})

@app.route("/api/members/<int:id>", methods=["PUT","DELETE","OPTIONS"])
@need_key
def modify(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    if request.method=="DELETE": conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return jsonify({"message":f"Deleted {id}"})
    d=request.get_json(silent=True); fields=[]; vals=[]
    for k in ["staff_no","full_names","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]:
        if k in d: fields.append(f"{k}=?"); vals.append(d[k])
    vals.append(id); conn.execute(f"UPDATE users SET {', '.join(fields)}, project='FIG' WHERE id=?",vals); conn.commit(); conn.close()
    return jsonify({"message":"Updated FIG","id":id})

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    conn=get_db(); total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"project":"FIG","total_members":total})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
