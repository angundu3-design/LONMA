from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
PROJECTS = ["Antonia","GCB-MT","GCB-Ws","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PMAP = {"Antonio":"Antonia","ANTONIA":"Antonia","Antonia":"Antonia","Antonia Stogdale":"Antonia","GCB-MT":"GCB-MT","GCB MT":"GCB-MT","GCB":"GCB-MT","GCB-Ws":"GCB-Ws","GCB Ws":"GCB-Ws","GCB TDS":"GCB-Ws","GCB-TDs":"GCB-Ws","GCB-TDS":"GCB-Ws","Higchem":"Higchem","HIGHCHEM":"Higchem","HIGCHEM MARKETING LIMITED":"Higchem","Hichem":"Higchem","Highchem":"Higchem","HQ":"HQ","Kanji":"Kanji","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","Java House":"Java House","JAVA":"Java House","Java":"Java House","Pwani Oil Products":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","SC Johnson":"SC Johnson","SJ Johnson":"SC Johnson","JOHNSON":"SC Johnson","Johnson":"SC Johnson","SJ":"SC Johnson","SCJohnson":"SC Johnson","Scjohnsons":"SC Johnson","scjohnsons":"SC Johnson","TF WSL":"TF WSL","TF WS":"TF WSL","TF-WS":"TF WSL","TF":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
def norm_project(p):
    p=(p or "").strip()
    if p in PMAP: return PMAP[p]
    up = " ".join(p.upper().split())
    if up in PMAP: return PMAP[up]
    return PMAP.get(p.title(), p or "Pwani Oil Products")
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
BF = 855759
RESERVE = 200000
DISTRIBUTABLE = BF - RESERVE
MONTHLY_RATE = 300
PERIOD_START = (2025, 12)
PERIOD_END = (2026, 9)
SEED_TXT = '''202731|Pwani Oil Products|2025|Angela Nyaguthii Gathege|Philip Gathege|Elizabeth Wanjiru||||||
202863|Pwani Oil Products|2025|Peter Olonde|6600561|0745115734||41572317|67272316||||
202656|Pwani Oil Products|2025|Patrick Sifuna Wanjala||4396984||31939216|151468||||
202679|Pwani Oil Products|2016|Jack Omondi Juma|||||9927L79|3300789|26057L7|9999788|
202680|Pwani Oil Products|2016|Marlon Ang'undu Kikuyu|||1951498||6879175||||
202712|Pwani Oil Products|Nov.2022|Laura Imali|NA|NA|0327707|37982161|112409612||||
202710|Pwani Oil Products|Dec.2020|Edith Kabera|NA|NA|23740423|23965879|10700481|112152616|11250650||
202677|Pwani Oil Products|October.2024|Phoebe Anyango|1014509|2266278|NA|NA|NA|NA|NA|NA|NA
202706|Pwani Oil Products|Aug.2021|Cynthia Awuor|NA|9892352|NA||1231202182||||
202707|Pwani Oil Products|Nov.2021|Maureen Owino|2859205|4313510|28254592|24675501|9927L79|3300789|26057L7|9999788|
202721|Pwani Oil Products|March .2023|Merceline Adhiambo|4026148|13199939|NA|27472316|3271828||||
202705|Pwani Oil Products|Marh 2019|Odiembo Yvonne|NA|8351397|NA|NA|will  give  later||||
202722|Pwani Oil Products|Dec.2023|Linet oduor|2828431|14479498|NA|NA|NA|NA|NA|NA|NA
202746|Pwani Oil Products|Nov.2025|Divyan Dorcas|NA|13603542|NA|NA|||||
202708|Pwani Oil Products|Jan. 2020|Lilian muchuma|NA|261270|||110707451||||
202711|Pwani Oil Products|Sept.2021|John Adiel||1329824|28565804|32190036|||||
292932|Pwani Oil Products|May.2026|Milcah Otiende|8232129|7861021||32624856|4094626||||
280370|Pwani Oil Products|Sept. 2026|Lucy Mwende Mbatha|2991561|2965465|NA|NA|0852106551|NA|NA|NA|NA
202697|Pwani Oil Products|Sept.2017|Naomi Mwango Abenga|1658833|NA|NA|22188003|121032026|121622654|112220451||
202696|Pwani Oil Products|2015|Lydiah Nyaanga Osengo|1649626|1637770||10020853|160900879|168706540/19|||
202693|Pwani Oil Products|May.2022|Meggiling Abuga Nyakerario|||8647005|||160900879||
202695|Pwani Oil Products|2022|Gorrety Adhiambo Otieno|9807667|26810228||30257258|2348625|2350080|3743676||
202699|Pwani Oil Products|14/12/2022|Sophia Nyamoita Mokaya|-|6541570||27233755|||||
202751|Pwani Oil Products|02/10/2023|Benjamin Odiwuor Mboya|10596034|20015894||466468971|7893744||||
202730|Pwani Oil Products|4.8.2025|Orwa Diana Atieno|96811362|21136615||36519946|||will provide later||
202694|Pwani Oil Products|02/01/2020|Charles Adika|8837595|11833576|||||||
282000|Pwani Oil Products|01/05/2026|Hyphine chepkoech Mutai|10383876|28240917||26261936|||||
202750|Pwani Oil Products|May.2025|Priscah Anjemo Injili|-|21842168|-|32990585|795787|978435|||
202698|Pwani Oil Products|14/02/2022|Postine Atieno|7921446|8398928||38801320|122318007||||
202744|Pwani Oil Products|01/03/2024|Anthony Manyara Chania|21022712|86260659||923456988|||||
202683|Pwani Oil Products|01/03/2013|Eunice Makona|-|4722288|N/A|210327239|7575163|7575161|7575162||
202700|Pwani Oil Products|01/03/2025|Charles kimutai Kirui|3872261|3872429|N/A|31045698|612112010|N/A|N/A|N/A|N/A
202709|Pwani Oil Products|01/03/2025|Oyoyo Yvonne Bentar|N/A|11801824|N/A|27464418|N/A|N/A|N/A|N/A|N/A
202678|Pwani Oil Products|01/03/2025|Owen Muthee Waithaka|21217575|22555615|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202733|Pwani Oil Products|01/03/2025|Sharon Cherono|N/A|11635405|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202529|Pwani Oil Products|01/03/2025|Alex Shangala|4176764|7956390|N/A|33313078|692102029|691828162|N/A|N/A|N/A
202729|Pwani Oil Products|01/03/2025|ROSE LUMONYA SAIDI|N/A|4252080|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202747|Pwani Oil Products|01/07/2025|BRENDA NELIMA WAFULA|N/A|133101|N/A|N/A|N/A|N/A|N/A|N/A|N/A
10405|Pwani Oil Products|01/03/2025|Diana Atieno Oduor|NA|4722494|757617564|28078423- Ben Kitui|N/A|N/A|370702896 -Dennis Adams|21506184- Joy Nelima|Samantha  malia Achieng
202749|Pwani Oil Products|01/03/2025|Celine Nasimiyu Wamalwa|N/A|8784757|NA|28990208|William  Musungu|Moses  Musungu|Bryton Musungu|N/A|N/A
292976|Pwani Oil Products|01/04/2026|Belinda chemtai|N/A|4722288|N/A|N/A|372315084|182018971|N/A|N/A|N/A
202702|Pwani Oil Products|01/05/2025|Betty Akinyi Namamba|Fabians  Namamba|Janet  Atieno|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202723|Pwani Oil Products|01/03/2025|Metrine Cherop Chumo|N/A|N/A|N/A|29934624|411700883|411506469|N/A|N/A|N/A
50516|Pwani Oil Products|01/05/2025|SHEILA ADISA VOLEMI|VOLEMI|TERESIA|HUDSON IMBAYI|22175541|NA|NA|NA|N/A|N/A
202701|Pwani Oil Products|01/03/2025|Everlyne mukoya Stephen|NA|N/A|N/A|23600368|N/A|671767|395330|N/A|N/A
202703|Pwani Oil Products|01/03/2025|Caren Nanjala Chonge|NA|5639451|Later|22086206|364057|6090663|N/A|N/A|N/A
202704|Pwani Oil Products|01/03/2025|Hellen Achieng Onyango|711723882|726994852|N/A|722618476|N/A|N/A|N/A|N/A|N/A
202724|Pwani Oil Products|01/03/2025|BENTA ACHIENG MURUKA|CHRISTOPHER MURUKA|JANE MAGENGA|N/A|28687282|1311214785|21910561|N/A|||
202989|SC Johnson|01/02/2026|Bonface Nzuki|13592548|20001605|||||||
202774|SC Johnson|01/08/2024|Oscar kipkoech Ruto|8715105|25972243|N/A|643055126|604533||||
90117|SC Johnson|01/08/2022|Hilda Esende Lugangi|22499361|22546698|Nil|22499361|330400075|370207832|371929483||
Lena Cherono|SC Johnson|01/10/2026|Lena Cherono|N/A|6013139|6013139||||||
202788|SC Johnson|01/08/2023|Afline Anyango Onyango|N/A|N/A|25083427|N/A|538317|538318|538342|880993|8908622
202786|SC Johnson|01/08/2022|Judith Oweya Lukale|6308832|1232343|||7281845|8355678|||
202784|SC Johnson|01/07/2025|Farida Olesi|N/A|21667279|||4164247||||
Phesial Jaramogi Ooyi|SC Johnson|01/08/2022|Phesial Jaramogi Ooyi|2631938|21217207|N/A|38946763|7493054|3486480|||
201743|SC Johnson|25/04/2026|Zachary Joel Moriasi|N/A|31295653|N/A||||||
202976|SC Johnson|01/02/2026|Winfred mwende john|N/A|8966707|N/A|28782624||261287576|||
202782|SC Johnson|01/12/2025|Victoria wangechi Mugwe|5988617|11032615|||||1512406016||
202775|SC Johnson|01/02/2023|Milka Wawuda Mwang'ombe|N/A|58719|||||||
202780|SC Johnson|2022|Mokua Frankline|23751234|24351022||37120961|||||
202765|SC Johnson|01/08/2025|Hannah Warukira Mwangi|3582703|N/A|||0071503182||||
202977|SC Johnson|26 Jan,2026|Emily Mueni Mutua|N/A|N/A|3545974||212327285|212303274|||
202764|SC Johnson|August,2025|Agnes Wangu Mwangi|9263345|20409743|||201192||||
202769|SC Johnson|01/08/2025|Joshua mwangi iguna|10380353|31107389||511795193|||||
202761|SC Johnson|Apr_25|Hannah wanjiku|N/A|N/A|N/A|N/A|2384950||||
202777|SC Johnson|,Sept 2022|Caroline Kathomi Njebiu|N/A|N/A|||||||
202757|SC Johnson|2024|Fedinand Kafwa|N/A|N/A|||||||
202772|SC Johnson|,Feb 2025|Maureen Njeri|N/A|N/A|||||||
280267|SC Johnson|,July 2026|Patrick Kabiu Waweru|N/A|N/A|||||||
202766|SC Johnson|,April 2025|Veronica Mukolwe|N/A|21000046|N/A|N/A|265075567||||
202789|SC Johnson|,Aug 2022|Celestine Auma Ouko|25837011|8212095||21166739|6658291||||
202641|Higchem|18/05/2026|Irene Waeni Mwangangi|9638105|12583212|NA|NA|210865865|2616122654|||
202657|Higchem|16/06/2026|Isaac Ombati Rioba|NA|23630642|NA|31939473|371923347||||
202787|Higchem|18/05/2026|Emily Nanjala Wafula||||||||||
202998|Higchem|18/05/2026|Millianna Anyango Sadaka||||||||||
280005|Higchem|18/05/2026|Faith Njeri Kibungi|3121603|3589023|NA|N/A|A8858040||||
280007|Higchem|18/05/2026|Collins Ofula Mabwa|7421158|36301081||37416617|1442312021||||
280008|Higchem|18/05/2026|Wanga Atieno Beryl|||||2633392||||
280009|Higchem|18/05/2026|Nelson Miruka Kiyondi|8578391|21133401|NA|NA|||||
280012|Higchem|18/05/2026|Robert Kariuki Macharia||||||||||
280013|Higchem|18/05/2026|Thomas Felix Mwatu|7808718|BK758118||34661148|||||
280014|Higchem|18/05/2026|Mercy Nabulo Khabala|1431857|9216359|NA|26142738|392118249||||
280078|Higchem|28/05/2026|Joan Anyango Otewa||||||||||
280266|Higchem|08/07/2026|Anna Mbinya Kalia||||||||||
280325|Higchem|19/08/2026|Marion Waheto|||32175829|36914920|||||
280326|Higchem|03/08/2026|Maureen Wanjiru Kiarie|9745295|11241637|||CA001474219||||
280349|Higchem|01/09/2026|Wicklife Okemwa Nyangaresi|1593749|10468950||308049405|4713214||||
Sherine Atieno|Antonia|2025|Sherine Atieno Otieno|N/A|23333405|N/A|N/A|N/A|N/A|N/A|N/A|N/A
280225|Antonia|2026|Stepheny Keziah Wambui Mwangi|10452983|10166506||34439485|1463604|2498854|||
202640|Java House|06/01/2024|Samuel Njeru Njiru|NA|12402044|NA|NA|NA|NA|NA||
202642|Java House|02/01/2023|Eugene Daudi Aura|12684478|22143892|NA|NA|NA|NA|NA||
202643|Java House|16/06/2023|Wamuyu Irene Wairimu|NA|NA|NA|NA|NA|NA|NA||
280226|Java House|22/06/2026|Alice Maina|21154721|5925331|NA|NA|NA|NA|NA||
292965|Java House|05/05/2026|Sylvia Agosa|NA|27589904|NA|NA|NA|NA|NA||
202648|Java House|08/01/2022|Esther Wangari Karanja|NA|2947799|NA|28442445|661711470|131927789|NA||
202649|Java House|08/01/2023|Emily Waithera Njenga|12679084|29681293|NA|31609269|74506389|NA|NA||
280372|Java House|09/09/2026|Joan Ensha Wairimu|7178165|10271736|NA|NA|27163167|NA|NA||
202651|Java House|15/04/2024|Edwin Ondieki Kiyaka|6925315|25820458|NA|36314446|272309733|NA|NA||
202652|Java House|23/11/2023|Gladys Kinuthia|730157|NA|NA|NA|721471|B750670|NA||
280507|Java House|16/09/2026|Purity mukami|NA|21461686|NA|NA|207735072|NA|NA||
202654|Java House|17/05/2025|Samwel Erick Odhiambo|NA|11705391|NA|NA|NA|NA|NA||
202655|Java House|04/01/2025|Felister Gatwiri Muriithi|8601366|21461686|NA|27924521|1752770|NA|NA||
202666|Java House|21/07/2026|Charity Moraa Juma|12696585|NA|NA|NA|NA|NA|NA||
202660|Java House|01/01/2026|Brian Mwenda Njue|NA|11326767|NA|NA|NA|NA|NA||
202661|Java House|11/11/2025|Emmanuel Mike Ochieng|NA|20465576|NA|NA|NA|NA|NA||
202662|Java House|11/11/2025|Caroline Muthoni Mugo|NA|9410131|NA|NA|447404|NA|NA||
202664|Java House|13/03/2026|Jeniffer Wanjira Ndung'u|3081426|NA|NA|NA|4694621|NA|NA||
202670|Java House|06/06/2025|Maureen Gathiru Mwaniki|8949712|9484232|NA|NA|NA|NA|NA||
202671|Java House|01/01/2025|Lilian Adhiambo Randa|NA|NA|22175755|28042042|4363793|6390498|NA||
202673|Java House|05/05/2024|Pauline Wambui Masila|NA|4872231|NA|28587029|6097147|A3489654|NA||
202674|Java House|29/11/2023|Anne Kamonya Mulema|NA|NA|1881637|29867375|9746194|7016764|NA||
202675|Java House|06/06/2025|Daniel Ombui Mayaka|6925939|5825881|NA|29893290|7090003|9105030|NA||
202934|Java House|01/01/2026|Jeff Otieno Maina|NA|NA|33964654|NA|NA|NA|NA||
202935|Java House|01/01/2026|Jedida Njoki Kinyanjui|NA|4244441|NA|NA|NA|NA|NA||
202937|Java House|02/02/2026|Clifton Kelvin Makokha|NA|NA|NA|NA|NA|NA|NA||
202952|Java House|01/01/2026|Collen Elizabeth Ojiambo|NA|NA|NA|NA|7072542|7515539|7135442||
202978|Java House|02/02/2026|Jackline Wanza Muthoka|NA|13796649|NA|NA|NA|NA|NA||
292915|Java House|05/05/2026|Francis Omari|NA|21065823|NA|NA|NA|NA|NA||
202686|Java House|16/04/2026|Evaperpetual Wambui Maina|NA|13542413|NA|NA|NA|NA|NA||
202603|Java House|01/09/2026|Mariam Juma|NA|NA|NA|NA|41335956|260828238|608994032||
280528|Java House|11/01/2026|Hydrick Kipkorir|NA|NA|NA|620201|NA|NA|NA||
Kendy Njeri|Java House|01/11/2026|Kendy Njeri|NA|26001602|NA|NA|NA|NA|NA||
Joseph Chege|Java House|01/11/2026|Joseph Chege|3054830|NA|NA|38220338|NA|NA|NA||
Specioza Matitsa|Java House|01/11/2026|Specioza Matitsa|NA|NA|NA|NA|NA|NA|NA||'''
PWANI_ROSTER = ''
PERIODS = []
BENEFICIARIES2 = []
FARES2 = []
MONTHLY_INDIVIDUAL = []
SEED_DATA = [tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
def clean(v):
    if v is None: return ""
    s = str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL","NIL"): return ""
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
    if m: return (int(m.group(2)), months[m.group(1)[:3]])
    m = re.search(r"(\d{4})", s)
    if m: return (int(m.group(1)), 1)
    return None
def months_active(j):
    sy, sm = PERIOD_START; ey, em = PERIOD_END
    p = parse_join(j)
    if p and (p[0], p[1]) > (sy, sm): sy, sm = p
    if (sy, sm) > (ey, em): return 0
    return (ey - sy) * 12 + (em - sm) + 1
def calc_shares():
    c = get_db()
    try: rows = c.execute("SELECT id,staff_no,full_names,project,email,month_joined FROM users WHERE email != ? ORDER BY full_names", (ADMIN_EMAIL,)).fetchall()
    finally: c.close()
    out = []
    for r in rows:
        mo = months_active(r["month_joined"])
        out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0})
    tm = sum(x["months"] for x in out); tc = sum(x["contribution"] for x in out); rate = DISTRIBUTABLE / tm if tm else 0
    for x in out: x["per_month"] = round(rate,2); x["share"] = round(x["months"]*rate,2)
    diff = round(DISTRIBUTABLE - sum(x["share"] for x in out),2)
    if out and diff != 0:
        out.sort(key=lambda x: x["share"], reverse=True); out[0]["share"] = round(out[0]["share"]+diff,2)
    out.sort(key=lambda x: x["share"], reverse=True)
    return out, tc, tm, rate
def get_db():
    c = sqlite3.connect(DB, timeout=10, check_same_thread=False, isolation_level=None); c.row_factory = sqlite3.Row
    try: c.execute("PRAGMA journal_mode=WAL;"); c.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return c
def add_user(c, staff, names, project, month, father="", mother="", guardian="", spouse="", k1="", k2="", k3="", k4="", k5="", photo=""):
    staff = clean(staff); names = clean(names); project = norm_project(project)
    if not staff or not names: return False
    if c.execute("SELECT id FROM users WHERE staff_no=?", (staff,)).fetchone(): return False
    if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)", (names,)).fetchone(): return False
    email = make_email(names, staff)
    if c.execute("SELECT id FROM users WHERE email=?", (email,)).fetchone(): email = f"member.{staff}@figbrands.co.ke"
    vals = (staff, names, project, email, generate_password_hash(staff), "fig_"+secrets.token_hex(12), clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5), photo)
    c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", vals)
    return True
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
    for col, typ in [("target","TEXT"),("is_read","INTEGER DEFAULT 0")]:
        try: c.execute(f"ALTER TABLE notifications ADD COLUMN {col} {typ}")
        except: pass
    for r in c.execute("SELECT id, project FROM users").fetchall():
        np = norm_project(r["project"])
        if np != r["project"]: c.execute("UPDATE users SET project=? WHERE id=?", (np, r["id"]))
    if not c.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    added = 0
    for r in SEED_DATA:
        staff, proj_raw, month, names, father, mother, guardian, spouse, k1, k2, k3, k4, k5 = r
        project = norm_project(proj_raw)
        ex = c.execute("SELECT id FROM users WHERE staff_no=?", (clean(staff),)).fetchone()
        if ex:
            c.execute("UPDATE users SET full_names=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE staff_no=?", (clean(names), project, clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5), clean(staff))); continue
        ex2 = c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)", (clean(names),)).fetchone()
        if ex2:
            c.execute("UPDATE users SET staff_no=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE id=?", (clean(staff), project, clean(month), clean(father), clean(mother), clean(guardian), clean(spouse), clean(k1), clean(k2), clean(k3), clean(k4), clean(k5), ex2["id"])); continue
        if add_user(c, staff, names, project, month, father, mother, guardian, spouse, k1, k2, k3, k4, k5): added += 1
    c.commit(); c.close(); print(f"v85 Pwani update seeded {added}")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); return r
@app.route("/favicon.ico")
def favicon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="14" fill="#0A1F33"/><text x="32" y="42" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#C9A86A" text-anchor="middle">FIG</text></svg>'
    return svg, 200, {"Content-Type": "image/svg+xml"}
def shell(title, body):
    return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + title + ''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Fraunces:opsz,wght@9..144,500;9..144,600&family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><style>:root{--navy:#0A1F33;--navy2:#122F4A;--gold:#C9A86A;--gold2:#A98A4F;--ink:#141A22;--muted:#6B7280;--line:#E9E2D6;--bg:#F7F5F0;--card:#FFFFFF;--green:#0E6B4A}*{box-sizing:border-box}body{font-family:Inter,system-ui,sans-serif;background:var(--bg);color:var(--ink);margin:0;padding-bottom:96px;-webkit-font-smoothing:antialiased}h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:600;letter-spacing:-.02em;color:var(--navy);margin:0 0 10px}.top{height:64px;background:var(--navy);color:#fff;display:flex;align-items:center;gap:12px;padding:0 16px;position:sticky;top:0;z-index:20;border-bottom:2px solid var(--gold)}.logo{background:#fff;color:var(--navy);border:1px solid var(--gold);border-radius:12px;padding:7px 10px;font-family:Fraunces,Georgia,serif;font-weight:600;font-size:19px;letter-spacing:.02em}.top small{display:block;font-size:9px;letter-spacing:.28em;color:var(--gold);font-weight:700;margin-top:2px}.top b{font-family:Fraunces,Georgia,serif;font-size:19px;letter-spacing:.01em;font-weight:600}.iconbtn{background:rgba(255,255,255,.08);border:1px solid rgba(255,255,255,.18);color:#fff;border-radius:999px;width:38px;height:38px;cursor:pointer;font-size:12px;font-weight:600}.toplinks{background:#fff;border-bottom:1px solid var(--line);padding:11px 16px;display:flex;gap:18px;flex-wrap:wrap;position:sticky;top:64px;z-index:15}.toplinks a{color:var(--navy);text-decoration:none;font-size:13px;font-weight:600;letter-spacing:.01em;padding-bottom:2px;border-bottom:2px solid transparent}.toplinks a:hover{border-bottom-color:var(--gold)}.page{max-width:1080px;margin:auto;padding:22px 16px}.eyebrow{font-size:11px;letter-spacing:.22em;text-transform:uppercase;color:var(--gold2);font-weight:700;margin-bottom:8px}.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:20px;margin-bottom:14px;box-shadow:0 6px 22px rgba(10,31,51,.05)}.input{width:100%;height:46px;border:1px solid #D9D0BF;border-radius:12px;padding:0 13px;box-sizing:border-box;background:#FFFDF9;font-size:14px;color:var(--ink);outline:none}.input:focus{border-color:var(--navy);box-shadow:0 0 0 3px rgba(201,168,106,.22)}label{font-size:12px;font-weight:600;color:#475569;display:block;margin-bottom:6px}.btn{width:100%;height:48px;background:var(--navy);color:#fff;border:0;border-radius:12px;font-weight:700;cursor:pointer;letter-spacing:.01em}.btn:active{transform:translateY(1px)}.btn2{display:inline-block;background:var(--navy);color:#fff;padding:11px 16px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}.btn2.gold{background:var(--gold);color:var(--navy)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.kpi{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px;box-shadow:0 6px 22px rgba(10,31,51,.04)}.kpi div:first-child{font-size:12px;letter-spacing:.14em;text-transform:uppercase;color:var(--muted);font-weight:700}.kpi h2{font-size:34px;margin:10px 0 4px}.hero{background:linear-gradient(135deg,#0A1F33 0%,#122F4A 58%,#0E6B4A 100%);color:#fff;border-radius:22px;padding:24px;position:relative;overflow:hidden;border:1px solid rgba(201,168,106,.35)}.hero:before{content:"";position:absolute;right:-30px;top:-40px;width:150px;height:150px;border:1px solid rgba(201,168,106,.35);border-radius:50%}.hero:after{content:"";position:absolute;right:10px;top:0;width:90px;height:90px;border:1px solid rgba(255,255,255,.12);border-radius:50%}.hero .lbl{font-size:11px;letter-spacing:.24em;color:var(--gold);font-weight:700}.hero h1{color:#fff;font-size:38px;margin:12px 0 10px}.hero p{color:rgba(255,255,255,.82);margin:0}.nav{position:fixed;left:14px;right:14px;bottom:14px;height:62px;background:var(--navy);border:1px solid rgba(201,168,106,.35);border-radius:999px;display:flex;box-shadow:0 14px 34px rgba(10,31,51,.28);z-index:30}.nav a{flex:1;color:#fff;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:700;letter-spacing:.02em}.nav a span{color:var(--gold);font-size:13px;line-height:1}.row{display:flex;justify-content:space-between;gap:12px;padding:13px 2px;border-bottom:1px solid #F1EDE3}.row:last-child{border-bottom:0}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid #EEEBE0;text-align:left}th{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted)}td b{color:var(--navy)}.num{text-align:right;white-space:nowrap}.pill{display:inline-block;background:#F3EDDD;color:#6B4F1D;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700;border:1px solid #E6D9B8}.popup{position:fixed;inset:0;background:rgba(10,31,51,.5);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:#fff;width:100%;max-width:520px;border-radius:22px 22px 0 0;padding:20px;max-height:86vh;overflow:auto}@media(max-width:640px){.grid{grid-template-columns:1fr}.hero h1{font-size:32px}.toplinks{gap:14px}}</style></head><body><div class="top"><div class="logo">FIG</div><div><b>F.I.G BRANDS</b><small>WELFARE SYSTEM &nbsp; v85</small></div><div style="margin-left:auto;display:flex;gap:8px"><button class="iconbtn" onclick="openBell()">Bell</button><button class="iconbtn" onclick="openSupport()">Help</button></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/admin">Admin</a></div><div class="page">''' + body + '''</div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="pop"><div style="display:flex;justify-content:space-between;align-items:center"><b style="font-family:Fraunces,Georgia,serif;font-size:20px">Notifications</b><button onclick="closeBell()" style="border:1px solid #E9E2D6;background:#fff;border-radius:999px;width:32px;height:32px;cursor:pointer">X</button></div><div id="notifList" style="margin-top:12px"></div><button class="btn" onclick="markRead()" style="margin-top:12px">Mark all as read</button></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="pop"><div style="display:flex;justify-content:space-between;align-items:center"><b style="font-family:Fraunces,Georgia,serif;font-size:20px">Contact Support</b><button onclick="closeSupport()" style="border:1px solid #E9E2D6;background:#fff;border-radius:999px;width:32px;height:32px;cursor:pointer">X</button></div><p style="color:#475569"><a href="https://wa.me/254707780807" target="_blank" style="color:#0A1F33;font-weight:700">WhatsApp 0707 780 807</a> &nbsp;·&nbsp; <a href="mailto:info@figbrands.co.ke" style="color:#0A1F33;font-weight:700">info@figbrands.co.ke</a></p><label>Your name</label><input class="input" id="supName" placeholder="Your name"><div style="margin-top:12px"><label>Message</label><textarea id="supMsg" class="input" style="height:96px;padding-top:10px" placeholder="Message"></textarea></div><button class="btn" onclick="sendSupport()" style="margin-top:14px">Send Message</button><p id="supStatus"></p></div></div><nav class="nav"><a href="/"><span>⌂</span>Home</a><a href="/members"><span>◉</span>Members</a><a href="/shareout"><span>◈</span>Share-Out</a><a href="/breakdown2"><span>≡</span>History</a><a href="/register"><span>+</span>Add</a></nav><script>function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{h+='<div onclick="tapNotif('+n.id+',\\''+esc(n.target||'/')+'\\')" style="padding:13px 0;border-bottom:1px solid #eee;cursor:pointer"><b>'+esc(n.title)+'</b><div style="color:#475569">'+esc(n.msg)+'</div><div style="font-size:11px;color:#888">'+esc(n.created)+'</div></div>'});document.getElementById('notifList').innerHTML=h||'No notifications';}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}async function tapNotif(id,t){await fetch('/api/notifications/'+id+'/read',{method:'POST'});location.href=t}async function markRead(){await fetch('/api/notifications/read',{method:'POST'});closeBell()}function openSupport(){document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}</script></body></html>''')
@app.route("/")
def home():
    body = '''<div class="eyebrow">F.I.G Brands &middot; Welfare</div><h1 style="font-size:42px">Overview</h1><p style="color:#475569;font-size:15px;line-height:1.6;max-width:620px">Balance brought forward, less KES 200,000 retained — shared fairly, per month of contributions.</p><div class="grid"><div class="kpi"><div>Total Members</div><h2 id="total">0</h2><div style="color:#6B7280;font-size:13px">Active welfare members</div></div><div class="kpi"><div>Projects</div><h2 id="projCount">0</h2><div style="color:#6B7280;font-size:13px">Projects with members</div></div></div><div class="hero" style="margin-top:14px"><div class="lbl">BALANCE BROUGHT FORWARD</div><h1>KES 855,759</h1><p>KES 655,759 to share &nbsp;·&nbsp; KES 200,000 retained</p></div><div class="grid" style="margin-top:14px"><div class="kpi"><div>Amount to Share</div><h2 style="color:#0E6B4A">KES 655,759</h2></div><div class="kpi"><div>Retained</div><h2 style="color:#9A1B1B">KES 200,000</h2></div><div class="kpi"><div>Value of One Month</div><h2 id="oneMonth" style="font-size:26px">-</h2><div id="oneMonthNote" style="color:#6B7280;font-size:13px"></div></div></div><div class="card" style="margin-top:14px"><div class="eyebrow">Distribution</div><h2>Project Distribution</h2><p style="color:#6B7280;font-size:13px">Only projects with members are shown.</p><div id="breakdown"></div><div class="row"><b id="projTotalLabel">Total</b><b id="projTotal">0</b></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('projTotal').textContent=d.total_members;document.getElementById('projTotalLabel').textContent='Total Members ('+d.projects_total+' projects)';let h='';Object.keys(d.projects_breakdown).sort().forEach(k=>{h+='<div class="row"><b>'+k+'</b><span>'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h||'No members yet';let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='655,759 / '+s.total_months+' months';}load();</script>'''
    return shell("Overview", body)
@app.route("/breakdown")
def breakdown_page(): return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
    h = "<div class='eyebrow'>History</div><h1>Full History</h1><p style='color:#475569'>No history yet — cleared.</p>"
    for p in PERIODS: h += f"<div class='card'><h3>{p['label']}</h3></div>"
    h += "<div class='card'><div class='eyebrow'>Beneficiaries</div><h2>Beneficiaries</h2>"
    for per,n,pr,r2,d,a in BENEFICIARIES2: h += f"<div class='row'><span><b>{n}</b></span><b>KES {a:,}</b></div>"
    h += "</div><div class='card'><div class='eyebrow'>Fares</div><h2>Fares</h2>"
    for per,n,ph,a in FARES2: h += f"<div class='row'><span><b>{n}</b></span><b>KES {a:,}</b></div>"
    h += "</div>"
    return shell("Full History", h)
@app.route("/shareout")
def shareout_page():
    shares, total_contrib, total_months, per_month_rate = calc_shares(); total_shares = sum(x["share"] for x in shares)
    h = f"<div class='eyebrow'>Share-Out &nbsp;·&nbsp; Dec 2025 — Sep 2026</div><h1 style='font-size:42px'>Share-Out</h1><p style='color:#475569'>Balance brought forward, less KES 200,000 retained — per month of contributions, KES 300 per month.</p><div class='hero'><div class='lbl'>AMOUNT TO SHARE</div><h1>KES 655,759</h1><p>1 month = KES {per_month_rate:,.2f} &nbsp;·&nbsp; Shares KES {total_shares:,.2f} + Retained 200,000 = BF 855,759</p></div><div class='grid' style='margin-top:14px'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{total_months}</h2></div><div class='kpi'><div>Total Contributions</div><h2 style='font-size:26px'>KES {total_contrib:,}</h2></div><div class='kpi'><div>Total Shares</div><h2 style='font-size:26px'>KES {total_shares:,.2f}</h2></div></div>"
    h += '''<div class="card"><div style="display:flex;justify-content:space-between;align-items:center;gap:12px;flex-wrap:wrap"><div><div class="eyebrow">Schedule</div><h2 style="margin:0">Member Share-Out Schedule</h2></div><a class="btn2 gold" href="/download/shareout">Download Excel</a></div><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="margin:14px 0"><div style="overflow:auto"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share Payable</th></tr><tbody id="shareBody">'''
    for i, x in enumerate(shares, 1): h += f"<tr data-search='{(x['full_names'] + ' ' + x['staff_no'] + ' ' + x['project']).lower()}'><td>{i}</td><td><b>{x['full_names']}</b><div style='font-size:11px;color:#667085'>{x['staff_no']} &middot; {x['email']}</div></td><td><span class='pill'>{x['project']}</span></td><td>{x['month_joined'] or '-'}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>"
    h += "</tbody></table></div></div><script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(r=>{r.style.display=r.getAttribute('data-search').includes(q)?'':'none'})}</script>"
    return shell("Share-Out", h)
@app.route("/download/shareout")
def download_shareout():
    shares, total_contrib, total_months, per_month_rate = calc_shares()
    from openpyxl import Workbook
    from openpyxl.styles import Font, PatternFill, Alignment
    wb = Workbook(); ws = wb.active; ws.title = "Share-Out"
    ws.append(["F.I.G BRANDS WELFARE - SHARE-OUT SCHEDULE"]); ws.append(["BF less 200,000 shared per month of contributions"])
    ws.append([f"BF: {BF:,} | Retained: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Months: {total_months} | Value of One Month: {per_month_rate:,.2f} | Total Contributions: {total_contrib:,}"]); ws.append([])
    ws.append(["#","Staff No","Full Names","Project","Date Joined","Months Contributed","Contribution (Months x 300)","Share Payable"])
    for c in ws[5]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0A1F33"); c.alignment = Alignment(horizontal="center", vertical="center")
    for i, x in enumerate(shares, 1): ws.append([i, x["staff_no"], x["full_names"], x["project"], x["month_joined"], x["months"], x["contribution"], round(x["share"], 2)])
    ws.append([]); ws.append(["","","","","","TOTAL", total_contrib, round(sum(x["share"] for x in shares), 2)]); ws.append(["","","","","","RETAINED IN ACCOUNT","", RESERVE]); ws.append(["","","","","","BALANCE BROUGHT FORWARD","", round(sum(x["share"] for x in shares), 2) + RESERVE])
    ws.freeze_panes = "A6"; ws.auto_filter.ref = ws.dimensions
    for col, w in zip("ABCDEFGH", [6, 14, 30, 22, 14, 18, 20, 20]): ws.column_dimensions[col].width = w
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
@app.route("/members")
def members_page():
    body = '''<div class="eyebrow">Directory</div><h1 style="font-size:42px">Members</h1><p id="memberCountLabel" style="color:#475569"></p><div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap"><input class="input" id="q" placeholder="Search by name, staff, project" oninput="fil()" style="flex:2;min-width:200px"><select class="input" id="projFilter" onchange="fil()" style="flex:1;min-width:160px"><option value="All Projects">All Projects</option></select></div><div id="list" style="margin-top:14px"></div><a class="btn2" href="/download/excel">Download Excel</a></div><script>let all=[];async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('memberCountLabel').textContent=d.total_members+' members — filter shows count per project';let sel=document.getElementById('projFilter');sel.innerHTML='<option value="All Projects">All Projects ('+d.total_members+')</option>';(d.projects||[]).forEach(p=>{let o=document.createElement('option');o.value=p;o.textContent=p+' ('+(d.projects_breakdown[p]||0)+')';sel.appendChild(o)});let r2=await fetch('/api/members');let dd=await r2.json();all=dd.members;render(all)}function row(l,v){return '<div class="row"><span style="color:#6B7280">'+l+'</span><b>'+(v||'-')+'</b></div>'}function render(l){let h='';l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<div class="card"><div style="display:flex;justify-content:space-between;gap:12px;align-items:flex-start"><div><b style="font-family:Fraunces,Georgia,serif;font-size:19px">'+m.full_names+'</b><div style="color:#6B7280;font-size:13px">'+m.email+'</div></div><span class="pill">'+m.project+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID',m.guardian_id)+row('Spouse ID',m.spouse_id)+row('Kids Birth Certs',kids)+'</div>'});document.getElementById('list').innerHTML=h||'No members found'}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(m=>(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(qq)&&(pf=='All Projects'||m.project==pf)))}load();</script>'''
    return shell("Members", body)
@app.route("/register")
def register_page():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    body = '''<div class="eyebrow">New Member</div><h1 style="font-size:42px">Register Member</h1><div class="card"><div style="display:flex;gap:16px;align-items:center"><div onclick="document.getElementById('photoInput').click()" style="width:96px;height:96px;border-radius:999px;border:1px solid #D9D0BF;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer;background:#F7F5F0"><img id="photoPreview" style="display:none;width:100%;height:100%;object-fit:cover"><span id="photoPlaceholder" style="font-size:12px;font-weight:600;color:#475569">Add Photo</span></div><div><b style="font-family:Fraunces,Georgia,serif;font-size:18px">Member Photo</b><div style="color:#6B7280;font-size:13px">Max 2MB, JPG or PNG</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div></div>'''
    for sec, fields in [("1. Staff Information", [("staff_no","Staff Number","text"),("project","Project","select"),("month_joined","Date Joined","text"),("full_names","Full Names","text"),("email","Email","text"),("password","Password","password")]), ("2. Parents IDs", [("father_id","Father ID","text"),("mother_id","Mother ID","text")]), ("3. Guardian and Spouse", [("guardian_id","Guardian ID No.","text"),("spouse_id","Spouse ID No.","text")]), ("4. Kids Birth Certificates", [("kid1","Kid 1","text"),("kid2","Kid 2","text"),("kid3","Kid 3","text"),("kid4","Kid 4","text"),("kid5","Kid 5","text")])]:
        body += f"<h3 style='margin-top:22px'>{sec}</h3><div class='grid'>"
        for fid, label, typ in fields:
            if fid == "project": body += f"<div><label>{label}</label><select class='input' id='project'>{opts}</select></div>"
            else: body += f"<div><label>{label}</label><input class='input' id='{fid}' type='{typ}'></div>"
        body += "</div>"
    body += '''<button class="btn" onclick="doReg()" id="btn" style="margin-top:20px">Create Member</button><p id="msg"></p></div><script>let photoBase64="";function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>2*1024*1024){alert('File too large');return}let r=new FileReader();r.onload=function(ev){photoBase64=ev.target.result;document.getElementById('photoPreview').src=photoBase64;document.getElementById('photoPreview').style.display='block';document.getElementById('photoPlaceholder').style.display='none'};r.readAsDataURL(f)}async function doReg(){let d={};["staff_no","project","full_names","email","password","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>{d[k]=document.getElementById(k).value});d.photo=photoBase64;if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';return}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;if(r.ok)setTimeout(()=>location.href='/members',800)}</script>'''
    return shell("Register", body)
@app.route("/admin")
def admin_login_page():
    body = '''<div class="eyebrow">Secure Area</div><h1 style="font-size:42px">Admin Login</h1><div class="card"><label>Email</label><input class="input" id="email" value="admin@lonma.com"><div style="margin-top:14px"><label>Password</label><input class="input" id="pass" type="password" value="admin123"></div><button class="btn" onclick="login()" style="margin-top:18px">Login</button><p id="msg"></p></div><script>async function login(){let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('pass').value})});let j=await r.json();if(r.ok)location.href='/admin/dashboard?key='+j.key;else document.getElementById('msg').textContent=j.error}</script>'''
    return shell("Admin", body)
@app.route("/admin/dashboard")
def admin_dashboard():
    if request.args.get("key") != ADMIN_KEY: return redirect("/admin")
    body = '''<div class="eyebrow">Administration</div><h1 style="font-size:42px">Admin Dashboard</h1><div class="card"><button class="btn" onclick="clearAll()" style="background:#9A1B1B">Clear All Data</button><p id="clearMsg"></p></div><div class="card"><h2>Members</h2><a class="btn2" href="/download/excel">Download Excel</a><div id="tbl" style="margin-top:12px"></div></div><div class="card"><h2>Support Messages</h2><div id="supList">Loading...</div></div><script>async function clearAll(){if(!confirm('DELETE ALL MEMBERS + HISTORY? Cannot be undone. Download Excel first.'))return;let r=await fetch('/api/clear-all?key=''' + ADMIN_KEY + ''',{method:'POST'});let j=await r.json();document.getElementById('clearMsg').textContent=j.message||j.error;load()}async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{h+='<div class="row"><span><b>'+m.staff_no+'</b> '+m.full_names+'<div style="color:#6B7280">'+m.email+'</div></span><span>'+m.project+' <button onclick="del('+m.id+')" style="border:1px solid #E9E2D6;background:#fff;border-radius:999px;padding:6px 10px;cursor:pointer">Delete</button></span></div>'});document.getElementById('tbl').innerHTML=h||'No members';let r2=await fetch('/api/support_list');let d2=await r2.json();document.getElementById('supList').innerHTML=d2.messages.map(m=>'<div style="padding:8px 0;border-bottom:1px solid #eee"><b>'+(m.name||'Guest')+'</b> '+m.msg+'</div>').join('')||'No messages'}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key=''' + ADMIN_KEY + ''',{method:'DELETE'});let j=await r.json();if(!r.ok)alert(j.error);load()}load();</script>'''
    return shell("Admin Dashboard", body)
@app.route("/download/excel")
def download_excel():
    proj = request.args.get("project",""); c = get_db()
    try:
        q = "SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"; a = (ADMIN_EMAIL,)
        if proj and proj != "All Projects": q = "SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a = (ADMIN_EMAIL, norm_project(proj))
        rows = c.execute(q, a).fetchall(); headers = ["Staff Number","Full Names","Project","Email","Date Joined","Father ID","Mother ID","Guardian ID","Spouse ID","Kid 1","Kid 2","Kid 3","Kid 4","Kid 5"]
        from openpyxl import Workbook
        from openpyxl.styles import Font, PatternFill, Alignment
        wb = Workbook(); ws = wb.active; ws.title = "Members"; ws.append(headers)
        for cell in ws[1]: cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="0A1F33"); cell.alignment = Alignment(horizontal="center")
        for r in rows: ws.append([r[x] or "" for x in ["staff_no","full_names","project","email","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]])
        ws.freeze_panes = "A2"; ws.auto_filter.ref = ws.dimensions; out = io.BytesIO(); wb.save(out); out.seek(0)
        return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_BRANDS_Members.xlsx")
    finally: c.close()
@app.route("/api/stats")
def api_stats():
    c = get_db()
    try:
        total = c.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        rows = c.execute("SELECT project, COUNT(*) AS n FROM users WHERE email != ? GROUP BY project ORDER BY project", (ADMIN_EMAIL,)).fetchall()
        merged = {}
        for r in rows:
            k = norm_project(r["project"]); merged[k] = merged.get(k, 0) + r["n"]
        ordered = {p: merged.get(p, 0) for p in PROJECTS if p in merged}
        for k, v in merged.items():
            if k not in ordered: ordered[k] = v
        return jsonify({"total_members": total, "projects_total": len(merged), "projects": list(ordered.keys()), "projects_breakdown": ordered})
    finally: c.close()
@app.route("/api/clear-all", methods=["POST"])
def api_clear_all():
    if request.args.get("key") != ADMIN_KEY: return jsonify({"error": "Admin key required"}), 401
    c = get_db()
    try:
        c.execute("DELETE FROM users WHERE email != ?", (ADMIN_EMAIL,))
        c.execute("DELETE FROM notifications"); c.execute("DELETE FROM support_msgs"); c.execute("DELETE FROM beneficiaries2"); c.execute("DELETE FROM fares2"); c.commit()
        return jsonify({"message": "All data cleared. Only admin remains."})
    finally: c.close()
@app.route("/api/repair", methods=["POST"])
def api_repair():
    if request.args.get("key") != ADMIN_KEY: return jsonify({"error": "Admin key required"}), 401
    init_db()
    return jsonify({"message": "v85 - 125 re-seeded / updated"})
@app.route("/api/breakdown")
def api_breakdown():
    return jsonify({"periods": PERIODS, "monthly_individual": MONTHLY_INDIVIDUAL, "beneficiaries": [], "beneficiaries_total": 0, "fares": [], "grand_total": 0, "bf": BF, "transfer_total": 0})
@app.route("/api/shareout")
def api_shareout():
    shares, total_contrib, total_months, per_month_rate = calc_shares()
    return jsonify({"bf": BF, "reserve": RESERVE, "distributable": DISTRIBUTABLE, "total_contributions": total_contrib, "total_months": total_months, "per_month_rate": round(per_month_rate, 2), "members": len(shares), "total_shares": round(sum(x["share"] for x in shares), 2), "shares": shares})
@app.route("/api/notifications")
def api_notifs():
    c = get_db()
    try:
        rows = c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall(); notifs = [dict(r) for r in rows]; unread = sum(1 for n in notifs if not n.get("is_read"))
        return jsonify({"notifications": notifs, "unread": unread, "total": len(notifs)})
    finally: c.close()
@app.route("/api/notifications/read", methods=["POST"])
def api_notifs_read_all():
    c = get_db()
    try: c.execute("UPDATE notifications SET is_read=1"); c.commit(); return jsonify({"message": "All read", "unread": 0})
    finally: c.close()
@app.route("/api/notifications/<int:nid>/read", methods=["POST"])
def api_notif_read_one(nid):
    c = get_db()
    try:
        c.execute("UPDATE notifications SET is_read=1 WHERE id=?", (nid,)); c.commit(); row = c.execute("SELECT * FROM notifications WHERE id=?", (nid,)).fetchone()
        return jsonify({"message": "Read", "notification": dict(row) if row else None})
    finally: c.close()
@app.route("/api/support", methods=["POST"])
def api_support():
    d = request.get_json(silent=True) or {}; c = get_db()
    try: c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))", (d.get("name","Guest"), d.get("msg",""))); c.commit(); return jsonify({"message": "Message sent. Support will reply soon."})
    finally: c.close()
@app.route("/api/support_list")
def api_support_list():
    c = get_db()
    try:
        rows = c.execute("SELECT * FROM support_msgs ORDER BY id DESC").fetchall(); return jsonify({"messages": [dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/members")
def api_members():
    proj = request.args.get("project",""); c = get_db()
    try:
        q = "SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"; a = (ADMIN_EMAIL,)
        if proj and proj != "All Projects": q = "SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a = (ADMIN_EMAIL, norm_project(proj))
        rows = c.execute(q, a).fetchall(); return jsonify({"members": [dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/members_admin")
def api_members_admin():
    c = get_db()
    try:
        rows = c.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users ORDER BY id DESC").fetchall(); return jsonify({"members": [dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/admin/login", methods=["POST"])
def api_admin_login():
    d = request.get_json(silent=True); c = get_db()
    try:
        u = c.execute("SELECT password,api_key FROM users WHERE email=?", (d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"], d.get("password","")): return jsonify({"error": "Invalid"}), 401
        return jsonify({"key": u["api_key"]})
    finally: c.close()
@app.route("/api/register", methods=["POST","OPTIONS"])
def api_register():
    if request.method == "OPTIONS": return "", 200
    d = request.get_json(silent=True)
    if not d or not d.get("email") or not d.get("password"): return jsonify({"error": "Email and password required"}), 400
    c = get_db()
    try:
        if c.execute("SELECT id FROM users WHERE email=?", (d["email"],)).fetchone(): return jsonify({"error": "Email exists"}), 400
        photo = d.get("photo","")
        if len(photo) > 500000: photo = photo[:500000]
        proj = norm_project(d.get("project","HQ"))
        if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)", (d.get("full_names",""),)).fetchone(): return jsonify({"error": "Name exists"}), 400
        vals = (d.get("staff_no",""), d.get("full_names",""), proj, d["email"], generate_password_hash(d["password"]), "fig_"+secrets.token_hex(12), d.get("month_joined",""), d.get("father_id",""), d.get("mother_id",""), d.get("guardian_id",""), d.get("spouse_id",""), d.get("kid1",""), d.get("kid2",""), d.get("kid3",""), d.get("kid4",""), d.get("kid5",""), photo)
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)", vals)
        c.execute("INSERT INTO notifications (title,msg,created,target,is_read) VALUES (?,?,?,?,?)", ("New Member Registered", f"{d.get('full_names','')} joined {proj}", "Just now", "/members", 0)); c.commit(); return jsonify({"message": "Member created"}), 201
    except Exception as e: return jsonify({"error": str(e)}), 400
    finally: c.close()
@app.route("/api/members/<int:member_id>", methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method == "OPTIONS": return "", 200
    if request.args.get("key") != ADMIN_KEY: return jsonify({"error": "Admin key required"}), 401
    c = get_db()
    try:
        u = c.execute("SELECT email FROM users WHERE id=?", (member_id,)).fetchone()
        if not u or u["email"] == ADMIN_EMAIL: return jsonify({"error": "Cannot delete Protected Admin"}), 403
        c.execute("DELETE FROM users WHERE id=?", (member_id,)); c.commit(); return jsonify({"message": "Deleted"})
    finally: c.close()
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
