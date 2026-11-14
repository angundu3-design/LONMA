import os
import json
from datetime import datetime
from flask import Flask, request, jsonify, render_template_string

app = Flask(__name__)

# ===== DATA STORE (in-memory, seeded) =====
MEMBERS = []
CONTRIBUTIONS = []
LOANS = []
NOTIFICATIONS = []

def seed_data():
    global MEMBERS, CONTRIBUTIONS, LOANS, NOTIFICATIONS
    if MEMBERS:
        return
    names = ["Mary Achieng", "John Otieno", "Grace Wanjiru", "Peter Kamau", "Sarah Njeri",
             "David Mwangi", "Faith Atieno", "Joseph Kiprop", "Esther Muthoni", "Daniel Onyango"]
    for i, name in enumerate(names, start=1):
        MEMBERS.append({
            "id": i,
            "name": name,
            "phone": f"07{i}0 123 45{i}",
            "status": "Active",
            "joined": "2025-01-15",
            "shares": 10 + i,
            "total_contributed": 5000 * i,
            "total_loans": 0
        })
    for i in range(1, 21):
        CONTRIBUTIONS.append({
            "id": i,
            "member_id": (i % 10) + 1,
            "amount": 1000,
            "date": "2026-11-01",
            "type": "Monthly Contribution"
        })
    NOTIFICATIONS.append({
        "id": 1,
        "title": "Welcome to LONMA Orbit",
        "message": "Your account is active. Welcome!",
        "date": datetime.now().strftime("%Y-%m-%d"),
        "read": False
    })
    print(f"v113 seeded {len(MEMBERS) + len(CONTRIBUTIONS)}")

seed_data()

# ===== HTML TEMPLATE =====
HTML = """
<!DOCTYPE html>
<html><head><meta name="viewport" content="width=device-width,initial-scale=1">
<title>LONMA Orbit</title>
<style>
body{font-family:Arial;margin:0;background:#f4f6f8}
header{background:#0b3d91;color:#fff;padding:16px;text-align:center}
nav{display:flex;gap:8px;justify-content:center;padding:12px;flex-wrap:wrap}
nav a{background:#fff;padding:10px 16px;border-radius:20px;text-decoration:none;color:#0b3d91;font-weight:bold;box-shadow:0 1px 4px rgba(0,0,0,.1)}
.card{background:#fff;margin:12px;padding:16px;border-radius:12px;box-shadow:0 1px 4px rgba(0,0,0,.1)}
h2{margin:0 0 8px} .big{font-size:28px;font-weight:bold;color:#0b3d91}
table{width:100%;border-collapse:collapse} td,th{padding:8px;border-bottom:1px solid #eee;text-align:left;font-size:14px}
button{background:#0b3d91;color:#fff;border:0;padding:10px 16px;border-radius:8px}
input{padding:10px;width:100%;margin:6px 0;border:1px solid #ddd;border-radius:8px;box-sizing:border-box}
</style></head>
<body>
<header><h1>LONMA ORBIT</h1><p>Members • Savings • Loans • Shareout</p></header>
<nav>
<a href="/">Home</a><a href="/members">Members</a><a href="/shareout">Shareout</a>
<a href="/contributions">Contributions</a><a href="/loans">Loans</a>
</nav>
<div class="card"><h2>Dashboard</h2>
<p>Total Members: <span class="big" id="totalMembers">-</span></p>
<p>Total Contributions: <span class="big" id="totalContrib">-</span></p>
<p>Total Loans: <span class="big" id="totalLoans">-</span></p>
</div>
<div class="card"><h2>Add Member</h2>
<input id="mName" placeholder="Full Name"><input id="mPhone" placeholder="Phone e.g 0712345678">
<button onclick="addMember()">Add Member</button><p id="msg"></p></div>
<div class="card"><h2>Members List</h2><div id="list">Loading...</div></div>
<script>
async function load(){
  let r = await fetch('/api/stats'); let s = await r.json();
  document.getElementById('totalMembers').innerText = s.total_members;
  document.getElementById('totalContrib').innerText = 'KES ' + s.total_contributions;
  document.getElementById('totalLoans').innerText = 'KES ' + s.total_loans;
  let r2 = await fetch('/api/members'); let m = await r2.json();
  let h = '<table><tr><th>#</th><th>Name</th><th>Phone</th><th>Shares</th></tr>';
  m.forEach(x=>{ h += `<tr><td>${x.id}</td><td>${x.name}</td><td>${x.phone}</td><td>${x.shares}</td></tr>` });
  h += '</table>'; document.getElementById('list').innerHTML = h;
}
async function addMember(){
  let name = document.getElementById('mName').value;
  let phone = document.getElementById('mPhone').value;
  if(!name){ alert('Enter name'); return; }
  let r = await fetch('/api/members',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,phone:phone})});
  let d = await r.json();
  document.getElementById('msg').innerText = d.message || 'Added!';
  load();
}
load();
</script></body></html>
"""

# ===== ROUTES =====
@app.route("/")
def home():
    return render_template_string(HTML)

@app.route("/members")
def members_page():
    return render_template_string(HTML)

@app.route("/shareout")
def shareout_page():
    return render_template_string(HTML)

@app.route("/contributions")
def contrib_page():
    return render_template_string(HTML)

@app.route("/loans")
def loans_page():
    return render_template_string(HTML)

@app.route("/api/stats")
def api_stats():
    return jsonify({
        "total_members": len(MEMBERS),
        "total_contributions": sum(c["amount"] for c in CONTRIBUTIONS),
        "total_loans": sum(l.get("amount", 0) for l in LOANS),
        "total_shares": sum(m.get("shares", 0) for m in MEMBERS)
    })

@app.route("/api/members", methods=["GET", "POST"])
def api_members():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        name = data.get("name", "").strip()
        if not name:
            return jsonify({"error": "Name is required"}), 400
        new_id = max([m["id"] for m in MEMBERS], default=0) + 1
        member = {
            "id": new_id,
            "name": name,
            "phone": data.get("phone", ""),
            "status": "Active",
            "joined": datetime.now().strftime("%Y-%m-%d"),
            "shares": 0,
            "total_contributed": 0,
            "total_loans": 0
        }
        MEMBERS.append(member)
        return jsonify({"message": "Member added successfully", "member": member}), 201
    return jsonify(MEMBERS)

@app.route("/api/members/<int:member_id>", methods=["GET", "DELETE"])
def api_member_one(member_id):
    m = next((x for x in MEMBERS if x["id"] == member_id), None)
    if not m:
        return jsonify({"error": "Member not found"}), 404
    if request.method == "DELETE":
        MEMBERS.remove(m)
        return jsonify({"message": "Member deleted"})
    return jsonify(m)

@app.route("/api/contributions", methods=["GET", "POST"])
def api_contributions():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            amount = float(data.get("amount", 0))
        except:
            return jsonify({"error": "Invalid amount"}), 400
        if amount <= 0:
            return jsonify({"error": "Amount must be > 0"}), 400
        new_id = max([c["id"] for c in CONTRIBUTIONS], default=0) + 1
        c = {"id": new_id, "member_id": int(data.get("member_id", 1)), "amount": amount,
             "date": datetime.now().strftime("%Y-%m-%d"), "type": data.get("type", "Contribution")}
        CONTRIBUTIONS.append(c)
        return jsonify({"message": "Contribution added", "contribution": c}), 201
    return jsonify(CONTRIBUTIONS)

@app.route("/api/loans", methods=["GET", "POST"])
def api_loans():
    if request.method == "POST":
        data = request.get_json(silent=True) or {}
        try:
            amount = float(data.get("amount", 0))
        except:
            return jsonify({"error": "Invalid amount"}), 400
        new_id = max([l.get("id", 0) for l in LOANS], default=0) + 1
        loan = {"id": new_id, "member_id": int(data.get("member_id", 1)), "amount": amount,
                "status": "Pending", "date": datetime.now().strftime("%Y-%m-%d")}
        LOANS.append(loan)
        return jsonify({"message": "Loan requested", "loan": loan}), 201
    return jsonify(LOANS)

@app.route("/api/notifications")
def api_notifications():
    return jsonify(NOTIFICATIONS)

@app.route("/api/shareout")
def api_shareout():
    total = sum(c["amount"] for c in CONTRIBUTIONS)
    per_member = round(total / len(MEMBERS), 2) if MEMBERS else 0
    return jsonify({
        "total_pool": total,
        "members": len(MEMBERS),
        "per_member": per_member,
        "breakdown": [{"id": m["id"], "name": m["name"], "share": per_member} for m in MEMBERS]
    })

@app.route("/health")
def health():
    return jsonify({"status": "ok"}), 200

@app.errorhandler(404)
def not_found(e):
    # Return home page for frontend routes, JSON for API
    if request.path.startswith("/api/"):
        return jsonify({"error": "Not found"}), 404
    return render_template_string(HTML), 200

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
