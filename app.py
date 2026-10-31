from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from datetime import datetime

app = Flask(__name__)
app.secret_key = "lonma-fig-2026-complete"
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
    try: conn.execute("UPDATE users SET project='FIG' WHERE project='PWANI' OR project='pwani'")
    except: pass
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("FIG/001","Admin User","FIG","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","FATHER_001","MOTHER_001","22400966","23601476","42107914","111041990","","","","lonma_api_key_12345"))
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

# ========= FRONTEND TEMPLATES (COMPLETE UI) =========

BASE_CSS = """
*{box-sizing:border-box}body{font-family:system-ui,sans-serif;background:#0f172a;color:#e2e8f0;margin:0}
.nav{background:#1e293b;padding:12px 20px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0}
.nav a{color:#38bdf8;text-decoration:none;margin:0 8px;font-weight:600}
.card{max-width:900px;margin:20px auto;background:#1e293b;border-radius:16px;padding:24px;box-shadow:0 10px 30px rgba(0,0,0,.3)}
.btn{background:#38bdf8;color:#0f172a;padding:10px 18px;border-radius:8px;display:inline-block;font-weight:bold;margin:6px;text-decoration:none;border:none;cursor:pointer}
.btn-green{background:#4ade80}.btn-red{background:#f87171}
input,select{width:100%;padding:10px;border-radius:8px;border:1px solid #334155;background:#0f172a;color:#fff;margin:6px 0}
.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px} .endpoint{background:#0f172a;padding:12px;border-radius:8px;margin:8px 0;font-family:monospace;font-size:13px;border-left:4px solid #38bdf8}
.badge{background:#334155;padding:4px 10px;border-radius:20px;font-size:12px}
"""

HOME_PAGE = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA FIG - Complete</title><style>{BASE_CSS}</style></head><body>
<div class="nav"><div><b style="color:#38bdf8">LONMA FIG</b> WELFARE</div><div><a href="/">Home</a><a href="/login">Login</a><a href="/register">Register</a><a href="/dashboard">Dashboard</a></div></div>
<div class="card">
<h1 style="color:#38bdf8">🚀 LONMA FIG WELFARE SYSTEM</h1>
<p><span style="color:#4ade80">● LIVE</span> Complete System v10 - FIG Project | <span class="badge">lonma_api_key_12345</span> <span class="badge">Project: FIG</span></p>
<p><b>Base URL:</b> https://lonma-orbit-24qw.onrender.com</p>
<div class="grid"><div style="background:#0f172a;padding:16px;border-radius:12px;text-align:center"><b id="total" style="font-size:28px;color:#38bdf8">-</b><br>Total FIG Members</div><div style="background:#0f172a;padding:16px;border-radius:12px;text-align:center"><b style="font-size:28px;color:#4ade80">FIG</b><br>Project Active</div></div>
<div style="margin-top:20px"><a class="btn" href="/login">🔐 Admin Login</a><a class="btn btn-green" href="/register">➕ Register Member</a><a class="btn" style="background:#fb923c" href="/dashboard">📊 Dashboard</a></div>
<h3>📋 Complete API Endpoints</h3>
<div class="endpoint">GET /api/health → Health check</div>
<div class="endpoint">GET /api/members?api_key=KEY → Get all FIG members</div>
<div class="endpoint">POST /api/register → full_names,email,password,father_id,mother_id,guardian_id,spouse_id,kid1-kid5</div>
<div class="endpoint">POST /api/login → email,password</div>
<div class="endpoint">PUT /api/members/ID → Update</div>
<div class="endpoint">DELETE /api/members/ID → Delete</div>
<p style="color:#94a3b8;font-size:12px;margin-top:20px">Default Admin: admin@lonma.com / admin123 | WELFARE_DATA: staff_no, full_names, project=FIG, month_year_joined, phone, father_id, mother_id, guardian_id, spouse_id, kid1-5</p>
</div>
<script>fetch('/api/stats?api_key=lonma_api_key_12345').then(r=>r.json()).then(d=>document.getElementById('total').innerText=d.total_members||0)</script>
</body></html>
"""

LOGIN_PAGE = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login FIG</title><style>{BASE_CSS} body{{display:flex;justify-content:center;align-items:center;min-height:100vh}} .card{{max-width:400px;width:90%}}</style></head><body>
<div class="card"><h2>🔐 FIG Login</h2><input id="email" value="admin@lonma.com" placeholder="Email"><input id="pass" type="password" value="admin123" placeholder="Password"><button class="btn" style="width:100%" onclick="login()">Login</button><p id="msg"></p><a href="/">← Home</a></div>
<script>
async function login(){{ let r=await fetch('/api/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:pass.value}})}}); let d=await r.json(); msg.innerText=JSON.stringify(d); if(d.member){{localStorage.setItem('api_key',d.member.api_key); location.href='/dashboard';}} }}
</script></body></html>
"""

REGISTER_PAGE = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register FIG</title><style>{BASE_CSS} .card{{max-width:700px}}</style></head><body>
<div class="nav"><a href="/" style="color:#38bdf8">← Home</a><a href="/dashboard">Dashboard</a></div>
<div class="card"><h2>➕ Register FIG Member - WELFARE_DATA</h2>
<div class="grid"><div><label>Staff No</label><input id="staff_no" placeholder="FIG/002"></div><div><label>Full Names *</label><input id="full_names" placeholder="John Doe"></div></div>
<div class="grid"><div><label>Email *</label><input id="email"></div><div><label>Password *</label><input id="password"></div></div>
<div class="grid"><div><label>Phone</label><input id="phone"></div><div><label>Month/Year Joined</label><input id="month_year_joined" placeholder="Oct 2026"></div></div>
<h4>Family IDs</h4><div class="grid"><div><input id="father_id" placeholder="Father ID"></div><div><input id="mother_id" placeholder="Mother ID"></div></div>
<div class="grid"><div><input id="guardian_id" placeholder="Guardian ID 22400966"></div><div><input id="spouse_id" placeholder="Spouse ID 23601476"></div></div>
<h4>Kids Birth Certificates</h4><div class="grid"><div><input id="kid1" placeholder="Kid1 42107914"></div><div><input id="kid2" placeholder="Kid2 111041990"></div></div><div class="grid"><div><input id="kid3" placeholder="Kid3"></div><div><input id="kid4" placeholder="Kid4"></div></div><input id="kid5" placeholder="Kid5">
<button class="btn btn-green" style="width:100%" onclick="reg()">Register to FIG</button><p id="msg"></p></div>
<script>
async function reg(){{ let d={{}}; ["staff_no","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>d[k]=document.getElementById(k).value); let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}}); let j=await r.json(); msg.innerText=JSON.stringify(j); if(r.ok) alert('Registered to FIG!'); }}
</script></body></html>
"""

DASHBOARD_PAGE = f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard FIG</title><style>{BASE_CSS} table{{width:100%;border-collapse:collapse;font-size:12px}} th,td{{border:1px solid #334155;padding:8px}} th{{background:#0f172a}}</style></head><body>
<div class="nav"><b>FIG DASHBOARD</b><div><a href="/">Home</a><a href="/register">+ Add</a><a href="#" onclick="localStorage.clear();location.href='/login'">Logout</a></div></div>
<div class="card"><h3>FIG Members <span id="count"></span></h3><div style="overflow:auto"><table id="tbl"></table></div></div>
<script>
async function load(){{ let key=localStorage.getItem('api_key')||'lonma_api_key_12345'; let r=await fetch('/api/members?api_key='+key); let d=await r.json(); count.innerText='('+d.total+')'; let h='<tr><th>ID</th><th>Staff</th><th>Name</th><th>Email</th><th>Family</th><th>Kids</th><th>Action</th></tr>'; d.members.forEach(m=>{{h+=`<tr><td>${{m.id}}</td><td>${{m.staff_no}}</td><td>${{m.full_names}}</td><td>${{m.email}}</td><td>F:${{m.family.father_id}} M:${{m.family.mother_id}}<br>G:${{m.family.guardian_id}} S:${{m.family.spouse_id}}</td><td>${{Object.values(m.kids).filter(Boolean).join(',')}}</td><td><button class="btn btn-red" style="padding:4px 8px" onclick="del(${{m.id}})">Del</button></td></tr>`}}); tbl.innerHTML=h; }}
async function del(id){{ if(!confirm('Delete '+id+'?')) return; let k=localStorage.getItem('api_key')||'lonma_api_key_12345'; await fetch('/api/members/'+id+'?api_key='+k,{{method:'DELETE'}}); load(); }} load();
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HOME_PAGE)

@app.route("/login")
def login_p(): return render_template_string(LOGIN_PAGE)

@app.route("/register")
def reg_p(): return render_template_string(REGISTER_PAGE)

@app.route("/dashboard")
def dash_p(): return render_template_string(DASHBOARD_PAGE)

# ===== PURE FIG API =====
@app.route("/api/health")
def health():
    conn=get_db(); c=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"status":"ok","project":"FIG","version":"v10 COMPLETE","total_members":c,"timestamp":datetime.now().isoformat()})

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
    return jsonify({"project":"FIG","total_members":total,"system":"COMPLETE v10"})

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
