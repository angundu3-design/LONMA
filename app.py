from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "lonma-fig-professional-2026"
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
    try: conn.execute("UPDATE users SET project='FIG' WHERE project!='FIG'")
    except: pass
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("FIG/001","Administrator","FIG","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","FATHER_001","MOTHER_001","22400966","23601476","42107914","111041990","","","","lonma_api_key_12345"))
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

# ========= PROFESSIONAL UI =========

PRO_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',system-ui,sans-serif;background:#f8fafc;color:#1e293b;line-height:1.6}
.nav{background:#fff;border-bottom:1px solid #e2e8f0;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:50;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.nav-brand{display:flex;align-items:center;gap:12px}.logo{width:40px;height:40px;background:linear-gradient(135deg,#0ea5e9,#0284c7);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700;font-size:18px}
.brand-text b{font-size:18px;color:#0f172a}.brand-text span{font-size:12px;color:#64748b;display:block;letter-spacing:.5px}
.nav-links a{color:#475569;text-decoration:none;font-weight:500;font-size:14px;margin-left:20px;padding:8px 14px;border-radius:8px;transition:.2s}.nav-links a:hover{background:#f1f5f9;color:#0f172a}.nav-links a.active{background:#0ea5e9;color:#fff}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;padding:48px 24px}.hero-inner{max-width:1100px;margin:0 auto;display:grid;grid-template-columns:1.2fr .8fr;gap:40px;align-items:center}
.hero h1{font-size:40px;font-weight:700;line-height:1.1;margin-bottom:12px}.hero h1 span{background:linear-gradient(90deg,#38bdf8,#22d3ee);-webkit-background-clip:text;-webkit-text-fill-color:transparent}
.hero p{color:#94a3b8;font-size:16px;margin-bottom:24px}.stats-row{display:flex;gap:12px;margin-top:20px}
.stat-card{background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);backdrop-filter:blur(10px);padding:16px 20px;border-radius:12px;min-width:140px}
.stat-card b{font-size:28px;display:block;color:#fff}.stat-card span{font-size:12px;color:#94a3b8;text-transform:uppercase;letter-spacing:.5px}
.container{max-width:1100px;margin:0 auto;padding:32px 24px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.btn{padding:10px 18px;border-radius:10px;font-weight:600;font-size:14px;border:none;cursor:pointer;display:inline-flex;align-items:center;gap:8px;text-decoration:none;transition:.2s}
.btn-primary{background:#0ea5e9;color:#fff}.btn-primary:hover{background:#0284c7}.btn-dark{background:#0f172a;color:#fff}.btn-dark:hover{background:#1e293b}.btn-outline{background:#fff;border:1px solid #e2e8f0;color:#475569}.btn-outline:hover{background:#f8fafc}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}
@media(max-width:768px){.hero-inner{grid-template-columns:1fr}.grid-2,.grid-3{grid-template-columns:1fr}.nav-links{display:none}}
.endpoint{background:#f8fafc;border:1px solid #e2e8f0;padding:14px;border-radius:10px;margin:10px 0;font-family:monospace;font-size:13px;display:flex;justify-content:space-between;align-items:center}
.method{padding:4px 8px;border-radius:6px;font-size:11px;font-weight:700;color:#fff}.GET{background:#10b981}.POST{background:#0ea5e9}.PUT{background:#f59e0b}.DELETE{background:#ef4444}
.badge{background:#f1f5f9;padding:4px 10px;border-radius:20px;font-size:12px;font-weight:500;color:#475569;border:1px solid #e2e8f0}
input{width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:10px;font-size:14px;transition:.2s;background:#fff}input:focus{outline:none;border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.1)}
label{font-size:12px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block}
table{width:100%;border-collapse:collapse}th{font-size:11px;text-transform:uppercase;letter-spacing:.5px;color:#64748b;padding:12px;text-align:left;background:#f8fafc;border-bottom:1px solid #e2e8f0}td{padding:14px 12px;border-bottom:1px solid #f1f5f9;font-size:14px}
</style>
"""

HOME_PRO = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA FIG - Professional Welfare System</title>{PRO_CSS}</head><body>
<div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a><a href="/login">Login</a></div></div>
<div class="hero"><div class="hero-inner"><div><div style="display:inline-flex;background:rgba(56,189,248,.15);border:1px solid rgba(56,189,248,.3);color:#38bdf8;padding:6px 12px;border-radius:20px;font-size:12px;font-weight:600;margin-bottom:16px">● SYSTEM LIVE • FIG PROJECT</div><h1>Professional <span>Welfare Management</span> System</h1><p>Enterprise-grade member management for FIG Project. Secure, scalable, and built for welfare operations with complete family linkage.</p><div style="display:flex;gap:10px"><a href="/dashboard" class="btn btn-primary">→ Open Dashboard</a><a href="/register" class="btn" style="background:rgba(255,255,255,.1);color:#fff;border:1px solid rgba(255,255,255,.2)">+ New Member</a></div><div class="stats-row"><div class="stat-card"><b id="total">2</b><span>Total Members</span></div><div class="stat-card"><b>FIG</b><span>Active Project</span></div><div class="stat-card"><b>100%</b><span>Uptime</span></div></div></div>
<div><div class="card" style="background:rgba(255,255,255,.05);border-color:rgba(255,255,255,.1);backdrop-filter:blur(20px)"><h3 style="color:#fff;margin-bottom:16px;font-size:14px">System Status</h3><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.1)"><span style="color:#94a3b8;font-size:13px">Base URL</span><span style="color:#fff;font-size:12px">lonma-orbit-24qw.onrender.com</span></div><div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px solid rgba(255,255,255,.1)"><span style="color:#94a3b8;font-size:13px">Project</span><span class="badge" style="background:#10b981;color:#fff;border:none">FIG • Production</span></div><div style="display:flex;justify-content:space-between;padding:10px 0"><span style="color:#94a3b8;font-size:13px">API Key</span><span style="color:#38bdf8;font-size:11px">lonma_api_key_12345</span></div></div></div></div></div>
<div class="container"><div class="grid-2"><div class="card"><h3 style="font-size:16px;margin-bottom:4px">📋 Complete API</h3><p style="color:#64748b;font-size:13px;margin-bottom:16px">RESTful endpoints for integration</p>
<div class="endpoint"><span><span class="method GET">GET</span> /api/health</span><span style="color:#64748b">Health check</span></div>
<div class="endpoint"><span><span class="method GET">GET</span> /api/members</span><span style="color:#64748b">List FIG members</span></div>
<div class="endpoint"><span><span class="method POST">POST</span> /api/register</span><span style="color:#64748b">Create member</span></div>
<div class="endpoint"><span><span class="method POST">POST</span> /api/login</span><span style="color:#64748b">Authentication</span></div>
<div class="endpoint"><span><span class="method PUT">PUT</span> /api/members/ID</span><span style="color:#64748b">Update</span></div>
<div class="endpoint"><span><span class="method DELETE">DELETE</span> /api/members/ID</span><span style="color:#64748b">Delete</span></div>
</div><div class="card"><h3 style="font-size:16px;margin-bottom:4px">🎯 WELFARE_DATA Schema</h3><p style="color:#64748b;font-size:13px;margin-bottom:16px">Complete family linkage system</p>
<div style="background:#f8fafc;border:1px solid #e2e8f0;border-radius:10px;padding:16px;font-size:12px;line-height:1.8"><b style="color:#0f172a">Core:</b> staff_no, full_names, project=FIG, month_year_joined, email, phone<br><b style="color:#0f172a">Family IDs:</b> father_id, mother_id, guardian_id (22400966), spouse_id (23601476)<br><b style="color:#0f172a">Children:</b> kid1 (42107914), kid2 (111041990), kid3, kid4, kid5 - Birth Certificates<br><b style="color:#0f172a">Auth:</b> role, api_key, password (hashed)</div>
<div style="margin-top:16px;padding:12px;background:#f0f9ff;border:1px solid #bae6fd;border-radius:8px;font-size:12px"><b style="color:#0284c7">Default Admin:</b> admin@lonma.com / admin123</div>
</div></div></div>
<script>fetch('/api/stats?api_key=lonma_api_key_12345').then(r=>r.json()).then(d=>document.getElementById('total').innerText=d.total_members||0)</script>
</body></html>
"""

LOGIN_PRO = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login - LONMA FIG</title>{PRO_CSS}</head><body style="background:#f8fafc;display:flex;justify-content:center;align-items:center;min-height:100vh">
<div class="card" style="max-width:400px;width:90%"><div style="text-align:center;margin-bottom:24px"><div class="logo" style="margin:0 auto 12px">F</div><h2 style="font-size:20px">Welcome back</h2><p style="color:#64748b;font-size:13px">Sign in to FIG Welfare System</p></div><label>Email Address</label><input id="email" value="admin@lonma.com"><label style="margin-top:12px">Password</label><input id="pass" type="password" value="admin123"><button class="btn btn-dark" style="width:100%;margin-top:20px;justify-content:center" onclick="login()">Sign In →</button><p id="msg" style="font-size:12px;margin-top:12px;color:#ef4444"></p><div style="text-align:center;margin-top:20px;font-size:13px"><a href="/" style="color:#64748b;text-decoration:none">← Back to overview</a></div></div>
<script>
async function login(){{ let r=await fetch('/api/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:pass.value}})}}); let d=await r.json(); if(d.member){{localStorage.setItem('api_key',d.member.api_key); location.href='/dashboard';}} else {{msg.innerText=d.error||'Invalid credentials';}} }}
</script></body></html>
"""

REGISTER_PRO = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register Member - LONMA FIG</title>{PRO_CSS}</head><body>
<div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div>
<div class="container"><div class="card"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:24px"><div><h2 style="font-size:20px">Register New Member</h2><p style="color:#64748b;font-size:13px">Add a new FIG welfare member with complete family linkage</p></div><span class="badge">Project: FIG</span></div>
<div class="grid-2"><div><label>Staff Number</label><input id="staff_no" placeholder="FIG/002"></div><div><label>Full Names *</label><input id="full_names" placeholder="John Doe Kamau"></div></div>
<div class="grid-2" style="margin-top:16px"><div><label>Email Address *</label><input id="email" placeholder="john@lonma.com"></div><div><label>Password *</label><input id="password" placeholder="Secure password"></div></div>
<div class="grid-2" style="margin-top:16px"><div><label>Phone Number</label><input id="phone" placeholder="0700 000 000"></div><div><label>Month / Year Joined</label><input id="month_year_joined" placeholder="Oct 2026"></div></div>
<h3 style="font-size:14px;margin:24px 0 12px;color:#0f172a">Family Linkage</h3>
<div class="grid-2"><div><label>Father ID Number</label><input id="father_id"></div><div><label>Mother ID Number</label><input id="mother_id"></div></div>
<div class="grid-2" style="margin-top:12px"><div><label>Guardian ID (22400966)</label><input id="guardian_id"></div><div><label>Spouse ID (23601476)</label><input id="spouse_id"></div></div>
<h3 style="font-size:14px;margin:24px 0 12px;color:#0f172a">Children - Birth Certificates</h3>
<div class="grid-2"><div><label>Child 1 - 42107914</label><input id="kid1"></div><div><label>Child 2 - 111041990</label><input id="kid2"></div></div>
<div class="grid-2" style="margin-top:12px"><div><label>Child 3</label><input id="kid3"></div><div><label>Child 4</label><input id="kid4"></div></div>
<div style="margin-top:12px"><label>Child 5</label><input id="kid5"></div>
<button class="btn btn-primary" style="width:100%;margin-top:24px;justify-content:center;padding:14px" onclick="reg()">+ Register Member to FIG Project</button><p id="msg" style="margin-top:12px;font-size:13px"></p>
</div></div>
<script>
async function reg(){{ let d={{}}; ["staff_no","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>d[k]=document.getElementById(k).value); let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}}); let j=await r.json(); msg.innerText=JSON.stringify(j); if(r.ok){{ alert('Member registered to FIG!'); location.href='/dashboard'; }} }}
</script></body></html>
"""

DASHBOARD_PRO = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - LONMA FIG</title>{PRO_CSS}</head><body>
<div class="nav"><div class="nav-brand"><div class="logo">F</div><div class="brand-text"><b>LONMA FIG</b><span>WELFARE MANAGEMENT</span></div></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a><a href="#" onclick="localStorage.clear();location.href='/login'">Logout</a></div></div>
<div class="container"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:20px"><div><h2 style="font-size:22px">FIG Members</h2><p style="color:#64748b;font-size:13px"><span id="count">0</span> members in FIG Project</p></div><a href="/register" class="btn btn-primary">+ New Member</a></div>
<div class="card" style="padding:0;overflow:hidden"><div style="padding:16px;border-bottom:1px solid #e2e8f0;display:flex;gap:10px"><input id="search" placeholder="🔍 Search by name, staff no, email..." style="max-width:320px" oninput="filter()"><select id="filterRole" style="max-width:150px;padding:10px;border:1px solid #e2e8f0;border-radius:10px"><option>All Projects</option><option selected>FIG</option></select></div><div style="overflow:auto"><table id="tbl"></table></div></div></div>
<script>
let allData=[];
async function load(){{ let key=localStorage.getItem('api_key')||'lonma_api_key_12345'; let r=await fetch('/api/members?api_key='+key); let d=await r.json(); allData=d.members; count.innerText=d.total; render(d.members); }}
function render(list){{ let h='<tr><th>Member</th><th>Contact</th><th>Family Linkage</th><th>Children</th><th></th></tr>'; list.forEach(m=>{{h+=`<tr><td><div style="display:flex;gap:10px;align-items:center"><div style="width:36px;height:36px;background:#f1f5f9;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:12px">${{m.full_names.charAt(0)}}</div><div><div style="font-weight:600">${{m.full_names}}</div><div style="font-size:12px;color:#64748b">${{m.staff_no}} • ${{m.project}}</div></div></div></td><td><div style="font-size:13px">${{m.email}}</div><div style="font-size:12px;color:#64748b">${{m.phone||''}} • ${{m.month_year_joined||''}}</div></td><td style="font-size:12px;line-height:1.6">F: ${{m.family.father_id||'-'}}<br>M: ${{m.family.mother_id||'-'}}<br>G: ${{m.family.guardian_id||'-'}} S: ${{m.family.spouse_id||'-'}}</td><td style="font-size:12px">${{Object.values(m.kids).filter(Boolean).join(', ')||'-'}}</td><td><button onclick="del(${{m.id}})" style="background:#fff;border:1px solid #fee2e2;color:#ef4444;padding:6px 12px;border-radius:8px;font-size:12px;font-weight:600;cursor:pointer">Delete</button></td></tr>`}}); tbl.innerHTML=h; }}
function filter(){{ let q=search.value.toLowerCase(); render(allData.filter(m=> (m.full_names+m.staff_no+m.email).toLowerCase().includes(q) )); }}
async function del(id){{ if(!confirm('Delete FIG member '+id+'?')) return; let k=localStorage.getItem('api_key')||'lonma_api_key_12345'; await fetch('/api/members/'+id+'?api_key='+k,{{method:'DELETE'}}); load(); }} load();
</script></body></html>
"""

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
    conn=get_db(); c=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"status":"ok","project":"FIG","version":"v11 PROFESSIONAL","total_members":c,"timestamp":datetime.now().isoformat()})

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
        conn.commit(); u=conn.execute("SELECT * FROM users WHERE email=?",(d["email"],)).fetchone(); conn.close()
        return jsonify({"message":"FIG member registered","member":{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"email":u["email"],"api_key":u["api_key"]}}),201
    except Exception as e: return jsonify({"error":str(e)}),400

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True); conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); conn.close()
    if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
    return jsonify({"message":"Login success","project":"FIG","member":{"id":u["id"],"full_names":u["full_names"],"email":u["email"],"api_key":u["api_key"],"role":u["role"]}})

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
    if request.method=='OPTIONS': return '',200
    conn=get_db(); total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"project":"FIG","total_members":total,"system":"PROFESSIONAL v11"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
