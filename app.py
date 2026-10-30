from flask import Flask, render_template_string, request, redirect, session, Response, jsonify
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps

app = Flask(__name__)
app.secret_key = "lonma-welfare-final"
DB = "lonma.db"

def get_db():
    conn = sqlite3.connect(DB)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    conn = get_db()
    conn.execute('''CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY,
    staff_no TEXT, full_names TEXT, project TEXT, month_year_joined TEXT,
    email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT,
    father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT,
    kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT,
    api_key TEXT)''')
    admin = conn.execute("SELECT * FROM users WHERE email='admin@lonma.com'").fetchone()
    if not admin:
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        ("PWANI/001", "Admin User", "PWANI", "Oct 2026", "admin@lonma.com", generate_password_hash("admin123"), "Admin", "0700000000",
         "N/A", "N/A", "22400966", "23601476", "42107914", "111041990", "", "", "", "lonma_api_key_12345"))
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

STYLE = """<style>body{font-family:Arial;background:#f4f4f4;margin:0}.nav{background:#007bff;padding:12px}.nav a{color:white;margin:0 8px;text-decoration:none;font-weight:bold}.card{background:white;max-width:1200px;margin:15px auto;padding:15px;border-radius:10px;box-shadow:0 2px 8px #ccc;overflow-x:auto}table{width:100%;border-collapse:collapse;font-size:11px}th,td{border:1px solid #ddd;padding:6px}th{background:#007bff;color:white}.btn{padding:5px 10px;border:none;border-radius:4px;color:white;text-decoration:none;display:inline-block;margin:1px;font-size:11px}.blue{background:#007bff}.red{background:#dc3545}.green{background:#28a745}input,select{padding:8px;margin:3px;border:1px solid #ccc;border-radius:4px}</style>"""

# API WITH WELFARE DATA
@app.route("/api")
def api_docs(): 
    return jsonify({
        "live": "https://lonma-orbit-24qw.onrender.com",
        "api_key": "lonma_api_key_12345",
        "welfare_fields": ["staff_no","full_names","project","month_year_joined","father_id","mother_id","guardian_id","spouse_id","kid1-kid5"],
        "endpoints": {
            "GET /api/members": "Get ALL welfare members",
            "POST /api/register": "Register with welfare data",
            "PUT /api/members/<id>": "Update welfare data"
        }
    })

@app.route("/api/members", methods=["GET","OPTIONS"])
@need_key
def get_members():
    conn=get_db(); users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); conn.close()
    result=[]
    for u in users:
        result.append({
            "id": u["id"], "staff_no": u["staff_no"], "full_names": u["full_names"],
            "project": u["project"], "month_year_joined": u["month_year_joined"],
            "email": u["email"], "phone": u["phone"], "role": u["role"],
            "parents_ids": {"father": u["father_id"], "mother": u["mother_id"]},
            "guardian_id": u["guardian_id"], "spouse_id": u["spouse_id"],
            "kids_birth_certs": [u["kid1"], u["kid2"], u["kid3"], u["kid4"], u["kid5"]]
        })
    return jsonify({"total": len(result), "project": "PWANI", "members": result})

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method=='OPTIONS': return '',200
    d=request.get_json() or request.form
    try:
        key=f"lonma_{secrets.token_hex(8)}"
        conn=get_db()
        conn.execute("""INSERT INTO users 
        (staff_no, full_names, project, month_year_joined, email, password, role, phone,
         father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key)
        VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
        (d.get("staff_no",""), d.get("full_names",d.get("name","")), d.get("project","PWANI"), d.get("month_year_joined",""),
         d.get("email"), generate_password_hash(d.get("password","1234")), d.get("role","Member"), d.get("phone",""),
         d.get("father_id",""), d.get("mother_id",""), d.get("guardian_id",""), d.get("spouse_id",""),
         d.get("kid1",""), d.get("kid2",""), d.get("kid3",""), d.get("kid4",""), d.get("kid5",""), key))
        conn.commit(); u=conn.execute("SELECT * FROM users WHERE email=?",(d["email"],)).fetchone(); conn.close()
        return jsonify({"message":"Welfare member registered","id":u["id"],"api_key":key}),201
    except Exception as e: return jsonify({"error":str(e)}),400

@app.route("/api/members/<int:id>", methods=["PUT","OPTIONS"])
@need_key
def api_update(id):
    if request.method=='OPTIONS': return '',200
    d=request.get_json(); conn=get_db()
    fields=[]; vals=[]
    for k in ["staff_no","full_names","project","month_year_joined","email","phone","role","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]:
        if k in d: fields.append(f"{k}=?"); vals.append(d[k])
    if not fields: return jsonify({"error":"No fields"}),400
    vals.append(id); conn.execute(f"UPDATE users SET {', '.join(fields)} WHERE id=?", vals); conn.commit(); conn.close()
    return jsonify({"updated":id})

@app.route("/api/members/<int:id>", methods=["DELETE","OPTIONS"])
@need_key
def api_del(id):
    conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close()
    return jsonify({"deleted":id})

@app.route("/api/stats", methods=["GET","OPTIONS"])
@need_key
def stats():
    conn=get_db(); total=conn.execute("SELECT COUNT(*) FROM users").fetchone()[0]; conn.close()
    return jsonify({"total_members":total,"project":"PWANI","welfare_data":"active"})

# WEB SIMPLE ADMIN WITH WELFARE
@app.route("/")
def home():
    if "uid" not in session: return redirect("/login")
    conn=get_db(); u=conn.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone(); conn.close()
    return render_template_string(STYLE+f"<div class='nav'><a href='/'>Home</a><a href='/admin'>Admin</a><a href='/tester'>Tester</a><a href='/logout'>Logout</a></div><div class='card'><h2>{u['full_names']}</h2><p>Staff: {u['staff_no']} | Project: {u['project']} | Role: {u['role']}</p><p>Parents: Father {u['father_id']} / Mother {u['mother_id']}<br>Guardian: {u['guardian_id']} | Spouse: {u['spouse_id']}<br>Kids: {u['kid1']}, {u['kid2']}, {u['kid3']}, {u['kid4']}, {u['kid5']}</p></div>")

@app.route("/admin")
def admin():
    if "uid" not in session: return redirect("/login")
    conn=get_db(); me=conn.execute("SELECT * FROM users WHERE id=?",(session["uid"],)).fetchone()
    if me["role"]!="Admin": conn.close(); return render_template_string(STYLE+"<div class='card'><h3 style='color:red'>Admin only</h3></div>")
    users=conn.execute("SELECT * FROM users ORDER BY id DESC").fetchall(); conn.close()
    rows="".join([f"<tr><td>{u['staff_no']}</td><td>{u['full_names']}</td><td>{u['project']}</td><td>{u['father_id']}</td><td>{u['mother_id']}</td><td>{u['guardian_id']}</td><td>{u['spouse_id']}</td><td>{u['kid1']},{u['kid2']},{u['kid3']}</td><td>{u['role']}</td><td><a class='btn red' href='/delete/{u['id']}'>Del</a></td></tr>" for u in users])
    return render_template_string(STYLE+f"<div class='nav'><a href='/'>Home</a><a href='/admin'>Admin</a><a href='/tester'>Tester</a><a href='/logout'>Logout</a></div><div class='card'><h2>PWANI Welfare Admin ({len(users)} Members)</h2><p>Master Key: lonma_api_key_12345 | <a href='/api/members?api_key=lonma_api_key_12345' target='_blank'>View API JSON</a></p><table><tr><th>Staff No</th><th>Full Names</th><th>Project</th><th>Father ID</th><th>Mother ID</th><th>Guardian</th><th>Spouse</th><th>Kids Certs</th><th>Role</th><th>Action</th></tr>{rows}</table><br><a href='/register' class='btn blue'>+ Add Welfare Member</a></div>")

@app.route("/delete/<int:id>")
def delete(id): conn=get_db(); conn.execute("DELETE FROM users WHERE id=?",(id,)); conn.commit(); conn.close(); return redirect("/admin")
@app.route("/login", methods=["GET","POST"])
def login():
    if request.method=="POST":
        conn=get_db(); u=conn.execute("SELECT * FROM users WHERE email=?",(request.form["email"],)).fetchone(); conn.close()
        if u and check_password_hash(u["password"],request.form["password"]): session["uid"]=u["id"]; return redirect("/")
    return render_template_string(STYLE+"<div class='card'><h2>PWANI Welfare Login</h2><form method='post'><input name='email' placeholder='Email' required><br><input name='password' type='password' placeholder='Password' required><br><button class='btn blue'>Login</button></form><p>admin@lonma.com / admin123</p></div>")
@app.route("/register", methods=["GET","POST"])
def register():
    if request.method=="POST":
        try:
            d=request.form; conn=get_db(); key=f"lonma_{secrets.token_hex(8)}"
            conn.execute("""INSERT INTO users (staff_no, full_names, project, month_year_joined, email, password, role, phone, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, api_key) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
            (d.get("staff_no"), d.get("full_names"), d.get("project"), d.get("month_year_joined"), d.get("email"), generate_password_hash(d.get("password")), "Member", d.get("phone"), d.get("father_id"), d.get("mother_id"), d.get("guardian_id"), d.get("spouse_id"), d.get("kid1"), d.get("kid2"), d.get("kid3"), d.get("kid4"), d.get("kid5"), key))
            conn.commit(); conn.close(); return redirect("/login")
        except Exception as e: return f"Error {e}"
    return render_template_string(STYLE+"""<div class='card'><h2>Register PWANI Welfare Member</h2><form method='post'>
    <input name='staff_no' placeholder='Staff No & Full Names (e.g PWANI/001)' required><br>
    <input name='full_names' placeholder='Full Names' required><br>
    <input name='project' placeholder='Project' value='PWANI'><br>
    <input name='month_year_joined' placeholder='Month & Year Joined'><br>
    <input name='email' placeholder='Email' required><br>
    <input name='phone' placeholder='Phone'><br>
    <input name='father_id' placeholder='Father ID'><br>
    <input name='mother_id' placeholder='Mother ID'><br>
    <input name='guardian_id' placeholder='Guardian ID NO'><br>
    <input name='spouse_id' placeholder='Spouse ID NO'><br>
    <input name='kid1' placeholder='Kid 1 Birth Cert'><br>
    <input name='kid2' placeholder='Kid 2 Birth Cert'><br>
    <input name='kid3' placeholder='Kid 3 Birth Cert'><br>
    <input name='kid4' placeholder='Kid 4 Birth Cert'><br>
    <input name='kid5' placeholder='Kid 5 Birth Cert'><br>
    <input name='password' type='password' placeholder='Password' required><br>
    <button class='btn blue'>Register Welfare Member</button></form></div>""")
@app.route("/logout")
def logout(): session.clear(); return redirect("/login")
@app.route("/tester")
def tester():
    return """<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><style>body{font-family:Arial;background:#0f172a;color:white;padding:10px}.card{background:#1e293b;padding:15px;border-radius:10px;max-width:800px;margin:auto}input{width:92%;padding:8px;margin:3px;border-radius:6px;border:none}button{padding:8px 12px;border:none;border-radius:6px;background:#38bdf8;font-weight:bold;margin:3px}pre{background:#020617;padding:10px;border-radius:6px;color:#22c55e;overflow:auto;font-size:11px}</style></head><body>
<div class="card"><h2>PWANI Welfare API Tester</h2><p>Key: lonma_api_key_12345 | <a href="/api/members?api_key=lonma_api_key_12345" style="color:#38bdf8" target="_blank">View JSON</a> | <a href="/admin" style="color:#38bdf8">Admin</a></p>
<button onclick="getAll()">GET ALL WELFARE MEMBERS</button><pre id="o1"></pre>
<h3>Add Welfare Member</h3><input id="sn" placeholder="Staff No"><input id="fn" placeholder="Full Names"><input id="em" placeholder="Email"><input id="ph" placeholder="Phone"><input id="fid" placeholder="Father ID"><input id="mid" placeholder="Mother ID"><input id="gid" placeholder="Guardian ID"><input id="sid" placeholder="Spouse ID"><input id="k1" placeholder="Kid1 Cert"><input id="k2" placeholder="Kid2 Cert"><input id="pw" placeholder="Password" type="password"><button onclick="reg()">REGISTER WELFARE</button><pre id="o2"></pre>
</div><script>
const BASE="https://lonma-orbit-24qw.onrender.com"; const KEY="lonma_api_key_12345";
async function getAll(){document.getElementById('o1').innerText="Loading..."; let r=await fetch(BASE+"/api/members",{headers:{"X-API-KEY":KEY}}); document.getElementById('o1').innerText=JSON.stringify(await r.json(),null,2);}
async function reg(){let b={staff_no:document.getElementById('sn').value,full_names:document.getElementById('fn').value,email:document.getElementById('em').value,phone:document.getElementById('ph').value,father_id:document.getElementById('fid').value,mother_id:document.getElementById('mid').value,guardian_id:document.getElementById('gid').value,spouse_id:document.getElementById('sid').value,kid1:document.getElementById('k1').value,kid2:document.getElementById('k2').value,password:document.getElementById('pw').value,project:"PWANI"}; let r=await fetch(BASE+"/api/register",{method:"POST",headers:{"Content-Type":"application/json"},body:JSON.stringify(b)}); document.getElementById('o2').innerText=JSON.stringify(await r.json(),null,2); if(r.ok) getAll();}
</script></body></html>"""

if __name__=="__main__": app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
