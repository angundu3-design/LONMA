@app.route("/community")
def community_page():
 body='''<div class="eyebrow">F.I.G Brands · Together</div><h1>Community Chat</h1><p style="color:#6B7280">Post, repost, share, save. Be kind — no insults, no politics.</p><div class="card"><div style="display:flex;gap:12px"><div class="avatar" id="comAvatar">--</div><div style="flex:1"><div id="comName" style="font-weight:700"></div><div id="comProj" style="font-size:12px;color:#6B7280"></div></div></div><textarea id="comMsg" class="input" style="height:90px;padding:12px;margin-top:12px" placeholder="What's on your mind? Share with the family..."></textarea><div id="mediaPreview" style="margin-top:10px"></div><div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;align-items:center"><label class="btn2" style="background:#F3F4F6;color:#111827;cursor:pointer">📷 Photo <input type="file" id="comImg" accept="image/*" style="display:none" onchange="handleMedia(event,'image')"></label><label class="btn2" style="background:#F3F4F6;color:#111827;cursor:pointer">🎬 Video <input type="file" id="comVid" accept="video/*" style="display:none" onchange="handleMedia(event,'video')"></label><button class="btn2" onclick="postMsg()">Post to Community</button></div><div class="stackBtns"><button class="btn2 gold" onclick="loadCom('mine')">My Posts</button><button class="btn2 gold" onclick="loadCom('saved')">🔖 Saved</button><button class="btn2" onclick="loadCom('all')" style="background:#F3F4F6;color:#111827">All Posts</button></div><p id="comStatus"></p></div><div id="comFeed"></div><script>let comFilter='all';let comMedia='';let comMediaType='';function comInit(){let n=localStorage.getItem('fig_name')||'Member';document.getElementById('comName').textContent=n;document.getElementById('comAvatar').textContent=n.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();document.getElementById('comProj').textContent=localStorage.getItem('fig_email')||''}function handleMedia(e,type){let f=e.target.files[0];if(!f)return;let max=type=='video'?12*1024*1024:4*1024*1024;if(f.size>max){alert(type=='video'?'Video too big, max 12MB':'Photo too big, max 4MB');return}let r=new FileReader();r.onload=function(ev){comMedia=ev.target.result;comMediaType=type;document.getElementById('mediaPreview').innerHTML=type=='video'?'<video src="'+comMedia+'" controls style="width:100%;border-radius:12px;max-height:240px"></video><button onclick="clearMedia()" style="border:0;background:none;color:#B42318;cursor:pointer">✕ Remove video</button>':'<img src="'+comMedia+'" style="width:100%;border-radius:12px;max-height:240px;object-fit:cover"><button onclick="clearMedia()" style="border:0;background:none;color:#B42318;cursor:pointer">✕ Remove photo</button>'};r.readAsDataURL(f)}function clearMedia(){comMedia='';comMediaType='';document.getElementById('mediaPreview').innerHTML='';document.getElementById('comImg').value='';document.getElementById('comVid').value=''}function mediaHtml(p){if(!p.media_data)return '';if(p.media_type=='video')return '<video src="'+p.media_data+'" controls playsinline style="width:100%;border-radius:12px;max-height:320px;margin-top:8px"></video>';return '<img src="'+p.media_data+'" style="width:100%;border-radius:12px;max-height:320px;object-fit:cover;margin-top:8px">'}async function loadCom(f){comFilter=f||comFilter;let r=await fetch('/api/community?filter='+comFilter+'&email='+encodeURIComponent(localStorage.getItem('fig_email')||''));let d=await r.json();let h='';d.posts.forEach(p=>{let liked=p.liked?'❤️':'🤍';let saved=p.bookmarked?'🔖 Saved':'🔖 Save';let delBtn=(localStorage.getItem('fig_role')=='Admin'||p.author_email==localStorage.getItem('fig_email'))?'<button onclick="delPost('+p.id+')" style="border:0;background:none;color:#B42318;cursor:pointer;font-size:12px">Delete</button>':'';let repostBadge=p.repost_of?'<div style="background:#FFFBEB;border:1px solid #FDE68A;padding:8px 12px;border-radius:10px;font-size:13px;margin:0 18px 10px">🔁 Reposted from <b>'+(p.repost_name||'Member')+'</b><div style="color:#6B7280">'+(p.repost_msg||'')+'</div></div>':'';let coms=(p.comments||[]).map(c=>'<div style="display:flex;gap:8px;padding:8px 0;border-top:1px solid #F3F4F6"><b style="font-size:13px">'+c.author_name+'</b><span style="font-size:13px">'+c.msg+'</span></div>').join('');h+='<div class="mcard"><div class="mhead"><div class="mavatar"><div class="mavatarCircle">'+p.author_name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()+'</div></div><div class="minfo"><div class="mname" style="font-size:17px">'+p.author_name+'</div><div class="memail">'+p.project+' · '+p.created+'</div></div>'+delBtn+'</div>'+repostBadge+'<div style="padding:0 18px 12px;font-size:15px;line-height:1.6">'+p.msg+mediaHtml(p)+'</div><div style="display:flex;gap:10px;padding:10px 18px;border-top:1px solid #F3F4F6;flex-wrap:wrap"><button onclick="likePost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">'+liked+' '+p.likes+'</button><button onclick="document.getElementById(\\'c'+p.id+'\\').focus()" style="border:0;background:none;cursor:pointer;font-weight:600">💬 '+p.comments.length+'</button><button onclick="repostPost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">🔁 '+p.reposts+' Repost</button><button onclick="sharePost('+p.id+',\\''+p.author_name.replace(/'/g,"")+'\\')" style="border:0;background:none;cursor:pointer;font-weight:600">↗️ Share</button><button onclick="bookmarkPost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">'+saved+'</button></div><div style="padding:0 18px 14px"><div>'+coms+'</div><div style="display:flex;gap:8px;margin-top:8px"><input class="input" id="c'+p.id+'" placeholder="Write a reply..." style="height:40px"><button class="btn2" onclick="commentPost('+p.id+')">Reply</button></div></div></div>'});document.getElementById('comFeed').innerHTML=h||'<div class="card">No posts yet. Be the first to say hello 👋</div>'}async function postMsg(){let m=document.getElementById('comMsg').value.trim();if(!m&&!comMedia){document.getElementById('comStatus').textContent='Write something or add photo/video';return}let r=await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:m,media_type:comMediaType,media_data:comMedia})});let j=await r.json();document.getElementById('comStatus').textContent=j.message||j.error;if(r.ok){document.getElementById('comMsg').value='';clearMedia();loadCom('all')}}async function likePost(id){await fetch('/api/community/'+id+'/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:localStorage.getItem('fig_email')})});loadCom()}async function bookmarkPost(id){let r=await fetch('/api/community/'+id+'/bookmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:localStorage.getItem('fig_email')})});let j=await r.json();document.getElementById('comStatus').textContent=j.message||'';loadCom()}async function commentPost(id){let m=document.getElementById('c'+id).value.trim();if(!m)return;await fetch('/api/community/'+id+'/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:m})});loadCom()}async function repostPost(id){let c=prompt('Add your comment on this repost (optional):');if(c===null)return;let r=await fetch('/api/community/'+id+'/repost',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:c||'Reposted'})});let j=await r.json();alert(j.message||j.error);loadCom('all')}async function sharePost(id,author){let url=location.origin+'/community';let text='F.I.G Brands Community — Post by '+author+': '+url;if(navigator.share){try{await navigator.share({title:'F.I.G Brands Community',text:text,url:url});return}catch(e){}}try{await navigator.clipboard.writeText(text);alert('Link copied! Paste it on WhatsApp ✅')}catch(e){let w='https://wa.me/?text='+encodeURIComponent(text);window.open(w,'_blank')}}async function delPost(id){if(!confirm('Delete this post?'))return;await fetch('/api/community/'+id+'?key='''+ADMIN_KEY+'''&email='+encodeURIComponent(localStorage.getItem('fig_email')||''),{method:'DELETE'});loadCom()}comInit();loadCom('all');setInterval(()=>loadCom(),20000);</script>'''
 return shell("Community",body)
@app.route("/download/shareout")
def download_shareout():
 shares,tc,tm,rate=calc_shares()
 from openpyxl import Workbook
 from openpyxl.styles import Font,PatternFill,Alignment
 wb=Workbook();ws=wb.active;ws.title="Share-Out";ws.append(["F.I.G BRANDS WELFARE - SHARE-OUT SCHEDULE"]);ws.append(["BF less 250,000 shared per month"]);ws.append([f"BF: {BF:,} | Retained: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Months: {tm} | Value of One Month: {rate:,.2f} | Total Contributions: {tc:,}"]);ws.append([]);ws.append(["#","ID","Staff No","Full Names","Project","Date Joined","Months","Contribution","Share Payable","Father","Mother","Guardian","Spouse","Kid1","Kid2","Kid3","Kid4","Kid5"])
 for c in ws[5]: c.font=Font(bold=True,color="FFFFFF");c.fill=PatternFill("solid",fgColor="0F2A44");c.alignment=Alignment(horizontal="center")
 for i,x in enumerate(shares,1): ws.append([i,x["id"],x["staff_no"],x["full_names"],x["project"],x["month_joined"],x["months"],x["contribution"],round(x["share"],2),x["father_id"],x["mother_id"],x["guardian_id"],x["spouse_id"],x["kid1"],x["kid2"],x["kid3"],x["kid4"],x["kid5"]])
 ws.append([]);ws.append(["","","","","","","TOTAL",tc,round(sum(x["share"] for x in shares),2)]);ws.append(["","","","","","","RETAINED","",RESERVE]);ws.append(["","","","","","","BF","",round(sum(x["share"] for x in shares),2)+RESERVE]);ws.freeze_panes="A6";ws.auto_filter.ref=ws.dimensions
 for col,w in zip("ABCDEFGHIJKLMNOPQR",[6,6,14,30,22,14,10,14,16,20,20,20,20,20,20,20,20,20]): ws.column_dimensions[col].width=w
 out=io.BytesIO();wb.save(out);out.seek(0);return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
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
        import datetime as _dt
        c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, media_type, media_data) VALUES (?,?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M"), d.get("media_type") or "", d.get("media_data") or ""))
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
    import datetime as _dt
    c=get_db(); c.execute("INSERT INTO community_comments (post_id, author_name, author_email, msg, created) VALUES (?,?,?,?,?)", (pid, d.get("name") or "Member", d.get("email") or "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Reply posted"})
@app.route("/api/community/<int:pid>/repost", methods=["POST"])
def api_repost(pid):
    d=request.get_json(force=True) or {}
    import datetime as _dt
    c=get_db(); orig=c.execute("SELECT * FROM community_posts WHERE id=?", (pid,)).fetchone()
    if not orig: c.close(); return jsonify({"error": "Not found"}), 404
    c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, repost_of) VALUES (?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "Reposted", _dt.datetime.now().strftime("%d %b %Y %H:%M"), str(pid)))
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
        import datetime as _dt
        c.execute("INSERT INTO notifications (title, msg, created, target, is_read) VALUES (?,?,?,?,?)", (d.get("title") or "F.I.G", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M"), d.get("target") or "/", 0))
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
    import datetime as _dt
    c=get_db(); c.execute("INSERT INTO support_msgs (name, msg, created) VALUES (?,?,?)", (d.get("name") or "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Message sent. We will reply on WhatsApp 0707 780 807"})
@app.route("/download/excel")
def download_excel():
    shares, tc, tm, rate = calc_shares()
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title="Members"
    ws.append(["ID","Staff No","Full Names","Project","Email","Date Joined","Months","Contribution","Share","Father","Mother","Guardian","Spouse","Kid1","Kid2","Kid3","Kid4","Kid5"])
    for x in shares:
        ws.append([x["id"],x["staff_no"],x["full_names"],x["project"],x["email"],x["month_joined"],x["months"],x["contribution"],round(x["share"],2),x["father_id"],x["mother_id"],x["guardian_id"],x["spouse_id"],x["kid1"],x["kid2"],x["kid3"],x["kid4"],x["kid5"]])
    out=io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_Members.xlsx")
@app.route("/health")
def health(): return jsonify({"ok": True, "version": "v114"})
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
