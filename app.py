from flask import Flask, request, jsonify, render_template_string, redirect
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem"]
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"

def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=10000;")
    except:
        pass
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]:
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    if not conn.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    conn.close()
init_db()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
    return r

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:#f8f9fb;color:#0f172a;-webkit-font-smoothing:antialiased}
.header{height:72px;background:#ffffff;border-bottom:1px solid #eef0f3;display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:20}
.brand{display:flex;gap:12px;align-items:center}.brand-icon{width:40px;height:40px;background:#0f172a;color:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px;letter-spacing:-0.5px}
.brand-name{font-weight:800;font-size:15px;line-height:1.1;letter-spacing:-0.3px}.brand-name span{font-size:10.5px;display:block;color:#64748b;font-weight:600;letter-spacing:0.6px;line-height:1.3;margin-top:1px}
.nav{display:flex;gap:6px;background:#f1f5f9;padding:4px;border-radius:999px}.nav a{padding:8px 18px;border-radius:999px;font-size:13.5px;color:#64748b;text-decoration:none;font-weight:600;transition:all .2s;white-space:nowrap}.nav a.active{background:#0f172a;color:#fff;box-shadow:0 1px 2px rgba(0,0,0,.1)}
.page{max-width:720px;margin:0 auto;padding:20px 16px}
.card{background:#ffffff;border:1px solid #eef0f3;border-radius:20px;box-shadow:0 1px 2px rgba(16,24,40,.04), 0 1px 3px rgba(16,24,40,.03);margin-bottom:16px;overflow:hidden}
.card-header{padding:24px 28px 20px 28px;border-bottom:1px solid #f1f5f9}
.card-title{font-size:18px;font-weight:800;letter-spacing:-0.4px;color:#0f172a}
.card-subtitle{font-size:13px;color:#64748b;margin-top:6px;font-weight:500}
.card-body{padding:26px 28px}
.label{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:0.7px;margin-bottom:8px;display:block}
.input{width:100%;height:46px;padding:0 14px;border:1px solid #e2e8f0;border-radius:12px;font-size:14px;font-weight:500;background:#ffffff;color:#0f172a;transition:all .15s;outline:none}
.input::placeholder{color:#94a3b8;font-weight:400}
.input:focus{border-color:#0f172a;box-shadow:0 0 0 3px rgba(15,23,42,.08)}
select.input{background:#f8fafc;font-weight:600}
.section{display:flex;align-items:center;gap:12px;margin:28px 0 16px 0}
.section:first-child{margin-top:0}
.section-num{width:24px;height:24px;background:#0f172a;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:800}
.section-label{font-size:12.5px;font-weight:800;letter-spacing:0.6px;text-transform:uppercase;color:#0f172a}
.section-line{flex:1;height:1px;background:#f1f5f9;margin-left:8px}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:14px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:14px}
.btn-primary{width:100%;height:50px;background:#0f172a;color:#fff;border:none;border-radius:12px;font-weight:700;font-size:14px;letter-spacing:-0.2px;cursor:pointer;transition:all .15s;display:flex;align-items:center;justify-content:center;gap:8px;margin-top:8px}
.btn-primary:hover{background:#1e293b;transform:translateY(-1px);box-shadow:0 4px 12px rgba(15,23,42,.15)}
.btn-primary:active{transform:translateY(0)}
.stat-card{background:#fff;border:1px solid #eef0f3;border-radius:20px;padding:22px 24px;box-shadow:0 1px 2px rgba(16,24,40,.04)}
.stat-label{font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px}
.stat-value{font-size:30px;font-weight:800;letter-spacing:-1px;margin-top:6px;color:#0f172a}
.stat-value.green{color:#16a34a}
.row-prof{padding:15px 24px;border-bottom:1px solid #f8fafc;display:flex;justify-content:space-between;font-size:14px;font-weight:500}
@media(max-width:600px){.grid2,.grid3{grid-template-columns:1fr}.header{padding:0 16px}.card-body{padding:20px}.card-header{padding:20px}}
</style>
"""

@app.route("/")
def home():
    html = """<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LONMA - Welfare</title>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE MANAGEMENT SYSTEM</span></div></div><div class='nav'><a href='/' class='active'>Overview</a><a href='/members'>Members</a><a href='/register'>Register</a></div></div>
<div class='page'>
<div style='display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px;margin-bottom:16px'><div class='stat-card'><div class='stat-label'>Total Members</div><div class='stat-value' id='total'>0</div></div><div class='stat-card'><div class='stat-label'>Projects</div><div class='stat-value'>12</div></div><div class='stat-card'><div class='stat-label'>Status</div><div class='stat-value green'>Active</div></div></div>
<div class='card'><div class='card-header' style='display:flex;justify-content:space-between;align-items:center'><div><div class='card-title'>Project Distribution</div><div class='card-subtitle'>Members per project</div></div><a href='/members' style='height:36px;padding:0 16px;border-radius:999px;border:1px solid #e2e8f0;background:#fff;font-weight:600;font-size:13px;text-decoration:none;color:#0f172a;display:flex;align-items:center'>View All</a></div><div id='breakdown'></div></div>
</div>
<script>
async function load(){
 let r=await fetch('/api/stats');
 let d=await r.json();
 document.getElementById('total').textContent=d.total_members;
 let h='';
 for(let k in d.projects_breakdown){ h+='<div class="row-prof"><span style="color:#475569">'+k+'</span><b style="font-weight:700">'+d.projects_breakdown[k]+'</b></div>'; }
 document.getElementById('breakdown').innerHTML=h;
}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/members")
def members_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Members - LONMA</title>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE MANAGEMENT SYSTEM</span></div></div><div class='nav'><a href='/'>Overview</a><a href='/members' class='active'>Members</a><a href='/register'>Register</a></div></div>
<div class='page' style='max-width:900px'><div class='card'><div class='card-header'><div class='card-title'>Member Directory</div><div class='card-subtitle'>All registered welfare members</div></div><div style='padding:12px 16px;border-bottom:1px solid #f1f5f9'><input class='input' id='q' placeholder='Search members, staff number, project...' oninput='fil()' style='height:42px'></div><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><thead><tr><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 20px;background:#f8fafc;text-align:left'>Staff</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 20px;background:#f8fafc;text-align:left'>Member</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 20px;background:#f8fafc;text-align:left'>Project</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 20px;background:#f8fafc;text-align:left'>Family</th></tr></thead><tbody id='tbl'></tbody></table></div></div></div>
<script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function render(l){let h='';if(l.length==0){h='<tr><td colspan=4 style="padding:48px;text-align:center;color:#64748b"><div style="font-weight:600;color:#0f172a">No members yet</div><div style="font-size:13px;margin-top:4px">Register your first welfare member to get started</div></td></tr>';}else{l.forEach(m=>{h+='<tr style="border-bottom:1px solid #f8fafc"><td style="padding:16px 20px"><span style="font-weight:700;font-size:13px;background:#f1f5f9;padding:4px 10px;border-radius:8px">'+m.staff_no+'</span><div style="font-size:12px;color:#64748b;margin-top:6px">'+(m.month_joined||'-')+'</div></td><td style="padding:16px 20px"><div style="font-weight:700;font-size:14px">'+m.full_names+'</div><div style="font-size:12px;color:#64748b;margin-top:2px">Spouse: '+(m.spouse_id||'—')+' • Guardian: '+(m.guardian_id||'—')+'</div></td><td style="padding:16px 20px"><span style="font-size:13px;font-weight:600">'+m.project+'</span></td><td style="padding:16px 20px"><div style="font-size:12px;font-weight:600">Kids: '+( [m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).length || 0 )+'</div><div style="font-size:11px;color:#64748b">Father: '+(m.father_id||'—')+' • Mother: '+(m.mother_id||'—')+'</div></td></tr>';});}document.getElementById('tbl').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();render(all.filter(m=>(m.full_names+m.staff_no+m.project+(m.spouse_id||'')).toLowerCase().includes(qq)));}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/register")
def register_page():
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register - LONMA Welfare</title>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE MANAGEMENT SYSTEM</span></div></div><div class='nav'><a href='/'>Overview</a><a href='/members'>Members</a><a href='/register' class='active'>Register</a></div></div>
<div class='page'>
<div class='card'><div class='card-header'><div class='card-title'>Welfare Registration Form</div><div class='card-subtitle'>Add a new member to the welfare system</div></div><div class='card-body'>

<div class='section'><div class='section-num'>1</div><div class='section-label'>Staff Information</div><div class='section-line'></div></div>
<div class='grid2'><div><label class='label'>Staff Number</label><input class='input' id='staff_no' placeholder='PWANI/001'></div><div><label class='label'>Project</label><select class='input' id='project'>""" + opts + """</select></div></div>
<div style='margin-top:14px' class='grid2'><div><label class='label'>Date Joined</label><input class='input' id='month_joined' placeholder='January 2024'></div><div><label class='label'>Full Names *</label><input class='input' id='full_names' placeholder='John Doe'></div></div>
<div style='margin-top:14px' class='grid2'><div><label class='label'>Email Address *</label><input class='input' id='email' placeholder='member@lonma.com'></div><div><label class='label'>Password *</label><input class='input' id='password' type='password' placeholder='••••••••'></div></div>

<div class='section'><div class='section-num'>2</div><div class='section-label'>Parents Identification</div><div class='section-line'></div></div>
<div class='grid2'><div><label class='label'>Father ID Number</label><input class='input' id='father_id' placeholder='ID Number'></div><div><label class='label'>Mother ID Number</label><input class='input' id='mother_id' placeholder='ID Number'></div></div>

<div class='section'><div class='section-num'>3</div><div class='section-label'>Guardian & Spouse</div><div class='section-line'></div></div>
<div class='grid2'><div><label class='label'>Guardian ID Number</label><input class='input' id='guardian_id' placeholder='e.g. 22400966'></div><div><label class='label'>Spouse ID Number</label><input class='input' id='spouse_id' placeholder='e.g. 23601476'></div></div>

<div class='section'><div class='section-num'>4</div><div class='section-label'>Children - Birth Certificates</div><div class='section-line'></div></div>
<div class='grid3'><div><label class='label'>Child 1</label><input class='input' id='kid1' placeholder='e.g. 42107914'></div><div><label class='label'>Child 2</label><input class='input' id='kid2' placeholder='e.g. 111041990'></div><div><label class='label'>Child 3</label><input class='input' id='kid3' placeholder='Certificate No.'></div></div>
<div style='margin-top:14px' class='grid2'><div><label class='label'>Child 4</label><input class='input' id='kid4' placeholder='Certificate No.'></div><div><label class='label'>Child 5</label><input class='input' id='kid5' placeholder='Certificate No.'></div></div>

<button class='btn-primary' onclick='doReg()' id='btn'><span id='btnTxt'>Create Member</span></button>
<p id='msg' style='font-size:13px;margin-top:14px;text-align:center;font-weight:600'></p>
</div></div>
</div>
<script>async function doReg(){let btn=document.getElementById('btn');let txt=document.getElementById('btnTxt');let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value};if(!d.email||!d.password||!d.full_names){let m=document.getElementById('msg');m.textContent='Please fill required fields: Full Names, Email, Password';m.style.color='#dc2626';return;}btn.disabled=true;txt.textContent='Creating...';let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();let m=document.getElementById('msg');m.textContent=j.error||j.message;m.style.color=r.ok?'#16a34a':'#dc2626';btn.disabled=false;txt.textContent=r.ok?'Created Successfully':'Create Member';if(r.ok){setTimeout(()=>{window.location.href='/members'},800);}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin")
def admin_login_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin - LONMA</title>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>ADMIN PORTAL</span></div></div></div>
<div class='page' style='max-width:420px;padding-top:40px'><div class='card'><div class='card-header'><div class='card-title'>Admin Access</div><div class='card-subtitle'>Secure login for administrators</div></div><div class='card-body'><label class='label'>Email Address</label><input class='input' id='email' value='admin@lonma.com'><div style='margin-top:14px'><label class='label'>Password</label><input class='input' id='pass' type='password' value='admin123'></div><button class='btn-primary' style='margin-top:20px' onclick='login()'>Sign In</button><p id='msg' style='font-size:13px;margin-top:12px;text-align:center;color:#dc2626;font-weight:600'></p></div></div></div>
<script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok){location.href='/admin/dashboard?key='+j.key;}else{document.getElementById('msg').textContent=j.error;}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/dashboard")
def admin_dashboard():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Dashboard - LONMA</title>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>ADMIN DASHBOARD</span></div></div><div class='nav'><a href='/admin/dashboard?key=""" + ADMIN_KEY + """' class='active'>Dashboard</a><a href='/'>Overview</a></div></div>
<div class='page' style='max-width:1100px'><div class='card'><div class='card-header' style='display:flex;justify-content:space-between;align-items:center'><div><div class='card-title'>Welfare Members Management</div><div class='card-subtitle'>Full control with family data</div></div><a href='/admin/register?key=""" + ADMIN_KEY + """' class='btn-primary' style='width:auto;padding:0 20px;height:40px'>+ New Member</a></div><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><thead><tr><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 16px;background:#f8fafc;text-align:left'>Staff & Name</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 16px;background:#f8fafc;text-align:left'>Project</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 16px;background:#f8fafc;text-align:left'>Family IDs</th><th style='font-size:11px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:12px 16px;background:#f8fafc;text-align:left'>Action</th></tr></thead><tbody id='tbl'></tbody></table></div></div></div>
<script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let badge=prot?'<span style="font-size:9px;background:#0f172a;color:#fff;padding:3px 8px;border-radius:999px;margin-left:8px">PROTECTED</span>':'';let btn=prot?'<span style="color:#94a3b8;font-size:12px;font-weight:600">System Admin</span>':'<button onclick="del('+m.id+')" style="color:#dc2626;font-weight:700;border:1px solid #fee2e2;background:#fff;border-radius:999px;padding:6px 14px;cursor:pointer;font-size:12px">Delete</button>';let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'—';h+='<tr style="border-bottom:1px solid #f8fafc"><td style="padding:16px"><div style="display:flex;align-items:center"><b style="font-size:14px">'+m.staff_no+'</b>'+badge+'</div><div style="font-weight:700;margin-top:2px">'+m.full_names+'</div><div style="font-size:12px;color:#64748b">'+m.email+'</div><div style="font-size:11px;color:#64748b;margin-top:4px">Joined: '+(m.month_joined||'—')+'</div></td><td style="padding:16px"><span style="font-weight:600;background:#f1f5f9;padding:6px 12px;border-radius:999px;font-size:12px">'+m.project+'</span></td><td style="padding:16px"><div style="font-size:12px"><b>G:</b> '+(m.guardian_id||'—')+' <b>S:</b> '+(m.spouse_id||'—')+'</div><div style="font-size:11px;color:#64748b;margin-top:2px"><b>Father:</b> '+(m.father_id||'—')+' <b>Mother:</b> '+(m.mother_id||'—')+'</div><div style="font-size:11px;margin-top:4px"><b>Kids:</b> '+kids+'</div></td><td style="padding:16px">'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key=""" + ADMIN_KEY + """',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/register")
def admin_register_page():
    return redirect("/register")

@app.route("/api/stats")
def api_stats():
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        breakdown = {}
        for p in PROJECTS:
            breakdown[p] = conn.execute("SELECT COUNT(*) FROM users WHERE project=? AND email != ?", (p, ADMIN_EMAIL)).fetchone()[0]
        return jsonify({"total_members": total, "projects_breakdown": breakdown})
    finally:
        conn.close()

@app.route("/api/members")
def api_members():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC", (ADMIN_EMAIL,)).fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/members_admin")
def api_members_admin():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users ORDER BY id DESC").fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json(silent=True)
    conn = get_db()
    try:
        user = conn.execute("SELECT password,api_key FROM users WHERE email=?", (data.get("email"),)).fetchone()
        if not user or not check_password_hash(user["password"], data.get("password","")):
            return jsonify({"error": "Invalid credentials"}), 401
        return jsonify({"key": user["api_key"]})
    finally:
        conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json(silent=True)
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "Email and password are required"}), 400
    conn = get_db()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (data["email"],)).fetchone():
            return jsonify({"error": "Email already exists - use a different email"}), 400
        api_key = "lonma_" + secrets.token_hex(16)
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (data.get("staff_no",""), data.get("full_names",""), data.get("project","HQ"), data["email"], generate_password_hash(data["password"]), api_key, data.get("month_joined",""), data.get("father_id",""), data.get("mother_id",""), data.get("guardian_id",""), data.get("spouse_id",""), data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5","")))
        conn.commit()
        return jsonify({"message": "Member registered successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS":
        return "", 200
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return jsonify({"error": "Admin key required"}), 401
    conn = get_db()
    try:
        u = conn.execute("SELECT email FROM users WHERE id=?", (member_id,)).fetchone()
        if not u or u["email"]==ADMIN_EMAIL:
            return jsonify({"error": "Cannot delete Protected Admin"}), 403
        conn.execute("DELETE FROM users WHERE id=?", (member_id,))
        conn.commit()
        return jsonify({"message": "Deleted"})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
