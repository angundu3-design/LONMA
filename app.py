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
# --- BREAKDOWN v44 - F.I.G_WALFARE_UPDATES.xlsx ---
# Period 1: Oct24-Dec25 (14 months), Period 2: Dec25-Oct26 (10 months, Dec25 is overlap/correction)
PERIODS = [
 {"label":"Period 1: Oct 2024 - Dec 2025","months":["Oct24","Nov24","Dec24","Jan25","Feb25","Mar25","Apr25","May25","Jun25","Jul25","Aug25","Sep25","Oct25","Nov25","Dec25"],"totals":[98100,95400,95400,101700,108000,108000,110700,110700,104100,101700,99900,96600,86700,87000],"counts":[327,318,318,339,360,360,369,369,347,339,333,322,289,290,0],"grand":1404000,"expenditures":494625,
  "projects":[("Pwani",[24600,23700,22500,24900,21600,21900,21600,21300,21900,21600,21300,21300,21300,21000,0]),("Java",[8700,8400,8700,9300,7800,7800,8700,8100,9600,9300,9600,8700,9600,9300,0]),("Johnson",[10500,10800,10200,9300,9000,9000,10200,9900,10200,9900,10200,10200,10200,9600,0]),("Kaysalt",[9600,9600,9300,9600,9000,8400,8700,8700,0,0,0,0,0,0,0]),("Kanji",[900]*15),("HQ",[900,0,1800,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,0]),("GCB-MT",[5400,4800,5100,4800,4800,4800,5100,5700,4800,4800,4800,4800,5100,5100,0]),("TF-WS",[3300,3300,3000,6300,6900,6900,5700,5100,5100,5700,5400,4800,4800,4800,0]),("TF-LM",[11700,12300,12300,11700,13200,13200,12600,12600,12300,12300,12000,12000,12600,12300,0]),("TF-MT",[19200,18000,17700,19800,17700,18000,18600,18000,18900,18000,18600,18300,18600,20100,0]),("Kenafric",[0,0,0,0,11700,12000,12300,12000,12300,12000,12600,12000,0,0,0]),("GCB-TDs",[3300,3600,3900,3900,4200,3900,5100,4800,3900,3600,3300,2400,2400,2700,0]),("LAB",[0,0,0,0,0,0,0,2400,3000,2400,0,0,0,0,0])]},
 {"label":"Period 2: Dec 2025 - Oct 2026","months":["Dec25","Jan26","Feb26","Mar26","Apr26","May26","Jun26","Jul26","Aug26","Sep26","Oct26"],"totals":[86700,87300,89700,89700,90000,90300,92400,92400,94800,89700,0],"counts":[289,291,299,299,300,301,308,308,316,299,0],"grand":903000,"expenditures":385141,
  "projects":[("Pwani",[21000,20400,21300,21000,21300,21600,21300,21600,20700,15300,0]),("Java",[9000,9600,9900,9900,9600,9300,9600,9300,9900,9900,0]),("Johnson",[10500,9600,10200,9900,9900,9300,8400,8700,8700,8100,0]),("Kanji",[900]*11),("HQ",[1200,1200,1200,1200,1200,1200,1200,1200,1500,1500,0]),("GCB-MT",[4500,4500,4800,4800,4800,4500,6000,5100,6000,5700,0]),("TF-WS",[4800,5100,4800,4800,4800,4500,4500,4200,3900,3900,0]),("TF-LM",[12300,12300,11700,11700,12600,9300,9000,9900,10200,12000,0]),("TF-MT",[19800,20700,21900,22200,21300,21300,21900,21900,22200,21900,0]),("GCB-TDs",[2700,3000,3000,3300,3600,3600,3600,3600,4800,5100,0]),("Highchem",[0,0,0,0,0,4800,5100,5100,5400,4800,0]),("Antonia",[0,0,0,0,0,0,900,900,600,600,0])]},
]
# Beneficiaries unique - Period1 461000 (20) + Period2 new 320075 (11, Nostar dup removed) = 781075
BENEFICIARIES2 = [
 ("Period 1","Mary Ngota","GCB","Dad-Death","Nov 2024",30000),("Period 1","Mariamu","GCB","Dad-Death","Dec 2024",30000),("Period 1","Claire Osiako","Kaysalt","Dad-Death","2 Dec 2024",30000),("Period 1","Rachael Ndungu","Pwani","Mum-Death","10 Dec 2024",30000),("Period 1","Teresih Kariuki","TF","Dad-Death","17 Dec 2024",30000),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","4 Dec 2024",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Jan 2025",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Feb 2025",9500),("Period 1","(Unnamed)","SJ","Daughter-Death","",30000),("Period 1","Jecinta Nduta Karanja","TF","Loss of earning","",9000),("Period 1","Winnie","TF B","Dad-Death","",30000),("Period 1","Maureen Kiare","Kenafric","Dad-Death","July",30000),("Period 1","Eugene Otieno","TF","Dad-Death","July",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",22000),("Period 1","Mercy Mwikali","TF","Guardian","Aug 2025",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",11000),("Period 1","Annah Nthamba Musyoki","Java","Dad-Death","Sep 2025",30000),("Period 1","Eunice Wairimu Wanjiku","SJ","Dad-Death","Oct 2025",30000),("Period 1","JJJJ","","Loss of earning","",11500),("Period 1","Nostar","TF","Loss of earning","",19000),
 ("Period 2","Rose Lumonya Saidi","POPL","Death-Father","Dec 2025",40000),("Period 2","Susan Ndungu","TF","Death-Father","26 Jan 2026",40000),("Period 2","Irene Wairimu","Java","Death-Guardian","May 2026",40000),("Period 2","Mercy Mwende","GCB","Loss of earning","May 2026",11075),("Period 2","Damarais Muyoka","TF","Death-Father","May 2026",40000),("Period 2","Ruth Amollo Nyangun","","Death-Father","Jun 2026",40000),("Period 2","Sheila Okomo","TF","Loss of earning","May",9000),("Period 2","Sheila Okomo","TF","Loss of earning","June",9000),("Period 2","(Unnamed)","TF","Death-Father","",40000),("Period 2","Vivian Moraa","Java","Loss of earning","",11000),("Period 2","Hannah Wanjiku","TF","Death-Father","17 Aug",40000),
]
# Fares - Period1 30000 (25) / Latest 28200 (18, incl 5 new)
FARES2 = [
 ("Period 1","Peter Ikegu","0704886421",1000),("Period 1","George Ibuba","0113964865",1000),("Period 1","Kevin Kipkurui","0704284388",1000),("Period 1","Valary Chepkoech","0713053696",1500),("Period 1","Mercy Njeri","0713881793",1500),("Period 1","Margaret Wangari","0720331094",1000),("Period 1","Mary Wangare","0796805933",1000),("Period 1","Daniel Mayaka","0722620252",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","Rose","",3000),("Period 1","Jecinta Apondi","",1000),("Period 1","Mercy Onyango","",1000),("Period 1","Preskila Ondiek","",1000),("Period 1","Jane Wangari","",1500),("Period 1","Caroline Wachira","",1500),("Period 1","Joy","",1500),("Period 1","Berbciter","",1500),("Period 1","Irene Wamuyu","0719606834",1000),("Period 1","Ann Mulema","0729218786",1000),("Period 1","Gloria Luksenaka","0796426074",1000),("Period 1","Mary Thika","0719572174",1000),("Period 1","Joshua Iguna","0792529926",1000),("Period 1","Jackline Kamau","0724562145",1000),
 ("Latest","Eunice Makona","0714910135",1200),("Latest","Hellen Onyango","0724570228",1200),("Latest","Caren Chonge","0710427468",900),("Latest","Antony Mwendia","",1500),("Latest","Gladys Nyaga","",1500),("Latest","Marlon K. Ang'undu","",1200),("Latest","Gladys Wambaire Kinuthia","",1200),("Latest","Evapertual Wambui","",1200),("Latest","Catherine Ogutu","",1700),("Latest","Ebby Lomoi","",1700),("Latest","Jackline Ayiga","",1700),("Latest","Esther Marenya","",1600),("Latest","George Odhiambo","",1400),("Latest","Kiplimo","",4200),("Latest","Maureen Njeri Kamunyu","",1500),("Latest","Eunice Wairimu","",2000),("Latest","Victoria Wangechi Mugwe","",2000),("Latest","(Unnamed)","",500),
]
MONTHLY_INDIVIDUAL = [("Oct 2024",327,98100),("Nov 2024",318,95400),("Dec 2024",318,95400),("Jan 2025",339,101700)]
GRAND_TOTAL = 1153000
TRANSFER_TOTAL = 673270
BENEFICIARIES_TOTAL = 781075

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
    conn.execute('CREATE TABLE IF NOT EXISTS beneficiaries2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, project TEXT, reason TEXT, date_str TEXT, amount REAL)')
    conn.execute('CREATE TABLE IF NOT EXISTS fares2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, phone TEXT, amount REAL)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try: conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    if not conn.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        conn.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    if not conn.execute("SELECT id FROM notifications").fetchone():
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Welcome to F.I.G BRANDS WELFARE","Your welfare system is active. HQ 0 - ready to register members.","Now"))
        conn.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Full History Added","Oct 2024-Oct 2026 breakdown - 1,404,000 + 903,000, beneficiaries 781,075.","Now"))
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
    if not conn.execute("SELECT id FROM beneficiaries2").fetchone():
        for per,n,p,r,d,a in BENEFICIARIES2:
            conn.execute("INSERT INTO beneficiaries2 (period,name,project,reason,date_str,amount) VALUES (?,?,?,?,?,?)", (per,n,p,r,d,a))
    if not conn.execute("SELECT id FROM fares2").fetchone():
        for per,n,ph,a in FARES2:
            conn.execute("INSERT INTO fares2 (period,name,phone,amount) VALUES (?,?,?,?)", (per,n,ph,a))
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
table.fin{width:100%;border-collapse:collapse;font-size:12px}table.fin th{padding:8px 6px;background:#f8fafc;text-align:left;font-size:10px;white-space:nowrap}table.fin td{padding:8px 6px;border-bottom:1px solid #f1f5f9;white-space:nowrap}table.fin tr.total td{font-weight:800;background:#e3f2fd}
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
<div class='stat-grid'><div class='stat'><div class='stat-l'>Total Members</div><div class='stat-v' id='total'>0</div></div><div class='stat'><div class='stat-l'>Grand Total</div><div class='stat-v' style='font-size:20px'>Ksh 1,153,000</div></div><div class='stat'><div class='stat-l'>Period 1 Oct24-Dec25</div><div class='stat-v' style='font-size:20px;color:#16a34a'>Ksh 1,404,000</div></div></div>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Period 2 Dec25-Oct26</div><div class='stat-v' style='font-size:20px;color:#16a34a'>Ksh 903,000</div></div><div class='stat'><div class='stat-l'>Beneficiaries Unique</div><div class='stat-v' style='font-size:20px;color:#dc2626'>Ksh 781,075</div></div><div class='stat'><div class='stat-l'>Status</div><div class='stat-v' style='color:#16a34a'>Active</div></div></div>
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
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1'><title>Breakdown - F.I.G BRANDS</title>""" + BASE + """<div class='page' style='max-width:1100px'>
<div class='stat-grid'><div class='stat'><div class='stat-l'>Grand Total (2026 file)</div><div class='stat-v' style='font-size:20px'>Ksh 1,153,000</div></div><div class='stat'><div class='stat-l'>Transfer</div><div class='stat-v' style='font-size:20px'>Ksh 673,270</div></div><div class='stat'><div class='stat-l'>Pwani BF / End Yr</div><div class='stat-v' style='font-size:20px'>909,375 / 659,375</div></div></div>
<div class='card'><div class='card-header'><div class='card-title'>👥 Monthly Individual - 300 each</div><div class='card-sub'>Oct 2024 - Jan 2025 verified from individual sheets</div></div><div id='indiv' style='padding:6px 20px 16px'></div></div>
<div id='periods'></div>
<div class='card'><div class='card-header'><div class='card-title'>🎁 Beneficiaries - Unique Ksh 781,075</div><div class='card-sub'>Period 1: 461,000 (20) + Period 2 new: 320,075 (11) - Nostar 19,000 dup removed</div></div><div id='benList' style='padding:6px 20px 16px'></div></div>
<div class='card'><div class='card-header'><div class='card-title'>🚌 Fares</div><div class='card-sub'>Period 1: 30,000 (25) | Latest: 28,200 (18)</div></div><div id='fareList' style='padding:6px 20px 16px'></div></div>
</div>
<script>
function fmt(n){return Number(n).toLocaleString()}
async function load(){let r=await fetch('/api/breakdown');let d=await r.json();
let ih='';d.monthly_individual.forEach(m=>{ih+='<div style="display:flex;justify-content:space-between;padding:10px 0;border-bottom:1px dashed #f1f5f9;font-size:14px"><span><b>'+m[0]+'</b> - '+m[1]+' people x 300</span><b>Ksh '+fmt(m[2])+'</b></div>';});document.getElementById('indiv').innerHTML=ih;
let ph='';d.periods.forEach(p=>{let cols=p.months.map(m=>'<th>'+m+'</th>').join('');let rows='';p.projects.forEach(pr=>{let tot=pr[1].reduce((a,b)=>a+b,0);rows+='<tr><td><b>'+pr[0]+'</b></td>'+pr[1].map(v=>'<td>'+fmt(v)+'</td>').join('')+'<td><b>'+fmt(tot)+'</b></td></tr>';});let totRow='<tr class="total"><td>TOTAL</td>'+p.totals.map((v,i)=>'<td>'+fmt(v)+' ('+(p.counts[i]||'')+')</td>').join('')+'<td>'+fmt(p.grand)+'</td></tr>';ph+='<div class="card"><div class="card-header"><div class="card-title">💰 '+p.label+' - Ksh '+fmt(p.grand)+'</div><div class="card-sub">Expenditures: Ksh '+fmt(p.expenditures)+'</div></div><div style="overflow:auto"><table class="fin"><thead><tr><th>Project</th>'+cols+'<th>Total</th></tr></thead><tbody>'+rows+totRow+'</tbody></table></div></div>';});document.getElementById('periods').innerHTML=ph;
let bh='';let cur='';d.beneficiaries.forEach(b=>{if(b.period!==cur){cur=b.period;bh+='<div style="font-weight:800;margin:14px 0 4px">'+cur+'</div>';}bh+='<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #f1f5f9;font-size:13px"><span><b>'+b.name+'</b> <span style="color:#64748b">- '+b.project+' - '+b.reason+' - '+b.date_str+'</span></span><b>Ksh '+fmt(b.amount)+'</b></div>';});bh+='<div style="display:flex;justify-content:space-between;padding:12px 0;font-weight:800"><span>TOTAL UNIQUE</span><span>Ksh '+fmt(d.beneficiaries_total)+'</span></div>';document.getElementById('benList').innerHTML=bh;
let fh='';let cur2='';d.fares.forEach(f=>{if(f.period!==cur2){cur2=f.period;fh+='<div style="font-weight:800;margin:14px 0 4px">'+cur2+'</div>';}fh+='<div style="display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #f1f5f9;font-size:13px"><span><b>'+f.name+'</b> <span style="color:#64748b">'+(f.phone||'')+'</span></span><b>Ksh '+fmt(f.amount)+'</b></div>';});document.getElementById('fareList').innerHTML=fh;}
load();
</script>
</body></html>"""
    return render_template_string(html)

@app.route("/members")
def members_page():
    proj_opts = "".join(['<option value="%s">%s</option>' % (p,p) for p in ["All Projects"]+PROJECTS])
    html = """<!DOCTYPE html><html><head><meta name='viewport' content='width=device-width,initial-scale=1
