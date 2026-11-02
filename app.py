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
    # Add new columns if DB exists from old version
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
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#f5f6f8;color:#111827}
.header{height:64px;background:#fff;border-bottom:1px solid #e5e7eb;display:flex;align-items:center;justify-content:space-between;padding:0 16px;position:sticky;top:0;z-index:10}
.brand{display:flex;gap:10px;align-items:center}.brand-icon{width:36px;height:42px;background:#111827;color:#fff;border-radius:10px;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}
.brand-name{font-weight:800;font-size:15px;line-height:1.1}.brand-name span{font-size:11px;display:block;color:#6b7280;font-weight:700;letter-spacing:.6px;line-height:1.2}
.nav{display:flex;gap:8px;overflow:auto}.nav a{padding:8px 16px;border-radius:10px;font-size:14px;color:#6b7280;text-decoration:none;font-weight:600;white-space:nowrap}.nav a.active{background:#111827;color:#fff}
.page{max-width:700px;margin:0 auto;padding:12px}
.card{background:#fff;border:1px solid #e5e7eb;border-radius:16px;margin-bottom:12px;overflow:hidden}
.card-pad{padding:18px 20px}
.label{font-size:11px;font-weight:700;color:#6b7280;text-transform:uppercase;letter-spacing:.8px;margin-bottom:6px}
.value{font-size:28px;font-weight:800;color:#111827}
.value.green{color:#16a34a}
.row{padding:14px 20px;border-bottom:1px solid #f3f4f6;display:flex;justify-content:space-between;font-size:15px}
.row b{font-weight:700}
.btn{height:38px;padding:0 16px;border-radius:10px;border:1px solid #e5e7eb;background:#fff;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;color:#111827;display:inline-flex;align-items:center}
table{width:100%;border-collapse:collapse}th{font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;padding:10px 14px;background:#f9fafb;border-bottom:1px solid #e5e7eb;text-align:left}td{padding:12px 14px;font-size:13px;border-bottom:1px solid #f3f4f6}
.input{width:100%;height:38px;padding:0 12px;border:1px solid #e5e7eb;border-radius:8px;font-size:13px}label{font-size:10px;font-weight:700;color:#6b7280;text-transform:uppercase;margin-bottom:5px;display:block}
.section-title{font-size:12px;font-weight:800;color:#111827;text-transform:uppercase;letter-spacing:.8px;margin:18px 0 10px 0;padding-bottom:8px;border-bottom:1px solid #f3f4f6}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:10px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px}
</style>
"""

@app.route("/")
def home():
    html = """<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LONMA</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE<br>MANAGEMENT<br>SYSTEM</span></div></div><div class='nav'><a href='/' class='active'>Overview</a><a href='/members'>Members</a><a href='/register'>Register</a></div></div>
<div class='page'>
<div class='card'><div class='card-pad'><div class='label'>Total Members</div><div class='value' id='total'>0</div></div></div>
<div class='card'><div class='card-pad'><div class='label'>Projects</div><div class='value'>12</div></div></div>
<div class='card'><div class='card-pad'><div class='label'>Status</div><div class='value green'>Active</div></div></div>
<div class='card'><div style='padding:16px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #f3f4f6'><div><div style='font-weight:700;font-size:16px'>Project Distribution</div><div style='font-size:13px;color:#6b7280'>Members per project</div></div><a href='/members' class='btn'>View All</a></div><div id='breakdown'></div></div>
</div>
<script>
async function load(){
 let r=await fetch('/api/stats');
 let d=await r.json();
 document.getElementById('total').textContent=d.total_members;
 let h='';
 for(let k in d.projects_breakdown){ h+='<div class="row"><span>'+k+'</span><b>'+d.projects_breakdown[k]+'</b></div>'; }
 document.getElementById('breakdown').innerHTML=h;
}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/members")
def members_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Members</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE<br>MANAGEMENT<br>SYSTEM</span></div></div><div class='nav'><a href='/'>Overview</a><a href='/members' class='active'>Members</a><a href='/register'>Register</a></div></div>
<div class='page' style='max-width:900px'><div class='card'><div style='padding:10px;border-bottom:1px solid #e5e7eb'><input class='input' id='q' placeholder='Search by name, staff no, project...' oninput='fil()'></div><div style='overflow:auto'><table id='tbl'></table></div></div></div>
<script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function render(l){let h='<tr><th>Staff No</th><th>Name</th><th>Project</th><th>Joined</th><th>Family IDs</th></tr>';if(l.length==0){h+='<tr><td colspan=5 style="padding:30px;text-align:center;color:#6b7280">No members yet - Register from your Excel data</td></tr>';}else{l.forEach(m=>{let fam=(m.father_id||'-')+' / '+(m.mother_id||'-');h+='<tr><td>'+m.staff_no+'</td><td><div style="font-weight:600">'+m.full_names+'</div><div style="font-size:11px;color:#6b7280">Spouse: '+(m.spouse_id||'-')+' | Guardian: '+(m.guardian_id||'-')+'</div></td><td>'+m.project+'</td><td>'+(m.month_joined||'-')+'</td><td><div style="font-size:11px">Kids: '+(m.kid1||'')+' '+(m.kid2||'')+' '+(m.kid3||'')+'</div><div style="font-size:11px;color:#6b7280">'+fam+'</div></td></tr>';});}document.getElementById('tbl').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();render(all.filter(m=>(m.full_names+m.staff_no+m.project+(m.father_id||'')+(m.spouse_id||'')).toLowerCase().includes(qq)));}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/register")
def register_page():
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register - Welfare Data</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE<br>MANAGEMENT<br>SYSTEM</span></div></div><div class='nav'><a href='/'>Overview</a><a href='/members'>Members</a><a href='/register' class='active'>Register</a></div></div>
<div class='page' style='max-width:700px'>
<div class='card'><div style='padding:16px 20px;border-bottom:1px solid #e5e7eb'><b>WELFARE REGISTRATION FORM</b><div style='font-size:11px;color:#6b7280;margin-top:4px'>Based on your WELFARE_DATA.xlsx structure</div></div><div style='padding:18px'>
<div class='section-title'>Staff Information</div>
<div class='grid2'><div><label>Staff No & Full Names (Staff No)</label><input class='input' id='staff_no' placeholder='e.g. PWANI/001'></div><div><label>Project</label><select class='input' id='project'>""" + opts + """</select></div></div>
<div style='margin-top:10px' class='grid2'><div><label>Month & Year Joined</label><input class='input' id='month_joined' placeholder='e.g. Jan 2024'></div><div><label>Full Names</label><input class='input' id='full_names' placeholder='Full Name'></div></div>
<div style='margin-top:10px' class='grid2'><div><label>Email (Login)</label><input class='input' id='email' placeholder='email@lonma.com'></div><div><label>Password</label><input class='input' id='password' type='password' placeholder='password'></div></div>

<div class='section-title'>Parents IDs</div>
<div class='grid2'><div><label>Father ID</label><input class='input' id='father_id' placeholder='Father ID No.'></div><div><label>Mother ID</label><input class='input' id='mother_id' placeholder='Mother ID No.'></div></div>

<div class='section-title'>Guardian & Spouse</div>
<div class='grid2'><div><label>Guardian ID No.</label><input class='input' id='guardian_id' placeholder='e.g. 22400966'></div><div><label>Spouse ID No.</label><input class='input' id='spouse_id' placeholder='e.g. 23601476'></div></div>

<div class='section-title'>Kids Birth Certificates Numbers</div>
<div class='grid3'><div><label>Kid 1</label><input class='input' id='kid1' placeholder='e.g. 42107914'></div><div><label>Kid 2</label><input class='input' id='kid2' placeholder='e.g. 111041990'></div><div><label>Kid 3</label><input class='input' id='kid3'></div></div>
<div style='margin-top:10px' class='grid2'><div><label>Kid 4</label><input class='input' id='kid4'></div><div><label>Kid 5</label><input class='input' id='kid5'></div></div>

<button class='btn' style='width:100%;margin-top:20px;background:#111827;color:#fff;justify-content:center;height:44px;font-size:14px' onclick='doReg()'>Register Member with Welfare Data</button>
<p id='msg' style='font-size:12px;margin-top:12px;text-align:center'></p>
</div></div>
</div>
<script>async function doReg(){let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value};if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Full Names, Email, Password required';document.getElementById('msg').style.color='#dc2626';return;}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();let m=document.getElementById('msg');m.textContent=j.error||j.message;m.style.color=r.ok?'#16a34a':'#dc2626';if(r.ok){m.textContent+=' - View in Members';}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin")
def admin_login_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin Only</span></div></div></div>
<div class='page' style='max-width:400px'><div class='card'><div style='padding:16px 20px;border-bottom:1px solid #e5e7eb'><b>Admin Login - Private</b></div><div style='padding:20px'><label>Email</label><input class='input' id='email' value='admin@lonma.com'><div style='margin-top:10px'><label>Password</label><input class='input' id='pass' type='password' value='admin123'></div><button class='btn' style='width:100%;margin-top:16px;background:#111827;color:#fff;justify-content:center' onclick='login()'>Login</button><p id='msg' style='font-size:12px;margin-top:10px;text-align:center;color:#dc2626'></p></div></div></div>
<script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok){location.href='/admin/dashboard?key='+j.key;}else{document.getElementById('msg').textContent=j.error;}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/dashboard")
def admin_dashboard():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Dashboard</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin - Full Control</span></div></div><div class='nav'><a href='/admin/dashboard?key=""" + ADMIN_KEY + """' class='active'>Dashboard</a><a href='/admin/register?key=""" + ADMIN_KEY + """'>Register</a><a href='/'>Overview</a></div></div>
<div class='page' style='max-width:1000px'><div style='display:flex;justify-content:space-between;margin-bottom:12px'><b>Admin Panel - Welfare Data View</b><a href='/admin/register?key=""" + ADMIN_KEY + """' class='btn' style='background:#111827;color:#fff'>+ Register</a></div><div class='card'><div style='overflow:auto'><table id='tbl'></table></div></div></div>
<script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='<tr><th>Staff</th><th>Name</th><th>Project</th><th>Joined</th><th>Guardian/Spouse</th><th>Kids</th><th>Action</th></tr>';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let badge=prot?'<span style="font-size:9px;background:#111827;color:#fff;padding:2px 6px;border-radius:4px;margin-left:6px">PROTECTED</span>':'';let btn=prot?'<span style="color:#9ca3af;font-size:11px">System</span>':'<button onclick="del('+m.id+')" style="color:#dc2626;font-weight:700;border:1px solid #fee2e2;background:#fff;border-radius:6px;padding:4px 10px;cursor:pointer">Delete</button>';let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<tr><td>'+m.staff_no+' '+badge+'</td><td><b>'+m.full_names+'</b><br><span style="font-size:11px;color:#6b7280">'+m.email+'</span><br><span style="font-size:11px">Father:'+(m.father_id||'-')+' Mother:'+(m.mother_id||'-')+'</span></td><td>'+m.project+'</td><td>'+(m.month_joined||'-')+'</td><td><div style="font-size:11px">G:'+(m.guardian_id||'-')+'<br>S:'+(m.spouse_id||'-')+'</div></td><td style="font-size:11px">'+kids+'</td><td>'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;}async function del(id){if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?key=""" + ADMIN_KEY + """',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/register")
def admin_register_page():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Register Welfare</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap' rel='stylesheet'>""" + CSS + """</head><body>
<div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin</span></div></div><div class='nav'><a href='/admin/dashboard?key=""" + ADMIN_KEY + """' class='active'>Dashboard</a></div></div>
<div class='page' style='max-width:700px'><div class='card'><div style='padding:16px 20px;border-bottom:1px solid #e5e7eb'><b>Register - Welfare Data (Admin)</b></div><div style='padding:18px'>
<div class='grid2'><div><label>Staff No</label><input class='input' id='staff_no'></div><div><label>Project</label><select class='input' id='project'>""" + opts + """</select></div></div>
<div style='margin-top:10px' class='grid2'><div><label>Month & Year Joined</label><input class='input' id='month_joined'></div><div><label>Full Names</label><input class='input' id='full_names'></div></div>
<div style='margin-top:10px' class='grid2'><div><label>Email</label><input class='input' id='email'></div><div><label>Password</label><input class='input' id='password' type='password'></div></div>
<div class='section-title'>Parents IDs</div><div class='grid2'><div><label>Father ID</label><input class='input' id='father_id'></div><div><label>Mother ID</label><input class='input' id='mother_id'></div></div>
<div class='section-title'>Guardian & Spouse</div><div class='grid2'><div><label>Guardian ID</label><input class='input' id='guardian_id'></div><div><label>Spouse ID</label><input class='input' id='spouse_id'></div></div>
<div class='section-title'>Kids Birth Certificates</div><div class='grid3'><div><label>Kid 1</label><input class='input' id='kid1'></div><div><label>Kid 2</label><input class='input' id='kid2'></div><div><label>Kid 3</label><input class='input' id='kid3'></div></div><div style='margin-top:10px' class='grid2'><div><label>Kid 4</label><input class='input' id='kid4'></div><div><label>Kid 5</label><input class='input' id='kid5'></div></div>
<button class='btn' style='width:100%;margin-top:16px;background:#111827;color:#fff;justify-content:center' onclick='doReg()'>Create</button><p id='msg' style='font-size:12px;margin-top:10px;text-align:center'></p></div></div></div>
<script>async function doReg(){let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value};let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();let m=document.getElementById('msg');m.textContent=j.error||j.message;m.style.color=r.ok?'#16a34a':'#dc2626';if(r.ok)setTimeout(()=>location.href='/admin/dashboard?key=""" + ADMIN_KEY + """',700);}</script>
</body></html>"""
    return render_template_string(html)

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
        return jsonify({"error": "email and password required"}), 400
    conn = get_db()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (data["email"],)).fetchone():
            return jsonify({"error": "Email already exists - use new email"}), 400
        api_key = "lonma_" + secrets.token_hex(16)
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (data.get("staff_no",""), data.get("full_names",""), data.get("project","HQ"), data["email"], generate_password_hash(data["password"]), api_key, data.get("month_joined",""), data.get("father_id",""), data.get("mother_id",""), data.get("guardian_id",""), data.get("spouse_id",""), data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5","")))
        conn.commit()
        return jsonify({"message": "Created with Welfare Data"}), 201
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
