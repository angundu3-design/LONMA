from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, csv
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem","TF WSL"]
PROJECT_MAP = {"Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani Oil Products":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","Java":"Java House","SJ":"SJ Johnson","TF WSL":"TF WSL","TF":"TF WSL"}
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"

SEED_DATA = [
 ("202712","Pwani","Nov.2022","Laura Imali","","","0327707","37982161","112409612","","","",""),
 ("202710","Pwani","Dec.2020","Edith Kabera","","","23740423","23965879","10700481","112152616","11250650","",""),
 ("202677","Pwani","October.2024","Phoebe Anyango","1014509","2266278","","","","","","",""),
 ("202706","Pwani","Aug.2021","Cynthia Awuor","","9892352","","","1231202182","","","",""),
 ("202707","Pwani","Nov.2021","Maureen Owino","2859205","4313510","28254592","24675501","9927L79","3300789","26057L7","9999788",""),
 ("202721","Pwani","March .2023","Merceline Adhiambo","4026148","13199939","","27472316","3271828","","","",""),
 ("202705","Pwani","Marh 2019","Odiembo Yvonne","","8351397","","","will give later","","","",""),
 ("202722","Pwani","Dec.2023","Linet Oduor","2828431","14479498","","","","","","",""),
 ("202746","Pwani","Nov.2025","Divyan Dorcas","","13603542","","","","","","",""),
 ("202708","Pwani","Jan. 2020","Lilian Muchuma","","261270","","","110707451","","","",""),
 ("202711","Pwani","Sept.2021","John Adiel","","1329824","28565804","32190036","","","","",""),
 ("292932","Pwani","May.2026","Milcah Otiende","8232129","7861021","","32624856","4094626","","","",""),
 ("280370","Pwani","Sept. 2026","Lucy Mwende Mbatha","2991561","2965465","","","0852106551","","","",""),
 ("202700","Pwani Oil Products Ltd.","Mar.2025","Charles Kimutai Kirui","3872261","3872429","","31045698","612112010","","","",""),
 ("202709","Pwani Oil Products Ltd.","Mar.2025","Oyoyo Yvonne Bentar","","11801824","","27464418","","","","",""),
 ("202678","Pwani Oil Products Ltd.","Mar.2025","Owen Muthee Waithaka","21217575","22555615","","","","","","",""),
 ("202733","Pwani Oil Products Ltd.","Mar.2025","Sharon Cherono","","11635405","","","","","","",""),
 ("202529","Pwani Oil Products Ltd.","Mar.2025","Alex Shangala","4176764","7956390","","33313078","692102029","691828162","","",""),
 ("202729","Pwani Oil Products Ltd.","Mar.2025","Rose Lumonya Saidi","","4252080","","","","","","",""),
 ("202747","Pwani Oil Products Ltd.","Jul.2025","Brenda Nelima Wafula","","133101","","","","","","",""),
 ("10405","Pwani Oil Products Ltd.","Mar.2025","Diana Atieno Oduor","","4722494","757617564","28078423- Ben Kitui","","370702896 -Dennis Adams","21506184- Joy Nelima","Samantha Malia Achieng",""),
 ("202749","Pwani Oil Products Ltd.","Mar.2025","Celine Nasimiyu Wamalwa","","8784757","","28990208","William Musungu","Moses Musungu","Bryton Musungu","",""),
 ("292976","Pwani Oil Products Ltd.","Apr.2026","Belinda Chemtai","","4722288","","","372315084","182018971","","",""),
 ("202702","Pwani Oil Products Ltd.","May.2025","Betty Akinyi Namamba","Fabians Namamba","Janet Atieno","","","","","","",""),
 ("202723","Pwani Oil Products Ltd.","Mar.2025","Metrine Cherop Chumo","","","","29934624","411700883","411506469","","",""),
 ("50516","Pwani Oil Products Ltd.","May.2025","Sheila Adisa Volemi","VOLEMI","TERESIA","HUDSON IMBAYI","22175541","","","","",""),
 ("202701","Pwani Oil Products Ltd.","Mar.2025","Everlyne Mukoya Stephen","","","","23600368","","671767","395330","",""),
 ("202703","Pwani Oil Products Ltd.","Mar.2025","Caren Nanjala Chonge","","5639451","","22086206","364057","6090663","","",""),
 ("202704","Pwani Oil Products Ltd.","Mar.2025","Hellen Achieng Onyango","711723882","726994852","","722618476","","","","",""),
 ("202724","Pwani Oil Products Ltd.","Mar.2025","Benta Achieng Muruka","CHRISTOPHER MURUKA","JANE MAGENGA","","28687282","1311214785","21910561","","",""),
 ("202697","Pwani","Sept.2017","Naomi Mwango Abenga","1658833","","","22188003","121032026","121622654","112220451","",""),
 ("202696","Pwani","2015","Lydiah Nyaanga Osengo","1649626","1637770","","10020853","160900879","168706540/19","","",""),
 ("202693","Pwani","May.2022","Meggiling Abuga Nyakerario","","","8647005","","","","160900879","",""),
 ("202695","Pwani","2022","Gorrety Adhiambo Otieno","9807667","26810228","","30257258","2348625","2350080","3743676","",""),
 ("202699","Pwani","14/12/2022","Sophia Nyamoita Mokaya","","6541570","","27233755","","","",""),
 ("202751","Pwani","Oct.2023","Benjamin Odiwuor Mboya","10596034","20015894","","466468971","7893744","","",""),
 ("202730","pwani","4.8.2025","Orwa Diana Atieno","96811362","21136615","","36519946","","","",""),
 ("202694","Pwani","Jan.2020","Charles Adika","8837595","11833576","","","","","",""),
 ("282000","Pwani","May.2026","Hyphine Chepkoech Mutai","10383876","28240917","","26261936","","","",""),
 ("202750","Pwani","May.2025","Priscah Anjemo Injili","","21842168","","32990585","795787","978435","",""),
 ("202698","Pwani","Feb.2022","Postine Atieno","7921446","8398928","","38801320","122318007","","",""),
 ("202744","PWANI","Mar.2024","Anthony Manyara Chania","21022712","86260659","","923456988","","","",""),
 ("202683","Pwani","Mar.2013","Eunice Makona","","4722288","","210327239","7575163","7575161","7575162","",""),
 ("202914","TF WSL","20th Jan 2025","Said Roseline Heri","Musa Bin Said","Beatrice N. Munoko","1319025","9765327","4408202","7758933","7108428","",""),
 ("202906","TF WSL","27th Mar 2025","Jecinta Karanja","KARANJA NDUNG'U","PAULINE NJOKI","11114948","30461200","1358036","614595","","",""),
 ("202905","TF WSL","5th Feb 2025","Mary Atieno","","Mary Atieno Onyango","14438209","","001432321","4898710","","",""),
 ("202915","TF WSL","2025","Pauline Murathi","George Murathi","Jane Nungari","23236444","","","","",""),
 ("202916","TF WSL","Jan.2027","Ann Njeri Kareiya","STEPHEN KAREIYA","JENNIFER WANGUI","32317216","23524787","9901560","","",""),
 ("202913","TF WSL","Jan.2025","Tabitha Wanjiku","David Karugah","Grace David","10893197","33095213","37220833","","",""),
 ("202917","TF WSL","13th Jan 2025","Prudence Achieng Wanyangu","","WILFRIDA ADHIAMBO WANYANGU","22482407","37155644","","","",""),
 ("292943","TF WSL","15/01/2026","Linda Naliaka Juma","SIMON KARIUKI","Jane Jareda","24928699","","9655625","6031104","",""),
 ("202908","TF WSL","2025","Pascaline Njoki","Joseph Wachira Ngigi (deceased)","Lucy Wanjiru Njogu","38761889","","645865","","",""),
 ("202910","TF WSL","16th Oct 2025","Lucy Nyambura","","Eddah Wanjiru","14495721","","","","",""),
 ("292977","TF WSL","2026","Diana Muse","Fanuel Muse","Regina Kaveza","28385461","","","","",""),
 ("202907","TF WSL","22/07/2026","Janet Wairimu","Joseph Waiganjo Kariuki","Grace Muthakyi Kimanzi","10767868","","3868681","","",""),
 ("280293","TF WSL","13th July 2026","Catherine Mukami","Andrew Kiruja","Naomi Adrew","","24041649","361716972","5810997","",""),
]
# --- BREAKDOWN DATA - WALFARE_API_DATA.xlsx Sheet1 ---
# project, dec, jan, feb, mar, apr, may, dec_n, jan_n, feb_n, mar_n, apr_n, may_n
FINANCE_PROJECTS = [
 ("Pwani",21000,20400,21300,21000,21300,21600,70,68,71,70,71,72),
 ("Java",9000,9600,9900,9900,9600,9300,30,32,33,33,32,31),
 ("Johnson",10500,9600,10200,9900,9900,9300,35,32,34,33,33,31),
 ("Kanji",900,900,900,900,900,900,3,3,3,3,3,3),
 ("HQ",1200,1200,1200,1200,1200,1200,4,4,4,4,4,4),
 ("GCB-MT",4500,4500,4800,4800,4800,4500,15,15,16,16,16,15),
 ("TF-WS",4800,5100,4800,4800,4800,4500,16,17,16,16,16,15),
 ("TF-LM",12300,12300,11700,11700,12600,9300,41,41,39,39,42,31),
 ("TF-MT",19800,20700,21900,22200,21300,21300,66,69,73,74,71,71),
 ("GCB-TDs",2700,3000,3000,3300,3600,3600,9,10,10,11,12,12),
 ("Highchem",0,0,0,0,0,4800,0,0,0,0,0,16),
]
FINANCE_TOTALS = (86700,87300,89700,89700,90000,90300,289,291,299,299,300,301)
BENEFICIARIES = [
 ("Rose Lumonya Saidi","POPL","Death-Father","Dec 2025",40000),
 ("Nostar","TF","Loss of earning","Dec 2025",19000),
 ("Susan Ndungu","TF","Death-Father","26 Jan 2026",40000),
 ("Irene Wairimu","Java","Death-Guardian","May 2026",40000),
 ("Mercy Mwende","GCB","Loss of earning","May 2026",11075),
 ("Damarais Muyoka","TF","Death-Father","May 2026",40000),
 ("Ruth Amollo Nyangun","","Death-Father","Jun 2026",40000),
 ("Sheila Okomo","TF","Loss of earning","May",9000),
 ("Sheila Okomo","TF","Loss of earning","June",9000),
]
FARES = [
 ("Eunice Makona","0714910135",1200),
 ("Hellen Onyango","0724570228",1200),
 ("Caren Chonge","0710427468",900),
 ("Antony Mwendia","",1500),
 ("Gladys Nyaga","",1500),
 ("Marlon K. Ang'undu","",1200),
 ("Gladys Wambaire Kinuthia","",1200),
 ("Evapertual Wambui","",1200),
 ("Catherine Ogutu","",1700),
 ("Ebby Lomoi","",1700),
 ("Jackline Ayiga","",1700),
 ("Esther Marenya","",1600),
 ("George Odhiambo","",1400),
]
GRAND_TOTAL = 783700
TRANSFER_TOTAL = 673270
EXPENDITURES_TOTAL = 283141
BENEFICIARIES_TOTAL = 248075
FARES_TOTAL = 18000

def clean(v):
    if v is None: return ""
    s = str(v).strip()
    if s.upper() in ("NA","N/A","NA ","-","NONE","LATER","NULL"): return ""
    if "will give" in s.lower(): return ""
    if "will provide" in s.lower(): return ""
    if "notification:" in s.lower(): return s.split(":",1)[1].strip()
    return s

def make_email(full_names, staff_no):
    parts = [p for p in full_names.lower().replace(".","").split() if p.isalpha()]
    if len(parts) >= 2:
        return f"{parts[0]}.{parts[-1]}@figbrands.co.ke"
    elif parts:
        return f"{parts[0]}.{staff_no}@figbrands.co.ke"
    return f"member.{staff_no}@figbrands.co.ke"

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
    conn.execute('CREATE TABLE IF NOT EXISTS finance_projects (id INTEGER PRIMARY KEY AUTOINCREMENT, project TEXT UNIQUE, dec_amt REAL, jan_amt REAL, feb_amt REAL, mar_amt REAL, apr_amt REAL, may_amt REAL, dec_n INTEGER, jan_n INTEGER, feb_n INTEGER, mar_n INTEGER, apr_n INTEGER, may_n INTEGER)')
    conn.execute('CREATE TABLE IF NOT EXISTS beneficiaries (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, project TEXT, reason TEXT, date_str TEXT, amount REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS fares (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, phone TEXT, amount REAL)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    if not conn.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    if not conn.execute("SELECT id FROM notifications").fetchone():
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Welcome to F.I.G BRANDS WELFARE","Your welfare system is active. HQ 0 - ready to register members.","Now"))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Breakdown Added","Finance breakdown Dec-May added - 534,700 contributions, 248,075 beneficiaries.","Now"))
    added = 0
    for _row in SEED_DATA:
        _row = tuple(list(_row) + [""] * (13 - len(_row)))[:13]
        staff_no, proj_raw, month, names, father, mother, guardian, spouse, k1, k2, k3, k4, k5 = _row
        staff_no = clean(staff_no); names = clean(names)
        if not staff_no or not names: continue
        if conn.execute("SELECT id FROM users WHERE staff_no=?", (staff_no,)).fetchone(): continue
        project = PROJECT_MAP.get(proj_raw, proj_raw)
        email = make_email(names, staff_no)
        if conn.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            email = f"member.{staff_no}@figbrands.co.ke"
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (staff_no, names, project, email, generate_password_hash(staff_no), "fig_"+secrets.token_hex(12), clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5), ""))
        added += 1
    if not conn.execute("SELECT id FROM finance_projects").fetchone():
        for p,dec,jan,feb,mar,apr,may,dn,jn,fn,man,an,mn in FINANCE_PROJECTS:
            conn.execute("INSERT INTO finance_projects (project,dec_amt,jan_amt,feb_amt,mar_amt,apr_amt,may_amt,dec_n,jan_n,feb_n,mar_n,apr_n,may_n) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?)", (p,dec,jan,feb,mar,apr,may,dn,jn,fn,man,an,mn))
    if not conn.execute("SELECT id FROM beneficiaries").fetchone():
        for n,p,r,d,a in BENEFICIARIES:
            conn.execute("INSERT INTO beneficiaries (name,project,reason,date_str,amount) VALUES (?,?,?,?,?)", (n,p,r,d,a))
    if not conn.execute("SELECT id FROM fares").fetchone():
        for n,ph,a in FARES:
            conn.execute("INSERT INTO fares (name,phone,amount) VALUES (?,?,?)", (n,ph,a))
    conn.commit(); conn.close()
    print(f"Seeded {added} new members - total seed {len(SEED_DATA)}")
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
.badge{position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;font-size:10px;font-weight:800;min-width:18px;height:18px;border-radius:999px;display:flex;align-items:center;justify-content:center;padding:0 4px;border:2px solid #1565c0}
.overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:40;display:none}.overlay.show{display:block}
.sidebar{position:fixed;top:0;left:0;width:300px;height:100%;background:#fff;z-index:50;transform:translateX(-100%);transition:transform .3s ease;overflow:hidden;display:flex;flex-direction:column;border-radius:0 20px 20px 0;box-shadow:4px 0 24px rgba(0,0,0,.15)}
.sidebar.open{transform:translateX(0)}
.sidebar-top{background:#1e88e5;color:#fff;padding:24px 20px 18px 20px}
.avatar{width:72px;height:72px;border-radius:50%;background:#fff;display:flex;align-items:center;justify-content:center;overflow:hidden;border:3px solid rgba(255,255,255,.4)}
.avatar img{width:100%;height:100%;object-fit:cover}
.profile-name{font-size:16px;font-weight:700;margin-top:14px;text-transform:uppercase}
.profile-email{font-size:13px;margin-top:4px;opacity:.9;word-break:break-all}
.menu-list{flex:1;overflow:auto;padding:12px 0}
.menu-item{display:flex;align-items:center;gap:16px;padding:15px 22px;font-size:15px;font-weight:600;color:#0f172a;cursor:pointer;text-decoration:none}
.menu-item:hover{background:#f1f5f9}
.menu-item .icon{width:26px;height:26px;display:flex;align-items:center;justify-content:center;font-size:20px}
.menu-item.active{background:#e3f2fd;color:#1565c0}
.sidebar-bottom{padding:14px 20px;border-top:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:11px;color:#94a3b8;font-weight:600}
.page{max-width:800px;margin:0 auto;padding:16px}
.card{background:#fff;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:12px}
.card-header{padding:20px 22px;border-bottom:1px solid #f1f5f9}
.card-title{font-weight:800;font-size:16px}
.card-sub{font-size:12px;color:#64748b;margin-top:4px}
.card-body{padding:22px}
.input{width:100%;height:46px;border:1px solid #e2e8f0;border-radius:12px;padding:0 14px;font-size:14px;outline:none}
.input:focus{border-color:#1e88e5;box-shadow:0 0 0 3px rgba(30,136,229,.12)}
.label{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.6px;margin-bottom:7px;display:block}
.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}
.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}
.section{display:flex;align-items:center;gap:10px;margin:22px 0 14px 0}
.section-num{width:22px;height:22px;background:#0f172a;color:#fff;border-radius:7px;display:flex;align-items:center;justify-content:center;font-size:10px;font-weight:800}
.section-label{font-size:11.5px;font-weight:800;text-transform:uppercase;letter-spacing:.6px}
.btn-primary{width:100%;height:50px;background:#0f172a;color:#fff;border:none;border-radius:12px;font-weight:700;font-size:14px;cursor:pointer;margin-top:10px}
.btn-excel{display:inline-flex;align-items:center;gap:8px;background:#16a34a;color:#fff;padding:10px 16px;border-radius:12px;font-weight:700;font-size:13px;text-decoration:none;border:none;cursor:pointer}
.stat-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px}
.stat{background:#fff;border-radius:16px;padding:18px;border:1px solid #e2e8f0}
.stat-l{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase;letter-spacing:.6px}
.stat-v{font-size:26px;font-weight:800;margin-top:4px}
.photo-box{width:110px;height:110px;border-radius:50%;border:3px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#f8fafc;cursor:pointer}
.photo-box img{width:100%;height:100%;object-fit:cover}
.photo-box.has-photo{border-style:solid;border-color:#1e88e5}
.photo-upload-text{font-size:11px;color:#64748b;font-weight:600;text-align:center}
.popup{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:100;display:none;align-items:flex-end;justify-content:center}
.popup.show{display:flex}
.popup-card{background:#fff;width:100%;max-width:520px;border-radius:22px 22px 0 0;max-height:82vh;overflow:auto;padding-bottom:20px}
.popup-head{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #f1f5f9;position:sticky;top:0;background:#fff}
.notif-item{padding:16px 20px;border-bottom:1px solid #f8fafc;display:flex;gap:12px}
.notif-dot{width:10px;height:10px;background:#1565c0;border-radius:50%;margin-top:6px;flex-shrink:0}
.support-opt{display:flex;gap:14px;align-items:center;padding:16px;border:1px solid #e2e8f0;border-radius:14px;margin-bottom:10px;cursor:pointer}
.cred-row{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px dashed #f1f5f9;font-size:13px}
.cred-row span:first-child{color:#64748b}
.cred-row span:last-child{font-weight:600;text-align:right}
table.fin{width:100%;border-collapse:collapse;font-size:13px}table.fin th{padding:10px 8px;background:#f8fafc;text-align:left;font-size:11px}table.fin td{padding:10px 8px;border-bottom:1px solid #f1f5f9}table.fin tr.total td{font-weight:800;background:#e3f2fd}
@media(max-width:600px){.stat-grid{grid-template-columns:1fr 1fr}.grid2,.grid3{grid-template-columns:1fr}}
</style>
<div class="app-header">
<div class="left"><button class="menu-btn" onclick="openMenu()">☰</button><div class="brand-top"><div class="brand-icon">F</div><div class="brand-name">F.I.G BRANDS<span>WELFARE SYSTEM</span></div></div></div>
<div class="header-icons"><div class="h-icon" onclick="openBell()">🔔<span class="badge" id="bellBadge">3</span></div><div class="h-icon" onclick="openSupport()">🎧</div></div>
</div>
<div class="overlay" id="overlay" onclick="closeMenu()"></div>
<div class="sidebar" id="sidebar">
<div class="sidebar-top">
<div class="avatar"><img src="https://i.pravatar.cc/150?img=3"></div>
<div class="profile-name">F.I.G ADMIN</div>
<div class="profile-email">admin@lonma.com</div>
</div>
<div class="menu-list">
<a class="menu-item" href="/"><span class="icon">📊</span> Overview</a>
<a class="menu-item" href="/members"><span class="icon">👥</span> Members</a>
<a class="menu-item" href="/breakdown"><span class="icon">💰</span> Breakdown / Finance</a>
<a class="menu-item" href="/register"><span class="icon">➕</span> Register Member</a>
<a class="menu-item" href="/download/excel"><span class="icon">📥</span> Download Excel</a>
<div style="height:1px;background:#f1f5f9;margin:8px 20px"></div>
<a class="menu-item" href="#" onclick="openBell();return false"><span class="icon">🔔</span> Notifications</a>
<a class="menu-item" href="#" onclick="openSupport();return false"><span class="icon">🎧</span> Contact Support</a>
<a class="menu-item" href="#"><span class="icon">🔄</span> Syncing</a>
<a class="menu-item" href="#"><span class="icon">💬</span> Give Feedback</a>
<a class="menu-item" href="/admin"><span class="icon">⚙️</span> Settings</a>
<a class="menu-item" href="/admin" style="color:#dc2626"><span class="icon">⏻</span> Log Out</a>
</div>
<div class="sidebar-bottom"><span>F.I.G BRANDS WELFARE</span><span>v4.33.0 (patch 1)</span></div>
</div>
<div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()">
<div class="popup-card">
<div class="popup-head"><div><div style="font-weight:800;font-size:17px">🔔 Notifications</div><div style="font-size:12px;color:#64748b" id="notifCount">3 new</div></div><button onclick="closeBell()" style="width:32px;height:32px;border-radius:50%;border:none;background:#f1f5f9;font-size:18px;cursor:pointer">✕</button></div>
<div id="notifList"><div style="padding:30px;text-align:center;color:#64748b">Loading...</div></div>
<div style="padding:0 20px"><button onclick="markRead()" style="width:100%;height:44px;border-radius:12px;border:1px solid #e2e8f0;background:#fff;font-weight:700;cursor:pointer">Mark all as read</button></div>
</div>
</div>
<div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()">
<div class="popup-card">
<div class="popup-head"><div><div style="font-weight:800;font-size:17px">🎧 Contact Support</div><div style="font-size:12px;color:#64748b">We reply within 1 hour</div></div><button onclick="closeSupport()" style="width:32px;height:32px;border-radius:50%;border:none;background:#f1f5f9;font-size:18px;cursor:pointer">✕</button></div>
<div style="padding:18px 20px">
<div class="support-opt" onclick="window.open('https://wa.me/254707780807?text=Hi F.I.G BRANDS Support, I need help','_blank')"><div style="font-size:28px">💬</div><div><div style="font-weight:700">WhatsApp Support</div><div style="font-size:12px;color:#64748b">Chat now - 0707 780 807</div></div><div style="margin-left:auto">›</div></div>
<div class="support-opt" onclick="window.location.href='mailto:info@figbrands.co.ke?subject=F.I.G BRANDS Support'"><div style="font-size:28px">📧</div><div><div style="font-weight:700">Email Support</div><div style="font-size:12px;color:#64748b">info@figbrands.co.ke</div></div><div style="margin-left:auto">›</div></div>
<div class="support-opt" onclick="window.location.href='tel:0707780807'"><div style="font-size:28px">📞</div><div><div style="font-weight:700">Call Support</div><div style="font-size:12px;color:#64748b">0707 780 807 - Mon-Sat 8am-6pm</div></div><div style="margin-left:auto">›</div></div>
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

MEMBER_BASE = BASE.replace('F.I.G ADMIN','F.I.G MEMBER').replace('admin@lonma.com','info@figbrands.co.ke').replace('https://i.pravatar.cc/150?img=3','https://i.pravatar.cc/150?img=12')

@app.route("/")
def home():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>F.I.G BRANDS WELFARE</title>""" + BASE + """<div class='page'>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Total Members</div><div class='stat-v' id='total'>0</div></div><div class='stat'><div class='stat-l'>Grand Total</div><div class='stat-v' style='font-size:20px'>Ksh 783,700</div></div><div class='stat'><div class='stat-l'>Contributions Dec-May</div><div class='stat-v' style='font-size:20px;color:#16a34a'>Ksh 534,700</div></div></div>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Beneficiaries Paid</div><div class='stat-v' style='font-size:20px;color:#dc2626'>Ksh 248,075</div></div><div class='stat'><div class='stat-l'>Fares</div><div class='stat-v' style='font-size:20px'>Ksh 18,000</div></div><div class='stat'><div class='stat-l'>Status</div><div class='stat-v' style='color:#16a34a'>Active</div></div></div>
<div class='card'><div class='card-header'><div class='card-title'>Project Distribution</div><div class='card-sub'>Members per project - <a href='/breakdown'>View Full Breakdown →</a></div></div><div id='breakdown'></div></div>
</div>
<script>
async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;let h='';for(let k in d.projects_breakdown){h+='<div style="padding:14px 22px;border-bottom:1px solid #f8fafc;display:flex;justify-content:space-between;font-size:14px"><span>'+k+'</span><b>'+d.projects_breakdown[k]+'</b></div>';}document.getElementById('breakdown').innerHTML=h;}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/breakdown")
def breakdown_page():
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Breakdown - F.I.G BRANDS</title>""" + BASE + """<div class='page' style='max-width:1000px'>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Grand Total</div><div class='stat-v' style='font-size:20px'>Ksh 783,700</div></div><div class='stat'><div class='stat-l'>Transfer</div><div class='stat-v' style='font-size:20px'>Ksh 673,270</div></div><div class='stat'><div class='stat-l'>Expenditures</div><div class='stat-v' style='font-size:20px;color:#dc2626'>Ksh 283,141</div></div></div>
<div class='card'><div class='card-header'><div class='card-title'>💰 Monthly Contributions by Project - Dec to May</div><div class='card-sub'>Amount (Ksh) + Members in brackets</div></div><div style='overflow:auto'><table class='fin'><thead><tr><th>Project</th><th>DEC</th><th>JAN</th><th>FEB</th><th>MAR</th><th>APR</th><th>MAY</th><th>Total</th></tr></thead><tbody id='finBody'></tbody></table></div></div>
<div class='card'><div class='card-header'><div class='card-title'>🎁 Beneficiaries - Ksh 248,075</div><div class='card-sub'>9 payouts</div></div><div id='benList' style='padding:6px 20px 16px'></div></div>
<div class='card'><div class='card-header'><div class='card-title'>🚌 Fares - Ksh 18,000</div><div class='card-sub'>13 people</div></div><div id='fareList' style='padding:6px 20px 16px'></div></div>
</div>
<script>
function fmt(n){return Number(n).toLocaleString()}
async function load(){let r=await fetch('/api/breakdown');let d=await r.json();let h='';let tot=[0,0,0,0,0,0];let totN=[0,0,0,0,0,0];d.projects.forEach(p=>{let rowTotal=p.dec_amt+p.jan_amt+p.feb_amt+p.mar_amt+p.apr_amt+p.may_amt;h+='<tr><td><b>'+p.project+'</b></td><td>'+fmt(p.dec_amt)+' ('+p.dec_n+')</td><td>'+fmt(p.jan_amt)+' ('+p.jan_n+')</td><td>'+fmt(p.feb_amt)+' ('+p.feb_n+')</td><td>'+fmt(p.mar_amt)+' ('+p.mar_n+')</td><td>'+fmt(p.apr_amt)+' ('+p.apr_n+')</td><td>'+fmt(p.may_amt)+' ('+p.may_n+')</td><td><b>'+fmt(rowTotal)+'</b></td></tr>';});h+='<tr class="total"><td>TOTAL</td><td>'+fmt(d.totals[0])+' ('+d.totals[6]+')</td><td>'+fmt(d.totals[1])+' ('+d.totals[7]+')</td><td>'+fmt(d.totals[2])+' ('+d.totals[8]+')</td><td>'+fmt(d.totals[3])+' ('+d.totals[9]+')</td><td>'+fmt(d.totals[4])+' ('+d.totals[10]+')</td><td>'+fmt(d.totals[5])+' ('+d.totals[11]+')</td><td>'+fmt(d.totals.slice(0,6).reduce((a,b)=>a+b,0))+'</td></tr>';document.getElementById('finBody').innerHTML=h;
let bh='';d.beneficiaries.forEach(b=>{bh+='<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed #f1f5f9;font-size:14px"><span><b>'+b.name+'</b> <span style="color:#64748b">- '+b.project+' - '+b.reason+' - '+b.date_str+'</span></span><b>Ksh '+fmt(b.amount)+'</b></div>';});bh+='<div style="display:flex;justify-content:space-between;padding:12px 0;font-weight:800"><span>TOTAL BENEFICIARIES</span><span>Ksh '+fmt(d.beneficiaries_total)+'</span></div>';document.getElementById('benList').innerHTML=bh;
let fh='';d.fares.forEach(f=>{fh+='<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed #f1f5f9;font-size:14px"><span><b>'+f.name+'</b> <span style="color:#64748b">'+(f.phone||'')+'</span></span><b>Ksh '+fmt(f.amount)+'</b></div>';});fh+='<div style="display:flex;justify-content:space-between;padding:12px 0;font-weight:800"><span>TOTAL FARES</span><span>Ksh '+fmt(d.fares_total)+'</span></div>';document.getElementById('fareList').innerHTML=fh;}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/members")
def members_page():
    proj_opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in ["All Projects"]+PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Members - F.I.G BRANDS WELFARE</title>""" + MEMBER_BASE + """<div class='page' style='max-width:900px'><div class='card'><div class='card-header' style='display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px'><div><div class='card-title'>Members - Credentials</div><div class='card-sub'>Registered member credentials only - No photo</div></div><a class='btn-excel' href='/download/excel'>📥 Download Excel</a></div><div style='padding:12px;display:flex;gap:10px'><input class='input' id='q' placeholder='Search by name, staff no, project...' oninput='fil()' style='flex:2'><select class='input' id='projFilter' onchange='fil()' style='flex:1'>""" + proj_opts + """</select></div><div id='list' style='padding:0 12px 16px'></div></div></div>
<script>
let all=[];
async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}
function row(label,val){return '<div class="cred-row"><span>'+label+'</span><span>'+(val||'-')+'</span></div>';}
function render(l){
 let h='';
 if(l.length==0){h='<div style="padding:30px;text-align:center;color:#64748b">No members yet for this project</div>';}
 else{l.forEach(m=>{
   let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';
   h+='<div style="background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:18px;margin-bottom:12px">'
   +'<div style="display:flex;justify-content:space-between;align-items:center;margin-bottom:10px"><div><div style="font-weight:800;font-size:16px">'+m.full_names+'</div><div style="font-size:12px;color:#64748b">'+m.email+'</div></div><span style="background:#e3f2fd;color:#1565c0;padding:5px 12px;border-radius:999px;font-weight:700;font-size:12px">'+m.project+'</span></div>'
   +row('Staff Number',m.staff_no)
   +row('Date Joined',m.month_joined)
   +row('Father ID',m.father_id)
   +row('Mother ID',m.mother_id)
   +row('Guardian ID No.',m.guardian_id)
   +row('Spouse ID No.',m.spouse_id)
   +row('Kids Birth Certs',kids)
   +'</div>';
 });}
 document.getElementById('list').innerHTML=h;
}
function fil(){
 let qq=document.getElementById('q').value.toLowerCase();
 let pf=document.getElementById('projFilter').value;
 render(all.filter(m=>{
   let okSearch=(m.full_names+' '+m.staff_no+' '+m.project+' '+(m.guardian_id||'')+' '+(m.spouse_id||'')).toLowerCase().includes(qq);
   let okProj=(pf=='All Projects'||m.project==pf);
   return okSearch&&okProj;
 }));
}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/register")
def register_page():
    opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Register - F.I.G BRANDS</title>""" + BASE + """<div class='page'><div class='card'><div class='card-header'><div class='card-title'>Welfare Registration Form</div><div class='card-sub'>F.I.G BRANDS WELFARE - Add member with photo</div></div><div class='card-body'>
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
<div style='margin-top:12px' class='grid2'><div><label class='label'>Email *</label><input class='input' id='email' placeholder='email@figbrands.co.ke'></div><div><label class='label'>Password *</label><input class='input' id='password' type='password' placeholder='••••'></div></div>
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
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin - F.I.G BRANDS</title>""" + BASE + """<div class='page' style='max-width:400px'><div class='card'><div class='card-header'><div class='card-title'>Admin Login - F.I.G BRANDS WELFARE</div></div><div class='card-body'><label class='label'>Email</label><input class='input' id='email' value='admin@lonma.com'><div style='margin-top:12px'><label class='label'>Password</label><input class='input' id='pass' type='password' value='admin123'></div><button class='btn-primary' onclick='login()'>Login</button><p id='msg' style='text-align:center;color:#dc2626;margin-top:10px'></p></div></div></div>
<script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok){location.href='/admin/dashboard?key='+j.key;}else{document.getElementById('msg').textContent=j.error;}}</script>
</body></html>"""
    return render_template_string(html)

@app.route("/admin/dashboard")
def admin_dashboard():
    key = request.args.get("key")
    if key != ADMIN_KEY:
        return redirect("/admin")
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Admin - F.I.G BRANDS</title>""" + BASE + """<div class='page' style='max-width:1000px'><div class='card'><div class='card-header' style='display:flex;justify-content:space-between;align-items:center'><div class='card-title'>Admin - F.I.G BRANDS Welfare Management with Photos</div><a class='btn-excel' href='/download/excel'>📥 Download Excel</a></div><div style='overflow:auto'><table style='width:100%;border-collapse:collapse'><thead><tr><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Photo</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Staff & Name</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Family</th><th style='padding:10px 14px;background:#f8fafc;font-size:11px;text-align:left'>Action</th></tr></thead><tbody id='tbl'></tbody></table></div></div>
<div class='card'><div class='card-header'><div class='card-title'>📩 Support Messages</div></div><div id='supList' style='padding:10px 20px'>Loading...</div></div></div>
<script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let photo=m.photo?'<img src="'+m.photo+'" style="width:44px;height:44px;border-radius:50%;object-fit:cover">':'<div style="width:44px;height:44px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-weight:700">'+(m.full_names||'A').charAt(0)+'</div>';let btn=prot?'<span style="color:#94a3b8;font-size:12px">System</span>':'<button onclick="del('+m.id+')" style="color:#dc2626;border:1px solid #fee2e2;background:#fff;border-radius:999px;padding:5px 12px;cursor:pointer">Delete</button>';h+='<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px">'+photo+'</td><td style="padding:14px"><b>'+m.staff_no+'</b><div style="font-weight:700">'+m.full_names+'</div><div style="font-size:11px;color:#64748b">'+m.email+'</div></td><td style="padding:14px;font-size:11px">G:'+(m.guardian_id||'-')+' S:'+(m.spouse_id||'-')+'<br>Kids:'+([m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(',')||'-')+'</td><td style="padding:14px">'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;let r2=await fetch('/api/support_list');let d2=await r2.json();let h2='';if(d2.messages.length==0)h2='<div style="color:#64748b">No support messages yet</div>';else d2.messages.forEach(m=>{h2+='<div style="padding:12px 0;border-bottom:1px solid #f1f5f9"><b>'+(m.name||'Guest')+'</b> <span style="font-size:11px;color:#94a3b8">'+m.created+'</span><div style="font-size:14px">'+m.msg+'</div></div>'});document.getElementById('supList').innerHTML=h2;}async function del(id){if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?key=""" + ADMIN_KEY + """',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script>
</body></html>"""
    return render_template_string(html)

@app.route("/download/excel")
def download_excel():
    proj = request.args.get("project","")
    conn = get_db()
    try:
        if proj and proj != "All Projects":
            rows = conn.execute("SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC", (ADMIN_EMAIL, proj)).fetchall()
        else:
            rows = conn.execute("SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC", (ADMIN_EMAIL,)).fetchall()
        headers = ["Staff Number","Full Names","Project","Email","Date Joined","Father ID","Mother ID","Guardian ID","Spouse ID","Kid 1 Birth Cert","Kid 2 Birth Cert","Kid 3 Birth Cert","Kid 4 Birth Cert","Kid 5 Birth Cert"]
        try:
            from openpyxl import Workbook
            from openpyxl.styles import Font, PatternFill, Alignment
            wb = Workbook(); ws = wb.active; ws.title = "F.I.G BRANDS Members"
            ws.append(headers)
            for c in ws[1]:
                c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1565C0"); c.alignment = Alignment(horizontal="center")
            for r in rows:
                ws.append([r["staff_no"] or "", r["full_names"] or "", r["project"] or "", r["email"] or "", r["month_joined"] or "", r["father_id"] or "", r["mother_id"] or "", r["guardian_id"] or "", r["spouse_id"] or "", r["kid1"] or "", r["kid2"] or "", r["kid3"] or "", r["kid4"] or "", r["kid5"] or ""])
            for col in ws.columns:
                ws.column_dimensions[col[0].column_letter].width = 18
            ws.column_dimensions['B'].width = 28
            ws.column_dimensions['D'].width = 30
            ws.freeze_panes = "A2"
            ws.auto_filter.ref = ws.dimensions
            out = io.BytesIO(); wb.save(out); out.seek(0)
            return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="fig_brands_members.xlsx")
        except ImportError:
            out = io.StringIO(); w = csv.writer(out); w.writerow(headers)
            for r in rows:
                w.writerow([r["staff_no"] or "", r["full_names"] or "", r["project"] or "", r["email"] or "", r["month_joined"] or "", r["father_id"] or "", r["mother_id"] or "", r["guardian_id"] or "", r["spouse_id"] or "", r["kid1"] or "", r["kid2"] or "", r["kid3"] or "", r["kid4"] or "", r["kid5"] or ""])
            b = io.BytesIO(out.getvalue().encode('utf-8-sig')); b.seek(0)
            return send_file(b, mimetype="text/csv", as_attachment=True, download_name="fig_brands_members.csv")
    finally:
        conn.close()

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

@app.route("/api/breakdown")
def api_breakdown():
    conn = get_db()
    try:
        prows = conn.execute("SELECT * FROM finance_projects ORDER BY id").fetchall()
        brows = conn.execute("SELECT * FROM beneficiaries ORDER BY id").fetchall()
        frows = conn.execute("SELECT * FROM fares ORDER BY id").fetchall()
        return jsonify({"projects": [dict(r) for r in prows], "totals": list(FINANCE_TOTALS), "beneficiaries": [dict(r) for r in brows], "beneficiaries_total": BENEFICIARIES_TOTAL, "fares": [dict(r) for r in frows], "fares_total": FARES_TOTAL, "grand_total": GRAND_TOTAL, "transfer_total": TRANSFER_TOTAL, "expenditures_total": EXPENDITURES_TOTAL})
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
    proj = request.args.get("project","")
    conn = get_db()
    try:
        if proj and proj != "All Projects":
            rows = conn.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC", (ADMIN_EMAIL, proj)).fetchall()
        else:
            rows = conn.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC", (ADMIN_EMAIL,)).fetchall()
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
        api_key = "fig_"+secrets.token_hex(12)
        photo = data.get("photo","")
        if len(photo) > 500000:
            photo = photo[:500000]
        proj = PROJECT_MAP.get(data.get("project","HQ"), data.get("project","HQ"))
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (data.get("staff_no",""), data.get("full_names",""), proj, data["email"], generate_password_hash(data["password"]), api_key, data.get("month_joined",""), data.get("father_id",""), data.get("mother_id",""), data.get("guardian_id",""), data.get("spouse_id",""), data.get("kid1",""), data.get("kid2",""), data.get("kid3",""), data.get("kid4",""), data.get("kid5",""), photo))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("New Member Registered", f"{data.get('full_names','')} joined {proj}", "Just now"))
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
