from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets, time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-12-projects-professional"
DB = "lonma.db"

# ===== 12 PROJECTS CODED =====
PROJECTS = [
    "Pwani Oil Products",
    "Java House",
    "SJ Johnson",
    "Kanji",
    "HQ",
    "Antonio",
    "TF-TDs",
    "TF-MT",
    "TF-LM",
    "GCB-MT",
    "GCB-Ws",
    "Hichem"
]

PROJECT_SHORT = {
    "Pwani Oil Products": "PWANI",
    "Java House": "JAVA",
    "SJ Johnson": "SJ",
    "Kanji": "KANJI",
    "HQ": "HQ",
    "Antonio": "ANTONIO",
    "TF-TDs": "TF-TDs",
    "TF-MT": "TF-MT",
    "TF-LM": "TF-LM",
    "GCB-MT": "GCB-MT",
    "GCB-Ws": "GCB-Ws",
    "Hichem": "HICHEM"
}

def get_db():
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
    except: pass
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        ("HQ/001","Administrator","HQ","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","FATHER_001","MOTHER_001","22400966","23601476","42107914","111041990","","","","lonma_api_key_12345"))
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
        try: u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone()
        finally: conn.close()
        if not u: return jsonify({"error":"Invalid key"}),401
        return f(*a,**k)
    return d

@app.route("/favicon.ico")
def favicon(): return "",204

PRO_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',system-ui,sans-serif;background:#f8fafc;color:#1e293b}
.nav{background:#fff;border-bottom:1px solid #e2e8f0;padding:16px 24px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:50}
.logo{width:40px;height:40px;background:linear-gradient(135deg,#0ea5e9,#0284c7);border-radius:10px;display:flex;align-items:center;justify-content:center;color:#fff;font-weight:700}
.nav-links a{color:#475569;text-decoration:none;font-weight:500;font-size:14px;margin-left:16px;padding:8px 14px;border-radius:8px}.nav-links a:hover{background:#f1f5f9}.nav-links a.active{background:#0ea5e9;color:#fff}
.hero{background:linear-gradient(135deg,#0f172a 0%,#1e293b 100%);color:#fff;padding:40px 24px}.hero-inner{max-width:1200px;margin:0 auto}
.container{max-width:1200px;margin:0 auto;padding:24px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:24px;box-shadow:0 1px 3px rgba(0,0,0,.05)}
.btn{padding:10px 18px;border-radius:10px;font-weight:600;font-size:14px;border:none;cursor:pointer;text-decoration:none;display:inline-flex}
.btn-primary{background:#0ea5e9;color:#fff}.btn-dark{background:#0f172a;color:#fff}
input,select{width:100%;padding:12px 14px;border:1px solid #e2e8f0;border-radius:10px;font-size:14px;background:#fff}input:focus,select:focus{outline:none;border-color:#0ea5e9;box-shadow:0 0 0 3px rgba(14,165,233,.1)}
label{font-size:11px;font-weight:600;color:#475569;text-transform:uppercase;letter-spacing:.5px;margin-bottom:4px;display:block}
table{width:100%;border-collapse:collapse}th{font-size:11px;text-transform:uppercase;color:#64748b;padding:12px;text-align:left;background:#f8fafc;border-bottom:1px solid #e2e8f0}td{padding:12px;border-bottom:1px solid #f1f5f9;font-size:13px}
.grid-2{display:grid;grid-template-columns:1fr 1fr;gap:16px}.grid-3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:16px}.grid-4{display:grid;grid-template-columns:1fr 1fr 1fr 1fr;gap:12px}
@media(max-width:768px){.grid-2,.grid-3,.grid-4{grid-template-columns:1fr}}
.project-badge{padding:4px 10px;border-radius:20px;font-size:11px;font-weight:600;color:#fff;display:inline-block}
.badge-PWANI{background:#f59e0b}.badge-JAVA{background:#8b5cf6}.badge-SJ{background:#ef4444}.badge-KANJI{background:#10b981}.badge-HQ{background:#0f172a}.badge-ANTONIO{background:#ec4899}.badge-TF-TDs{background:#06b6d4}.badge-TF-MT{background:#84cc16}.badge-TF-LM{background:#f97316}.badge-GCB-MT{background:#6366f1}.badge-GCB-Ws{background:#14b8a6}.badge-HICHEM{background:#a855f7}
</style>
"""

def project_options(selected=""):
    html = ""
    for p in PROJECTS:
        sel = "selected" if p==selected else ""
        html += f'<option value="{p}" {sel}>{p} ({PROJECT_SHORT[p]})</option>'
    return html

def project_badge(project):
    short = PROJECT_SHORT.get(project, project[:4].upper())
    cls = f"badge-{short}" if f"badge-{short}" in ["badge-PWANI","badge-JAVA","badge-SJ","badge-KANJI","badge-HQ","badge-ANTONIO","badge-TF-TDs","badge-TF-MT","badge-TF-LM","badge-GCB-MT","badge-GCB-Ws","badge-HICHEM"] else "badge-HQ"
    # simplify: use inline colors
    colors = {"Pwani Oil Products":"#f59e0b","Java House":"#8b5cf6","SJ Johnson":"#ef4444","Kanji":"#10b981","HQ":"#0f172a","Antonio":"#ec4899","TF-TDs":"#06b6d4","TF-MT":"#84cc16","TF-LM":"#f97316","GCB-MT":"#6366f1","GCB-Ws":"#14b8a6","Hichem":"#a855f7"}
    color = colors.get(project,"#0f172a")
    return f'<span class="project-badge" style="background:{color}">{project}</span>'

HOME_PAGE = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA - 12 Projects Welfare</title>{PRO_CSS}</head><body>
<div class="nav"><div style="display:flex;align-items:center;gap:12px"><div class="logo">L</div><div><b>LONMA WELFARE</b><br><span style="font-size:11px;color:#64748b">12 PROJECTS • MULTI-PROJECT SYSTEM</span></div></div><div class="nav-links"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a><a href="/login">Login</a></div></div>
<div class="hero"><div class="hero-inner"><h1 style="font-size:32px">12 Projects Welfare System <span style="color:#38bdf8">Professional</span></h1><p style="color:#94a3b8;margin-top:8px">Pwani Oil Products, Java House, SJ Johnson, Kanji, HQ, Antonio, TF-TDs, TF-MT, TF-LM, GCB-MT, GCB-Ws, Hichem</p>
<div class="grid-4" style="margin-top:20px"><div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:14px;border-radius:12px"><b id="total" style="font-size:24px;color:#fff">-</b><br><span style="color:#94a3b8;font-size:11px">TOTAL MEMBERS</span></div><div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:14px;border-radius:12px"><b style="font-size:24px;color:#fff">12</b><br><span style="color:#94a3b8;font-size:11px">PROJECTS CODED</span></div><div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:14px;border-radius:12px"><b style="font-size:24px;color:#4ade80">LIVE</b><br><span style="color:#94a3b8;font-size:11px">SYSTEM STATUS</span></div><div style="background:rgba(255,255,255,.06);border:1px solid rgba(255,255,255,.1);padding:14px;border-radius:12px"><b style="font-size:24px;color:#fff">v13</b><br><span style="color:#94a3b8;font-size:11px">VERSION</span></div></div>
</div></div>
<div class="container">
<div class="grid-2">
<div class="card"><h3 style="margin-bottom:12px">📊 Projects Breakdown</h3><div id="breakdown" style="font-size:13px">Loading...</div></div>
<div class="card"><h3 style="margin-bottom:12px">🎯 All 12 Projects Coded</h3>
<div style="display:flex;flex-wrap:wrap;gap:6px">
<span style="background:#f59e0b;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">1. Pwani Oil Products</span>
<span style="background:#8b5cf6;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">2. Java House</span>
<span style="background:#ef4444;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">3. SJ Johnson</span>
<span style="background:#10b981;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">4. Kanji</span>
<span style="background:#0f172a;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">5. HQ</span>
<span style="background:#ec4899;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">6. Antonio</span>
<span style="background:#06b6d4;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">7. TF-TDs</span>
<span style="background:#84cc16;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">8. TF-MT</span>
<span style="background:#f97316;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">9. TF-LM</span>
<span style="background:#6366f1;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">10. GCB-MT</span>
<span style="background:#14b8a6;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">11. GCB-Ws</span>
<span style="background:#a855f7;color:#fff;padding:4px 10px;border-radius:20px;font-size:11px">12. Hichem</span>
</div>
<div style="margin-top:16px"><a href="/register" class="btn btn-primary">+ Register Member</a> <a href="/dashboard" class="btn" style="background:#f1f5f9">View Dashboard</a></div>
</div>
</div>
</div>
<script>
async function load(){{
 let r=await fetch('/api/stats?api_key=lonma_api_key_12345'); let d=await r.json();
 document.getElementById('total').innerText=d.total_members;
 let html=''; for(let [proj,count] of Object.entries(d.projects_breakdown||{{}})){{ html+=`<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px solid #f1f5f9"><span>${{proj}}</span><b>${{count}}</b></div>`; }}
 document.getElementById('breakdown').innerHTML=html||'No data yet';
}}
load();
</script>
</body></html>
"""

# Build pages dynamically with projects
def get_register_page():
    opts = project_options()
    return f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - 12 Projects</title>{PRO_CSS}</head><body>
<div class="nav"><div style="display:flex;align-items:center;gap:12px"><div class="logo">L</div><b>LONMA - 12 PROJECTS</b></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div>
<div class="container"><div class="card"><h2>Register Member - 12 Projects</h2><p style="color:#64748b;font-size:13px;margin-bottom:16px">Select project from coded list</p>
<div class="grid-2"><div><label>Staff Number *</label><input id="staff_no" placeholder="e.g. PWANI/001 or JAVA/002"></div><div><label>Project * (12 Coded)</label><select id="project">{opts}</select></div></div>
<div class="grid-2" style="margin-top:12px"><div><label>Full Names *</label><input id="full_names"></div><div><label>Email *</label><input id="email"></div></div>
<div class="grid-2" style="margin-top:12px"><div><label>Password *</label><input id="password"></div><div><label>Phone</label><input id="phone"></div></div>
<div style="margin-top:12px"><label>Month / Year Joined</label><input id="month_year_joined" placeholder="Oct 2026"></div>
<h3 style="font-size:14px;margin:20px 0 12px">Family IDs</h3><div class="grid-2"><div><input id="father_id" placeholder="Father ID"></div><div><input id="mother_id" placeholder="Mother ID"></div></div><div class="grid-2" style="margin-top:10px"><div><input id="guardian_id" placeholder="Guardian 22400966"></div><div><input id="spouse_id" placeholder="Spouse 23601476"></div></div>
<h3 style="font-size:14px;margin:20px 0 12px">Kids Birth Certs</h3><div class="grid-2"><div><input id="kid1" placeholder="Kid1 42107914"></div><div><input id="kid2" placeholder="Kid2 111041990"></div></div><div class="grid-2" style="margin-top:10px"><div><input id="kid3" placeholder="Kid3"></div><div><input id="kid4" placeholder="Kid4"></div></div><input id="kid5" placeholder="Kid5" style="margin-top:10px">
<button class="btn btn-primary" style="width:100%;margin-top:20px;padding:14px;justify-content:center" onclick="reg()">+ Register to Selected Project</button><p id="msg" style="margin-top:12px"></p></div></div>
<script>
async function reg(){{let d={{}};["staff_no","project","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>d[k]=document.getElementById(k).value);let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});let j=await r.json();msg.innerText=JSON.stringify(j);if(r.ok)location.href='/dashboard';}}
</script></body></html>
"""

def get_dashboard_page():
    proj_opts = '<option value="">All Projects (12)</option>' + project_options()
    return f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Dashboard - 12 Projects</title>{PRO_CSS}</head><body>
<div class="nav"><div style="display:flex;align-items:center;gap:12px"><div class="logo">L</div><b>LONMA 12 PROJECTS</b></div><div class="nav-links"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div></div>
<div class="container"><div style="display:flex;justify-content:space-between;margin-bottom:16px;flex-wrap:wrap;gap:10px"><div><h2>Members - All Projects</h2><p style="color:#64748b;font-size:13px"><span id="count">0</span> total across 12 projects</p></div><a href="/register" class="btn btn-primary">+ New Member</a></div>
<div class="card" style="padding:0;overflow:hidden"><div style="padding:16px;display:flex;gap:10px;flex-wrap:wrap;border-bottom:1px solid #e2e8f0"><input id="search" placeholder="🔍 Search name, staff, email..." style="max-width:280px" oninput="filter()"><select id="projFilter" style="max-width:200px" onchange="filter()">{proj_opts}</select></div><div style="overflow:auto"><table id="tbl"></table></div></div></div>
<script>
let allData=[];
async function load(){{let k=localStorage.getItem('api_key')||'lonma_api_key_12345';let r=await fetch('/api/members?api_key='+k);let d=await r.json();allData=d.members;count.innerText=d.total;render(d.members);}}
function render(list){{let h='<tr><th>Staff / Project</th><th>Member</th><th>Contact</th><th>Family</th><th>Kids</th><th>Action</th></tr>';list.forEach(m=>{{let color={{'Pwani Oil Products':'#f59e0b','Java House':'#8b5cf6','SJ Johnson':'#ef4444','Kanji':'#10b981','HQ':'#0f172a','Antonio':'#ec4899','TF-TDs':'#06b6d4','TF-MT':'#84cc16','TF-LM':'#f97316','GCB-MT':'#6366f1','GCB-Ws':'#14b8a6','Hichem':'#a855f7'}}[m.project]||'#0f172a';h+=`<tr><td><b>${{m.staff_no}}</b><br><span style="background:${{color}};color:#fff;padding:2px 8px;border-radius:10px;font-size:10px">${{m.project}}</span></td><td><b>${{m.full_names}}</b><br><span style="color:#64748b;font-size:11px">${{m.month_year_joined||''}}</span></td><td style="font-size:12px">${{m.email}}<br>${{m.phone||''}}</td><td style="font-size:10px">F:${{m.family.father_id||'-'}} M:${{m.family.mother_id||'-'}}<br>G:${{m.family.guardian_id||'-'}} S:${{m.family.spouse_id||'-'}}</td><td style="font-size:11px">${{Object.values(m.kids).filter(Boolean).join(', ')||'-'}}</td><td><button onclick="del(${{m.id}})" style="background:#fff;border:1px solid #fee2e2;color:#ef4444;padding:6px 10px;border-radius:8px;font-size:11px;cursor:pointer">Delete</button></td></tr>`}});tbl.innerHTML=h;}}
function filter(){{let q=search.value.toLowerCase();let p=projFilter.value;let filtered=allData.filter(m=>{{let matchQ=(m.full_names+m.staff_no+m.email).toLowerCase().includes(q);let matchP=!p||m.project===p;return matchQ&&matchP;}});render(filtered);}}
async function del(id){{if(!confirm('Delete member '+id+'?'))return;let k=localStorage.getItem('api_key')||'lonma_api_key_12345';await fetch('/api/members/'+id+'?api_key='+k,{{method:'DELETE'}});load();}}
load();
</script></body></html>
"""

@app.route("/")
def home(): return render_template_string(HOME_PAGE)

@app.route("/register")
def reg_page(): return render_template_string(get_register_page())

@app.route("/dashboard")
def dash_page(): return render_template_string(get_dashboard_page())

@app.route("/login")
def login_page():
    return render_template_string(f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login</title>{PRO_CSS}</head><body style="display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f8fafc"><div class="card" style="max-width:400px;width:90%"><div style="text-align:center;margin-bottom:20px"><div class="logo" style="margin:0 auto">L</div><h2>LONMA Login</h2><p style="color:#64748b;font-size:13px">12 Projects System</p></div><label>Email</label><input id="email" value="admin@lonma.com"><label style="margin-top:12px">Password</label><input id="pass" type="password" value="admin123"><button class="btn btn-dark" style="width:100%;margin-top:16px;justify-content:center" onclick="login()">Sign In</button><p id="msg" style="font-size:12px;margin-top:10px;color:#ef4444"></p></div><script>async function login(){{let r=await fetch('/api/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:pass.value}})}});let d=await r.json();if(d.member){{localStorage.setItem('api_key',d.member.api_key);location.href='/dashboard';}}else{{msg.innerText=d.error;}}}}</script></body></html>""")

@app.route("/api/health")
def health():
    conn=get_db()
    try:
        c=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        return jsonify({"status":"ok","version":"v13 12-PROJECTS","total_members":c,"projects":PROJECTS})
    finally: conn.close()

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        users=conn.execute("SELECT * FROM users ORDER BY project, id DESC").fetchall()
        data=[{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"project":u["project"],"month_year_joined":u["month_year_joined"],"email":u["email"],"phone":u["phone"],"role":u["role"],"family":{"father_id":u["father_id"],"mother_id":u["mother_id"],"guardian_id":u["guardian_id"],"spouse_id":u["spouse_id"]},"kids":{"kid1":u["kid1"],"kid2":u["kid2"],"kid3":u["kid3"],"kid4":u["kid4"],"kid5":u["kid5"]}} for u in users]
        return jsonify({"total":len(data),"projects_coded":PROJECTS,"members":data})
    finally: conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"email,password required"}),400
    proj = d.get("project","HQ")
    if proj not in PROJECTS: return jsonify({"error":f"Invalid project. Must be one of: {', '.join(PROJECTS)}"}),400
    conn=get_db()
    try:
        key=f"lonma_{secrets.token_hex(16)}"
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
        (d.get("staff_no",f"{PROJECT_SHORT.get(proj, 'HQ')}/{secrets.token_hex(2).upper()}"),d.get("full_names",""),proj,d.get("month_year_joined",""),d["email"],generate_password_hash(d["password"]),d.get("role","Member"),d.get("phone",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),key))
        conn.execute("COMMIT")
        u=conn.execute("SELECT * FROM users WHERE email=?",(d["email"],)).fetchone()
        return jsonify({"message":f"Member registered to {proj}","project":proj,"member":{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"project":u["project"],"email":u["email"],"api_key":u["api_key"]}}),201
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),400
    finally: conn.close()

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    conn=get_db()
    try:
        u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
        return jsonify({"message":"Login success","member":{"id":u["id"],"full_names":u["full_names"],"email":u["email"],"project":u["project"],"api_key":u["api_key"],"role":u["role"]}})
    finally: conn.close()

@app.route("/api/members/<int:id>", methods=["PUT","DELETE","OPTIONS"])
@need_key
def modify(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        if request.method=="DELETE":
            for attempt in range(3):
                try:
                    conn.execute("BEGIN IMMEDIATE")
                    conn.execute("DELETE FROM users WHERE id=?",(id,))
                    conn.execute("COMMIT")
                    return jsonify({"message":f"Deleted {id}"})
                except sqlite3.OperationalError as e:
                    if "locked" in str(e) and attempt<2:
                        try: conn.execute("ROLLBACK")
                        except: pass
                        time.sleep(0.5)
                        continue
                    else: raise e
        d=request.get_json(silent=True)
        if d.get("project") and d["project"] not in PROJECTS: return jsonify({"error":f"Invalid project"}),400
        fields=[]; vals=[]
        for k in ["staff_no","full_names","project","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]:
            if k in d: fields.append(f"{k}=?"); vals.append(d[k])
        vals.append(id)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?",vals)
        conn.execute("COMMIT")
        return jsonify({"message":"Updated","id":id})
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),500
    finally: conn.close()

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown={}
        for proj in PROJECTS:
            cnt=conn.execute("SELECT COUNT(*) FROM users WHERE project=?",(proj,)).fetchone()[0]
            breakdown[proj]=cnt
        return jsonify({"total_members":total,"projects_coded":12,"projects_list":PROJECTS,"projects_breakdown":breakdown,"version":"v13 12-PROJECTS"})
    finally: conn.close()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
