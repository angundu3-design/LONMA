import os, json, sqlite3, hashlib, datetime, random
from flask import Flask, request, jsonify, g, render_template_string, redirect, sessionapp = Flask(name)
app.secret_key = os.environ.get("SECRET_KEY", "lonma-secret-2026")
DB = "lonma.db"
VERSION = "v117-fixed"PROJECTS = ["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]FIRST_NAMES = ["Mary","John","Peter","Grace","David","Sarah","James","Esther","Michael","Ruth","Daniel","Faith","Joseph","Hannah","Samuel","Rebecca","Paul","Martha","Stephen","Naomi","George","Lydia","Andrew","Deborah","Thomas","Priscilla","Charles","Elizabeth","Francis","Margaret"]
LAST_NAMES = ["Kamau","Mwangi","Otieno","Wanjiru","Kiprop","Achieng","Muthoni","Omondi","Njeri","Kariuki","Atieno","Maina","Chebet","Koech","Wambui","Onyango","Njoroge","Chepkoech","Mutua","Wekesa"]def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return dbdef init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, project TEXT, amount REAL DEFAULT 0, joined TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT, role TEXT DEFAULT 'member')")
    db.commit()
    c = db.execute("SELECT COUNT() as c FROM members").fetchone()["c"]
    if c == 0:
        random.seed(42)
        for i in range(159):
            name = random.choice(FIRST_NAMES) + " " + random.choice(LAST_NAMES)
            phone = "07" + str(random.randint(10000000, 99999999))
            proj = random.choice(PROJECTS)
            amt = random.choice([500,1000,1500,2000,5000])
            db.execute("INSERT INTO members (name, phone, project, amount, joined) VALUES (?,?,?,?,?)", (name, phone, proj, amt, "2026-01-15"))
        db.commit()
        print(f"{VERSION} seeded 159")
    u = db.execute("SELECT COUNT() as c FROM users").fetchone()["c"]
    if u == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        db.execute("INSERT INTO users (email, password, name, role) VALUES (?,?,?,?)", ("admin@lonma.com", pw, "Admin", "admin"))
        db.commit()@app.teardown_appcontext
def close_db(e):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()HTML = r"""<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA Orbit - FIG</title>
<style>
body{font-family:Arial,sans-serif;margin:0;background:#f4f6f8;color:#111}
header{background:#0b3d2e;color:#fff;padding:14px 16px;display:flex;justify-content:space-between;align-items:center}
header b{font-size:20px}
.btn{background:#0b3d2e;color:#fff;border:0;padding:10px 14px;border-radius:8px;cursor:pointer}
.btn2{background:#fff;color:#0b3d2e;border:1px solid #0b3d2e;padding:8px 12px;border-radius:8px;cursor:pointer}
.card{background:#fff;margin:12px;padding:14px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1)}
input,select{width:100%;padding:11px;margin:6px 0;border:1px solid #ccc;border-radius:8px;box-sizing:border-box;font-size:16px}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{padding:8px;border-bottom:1px solid #eee;text-align:left}
.top{display:flex;gap:10px;flex-wrap:wrap}
.pill{background:#e8f5e9;padding:6px 10px;border-radius:20px;font-weight:bold}
</style></head>
<body>
<header><div><b>FIG</b> <span>LONMA Orbit</span></div><div><span id="notifCount">0</span> 🔔 &nbsp; <span id="userName">MA</span></div></header>
<div class="card">
<div class="top"><span class="pill" id="countLabel">0 members . 0 projects</span><span class="pill">v117-fixed</span></div>
<h2>Members</h2>
<input id="searchBox" placeholder="Search name or phone..." oninput="loadMembers()">
<label>Project Filter</label>
<select id="projFilter" onchange="loadMembers()"><option>All Projects</option></select>
<label>Search Project</label>
<input id="projSearch" placeholder="Type project..." oninput="filterProjOptions()">
<div id="membersList"></div>
</div>
<div class="card"><h3>Register Member</h3>
<input id="rName" placeholder="Full Name"><input id="rPhone" placeholder="Phone 07...">
<select id="rProj"></select><input id="rAmt" type="number" placeholder="Amount" value="1000">
<button class="btn" onclick="doRegister()">Register Member</button><div id="regMsg"></div></div>
<div class="card"><h3>Community</h3><div id="chatBox">Welcome to LONMA FIG Community</div></div>
<script>
const PROJECTS = ["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"];
async function loadStats(){
  try{
    let r = await fetch('/api/stats'); let d = await {{IE_23}}http://r.json{{/IE_23}}();
    {{IE_24}}http://document.getElementById{{/IE_24}}('countLabel').textContent = {{IE_25}}http://d.total{{/IE_25}}_members + ' members . ' + {{IE_26}}http://d.projects{{/IE_26}}_total + ' projects';
    let sel = {{IE_27}}http://document.getElementById{{/IE_27}}('projFilter');
    {{IE_28}}http://sel.innerHTML{{/IE_28}}='<option>All Projects</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option>';
    let rp = {{IE_29}}http://document.getElementById{{/IE_29}}('rProj');
    {{IE_30}}http://rp.innerHTML{{/IE_30}} = {{IE_31}}http://PROJECTS.map{{/IE_31}}(p=>'<option>'+p+'</option>').join('');
  }catch(e){}
}
function filterProjOptions(){
  let q = {{IE_32}}http://document.getElementById{{/IE_32}}('projSearch').value.toLowerCase();
  let sel = {{IE_33}}http://document.getElementById{{/IE_33}}('projFilter');
  let all = ["All Projects"].concat(PROJECTS);
  let f = {{IE_34}}http://all.filter{{/IE_34}}(p=>p.toLowerCase().includes(q));
  {{IE_35}}http://sel.innerHTML{{/IE_35}} = {{IE_36}}http://f.map{{/IE_36}}(p=>'<option>'+p+'</option>').join('');
  if(f.length==0){ {{IE_37}}http://sel.innerHTML{{/IE_37}}='<option>All Projects</option>'; }
}
async function loadMembers(){
  let q = {{IE_38}}http://document.getElementById{{/IE_38}}('searchBox').value || '';
  let proj = {{IE_39}}http://document.getElementById{{/IE_39}}('projFilter').value || 'All Projects';
  let r = await fetch('/api/members?search='+encodeURIComponent(q)+'&project='+encodeURIComponent(proj));
  let d = await {{IE_40}}http://r.json{{/IE_40}}();
  let html = '<table><tr><th>Name</th><th>Phone</th><th>Project</th><th>Amount</th></tr>';
  {{IE_41}}http://d.members.forEach{{/IE_41}}(m=>{ html += '<tr><td>'+m.name+'</td><td>'+m.phone+'</td><td>'+m.project+'</td><td>'+m.amount+'</td></tr>'; });
  html += '</table><p>Showing '+d.members.length+' members</p>';
  {{IE_42}}http://document.getElementById{{/IE_42}}('membersList').innerHTML = html;
}
async function doRegister(){
  let body = {name:document.getElementById('rName').value, phone:document.getElementById('rPhone').value, project:document.getElementById('rProj').value, amount:document.getElementById('rAmt').value};
  let r = await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});
  let d = await {{IE_43}}http://r.json{{/IE_43}}();
  {{IE_44}}http://document.getElementById{{/IE_44}}('regMsg').textContent = {{IE_45}}http://d.message{{/IE_45}} || 'Registered';
  loadMembers(); loadStats();
}
loadStats(); loadMembers();
</script></body></html>"""

@app.route("/")
def home():
    init_db()
    return render_template_string(HTML)@app.route("/members")
def members_page():
    init_db()
    return render_template_string(HTML)@app.route("/api/stats")
def stats():
    init_db()
    db = get_db()
    total = db.execute("SELECT COUNT() as c FROM members").fetchone()["c"]
    rows = db.execute("SELECT project, COUNT() as c FROM members GROUP BY project ORDER BY project").fetchall()
    projs = [{"project": r["project"], "count": r["c"]} for r in rows]
    return jsonify({"total_members": total, "projects_total": len(PROJECTS), "projects": projs, "version": VERSION})@app.route("/api/members")
def api_members():
    init_db()
    db = get_db()
    q = request.args.get("search", "").strip()
    proj = request.args.get("project", "All Projects")
    sql = "SELECT _ FROM members WHERE 1=1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR phone LIKE ?)"
        args += ["%"+q+"%", "%"+q+"%"]
    if proj and proj != "All Projects":
        sql += " AND project = ?"
        args.append(proj)
    sql += " ORDER BY name LIMIT 500"
    rows = db.execute(sql, args).fetchall()
    return jsonify({"members": [dict(r) for r in rows]})@app.route("/api/register", methods=["POST"])
def api_register():
    init_db()
    db = get_db()
    d = request.get_json(force=True)
    name = (d.get("name") or "").strip()
    phone = (d.get("phone") or "").strip()
    project = d.get("project") or "HQ"
    amount = d.get("amount") or 0
    if not name or not phone:
        return jsonify({"message": "Name and Phone required"}), 400
    db.execute("INSERT INTO members (name, phone, project, amount, joined) VALUES (?,?,?,?,?)", (name, phone, project, amount, datetime.date.today().isoformat()))
    db.commit()
    return jsonify({"message": "Member registered: " + name + " - " + project})@app.route("/api/notifications")
def notif():
    return jsonify({"count": 0, "items": []})@app.route("/api/login", methods=["POST"])
def login():
    init_db()
    db = get_db()
    d = request.get_json(force=True)
    pw = hashlib.sha256((d.get("password") or "").encode()).hexdigest()
    u = db.execute("SELECT _ FROM users WHERE email=? AND password=?", (d.get("email"), pw)).fetchone()
    if u:
        session["user"] = u["email"]
        return jsonify({"ok": True, "name": u["name"]})
    return jsonify({"ok": False, "message": "Invalid login"}), 401if name == "main":
    with app.app_context():
        init_db()
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
