# F.I.G BRANDS WELFARE - v53
# UPDATED FROM WELFARE_DATA-2_1.xlsx (TF WSL sheet, 356 rows)
# - TF WSL 13 members: family IDs corrected to match the new file (IDs, not names)
#   e.g. Pauline Murathi father 20964177 / mother 23236444, Ann Njeri mother 6106608 / spouse 23524787,
#   Jecinta Karanja father 8483221, Tabitha Wanjiku father 8040754, Catherine Mukami father 16005886, etc.
# - Diana Muse date kept as 2026 (file has Excel bug: 1905-07-18)
# - The other ~340 rows in the file are name + staff-no ONLY (no project, no joined date, no family IDs)
#   so they are NOT added as members - adding them would duplicate Pwani / Java / etc staff and break Share-Out.
#   They look like a staff directory list, not welfare registrations.
# Total members: 73 (56 + 17 Higchem) | Filter: "Higchem (17)", "Pwani Oil Products (43)", "All Projects (73)"
# Share-Out unchanged: BF 767,859 - 200,000 = 567,859 per month (Dec 2025 - Sep 2026)
from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, csv, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Higchem","TF WSL"]
PMAP = {"Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","Java":"Java House","SJ":"SJ Johnson","TF WSL":"TF WSL","TF":"TF WSL","HIGCHEM MARKETING LIMITED":"Higchem","Higchem":"Higchem","Hichem":"Higchem"}
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
BF = 767859
RESERVE = 200000
DISTRIBUTABLE = BF - RESERVE
GRAND_TOTAL = 1153000
MONTHLY_RATE = 300
PERIOD_START = (2025, 12)
PERIOD_END = (2026, 9)
# staff|project|joined|names|father|mother|guardian|spouse|k1|k2|k3|k4|k5
SEED_TXT = '''202712|Pwani|Nov.2022|Laura Imali|||0327707|37982161|112409612||||
202710|Pwani|Dec.2020|Edith Kabera|||23740423|23965879|10700481|112152616|11250650||
202677|Pwani|October.2024|Phoebe Anyango|1014509|2266278||||||||
202706|Pwani|Aug.2021|Cynthia Awuor||9892352|||1231202182||||
202707|Pwani|Nov.2021|Maureen Owino|2859205|4313510|28254592|24675501|9927L79|3300789|26057L7|9999788|
202721|Pwani|March .2023|Merceline Adhiambo|4026148|13199939||27472316|3271828||||
202705|Pwani|Marh 2019|Odiembo Yvonne||8351397|||will give later||||
202722|Pwani|Dec.2023|Linet Oduor|2828431|14479498||||||||
202746|Pwani|Nov.2025|Divyan Dorcas||13603542||||||||
202708|Pwani|Jan. 2020|Lilian Muchuma||261270|||110707451||||
202711|Pwani|Sept.2021|John Adiel||1329824|28565804|32190036||||
292932|Pwani|May.2026|Milcah Otiende|8232129|7861021||32624856|4094626||||
280370|Pwani|Sept. 2026|Lucy Mwende Mbatha|2991561|2965465|||0852106551||||
202700|Pwani Oil Products Ltd.|Mar.2025|Charles Kimutai Kirui|3872261|3872429||31045698|612112010||||
202709|Pwani Oil Products Ltd.|Mar.2025|Oyoyo Yvonne Bentar||11801824||27464418||||
202678|Pwani Oil Products Ltd.|Mar.2025|Owen Muthee Waithaka|21217575|22555615||||||||
202733|Pwani Oil Products Ltd.|Mar.2025|Sharon Cherono||11635405||||||||
202529|Pwani Oil Products Ltd.|Mar.2025|Alex Shangala|4176764|7956390||33313078|692102029|691828162||
202729|Pwani Oil Products Ltd.|Mar.2025|Rose Lumonya Saidi||4252080||||||||
202747|Pwani Oil Products Ltd.|Jul.2025|Brenda Nelima Wafula||133101||||||||
10405|Pwani Oil Products Ltd.|Mar.2025|Diana Atieno Oduor||4722494|757617564|28078423- Ben Kitui||370702896 -Dennis Adams|21506184- Joy Nelima|Samantha Malia Achieng|
202749|Pwani Oil Products Ltd.|Mar.2025|Celine Nasimiyu Wamalwa||8784757||28990208|William Musungu|Moses Musungu|Bryton Musungu|
292976|Pwani Oil Products Ltd.|Apr.2026|Belinda Chemtai||4722288|||372315084|182018971||
202702|Pwani Oil Products Ltd.|May.2025|Betty Akinyi Namamba|Fabians Namamba|Janet Atieno|||||||
202723|Pwani Oil Products Ltd.|Mar.2025|Metrine Cherop Chumo||||29934624|411700883|411506469||
50516|Pwani Oil Products Ltd.|May.2025|Sheila Adisa Volemi|VOLEMI|TERESIA|HUDSON IMBAYI|22175541||||
202701|Pwani Oil Products Ltd.|Mar.2025|Everlyne Mukoya Stephen||||23600368||671767|395330|
202703|Pwani Oil Products Ltd.|Mar.2025|Caren Nanjala Chonge||5639451||22086206|364057|6090663||
202704|Pwani Oil Products Ltd.|Mar.2025|Hellen Achieng Onyango|711723882|726994852||722618476||||
202724|Pwani Oil Products Ltd.|Mar.2025|Benta Achieng Muruka|CHRISTOPHER MURUKA|JANE MAGENGA||28687282|1311214785|21910561||
202697|Pwani|Sept.2017|Naomi Mwango Abenga|1658833|||22188003|121032026|121622654|112220451||
202696|Pwani|2015|Lydiah Nyaanga Osengo|1649626|1637770||10020853|160900879|168706540/19||
202693|Pwani|May.2022|Meggiling Abuga Nyakerario|||8647005||||160900879||
202695|Pwani|2022|Gorrety Adhiambo Otieno|9807667|26810228||30257258|2348625|2350080|3743676||
202699|Pwani|14/12/2022|Sophia Nyamoita Mokaya||6541570||27233755||||
202751|Pwani|Oct.2023|Benjamin Odiwuor Mboya|10596034|20015894||466468971|7893744||||
202730|pwani|4.8.2025|Orwa Diana Atieno|96811362|21136615||36519946||||
202694|Pwani|Jan.2020|Charles Adika|8837595|11833576||||||||
282000|Pwani|May.2026|Hyphine Chepkoech Mutai|10383876|28240917||26261936||||
202750|Pwani|May.2025|Priscah Anjemo Injili||21842168||32990585|795787|978435||
202698|Pwani|Feb.2022|Postine Atieno|7921446|8398928||38801320|122318007||||
202744|PWANI|Mar.2024|Anthony Manyara Chania|21022712|86260659||923456988||||
202683|Pwani|Mar.2013|Eunice Makona||4722288||210327239|7575163|7575161|7575162||
202914|TF WSL|20th Jan 2025|Said Roseline Heri||1319025||9765327|4408202|7758933|7108428||
202906|TF WSL|27th Mar 2025|Jecinta Karanja|8483221|11114948||30461200|1358036|614595|||
202905|TF WSL|5th Feb 2025|Mary Atieno||14438209|||001432321|4898710|||
202915|TF WSL|13th Jan 2025|Pauline Murathi|20964177|23236444||||||
202916|TF WSL|27th Jan 2025|Ann Njeri Kareiya|Deceased|6106608||23524787|9901560||||
202913|TF WSL|13th Jan 2025|Tabitha Wanjiku|8040754|10893197||33095213|37220833||||
202917|TF WSL|13th Jan 2025|Prudence Achieng Wanyangu||22482407||37155644|||||
292943|TF WSL|15/01/2026|Linda Naliaka Juma|21927102|20475201|||9655625|Notification: 6031104|||
202908|TF WSL|12th Sep 2025|Pascaline Njoki|Deceased|23429425|||645865||||
202910|TF WSL|16th Oct 2025|Lucy Nyambura||14495721||||||
292977|TF WSL|2026|Diana Muse|5675695|5301379||||||||
202907|TF WSL|22/07/2026|Janet Wairimu|10767868|13507411|||3868681||||
280293|TF WSL|13th July 2026|Catherine Mukami|16005886|16022069||24041649|361716972|Notification:5810997|||
202641|Higchem|May.2026|Irene Waeni Mwangangi|9638105|12583212|NA|NA|210865865|2616122654|||
202657|Higchem|Jun.2026|Isaac Ombati Rioba|NA|23630642|NA|31939473|371923347||||
202787|Higchem|May.2026|Emily Nanjala Wafula||||||||||
202998|Higchem|May.2026|Millianna Anyango Sadaka||||||||||
280005|Higchem|May.2026|Faith Njeri Kibungi|3121603|3589023|NA|N/A|A8858040||||
280007|Higchem|May.2026|Collins Ofula Mabwa|7421158|36301081||37416617|1442312021||||
280008|Higchem|May.2026|Wanga Atieno Beryl|||||2633392||||
280009|Higchem|May.2026|Nelson Miruka Kiyondi|8578391|21133401|NA|NA|||||
280012|Higchem|May.2026|Robert Kariuki Macharia||||||||||
280013|Higchem|May.2026|Thomas Felix Mwatu|7808718|BK758118||34661148|||||
280014|Higchem|May.2026|Mercy Nabulo Khabala|1431857|9216359|NA|26142738|392118249||||
280078|Higchem|May.2026|Joan Anyango Otewa||||||||||
280266|Higchem|Jul.2026|Anna Mbinya Kalia||||||||||
280325|Higchem|Aug.2026|Marion Waheto|||32175829|36914920|||||
280326|Higchem|Aug.2026|Maureen Wanjiru Kiarie|9745295|11241637|||CA001474219||||
280349|Higchem|Sep.2026|Wicklife Okemwa Nyangaresi|1593749|10468950||308049405|4713214||||'''
SEED_DATA = [tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
PERIODS = [
 {"label":"Period 1: Oct 2024 - Dec 2025","months":["Oct 24","Nov 24","Dec 24","Jan 25","Feb 25","Mar 25","Apr 25","May 25","Jun 25","Jul 25","Aug 25","Sep 25","Oct 25","Nov 25","Dec 25"],"totals":[98100,95400,95400,101700,108000,108000,110700,110700,104100,101700,99900,96600,86700,87000],"counts":[327,318,318,339,360,360,369,369,347,339,333,322,289,290,0],"grand":1404000,"expenditures":494625,"projects":[("Pwani",[24600,23700,22500,24900,21600,21900,21600,21300,21900,21600,21300,21300,21300,21000,0]),("Java",[8700,8400,8700,9300,7800,7800,8700,8100,9600,9300,9600,8700,9600,9300,0]),("Johnson",[10500,10800,10200,9300,9000,9000,10200,9900,10200,9900,10200,10200,10200,9600,0]),("Kaysalt",[9600,9600,9300,9600,9000,8400,8700,8700,0,0,0,0,0,0,0]),("Kanji",[900]*15),("HQ",[900,0,1800,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,0]),("GCB-MT",[5400,4800,5100,4800,4800,4800,5100,5700,4800,4800,4800,4800,5100,5100,0]),("TF-WS",[3300,3300,3000,6300,6900,6900,5700,5100,5100,5700,5400,4800,4800,4800,0]),("TF-LM",[11700,12300,12300,11700,13200,13200,12600,12600,12300,12300,12000,12000,12600,12300,0]),("TF-MT",[19200,18000,17700,19800,17700,18000,18600,18000,18900,18000,18600,18300,18600,20100,0]),("Kenafric",[0,0,0,0,11700,12000,12300,12000,12300,12000,12600,12000,0,0,0]),("GCB-TDs",[3300,3600,3900,3900,4200,3900,5100,4800,3900,3600,3300,2400,2400,2700,0]),("LAB",[0,0,0,0,0,0,0,2400,3000,2400,0,0,0,0,0])]},
 {"label":"Period 2: Dec 2025 - Oct 2026","months":["Dec 25","Jan 26","Feb 26","Mar 26","Apr 26","May 26","Jun 26","Jul 26","Aug 26","Sep 26","Oct 26"],"totals":[86700,87300,89700,89700,90000,90300,92400,92400,94800,89700,0],"counts":[289,291,299,299,300,301,308,308,316,299,0],"grand":903000,"expenditures":385141,"projects":[("Pwani",[21000,20400,21300,21000,21300,21600,21300,21600,20700,15300,0]),("Java",[9000,9600,9900,9900,9600,9300,9600,9300,9900,9900,0]),("Johnson",[10500,9600,10200,9900,9900,9300,8400,8700,8700,8100,0]),("Kanji",[900]*11),("HQ",[1200,1200,1200,1200,1200,1200,1200,1200,1500,1500,0]),("GCB-MT",[4500,4500,4800,4800,4800,4500,6000,5100,6000,5700,0]),("TF-WS",[4800,5100,4800,4800,4800,4500,4500,4200,3900,3900,0]),("TF-LM",[12300,12300,11700,11700,12600,9300,9000,9900,10200,12000,0]),("TF-MT",[19800,20700,21900,22200,21300,21300,21900,21900,22200,21900,0]),("GCB-TDs",[2700,3000,3000,3300,3600,3600,3600,3600,4800,5100,0]),("Highchem",[0,0,0,0,0,4800,5100,5100,5400,4800,0]),("Antonia",[0,0,0,0,0,0,900,900,600,600,0])]},
]
BENEFICIARIES2 = [("Period 1","Mary Ngota","GCB","Dad-Death","Nov 2024",30000),("Period 1","Mariamu","GCB","Dad-Death","Dec 2024",30000),("Period 1","Claire Osiako","Kaysalt","Dad-Death","2 Dec 2024",30000),("Period 1","Rachael Ndungu","Pwani","Mum-Death","10 Dec 2024",30000),("Period 1","Teresih Kariuki","TF","Dad-Death","17 Dec 2024",30000),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","4 Dec 2024",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Jan 2025",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Feb 2025",9500),("Period 1","(Unnamed)","SJ","Daughter-Death","",30000),("Period 1","Jecinta Nduta Karanja","TF","Loss of earning","",9000),("Period 1","Winnie","TF B","Dad-Death","",30000),("Period 1","Maureen Kiare","Kenafric","Dad-Death","July",30000),("Period 1","Eugene Otieno","TF","Dad-Death","July",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",22000),("Period 1","Mercy Mwikali","TF","Guardian","Aug 2025",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",11000),("Period 1","Annah Nthamba Musyoki","Java","Dad-Death","Sep 2025",30000),("Period 1","Eunice Wairimu Wanjiku","SJ","Dad-Death","Oct 2025",30000),("Period 1","JJJJ","","Loss of earning","",11500),("Period 1","Nostar","TF","Loss of earning","",19000),("Period 2","Rose Lumonya Saidi","POPL","Death-Father","Dec 2025",40000),("Period 2","Susan Ndungu","TF","Death-Father","26 Jan 2026",40000),("Period 2","Irene Wairimu","Java","Death-Guardian","May 2026",40000),("Period 2","Mercy Mwende","GCB","Loss of earning","May 2026",11075),("Period 2","Damarais Muyoka","TF","Death-Father","May 2026",40000),("Period 2","Ruth Amollo Nyangun","","Death-Father","Jun 2026",40000),("Period 2","Sheila Okomo","TF","Loss of earning","May",9000),("Period 2","Sheila Okomo","TF","Loss of earning","June",9000),("Period 2","(Unnamed)","TF","Death-Father","",40000),("Period 2","Vivian Moraa","Java","Loss of earning","",11000),("Period 2","Hannah Wanjiku","TF","Death-Father","17 Aug",40000)]
FARES2 = [("Period 1","Peter Ikegu","0704886421",1000),("Period 1","George Ibuba","0113964865",1000),("Period 1","Kevin Kipkurui","0704284388",1000),("Period 1","Valary Chepkoech","0713053696",1500),("Period 1","Mercy Njeri","0713881793",1500),("Period 1","Margaret Wangari","0720331094",1000),("Period 1","Mary Wangare","0796805933",1000),("Period 1","Daniel Mayaka","0722620252",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","Rose","",3000),("Period 1","Jecinta Apondi","",1000),("Period 1","Mercy Onyango","",1000),("Period 1","Preskila Ondiek","",1000),("Period 1","Jane Wangari","",1500),("Period 1","Caroline Wachira","",1500),("Period 1","Joy","",1500),("Period 1","Berbciter","",1500),("Period 1","Irene Wamuyu","0719606834",1000),("Period 1","Ann Mulema","0729218786",1000),("Period 1","Gloria Luksenaka","0796426074",1000),("Period 1","Mary Thika","0719572174",1000),("Period 1","Joshua Iguna","0792529926",1000),("Period 1","Jackline Kamau","0724562145",1000),("Latest","Eunice Makona","0714910135",1200),("Latest","Hellen Onyango","0724570228",1200),("Latest","Caren Chonge","0710427468",900),("Latest","Antony Mwendia","",1500),("Latest","Gladys Nyaga","",1500),("Latest","Marlon K. Ang'undu","",1200),("Latest","Gladys Wambaire Kinuthia","",1200),("Latest","Evapertual Wambui","",1200),("Latest","Catherine Ogutu","",1700),("Latest","Ebby Lomoi","",1700),("Latest","Jackline Ayiga","",1700),("Latest","Esther Marenya","",1600),("Latest","George Odhiambo","",1400),("Latest","Kiplimo","",4200),("Latest","Maureen Njeri Kamunyu","",1500),("Latest","Eunice Wairimu","",2000),("Latest","Victoria Wangechi Mugwe","",2000),("Latest","(Unnamed)","",500)]
MONTHLY_INDIVIDUAL = [("Oct 2024",327,98100),("Nov 2024",318,95400),("Dec 2024",318,95400),("Jan 2025",339,101700)]
def clean(v):
    if v is None: return ""
    s = str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL"): return ""
    if "will give" in s.lower(): return ""
    if "will provide" in s.lower(): return ""
    if "notification:" in s.lower(): return s.split(":",1)[1].strip()
    return s
def make_email(n, staff):
    p = [x for x in n.lower().replace(".","").split() if x.isalpha()]
    return f"{p[0]}.{p[-1]}@figbrands.co.ke" if len(p) >= 2 else f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
def parse_join(s):
    if not s: return None
    s = str(s).strip().lower()
    months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,"january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
    m = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", s)
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo > 12: d, mo = mo, d
        return (y, mo)
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})", s)
    if m:
        return (int(m.group(2)), months[m.group(1)[:3]])
    m = re.search(r"(\d{4})", s)
    if m:
        return (int(m.group(1)), 1)
    return None
def months_active(join_str):
    start_y, start_m = PERIOD_START
    end_y, end_m = PERIOD_END
    j = parse_join(join_str)
    if j:
        if (j[0], j[1]) > (start_y, start_m):
            start_y, start_m = j
    if (start_y, start_m) > (end_y, end_m):
        return 0
    return (end_y - start_y) * 12 + (end_m - start_m) + 1
def calc_shares():
    c = get_db()
    try:
        rows = c.execute("SELECT id,staff_no,full_names,project,email,month_joined FROM users WHERE email != ? ORDER BY full_names", (ADMIN_EMAIL,)).fetchall()
    finally:
        c.close()
    out = []
    for r in rows:
        months = months_active(r["month_joined"])
        contrib = months * MONTHLY_RATE
        out.append({"id": r["id"], "staff_no": r["staff_no"] or "", "full_names": r["full_names"] or "", "project": r["project"] or "", "email": r["email"] or "", "month_joined": r["month_joined"] or "", "months": months, "contribution": contrib, "share": 0.0, "per_month": 0.0})
    total_months = sum(x["months"] for x in out)
    total_contrib = sum(x["contribution"] for x in out)
    per_month_rate = DISTRIBUTABLE / total_months if total_months else 0
    for x in out:
        x["per_month"] = round(per_month_rate, 2)
        x["share"] = round(x["months"] * per_month_rate, 2)
    diff = round(DISTRIBUTABLE - sum(x["share"] for x in out), 2)
    if out and diff != 0:
        out.sort(key=lambda x: x["share"], reverse=True)
        out[0]["share"] = round(out[0]["share"] + diff, 2)
    out.sort(key=lambda x: x["share"], reverse=True)
    return out, total_contrib, total_months, per_month_rate
def get_db():
    c = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None)
    c.row_factory = sqlite3.Row
    try:
        c.execute("PRAGMA journal_mode=WAL;"); c.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return c
def init_db():
    c = get_db()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS beneficiaries2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, project TEXT, reason TEXT, date_str TEXT, amount REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS fares2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, phone TEXT, amount REAL)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    if not c.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    if not c.execute("SELECT id FROM notifications").fetchone():
        c.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Welcome to F.I.G BRANDS Welfare","Your welfare system is active.","Now"))
        c.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Share-Out: BF less 200,000","BF 767,859 less 200,000 = 567,859 shared per month of contributions.","Now"))
    # v53: TF WSL corrections - if a seed staff_no already exists, update its family/joined/project fields
    # (Render DB persists, so seed-insert alone would NOT overwrite old TF WSL rows)
    added = 0
    for r in SEED_DATA:
        staff, proj_raw, month, names, father, mother, guardian, spouse, k1, k2, k3, k4, k5 = r
        staff = clean(staff); names = clean(names)
        if not staff or not names: continue
        project = PMAP.get(proj_raw, proj_raw)
        vals = (names, project, clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5))
        existing = c.execute("SELECT id FROM users WHERE staff_no=?", (staff,)).fetchone()
        if existing:
            c.execute("UPDATE users SET full_names=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE staff_no=?", vals + (staff,))
            continue
        email = make_email(names, staff)
        if c.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone():
            email = f"member.{staff}@figbrands.co.ke"
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (staff, names, project, email, generate_password_hash(staff), "fig_"+secrets.token_hex(12), clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5), ""))
        added += 1
    if not c.execute("SELECT id FROM beneficiaries2").fetchone():
        for per,n,p,r2,d,a in BENEFICIARIES2:
            c.execute("INSERT INTO beneficiaries2 (period,name,project,reason,date_str,amount) VALUES (?,?,?,?,?,?)", (per,n,p,r2,d,a))
    if not c.execute("SELECT id FROM fares2").fetchone():
        for per,n,ph,a in FARES2:
            c.execute("INSERT INTO fares2 (period,name,phone,amount) VALUES (?,?,?,?)", (per,n,ph,a))
    c.commit(); c.close()
    print(f"Seeded {added} new members - total seed {len(SEED_DATA)}")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
    return r
@app.route("/favicon.ico")
def favicon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="14" fill="#0A2540"/><text x="32" y="42" font-family="Arial" font-size="24" font-weight="800" fill="white" text-anchor="middle">FIG</text></svg>'
    return svg, 200, {"Content-Type": "image/svg+xml"}
BASE = '''<style>@import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap');:root{--navy:#0A2540;--ink:#101828;--muted:#667085;--line:#E6EBF2;--bg:#F2F4F7;--green:#067647;--red:#C81E1E;--radius:16px}*{margin:0;padding:0;box-sizing:border-box}body{font-family:'Inter',system-ui,sans-serif;background:var(--bg);color:var(--ink);-webkit-font-smoothing:antialiased;padding-bottom:76px}.topbar{height:60px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:space-between;gap:10px;padding:0 10px 0 8px;position:sticky;top:0;z-index:40}.topbar-left{display:flex;align-items:center;gap:10px;min-width:0;flex:1}.menu-btn{flex:0 0 38px;width:38px;height:38px;border-radius:11px;background:rgba(255,255,255,.12);border:1px solid rgba(255,255,255,.16);color:#fff;font-size:19px;cursor:pointer;display:flex;align-items:center;justify-content:center}.logo{flex:0 0 36px;width:36px;height:36px;border-radius:11px;background:#fff;color:var(--navy);display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:800}.brand{min-width:0;line-height:1.2}.brand b{display:block;font-size:14.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.brand span{display:block;font-size:9px;letter-spacing:1.9px;text-transform:uppercase;opacity:.72;white-space:nowrap}.topbar-right{display:flex;gap:8px;flex:0 0 auto}.icon-btn{width:37px;height:37px;border-radius:999px;background:rgba(255,255,255,.12);display:flex;align-items:center;justify-content:center;cursor:pointer;position:relative}.icon-btn svg{width:19px;height:19px;stroke:#fff;fill:none;stroke-width:1.8}.badge{position:absolute;top:-3px;right:-3px;background:#E11D48;color:#fff;font-size:10px;font-weight:700;min-width:18px;height:18px;border-radius:999px;display:flex;align-items:center;justify-content:center;padding:0 4px}.overlay{position:fixed;inset:0;background:rgba(2,6,23,.48);z-index:50;display:none}.overlay.show{display:block}.sidebar{position:fixed;top:0;left:0;width:312px;max-width:88vw;height:100dvh;background:#fff;z-index:60;transform:translateX(-102%);transition:transform .28s cubic-bezier(.2,.8,.2,1);display:flex;flex-direction:column;box-shadow:0 16px 48px rgba(0,0,0,.22);border-radius:0 20px 20px 0;overflow:hidden}.sidebar.open{transform:translateX(0)}.sidebar-head{padding:18px 18px 14px;display:flex;align-items:center;justify-content:space-between;border-bottom:1px solid var(--line)}.sidebar-head .who{display:flex;gap:12px;align-items:center;min-width:0}.avatar{flex:0 0 46px;width:46px;height:46px;border-radius:50%;background:linear-gradient(135deg,#0A2540,#0E6B4A);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px}.who b{display:block;font-size:14.5px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.who span{display:block;font-size:11.5px;color:var(--muted);white-space:nowrap;overflow:hidden;text-overflow:ellipsis;margin-top:2px}.role-pill{display:inline-block;margin-top:6px;font-size:10px;font-weight:700;letter-spacing:.6px;text-transform:uppercase;background:#ECFDF3;color:#067647;padding:3px 8px;border-radius:999px}.close-btn{flex:0 0 34px;width:34px;height:34px;border-radius:999px;border:1px solid var(--line);background:#fff;font-size:15px;cursor:pointer;color:#475467}.menu-list{flex:1;overflow:auto;padding:14px 12px 8px}.nav-label{font-size:10.5px;font-weight:700;letter-spacing:1.2px;text-transform:uppercase;color:#98A2B3;padding:10px 12px 6px}.menu-item{display:flex;gap:12px;align-items:center;padding:11px 12px;border-radius:12px;font-size:14px;font-weight:600;color:#344054;text-decoration:none;margin-bottom:2px}.menu-item:hover{background:#F2F4F7}.menu-item.active{background:#0A2540;color:#fff}.menu-item.active .ico{background:rgba(255,255,255,.18);color:#fff}.menu-item.active .chev{opacity:1}.ico{flex:0 0 36px;width:36px;height:36px;border-radius:10px;background:#EEF2F6;color:#0A2540;display:flex;align-items:center;justify-content:center;font-size:16px}.menu-item .txt{flex:1;min-width:0}.menu-item .sub{display:block;font-size:11.5px;font-weight:500;color:#98A2B3;margin-top:1px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis}.menu-item.active .sub{color:rgba(255,255,255,.75)}.chev{font-size:16px;color:#98A2B3;opacity:0}.mini-badge{background:#FEE4E2;color:#B42318;font-size:11px;font-weight:700;padding:2px 7px;border-radius:999px}.sidebar-foot{padding:14px;border-top:1px solid var(--line)}.share-mini{background:#F8FAFC;border:1px solid var(--line);border-radius:13px;padding:12px 13px}.share-mini .l{font-size:10.5px;font-weight:700;letter-spacing:.8px;text-transform:uppercase;color:var(--muted)}.share-mini .v{font-size:18px;font-weight:800;margin-top:5px}.share-mini .bar{height:7px;background:#E6EBF2;border-radius:999px;overflow:hidden;margin:10px 0 6px;display:flex}.logout{display:flex;gap:10px;align-items:center;justify-content:center;width:100%;margin-top:10px;padding:12px;border-radius:12px;border:1px solid #FECDC2;background:#FEF3F2;color:#B42318;font-weight:700;font-size:14px;cursor:pointer;text-decoration:none}.foot-note{display:flex;justify-content:space-between;padding:10px 4px 0;font-size:11px;color:#98A2B3;font-weight:600}.page{max-width:1080px;margin:0 auto;padding:18px 14px 10px}.page-head{margin:4px 2px 16px}.page-head h1{font-size:26px;font-weight:800;letter-spacing:-.4px}.page-head p{font-size:13.5px;color:var(--muted);margin-top:7px;line-height:1.55;max-width:640px}.card{background:#fff;border:1px solid var(--line);border-radius:var(--radius);overflow:hidden;margin-bottom:13px;box-shadow:0 1px 2px rgba(16,24,40,.05)}.card-header{padding:16px 18px;border-bottom:1px solid #F1F5F9;display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap}.card-title{font-weight:700;font-size:15px}.card-sub{font-size:12px;color:var(--muted);margin-top:3px}.card-body{padding:18px}.input{width:100%;height:44px;border:1px solid #D9E1EC;border-radius:11px;padding:0 14px;font-size:14px;outline:none;background:#fff}.input:focus{border-color:var(--navy);box-shadow:0 0 0 3px rgba(10,37,64,.12)}.label{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;letter-spacing:.6px;margin-bottom:7px;display:block}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}.section{margin:22px 0 12px;font-size:12px;font-weight:800;text-transform:uppercase;letter-spacing:.6px;color:#334155}.btn-primary{width:100%;height:48px;background:var(--navy);color:#fff;border:none;border-radius:11px;font-weight:700;font-size:14px;cursor:pointer}.btn-dark{display:inline-flex;align-items:center;gap:8px;background:var(--navy);color:#fff;padding:10px 16px;border-radius:11px;font-weight:600;font-size:13px;text-decoration:none;border:none;cursor:pointer;white-space:nowrap}.btn-green{display:inline-flex;align-items:center;gap:8px;background:var(--green);color:#fff;padding:10px 16px;border-radius:11px;font-weight:600;font-size:13px;text-decoration:none;border:none;cursor:pointer;white-space:nowrap}.kpi-grid{display:grid;grid-template-columns:1fr 1fr;gap:12px;margin-bottom:13px}.kpi{background:#fff;border:1px solid var(--line);border-radius:var(--radius);padding:16px;display:flex;flex-direction:column;justify-content:space-between;min-height:118px;box-shadow:0 1px 2px rgba(16,24,40,.05)}.kpi-label{font-size:10.5px;font-weight:700;color:var(--muted);text-transform:uppercase;letter-spacing:.7px;line-height:1.35;min-height:28px}.kpi-value{font-size:23px;font-weight:800;letter-spacing:-.4px;margin:8px 0 6px;line-height:1;white-space:nowrap}.kpi-value small{font-size:12px;font-weight:700;color:var(--muted);margin-right:4px}.kpi-note{font-size:12px;color:var(--muted);line-height:1.35}.kpi.accent{border-top:3px solid var(--navy)}.kpi.success{border-top:3px solid var(--green)}.kpi.danger{border-top:3px solid var(--red)}.hero{background:linear-gradient(135deg,#0A2540 0%,#14365E 58%,#0E6B4A 100%);color:#fff;border-radius:18px;padding:20px;margin-bottom:13px;overflow:hidden}.hero-label{font-size:10.5px;letter-spacing:1.6px;text-transform:uppercase;opacity:.75;font-weight:700}.hero-value{font-size:34px;font-weight:800;letter-spacing:-.6px;margin:10px 0 4px;line-height:1}.hero-value small{font-size:15px;font-weight:700;opacity:.8}.hero-sub{font-size:13px;opacity:.82;line-height:1.5}.sharebar{display:flex;height:10px;border-radius:999px;overflow:hidden;background:rgba(255,255,255,.22);margin:16px 0 10px}.sharebar i{display:block}.legend{display:flex;gap:16px;flex-wrap:wrap;font-size:12px}.legend b{font-weight:700}.dot{width:9px;height:9px;border-radius:999px;display:inline-block;vertical-align:middle;margin-right:6px}.formula{background:#F8FAFC;border:1px solid var(--line);border-radius:13px;padding:14px 16px;font-size:13px;color:#334155;line-height:1.6;margin-bottom:13px}.formula b{color:var(--ink)}.photo-box{width:110px;height:110px;border-radius:999px;border:2px dashed #CBD5E1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#F8FAFC;cursor:pointer;text-align:center}.photo-box img{width:100%;height:100%;object-fit:cover}.popup{position:fixed;inset:0;background:rgba(2,6,23,.45);z-index:100;display:none;align-items:flex-end;justify-content:center}.popup.show{display:flex}.popup-card{background:#fff;width:100%;max-width:520px;border-radius:20px 20px 0 0;max-height:84vh;overflow:auto;padding-bottom:20px}.popup-head{padding:18px 20px;display:flex;justify-content:space-between;align-items:center;border-bottom:1px solid #EEF2F7}.notif-item{padding:16px 20px;border-bottom:1px solid #F8FAFC}.support-opt{display:flex;gap:14px;padding:16px;border:1px solid var(--line);border-radius:12px;margin-bottom:10px;cursor:pointer}.cred-row{display:flex;justify-content:space-between;gap:16px;padding:8px 0;border-bottom:1px dashed #EEF2F7;font-size:13px}.cred-row span:first-child{color:var(--muted)}.cred-row span:last-child{font-weight:600;text-align:right}table.fin{width:100%;border-collapse:collapse;font-size:13px}table.fin th{padding:12px 14px;background:#F8FAFC;text-align:left;font-size:11px;font-weight:700;text-transform:uppercase;letter-spacing:.5px;color:#475569;white-space:nowrap}table.fin td{padding:12px 14px;border-bottom:1px solid #EEF2F7;vertical-align:top}table.fin tr:hover td{background:#F8FAFC}table.fin tr.total td{font-weight:800;background:#EDF2F9}.num{text-align:right;font-variant-numeric:tabular-nums;white-space:nowrap}.pill{display:inline-block;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;background:#EDF2F9;color:var(--navy);white-space:nowrap}.totals{padding:16px 20px;border-top:1px solid var(--line)}.totals>div{display:flex;justify-content:space-between;gap:12px;padding:6px 0;font-size:14px}.totals .grand{font-weight:800;font-size:15px;border-top:1px solid var(--line);margin-top:8px;padding-top:12px}.bottomnav{position:fixed;left:12px;right:12px;bottom:12px;height:62px;background:#0A2540;border-radius:18px;display:flex;z-index:40;padding:6px;box-shadow:0 12px 32px rgba(10,37,64,.35)}.bottomnav a{flex:1;display:flex;flex-direction:column;align-items:center;justify-content:center;gap:2px;text-decoration:none;color:rgba(255,255,255,.65);font-size:10px;font-weight:700;border-radius:13px}.bottomnav a.active{background:#fff;color:#0A2540}.bottomnav a i{font-size:18px;font-style:normal}.proj-row{display:flex;justify-content:space-between;gap:12px;align-items:center;padding:16px 4px;border-bottom:1px solid #F1F5F9}.proj-row:last-child{border-bottom:none}.proj-row b{font-size:16px;font-weight:500;color:#101828}.proj-row span{font-size:16px;font-weight:700}.proj-bar{height:6px;background:#EDF2F9;border-radius:999px;overflow:hidden;margin-top:7px}.proj-bar i{display:block;height:100%;background:var(--navy);border-radius:999px}@media(min-width:760px){.page{padding:22px 20px 10px}.kpi-grid{grid-template-columns:repeat(3,1fr)}.hero{padding:24px}.hero-value{font-size:40px}.bottomnav{display:none}body{padding-bottom:0}}@media(max-width:420px){.kpi-value{font-size:21px}.brand b{font-size:13px}}@media print{.topbar,.sidebar,.popup,.overlay,.bottomnav{display:none!important}body{padding-bottom:0}.page{max-width:none;padding:0}.card,.kpi{box-shadow:none;break-inside:avoid}}</style><div class="topbar"><div class="topbar-left"><button class="menu-btn" onclick="openMenu()" aria-label="Menu">&#9776;</button><div class="logo">FIG</div><div class="brand"><b>F.I.G BRANDS</b><span>Welfare System</span></div></div><div class="topbar-right"><div class="icon-btn" onclick="openBell()" aria-label="Notifications"><svg viewBox="0 0 24 24"><path d="M18 8a6 6 0 0 0-12 0c0 7-3 9-3 9h18s-3-2-3-9"/><path d="M13.7 21a2 2 0 0 1-3.4 0"/></svg><span class="badge" id="bellBadge">3</span></div><div class="icon-btn" onclick="openSupport()" aria-label="Support"><svg viewBox="0 0 24 24"><path d="M3 18v-6a9 9 0 0 1 18 0v6"/><rect x="3" y="14" width="4" height="7" rx="1.5"/><rect x="17" y="14" width="4" height="7" rx="1.5"/></svg></div></div></div><div class="overlay" id="overlay" onclick="closeMenu()"></div><div class="sidebar" id="sidebar"><div class="sidebar-head"><div class="who"><div class="avatar">FA</div><div><b>F.I.G Admin</b><span>admin@lonma.com</span><span class="role-pill">Administrator</span></div></div><button class="close-btn" onclick="closeMenu()" aria-label="Close">&times;</button></div><div class="menu-list"><div class="nav-label">Main</div><a class="menu-item" href="/"><span class="ico">&#8962;</span><span class="txt">Overview<span class="sub">Dashboard &amp; KPIs</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/members"><span class="ico">&#128101;</span><span class="txt">Members<span class="sub">73 registered members</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/register"><span class="ico">+</span><span class="txt">Register Member<span class="sub">Add new member</span></span><span class="chev">&rsaquo;</span></a><div class="nav-label">Finance</div><a class="menu-item" href="/shareout"><span class="ico">KES</span><span class="txt">Share-Out<span class="sub">BF less 200,000 &middot; 567,859</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/breakdown2"><span class="ico">&#128200;</span><span class="txt">Full History<span class="sub">Periods, beneficiaries</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/breakdown"><span class="ico">&#128176;</span><span class="txt">Breakdown / Finance<span class="sub">Monthly breakdown</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/download/excel"><span class="ico">&#8681;</span><span class="txt">Download Excel<span class="sub">Members export</span></span><span class="chev">&rsaquo;</span></a><div class="nav-label">Support</div><a class="menu-item" href="#" onclick="openBell();return false"><span class="ico">&#128276;</span><span class="txt">Notifications<span class="sub">Latest updates</span></span><span class="mini-badge">3</span></a><a class="menu-item" href="#" onclick="openSupport();return false"><span class="ico">&#127911;</span><span class="txt">Contact Support<span class="sub">WhatsApp &amp; email</span></span><span class="chev">&rsaquo;</span></a><a class="menu-item" href="/admin"><span class="ico">&#9881;</span><span class="txt">Settings<span class="sub">Admin &amp; dashboard</span></span><span class="chev">&rsaquo;</span></a></div><div class="sidebar-foot"><div class="share-mini"><div class="l">Share-Out Progress</div><div class="v">KES 567,859 <span style="font-size:12px;color:#667085;font-weight:600">/ 767,859 BF</span></div><div class="bar"><i style="width:74%;background:#067647"></i><i style="width:26%;background:#FDB022"></i></div><div style="font-size:11.5px;color:#667085">74% to share &middot; 26% retained</div></div><a class="logout" href="/admin">&#10132; Log Out</a><div class="foot-note"><span>F.I.G BRANDS WELFARE</span><span>v53</span></div></div></div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="popup-card"><div class="popup-head"><div><div style="font-weight:800">Notifications</div><div style="font-size:12px;color:#667085" id="notifCount"></div></div><button onclick="closeBell()" style="width:32px;height:32px;border-radius:999px;border:none;cursor:pointer">X</button></div><div id="notifList"></div><div style="padding:0 20px"><button onclick="markRead()" style="width:100%;height:44px;border-radius:10px;border:1px solid #E6EBF2;background:#fff;font-weight:700;cursor:pointer">Mark all as read</button></div></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="popup-card"><div class="popup-head"><div><div style="font-weight:800">Contact Support</div><div style="font-size:12px;color:#667085">We reply within 1 hour</div></div><button onclick="closeSupport()" style="width:32px;height:32px;border-radius:999px;border:none;cursor:pointer">X</button></div><div style="padding:18px 20px"><div class="support-opt" onclick="window.open('https://wa.me/254707780807?text=Hi F.I.G BRANDS Support','_blank')"><div><b>WhatsApp Support</b><div style="font-size:12px;color:#667085">0707 780 807</div></div></div><div class="support-opt" onclick="window.location.href='mailto:info@figbrands.co.ke'"><div><b>Email Support</b><div style="font-size:12px;color:#667085">info@figbrands.co.ke</div></div></div><label class="label">Your Name</label><input class="input" id="supName"><div style="margin-top:12px"><label class="label">Message</label><textarea id="supMsg" style="width:100%;height:90px;border:1px solid #E6EBF2;border-radius:10px;padding:12px"></textarea></div><button class="btn-primary" onclick="sendSupport()">Send Message</button><p id="supStatus" style="text-align:center;margin-top:10px"></p></div></div></div><nav class="bottomnav"><a href="/" data-nav="/"><i>&#8962;</i>Home</a><a href="/members" data-nav="/members"><i>&#128101;</i>Members</a><a href="/shareout" data-nav="/shareout"><i>KES</i>Share-Out</a><a href="/breakdown2" data-nav="/breakdown2"><i>&#128200;</i>History</a><a href="/register" data-nav="/register"><i>+</i>Add</a></nav><script>function openMenu(){document.getElementById('sidebar').classList.add('open');document.getElementById('overlay').classList.add('show')}function closeMenu(){document.getElementById('sidebar').classList.remove('open');document.getElementById('overlay').classList.remove('show')}async function openBell(){closeMenu();document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{h+='<div class="notif-item"><div><b>'+n.title+'</b><div style="font-size:13px;color:#475569;margin-top:3px">'+n.msg+'</div><div style="font-size:11px;color:#98A2B3;margin-top:4px">'+n.created+'</div></div></div>'});document.getElementById('notifList').innerHTML=h;document.getElementById('notifCount').textContent=d.notifications.length+' notifications';}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}function markRead(){document.getElementById('bellBadge').style.display='none';document.getElementById('notifList').innerHTML='<div style="padding:30px;text-align:center;color:#067647;font-weight:700">All read</div>';}function openSupport(){closeMenu();document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let name=document.getElementById('supName').value;let msg=document.getElementById('supMsg').value;if(!msg){document.getElementById('supStatus').textContent='Please write a message';return;}let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,msg:msg})});let j=await r.json();document.getElementById('supStatus').textContent=j.message;document.getElementById('supMsg').value='';}document.addEventListener('DOMContentLoaded',()=>{let p=location.pathname;document.querySelectorAll('.menu-item').forEach(a=>{if(a.getAttribute('href')===p)a.classList.add('active')});document.querySelectorAll('.bottomnav a').forEach(a=>{if(a.getAttribute('data-nav')===p)a.classList.add('active')})})</script>'''
MEMBER_BASE = BASE.replace('F.I.G Admin','F.I.G Member').replace('admin@lonma.com','info@figbrands.co.ke').replace('FA</div>','ME</div>').replace('Administrator','Member')
@app.route("/")
def home():
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>F.I.G BRANDS Welfare</title>''' + BASE + '''<div class="page"><div class="page-head"><h1>Overview</h1><p>Welfare contributions, share-out and member records. Share-out is BF less KES 200,000, allocated per month of contributions.</p></div><div class="kpi-grid"><div class="kpi"><div class="kpi-label">Total Members</div><div class="kpi-value" id="total" style="font-size:36px">0</div><div class="kpi-note">Registered members</div></div><div class="kpi"><div class="kpi-label">Projects</div><div class="kpi-value" id="projCount" style="font-size:36px">0</div><div class="kpi-note">All projects</div></div><div class="kpi"><div class="kpi-label">Status</div><div class="kpi-value" style="color:#067647;font-size:36px">Active</div><div class="kpi-note">System is live</div></div></div><div class="hero"><div class="hero-label">Balance Brought Forward &middot; Dec 2025 - Sep 2026</div><div class="hero-value"><small>KES</small>767,859</div><div class="hero-sub">KES 567,859 to share &middot; KES 200,000 retained in account</div><div class="sharebar"><i style="width:74%;background:#34D399"></i><i style="width:26%;background:#FBBF24"></i></div><div class="legend"><span><span class="dot" style="background:#34D399"></span><b>74%</b> To share</span><span><span class="dot" style="background:#FBBF24"></span><b>26%</b> Retained</span></div></div><div class="kpi-grid"><div class="kpi success"><div class="kpi-label">Amount to Share</div><div class="kpi-value" style="color:#067647"><small>KES</small>567,859</div><div class="kpi-note">BF less 200,000</div></div><div class="kpi danger"><div class="kpi-label">Retained in Account</div><div class="kpi-value" style="color:#C81E1E"><small>KES</small>200,000</div><div class="kpi-note">Reserve - not shared</div></div><div class="kpi"><div class="kpi-label">Value of One Month</div><div class="kpi-value"><small>KES</small>1,111.27</div><div class="kpi-note">567,859 / 511 months</div></div></div><div class="card"><div class="card-header"><div><div class="card-title">Share-Out Summary</div><div class="card-sub">BF 767,859 - 200,000 = 567,859 &middot; 10 months at KES 300 per month</div></div><a class="btn-dark" href="/shareout">View Share-Out</a></div></div><div class="card"><div class="card-header"><div><div class="card-title" style="font-size:19px">Project Distribution</div><div class="card-sub" id="projSub">Members per project</div></div></div><div class="card-body" id="breakdown" style="padding:4px 18px 10px"></div><div style="padding:0 18px 16px;display:flex;justify-content:space-between;font-size:13px;color:#667085;border-top:1px solid #F1F5F9;padding-top:12px"><span id="projTotalLabel">Total</span><b id="projTotal" style="color:#101828;font-size:15px">0</b></div></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('projTotal').textContent=d.total_members;document.getElementById('projTotalLabel').textContent='Total Members ('+d.projects_total+' projects)';let hq=d.projects_breakdown['HQ']||0;document.getElementById('projSub').textContent='Members per project (HQ '+hq+')';let names=Object.keys(d.projects_breakdown).sort((a,b)=>a.localeCompare(b));let h='';names.forEach(k=>{let n=d.projects_breakdown[k]||0;h+='<div class="proj-row"><b>'+k+'</b><span>'+n+'</span></div>';});document.getElementById('breakdown').innerHTML=h;}load();</script></body></html>'''
    return render_template_string(html)
@app.route("/breakdown")
def breakdown_page():
    return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
    h = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Full History - F.I.G BRANDS</title>''' + BASE + '''<div class="page"><div class="page-head"><h1>Full History</h1><p>Monthly contributions by project, beneficiaries and fares.</p></div><div class="kpi-grid"><div class="kpi"><div class="kpi-label">Period 1 &middot; Oct 2024 - Dec 2025</div><div class="kpi-value"><small>KES</small>1,404,000</div><div class="kpi-note">Expenditures 494,625</div></div><div class="kpi"><div class="kpi-label">Period 2 &middot; Dec 2025 - Oct 2026</div><div class="kpi-value"><small>KES</small>903,000</div><div class="kpi-note">Expenditures 385,141</div></div><div class="kpi"><div class="kpi-label">Beneficiaries (Unique)</div><div class="kpi-value" style="color:#C81E1E"><small>KES</small>781,075</div><div class="kpi-note">31 beneficiaries</div></div><div class="kpi"><div class="kpi-label">Grand Total</div><div class="kpi-value"><small>KES</small>1,153,000</div><div class="kpi-note">2026 file</div></div><div class="kpi"><div class="kpi-label">Transfer</div><div class="kpi-value"><small>KES</small>673,270</div><div class="kpi-note">Bank transfers</div></div><div class="kpi"><div class="kpi-label">Pwani BF / End of Year</div><div class="kpi-value" style="font-size:20px">767,859 / 517,859</div><div class="kpi-note">From WALFARE_API_DATA.xlsx</div></div></div>'''
    h += '''<div class="card"><div class="card-header"><div class="card-title">Monthly Individual Contributions</div><div class="card-sub">KES 300 per member per month</div></div><div style="padding:6px 18px 14px">'''
    for m,c,t in MONTHLY_INDIVIDUAL:
        h += f"<div style='display:flex;justify-content:space-between;gap:12px;padding:10px 0;border-bottom:1px dashed #EEF2F7'><span><b>{m}</b> &middot; {c} members</span><b>KES {t:,}</b></div>"
    h += "</div></div>"
    for p in PERIODS:
        h += f"<div class='card'><div class='card-header'><div><div class='card-title'>{p['label']}</div><div class='card-sub'>Expenditures: KES {p['expenditures']:,} &middot; Total: KES {p['grand']:,}</div></div></div><div style='overflow:auto'><table class='fin'><thead><tr><th>Project</th>"
        for mo in p['months']:
            h += f"<th class='num'>{mo}</th>"
        h += "<th class='num'>Total</th></tr></thead><tbody>"
        for name, vals in p['projects']:
            h += f"<tr><td><b>{name}</b></td>" + "".join([f"<td class='num'>{v:,}</td>" for v in vals]) + f"<td class='num'><b>{sum(vals):,}</b></td></tr>"
        h += "<tr class='total'><td>Total</td>" + "".join([f"<td class='num'>{v:,} ({p['counts'][i]})</td>" for i,v in enumerate(p['totals'])]) + f"<td class='num'>{p['grand']:,}</td></tr></tbody></table></div></div>"
    h += "<div class='card'><div class='card-header'><div class='card-title'>Beneficiaries &middot; KES 781,075 (31 unique)</div><div class='card-sub'>Period 1: 461,000 + Period 2 new: 320,075</div></div><div style='padding:6px 18px 14px'>"
    for per,n,pr,r2,d,a in BENEFICIARIES2:
        h += f"<div style='display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px dashed #EEF2F7;font-size:13px'><span><b>{n}</b> <span style='color:#667085'>&middot; {per} &middot; {pr} &middot; {r2} &middot; {d}</span></span><b>KES {a:,}</b></div>"
    h += "</div></div><div class='card'><div class='card-header'><div class='card-title'>Fares</div><div class='card-sub'>Period 1: 30,000 &middot; Latest: 28,200</div></div><div style='padding:6px 18px 14px'>"
    for per,n,ph,a in FARES2:
        h += f"<div style='display:flex;justify-content:space-between;gap:12px;padding:9px 0;border-bottom:1px dashed #EEF2F7;font-size:13px'><span><b>{n}</b> <span style='color:#667085'>&middot; {per} &middot; {ph}</span></span><b>KES {a:,}</b></div>"
    h += "</div></div></div></body></html>"
    return render_template_string(h)
@app.route("/shareout")
def shareout_page():
    shares, total_contrib, total_months, per_month_rate = calc_shares()
    total_shares = sum(x["share"] for x in shares)
    h = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Share-Out - F.I.G BRANDS</title>''' + BASE + f'''<div class="page"><div class="page-head"><h1>Share-Out</h1><p>Balance Brought Forward less KES 200,000, shared per month of contributions. Period: Dec 2025 - Sep 2026 (10 months) &middot; KES 300 per month.</p></div><div class="hero"><div class="hero-label">Amount to Share</div><div class="hero-value"><small>KES</small>567,859</div><div class="hero-sub">BF 767,859 &minus; 200,000 retained &middot; 1 month = KES {per_month_rate:,.2f}</div><div class="sharebar"><i style="width:74%;background:#34D399"></i><i style="width:26%;background:#FBBF24"></i></div><div class="legend"><span><span class="dot" style="background:#34D399"></span><b>74%</b> To share</span><span><span class="dot" style="background:#FBBF24"></span><b>26%</b> Retained</span></div></div><div class="formula"><b>Formula:</b> Share = Months Contributed &times; (KES 567,859 / Total Months of All Members)<br><b>Reconciliation:</b> Total Shares (KES {total_shares:,.2f}) + Retained (KES 200,000) = BF (KES 767,859). Rounding difference is applied to the largest share so the total reconciles exactly.</div><div class="kpi-grid"><div class="kpi"><div class="kpi-label">Members</div><div class="kpi-value">{len(shares)}</div><div class="kpi-note">Sharing members</div></div><div class="kpi"><div class="kpi-label">Total Months</div><div class="kpi-value">{total_months}</div><div class="kpi-note">All members combined</div></div><div class="kpi"><div class="kpi-label">Value of One Month</div><div class="kpi-value"><small>KES</small>{per_month_rate:,.2f}</div><div class="kpi-note">567,859 / {total_months}</div></div><div class="kpi"><div class="kpi-label">Total Contributions</div><div class="kpi-value"><small>KES</small>{total_contrib:,}</div><div class="kpi-note">{total_months} months &times; KES 300</div></div><div class="kpi"><div class="kpi-label">Total Shares</div><div class="kpi-value"><small>KES</small>{total_shares:,.2f}</div><div class="kpi-note">Reconciles to 567,859</div></div><div class="kpi success"><div class="kpi-label">Reconciliation Check</div><div class="kpi-value"><small>KES</small>{total_shares + RESERVE:,.0f}</div><div class="kpi-note">Shares + Retained = BF</div></div></div>'''
    h += '''<div class="card"><div class="card-header"><div><div class="card-title">Member Share-Out Schedule</div><div class="card-sub">Largest share first. Members who joined later have fewer months and a smaller share.</div></div><a class="btn-green" href="/download/shareout">Download Excel</a></div><div style="padding:14px 18px"><input class="input" id="q" placeholder="Search by name, staff number or project" oninput="fil()"></div><div style="overflow:auto"><table class="fin"><thead><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share Payable</th></tr></thead><tbody id="shareBody">'''
    for i, x in enumerate(shares, 1):
        h += f"<tr data-search='{(x['full_names'] + ' ' + x['staff_no'] + ' ' + x['project']).lower()}'><td>{i}</td><td><b>{x['full_names']}</b><div style='font-size:11px;color:#667085;margin-top:2px'>{x['staff_no']} &middot; {x['email']}</div></td><td><span class='pill'>{x['project']}</span></td><td>{x['month_joined'] or '-'}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>"
    h += f"</tbody></table></div><div class='totals'><div><span>Total to Share</span><b>KES {total_shares:,.2f}</b></div><div><span>Retained in Account</span><b>KES {RESERVE:,}</b></div><div class='grand'><span>Balance Brought Forward</span><span>KES {total_shares + RESERVE:,.0f}</span></div></div></div></div>"
    h += '''<script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(r=>{r.style.display=r.getAttribute('data-search').includes(q)?'':'none';});}</script></body></html>'''
    return render_template_string(h)
@app.route("/download/shareout")
def download_shareout():
    shares, total_contrib, total_months, per_month_rate = calc_shares()
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); ws = wb.active; ws.title = "Share-Out"
    ws.append(["F.I.G BRANDS WELFARE - SHARE-OUT SCHEDULE"])
    ws.append(["BF less 200,000 shared per month of contributions"])
    ws.append([f"BF: {BF:,} | Retained: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Months: {total_months} | Value of One Month: {per_month_rate:,.2f} | Total Contributions: {total_contrib:,}"])
    ws.append([])
    ws.append(["#","Staff No","Full Names","Project","Date Joined","Months Contributed","Contribution (Months x 300)","Share Payable"])
    for c in ws[5]:
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0A2540"); c.alignment = Alignment(horizontal="center", vertical="center")
    for i, x in enumerate(shares, 1):
        ws.append([i, x["staff_no"], x["full_names"], x["project"], x["month_joined"], x["months"], x["contribution"], round(x["share"], 2)])
    ws.append([]); ws.append(["","","","","","TOTAL", total_contrib, round(sum(x["share"] for x in shares), 2)])
    ws.append(["","","","","","RETAINED IN ACCOUNT","", RESERVE])
    ws.append(["","","","","","BALANCE BROUGHT FORWARD","", round(sum(x["share"] for x in shares), 2) + RESERVE])
    ws.freeze_panes = "A6"; ws.auto_filter.ref = ws.dimensions
    for col, w in zip("ABCDEFGH", [6, 14, 30, 22, 14, 18, 20, 20]):
        ws.column_dimensions[col].width = w
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
@app.route("/members")
def members_page():
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - F.I.G BRANDS</title>''' + MEMBER_BASE + '''<div class="page"><div class="page-head"><h1>Members</h1><p>Registered member credentials. Filter shows how many members are registered in each project.</p></div><div class="card"><div class="card-header"><div><div class="card-title">Member Records</div><div class="card-sub" id="memberCountLabel">Search by name, staff number or project</div></div><a class="btn-green" href="/download/excel">Download Excel</a></div><div style="padding:14px 18px;display:flex;gap:10px"><input class="input" id="q" placeholder="Search by name, staff number, project" oninput="fil()" style="flex:2"><select class="input" id="projFilter" onchange="fil()" style="flex:1"><option value="All Projects">All Projects</option></select></div><div id="list" style="padding:0 18px 16px"></div></div></div><script>let all=[];let counts={};async function loadCounts(){try{let r=await fetch('/api/stats');let d=await r.json();counts=d.projects_breakdown||{};let total=d.total_members||0;document.getElementById('memberCountLabel').textContent=total+' members registered - filter shows count per project';let sel=document.getElementById('projFilter');let cur=sel.value;sel.innerHTML='<option value="All Projects">All Projects ('+total+')</option>';(d.projects||Object.keys(counts)).forEach(p=>{let n=counts[p]||0;let o=document.createElement('option');o.value=p;o.textContent=p+' ('+n+')';sel.appendChild(o);});sel.value=cur;}catch(e){}}async function load(){await loadCounts();let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function row(l,v){return '<div class="cred-row"><span>'+l+'</span><span>'+(v||'-')+'</span></div>';}function render(l){let h='';if(l.length==0)h='<div style="padding:30px;text-align:center;color:#667085">No members found in this project</div>';else l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<div style="background:#fff;border:1px solid #E6EBF2;border-radius:14px;padding:18px;margin-bottom:12px"><div style="display:flex;justify-content:space-between;gap:12px"><div><div style="font-weight:700">'+m.full_names+'</div><div style="font-size:12px;color:#667085">'+m.email+'</div></div><span class="pill">'+m.project+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID No.',m.guardian_id)+row('Spouse ID No.',m.spouse_id)+row('Kids Birth Certificates',kids)+'</div>';});document.getElementById('list').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;let filtered=all.filter(m=>{let s=(m.full_names+' '+m.staff_no+' '+m.project+' '+(m.guardian_id||'')+' '+(m.spouse_id||'')).toLowerCase().includes(qq);let p=(pf=='All Projects'||m.project==pf);return s&&p;});render(filtered);}load();</script></body></html>'''
    return render_template_string(html)
@app.route("/register")
def register_page():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - F.I.G BRANDS</title>''' + BASE + '''<div class="page"><div class="page-head"><h1>Register Member</h1><p>Add a new member with photo and family records.</p></div><div class="card"><div class="card-header"><div class="card-title">Welfare Registration Form</div></div><div class="card-body"><div style="display:flex;gap:20px;align-items:center;margin-bottom:20px"><div class="photo-box" id="photoBox" onclick="document.getElementById('photoInput').click()"><img id="photoPreview" style="display:none"><div id="photoPlaceholder"><div style="font-size:14px;color:#667085">Add Photo</div></div></div><div><b>Member Photo</b><div style="font-size:12px;color:#667085;margin-top:4px">Select a photo - Max 2MB, JPG or PNG</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div></div><div class="section">1. Staff Information</div><div class="grid2"><div><label class="label">Staff Number</label><input class="input" id="staff_no"></div><div><label class="label">Project</label><select class="input" id="project">''' + opts + '''</select></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Date Joined</label><input class="input" id="month_joined"></div><div><label class="label">Full Names</label><input class="input" id="full_names"></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Email</label><input class="input" id="email"></div><div><label class="label">Password</label><input class="input" id="password" type="password"></div></div><div class="section">2. Parents IDs</div><div class="grid2"><div><label class="label">Father ID</label><input class="input" id="father_id"></div><div><label class="label">Mother ID</label><input class="input" id="mother_id"></div></div><div class="section">3. Guardian and Spouse</div><div class="grid2"><div><label class="label">Guardian ID No.</label><input class="input" id="guardian_id"></div><div><label class="label">Spouse ID No.</label><input class="input" id="spouse_id"></div></div><div class="section">4. Kids Birth Certificates</div><div class="grid3"><div><label class="label">Kid 1</label><input class="input" id="kid1"></div><div><label class="label">Kid 2</label><input class="input" id="kid2"></div><div><label class="label">Kid 3</label><input class="input" id="kid3"></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Kid 4</label><input class="input" id="kid4"></div><div><label class="label">Kid 5</label><input class="input" id="kid5"></div></div><button class="btn-primary" onclick="doReg()" id="btn">Create Member</button><p id="msg" style="text-align:center;margin-top:10px"></p></div></div></div><script>let photoBase64="";function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>2*1024*1024){alert('File too large');return;}let r=new FileReader();r.onload=function(ev){photoBase64=ev.target.result;document.getElementById('photoPreview').src=photoBase64;document.getElementById('photoPreview').style.display='block';document.getElementById('photoPlaceholder').style.display='none';};r.readAsDataURL(f);}async function doReg(){let btn=document.getElementById('btn');btn.textContent='Creating...';let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value,photo:photoBase64};if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';btn.textContent='Create Member';return;}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;btn.textContent=r.ok?'Created':'Create Member';if(r.ok)setTimeout(()=>location.href='/members',800);}</script></body></html>'''
    return render_template_string(html)
@app.route("/admin")
def admin_login_page():
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - F.I.G BRANDS</title>''' + BASE + '''<div class="page" style="max-width:420px"><div class="page-head"><h1>Admin Login</h1></div><div class="card"><div class="card-body"><label class="label">Email</label><input class="input" id="email" value="admin@lonma.com"><div style="margin-top:12px"><label class="label">Password</label><input class="input" id="pass" type="password" value="admin123"></div><button class="btn-primary" onclick="login()" style="margin-top:16px">Login</button><p id="msg" style="text-align:center;color:#C81E1E;margin-top:10px"></p></div></div></div><script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok)location.href='/admin/dashboard?key='+j.key;else document.getElementById('msg').textContent=j.error;}</script></body></html>'''
    return render_template_string(html)
@app.route("/admin/dashboard")
def admin_dashboard():
    if request.args.get("key") != ADMIN_KEY:
        return redirect("/admin")
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - F.I.G BRANDS</title>''' + BASE + '''<div class="page"><div class="page-head"><h1>Admin Dashboard</h1><p>Manage members and support messages.</p></div><div class="card"><div class="card-header"><div class="card-title">Members</div><a class="btn-green" href="/download/excel">Download Excel</a></div><div style="overflow:auto"><table style="width:100%;border-collapse:collapse"><thead><tr><th style="padding:12px;text-align:left">Photo</th><th style="padding:12px;text-align:left">Staff and Name</th><th style="padding:12px;text-align:left">Family</th><th style="padding:12px;text-align:left">Action</th></tr></thead><tbody id="tbl"></tbody></table></div></div><div class="card"><div class="card-header"><div class="card-title">Support Messages</div></div><div id="supList" style="padding:10px 20px">Loading...</div></div></div><script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let photo=m.photo?'<img src="'+m.photo+'" style="width:44px;height:44px;border-radius:999px;object-fit:cover">':'<div style="width:44px;height:44px;border-radius:999px;background:#EEF2F7;display:flex;align-items:center;justify-content:center;font-weight:700">'+(m.full_names||'A').charAt(0)+'</div>';let btn=prot?'<span>System</span>':'<button onclick="del('+m.id+')" style="color:#C81E1E;border:1px solid #FECACA;background:#fff;border-radius:999px;padding:5px 12px;cursor:pointer">Delete</button>';h+='<tr style="border-bottom:1px solid #EEF2F7"><td style="padding:10px">'+photo+'</td><td style="padding:14px"><b>'+m.staff_no+'</b><div style="font-weight:700">'+m.full_names+'</div><div style="font-size:11px;color:#667085">'+m.email+'</div></td><td style="padding:14px;font-size:11px">G:'+(m.guardian_id||'-')+' S:'+(m.spouse_id||'-')+'<br>Kids:'+([m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(',')||'-')+'</td><td style="padding:14px">'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;let r2=await fetch('/api/support_list');let d2=await r2.json();let h2='';if(d2.messages.length==0)h2='No messages';else d2.messages.forEach(m=>{h2+='<div style="padding:12px 0;border-bottom:1px solid #EEF2F7"><b>'+(m.name||'Guest')+'</b> <span style="font-size:11px;color:#98A2B3">'+m.created+'</span><div>'+m.msg+'</div></div>'});document.getElementById('supList').innerHTML=h2;}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key=''' + ADMIN_KEY + '''',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script></body></html>'''
    return render_template_string(html)
@app.route("/download/excel")
def download_excel():
    proj = request.args.get("project","")
    c = get_db()
    try:
        q = "SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"
        a = (ADMIN_EMAIL,)
        if proj and proj != "All Projects":
            q = "SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a = (ADMIN_EMAIL, proj)
        rows = c.execute(q, a).fetchall()
        headers = ["Staff Number","Full Names","Project","Email","Date Joined","Father ID","Mother ID","Guardian ID","Spouse ID","Kid 1","Kid 2","Kid 3","Kid 4","Kid 5"]
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = Workbook(); ws = wb.active; ws.title = "Members"; ws.append(headers)
        for cell in ws[1]:
            cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="0A2540"); cell.alignment = Alignment(horizontal="center")
        for r in rows:
            ws.append([r[x] or "" for x in ["staff_no","full_names","project","email","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]])
        ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
        out = io.BytesIO(); wb.save(out); out.seek(0)
        return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_BRANDS_Members.xlsx")
    finally:
        c.close()
@app.route("/api/stats")
def api_stats():
    c = get_db()
    try:
        total = c.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        b = {}
        for p in PROJECTS:
            b[p] = c.execute("SELECT COUNT(*) FROM users WHERE project=? AND email != ?", (p, ADMIN_EMAIL)).fetchone()[0]
        return jsonify({"total_members": total, "projects_total": len(PROJECTS), "projects": PROJECTS, "projects_breakdown": b})
    finally:
        c.close()
@app.route("/api/breakdown")
def api_breakdown():
    c = get_db()
    try:
        brows = c.execute("SELECT * FROM beneficiaries2 ORDER BY id").fetchall()
        frows = c.execute("SELECT * FROM fares2 ORDER BY id").fetchall()
        return jsonify({"periods": PERIODS, "monthly_individual": MONTHLY_INDIVIDUAL, "beneficiaries": [dict(r) for r in brows], "beneficiaries_total": 781075, "fares": [dict(r) for r in frows], "grand_total": GRAND_TOTAL, "bf": BF, "transfer_total": 673270})
    finally:
        c.close()
@app.route("/api/shareout")
def api_shareout():
    shares, total_contrib, total_months, per_month_rate = calc_shares()
    return jsonify({"bf": BF, "reserve": RESERVE, "distributable": DISTRIBUTABLE, "total_contributions": total_contrib, "total_months": total_months, "per_month_rate": round(per_month_rate, 2), "members": len(shares), "total_shares": round(sum(x["share"] for x in shares), 2), "shares": shares})
@app.route("/api/notifications")
def api_notifs():
    c = get_db()
    try:
        rows = c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
        return jsonify({"notifications": [dict(r) for r in rows]})
    finally:
        c.close()
@app.route("/api/support", methods=["POST"])
def api_support():
    d = request.get_json(silent=True) or {}
    c = get_db()
    try:
        c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))", (d.get("name","Guest"), d.get("msg",""))); c.commit()
        return jsonify({"message": "Message sent. Support will reply soon."})
    finally:
        c.close()
@app.route("/api/support_list")
def api_support_list():
    c = get_db()
    try:
        rows = c.execute("SELECT * FROM support_msgs ORDER BY id DESC").fetchall()
        return jsonify({"messages": [dict(r) for r in rows]})
    finally:
        c.close()
@app.route("/api/members")
def api_members():
    proj = request.args.get("project","")
    c = get_db()
    try:
        q = "SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"; a = (ADMIN_EMAIL,)
        if proj and proj != "All Projects":
            q = "SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a = (ADMIN_EMAIL, proj)
        rows = c.execute(q, a).fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        c.close()
@app.route("/api/members_admin")
def api_members_admin():
    c = get_db()
    try:
        rows = c.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users ORDER BY id DESC").fetchall()
        return jsonify({"members": [dict(r) for r in rows]})
    finally:
        c.close()
@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    d = request.get_json(silent=True)
    c = get_db()
    try:
        u = c.execute("SELECT password,api_key FROM users WHERE email=?", (d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"], d.get("password","")):
            return jsonify({"error": "Invalid"}), 401
        return jsonify({"key": u["api_key"]})
    finally:
        c.close()
@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS":
        return "", 200
    d = request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"):
        return jsonify({"error": "Email and password required"}), 400
    c = get_db()
    try:
        if c.execute("SELECT id FROM users WHERE email=?", (d["email"],)).fetchone():
            return jsonify({"error": "Email exists"}), 400
        photo = d.get("photo","")
        if len(photo) > 500000:
            photo = photo[:500000]
        proj = PMAP.get(d.get("project","HQ"), d.get("project","HQ"))
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", (d.get("staff_no",""), d.get("full_names",""), proj, d["email"], generate_password_hash(d["password"]), "fig_"+secrets.token_hex(12), d.get("month_joined",""), d.get("father_id",""), d.get("mother_id",""), d.get("guardian_id",""), d.get("spouse_id",""), d.get("kid1",""), d.get("kid2",""), d.get("kid3",""), d.get("kid4",""), d.get("kid5",""), photo))
        c.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("New Member Registered", f"{d.get('full_names','')} joined {proj}", "Just now"))
        c.commit()
        return jsonify({"message": "Member created"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        c.close()
@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS":
        return "", 200
    if request.args.get("key") != ADMIN_KEY:
        return jsonify({"error": "Admin key required"}), 401
    c = get_db()
    try:
        u = c.execute("SELECT email FROM users WHERE id=?", (member_id,)).fetchone()
        if not u or u["email"] == ADMIN_EMAIL:
            return jsonify({"error": "Cannot delete Protected Admin"}), 403
        c.execute("DELETE FROM users WHERE id=?", (member_id,)); c.commit()
        return jsonify({"message": "Deleted"})
    finally:
        c.close()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
