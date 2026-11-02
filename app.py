from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash

app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem"]

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
    row = conn.execute("SELECT id FROM users WHERE email='admin@lonma.com'").fetchone()
    if not row:
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?,1)", ("HQ/001","System Administrator","HQ","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","lonma_api_key_12345",1))
    conn.close()

init_db()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-KEY')
    response.headers.add('Access-Control-Allow-Methods', 'GET,POST,DELETE,OPTIONS')
    return response

CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#f8fafc;color:#0f172a}
.header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 20px;position:sticky;top:0;z-index:10}
.brand{display:flex;gap:10px;align-items:center}.brand-icon{width:32px;height:32px;background:#0f172a;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.brand-name{font-weight:700;font-size:13px}.brand-name span{font-size:10px;display:block;color:#64748b;text-transform:uppercase;letter-spacing:.6px}
.nav{display:flex;gap:4px}.nav a{padding:6px 12px;border-radius:7px;font-size:13px;color:#64748b;text-decoration:none;font-weight:500}.nav a.active{background:#0f172a;color:#fff}
.page{max-width:1100px;margin:0 auto;padding:20px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px}
.stat{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px}.stat label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px}.stat b{font-size:20px;font-weight:700;display:block;margin-top:2px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden}
.card-h{padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center}
.row{padding:12px 18px;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:13px}
.btn{height:36px;padding:0 14px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;color:#0f172a;display:inline-flex;align-items:center}
.btn-dark{background:#0f172a;color:#fff;border-color:#0f172a}
table{width:100%;border-collapse:collapse}th{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;text-align:left}td{padding:12px 14px;font-size:13px;border-bottom:1px solid #f1f5f9}
.input{width:100%;height:38px;padding:0 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px}label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;margin-bottom:5px;display:block}
.badge{font-size:11px;padding:3px 8px;border-radius:6px;background:#f1f5f9;border:1px solid #e2e8f0}
@media(max-width:700px){.stats{grid-template-columns:1fr}}
</style>
"""

@app.route("/")
def home():
    opts = ""
    page = """
<!DOCTYPE html>
<html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA Welfare</title>
""" + CSS + """
</head><body>
<div class="header">
  <div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management System</span></div></div>
  <div class="nav"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a></div>
</div>
<div class="page">
  <div class="stats">
    <div class="stat"><label>Total Members</label><b id="total">0</b><div style="font-size:11px;color:#94a3b8">Active records</div></div>
    <div class="stat"><label>Projects</label><b>12</b><div style="font-size:11px;color:#94a3b8">All locations operational</div></div>
    <div class="stat"><label>Status</label><b style="color:#16a34a">Active</b><div style="font-size:11px;color:#94a3b8">Production system</div></div>
  </div>
  <div class="card">
    <div class="card-h"><div><div style="font-weight:600;font-size:13px">Project Distribution</div><div style="font-size:11px;color:#64748b">Members per project location</div></div><a href="/dashboard" class="btn">View All Members</a></div>
    <div id="breakdown"><div class="row">Loading...</div></div>
  </div>
</div>
<script>
async function loadData(){
  try{
    const res = await fetch('/api/stats');
    const data = await res.json();
    document.getElementById('total').textContent = data.total_members;
    const colors = {"Pwani Oil Products":"#f59e0b","Java House":"#7c3aed","SJ Johnson":"#dc2626","Kanji":"#059669","HQ":"#0f172a","Antonio":"#db2777","TF-TDs":"#0891b2","TF-MT":"#65a30d","TF-LM":"#ea580c","GCB-MT":"#4f46e5","GCB-Ws":"#0d9488","Hichem":"#9333ea"};
    let html = "";
    for(const proj in data.projects_breakdown){
      const count = data.projects_breakdown[proj];
      const color = colors[proj] || "#64748b";
      html += '<div class="row"><span><span style="width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:7px;background:'+color+'"></span>'+proj+'</span><b>'+count+'</b></div>';
    }
    document.getElementById('breakdown').innerHTML = html || '<div class="row">No members yet</div>';
  }catch(err){
    document.getElementById('breakdown').innerHTML = '<div class="row" style="color:#dc2626">Failed to load - retrying...</div>';
    setTimeout(loadData, 1000);
  }
}
loadData();
</script>
</body></html>
"""
    return render_template_string(page)

@app.route("/dashboard")
def dashboard():
    project_options = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    page = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - LONMA</title>
""" + CSS + """
</head><body>
<div class="header">
  <div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management</span></div></div>
  <div class="nav"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div>
</div>
<div class="page">
  <div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:12px">
    <div><div style="font-weight:700">Members</div><div style="font-size:11px;color:#64748b"><span id="cnt">0</span> records</div></div>
    <a href="/register" class="btn btn-dark">+ New Member</a>
  </div>
  <div class="card">
    <div style="padding:10px 12px;border-bottom:1px solid #e2e8f0;display:flex;gap:8px">
      <input class="input" id="q" placeholder="Search staff, name..." style="max-width:220px;height:34px" oninput="applyFilter()">
      <select class="input" id="pf" style="max-width:160px;height:34px" onchange="applyFilter()"><option value="">All Projects</option>""" + project_options + """</select>
    </div>
    <div style="overflow:auto"><table id="tbl"></table></div>
  </div>
</div>
<script>
let allMembers = [];
async function loadMembers(){
  const res = await fetch('/api/members');
  const data = await res.json();
  allMembers = data.members;
  document.getElementById('cnt').textContent = data.total;
  renderTable(data.members);
}
function renderTable(list){
  let h = '<tr><th>Staff No</th><th>Member</th><th>Project</th><th>Contact</th><th>Action</th></tr>';
  list.forEach(m=>{
    const isProtected = m.is_protected == 1 || m.email == 'admin@lonma.com';
    const badge = isProtected ? '<span style="font-size:9px;background:#0f172a;color:#fff;padding:2px 6px;border-radius:4px;margin-left:6px">PROTECTED</span>' : '';
    const btn = isProtected ? '<span style="font-size:11px;color:#94a3b8">System</span>' : '<button onclick="deleteMember('+m.id+')" style="height:30px;padding:0 10px;border-radius:6px;border:1px solid #fee2e2;background:#fff;color:#dc2626;font-size:12px;font-weight:600;cursor:pointer">Delete</button>';
    h += '<tr style="'+(isProtected ? 'background:#f8fafc' : '')+'"><td style="font-weight:600">'+m.staff_no+' '+badge+'</td><td><div style="font-weight:500">'+m.full_names+'</div><div style="font-size:11px;color:#64748b">'+(m.month_year_joined||'')+'</div></td><td><span class="badge">'+m.project+'</span></td><td style="font-size:12px">'+m.email+'</td><td>'+btn+'</td></tr>';
  });
  document.getElementById('tbl').innerHTML = h;
}
function applyFilter(){
  const qq = document.getElementById('q').value.toLowerCase();
  const pp = document.getElementById('pf').value;
  const filtered = allMembers.filter(m=>{
    const txt = (m.full_names + m.staff_no + m.email).toLowerCase();
    return txt.includes(qq) && (!pp || m.project == pp);
  });
  renderTable(filtered);
}
async function deleteMember(id){
  if(!confirm('Delete member '+id+'?')) return;
  const res = await fetch('/api/members/'+id+'?api_key=lonma_api_key_12345', {method:'DELETE'});
  const j = await res.json();
  if(!res.ok){ alert(j.error); return; }
  loadMembers();
}
loadMembers();
</script>
</body></html>
"""
    return render_template_string(page)

@app.route("/register")
def register_page():
    project_options = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    page = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - LONMA</title>
""" + CSS + """
</head><body>
<div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div>
<div class="page" style="max-width:700px"><div class="card"><div class="card-h"><b>New Member Registration</b></div><div style="padding:18px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Staff Number *</label><input class="input" id="staff_no"></div><div><label>Project *</label><select class="input" id="project">""" + project_options + """</select></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><div><label>Full Names *</label><input class="input" id="full_names"></div><div><label>Email *</label><input class="input" id="email"></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><div><label>Password *</label><input class="input" id="password" type="password"></div><div><label>Phone</label><input class="input" id="phone"></div></div>
<div style="margin-top:10px"><label>Month / Year Joined</label><input class="input" id="month_year_joined" placeholder="Nov 2026"></div>
<div style="margin-top:16px;border-top:1px solid #e2e8f0;padding-top:12px"><div style="font-size:12px;font-weight:600;margin-bottom:8px">Family</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Father ID</label><input class="input" id="father_id"></div><div><label>Mother ID</label><input class="input" id="mother_id"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><div><label>Guardian</label><input class="input" id="guardian_id"></div><div><label>Spouse</label><input class="input" id="spouse_id"></div></div></div>
<div style="margin-top:16px;border-top:1px solid #e2e8f0;padding-top:12px"><div style="font-size:12px;font-weight:600;margin-bottom:8px">Children</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Child 1</label><input class="input" id="kid1"></div><div><label>Child 2</label><input class="input" id="kid2"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><div><label>Child 3</label><input class="input" id="kid3"></div><div><label>Child 4</label><input class="input" id="kid4"></div></div><div style="margin-top:8px"><label>Child 5</label><input class="input" id="kid5"></div></div>
<button class="btn btn-dark" style="width:100%;margin-top:18px;justify-content:center" onclick="doRegister()">Create Member</button><p id="msg" style="font-size:12px;margin-top:10px;text-align:center"></p>
</div></div></div>
<script>
async function doRegister(){
  const fields = ["staff_no","project","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"];
  let data = {};
  fields.forEach(k=>{ data[k] = document.getElementById(k).value; });
  const res = await fetch('/api/register', {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(data)});
  const j = await res.json();
  const msg = document.getElementById('msg');
  msg.textContent = j.error || j.message;
  msg.style.color = res.ok ? '#16a34a' : '#dc2626';
  if(res.ok) setTimeout(()=>{ location.href='/dashboard'; }, 700);
}
</script>
</body></html>
"""
    return render_template_string(page)

@app.route("/api/stats")
def api_stats():
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown = {}
        for p in PROJECTS:
            cnt = conn.execute("SELECT COUNT(*) FROM users WHERE project=?", (p,)).fetchone()[0]
            breakdown[p] = cnt
        return jsonify({"total_members": total, "projects_breakdown": breakdown})
    finally:
        conn.close()

@app.route("/api/members")
def api_members():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,month_year_joined,email,phone,is_protected FROM users ORDER BY is_protected DESC, id DESC").fetchall()
        members = []
        for r in rows:
            members.append(dict(r))
        return jsonify({"total": len(members), "members": members})
    finally:
        conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json(silent=True)
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password required"}), 400
    if data.get("project") and data["project"] not in PROJECTS:
        return jsonify({"error": "Invalid project"}), 400
    conn = get_db()
    try:
        api_key = "lonma_" + secrets.token_hex(16)
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",
            (data.get("staff_no","HQ/"+secrets.token_hex(2).upper()), data.get("full_names",""), data.get("project","HQ"), data.get("month_year_joined",""), data["email"], generate_password_hash(data["password"]), data.get("phone",""), data.get("father_id",""), data.get("mother_id",""), data.get("guardian_id",""), data.get("spouse_id",""), data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5",""), api_key))
        conn.execute("COMMIT")
        return jsonify({"message": "Member created"}), 201
    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except:
            pass
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS":
        return "", 200
    conn = get_db()
    try:
        user = conn.execute("SELECT id,email,is_protected,role FROM users WHERE id=?", (member_id,)).fetchone()
        if not user:
            return jsonify({"error": "Member not found"}), 404
        if user["is_protected"] == 1 or user["email"] == "admin@lonma.com" or user["role"] == "Admin":
            return jsonify({"error": "Cannot delete Protected System Administrator"}), 403
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("DELETE FROM users WHERE id=?", (member_id,))
        conn.execute("COMMIT")
        return jsonify({"message": "Member deleted"})
    except Exception as e:
        try:
            conn.execute("ROLLBACK")
        except:
            pass
        return jsonify({"error": str(e)}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
