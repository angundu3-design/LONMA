import sqlite3
import os
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
DB = "lonma.db"

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, staff_no TEXT, project TEXT, month_joined TEXT, status TEXT DEFAULT 'active member', father_id TEXT DEFAULT '-', mother_id TEXT DEFAULT '-', guardian_id TEXT DEFAULT '-', spouse_id TEXT DEFAULT '-', kid1 TEXT DEFAULT '-', kid2 TEXT DEFAULT '-', kid3 TEXT DEFAULT '-', kid4 TEXT DEFAULT '-', kid5 TEXT DEFAULT '-')")
    cur.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, action TEXT, amount REAL DEFAULT 0, date TEXT)")
    con.commit()
    count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        seed = [
            ("Marlon K. Ang'undu", "FIG001", "FIG", "2026-01", "active member", "-", "-", "1951498", "-", "6879175", "-", "-", "-", "-"),
            ("Mary Ngotah", "FIG002", "Gold Crown Beverage", "2026-01", "active member", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("Celestine Ouko", "FIG003", "SC Johnsons", "2026-01", "active member", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("Irene Wamuyu", "FIG004", "Nairobi Java", "2026-01", "active member", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("Jonathan Mutunga", "FIG005", "Last Mile Trufoods Ltd", "2026-01", "active member", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
        ]
        for s in seed:
            cur.execute("INSERT INTO users (full_names, staff_no, project, month_joined, status, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?)", s)
        con.commit()
    con.close()

init_db()

def shell(title, body):
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>body{{font-family:Arial;margin:0;background:white;color:black}}header{{background:darkblue;color:white;padding:14px}}nav a{{color:white;margin-right:12px;text-decoration:none;font-weight:bold}}main{{padding:14px}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid lightgray;padding:8px;text-align:left}}th{{background:lightgray}}input,select,button{{padding:10px;margin:4px 0;width:100%;box-sizing:border-box}}button{{background:darkblue;color:white;border:none;font-weight:bold}}.card{{border:1px solid lightgray;padding:12px;margin-bottom:10px}}</style></head><body><header><b>LONMA ORBIT - FIG WELFARE</b><br><nav><a href="/">Home</a><a href="/register">Register</a><a href="/members">Members</a><a href="/history">History</a><a href="/shareout">Share-Out</a><a href="/community">Community</a></nav></header><main><h1>{title}</h1>{body}</main></body></html>"""

@app.route("/")
def home():
    con = get_db()
    total = con.execute("SELECT COUNT(*) FROM users WHERE status='active member'").fetchone()[0]
    con.close()
    h = ""
    h += f"<div class='card'><b>Active Members: {total}</b><br>Contribution: Ksh 300 per month<br>Deducted from monthly pay</div>"
    h += "<div class='card'><b>Membership Rule</b><br>Once you are employed with FIG, you automatically become a member. No application needed. Membership starts on your employment date.</div>"
    h += "<div class='card'><b>Death Benefits</b><br>Member: 100,000 | Spouse: 50,000 | Child: 40,000 | Parents: 40,000<br>Loss of Earning: 50% of basic pay, max Ksh 20,000, after 10 days unable to work</div>"
    h += "<div class='card'><b>Year-End</b><br>Minimum balance Ksh 250,000. Amount above is shared only among current active members. Year ends 30 November. Audited accounts by 20 December in FACES family group.</div>"
    return shell("Home", h)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_names = request.form.get("full_names", "").strip()
        staff_no = request.form.get("staff_no", "").strip()
        project = request.form.get("project", "").strip()
        month_joined = request.form.get("month_joined", "").strip()
        father_id = request.form.get("father_id", "-").strip() or "-"
        mother_id = request.form.get("mother_id", "-").strip() or "-"
        guardian_id = request.form.get("guardian_id", "-").strip() or "-"
        spouse_id = request.form.get("spouse_id", "-").strip() or "-"
        kid1 = request.form.get("kid1", "-").strip() or "-"
        kid2 = request.form.get("kid2", "-").strip() or "-"
        kid3 = request.form.get("kid3", "-").strip() or "-"
        kid4 = request.form.get("kid4", "-").strip() or "-"
        kid5 = request.form.get("kid5", "-").strip() or "-"
        if full_names:
            con = get_db()
            con.execute("INSERT INTO users (full_names, staff_no, project, month_joined, status, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5) VALUES (?,?,?,?, 'active member', ?,?,?,?,?,?,?,?,?)", (full_names, staff_no, project, month_joined, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5))
            con.execute("INSERT INTO history (full_names, action, amount, date) VALUES (?, 'Joined - Automatic Membership on Employment', 0, ?)", (full_names, month_joined))
            con.commit()
            con.close()
            return redirect("/members")
    h = ""
    h += "<form method='POST'>"
    h += "<label>Full Names</label><input name='full_names' required>"
    h += "<label>Staff No</label><input name='staff_no'>"
    h += "<label>Project / Company</label><input name='project' placeholder='FIG'>"
    h += "<label>Month Joined / Employment Date</label><input name='month_joined' placeholder='2026-01'>"
    h += "<label>Father ID</label><input name='father_id' placeholder='-'>"
    h += "<label>Mother ID</label><input name='mother_id' placeholder='-'>"
    h += "<label>Guardian ID - if no biological parents</label><input name='guardian_id' placeholder='-'>"
    h += "<label>Spouse ID</label><input name='spouse_id' placeholder='-'>"
    h += "<label>Kid 1 - Birth Cert / ID</label><input name='kid1' placeholder='-'>"
    h += "<label>Kid 2</label><input name='kid2' placeholder='-'>"
    h += "<label>Kid 3</label><input name='kid3' placeholder='-'>"
    h += "<label>Kid 4</label><input name='kid4' placeholder='-'>"
    h += "<label>Kid 5</label><input name='kid5' placeholder='-'>"
    h += "<button type='submit'>Register - Automatic Member</button></form>"
    h += "<p>By registering, you confirm employment with FIG. You automatically become a member.</p>"
    return shell("Register", h)

@app.route("/members")
def members():
    con = get_db()
    rows = con.execute("SELECT * FROM users ORDER BY full_names").fetchall()
    con.close()
    h = "<input id='q' placeholder='Search member...' onkeyup='f()'>"
    h += "<table><thead><tr><th>Name</th><th>Staff</th><th>Project</th><th>Status</th><th>Joined</th><th>Father</th><th>Mother</th><th>Guardian</th><th>Spouse</th><th>Kid 1</th><th>Kid 2</th><th>Kid 3</th><th>Kid 4</th><th>Kid 5</th></tr></thead><tbody id='tb'>"
    for m in rows:
        h += f"<tr><td>{m['full_names']}</td><td>{m['staff_no']}</td><td>{m['project']}</td><td>{m['status']}</td><td>{m['month_joined']}</td><td>{m['father_id']}</td><td>{m['mother_id']}</td><td>{m['guardian_id']}</td><td>{m['spouse_id']}</td><td>{m['kid1']}</td><td>{m['kid2']}</td><td>{m['kid3']}</td><td>{m['kid4']}</td><td>{m['kid5']}</td></tr>"
    h += "</tbody></table>"
    h += "<script>function f(){var q=document.getElementById('q').value.toLowerCase();var tr=document.getElementById('tb').getElementsByTagName('tr');for(var i=0;i<tr.length;i++){tr[i].style.display=tr[i].textContent.toLowerCase().includes(q)?'':'none'}}</script>"
    return shell("Members", h)

@app.route("/history")
def history():
    con = get_db()
    rows = con.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    con.close()
    h = "<table><tr><th>Name</th><th>Action</th><th>Amount</th><th>Date</th></tr>"
    for r in rows:
        h += f"<tr><td>{r['full_names']}</td><td>{r['action']}</td><td>{r['amount']}</td><td>{r['date']}</td></tr>"
    h += "</table>"
    return shell("History", h)

@app.route("/shareout")
def shareout():
    con = get_db()
    rows = con.execute("SELECT * FROM users WHERE status='active member'").fetchall()
    con.close()
    total = len(rows) * 300
    above = total - 250000
    if above < 0:
        above = 0
    share = 0
    if len(rows) > 0:
        share = above / len(rows)
    h = f"<div class='card'>Active Members: {len(rows)}<br>Total Contribution: Ksh {total}<br>Minimum Balance: Ksh 250000<br>Amount Above Minimum: Ksh {above}<br>Share Per Member: Ksh {round(share,2)}</div>"
    h += "<table><tr><th>Name</th><th>Share</th></tr>"
    for m in rows:
        h += f"<tr><td>{m['full_names']}</td><td>{round(share,2)}</td></tr>"
    h += "</table>"
    return shell("Share-Out", h)

@app.route("/community")
def community():
    h = "<div class='card'><b>Officials</b><br>Marlon K. Ang'undu - Chairman, FIG - +254 707 780 807<br>Mary Ngotah - Gold Crown Beverage - 0719 203 286<br>Celestine Ouko - SC Johnsons - 0725 543 224<br>Irene Wamuyu - Nairobi Java - 0719 606 834<br>Jonathan Mutunga - Last Mile Trufoods Ltd - 0719 555 326</div>"
    h += "<div class='card'><b>Welfare Management</b><br>Welfare managed by committee elected by all members. Every project must have at least one member on board. Members elect office bearers from among themselves.</div>"
    return shell("Community", h)

@app.route("/fix_ids")
def fix_ids():
    con = get_db()
    con.execute("UPDATE users SET guardian_id='1951498', kid1='6879175' WHERE lower(full_names) LIKE '%marlon%'")
    con.commit()
    con.close()
    return "FIXED Marlon - Guardian 1951498 Kid 6879175"

@app.route("/api/members")
def api_members():
    con = get_db()
    rows = con.execute("SELECT * FROM users ORDER BY full_names").fetchall()
    con.close()
    out = []
    for m in rows:
        out.append({"full_names": m["full_names"], "staff_no": m["staff_no"], "project": m["project"], "status": m["status"], "month_joined": m["month_joined"], "father_id": m["father_id"], "mother_id": m["mother_id"], "guardian_id": m["guardian_id"], "spouse_id": m["spouse_id"], "kid1": m["kid1"], "kid2": m["kid2"], "kid3": m["kid3"], "kid4": m["kid4"], "kid5": m["kid5"]})
    return jsonify(out)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
