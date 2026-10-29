from flask import Flask, render_template_string, request, redirect, session, Response
import sqlite3, os, csv, io
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime

app = Flask(__name__)
app.secret_key = "lonma-pro-2024"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, membership TEXT, join_date TEXT, status TEXT)''')
    # Add columns if old DB
    try: conn.execute("ALTER TABLE users ADD COLUMN phone TEXT")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN membership TEXT")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN join_date TEXT")
    except: pass
    try: conn.execute("ALTER TABLE users ADD COLUMN status TEXT")
    except: pass
    
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status) VALUES (?,?,?,?,?,?,?,?)",
        ("Admin", "admin@lonma.com", generate_password_hash("admin123"), "Admin", "0700000000", "Lifetime", datetime.now().strftime("%Y-%m-%d %H:%M"), "Active"))
    conn.commit(); conn.close()

init_db()

BASE = """
<style>
body{font-family:Arial;background:#f0f2f5;margin:0;padding:10px}
.card{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px #ccc;max-width:1000px;margin:auto;margin-bottom:15px}
.stats{display:flex;gap:10px;flex-wrap:wrap}
.stat{flex:1;min-width:120px;background:linear-gradient(135deg,#007bff,#0056b3);color:white;padding:15px;border-radius:10px;text-align:center}
.stat.green{background:linear-gradient(135deg,#28a745,#1e7e34)} .stat.orange{background:linear-gradient(135deg,#ff9800,#e65100)} .stat.purple{background:linear-gradient(135deg,#9c27b0,#6a1b9a)}
table{width:100%;border-collapse:collapse;font-size:14px}
th,td{border:1px solid #ddd;padding:8px;text-align:left} th{background:#007bff;color:white;position:sticky;top:0}
.btn{padding:5px 10px;border:none;border-radius:5px;color:white;text-decoration:none;font-size:12px;margin:1px;display:inline-block}
.btn-blue{background:#007bff} .btn-red{background:#dc3545} .btn-green{background:#28a745} .btn-orange{background:#ff9800}
input,select{padding:8px;margin:4px;border:1px solid #ccc;border-radius:5px;width:95%}
.nav{margin-bottom:10px} .nav a{margin-right:10px;text-decoration:none;color:#007bff;font-weight:bold}
</style>
<div class="card">
<div class="nav"><a href="/">🏠 Home</a> <a href="/admin">📊 Admin Dashboard</a> <a href="/export">📥 Export CSV</a> <a href="/logout">🚪 Logout</a></div>
<hr>
{{CONTENT}}
</div>
"""

@app.route("/")
def home():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); user=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone(); conn.close()
    content=f"""
    <h2>Welcome, {user['name']}! 👋</h2>
    <p><b>Email:</b> {user['email']}<br><b>Phone:</b> {user['phone'] or 'N/A'}<br><b>Role:</b> <span style="background:{'#28a745' if user['role']=='Admin' else '#007bff'};color:white;padding:3px 8px;border-radius:10px">{user['role']}</span><br>
    <b>Membership:</b> {user['membership'] or 'Standard'}<br><b>Joined:</b> {user['join_date']}<br><b>Status:</b> {user['status']}</p>
    {"<div style='background:#d4edda;padding:10px;border-radius:5px'>✅ You are Admin! <a href='/admin'>Go to Admin Dashboard to see all data</a></div>" if user['role']=='Admin' else "<div style='background:#fff3cd;padding:10px;border-radius:5px'>ℹ️ Member view. Login as admin@lonma.com / admin123 or ask Admin to make you Admin.</div>"}
    """
    return render_template_string(BASE.replace("{{CONTENT}}", content))

@app.route("/admin")
def admin():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); cur=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    if cur["role"]!="Admin":
        conn.close(); return render_template_string(BASE.replace("{{CONTENT}}", "<h3 style='color:red'>⛔ Access Denied! Admin only.<br>Login as admin@lonma.com / admin123</h3>"))
    
    q=request.args.get("q",""); f=request.args.get("filter","")
    query="SELECT * FROM users"; params=[]
    if q and f: query+=" WHERE (name LIKE ? OR email LIKE ?) AND role=?"; params=[f"%{q}%",f"%{q}%",f]
    elif q: query+=" WHERE name LIKE ? OR email LIKE ?"; params=[f"%{q}%",f"%{q}%"]
    elif f: query+=" WHERE role=?"; params=[f]
    query+=" ORDER BY id DESC"
    users=conn.execute(query, params).fetchall()
    total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    admins=conn.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
    members=conn.execute("SELECT COUNT(*) FROM users WHERE role='Member'").fetchone()[0]
    conn.close()
    
    rows=""
    for u in users:
        rows+=f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['phone'] or '-'}</td><td>{u['role']}</td><td>{u['membership'] or 'Std'}</td><td>{u['join_date'][:10] if u['join_date'] else '-'}</td><td><span style='background:{'#28a745' if u['status']=='Active' else '#dc3545'};color:white;padding:2px 6px;border-radius:8px'>{u['status'] or 'Active'}</span></td><td><a class='btn btn-green' href='/make_admin/{u['id']}'>Admin</a><a class='btn btn-orange' href='/edit/{u['id']}'>Edit</a><a class='btn btn-red' href='/delete/{u['id']}' onclick='return confirm(\"Delete?\")'>Del</a></td></tr>"
    
    content=f"""
    <h2>📊 Admin Dashboard</h2>
    <div class="stats">
      <div class="stat"><h2>{total}</h2><div>Total Members</div></div>
      <div class="stat green"><h2>{members}</h2><div>Members</div></div>
      <div class="stat orange"><h2>{admins}</h2><div>Admins</div></div>
      <div class="stat purple"><h2>{total}</h2><div>Active</div></div>
    </div>
    <br>
    <form method="get" style="display:flex;gap:5px;flex-wrap:wrap"><input name="q" placeholder="🔍 Search name/email" value="{q}" style="flex:2"><select name="filter"><option value="">All Roles</option><option value="Admin" {"selected" if f=="Admin" else ""}>Admin</option><option value="Member" {"selected" if f=="Member" else ""}>Member</option></select><button class="btn btn-blue">Search</button><a class="btn btn-blue" href="/admin">Reset</a></form>
    <div style="overflow-x:auto"><table><tr><th>ID</th><th>Name</th><th>Email</th><th>Phone</th><th>Role</th><th>Type</th><th>Joined</th><th>Status</th><th>Actions</th></tr>{rows}</table></div>
    <br><a class="btn btn-blue" href="/export">📥 Download CSV</a> <a class="btn btn-green" href="/export?format=json">📄 Export JSON</a>
    <br><br><canvas id="chart" height="80"></canvas>
    <script src="https://cdn.jsdelivr.net/npm/chart.js"></script>
    <script>new Chart(document.getElementById('chart'),{{type:'doughnut',data:{{labels:['Admins','Members'],datasets:[{{data:[{admins},{members}],backgroundColor:['#ff9800','#007bff']}}]}},options:{{plugins:{{title:{{display:true,text:'Members by Role'}}}}}}}})</script>
    """
    return render_template_string(BASE.replace("{{CONTENT}}", content))

@app.route("/make_admin/<int:id>")
def make_admin(id): 
    conn=get_db(); conn.execute("UPDATE users SET role='Admin' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/delete/<int:id>")
def delete(id): conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")

@app.route("/edit/<int:id>", methods=["GET","POST"])
def edit(id):
    conn=get_db()
    if request.method=="POST":
        conn.execute("UPDATE users SET name=?,email=?,phone=?,membership=?,status=?,role=? WHERE id=?",(request.form["name"],request.form["email"],request.form["phone"],request.form["membership"],request.form["status"],request.form["role"],id)); conn.commit(); conn.close(); return redirect("/admin")
    u=conn.execute("SELECT * FROM users WHERE id=?",(id,)).fetchone(); conn.close()
    form=f"""<h3>Edit Member #{id}</h3><form method="post">
    Name: <input name="name" value="{u['name']}" required><br>Email: <input name="email" value="{u['email']}" required><br>Phone: <input name="phone" value="{u['phone'] or ''}"><br>
    Membership: <select name="membership"><option {"selected" if u['membership']=="Standard" else ""}>Standard</option><option {"selected" if u['membership']=="Premium" else ""}>Premium</option><option {"selected" if u['membership']=="Lifetime" else ""}>Lifetime</option></select><br>
    Role: <select name="role"><option {"selected" if u['role']=="Member" else ""}>Member</option><option {"selected" if u['role']=="Admin" else ""}>Admin</option></select><br>
    Status: <select name="status"><option {"selected" if u['status']=="Active" else ""}>Active</option><option {"selected" if u['status']=="Inactive" else ""}>Inactive</option></select><br>
    <button class="btn btn-blue">Save</button> <a href="/admin">Cancel</a></form>"""
    return render_template_string(BASE.replace("{{CONTENT}}", form))

@app.route("/export")
def export():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); users=conn.execute("SELECT * FROM users").fetchall(); conn.close()
    if request.args.get("format")=="json":
        import json; data=[dict(u) for u in users]; return Response(json.dumps(data, indent=2), mimetype="application/json", headers={"Content-Disposition":"attachment;filename=lonma.json"})
    out=io.StringIO(); w=csv.writer(out); w.writerow(["ID","Name","Email","Phone","Role","Membership","Join Date","Status"])
    for u in users: w.writerow([u["id"],u["name"],u["email"],u["phone"],u["role"],u["membership"],u["join_date"],u["status"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=lonma_members.csv"})

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(request.form["email"],)).fetchone(); conn.close()
        if u and check_password_hash(u["password"], request.form["password"]): session["user_id"]=u["id"]; return redirect("/")
        err="<p style='color:red'>Wrong credentials</p>"
    else: err=""
    form=err+"""<h3>Login</h3><form method="post"><input name="email" placeholder="Email" required><br><input name="password" type="password" placeholder="Password" required><br><button class="btn btn-blue">Login</button></form><p>No account? <a href="/register">Register</a></p><p><b>Admin:</b> admin@lonma.com / admin123</p>"""
    return render_template_string(BASE.replace("{{CONTENT}}", form))

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            conn=get_db(); conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status) VALUES (?,?,?,?,?,?,?,?)",(request.form["name"],request.form["email"],generate_password_hash(request.form["password"]),"Member",request.form["phone"],request.form["membership"],datetime.now().strftime("%Y-%m-%d %H:%M"),"Active")); conn.commit(); conn.close(); return redirect("/login")
        except: return render_template_string(BASE.replace("{{CONTENT}}", "Email exists! <a href='/register'>Try again</a>"))
    form="""<h3>Register - Join LONMA</h3><form method="post">
    <input name="name" placeholder="Full Name" required><br><input name="email" placeholder="Email" required><br><input name="phone" placeholder="Phone e.g. 0712345678" required><br>
    <select name="membership" required><option value="Standard">Standard - Free</option><option value="Premium">Premium - KES 1000/yr</option><option value="Lifetime">Lifetime - KES 5000</option></select><br>
    <input name="password" type="password" placeholder="Password" required><br><button class="btn btn-blue">Register</button></form>"""
    return render_template_string(BASE.replace("{{CONTENT}}", form))

@app.route("/logout")
def logout(): session.clear(); return redirect("/login")

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
