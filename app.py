from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets, time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-ultra-pro-v15"
DB = "lonma.db"

PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem"]

def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try: conn.execute("PRAGMA journal_mode=WAL;"); conn.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, api_key TEXT, created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    if not conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,api_key) VALUES (?,?,?,?,?,?,?,?,?)",("HQ/001","System Administrator","HQ","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","lonma_api_key_12345"))
    conn.close()
init_db()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); return r

def need_key(f):
    @wraps(f)
    def d(*a,**k):
        if request.method=='OPTIONS': return '',200
        key=request.headers.get("X-API-KEY") or request.args.get("api_key")
        if not key: return jsonify({"error":"Unauthorized"}),401
        conn=get_db()
        try: u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone()
        finally: conn.close()
        if not u: return jsonify({"error":"Invalid"}),401
        return f(*a,**k)
    return d

@app.route("/favicon.ico")
def favicon(): return "",204

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
:root{--bg:#f8fafc;--card:#fff;--border:#e2e8f0;--text:#0f172a;--muted:#64748b}
*{box-sizing:border-box;margin:0;padding:0}body{font-family:'Inter',sans-serif;background:var(--bg);color:var(--text);-webkit-font-smoothing:antialiased}
.header{height:60px;background:#fff;border-bottom:1px solid var(--border);display:flex;align-items:center;justify-content:space-between;padding:0 28px;position:sticky;top:0;z-index:10}
.logo{display:flex;align-items:center;gap:10px}.logo-icon{width:32px;height:32px;background:#0f172a;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;border-radius:8px;font-size:14px}
.brand{font-weight:700;font-size:14px}.brand span{font-weight:500;font-size:11px;color:var(--muted);display:block;letter-spacing:.5px;text-transform:uppercase}
.nav a{padding:7px 12px;border-radius:8px;font-size:13px;font-weight:500;color:var(--muted);text-decoration:none;margin-left:4px}.nav a.active{background:#0f172a;color:#fff}
.page{max-width:1200px;margin:0 auto;padding:28px}
.kpis{display:grid;grid-template-columns:repeat(3,1fr);gap:14px;margin-bottom:20px}
.kpi{background:#fff;border:1px solid var(--border);border-radius:12px;padding:18px 20px}.kpi label{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.6px}.kpi b{font-size:26px;font-weight:700;display:block;margin-top:4px;letter-spacing:-.5px}.kpi p{font-size:12px;color:var(--muted);margin-top:2px}
.card{background:#fff;border:1px solid var(--border);border-radius:12px}
.card-h{padding:18px 22px;border-bottom:1px solid var(--border);display:flex;justify-content:space-between;align-items:center}.card-h h3{font-size:14px;font-weight:600}.card-h small{font-size:12px;color:var(--muted)}
.row{padding:13px 22px;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:13px}.row:last-child{border:0}
.dot{width:8px;height:8px;border-radius:50%;display:inline-block;margin-right:8px}
.btn{padding:8px 14px;border-radius:8px;font-size:13px;font-weight:600;border:1px solid var(--border);background:#fff;cursor:pointer;text-decoration:none;color:var(--text)}.btn-dark{background:#0f172a;color:#fff;border-color:#0f172a}
input,select{width:100%;height:40px;padding:0 12px;border:1px solid var(--border);border-radius:8px;font-size:13px}label{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;letter-spacing:.5px;margin-bottom:5px;display:block}
table{width:100%;border-collapse:collapse}th{font-size:11px;font-weight:600;color:var(--muted);text-transform:uppercase;padding:12px 16px;text-align:left;background:#f8fafc;border-bottom:1px solid var(--border)}td{padding:13px 16px;font-size:13px;border-bottom:1px solid #f1f5f9}
@media(max-width:800px){.kpis{grid-template-columns:1fr}.page{padding:16px}}
</style>
"""

HOME = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA Welfare</title>{CSS}</head><body>
<div class="header"><div class="logo"><div class="logo-icon">L</div><div class="brand">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a></div></div>
<div class="page">
<div class="kpis">
<div class="kpi"><label>Total Members</label><b id="total">—</b><p>Active across all projects</p></div>
<div class="kpi"><label>Projects</label><b>12</b><p>Pwani, Java, SJ, Kanji, HQ, Antonio, TF, GCB, Hichem</p></div>
<div class="kpi"><label>Coverage</label><b>100%</b><p>Welfare data complete</p></div>
</div>
<div class="card"><div class="card-h"><div><h3>Project Distribution</h3><small>Members per project</small></div><a href="/dashboard" class="btn">View Members</a></div><div id="breakdown"></div></div>
</div>
<script>
async function load(){{
 let r=await fetch('/api/stats?api_key=lonma_api_key_12345'); let d=await r.json();
 document.getElementById('total').innerText=d.total_members;
 let colors={{"Pwani Oil Products":"#f59e0b","Java House":"#7c3aed","SJ Johnson":"#dc2626","Kanji":"#059669","HQ":"#0f172a","Antonio":"#db2777","TF-TDs":"#0891b2","TF-MT":"#65a30d","TF-LM":"#ea580c","GCB-MT":"#4f46e5","GCB-Ws":"#0d9488","Hichem":"#9333ea"}};
 let html=''; for(let [proj,count] of Object.entries(d.projects_breakdown||{{}})){{ html+=`<div class="row"><span><i class="dot" style="background:${{colors[proj]||'#64748b'}}"></i>${{proj}}</span><span style="font-weight:600">${{count}}</span></div>`; }}
 document.getElementById('breakdown').innerHTML=html;
}}
load();
</script>
</body></html>
"""

@app.route("/")
def home(): return render_template_string(HOME)

@app.route("/register")
def register_page():
    opts=''.join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - LONMA</title>{CSS}</head><body>
<div class="header"><div class="logo"><div class="logo-icon">L</div><div class="brand">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div>
<div class="page" style="max-width:760px"><div class="card"><div class="card-h"><h3>New Member Registration</h3></div><div style="padding:22px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label>Staff Number</label><input id="staff_no" placeholder="HQ/001"></div><div><label>Project</label><select id="project">{opts}</select></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px"><div><label>Full Names</label><input id="full_names"></div><div><label>Email</label><input id="email"></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:14px"><div><label>Password</label><input id="password" type="password"></div><div><label>Phone</label><input id="phone"></div></div>
<div style="margin-top:14px"><label>Month / Year Joined</label><input id="month_year_joined" placeholder="Oct 2026"></div>
<div style="margin-top:20px;border-top:1px solid #e2e8f0;padding-top:16px"><h4 style="font-size:13px;margin-bottom:10px">Family Details</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label>Father ID</label><input id="father_id"></div><div><label>Mother ID</label><input id="mother_id"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px"><div><label>Guardian ID</label><input id="guardian_id"></div><div><label>Spouse ID</label><input id="spouse_id"></div></div></div>
<div style="margin-top:20px;border-top:1px solid #e2e8f0;padding-top:16px"><h4 style="font-size:13px;margin-bottom:10px">Children</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:14px"><div><label>Child 1</label><input id="kid1"></div><div><label>Child 2</label><input id="kid2"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:14px;margin-top:10px"><div><label>Child 3</label><input id="kid3"></div><div><label>Child 4</label><input id="kid4"></div></div><div style="margin-top:10px"><label>Child 5</label><input id="kid5"></div></div>
<button class="btn btn-dark" style="width:100%;margin-top:20px;height:42px;justify-content:center" onclick="reg()">Create Member</button><p id="msg" style="font-size:12px;margin-top:10px;color:#dc2626"></p>
</div></div></div>
<script>async function reg(){{let d={{}};["staff_no","project","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>d[k]=document.getElementById(k).value);let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});let j=await r.json();msg.innerText=j.error||'Created successfully';if(r.ok)location.href='/dashboard';}}</script></body></html>
""")

@app.route("/dashboard")
def dashboard():
    opts='<option value="">All Projects</option>'+''.join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - LONMA</title>{CSS}</head><body>
<div class="header"><div class="logo"><div class="logo-icon">L</div><div class="brand">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div></div>
<div class="page"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:14px"><div><h2 style="font-size:18px;font-weight:700">Members</h2><p style="font-size:12px;color:#64748b"><span id="count">0</span> total</p></div><a href="/register" class="btn btn-dark">+ Register</a></div>
<div class="card"><div style="padding:12px 16px;border-bottom:1px solid #e2e8f0;display:flex;gap:10px"><input id="search" placeholder="Search..." style="max-width:280px;height:36px" oninput="filter()"><select id="projFilter" style="max-width:180px;height:36px" onchange="filter()">{opts}</select></div><div style="overflow:auto"><table id="tbl"></table></div></div></div>
<script>
let all=[];
async function load(){{let k=localStorage.getItem('api_key')||'lonma_api_key_12345';let r=await fetch('/api/members?api_key='+k);let d=await r.json();all=d.members;count.innerText=d.total;render(d.members);}}
function render(list){{let h='<tr><th>Staff</th><th>Member</th><th>Project</th><th>Contact</th><th></th></tr>';list.forEach(m=>{{h+=`<tr><td style="font-weight:600">${{m.staff_no}}</td><td>${{m.full_names}}<br><span style="font-size:11px;color:#64748b">${{m.month_year_joined||''}}</span></td><td><span style="font-size:11px;padding:4px 8px;border-radius:6px;background:#f8fafc;border:1px solid #e2e8f0">${{m.project}}</span></td><td style="font-size:12px">${{m.email}}</td><td><button onclick="del(${{m.id}})" style="padding:5px 10px;border-radius:6px;border:1px solid #fee2e2;background:#fff;color:#dc2626;font-size:12px;font-weight:600;cursor:pointer">Delete</button></td></tr>`}});tbl.innerHTML=h;}}
function filter(){{let q=search.value.toLowerCase();let p=projFilter.value;render(all.filter(m=>(m.full_names+m.staff_no+m.email).toLowerCase().includes(q)&&(!p||m.project===p)));}}
async function del(id){{if(!confirm('Delete '+id+'?'))return;let k=localStorage.getItem('api_key')||'lonma_api_key_12345';let r=await fetch('/api/members/'+id+'?api_key='+k,{{method:'DELETE'}});if(r.ok)load();}}
load();
</script></body></html>
""")

@app.route("/login")
def login():
    return render_template_string(f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login</title>{CSS}</head><body style="display:flex;justify-content:center;align-items:center;min-height:100vh;background:#f8fafc"><div class="card" style="width:360px"><div style="padding:24px;text-align:center;border-bottom:1px solid #e2e8f0"><div class="logo-icon" style="margin:0 auto 10px">L</div><div style="font-weight:700">LONMA</div><div style="font-size:11px;color:#64748b;text-transform:uppercase;letter-spacing:.5px">Welfare Management</div></div><div style="padding:20px"><label>Email</label><input id="email" value="admin@lonma.com"><label style="margin-top:12px">Password</label><input id="pass" type="password" value="admin123"><button class="btn btn-dark" style="width:100%;margin-top:16px;height:40px;justify-content:center" onclick="login()">Sign in</button><p id="msg" style="font-size:12px;margin-top:10px;color:#dc2626"></p></div></div><script>async function login(){{let r=await fetch('/api/login',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify({{email:email.value,password:pass.value}})}});let d=await r.json();if(d.member){{localStorage.setItem('api_key',d.member.api_key);location.href='/';}}else{{msg.innerText=d.error;}}}}</script></body></html>""")

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown={p:conn.execute("SELECT COUNT(*) FROM users WHERE project=?",(p,)).fetchone()[0] for p in PROJECTS}
        return jsonify({"total_members":total,"projects_breakdown":breakdown})
    finally: conn.close()

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall()
        data=[{"id":u["id"],"staff_no":u["staff_no"],"full_names":u["full_names"],"project":u["project"],"month_year_joined":u["month_year_joined"],"email":u["email"],"phone":u["phone"],"family":{"father_id":u["father_id"],"mother_id":u["mother_id"],"guardian_id":u["guardian_id"],"spouse_id":u["spouse_id"]},"kids":{"kid1":u["kid1"],"kid2":u["kid2"],"kid3":u["kid3"],"kid4":u["kid4"],"kid5":u["kid5"]}} for u in users]
        return jsonify({"total":len(data),"members":data})
    finally: conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"email,password required"}),400
    conn=get_db()
    try:
        key=f"lonma_{secrets.token_hex(16)}"; conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(d.get("staff_no",f"HQ/{secrets.token_hex(2).upper()}"),d.get("full_names",""),d.get("project","HQ"),d.get("month_year_joined",""),d["email"],generate_password_hash(d["password"]),d.get("phone",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),key)); conn.execute("COMMIT")
        return jsonify({"message":"Created"}),201
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),400
    finally: conn.close()

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json(silent=True); conn=get_db()
    try:
        u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
        return jsonify({"member":{"id":u["id"],"full_names":u["full_names"],"api_key":u["api_key"]}})
    finally: conn.close()

@app.route("/api/members/<int:id>", methods=["DELETE","OPTIONS"])
@need_key
def delete_member(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db()
    try:
        for _ in range(3):
            try:
                conn.execute("BEGIN IMMEDIATE"); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.execute("COMMIT"); return jsonify({"message":"Deleted"})
            except sqlite3.OperationalError:
                try: conn.execute("ROLLBACK")
                except: pass
                time.sleep(0.5); continue
    finally: conn.close()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
