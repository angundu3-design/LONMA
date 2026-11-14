from flask import Flask,request,jsonify,render_template_string,redirect,send_file
import sqlite3,os,secrets,io,re,datetime
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
DB="lonma.db"
PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PMAP={"Antonio":"Antonia","ANTONIA":"Antonia","Antonia":"Antonia","GCB-MT":"GCB-MT","GCB MT":"GCB-MT","GCB":"GCB-MT","GCB-Ws":"GCB-TDs","GCB Ws":"GCB-TDs","GCB TDS":"GCB-TDs","GCB-TDs":"GCB-TDs","GCB-TDS":"GCB-TDs","Higchem":"Higchem","HIGHCHEM":"Higchem","HIGCHEM MARKETING LIMITED":"Higchem","Hichem":"Higchem","Highchem":"Higchem","HQ":"HQ","Kanji":"Kanji","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","Java House":"Java House","JAVA":"Java House","Java":"Java House","Pwani Oil Products":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","SC Johnson":"SC Johnson","SJ Johnson":"SC Johnson","JOHNSON":"SC Johnson","Johnson":"SC Johnson","SJ":"SC Johnson","SCJohnson":"SC Johnson","Scjohnsons":"SC Johnson","scjohnsons":"SC Johnson","TF WSL":"TF WSL","TF WS":"TF WSL","TF-WS":"TF WSL","TF":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
def norm_project(p):
    p=(p or "").strip()
    if p in PMAP:
        return PMAP[p]
    up=" ".join(p.upper().split())
    if up in PMAP:
        return PMAP[up]
    return PMAP.get(p.title(),p or "Pwani Oil Products")
ADMIN_KEY=os.environ.get("ADMIN_KEY","lonma_api_key_12345").strip()
ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL","marlonkikuyu@gmail.com").strip().lower()
ADMIN_PASS=os.environ.get("ADMIN_PASS","admin123")
BF=855759
RESERVE=250000
DISTRIBUTABLE=BF-RESERVE
MONTHLY_RATE=300
PERIOD_START=(2025,12)
PERIOD_END=(2026,9)
SEED_TXT='''202731|Pwani Oil Products|2025|Angela Nyaguthii Gathege|Philip Gathege|Elizabeth Wanjiru||||||
202680|Pwani Oil Products|2016|Marlon Ang'undu Kikuyu|||1951498||6879175||||
'''
PERIODS=[{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200 | Kaysalt 72,900 | Kanji 12,600 | HQ 15,900 | GCB-MT 69,900 | TF-WS 71,100 | TF-LM 173,100 | TF-MT 259,500 | Kenafric 96,900 | GCB-TDs 51,000 | LAB 7,800"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400 | Kanji 9,900 | HQ 14,100 | GCB-MT 56,700 | TF-WS 49,200 | TF-LM 122,400 | TF-MT 236,100 | GCB-TDs 41,100 | Higchem 30,000 | Antonia 3,600"}]
SEED_DATA=[tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines() if l.strip()]
def clean(v):
    if v is None:
        return ""
    s=str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL","NIL"):
        return ""
    if "will give" in s.lower() or "will provide" in s.lower():
        return ""
    return s
def make_email(n,staff):
    p=[x for x in n.lower().replace(".","").split() if x.isalpha()]
    if len(p)>=2:
        return f"{p[0]}.{p[-1]}@figbrands.co.ke"
    return f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
def parse_join(s):
    if not s:
        return None
    s=str(s).strip().lower()
    months={"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,"january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
    m=re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})",s)
    if m:
        d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
        if mo>12:
            d,mo=mo,d
        return (y,mo)
    m=re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})",s)
    if m:
        return (int(m.group(2)),months[m.group(1)[:3]])
    m=re.search(r"(\d{4})",s)
    if m:
        return (int(m.group(1)),1)
    return None
def get_join_year(mj):
    p=parse_join(mj)
    return str(p[0]) if p else ""
def months_active(j):
    sy,sm=PERIOD_START
    ey,em=PERIOD_END
    p=parse_join(j)
    if p and (p[0],p[1])>(sy,sm):
        sy,sm=p
    if (sy,sm)>(ey,em):
        return 0
    return (ey-sy)*12+(em-sm)+1
def calc_shares(year_filter=""):
    c=get_db()
    try:
        rows=c.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users ORDER BY full_names").fetchall()
    finally:
        c.close()
    out=[]
    for r in rows:
        if year_filter and get_join_year(r["month_joined"])!=str(year_filter):
            continue
        mo=months_active(r["month_joined"])
        kids=[r[f"kid{i}"] or "" for i in range(1,6)]
        kids=[k for k in kids if k and k.strip()]
        out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","join_year":get_join_year(r["month_joined"]),"months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0,"father_id":r["father_id"] or "","mother_id":r["mother_id"] or "","guardian_id":r["guardian_id"] or "","spouse_id":r["spouse_id"] or "","kids":kids,"kid1":r["kid1"] or "","kid2":r["kid2"] or "","kid3":r["kid3"] or "","kid4":r["kid4"] or "","kid5":r["kid5"] or ""})
    tm=sum(x["months"] for x in out)
    tc=sum(x["contribution"] for x in out)
    rate=DISTRIBUTABLE/tm if tm else 0
    for x in out:
        x["per_month"]=round(rate,2)
        x["share"]=round(x["months"]*rate,2)
    diff=round(DISTRIBUTABLE-sum(x["share"] for x in out),2)
    if out and diff!=0:
        out.sort(key=lambda x:x["share"],reverse=True)
        out[0]["share"]=round(out[0]["share"]+diff,2)
    out.sort(key=lambda x:x["share"],reverse=True)
    return out,tc,tm,rate
def get_db():
    c=sqlite3.connect(DB,timeout=10,check_same_thread=False,isolation_level=None)
    c.row_factory=sqlite3.Row
    try:
        c.execute("PRAGMA journal_mode=WAL;")
        c.execute("PRAGMA busy_timeout=10000;")
    except:
        pass
    return c
def add_user(c,staff,names,project,month,father="",mother="",guardian="",spouse="",k1="",k2="",k3="",k4="",k5="",photo=""):
    staff=clean(staff)
    names=clean(names)
    project=norm_project(project)
    if not staff or not names:
        return False
    if c.execute("SELECT id FROM users WHERE staff_no=?",(staff,)).fetchone():
        return False
    if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(names,)).fetchone():
        return False
    email=make_email(names,staff)
    if c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone():
        email=f"member.{staff}@figbrands.co.ke"
    c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(staff,names,project,email,generate_password_hash(staff),"fig_"+secrets.token_hex(12),clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),photo))
    return True
def init_db():
    c=get_db()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT, target TEXT, is_read INTEGER DEFAULT 0)')
    c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS community_posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author_name TEXT, author_email TEXT, project TEXT, msg TEXT, created TEXT, media_type TEXT, media_data TEXT, repost_of TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS community_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author_name TEXT, author_email TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS community_likes (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, email TEXT, UNIQUE(post_id,email))')
    c.execute('CREATE TABLE IF NOT EXISTS community_bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, email TEXT, UNIQUE(post_id,email))')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try:
            c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except:
            pass
    for col in ["media_type","media_data","repost_of"]:
        try:
            c.execute(f"ALTER TABLE community_posts ADD COLUMN {col} TEXT")
        except:
            pass
    for r in c.execute("SELECT id, project FROM users").fetchall():
        np=norm_project(r["project"])
        if np!=r["project"]:
            c.execute("UPDATE users SET project=? WHERE id=?",(np,r["id"]))
    admin=c.execute("SELECT id FROM users WHERE email=?",(ADMIN_EMAIL,)).fetchone()
    if not admin:
        marlon=c.execute("SELECT id FROM users WHERE staff_no=?",("202680",)).fetchone()
        if marlon:
            c.execute("UPDATE users SET email=?, password=?, role=?, api_key=?, is_protected=1 WHERE id=?",(ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin",ADMIN_KEY,marlon["id"]))
        else:
            c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)",("202680","Marlon Ang'undu Kikuyu","Pwani Oil Products",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0707780807",ADMIN_KEY,1))
    else:
        c.execute("UPDATE users SET role=?, api_key=?, is_protected=1, password=? WHERE email=?",("Admin",ADMIN_KEY,generate_password_hash(ADMIN_PASS),ADMIN_EMAIL))
    c.execute("DELETE FROM users WHERE email=? AND email != ?",("admin@lonma.com",ADMIN_EMAIL))
    added=0
    for r in SEED_DATA:
        staff,proj_raw,month,names,father,mother,guardian,spouse,k1,k2,k3,k4,k5=r
        project=norm_project(proj_raw)
        ex=c.execute("SELECT id FROM users WHERE staff_no=?",(clean(staff),)).fetchone()
        if ex:
            c.execute("UPDATE users SET full_names=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE staff_no=?",(clean(names),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),clean(staff)))
            continue
        ex2=c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(clean(names),)).fetchone()
        if ex2:
            c.execute("UPDATE users SET staff_no=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE id=?",(clean(staff),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),ex2["id"]))
            continue
        if add_user(c,staff,names,project,month,father,mother,guardian,spouse,k1,k2,k3,k4,k5):
            added+=1
    c.commit()
    c.close()
    print(f"v115 seeded {added}")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
    return r
@app.route("/favicon.ico")
def favicon():
    return '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="12" fill="#0F2A44"/><text x="32" y="42" font-family="Georgia, serif" font-size="20" font-weight="700" fill="#FFFFFF" text-anchor="middle">FIG</text></svg>',200,{"Content-Type":"image/svg+xml"}
YEAR_BAR='''
<div style="background:#fff;border-bottom:1px solid #E5E7EB;padding:10px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
<label style="font-weight:700;font-size:13px;color:#0F2A44">Filter Year:</label>
<select id="yearFilter" onchange="onYearChange()" style="height:42px;border:1px solid #D1D5DB;border-radius:10px;padding:0 10px;min-width:130px;font-size:14px">
<option value="">All Years - All 240</option>
<option value="2011">2011</option><option value="2013">2013</option><option value="2014">2014</option>
<option value="2015">2015</option><option value="2016">2016</option><option value="2017">2017</option>
<option value="2019">2019</option><option value="2020">2020</option><option value="2021">2021</option>
<option value="2022">2022</option><option value="2023">2023</option><option value="2024">2024</option>
<option value="2025">2025</option><option value="2026">2026</option>
</select>
<button onclick="clearYear()" style="height:42px;background:#6B7280;color:#fff;border:0;border-radius:10px;padding:0 14px;font-weight:600">Clear / All</button>
<span id="yearLabel" style="font-weight:700;color:#0F2A44;font-size:13px"></span>
</div>
<script>
function getYear(){return localStorage.getItem('lonma_year') || '';}
function setYearUI(){var y=getYear();var el=document.getElementById('yearFilter');if(el)el.value=y;var lab=document.getElementById('yearLabel');if(lab)lab.innerText=y?'Showing: '+y:'Showing: All Years';}
function onYearChange(){localStorage.setItem('lonma_year',document.getElementById('yearFilter').value);setYearUI();location.reload();}
function clearYear(){localStorage.setItem('lonma_year','');setYearUI();location.reload();}
function yearQuery(){var y=getYear();return y?'?year='+y:'';}
function getEmail(){return localStorage.getItem('fig_email')||'guest@figbrands.co.ke';}
function getName(){return localStorage.getItem('fig_name')||'Member';}
setYearUI();
</script>
'''
def shell(title,body):
    full=YEAR_BAR+body
    return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;700&display=swap" rel="stylesheet"><script>if(!localStorage.getItem('fig_user')&&location.pathname!='/login'&&location.pathname!='/register'){location.href='/login'}</script><style>body{font-family:Inter,sans-serif;background:#F8F9FA;margin:0;padding-bottom:80px;color:#111827}.card{background:#fff;border:1px solid #E5E7EB;border-radius:20px;padding:20px;margin-bottom:14px}.input{width:100%;height:48px;border:1px solid #D1D5DB;border-radius:12px;padding:0 14px;box-sizing:border-box}.btn-dark{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#0F2A44;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px;border:0}.btn-gold{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#C9A86A;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px;border:0}.top{height:64px;background:#fff;display:flex;align-items:center;gap:12px;padding:0 14px;position:sticky;top:0;z-index:20;border-bottom:1px solid #E5E7EB}.logo{width:52px;height:52px;border-radius:14px;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}.toplinks{background:#fff;border-bottom:1px solid #E5E7EB;padding:10px 14px;display:flex;gap:24px;overflow-x:auto;white-space:nowrap;position:sticky;top:64px;z-index:15;flex-wrap:wrap}.toplinks a{color:#111827;text-decoration:none;font-size:15px;font-weight:600}.page{max-width:1080px;margin:auto;padding:18px 14px 180px}.dark{background:#0F2A44;color:#fff;border-radius:20px;padding:22px;margin-bottom:14px}.gold{color:#C9A86A;letter-spacing:2px;font-size:12px;font-weight:700}h1,h2{font-family:Fraunces,Georgia,serif}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid #F3F4F6;text-align:left}.nav{position:fixed;left:10px;right:10px;bottom:8px;height:60px;background:#fff;border:1px solid #E5E7EB;border-radius:24px;display:flex;z-index:30;box-shadow:0 4px 20px rgba(0,0,0,.08)}.nav a{flex:1;color:#6B7280;text-decoration:none;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600}.xbtn{border:0;background:#F3F4F6;border-radius:999px;padding:8px 12px;font-size:13px;cursor:pointer}.xbtn.liked{background:#FEE2E2;color:#DC2626}.xbtn.saved{background:#FEF3C7;color:#92400E}.avatar{width:40px;height:40px;border-radius:50%;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0}</style></head><body><div class="top"><div class="logo">FIG</div><div><b style="font-size:17px;letter-spacing:.5px">F.I.G BRANDS</b><div style="color:#6B7280;letter-spacing:2px;font-size:11px">WELFARE SYSTEM</div></div><div style="margin-left:auto;display:flex;gap:8px;align-items:center"><span style="width:38px;height:38px;border-radius:50%;background:#F3F4F6;display:flex;align-items:center;justify-content:center">◐</span><span style="width:38px;height:38px;border-radius:50%;background:#F3F4F6;display:flex;align-items:center;justify-content:center">○</span><span style="width:38px;height:38px;border-radius:50%;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700">MA</span></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/community">Community</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/terms">Terms &amp; Policies</a><a href="/admin">Admin</a></div><div class="page">'''+full+'''</div><nav class="nav"><a href="/">Home</a><a href="/members">Members</a><a href="/community">Community</a><a href="/shareout">Share-Out</a><a href="/terms">Terms</a><a href="/register">Add</a></nav></body></html>''')
@app.route("/")
def index():
    body='''<div class="card"><div class="gold">WELFARE CLAUSES 2026</div><h1 style="font-size:34px;line-height:1.2">Death Benefit: Member 100,000 &middot; Spouse 50,000 &middot; Child 40,000 &middot; Parents 40,000</h1><p style="color:#4B5563;line-height:1.6">Loss of Earning: 50% of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn-dark" href="/terms">Read Full Terms</a><a class="btn-gold" href="/community">Join Community Chat</a></div></div><div class="card"><div class="gold">DISTRIBUTION</div><h2 style="font-size:30px;margin:8px 0">Project Distribution <span id="bdYear" style="font-size:16px"></span></h2><div id="breakdown"></div><div style="margin-top:14px">Total Members: <b id="total">0</b></div></div><script>async function load(){let q=yearQuery();let r=await fetch('/api/stats'+q);let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('bdYear').textContent=getYear()? '('+getYear()+')':'(All Years)';let h='';Object.keys(d.projects_breakdown).sort((a,b)=>d.projects_breakdown[b]-d.projects_breakdown[a]).forEach(k=>{h+='<div style="display:flex;justify-content:space-between;padding:14px 0;border-bottom:1px solid #eee"><span style="font-size:18px;font-weight:600">'+k+'</span><b style="font-size:18px">'+d.projects_breakdown[k]+'</b></div>'});document.getElementById('breakdown').innerHTML=h;}load();</script>'''
    return shell("Overview",body)
@app.route("/members")
def members_page():
    body='''<h1>Members <span id="mYear" style="font-size:18px"></span></h1><p>Total: <b id="mTotal">0</b> members</p><input class="input" id="search" placeholder="Search name / staff no / project..." oninput="filterM()"><div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0" id="projChips"></div><div class="card"><div id="list">Loading...</div></div><script>let ALL=[];let CUR='All';async function load(){let q=yearQuery();document.getElementById('mYear').textContent=getYear()? '('+getYear()+')':'(All 240)';let r=await fetch('/api/members'+q);ALL=await r.json();document.getElementById('mTotal').textContent=ALL.length;let chips='<button class="xbtn" onclick="setProj(\\'All\\')">All</button>';['Antonia','GCB-MT','GCB-TDs','Higchem','HQ','Java House','Kanji','Pwani Oil Products','SC Johnson','TF WSL','TF-LM','TF-MT'].forEach(p=>{chips+='<button class="xbtn" onclick="setProj(\\''+p+'\\')">'+p+'</button>'});document.getElementById('projChips').innerHTML=chips;render();}function setProj(p){CUR=p;render();}function render(){let q=(document.getElementById('search').value||'').toLowerCase();let f=ALL.filter(x=>(CUR=='All'||x.project==CUR)&&(x.full_names+' '+x.staff_no+' '+x.project).toLowerCase().includes(q));let h='<table><tr><th>Staff</th><th>Name</th><th>Project</th><th>Joined</th><th>Year</th><th>Months</th><th>Share</th></tr>';f.forEach(x=>{h+='<tr><td>'+x.staff_no+'</td><td><b>'+x.full_names+'</b></td><td>'+x.project+'</td><td>'+x.month_joined+'</td><td>'+x.join_year+'</td><td>'+x.months+'</td><td>KES '+x.share.toLocaleString()+'</td></tr>'});h+='</table><p>'+f.length+' members shown - '+CUR+'</p>';document.getElementById('list').innerHTML=h;}function filterM(){render();}load();</script>'''
    return shell("Members",body)
@app.route("/shareout")
def shareout_page():
    body='''<h1>Share-Out <span id="sYear" style="font-size:18px"></span></h1><div class="dark"><div>Total to Share: <b>KES 605,759</b></div><div style="opacity:.8">KES 250,000 retained - 240 members</div></div><div class="card"><div id="share">Loading...</div></div><script>async function load(){let q=yearQuery();document.getElementById('sYear').textContent=getYear()? '('+getYear()+')':'(All 240)';let r=await fetch('/api/shareout'+q);let d=await r.json();document.getElementById('share').innerHTML='Members: '+d.total_members+'<br>Total Months: '+d.total_months+'<br>Per Month: KES '+d.per_month_rate.toFixed(2)+'<br>Year: '+(d.year||'All');}load();</script>'''
    return shell("Share-Out",body)
@app.route("/breakdown2")
def breakdown2_page():
    h="<h1>Full History</h1>"
    for p in PERIODS:
        h+=f"<div class='card'><h3>{p['label']}</h3><div>Contributions: <b>KES {p.get('total',0):,}</b></div><div>Beneficiaries: <b>KES {p.get('beneficiaries',0):,}</b></div><div>Fares: <b>KES {p.get('fares',0):,}</b></div><p>{p.get('detail','')}</p></div>"
    return shell("History",h)
@app.route("/terms")
def terms_page():
    return shell("Terms","<div class='card'><div class='gold'>WELFARE CLAUSES 2026</div><h1>Terms & Policies</h1><p>Member KES 100,000 | Spouse KES 50,000 | Child KES 40,000 | Parents KES 40,000</p><p>Contribution: KES 300 monthly</p><p>Loss of Earning: 50% of basic pay up to KES 20,000 after 10 days unable to work due to injury at work.</p></div>")
@app.route("/community")
def community_page():
    body='''<h1 style="font-size:32px">Community <span style="font-size:14px;background:#0F2A44;color:#fff;padding:4px 10px;border-radius:999px">Twitter-like</span></h1><div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"><button class="xbtn" onclick="setFeed('all')">All Posts</button><button class="xbtn" onclick="setFeed('liked')">❤️ My Likes</button><button class="xbtn" onclick="setFeed('saved')">🔖 Saved</button><input id="comSearch" class="input" style="flex:1;min-width:160px" placeholder="Search posts..." oninput="loadCom()"><select id="comProj" class="input" style="width:140px" onchange="loadCom()"><option value="">All Projects</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option></select></div><div class="card"><div style="display:flex;gap:12px"><div class="avatar" id="myAvatar">M</div><div style="flex:1"><textarea id="comMsg" class="input" style="height:80px;padding:12px;border:0;border-bottom:1px solid #eee;border-radius:0" placeholder="What is happening?"></textarea><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><span style="color:#6B7280;font-size:13px">Posting as <b id="myName">Member</b></span><button class="btn-dark" onclick="postMsg()">Post</button></div><p id="comStatus"></p></div></div></div><div id="comFeed">Loading...</div><script>let FEED='all';document.getElementById('myName').textContent=getName();document.getElementById('myAvatar').textContent=getName().charAt(0);function setFeed(f){FEED=f;loadCom();}async function loadCom(){let r=await fetch('/api/community?email='+encodeURIComponent(getEmail())+'&feed='+FEED+'&search='+encodeURIComponent(document.getElementById('comSearch').value||'')+'&project='+encodeURIComponent(document.getElementById('comProj').value||''));let d=await r.json();let h='';(d.posts||[]).forEach(p=>{let init=p.author_name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();let com='';(p.comments||[]).forEach(cm=>{com+='<div style="display:flex;gap:8px;padding:8px 0;border-top:1px solid #f3f4f6"><div class="avatar" style="width:28px;height:28px;font-size:11px">'+cm.author_name.charAt(0)+'</div><div><b>'+cm.author_name+'</b> <span style="color:#888;font-size:12px">'+cm.created+'</span><div>'+cm.msg+'</div></div></div>'});h+='<div class="card"><div style="display:flex;gap:12px"><div class="avatar">'+init+'</div><div style="flex:1;min-width:0"><div style="display:flex;gap:8px;flex-wrap:wrap"><b>'+p.author_name+'</b><span style="color:#6B7280">@'+p.author_email.split('@')[0]+' - '+p.project+' - '+p.created+'</span></div>'+(p.repost_of?'<div style="background:#F9FAFB;border-radius:12px;padding:10px;margin:8px 0;color:#4B5563;font-size:13px">🔁 Reposted: '+p.repost_of+'</div>':'')+'<div style="font-size:15px;line-height:1.5;margin:6px 0">'+p.msg+'</div><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px"><button class="xbtn '+(p.liked?'liked':'')+'" onclick="act('+p.id+',\\'like\\')">❤️ '+p.likes+'</button><button class="xbtn" onclick="toggleCom('+p.id+')">💬 '+(p.comments?p.comments.length:0)+'</button><button class="xbtn" onclick="act('+p.id+',\\'repost\\')">🔁 '+p.reposts+'</button><button class="xbtn '+(p.saved?'saved':'')+'" onclick="act('+p.id+',\\'bookmark\\')">🔖 '+(p.saved?'Saved':'Save')+'</button><button class="xbtn" onclick="delPost('+p.id+')">🗑️</button></div><div id="comBox'+p.id+'" style="display:none;margin-top:10px"><input id="comIn'+p.id+'" class="input" placeholder="Write a reply..."><button class="btn-dark" style="margin-top:8px" onclick="sendComment('+p.id+')">Reply</button></div><div id="comList'+p.id+'">'+com+'</div></div></div></div>'});document.getElementById('comFeed').innerHTML=h||'No posts yet - be the first to post!';}function toggleCom(id){let el=document.getElementById('comBox'+id);el.style.display=el.style.display=='none'?'block':'none';}async function act(id,action){await fetch('/api/community/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id})});loadCom();}async function sendComment(id){let m=document.getElementById('comIn'+id).value;if(!m)return;await fetch('/api/community/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id,msg:m})});loadCom();}async function postMsg(){let m=document.getElementById('comMsg').value;if(!m)return alert('Write something');await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:getName(),email:getEmail(),msg:m,project:localStorage.getItem('fig_project')||'HQ'})});document.getElementById('comMsg').value='';document.getElementById('comStatus').textContent='Posted!';loadCom();}async function delPost(id){if(!confirm('Delete this post?'))return;await fetch('/api/community/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id,email:getEmail()})});loadCom();}loadCom();</script>'''
    return shell("Community",body)
@app.route("/login")
def login_page():
    return shell("Login","<h1>Login</h1><input class='input' id='em' placeholder='Email'><input class='input' id='pw' type='password' placeholder='Password' style='margin-top:10px'><button class='btn-dark' style='margin-top:10px' onclick='doLogin()'>Login</button><script>async function doLogin(){let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('em').value,password:document.getElementById('pw').value})});let d=await r.json();if(d.ok){localStorage.setItem('fig_user',d.user.email);localStorage.setItem('fig_role',d.user.role);localStorage.setItem('fig_name',d.user.full_names);localStorage.setItem('fig_email',d.user.email);localStorage.setItem('fig_project',d.user.project);location.href='/';}else alert(d.error);}</script>")
@app.route("/register")
def register_page():
    return shell("Register","<h1>Register Member</h1><p>Admin only.</p>")
@app.route("/admin")
def admin_page():
    return shell("Admin","<h1>Admin</h1><p>Manage members.</p>")
@app.route("/api/stats")
def api_stats():
    year=request.args.get("year","")
    c=get_db()
    rows=c.execute("SELECT project, month_joined FROM users").fetchall()
    c.close()
    if year:
        rows=[r for r in rows if get_join_year(r["month_joined"])==str(year)]
    from collections import Counter
    bc=dict(Counter([norm_project(r["project"]) for r in rows]))
    return jsonify({"total_members":len(rows),"projects_total":len(bc),"projects_breakdown":bc,"year":year,"projects":PROJECTS})
@app.route("/api/members")
def api_members():
    year=request.args.get("year","")
    out,tc,tm,rate=calc_shares(year_filter=year)
    return jsonify(out)
@app.route("/api/shareout")
def api_shareout():
    year=request.args.get("year","")
    out,tc,tm,rate=calc_shares(year_filter=year)
    return jsonify({"total_members":len(out),"total_months":tm,"total_contribution":tc,"per_month_rate":rate,"distributable":DISTRIBUTABLE,"year":year,"members":out})
@app.route("/api/years")
def api_years():
    c=get_db()
    rows=c.execute("SELECT DISTINCT month_joined FROM users").fetchall()
    c.close()
    ys=sorted(set([get_join_year(r["month_joined"]) for r in rows if get_join_year(r["month_joined"])]))
    return jsonify(ys)
def community_posts(email,feed,search,project):
    c=get_db()
    rows=c.execute("SELECT * FROM community_posts ORDER BY id DESC LIMIT 200").fetchall()
    out=[]
    for p in rows:
        likes=c.execute("SELECT COUNT(*) FROM community_likes WHERE post_id=?",(p["id"],)).fetchone()[0]
        liked=c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?",(p["id"],email)).fetchone() is not None
        saved=c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?",(p["id"],email)).fetchone() is not None
        reposts=c.execute("SELECT COUNT(*) FROM community_posts WHERE repost_of=?",(str(p["id"]),)).fetchone()[0]
        comments=[dict(x) for x in c.execute("SELECT * FROM community_comments WHERE post_id=? ORDER BY id ASC",(p["id"],)).fetchall()]
        item={"id":p["id"],"author_name":p["author_name"],"author_email":p["author_email"],"project":p["project"],"msg":p["msg"],"created":p["created"],"likes":likes,"liked":liked,"saved":saved,"reposts":reposts,"comments":comments,"repost_of":p["repost_of"] or ""}
        if project and item["project"]!=project:
            continue
        if search and search.lower() not in (item["msg"]+item["author_name"]+item["project"]).lower():
            continue
        if feed=="liked" and not liked:
            continue
        if feed=="saved" and not saved:
            continue
        out.append(item)
    c.close()
    return out
@app.route("/api/community", methods=["GET","POST"])
def api_community():
    c=get_db()
    if request.method=="POST":
        d=request.get_json(silent=True) or {}
        c.execute("INSERT INTO community_posts (author_name,author_email,project,msg,created) VALUES (?,?,?,?,?)",(d.get("name","Member"),d.get("email",""),d.get("project","HQ"),d.get("msg",""),str(datetime.datetime.now())[:19]))
        c.commit()
        c.close()
        return jsonify({"message":"Posted"}),201
    email=request.args.get("email","")
    feed=request.args.get("feed","all")
    search=request.args.get("search","")
    project=request.args.get("project","")
    return jsonify({"posts":community_posts(email,feed,search,project)})
@app.route("/api/community/like", methods=["POST"])
def api_like():
    d=request.get_json(silent=True) or {}
    c=get_db()
    ex=c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?",(d.get("post_id"),d.get("email"))).fetchone()
    if ex:
        c.execute("DELETE FROM community_likes WHERE id=?",(ex["id"],))
    else:
        c.execute("INSERT INTO community_likes (post_id,email) VALUES (?,?)",(d.get("post_id"),d.get("email")))
    c.commit()
    c.close()
    return jsonify({"ok":True})
@app.route("/api/community/bookmark", methods=["POST"])
def api_bookmark():
    d=request.get_json(silent=True) or {}
    c=get_db()
    ex=c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?",(d.get("post_id"),d.get("email"))).fetchone()
    if ex:
        c.execute("DELETE FROM community_bookmarks WHERE id=?",(ex["id"],))
    else:
        c.execute("INSERT INTO community_bookmarks (post_id,email) VALUES (?,?)",(d.get("post_id"),d.get("email")))
    c.commit()
    c.close()
    return jsonify({"ok":True})
@app.route("/api/community/repost", methods=["POST"])
def api_repost():
    d=request.get_json(silent=True) or {}
    c=get_db()
    orig=c.execute("SELECT * FROM community_posts WHERE id=?",(d.get("post_id"),)).fetchone()
    if not orig:
        c.close()
        return jsonify({"error":"Not found"}),404
    c.execute("INSERT INTO community_posts (author_name,author_email,project,msg,created,repost_of) VALUES (?,?,?,?,?,?)",(d.get("name","Member"),d.get("email",""),orig["project"],"Reposted: "+(orig["msg"] or "")[:200],str(datetime.datetime.now())[:19],str(orig["id"])))
    c.commit()
    c.close()
    return jsonify({"ok":True})
@app.route("/api/community/comment", methods=["POST"])
def api_comment():
    d=request.get_json(silent=True) or {}
    c=get_db()
    c.execute("INSERT INTO community_comments (post_id,author_name,author_email,msg,created) VALUES (?,?,?,?,?)",(d.get("post_id"),d.get("name","Member"),d.get("email",""),d.get("msg",""),str(datetime.datetime.now())[:19]))
    c.commit()
    c.close()
    return jsonify({"ok":True})
@app.route("/api/community/delete", methods=["POST"])
def api_delete_post():
    d=request.get_json(silent=True) or {}
    c=get_db()
    c.execute("DELETE FROM community_posts WHERE id=?",(d.get("post_id"),))
    c.execute("DELETE FROM community_comments WHERE post_id=?",(d.get("post_id"),))
    c.execute("DELETE FROM community_likes WHERE post_id=?",(d.get("post_id"),))
    c.execute("DELETE FROM community_bookmarks WHERE post_id=?",(d.get("post_id"),))
    c.commit()
    c.close()
    return jsonify({"ok":True})
@app.route("/api/notifications")
def api_notif():
    c=get_db()
    rows=c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
    c.close()
    return jsonify({"notifications":[dict(r) for r in rows],"unread":0})
@app.route("/api/login", methods=["POST"])
def api_login():
    d=request.get_json(silent=True) or {}
    c=get_db()
    u=c.execute("SELECT * FROM users WHERE lower(email)=lower(?)",(d.get("email","").strip(),)).fetchone()
    c.close()
    if not u:
        return jsonify({"ok":False,"error":"User not found"}),404
    if not check_password_hash(u["password"] or "", d.get("password","")):
        if d.get("password","") != (u["staff_no"] or ""):
            return jsonify({"ok":False,"error":"Wrong password"}),401
    return jsonify({"ok":True,"user":{"email":u["email"],"full_names":u["full_names"],"role":u["role"] or "Member","project":u["project"]}})
@app.route("/download/excel")
def download_excel():
    from openpyxl import Workbook
    shares,tc,tm,rate=calc_shares()
    wb=Workbook()
    ws=wb.active
    ws.title="Members"
    ws.append(["ID","Staff No","Full Names","Project","Email","Date Joined","Months","Contribution","Share"])
    for x in shares:
        ws.append([x["id"],x["staff_no"],x["full_names"],x["project"],x["email"],x["month_joined"],x["months"],x["contribution"],x["share"]])
    out=io.BytesIO()
    wb.save(out)
    out.seek(0)
    return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="lonma_members.xlsx")
@app.route("/api/support", methods=["POST"])
def api_support():
    d=request.get_json(force=True) or {}
    c=get_db()
    c.execute("INSERT INTO support_msgs (name, msg, created) VALUES (?,?,?)",(d.get("name") or "",d.get("msg") or "",str(datetime.datetime.now())))
    c.commit()
    c.close()
    return jsonify({"message":"Message sent. We will reply on WhatsApp 0707 780 807"})
@app.route("/health")
def health():
    return jsonify({"status":"ok"}),200
@app.errorhandler(404)
def nf(e):
    if request.path.startswith("/api/"):
        return jsonify({"error":"Not found"}),404
    return redirect("/")
if __name__=="__main__":
    port=int(os.environ.get("PORT",10000))
    app.run(host="0.0.0.0",port=port)
