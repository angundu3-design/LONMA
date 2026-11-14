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
SEED_TXT='''202731|Pwani Oil Products|2025|Angela Nyaguthii Gathege|Philip Gathege|Elizabeth Wanjiru||||||
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
Specioza Matitsa|Java House|01/11/2026|Specioza Matitsa|NA|NA|NA|NA|NA|NA|NA||
202607 Mary ngotah|GCB-MT|1st Dec 2019|Mary ngotah|||6514355  Gideon|5647988  Johnson|5029251  Shantel|821770  Ryan|||
202602Hillary nzive|GCB-MT|19th Dec|Hillary nzive kasiva|mumo|Christabel||33080053|5523041707|552304792|giana sage||
202609 Joan Atieno Odhiambo|GCB-MT|11th Nov|Joan Atieno Odhiambo||Roseline|9007625||710552151||||
202612 purity ndunda|GCB-MT|2025 November|purity ndunda|ndunda|Jemima|20451178|56342190||3820546|||
280322|GCB-MT|01/08/2021|Nelson karani|Patrick|Martha|20035038|35833677|||||
292916|GCB-MT|1st Aug 2026|Grace muthoni chege|Benson|Elizabeth||31744265|3820546 Jayden||||
202606 peter omondi|GCB-MT|11th Nov 2022|peter omondi|maurice|Teressa|||||||
202613|GCB-MT|1st jan 2026|Joan wambui|none|hannah njeri|6431600||tracy njeri 3954756|Israel Githuku 4681696|||
292962|GCB-MT|1st September 2026|Stephen Mwose|Antony|Magdaline|4916541|37679067|Brielle Mbithe|-|||
280265|GCB-MT|1st July 2026|Caroline Maina|Maina|Jane|8812236||||||
202610|GCB-MT|15th November 2025|Mercy Wambui Njer|none|none|21785795 Grace Lucy||shalomlynnnjeri  2739159||||
292964|GCB-MT|1st june 2026|Mary Mbinya|Musyoka|Ruth|9224221|34123070|0212336591 Jayden||||
280315|GCB-MT|1st Aug 2026|Dorcas Mukenyi|Mwanzia|Joyce||22228902|Geoffrey||||
202926|GCB-MT|1st Jan ,2026|Stephen Mwalimu|Mwalimu|Damaris|21 459928|N/A|||||
202604|GCB-MT|14th September 2020|Dennis Mbindyo Mwamuli|Alfred Mwamuli|Catherine Monica|||||||
280321 Geoffery Matata Mbeva|GCB-MT|19th August 2026|Geoffrey Matata Mbeva||Rosina Beth Mbeva 73696420||32512477 Faith Mwende|Nathan Musyoki Matata 0262718439|Ethan Mbeva Matata 0262718432|Carlos Mwendwa Matata 0265294261||
202611|GCB-MT|1st Dec 2025|Robert Muthui Matheka|Julius Matheka|Jedidah Matheka|||||||
202601|GCB-MT|1st Feb 2011|Evelyne Mpinda Kinyua|||Sophia Mbiriga 8351177||Rordrique Kimathi - 481336|Imani Raylen - 5167251|||
280322|GCB-MT|15th Aug 2026|Nelson karani||Martha adisa-20035038||N/A|Teddy khainza|N/A|N/A||
202615|GCB-MT|4th April 2019|Emiliana mwanaidi||Diana mwandisha, 8464065||marvin cassiano 22582763|Gybies 0572301813|Asaph 5170301|||
202628|HQ|2015|JANEDRIX AKINYI SADAKA|N/A|JOYCE SAKAKA||N/A|JAMES SADAKSA|JOYBLESSING|||
CELESTINE ATIENO SADAKA|HQ|2015|CELESTINE ATIENO SADAKA|N/A|JOYCE SAKAKA||N/A|LINCOL|IAN|ANDREY||
280314|HQ|AUGUST 1ST 2026|LAZARUS OKECHI|NICODEMUS OGOTI|MARY AJIAMBO||PURITY KABATI|AZARIA  AJIAMBO||||
PATRIC TITO|HQ|2020|PATRIC TITO|TITO NZONGA|FELISTERS TITO||FRIDAH KARIMI|TIFFANY TITO|BARAKA TITO|||
292930|HQ|AUGUST 1ST 2026|EDDY  NYANGORI|JOHN  NYANGORI|HELLENE ACHIENG||N/A|||||
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
 # SYNC TO 1ST DATA ONLY - remove old simplified 10009 etc members not in this list
 seed_staffs=set([clean(r[0]) for r in SEED_DATA if clean(r[0])])
 seed_names=set([clean(r[3]).lower() for r in SEED_DATA if clean(r[3])])
 for row in c.execute("SELECT id, staff_no, full_names, email FROM users").fetchall():
  if row["email"]==ADMIN_EMAIL:
   continue
  if (row["staff_no"] or "") not in seed_staffs and (row["full_names"] or "").lower() not in seed_names:
   c.execute("DELETE FROM users WHERE id=?",(row["id"],))
 c.commit()
 c.close()
 print(f"v124 seeded {added}")
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
COMPANY_BAR='''
<div style="background:#fff;border-bottom:1px solid #E5E7EB;padding:10px 14px;display:flex;gap:10px;align-items:center;flex-wrap:wrap">
<label style="font-weight:700;font-size:13px;color:#0F2A44">Filter Company:</label>
<select id="companyFilter" onchange="onCompanyChange()" style="height:42px;border:1px solid #D1D5DB;border-radius:999px;padding:0 10px;min-width:180px;font-size:14px;background:#fff">
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
<button onclick="clearCompany()" style="height:42px;background:#6B7280;color:#fff;border:0;border-radius:999px;padding:0 14px;font-weight:600">Clear / All</button>
<span id="companyLabel" style="font-weight:700;color:#0F2A44;font-size:13px"></span>
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
 return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600;700&display=swap" rel="stylesheet"><script>if(!localStorage.getItem('fig_user')&&location.pathname!='/login'&&location.pathname!='/register'){location.href='/login'}</script><style>*{box-sizing:border-box}body{font-family:Inter,sans-serif;background:#F8F9FA;margin:0;padding-bottom:80px;color:#111827;overflow-x:hidden}body.dark{background:#000;color:#E7E9EA}body.dark .card,body.dark .top,body.dark .toplinks,body.dark #slideDrawer,body.dark .nav{background:#000!important;color:#E7E9EA!important;border-color:#2F3336!important}body.dark .input{background:#000!important;color:#fff!important;border-color:#2F3336!important}.card{background:#fff;border:1px solid #E5E7EB;border-radius:20px;padding:20px;margin-bottom:14px}.input{width:100%;height:48px;border:1px solid #D1D5DB;border-radius:999px;padding:0 14px;background:#fff}.btn-dark{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#0F2A44;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px;border:0}.btn-gold{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:#C9A86A;color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px;border:0}.top{height:64px;background:#fff;display:flex;align-items:center;gap:12px;padding:0 14px;position:sticky;top:0;z-index:20;border-bottom:1px solid #E5E7EB}.logo{width:52px;height:52px;border-radius:14px;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:18px}.toplinks{background:#fff;border-bottom:1px solid #E5E7EB;padding:10px 14px;display:flex;gap:24px;overflow-x:auto;white-space:nowrap;position:sticky;top:64px;z-index:15;flex-wrap:wrap}.toplinks a{color:#111827;text-decoration:none;font-size:15px;font-weight:600}.page{max-width:1080px;margin:auto;padding:18px 14px 180px}.dark{background:#0F2A44;color:#fff;border-radius:20px;padding:22px;margin-bottom:14px}.gold{color:#C9A86A;letter-spacing:2px;font-size:12px;font-weight:700}h1,h2{font-family:Fraunces,Georgia,serif}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid #F3F4F6;text-align:left}.nav{position:fixed;left:10px;right:10px;bottom:8px;height:60px;background:#fff;border:1px solid #E5E7EB;border-radius:24px;display:flex;z-index:30;box-shadow:0 4px 20px rgba(0,0,0,.08)}.nav a{flex:1;color:#6B7280;text-decoration:none;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:600}.xbtn{border:0;background:#F3F4F6;border-radius:999px;padding:8px 12px;font-size:13px;cursor:pointer}.xbtn.liked{background:#FEE2E2;color:#DC2626}.xbtn.saved{background:#FEF3C7;color:#92400E}.avatar{width:40px;height:40px;border-radius:50%;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700;font-size:14px;flex-shrink:0}.projlogo{width:32px;height:32px;border-radius:8px;object-fit:cover;background:#F3F4F6}
#slideOverlay{position:fixed;top:0;left:0;right:0;bottom:0;background:rgba(0,0,0,0.4);z-index:100;opacity:0;pointer-events:none;transition:opacity .3s}
#slideOverlay.open{opacity:1;pointer-events:auto}
#slideDrawer{position:fixed;top:0;left:0;bottom:0;width:320px;max-width:88vw;background:#fff;z-index:101;transform:translateX(-105%);transition:transform .32s ease;overflow-y:auto;border-right:1px solid #E5E7EB;box-shadow:20px 0 40px rgba(0,0,0,.2);padding:14px 14px 30px}
#slideDrawer.open{transform:translateX(0)}
.drawer-row{display:flex;align-items:center;gap:14px;padding:14px 8px;text-decoration:none;color:#111827;border-radius:14px}
.drawer-row:active{background:#F3F4F6}
.drawer-label{font-size:19px;font-weight:600;flex:1}
.drawer-arrow{color:#9CA3AF;font-size:18px}
.section-title{color:#6B7280;letter-spacing:2px;font-size:13px;font-weight:700;margin:22px 8px 10px}
.appear-row{display:flex;gap:8px;padding:0 8px}
.appear-btn{flex:1;height:46px;border:1px solid #E5E7EB;background:#fff;border-radius:14px;font-weight:600;font-size:16px;cursor:pointer;color:#111827}
.appear-btn.active{background:#0F2A44;color:#fff;border-color:#0F2A44}
.drawer-footer{margin:26px 8px 0;color:#6B7280;font-size:14px;line-height:1.6}
</style></head><body>
<div id="slideOverlay" onclick="closeDrawer()"></div>
<aside id="slideDrawer">
<div style="display:flex;justify-content:space-between;align-items:center;padding:4px 8px"><div class="avatar" style="width:48px;height:48px;font-size:18px">W</div><button onclick="closeDrawer()" style="background:none;border:0;font-size:22px;cursor:pointer">✕</button></div>
<div style="padding:10px 8px 0"><div style="font-size:21px;font-weight:800">Welfare</div></div>
<a class="drawer-row" href="/register" onclick="closeDrawer()"><span class="drawer-label">Register Member</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/shareout" onclick="closeDrawer()"><span class="drawer-label">Share-Out</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/breakdown2" onclick="closeDrawer()"><span class="drawer-label">History</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/terms" onclick="closeDrawer()"><span class="drawer-label">Terms &amp; Policies</span><span class="drawer-arrow">›</span></a>
<div class="section-title">APPEARANCE</div>
<div class="appear-row"><button class="appear-btn active" id="btnLight" onclick="setTheme('light')">Light</button><button class="appear-btn" id="btnDark" onclick="setTheme('dark')">Dark</button><button class="appear-btn" id="btnSystem" onclick="setTheme('system')">System</button></div>
<div class="section-title">NOTIFICATIONS &amp; SETTINGS</div>
<a class="drawer-row" href="/community" onclick="closeDrawer()"><span class="drawer-label">Notifications</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/admin" onclick="closeDrawer()"><span class="drawer-label">Admin / Settings</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/terms" onclick="closeDrawer()"><span class="drawer-label">Help Centre</span><span class="drawer-arrow">›</span></a>
<a class="drawer-row" href="/download/excel" onclick="closeDrawer()"><span class="drawer-label">Download Excel</span><span class="drawer-arrow">›</span></a>
<div class="section-title">ACCOUNT</div>
<a class="drawer-row" href="/login" onclick="closeDrawer()"><span class="drawer-label">Login as Admin</span><span class="drawer-arrow">›</span></a>
<div class="drawer-footer">F.I.G BRANDS Welfare · v100<br>marlonkikuyu@gmail.com · +254 707 780 807</div>
</aside>
<div class="top"><button onclick="openDrawer()" style="background:none;border:0;color:#111827;font-size:24px;cursor:pointer;padding:6px">☰</button><div class="logo">FIG</div><div><b style="font-size:17px;letter-spacing:.5px">F.I.G BRANDS</b><div style="color:#6B7280;letter-spacing:2px;font-size:11px">WELFARE SYSTEM</div></div><div style="margin-left:auto;display:flex;gap:8px;align-items:center"><span style="width:38px;height:38px;border-radius:50%;background:#F3F4F6;display:flex;align-items:center;justify-content:center">◐</span><span style="width:38px;height:38px;border-radius:50%;background:#F3F4F6;display:flex;align-items:center;justify-content:center">○</span><button onclick="openDrawer()" style="background:none;border:0;cursor:pointer;padding:0"><span style="width:38px;height:38px;border-radius:50%;background:#0F2A44;color:#fff;display:flex;align-items:center;justify-content:center;font-size:13px;font-weight:700">W</span></button></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/community">Community</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/terms">Terms &amp; Policies</a><a href="/admin">Admin</a></div><div class="page">'''+full+'''</div><nav class="nav"><a href="/">Home</a><a href="/members">Members</a><a href="/community">Community</a><a href="/shareout">Share-Out</a><a href="/terms">Terms</a><a href="/register">Add</a></nav>
<script>
function openDrawer(){document.getElementById('slideDrawer').classList.add('open');document.getElementById('slideOverlay').classList.add('open');document.body.style.overflow='hidden';}
function closeDrawer(){document.getElementById('slideDrawer').classList.remove('open');document.getElementById('slideOverlay').classList.remove('open');document.body.style.overflow='';}
function applyTheme(){var t=localStorage.getItem('lonma_theme')||'light';var dark=(t=='dark')||(t=='system'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.body.classList.toggle('dark',dark);['btnLight','btnDark','btnSystem'].forEach(function(id){var el=document.getElementById(id);if(el)el.classList.remove('active');});var active=t=='dark'?'btnDark':t=='system'?'btnSystem':'btnLight';var a=document.getElementById(active);if(a)a.classList.add('active');}
function setTheme(t){localStorage.setItem('lonma_theme',t);applyTheme();}
applyTheme();
var _startX=null;document.addEventListener('touchstart',function(e){_startX=e.touches[0].clientX;},{passive:true});document.addEventListener('touchend',function(e){if(_startX===null)return;var dx=e.changedTouches[0].clientX-_startX;if(_startX<30&&dx>60)openDrawer();if(dx<-60)closeDrawer();_startX=null;},{passive:true});
</script></body></html>''')
@app.route("/")
def index():
 body='''<div style="color:#C9A86A;letter-spacing:2px;font-size:12px;font-weight:700">F.I.G BRANDS · WELFARE</div><h1 style="font-size:42px;margin:6px 0">Overview</h1><p style="color:#4B5563;line-height:1.6;font-size:17px">Balance brought forward, less KES 250,000 retained — shared fairly, per month of contributions.</p><div class="card"><div style="color:#6B7280;letter-spacing:2px;font-size:13px;font-weight:700">TOTAL MEMBERS</div><div style="font-family:Fraunces,Georgia,serif;font-size:52px;font-weight:700;color:#0F2A44" id="total">0</div></div><div class="card"><div style="color:#6B7280;letter-spacing:2px;font-size:13px;font-weight:700">PROJECTS</div><div style="font-family:Fraunces,Georgia,serif;font-size:52px;font-weight:700;color:#0F2A44" id="projCount">0</div></div><div class="dark"><div style="color:#C9A86A;letter-spacing:2px;font-size:13px;font-weight:700">BALANCE BROUGHT FORWARD</div><div style="font-family:Fraunces,Georgia,serif;font-size:38px;font-weight:700;margin:8px 0">KES 855,759</div><div style="opacity:.9;font-size:17px">KES 605,759 to share · KES 250,000 retained</div></div><div class="card"><div class="gold">DISTRIBUTION</div><h2 style="font-size:30px;margin:8px 0">Project Distribution <span id="bdYear" style="font-size:16px"></span></h2><div id="breakdown"></div></div><script>async function load(){let q=companyQuery();let r=await fetch('/api/stats'+q);let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('bdYear').textContent=getCompany()? '('+getCompany()+')':'(All Companies)';let h='';Object.keys(d.projects_breakdown).sort((a,b)=>d.projects_breakdown[b]-d.projects_breakdown[a]).forEach(k=>{let lg=d.logos[k]||'';let img=lg?'<img class="projlogo" src="'+lg+'">':'';h+='<div style="display:flex;justify-content:space-between;align-items:center;padding:14px 0;border-bottom:1px solid #eee"><span style="display:flex;gap:10px;align-items:center;font-size:18px;font-weight:600">'+img+k+'</span><b style="font-size:18px">'+d.projects_breakdown[k]+'</b></div>'});document.getElementById('breakdown').innerHTML=h;}load();</script>'''
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
 body='''<h1 style="font-size:32px">Community <span style="font-size:14px;background:#0F2A44;color:#fff;padding:4px 10px;border-radius:999px">Twitter-like</span></h1><div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:12px"><button class="xbtn" onclick="setFeed('all')">All Posts</button><button class="xbtn" onclick="setFeed('liked')">❤️ My Likes</button><button class="xbtn" onclick="setFeed('saved')">🔖 Saved</button><input id="comSearch" class="input" style="flex:1;min-width:160px" placeholder="Search posts..." oninput="loadCom()"><select id="comProj" class="input" style="width:140px" onchange="loadCom()"><option value="">All Companies</option><option>Antonia</option><option>GCB-MT</option><option>GCB-TDs</option><option>Higchem</option><option>HQ</option><option>Java House</option><option>Kanji</option><option>Pwani Oil Products</option><option>SC Johnson</option><option>TF WSL</option><option>TF-LM</option><option>TF-MT</option></select></div><div class="card"><div style="display:flex;gap:12px"><div class="avatar" id="myAvatar">M</div><div style="flex:1"><textarea id="comMsg" class="input" style="height:80px;padding:12px;border:0;border-bottom:1px solid #eee;border-radius:0" placeholder="What is happening?"></textarea><div style="display:flex;justify-content:space-between;align-items:center;margin-top:10px"><span style="color:#6B7280;font-size:13px">Posting as <b id="myName">Member</b></span><button class="btn-dark" onclick="postMsg()">Post</button></div><p id="comStatus"></p></div></div></div><div id="comFeed">Loading...</div><script>let FEED='all';document.getElementById('myName').textContent=getName();document.getElementById('myAvatar').textContent=getName().charAt(0);function setFeed(f){FEED=f;loadCom();}async function loadCom(){let r=await fetch('/api/community?email='+encodeURIComponent(getEmail())+'&feed='+FEED+'&search='+encodeURIComponent(document.getElementById('comSearch').value||'')+'&project='+encodeURIComponent(document.getElementById('comProj').value||''));let d=await r.json();let h='';(d.posts||[]).forEach(p=>{let init=p.author_name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();let com='';(p.comments||[]).forEach(cm=>{com+='<div style="display:flex;gap:8px;padding:8px 0;border-top:1px solid #f3f4f6"><div class="avatar" style="width:28px;height:28px;font-size:11px">'+cm.author_name.charAt(0)+'</div><div><b>'+cm.author_name+'</b> <span style="color:#888;font-size:12px">'+cm.created+'</span><div>'+cm.msg+'</div></div></div>'});h+='<div class="card"><div style="display:flex;gap:12px"><div class="avatar">'+init+'</div><div style="flex:1;min-width:0"><div style="display:flex;gap:8px;flex-wrap:wrap"><b>'+p.author_name+'</b><span style="color:#6B7280">@'+p.author_email.split('@')[0]+' - '+p.project+' - '+p.created+'</span></div>'+(p.repost_of?'<div style="background:#F9FAFB;border-radius:12px;padding:10px;margin:8px 0;color:#4B5563;font-size:13px">🔁 Reposted: '+p.repost_of+'</div>':'')+'<div style="font-size:15px;line-height:1.5;margin:6px 0">'+p.msg+'</div><div style="display:flex;gap:8px;flex-wrap:wrap;margin-top:12px"><button class="xbtn '+(p.liked?'liked':'')+'" onclick="act('+p.id+',\\'like\\')">❤️ '+p.likes+'</button><button class="xbtn" onclick="toggleCom('+p.id+')">💬 '+(p.comments?p.comments.length:0)+'</button><button class="xbtn" onclick="act('+p.id+',\\'repost\\')">🔁 '+p.reposts+'</button><button class="xbtn '+(p.saved?'saved':'')+'" onclick="act('+p.id+',\\'bookmark\\')">🔖 '+(p.saved?'Saved':'Save')+'</button><button class="xbtn" onclick="delPost('+p.id+')">🗑️</button></div><div id="comBox'+p.id+'" style="display:none;margin-top:10px"><input id="comIn'+p.id+'" class="input" placeholder="Write a reply..."><button class="btn-dark" style="margin-top:8px" onclick="sendComment('+p.id+')">Reply</button></div><div id="comList'+p.id+'">'+com+'</div></div></div></div>'});document.getElementById('comFeed').innerHTML=h||'No posts yet - be the first to post!';}function toggleCom(id){let el=document.getElementById('comBox'+id);el.style.display=el.style.display=='none'?'block':'none';}async function act(id,action){await fetch('/api/community/'+action,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id})});loadCom();}async function sendComment(id){let m=document.getElementById('comIn'+id).value;if(!m)return;await fetch('/api/community/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:getEmail(),name:getName(),post_id:id,msg:m})});loadCom();}async function postMsg(){let m=document.getElementById('comMsg').value;if(!m)return alert('Write something');await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:getName(),email:getEmail(),msg:m,project:localStorage.getItem('fig_project')||'HQ'})});document.getElementById('comMsg').value='';document.getElementById('comStatus').textContent='Posted!';loadCom();}async function delPost(id){if(!confirm('Delete this post?'))return;await fetch('/api/community/delete',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({post_id:id,email:getEmail()})});loadCom();}loadCom();</script>'''
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
