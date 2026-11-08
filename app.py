# 🎉 F.I.G BRANDS WELFARE SYSTEM - v45 - SHARE-OUT 💸
# 💡 RULE: Leave Ksh 200,000 in account, share the REST by contribution
# 🧮 FORMULA: Member Share = (Member Contribution / Total Contributions) x Distributable
# 💰 Distributable = Grand Total (1,153,000) - Reserve (200,000) = 953,000
# 📊 Member Contribution = 300 per month x months active (every project = 300/month in file - verified!)
# ✅ Check: Sum(Shares) + Reserve = Grand Total
from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, csv, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonio","TF-TDs","TF-MT","TF-LM","GCB-MT","GCB-Ws","Hichem","TF WSL"]
PMAP = {"Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","Java":"Java House","SJ":"SJ Johnson","TF WSL":"TF WSL","TF":"TF WSL"}
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
# 💰 SHARE-OUT SETTINGS - change these 2 numbers only!
GRAND_TOTAL = 1153000  # 🏦 Grand Total from WALFARE_API_DATA.xlsx
RESERVE = 200000  # 🔒 Amount to LEAVE in account
DISTRIBUTABLE = GRAND_TOTAL - RESERVE  # 💸 Amount to SHARE = 953,000
MONTHLY_RATE = 300  # 💵 Every member pays 300/month - verified in every project/month
# 📅 Share-out period: Dec 2025 - Sep 2026 (10 months, Oct 2026 = 0 in file)
PERIOD_START = (2025, 12)  # 🗓️ Dec 2025
PERIOD_END = (2026, 9)  # 🗓️ Sep 2026
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
202914|TF WSL|20th Jan 2025|Said Roseline Heri|Musa Bin Said|Beatrice N. Munoko|1319025|9765327|4408202|7758933|7108428||
202906|TF WSL|27th Mar 2025|Jecinta Karanja|KARANJA NDUNG'U|PAULINE NJOKI|11114948|30461200|1358036|614595||
202905|TF WSL|5th Feb 2025|Mary Atieno||Mary Atieno Onyango|14438209||001432321|4898710||
202915|TF WSL|2025|Pauline Murathi|George Murathi|Jane Nungari|23236444|||||
202916|TF WSL|Jan.2027|Ann Njeri Kareiya|STEPHEN KAREIYA|JENNIFER WANGUI|32317216|23524787|9901560|||
202913|TF WSL|Jan.2025|Tabitha Wanjiku|David Karugah|Grace David|10893197|33095213|37220833|||
202917|TF WSL|13th Jan 2025|Prudence Achieng Wanyangu||WILFRIDA ADHIAMBO WANYANGU|22482407|37155644||||
292943|TF WSL|15/01/2026|Linda Naliaka Juma|SIMON KARIUKI|Jane Jareda|24928699||9655625|6031104||
202908|TF WSL|2025|Pascaline Njoki|Joseph Wachira Ngigi (deceased)|Lucy Wanjiru Njogu|38761889||645865|||
202910|TF WSL|16th Oct 2025|Lucy Nyambura||Eddah Wanjiru|14495721|||||
292977|TF WSL|2026|Diana Muse|Fanuel Muse|Regina Kaveza|28385461|||||
202907|TF WSL|22/07/2026|Janet Wairimu|Joseph Waiganjo Kariuki|Grace Muthakyi Kimanzi|10767868||3868681|||
280293|TF WSL|13th July 2026|Catherine Mukami|Andrew Kiruja|Naomi Adrew||24041649|361716972|5810997||'''
SEED_DATA = [tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
# 📊 PERIODS - from WALFARE_API_DATA.xlsx + F.I.G_WALFARE_UPDATES.xlsx
PERIODS = [
 {"label":"Period 1: Oct 2024 - Dec 2025","months":["Oct24","Nov24","Dec24","Jan25","Feb25","Mar25","Apr25","May25","Jun25","Jul25","Aug25","Sep25","Oct25","Nov25","Dec25"],"totals":[98100,95400,95400,101700,108000,108000,110700,110700,104100,101700,99900,96600,86700,87000],"counts":[327,318,318,339,360,360,369,369,347,339,333,322,289,290,0],"grand":1404000,"expenditures":494625,"projects":[("Pwani",[24600,23700,22500,24900,21600,21900,21600,21300,21900,21600,21300,21300,21300,21000,0]),("Java",[8700,8400,8700,9300,7800,7800,8700,8100,9600,9300,9600,8700,9600,9300,0]),("Johnson",[10500,10800,10200,9300,9000,9000,10200,9900,10200,9900,10200,10200,10200,9600,0]),("Kaysalt",[9600,9600,9300,9600,9000,8400,8700,8700,0,0,0,0,0,0,0]),("Kanji",[900]*15),("HQ",[900,0,1800,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,0]),("GCB-MT",[5400,4800,5100,4800,4800,4800,5100,5700,4800,4800,4800,4800,5100,5100,0]),("TF-WS",[3300,3300,3000,6300,6900,6900,5700,5100,5100,5700,5400,4800,4800,4800,0]),("TF-LM",[11700,12300,12300,11700,13200,13200,12600,12600,12300,12300,12000,12000,12600,12300,0]),("TF-MT",[19200,18000,17700,19800,17700,18000,18600,18000,18900,18000,18600,18300,18600,20100,0]),("Kenafric",[0,0,0,0,11700,12000,12300,12000,12300,12000,12600,12000,0,0,0]),("GCB-TDs",[3300,3600,3900,3900,4200,3900,5100,4800,3900,3600,3300,2400,2400,2700,0]),("LAB",[0,0,0,0,0,0,0,2400,3000,2400,0,0,0,0,0])]},
 {"label":"Period 2: Dec 2025 - Oct 2026 - WALFARE_API_DATA.xlsx","months":["Dec25","Jan26","Feb26","Mar26","Apr26","May26","Jun26","Jul26","Aug26","Sep26","Oct26"],"totals":[86700,87300,89700,89700,90000,90300,92400,92400,94800,89700,0],"counts":[289,291,299,299,300,301,308,308,316,299,0],"grand":903000,"expenditures":385141,"projects":[("Pwani",[21000,20400,21300,21000,21300,21600,21300,21600,20700,15300,0]),("Java",[9000,9600,9900,9900,9600,9300,9600,9300,9900,9900,0]),("Johnson",[10500,9600,10200,9900,9900,9300,8400,8700,8700,8100,0]),("Kanji",[900]*11),("HQ",[1200,1200,1200,1200,1200,1200,1200,1200,1500,1500,0]),("GCB-MT",[4500,4500,4800,4800,4800,4500,6000,5100,6000,5700,0]),("TF-WS",[4800,5100,4800,4800,4800,4500,4500,4200,3900,3900,0]),("TF-LM",[12300,12300,11700,11700,12600,9300,9000,9900,10200,12000,0]),("TF-MT",[19800,20700,21900,22200,21300,21300,21900,21900,22200,21900,0]),("GCB-TDs",[2700,3000,3000,3300,3600,3600,3600,3600,4800,5100,0]),("Highchem",[0,0,0,0,0,4800,5100,5100,5400,4800,0]),("Antonia",[0,0,0,0,0,0,900,900,600,600,0])]},
]
BENEFICIARIES2 = [("Period 1","Mary Ngota","GCB","Dad-Death","Nov 2024",30000),("Period 1","Mariamu","GCB","Dad-Death","Dec 2024",30000),("Period 1","Claire Osiako","Kaysalt","Dad-Death","2 Dec 2024",30000),("Period 1","Rachael Ndungu","Pwani","Mum-Death","10 Dec 2024",30000),("Period 1","Teresih Kariuki","TF","Dad-Death","17 Dec 2024",30000),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","4 Dec 2024",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Jan 2025",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Feb 2025",9500),("Period 1","(Unnamed)","SJ","Daughter-Death","",30000),("Period 1","Jecinta Nduta Karanja","TF","Loss of earning","",9000),("Period 1","Winnie","TF B","Dad-Death","",30000),("Period 1","Maureen Kiare","Kenafric","Dad-Death","July",30000),("Period 1","Eugene Otieno","TF","Dad-Death","July",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",22000),("Period 1","Mercy Mwikali","TF","Guardian","Aug 2025",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",11000),("Period 1","Annah Nthamba Musyoki","Java","Dad-Death","Sep 2025",30000),("Period 1","Eunice Wairimu Wanjiku","SJ","Dad-Death","Oct 2025",30000),("Period 1","JJJJ","","Loss of earning","",11500),("Period 1","Nostar","TF","Loss of earning","",19000),("Period 2","Rose Lumonya Saidi","POPL","Death-Father","Dec 2025",40000),("Period 2","Susan Ndungu","TF","Death-Father","26 Jan 2026",40000),("Period 2","Irene Wairimu","Java","Death-Guardian","May 2026",40000),("Period 2","Mercy Mwende","GCB","Loss of earning","May 2026",11075),("Period 2","Damarais Muyoka","TF","Death-Father","May 2026",40000),("Period 2","Ruth Amollo Nyangun","","Death-Father","Jun 2026",40000),("Period 2","Sheila Okomo","TF","Loss of earning","May",9000),("Period 2","Sheila Okomo","TF","Loss of earning","June",9000),("Period 2","(Unnamed)","TF","Death-Father","",40000),("Period 2","Vivian Moraa","Java","Loss of earning","",11000),("Period 2","Hannah Wanjiku","TF","Death-Father","17 Aug",40000)]
FARES2 = [("Period 1","Peter Ikegu","0704886421",1000),("Period 1","George Ibuba","0113964865",1000),("Period 1","Kevin Kipkurui","0704284388",1000),("Period 1","Valary Chepkoech","0713053696",1500),("Period 1","Mercy Njeri","0713881793",1500),("Period 1","Margaret Wangari","0720331094",1000),("Period 1","Mary Wangare","0796805933",1000),("Period 1","Daniel Mayaka","0722620252",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","Rose","",3000),("Period 1","Jecinta Apondi","",1000),("Period 1","Mercy Onyango","",1000),("Period 1","Preskila Ondiek","",1000),("Period 1","Jane Wangari","",1500),("Period 1","Caroline Wachira","",1500),("Period 1","Joy","",1500),("Period 1","Berbciter","",1500),("Period 1","Irene Wamuyu","0719606834",1000),("Period 1","Ann Mulema","0729218786",1000),("Period 1","Gloria Luksenaka","0796426074",1000),("Period 1","Mary Thika","0719572174",1000),("Period 1","Joshua Iguna","0792529926",1000),("Period 1","Jackline Kamau","0724562145",1000),("Latest","Eunice Makona","0714910135",1200),("Latest","Hellen Onyango","0724570228",1200),("Latest","Caren Chonge","0710427468",900),("Latest","Antony Mwendia","",1500),("Latest","Gladys Nyaga","",1500),("Latest","Marlon K. Ang'undu","",1200),("Latest","Gladys Wambaire Kinuthia","",1200),("Latest","Evapertual Wambui","",1200),("Latest","Catherine Ogutu","",1700),("Latest","Ebby Lomoi","",1700),("Latest","Jackline Ayiga","",1700),("Latest","Esther Marenya","",1600),("Latest","George Odhiambo","",1400),("Latest","Kiplimo","",4200),("Latest","Maureen Njeri Kamunyu","",1500),("Latest","Eunice Wairimu","",2000),("Latest","Victoria Wangechi Mugwe","",2000),("Latest","(Unnamed)","",500)]
MONTHLY_INDIVIDUAL = [("Oct 2024",327,98100),("Nov 2024",318,95400),("Dec 2024",318,95400),("Jan 2025",339,101700)]
# 🧹 Helper: clean dirty Excel values
def clean(v):
    if v is None: return ""
    s = str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL"): return ""
    if "will give" in s.lower(): return ""
    if "will provide" in s.lower(): return ""
    if "notification:" in s.lower(): return s.split(":",1)[1].strip()
    return s
# 📧 Helper: make email from names
def make_email(n, staff):
    p = [x for x in n.lower().replace(".","").split() if x.isalpha()]
    return f"{p[0]}.{p[-1]}@figbrands.co.ke" if len(p) >= 2 else f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
# 🗓️ Helper: parse "Nov.2022" / "May.2026" / "22/07/2026" -> (year, month)
def parse_join(s):
    if not s: return None
    s = str(s).strip().lower()
    months = {"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,"january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
    m = re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})", s)  # 📅 DD/MM/YYYY
    if m:
        d, mo, y = int(m.group(1)), int(m.group(2)), int(m.group(3))
        if mo > 12: d, mo = mo, d  # 🔄 swap if MM/DD
        return (y, mo)
    m = re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})", s)  # 📅 Month YYYY
    if m:
        return (int(m.group(2)), months[m.group(1)[:3]])
    m = re.search(r"(\d{4})", s)  # 📅 Year only -> Jan that year
    if m:
        return (int(m.group(1)), 1)
    return None
# 💸 CORE: months active in share-out period Dec 2025 - Sep 2026
def months_active(join_str):
    # 🕐 Start = later of (join date, Dec 2025) | End = Sep 2026
    start_y, start_m = PERIOD_START
    end_y, end_m = PERIOD_END
    j = parse_join(join_str)
    if j:  # 👤 Member joined during/after period? Start from join month
        if (j[0], j[1]) > (start_y, start_m):
            start_y, start_m = j
    if (start_y, start_m) > (end_y, end_m):  # 🚫 Joined after Sep 2026 -> 0 months
        return 0
    # 🧮 Count inclusive months: (end - start) + 1
    return (end_y - start_y) * 12 + (end_m - start_m) + 1
# 💸 CORE: build share-out table for ALL members
def calc_shares():
    c = get_db()  # 🗄️ Open DB
    try:
        rows = c.execute("SELECT id,staff_no,full_names,project,email,month_joined FROM users WHERE email != ? ORDER BY full_names", (ADMIN_EMAIL,)).fetchall()
    finally:
        c.close()
    out = []
    for r in rows:  # 👥 Loop every member
        months = months_active(r["month_joined"])  # 📅 How long in period?
        contrib = months * MONTHLY_RATE  # 💵 Contribution = months x 300
        out.append({"id": r["id"], "staff_no": r["staff_no"] or "", "full_names": r["full_names"] or "", "project": r["project"] or "", "email": r["email"] or "", "month_joined": r["month_joined"] or "", "months": months, "contribution": contrib, "share": 0.0})
    total_contrib = sum(x["contribution"] for x in out)  # 📊 Total contributions
    for x in out:  # 🧮 Share = contrib / total x 953,000
        x["share"] = round(DISTRIBUTABLE * x["contribution"] / total_contrib, 2) if total_contrib else 0.0
    out.sort(key=lambda x: x["share"], reverse=True)  # 🏆 Biggest share first
    return out, total_contrib
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
        c.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("Welcome to F.I.G BRANDS WELFARE","Your welfare system is active.","Now"))
        c.execute("INSERT INTO notifications (title,msg,created) VALUES (?,?,?)", ("💸 Share-Out Added","Leave 200,000 in account - share 953,000 by contribution.","Now"))
    added = 0
    for r in SEED_DATA:
        staff, proj_raw, month, names, father, mother, guardian, spouse, k1, k2, k3, k4, k5 = r
        staff = clean(staff); names = clean(names)
        if not staff or not names: continue
        if c.execute("SELECT id FROM users WHERE staff_no=?", (staff,)).fetchone(): continue
        project = PMAP.get(proj_raw, proj_raw)
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
# 🎨 BASE LAYOUT - header + sidebar + popups
BASE = '''<style>*{margin:0;padding:0;box-sizing:border-box}body{font-family:sans-serif;background:#f1f5f9;color:#0f172a}.app-header{height:64px;background:#1565c0;color:#fff;display:flex;align-items:center;justify-content:space-between;padding:0 16px;position:sticky;top:0;z-index:30}.menu-btn{width:40px;height:40px;border-radius:10px;background:rgba(255,255,255,.15);border:none;color:#fff;font-size:22px;cursor:pointer}.brand-name{font-weight:800;font-size:14px}.brand-name span{font-size:10px;display:block}.header-icons{display:flex;gap:12px}.h-icon{width:36px;height:36px;border-radius:50%;background:rgba(255,255,255,.15);display:flex;align-items:center;justify-content:center;cursor:pointer;position:relative}.badge{position:absolute;top:-4px;right:-4px;background:#ef4444;color:#fff;font-size:10px;min-width:18px;height:18px;border-radius:999px;display:flex;align-items:center;justify-content:center}.overlay{position:fixed;inset:0;background:rgba(0,0,0,.4);z-index:40;display:none}.overlay.show{display:block}.sidebar{position:fixed;top:0;left:0;width:300px;height:100%;background:#fff;z-index:50;transform:translateX(-100%);transition:transform .3s;overflow:hidden;display:flex;flex-direction:column}.sidebar.open{transform:translateX(0)}.sidebar-top{background:#1e88e5;color:#fff;padding:24px 20px}.profile-name{font-weight:700;margin-top:10px;text-transform:uppercase}.profile-email{font-size:13px;opacity:.9;word-break:break-all}.menu-list{flex:1;overflow:auto;padding:12px 0}.menu-item{display:flex;gap:16px;padding:15px 22px;font-weight:600;color:#0f172a;text-decoration:none}.menu-item.active{background:#e3f2fd;color:#1565c0}.sidebar-bottom{padding:14px 20px;border-top:1px solid #f1f5f9;display:flex;justify-content:space-between;font-size:11px;color:#94a3b8}.page{max-width:1000px;margin:0 auto;padding:16px}.card{background:#fff;border-radius:16px;border:1px solid #e2e8f0;overflow:hidden;margin-bottom:12px}.card-header{padding:20px 22px;border-bottom:1px solid #f1f5f9}.card-title{font-weight:800;font-size:16px}.card-sub{font-size:12px;color:#64748b}.card-body{padding:22px}.input{width:100%;height:46px;border:1px solid #e2e8f0;border-radius:12px;padding:0 14px;font-size:14px;outline:none}.label{font-size:11px;font-weight:700;color:#475569;text-transform:uppercase;margin-bottom:7px;display:block}.grid2{display:grid;grid-template-columns:1fr 1fr;gap:12px}.grid3{display:grid;grid-template-columns:1fr 1fr 1fr;gap:12px}.section{margin:22px 0 14px;font-size:12px;font-weight:800}.btn-primary{width:100%;height:50px;background:#0f172a;color:#fff;border:none;border-radius:12px;font-weight:700;cursor:pointer;margin-top:10px}.btn-excel{display:inline-flex;gap:8px;background:#16a34a;color:#fff;padding:10px 16px;border-radius:12px;font-weight:700;font-size:13px;text-decoration:none}.stat-grid{display:grid;grid-template-columns:1fr 1fr 1fr;gap:10px;margin-bottom:12px}.stat{background:#fff;border-radius:16px;padding:18px;border:1px solid #e2e8f0}.stat-l{font-size:10px;font-weight:700;color:#64748b;text-transform:uppercase}.stat-v{font-size:22px;font-weight:800;margin-top:4px}.photo-box{width:110px;height:110px;border-radius:50%;border:3px dashed #cbd5e1;display:flex;align-items:center;justify-content:center;overflow:hidden;background:#f8fafc;cursor:pointer}.photo-box img{width:100%;height:100%;object-fit:cover}.popup{position:fixed;inset:0;background:rgba(0,0,0,.45);z-index:100;display:none;align-items:flex-end;justify-content:center}.popup.show{display:flex}.popup-card{background:#fff;width:100%;max-width:520px;border-radius:22px 22px 0 0;max-height:82vh;overflow:auto;padding-bottom:20px}.popup-head{padding:18px 20px;display:flex;justify-content:space-between;border-bottom:1px solid #f1f5f9}.notif-item{padding:16px 20px;border-bottom:1px solid #f8fafc;display:flex;gap:12px}.support-opt{display:flex;gap:14px;padding:16px;border:1px solid #e2e8f0;border-radius:14px;margin-bottom:10px;cursor:pointer}.cred-row{display:flex;justify-content:space-between;padding:7px 0;border-bottom:1px dashed #f1f5f9;font-size:13px}.cred-row span:first-child{color:#64748b}.cred-row span:last-child{font-weight:600;text-align:right}table.fin{width:100%;border-collapse:collapse;font-size:12px}table.fin th{padding:8px 6px;background:#f8fafc;text-align:left;white-space:nowrap}table.fin td{padding:8px 6px;border-bottom:1px solid #f1f5f9;white-space:nowrap}table.fin tr.total td{font-weight:800;background:#e3f2fd}@media(max-width:600px){.stat-grid{grid-template-columns:1fr 1fr}.grid2,.grid3{grid-template-columns:1fr}}</style><div class="app-header"><div style="display:flex;align-items:center;gap:14px"><button class="menu-btn" onclick="openMenu()">☰</button><div class="brand-name">F.I.G BRANDS<span>WELFARE SYSTEM</span></div></div><div class="header-icons"><div class="h-icon" onclick="openBell()">🔔<span class="badge" id="bellBadge">3</span></div><div class="h-icon" onclick="openSupport()">🎧</div></div></div><div class="overlay" id="overlay" onclick="closeMenu()"></div><div class="sidebar" id="sidebar"><div class="sidebar-top"><div class="profile-name">F.I.G ADMIN</div><div class="profile-email">admin@lonma.com</div></div><div class="menu-list"><a class="menu-item" href="/">📊 Overview</a><a class="menu-item" href="/members">👥 Members</a><a class="menu-item" href="/breakdown">💰 Breakdown / Finance</a><a class="menu-item" href="/breakdown2">💰 Full History</a><a class="menu-item" href="/shareout">💸 Share-Out</a><a class="menu-item" href="/register">➕ Register Member</a><a class="menu-item" href="/download/excel">📥 Download Excel</a><a class="menu-item" href="#" onclick="openBell();return false">🔔 Notifications</a><a class="menu-item" href="#" onclick="openSupport();return false">🎧 Contact Support</a><a class="menu-item" href="/admin">⚙️ Settings</a><a class="menu-item" href="/admin" style="color:#dc2626">⏻ Log Out</a></div><div class="sidebar-bottom"><span>F.I.G BRANDS WELFARE</span><span>v45 💸</span></div></div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="popup-card"><div class="popup-head"><div><div style="font-weight:800">🔔 Notifications</div><div style="font-size:12px;color:#64748b" id="notifCount"></div></div><button onclick="closeBell()" style="width:32px;height:32px;border-radius:50%;border:none;cursor:pointer">✕</button></div><div id="notifList"></div><div style="padding:0 20px"><button onclick="markRead()" style="width:100%;height:44px;border-radius:12px;border:1px solid #e2e8f0;background:#fff;font-weight:700;cursor:pointer">Mark all as read</button></div></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="popup-card"><div class="popup-head"><div><div style="font-weight:800">🎧 Contact Support</div><div style="font-size:12px;color:#64748b">We reply within 1 hour</div></div><button onclick="closeSupport()" style="width:32px;height:32px;border-radius:50%;border:none;cursor:pointer">✕</button></div><div style="padding:18px 20px"><div class="support-opt" onclick="window.open('https://wa.me/254707780807?text=Hi F.I.G BRANDS Support','_blank')"><div><b>WhatsApp Support</b><div style="font-size:12px;color:#64748b">0707 780 807</div></div></div><div class="support-opt" onclick="window.location.href='mailto:info@figbrands.co.ke'"><div><b>Email Support</b><div style="font-size:12px;color:#64748b">info@figbrands.co.ke</div></div></div><label class="label">Your Name</label><input class="input" id="supName"><div style="margin-top:12px"><label class="label">Message</label><textarea id="supMsg" style="width:100%;height:90px;border:1px solid #e2e8f0;border-radius:12px;padding:12px"></textarea></div><button class="btn-primary" onclick="sendSupport()">Send Message →</button><p id="supStatus" style="text-align:center;margin-top:10px"></p></div></div></div><script>function openMenu(){document.getElementById('sidebar').classList.add('open');document.getElementById('overlay').classList.add('show')}function closeMenu(){document.getElementById('sidebar').classList.remove('open');document.getElementById('overlay').classList.remove('show')}async function openBell(){closeMenu();document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{h+='<div class="notif-item"><div><b>'+n.title+'</b><div style="font-size:13px;color:#475569">'+n.msg+'</div><div style="font-size:11px;color:#94a3b8">'+n.created+'</div></div></div>'});document.getElementById('notifList').innerHTML=h;document.getElementById('notifCount').textContent=d.notifications.length+' notifications';}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}function markRead(){document.getElementById('bellBadge').style.display='none';document.getElementById('notifList').innerHTML='<div style="padding:30px;text-align:center;color:#16a34a;font-weight:700">✓ All read</div>';}function openSupport(){closeMenu();document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let name=document.getElementById('supName').value;let msg=document.getElementById('supMsg').value;if(!msg){document.getElementById('supStatus').textContent='Please write a message';return;}let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,msg:msg})});let j=await r.json();document.getElementById('supStatus').textContent=j.message;document.getElementById('supMsg').value='';}document.addEventListener('DOMContentLoaded',()=>{let p=location.pathname;document.querySelectorAll('.menu-item').forEach(a=>{if(a.getAttribute('href')===p)a.classList.add('active')})})</script>'''
MEMBER_BASE = BASE.replace('F.I.G ADMIN','F.I.G MEMBER').replace('admin@lonma.com','info@figbrands.co.ke')
# 🏠 HOME PAGE
@app.route("/")
def home():
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>F.I.G BRANDS WELFARE</title>''' + BASE + '''<div class="page"><div class="stat-grid"><div class="stat"><div class="stat-l">Total Members</div><div class="stat-v" id="total">0</div></div><div class="stat"><div class="stat-l">Grand Total</div><div class="stat-v">Ksh 1,153,000</div></div><div class="stat"><div class="stat-l">Period 1 Oct24-Dec25</div><div class="stat-v" style="color:#16a34a">Ksh 1,404,000</div></div></div><div class="stat-grid"><div class="stat"><div class="stat-l">💸 To Share</div><div class="stat-v" style="color:#16a34a">Ksh 953,000</div></div><div class="stat"><div class="stat-l">🔒 Left in Account</div><div class="stat-v" style="color:#dc2626">Ksh 200,000</div></div><div class="stat"><div class="stat-l">Status</div><div class="stat-v" style="color:#16a34a">Active</div></div></div><div class="card"><div class="card-header"><div class="card-title">💸 Share-Out - Leave 200,000, Share 953,000 by Contribution</div><div class="card-sub"><a href="/shareout">View Each Member Share →</a></div></div></div><div class="card"><div class="card-header"><div class="card-title">Project Distribution</div><div class="card-sub">Members per project - <a href="/breakdown2">View Full History →</a></div></div><div id="breakdown"></div></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;let h='';for(let k in d.projects_breakdown){h+='<div style="padding:14px 22px;border-bottom:1px solid #f8fafc;display:flex;justify-content:space-between"><span>'+k+'</span><b>'+d.projects_breakdown[k]+'</b></div>';}document.getElementById('breakdown').innerHTML=h;}load();</script></body></html>'''
    return render_template_string(html)
# 💰 BREAKDOWN REDIRECT
@app.route("/breakdown")
def breakdown_page():
    return redirect("/breakdown2")
# 📜 FULL HISTORY PAGE
@app.route("/breakdown2")
def breakdown2_page():
    h = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Full History - F.I.G BRANDS</title>''' + BASE + '''<div class="page" style="max-width:1100px"><div class="stat-grid"><div class="stat"><div class="stat-l">Period 1 Oct24-Dec25</div><div class="stat-v">Ksh 1,404,000</div></div><div class="stat"><div class="stat-l">Period 2 Dec25-Oct26</div><div class="stat-v">Ksh 903,000</div></div><div class="stat"><div class="stat-l">Beneficiaries Unique</div><div class="stat-v" style="color:#dc2626">Ksh 781,075</div></div></div><div class="stat-grid"><div class="stat"><div class="stat-l">Grand Total (2026 file)</div><div class="stat-v">Ksh 1,153,000</div></div><div class="stat"><div class="stat-l">Transfer</div><div class="stat-v">Ksh 673,270</div></div><div class="stat"><div class="stat-l">Pwani BF / End Yr</div><div class="stat-v">767,859 / 517,859</div></div></div>'''
    h += '''<div class="card"><div class="card-header"><div class="card-title">Monthly Individual - 300 each</div></div><div style="padding:10px 20px">'''
    for m,c,t in MONTHLY_INDIVIDUAL:  # 👥 Monthly 300s
        h += f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #f1f5f9'><span><b>{m}</b> - {c} people</span><b>Ksh {t:,}</b></div>"
    h += "</div></div>"
    for p in PERIODS:  # 📊 Period tables
        h += f"<div class='card'><div class='card-header'><div class='card-title'>{p['label']} - Ksh {p['grand']:,}</div><div class='card-sub'>Expenditures: Ksh {p['expenditures']:,}</div></div><div style='overflow:auto'><table class='fin'><thead><tr><th>Project</th>"
        for mo in p['months']:
            h += f"<th>{mo}</th>"
        h += "<th>Total</th></tr></thead><tbody>"
        for name, vals in p['projects']:
            h += f"<tr><td><b>{name}</b></td>" + "".join([f"<td>{v:,}</td>" for v in vals]) + f"<td><b>{sum(vals):,}</b></td></tr>"
        h += "<tr class='total'><td>TOTAL</td>" + "".join([f"<td>{v:,} ({p['counts'][i]})</td>" for i,v in enumerate(p['totals'])]) + f"<td>{p['grand']:,}</td></tr></tbody></table></div></div>"
    h += "<div class='card'><div class='card-header'><div class='card-title'>🎁 Beneficiaries - Unique Ksh 781,075 (31)</div><div class='card-sub'>Period 1: 461,000 + Period 2 new: 320,075 - Nostar dup removed</div></div><div style='padding:10px 20px'>"
    for per,n,pr,r2,d,a in BENEFICIARIES2:  # 🎁 Beneficiaries
        h += f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #f1f5f9;font-size:13px'><span><b>{n}</b> - {per} - {pr} - {r2} - {d}</span><b>Ksh {a:,}</b></div>"
    h += "</div></div><div class='card'><div class='card-header'><div class='card-title'>🚌 Fares - Period 1: 30,000 | Latest: 28,200</div></div><div style='padding:10px 20px'>"
    for per,n,ph,a in FARES2:  # 🚌 Fares
        h += f"<div style='display:flex;justify-content:space-between;padding:8px 0;border-bottom:1px dashed #f1f5f9;font-size:13px'><span><b>{n}</b> - {per} - {ph}</span><b>Ksh {a:,}</b></div>"
    h += "</div></div></div></body></html>"
    return render_template_string(h)
# 💸 SHARE-OUT PAGE - NEW!
@app.route("/shareout")
def shareout_page():
    shares, total_contrib = calc_shares()  # 🧮 Calculate all shares
    total_shares = sum(x["share"] for x in shares)  # 📊 Sum check
    # 🎨 Build page
    h = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Share-Out - F.I.G BRANDS</title>''' + BASE + f'''<div class="page"><div class="card"><div class="card-header"><div class="card-title">💸 Share-Out - Leave 200,000, Share the Rest by Contribution</div><div class="card-sub">🧮 Share = (Your Contribution / Total Contributions) x 953,000 | 📅 Period: Dec 2025 - Sep 2026 (10 months) | 💵 Rate: 300/month</div></div></div><div class="stat-grid"><div class="stat"><div class="stat-l">🏦 Grand Total</div><div class="stat-v">Ksh {GRAND_TOTAL:,}</div></div><div class="stat"><div class="stat-l">🔒 Left in Account</div><div class="stat-v" style="color:#dc2626">Ksh {RESERVE:,}</div></div><div class="stat"><div class="stat-l">💸 To Share</div><div class="stat-v" style="color:#16a34a">Ksh {DISTRIBUTABLE:,}</div></div></div><div class="stat-grid"><div class="stat"><div class="stat-l">👥 Members Sharing</div><div class="stat-v">{len(shares)}</div></div><div class="stat"><div class="stat-l">📊 Total Contributions</div><div class="stat-v">Ksh {total_contrib:,}</div></div><div class="stat"><div class="stat-l">✅ Check: Shares + Reserve</div><div class="stat-v">Ksh {total_shares + RESERVE:,.0f}</div></div></div>'''
    h += '''<div class="card"><div class="card-header" style="display:flex;justify-content:space-between;align-items:center"><div><div class="card-title">🏆 Each Member Share</div><div class="card-sub">Sorted biggest first - 10 months = 3,000 contrib = full share</div></div><a class="btn-excel" href="/download/shareout">📥 Download Share-Out Excel</a></div><div style="padding:12px"><input class="input" id="q" placeholder="🔍 Search by name, staff no, project..." oninput="fil()"></div><div style="overflow:auto"><table class="fin"><thead><tr><th>#</th><th>👤 Member</th><th>🏢 Project</th><th>📅 Joined</th><th>📅 Months</th><th>💵 Contribution</th><th>💸 Share to Receive</th></tr></thead><tbody id="shareBody">'''
    for i, x in enumerate(shares, 1):  # 👥 One row per member
        h += f"<tr data-search='{(x['full_names'] + ' ' + x['staff_no'] + ' ' + x['project']).lower()}'><td>{i}</td><td><b>{x['full_names']}</b><div style='font-size:11px;color:#64748b'>{x['staff_no']} - {x['email']}</div></td><td>{x['project']}</td><td>{x['month_joined'] or '-'}</td><td>{x['months']}</td><td>Ksh {x['contribution']:,}</td><td><b>Ksh {x['share']:,.2f}</b></td></tr>"
    h += f"</tbody></table></div><div style='padding:16px 20px;display:flex;justify-content:space-between;font-weight:800'><span>TOTAL TO SHARE</span><span>Ksh {total_shares:,.2f}</span></div><div style='padding:0 20px 16px;display:flex;justify-content:space-between;font-weight:800'><span>🔒 LEFT IN ACCOUNT</span><span>Ksh {RESERVE:,}</span></div><div style='padding:0 20px 16px;display:flex;justify-content:space-between;font-weight:800;background:#e3f2fd'><span>🏦 GRAND TOTAL</span><span>Ksh {total_shares + RESERVE:,.0f}</span></div></div></div>"
    h += '''<script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(r=>{r.style.display=r.getAttribute('data-search').includes(q)?'':'none';});}</script></body></html>'''
    return render_template_string(h)
# 📥 SHARE-OUT EXCEL DOWNLOAD
@app.route("/download/shareout")
def download_shareout():
    shares, total_contrib = calc_shares()  # 🧮 Same numbers as page
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); ws = wb.active; ws.title = "Share-Out"  # 📗 New sheet
    ws.append(["F.I.G BRANDS - SHARE-OUT"]); ws.append([f"Grand Total: {GRAND_TOTAL:,} | Left in Account: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Contributions: {total_contrib:,}"])
    ws.append([]); ws.append(["#","Staff No","Full Names","Project","Joined","Months","Contribution","Share to Receive"])
    for c in ws[4]:  # 🎨 Header styling
        c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="1565C0"); c.alignment = Alignment(horizontal="center")
    for i, x in enumerate(shares, 1):  # ✍️ One row per member
        ws.append([i, x["staff_no"], x["full_names"], x["project"], x["month_joined"], x["months"], x["contribution"], round(x["share"], 2)])
    ws.append([]); ws.append(["","","","","","TOTAL", total_contrib, round(sum(x["share"] for x in shares), 2)])
    ws.append(["","","","","","LEFT IN ACCOUNT","", RESERVE])
    ws.append(["","","","","","GRAND TOTAL","", round(sum(x["share"] for x in shares), 2) + RESERVE])
    ws.freeze_panes = "A5"; ws.auto_filter.ref = ws.dimensions
    for col, w in zip("ABCDEFGH", [6, 14, 30, 22, 14, 10, 14, 18]):
        ws.column_dimensions[col].width = w
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="fig_brands_shareout.xlsx")
# 👥 MEMBERS PAGE
@app.route("/members")
def members_page():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in ["All Projects"]+PROJECTS])
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Members - F.I.G BRANDS</title>''' + MEMBER_BASE + '''<div class="page"><div class="card"><div class="card-header" style="display:flex;justify-content:space-between;align-items:center;flex-wrap:wrap;gap:10px"><div><div class="card-title">Members - Credentials</div><div class="card-sub">No photo</div></div><a class="btn-excel" href="/download/excel">📥 Download Excel</a></div><div style="padding:12px;display:flex;gap:10px"><input class="input" id="q" placeholder="Search by name, staff no, project..." oninput="fil()" style="flex:2"><select class="input" id="projFilter" onchange="fil()" style="flex:1">''' + opts + '''</select></div><div id="list" style="padding:0 12px 16px"></div></div></div><script>let all=[];async function load(){let r=await fetch('/api/members');let d=await r.json();all=d.members;render(d.members);}function row(l,v){return '<div class="cred-row"><span>'+l+'</span><span>'+(v||'-')+'</span></div>';}function render(l){let h='';if(l.length==0)h='<div style="padding:30px;text-align:center;color:#64748b">No members yet</div>';else l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<div style="background:#fff;border:1px solid #e2e8f0;border-radius:16px;padding:18px;margin-bottom:12px"><div style="display:flex;justify-content:space-between"><div><div style="font-weight:800">'+m.full_names+'</div><div style="font-size:12px;color:#64748b">'+m.email+'</div></div><span style="background:#e3f2fd;color:#1565c0;padding:5px 12px;border-radius:999px;font-weight:700;font-size:12px">'+m.project+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID No.',m.guardian_id)+row('Spouse ID No.',m.spouse_id)+row('Kids Birth Certs',kids)+'</div>';});document.getElementById('list').innerHTML=h;}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(m=>{let s=(m.full_names+' '+m.staff_no+' '+m.project+' '+(m.guardian_id||'')+' '+(m.spouse_id||'')).toLowerCase().includes(qq);let p=(pf=='All Projects'||m.project==pf);return s&&p;}));}load();</script></body></html>'''
    return render_template_string(html)
# ➕ REGISTER PAGE
@app.route("/register")
def register_page():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Register - F.I.G BRANDS</title>''' + BASE + '''<div class="page"><div class="card"><div class="card-header"><div class="card-title">Welfare Registration Form</div><div class="card-sub">Add member with photo</div></div><div class="card-body"><div style="display:flex;gap:20px;align-items:center;margin-bottom:20px"><div class="photo-box" id="photoBox" onclick="document.getElementById('photoInput').click()"><img id="photoPreview" style="display:none"><div id="photoPlaceholder"><div style="font-size:32px">📷</div><div>Add Photo</div></div></div><div><b>Member Photo</b><div style="font-size:12px;color:#64748b">Tap to upload - Max 2MB</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div></div><div class="section">1. Staff Information</div><div class="grid2"><div><label class="label">Staff Number</label><input class="input" id="staff_no"></div><div><label class="label">Project</label><select class="input" id="project">''' + opts + '''</select></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Date Joined</label><input class="input" id="month_joined"></div><div><label class="label">Full Names *</label><input class="input" id="full_names"></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Email *</label><input class="input" id="email"></div><div><label class="label">Password *</label><input class="input" id="password" type="password"></div></div><div class="section">2. Parents IDs</div><div class="grid2"><div><label class="label">Father ID</label><input class="input" id="father_id"></div><div><label class="label">Mother ID</label><input class="input" id="mother_id"></div></div><div class="section">3. Guardian & Spouse</div><div class="grid2"><div><label class="label">Guardian ID No.</label><input class="input" id="guardian_id"></div><div><label class="label">Spouse ID No.</label><input class="input" id="spouse_id"></div></div><div class="section">4. Kids Birth Certificates</div><div class="grid3"><div><label class="label">Kid 1</label><input class="input" id="kid1"></div><div><label class="label">Kid 2</label><input class="input" id="kid2"></div><div><label class="label">Kid 3</label><input class="input" id="kid3"></div></div><div style="margin-top:12px" class="grid2"><div><label class="label">Kid 4</label><input class="input" id="kid4"></div><div><label class="label">Kid 5</label><input class="input" id="kid5"></div></div><button class="btn-primary" onclick="doReg()" id="btn">Create Member</button><p id="msg" style="text-align:center;margin-top:10px"></p></div></div></div><script>let photoBase64="";function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>2*1024*1024){alert('File too large');return;}let r=new FileReader();r.onload=function(ev){photoBase64=ev.target.result;document.getElementById('photoPreview').src=photoBase64;document.getElementById('photoPreview').style.display='block';document.getElementById('photoPlaceholder').style.display='none';};r.readAsDataURL(f);}async function doReg(){let btn=document.getElementById('btn');btn.textContent='Creating...';let d={staff_no:document.getElementById('staff_no').value,project:document.getElementById('project').value,full_names:document.getElementById('full_names').value,email:document.getElementById('email').value,password:document.getElementById('password').value,month_joined:document.getElementById('month_joined').value,father_id:document.getElementById('father_id').value,mother_id:document.getElementById('mother_id').value,guardian_id:document.getElementById('guardian_id').value,spouse_id:document.getElementById('spouse_id').value,kid1:document.getElementById('kid1').value,kid2:document.getElementById('kid2').value,kid3:document.getElementById('kid3').value,kid4:document.getElementById('kid4').value,kid5:document.getElementById('kid5').value,photo:photoBase64};if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';btn.textContent='Create Member';return;}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;btn.textContent=r.ok?'Created':'Create Member';if(r.ok)setTimeout(()=>location.href='/members',800);}</script></body></html>'''
    return render_template_string(html)
# ⚙️ ADMIN LOGIN
@app.route("/admin")
def admin_login_page():
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - F.I.G BRANDS</title>''' + BASE + '''<div class="page" style="max-width:400px"><div class="card"><div class="card-header"><div class="card-title">Admin Login</div></div><div class="card-body"><label class="label">Email</label><input class="input" id="email" value="admin@lonma.com"><div style="margin-top:12px"><label class="label">Password</label><input class="input" id="pass" type="password" value="admin123"></div><button class="btn-primary" onclick="login()">Login</button><p id="msg" style="text-align:center;color:#dc2626;margin-top:10px"></p></div></div></div><script>async function login(){let e=document.getElementById('email').value;let p=document.getElementById('pass').value;let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(r.ok)location.href='/admin/dashboard?key='+j.key;else document.getElementById('msg').textContent=j.error;}</script></body></html>'''
    return render_template_string(html)
# ⚙️ ADMIN DASHBOARD
@app.route("/admin/dashboard")
def admin_dashboard():
    if request.args.get("key") != ADMIN_KEY:
        return redirect("/admin")
    html = '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Admin - F.I.G BRANDS</title>''' + BASE + '''<div class="page"><div class="card"><div class="card-header" style="display:flex;justify-content:space-between;align-items:center"><div class="card-title">Admin - Welfare Management</div><a class="btn-excel" href="/download/excel">📥 Download Excel</a></div><div style="overflow:auto"><table style="width:100%;border-collapse:collapse"><thead><tr><th style="padding:10px;text-align:left">Photo</th><th style="padding:10px;text-align:left">Staff & Name</th><th style="padding:10px;text-align:left">Family</th><th style="padding:10px;text-align:left">Action</th></tr></thead><tbody id="tbl"></tbody></table></div></div><div class="card"><div class="card-header"><div class="card-title">📩 Support Messages</div></div><div id="supList" style="padding:10px 20px">Loading...</div></div></div><script>async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{let prot=m.email=='admin@lonma.com';let photo=m.photo?'<img src="'+m.photo+'" style="width:44px;height:44px;border-radius:50%;object-fit:cover">':'<div style="width:44px;height:44px;border-radius:50%;background:#f1f5f9;display:flex;align-items:center;justify-content:center;font-weight:700">'+(m.full_names||'A').charAt(0)+'</div>';let btn=prot?'<span>System</span>':'<button onclick="del('+m.id+')" style="color:#dc2626;border:1px solid #fee2e2;background:#fff;border-radius:999px;padding:5px 12px;cursor:pointer">Delete</button>';h+='<tr style="border-bottom:1px solid #f1f5f9"><td style="padding:10px">'+photo+'</td><td style="padding:14px"><b>'+m.staff_no+'</b><div style="font-weight:700">'+m.full_names+'</div><div style="font-size:11px;color:#64748b">'+m.email+'</div></td><td style="padding:14px;font-size:11px">G:'+(m.guardian_id||'-')+' S:'+(m.spouse_id||'-')+'<br>Kids:'+([m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(',')||'-')+'</td><td style="padding:14px">'+btn+'</td></tr>';});document.getElementById('tbl').innerHTML=h;let r2=await fetch('/api/support_list');let d2=await r2.json();let h2='';if(d2.messages.length==0)h2='No messages';else d2.messages.forEach(m=>{h2+='<div style="padding:12px 0;border-bottom:1px solid #f1f5f9"><b>'+(m.name||'Guest')+'</b> <span style="font-size:11px;color:#94a3b8">'+m.created+'</span><div>'+m.msg+'</div></div>'});document.getElementById('supList').innerHTML=h2;}async function del(id){if(!confirm('Delete?'))return;let r=await fetch('/api/members/'+id+'?key=''' + ADMIN_KEY + '''',{method:'DELETE'});let j=await r.json();if(!r.ok){alert(j.error);return;}load();}load();</script></body></html>'''
    return render_template_string(html)
# 📥 MEMBERS EXCEL
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
            cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="1565C0"); cell.alignment = Alignment(horizontal="center")
        for r in rows:
            ws.append([r[x] or "" for x in ["staff_no","full_names","project","email","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]])
        ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions
        out = io.BytesIO(); wb.save(out); out.seek(0)
        return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="fig_brands_members.xlsx")
    finally:
        c.close()
# 📊 API: STATS
@app.route("/api/stats")
def api_stats():
    c = get_db()
    try:
        total = c.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        b = {}
        for p in PROJECTS:
            b[p] = c.execute("SELECT COUNT(*) FROM users WHERE project=? AND email != ?", (p, ADMIN_EMAIL)).fetchone()[0]
        return jsonify({"total_members": total, "projects_breakdown": b})
    finally:
        c.close()
# 💰 API: BREAKDOWN
@app.route("/api/breakdown")
def api_breakdown():
    c = get_db()
    try:
        brows = c.execute("SELECT * FROM beneficiaries2 ORDER BY id").fetchall()
        frows = c.execute("SELECT * FROM fares2 ORDER BY id").fetchall()
        return jsonify({"periods": PERIODS, "monthly_individual": MONTHLY_INDIVIDUAL, "beneficiaries": [dict(r) for r in brows], "beneficiaries_total": 781075, "fares": [dict(r) for r in frows], "grand_total": GRAND_TOTAL, "transfer_total": 673270})
    finally:
        c.close()
# 💸 API: SHARE-OUT - returns every member share as JSON
@app.route("/api/shareout")
def api_shareout():
    shares, total_contrib = calc_shares()  # 🧮 Calculate
    return jsonify({"grand_total": GRAND_TOTAL, "reserve": RESERVE, "distributable": DISTRIBUTABLE, "total_contributions": total_contrib, "members": len(shares), "total_shares": round(sum(x["share"] for x in shares), 2), "shares": shares})
# 🔔 API: NOTIFICATIONS
@app.route("/api/notifications")
def api_notifs():
    c = get_db()
    try:
        rows = c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall()
        return jsonify({"notifications": [dict(r) for r in rows]})
    finally:
        c.close()
# 🎧 API: SUPPORT
@app.route("/api/support", methods=["POST"])
def api_support():
    d = request.get_json(silent=True) or {}
    c = get_db()
    try:
        c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))", (d.get("name","Guest"), d.get("msg",""))); c.commit()
        return jsonify({"message": "Message sent! Support will reply soon."})
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
# 👥 API: MEMBERS
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
# 🔐 API: ADMIN LOGIN
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
# ➕ API: REGISTER
@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS":
        return "", 200
    d = request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"):
        return jsonify({"error": "email and password required"}), 400
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
        return jsonify({"message": "Member created with photo"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 400
    finally:
        c.close()
# 🗑️ API: DELETE MEMBER
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
# 🚀 RUN APP
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
