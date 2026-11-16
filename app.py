from flask import Flask, request, jsonify, render_template_string, redirect, send_file, session
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = secrets.token_hex(16)
DB = "lonma.db"
VERSION = "v169"
BF = 855759
RESERVE = 250000
SHARE_TABLE_2026 = {1:11, 2:10, 3:9, 4:8, 5:7, 6:6, 7:5, 8:4, 9:3, 10:2, 11:1}
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
ADMIN_KEY = "lonma_api_key_123"

PROJ = {"P":"Pwani Oil Products","S":"SC Johnson","H":"Higchem","A":"Antonia","J":"Java House"}
PROJECTS = ["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","F.I.G Brands"]

def get_db():
    c = sqlite3.connect(DB)
    c.row_factory = sqlite3.Row
    return c

def init_db():
    c = get_db()
    c.execute("CREATE TABLE IF NOT EXISTS members (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, email TEXT, staff TEXT, project TEXT, joined TEXT, father TEXT, mother TEXT, guardian TEXT)")
    c.execute("CREATE TABLE IF NOT EXISTS posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author TEXT, text TEXT, created TEXT DEFAULT CURRENT_TIMESTAMP)")
    c.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, amount TEXT, date TEXT)")
    c.commit()
    # Seed 247 if empty
    n = c.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    if n == 0:
        for i in range(1, 248):
            proj = PROJECTS[i % len(PROJECTS)]
            c.execute("INSERT INTO members (name,email,staff,project,joined,father,mother,guardian) VALUES (?,?,?,?,?,?,?,?)",
                      (f"Member {i}", f"member{i}@pwani.co.ke", f"280{i:03d}", proj, "01/09/2026", "-", "-", "-"))
        c.execute("INSERT INTO members (name,email,staff,project,joined,father,mother,guardian) VALUES (?,?,?,?,?,?,?,?)",
                  ("Marlon Kikuyu","marlonkikuyu@gmail.com","280001","HQ","01/01/2026","-","-","-"))
        c.execute("INSERT INTO members (name,email,staff,project,joined,father,mother,guardian) VALUES (?,?,?,?,?,?,?,?)",
                  ("Samuel Kikweo","samuel.nthenya@pwani.co.ke","280472","Pwani Oil Products","01/09/2026","Kikweo","Nthenya","-"))
        c.commit()
    c.close()
    print(f"{VERSION} seeded 247 added 0")

init_db()

# ---------- BASE WITH LIGHT SIDEBAR ----------
BASE = """
<!DOCTYPE html><html><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>F.I.G BRANDS - {{title}}</title>
<style>
*{box-sizing:border-box;margin:0;padding:0;font-family:Inter,system-ui,sans-serif}
body{background:#f8fafc;color:#0f2a44;padding-bottom:90px}
body.dark{background:#0b1a2e;color:#fff}
a{text-decoration:none;color:inherit}
.topbar{display:flex;align-items:center;gap:12px;padding:14px 16px;background:#fff;position:sticky;top:0;z-index:50;box-shadow:0 1px 10px rgba(0,0,0,.05)}
body.dark .topbar{background:#0f2a44}
.logo{width:48px;height:48px;background:#0f2a44;color:#fff;display:grid;place-items:center;border-radius:12px;font-weight:900}
.topbar h1{font-size:19px}.topbar p{font-size:11px;letter-spacing:2px;color:#94a3b8}
.hamburger{font-size:26px;cursor:pointer;padding:4px 8px}.avatar{margin-left:auto;width:42px;height:42px;border-radius:50%;background:#0f2a44;color:#fff;display:grid;place-items:center;font-weight:800}
.tabs{display:flex;gap:18px;padding:12px 16px;overflow-x:auto;white-space:nowrap;background:#fff;border-bottom:1px solid #e2e8f0}
body.dark .tabs{background:#0f2a44}
.tabs a{font-weight:700}
/* LIGHT SIDEBAR */
.sidebar{position:fixed;top:0;left:0;bottom:0;width:305px;background:#fff;color:#0f2a44;z-index:200;box-shadow:2px 0 25px rgba(0,0,0,.15);transform:translateX(-105%);transition:.3s}
.sidebar.open{transform:translateX(0)}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:150;display:none}.overlay.show{display:block}
.side-scroll{padding:22px 14px;overflow-y:auto;height:100%}
.side-item{display:flex;align-items:center;gap:12px;padding:12px 8px;border-radius:12px;color:#0f2a44;font-weight:600;font-size:17px}
.side-icon{width:38px;height:38px;display:grid;place-items:center;background:#eef3f6;border-radius:10px;font-size:14px;font-weight:800;flex-shrink:0}
.arrow{margin-left:auto;color:#94a3b8;font-size:22px}
.side-label{font-size:12px;letter-spacing:2px;color:#64748b;font-weight:700;margin:24px 8px 10px}
.theme-row{display:flex;gap:8px;padding:0 4px}
.theme-btn{flex:1;padding:11px 0;border:1px solid #e2e8f0;border-radius:12px;background:#fff;font-weight:700;color:#0f2a44;cursor:pointer}
.theme-btn.active{background:#0f2a44;color:#fff}
.side-footer{margin:30px 8px 10px;font-size:13px;color:#64748b;line-height:1.6}
body.dark .sidebar{background:#0f2a44;color:#fff}
body.dark .side-item{color:#fff}body.dark .side-icon{background:#1e3a56;color:#fff}
body.dark .theme-btn{background:#1e3a56;color:#fff;border-color:#1e3a56}body.dark .theme-btn.active{background:#fff;color:#0f2a44}
.container{padding:18px 16px}.page-title{font-size:36px;font-weight:900;margin:6px 0 4px}.sub{color:#64748b;margin-bottom:16px}
.card{background:#fff;border:1px solid #eef2f7;border-radius:18px;padding:18px;margin-bottom:14px}
body.dark .card{background:#132e4a;border-color:#1e3a56}
input,select,textarea{width:100%;padding:14px;border:1px solid #e2e8f0;border-radius:12px;font-size:16px;margin-bottom:12px;background:#fff}
.btn{width:100%;padding:15px;background:#0f2a44;color:#fff;border:none;border-radius:12px;font-weight:800;font-size:16px;cursor:pointer}
.member-head{display:flex;align-items:center;gap:10px;margin-bottom:14px}
.m-logo{width:46px;height:46px;border-radius:50%;background:#fef2f2;display:grid;place-items:center;font-weight:900;flex-shrink:0;border:1px solid #fee2e2}
.member-info{flex:1;min-width:0}.member-name{font-weight:800;font-size:19px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.member-email{color:#64748b;font-size:14px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}
.project-badge{background:#f1f5f9;padding:7px 10px;border-radius:20px;font-size:12px;font-weight:600;white-space:nowrap;flex-shrink:0;max-width:45%;overflow:hidden;text-overflow:ellipsis}
.row{display:flex;justify-content:space-between;padding:11px 0;border-bottom:1px solid #f1f5f9;font-size:16px}.row:last-child{border:none}.row b{font-weight:800}
.bottom{position:fixed;left:12px;right:12px;bottom:12px;background:#fff;border-radius:30px;box-shadow:0 10px 30px rgba(0,0,0,.15);display:flex;justify-content:space-around;padding:14px 6px;z-index:100}
body.dark .bottom{background:#132e4a}.bottom a{font-weight:600;font-size:14px}
.add-btn{position:fixed;right:18px;bottom:88px;background:#0f2a44;color:#fff;width:62px;height:62px;border-radius:50%;display:grid;place-items:center;font-size:28px;z-index:90;box-shadow:0 8px 20px rgba(0,0,0,.25)}
</style></head><body>
<div class="overlay" id="overlay" onclick="toggleSidebar()"></div>
<aside id="sidebar" class="sidebar"><div class="side-scroll">
<a href="/register" class="side-item"><span class="side-icon">RG</span>Register Member <span class="arrow">›</span></a>
<a href="/shareout" class="side-item"><span class="side-icon">SO</span>Share-Out <span class="arrow">›</span></a>
<a href="/history" class="side-item"><span class="side-icon">HS</span>History <span class="arrow">›</span></a>
<a href="/terms" class="side-item"><span class="side-icon">TP</span>Terms & Policies <span class="arrow">›</span></a>
<p class="side-label">APPEARANCE</p><div class="theme-row">
<button class="theme-btn active" id="btn-light" onclick="setTheme('light')">Light</button>
<button class="theme-btn" id="btn-dark" onclick="setTheme('dark')">Dark</button>
<button class="theme-btn" id="btn-system" onclick="setTheme('system')">System</button></div>
<p class="side-label">NOTIFICATIONS & SETTINGS</p>
<a href="/notifications" class="side-item"><span class="side-icon">NT</span>Notifications</a>
<a href="/admin" class="side-item"><span class="side-icon">AD</span>Admin / Settings <span class="arrow">›</span></a>
<a href="/help" class="side-item"><span class="side-icon">HP</span>Help Centre <span class="arrow">›</span></a>
<a href="/download-excel" class="side-item"><span class="side-icon">XL</span>Download Excel <span class="arrow">›</span></a>
<p class="side-label">ACCOUNT</p>
<a href="/login" class="side-item"><span class="side-icon">LG</span>Login as Admin <span class="arrow">›</span></a>
<div class="side-footer">F.I.G BRANDS Welfare · {{version}}<br>marlonkikuyu@gmail.com · +254 707 780 807</div>
</div></aside>
<div class="topbar"><span class="hamburger" onclick="toggleSidebar()">☰</span><div class="logo">FIG</div><div><h1>F.I.G BRANDS</h1><p>WELFARE SYSTEM</p></div><div class="avatar">MA</div></div>
<div class="tabs"><a href="/">Overview</a><a href="/members">Members</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/history">History</a><a href="/terms">Terms & Policies</a><a href="/admin">Admin</a></div>
<div class="container">{{content|safe}}</div>
<a href="/register" class="add-btn">+</a>
<nav class="bottom"><a href="/">Home</a><a href="/members">Members</a><a href="/shareout">Share-Out</a><a href="/terms">Terms</a><a href="/register">Add</a></nav>
<script>
function toggleSidebar(){document.getElementById('sidebar').classList.toggle('open');document.getElementById('overlay').classList.toggle('show')}
function setTheme(t){localStorage.setItem('theme',t);document.querySelectorAll('.theme-btn').forEach(b=>b.classList.remove('active'));
if(t=='light'){document.body.classList.remove('dark');document.getElementById('btn-light').classList.add('active')}
if(t=='dark'){document.body.classList.add('dark');document.getElementById('btn-dark').classList.add('active')}
if(t=='system'){document.getElementById('btn-system').classList.add('active');document.body.classList.toggle('dark',window.matchMedia('(prefers-color-scheme: dark)').matches)}}
setTheme(localStorage.getItem('theme')||'light');
</script></body></html>
"""

def page(title, content):
    return render_template_string(BASE, title=title, content=content, version=VERSION)

@app.route("/")
def home():
    c = get_db()
    total = c.execute("SELECT COUNT(*) FROM members").fetchone()[0]
    c.close()
    return page("Overview", f"""
    <div style="letter-spacing:2px;font-size:12px;color:#b45309;font-weight:700">OVERVIEW</div>
    <div class="page-title">Dashboard</div><div class="sub">{total} members · Benevolent Fund KES {BF:,}</div>
    <div class="card"><div class="row"><span>Total Members</span><b>{total}</b></div><div class="row"><span>Benevolent Fund</span><b>KES {BF:,}</b></div><div class="row"><span>Reserve</span><b>KES {RESERVE:,}</b></div><div class="row"><span>Version</span><b>{VERSION}</b></div></div>
    <a href="/members" class="btn" style="display:block;text-align:center">View Members →</a><br>
    <a href="/community" class="btn" style="display:block;text-align:center;background:#fff;color:#0f2a44;border:2px solid #0f2a44">Community →</a>
    """)

@app.route("/members")
def members():
    q = request.args.get("q","").lower()
    c = get_db()
    rows = c.execute("SELECT * FROM members ORDER BY name").fetchall()
    c.close()
    cards = ""
    for r in rows:
        if q and q not in r["name"].lower() and q not in r["project"].lower() and q not in (r["staff"] or "").lower():
            continue
        cards += f"""<div class="card"><div class="member-head"><div class="m-logo">FIG</div>
        <div class="member-info"><div class="member-name">{r['name']}</div><div class="member-email">{r['email']}</div></div>
        <span class="project-badge">{r['project']}</span></div>
        <div class="row"><span>Staff Number</span><b>{r['staff']}</b></div>
        <div class="row"><span>Date Joined</span><b>{r['joined']}</b></div>
        <div class="row"><span>Father ID</span><b>{r['father']}</b></div>
        <div class="row"><span>Mother ID</span><b>{r['mother']}</b></div>
        <div class="row"><span>Guardian ID</span><b>{r['guardian']}</b></div></div>"""
    return page("Members", f"""
    <div style="letter-spacing:2px;font-size:12px;color:#b45309;font-weight:700">DIRECTORY</div>
    <div class="page-title">Members</div><div class="sub">{len(rows)} members</div>
    <form method="get"><input name="q" placeholder="Search by name, staff, project" value="{request.args.get('q','')}"></form>
    {cards or '<div class="card">No members found</div>'}
    """)

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method == "POST":
        c = get_db()
        c.execute("INSERT INTO members (name,email,staff,project,joined,father,mother,guardian) VALUES (?,?,?,?,?,?,?,?)",
                  (request.form.get("name"), request.form.get("email"), request.form.get("staff"), request.form.get("project"), request.form.get("joined","01/09/2026"), request.form.get("father","-"), request.form.get("mother","-"), request.form.get("guardian","-")))
        c.commit(); c.close()
        return redirect("/members")
    opts = "".join([f"<option>{p}</option>" for p in PROJECTS])
    return page("Register", f"""
    <div class="page-title">Register Member</div><div class="sub">Add a new member</div>
    <form method="post" class="card"><input name="name" placeholder="Full Name" required><input name="email" placeholder="Email"><input name="staff" placeholder="Staff Number" required>
    <select name="project">{opts}</select><input name="joined" placeholder="Date Joined - 01/09/2026">
    <input name="father" placeholder="Father ID"><input name="mother" placeholder="Mother ID"><input name="guardian" placeholder="Guardian ID">
    <button class="btn">Save Member</button></form>""")

@app.route("/shareout")
def shareout():
    return page("Share-Out", f"""
    <div class="page-title">Share-Out</div><div class="sub">2026 Distribution</div>
    <div class="card"><div class="row"><span>Benevolent Fund</span><b>KES {BF:,}</b></div><div class="row"><span>Reserve</span><b>KES {RESERVE:,}</b></div><div class="row"><span>To Share</span><b>KES {BF-RESERVE:,}</b></div></div>
    <div class="card"><h3>Share Table 2026</h3><br>{'<br>'.join([f'Month {m}: {v} shares' for m,v in SHARE_TABLE_2026.items()])}</div>""")

@app.route("/history")
def history():
    return page("History", """<div class="page-title">History</div><div class="sub">Past payouts & records</div><div class="card">No history yet - payouts will appear here.</div>""")

@app.route("/terms")
def terms():
    return page("Terms", """<div class="page-title">Terms & Policies</div><div class="card"><p>1. Membership is open to all F.I.G Brands staff.<br><br>2. Contributions are monthly and non-refundable except on Share-Out.<br><br>3. Benevolent Fund supports members in times of need.<br><br>4. Share-Out is done annually based on months contributed.</p></div>""")

@app.route("/community", methods=["GET","POST"])
def community():
    c = get_db()
    if request.method == "POST":
        c.execute("INSERT INTO posts (author,text) VALUES (?,?)", (request.form.get("author","Member"), request.form.get("text","")))
        c.commit()
        c.close()
        return redirect("/community")
    posts = c.execute("SELECT * FROM posts ORDER BY id DESC").fetchall()
    c.close()
    items = "".join([f"<div class='card'><b>{p['author']}</b><p style='margin-top:8px'>{p['text']}</p></div>" for p in posts]) or "<div class='card'>No posts yet. Be the first!</div>"
    return page("Community", f"""<div class="page-title">Community</div><div class="sub">Connect with members</div>
    <form method="post" class="card"><input name="author" placeholder="Your name"><textarea name="text" placeholder="Share something..."></textarea><button class="btn">Post</button></form>{items}""")

@app.route("/notifications")
def notifications():
    return page("Notifications", """<div class="page-title">Notifications</div><div class="card">No new notifications.</div>""")

@app.route("/help")
def help_page():
    return page("Help", """<div class="page-title">Help Centre</div><div class="card"><p>Contact: marlonkikuyu@gmail.com<br>Phone: +254 707 780 807<br><br>For help with registration, share-out or login, message admin.</p></div>""")

@app.route("/admin")
def admin():
    return page("Admin", f"""<div class="page-title">Admin / Settings</div><div class="card"><div class="row"><span>Version</span><b>{VERSION}</b></div><div class="row"><span>Admin Email</span><b>{ADMIN_EMAIL}</b></div></div><a href="/login" class="btn" style="display:block;text-align:center">Login as Admin →</a>""")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method == "POST":
        if request.form.get("email") == ADMIN_EMAIL and request.form.get("password") == ADMIN_PASS:
            session["admin"] = True
            return redirect("/admin")
        return page("Login", """<div class="card" style="color:red">Wrong email or password</div><a href="/login">Try again</a>""")
    return page("Login", """<div class="page-title">Login as Admin</div><form method="post" class="card"><input name="email" placeholder="Email"><input name="password" type="password" placeholder="Password"><button class="btn">Login</button></form>""")

@app.route("/download-excel")
def download_excel():
    import csv
    c = get_db()
    rows = c.execute("SELECT name,email,staff,project,joined FROM members").fetchall()
    c.close()
    out = io.StringIO()
    w = csv.writer(out); w.writerow(["Name","Email","Staff","Project","Joined"])
    for r in rows: w.writerow([r["name"], r["email"], r["staff"], r["project"], r["joined"]])
    b = io.BytesIO(out.getvalue().encode())
    return send_file(b, as_attachment=True, download_name="members.csv", mimetype="text/csv")

@app.route("/health")
def health():
    return jsonify({"status":"ok","version":VERSION})

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
