from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
PMAP = {"Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","Pwani Oil Products":"Pwani Oil Products","Java":"Java House","Java House":"Java House","SJ":"SJ Johnson","SJ Johnson":"SJ Johnson","SCJohnson":"SJ Johnson","Scjohnsons":"SJ Johnson","scjohnsons":"SJ Johnson","SC Johnson":"SJ Johnson","TF WSL":"TF WSL","TF":"TF WSL","TF-WS":"TF WSL","TF WS":"TF WSL","TF-MT":"TF-MT","TF-LM":"TF-LM","TF MT":"TF-MT","TF LM":"TF-LM","GCB-MT":"GCB-MT","GCB-Ws":"GCB-Ws","GCB":"GCB-MT","Higchem":"Higchem","HIGCHEM MARKETING LIMITED":"Higchem","Hichem":"Higchem","Antonia":"Antonia","Antonia Stogdale":"Antonia","Antonio":"Antonia","Kanji":"Kanji","HQ":"HQ"}
def norm_project(p):
    p=(p or "").strip()
    return PMAP.get(p, PMAP.get(p.title(), p or "Pwani Oil Products"))
PROJECTS = ["Pwani Oil Products","Java House","SJ Johnson","Kanji","HQ","Antonia","TF-MT","TF-LM","GCB-MT","GCB-Ws","Higchem","TF WSL"]
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
BF = 855759
RESERVE = 200000
DISTRIBUTABLE = BF - RESERVE
MONTHLY_RATE = 300
PERIOD_START = (2025, 12)
PERIOD_END = (2026, 9)
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
10052|Pwani||Stephen Wesonga Ouma|Musa Bin Said|||9765327||||||||
10325|Pwani||Maradi Ruth Mercylyne|||22400966|23601476|42107914|111041990|||
202731|Pwani|2025|Angela Nyaguthii Gathege|Philip Gathege|Elizabeth Wanjiru||||||||
202863|Pwani|2025|Peter Olonde|6600561|0745115734||41572317|67272316||||
202656|Pwani|2025|Patrick Sifuna Wanjala|||4396984||31939216|151468||||
202679|Pwani|2016|Jack Omondi Juma|||||9927L79|3300789|26057L7|9999788|
202680|Pwani|2016|Marlon Ang'undu Kikuyu||||1951498||6879175||||
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
280349|Higchem|Sep.2026|Wicklife Okemwa Nyangaresi|1593749|10468950||308049405|4713214||||
Sherine Atieno|Antonia|2025|Sherine Atieno Otieno||23333405||||||||
280225|Antonia Stogdale|2026|Stepheny Keziah Wambui Mwangi|10452983|10166506||34439485|1463604|2498854||||
202989|SCJohnson|Feb 2026|Bonface Nzuki|13592548|20001605||||||||
202774|SCJohnson|Aug 2024|Oscar Kipkoech Ruto|8715105|25972243||643055126|604533||||
90117|SCJohnson|Aug 2022|Hilda Esende Lugangi|22499361|22546698||22499361|330400075|370207832|371929483||
Lena Cherono|SCJohnson|Oct 2026|Lena Cherono||6013139|6013139||||||||
202788|SCJohnson|Aug 2023|Afline Anyango Onyango|||25083427||538317|538318|538342|880993|8908622
202786|SCJohnson|Aug 2022|Judith Oweya Lukale|6308832|1232343|||7281845|8355678|||
202784|SCJohnson|Jul 2025|Farida Olesi||21667279|||4164247||||
Phesial Jaramogi Ooyi|SCJohnson|Aug 2022|Phesial Jaramogi Ooyi|2631938|21217207||38946763|7493054|3486480|||
201743|SCJohnson|Apr 2026|Zachary Joel Moriasi||31295653||||||||
202976|SCJohnson|Feb 2026|Winfred Mwende John||8966707||28782624||261287576|||
202782|SCJohnson|Dec 2025|Victoria Wangechi Mugwe|5988617|11032615||||1512406016|||
202775|SCJohnson|Feb 2023|Milka Wawuda Mwangombe||58719||||||||
202780|SCJohnson|2022|Mokua Frankline|23751234|24351022||37120961|||||
202765|SCJohnson|Aug 2025|Hannah Warukira Mwangi|3582703||||||||0071503182|||
202977|SCJohnson|Jan 2026|Emily Mueni Mutua|||3545974||212327285|212303274|||
202764|SCJohnson|Aug 2025|Agnes Wangu Mwangi|9263345|20409743|||201192||||
202769|SCJohnson|Aug 2025|Joshua Mwangi Iguna|10380353|31107389||511795193|||||
202761|SCJohnson|Apr 2025|Hannah Wanjiku||||2384950||||
202777|SCJohnson|Sep 2022|Caroline Kathomi Njebiu|||||||||
202757|SCJohnson|2024|Fedinand Kafwa|||||||||
202772|SCJohnson|Feb 2025|Maureen Njeri|||||||||
280267|SCJohnson|Jul 2026|Patrick Kabiu Waweru|||||||||
202766|SCJohnson|Apr 2025|Veronica Mukolwe||21000046|||265075567||||
202789|SCJohnson|Aug 2022|Celestine Auma Ouko|25837011|8212095||21166739|6658291||||'''
SEED_DATA = [tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
PWANI_ROSTER = "00001|Patrick Kilungu Tito;10009|Esther Wambui Kimani;10025|Nostar Nyanchama Osiemo;10043|Doreen Talu Mwanga;10047|Winnie Jemutai Chepkwony;10048|Millianna Anyango Sadaka;10050|Samuel Kikweo Nthenya;10072|Mary Wangari Mwimenyi;10073|Linet Awino Wayumba;10077|Celestine Achieng;10093|Diana Nanjala Wafula;10094|Njugu Rispa Wanyaga;10097|Jecinta Gathoni Mwangi;10100|Owen Muthee Waithaka;10101|George Mbithi Maingi;10106|Gwen Moraa Kegege;10108|Polly Wangui Nyaguthii;10111|Sally Kanaiza Barasa;10112|Evans Mwaita Ngoma;10320|Gabriel Michael Mutisya;10322|Samuel Njeru Njiru;10324|Getrude Juma Juma;10331|Eunice Nafula Makona;10352|Clare Vuyanzi Osiako;10353|Everlyne Mukoya Stephen;10355|Peter Kibet Chepsigor;10356|Sheillah Jepchumba;10357|Betty Akinyi Namamba;10358|Alex Esamai;10360|Caren Nanjala Chonge;10362|Fredrick Nick Osotsi;10363|Hellen Achieng Onyango;10379|Harriet Kaveza Olome;10382|Hannah Muthoni Ngaruiya;10386|Rachel Wanjiku Ndungu;10387|Lydia Achieng Asaka;10388|Karen Auma Asaka;10390|George Ibuba Nganga;10397|Jairus Oduor Makona;10399|Merceline Adhiambo Osewe;10400|Linet Achieng Oduor;10402|Metrine Cherop Chumo;10403|Benta Achieng Muruka;10407|Mercy Njeri Wanjiru;10409|Tabitha Koki Musembi;10410|Dorcas Wangeshi Mwaurah;10415|Henry Omondi Oganga;10416|Peter Wamalwa Odhiambo;10417|Ingavi Julius Seseda;10419|Cornelius Muteti Kioko;10420|Caroline Nyambura Kagera;10431|Joackim Bachwa Bachwa;11010|Linda Kanana;11018|Agatha Wanjiku Mbugua;11019|Rhoda Akinyi Odhiambo;11020|Elizabeth Matinde;11022|Lavenda Anyango Otieno;11024|Susan Akoth Owiti;11028|Brendah Mijidie Kiduyu;11113|Bernice Katende Muthoka;11114|Dorine Akinyi;11115|Leila Salma Odiwour;11118|Francisca Mutanu Ndunga;11119|Fridah Kathure Gatobu;12169|Boniface Museve Ashiona;12345|Celestine Atieno Sadaka;12346|Janedrix Akinyi Sadaka;16322|Sharon Wafula Ajwangi;17100|Dorice Awino Anyango;17102|Clarice Achieng Omaya;17103|Teresia Mueni Syombua;30101|Kevin Karanja Njoroge;30102|Eugene Daudi Aura;30103|Wamuyu Irene Wairimu;30104|Lennox Amani Daniel;30105|Victoria Mbeke Ngave;30106|Hillary Omondi Alindi;30108|Felix Kiarie Ndungu;30110|Claire Wambui Kariuki;30111|Hellen Awuor Odari;30112|Zaweria Warungari Wairegi;30113|Ann Wambui Muchemi;30115|Esther Wangari Karanja;30116|Emily Waithera Njenga;30117|Judith Chepngeno;30119|Michael Ondieki Kerosi;30120|Gloria Mukhwana Lusenaka;30121|Judith Lozenjah Ominde;30126|Edwin Ondieki Kiyaka;30129|Gladys Kinuthia;30131|Onganga Gwako Edmond;30132|Jane Kanini Mbirichi;30133|Diana Kathure;38103|Evelyne Mpinda Kinyua;38104|Hillary Nzive Kasiva;38105|Mariamu Ali Juma;38106|Dennis Mbindyo Mwamuli;38107|Stanely Muigai Njoroge;38108|Josyline Nkatha Karambu;38109|Caroline Gaceri Kimathi;38111|Peter Omondi Onyango;38112|Mary Ngotah;38116|Teresa Mwihaki Gichuki;38117|Carol Wanjiku Njuguna;38118|Mercy Jepkorir Yatich;38120|Dennis Muchangi Wanja;38122|Tabitha Wambui Mwangi;38123|Rabin Nyasinga Winston;38124|Cynthia Obaga Lwangu;38125|Pennina Awuor Olango;38129|Ruth Waitherero Kihugu;38130|Ferdinand Kafwa;38132|Lilian Wambui Muthigani;38133|Emily Mueni Mutua;38134|Victoria Waeni Mutua;38135|Mourin Wangui Karomo;38139|Abel Nyandega Rasugu;38140|Samwel Erick Odhiambo;38141|Sarah Nyambura Kibe;38142|Amina Godana;38143|Kashulina Milphat;40103|Phylis Khayenga Barasa;40105|Caroline Nkatha Mbaya;40106|Mercy Mwikali Muthio;40108|Jackline Wambui Mwendia;40109|Joyce Wambui Wanjiru;40110|Linda Atieno Odhiambo;40112|Samuel Sidhani Menza;40113|Peter Murithi Mugambi;40115|Lucy Muhanji;40118|Josiah Manua Misiani;40119|Peter Ondieki Onyoni;40120|Susan Wambui Ndungu;40125|Mueni Kisingu;40126|Jonathan Mutunga Kilonzo"
PERIODS = [
 {"label":"Period 1: Oct 2024 - Dec 2025","months":["Oct 24","Nov 24","Dec 24","Jan 25","Feb 25","Mar 25","Apr 25","May 25","Jun 25","Jul 25","Aug 25","Sep 25","Oct 25","Nov 25","Dec 25"],"totals":[98100,95400,95400,101700,108000,108000,110700,110700,104100,101700,99900,96600,86700,87000],"counts":[327,318,318,339,360,360,369,369,347,339,333,322,289,290,0],"grand":1404000,"expenditures":494625,"projects":[("Pwani",[24600,23700,22500,24900,21600,21900,21600,21300,21900,21600,21300,21300,21300,21000,0]),("Java",[8700,8400,8700,9300,7800,7800,8700,8100,9600,9300,9600,8700,9600,9300,0]),("Johnson",[10500,10800,10200,9300,9000,9000,10200,9900,10200,9900,10200,10200,10200,9600,0]),("Kaysalt",[9600,9600,9300,9600,9000,8400,8700,8700,0,0,0,0,0,0,0]),("Kanji",[900]*15),("HQ",[900,0,1800,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,0]),("GCB-MT",[5400,4800,5100,4800,4800,4800,5100,5700,4800,4800,4800,4800,5100,5100,0]),("TF-WS",[3300,3300,3000,6300,6900,6900,5700,5100,5100,5700,5400,4800,4800,4800,0]),("TF-LM",[11700,12300,12300,11700,13200,13200,12600,12600,12300,12300,12000,12000,12600,12300,0]),("TF-MT",[19200,18000,17700,19800,17700,18000,18600,18000,18900,18000,18600,18300,18600,20100,0]),("Kenafric",[0,0,0,0,11700,12000,12300,12000,12300,12000,12600,12000,0,0,0]),("GCB-TDs",[3300,3600,3900,3900,4200,3900,5100,4800,3900,3600,3300,2400,2400,2700,0]),("LAB",[0,0,0,0,0,0,0,2400,3000,2400,0,0,0,0,0])]},
 {"label":"Period 2: Dec 2025 - Oct 2026","months":["Dec 25","Jan 26","Feb 26","Mar 26","Apr 26","May 26","Jun 26","Jul 26","Aug 26","Sep 26","Oct 26"],"totals":[86700,87300,89700,89700,90000,90300,92400,92400,94800,89700,87900],"counts":[289,291,299,299,300,301,308,308,316,299,293],"grand":990900,"expenditures":385141,"projects":[("Pwani",[21000,20400,21300,21000,21300,21600,21300,21600,20700,15300,14700]),("Java",[9000,9600,9900,9900,9600,9300,9600,9300,9900,9900,10200]),("Johnson",[10500,9600,10200,9900,9900,9300,8400,8700,8700,8100,8100]),("Kanji",[900]*11),("HQ",[1200,1200,1200,1200,1200,1200,1200,1200,1500,1500,1500]),("GCB-MT",[4500,4500,4800,4800,4800,4500,6000,5100,6000,5700,6000]),("TF-WS",[4800,5100,4800,4800,4800,4500,4500,4200,3900,3900,3900]),("TF-LM",[12300,12300,11700,11700,12600,9300,9000,9900,10200,12000,11400]),("TF-MT",[19800,20700,21900,22200,21300,21300,21900,21900,22200,21900,21000]),("GCB-TDs",[2700,3000,3000,3300,3600,3600,3600,3600,4800,5100,4800]),("Highchem",[0,0,0,0,0,4800,5100,5100,5400,4800,4800]),("Antonia",[0,0,0,0,0,0,900,900,600,600,600])]},
]
BENEFICIARIES2 = [("Period 1","Mary Ngota","GCB","Dad-Death","Nov 2024",30000),("Period 1","Mariamu","GCB","Dad-Death","Dec 2024",30000),("Period 1","Claire Osiako","Kaysalt","Dad-Death","2 Dec 2024",30000),("Period 1","Rachael Ndungu","Pwani","Mum-Death","10 Dec 2024",30000),("Period 1","Teresih Kariuki","TF","Dad-Death","17 Dec 2024",30000),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","4 Dec 2024",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Jan 2025",9500),("Period 1","Hannah Ngaruiya","Pwani","Loss of earning","2 Feb 2025",9500),("Period 1","(Unnamed)","SJ","Daughter-Death","",30000),("Period 1","Jecinta Nduta Karanja","TF","Loss of earning","",9000),("Period 1","Winnie","TF B","Dad-Death","",30000),("Period 1","Maureen Kiare","Kenafric","Dad-Death","July",30000),("Period 1","Eugene Otieno","TF","Dad-Death","July",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",22000),("Period 1","Mercy Mwikali","TF","Guardian","Aug 2025",30000),("Period 1","Ann Wambui Muchemi","Java","Loss of earning","Aug 2025",11000),("Period 1","Annah Nthamba Musyoki","Java","Dad-Death","Sep 2025",30000),("Period 1","Eunice Wairimu Wanjiku","SJ","Dad-Death","Oct 2025",30000),("Period 1","JJJJ","","Loss of earning","",11500),("Period 1","Nostar","TF","Loss of earning","",19000),("Period 2","Rose Lumonya Saidi","POPL","Death-Father","Dec 2025",40000),("Period 2","Nostar","TF","Loss of earning","Dec 2025",19000),("Period 2","Susan Ndungu","TF","Death-Father","26 Jan 2026",40000),("Period 2","Irene Wairimu","Java","Death-Guardian","May 2026",40000),("Period 2","Mercy Mwende","GCB","Loss of earning","May 2026",11075),("Period 2","Damarais Muyoka","TF","Death-Father","May 2026",40000),("Period 2","Ruth Amollo Nyangun","","Death-Father","Jun 2026",40000),("Period 2","Sheila Okomo","TF","Loss of earning","May",9000),("Period 2","Sheila Okomo","TF","Loss of earning","June",9000),("Period 2","(Unnamed)","TF","Death-Father","",40000),("Period 2","Vivian Moraa","Java","Loss of earning","",11000),("Period 2","Hannah Wanjiku","TF","Death-Father","17 Aug",40000)]
FARES2 = [("Period 1","Peter Ikegu","0704886421",1000),("Period 1","George Ibuba","0113964865",1000),("Period 1","Kevin Kipkurui","0704284388",1000),("Period 1","Valary Chepkoech","0713053696",1500),("Period 1","Mercy Njeri","0713881793",1500),("Period 1","Margaret Wangari","0720331094",1000),("Period 1","Mary Wangare","0796805933",1000),("Period 1","Daniel Mayaka","0722620252",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","(Unnamed)","",1000),("Period 1","Rose","",3000),("Period 1","Jecinta Apondi","",1000),("Period 1","Mercy Onyango","",1000),("Period 1","Preskila Ondiek","",1000),("Period 1","Jane Wangari","",1500),("Period 1","Caroline Wachira","",1500),("Period 1","Joy","",1500),("Period 1","Berbciter","",1500),("Period 1","Irene Wamuyu","0719606834",1000),("Period 1","Ann Mulema","0729218786",1000),("Period 1","Gloria Luksenaka","0796426074",1000),("Period 1","Mary Thika","0719572174",1000),("Period 1","Joshua Iguna","0792529926",1000),("Period 1","Jackline Kamau","0724562145",1000),("Latest","Eunice Makona","0714910135",1200),("Latest","Hellen Onyango","0724570228",1200),("Latest","Caren Chonge","0710427468",900),("Latest","Antony Mwendia","",1500),("Latest","Gladys Nyaga","",1500),("Latest","Marlon K. Ang'undu","",1200),("Latest","Gladys Wambaire Kinuthia","",1200),("Latest","Evapertual Wambui","",1200),("Latest","Catherine Ogutu","",1700),("Latest","Ebby Lomoi","",1700),("Latest","Jackline Ayiga","",1700),("Latest","Esther Marenya","",1600),("Latest","George Odhiambo","",1400),("Latest","Kiplimo","",4200),("Latest","Maureen Njeri Kamunyu","",1500),("Latest","Eunice Wairimu","",2000),("Latest","Victoria Wangechi Mugwe","",2000),("Latest","(Unnamed)","",500)]
MONTHLY_INDIVIDUAL = [("Oct 2024",327,98100),("Nov 2024",318,95400),("Dec 2024",318,95400),("Jan 2025",339,101700)]
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
    assert len(vals) == 17
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
    c.execute("DELETE FROM beneficiaries2")
    for per,n,p,r2,d,a in BENEFICIARIES2: c.execute("INSERT INTO beneficiaries2 (period,name,project,reason,date_str,amount) VALUES (?,?,?,?,?,?)", (per,n,p,r2,d,a))
    c.execute("DELETE FROM fares2")
    for per,n,ph,a in FARES2: c.execute("INSERT INTO fares2 (period,name,phone,amount) VALUES (?,?,?,?)", (per,n,ph,a))
    if not c.execute("SELECT id FROM users WHERE email=?", (ADMIN_EMAIL,)).fetchone():
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)", ("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    if not c.execute("SELECT id FROM notifications").fetchone():
        c.execute("INSERT INTO notifications (title,msg,created,target,is_read) VALUES (?,?,?,?,?)", ("Welcome to F.I.G BRANDS Welfare","Your welfare system is active.","Now","/",0))
        c.execute("INSERT INTO notifications (title,msg,created,target,is_read) VALUES (?,?,?,?,?)", ("Share-Out: BF less 200,000","BF 855,759 less 200,000 = 655,759 shared per month of contributions.","Now","/shareout",0))
    else:
        c.execute("UPDATE notifications SET target='/' WHERE title LIKE 'Welcome%' AND (target IS NULL OR target='')")
        c.execute("UPDATE notifications SET target='/shareout' WHERE title LIKE 'Share-Out%' AND (target IS NULL OR target='')")
        c.execute("UPDATE notifications SET target='/members' WHERE title LIKE 'New Member%' AND (target IS NULL OR target='')")
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
    for item in PWANI_ROSTER.split(";"):
        if "|" not in item: continue
        staff, names = item.split("|",1)
        if add_user(c, staff, names, "Pwani Oil Products", ""): added += 1
    c.commit(); c.close(); print(f"Seeded {added} new members")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); return r
@app.route("/favicon.ico")
def favicon():
    svg = '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="14" fill="#0A2540"/><text x="32" y="42" font-family="Arial" font-size="24" font-weight="800" fill="white" text-anchor="middle">FIG</text></svg>'
    return svg, 200, {"Content-Type": "image/svg+xml"}
def shell(title, body):
    return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>''' + title + ''' - F.I.G BRANDS</title><style>body{font-family:system-ui,sans-serif;background:#F2F4F7;color:#101828;margin:0;padding-bottom:80px}.top{height:56px;background:#0A2540;color:#fff;display:flex;align-items:center;gap:10px;padding:0 12px;position:sticky;top:0}.logo{background:#fff;color:#0A2540;border-radius:10px;padding:6px 8px;font-weight:800}.page{max-width:1080px;margin:auto;padding:16px 12px}.card{background:#fff;border:1px solid #E6EBF2;border-radius:16px;padding:16px;margin-bottom:12px}.input{width:100%;height:42px;border:1px solid #D9E1EC;border-radius:10px;padding:0 12px;box-sizing:border-box}.btn{width:100%;height:46px;background:#0A2540;color:#fff;border:0;border-radius:10px;font-weight:700;cursor:pointer}.btn2{display:inline-block;background:#067647;color:#fff;padding:10px 14px;border-radius:10px;text-decoration:none;font-weight:600}.grid{display:grid;grid-template-columns:1fr 1fr;gap:12px}.kpi{background:#fff;border:1px solid #E6EBF2;border-radius:16px;padding:16px}.hero{background:linear-gradient(135deg,#0A2540,#0E6B4A);color:#fff;border-radius:18px;padding:20px}.nav{position:fixed;left:12px;right:12px;bottom:12px;height:60px;background:#0A2540;border-radius:18px;display:flex}.nav a{flex:1;color:#fff;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:700}.row{display:flex;justify-content:space-between;padding:12px 4px;border-bottom:1px solid #F1F5F9}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:10px;border-bottom:1px solid #EEF2F7;text-align:left}.num{text-align:right;white-space:nowrap}.pill{display:inline-block;background:#EDF2F9;color:#0A2540;padding:3px 9px;border-radius:999px;font-size:11px;font-weight:700}.popup{position:fixed;inset:0;background:rgba(0,0,0,.45);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:#fff;width:100%;max-width:520px;border-radius:18px 18px 0 0;padding:16px;max-height:84vh;overflow:auto}</style></head><body><div class="top"><div class="logo">FIG</div><div><b>F.I.G BRANDS</b><div style="font-size:10px;letter-spacing:2px">WELFARE SYSTEM v71</div></div><div style="margin-left:auto;display:flex;gap:8px"><button onclick="openBell()" style="background:rgba(255,255,255,.15);border:0;color:#fff;border-radius:999px;width:36px;height:36px;cursor:pointer">🔔<span id="bellBadge"></span></button><button onclick="openSupport()" style="background:rgba(255,255,255,.15);border:0;color:#fff;border-radius:999px;width:36px;height:36px;cursor:pointer">🎧</button></div></div><div style="background:#fff;padding:10px 12px;display:flex;gap:12px;flex-wrap:wrap"><a href="/">Overview</a><a href="/members">Members</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/admin">Admin</a></div><div class="page">''' + body + '''</div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Notifications</b><button onclick="closeBell()">X</button></div><div id="notifList"></div><button class="btn" onclick="markRead()" style="margin-top:10px">Mark all as read</button></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Contact Support</b><button onclick="closeSupport()">X</button></div><p><a href="https://wa.me/254707780807" target="_blank">WhatsApp 0707 780 807</a> &middot; <a href="mailto:info@figbrands.co.ke">info@figbrands.co.ke</a></p><input class="input" id="supName" placeholder="Your name"><textarea id="supMsg" class="input" style="height:90px;margin-top:10px" placeholder="Message"></textarea><button class="btn" onclick="sendSupport()" style="margin-top:10px">Send Message</button><p id="supStatus"></p></div></div><nav class="nav"><a href="/">🏠 Home</a><a href="/members">👥 Members</a><a href="/shareout">KES Share-Out</a><a href="/breakdown2">📈 History</a><a href="/register">+ Add</a></nav><script>function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{h+='<div onclick="tapNotif('+n.id+',\\''+esc(n.target||'/')+'\\')" style="padding:12px 0;border-bottom:1px solid #eee;cursor:pointer"><b>'+esc(n.title)+'</b><div>'+esc(n.msg)+'</div><div style="font-size:11px;color:#888">'+esc(n.created)+'</div></div>'});document.getElementById('notifList').innerHTML=h||'No notifications';}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}async function tapNotif(id,t){await fetch('/api/notifications/'+id+'/read',{method:'POST'});location.href=t}async function markRead(){await fetch('/api/notifications/read',{method:'POST'});closeBell()}function openSupport(){document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}</script></body></html>''')
@app.route("/")
def home():
    body = '''<h1>Overview</h1><p>BF less KES 200,000, shared per month of contributions.</p><div class="grid"><div class="kpi"><div>Total Members</div><h2 id="total">0</h2></div><div class="kpi"><div>Projects</div><h2 id="projCount">0</h2><div>Projects with members</div></div></div><div class="hero" style="margin-top:12px"><div>BALANCE BROUGHT FORWARD</div><h1>KES 855,759</h1><div>KES 655,759 to share &middot; KES 200,000 retained</div></div><div class="grid" style="margin-top:12px"><div class="kpi"><div>Amount to Share</div><h2 style="color:#067647">KES 655,759</h2></div><div class="kpi"><div>Retained</div><h2 style="color:#C81E1E">KES 200,000</h2></div><div class="kpi"><div>Value of One Month</div><h2 id="oneMonth">-</h2><div id="oneMonthNote"></div></div></div><div class="card" style="margin-top:12px"><h2>Project Distribution</h2><p>Only projects with members</p><div id="breakdown"></div><div class="row"><b id="projTotalLabel">Total</b><b id="projTotal">0</b></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('projTotal').textContent=d.total_members;document.getElementById('projTotalLabel').textContent='Total Members ('+d.projects_total+' projects)';let h='';Object.keys(d.projects_breakdown).sort().forEach(k=>{h+='<div class="row"><b>'+k+'</b><span>'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h;let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='655,759 / '+s.total_months+' months';}load();</script>'''
    return shell("Overview", body)
@app.route("/breakdown")
def breakdown_page(): return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
    h = "<h1>Full History</h1><p>Monthly contributions, beneficiaries and fares.</p>"
    h += '<div class="grid"><div class="kpi"><div>Period 1 Oct 2024 - Dec 2025</div><h2>KES 1,404,000</h2><div>Expenditures 494,625</div></div><div class="kpi"><div>Period 2 Dec 2025 - Oct 2026</div><h2>KES 990,900</h2><div>Expenditures 385,141</div></div><div class="kpi"><div>Beneficiaries</div><h2>KES 800,075</h2></div><div class="kpi"><div>Grand Total</div><h2>KES 1,240,900</h2></div></div>'
    for m,c,t in MONTHLY_INDIVIDUAL: h += f'<div class="row"><span><b>{m}</b> &middot; {c} members</span><b>KES {t:,}</b></div>'
    for p in PERIODS:
        h += f"<div class='card'><h3>{p['label']}</h3><div>Expenditures KES {p['expenditures']:,} &middot; Total KES {p['grand']:,}</div><div style='overflow:auto'><table><tr><th>Project</th>" + "".join([f"<th class='num'>{mo}</th>" for mo in p['months']]) + "<th class='num'>Total</th></tr>"
        for name, vals in p['projects']: h += f"<tr><td><b>{name}</b></td>" + "".join([f"<td class='num'>{v:,}</td>" for v in vals]) + f"<td class='num'><b>{sum(vals):,}</b></td></tr>"
        h += "<tr><td><b>Total</b></td>" + "".join([f"<td class='num'>{v:,} ({p['counts'][i]})</td>" for i,v in enumerate(p['totals'])]) + f"<td class='num'><b>{p['grand']:,}</b></td></tr></table></div></div>"
    h += "<div class='card'><h3>Beneficiaries KES 800,075</h3>"
    for per,n,pr,r2,d,a in BENEFICIARIES2: h += f"<div class='row'><span><b>{n}</b> &middot; {per} &middot; {pr} &middot; {r2} &middot; {d}</span><b>KES {a:,}</b></div>"
    h += "</div><div class='card'><h3>Fares</h3>"
    for per,n,ph,a in FARES2: h += f"<div class='row'><span><b>{n}</b> &middot; {per} &middot; {ph}</span><b>KES {a:,}</b></div>"
    h += "</div>"
    return shell("Full History", h)
@app.route("/shareout")
def shareout_page():
    shares, total_contrib, total_months, per_month_rate = calc_shares(); total_shares = sum(x["share"] for x in shares)
    h = f"<h1>Share-Out</h1><p>BF less 200,000, per month of contributions. Dec 2025 - Sep 2026, KES 300/month.</p><div class='hero'><div>AMOUNT TO SHARE</div><h1>KES 655,759</h1><div>1 month = KES {per_month_rate:,.2f} &middot; Shares KES {total_shares:,.2f} + Retained 200,000 = BF 855,759</div></div><div class='grid' style='margin-top:12px'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{total_months}</h2></div><div class='kpi'><div>Total Contributions</div><h2>KES {total_contrib:,}</h2></div><div class='kpi'><div>Total Shares</div><h2>KES {total_shares:,.2f}</h2></div></div>"
    h += '''<div class="card"><div style="display:flex;justify-content:space-between"><h3>Member Share-Out Schedule</h3><a class="btn2" href="/download/shareout">Download Excel</a></div><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="margin:12px 0"><div style="overflow:auto"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share Payable</th></tr><tbody id="shareBody">'''
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
    for c in ws[5]: c.font = Font(bold=True, color="FFFFFF"); c.fill = PatternFill("solid", fgColor="0A2540"); c.alignment = Alignment(horizontal="center", vertical="center")
    for i, x in enumerate(shares, 1): ws.append([i, x["staff_no"], x["full_names"], x["project"], x["month_joined"], x["months"], x["contribution"], round(x["share"], 2)])
    ws.append([]); ws.append(["","","","","","TOTAL", total_contrib, round(sum(x["share"] for x in shares), 2)]); ws.append(["","","","","","RETAINED IN ACCOUNT","", RESERVE]); ws.append(["","","","","","BALANCE BROUGHT FORWARD","", round(sum(x["share"] for x in shares), 2) + RESERVE])
    ws.freeze_panes = "A6"; ws.auto_filter.ref = ws.dimensions
    for col, w in zip("ABCDEFGH", [6, 14, 30, 22, 14, 18, 20, 20]): ws.column_dimensions[col].width = w
    out = io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
@app.route("/members")
def members_page():
    body = '''<h1>Members</h1><p id="memberCountLabel"></p><div class="card"><div style="display:flex;gap:10px"><input class="input" id="q" placeholder="Search by name, staff, project" oninput="fil()" style="flex:2"><select class="input" id="projFilter" onchange="fil()" style="flex:1"><option value="All Projects">All Projects</option></select></div><div id="list" style="margin-top:12px"></div><a class="btn2" href="/download/excel">Download Excel</a></div><script>let all=[];async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('memberCountLabel').textContent=d.total_members+' members - filter shows count per project';let sel=document.getElementById('projFilter');sel.innerHTML='<option value="All Projects">All Projects ('+d.total_members+')</option>';(d.projects||[]).forEach(p=>{let o=document.createElement('option');o.value=p;o.textContent=p+' ('+(d.projects_breakdown[p]||0)+')';sel.appendChild(o)});let r2=await fetch('/api/members');let dd=await r2.json();all=dd.members;render(all)}function row(l,v){return '<div class="row"><span>'+l+'</span><b>'+(v||'-')+'</b></div>'}function render(l){let h='';l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<div class="card"><div style="display:flex;justify-content:space-between"><div><b>'+m.full_names+'</b><div>'+m.email+'</div></div><span class="pill">'+m.project+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID',m.guardian_id)+row('Spouse ID',m.spouse_id)+row('Kids Birth Certs',kids)+'</div>'});document.getElementById('list').innerHTML=h||'No members found'}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(m=>(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(qq)&&(pf=='All Projects'||m.project==pf)))}load();</script>'''
    return shell("Members", body)
@app.route("/register")
def register_page():
    opts = "".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    body = '''<h1>Register Member</h1><div class="card"><div style="display:flex;gap:16px;align-items:center"><div onclick="document.getElementById('photoInput').click()" style="width:100px;height:100px;border-radius:999px;border:2px dashed #CBD5E1;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer"><img id="photoPreview" style="display:none;width:100%;height:100%;object-fit:cover"><span id="photoPlaceholder">Add Photo</span></div><div><b>Member Photo</b><div>Max 2MB, JPG or PNG</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div></div>'''
    for sec, fields in [("1. Staff Information", [("staff_no","Staff Number","text"),("project","Project","select"),("month_joined","Date Joined","text"),("full_names","Full Names","text"),("email","Email","text"),("password","Password","password")]), ("2. Parents IDs", [("father_id","Father ID","text"),("mother_id","Mother ID","text")]), ("3. Guardian and Spouse", [("guardian_id","Guardian ID No.","text"),("spouse_id","Spouse ID No.","text")]), ("4. Kids Birth Certificates", [("kid1","Kid 1","text"),("kid2","Kid 2","text"),("kid3","Kid 3","text"),("kid4","Kid 4","text"),("kid5","Kid 5","text")])]:
        body += f"<h3>{sec}</h3><div class='grid'>"
        for fid, label, typ in fields:
            if fid == "project": body += f"<div><label>{label}</label><select class='input' id='project'>{opts}</select></div>"
            else: body += f"<div><label>{label}</label><input class='input' id='{fid}' type='{typ}'></div>"
        body += "</div>"
    body += '''<button class="btn" onclick="doReg()" id="btn" style="margin-top:16px">Create Member</button><p id="msg"></p></div><script>let photoBase64="";function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>2*1024*1024){alert('File too large');return}let r=new FileReader();r.onload=function(ev){photoBase64=ev.target.result;document.getElementById('photoPreview').src=photoBase64;document.getElementById('photoPreview').style.display='block';document.getElementById('photoPlaceholder').style.display='none'};r.readAsDataURL(f)}async function doReg(){let d={};["staff_no","project","full_names","email","password","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>{d[k]=document.getElementById(k).value});d.photo=photoBase64;if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';return}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;if(r.ok)setTimeout(()=>location.href='/members',800)}</script>'''
    return shell("Register", body)
@app.route("/admin")
def admin_login_page():
    body = '''<h1>Admin Login</h1><div class="card"><label>Email</label><input class="input" id="email" value="admin@lonma.com"><div style="margin-top:12px"><label>Password</label><input class="input" id="pass" type="password" value="admin123"></div><button class="btn" onclick="login()" style="margin-top:16px">Login</button><p id="msg"></p></div><script>async function login(){let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('pass').value})});let j=await r.json();if(r.ok)location.href='/admin/dashboard?key='+j.key;else document.getElementById('msg').textContent=j.error}</script>'''
    return shell("Admin", body)
@app.route("/admin/dashboard")
def admin_dashboard():
    if request.args.get("key") != ADMIN_KEY: return redirect("/admin")
    body = '''<h1>Admin Dashboard</h1><div class="card"><button class="btn" onclick="repair()" style="background:#067647">Repair Projects + Re-seed Missing Members</button><p id="repairMsg"></p></div><div class="card"><h3>Members</h3><a class="btn2" href="/download/excel">Download Excel</a><div id="tbl" style="margin-top:12px"></div></div><div class="card"><h3>Support Messages</h3><div id="supList">Loading...</div></div><script>async function repair(){let r=await fetch('/api/repair?key=''' + ADMIN_KEY + ''',{method:'POST'});let j=await r.json();document.getElementById('repairMsg').textContent=JSON.stringify(j);load()}async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{h+='<div class="row"><span><b>'+m.staff_no+'</b> '+m.full_names+'<div>'+m.email+'</div></span><span>'+m.project+' <button onclick="del('+m.id+')">Delete</button></span></div>'});document.getElementById('tbl').innerHTML=h;let r2=await fetch('/api/support_list');let d2=await r2.json();document.getElementById('supList').innerHTML=d2.messages.map(m=>'<div><b>'+(m.name||'Guest')+'</b> '+m.msg+'</div>').join('')||'No messages'}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key=''' + ADMIN_KEY + ''',{method:'DELETE'});let j=await r.json();if(!r.ok)alert(j.error);load()}load();</script>'''
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
        for cell in ws[1]: cell.font = Font(bold=True, color="FFFFFF"); cell.fill = PatternFill("solid", fgColor="0A2540"); cell.alignment = Alignment(horizontal="center")
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
        raw = {r["project"]: r["n"] for r in rows}
        merged = {}
        for r in rows:
            k = norm_project(r["project"]); merged[k] = merged.get(k, 0) + r["n"]
        return jsonify({"total_members": total, "projects_total": len(merged), "projects": sorted(merged.keys()), "projects_breakdown": merged, "raw_breakdown": raw})
    finally: c.close()
@app.route("/api/repair", methods=["POST"])
def api_repair():
    if request.args.get("key") != ADMIN_KEY: return jsonify({"error": "Admin key required"}), 401
    init_db()
    c = get_db()
    try:
        total = c.execute("SELECT COUNT(*) FROM users WHERE email != ?", (ADMIN_EMAIL,)).fetchone()[0]
        rows = c.execute("SELECT project, COUNT(*) AS n FROM users WHERE email != ? GROUP BY project", (ADMIN_EMAIL,)).fetchall()
        return jsonify({"message": "Repaired", "total_members": total, "projects": {r["project"]: r["n"] for r in rows}})
    finally: c.close()
@app.route("/api/breakdown")
def api_breakdown():
    c = get_db()
    try:
        brows = c.execute("SELECT * FROM beneficiaries2 ORDER BY id").fetchall(); frows = c.execute("SELECT * FROM fares2 ORDER BY id").fetchall()
        return jsonify({"periods": PERIODS, "monthly_individual": MONTHLY_INDIVIDUAL, "beneficiaries": [dict(r) for r in brows], "beneficiaries_total": 800075, "fares": [dict(r) for r in frows], "grand_total": 1240900, "bf": BF, "transfer_total": 673270})
    finally: c.close()
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
        assert len(vals) == 17
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
