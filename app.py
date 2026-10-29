from flask import Flask, render_template_string, request, redirect, session, Response, jsonify
import sqlite3, os, csv, io, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-final-complete-2024"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, membership TEXT, join_date TEXT, status TEXT, api_key TEXT)''')
    for col in ["phone","membership","join_date","status","api_key"]:
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status,api_key) VALUES (?,?,?,?,?,?,?,?,?)",
        ("Admin", "admin@lonma.com", generate_password_hash("admin123"), "Admin", "0700000000", "Lifetime", datetime.now().strftime("%Y-%m-%d %H:%M"), "Active", "lonma_api_key_12345"))
    conn.commit(); conn.close()
init_db()

@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,X-API-KEY,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if request.method == 'OPTIONS': return '', 200
        key = request.headers.get("X-API-KEY") or request.args.get("api_key") or request.headers.get("Authorization")
        if key and key.startswith("Bearer "): key = key.replace("Bearer ","")
        if not key: return jsonify({"error": "API key required. Use X-API-KEY"}), 401
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE api_key=?", (key,)).fetchone()
        conn.close()
        if not user: return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated

# API DOCS
@app.route("/api")
def api_docs():
    return jsonify({
        "status": "LONMA API LIVE",
        "url": "https://lonma-orbit-24qw.onrender.com",
        "tester": "https://lonma-orbit-24qw.onrender.com/tester",
        "master_api_key": "lonma_api_key_12345",
        "endpoints": {
            "GET /api/health": "Health check",
            "GET /api/members": "Get ALL members",
            "POST /api/register": "Register",
            "POST /api/login": "Login",
            "PUT /api/members/<id>": "Update",
            "DELETE /api/members/<id>": "Delete",
            "GET /api/stats": "Stats"
        }
    })

@app.route("/api/health")
def api_health(): return jsonify({"status":"ok","service":"LONMA","version":"4.0 FINAL"})

@app.route("/api/members", methods=["GET","OPTIONS"])
@require_api_key
def api_get_members():
    conn = get_db()
    users = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status,api_key FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({"total": len(users), "members": [dict(u) for u in users]})

@app.route("/api/members/<int:id>", methods=["GET","OPTIONS"])
@require_api_key
def api_get_member(id):
    conn = get_db()
    u = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status FROM users WHERE id=?", (id,)).fetchone()
    conn.close()
    if not u: return jsonify({"error":"Not found"}), 404
    return jsonify(dict(u))

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == 'OPTIONS': return '', 200
    data = request.get_json(silent=True) or request.form
    if not data or not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error":"name,email,password required"}), 400
    try:
        api_key = f"lonma_{secrets.token_hex(16)}"
        conn = get_db()
        conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status,api_key) VALUES (?,?,?,?,?,?,?,?,?)",
        (data["name"], data["email"], generate_password_hash(data["password"]), data.get("role","Member"), data.get("phone",""), data.get("membership","Standard"), datetime.now().strftime("%Y-%m-%d %H:%M"), "Active", api_key))
        conn.commit()
        user = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status,api_key FROM users WHERE email=?", (data["email"],)).fetchone()
        conn.close()
        return jsonify({"message":"Registered","member":dict(user)}), 201
    except Exception as e:
        return jsonify({"error":str(e)}), 400

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method == 'OPTIONS': return '', 200
    data = request.get_json(silent=True) or request.form
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE email=?", (data.get("email"),)).fetchone()
    conn.close()
    if not u or not check_password_hash(u["password"], data.get("password","")):
        return jsonify({"error":"Invalid credentials"}), 401
    return jsonify({"message":"Login success","member":{"id":u["id"],"name":u["name"],"email":u["email"],"phone":u["phone"],"role":u["role"],"api_key":u["api_key"]}})

@app.route("/api/members/<int:id>", methods=["PUT","OPTIONS"])
@require_api_key
def api_update_member(id):
    if request.method == 'OPTIONS': return '', 200
    data = request.get_json()
    conn = get_db()
    fields=[]; vals=[]
    for k in ["name","email","phone","role","membership","status"]:
        if k in data: fields.append(f"{k}=?"); vals.append(data[k])
    if not fields: return jsonify({"error":"No fields"}), 400
    vals.append(id)
    conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", vals)
    conn.commit()
    u = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status FROM users WHERE id=?", (id,)).fetchone()
    conn.close()
    return jsonify({"message":"Updated","member":dict(u)})

@app.route("/api/members/<int:id>", methods=["DELETE","OPTIONS"])
@require_api_key
def api_delete_member(id):
    if request.method == 'OPTIONS': return '', 200
    conn = get_db(); conn.execute("DELETE FROM users WHERE id=?", (id,)); conn.commit(); conn.close()
    return jsonify({"message":f"Member {id} deleted"})

@app.route("/api/stats", methods=["GET","OPTIONS"])
@require_api_key
def api_stats():
    if request.method == 'OPTIONS': return '', 200
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    admins = conn.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
    conn.close()
    return jsonify({"total_members":total,"admins":admins,"members":total-admins})

# WEB UI
BASE = """<style>body{font-family:Arial;background:#f0f2f5;padding:10px}.card{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px #ccc;max-width:1100px;margin:auto}table{width:100%;border-collapse:collapse;font-size:13px}th,td{border:1px solid #ddd;padding:7px}th{background:#007bff;color:white}.btn{padding:6px 12px;border:none;border-radius:5px;color:white;text-decoration:none;font-size:12px;margin:2px;display:inline-block}.btn-blue{background:#007bff}.btn-red{background:#dc3545}.btn-green{background:#28a745}.nav a{margin-right:12px;text-decoration:none;color:#007bff;font-weight:bold}code{background:#eee;padding:2px 5px;border-radius:3px}</style>
<div class="card"><div class="nav"><a href="/">Home</a><a href="/admin">Admin</a><a href="/api">API Docs</a><a href="/tester">API Tester</a><a href="/export_csv">Export CSV</a><a href="/logout">Logout</a></div><hr>{{CONTENT}}</div>"""

@app.route("/")
def home():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); user=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone(); conn.close()
    return render_template_string(BASE.replace("{{CONTENT}}", f"<h2>Welcome {user['name']}!</h2><p>Email: {user['email']}<br>Role: {user['role']}<br>API Key: <code>{user['api_key']}</code></p><p><a href='/tester' class='btn btn-blue'>🚀 Open API Tester</a> <a href='/api' class='btn btn-green'>API Docs</a> <a href='/admin' class='btn btn-blue'>Admin Dashboard</a></p><p>API URL: <code>https://lonma-orbit-24qw.onrender.com/api/members</code></p>"))

@app.route("/admin")
def admin():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); cur=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    if cur["role"]!="Admin": conn.close(); return render_template_string(BASE.replace("{{CONTENT}}", "<h3 style='color:red'>Admin only. Login admin@lonma.com / admin123</h3>"))
    users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); total=len(users); conn.close()
    rows="".join([f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['phone'] or '-'}</td><td>{u['role']}</td><td>{u['membership']}</td><td><code>{u['api_key'][:18]}...</code></td><td><a class='btn btn-green' href='/make_admin/{u['id']}'>Admin</a><a class='btn btn-red' href='/delete/{u['id']}'>Del</a></td></tr>" for u in users])
    content=f"<h2>Admin - All Data ({total})</h2><p>Master API Key: <code>{cur['api_key']}</code></p><div style='overflow-x:auto'><table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Type</th><th>API Key</th><th>Actions</th></tr>{rows}</table></div><br><a href='/export_csv' class='btn btn-blue'>Download CSV</a> <a href='/tester' class='btn btn-green'>API Tester</a> <a href='/api/members?api_key={cur['api_key']}' class='btn btn-blue' target='_blank'>Test JSON</a>"
    return render_template_string(BASE.replace("{{CONTENT}}", content))

@app.route("/make_admin/<int:id>")
def make_admin(id): conn=get_db(); conn.execute("UPDATE users SET role='Admin' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/delete/<int:id>")
def delete(id): conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/export_csv")
def export_csv():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); users=conn.execute("SELECT id,name,email,phone,role,membership,join_date,status,api_key FROM users").fetchall(); conn.close()
    out=io.StringIO(); w=csv.writer(out); w.writerow(["ID","Name","Email","Phone","Role","Membership","JoinDate","Status","APIKey"])
    for u in users: w.writerow([u["id"],u["name"],u["email"],u["phone"],u["role"],u["membership"],u["join_date"],u["status"],u["api_key"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=lonma_all_data.csv"})
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(request.form["email"],)).fetchone(); conn.close()
        if u and check_password_hash(u["password"], request.form["password"]): session["user_id"]=u["id"]; return redirect("/")
    return render_template_string(BASE.replace("{{CONTENT}}", "<h3>Login</h3><form method='post'><input name='email' placeholder='Email' required style='width:90%;padding:8px;margin:5px'><br><input name='password' type='password' placeholder='Password' required style='width:90%;padding:8px;margin:5px'><br><button class='btn btn-blue'>Login</button></form><p>Admin: admin@lonma.com / admin123</p><p>No account? <a href='/register'>Register</a></p>"))
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            conn=get_db(); api_key=f"lonma_{secrets.token_hex(16)}"; conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status,api_key) VALUES (?,?,?,?,?,?,?,?,?)",(request.form["name"],request.form["email"],generate_password_hash(request.form["password"]),"Member",request.form["phone"],request.form["membership"],datetime.now().strftime("%Y-%m-%d %H:%M"),"Active",api_key)); conn.commit(); conn.close(); return redirect("/login")
        except Exception as e: return f"Error {e} <a href='/register'>Try again</a>"
    return render_template_string(BASE.replace("{{CONTENT}}", "<h3>Register</h3><form method='post'><input name='name' placeholder='Full Name' required style='width:90%;padding:8px'><br><input name='email' placeholder='Email' required style='width:90%;padding:8px'><br><input name='phone' placeholder='Phone' required style='width:90%;padding:8px'><br><select name='membership' style='width:90%;padding:8px'><option>Standard</option><option>Premium</option><option>Lifetime</option></select><br><input name='password' type='password' placeholder='Password' required style='width:90%;padding:8px'><br><button class='btn btn-blue'>Register</button></form>"))
@app.route("/logout")
def logout(): session.clear(); return redirect("/login")

# API TESTER PAGE FOR OTHER TEAMS
@app.route("/tester")
def api_tester():
    html = """<!DOCTYPE html>
<html>
<head>
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>LONMA API Tester</title>
<style>
body{font-family:Arial;background:#0f172a;color:white;padding:15px}
.card{background:#1e293b;padding:20px;border-radius:15px;max-width:850px;margin:15px auto;box-shadow:0 4px 15px #000}
h2{color:#38bdf8} h3{color:#7dd3fc;margin-top:25px}
input,select{width:95%;padding:10px;margin:6px 0;border-radius:8px;border:none;background:#334155;color:white}
button{background:#38bdf8;color:#000;padding:10px 18px;border:none;border-radius:8px;font-weight:bold;cursor:pointer;margin:5px}
button:hover{background:#0ea5e9}
pre{background:#020617;padding:12px;border-radius:8px;overflow:auto;max-height:320px;color:#22c55e;font-size:12px;border:1px solid #334155}
.keybox{background:#020617;padding:12px;border-radius:8px;border:1px solid #38bdf8;margin:10px 0}
a{color:#38bdf8}
</style>
</head>
<body>
<div class="card">
<h2>🚀 LONMA API Tester - For Other Teams</h2>
<div class="keybox">
<b>Live URL:</b> https://lonma-orbit-24qw.onrender.com<br>
<b>Master API Key:</b> <code id="key">lonma_api_key_12345</code>
<button onclick="copyKey()">Copy Key</button><br>
<b>Quick Links:</b> <a href="/api" target="_blank">API Docs</a> | <a href="/admin" target="_blank">Admin</a> | <a href="/api/members?api_key=lonma_api_key_12345" target="_blank">View JSON</a>
</div>

<h3>1️⃣ GET ALL MEMBERS (Complete Data)</h3>
<button onclick="getAll()">▶️ GET /api/members</button>
<pre id="out1">Click to fetch all data...</pre>

<h3>2️⃣ REGISTER New Member</h3>
<input id="r_name" placeholder="Full Name - e.g John Doe">
<input id="r_email" placeholder="Email - e.g john@lonma.com">
<input id="r_phone" placeholder="Phone - e.g 0712345678">
<input id="r_pass" placeholder="Password" type="password">
<select id="r_mem"><option>Standard</option><option>Premium</option><option>Lifetime</option></select>
<button onclick="register()">▶️ POST /api/register</button>
<pre id="out2"></pre>

<h3>3️⃣ LOGIN</h3>
<input id="l_email" placeholder="Email" value="admin@lonma.com">
<input id="l_pass" placeholder="Password" value="admin123" type="password">
<button onclick="login()">▶️ POST /api/login</button>
<pre id="out3"></pre>

<h3>4️⃣ STATS</h3>
<button onclick="stats()">▶️ GET /api/stats</button>
<pre id="out4"></pre>

<h3>5️⃣ DELETE Member</h3>
<input id="del_id" placeholder="Member ID to delete - e.g 2" type="number">
<button onclick="delMember()" style="background:#ef4444;color:white">▶️ DELETE /api/members/ID</button>
<pre id="out5"></pre>
</div>

<script>
const BASE = "https://lonma-orbit-24qw.onrender.com";
const API_KEY = "lonma_api_key_12345";
function copyKey(){navigator.clipboard.writeText(API_KEY); alert("API Key Copied: "+API_KEY);}
async function getAll(){
 document.getElementById('out1').innerText = "Loading...";
 const res = await fetch(BASE+"/api/members", {headers:{"X-API-KEY":API_KEY}});
 const data = await res.json();
 document.getElementById('out1').innerText = JSON.stringify(data, null, 2);
}
async function register(){
 const body = {name: document.getElementById('r_name').value,email: document.getElementById('r_email').value,phone: document.getElementById('r_phone').value,password: document.getElementById('r_pass').value,membership: document.getElementById('r_mem').value};
 if(!body.name || !body.email || !body.password) return alert("Fill name, email, password");
 document.getElementById('out2').innerText = "Registering...";
 const res = await fetch(BASE+"/api/register", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
 const data = await res.json();
 document.getElementById('out2').innerText = JSON.stringify(data, null, 2);
 if(res.ok) getAll();
}
async function login(){
 const body = {email: document.getElementById('l_email').value, password: document.getElementById('l_pass').value};
 document.getElementById('out3').innerText = "Logging in...";
 const res = await fetch(BASE+"/api/login", {method:"POST", headers:{"Content-Type":"application/json"}, body: JSON.stringify(body)});
 const data = await res.json();
 document.getElementById('out3').innerText = JSON.stringify(data, null, 2);
}
async function stats(){
 document.getElementById('out4').innerText = "Loading...";
 const res = await fetch(BASE+"/api/stats", {headers:{"X-API-KEY":API_KEY}});
 const data = await res.json();
 document.getElementById('out4').innerText = JSON.stringify(data, null, 2);
}
async function delMember(){
 const id = document.getElementById('del_id').value;
 if(!id) return alert("Enter ID");
 if(!confirm("Delete member "+id+"?")) return;
 document.getElementById('out5').innerText = "Deleting...";
 const res = await fetch(BASE+"/api/members/"+id, {method:"DELETE", headers:{"X-API-KEY":API_KEY}});
 const data = await res.json();
 document.getElementById('out5').innerText = JSON.stringify(data, null, 2);
 if(res.ok) getAll();
}
</script>
</body>
</html>"""
    return html

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
