from flask import Flask,request,jsonify,render_template_string,redirect,send_file
import sqlite3,os,secrets,io,re,datetime
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__)
DB="lonma.db"
PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PWANI_LOGO="https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png"
JAVA_LOGO="https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_l.jpg"
SCJ_LOGO="https://bhp-plus.pl/usr/s.c.-johnson-logo.png"
HIGHCHEM_LOGO="https://directory.africa-business.com/assets/uploads/logo/highchemafrica1.png"
TRUFOODS_LOGO="https://www.viprocgeneralenterprises.co.ke/site-images/Trufoods%20Limited.jpg"
LOGOS={"Pwani Oil Products":PWANI_LOGO,"Java House":JAVA_LOGO,"SC Johnson":SCJ_LOGO,"Higchem":HIGHCHEM_LOGO,"TF WSL":TRUFOODS_LOGO,"TF-LM":TRUFOODS_LOGO,"TF-MT":TRUFOODS_LOGO,"Kanji":TRUFOODS_LOGO}
PMAP={"Antonio":"Antonia","ANTONIA":"Antonia","Antonia":"Antonia","GCB-MT":"GCB-MT","GCB MT":"GCB-MT","GCB":"GCB-MT","GCB-Ws":"GCB-TDs","GCB Ws":"GCB-TDs","GCB TDS":"GCB-TDs","GCB-TDs":"GCB-TDs","GCB-TDS":"GCB-TDs","Higchem":"Higchem","HIGHCHEM":"Higchem","HIGCHEM MARKETING LIMITED":"Higchem","Hichem":"Higchem","Highchem":"Higchem","HQ":"HQ","Kanji":"Kanji","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","Java House":"Java House","JAVA":"Java House","Java":"Java House","Pwani Oil Products":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","SC Johnson":"SC Johnson","SJ Johnson":"SC Johnson","JOHNSON":"SC Johnson","Johnson":"SC Johnson","SJ":"SC Johnson","SCJohnson":"SC Johnson","Scjohnsons":"SC Johnson","scjohnsons":"SC Johnson","TF WSL":"TF WSL","TF WS":"TF WSL","TF-WS":"TF WSL","TF":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
def norm_project(p):
 p=(p or "").strip()
 if p in PMAP:
  return PMAP[p]
 up=" ".join(p.upper().split())
 if up in PMAP:
  return PMAP[up]
 return PMAP.get(p.title(),p or "Pwani Oil Products")
def project_logo(p):
 return LOGOS.get(norm_project(p),"")
ADMIN_KEY=os.environ.get("ADMIN_KEY","lonma_api_key_12345").strip()
ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL","marlonkikuyu@gmail.com").strip().lower()
ADMIN_PASS=os.environ.get("ADMIN_PASS","admin123")
BF=855759
RESERVE=250000
DISTRIBUTABLE=BF-RESERVE
MONTHLY_RATE=300
PERIOD_START=(2025,12)
PERIOD_END=(2026,9)
PERIODS=[{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200 | Kaysalt 72,900 | Kanji 12,600 | HQ 15,900 | GCB-MT 69,900 | TF-WS 71,100 | TF-LM 173,100 | TF-MT 259,500 | Kenafric 96,900 | GCB-TDs 51,000 | LAB 7,800"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400 | Kanji 9,900 | HQ 14,100 | GCB-MT 56,700 | TF-WS 49,200 | TF-LM 122,400 | TF-MT 236,100 | GCB-TDs 41,100 | Higchem 30,000 | Antonia 3,600"}]
SEED_TXT='''10009|Pwani Oil Products|2024|Esther Wambui Kimani||||||||
10025|Pwani Oil Products|2024|Nostar Nyanchama Osiemo||||||||
10043|Pwani Oil Products|2024|Doreen Talu Mwanga||||||||
10047|Pwani Oil Products|2024|Winnie Jemutai Chepkwony||||||||
10048|Pwani Oil Products|2024|Millianna Anyango Sadaka||||||||
10050|Pwani Oil Products|2024|Samuel Kikweo Nthenya||||||||
10052|Pwani Oil Products|2024|Stephen Wesonga Ouma||||||||
10072|Pwani Oil Products|2024|MARY WANGARI MWIMENYI||||||||
10073|Pwani Oil Products|2024|Linet Awino Wayumba||||||||
10077|Pwani Oil Products|2024|Celestine Achieng'||||||||
10093|Pwani Oil Products|2024|Diana Nanjala Wafula||||||||
10094|Pwani Oil Products|2024|NJUGU RISPA WANYAGA||||||||
10099|Pwani Oil Products|2024|Phoebe Anyango Oliech||||||||
10100|Pwani Oil Products|2024|Owen Muthee Waithaka||||||||
10101|Pwani Oil Products|2024|George Mbithi Maingi||||||||
10106|Pwani Oil Products|2024|Gwen Moraa Kegege||||||||
10108|Pwani Oil Products|2024|Polly Wangui Nyaguthii||||||||
10111|Pwani Oil Products|2024|Sally Kanaiza Barasa||||||||
10112|Pwani Oil Products|2024|Evans Mwaita Ngoma||||||||
10320|Pwani Oil Products|2024|Gabriel Michael Mutisya||||||||
10321|Pwani Oil Products|2024|Jack Omondi Juma||||||||
10322|Pwani Oil Products|2024|Samuel Njeru Njiru||||||||
10323|Pwani Oil Products|2024|Marlon Ang'undu Kikuyu||||||||
10324|Pwani Oil Products|2024|Getrude Juma Juma||||||||
10325|Pwani Oil Products|2024|Maradi Ruth Mercylyne||||||||
10329|Pwani Oil Products|2024|Victor Meso Onyango||||||||
10330|Pwani Oil Products|2024|Meshack Ouma Ojwang||||||||
10331|Pwani Oil Products|2024|Eunice Nafula Makona||||||||
10333|Pwani Oil Products|2024|Nannis Karambu Samuel||||||||
10334|Pwani Oil Products|2024|Maureen Wambui Kimani||||||||
10335|Pwani Oil Products|2024|Evaperpetual Wambui Maina||||||||
10336|Pwani Oil Products|2024|Millicent Njeri Matheng'e||||||||
10337|Pwani Oil Products|2024|Lydia Karambu Matumbi||||||||
10338|Pwani Oil Products|2024|Margaret Wambui Kamunya||||||||
10339|Pwani Oil Products|2024|Caroline Wanja Wanja||||||||
10340|Pwani Oil Products|2024|Peris Wangari Muriithi||||||||
10341|Pwani Oil Products|2024|Alex Kalawai Shangala||||||||
10342|Pwani Oil Products|2024|Meggiline Nyakerario Abuga||||||||
10343|Pwani Oil Products|2024|Charles Savatia Adika||||||||
10344|Pwani Oil Products|2024|Gorrety Adhiambo Otieno||||||||
10345|Pwani Oil Products|2024|Janet Akinyi Oswago||||||||
10346|Pwani Oil Products|2024|Lydiah Nyaanga Osengo||||||||
10348|Pwani Oil Products|2024|Naomi Mwango Abenga||||||||
10349|Pwani Oil Products|2024|Postine Atieno Atieno||||||||
10350|Pwani Oil Products|2024|Sophia Nyamoita Mokaya||||||||
10351|Pwani Oil Products|2024|Charles Kimutai Kirui||||||||
10352|Pwani Oil Products|2024|Clare Vuyanzi Osiako||||||||
10353|Pwani Oil Products|2024|Everlyne mukoya Stephen||||||||
10355|Pwani Oil Products|2024|Peter Kibet Chepsigor||||||||
10356|Pwani Oil Products|2024|Sheillah Jepchumba||||||||
10357|Pwani Oil Products|2024|Betty Akinyi Namamba||||||||
10358|Pwani Oil Products|2024|Alex Esamai||||||||
10360|Pwani Oil Products|2024|Caren Nanjala Chonge||||||||
10362|Pwani Oil Products|2024|Fredrick Nick Osotsi||||||||
10363|Pwani Oil Products|2024|Hellen Achieng Onyango||||||||
10366|Pwani Oil Products|2024|Odiembo Yvonne Awuor||||||||
10367|Pwani Oil Products|2024|Awuor Cynthia Onyango||||||||
10368|Pwani Oil Products|2024|Opiyo Irene Achieng||||||||
10369|Pwani Oil Products|2024|Oduor Stephen Oduor||||||||
10371|Pwani Oil Products|2024|Owino Maurine Achieng||||||||
10372|Pwani Oil Products|2024|Muchuma Lilian Khalituma||||||||
10373|Pwani Oil Products|2024|Oyoyo Yvonne Benter||||||||
10375|Pwani Oil Products|2024|Kabera Edith Mmaitsi||||||||
10376|Pwani Oil Products|2024|Adiel John Erick||||||||
10377|Pwani Oil Products|2024|Imali Laura Imali||||||||
10378|Pwani Oil Products|2024|Joan Mumbi Kahura||||||||
10379|Pwani Oil Products|2024|Harriet Kaveza Olome||||||||
10381|Pwani Oil Products|2024|Margaret Mugure Ngaruiya||||||||
10382|Pwani Oil Products|2024|Hannah Muthoni Ngaruiya||||||||
10385|Pwani Oil Products|2024|Peter Ikegu Mwaniki||||||||
10386|Pwani Oil Products|2024|Rachel Wanjiku Ndungu||||||||
10387|Pwani Oil Products|2024|Lydia Achieng Asaka||||||||
10389|Pwani Oil Products|2024|Maureen Omuchinia Analo||||||||
10390|Pwani Oil Products|2024|George Ibuba Nganga||||||||
10391|Pwani Oil Products|2024|Mary Wambui Kahiga||||||||
10397|Pwani Oil Products|2024|Jairus Oduor Makona||||||||
10399|Pwani Oil Products|2024|Merceline Adhiambo Osewe||||||||
10400|Pwani Oil Products|2024|Linet Achieng' Oduor||||||||
10402|Pwani Oil Products|2024|Metrine Cherop Chumo||||||||
10403|Pwani Oil Products|2024|Benta Achieng Muruka||||||||
10405|Pwani Oil Products|2024|Diana Atieno Oduor||||||||
10407|Pwani Oil Products|2024|Mercy Njeri Wanjiru||||||||
10410|Pwani Oil Products|2024|Dorcas Wangeshi Mwaurah||||||||
10415|Pwani Oil Products|2024|Henry Omondi Oganga||||||||
10417|Pwani Oil Products|2024|INGAVI JULIUS SESEDA||||||||
10419|Pwani Oil Products|2024|CORNELIUS MUTETI KIOKO||||||||
10431|Pwani Oil Products|2024|Joackim Bachwa Bachwa||||||||
11010|Pwani Oil Products|2024|Linda Kanana||||||||
11018|Pwani Oil Products|2024|Agatha Wanjiku Mbugua||||||||
11019|Pwani Oil Products|2024|Rhoda Akinyi Odhiambo||||||||
11020|Pwani Oil Products|2024|Elizabeth Matinde||||||||
11022|Pwani Oil Products|2024|Lavenda Anyango Otieno||||||||
11028|Pwani Oil Products|2024|Brendah Mijidie Kiduyu||||||||
11113|Pwani Oil Products|2024|Bernice Katende Muthoka||||||||
11119|Pwani Oil Products|2024|Fridah Kathure Gatobu||||||||
12169|Pwani Oil Products|2024|Boniface Museve Ashiona||||||||
16322|Pwani Oil Products|2024|SHARON WAFULA AJWANGI||||||||
17100|Pwani Oil Products|2024|DORICE AWINO ANYANGO||||||||
17102|Pwani Oil Products|2024|Clarice ACHIENG OMAYA||||||||
17103|Pwani Oil Products|2024|Teresia Mueni Kiama||||||||
30102|Java House|2024|EUGENE DAUDI AURA||||||||
30103|Java House|2024|WAMUYU IRENE WAIRIMU||||||||
30104|Java House|2024|LENNOX AMANI DANIEL||||||||
30105|Java House|2024|VICTORIA MBEKE NGAVE||||||||
30106|Java House|2024|HILLARY OMONDI ALINDI||||||||
30108|Java House|2024|FELIX KIARIE NDUNGU||||||||
30110|Java House|2024|CLAIRE WAMBUI KARIUKI||||||||
30111|Java House|2024|HELLEN AWUOR ODARI||||||||
30112|Java House|2024|ZAWERIA KARUNGARI WAIREGI||||||||
30113|Java House|2024|ANN WAMBUI MUCHEMI||||||||
30115|Java House|2024|ESTHER WANGARI KARANJA||||||||
30116|Java House|2024|EMILY WAITHERA NJENGA||||||||
30117|Java House|2024|JUDITH CHEPNG'ENO||||||||
30119|Java House|2024|MICHAEL ONDIEKI KEROSI||||||||
30120|Java House|2024|GLORIA MUKHWANA LUSENAKA||||||||
30121|Java House|2024|Judith Lozenjah Ominde||||||||
30126|Java House|2024|Edwin Ondieki Kiyaka||||||||
30129|Java House|2024|GLADYS KINUTHIA||||||||
30131|Java House|2024|Onganga Gwako Edmond||||||||
30133|Java House|2024|DIANA KATHURE||||||||
38103|GCB-MT|2024|Evelyne Mpinda Kinyua||||||||
38104|GCB-MT|2024|Hillary Nzive Kasiva||||||||
38105|GCB-MT|2024|Mariamu Ali Juma||||||||
38106|GCB-MT|2024|Dennis Mbindyo Mwamuli||||||||
38107|GCB-MT|2024|Stanely Muigai Njoroge||||||||
38108|GCB-MT|2024|Josyline Nkatha Karambu||||||||
38109|GCB-MT|2024|Caroline Gaceri Kimathi||||||||
38111|GCB-MT|2024|Peter Omondi Onyango||||||||
38112|GCB-MT|2024|Mary Ngotah||||||||
38116|GCB-MT|2024|Teresa Mwihaki Gichuki||||||||
38117|GCB-MT|2024|Carol Wanjiku Njuguna||||||||
38118|GCB-MT|2024|Mercy Jepkorir Yatich||||||||
38120|GCB-MT|2024|Dennis Muchangi Wanja||||||||
38122|GCB-MT|2024|Tabitha Wambui Mwangi||||||||
38123|GCB-MT|2024|Rabin Nyasinga Winston||||||||
38124|GCB-MT|2024|Cynthia Obaga lwangu||||||||
38125|GCB-MT|2024|Pennina Awuor Olango||||||||
38129|GCB-MT|2024|Ruth Waitherero Kihugu||||||||
38130|GCB-MT|2024|Ferdinand Kafwa||||||||
38133|GCB-MT|2024|Emily Mueni Mutua||||||||
38135|GCB-MT|2024|Mourin Wangui Karomo||||||||
38139|GCB-MT|2024|Abel Nyandega Rasugu||||||||
38140|GCB-MT|2024|Samwel Erick Odhiambo||||||||
40103|TF-LM|2024|Phylis Khayenga Barasa||||||||
40105|TF-LM|2024|Caroline Nkatha Mbaya||||||||
40106|TF-LM|2024|Mercy Mwikali Muthio||||||||
40108|TF-LM|2024|Jackline Wambui Mwendia||||||||
40109|TF-LM|2024|Joyce Wambui Wanjiru||||||||
40110|TF-LM|2024|Linda Atieno Odhiambo||||||||
40112|TF-LM|2024|Samuel Sidhani Menza||||||||
40115|TF-LM|2024|Lucy Muhanji||||||||
40118|TF-LM|2024|Josiah Manua Misiani||||||||
40119|TF-LM|2024|Peter Ondieki Onyoni||||||||
40120|TF-LM|2024|Susan Wambui Ndung'u||||||||
40125|TF-LM|2024|Mueni Kisingu||||||||
40126|TF-LM|2024|Jonathan Mutunga Kilonzo||||||||
40127|TF-LM|2024|Gladys Nyamuhu Nyaga||||||||
40130|TF-LM|2024|Matilder Jepkoech Chelimo||||||||
40131|TF-LM|2024|Purity Wangechi Kariuki||||||||
40132|TF-LM|2024|Esther Awuor Marenya||||||||
40135|TF-LM|2024|Brian Odhiambo Otieno||||||||
40322|TF-MT|2024|Leah Wangui Njeri||||||||
40323|TF-MT|2024|Daniel Ejikon||||||||
40414|TF-MT|2024|Veronicah Khevali Mukulwe||||||||
40416|TF-MT|2024|Hellen Mbesa Mumbi||||||||
40417|TF-MT|2024|Zainab Chizi Suleiman||||||||
40418|TF-MT|2024|Lolonancy Mambori Mghenyi||||||||
40419|TF-MT|2024|Raphael Mwenja Kagondo||||||||
40420|TF-MT|2024|Isaack Kagunda King'ori||||||||
40434|TF-MT|2024|Esther Awuor Agutu||||||||
40440|TF-MT|2024|Mirriam Muthoni||||||||
40442|TF-MT|2024|Faith Ingadima Bunyali||||||||
40446|TF-MT|2024|Valerian Kemunto Misati||||||||
40447|TF-MT|2024|Joshua Mwangi Iguna||||||||
40451|TF-MT|2024|Kelvin Orina Sabwengi||||||||
40455|TF-MT|2024|Blossom Nangila Wanyonyi||||||||
40459|TF-MT|2024|Antony Manyara Chania||||||||
40462|TF-MT|2024|Queen Ndila Mwania||||||||
40463|TF-MT|2024|Ruth Amolo Nyangun||||||||
40464|TF-MT|2024|Caleb Kibet Kirui||||||||
40469|TF-MT|2024|Emmah Adhiambo Waswa||||||||
40471|TF-MT|2024|Mary Joyce Wangeci Thika||||||||
40472|TF-MT|2024|Purity Ndinda Ndunda||||||||
40473|TF-MT|2024|Jackline Kamene Daniel||||||||
40474|TF-MT|2024|Maureen Gathiru Mwaniki||||||||
44031|TF WSL|2024|Oscar Kipkoech Ruto||||||||
50030|TF WSL|2024|Faith Angulu Anyona||||||||
50039|TF WSL|2024|Valary Chepkoech Bii||||||||
55123|TF WSL|2024|Mercy Mwende||||||||
55124|TF WSL|2024|Winfred Mukuba Mbaabu||||||||
60127|SC Johnson|2024|Prisca Anjemo Injili||||||||
60131|SC Johnson|2024|BRENDAH ACHIENG GUMBA||||||||
60148|SC Johnson|2024|Paul Janes Okombo||||||||
60156|SC Johnson|2024|Pauline Wambui Masila||||||||
60182|SC Johnson|2024|Anne Kamonya Mulema||||||||
60186|SC Johnson|2024|Daniel Katumo Musyoka||||||||
60192|SC Johnson|2024|Mercy Waringa Waweru||||||||
60198|SC Johnson|2024|Scholastica Loko Kilonzi||||||||
60200|SC Johnson|2024|Winfred Katungwa Mulee||||||||
60208|SC Johnson|2024|Loise Njoki Kibaiyu||||||||
60218|SC Johnson|2024|Melvin Mumo Kimondiu||||||||
70201|TF-MT|2024|Irene Atieno Ogutu||||||||
70202|TF-MT|2024|Vicky Hellen Otieno||||||||
70203|TF-MT|2024|Mercy Achieng Onyango||||||||
70204|TF-MT|2024|Mourine Akoth||||||||
70205|TF-MT|2024|Faith Atieni Ogembo||||||||
70206|TF-MT|2024|Innolyne Anyango Agutu||||||||
70207|TF-MT|2024|Lena Cherono Cheruiyot||||||||
70208|TF-MT|2024|Jackline Kavere Ayiga||||||||
70211|TF-MT|2024|George Okeyo Owiti||||||||
70213|TF-MT|2024|Naomi Jeruto Tanui||||||||
70216|TF-MT|2024|Linda Achieng Oduor||||||||
70217|TF-MT|2024|John Gatitu Mwangi||||||||
70219|TF-MT|2024|Mary Wangari Mwangi||||||||
70220|TF-MT|2024|Maryanne Wanjiru Kariuki||||||||
70221|TF-MT|2024|Pamela Awuor Nyadodo||||||||
70222|TF-MT|2024|Damaris Muyoka Wekesa||||||||
70223|TF-MT|2024|Gladys Wangeci Wahogo||||||||
70224|TF-MT|2024|Laura Akumu Barasa||||||||
70226|TF-MT|2024|Jane Wairimu||||||||
70228|TF-MT|2024|Joseph Musyoka Mwasaru||||||||
70229|TF-MT|2024|Daniel Ombui Mayaka||||||||
70230|TF-MT|2024|Joyce Wangeci Murithi||||||||
70231|TF-MT|2024|Faith Mutunge Mutua||||||||
70234|TF-MT|2024|Elizabeth Kaluki Mbithe||||||||
70235|TF-MT|2024|Fiona Apiyo Omondi||||||||
70237|TF-MT|2024|Wellington Owino Lubale||||||||
70238|TF-MT|2024|Daniel Mwangi||||||||
70240|TF-MT|2024|Fidel Otieno||||||||
70241|TF-MT|2024|Martin Munene Grishon||||||||
70242|TF-MT|2024|Trizah Kabaki Wanjiku||||||||
70243|TF-MT|2024|Julius Musau Mwania||||||||
70246|TF-MT|2024|Abel Kiptoo Kosgei||||||||
70247|TF-MT|2024|Ann Mathei Maive||||||||
70250|TF-MT|2024|Samuel Nzau Muli||||||||
70251|TF-MT|2024|Thomas Felix Mwatu||||||||
77300|HQ|2024|Margaret Wangari George||||||||
77301|HQ|2024|Teresia Muthoni Kariuki||||||||
77311|HQ|2024|Colman Collins Were||||||||
77314|HQ|2024|Miriam Wanjera Wangui||||||||
80100|GCB-TDs|2024|Joice Wanjiru Mwaura||||||||
80101|GCB-TDs|2024|Pamela Oduor||||||||
80105|GCB-TDs|2024|Joane Wanjru||||||||
80106|GCB-TDs|2024|Catherine Mukami||||||||
80108|GCB-TDs|2024|Everlyn Nyambura||||||||
80111|GCB-TDs|2024|Wendy Charles||||||||
80113|GCB-TDs|2024|Phelistars Owino||||||||
80120|GCB-TDs|2024|Mwanaidi David Emiliana||||||||
80121|GCB-TDs|2024|Hellen Omiti Anyango||||||||
90100|Kanji|2024|Sarah Wamuyu Kinyua||||||||
90102|Kanji|2024|Anthony Njoroge Maina||||||||
90103|Kanji|2024|Racheal Mueni Matali||||||||
90105|Kanji|2024|Caroline Kathomi Njebiu||||||||
90107|Kanji|2024|Elizabeth Njuru Kariuki||||||||
90109|Kanji|2024|Mecyline Nelima Ndala||||||||
90110|Kanji|2024|Jackline Nduta Kamau||||||||
90111|Kanji|2024|Frankline Ombego Mokua||||||||
90115|Kanji|2024|Brenda Jepkogei Cheruiyot||||||||
90116|Kanji|2024|Mugwe Victoria Wangeci||||||||
90117|Kanji|2024|Hilda Esende lugali||||||||
90118|Kanji|2024|Fridah Olesi||||||||
90119|Kanji|2024|Phesial Jaramogi Ooyi||||||||
90120|Kanji|2024|Judith Oweya Lukale||||||||
90121|Kanji|2024|Emily Nanjala Wafula||||||||
90122|Kanji|2024|Afline Anyango Onyango||||||||
90123|Kanji|2024|Celestine Auma Ouko||||||||
90124|Kanji|2024|Euphate Sarange Kerubo||||||||
90125|Kanji|2024|Cyril Mari Sadak||||||||
98214|Higchem|2024|Benjamin Odiwuor Mboya||||||||
98218|Higchem|2024|George Wanderi Simon||||||||
99222|Antonia|2024|Elvis Emmanuel Shikuku||||||||
99227|Antonia|2024|Peurity Musebe Luseka||||||||
99228|Antonia|2024|Joseph Odhiambo||||||||
99231|Antonia|2024|Merselline Awuor Okode||||||||
99237|Antonia|2024|Kevin Kipkurui||||||||
99240|Antonia|2024|LYDIA NJOKI DAMARIAN||||||||
'''
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
def get_db():
 c=sqlite3.connect(DB,timeout=10,check_same_thread=False,isolation_level=None)
 c.row_factory=sqlite3.Row
 try:
  c.execute("PRAGMA journal_mode=WAL;")
  c.execute("PRAGMA busy_timeout=10000;")
 except:
  pass
 return c
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
  out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","join_year":get_join_year(r["month_joined"]),"months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0,"father_id":r["father_id"] or "","mother_id":r["mother_id"] or "","guardian_id":r["guardian_id"] or "","spouse_id":r["spouse_id"] or "","kids":kids,"kid1":r["kid1"] or "","kid2":r["kid2"] or "","kid3":r["kid3"] or "","kid4":r["kid4"] or "","kid5":r["kid5"] or "","logo":project_logo(r["project"])})
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
 print(f"v119 seeded {added}")
init_db()
@app.after_request
def after(r):
 r.headers.add('Access-Control-Allow-Origin','*')
 r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY')
 r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS')
 return r
@app.route("/favicon.ico")
def favicon():
 return '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="12" fill="#000"/><text x="32" y="42" font-family="Georgia, serif" font-size="20" font-weight="700" fill="#FFFFFF" text-anchor="middle">FIG</text></svg>',200,{"Content-Type":"image/svg+xml"}
COMPANY_BAR='''
<div style="background:#000;border-bottom:1px solid #2F3336;padding:10px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
<label style="font-weight:700;font-size:13px;color:#fff">Filter Company:</label>
<select id="companyFilter" onchange="onCompanyChange()" style="height:42px;background:#000;color:#fff;border:1px solid #2F3336;border-radius:999px;padding:0 10px;min-width:180px;font-size:14px">
<option value="">All Companies</option>
<option value="Antonia">Antonia</option>
<option value="GCB-MT">GCB-MT</option>
<option value="GCB-TDs">GCB-TDs</option>
<option value="Higchem">Higchem</option>
<option value="HQ">HQ</option>
<option value="Java House">Java House</option>
<option value="Kanji">Kanji</option>
<option value="Pwani Oil Products">Pwani Oil Products</option>
<option value="SC Johnson">SC Johnson</option>
<option value="TF WSL">TF WSL</option>
<option value="TF-LM">TF-LM</option>
<option value="TF-MT">TF-MT</option>
</select>
<button onclick="clearCompany()" style="height:42px;background:#1D9BF0;color:#fff;border:0;border-radius:999px;padding:0 14px;font-weight:700">Clear / All</button>
<span id="companyLabel" style="font-weight:700;color:#fff;font-size:13px"></span>
</div>
<script>
function getCompany(){return localStorage.getItem('lonma_company') || '';}
function setCompanyUI(){var c=getCompany();var el=document.getElementById('companyFilter');if(el)el.value=c;var lab=document.getElementById('companyLabel');if(lab)lab.innerText=c?'Showing: '+c:'Showing: All Companies';}
function onCompanyChange(){localStorage.setItem('lonma_company',document.getElementById('companyFilter').value);setCompanyUI();location.reload();}
function clearCompany(){localStorage.setItem('lonma_company','');setCompanyUI();location.reload();}
function companyQuery(){var c=getCompany();return c?'?project='+encodeURIComponent(c):'';}
function getEmail(){return localStorage.getItem('fig_email')||'guest@figbrands.co.ke';}
function getName(){return localStorage.getItem('fig_name')||'Member';}
setCompanyUI();
</script>
'''
def shell(title,body):
 full=COMPANY_BAR+body
 return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&display=swap" rel="stylesheet"><script>if(!localStorage.getItem('fig_user')&&location.pathname!='/login'&&location.pathname!='/register'){location.href='/login'}</script><style>*{box-sizing:border-box}body{font-family:Inter,sans-serif;background:#000;margin:0;padding-bottom:80px;color:#fff;overflow-x:hidden}.card{background:#000;border:1px solid #2F3336;border-radius:16px;padding:20px;margin-bottom:14px}.input{width:100%;height:48px;background:#000;border:1px solid #2F3336;border-radius:999px;padding:0 16px;color:#fff}.input::placeholder{color:#71767B}.btn-dark{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#fff;color:#000;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:700;font-size:14px;border:0}.btn-gold{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#1D9BF0;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:700;font-size:14px;border:0}.top{height:56px;background:#000;display:flex;align-items:center;gap:12px;padding:0 14px;position:sticky;top:0;z-index:20;border-bottom:1px solid #2F3336}.logo{width:40px;height:40px;border-radius:50%;background:#fff;color:#000;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:16px}.toplinks{background:#000;border-bottom:1px solid #2F3336;padding:10px 14px;display:flex;gap:24px;overflow-x:auto;white-space:nowrap;position:sticky;top:56px;z-index:15}.toplinks a{color:#E7E9EA;text-decoration:none;font-size:15px;font-weight:700}.page{max-width:1080px;margin:auto;padding:18px 14px 180px}.dark{background:#16181C;color:#fff;border-radius:16px;padding:22px;margin-bottom:14px;border:1px solid #2F3336}.gold{color:#1D9BF0;letter-spacing:1px;font-size:12px;font-weight:700}h1,h2{font-weight:800;color:#fff}table{width:100%;border-collapse:collapse;font-size:14px;color:#E7E9EA}th,td{padding:12px 10px;border-bottom:1px solid #2F3336;text-align:left}.nav{position:fixed;left:10px;right:10px;bottom:8px;height:60px;background:#000;border:1px solid #2F3336;border-radius:999px;display:flex;z-index:30}.nav a{flex:1;color:#E7E9EA;text-decoration:none;display:flex;align-items:center;justify-content:center;font-size:14px;font-weight:700}.xbtn{border:1px solid #2F3336;background:#000;color:#fff;border-radius:999px;padding:8px 14px;font-size:14px;cursor:pointer;font-weight:600}.xbtn.liked{background:#200A12;color:#F91880;border-color:#F91880}.xbtn.saved{background:#1A2A1A;color:#1D9BF0}.avatar{width:40px;height:40px;border-radius:50%;background:#333;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0}.projlogo{width:32px;height:32px;border-radius:50%;object-fit:cover;background:#222}
/* SLIDE DRAWER LIKE TWITTER */
#slideOverlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(91,112,131,0.4);z-index:100;opacity:0;pointer-events:none;transition:opacity .3s}
#slideOverlay.open{opacity:1;pointer-events:auto}
#slideDrawer{position:fixed;top:0;left:0;bottom:0;width:300px;max-width:85vw;background:#000;z-index:101;transform:translateX(-105%);transition:transform .32s ease;overflow-y:auto;border-right:1px solid #2F3336;box-shadow:20px 0 40px rgba(0,0,0,.6)}
#slideDrawer.open{transform:translateX(0)}
.drawer-head{padding:16px;display:flex;justify-content:space-between;align-items:flex-start}
.drawer-name{font-size:20px;font-weight:800;margin-top:10px}
.drawer-handle{color:#71767B;font-size:15px}
.drawer-follow{display:flex;gap:16px;margin-top:12px;font-size:15px}
.drawer-follow b{font-weight:800}
.drawer-follow span{color:#71767B}
.menu-item{display:flex;align-items:center;gap:18px;padding:13px 12px;font-size:19px;font-weight:700;color:#E7E9EA;text-decoration:none;border-radius:999px}
.menu-item:active{background:#181818}
.menu-item span.icon{font-size:22px;width:28px;text-align:center}
.badge{background:#1D9BF0;color:#fff;font-size:13px;font-weight:700;padding:3px 10px;border-radius:999px;margin-left:8px}
.badge-new{background:#1D9BF0;color:#fff;font-size:13px;font-weight:700;padding:3px 10px;border-radius:999px}
.divider{height:1px;background:#2F3336;margin:16px 0}
</style></head><body>
<div id="slideOverlay" onclick="closeDrawer()"></div>
<aside id="slideDrawer">
<div class="drawer-head"><div class="avatar" style="width:48px;height:48px;font-size:18px" id="drawerAvatar">MA</div><button onclick="closeDrawer()" style="background:none;border:0;color:#fff;font-size:22px;cursor:pointer">✕</button></div>
<div style="padding:0 16px"><div class="drawer-name" id="menuName">Marlon K.</div><div class="drawer-handle" id="menuHandle">@Mongela_h</div><div class="drawer-follow"><span><b>8,493</b> <span>Following</span></span><span><b>8,618</b> <span>Followers</span></span></div><div class="divider"></div>
<a class="menu-item" href="/members" onclick="closeDrawer()"><span class="icon">👤</span> Profile</a>
<a class="menu-item" href="/terms" onclick="closeDrawer()"><span class="icon">✓</span> Premium <span class="badge">50% off</span></a>
<a class="menu-item" href="/community" onclick="closeDrawer()"><span class="icon">📞</span> Calls</a>
<a class="menu-item" href="/community" onclick="closeDrawer()"><span class="icon">👥</span> Communities</a>
<a class="menu-item" href="/breakdown2" onclick="closeDrawer()"><span class="icon">🔖</span> History</a>
<a class="menu-item" href="/members" onclick="closeDrawer()"><span class="icon">☰</span> Lists</a>
<a class="menu-item" href="/community" onclick="closeDrawer()"><span class="icon">🎙️</span> Spaces</a>
<a class="menu-item" href="/admin" onclick="closeDrawer()"><span class="icon">🚀</span> Creator Studio</a>
<div class="divider"></div>
<a class="menu-item" href="/admin" onclick="closeDrawer()"><span class="icon">⏱️</span> Automate work <span class="badge-new">New</span></a>
<a class="menu-item" href="/admin" onclick="closeDrawer()"><span class="icon">⚙️</span> Settings and privacy</a>
<a class="menu-item" href="/terms" onclick="closeDrawer()"><span class="icon">🌙</span> Help Centre</a>
</div></aside>
<div class="top"><button onclick="openDrawer()" style="background:none;border:0;color:#fff;font-size:24px;cursor:pointer;padding:6px">☰</button><div class="logo">FIG</div><div><b style="font-size:17px">F.I.G BRANDS</b><div style="color:#71767B;font-size:12px">WELFARE SYSTEM</div></div><div style="margin-left:auto"><button onclick="openDrawer()" style="background:none;border:0;cursor:pointer"><span style="width:38px;height:38px;border-radius:50%;background:#333;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700">MA</span></button></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/community">Community</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/terms">Terms</a><a href="/admin">Admin</a></div><div class="page">'''+full+'''</div><nav class="nav"><a href="/">Home</a><a href="/members">Members</a><a href="/community">Community</a><a href="/shareout">Share-Out</a><a href="/terms">Terms</a><a href="/register">Add</a></nav>
<script>
function openDrawer(){document.getElementById('slideDrawer').classList.add('open');document.getElementById('slideOverlay').classList.add('open');document.body.style.overflow='hidden';}
function closeDrawer(){document.getElementById('slideDrawer').classList.remove('open');document.getElementById('slideOverlay').classList.remove('open');document.body.style.overflow='';}
var _startX=null;document.addEventListener('touchstart',function(e){_startX=e.touches[0].clientX;},{passive:true});document.addEventListener('touchend',function(e){if(_startX===null)return;var dx=e.changedTouches[0].clientX-_startX;if(_startX<30&&dx>60)openDrawer();if(dx<-60)closeDrawer();_startX=null;},{passive:true});
var _n=localStorage.getItem('fig_name');if(_n){document.getElementById('menuName').textContent=_n;document.getElementById('menuHandle').textContent='@'+_n.split(' ')[0].toLowerCase();document.getElementById('drawerAvatar').textContent=_n.charAt(0);}
</script></body></html>''')
@app.route("/")
def index():
 body='''<div class="card"><div class="gold">WELFARE CLAUSES 2026</div><h1 style="font-size:34px;line-height:1.2">Death Benefit: Member 100,000 &middot; Spouse 50,000 &middot; Child 40,000 &middot; Parents 40,000</h1><p style="color:#A1A1AA;line-height:1.6">Loss of Earning: 50% of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn-dark" href="/terms">Read Full Terms</a><a class="btn-gold" href="/community">Join Community Chat</a></div></div><div class="card"><div class="gold">DISTRIBUTION</div><h2 style="font-size:30px;margin:8px 0">Project Distribution <span id="bdYear" style="font-size:16px"></span></h2><div id="breakdown"></div><div style="margin-top:14px">Total Members: <b id="total">0</b></div></div><script>async function load(){let q=companyQuery();let r=await fetch('/api/stats'+q);let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('bdYear').textContent=getCompany()? '('+getCompany()+')':'(All Companies)';let h='';Object.keys(d.projects_breakdown).sort((a,b)=>d.projects_breakdown[b]-d.projects_breakdown[a]).forEach(k=>{let lg=d.logos[k]||'';let img=lg?'<img class="projlogo" src="'+lg+'">':'';h+='<div style="display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #2F3336"><span style="display:flex;gap:10px;align-items:center;font-size:18px;font-weight:600">'+img+k+'</span><b style="font-size:18px">'+d.projects_breakdown[k]+'</b></div>'});document.getElementById('breakdown').innerHTML=h;}load();</script>'''
 return shell("Overview",body)
@app.route("/members")
def members_page():
 body='''<h1>Members <span id="mYear" style="font-size:18px"></span></h1><p>Total: <b id="mTotal">0</b> members</p><input class="input" id="search" placeholder="Search name / staff no / company..." oninput="filterM()"><div style="display:flex;gap:8px;flex-wrap:wrap;margin:10px 0" id="projChips"></div><div class="card"><div id="list">Loading...</div></div><script>let ALL=[];let CUR='All';async function load(){let q=companyQuery();document.getElementById('mYear').textContent=getCompany()? '('+getCompany()+')':'(All Companies)';let r=await fetch('/api/members'+q);ALL=await r.json();document.getElementById('mTotal').textContent=ALL.length;let chips='<button class="xbtn" onclick="setProj(\\'All\\')">All</button>';['Antonia','GCB-MT','GCB-TDs','Higchem','HQ','Java House','Kanji','Pwani Oil Products','SC Johnson','TF WSL','TF-LM','TF-MT'].forEach(p=>{chips+='<button class="xbtn" onclick="setProj(\\''+p+'\\')">'+p+'</button>'});document.getElementById('projChips').innerHTML=chips;render();}function setProj(p){CUR=p;render();}function render(){let q=(document.getElementById('search').value||'').toLowerCase();let f=ALL.filter(x=>(CUR=='All'||x.project==CUR)&&(x.full_names+' '+x.staff_no+' '+x.project).toLowerCase().includes(q));let h='<table><tr><th></th><th>Staff</th><th>Name</th><th>Company</th><th>Joined</th><th>Year</th><th>Months</th><th>Share</th></tr>';f.forEach(x=>{let img=x.logo?'<img class="projlogo" src="'+x.logo+'">':'';h+='<tr><td>'+img+'</td><td>'+x.staff_no+'</td><td><b>'+x.full_names+'</b></td><td>'+x.project+'</td><td>'+x.month_joined+'</td><td>'+x.join_year+'</td><td>'+x.months+'</td><td>KES '+x.share.toLocaleString()+'</td></tr>'});h+='</table><p>'+f.length+' members shown - '+CUR+'</p>';document.getElementById('list').innerHTML=h;}function filterM(){render();}load();</script>'''
 return shell("Members",body)
@app.route("/shareout")
def shareout_page():
 body='''<h1>Share-Out <span id="sYear" style="font-size:18px"></span></h1><div class="dark"><div>Total to Share: <b>KES 605,759</b></div><div style="opacity:.8">KES 250,000 retained</div></div><div class="card"><div id="share">Loading...</div></div><script>async function load(){let q=companyQuery();document.getElementById('sYear').textContent=getCompany()? '('+getCompany()+')':'(All Companies)';let r=await fetch('/api/shareout'+q);let d=await r.json();document.getElementById('share').innerHTML='Members: '+d.total_members+'<br>Total Months: '+d.total_months+'<br>Per Month: KES '+d.per_month_rate.toFixed(2)+'<br>Company: '+(d.project||'All');}load();</script>'''
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
 body='''<h1 style="font-size:32px">Community <span style="font-size:14px;background:#1D9BF0;color:#fff;padding:4px 10px;border-radius:999px">Twitter-like</span></h1><div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"><button class="xbtn" onclick="setFeed('all')">All Posts</button><button class="xbtn" onclick="setFeed('liked')">❤️ My Likes</button><button class="xbtn" onclick="setFeed('saved')">🔖 Saved</button><input id="comSearch" class="input" style="flex:1;min-width:160px" placeholder="Search posts..." oninput="loadCom()"><select id="comProj" class="input" style="width:140px" onchange="loadCom()"><option value="">All Companies</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option></select></div><div class="card"><div style="display:flex;gap:12px"><div class="avatar" id="myAvatar">M</div><div style="flex:1"><textarea id="comMsg" class="input" style="height:80px;padding:12px;border:0;border-bottom:1px solid #2F3336;border-radius:0" placeholder="What is happening?"></textarea><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><span style="color:#71767B;font-size:13px">Posting as <b id="myName">Member</b></span><button class="btn-dark" onclick="postMsg()">Post</button></div><p id="comStatus"></p></div></div></div><div id="comFeed">Loading...</div><script>let FEED='all';document.getElementById('myName').textContent=getName();document.getElementById('myAvatar').textContent=getName().charAt(0);function setFeed(f){FEED=f;loadCom();}async function loadCom(){let r=await fetch('/api/community?email='+encodeURIComponent(getEmail())+'&feed='+FEED+'&search='+encodeURIComponent(document.getElementById('comSearch').value||'')+'&project='+encodeURIComponent(document.getElementById('comProj').value||''));let d=await r.json();let h='';(d.posts||[]).forEach(p=>{let init=p.author_name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();let com='';(p.comments||[]).forEach(cm=>{com+='<div style="display:flex;gap:8px;padding:8px 0;border-top:1px solid #2F3336"><div class="avatar" style="width:28px;height:28px;font-size:11px">'+cm.author_name.charAt(0)+'</div><div><b>'+cm.author_name+'</b> <span style="color:#71767B;font-size:12px">'+cm.created+'</span><div>'+cm.msg+'</div></div></div>'});h+='<div class="card"><div style="display:flex;gap:12px"><div class="avatar">'+init+'</div><div style="flex:1;min-width:0"><div style="display:flex;gap:8px;flex-wrap:wrap"><b>'+p.author_name+'</b><span style="color:#71767B">@'+p.author_email.split('@')[0]+' - '+p.project+' - '+p.created+'</span></div>'+(p.repost_of?'<div style="background:#16181C;border-radius:12px;padding:10px;margin:8px 0;color:#A1A1AA;font-size:13px">🔁 Reposted: '+p.repost_of+'</div>':'')+'<div style="font-size:15px;line-height:1.5;margin:6px 0">'+p.msg+'</div><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px"><button class="xbtn '+(p.liked?'liked':'')+'" onclick="act('+p.id+',\\'like\\')">❤️ '+p.likes+'</button><button class="xbtn" onclick="toggleCom('+p.id+')">💬 '+(p.comments?p.comments.length:0)+'</button><button class="xbtn" onclick="act('+p.id+',\\'repost\\')">🔁 '+p.reposts+'</button><button class="xbtn '+(p.saved?'saved':'')+'" onclick="act('+p.id+',\\'bookmark\\')">🔖 '+(p.saved?'Saved':'Save')+'</button><button class="xbtn" onclick="delPost('+p.id+')">🗑️</button></div><div id="comBox'+p.id+'" style="display:none;margin-top:10px"><input id="comIn'+p.id+'" class="input" placeholder="Write a reply..."><button class="btn-dark" style="margin-top:8px" onclick="sendComment('+p.id+')">Reply</button></div><div id="comList'+p.id+'">'+com+'</div></div></div></div>'});document.getElementById('comFeed').innerHTML=h||'No posts yet - be the first to post!';}function toggleCom(id){let el=document.getElementById('comBox'+id);el.style.display=el.style.display=='none'?'block':'none';}async function act(id,action){await fetch('/api/community/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id})});loadCom();}async function sendComment(id){let m=document.getElementById('comIn'+id).value;if(!m)return;await fetch('/api/community/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id,msg:m})});loadCom();}async function postMsg(){let m=document.getElementById('comMsg').value;if(!m)return alert('Write something');await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:getName(),email:getEmail(),msg:m,project:localStorage.getItem('fig_project')||'HQ'})});document.getElementById('comMsg').value='';document.getElementById('comStatus').textContent='Posted!';loadCom();}async function delPost(id){if(!confirm('Delete this post?'))return;await fetch('/api/community/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id,email:getEmail()})});loadCom();}loadCom();</script>'''
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
 project=request.args.get("project","")
 c=get_db()
 rows=c.execute("SELECT project, month_joined FROM users").fetchall()
 c.close()
 if project:
  rows=[r for r in rows if norm_project(r["project"])==project]
 from collections import Counter
 bc=dict(Counter([norm_project(r["project"]) for r in rows]))
 logos={k:project_logo(k) for k in bc}
 return jsonify({"total_members":len(rows),"projects_total":len(bc),"projects_breakdown":bc,"project":project,"projects":PROJECTS,"logos":logos})
@app.route("/api/members")
def api_members():
 project=request.args.get("project","")
 out,tc,tm,rate=calc_shares()
 if project:
  out=[x for x in out if x["project"]==project]
 return jsonify(out)
@app.route("/api/shareout")
def api_shareout():
 project=request.args.get("project","")
 out,tc,tm,rate=calc_shares()
 if project:
  out=[x for x in out if x["project"]==project]
 tm=sum(x["months"] for x in out)
 return jsonify({"total_members":len(out),"total_months":tm,"total_contribution":sum(x["contribution"] for x in out),"per_month_rate":rate,"distributable":DISTRIBUTABLE,"project":project,"members":out})
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
