from flask import Flask, render_template_string, request, redirect, url_for, session, Response
import sqlite3, os, csv, io
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.secret_key = "lonma-secret-key-2024"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users 
    (id INTEGER PRIMARY KEY, name TEXT, email TEXT UNIQUE, password TEXT, role TEXT)''')
    # Create default admin if not exists
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",
        ("Admin", "admin@lonma.com", generate_password_hash("admin123"), "Admin"))
        conn.commit()
    conn.close()

init_db()

# HTML Templates
BASE_HTML = """
<style>
body{font-family:Arial;padding:20px;background:#f5f5f5}
.card{background:white;padding:20px;border-radius:10px;box-shadow:0 2px 5px #ccc;max-width:900px;margin:auto}
table{width:100%;border-collapse:collapse;margin-top:15px}
th,td{border:1px solid #ddd;padding:8px;text-align:left}
th{background:#007bff;color:white}
.btn{padding:6px 12px;border:none;border-radius:5px;color:white;text-decoration:none;display:inline-block;margin:2px}
.btn-blue{background:#007bff} .btn-red{background:#dc3545} .btn-green{background:#28a745}
input{padding:8px;margin:5px;width:90%}
</style>
<div class="card">
<h2>LONMA Membership System</h2>
<a href="/">Home</a> | <a href="/admin">Admin Dashboard</a> | <a href="/export">Export CSV</a> | <a href="/logout">Logout</a>
<hr>
{{content}}
</div>
"""

@app.route("/")
def home():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_db()
    user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    conn.close()
    content = f"""
    <h3>Welcome, {user['name']}!</h3>
    <p>Email: {user['email']}<br>Role: <span style="background:green;color:white;padding:2px 8px;border-radius:5px">{user['role']}</span></p>
    <p><b>Your Role: {user['role']}</b> - {'You can see ALL members in Admin Dashboard' if user['role']=='Admin' else 'Ask Admin to make you Admin to see all data'}</p>
    """
    return render_template_string(BASE_HTML.replace("{{content}}", content))

@app.route("/admin")
def admin():
    if "user_id" not in session:
        return redirect("/login")
    conn = get_db()
    cur_user = conn.execute("SELECT * FROM users WHERE id=?", (session["user_id"],)).fetchone()
    if cur_user["role"] != "Admin":
        conn.close()
        return render_template_string(BASE_HTML.replace("{{content}}", "<h3 style='color:red'>Access Denied! Only Admin can view all data.<br><br>Login as admin@lonma.com / admin123 to see all data</h3>"))
    
    search = request.args.get("q", "")
    if search:
        users = conn.execute("SELECT * FROM users WHERE name LIKE ? OR email LIKE ?", (f"%{search}%", f"%{search}%")).fetchall()
    else:
        users = conn.execute("SELECT * FROM users").fetchall()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    conn.close()
    
    rows = ""
    for u in users:
        rows += f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['role']}</td><td><a class='btn btn-green' href='/make_admin/{u['id']}'>Make Admin</a> <a class='btn btn-red' href='/delete/{u['id']}'>Delete</a></td></tr>"
    
    content = f"""
    <h3>Admin Dashboard - All Members ({total} Total)</h3>
    <form method="get"><input name="q" placeholder="Search name or email..." value="{search}"> <button>Search</button></form>
    <table><tr><th>ID</th><th>Name</th><th>Email</th><th>Role</th><th>Actions</th></tr>{rows}</table>
    <p><a class='btn btn-blue' href='/export'>Download All as CSV</a></p>
    """
    return render_template_string(BASE_HTML.replace("{{content}}", content))

@app.route("/make_admin/<int:id>")
def make_admin(id):
    if "user_id" not in session: return redirect("/login")
    conn = get_db()
    conn.execute("UPDATE users SET role='Admin' WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect("/admin")

@app.route("/delete/<int:id>")
def delete(id):
    if "user_id" not in session: return redirect("/login")
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit(); conn.close()
    return redirect("/admin")

@app.route("/export")
def export():
    if "user_id" not in session: return redirect("/login")
    conn = get_db()
    users = conn.execute("SELECT * FROM users").fetchall()
    conn.close()
    output = io.StringIO()
    writer = csv.writer(output)
    writer.writerow(["ID","Name","Email","Role"])
    for u in users: writer.writerow([u["id"], u["name"], u["email"], u["role"]])
    return Response(output.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=lonma_members.csv"})

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        email=request.form["email"]; pwd=request.form["password"]
        conn=get_db(); user=conn.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone(); conn.close()
        if user and check_password_hash(user["password"], pwd):
            session["user_id"]=user["id"]; return redirect("/")
        else:
            return render_template_string(BASE_HTML.replace("{{content}}", "<p style='color:red'>Wrong email or password</p>"+login_form()))
    return render_template_string(BASE_HTML.replace("{{content}}", login_form()))

def login_form():
    return """<h3>Login</h3><form method="post"><input name="email" placeholder="Email" required><br><input name="password" type="password" placeholder="Password" required><br><button class="btn btn-blue">Login</button></form><p>No account? <a href="/register">Register</a></p><p><b>Admin Login:</b> admin@lonma.com / admin123</p>"""

@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        name=request.form["name"]; email=request.form["email"]; pwd=generate_password_hash(request.form["password"])
        try:
            conn=get_db(); conn.execute("INSERT INTO users (name,email,password,role) VALUES (?,?,?,?)",(name,email,pwd,"Member")); conn.commit(); conn.close()
            return redirect("/login")
        except: return "Email already exists <a href='/register'>Try again</a>"
    return render_template_string(BASE_HTML.replace("{{content}}", """<h3>Register</h3><form method="post"><input name="name" placeholder="Full Name" required><br><input name="email" placeholder="Email" required><br><input name="password" type="password" placeholder="Password" required><br><button class="btn btn-blue">Register</button></form>"""))

@app.route("/logout")
def logout():
    session.clear(); return redirect("/login")

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 10000)))
