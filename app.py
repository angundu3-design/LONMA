from flask import Flask, render_template_string, request, redirect, session, Response, jsonify
from flask_cors import CORS
import sqlite3, os, csv, io
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-api-secret-2024"
CORS(app)  # Allow other teams to call API
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

# --- API AUTH DECORATOR ---
def require_api_key(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        key = request.headers.get("X-API-KEY") or request.args.get("api_key")
        if not key:
            return jsonify({"error": "API key required. Use header X-API-KEY"}), 401
        conn = get_db()
        user = conn.execute("SELECT * FROM users WHERE api_key=?", (key,)).fetchone()
        conn.close()
        if not user:
            return jsonify({"error": "Invalid API key"}), 401
        return f(*args, **kwargs)
    return decorated

# ==================== REST API ENDPOINTS FOR OTHER TEAMS ====================

@app.route("/api")
def api_docs():
    return jsonify({
        "message": "LONMA API is Live!",
        "base_url": "https://lonma-orbit-24qw.onrender.com",
        "api_key": "Use admin api_key: lonma_api_key_12345 (get yours from /admin)",
        "endpoints": {
            "GET /api/members": "Get all members (requires X-API-KEY)",
            "GET /api/members/<id>": "Get single member",
            "POST /api/register": "Register new member {name,email,password,phone,membership}",
            "POST /api/login": "Login {email,password} returns user + api_key",
            "PUT /api/members/<id>": "Update member",
            "DELETE /api/members/<id>": "Delete member",
            "GET /api/stats": "Get dashboard stats",
            "GET /api/health": "Check API health"
        }
    })

@app.route("/api/health")
def api_health():
    return jsonify({"status": "ok", "service": "LONMA API", "version": "2.0", "live_url": "https://lonma-orbit-24qw.onrender.com"})

@app.route("/api/members", methods=["GET"])
@require_api_key
def api_get_members():
    conn = get_db()
    users = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status FROM users ORDER BY id DESC").fetchall()
    conn.close()
    return jsonify({"total": len(users), "members": [dict(u) for u in users]})

@app.route("/api/members/<int:id>", methods=["GET"])
@require_api_key
def api_get_member(id):
    conn = get_db()
    u = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status FROM users WHERE id=?", (id,)).fetchone()
    conn.close()
    if not u: return jsonify({"error": "Member not found"}), 404
    return jsonify(dict(u))

@app.route("/api/register", methods=["POST"])
def api_register():
    data = request.get_json() or request.form
    if not data.get("email") or not data.get("password") or not data.get("name"):
        return jsonify({"error": "name, email, password required"}), 400
    try:
        import secrets
        api_key = f"lonma_{secrets.token_hex(16)}"
        conn = get_db()
        conn.execute("INSERT INTO users (name,email,password,role,phone,membership,join_date,status,api_key) VALUES (?,?,?,?,?,?,?,?,?)",
        (data["name"], data["email"], generate_password_hash(data["password"]), data.get("role","Member"), data.get("phone",""), data.get("membership","Standard"), datetime.now().strftime("%Y-%m-%d %H:%M"), "Active", api_key))
        conn.commit()
        user = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status,api_key FROM users WHERE email=?", (data["email"],)).fetchone()
        conn.close()
        return jsonify({"message": "Registered successfully", "member": dict(user)}), 201
    except Exception as e:
        return jsonify({"error": f"Email already exists or {str(e)}"}), 400

@app.route("/api/login", methods=["POST"])
def api_login():
    data = request.get_json() or request.form
    conn = get_db()
    u = conn.execute("SELECT * FROM users WHERE email=?", (data.get("email"),)).fetchone()
    conn.close()
    if not u or not check_password_hash(u["password"], data.get("password","")):
        return jsonify({"error": "Invalid email or password"}), 401
    return jsonify({"message": "Login success", "member": {"id": u["id"], "name": u["name"], "email": u["email"], "phone": u["phone"], "role": u["role"], "membership": u["membership"], "api_key": u["api_key"]}})

@app.route("/api/members/<int:id>", methods=["PUT"])
@require_api_key
def api_update_member(id):
    data = request.get_json()
    conn = get_db()
    fields = []
    values = []
    for k in ["name","email","phone","role","membership","status"]:
        if k in data:
            fields.append(f"{k}=?")
            values.append(data[k])
    if not fields: return jsonify({"error": "No fields to update"}), 400
    values.append(id)
    conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", values)
    conn.commit()
    u = conn.execute("SELECT id,name,email,phone,role,membership,join_date,status FROM users WHERE id=?", (id,)).fetchone()
    conn.close()
    return jsonify({"message": "Updated", "member": dict(u)})

@app.route("/api/members/<int:id>", methods=["DELETE"])
@require_api_key
def api_delete_member(id):
    conn = get_db()
    conn.execute("DELETE FROM users WHERE id=?", (id,))
    conn.commit(); conn.close()
    return jsonify({"message": f"Member {id} deleted"})

@app.route("/api/stats", methods=["GET"])
@require_api_key
def api_stats():
    conn = get_db()
    total = conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    admins = conn.execute("SELECT COUNT(*) FROM users WHERE role='Admin'").fetchone()[0]
    members = conn.execute("SELECT COUNT(*) FROM users WHERE role='Member'").fetchone()[0]
    conn.close()
    return jsonify({"total_members": total, "admins": admins, "members": members, "active": total})

# ==================== WEB UI (same as before) ====================
BASE = """<style>body{font-family:Arial;background:#f0f2f5;margin:0;padding:10px}.card{background:white;padding:15px;border-radius:12px;box-shadow:0 2px 8px #ccc;max-width:1000px;margin:auto}table{width:100%;border-collapse:collapse;font-size:14px}th,td{border:1px solid #ddd;padding:8px}th{background:#007bff;color:white}.btn{padding:5px 10px;border:none;border-radius:5px;color:white;text-decoration:none;font-size:12px;margin:1px;display:inline-block}.btn-blue{background:#007bff}.btn-red{background:#dc3545}.btn-green{background:#28a745}input,select{padding:8px;margin:4px;border:1px solid #ccc;border-radius:5px;width:95%}</style>
<div class="card"><div><a href="/">🏠 Home</a> | <a href="/admin">📊 Admin</a> | <a href="/api">📚 API Docs</a> | <a href="/export">📥 Export</a> | <a href="/logout">🚪 Logout</a></div><hr>{{CONTENT}}</div>"""

@app.route("/")
def home():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); user=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone(); conn.close()
    return render_template_string(BASE.replace("{{CONTENT}}", f"<h2>Welcome {user['name']}!</h2><p>Email: {user['email']}<br>Role: {user['role']}<br>API Key: <code>{user['api_key']}</code> (give to team)</p><p><a href='/api'>View API Docs</a> - Your API is at <b>https://lonma-orbit-24qw.onrender.com/api/members</b></p>"))

@app.route("/admin")
def admin():
    if "user_id" not in session: return redirect("/login")
    conn=get_db(); cur=conn.execute("SELECT * FROM users WHERE id=?",(session["user_id"],)).fetchone()
    if cur["role"]!="Admin": conn.close(); return render_template_string(BASE.replace("{{CONTENT}}", "Admin only. Login admin@lonma.com / admin123"))
    users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); conn.close()
    rows="".join([f"<tr><td>{u['id']}</td><td>{u['name']}</td><td>{u['email']}</td><td>{u['api_key'][:15]}...</td><td>{u['role']}</td><td><a class='btn btn-green' href='/make_admin/{u['id']}'>Admin</a><a class='btn btn-red' href='/delete/{u['id']}'>Del</a></td></tr>" for u in users])
    content=f"<h2>Admin - All Members ({len(users)})</h2><p>API Base: <code>https://lonma-orbit-24qw.onrender.com/api</code><br>Master API Key: <code>{cur['api_key']}</code></p><table><tr><th>ID</th><th>Name</th><th>Email</th><th>API Key</th><th>Role</th><th>Actions</th></tr>{rows}</table>"
    return render_template_string(BASE.replace("{{CONTENT}}", content))

@app.route("/make_admin/<int:id>")
def make_admin(id): conn=get_db(); conn.execute("UPDATE users SET role='Admin' WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/delete/<int:id>")
def delete(id): conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/export")
def export():
    conn=get_db(); users=conn.execute("SELECT id,name,email,phone,role,membership,join_date,status,api_key FROM users").fetchall(); conn.close()
    out=io.StringIO(); w=csv.writer(out); w.writerow(["ID","Name","Email","Phone","Role","Membership","JoinDate","Status","APIKey"])
    for u in users: w.writerow([u["id"],u["name"],u["email"],u["phone"],u["role"],u["membership"],u["join_date"],u["status"],u["api_key"]])
    return Response(out.getvalue(), mimetype="text/csv", headers={"Content-Disposition":"attachment;filename=lonma.csv"})

@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(request.form["email"],)).fetchone(); conn.close()
        if u and check_password_hash(u["password"], request.form["password"]): session["user_id"]=u["id"]; return redirect("/")
    return render_template_string(BASE.replace("{{CONTENT}}", "<h3>Login</h3><form method='post'><input name='email' placeholder='Email' required><br><input name='password' type='password' placeholder='Password' required><br><button class='btn btn-blue'>Login</button></form><p>Admin: admin@lonma.com / admin123</p>"))
@app.route("/logout")
def logout(): session.clear(); return redirect("/login")

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
