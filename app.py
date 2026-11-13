@app.route("/members")
def members_page():
    body='''<div class="eyebrow">Directory - F.I.G Brands Welfare</div><h1>Members</h1><p id="memberCountLabel" style="color:#6B7280"></p><div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap"><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="flex:1;min-width:200px"><select class="input" id="projFilter" onchange="fil()" style="max-width:220px"><option value="">All Projects</option>''' + ''.join([f'<option>{p}</option>' for p in PROJECTS]) + '''</select></div><div id="membersList" style="margin-top:14px"></div></div><script>let ALL=[];async function loadM(){let r=await fetch('/api/members');let d=await r.json();ALL=d.members;document.getElementById('memberCountLabel').textContent=ALL.length+' members - '+d.projects_total+' projects';fil()}function fil(){let q=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;let h='';ALL.filter(m=>(!q||(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(q))&&(!pf||m.project==pf)).forEach(m=>{h+='<div class="mcard"><div class="mhead"><div class="mavatar"><div class="mavatarCircle">'+m.full_names.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()+'</div></div><div class="minfo"><div class="mname">'+m.full_names+'</div><div class="memail">'+m.email+'</div><div class="mchips"><span class="pill">'+m.project+'</span><span class="mstatus"><i></i>Active</span></div></div></div><div class="mdetails"><div class="mdetail"><span>Staff No</span><b>'+m.staff_no+'</b></div><div class="mdetail"><span>Joined</span><b>'+(m.month_joined||'-')+'</b></div><div class="mdetail"><span>Project</span><b>'+m.project+'</b></div><div class="mdetail"><span>Months</span><b>'+m.months+'</b></div><div class="mdetail full"><span>Share Payable</span><b>KES '+m.share.toLocaleString(undefined,{minimumFractionDigits:2})+'</b></div></div></div>'});document.getElementById('membersList').innerHTML=h||'No members found';}loadM();</script>'''
    return shell("Members", body)

@app.route("/register", methods=["GET","POST"])
def register_page():
    if request.method=="POST":
        d=request.form or request.get_json(silent=True) or {}
        c=get_db()
        ok=add_user(c, d.get("staff_no",""), d.get("full_names",""), d.get("project",""), d.get("month_joined",""))
        c.commit(); c.close()
        if request.is_json: return jsonify({"ok": ok})
        return redirect("/members")
    body='''<div class="eyebrow">Join F.I.G</div><h1>Register Member</h1><div class="card"><form method="POST"><label>Staff No</label><input class="input" name="staff_no" required><div style="margin-top:12px"><label>Full Names</label><input class="input" name="full_names" required></div><div style="margin-top:12px"><label>Project</label><select class="input" name="project">''' + ''.join([f'<option>{p}</option>' for p in PROJECTS]) + '''</select></div><div style="margin-top:12px"><label>Date Joined e.g. 01/03/2025</label><input class="input" name="month_joined" placeholder="01/03/2025"></div><button class="btn" style="margin-top:16px">Register Member</button></form></div>'''
    return shell("Register", body)

@app.route("/login", methods=["GET","POST"])
def login_page():
    if request.method=="POST":
        d=request.form or request.get_json(silent=True) or {}
        email=(d.get("email") or "").strip().lower(); pw=d.get("password") or ""
        c=get_db(); u=c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); c.close()
        if u and check_password_hash(u["password"], pw):
            return jsonify({"ok": True, "name": u["full_names"], "email": u["email"], "role": u["role"] or "Member"})
        return jsonify({"ok": False, "error": "Invalid login"}), 401
    body='''<div class="eyebrow">Welcome Back</div><h1>Login</h1><div class="card"><label>Email</label><input class="input" id="email" value="marlonkikuyu@gmail.com"><div style="margin-top:12px"><label>Password</label><input class="input" id="pw" type="password" value="admin123"></div><button class="btn" onclick="doLogin()" style="margin-top:16px">Login</button><p id="st"></p><p style="color:#6B7280;font-size:13px">Admin: marlonkikuyu@gmail.com / admin123</p></div><script>async function doLogin(){let r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('pw').value})});let j=await r.json();if(j.ok){localStorage.setItem('fig_user',j.email);localStorage.setItem('fig_name',j.name);localStorage.setItem('fig_email',j.email);localStorage.setItem('fig_role',j.role);location.href='/'}else{document.getElementById('st').textContent=j.error}}</script>'''
    return shell("Login", body)

@app.route("/admin")
def admin_page():
    body='''<div class="eyebrow">Admin</div><h1>Admin / Settings</h1><div class="card"><p>BF: 855,759 | Reserve: 250,000 | To Share: 605,759</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn2" href="/download/excel">Download Excel</a><a class="btn2 gold" href="/download/shareout">Download Share-Out</a><a class="btn2" href="/register" style="background:#F3F4F6;color:#111827">Add Member</a></div></div><div class="card"><h2>Add Notification</h2><input class="input" id="nTitle" placeholder="Title"><input class="input" id="nMsg" placeholder="Message" style="margin-top:10px"><button class="btn" onclick="addN()" style="margin-top:12px">Send Notification</button><p id="nSt"></p></div><script>async function addN(){let r=await fetch('/api/notifications',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:document.getElementById('nTitle').value,msg:document.getElementById('nMsg').value})});let j=await r.json();document.getElementById('nSt').textContent=j.message}</script>'''
    return shell("Admin", body)

@app.route("/api/stats")
def api_stats():
    c=get_db(); rows=c.execute("SELECT project, COUNT(*) as cnt FROM users GROUP BY project").fetchall(); total=c.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]; c.close()
    bd={r["project"]: r["cnt"] for r in rows}
    return jsonify({"total_members": total, "projects_total": len(bd), "projects_breakdown": bd})

@app.route("/api/members")
def api_members():
    shares, tc, tm, rate = calc_shares()
    return jsonify({"members": shares, "total_members": len(shares), "projects_total": len(set(x["project"] for x in shares))})

@app.route("/api/shareout")
def api_shareout():
    shares, tc, tm, rate = calc_shares()
    return jsonify({"per_month_rate": rate, "total_months": tm, "total_contributions": tc, "total_shares": sum(x["share"] for x in shares), "members": len(shares)})

@app.route("/api/community", methods=["GET","POST"])
def api_community():
    c=get_db()
    if request.method=="POST":
        d=request.get_json(force=True)
        c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, media_type, media_data) VALUES (?,?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "", __import__("datetime").datetime.now().strftime("%d %b %Y %H:%M"), d.get("media_type") or "", d.get("media_data") or ""))
        c.commit(); c.close(); return jsonify({"message": "Posted"})
    filt=request.args.get("filter","all"); email=request.args.get("email","")
    rows=c.execute("SELECT * FROM community_posts ORDER BY id DESC LIMIT 100").fetchall()
    posts=[]
    for p in rows:
        likes=c.execute("SELECT COUNT(*) as n FROM community_likes WHERE post_id=?", (p["id"],)).fetchone()["n"]
        reposts=c.execute("SELECT COUNT(*) as n FROM community_posts WHERE repost_of=?", (str(p["id"]),)).fetchone()["n"]
        liked=bool(c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?", (p["id"], email)).fetchone()) if email else False
        bm=bool(c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?", (p["id"], email)).fetchone()) if email else False
        coms=[dict(x) for x in c.execute("SELECT * FROM community_comments WHERE post_id=? ORDER BY id ASC", (p["id"],)).fetchall()]
        d=dict(p); d["likes"]=likes; d["reposts"]=reposts; d["liked"]=liked; d["bookmarked"]=bm; d["comments"]=coms
        d["repost_name"]=""; d["repost_msg"]=""
        if p["repost_of"]:
            orig=c.execute("SELECT * FROM community_posts WHERE id=?", (p["repost_of"],)).fetchone()
            if orig: d["repost_name"]=orig["author_name"]; d["repost_msg"]=orig["msg"]
        posts.append(d)
    if filt=="mine": posts=[x for x in posts if x["author_email"]==email]
    if filt=="saved":
        ids=[r["post_id"] for r in c.execute("SELECT post_id FROM community_bookmarks WHERE email=?", (email,)).fetchall()]
        posts=[x for x in posts if x["id"] in ids]
    c.close(); return jsonify({"posts": posts})

@app.route("/api/community/<int:pid>/like", methods=["POST"])
def api_like(pid):
    d=request.get_json(force=True) or {}; email=d.get("email") or ""
    c=get_db()
    ex=c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?", (pid, email)).fetchone()
    if ex: c.execute("DELETE FROM community_likes WHERE id=?", (ex["id"],)); msg="Unliked"
    else: c.execute("INSERT INTO community_likes (post_id,email) VALUES (?,?)", (pid, email)); msg="Liked"
    c.commit(); c.close(); return jsonify({"message": msg})

@app.route("/api/community/<int:pid>/bookmark", methods=["POST"])
def api_bookmark(pid):
    d=request.get_json(force=True) or {}; email=d.get("email") or ""
    c=get_db()
    ex=c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?", (pid, email)).fetchone()
    if ex: c.execute("DELETE FROM community_bookmarks WHERE id=?", (ex["id"],)); msg="Removed from saved"
    else: c.execute("INSERT INTO community_bookmarks (post_id,email) VALUES (?,?)", (pid, email)); msg="Saved"
    c.commit(); c.close(); return jsonify({"message": msg})

@app.route("/api/community/<int:pid>/comment", methods=["POST"])
def api_comment(pid):
    d=request.get_json(force=True) or {}
    c=get_db(); c.execute("INSERT INTO community_comments (post_id, author_name, author_email, msg, created) VALUES (?,?,?,?,?)", (pid, d.get("name") or "Member", d.get("email") or "", d.get("msg") or "", __import__("datetime").datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Reply posted"})

@app.route("/api/community/<int:pid>/repost", methods=["POST"])
def api_repost(pid):
    d=request.get_json(force=True) or {}
    c=get_db(); orig=c.execute("SELECT * FROM community_posts WHERE id=?", (pid,)).fetchone()
    if not orig: c.close(); return jsonify({"error": "Not found"}), 404
    c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, repost_of) VALUES (?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "Reposted", __import__("datetime").datetime.now().strftime("%d %b %Y %H:%M"), str(pid)))
    c.commit(); c.close(); return jsonify({"message": "Reposted"})

@app.route("/api/community/<int:pid>", methods=["DELETE"])
def api_del_post(pid):
    key=request.args.get("key",""); email=request.args.get("email","")
    if key!=ADMIN_KEY and email.lower()!=ADMIN_EMAIL: return jsonify({"error": "Not allowed"}), 403
    c=get_db(); c.execute("DELETE FROM community_posts WHERE id=?", (pid,)); c.execute("DELETE FROM community_comments WHERE post_id=?", (pid,)); c.commit(); c.close()
    return jsonify({"message": "Deleted"})

@app.route("/api/notifications", methods=["GET","POST"])
def api_notif():
    c=get_db()
    if request.method=="POST":
        d=request.get_json(force=True) or {}
        c.execute("INSERT INTO notifications (title, msg, created, target, is_read) VALUES (?,?,?,?,?)", (d.get("title") or "F.I.G", d.get("msg") or "", __import__("datetime").datetime.now().strftime("%d %b %Y %H:%M"), d.get("target") or "/", 0))
        c.commit(); c.close(); return jsonify({"message": "Notification sent"})
    rows=[dict(x) for x in c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()]
    unread=c.execute("SELECT COUNT(*) as n FROM notifications WHERE is_read=0").fetchone()["n"]; c.close()
    return jsonify({"notifications": rows, "unread": unread})

@app.route("/api/notifications/<int:nid>/read", methods=["POST"])
def api_notif_read(nid):
    c=get_db(); c.execute("UPDATE notifications SET is_read=1 WHERE id=?", (nid,)); c.commit(); c.close(); return jsonify({"ok": True})

@app.route("/api/notifications/read", methods=["POST"])
def api_notif_read_all():
    c=get_db(); c.execute("UPDATE notifications SET is_read=1"); c.commit(); c.close(); return jsonify({"ok": True})

@app.route("/api/support", methods=["POST"])
def api_support():
    d=request.get_json(force=True) or {}
    c=get_db(); c.execute("INSERT INTO support_msgs (name, msg, created) VALUES (?,?,?)", (d.get("name") or "", d.get("msg") or "", __import__("datetime").datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Message sent. We will reply on WhatsApp 0707 780 807"})

@app.route("/download/excel")
def download_excel():
    shares, tc, tm, rate = calc_shares()
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title="Members"; ws.append(["Staff No","Full Names","Project","Email","Date Joined","Months","Contribution","Share"])
    for x in shares: ws.append([x["staff_no"], x["full_names"], x["project"], x["email"], x["month_joined"], x["months"], x["contribution"], round(x["share"],2)])
    out=io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_Members.xlsx")

@app.route("/health")
def health(): return jsonify({"ok": True, "version": "v113-fixed"})

if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
