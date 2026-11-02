
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
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0)')
    if not conn.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ","Oct 2026",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
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
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#f8fafc;color:#0f172a}
.header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 20px;position:sticky;top:0}
.brand{display:flex;gap:10px;align-items:center}.brand-icon{width:32px;height:32px;background:#0f172a;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700}
.brand-name{font-weight:700;font-size:13px}.brand-name span{font-size:10px;display:block;color:#64748b;text-transform:uppercase;letter-spacing:.6px}
.nav{display:flex;gap:4px}.nav a{padding:6px 12px;border-radius:7px;font-size:13px;color:#64748b;text-decoration:none;font-weight:500}.nav a.active{background:#0f172a;color:#fff}
.page{max-width:1100px;margin:0 auto;padding:20px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:12px;overflow:hidden}
.card-h{padding:16px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center}
.row{padding:14px 18px;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:14px}
.btn{height:38px;padding:0 14px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;color:#0f172a;display:inline-flex;align-items:center}
.btn-dark{background:#0f172a;color:#fff;border-color:#0f172a}
table{width:100%;border-collapse:collapse}th{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;text-align:left}td{padding:12px 14px;font-size:13px;border-bottom:1px solid #f1f5f9}
.input{width:100%;height:38px;padding:0 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px}label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;margin-bottom:5px;display:block}
.badge{font-size:11px;padding:3px 8px;border-radius:6px;background:#f1f5f9;border:1px solid #e2e8f0}
</style>
"""

# HOME - NO TOTAL FEEDS, ONLY PROJECT DISTRIBUTION
@app.route("/")
def home():
    html = "<!DOCTYPE html><html><head><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>LONMA</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" + CSS + "</head><body><div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>WELFARE MANAGEMENT</span></div></div><div class='nav'><a href='/' class='active'>Overview</a><a href='/members'>Members</a></div></div><div class='page'><div class='card'><div class='card-h'><div><div style='font-weight:700;font-size:15px'>Project Distribution</div><div style='font-size:12px;color:#64748b;margin-top:2px'>Members per project</div></div><a href='/members' class='btn'>View Members</a></div><div id='breakdown'><div class='row'>Loading...</div></div></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();let h='';for(let k in d.projects_breakdown){h+='<div class=\"row\"><span>'+k+'</span><b>'+d.projects_breakdown[k]+'</b></div>';}document.getElementById('breakdown').innerHTML=h;}load();</script></body></html>"
    return render_template_string(html)

@app.route("/members")
def members_page():
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Members - LONMA</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" + CSS + "</head><body><div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Members</span></div></div><div class='nav'><a href='/'>Overview</a><a href='/members' class='active'>Members</a></div></div><div class='page'><div class='card'><div style='padding:10px 12px;border-bottom:1px solid #e2e8f0;display:flex;gap:8px'><input class='input' id='q' placeholder='Search...' style='max-width:220px;height:34px' oninput='fil()'><select class='input' id='pf' style='max-width:160px;height:34px' onchange='fil()'><option value=''>All Projects</option>" + opts + "</select></div><div style='overflow:auto'><table id='tbl'></table></div></div></div><script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function render(l){let h='<tr><th>Staff No</th><th>Name</th><th>Project</th><th>Joined</th></tr>';l.forEach(m=>{h+='<tr><td style=\"font-weight:600\">'+m.staff_no+'</td><td>'+m.full_names+'</td><td><span class=\"badge\">'+m.project+'</span></td><td style=\"font-size:11px;color:#64748b\">'+(m.month_year_joined||'')+'</td></tr>';});document.getElementById('tbl').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pp=document.getElementById('pf').value;render(all.filter(m=>{let t=(m.full_names+m.staff_no+m.project).toLowerCase();return t.includes(qq)&&(!pp||m.project==pp);}));}load();</script></body></html>"
    return render_template_string(html)

@app.route("/admin")
def admin_login():
    html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Login</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" + CSS + "</head><body><div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin Only</span></div></div><div class='nav'><a href='/admin' class='active'>Admin</a></div></div><div class='page' style='max-width:400px'><div class='card'><div class='card-h'><b>Admin Login - Private</b></div><div style='padding:20px'><label>Email</label><input class='input' id='email' value='admin@lonma.com'><div style='margin-top:10px'><label>Password</label><input class='input' id='pass' type='password' value='admin123'></div><button class='btn btn-dark' style='width:100%;margin-top:16px;justify-content:center' onclick='login()'>Login</button><p id='msg' style='font-size:12px;margin-top:10px;text-align:center;color:#dc2626'></p></div></div></div><script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok){location.href='/admin/dashboard?key='+j.key;}else{document.getElementById('msg').textContent=j.error;}}</script></body></html>"
    return render_template_string(html)

@app.route("/admin/dashboard")
def admin_dashboard():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin Dashboard</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" + CSS + "</head><body><div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin - Full Control</span></div></div><div class='nav'><a href='/admin/dashboard?key=" + ADMIN_KEY + "' class='active'>Dashboard</a><a href='/admin/register?key=" + ADMIN_KEY + "'>Register</a></div></div><div class='page'><div style='display:flex;justify-content:space-between;margin-bottom:12px'><div><b>Admin - Full Control</b><div style='font-size:11px;color:#64748b'><span id='cnt'>0</span> records</div></div><a href='/admin/register?key=" + ADMIN_KEY + "' class='btn btn-dark'>+ Register Member</a></div><div class='card'><div style='padding:10px 12px;border-bottom:1px solid #e2e8f0;display:flex;gap:8px'><input class='input' id='q' placeholder='Search...' style='max-width:220px;height:34px' oninput='fil()'><select class='input' id='pf' style='max-width:160px;height:34px' onchange='fil()'><option value=''>All Projects</option>" + opts + "</select></div><div style='overflow:auto'><table id='tbl'></table></div></div></div><script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;document.getElementById('cnt').textContent=d.total;render(d.members);}function render(l){let h='<tr><th>Staff</th><th>Name</th><th>Project</th><th>Email</th><th>Action</th></tr>';l.forEach(m=>{let prot=m.is_protected==1||m.email=='admin@lonma.com';let badge=prot?'<span style=\"font-size:9px;background:#0f172a;color:#fff;padding:2px 6px;border-radius:4px;margin-left:6px\">PROTECTED</span>':'';let btn=prot?'<span style=\"font-size:11px;color:#94a3b8\">System</span>':'<button onclick=\"del('+m.id+')\" style=\"height:30px;padding:0 10px;border-radius:6px;border:1px solid #fee2e2;background:#fff;color:#dc2626;font-size:12px;font-weight:600;cursor:pointer\">Delete</button>';h+='<tr style=\"'+(prot?'background:#f8fafc':'')+'\"><td style=\"font-weight:600\">'+m.staff_no+' '+badge+'</td><td>'+m.full_names+'</td><td><span class=\"badge\">'+m.project+'</span></td><td>'+m.email+'</td><td>'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pp=document.getElementById('pf').value;render(all.filter(m=>{let t=(m.full_names+m.staff_no+m.email).toLowerCase();return t.includes(qq)&&(!pp||m.project==pp);}));}async function del(id){if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?key=" + ADMIN_KEY + "',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script></body></html>"
    return render_template_string(html)

@app.route("/admin/register")
def admin_register():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = "<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register</title><link href='https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap' rel='stylesheet'>" + CSS + "</head><body><div class='header'><div class='brand'><div class='brand-icon'>L</div><div class='brand-name'>LONMA<span>Admin</span></div></div><div class='nav'><a href='/admin/dashboard?key=" + ADMIN_KEY + "' class='active'>Dashboard</a></div></div><div class='page' style='max-width:700px'><div class='card'><div class='card-h'><b>Register New Member</b></div><div style='padding:18px'><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px'><div><label>Staff No *</label><input class='input' id='staff_no'></div><div><label>Project *</label><select class='input' id='project'>" + opts + "</select></div></div><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px'><div><label>Full Names *</label><input class='input' id='full_names'></div><div><label>Email *</label><input class='input' id='email'></div></div><div style='display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px'><div><label>Password *</label><input class='input' id='password' type='password'></div><div><label>Phone</label><input class='input' id='phone'></div></div><div style='margin-top:10px'><label>Month/Year</label><input class='input' id='month_year_joined'></div><button class='btn btn-dark' style='width:100%;margin-top:18px;justify-content:center' onclick='doReg()'>Create Member</button><p id='msg' style='font-size:12px;margin-top:10px;text-align:center'></p></div></div></div><script>async function doReg(){let f=['staff_no','project','full_names','email','password','phone','month_year_joined'];let d={};f.forEach(k=>d[k]=document.getElementById(k).value);let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();let m=document.getElementById('msg');m.textContent=j.error||j.message;m.style.color=r.ok?'#16a34a':'#dc2626';if(r.ok)setTimeout(()=>location.href='/admin/dashboard?key=" + ADMIN_KEY + "',700);}</script></body></html>"
    return render_template_string(html)

@app.route("/api/stats")
def api_stats():
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown = {}
        for p in PROJECTS:
            breakdown[p] = conn.execute("SELECT COUNT(*) FROM users WHERE project=?", (p,)).fetchone()[0]
        return jsonify({"total_members": total, "projects_breakdown": breakdown})
    finally:
        conn.close()

@app.route("/api/members")
def api_members():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,month_year_joined,email,phone,is_protected FROM users ORDER BY is_protected DESC, id DESC").fetchall()
        return jsonify({"total": len(rows), "members": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/admin/login", methods=["POST"])
def admin_login_api():
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
        api_key = "lonma_" + secrets.token_hex(16)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,phone,api_key) VALUES (?,?,?,?,?,?,?,?)",
            (data.get("staff_no","HQ/"+secrets.token_hex(2).upper()), data.get("full_names",""), data.get("project","HQ"), data.get("month_year_joined",""), data["email"], generate_password_hash(data["password"]), data.get("phone",""), api_key))
        conn.execute("COMMIT")
        return jsonify({"message": "Member created"}), 201
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS":
        return "", 200
    key = request.args.get("key") or request.args.get("api_key")
    if key != ADMIN_KEY:
        return jsonify({"error": "Admin key required"}), 401
    conn = get_db()
    try:
        user = conn.execute("SELECT id,email,is_protected,role FROM users WHERE id=?", (member_id,)).fetchone()
        if not user or user["is_protected"]==1 or user["email"]==ADMIN_EMAIL:
            return jsonify({"error": "Cannot delete Protected Admin"}), 403
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM users WHERE id=?", (member_id,))
        conn.execute("COMMIT")
        return jsonify({"message": "Deleted"})
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
