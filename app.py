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
PROJECTS = ["Antonia", "GCB-MT", "GCB-TDs", "Higchem", "HQ", "Java House", "Kanji", "Pwani Oil Products"]
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
    db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, email TEXT, text TEXT, created TEXT)")
    db.commit()
    c = db.execute("SELECT COUNT(id) as c FROM members").fetchone()["c"]
    if c == 0:
        random.seed(42)
        for i in range(160):
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
HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>F.I.G BRANDS Welfare System</title><style>body{font-family:Georgia,serif;margin:0;background:#faf7f0;color:#0a2540}header{background:#fff;padding:12px 14px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #eee;position:sticky;top:0;z-index:10}.logo{display:flex;align-items:center;gap:10px}.fig{background:#0a2540;color:#fff;width:52px;height:52px;border-radius:14px;display:flex;align-items:center;justify-content:center;font-weight:bold;font-size:18px}.logo b{font-size:19px;letter-spacing:1px}.logo span{display:block;font-family:Arial;font-size:11px;letter-spacing:3px;color:#666}.nav{display:flex;gap:16px;overflow-x:auto;padding:10px 14px;background:#fff;font-family:Arial;white-space:nowrap}.nav a{color:#0a2540;text-decoration:none;font-weight:bold;font-size:15px}.nav a.on{border-bottom:2px solid #c9a86a}.wrap{padding:14px}.eyebrow{font-family:Arial;color:#c9a86a;letter-spacing:3px;font-size:12px;font-weight:bold}.h1{font-size:42px;margin:8px 0;line-height:1}.sub{font-family:Arial;color:#555;font-size:17px;line-height:1.5}.card{background:#fff;border-radius:20px;padding:18px;margin:14px 0;box-shadow:0 2px 12px rgba(0,0,0,0.06)}.label{font-family:Arial;color:#666;letter-spacing:2px;font-size:12px}.big{font-size:52px;margin:8px 0}.dark{background:#0a2540;color:#fff;border-radius:20px;padding:20px;margin:14px 0}.dark .label{color:#c9a86a}.dark .big{font-size:44px}.gold{background:#c9a86a;color:#fff;border:0;padding:13px 18px;border-radius:30px;font-weight:bold}.navy{background:#0a2540;color:#fff;border:0;padding:13px 18px;border-radius:30px;font-weight:bold}.light{background:#eee;border:0;padding:12px 16px;border-radius:30px}input,select,textarea{width:100%;padding:13px;margin:7px 0;border:1px solid #ddd;border-radius:12px;box-sizing:border-box;font-size:15px}table{width:100%;border-collapse:collapse;font-family:Arial}th,td{padding:9px;border-bottom:1px solid #eee;text-align:left}.hide{display:none}.row{display:flex;justify-content:space-between;font-family:Arial;padding:10px 0;border-bottom:1px solid #f0f0f0}.bottom{position:fixed;bottom:12px;left:12px;right:12px;background:#fff;border-radius:30px;display:flex;justify-content:space-around;padding:14px;box-shadow:0 4px 20px rgba(0,0,0,0.12);font-family:Arial;font-weight:bold;z-index:20}.bottom a{color:#666;text-decoration:none}.bottom a.on{color:#0a2540}.avatar{background:#0a2540;color:#fff;width:48px;height:48px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold}.post{border-top:1px solid #eee;padding:12px 0;font-family:Arial}.pad{padding-bottom:90px}</style></head><body><header><div class="logo"><div class="fig">FIG</div><div>F.I.G BRANDS<span>WELFARE SYSTEM</span></div></div><div style="display:flex;gap:8px"><div style="width:38px;height:38px;border-radius:50%;background:#f0f0f0"></div><div style="width:38px;height:38px;border-radius:50%;background:#f0f0f0"></div><div class="avatar" style="width:38px;height:38px;font-size:13px">MA</div></div></header><div class="nav"><a href="#" onclick="showTab('overview',this)" class="on">Overview</a><a href="#" onclick="showTab('members',this)">Members</a><a href="#" onclick="showTab('community',this)">Community</a><a href="#" onclick="showTab('register',this)">Register</a><a href="#" onclick="showTab('shareout',this)">Share-Out</a><a href="#" onclick="showTab('history',this)">History</a><a href="#" onclick="showTab('terms',this)">Terms and Policies</a><a href="#" onclick="showTab('admin',this)">Admin</a></div><div class="wrap pad"><div id="tab-overview"><div class="eyebrow">F.I.G BRANDS - WELFARE</div><div class="h1">Overview</div><p class="sub">Balance brought forward, less KES 250,000 retained - shared fairly, per month of contributions.</p><div class="card"><div class="label">TOTAL MEMBERS</div><div class="big" id="countLabel">160</div></div><div class="card"><div class="label">PROJECTS</div><div class="big">8</div></div><div class="dark"><div class="label">BALANCE BROUGHT FORWARD</div><div class="big">KES 855,759</div><div style="font-family:Arial;color:#ddd">KES 605,759 to share - KES 250,000 retained</div><div style="margin-top:12px;font-family:Arial">Contribution: KES 300 monthly - Welfare Clauses 2026</div></div><div class="card"><div class="eyebrow">WELFARE CLAUSES 2026</div><h2 style="font-size:32px;line-height:1.2">Death Benefit: Member 100,000 - Spouse 50,000 - Child 40,000 - Parents 40,000</h2><p class="sub">Loss of Earning: 50 percent of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><button class="navy" onclick="showTab('terms',document.querySelectorAll('.nav a')[6])">Read Full Terms</button> <button class="gold" onclick="showTab('community',document.querySelectorAll('.nav a')[2])">Join Community Chat</button></div><div class="card"><div class="eyebrow">DISTRIBUTION</div><h2 style="font-size:30px">Project Distribution</h2><div id="distList"></div></div></div><div id="tab-members" class="hide"><div class="eyebrow">F.I.G BRANDS - WELFARE</div><div class="h1">Members</div><input id="searchBox" placeholder="Search name or phone..." oninput="loadMembers()"><label style="font-family:Arial">Project Filter</label><select id="projFilter" onchange="loadMembers()"></select><div id="membersList"></div></div><div id="tab-register" class="hide"><div class="h1">Register</div><div class="card"><input id="rName" placeholder="Full Name"><input id="rPhone" placeholder="Phone 07..."><select id="rProj"></select><input id="rAmt" type="number" value="1000"><button class="navy" style="width:100%" onclick="doRegister()">Register Member</button><div id="regMsg" style="font-family:Arial;margin-top:10px"></div></div></div><div id="tab-shareout" class="hide"><div class="h1">Share-Out</div><div class="card"><select id="soProj"></select><button class="navy" style="width:100%" onclick="doShareOut()">Calculate Share-Out</button><div id="soResult" style="font-family:Arial;margin-top:12px;line-height:1.7"></div></div><div class="dark"><div class="label">FORMULA</div><p style="font-family:Arial;line-height:1.6">Total to share KES 605,759 divided by months contributed. Retained KES 250,000 stays for next cycle.</p></div></div><div id="tab-history" class="hide"><div class="h1">History</div><div id="histList"></div></div><div id="tab-terms" class="hide"><div class="eyebrow">WELFARE CLAUSES 2026</div><div class="h1">Terms and Policies</div><div class="card"><h3>1. Membership</h3><p style="font-family:Arial;line-height:1.6">Open to F.I.G Brands staff. Contribution KES 300 monthly.</p><h3>2. Death Benefit</h3><p style="font-family:Arial;line-height:1.6">Member 100,000 - Spouse 50,000 - Child 40,000 - Parents 40,000. Claim within 30 days with documents.</p><h3>3. Loss of Earning</h3><p style="font-family:Arial;line-height:1.6">50 percent of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work.</p><h3>4. Share-Out</h3><p style="font-family:Arial;line-height:1.6">Balance brought forward less KES 250,000 retained, shared per month of contributions.</p><h3>5. Community</h3><p style="font-family:Arial;line-height:1.6">Be kind - no insults, no politics.</p></div></div><div id="tab-community" class="hide"><div class="h1" style="font-size:38px">Community Chat</div><p class="sub">Post, repost, share, save. Be kind - no insults, no politics.</p><div class="card"><div style="display:flex;gap:12px;align-items:center"><div class="avatar">MA</div><div><b style="font-family:Arial;font-size:18px">Marlon Ang'undu Kikuyu<div style="font-family:Arial;color:#777">marlonkikuyu@gmail.com</div></div></div><textarea id="chatIn" rows="3" placeholder="Share something..."></textarea><div style="display:flex;gap:8px"><button class="light">Photo</button><button class="light">Video</button><button class="navy" onclick="sendChat()">Post to Community</button></div><button class="gold" style="width:100%;margin-top:10px" onclick="loadPosts()">My Posts</button></div><div id="postsList"></div></div><div id="tab-admin" class="hide"><div class="h1">Admin</div><div class="card"><p style="font-family:Arial">Admin: admin@lonma.com / admin123</p><p style="font-family:Arial">Total Balance: KES 855,759</p><button class="navy" onclick="loadHistory()">View History</button><div id="adminHist"></div></div></div></div><div class="bottom"><a href="#" class="on" onclick="showTab('overview',this)">Home</a><a href="#" onclick="showTab('members',this)">Members</a><a href="#" onclick="showTab('community',this)">Community</a><a href="#" onclick="showTab('shareout',this)">Share-Out</a><a href="#" onclick="showTab('terms',this)">Terms</a><a href="#" onclick="showTab('register',this)">Add</a></div><script>const PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products"];function showTab(id,el){document.querySelectorAll('[id^="tab-"]').forEach(e=>e.classList.add('hide'));document.getElementById('tab-'+id).classList.remove('hide');document.querySelectorAll('.nav a').forEach(t=>t.classList.remove('on'));if(el && el.classList) el.classList.add('on');if(id=='history')loadHistory();if(id=='community')loadPosts();window.scrollTo(0,0);}function fillDropdowns(){document.getElementById('projFilter').innerHTML='<option>All Projects</option>'+PROJECTS.map(p=>'<option>'+p+'</option>').join('');document.getElementById('rProj').innerHTML=PROJECTS.map(p=>'<option>'+p+'</option>').join('');document.getElementById('soProj').innerHTML='<option>All Projects</option>'+PROJECTS.map(p=>'<option>'+p+'</option>').join('');}async function loadStats(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('countLabel').textContent=d.total_members;}catch(e){}}async function loadMembers(){let q=document.getElementById('searchBox').value||'';let proj=document.getElementById('projFilter').value||'All Projects';let r=await fetch('/api/members?search='+encodeURIComponent(q)+'&project='+encodeURIComponent(proj));let d=await r.json();let h='<table><tr><th>Name</th><th>Phone</th><th>Project</th><th>Amount</th></tr>';d.members.forEach(m=>{h+='<tr><td>'+m.name+'</td><td>'+m.phone+'</td><td>'+m.project+'</td><td>'+m.amount+'</td></tr>';});h+='</table><p style="font-family:Arial">Showing '+d.members.length+' members</p>';document.getElementById('membersList').innerHTML=h;let dist='';let counts={};d.members.forEach(m=>{counts[m.project]=(counts[m.project]||0)+1;});for(let k in counts){dist+='<div class="row"><span>'+k+'</span>'+counts[k]+'</div>';}document.getElementById('distList').innerHTML=dist||'<p style="font-family:Arial">Loading...</p>';}async function doRegister(){let b={name:document.getElementById('rName').value,phone:document.getElementById('rPhone').value,project:document.getElementById('rProj').value,amount:document.getElementById('rAmt').value};let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});let d=await r.json();document.getElementById('regMsg').textContent=d.message||'Registered';loadMembers();loadStats();}async function doShareOut(){let p=document.getElementById('soProj').value;let r=await fetch('/api/shareout?project='+encodeURIComponent(p));let d=await r.json();document.getElementById('soResult').innerHTML='Project: '+d.project+'
Members: '+d.count+'
Total: '+d.total+'
Per Member: '+d.per_member+'

Balance to share: KES 605,759 - Retained: KES 250,000';}async function loadHistory(){let r=await fetch('/api/history');let d=await r.json();document.getElementById('histList').innerHTML=d.items.map(x=>'<div class="card">'+x.created+' - '+x.action+' - '+x.detail+'</div>').join('')||'<p style="font-family:Arial">No history yet</p>';let ah=document.getElementById('adminHist');if(ah)ah.innerHTML=document.getElementById('histList').innerHTML;}async function loadPosts(){let r=await fetch('/api/posts');let d=await r.json();let list=document.getElementById('postsList');if(!d.items || d.items.length==0){list.innerHTML='<div class="card"><p style="font-family:Arial">Welcome to LONMA FIG Community. Post your first update.</p></div>';return;}list.innerHTML=d.items.map(x=>'<div class="card post">'+x.author+'<div style="color:#777;font-size:13px">'+x.created+'</div><p>'+x.text+'</p></div>').join('');}async function sendChat(){let v=document.getElementById('chatIn').value;if(!v)return;let r=await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:"Marlon Ang'undu Kikuyu",email:"marlonkikuyu@gmail.com",text:v})});document.getElementById('chatIn').value='';loadPosts();}fillDropdowns();loadStats();loadMembers();loadPosts();</script></body></html>"""
@app.route("/")
def home():
    init_db()
    return render_template_string(HTML)
@app.route("/members")
def members_page():
    init_db()
    return render_template_string(HTML)
@app.route("/community")
def community_page():
    init_db()
    return render_template_string(HTML)
@app.route("/terms")
def terms_page():
    init_db()
    return render_template_string(HTML)
@app.route("/api/stats")
def stats():
    init_db()
    db = get_db()
    total = db.execute("SELECT COUNT(id) as c FROM members").fetchone()["c"]
    return jsonify({"total_members": total, "total_amount": 855759, "to_share": 605759, "retained": 250000, "projects_total": 8, "version": "v121"})
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
        t = 605759
    else:
        c = db.execute("SELECT COUNT(id) as c FROM members WHERE project=?", (proj,)).fetchone()["c"]
        t = db.execute("SELECT COALESCE(SUM(amount),0) as s FROM members WHERE project=?", (proj,)).fetchone()["s"]
    per = round(t / c, 2) if c else 0
    if proj == "All Projects":
        per = round(605759 / c, 2) if c else 0
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
@app.route("/api/posts", methods=["GET", "POST"])
def posts():
    init_db()
    db = get_db()
    if request.method == "POST":
        d = request.get_json(force=True)
        db.execute("INSERT INTO posts (author, email, text, created) VALUES (?,?,?,?)", (d.get("author") or "MA", d.get("email") or "", d.get("text") or "", datetime.datetime.now().isoformat()))
        db.commit()
        return jsonify({"message": "Posted"})
    rows = db.execute("SELECT id, author, email, text, created FROM posts ORDER BY id DESC LIMIT 50").fetchall()
    out = []
    for r in rows:
        out.append({"id": r["id"], "author": r["author"], "email": r["email"], "text": r["text"], "created": r["created"]})
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
