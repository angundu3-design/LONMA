import sqlite3, os, secrets, io, re
from flask import Flask, request, jsonify, render_template_string, redirect, send_file
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB = "lonma.db"

PROJECTS = ["Antonia", "GCB-MT", "GCB-TDs", "Higchem", "HQ", "Java House", "Kanji", "Pwani Oil Products", "SC Johnson", "TF-LM", "TF-MT"]

PWANI_LOGO = "https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png"
JAVA_LOGO = "https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_1.jpg"
SCJ_LOGO = "https://bhp-plus.pl/usr/s.c.-johnson-logo.png"
HIGHCHEM_LOGO = "https://directory.africa-business.com/assets/uploads/logo/higchemafrica1.png"
TRUFOODS_LOGO = "https://www.viprocgeneralenterprises.co.ke/site-images/Trufoods%20Limited.jpg"

PMAP = {"Antonia": "Antonia", "ANTONIA": "Antonia", "Antonia1": "Antonia", "GCB-MT": "GCB-MT", "GCB MT": "GCB-MT", "GCB": "GCB-MT", "GCB-Ms": "GCB-MT",
"GCB-TDs": "GCB-TDs", "GCB Vs": "GCB-TDs", "GCB TDS": "GCB-TDs", "GCB-TDS": "GCB-TDs", "GCB-TDs": "GCB-TDs",
"Higchem": "Higchem", "HIGHCHEM": "Higchem", "HIGCHEM MARKETING": "Higchem", "Kanji": "Kanji", "KHS": "Kanji", "Kaysalt": "Kanji", "Kenafric": "Kanji",
"HQ": "HQ", "Java": "Java House", "Pwani Oil Products": "Pwani Oil Products", "LAB": "Kanji", "Java House": "Java House", "JAVA": "Java House",
"Pwani": "Pwani Oil Products", "Pwani Oil Products Ltd.": "Pwani Oil Products", "PWANI": "Pwani Oil Products", "Pwani1": "Pwani Oil Products",
"SC Johnson": "SC Johnson", "JOHNSON": "SC Johnson", "Johnson": "SC Johnson", "SJ": "SC Johnson", "S Johnson": "SC Johnson",
"SCJohnson": "SC Johnson", "ScJohnsons": "SC Johnson", "TF WSL": "TF WSL", "TF WS": "TF WSL", "TF-LM": "TF-LM", "TF LM": "TF-LM",
"TF-MT": "TF-MT", "TF MT": "TF-MT", "TF WSL": "TF WSL", "TF": "TF WSL", "TF-LM": "TF-LM", "TF-MT": "TF-MT"}

def db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = db()
    c.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, phone TEXT, project TEXT, status TEXT DEFAULT 'Active', shares REAL DEFAULT 0, total_contributed REAL DEFAULT 0, joined TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS contributions (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, amount REAL, date TEXT, type TEXT, project TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS loans (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, amount REAL, status TEXT DEFAULT 'Pending', date TEXT, project TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS community (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, message TEXT, likes INTEGER DEFAULT 0, date TEXT, project TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, message TEXT, date TEXT, read INTEGER DEFAULT 0)")
    c.execute("CREATE TABLE IF NOT EXISTS shareout (id INTEGER PRIMARY KEY AUTOINCREMENT, member_id INTEGER, amount REAL, date TEXT)")
    c.commit()
    cnt = c.execute("SELECT COUNT(*) as n FROM members").fetchone()["n"]
    if cnt == 0:
        seed(c)
    c.close()

def seed(c):
    names = [("Mary Achieng","marlonkikuyu@gmail.com","0712345678","Pwani Oil Products"),("John Otieno","john@gmail.com","0722345678","Java House"),("Grace Wanjiru","grace@gmail.com","0733345678","SC Johnson"),("Peter Kamau","peter@gmail.com","0744345678","Higchem"),("Sarah Njeri","sarah@gmail.com","0755345678","Kanji"),("David Mwangi","david@gmail.com","0766345678","GCB-MT"),("Faith Atieno","faith@gmail.com","0777345678","GCB-TDs"),("Joseph Kiprop","joseph@gmail.com","0788345678","Antonia"),("Esther Muthoni","esther@gmail.com","0799345678","TF-LM"),("Daniel Onyango","daniel@gmail.com","0710345678","TF-MT")]
    for n,e,p,proj in names:
        c.execute("INSERT INTO members (name,email,phone,project,shares,total_contributed,joined) VALUES (?,?,?,?,?,?,?)",(n,e,p,proj,20,20000,"2025-01-15"))
    mids = [r["id"] for r in c.execute("SELECT id FROM members").fetchall()]
    total = 0
    for i in range(200):
        mid = mids[i % len(mids)]
        amt = 1000
        c.execute("INSERT INTO contributions (member_id,amount,date,type,project) VALUES (?,?,?,?,?)",(mid,amt,"2026-11-01","Monthly Contribution","HQ"))
        total += 1
    for i in range(15):
        c.execute("INSERT INTO loans (member_id,amount,status,date,project) VALUES (?,?,?,?,?)",(mids[i % len(mids)],5000,"Approved","2026-10-20","HQ"))
    for i in range(10):
        c.execute("INSERT INTO community (name,email,message,likes,date,project) VALUES (?,?,?,?,?,?)",(f"Member {i+1}","marlonkikuyu@gmail.com",f"Hello LONMA community! Update {i+1} - let's grow together.",i+2,"2026-11-10","HQ"))
    c.execute("INSERT INTO notifications (title,message,date) VALUES (?,?,?)",("Welcome to LONMA Orbit","Your account is active. Welcome!","2026-11-14"))
    c.execute("INSERT INTO notifications (title,message,date) VALUES (?,?,?)",("Contribution Received","Your KES 1000 contribution was received.","2026-11-14"))
    c.commit()
    print(f"v113 seeded 239")

init_db()

BASE_CSS = """
body{font-family:Arial,Helvetica,sans-serif;margin:0;background:#f4f6f8;color:#222}
header{background:#0b3d91;color:#fff;padding:18px;text-align:center}
header h1{margin:0;font-size:26px;letter-spacing:1px}
header p{margin:4px 0 0;opacity:.9}
nav{display:flex;gap:8px;justify-content:center;padding:12px;flex-wrap:wrap;background:#fff;box-shadow:0 1px 4px rgba(0,0,0,.08)}
nav a{background:#eef2ff;padding:10px 16px;border-radius:20px;text-decoration:none;color:#0b3d91;font-weight:bold}
.card{background:#fff;margin:12px;padding:16px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.08)}
.big{font-size:26px;font-weight:bold;color:#0b3d91}
.grid{display:grid;grid-template-columns:repeat(auto-fit,minmax(150px,1fr));gap:12px}
table{width:100%;border-collapse:collapse} td,th{padding:8px;border-bottom:1px solid #eee;text-align:left;font-size:14px}
button{background:#0b3d91;color:#fff;border:0;padding:10px 16px;border-radius:8px;cursor:pointer}
input,select,textarea{padding:10px;width:100%;margin:6px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}
.logo{height:32px;margin:4px;border-radius:6px;background:#fff;padding:2px}
.badge{background:#e6f4ea;color:#137333;padding:4px 10px;border-radius:12px;font-size:12px}
"""

NAV = """<header><h1>LONMA ORBIT</h1><p>Members &bull; Savings &bull; Loans &bull; Shareout &bull; Community</p>
<div><img class="logo" src="PWANI_LOGO"><img class="logo" src="JAVA_LOGO"><img class="logo" src="SCJ_LOGO"><img class="logo" src="HIGHCHEM_LOGO"></div></header>
<nav><a href="/">Home</a><a href="/members">Members</a><a href="/shareout">Shareout</a><a href="/breakdown2">Breakdown2</a><a href="/community">Community</a><a href="/contributions">Contributions</a><a href="/loans">Loans</a></nav>"""
NAV = NAV.replace("PWANI_LOGO", PWANI_LOGO).replace("JAVA_LOGO", JAVA_LOGO).replace("SCJ_LOGO", SCJ_LOGO).replace("HIGHCHEM_LOGO", HIGHCHEM_LOGO)

HOME_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>LONMA Orbit</title><style>CSS</style></head>
<body>NAV
<div class="card"><h2>Dashboard - LONMA Orbit v113</h2><div class="grid">
<div><div>Total Members</div><div class="big" id="tm">-</div></div>
<div><div>Total Contributions</div><div class="big" id="tc">-</div></div>
<div><div>Total Loans</div><div class="big" id="tl">-</div></div>
<div><div>Projects</div><div class="big">11</div></div></div>
<p><span class="badge">Live</span> <span id="notif"></span></p></div>
<div class="card"><h2>Projects</h2><div id="projects"></div></div>
<div class="card"><h2>Add Member</h2><input id="mName" placeholder="Full Name"><input id="mPhone" placeholder="Phone"><input id="mEmail" placeholder="Email"><select id="mProj"><option>HQ</option><option>Pwani Oil Products</option><option>Java House</option><option>SC Johnson</option><option>Higchem</option><option>Kanji</option><option>GCB-MT</option><option>GCB-TDs</option><option>Antonia</option><option>TF-LM</option><option>TF-MT</option></select><button onclick="addM()">Add Member</button><p id="msg"></p></div>
<div class="card"><h2>Members</h2><div id="list">Loading...</div></div>
<div class="card"><h2>Shareout Preview</h2><div id="share"></div></div>
<script>
async function load(){
 let r=await fetch('/api/stats'); let s=await r.json();
 document.getElementById('tm').innerText=s.total_members;
 document.getElementById('tc').innerText='KES '+s.total_contributions;
 document.getElementById('tl').innerText='KES '+s.total_loans;
 let pr=await fetch('/api/projects'); let pj=await pr.json();
 document.getElementById('projects').innerHTML=pj.map(x=>'<span class="badge" style="margin:2px;display:inline-block">'+x+'</span>').join('');
 let r2=await fetch('/api/members'); let m=await r2.json();
 let h='<table><tr><th>#</th><th>Name</th><th>Project</th><th>Phone</th><th>Shares</th></tr>';
 m.forEach(x=>{h+=`<tr><td>${x.id}</td><td>${x.name}</td><td>${x.project||''}</td><td>${x.phone||''}</td><td>${x.shares}</td></tr>`});
 h+='</table>'; document.getElementById('list').innerHTML=h;
 let r3=await fetch('/api/shareout'); let sh=await r3.json();
 document.getElementById('share').innerHTML='Pool: KES '+sh.total_pool+' | Per Member: KES '+sh.per_member+' | Members: '+sh.members;
 let rn=await fetch('/api/notifications'); let nn=await rn.json();
 document.getElementById('notif').innerText=nn.length+' notifications';
}
async function addM(){
 let name=document.getElementById('mName').value; let phone=document.getElementById('mPhone').value; let email=document.getElementById('mEmail').value; let proj=document.getElementById('mProj').value;
 if(!name){alert('Enter name');return;}
 let r=await fetch('/api/members',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,phone:phone,email:email,project:proj})});
 let d=await r.json(); document.getElementById('msg').innerText=d.message||'Added'; load();
}
load();
</script></body></html>"""
HOME_HTML = HOME_HTML.replace("CSS", BASE_CSS).replace("NAV", NAV)

COMMUNITY_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Community - LONMA</title><style>CSS</style></head>
<body>NAV
<div class="card"><h2>Community</h2><p>Share updates with all LONMA members.</p><input id="cName" placeholder="Your Name"><input id="cEmail" placeholder="Email"><textarea id="cMsg" placeholder="Write a message..."></textarea><button onclick="postC()">Post</button><p id="cmsg"></p></div>
<div class="card"><h2>Posts</h2><div id="posts">Loading...</div></div>
<script>
async function loadC(){
 let email=document.getElementById('cEmail').value||'marlonkikuyu@gmail.com';
 let r=await fetch('/api/community?filter=all&email='+encodeURIComponent(email)); let d=await r.json();
 let h=''; d.forEach(p=>{h+=`<div style="border-bottom:1px solid #eee;padding:10px 0"><b>${p.name}</b> <span style="color:#888">${p.date} | ${p.project||''}</span><div>${p.message}</div><small>Likes: ${p.likes||0}</small></div>`});
 document.getElementById('posts').innerHTML=h||'No posts yet';
 let s=await (await fetch('/api/stats')).json(); 
}
async function postC(){
 let name=document.getElementById('cName').value; let email=document.getElementById('cEmail').value; let msg=document.getElementById('cMsg').value;
 if(!msg){alert('Write message');return;}
 await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name||'Member',email:email,message:msg,project:'HQ'})});
 document.getElementById('cmsg').innerText='Posted!'; loadC();
}
loadC();
</script></body></html>"""
COMMUNITY_HTML = COMMUNITY_HTML.replace("CSS", BASE_CSS).replace("NAV", NAV)

BREAKDOWN_HTML = """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Breakdown2 - LONMA</title><style>CSS</style></head>
<body>NAV
<div class="card"><h2>Breakdown2 - By Project</h2><div id="bd">Loading...</div></div>
<div class="card"><h2>Shareout Breakdown</h2><div id="sh"></div></div>
<script>
async function load(){
 let r=await fetch('/api/breakdown2'); let d=await r.json();
 let h='<table><tr><th>Project</th><th>Members</th><th>Contributions</th><th>Loans</th></tr>';
 d.forEach(x=>{h+=`<tr><td>${x.project}</td><td>${x.members}</td><td>${x.contributions}</td><td>${x.loans}</td></tr>`});
 h+='</table>'; document.getElementById('bd').innerHTML=h;
 let s=await (await fetch('/api/shareout')).json();
 document.getElementById('sh').innerHTML='Total Pool KES '+s.total_pool+' | Per Member KES '+s.per_member;
}
load();
</script></body></html>"""
BREAKDOWN_HTML = BREAKDOWN_HTML.replace("CSS", BASE_CSS).replace("NAV", NAV)

@app.route("/")
def home():
    return render_template_string(HOME_HTML)

@app.route("/members")
def members_page():
    return render_template_string(HOME_HTML)

@app.route("/shareout")
def shareout_page():
    return render_template_string(HOME_HTML)

@app.route("/contributions")
def contrib_page():
    return render_template_string(HOME_HTML)

@app.route("/loans")
def loans_page():
    return render_template_string(HOME_HTML)

@app.route("/community")
def community_page():
    return render_template_string(COMMUNITY_HTML)

@app.route("/breakdown2")
def breakdown2_page():
    return render_template_string(BREAKDOWN_HTML)

@app.route("/api/stats")
def api_stats():
    c = db()
    tm = c.execute("SELECT COUNT(*) n FROM members").fetchone()["n"]
    tc = c.execute("SELECT COALESCE(SUM(amount),0) s FROM contributions").fetchone()["s"]
    tl = c.execute("SELECT COALESCE(SUM(amount),0) s FROM loans").fetchone()["s"]
    ts = c.execute("SELECT COALESCE(SUM(shares),0) s FROM members").fetchone()["s"]
    c.close()
    return jsonify({"total_members": tm, "total_contributions": tc, "total_loans": tl, "total_shares": ts})

@app.route("/api/projects")
def api_projects():
    return jsonify(PROJECTS)

@app.route("/api/members", methods=["GET", "POST"])
def api_members():
    c = db()
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        name = (d.get("name") or "").strip()
        if not name:
            c.close()
            return jsonify({"error": "Name required"}), 400
        proj = PMAP.get(d.get("project", "HQ"), d.get("project", "HQ"))
        c.execute("INSERT INTO members (name,email,phone,project,shares,total_contributed,joined) VALUES (?,?,?,?,?,?,?)",(name, d.get("email",""), d.get("phone",""), proj, 0, 0, "2026-11-14"))
        c.commit()
        nid = c.execute("SELECT last_insert_rowid() id").fetchone()["id"]
        c.close()
        return jsonify({"message": "Member added successfully", "id": nid}), 201
    rows = c.execute("SELECT * FROM members ORDER BY id").fetchall()
    out = [dict(r) for r in rows]
    c.close()
    return jsonify(out)

@app.route("/api/members/<int:mid>", methods=["GET", "DELETE"])
def api_member_one(mid):
    c = db()
    r = c.execute("SELECT * FROM members WHERE id=?", (mid,)).fetchone()
    if not r:
        c.close()
        return jsonify({"error": "Not found"}), 404
    if request.method == "DELETE":
        c.execute("DELETE FROM members WHERE id=?", (mid,))
        c.commit(); c.close()
        return jsonify({"message": "Deleted"})
    out = dict(r); c.close()
    return jsonify(out)

@app.route("/api/contributions", methods=["GET", "POST"])
def api_contrib():
    c = db()
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        try: amt = float(d.get("amount", 0))
        except: c.close(); return jsonify({"error": "Invalid amount"}), 400
        if amt <= 0: c.close(); return jsonify({"error": "Amount must be > 0"}), 400
        c.execute("INSERT INTO contributions (member_id,amount,date,type,project) VALUES (?,?,?,?,?)",(int(d.get("member_id", 1)), amt, "2026-11-14", d.get("type", "Contribution"), d.get("project", "HQ")))
        c.commit(); c.close()
        return jsonify({"message": "Contribution added"}), 201
    rows = c.execute("SELECT * FROM contributions ORDER BY id DESC LIMIT 200").fetchall()
    out = [dict(r) for r in rows]; c.close()
    return jsonify(out)

@app.route("/api/loans", methods=["GET", "POST"])
def api_loans():
    c = db()
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        try: amt = float(d.get("amount", 0))
        except: c.close(); return jsonify({"error": "Invalid amount"}), 400
        c.execute("INSERT INTO loans (member_id,amount,status,date,project) VALUES (?,?,?,?,?)",(int(d.get("member_id", 1)), amt, "Pending", "2026-11-14", d.get("project", "HQ")))
        c.commit(); c.close()
        return jsonify({"message": "Loan requested"}), 201
    rows = c.execute("SELECT * FROM loans ORDER BY id DESC").fetchall()
    out = [dict(r) for r in rows]; c.close()
    return jsonify(out)

@app.route("/api/notifications")
def api_notif():
    c = db()
    rows = c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
    out = [dict(r) for r in rows]; c.close()
    return jsonify(out)

@app.route("/api/community", methods=["GET", "POST"])
def api_community():
    c = db()
    if request.method == "POST":
        d = request.get_json(silent=True) or {}
        msg = (d.get("message") or "").strip()
        if not msg: c.close(); return jsonify({"error": "Message required"}), 400
        c.execute("INSERT INTO community (name,email,message,likes,date,project) VALUES (?,?,?,?,?,?)",(d.get("name", "Member"), d.get("email", ""), msg, 0, "2026-11-14", d.get("project", "HQ")))
        c.commit(); c.close()
        return jsonify({"message": "Posted"}), 201
    filt = request.args.get("filter", "all")
    email = request.args.get("email", "")
    if filt == "mine" and email:
        rows = c.execute("SELECT * FROM community WHERE email=? ORDER BY id DESC", (email,)).fetchall()
    else:
        rows = c.execute("SELECT * FROM community ORDER BY id DESC LIMIT 100").fetchall()
    out = [dict(r) for r in rows]; c.close()
    return jsonify(out)

@app.route("/api/shareout")
def api_shareout():
    c = db()
    total = c.execute("SELECT COALESCE(SUM(amount),0) s FROM contributions").fetchone()["s"]
    n = c.execute("SELECT COUNT(*) n FROM members").fetchone()["n"]
    per = round(total / n, 2) if n else 0
    rows = c.execute("SELECT id,name FROM members").fetchall()
    c.close()
    return jsonify({"total_pool": total, "members": n, "per_member": per, "breakdown": [{"id": r["id"], "name": r["name"], "share": per} for r in rows]})

@app.route("/api/breakdown2")
def api_breakdown2():
    c = db()
    out = []
    for p in PROJECTS:
        m = c.execute("SELECT COUNT(*) n FROM members WHERE project=?", (p,)).fetchone()["n"]
        co = c.execute("SELECT COALESCE(SUM(amount),0) s FROM contributions WHERE project=?", (p,)).fetchone()["s"]
        lo = c.execute("SELECT COALESCE(SUM(amount),0) s FROM loans WHERE project=?", (p,)).fetchone()["s"]
        out.append({"project": p, "members": m, "contributions": co, "loans": lo})
    # also HQ catch-all
    if not any(x["project"] == "HQ" for x in out):
        out.append({"project": "HQ", "members": 0, "contributions": 0, "loans": 0})
    c.close()
    return jsonify(out)

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.errorhandler(404)
def nf(e):
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template_string(HOME_HTML), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
