from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets, time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "lonma-fig-professional-2026-fixed"
DB = "lonma.db"

def get_db():
    # FIX 1: Timeout + WAL mode to prevent locked error
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return conn

def init_db():
    conn = get_db()
    try:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT,
        email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT,
        father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT,
        kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT,
        api_key TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
        conn.execute("UPDATE users SET project='FIG' WHERE project!='FIG'")
    except: pass
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("FIG/001","Administrator","FIG","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","FATHER_001","MOTHER_001","22400966","23601476","42107914","111041990","","","","lonma_api_key_12345"))
    conn.close()

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
        conn=get_db()
        try:
            u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone()
        finally:
            conn.close()
        if not u: return jsonify({"error":"Invalid key"}),401
        return f(*a,**k)
    return d

@app.route("/favicon.ico")
def favicon(): return "",204

# ====== PROFESSIONAL UI (Same as v11) ======
PRO_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',system-ui,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6}
.nav{background:#fff;border-bottom:1px solid #e2e8f0;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:50}
.nav-brand{display:flex;align-items:center;gap:12px}.logo{width:40px;height:40px;background:linear-gradient(135deg,#0ea5e9,#0284c7);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:18px}
.brand-text b{font-size:18px;color:#0f172a}.brand-text span{font-size:12px;color:#64748b;display:block}
.nav-links a{color:#475569;text-decoration:none;font-weight:500;font-size:14px;margin-left:20px;padding:8px 14px;border-radius:8px}.nav-links a:hover{background:#f1f5f9}.nav-links a.active{background:#0ea5e9;color:#fff}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;padding:48px 24px}.hero-inner{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
.hero h1{font-size:40px;font-weight:700;line-height:1.1;margin-bottom:12px}.hero h1 span{background:linear-gradient(90deg,#38bdf8,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:#94a3b8;font-size:16px;margin-bottom:24px}.stats-row{display:flex;gap:12px;margin-top:20px}
.stat-card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(10px);padding:16px 20px;border-radius:12px;min-width:140px}
.stat-card b{font-size:28px;display:block;color:#fff}.stat-card span{font-size:12px;color:#94a3b8;text-transform:uppercase}
.container{max-width:1100px;margin:0 auto;padding:32px 24px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.btn{padding:10px 18px;border-radius:10px;font-weight:600;font-size:14px;border:none;cursor:pointer;display:inline-flex;align-items:center;gap:8px;text-decoration:none}
.btn-primary{background:#0ea5e9;color:#fff}.btn-dark{background:#0f172a;color:#fff}
input{width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:10px;font-size:14px;background:#fff}input:focus{outline:none;border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.1)}
label{font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block}
table{width:100%;border-collapse:collapse}th{font-size:11px;text-transform:uppercase;color:#64748b;padding:12px;text-align:left;background:#f8fafc;border-bottom:1px solid #e2e8f0}td{padding:14px 12px;border-bottom:1px solid #f1f5f9;font-size:14px}
.endpoint{background:#f8fafc;border:1px solid #e2e8f0;padding:14px;border-radius:10px;margin:10px 0;font-family:monospace;font-size:13px;display:flex;justify-content:space-between}
.method{padding:4px 8px;border-radius:6px;font-size:11px;font-weight:700;color:#fff}.GET{background:#10b981}.POST{background:#0ea5e9}.PUT{background:#f59e0b}.DELETE{background:#ef4444}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}@media(max-width:768px){.hero-inner{grid-template-columns:1fr}.grid-2{grid-template-columns:1fr}}
</style>
"""

HOME_PRO = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA FIG Professional</title>{PRO_CSS}</head><body>
<div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a><a href="/login">Login</a></div></div>
<div class="hero"><div class="hero-inner"><div><div style="display:inline-flex;background:rgba(56,189,248,.15);border:1px solid rgba(56,189,248,.3);color:#38bdf8;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:16px">● SYSTEM LIVE • FIG PROJECT • v12 FIXED</div><h1>Professional <span>Welfare Management</span> System</h1><p>Enterprise-grade member management for FIG Project. Secure, scalable, and built for welfare operations.</p><div style="display:flex;gap:10px"><a href="/dashboard" class="btn btn-primary">→ Open Dashboard</a><a href="/register" class="btn" style="background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2)">+ New Member</a></div><div class="stats-row"><div class="stat-card"><b id="total">-</b><span>Total Members</span></div><div class="stat-card"><b>FIG</b><span>Active Project</span></div><div class="stat-card"><b>FIXED</b><span>DB Lock</span></div></div></div>
<div><div class="card" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.1)"><h3 style="color:#fff;margin-bottom:16px;font-size:14px">System Status</h3><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.1)"><span style="color:#94a3b8;font-size:13px">Base URL</span><span style="color:#fff;font-size:11px">lonma-orbit-24qw.onrender.com</span></div><div style="display:flex;justify-content:space-between;padding:10px 0"><span style="color:#94a3b8;font-size:13px">Status</span><span style="background:#10b981;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">● LIVE v12</span></div></div></div></div></div>
<div class="container"><div class="card"><h3>📋 Complete API</h3><div class="endpoint"><span><span class="method GET">GET</span> /api/health</span><span>Health check</span></div><div class="endpoint"><span><span class="method GET">GET</span> /api/members</span><span>List FIG</span></div><div class="endpoint"><span><span class="method POST">POST</span> /api/register</span><span>Create</span></div><div class="endpoint"><span><span class="method DELETE">DELETE</span> /api/members/ID</span><span>Delete - FIXED</span></div></div></div>
<script>fetch('/api/stats?api_key=lonma_api_key_12345').then(r=>r.json()).then(d=>document.getElementById('total').innerText=d.total_members||0)</script></body></html>"""

LOGIN_PRO = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login FIG</title>{PRO_CSS}</head><body style="background:#f8fafc;display:flex;justify-content:center;align-items:center;min-height:100vh"><div class="card" style="max-width:400px;width:90%"><div style="text-align:center;margin-bottom:24px"><div class="logo" style="margin:0 auto 12px">F</div><h2>Welcome back</h2><p style="color:#64748b;font-size:13px">FIG Welfare System</p></div><label>Email</label><input id="email" value="admin@lonma.com"><label style="margin-top:12px">Password</label><input id="pass" type="password" value="admin123"><button class="btn btn-dark" style="width:100%;margin-top:20px;justify-content:center" onclick="login()">Sign In →</button><p id="msg" style="font-size:12px;margin-top:12px;color:#ef4444"></p></div>
<script>async function login(){{let r=await fetch('/api/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:pass.value}})}});let d=await r.json();if(d.member){{localStorage.setItem('api_key',d.member.api_key);location.href='/dashboard';}}else{{msg.innerText=d.error;}}}}</script></body></html>"""

REGISTER_PRO = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register FIG</title>{PRO_CSS}</head><body><div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div><div class="container"><div class="card"><h2>Register New Member</h2><div class="grid-2"><div><label>Staff No</label><input id="staff_no" placeholder="FIG/002"></div><div><label>Full Names *</label><input id="full_names"></div></div><div class="grid-2" style="margin-top:16px"><div><label>Email *</label><input id="email"></div><div><label>Password *</label><input id="password"></div></div><div class="grid-2" style="margin-top:16px"><div><label>Phone</label><input id="phone"></div><div><label>Month/Year</label><input id="month_year_joined" placeholder="Oct 2026"></div></div><h3 style="font-size:14px;margin:24px 0 12px">Family IDs</h3><div class="grid-2"><div><input id="father_id" placeholder="Father ID"></div><div><input id="mother_id" placeholder="Mother ID"></div></div><div class="grid-2" style="margin-top:12px"><div><input id="guardian_id" placeholder="Guardian 22400966"></div><div><input id="spouse_id" placeholder="Spouse 23601476"></div></div><h3 style="font-size:14px;margin:24px 0 12px">Kids Birth Certs</h3><div class="grid-2"><div><input id="kid1" placeholder="Kid1 42107914"></div><div><input id="kid2" placeholder="Kid2 111041990"></div></div><div class="grid-2" style="margin-top:12px"><div><input id="kid3" placeholder="Kid3"></div><div><input id="kid4" placeholder="Kid4"></div></div><input id="kid5" placeholder="Kid5" style="margin-top:12px"><button class="btn btn-primary" style="width:100%;margin-top:24px;justify-content:center;padding:14px" onclick="reg()">+ Register to FIG</button><p id="msg" style="margin-top:12px"></p></div></div>
<script>async function reg(){{let d={{}};["staff_no","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>d[k]=document.getElementById(k).value);let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});let j=await r.json();msg.innerText=JSON.stringify(j);if(r.ok)location.href='/dashboard';}}</script></body></html>"""

DASHBOARD_PRO = f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members FIG</title>{PRO_CSS}</head><body><div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div></div><div class="container"><div style="display:flex;justify-content:space-between;margin-bottom:20px"><div><h2>FIG Members</h2><p style="color:#64748b;font-size:13px"><span id="count">0</span> members</p></div><a href="/register" class="btn btn-primary">+ New Member</a></div><div class="card" style="padding:0;overflow:hidden"><div style="padding:16px;border-bottom:1px solid #e2e8f0"><input id="search" placeholder="🔍 Search..." style="max-width:320px" oninput="filter()"></div><div style="overflow:auto"><table id="tbl"></table></div></div></div>
<script>
let allData=[];
async function load(){{let k=localStorage.getItem('api_key')||'lonma_api_key_12345';let r=await fetch('/api/members?api_key='+k);let d=await r.json();allData=d.members;count.innerText=d.total;render(d.members);}}
function render(list){{let h='<tr><th>Member</th><th>Contact</th><th>Family</th><th>Kids</th><th>Action</th></tr>';list.forEach(m=>{{h+=`<tr><td><b>${{m.full_names}}</b><br><span style="color:#64748b;font-size:12px">${{m.staff_no}}</span></td><td style="font-size:12px">${{m.email}}<br>${{m.phone||''}}</td><td style="font-size:11px">F:${{m.family.father_id||'-'}} M:${{m.family.mother_id||'-'}}<br>G:${{m.family.guardian_id||'-'}} S:${{m.family.spouse_id||'-'}}</td><td style="font-size:12px">${{Object.values(m.kids).filter(Boolean).join(', ')||'-'}}</td><td><button onclick="del(${{m.id}})" style="background:#fff;border:1px solid #fee2e2;color:#ef4444;padding:6px 12px;border-radius:8px;font-size:12px;cursor:pointer">Delete</button></td></tr>`}});tbl.innerHTML=h;}}
function filter(){{let q=search.value.toLowerCase();render(allData.filter(m=>(m.full_names+m.staff_no+m.email).toLowerCase().includes(q)));}}
async function del(id){{if(!confirm('Delete FIG member '+id+'? This is permanent.'))return;let k=localStorage.getItem('api_key')||'lonma_api_key_12345';try{{let r=await fetch('/api/members/'+id+'?api_key='+k,{{method:'DELETE'}});let j=await r.json();if(!r.ok)throw j; alert('Deleted successfully'); load();}}catch(e){{alert('Error: '+(e.error||JSON.stringify(e)));}}}}
load();
</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HOME_PRO)
@app.route("/login")
def login_p(): return render_template_string(LOGIN_PRO)
@app.route("/register")
def reg_p(): return render_template_string(REGISTER_PRO)
@app.route("/dashboard")
def dash_p(): return render_template_string(DASHBOARD_PRO)

@app.route("/api/health")
def health():
    conn=get_db()
    try:
        c=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return jsonify({"status":"ok","project":"FIG","version":"v12 PROFESSIONAL FIXED","total_members":c,"db_status":"WAL mode, timeout 10s"})
    finally:
        conn.close()

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
        data=[{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"project":u["project"],"month_year_joined":u["month_year_joined"],"email":u["email"],"phone":u["phone"],"role":u["role"],"family":{"father_id":u["father_id"],"mother_id":u["mother_id"],"guardian_id":u["guardian_id"],"spouse_id":u["spouse_id"]},"kids":{"kid1":u["kid1"],"kid2":u["kid2"],"kid3":u["kid3"],"kid4":u["kid4"],"kid5":u["kid5"]}} for u in users]
        return jsonify({"project":"FIG","total":len(data),"members":data})
    finally:
        conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"email,password required"}),400
    conn=get_db()
    try:
        key=f"lonma_{secrets.token_hex(16)}"
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (d.get("staff_no",f"FIG/{secrets.token_hex(2).upper()}"),d.get("full_names",""),"FIG",d.get("month_year_joined",""),d["email"],generate_password_hash(d["password"]),d.get("role","Member"),d.get("phone",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),key))
        conn.execute("COMMIT")
        u=conn.execute("SELECT * FROM users WHERE email=?",(d["email"],)).fetchone()
        return jsonify({"message":"FIG member registered","member":{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"email":u["email"],"api_key":u["api_key"]}}),201
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),400
    finally:
        conn.close()

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    conn=get_db()
    try:
        u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid credentials"}),401
        return jsonify({"message":"Login success","project":"FIG","member":{"id":u["id"],"full_names":u["full_names"],"email":u["email"],"api_key":u["api_key"],"role":u["role"]}})
    finally:
        conn.close()

# FIXED DELETE - WITH RETRY AND PROPER CLOSE
@app.route("/api/members/<int:id>", methods=["PUT","DELETE","OPTIONS"])
@need_key
def modify(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        if request.method=="DELETE":
            # FIX: Retry logic for locked DB
            for attempt in range(3):
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute("DELETE FROM users WHERE id=?",(id,))
                    conn.execute("COMMIT")
                    return jsonify({"message":f"FIG Member {id} deleted successfully"})
                except sqlite3.OperationalError as e:
                    if "locked" in str(e) and attempt < 2:
                        try: conn.execute("ROLLBACK")
                        except: pass
                        time.sleep(0.5)
                        continue
                    else:
                        try: conn.execute("ROLLBACK")
                        except: pass
                        raise e
        
        # PUT - Update
        d=request.get_json(silent=True)
        fields=[]; vals=[]
        for k in ["staff_no","full_names","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]:
            if k in d: fields.append(f"{k}=?"); vals.append(d[k])
        if not fields: return jsonify({"error":"No fields"}),400
        vals.append(id)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(f"UPDATE users SET {', '.join(fields)}, project='FIG' WHERE id=?",vals)
        conn.execute("COMMIT")
        return jsonify({"message":"Updated FIG","id":id})
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":f"Database error: {str(e)}"}),500
    finally:
        conn.close()

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return jsonify({"project":"FIG","total_members":total,"system":"PROFESSIONAL v12 FIXED"})
    finally:
        conn.close()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
