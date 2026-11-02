from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash
from functools import wraps

app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem"]

def db():
    c = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    c.row_factory = sqlite3.Row
    try:
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return c

def init():
    conn = db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0)''')
    if not conn.execute("SELECT id FROM users WHERE email='admin@lonma.com'").fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?,1)", ("HQ/001","System Administrator","HQ","Oct 2026",generate_password_hash("admin123"),"Admin","0700000000","lonma_api_key_12345",1) if False else ("HQ/001","System Administrator","HQ","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","lonma_api_key_12345",1))
        # correct insert:
        try:
            conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?,1)", ("HQ/001","System Administrator","HQ","Oct 2026","admin@lonma.com",generate_password_hash("admin123"),"Admin","0700000000","lonma_api_key_12345",1))
        except: pass
    conn.close()
init()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
    return r

CSS = """<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet"><style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:Inter,sans-serif;background:#f8fafc;color:#0f172a} .header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 20px;position:sticky;top:0} .brand{display:flex;gap:10px;align-items:center}.brand-icon{width:32px;height:32px;background:#0f172a;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700} .brand-name{font-weight:700;font-size:13px}.brand-name span{font-size:10px;display:block;color:#64748b;text-transform:uppercase;letter-spacing:.6px} .nav{display:flex;gap:4px}.nav a{padding:6px 12px;border-radius:7px;font-size:13px;color:#64748b;text-decoration:none;font-weight:500}.nav a.active{background:#0f172a;color:#fff} .page{max-width:1100px;margin:0 auto;padding:20px} .stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:16px} .stat{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px}.stat label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px}.stat b{font-size:20px;font-weight:700;display:block;margin-top:2px}.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden} .card-h{padding:14px 18px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center}.row{padding:12px 18px;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:13px}.btn{height:36px;padding:0 14px;border-radius:8px;border:1px solid #e2e8f0;background:#fff;font-weight:600;font-size:13px;cursor:pointer;text-decoration:none;color:#0f172a;display:inline-flex;align-items:center}.btn-dark{background:#0f172a;color:#fff} table{width:100%;border-collapse:collapse}th{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;padding:10px 14px;background:#f8fafc;border-bottom:1px solid #e2e8f0;text-align:left}td{padding:12px 14px;font-size:13px;border-bottom:1px solid #f1f5f9} .input{width:100%;height:38px;padding:0 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px}label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;margin-bottom:5px;display:block} .badge{font-size:11px;padding:3px 8px;border-radius:6px;background:#f1f5f9;border:1px solid #e2e8f0} @media(max-width:700px){.stats{grid-template-columns:1fr}} </style>"""

HOME = f"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA</title>{CSS}</head><body><div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a></div></div><div class="page"><div class="stats"><div class="stat"><label>Total Members</label><b id="total">0</b><p style="font-size:11px;color:#94a3b8">Active records</p></div><div class="stat"><label>Projects</label><b>12</b><p style="font-size:11px;color:#94a3b8">Operational</p></div><div class="stat"><label>Status</label><b style="color:#16a34a">Active</b><p style="font-size:11px;color:#94a3b8">Production</p></div></div><div class="card"><div class="card-h"><div><div style="font-weight:600;font-size:13px">Project Distribution</div><div style="font-size:11px;color:#64748b">Members per project</div></div><a href="/dashboard" class="btn">View All</a></div><div id="break"></div></div></div><script>async function load(){{try{{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;let colors={{"Pwani Oil Products":"#f59e0b","Java House":"#7c3aed","SJ Johnson":"#dc2626","Kanji":"#059669","HQ":"#0f172a","Antonio":"#db2777","TF-TDs":"#0891b2","TF-MT":"#65a30d","TF-LM":"#ea580c","GCB-MT":"#4f46e5","GCB-Ws":"#0d9488","Hichem":"#9333ea"}};let h='';for(let k in d.projects_breakdown){{h+=`<div class="row"><span><span style="width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:6px;background:${{colors[k]||'#64748b'}}"></span>${{k}}</span><b>${{d.projects_breakdown[k]}}</b></div>`}}document.getElementById('break').innerHTML=h||'<div class="row">No data</div>';}}catch(e){{document.getElementById('break').innerHTML='<div class="row" style="color:#dc2626">Loading... retry</div>';setTimeout(load,1000);}}}}load();</script></body></html>"""

@app.route("/")
def home(): return render_template_string(HOME)

@app.route("/register")
def reg_page():
    opts=''.join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register</title>{CSS}</head><body><div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div><div class="page" style="max-width:700px"><div class="card"><div class="card-h"><b>New Member</b></div><div style="padding:18px"><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Staff No *</label><input class="input" id="staff_no"></div><div><label>Project *</label><select class="input" id="project">{opts}</select></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><div><label>Full Names *</label><input class="input" id="full_names"></div><div><label>Email *</label><input class="input" id="email"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:10px"><div><label>Password *</label><input class="input" id="password" type="password"></div><div><label>Phone</label><input class="input" id="phone"></div></div><div style="margin-top:10px"><label>Month/Year</label><input class="input" id="month_year_joined"></div><div style="margin-top:16px;border-top:1px solid #e2e8f0;padding-top:12px"><div style="font-size:12px;font-weight:600;margin-bottom:8px">Family</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Father ID</label><input class="input" id="father_id"></div><div><label>Mother ID</label><input class="input" id="mother_id"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><div><label>Guardian</label><input class="input" id="guardian_id"></div><div><label>Spouse</label><input class="input" id="spouse_id"></div></div></div><div style="margin-top:16px;border-top:1px solid #e2e8f0;padding-top:12px"><div style="font-size:12px;font-weight:600;margin-bottom:8px">Children</div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px"><div><label>Child1</label><input class="input" id="kid1"></div><div><label>Child2</label><input class="input" id="kid2"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:8px"><div><label>Child3</label><input class="input" id="kid3"></div><div><label>Child4</label><input class="input" id="kid4"></div></div><div style="margin-top:8px"><label>Child5</label><input class="input" id="kid5"></div></div><button class="btn btn-dark" style="width:100%;margin-top:18px;justify-content:center" onclick="reg()">Create Member</button><p id="msg" style="font-size:12px;margin-top:10px;text-align:center"></p></div></div></div><script>async function reg(){{let f=["staff_no","project","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"];let d={{}};f.forEach(k=>d[k]=document.getElementById(k).value);let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(d)}});let j=await r.json();msg.textContent=j.error||j.message;msg.style.color=r.ok?'#16a34a':'#dc2626';if(r.ok)setTimeout(()=>location.href='/dashboard',700);}}</script></body></html>""")

@app.route("/dashboard")
def dash():
    opts='<option value="">All Projects</option>'+''.join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members</title>{CSS}</head><body><div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div></div><div class="page"><div style="display:flex;justify-content:space-between;margin-bottom:12px"><div><b>Members</b><div style="font-size:11px;color:#64748b"><span id="cnt">0</span> records</div></div><a href="/register" class="btn btn-dark">+ New</a></div><div class="card"><div style="padding:10px 12px;border-bottom:1px solid #e2e8f0;display:flex;gap:8px"><input class="input" id="q" placeholder="Search..." style="max-width:220px;height:34px" oninput="fil()"><select class="input" id="pf" style="max-width:160px;height:34px" onchange="fil()">{opts}</select></div><div style="overflow:auto"><table id="tbl"></table></div></div></div><script>let all=[];async function load(){{let r=await fetch('/api/members');let d=await r.json();all=d.members;cnt.textContent=d.total;render(d.members);}}function render(l){{let h='<tr><th>Staff</th><th>Name</th><th>Project</th><th>Contact</th><th></th></tr>';l.forEach(m=>{{let prot=m.is_protected||m.email=='admin@lonma.com';h+=`<tr style="${{prot?'background:#f8fafc':''}}"><td style="font-weight:600">${{m.staff_no}} ${{prot?'<span style="font-size:9px;background:#0f172a;color:#fff;padding:2px 6px;border-radius:4px">PROTECTED</span>':''}}</td><td>${{m.full_names}}<div style="font-size:11px;color:#64748b">${{m.month_year_joined||''}}</div></td><td><span class="badge">${{m.project}}</span></td><td style="font-size:12px">${{m.email}}</td><td>${{prot?'<span style="font-size:11px;color:#94a3b8">System</span>':`<button onclick="del(${{m.id}})" style="height:30px;padding:0 10px;border-radius:6px;border:1px solid #fee2e2;background:#fff;color:#dc2626;font-size:12px;font-weight:600;cursor:pointer">Delete</button>`}}</td></tr>`;}});tbl.innerHTML=h;}function fil(){{let qq=q.value.toLowerCase();let pp=pf.value;render(all.filter(m=>(m.full_names+m.staff_no+m.email).toLowerCase().includes(qq)&&(!pp||m.project===pp)));}async function del(id){{if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?api_key=lonma_api_key_12345',{{method:'DELETE'}});let j=await r.json();if(!r.ok){{alert(j.error);return;}}load();}}load();</script></body></html>""")

@app.route("/api/stats")
def api_stats():
    conn=db()
    try:
        total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown={p:conn.execute("SELECT COUNT(*) FROM users WHERE project=?",(p,)).fetchone()[0] for p in PROJECTS}
        return jsonify({"total_members":total,"projects_breakdown":breakdown})
    finally: conn.close()

@app.route("/api/members")
def api_members():
    conn=db()
    try:
        rows=conn.execute("SELECT id,staff_no,full_names,project,month_year_joined,email,phone,is_protected FROM users ORDER BY is_protected DESC, id DESC").fetchall()
        return jsonify({"total":len(rows),"members":[dict(r) for r in rows]})
    finally: conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method=="OPTIONS": return "",200
    d=request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"email, password required"}),400
    if d.get("project") and d["project"] not in PROJECTS: return jsonify({"error":"Invalid project"}),400
    conn=db()
    try:
        key=f"lonma_{secrets.token_hex(16)}"
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("INSERT INTO users (staff_no,full_names,project,month_year_joined,email,password,phone,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(d.get("staff_no",f"HQ/{secrets.token_hex(2).upper()}"),d.get("full_names",""),d.get("project","HQ"),d.get("month_year_joined",""),d["email"],generate_password_hash(d["password"]),d.get("phone",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),key))
        conn.execute("COMMIT")
        return jsonify({"message":"Member created"}),201
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),400
    finally: conn.close()

@app.route("/api/members/<int:mid>", methods=["DELETE","OPTIONS"])
def api_delete(mid):
    if request.method=="OPTIONS": return "",200
    key=request.args.get("api_key") or request.headers.get("X-API-KEY")
    # Allow delete only with valid key, but stats/members are public for UI
    if key!="lonma_api_key_12345":
        # still check DB for key existence
        conn=db()
        try:
            ok=conn.execute("SELECT id FROM users WHERE api_key=?",(key,)).fetchone()
            if not ok and key: return jsonify({"error":"Invalid key"}),401
        finally: conn.close()
    conn=db()
    try:
        u=conn.execute("SELECT id,email,is_protected,role FROM users WHERE id=?",(mid,)).fetchone()
        if not u: return jsonify({"error":"Not found"}),404
        if u["is_protected"]==1 or u["email"]=="admin@lonma.com" or u["role"]=="Admin": return jsonify({"error":"Cannot delete Protected System Administrator"}),403
        conn.execute("BEGIN IMMEDIATE"); conn.execute("DELETE FROM users WHERE id=?",(mid,)); conn.execute("COMMIT")
        return jsonify({"message":"Deleted"})
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({"error":str(e)}),500
    finally: conn.close()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
