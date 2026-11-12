
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
    db.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, email TEXT, text TEXT, likes INTEGER DEFAULT 0, reposts INTEGER DEFAULT 0, created TEXT)")
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
    p = db.execute("SELECT COUNT(id) as c FROM posts").fetchone()["c"]
    if p == 0:
        db.execute("INSERT INTO posts (author, email, text, likes, reposts, created) VALUES (?,?,?,?,?,?)", ("F.I.G Brands", "admin@lonma.com", "Welcome to F.I.G Welfare. Balance brought forward KES 855,759. Share fairly.", 24, 8, datetime.datetime.now().isoformat()))
        db.execute("INSERT INTO posts (author, email, text, likes, reposts, created) VALUES (?,?,?,?,?,?)", ("Marlon Ang'undu Kikuyu", "marlonkikuyu@gmail.com", "Reminder: Contribution KES 300 monthly. Be kind - no insults, no politics.", 12, 3, datetime.datetime.now().isoformat()))
        db.commit()
@app.teardown_appcontext
def close_db(e):
    db = getattr(g, "_db", None)
    if db is not None:
        db.close()
HTML = """<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1"><title>F.I.G BRANDS - Twitter Style</title><style>body{font-family:Arial;margin:0;background:#faf7f0;color:#0a2540;padding-bottom:110px}header{background:#fff;padding:10px 14px;display:flex;justify-content:space-between;align-items:center;position:sticky;top:0;z-index:20;border-bottom:1px solid #eee}.fig{background:#0a2540;color:#fff;width:44px;height:44px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-weight:bold}.avatar{background:#0a2540;color:#fff;width:36px;height:36px;border-radius:50%;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:bold}.toptabs{display:flex;background:#fff;position:sticky;top:64px;z-index:19;border-bottom:1px solid #eee}.toptabs div{flex:1;text-align:center;padding:14px 4px;font-weight:bold;cursor:pointer;font-size:14px}.toptabs div.on{border-bottom:3px solid #0a2540}.wrap{padding:12px}.card{background:#fff;border-radius:16px;padding:16px;margin:12px 0;box-shadow:0 1px 8px rgba(0,0,0,0.06)}.eyebrow{color:#c9a86a;letter-spacing:2px;font-size:11px;font-weight:bold}.h1{font-family:Georgia;font-size:36px;margin:6px 0}.sub{color:#555;line-height:1.5}.big{font-size:48px;margin:6px 0;font-family:Georgia}.dark{background:#0a2540;color:#fff;border-radius:16px;padding:18px;margin:12px 0}.label{color:#c9a86a;letter-spacing:2px;font-size:11px}.gold{background:#c9a86a;color:#fff;border:0;padding:12px 18px;border-radius:30px;font-weight:bold}.navy{background:#0a2540;color:#fff;border:0;padding:12px 18px;border-radius:30px;font-weight:bold}.light{background:#eee;border:0;padding:10px 14px;border-radius:30px}input,select,textarea{width:100%;padding:12px;margin:6px 0;border:1px solid #ddd;border-radius:12px;box-sizing:border-box}table{width:100%;border-collapse:collapse}th,td{padding:8px;border-bottom:1px solid #eee;text-align:left;font-size:14px}.hide{display:none}.row{display:flex;justify-content:space-between;padding:9px 0;border-bottom:1px solid #f0f0f0}.tweet{display:flex;gap:10px;padding:14px 0;border-bottom:1px solid #eee}.actions{display:flex;gap:18px;margin-top:8px;color:#666;font-size:13px}.actions span{cursor:pointer}.bottom{position:fixed;bottom:0;left:0;right:0;background:#fff;border-top:1px solid #eee;display:flex;justify-content:space-around;padding:10px 4px 14px;z-index:30}.bottom div{text-align:center;cursor:pointer;font-size:11px;color:#666}.bottom div.on{color:#0a2540;font-weight:bold}.bottom .ic{font-size:24px;display:block}.fab{position:fixed;right:16px;bottom:84px;width:56px;height:56px;border-radius:50%;background:#0a2540;color:#fff;font-size:30px;border:0;z-index:31;box-shadow:0 4px 14px rgba(0,0,0,0.3);cursor:pointer}.composer{position:fixed;left:0;right:0;bottom:0;background:#fff;padding:14px;z-index:40;border-top:1px solid #ddd;box-shadow:0 -4px 20px rgba(0,0,0,0.15)}.notifdot{background:#c0392b;color:#fff;border-radius:50%;padding:1px 6px;font-size:11px;margin-left:2px}</style></head><body><header><div style="display:flex;gap:10px;align-items:center"><div class="fig">FIG</div><div>F.I.G BRANDS<div style="font-size:11px;letter-spacing:2px;color:#777">WELFARE SYSTEM</div></div></div><div style="display:flex;gap:10px;align-items:center"><span style="font-size:22px" onclick="showTab('notifications',null)">🔔<span class="notifdot" id="notifCount">2</span></span><div class="avatar" onclick="showTab('profile',null)">MA</div></div></header><div class="toptabs"><div id="tt-home" class="on" onclick="showTab('overview',this)">Home</div><div id="tt-feed" onclick="showTab('community',this)">Community</div><div id="tt-members" onclick="showTab('members',this)">Members</div><div id="tt-share" onclick="showTab('shareout',this)">Share-Out</div></div><div class="wrap"><div id="tab-overview"><div class="eyebrow">F.I.G BRANDS - WELFARE</div><div class="h1">Overview</div><p class="sub">Balance brought forward, less KES 250,000 retained - shared fairly, per month of contributions.</p><div class="card"><div style="color:#666;letter-spacing:2px;font-size:12px">TOTAL MEMBERS</div><div class="big" id="countLabel">160</div></div><div class="card"><div style="color:#666;letter-spacing:2px;font-size:12px">PROJECTS</div><div class="big">8</div></div><div class="dark"><div class="label">BALANCE BROUGHT FORWARD</div><div style="font-size:40px;font-family:Georgia">KES 855,759</div><div style="color:#ddd;font-size:14px">KES 605,759 to share - KES 250,000 retained</div></div><div class="card"><div class="eyebrow">WELFARE CLAUSES 2026</div><h2 style="font-family:Georgia;font-size:28px;line-height:1.2">Death Benefit: Member 100,000 - Spouse 50,000 - Child 40,000 - Parents 40,000</h2><p class="sub">Loss of Earning: 50 percent of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><button class="navy" onclick="showTab('terms',null)">Read Full Terms</button> <button class="gold" onclick="showTab('community',null)">Join Community Chat</button></div><div class="card"><div class="eyebrow">DISTRIBUTION</div><h2 style="font-family:Georgia">Project Distribution</h2><div id="distList"></div></div><div class="card"><h3>Latest from Community</h3><div id="homeFeed"></div><button class="navy" onclick="showTab('community',null)" style="width:100%">View All Posts</button></div></div><div id="tab-members" class="hide"><div class="h1">Members</div><input id="searchBox" placeholder="Search on Twitter style - name or phone..." oninput="loadMembers()"><select id="projFilter" onchange="loadMembers()"></select><div id="membersList"></div></div><div id="tab-register" class="hide"><div class="h1">Register</div><div class="card"><input id="rName" placeholder="Full Name"><input id="rPhone" placeholder="Phone 07..."><select id="rProj"></select><input id="rAmt" type="number" value="1000"><button class="navy" style="width:100%" onclick="doRegister()">Register Member</button><div id="regMsg" style="margin-top:10px"></div></div></div><div id="tab-shareout" class="hide"><div class="h1">Share-Out</div><div class="card"><select id="soProj"></select><button class="navy" style="width:100%" onclick="doShareOut()">Calculate Share-Out</button><div id="soResult" style="margin-top:12px;line-height:1.7"></div></div></div><div id="tab-history" class="hide"><div class="h1">History</div><div id="histList"></div></div><div id="tab-terms" class="hide"><div class="eyebrow">WELFARE CLAUSES 2026</div><div class="h1">Terms</div><div class="card"><h3>Death Benefit</h3><p class="sub">Member 100,000 - Spouse 50,000 - Child 40,000 - Parents 40,000</p><h3>Loss of Earning</h3><p class="sub">50 percent of basic pay, up to KES 20,000, after 10 days unable to work.</p><h3>Share-Out</h3><p class="sub">Balance less KES 250,000 retained, shared per month.</p><h3>Community</h3><p class="sub">Be kind - no insults, no politics.</p></div></div><div id="tab-community" class="hide"><div class="h1" style="font-size:34px">Community Chat</div><p class="sub">Post, repost, share, save. Be kind - no insults, no politics.</p><div class="card"><div style="display:flex;gap:10px"><div class="avatar">MA</div><div>Marlon Ang'undu Kikuyu<div style="color:#777;font-size:13px">marlonkikuyu@gmail.com</div></div></div><textarea id="chatIn" rows="3" placeholder="What is happening? Post like on Twitter..."></textarea><div style="display:flex;gap:8px"><button class="light">Photo</button><button class="light">Video</button><button class="navy" onclick="sendChat()">Post</button></div></div><div id="postsList"></div></div><div id="tab-notifications" class="hide"><div class="h1">Notifications</div><div class="card"><p>F.I.G Brands - Share-Out is ready. KES 605,759 to share.</p><p>Admin - New member registered.</p><p>Community - Marlon posted in Community.</p></div></div><div id="tab-profile" class="hide"><div class="h1">Profile</div><div class="card"><div style="display:flex;gap:12px;align-items:center"><div class="avatar" style="width:64px;height:64px;font-size:20px">MA</div><div><b style="font-size:20px">Marlon Ang'undu Kikuyu<div style="color:#777">marlonkikuyu@gmail.com</div><div style="color:#777;font-size:13px">Member - F.I.G Brands Welfare</div></div></div><p class="sub">160 members - 8 projects - KES 855,759 balance</p><button class="navy" onclick="showTab('register',null)">Add Member</button> <button class="gold" onclick="showTab('community',null)">My Posts</button></div><div id="myPosts"></div></div><div id="tab-admin" class="hide"><div class="h1">Admin</div><div class="card"><p>Admin: admin@lonma.com / admin123</p><button class="navy" onclick="loadHistory()">View History</button><div id="adminHist"></div></div></div></div><button class="fab" onclick="openComposer()">+</button><div id="composer" class="composer hide"><div style="display:flex;justify-content:space-between">New Post<span onclick="closeComposer()" style="cursor:pointer;font-size:20px">X</span></div><textarea id="fabText" rows="3" placeholder="What is happening?"></textarea><button class="navy" style="width:100%" onclick="sendFab()">Post to Community</button></div><div class="bottom"><div class="on" onclick="navTo('overview',this)"><span class="ic">🏠</span>Home</div><div onclick="navTo('members',this)"><span class="ic">🔍</span>Search</div><div onclick="navTo('community',this)"><span class="ic">👥</span>Community</div><div onclick="navTo('notifications',this)"><span class="ic">🔔</span>Alerts</div><div onclick="navTo('profile',this)"><span class="ic">👤</span>Profile</div></div><script>const PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products"];function showTab(id,el){document.querySelectorAll('[id^="tab-"]').forEach(e=>e.classList.add('hide'));let t=document.getElementById('tab-'+id);if(t)t.classList.remove('hide');document.querySelectorAll('.toptabs div').forEach(x=>x.classList.remove('on'));if(id=='overview')document.getElementById('tt-home').classList.add('on');if(id=='community')document.getElementById('tt-feed').classList.add('on');if(id=='members')document.getElementById('tt-members').classList.add('on');if(id=='shareout')document.getElementById('tt-share').classList.add('on');if(id=='history')loadHistory();if(id=='community')loadPosts();if(id=='profile')loadPosts();window.scrollTo(0,0);}function navTo(id,el){document.querySelectorAll('.bottom div').forEach(d=>d.classList.remove('on'));if(el)el.classList.add('on');showTab(id,null);}function openComposer(){document.getElementById('composer').classList.remove('hide');}function closeComposer(){document.getElementById('composer').classList.add('hide');}function fillDropdowns(){document.getElementById('projFilter').innerHTML='<option>All Projects</option>'+PROJECTS.map(p=>'<option>'+p+'</option>').join('');document.getElementById('rProj').innerHTML=PROJECTS.map(p=>'<option>'+p+'</option>').join('');document.getElementById('soProj').innerHTML='<option>All Projects</option>'+PROJECTS.map(p=>'<option>'+p+'</option>').join('');}async function loadStats(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('countLabel').textContent=d.total_members;}catch(e){}}async function loadMembers(){let q=document.getElementById('searchBox').value||'';let proj=document.getElementById('projFilter').value||'All Projects';let r=await fetch('/api/members?search='+encodeURIComponent(q)+'&project='+encodeURIComponent(proj));let d=await r.json();let h='<table><tr><th>Name</th><th>Phone</th><th>Project</th><th>Amount</th></tr>';d.members.forEach(m=>{h+='<tr><td>'+m.name+'</td><td>'+m.phone+'</td><td>'+m.project+'</td><td>'+m.amount+'</td></tr>';});h+='</table><p>Showing '+d.members.length+' members</p>';document.getElementById('membersList').innerHTML=h;let counts={};d.members.forEach(m=>{counts[m.project]=(counts[m.project]||0)+1;});let dist='';for(let k in counts){dist+='<div class="row"><span>'+k+'</span>'+counts[k]+'</div>';}document.getElementById('distList').innerHTML=dist;}async function doRegister(){let b={name:document.getElementById('rName').value,phone:document.getElementById('rPhone').value,project:document.getElementById('rProj').value,amount:document.getElementById('rAmt').value};let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(b)});let d=await r.json();document.getElementById('regMsg').textContent=d.message||'Registered';loadMembers();loadStats();}async function doShareOut(){let p=document.getElementById('soProj').value;let r=await fetch('/api/shareout?project='+encodeURIComponent(p));let d=await r.json();document.getElementById('soResult').innerHTML='Project: '+d.project+'
Members: '+d.count+'
Total: '+d.total+'
Per Member: '+d.per_member+'';}async function loadHistory(){let r=await fetch('/api/history');let d=await r.json();document.getElementById('histList').innerHTML=d.items.map(x=>'<div class="card">'+x.created+' - '+x.action+' - '+x.detail+'</div>').join('')||'<p>No history yet</p>';let ah=document.getElementById('adminHist');if(ah)ah.innerHTML=document.getElementById('histList').innerHTML;}async function loadPosts(){let r=await fetch('/api/posts');let d=await r.json();let html=d.items.map(x=>'<div class="tweet"><div class="avatar">'+x.author.substring(0,2).toUpperCase()+'</div><div style="flex:1">'+x.author+'<div style="color:#777;font-size:13px">'+x.created+'</div><div style="margin-top:6px;line-height:1.5">'+x.text+'</div><div class="actions"><span onclick="likePost('+x.id+',this)">♡ '+x.likes+'</span><span onclick="repostPost('+x.id+',this)">↻ '+x.reposts+'</span><span>💬 Reply</span><span>🔖 Save</span></div></div></div>').join('');let pl=document.getElementById('postsList');if(pl)pl.innerHTML=html;let hf=document.getElementById('homeFeed');if(hf)hf.innerHTML=html.substring(0,800);let mp=document.getElementById('myPosts');if(mp)mp.innerHTML='<div class="card"><h3>My Posts</h3>'+html+'</div>';}async function likePost(id,el){let r=await fetch('/api/like/'+id,{method:'POST'});let d=await r.json();if(el)el.textContent='♥ '+d.likes;loadPosts();}async function repostPost(id,el){let r=await fetch('/api/repost/'+id,{method:'POST'});let d=await r.json();if(el)el.textContent='↻ '+d.reposts;loadPosts();}async function sendChat(){let v=document.getElementById('chatIn').value;if(!v)return;await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:"Marlon Ang'undu Kikuyu",email:"marlonkikuyu@gmail.com",text:v})});document.getElementById('chatIn').value='';loadPosts();}async function sendFab(){let v=document.getElementById('fabText').value;if(!v)return;await fetch('/api/posts',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({author:"Marlon Ang'undu Kikuyu",email:"marlonkikuyu@gmail.com",text:v})});document.getElementById('fabText').value='';closeComposer();showTab('community',null);loadPosts();}fillDropdowns();loadStats();loadMembers();loadPosts();</script></body></html>"""
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
    return jsonify({"total_members": total, "total_amount": 855759, "to_share": 605759, "retained": 250000, "projects_total": 8, "version": "v122"})
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
        db.execute("INSERT INTO posts (author, email, text, likes, reposts, created) VALUES (?,?,?,?,?,?)", (d.get("author") or "MA", d.get("email") or "", d.get("text") or "", 0, 0, datetime.datetime.now().isoformat()))
        db.commit()
        return jsonify({"message": "Posted"})
    rows = db.execute("SELECT id, author, email, text, likes, reposts, created FROM posts ORDER BY id DESC LIMIT 50").fetchall()
    out = []
    for r in rows:
        out.append({"id": r["id"], "author": r["author"], "email": r["email"], "text": r["text"], "likes": r["likes"], "reposts": r["reposts"], "created": r["created"]})
    return jsonify({"items": out})
@app.route("/api/like/int:pid", methods=["POST"])
def like_post(pid):
    init_db()
    db = get_db()
    db.execute("UPDATE posts SET likes = likes + 1 WHERE id=?", (pid,))
    db.commit()
    r = db.execute("SELECT likes FROM posts WHERE id=?", (pid,)).fetchone()
    return jsonify({"likes": r["likes"] if r else 0})
@app.route("/api/repost/int:pid", methods=["POST"])
def repost_post(pid):
    init_db()
    db = get_db()
    db.execute("UPDATE posts SET reposts = reposts + 1 WHERE id=?", (pid,))
    db.commit()
    r = db.execute("SELECT reposts FROM posts WHERE id=?", (pid,)).fetchone()
    return jsonify({"reposts": r["reposts"] if r else 0})
@app.route("/api/notifications")
def notif():
    return jsonify({"count": 2, "items": [{"text": "Share-Out is ready"}, {"text": "New member registered"}]})
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
