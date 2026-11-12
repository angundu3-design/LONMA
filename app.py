import os
import json
import sqlite3
import hashlib
import datetime
import random
from flask import Flask
from flask import request
from flask import jsonify
from flask import g
from flask import render_template_string
from flask import session
app = Flask("lonma")
app.secret_key = "lonma-secret-2026"
DB = "lonma.db"
PROJECTS = ["Antonia", "GCB-MT", "GCB-TDs", "Higchem", "HQ", "Java House", "Kanji", "Pwani Oil Products", "SC Johnson", "TF WSL", "TF-LM", "TF-MT"]
FIRST = ["Mary", "John", "Peter", "Grace", "David", "Sarah", "James", "Esther", "Michael", "Ruth", "Daniel", "Faith", "Joseph", "Hannah"]
LAST = ["Kamau", "Mwangi", "Otieno", "Wanjiru", "Kiprop", "Achieng", "Muthoni", "Omondi", "Njeri", "Kariuki", "Atieno", "Maina"]
def get_db():
    db = getattr(g, "_db", None)
    if db is None:
        db = g._db = sqlite3.connect(DB)
        db.row_factory = sqlite3.Row
    return db
def init_db():
    db = get_db()
    db.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, project TEXT, amount REAL DEFAULT 0, joined TEXT)")
    db.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, email TEXT UNIQUE, password TEXT, name TEXT, role TEXT DEFAULT 'member')")
    db.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, action TEXT, detail TEXT, created TEXT)")
    db.commit()
    c = db.execute("SELECT COUNT(id) as c FROM members").fetchone()["c"]
    if c == 0:
        random.seed(42)
        for i in range(159):
            nm = random.choice(FIRST) + " " + random.choice(LAST)
            ph = "07" + str(random.randint(10000000, 99999999))
            pj = random.choice(PROJECTS)
            amt = random.choice([500, 1000, 1500, 2000, 5000])
            db.execute("INSERT INTO members (name, phone, project, amount, joined) VALUES (?,?,?,?,?)", (nm, ph, pj, amt, "2026-01-15"))
        db.commit()
    u = db.execute("SELECT COUNT(id) as c FROM users").fetchone()["c"]
    if u == 0:
        pw = hashlib.sha256("admin123".encode()).hexdigest()
        db.execute("INSERT INTO users (email, password, name, role) VALUES (?,?,?,?)", ("admin@lonma.com", pw, "Admin", "admin"))
        db.commit()
@app.teardown_appcontext
def close_db(e):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()
HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA Orbit</title><style>body{font-family:Arial;margin:0;background:#f4f6f8}header{background:#0b3d2e;color:#fff;padding:14px;display:flex;justify-content:space-between}.card{background:#fff;margin:12px;padding:14px;border-radius:12px}.btn{background:#0b3d2e;color:#fff;border:0;padding:11px;border-radius:8px;width:100%}input,select{width:100%;padding:11px;margin:6px 0;border:1px solid #ccc;border-radius:8px;box-sizing:border-box}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #eee;text-align:left}.pill{background:#e8f5e9;padding:6px 10px;border-radius:20px;font-weight:bold}.tab{padding:9px 12px;background:#eee;border-radius:20px;cursor:pointer;display:inline-block;margin:2px}.tab.on{background:#0b3d2e;color:#fff}.hide{display:none}</style></head><body><header><div>FIG LONMA Orbit</div><div>MA</div></header><div class="card"><span class="tab on" onclick="showTab('overview',this)">Overview</span><span class="tab" onclick="showTab('members',this)">Members</span><span class="tab" onclick="showTab('register',this)">Register</span><span class="tab" onclick="showTab('shareout',this)">Share-Out</span><span class="tab" onclick="showTab('history',this)">History</span><span class="tab" onclick="showTab('terms',this)">Terms</span><span class="tab" onclick="showTab('community',this)">Community</span></div><div id="tab-overview" class="card"><h2>Overview</h2><p><span class="pill" id="countLabel">Loading...</span></p><p>Total Savings: <b id="totalAmt">0</p><p>Version v120</p></div><div id="tab-members" class="card hide"><h2>Members</h2><input id="searchBox" placeholder="Search name or phone..." oninput="loadMembers()"><label>Project Filter</label><select id="projFilter" onchange="loadMembers()"><option>All Projects</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option></select><div id="membersList"></div></div><div id="tab-register" class="card hide"><h3>Register Member</h3><input id="rName" placeholder="Full Name"><input id="rPhone" placeholder="Phone 07..."><select id="rProj"></select><input id="rAmt" type="number" value="1000"><button class="btn" onclick="doRegister()">Register Member</button><div id="regMsg"></div></div><div id="tab-shareout" class="card hide"><h3>Share-Out</h3><select id="soProj"></select><button class="btn" onclick="doShareOut()">Calculate Share-Out</button><div id="soResult"></div></div><div id="tab-history" class="card hide"><h3>History</h3><div id="histList"></div></div><div id="tab-terms" class="card hide"><h3>Terms</h3><p>1. Members save weekly. 2. Loans approved by group. 3. Share-Out at end of cycle. 4. Be respectful in Community.</p></div><div id="tab-community" class="card hide"><h3>Community</h3><div id="chatBox">Welcome to LONMA FIG Community</div><input id="chatIn" placeholder="Type message..."><button class="btn" onclick="sendChat()">Send</button></div><script>const PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"];function showTab(id,el){document.querySelectorAll('[id^="tab-"]').forEach(e=>e.classList.add('hide'));document.getElementById('tab-'+id).classList.remove('hide');document.querySelectorAll('.tab').forEach(t=>t.classList.remove('on'));el.classList.add('on');if(id=='history')loadHistory();}function fillDropdowns(){let sel=document.getElementById('projFilter');sel.innerHTML='<option>All Projects</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option>';document.getElementById('rProj').innerHTML=PROJECTS.map(p=>'<option>'+p+'</option>').join('');document.getElementById('soProj').innerHTML='<option>All Projects</option>'+PROJECTS.map(p=>'<option>'+p+'</option>').join('');}async function loadStats(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('countLabel').textContent=d.total_members+' members . '+d.projects_total+' projects';document.getElementById('totalAmt').textContent=d.total_amount;}catch(e){}}async function loadMembers(){let q=document.getElementById('searchBox').value||'';let proj=document.getElementById('projFilter').value||'All Projects';let r=await fetch('/api/members?search='+encodeURIComponent(q)+'&project='+encodeURIComponent(proj));let d=await r.json();let h='<table><tr><th>Name</th><th>Phone</th><th>Project</th><th>Amount</th></tr>';d.members.forEach(m=>{h+='<tr><td>'+m.name+'</td><td>'+m.phone+'</td><td>'+m.project+'</td><td>'+m.amount+'</td></tr>';});h+='</table><p>Showing '+d.members.length+' members</p>';document.getElementById('membersList').innerHTML=h;}async function doRegister(){let b={name:document.getElementById('rName').value,phone:document.getElementById('rPhone').value,project:document.getElementById('rProj').value,amount:document.getElementById('rAmt').value};let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});let d=await r.json();document.getElementById('regMsg').textContent=d.message||'Registered';loadMembers();loadStats();}async function doShareOut(){let p=document.getElementById('soProj').value;let r=await fetch('/api/shareout?project='+encodeURIComponent(p));let d=await r.json();document.getElementById('soResult').innerHTML='Project: '+d.project+'Members: '+d.count+'Total: '+d.total+'Per Member: '+d.per_member+'';}async function loadHistory(){let r=await fetch('/api/history');let d=await r.json();document.getElementById('histList').innerHTML=d.items.map(x=>'<p>'+x.created+' - '+x.action+' - '+x.detail+'</p>').join('')||'<p>No history yet</p>';}function sendChat(){let v=document.getElementById('chatIn').value;if(!v)return;document.getElementById('chatBox').innerHTML+='<p>You: '+v+'</p>';document.getElementById('chatIn').value='';}fillDropdowns();loadStats();loadMembers();</script></body></html>"""
@app.route("/")
def home():
    init_db()
    return render_template_string(HTML)
@app.route("/members")
def members_page():
    init_db()
    return render_template_string(HTML)
@app.route("/api/stats")
def stats():
    init_db()
    db = get_db()
    total = db.execute("SELECT COUNT(id) as c FROM members").fetchone()["c"]
    amt = db.execute("SELECT COALESCE(SUM(amount),0) as s FROM members").fetchone()["s"]
    return jsonify({"total_members": total, "total_amount": amt, "projects_total": 12, "version": "v120"})
@app.route("/api/members")
def api_members():
    init_db()
    db = get_db()
    q = request.args.get("search", "").strip()
    proj = request.args.get("project", "All Projects")
    sql = "SELECT id, name, phone, project, amount, joined FROM members WHERE 1=1"
    args = []
    if q:
        sql += " AND (name LIKE ? OR phone LIKE ?)"
        args += ["%" + q + "%", "%" + q + "%"]
    if proj and proj != "All Projects":
        sql += " AND project = ?"
        args.append(proj)
    sql += " ORDER BY name LIMIT 500"
    rows = db.execute(sql, args).fetchall()
    out = []
    for r in rows:
        out.append({"id": r["id"], "name": r["name"], "phone": r["phone"], "project": r["project"], "amount": r["amount"], "joined": r["joined"]})
    return jsonify({"members": out})
@app.route("/api/register", methods=["POST"])
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
    db.execute("INSERT INTO history (action, detail, created) VALUES (?,?,?)", ("Register", name + " - " + project, datetime.datetime.now().isoformat()))
    db.commit()
    return jsonify({"message": "Member registered: " + name + " - " + project})
@app.route("/api/shareout")
def shareout():
    init_db()
    db = get_db()
    proj = request.args.get("project", "All Projects")
    if proj == "All Projects":
        c = db.execute("SELECT COUNT(id) as c FROM members").fetchone()["c"]
        t = db.execute("SELECT COALESCE(SUM(amount),0) as s FROM members").fetchone()["s"]
    else:
        c = db.execute("SELECT COUNT(id) as c FROM members WHERE project=?", (proj,)).fetchone()["c"]
        t = db.execute("SELECT COALESCE(SUM(amount),0) as s FROM members WHERE project=?", (proj,)).fetchone()["s"]
    per = round(t / c, 2) if c else 0
    return jsonify({"project": proj, "count": c, "total": t, "per_member": per})
@app.route("/api/history")
def history():
    init_db()
    db = get_db()
    rows = db.execute("SELECT id, action, detail, created FROM history ORDER BY id DESC LIMIT 50").fetchall()
    out = []
    for r in rows:
        out.append({"id": r["id"], "action": r["action"], "detail": r["detail"], "created": r["created"]})
    return jsonify({"items": out})
@app.route("/api/notifications")
def notif():
    return jsonify({"count": 0, "items": []})
@app.route("/api/login", methods=["POST"])
def login():
    init_db()
    db = get_db()
    d = request.get_json(force=True)
    pw = hashlib.sha256((d.get("password") or "").encode()).hexdigest()
    u = db.execute("SELECT id, email, password, name, role FROM users WHERE email=? AND password=?", (d.get("email"), pw)).fetchone()
    if u:
        session["user"] = u["email"]
        return jsonify({"ok": True, "name": u["name"]})
    return jsonify({"ok": False, "message": "Invalid login"}), 401
