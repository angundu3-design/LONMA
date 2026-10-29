from flask import Flask, render_template_string, request, redirect, session, Response, jsonify
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-simple-final"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT)''')
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (name,email,password,role,phone,api_key) VALUES (?,?,?,?,?,?)",
        ("Admin", "admin@lonma.com", generate_password_hash("admin123"), "Admin", "0700000000", "lonma_api_key_12345"))
    conn.commit(); conn.close()
init_db()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,PUT,DELETE,OPTIONS')
    return r

def need_key(f):
    @wraps(f)
    def d(*a,**k):
        if request.method=='OPTIONS': return '',200
        key=request.headers.get("X-API-KEY") or request.args.get("api_key")
        if not key: return jsonify({"error":"Need X-API-KEY"}),401
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE api_key=?",(key,)).fetchone(); conn.close()
        if not u: return jsonify({"error":"Invalid key"}),401
        return f(*a,**k)
    return d

# SIMPLE STYLES
STYLE = """<style>body{font-family:Arial;background:#f4f4f4;margin:0;padding:0}.nav{background:#007bff;padding:12px}.nav a{color:white;margin:0 10px;text-decoration:none;font-weight:bold}.card{background:white;max-width:900px;margin:20px auto;padding:20px;border-radius:10px;box-shadow:0 2px 10px #ccc}table{width:100%;border-collapse:collapse}th,td{border:1px solid #ddd;padding:8px;text-align:left}th{background:#007bff;color:white}.btn{padding:7px 12px;border:none;border-radius:5px;color:white;text-decoration:none;display:inline-block;margin:2px;cursor:pointer}.blue{background:#007bff}.red{background:#dc3545}.green{background:#28a745}input{width:90%;padding:10px;margin:5px 0;border:1px solid #ccc;border-radius:5px}</style>"""

# API
@app.route("/api")
def api_docs(): return jsonify({"live":"https://lonma-orbit-24qw.onrender.com","api_key":"lonma_api_key_12345","GET /api/members":"Get all","POST /api/register":"Register","POST /api/login":"Login","DELETE /api/members/1":"Delete","tester":"/tester"})

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    conn=get_db(); users=conn.execute("SELECT id,name,email,phone,role FROM users").fetchall(); conn.close()
    return jsonify({"total":len(users),"members":[dict(u) for u in users]})

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json() or request.form
    if not d.get("email") or not d.get("password") or not d.get("name"): return jsonify({"error":"name,email,password needed"}),400
    try:
        key=f"lonma_{secrets.token_hex(8)}"
        conn=get_db()
        conn.execute("INSERT INTO users (name,email,password,role,phone,api_key) VALUES (?,?,?,?,?,?)",(d["name"],d["email"],generate_password_hash(d["password"]),d.get("role","Member"),d.get("phone",""),key))
        conn.commit(); u=conn.execute("SELECT id,name,email,phone,role,api_key FROM users WHERE email=?",(d["email"],)).fetchone(); conn.close()
        return jsonify({"message":"Registered","member":dict(u)}),201
    except Exception as e: return jsonify({"error":str(e)}),400

@app.route("/api/login", methods=["POST","OPTIONS"])
def api_login():
    if request.method=='OPTIONS': return '',200
    d=request.get_json() or request.form
    conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(d.get("email"),)).fetchone(); conn.close()
    if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Wrong email/password"}),401
    return jsonify({"member":{"id":u["id"],"name":u["name"],"email":u["email"],"role":u["role"],"api_key":u["api_key"]}})

@app.route("/api/members/<int:id>", methods=["DELETE","OPTIONS"])
@need_key
def api_delete(id):
    if request.method=='OPTIONS': return '',200
    conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close()
    return jsonify({"deleted":id})

# WEB
@app.route("/")
def home():
    if "uid" not in session: return redirect("/login")
    conn=get_db(); u=conn.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone(); conn.close()
    return render_template_string(STYLE+f"<div class='nav'><a href='/'>Home</a><a href='/members'>Members</a><a href='/admin'>Admin</a><a href='/tester'>API Tester</a><a href='/logout'>Logout</a></div><div class='card'><h2>Welcome {u['name']}!</h2><p><b>Email:</b> {u['email']}<br><b>Role:</b> {u['role']}<br><b>Phone:</b> {u['phone']}</p><p>You are logged in as <b>{u['role']}</b></p></div>")

@app.route("/members")
def members():
    if "uid" not in session: return redirect("/login")
    conn=get_db(); users=conn.execute("SELECT id,name,email,phone,role FROM users ORDER BY id DESC").fetchall(); conn.close()
    rows="".join([f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['phone']}</td><td>{u['role']}</td></tr>" for u in users])
    return render_template_string(STYLE+f"<div class='nav'><a href='/'>Home</a><a href='/members'>Members</a><a href='/admin'>Admin</a><a href='/tester'>API Tester</a><a href='/logout'>Logout</a></div><div class='card'><h2>All Members ({len(users)})</h2><table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Role</th></tr>{rows}</table></div>")

@app.route("/admin")
def admin():
    if "uid" not in session: return redirect("/login")
    conn=get_db(); me=conn.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
    if me["role"]!="Admin": conn.close(); return render_template_string(STYLE+"<div class='nav'><a href='/'>Home</a></div><div class='card'><h3 style='color:red'>Admin only! Use admin@lonma.com / admin123</h3></div>")
    users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); conn.close()
    rows="".join([f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['phone']}</td><td>{u['role']}</td><td><a class='btn green' href='/make_admin/{u['id']}'>Make Admin</a> <a class='btn blue' href='/make_member/{u['id']}'>Make Member</a> <a class='btn red' href='/delete/{u['id']}'>Delete</a></td></tr>" for u in users])
    return render_template_string(STYLE+f"<div class='nav'><a href='/'>Home</a><a href='/members'>Members</a><a href='/admin'>Admin</a><a href='/tester'>API Tester</a><a href='/logout'>Logout</a></div><div class='card'><h2>Admin Panel - Simple</h2><p>Master Key: <code>lonma_api_key_12345</code></p><table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Actions</th></tr>{rows}</table></div>")

@app.route("/make_admin/<int:id>")
def make_admin(id): conn=get_db(); conn.execute("UPDATE users SET role='Admin' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/make_member/<int:id>")
def make_member(id): conn=get_db(); conn.execute("UPDATE users SET role='Member' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/delete/<int:id>")
def delete(id): conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(request.form["email"],)).fetchone(); conn.close()
        if u and check_password_hash(u["password"],request.form["password"]): session["uid"]=u["id"]; return redirect("/")
        return render_template_string(STYLE+"<div class='card'><h3 style='color:red'>Wrong password</h3><a href='/login'>Try again</a></div>")
    return render_template_string(STYLE+"<div class='card'><h2>Login</h2><form method='post'><input name='email' placeholder='Email' required><br><input name='password' type='password' placeholder='Password' required><br><button class='btn blue'>Login</button></form><p>Admin: admin@lonma.com / admin123<br>Don't have account? <a href='/register'>Register</a></p></div>")

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            conn=get_db(); key=f"lonma_{secrets.token_hex(8)}"; conn.execute("INSERT INTO users (name,email,password,role,phone,api_key) VALUES (?,?,?,?,?,?)",(request.form["name"],request.form["email"],generate_password_hash(request.form["password"]),"Member",request.form["phone"],key)); conn.commit(); conn.close(); return redirect("/login")
        except Exception as e: return f"Error {e} <a href='/register'>Back</a>"
    return render_template_string(STYLE+"<div class='card'><h2>Register as Member</h2><form method='post'><input name='name' placeholder='Full Name' required><br><input name='email' placeholder='Email' required><br><input name='phone' placeholder='Phone' required><br><input name='password' type='password' placeholder='Password' required><br><button class='btn blue'>Register</button></form><p>Already have account? <a href='/login'>Login</a></p></div>")

@app.route("/logout")
def logout(): session.clear(); return redirect("/login")

@app.route("/tester")
def tester():
    return """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>LONMA Simple Tester</title><style>body{font-family:Arial;background:#0f172a;color:white;padding:15px}.card{background:#1e293b;padding:20px;border-radius:12px;max-width:700px;margin:auto}input{width:95%;padding:10px;margin:5px;border-radius:8px;border:none}button{padding:10px 15px;border:none;border-radius:8px;background:#38bdf8;font-weight:bold;cursor:pointer;margin:3px}pre{background:#020617;padding:10px;border-radius:8px;color:#22c55e;overflow:auto}</style></head><body>
<div class="card"><h2>🚀 LONMA Simple - Members & Admin</h2><p>Key: <code>lonma_api_key_12345</code> | <a href="/api" style="color:#38bdf8">API Docs</a> | <a href="/admin" style="color:#38bdf8">Admin</a></p>
<h3>GET ALL MEMBERS</h3><button onclick="getAll()">GET /api/members</button><pre id="o1">Click...</pre>
<h3>REGISTER</h3><input id="n" placeholder="Name"><input id="e" placeholder="Email"><input id="p" placeholder="Phone"><input id="pw" placeholder="Password" type="password"><button onclick="reg()">REGISTER</button><pre id="o2"></pre>
<h3>DELETE</h3><input id="did" type="number" placeholder="ID to delete"><button onclick="del()" style="background:#ef4444;color:white">DELETE</button><pre id="o3"></pre>
</div><script>
const BASE="https://lonma-orbit-24qw.onrender.com"; const KEY="lonma_api_key_12345";
async function getAll(){document.getElementById('o1').innerText="Loading..."; let r=await fetch(BASE+"/api/members",{headers:{"X-API-KEY":KEY}}); document.getElementById('o1').innerText=JSON.stringify(await r.json(),null,2);}
async function reg(){let body={name:document.getElementById('n').value,email:document.getElementById('e').value,phone:document.getElementById('p').value,password:document.getElementById('pw').value}; let r=await fetch(BASE+"/api/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(body)}); document.getElementById('o2').innerText=JSON.stringify(await r.json(),null,2); if(r.ok) getAll();}
async function del(){let id=document.getElementById('did').value; if(!id) return alert("Enter ID"); let r=await fetch(BASE+"/api/members/"+id,{method:"DELETE",headers:{"X-API-KEY":KEY}}); document.getElementById('o3').innerText=JSON.stringify(await r.json(),null,2); if(r.ok) getAll();}
</script></body></html>"""

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
