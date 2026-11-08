from flask import Flask, request, jsonify, render_template_string, redirect
import sqlite3, os, secrets
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem"]
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"

def get_db():
    conn = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    conn.row_factory = sqlite3.Row
    try:
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return conn

def init_db():
    conn = get_db()
    conn.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)')
    conn.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    if not conn.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    if not conn.execute("SELECT id FROM notifications").fetchone():
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Welcome to LONMA","Your welfare system is active. HQ 0 - ready to register members.","Now"))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Photo Feature Added","You can now add a photo for each member in Register.","Now"))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("System Update","Pricelist, Products, Live Location & Off Site Order removed.","Now"))
    conn.commit(); conn.close()
init_db()

@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*')
    r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
    r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
    return r

BASE = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');
*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',sans-serif;background:#f1f5f9;color:#0f172a}
.app-header{height:64px;background:#1565c0;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 16px;position:sticky;top:0;z-index:30}
.app-header .left{display:flex;align-items:center;gap:14px}
.menu-btn{width:40px;height:40px;border-radius:10px;background:rgba(255,255,255,.15);border:none;color:#fff;font-size:22px;display:flex;align-items:center;justify-content:center;cursor:pointer}
.brand-top{display:flex;align-items:center;gap:10px}
.brand-icon{width:36px;height:36px;background:#fff;color:#1565c0;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:800}
.brand-name{font-weight:800;font-size:14px;line-height:1.1}.brand-name span{font-size:10px;font-weight:600;display:block;opacity:.9}
.header-icons{display:flex;gap:12px;position:relative}.h-icon{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;font-size:18px;cursor:pointer;position:relative}
.h-icon:active{background:rgba(255,255,255,.35)}
.badge{position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;font-size:10px;font-weight:800;min-width:18px;height:18px;border-radius:999px;display:flex;align-items:center;justify-content:center;padding:0 4px;border:2px solid #1565c0}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:40;display:none}.overlay.show{display:block}
.sidebar{position:fixed;top:0;left:0;width:300px;height:100%;background:#fff;z-index:50;transform:translateX(-100%);transition:transform .3s ease;overflow:hidden;display:flex;flex-direction:column;border-radius:0 20px 20px 0;box-shadow:4px 0 24px rgba(0,0,0,.15)}
.sidebar.open{transform:translateX(0)}
.sidebar-top{background:#1e88e5;color:#fff;padding:24px 20px 18px 20px}
.avatar{width:72px;height:72px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden;border:3px solid rgba(255,255,255,.4)}
.avatar img{width:100%;height:100%;object-fit:cover}
.profile-name{font-size:16px;font-weight:700;margin-top:14px;letter-spacing:-0.2px;text-transform:uppercase}
.profile-email{font-size:13px;margin-top:4px;opacity:.9;font-weight:400;word-break:break-all}
.menu-list{flex:1;overflow:auto;padding:12px 0}
.menu-item{display:flex;align-items:center;gap:16px;padding:15px 22px;font-size:15px;font-weight:600;color:#0f172a;cursor:pointer;text-decoration:none;transition:background .15s}
.menu-item:hover{background:#f1f5f9}
.menu-item .icon{width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:20px}
.menu-item.active{background:#e3f2fd;color:#1565c0}
.sidebar-bottom{padding:14px 20px;border-top:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:11px;color:#94a3b8;font-weight:600}
.page{max-width:800px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:16px;border:1px solid #e2e8f0;box-shadow:0 1px 2px rgba(0,0,0,.04);overflow:hidden;margin-bottom:12px}
.card-header{padding:20px 22px;border-bottom:1px solid #f1f5f9}
.card-title{font-weight:800;font-size:16px}
.card-sub{font-size:12px;color:#64748b;margin-top:4px}
.card-body{padding:22px}
.input{width:100%;height:46px;border:1px solid #e2e8f0;border-radius:12px;padding:0 14px;font-size:14px;outline:none;transition:all .15s}
.input:focus{border-color:#1e88e5;box-shadow:0 0 0 3px rgba(30,136,229,.12)}
.label{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.6px;margin-bottom:7px;display:block}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.section{display:flex;align-items:center;gap:10px;margin:22px 0 14px 0}
.section-num{width:22px;height:22px;background:#0f172a;color:#fff;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800}
.section-label{font-size:11.5px;font-weight:800;text-transform:uppercase;letter-spacing:.6px}
.btn-primary{width:100%;height:50px;background:#0f172a;color:#fff;border:none;border-radius:12px;font-weight:700;font-size:14px;cursor:pointer;margin-top:10px}
.stat-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px}
.stat{background:#fff;border-radius:16px;padding:18px;border:1px solid #e2e8f0}
.stat-l{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px}
.stat-v{font-size:26px;font-weight:800;margin-top:4px}
.photo-box{width:110px;height:110px;border-radius:50%;border:3px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#f8fafc;cursor:pointer;position:relative}
.photo-box img{width:100%;height:100%;object-fit:cover}
.photo-box.has-photo{border-style:solid;border-color:#1e88e5}
.photo-upload-text{font-size:11px;color:#64748b;font-weight:600;text-align:center}
/* POPUPS */
.popup{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:100;display:none;align-items:flex-end;justify-content:center}
.popup.show{display:flex}
.popup-card{background:#fff;width:100%;max-width:520px;border-radius:22px 22px 0 0;max-height:82vh;overflow:auto;padding-bottom:20px;animation:slideUp .25s ease}
@keyframes slideUp{from{transform:translateY(40px);opacity:0}to{transform:translateY(0);opacity:1}}
.popup-head{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #f1f5f9;position:sticky;top:0;background:#fff}
.notif-item{padding:16px 20px;border-bottom:1px solid #f8fafc;display:flex;gap:12px}
.notif-dot{width:10px;height:10px;background:#1565c0;border-radius:50%;margin-top:6px;flex-shrink:0}
.support-opt{display:flex;gap:14px;align-items:center;padding:16px;border:1px solid #e2e8f0;border-radius:14px;margin-bottom:10px;cursor:pointer}
@media(max-width:600px){.stat-grid{grid-template-columns:1fr 1fr}.grid2,.grid3{grid-template-columns:1fr}}
</style>
<div class="app-header">
<div class="left"><button class="menu-btn" onclick="openMenu()">☰</button><div class="brand-top"><div class="brand-icon">L</div><div class="brand-name">LONMA<span>WELFARE SYSTEM</span></div></div></div>
<div class="header-icons"><div class="h-icon" onclick="openBell()">🔔<span class="badge" id="bellBadge">3</span></div><div class="h-icon" onclick="openSupport()">🎧</div></div>
</div>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="sidebar" id="sidebar">
<div class="sidebar-top">
<div class="avatar"><img src="https://i.pravatar.cc/150?img=3"></div>
<div class="profile-name">LONMA ADMIN</div>
<div class="profile-email">admin@lonma.com</div>
</div>
<div class="menu-list">
<a class="menu-item" href="/"><span class="icon">📊</span> Overview</a>
<a class="menu-item" href="/members"><span class="icon">👥</span> Members</a>
<a class="menu-item" href="/register"><span class="icon">➕</span> Register Member</a>
<div style="height:1px;background:#f1f5f9;margin:8px 20px"></div>
<a class="menu-item" href="#" onclick="openBell();return false"><span class="icon">🔔</span> Notifications</a>
<a class="menu-item" href="#" onclick="openSupport();return false"><span class="icon">🎧</span> Contact Support</a>
<a class="menu-item" href="#"><span class="icon">🔄</span> Syncing</a>
<a class="menu-item" href="#"><span class="icon">💬</span> Give Feedback</a>
<a class="menu-item" href="/admin"><span class="icon">⚙️</span> Settings</a>
<a class="menu-item" href="/admin" style="color:#dc2626"><span class="icon">⏻</span> Log Out</a>
</div>
<div class="sidebar-bottom"><span>LONMA WELFARE</span><span>v4.33.0 (patch 1)</span></div>
</div>

<!-- BELL POPUP -->
<div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()">
<div class="popup-card">
<div class="popup-head"><div><div style="font-weight:800;font-size:17px">🔔 Notifications</div><div style="font-size:12px;color:#64748b" id="notifCount">3 new</div></div><button onclick="closeBell()" style="width:32px;height:32px;border-radius:50%;border:none;background:#f1f5f9;font-size:18px;cursor:pointer">✕</button></div>
<div id="notifList"><div style="padding:30px;text-align:center;color:#64748b">Loading...</div></div>
<div style="padding:0 20px"><button onclick="markRead()" style="width:100%;height:44px;border-radius:12px;border:1px solid #e2e8f0;background:#fff;font-weight:700;cursor:pointer">Mark all as read</button></div>
</div>
</div>

<!-- SUPPORT POPUP -->
<div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()">
<div class="popup-card">
<div class="popup-head"><div><div style="font-weight:800;font-size:17px">🎧 Contact Support</div><div style="font-size:12px;color:#64748b">We reply within 1 hour</div></div><button onclick="closeSupport()" style="width:32px;height:32px;border-radius:50%;border:none;background:#f1f5f9;font-size:18px;cursor:pointer">✕</button></div>
<div style="padding:18px 20px">
<div class="support-opt" onclick="window.open('https://wa.me/254700000000?text=Hi LONMA Support, I need help','_blank')"><div style="font-size:28px">💬</div><div><div style="font-weight:700">WhatsApp Support</div><div style="font-size:12px;color:#64748b">Chat now - 0700 000 000</div></div><div style="margin-left:auto">›</div></div>
<div class="support-opt" onclick="window.location.href='mailto:admin@lonma.com?subject=LONMA Support'"><div style="font-size:28px">📧</div><div><div style="font-weight:700">Email Support</div><div style="font-size:12px;color:#64748b">admin@lonma.com</div></div><div style="margin-left:auto">›</div></div>
<div class="support-opt" onclick="window.location.href='tel:0700000000'"><div style="font-size:28px">📞</div><div><div style="font-weight:700">Call Support</div><div style="font-size:12px;color:#64748b">0700 000 000 - Mon-Sat 8am-6pm</div></div><div style="margin-left:auto">›</div></div>
<div style="margin:18px 0 10px;font-weight:800;font-size:13px">SEND A MESSAGE</div>
<label class="label">Your Name</label><input class="input" id="supName" placeholder="Your name">
<div style="margin-top:12px"><label class="label">Message</label><textarea id="supMsg" style="width:100%;height:90px;border:1px solid #e2e8f0;border-radius:12px;padding:12px;font-size:14px;outline:none" placeholder="Describe your issue..."></textarea></div>
<button class="btn-primary" onclick="sendSupport()">Send Message →</button>
<p id="supStatus" style="text-align:center;font-size:13px;margin-top:10px;font-weight:600"></p>
</div>
</div>
</div>

<script>
function openMenu(){document.getElementById('sidebar').classList.add('open');document.getElementById('overlay').classList.add('show')}
function closeMenu(){document.getElementById('sidebar').classList.remove('open');document.getElementById('overlay').classList.remove('show')}
async function openBell(){
 closeMenu();
 document.getElementById('bellPopup').classList.add('show');
 let r=await fetch('/api/notifications');let d=await r.json();
 let h='';
 if(d.notifications.length==0) h='<div style="padding:30px;text-align:center;color:#64748b">No notifications</div>';
 else d.notifications.forEach(n=>{h+='<div class="notif-item"><div class="notif-dot"></div><div><div style="font-weight:700;font-size:14px">'+n.title+'</div><div style="font-size:13px;color:#475569;margin-top:3px">'+n.msg+'</div><div style="font-size:11px;color:#94a3b8;margin-top:4px">'+n.created+'</div></div></div>'});
 document.getElementById('notifList').innerHTML=h;
 document.getElementById('notifCount').textContent=d.notifications.length+' notifications';
}
function closeBell(){document.getElementById('bellPopup').classList.remove('show')}
function markRead(){document.getElementById('bellBadge').style.display='none';document.getElementById('notifList').innerHTML='<div style="padding:30px;text-align:center;color:#16a34a;font-weight:700">✓ All read</div>';}
function openSupport(){closeMenu();document.getElementById('supportPopup').classList.add('show')}
function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}
async function sendSupport(){
 let name=document.getElementById('supName').value;let msg=document.getElementById('supMsg').value;
 if(!msg){document.getElementById('supStatus').textContent='Please write a message';document.getElementById('supStatus').style.color='#dc2626';return;}
 let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,msg:msg})});
 let j=await r.json();let s=document.getElementById('supStatus');s.textContent=j.message;s.style.color='#16a34a';document.getElementById('supMsg').value='';
}
document.addEventListener('DOMContentLoaded',()=>{let path=location.pathname;document.querySelectorAll('.menu-item').forEach(a=>{if(a.getAttribute('href')===path)a.classList.add('active')})})
</script>
"""

@app.route("/")
def home():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>LONMA</title>""" + BASE + """<div class='page'>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Total Members</div><div class='stat-v' id='total'>0</div></div><div class='stat'><div class='stat-l'>Projects</div><div class='stat-v'>12</div></div><div class='stat'><div class='stat-l'>Status</div><div class='stat-v' style='color:#16a34a'>Active</div></div></div>
<div class='card'><div class='card-header'><div class='card-title'>Project Distribution</div><div class='card-sub'>Members per project (HQ 0)</div></div><div id='breakdown'></div></div>
</div>
<script>
async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;let h='';for(let k in d.projects_breakdown){h+='<div style="padding:14px 22px;border-bottom:1px solid #f8fafc;display:flex;justify-content:space-between;font-size:14px"><span>'+k+'</span><b>'+d.projects_breakdown[k]+'</b></div>';}document.getElementById('breakdown').innerHTML=h;}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/members")
def members_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Members</title>""" + BASE + """<div class='page'><div class='card'><div class='card-header'><div class='card-title'>Members</div><div class='card-sub'>All welfare members with photos</div></div><div style='padding:12px'><input class='input' id='q' placeholder='Search...' oninput='fil()'></div><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><thead><tr><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Photo</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Staff & Name</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Project</th></tr></thead><tbody id='tbl'></tbody></table></div></div></div>
<script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function render(l){let h='';if(l.length==0){h='<tr><td colspan=3 style="padding:30px;text-align:center;color:#64748b">No members yet</td></tr>';}else{l.forEach(m=>{let photo=m.photo?'<img src="'+m.photo+'" style="width:48px;height:48px;border-radius:50%;object-fit:cover;border:2px solid #e2e8f0">':'<div style="width:48px;height:48px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-weight:700;color:#64748b">'+m.full_names.charAt(0)+'</div>';h+='<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px 14px">'+photo+'</td><td style="padding:10px 14px"><div style="font-size:12px"><b style="background:#f1f5f9;padding:2px 8px;border-radius:6px">'+m.staff_no+'</b></div><div style="font-weight:700;font-size:14px;margin-top:4px">'+m.full_names+'</div><div style="font-size:11px;color:#64748b">G:'+(m.guardian_id||'-')+' S:'+(m.spouse_id||'-')+'</div></td><td style="padding:10px 14px;font-size:13px"><span style="background:#e3f2fd;color:#1565c0;padding:4px 10px;border-radius:999px;font-weight:600;font-size:12px">'+m.project+'</span></td></tr>';});}document.getElementById('tbl').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();render(all.filter(m=>(m.full_names+m.staff_no+m.project).toLowerCase().includes(qq)));}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/register")
def register_page():
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register</title>""" + BASE + """<div class='page'><div class='card'><div class='card-header'><div class='card-title'>Welfare Registration Form</div><div class='card-sub'>Add member with photo</div></div><div class='card-body'>
<div style="display:flex;gap:20px;align-items:center;margin-bottom:20px">
<div class="photo-box" id="photoBox" onclick="document.getElementById('photoInput').click()">
<img id="photoPreview" style="display:none">
<div id="photoPlaceholder"><div style="font-size:32px">📷</div><div class="photo-upload-text">Add Photo</div></div>
</div>
<div><div style="font-weight:700;font-size:14px">Member Photo</div><div style="font-size:12px;color:#64748b;margin-top:4px">Tap to upload photo<br>Max 2MB - JPG, PNG</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div>
</div>
<div class='section'><div class='section-num'>1</div><div class='section-label'>Staff Information</div></div>
<div class='grid2'><div><label class='label'>Staff Number</label><input class='input' id='staff_no' placeholder='PWANI/001'></div><div><label class='label'>Project</label><select class='input' id='project'>""" + opts + """</select></div></div>
<div style='margin-top:12px' class='grid2'><div><label class='label'>Date Joined</label><input class='input' id='month_joined' placeholder='Jan 2024'></div><div><label class='label'>Full Names *</label><input class='input' id='full_names' placeholder='Full Name'></div></div>
<div style='margin-top:12px' class='grid2'><div><label class='label'>Email *</label><input class='input' id='email' placeholder='email@lonma.com'></div><div><label class='label'>Password *</label><input class='input' id='password' type='password' placeholder='••••'></div></div>
<div class='section'><div class='section-num'>2</div><div class='section-label'>Parents IDs</div></div>
<div class='grid2'><div><label class='label'>Father ID</label><input class='input' id='father_id'></div><div><label class='label'>Mother ID</label><input class='input' id='mother_id'></div></div>
<div class='section'><div class='section-num'>3</div><div class='section-label'>Guardian & Spouse</div></div>
<div class='grid2'><div><label class='label'>Guardian ID No.</label><input class='input' id='guardian_id' placeholder='22400966'></div><div><label class='label'>Spouse ID No.</label><input class='input' id='spouse_id' placeholder='23601476'></div></div>
<div class='section'><div class='section-num'>4</div><div class='section-label'>Kids Birth Certificates</div></div>
<div class='grid3'><div><label class='label'>Kid 1</label><input class='input' id='kid1' placeholder='42107914'></div><div><label class='label'>Kid 2</label><input class='input' id='kid2' placeholder='111041990'></div><div><label class='label'>Kid 3</label><input class='input' id='kid3'></div></div>
<div style='margin-top:12px' class='grid2'><div><label class='label'>Kid 4</label><input class='input' id='kid4'></div><div><label class='label'>Kid 5</label><input class='input' id='kid5'></div></div>
<button class='btn-primary' onclick='doReg()' id='btn'>Create Member</button><p id='msg' style='text-align:center;font-size:13px;margin-top:10px;font-weight:600'></p>
</div></div></div>
<script>
let photoBase64 = "";
function handlePhoto(e){
 let file = e.target.files[0];
 if(!file) return;
 if(file.size > 2*1024*1024){alert('File too large, max 2MB');return;}
 let reader = new FileReader();
 reader.onload = function(ev){
   photoBase64 = ev.target.result;
   document.getElementById('photoPreview').src = photoBase64;
   document.getElementById('photoPreview').style.display='block';
   document.getElementById('photoPlaceholder').style.display='none';
   document.getElementById('photoBox').classList.add('has-photo');
 };
 reader.readAsDataURL(file);
}
async function doReg(){
 let btn=document.getElementById('btn');
 btn.textContent='Creating...';
 let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value,photo:photoBase64};
 if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';document.getElementById('msg').style.color='#dc2626';btn.textContent='Create Member';return;}
 let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});
 let j=await r.json();
 let m=document.getElementById('msg');
 m.textContent=j.error||j.message;
 m.style.color=r.ok?'#16a34a':'#dc2626';
 btn.textContent=r.ok?'Created':'Create Member';
 if(r.ok){setTimeout(()=>location.href='/members',800);}
}
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin")
def admin_login_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin</title>""" + BASE + """<div class='page' style='max-width:400px'><div class='card'><div class='card-header'><div class='card-title'>Admin Login</div></div><div class='card-body'><label class='label'>Email</label><input class='input' id='email' value='admin@lonma.com'><div style='margin-top:12px'><label class='label'>Password</label><input class='input' id='pass' type='password' value='admin123'></div><button class='btn-primary' onclick='login()'>Login</button><p id='msg' style='text-align:center;color:#dc2626;margin-top:10px'></p></div></div></div>
<script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok){location.href='/admin/dashboard?key='+j.key;}else{document.getElementById('msg').textContent=j.error;}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/dashboard")
def admin_dashboard():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin</title>""" + BASE + """<div class='page' style='max-width:1000px'><div class='card'><div class='card-header'><div class='card-title'>Admin - Welfare Management with Photos</div></div><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><thead><tr><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Photo</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Staff & Name</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Family</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Action</th></tr></thead><tbody id='tbl'></tbody></table></div></div>
<div class='card'><div class='card-header'><div class='card-title'>📩 Support Messages</div></div><div id='supList' style='padding:10px 20px'>Loading...</div></div></div>
<script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let photo=m.photo?'<img src="'+m.photo+'" style="width:44px;height:44px;border-radius:50%;object-fit:cover">':'<div style="width:44px;height:44px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-weight:700">'+(m.full_names||'A').charAt(0)+'</div>';let btn=prot?'<span style="color:#94a3b8;font-size:12px">System</span>':'<button onclick="del('+m.id+')" style="color:#dc2626;border:1px solid #fee2e2;background:#fff;border-radius:999px;padding:5px 12px;cursor:pointer">Delete</button>';h+='<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px">'+photo+'</td><td style="padding:14px"><b>'+m.staff_no+'</b><div style="font-weight:700">'+m.full_names+'</div><div style="font-size:11px;color:#64748b">'+m.email+'</div></td><td style="padding:14px;font-size:11px">G:'+(m.guardian_id||'-')+' S:'+(m.spouse_id||'-')+'<br>Kids:'+([m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(',')||'-')+'</td><td style="padding:14px">'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;let r2=await fetch('/api/support_list');let d2=await r2.json();let h2='';if(d2.messages.length==0)h2='<div style="color:#64748b">No support messages yet</div>';else d2.messages.forEach(m=>{h2+='<div style="padding:12px 0;border-bottom:1px solid #f1f5f9"><b>'+(m.name||'Guest')+'</b> <span style="font-size:11px;color:#94a3b8">'+m.created+'</span><div style="font-size:14px">'+m.msg+'</div></div>'});document.getElementById('supList').innerHTML=h2;}async function del(id){if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?key=""" + ADMIN_KEY + """',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/api/stats")
def api_stats():
    conn = get_db()
    try:
        total = conn.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        breakdown = {}
        for p in PROJECTS:
            breakdown[p] = conn.execute("SELECT COUNT(*) FROM users WHERE project=? AND email != ?", (p, ADMIN_EMAIL)).fetchone()[0]
        return jsonify({"total_members": total, "projects_breakdown": breakdown})
    finally:
        conn.close()

@app.route("/api/notifications")
def api_notifs():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
        return jsonify({"notifications": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/support", methods=["POST"])
def api_support():
    data = request.get_json(silent=True) or {}
    conn = get_db()
    try:
        conn.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))", (data.get("name","Guest"), data.get("msg","")))
        conn.commit()
        return jsonify({"message": "Message sent! Support will reply soon."})
    finally:
        conn.close()

@app.route("/api/support_list")
def api_support_list():
    conn = get_db()
    try:
        rows = conn.execute("SELECT * FROM support_msgs ORDER BY id DESC").fetchall()
        return jsonify({"messages": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/members")
def api_members():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users WHERE email != ? ORDER BY id DESC", (ADMIN_EMAIL,)).fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/members_admin")
def api_members_admin():
    conn = get_db()
    try:
        rows = conn.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users ORDER BY id DESC").fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        conn.close()

@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    data = request.get_json(silent=True)
    conn = get_db()
    try:
        user = conn.execute("SELECT password,api_key FROM users WHERE email=?", (data.get("email"),)).fetchone()
        if not user or not check_password_hash(user["password"], data.get("password","")):
            return jsonify({"error": "Invalid"}), 401
        return jsonify({"key": user["api_key"]})
    finally:
        conn.close()

@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS":
        return "", 200
    data = request.get_json(silent=True)
    if not data or not data.get("email") or not data.get("password"):
        return jsonify({"error": "email and password required"}), 400
    conn = get_db()
    try:
        if conn.execute("SELECT id FROM users WHERE email=?", (data["email"],)).fetchone():
            return jsonify({"error": "Email exists"}), 400
        api_key = "lonma_" + secrets.token_hex(16)
        photo = data.get("photo","")
        if len(photo) > 500000:
            photo = photo[:500000]
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (data.get("staff_no",""), data.get("full_names",""), data.get("project","HQ"), data["email"], generate_password_hash(data["password"]), api_key, data.get("month_joined",""), data.get("father_id",""), data.get("mother_id",""), data.get("guardian_id",""), data.get("spouse_id",""), data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5",""), photo))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("New Member Registered", f"{data.get('full_names','')} joined {data.get('project','')}", "Just now"))
        conn.commit()
        return jsonify({"message": "Member created with photo"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        conn.close()

@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS":
        return "", 200
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return jsonify({"error": "Admin key required"}), 401
    conn = get_db()
    try:
        u = conn.execute("SELECT email FROM users WHERE id=?", (member_id,)).fetchone()
        if not u or u["email"]==ADMIN_EMAIL:
            return jsonify({"error": "Cannot delete Protected Admin"}), 403
        conn.execute("DELETE FROM users WHERE id=?", (member_id,))
        conn.commit()
        return jsonify({"message": "Deleted"})
    finally:
        conn.close()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
