from flask import Flask, request, jsonify, render_template_string
import sqlite3, os, secrets, time
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.config['SECRET_KEY'] = os.environ.get('SECRET_KEY', 'lonma-production-v17')
DB_PATH = os.path.join(os.path.dirname(__file__), 'lonma.db')

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

def get_connection():
    conn = sqlite3.connect(DB_PATH, timeout=15, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    conn.execute("PRAGMA journal_mode=WAL")
    conn.execute("PRAGMA synchronous=NORMAL")
    conn.execute("PRAGMA busy_timeout=15000")
    conn.execute("PRAGMA foreign_keys=ON")
    return conn

def init_database():
    conn = get_connection()
    try:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS users (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                staff_no TEXT NOT NULL,
                full_names TEXT NOT NULL,
                project TEXT NOT NULL CHECK(project IN ('Pwani Oil Products','Java House','SJ Johnson','Kanji','HQ','Antonio','TF-TDs','TF-MT','TF-LM','GCB-MT','GCB-Ws','Hichem')),
                month_year_joined TEXT,
                email TEXT UNIQUE NOT NULL,
                password TEXT NOT NULL,
                role TEXT DEFAULT 'Member',
                phone TEXT,
                father_id TEXT,
                mother_id TEXT,
                guardian_id TEXT,
                spouse_id TEXT,
                kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT,
                api_key TEXT UNIQUE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_protected INTEGER DEFAULT 0
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_project ON users(project)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_email ON users(email)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_api_key ON users(api_key)")
        
        admin = conn.execute("SELECT id FROM users WHERE email=?", ("admin@lonma.com",)).fetchone()
        if not admin:
            conn.execute("""
                INSERT INTO users (staff_no, full_names, project, month_year_joined, email, password, role, phone, api_key, is_protected)
                VALUES (?,?,?,?,?,?,?,?,?,1)
            """, (
                "HQ/001",
                "System Administrator",
                "HQ",
                "Oct 2026",
                "admin@lonma.com",
                generate_password_hash("admin123"),
                "Admin",
                "0700000000",
                "lonma_api_key_12345"
            ))
    finally:
        conn.close()

init_database()

@app.after_request
def cors(response):
    response.headers['Access-Control-Allow-Origin'] = '*'
    response.headers['Access-Control-Allow-Headers'] = 'Content-Type, X-API-KEY'
    response.headers['Access-Control-Allow-Methods'] = 'GET, POST, DELETE, OPTIONS'
    return response

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS':
            return '', 200
        key = request.headers.get('X-API-KEY') or request.args.get('api_key')
        if not key:
            return jsonify({"error": "Authentication required"}), 401
        conn = get_connection()
        try:
            user = conn.execute("SELECT id, role, is_protected FROM users WHERE api_key=?", (key,)).fetchone()
            if not user:
                return jsonify({"error": "Invalid API key"}), 401
            request.current_user = user
        finally:
            conn.close()
        return f(*args, **kwargs)
    return decorated

# ============== ULTRA PROFESSIONAL UI ==============
BASE_CSS = """
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">
<style>
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',system-ui,sans-serif;background:#f8fafc;color:#0f172a;line-height:1.5;-webkit-font-smoothing:antialiased}
.header{height:56px;background:#fff;border-bottom:1px solid #e2e8f0;display:flex;align-items:center;justify-content:space-between;padding:0 24px;position:sticky;top:0;z-index:20}
.brand{display:flex;align-items:center;gap:10px}.brand-icon{width:32px;height:32px;background:#0f172a;color:#fff;border-radius:8px;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px}
.brand-name{font-weight:700;font-size:14px;letter-spacing:-.2px}.brand-name span{display:block;font-size:10px;font-weight:600;color:#64748b;letter-spacing:.8px;text-transform:uppercase}
.nav{display:flex;gap:4px}.nav a{padding:6px 12px;border-radius:7px;font-size:13px;font-weight:500;color:#64748b;text-decoration:none}.nav a:hover{background:#f1f5f9;color:#0f172a}.nav a.active{background:#0f172a;color:#fff}
.page{max-width:1160px;margin:0 auto;padding:24px}
.stats{display:grid;grid-template-columns:repeat(3,1fr);gap:12px;margin-bottom:20px}
.stat{background:#fff;border:1px solid #e2e8f0;border-radius:10px;padding:16px 18px}.stat label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.7px}.stat b{font-size:22px;font-weight:700;display:block;margin-top:2px;letter-spacing:-.5px}.stat p{font-size:11px;color:#94a3b8;margin-top:2px}
.card{background:#fff;border:1px solid #e2e8f0;border-radius:10px;overflow:hidden}
.card-head{padding:16px 20px;border-bottom:1px solid #e2e8f0;display:flex;justify-content:space-between;align-items:center}.card-head h3{font-size:13px;font-weight:600}.card-head p{font-size:11px;color:#64748b}
.list-row{padding:12px 20px;border-bottom:1px solid #f1f5f9;display:flex;justify-content:space-between;align-items:center;font-size:13px}.list-row:last-child{border:0}
.dot{width:7px;height:7px;border-radius:50%;display:inline-block;margin-right:7px}
.btn{height:36px;padding:0 14px;border-radius:8px;font-size:13px;font-weight:600;border:1px solid #e2e8f0;background:#fff;color:#0f172a;cursor:pointer;text-decoration:none;display:inline-flex;align-items:center;gap:6px}.btn-dark{background:#0f172a;color:#fff;border-color:#0f172a}
.input{width:100%;height:38px;padding:0 12px;border:1px solid #e2e8f0;border-radius:8px;font-size:13px;background:#fff}.input:focus{outline:none;border-color:#0f172a;box-shadow:0 0 0 3px rgba(15,23,42,.08)}
label{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;margin-bottom:6px;display:block}
table{width:100%;border-collapse:collapse}th{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px;padding:10px 14px;text-align:left;background:#f8fafc;border-bottom:1px solid #e2e8f0}td{padding:12px 14px;font-size:13px;border-bottom:1px solid #f1f5f9;vertical-align:middle}
.badge{font-size:11px;font-weight:500;padding:3px 8px;border-radius:6px;background:#f1f5f9;border:1px solid #e2e8f0}
@media(max-width:768px){.stats{grid-template-columns:1fr}.page{padding:16px}.header{padding:0 16px}}
</style>
"""

HOME_HTML = f"""
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA Welfare</title>{BASE_CSS}</head><body>
<div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management System</span></div></div><div class="nav"><a href="/" class="active">Overview</a><a href="/dashboard">Members</a><a href="/register">Register</a></div></div>
<div class="page">
<div class="stats">
<div class="stat"><label>Total Members</label><b id="total">—</b><p>Active records</p></div>
<div class="stat"><label>Projects</label><b>12</b><p>All locations operational</p></div>
<div class="stat"><label>Status</label><b style="color:#16a34a">Active</b><p>Production system</p></div>
</div>
<div class="card"><div class="card-head"><div><h3>Project Distribution</h3><p>Members per project location</p></div><a href="/dashboard" class="btn">View All Members</a></div><div id="breakdown"><div class="list-row" style="color:#64748b">Loading data...</div></div></div>
</div>
<script>
(async()=>{{
  try{{
    let r=await fetch('/api/stats?api_key=lonma_api_key_12345');
    let d=await r.json();
    document.getElementById('total').textContent=d.total_members;
    let colors={{"Pwani Oil Products":"#f59e0b","Java House":"#7c3aed","SJ Johnson":"#dc2626","Kanji":"#059669","HQ":"#0f172a","Antonio":"#db2777","TF-TDs":"#0891b2","TF-MT":"#65a30d","TF-LM":"#ea580c","GCB-MT":"#4f46e5","GCB-Ws":"#0d9488","Hichem":"#9333ea"}};
    let html='';
    for(let [proj,count] of Object.entries(d.projects_breakdown||{{}})){{ html+=`<div class="list-row"><span><i class="dot" style="background:${{colors[proj]||'#64748b'}}"></i>${{proj}}</span><b>${{count}}</b></div>`; }}
    document.getElementById('breakdown').innerHTML=html||'<div class="list-row">No members yet</div>';
  }}catch(e){{ document.getElementById('breakdown').innerHTML='<div class="list-row" style="color:#dc2626">Failed to load</div>'; }}
}})();
</script>
</body></html>
"""

@app.route("/")
def index(): return render_template_string(HOME_HTML)

@app.route("/register")
def register_view():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - LONMA</title>{BASE_CSS}</head><body>
<div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard">Members</a><a href="/register" class="active">Register</a></div></div>
<div class="page" style="max-width:720px"><div class="card"><div class="card-head"><h3>Register New Member</h3><p>Complete all required fields</p></div><div style="padding:20px">
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div><label>Staff Number *</label><input class="input" id="staff_no" placeholder="HQ/002"></div><div><label>Project *</label><select class="input" id="project">{opts}</select></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px"><div><label>Full Names *</label><input class="input" id="full_names"></div><div><label>Email *</label><input class="input" id="email" type="email"></div></div>
<div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px"><div><label>Password *</label><input class="input" id="password" type="password"></div><div><label>Phone</label><input class="input" id="phone"></div></div>
<div style="margin-top:12px"><label>Month / Year Joined</label><input class="input" id="month_year_joined" placeholder="Nov 2026"></div>
<div style="margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0"><h4 style="font-size:12px;font-weight:600;margin-bottom:12px">Family Information</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div><label>Father ID</label><input class="input" id="father_id"></div><div><label>Mother ID</label><input class="input" id="mother_id"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px"><div><label>Guardian ID</label><input class="input" id="guardian_id"></div><div><label>Spouse ID</label><input class="input" id="spouse_id"></div></div></div>
<div style="margin-top:20px;padding-top:16px;border-top:1px solid #e2e8f0"><h4 style="font-size:12px;font-weight:600;margin-bottom:12px">Children Details</h4><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px"><div><label>Child 1 Birth Cert</label><input class="input" id="kid1"></div><div><label>Child 2 Birth Cert</label><input class="input" id="kid2"></div></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-top:12px"><div><label>Child 3</label><input class="input" id="kid3"></div><div><label>Child 4</label><input class="input" id="kid4"></div></div><div style="margin-top:12px"><label>Child 5</label><input class="input" id="kid5"></div></div>
<button class="btn btn-dark" style="width:100%;margin-top:20px;justify-content:center" onclick="doRegister()">Create Member Record</button><p id="msg" style="font-size:12px;margin-top:12px;text-align:center"></p>
</div></div></div>
<script>
async function doRegister(){{
  let fields=["staff_no","project","full_names","email","password","phone","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"];
  let data={{}}; fields.forEach(f=>data[f]=document.getElementById(f).value);
  let msg=document.getElementById('msg');
  msg.style.color='#64748b'; msg.textContent='Creating...';
  try{{
    let r=await fetch('/api/register',{{method:'POST',headers:{{'Content-Type':'application/json'}},body:JSON.stringify(data)}});
    let j=await r.json();
    if(!r.ok) throw new Error(j.error||'Failed');
    msg.style.color='#16a34a'; msg.textContent='Member created successfully';
    setTimeout(()=>location.href='/dashboard',800);
  }}catch(e){{ msg.style.color='#dc2626'; msg.textContent=e.message; }}
}}
</script></body></html>
""")

@app.route("/dashboard")
def dashboard_view():
    opts = '<option value="">All Projects</option>' + "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    return render_template_string(f"""
<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - LONMA</title>{BASE_CSS}</head><body>
<div class="header"><div class="brand"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>Welfare Management</span></div></div><div class="nav"><a href="/">Overview</a><a href="/dashboard" class="active">Members</a><a href="/register">Register</a></div></div>
<div class="page"><div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:16px"><div><h2 style="font-size:16px;font-weight:700">Members Directory</h2><p style="font-size:12px;color:#64748b"><span id="count">0</span> records</p></div><a href="/register" class="btn btn-dark">+ New Member</a></div>
<div class="card"><div style="padding:12px 14px;border-bottom:1px solid #e2e8f0;display:flex;gap:8px"><input class="input" id="search" placeholder="Search staff, name, email..." style="max-width:260px;height:34px" oninput="applyFilter()"><select class="input" id="projFilter" style="max-width:180px;height:34px" onchange="applyFilter()">{opts}</select></div><div style="overflow:auto"><table id="tbl"></table></div></div></div>
<script>
let allMembers=[];
async function loadMembers(){{
  try{{
    let key=localStorage.getItem('api_key')||'lonma_api_key_12345';
    let r=await fetch('/api/members?api_key='+key);
    let d=await r.json();
    if(!r.ok){{ alert(d.error); return; }}
    allMembers=d.members; document.getElementById('count').textContent=d.total; renderTable(d.members);
  }}catch(e){{ alert('Load failed'); }}
}}
function renderTable(list){{
  let h='<tr><th>Staff No</th><th>Member Name</th><th>Project</th><th>Contact</th><th>Action</th></tr>';
  list.forEach(m=>{{
    let isProtected=m.is_protected||m.email==='admin@lonma.com';
    h+=`<tr style="${{isProtected?'background:#f8fafc':''}}"><td style="font-weight:600">${{m.staff_no}} ${{isProtected?'<span style="font-size:9px;background:#0f172a;color:#fff;padding:2px 6px;border-radius:4px;margin-left:6px">PROTECTED</span>':''}}</td><td><div style="font-weight:500">${{m.full_names}}</div><div style="font-size:11px;color:#64748b">${{m.month_year_joined||''}}</div></td><td><span class="badge">${{m.project}}</span></td><td style="font-size:12px">${{m.email}}<div style="font-size:11px;color:#64748b">${{m.phone||''}}</div></td><td>${{isProtected?'<span style="font-size:11px;color:#94a3b8">System</span>':`<button onclick="deleteMember(${{m.id}})" style="height:30px;padding:0 10px;border-radius:6px;border:1px solid #fee2e2;background:#fff;color:#dc2626;font-size:12px;font-weight:600;cursor:pointer">Delete</button>`}}</td></tr>`;
  }});
  document.getElementById('tbl').innerHTML=h;
}}
function applyFilter(){{
  let q=document.getElementById('search').value.toLowerCase();
  let p=document.getElementById('projFilter').value;
  let filtered=allMembers.filter(m=>{{ let matchQ=(m.full_names+m.staff_no+m.email).toLowerCase().includes(q); let matchP=!p||m.project===p; return matchQ&&matchP; }});
  renderTable(filtered);
}}
async function deleteMember(id){{
  if(!confirm('Delete member #'+id+'? This cannot be undone.')) return;
  let key=localStorage.getItem('api_key')||'lonma_api_key_12345';
  try{{
    let r=await fetch('/api/members/'+id+'?api_key='+key,{{method:'DELETE'}});
    let j=await r.json();
    if(!r.ok){{ alert(j.error); return; }}
    loadMembers();
  }}catch(e){{ alert('Delete failed'); }}
}}
loadMembers();
</script></body></html>
""")

# ============== API ==============
@app.route("/api/stats")
@require_api_key
def api_stats():
    conn = get_connection()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
        breakdown = {{}}
        for proj in PROJECTS:
            cnt = conn.execute("SELECT COUNT(*) FROM users WHERE project=?", (proj,)).fetchone()[0]
            breakdown[proj] = cnt
        return jsonify({{"total_members": total, "projects_breakdown": breakdown}})
    finally:
        conn.close()

@app.route("/api/members")
@require_api_key
def api_members():
    conn = get_connection()
    try:
        rows = conn.execute("SELECT id, staff_no, full_names, project, month_year_joined, email, phone, is_protected FROM users ORDER BY is_protected DESC, id DESC").fetchall()
        data = [dict(r) for r in rows]
        return jsonify({{"total": len(data), "members": data}})
    finally:
        conn.close()

@app.route("/api/register", methods=["POST", "OPTIONS"])
def api_register():
    if request.method == "OPTIONS": return "", 200
    data = request.get_json(silent=True)
    if not data or not data.get("email") or not data.get("password") or not data.get("full_names"):
        return jsonify({{"error": "full_names, email, password required"}}), 400
    project = data.get("project", "HQ")
    if project not in PROJECTS:
        return jsonify({{"error": f"Project must be one of: {', '.join(PROJECTS)}"}}), 400
    conn = get_connection()
    try:
        api_key = f"lonma_{secrets.token_hex(16)}"
        conn.execute("BEGIN IMMEDIATE")
        conn.execute("""
            INSERT INTO users (staff_no, full_names, project, month_year_joined, email, password, phone, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
            VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
        """, (
            data.get("staff_no", f"{project[:4].upper()}/{secrets.token_hex(2).upper()}"),
            data["full_names"], project, data.get("month_year_joined",""),
            data["email"], generate_password_hash(data["password"]),
            data.get("phone",""), data.get("father_id",""), data.get("mother_id",""),
            data.get("guardian_id",""), data.get("spouse_id",""),
            data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5",""),
            api_key
        ))
        conn.execute("COMMIT")
        return jsonify({{"message": "Member registered", "project": project}}), 201
    except sqlite3.IntegrityError:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({{"error": "Email already exists"}}), 400
    except Exception as e:
        try: conn.execute("ROLLBACK")
        except: pass
        return jsonify({{"error": str(e)}}), 400
    finally:
        conn.close()

@app.route("/api/members/<int:member_id>", methods=["DELETE", "OPTIONS"])
@require_api_key
def api_delete(member_id):
    if request.method == "OPTIONS": return "", 200
    conn = get_connection()
    try:
        user = conn.execute("SELECT id, email, is_protected, role FROM users WHERE id=?", (member_id,)).fetchone()
        if not user: return jsonify({{"error": "Member not found"}}), 404
        if user["is_protected"] == 1 or user["email"] == "admin@lonma.com" or user["role"] == "Admin":
            return jsonify({{"error": "Cannot delete System Administrator - This account is protected"}}), 403
        # Prevent self-delete via API key
        if user["id"] == request.current_user["id"]:
            return jsonify({{"error": "Cannot delete your own account"}}), 403
        
        for attempt in range(3):
            try:
                conn.execute("BEGIN IMMEDIATE")
                conn.execute("DELETE FROM users WHERE id=?", (member_id,))
                conn.execute("COMMIT")
                return jsonify({{"message": "Member deleted successfully"}})
            except sqlite3.OperationalError as e:
                try: conn.execute("ROLLBACK")
                except: pass
                if "locked" in str(e).lower() and attempt < 2:
                    time.sleep(0.5)
                    continue
                raise e
    except Exception as e:
        return jsonify({{"error": f"Delete failed: {str(e)}"}}), 500
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
