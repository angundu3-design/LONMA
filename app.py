from flask import Flask,request,jsonify,render_template_string,redirect,send_file
import sqlite3,os,secrets,io,re
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__);DB="lonma.db"
PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PWANI_LOGO="https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png"
JAVA_LOGO="https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_l.jpg"
SCJ_LOGO="https://bhp-plus.pl/usr/s.c.-johnson-logo.png"
PMAP={"Antonio":"Antonia","ANTONIA":"Antonia","Antonia":"Antonia","GCB-MT":"GCB-MT","GCB MT":"GCB-MT","GCB":"GCB-MT","GCB-Ws":"GCB-TDs","GCB Ws":"GCB-TDs","GCB TDS":"GCB-TDs","GCB-TDs":"GCB-TDs","GCB-TDS":"GCB-TDs","Higchem":"Higchem","HIGHCHEM":"Higchem","HIGCHEM MARKETING LIMITED":"Higchem","Hichem":"Higchem","Highchem":"Higchem","HQ":"HQ","Kanji":"Kanji","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","Java House":"Java House","JAVA":"Java House","Java":"Java House","Pwani Oil Products":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","pwani":"Pwani Oil Products","Pwani Oil Products Ltd.":"Pwani Oil Products","SC Johnson":"SC Johnson","SJ Johnson":"SC Johnson","JOHNSON":"SC Johnson","Johnson":"SC Johnson","SJ":"SC Johnson","SCJohnson":"SC Johnson","Scjohnsons":"SC Johnson","scjohnsons":"SC Johnson","TF WSL":"TF WSL","TF WS":"TF WSL","TF-WS":"TF WSL","TF":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
def norm_project(p):
 p=(p or "").strip()
 if p in PMAP: return PMAP[p]
 up=" ".join(p.upper().split())
 if up in PMAP: return PMAP[up]
 return PMAP.get(p.title(),p or "Pwani Oil Products")
ADMIN_KEY=os.environ.get("ADMIN_KEY","lonma_api_key_12345").strip();ADMIN_EMAIL=os.environ.get("ADMIN_EMAIL","marlonkikuyu@gmail.com").strip().lower();ADMIN_PASS=os.environ.get("ADMIN_PASS","admin123")
BF=int(os.environ.get("BF","855759"));RESERVE=int(os.environ.get("RESERVE","250000"));DISTRIBUTABLE=BF-RESERVE;MONTHLY_RATE=300;PERIOD_START=(2025,12);PERIOD_END=(2026,9)
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
280472|Pwani Oil Products|01/09/2026|Samuel Kikweo Nthenya|Kikweo|Nthenya|N/A|42804535|5986912||||
202619|GCB-TDs|1ST SEP 2024|DENIS MUCHANGI WANJA|N/A|N/A|3657222|33845884|||||
202617|GCB-TDs|1ST NOV 2023|CELESTINE ACHIENG|N/A|N/A|21686696|37131073|3402966|3550299||
202622|GCB-TDs|24TH NOV 2025|ALEX MUKUNZA ODERA|1789894|3962126|N/A|34025189|392203835|1442216536|1442613443||
202623|GCB-TDs|20TH JULY 2024|ESTHER AWUOR AGUTU|7948959|11295135|N/A||501915259||||
202964|GCB-TDs|1ST FEB 2026|PERIS WAITHERA GIKURU|9912441||||161304366|161502936|||
202620|GCB-TDs|17TH MAR 2025|SHARROW IMAMI|4224728|25048563||||||
280319|GCB-TDs|10TH OCT 2026|VIVIAN ATIENO OWUONDA|10024935|20483394||||||
202942|GCB-TDs|2026 JAN|PAUL KHAEMBA WAFULA|1103349|4732318|1103349|||||
280313|GCB-TDs|3RD AUG 2026|STEPHANIE WANJIRU|9280225|12712053|N/A||0371905680||||
202618|GCB-TDs|1ST JULY 2023|JOACHIM BACHWA BACHWA|13606151|23557862||||||'''
PERIODS=[{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200 | Kaysalt 72,900 | Kanji 12,600 | HQ 15,900 | GCB-MT 69,900 | TF-WS 71,100 | TF-LM 173,100 | TF-MT 259,500 | Kenafric 96,900 | GCB-TDs 51,000 | LAB 7,800"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400 | Kanji 9,900 | HQ 14,100 | GCB-MT 56,700 | TF-WS 49,200 | TF-LM 122,400 | TF-MT 236,100 | GCB-TDs 41,100 | Higchem 30,000 | Antonia 3,600"}]
BENEFICIARIES2=[("Oct 2024 - Dec 2025","Mary Ngota","GCB","Dad-Death","01/11/2024",30000),("Oct 2024 - Dec 2025","Mariamu","GCB","Dad-Death","01/12/2024",30000),("Oct 2024 - Dec 2025","Claire Osiako","Kaysalt","Dad-Death","2nd Dec 2024",30000),("Oct 2024 - Dec 2025","Rachael Ndungu","Pwani","Mum-Death","10th Dec 2024",30000),("Oct 2024 - Dec 2025","Teresih Kariuki","TF","Dad-Death","17th Dec 2024",30000),("Oct 2024 - Dec 2025","Hannah Ngaruiya","Pwani","Loss of earning","4th Dec 2024",9500),("Oct 2024 - Dec 2025","Hannah Ngaruiya","Pwani","Loss of earning","2nd Jan 2025",9500),("Oct 2024 - Dec 2025","Hannah Ngaruiya","Pwani","Loss of earning","2nd Feb 2025",9500),("Oct 2024 - Dec 2025","Unnamed Member","SJ","Daughter-Death","",30000),("Oct 2024 - Dec 2025","Jecinta Nduta Karanja","TF","Loss of earning","",9000),("Oct 2024 - Dec 2025","Winnie","TF B","Dad-Death","",30000),("Oct 2024 - Dec 2025","Maureen Kiare","Kenafrica","Dad-Death","July",30000),("Oct 2024 - Dec 2025","Eugene Otieno","TF","Dad-Death","July",30000),("Oct 2024 - Dec 2025","ANN WAMBUI MUCHEMI","Java","Loss of earning","01/08/2025",22000),("Oct 2024 - Dec 2025","Mercy Mwikali","TF","Guardian","01/08/2025",30000),("Oct 2024 - Dec 2025","ANN WAMBUI MUCHEMI","Java","Loss of earning","01/08/2025",11000),("Oct 2024 - Dec 2025","ANNAH NTHAMBA MUSYOKI","Java","Dad-Death","01/09/2025",30000),("Oct 2024 - Dec 2025","EUNICE WAIRIMU WANJIKU","SJ","Dad-Death","Oct 2025",30000),("Oct 2024 - Dec 2025","JJJJ","","Loss of earning","",11500),("Oct 2024 - Dec 2025","Nostar","TF","Loss of earning","",19000),("Dec 2025 - Nov 2026","ROSE Lumonya SAIDI","POPL","Death-Father","01/12/2025",40000),("Dec 2025 - Nov 2026","Nostar","TF","Loss of earning","01/12/2025",19000),("Dec 2025 - Nov 2026","SUSAN NDUNGU","TF","Death-Father","26/01/2026",40000),("Dec 2025 - Nov 2026","Irene Wairimu","Java","Death-Guardian","01/05/2026",40000),("Dec 2025 - Nov 2026","Mercy Mwende","GCB","Loss of earning","01/05/2026",11075),("Dec 2025 - Nov 2026","Damarais Muyoka","TF","Death-Father","01/05/2026",40000),("Dec 2025 - Nov 2026","Ruth Amollo Nyangun","","Death-Father","01/06/2026",40000),("Dec 2025 - Nov 2026","Sheila Okomo","TF","Loss of earning","May",9000),("Dec 2025 - Nov 2026","Sheila Okomo","TF","Loss of earning","June",9000),("Dec 2025 - Nov 2026","Unnamed Member","TF","Death-Father","",40000),("Dec 2025 - Nov 2026","Vivian Moraa","Java","Loss of earning","",11000),("Dec 2025 - Nov 2026","Hannah Wanjiku","TF","Death-Father","17th Aug",40000),("Dec 2025 - Nov 2026","Sherine Atieno Otieno","Antonia","Mother-Death","Nov 2026",40000)]
FARES2=[("Oct 2024 - Dec 2025","Peter Ikegu","0704886421",1000),("Oct 2024 - Dec 2025","George Ibuba","0113964865",1000),("Oct 2024 - Dec 2025","Kevin Kipkurui","0704284388",1000),("Oct 2024 - Dec 2025","Valary Chepkoech","0713053696",1500),("Oct 2024 - Dec 2025","Mercy Njeri","0713881793",1500),("Oct 2024 - Dec 2025","Margaret Wangari","0720331094",1000),("Oct 2024 - Dec 2025","Mary Wangare","0796805933",1000),("Oct 2024 - Dec 2025","Daniel Mayaka","0722620252",1000),("Oct 2024 - Dec 2025","Rose","",3000),("Oct 2024 - Dec 2025","Jecinta Apondi","",1000),("Oct 2024 - Dec 2025","Mercy Onyango","",1000),("Oct 2024 - Dec 2025","Preskila Ondiek","",1000),("Oct 2024 - Dec 2025","Jane Wangari","",1500),("Oct 2024 - Dec 2025","Caroline Wachira","",1500),("Oct 2024 - Dec 2025","Joy","",1500),("Oct 2024 - Dec 2025","Berbciter","",1500),("Oct 2024 - Dec 2025","IRENE WAMUYU","719606834",1000),("Oct 2024 - Dec 2025","ANN MULEMA","729218786",1000),("Oct 2024 - Dec 2025","gloria luksenaka","796426074",1000),("Oct 2024 - Dec 2025","MARY THIKA","719572174",1000),("Oct 2024 - Dec 2025","JOSHUA IGUNA","792529926",1000),("Oct 2024 - Dec 2025","JACKLINE KAMAU","724562145",1000),("Dec 2025 - Nov 2026","EUNICE MAKONA","0714910135",1200),("Dec 2025 - Nov 2026","HELLEN ONYANGO","724570228",1200),("Dec 2025 - Nov 2026","CAREN CHONGE","710427468",900),("Dec 2025 - Nov 2026","ANTONY MWENDIA","",1500),("Dec 2025 - Nov 2026","GLADYS NYAGA","",1500),("Dec 2025 - Nov 2026","Marlon K. Angundu","",1200),("Dec 2025 - Nov 2026","Gladys Wambaire Kinuthia","",1200),("Dec 2025 - Nov 2026","Evapertual Wambui","",1200),("Dec 2025 - Nov 2026","Catheine Ogutu","",1700),("Dec 2025 - Nov 2026","Ebby Lomoi","",1700),("Dec 2025 - Nov 2026","Jackline Ayiga","",1700),("Dec 2025 - Nov 2026","Esther Marenya","",1600),("Dec 2025 - Nov 2026","George Odhiambo","",1400),("Dec 2025 - Nov 2026","Kiplimo","",4200),("Dec 2025 - Nov 2026","Maureen Njeri Kamunyu","",1500),("Dec 2025 - Nov 2026","Eunice Wairimu","",2000),("Dec 2025 - Nov 2026","Victoria Wangechi Mugwe","",2000),("Dec 2025 - Nov 2026","Unnamed Member","",500),("Dec 2025 - Nov 2026","Marlon K. Angundu","",600),("Dec 2025 - Nov 2026","Patrick Macharia Mugo","",600),("Dec 2025 - Nov 2026","Stepheny Keziah Wambui Mwangi","",600)]
SEED_DATA=[tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
def clean(v):
 if v is None: return ""
 s=str(v).strip()
 if s.upper() in ("NA","N/A","-","NONE","LATER","NULL","NIL"): return ""
 if "will give" in s.lower() or "will provide" in s.lower(): return ""
 return s
def make_email(n,staff):
 p=[x for x in n.lower().replace(".","").split() if x.isalpha()]
 return f"{p[0]}.{p[-1]}@figbrands.co.ke" if len(p)>=2 else f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
def parse_join(s):
 if not s: return None
 s=str(s).strip().lower();months={"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,"january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
 m=re.search(r"(\d{1,2})[/\-.](\d{1,2})[/\-.](\d{4})",s)
 if m:
  d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
  if mo>12: d,mo=mo,d
  return (y,mo)
 m=re.search(r"(jan|feb|mar|apr|may|jun|jul|aug|sep|oct|nov|dec)[a-z]*\.?\s*(\d{4})",s)
 if m: return (int(m.group(2)),months[m.group(1)[:3]])
 m=re.search(r"(\d{4})",s)
 if m: return (int(m.group(1)),1)
 return None
def months_active(j):
 sy,sm=PERIOD_START;ey,em=PERIOD_END;p=parse_join(j)
 if p and (p[0],p[1])>(sy,sm): sy,sm=p
 if (sy,sm)>(ey,em): return 0
 return (ey-sy)*12+(em-sm)+1
def calc_shares():
 c=get_db()
 try: rows=c.execute("SELECT id,staff_no,full_names,project,email,month_joined FROM users ORDER BY full_names").fetchall()
 finally: c.close()
 out=[]
 for r in rows:
  mo=months_active(r["month_joined"]);out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0})
 tm=sum(x["months"] for x in out);tc=sum(x["contribution"] for x in out);rate=DISTRIBUTABLE/tm if tm else 0
 for x in out: x["per_month"]=round(rate,2);x["share"]=round(x["months"]*rate,2)
 diff=round(DISTRIBUTABLE-sum(x["share"] for x in out),2)
 if out and diff!=0: out.sort(key=lambda x:x["share"],reverse=True);out[0]["share"]=round(out[0]["share"]+diff,2)
 out.sort(key=lambda x:x["share"],reverse=True);return out,tc,tm,rate
def get_db():
 c=sqlite3.connect(DB,timeout=10,check_same_thread=False,isolation_level=None);c.row_factory=sqlite3.Row
 try: c.execute("PRAGMA journal_mode=WAL;");c.execute("PRAGMA busy_timeout=10000;")
 except: pass
 return c
def add_user(c,staff,names,project,month,father="",mother="",guardian="",spouse="",k1="",k2="",k3="",k4="",k5="",photo=""):
 staff=clean(staff);names=clean(names);project=norm_project(project)
 if not staff or not names: return False
 if c.execute("SELECT id FROM users WHERE staff_no=?",(staff,)).fetchone(): return False
 if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(names,)).fetchone(): return False
 email=make_email(names,staff)
 if c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone(): email=f"member.{staff}@figbrands.co.ke"
 c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(staff,names,project,email,generate_password_hash(staff),"fig_"+secrets.token_hex(12),clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),photo));return True
def init_db():
 c=get_db();c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)');c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS beneficiaries2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, project TEXT, reason TEXT, date_str TEXT, amount REAL)');c.execute('CREATE TABLE IF NOT EXISTS fares2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, phone TEXT, amount REAL)')
 for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
  try: c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
  except: pass
 for col,typ in [("target","TEXT"),("is_read","INTEGER DEFAULT 0")]:
  try: c.execute(f"ALTER TABLE notifications ADD COLUMN {col} {typ}")
  except: pass
 for r in c.execute("SELECT id, project FROM users").fetchall():
  np=norm_project(r["project"])
  if np!=r["project"]: c.execute("UPDATE users SET project=? WHERE id=?",(np,r["id"]))
 admin=c.execute("SELECT id FROM users WHERE email=?",(ADMIN_EMAIL,)).fetchone()
 if not admin:
  marlon=c.execute("SELECT id FROM users WHERE staff_no=?",("202680",)).fetchone()
  if marlon: c.execute("UPDATE users SET email=?, password=?, role=?, api_key=?, is_protected=1 WHERE id=?",(ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin",ADMIN_KEY,marlon["id"]))
  else: c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)",("202680","Marlon Ang'undu Kikuyu","Pwani Oil Products",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0707780807",ADMIN_KEY,1))
 else: c.execute("UPDATE users SET role=?, api_key=?, is_protected=1, password=? WHERE email=?",("Admin",ADMIN_KEY,generate_password_hash(ADMIN_PASS),ADMIN_EMAIL))
 c.execute("DELETE FROM users WHERE email=? AND email != ?",("admin@lonma.com",ADMIN_EMAIL));added=0
 for r in SEED_DATA:
  staff,proj_raw,month,names,father,mother,guardian,spouse,k1,k2,k3,k4,k5=r;project=norm_project(proj_raw);ex=c.execute("SELECT id FROM users WHERE staff_no=?",(clean(staff),)).fetchone()
  if ex: c.execute("UPDATE users SET full_names=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE staff_no=?",(clean(names),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),clean(staff)));continue
  ex2=c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(clean(names),)).fetchone()
  if ex2: c.execute("UPDATE users SET staff_no=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE id=?",(clean(staff),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),ex2["id"]));continue
  if add_user(c,staff,names,project,month,father,mother,guardian,spouse,k1,k2,k3,k4,k5): added+=1
 c.commit();c.close();print(f"v107 seeded {added}")
init_db()
@app.after_request
def after(r):
 r.headers.add('Access-Control-Allow-Origin','*');r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY');r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS');return r
@app.route("/favicon.ico")
def favicon(): return '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="10" fill="#0F2A44"/><text x="32" y="42" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#C9A86A" text-anchor="middle">FIG</text></svg>',200,{"Content-Type":"image/svg+xml"}
def shell(title,body):
 return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600&display=swap" rel="stylesheet"><script>if(!localStorage.getItem('fig_user')&&location.pathname!='/login'&&location.pathname!='/register'){location.href='/login'}function figLogout(){['fig_user','fig_role','fig_name','fig_email'].forEach(k=>localStorage.removeItem(k));location.href='/login'}</script><style>:root{--navy:#0F2A44;--gold:#B9975B;--ink:#111827;--muted:#6B7280;--muted2:#9CA3AF;--line:#E5E7EB;--line2:#F3F4F6;--bg:#F8F9FA;--card:#FFFFFF;--red:#B42318}*{box-sizing:border-box}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);margin:0;padding-bottom:96px}h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:600;color:var(--navy);margin:0 0 10px}.top{height:60px;background:#fff;display:flex;align-items:center;gap:12px;padding:0 16px;position:sticky;top:0;z-index:20;border-bottom:1px solid var(--line)}.logo{width:40px;height:40px;background:var(--navy);color:#fff;border:0;border-radius:10px;font-family:Fraunces,Georgia,serif;font-weight:600;cursor:pointer}.top small{display:block;font-size:10px;letter-spacing:.14em;color:var(--muted);font-weight:600;text-transform:uppercase}.top b{font-size:16px;color:var(--navy)}.iconbtn{background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:38px;height:38px;cursor:pointer;position:relative;display:flex;align-items:center;justify-content:center}.avatar{width:38px;height:38px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;cursor:pointer}.bellBadge{position:absolute;top:-4px;right:-4px;background:var(--red);color:#fff;min-width:19px;height:19px;border-radius:999px;font-size:11px;display:none;align-items:center;justify-content:center;padding:0 5px;border:2px solid #fff}.bellBadge.show{display:flex}.toplinks{background:#fff;border-bottom:1px solid var(--line);padding:10px 16px;display:flex;gap:20px;flex-wrap:wrap;position:sticky;top:60px;z-index:15}.toplinks a{color:#374151;text-decoration:none;font-size:13px;font-weight:600}.page{max-width:1080px;margin:auto;padding:22px 16px}.eyebrow{font-size:11px;letter-spacing:.16em;text-transform:uppercase;color:var(--gold);font-weight:700;margin-bottom:8px}.card{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:20px;margin-bottom:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}.input{width:100%;height:48px;border:1px solid #D1D5DB;border-radius:12px;padding:0 14px;background:var(--card);color:var(--ink);font-size:14px}label{font-size:12px;font-weight:600;display:block;margin-bottom:6px}.btn{width:100%;height:48px;background:var(--navy);color:#fff;border:0;border-radius:12px;font-weight:600;cursor:pointer}.btn2{display:inline-block;background:var(--navy);color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}.btn2.gold{background:var(--gold);color:#fff}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:16px;padding:18px}.kpi div:first-child{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700}.kpi h2{font-size:32px;margin:10px 0 4px}.hero{background:linear-gradient(135deg,#0F2A44 0%,#1E3A5F 100%);color:#fff;border-radius:16px;padding:24px}.hero .lbl{font-size:11px;letter-spacing:.18em;color:#D6C39A;font-weight:700}.hero h1{color:#fff;font-size:36px;margin:12px 0 8px}.hero p{color:rgba(255,255,255,.75);margin:0}.nav{position:fixed;left:14px;right:14px;bottom:14px;height:60px;background:#fff;border:1px solid var(--line);border-radius:999px;display:flex;z-index:30;box-shadow:0 8px 24px rgba(0,0,0,.12)}.nav a{flex:1;color:#6B7280;text-decoration:none;display:flex;align-items:center;justify-content:center;font-size:11px;font-weight:600}.nav a.active{color:var(--navy)}.row{display:flex;justify-content:space-between;gap:12px;padding:12px 2px;border-bottom:1px solid var(--line2)}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid var(--line2);text-align:left}th{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}td b{color:var(--navy)}.num{text-align:right;white-space:nowrap}.pill{display:inline-flex;align-items:center;background:#EEF2FF;color:#3730A3;padding:6px 12px;border-radius:999px;font-size:11px;font-weight:700;border:1px solid #C7D2FE;max-width:100%;line-height:1.3}.pill.pwani,.pill.java,.pill.scj{background:#FEF2F2;color:#991B1B;border-color:#FECACA}.mcard{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:0;margin-bottom:16px;overflow:hidden;box-shadow:0 2px 10px rgba(15,42,68,.07)}.mhead{display:flex;gap:14px;align-items:flex-start;padding:18px 18px 14px;background:linear-gradient(180deg,#F8FAFC 0%,#fff 100%)}.mavatar{position:relative;flex-shrink:0}.mavatarCircle{width:56px;height:56px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:19px}.mavatarBadge{position:absolute;right:-4px;bottom:-4px;width:24px;height:24px;border-radius:999px;background:#fff;border:1px solid #E5E7EB;display:flex;align-items:center;justify-content:center;overflow:hidden}.mavatarBadge img{width:20px;height:20px;object-fit:cover}.minfo{flex:1;min-width:0}.mname{font-family:Fraunces,Georgia,serif;font-size:20px;font-weight:600;color:var(--navy);line-height:1.25;word-break:break-word}.memail{font-size:13px;color:var(--muted);margin-top:3px;word-break:break-all;line-height:1.4}.mchips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.mstatus{display:inline-flex;align-items:center;gap:6px;background:#ECFDF5;color:#065F46;border:1px solid #A7F3D0;padding:5px 10px;border-radius:999px;font-size:11px;font-weight:700}.mstatus i{width:7px;height:7px;border-radius:999px;background:#10B981;display:block}.mdetails{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid var(--line2)}.mdetail{padding:13px 18px;border-bottom:1px solid var(--line2)}.mdetail:nth-child(odd){border-right:1px solid var(--line2)}.mdetail span{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:4px}.mdetail b{font-size:14px;color:var(--ink);word-break:break-word;line-height:1.4}.mdetail.full{grid-column:1/-1}.popup{position:fixed;inset:0;background:rgba(17,24,39,.45);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:var(--card);color:var(--ink);width:100%;max-width:520px;border-radius:16px 16px 0 0;padding:20px;max-height:86vh;overflow:auto}.notifItem{padding:13px 0;border-bottom:1px solid var(--line2);cursor:pointer}.drawerOverlay{position:fixed;inset:0;background:rgba(17,24,39,.45);display:none;z-index:98}.drawerOverlay.show{display:block}.drawer{position:fixed;top:0;left:0;bottom:0;width:320px;max-width:86vw;background:#fff;z-index:99;transform:translateX(-105%);transition:transform .28s;overflow-y:auto;padding:0 0 20px}.drawer.show{transform:translateX(0)}.dhead{padding:20px;border-bottom:1px solid var(--line)}.dprofile{display:flex;gap:12px;align-items:center}.davatar{width:52px;height:52px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700}.dstats{display:flex;gap:10px;margin-top:14px}.dstat{flex:1;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px}.dstat b{font-size:17px;color:var(--navy)}.dstat span{font-size:11px;color:var(--muted);display:block}.dlink{color:#1F2937;text-decoration:none;display:flex;padding:13px 20px;font-size:15px;font-weight:600}.dlink:hover{background:#F9FAFB}.dlink small{margin-left:auto;color:var(--muted2)}.dsec{padding:16px 20px 6px;font-size:11px;letter-spacing:.14em;color:var(--muted);font-weight:700}.modeBtn{flex:1;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 4px;cursor:pointer;font-weight:600}.modeBtn.active{background:var(--navy);color:#fff}body.dark{--bg:#0B1220;--card:#111A2E;--ink:#F1F5F9;--muted:#94A3B8;--muted2:#64748B;--line:#1E293B;--line2:#1E293B;--navy:#FFFFFF}body.dark .top,body.dark .toplinks,body.dark .nav,body.dark .drawer{background:#0F172A}body.dark h1,body.dark h2,body.dark h3,body.dark .top b{color:#fff}body.dark .toplinks a{color:#CBD5E1}body.dark td b{color:#fff}body.dark .pill{background:#1E293B;color:#E2E8F0;border-color:#334155}body.dark .pill.pwani,body.dark .pill.java,body.dark .pill.scj{background:#450A0A;color:#FECACA;border-color:#7F1D1D}body.dark .input{background:#0B1220;border-color:#334155;color:#fff}body.dark .pop{background:#111A2E;color:#fff}body.dark .dlink{color:#E2E8F0}body.dark .mhead{background:linear-gradient(180deg,#1E293B 0%,#111A2E 100%)}body.dark .mname{color:#fff}body.dark .mstatus{background:#064E3B;color:#A7F3D0;border-color:#065F46}body.dark .iconbtn{background:#1E293B;border-color:#334155;color:#fff}@media(max-width:640px){.grid{grid-template-columns:1fr}.hero h1{font-size:30px}.mname{font-size:19px}}</style></head><body><div class="drawerOverlay" id="drawerOverlay" onclick="closeDrawer()"></div><div class="drawer" id="drawer"><div class="dhead"><div style="display:flex;justify-content:space-between"><span style="font-size:11px;letter-spacing:.16em;color:var(--muted);font-weight:700">F.I.G BRANDS · WELFARE</span><button onclick="closeDrawer()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:30px;height:30px;cursor:pointer">✕</button></div><div class="dprofile" style="margin-top:16px"><div class="davatar" id="drawerAvatar">--</div><div><div style="font-weight:700;font-size:17px" id="drawerName">My Account</div><div style="font-size:13px;color:var(--muted)" id="drawerEmail">Please login</div><span id="drawerRoleBadge" style="display:inline-block;margin-top:6px;background:#ECFDF5;color:#065F46;border:1px solid #A7F3D0;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:600">Member</span></div></div><div class="dstats adminOnly" id="drawerStats"><div class="dstat"><b id="drawerMembers">-</b><span>Members</span></div><div class="dstat"><b id="drawerProjects">-</b><span>Projects</span></div><div class="dstat"><b>KES 605,759</b><span>To Share</span></div></div></div><a href="/" class="dlink">Overview <small>›</small></a><a href="/members" class="dlink">Members <small>›</small></a><a href="/register" class="dlink adminOnly">Register Member <small>›</small></a><a href="/shareout" class="dlink adminOnly">Share-Out <small>›</small></a><a href="/breakdown2" class="dlink adminOnly">History <small>›</small></a><a href="/terms" class="dlink">Terms &amp; Policies <small>›</small></a><div class="dsec">APPEARANCE</div><div style="display:flex;gap:8px;padding:0 20px"><button class="modeBtn" id="modeLight" onclick="setMode('light')">Light</button><button class="modeBtn" id="modeDark" onclick="setMode('dark')">Dark</button><button class="modeBtn" id="modeSystem" onclick="setMode('system')">System</button></div><div class="dsec">NOTIFICATIONS &amp; SETTINGS</div><a href="#" onclick="closeDrawer();openBell();return false" class="dlink">Notifications <span id="drawerBell" style="background:#B42318;color:#fff;border-radius:999px;font-size:11px;padding:2px 8px;display:none;margin-left:auto">0</span></a><a href="/admin" class="dlink adminOnly">Admin / Settings <small>›</small></a><a href="#" onclick="closeDrawer();openSupport();return false" class="dlink">Help Centre <small>›</small></a><a href="/download/excel" class="dlink adminOnly">Download Excel <small>›</small></a><div class="dsec">ACCOUNT</div><a href="#" onclick="figLogout();return false" class="dlink" style="color:#B42318">Logout <small>›</small></a><div style="padding:16px 20px;color:var(--muted);font-size:12px">F.I.G BRANDS Welfare · v107<br>Support: +254 707 780 807</div></div><div class="top"><button class="logo" onclick="openDrawer()">FIG</button><div><b>F.I.G BRANDS</b><small>Welfare System</small></div><div style="margin-left:auto;display:flex;gap:8px;align-items:center"><button class="iconbtn" id="modeToggle" onclick="toggleMode()">◐</button><button class="iconbtn" onclick="openBell()">○<span class="bellBadge" id="bellBadge">0</span></button><div class="avatar" id="topAvatar" onclick="openDrawer()">--</div></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/register" class="adminOnly">Register</a><a href="/shareout" class="adminOnly">Share-Out</a><a href="/breakdown2" class="adminOnly">History</a><a href="/terms">Terms &amp; Policies</a><a href="/admin" class="adminOnly">Admin</a></div><div class="page">'''+body+'''</div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Notifications</b><button onclick="closeBell()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:32px;height:32px">✕</button></div><div id="notifList"></div><button class="btn" onclick="markRead()" style="margin-top:12px">Mark all as read</button></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Contact Support</b><button onclick="closeSupport()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:32px;height:32px">✕</button></div><p><a href="https://wa.me/254707780807" target="_blank">WhatsApp 0707 780 807</a> · <a href="mailto:info@figbrands.co.ke">info@figbrands.co.ke</a></p><label>Your name</label><input class="input" id="supName"><div style="margin-top:12px"><label>Message</label><textarea id="supMsg" class="input" style="height:96px;padding-top:10px"></textarea></div><button class="btn" onclick="sendSupport()" style="margin-top:14px">Send Message</button><p id="supStatus"></p></div></div><nav class="nav"><a href="/" class="active">Home</a><a href="/members">Members</a><a href="/shareout" class="adminOnly">Share-Out</a><a href="/terms">Terms</a><a href="/register" class="adminOnly">Add</a></nav><script>function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}function applyRoleUI(){var role=localStorage.getItem('fig_role')||'Member';var name=localStorage.getItem('fig_name')||'My Account';var email=localStorage.getItem('fig_email')||'';var isAdmin=(role=='Admin');document.querySelectorAll('.adminOnly').forEach(function(e){e.style.display=isAdmin?'':'none'});var dn=document.getElementById('drawerName');if(dn)dn.textContent=name;var de=document.getElementById('drawerEmail');if(de)de.textContent=(isAdmin?'Chairman · ':'Member · ')+email;var rb=document.getElementById('drawerRoleBadge');if(rb)rb.textContent=isAdmin?'Active Admin':'Member';var ini=name.split(' ').map(function(w){return w[0]}).join('').slice(0,2).toUpperCase();var av=document.getElementById('drawerAvatar');if(av)av.textContent=ini||'--';var ta=document.getElementById('topAvatar');if(ta)ta.textContent=ini||'--';if(isAdmin)loadDrawerCounts()}function applyMode(){var m=localStorage.getItem('fig_mode')||'system';var dark=(m=='dark')||(m=='system'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.body.classList.toggle('dark',dark);var t=document.getElementById('modeToggle');if(t)t.textContent=dark?'○':'◐';['Light','Dark','System'].forEach(function(k){var b=document.getElementById('mode'+k);if(b)b.classList.toggle('active',m==k.toLowerCase())})}function setMode(m){localStorage.setItem('fig_mode',m);applyMode()}function toggleMode(){setMode(document.body.classList.contains('dark')?'light':'dark')}function openDrawer(){document.getElementById('drawer').classList.add('show');document.getElementById('drawerOverlay').classList.add('show');applyRoleUI()}function closeDrawer(){document.getElementById('drawer').classList.remove('show');document.getElementById('drawerOverlay').classList.remove('show')}async function loadDrawerCounts(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('drawerMembers').textContent=d.total_members;document.getElementById('drawerProjects').textContent=d.projects_total}catch(e){}}async function updateBell(){try{let r=await fetch('/api/notifications');let d=await r.json();let b=document.getElementById('bellBadge');let db=document.getElementById('drawerBell');if(d.unread>0){b.textContent=d.unread>99?'99+':d.unread;b.classList.add('show');db.textContent=d.unread;db.style.display='inline-block'}else{b.classList.remove('show');db.style.display='none'}}catch(e){}}async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{let tgt=(n.target||'/').replace(/'/g,"");h+='<div class="notifItem" onclick="tapNotif('+n.id+',\\''+esc(tgt)+'\\')"><b>'+esc(n.title)+'</b><div style="color:var(--muted)">'+esc(n.msg)+'</div><div style="font-size:11px;color:var(--muted2)">'+esc(n.created)+' · Tap to open →</div></div>'});document.getElementById('notifList').innerHTML=h||'No notifications';updateBell()}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}async function tapNotif(id,t){await fetch('/api/notifications/'+id+'/read',{method:'POST'});location.href=t||'/'}async function markRead(){await fetch('/api/notifications/read',{method:'POST'});updateBell();closeBell()}function openSupport(){document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}applyRoleUI();applyMode();updateBell();setInterval(updateBell,30000);if(window.matchMedia)window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){if((localStorage.getItem('fig_mode')||'system')=='system')applyMode()});</script></body></html>''')
@app.route("/")
def index():
 body='''<div class="eyebrow">F.I.G Brands · Welfare</div><h1>Overview</h1><p style="color:#475569">Balance brought forward, less KES 250,000 retained — shared fairly, per month of contributions.</p><div class="grid"><div class="kpi"><div>Total Members</div><h2 id="total">0</h2></div><div class="kpi"><div>Projects</div><h2 id="projCount">0</h2></div></div><div class="hero" style="margin-top:14px"><div class="lbl">BALANCE BROUGHT FORWARD</div><h1>KES 855,759</h1><p>KES 605,759 to share · KES 250,000 retained</p></div><div class="grid" style="margin-top:14px"><div class="kpi"><div>Amount to Share</div><h2 style="color:#0F766E">KES 605,759</h2></div><div class="kpi"><div>Retained</div><h2 style="color:#B42318">KES 250,000</h2></div><div class="kpi"><div>Value of One Month</div><h2 id="oneMonth">-</h2><div id="oneMonthNote"></div></div></div><div class="card" style="margin-top:14px"><div class="eyebrow">Welfare Clauses 2026</div><h2>Death Benefit: Member 100,000 · Spouse 50,000 · Child 40,000 · Parents 40,000</h2><p style="color:#475569">Loss of Earning: 50% of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><a class="btn2" href="/terms">Read Full Terms</a></div><div class="card"><div class="eyebrow">Distribution</div><h2>Project Distribution</h2><div id="breakdown"></div><div class="row"><b id="projTotalLabel">Total</b><b id="projTotal">0</b></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('projTotal').textContent=d.total_members;document.getElementById('projTotalLabel').textContent='Total Members ('+d.projects_total+' projects)';let h='';Object.keys(d.projects_breakdown).sort().forEach(k=>{h+='<div class="row"><b>'+k+'</b><span>'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h;let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='605,759 / '+s.total_months+' months';}load();</script>'''
 return shell("Overview",body)
@app.route("/terms")
def terms_page():
 body='''<div class="eyebrow">Welfare Clauses · 2026</div><h1>Terms &amp; Policies</h1><div class="card"><h2>Death Benefits</h2><table><tr><th>Beneficiary</th><th>Benefit</th></tr><tr><td><b>Member</b></td><td><b>KES 100,000</b></td></tr><tr><td><b>Spouse</b></td><td><b>KES 50,000</b></td></tr><tr><td><b>Child</b></td><td><b>KES 40,000</b></td></tr><tr><td><b>Parents</b></td><td><b>KES 40,000</b></td></tr></table><div class="row"><span>Spouse</span><b>Must be registered</b></div><div class="row"><span>Child</span><b>Birth certificate required</b></div><div class="row"><span>Parents</span><b>Birth certificate + parent ID required</b></div><div class="row"><span>No biological parents</span><b>May nominate one guardian</b></div></div><div class="card"><h2>Loss of Earning</h2><p>After 10 days unable to work due to injury at work: 50% of basic pay, max KES 20,000, paid end of month.</p></div><div class="card"><h2>Contribution: KES 300 Monthly</h2><p>Deducted from monthly pay.</p></div><div class="card"><h2>Management</h2><p>Committee elected by all members. Every project must have at least one member on board.</p></div><div class="card"><h2>Disbursement</h2><div class="row"><span>Death</span><b>Within 2 days on death notification</b></div><div class="row"><span>Incapacitation</span><b>End of month</b></div></div><div class="card"><h2>Year-End: Min Balance KES 250,000</h2><p>Above that shared only among current active members, per contribution share. FIG Year-End 30 Nov. Audited accounts in FACES group by 20 Dec.</p></div><div class="card"><h2>Accountable Leadership</h2><div class="row"><span><b>Marlon K. Ang&apos;undu</b><div style="color:#6B7280">Chairman · FIG</div></span><b>+254 707 780 807<br><span style="font-weight:400">marlonkikuyu@gmail.com</span></b></div><div class="row"><span><b>Mary Ngotah</b><div style="color:#6B7280">GCB</div></span><b>0719 203 286</b></div><div class="row"><span><b>Celestine Ouko</b><div style="color:#6B7280">SC Johnsons</div></span><b>0725 543 224</b></div><div class="row"><span><b>Irene Wamuyu</b><div style="color:#6B7280">Nairobi Java</div></span><b>0719 606 834</b></div><div class="row"><span><b>Jonathan Mutunga</b><div style="color:#6B7280">Last Mile Trufoods</div></span><b>0719 555 326</b></div></div>'''
 return shell("Terms",body)
@app.route("/policies")
def policies_page(): return redirect("/terms")
@app.route("/breakdown")
def breakdown_page(): return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
 h="<div class='eyebrow'>History</div><h1>Full History</h1>"
 for p in PERIODS: h+=f"<div class='card'><h3>{p['label']}</h3><div class='row'><span>Contributions</span><b>KES {p.get('total',0):,}</b></div><div class='row'><span>Beneficiaries</span><b>KES {p.get('beneficiaries',0):,}</b></div><div class='row'><span>Fares</span><b>KES {p.get('fares',0):,}</b></div><p>{p.get('detail','')}</p></div>"
 h+="<div class='card'><h2>Beneficiaries</h2>"
 for per,n,pr,r2,d,a in BENEFICIARIES2: h+=f"<div class='row'><span><b>{n}</b><div style='color:#6B7280'>{per} · {pr} · {r2} · {d}</div></span><b>KES {a:,}</b></div>"
 h+=f"<div class='row'><span><b>Total</b></span><b>KES {sum(x[5] for x in BENEFICIARIES2):,}</b></div></div><div class='card'><h2>Fares</h2>"
 for per,n,ph,a in FARES2: h+=f"<div class='row'><span><b>{n}</b><div style='color:#6B7280'>{per} · {ph}</div></span><b>KES {a:,}</b></div>"
 h+=f"<div class='row'><span><b>Total</b></span><b>KES {sum(x[3] for x in FARES2):,}</b></div></div>"
 return shell("History",h)
@app.route("/shareout")
def shareout_page():
 shares,tc,tm,rate=calc_shares();ts=sum(x["share"] for x in shares)
 h=f"<div class='eyebrow'>Share-Out · Dec 2025 — Sep 2026</div><h1>Share-Out</h1><div class='hero'><div class='lbl'>AMOUNT TO SHARE</div><h1>KES 605,759</h1><p>1 month = KES {rate:,.2f} · Shares KES {ts:,.2f} + Retained 250,000 = BF 855,759</p></div><div class='grid' style='margin-top:14px'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{tm}</h2></div><div class='kpi'><div>Total Contributions</div><h2>KES {tc:,}</h2></div><div class='kpi'><div>Total Shares</div><h2>KES {ts:,.2f}</h2></div></div>"
 h+='''<div class="card"><div style="display:flex;justify-content:space-between"><h2>Member Share-Out Schedule</h2><a class="btn2 gold" href="/download/shareout">Download Excel</a></div><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="margin:14px 0"><div style="overflow:auto"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share Payable</th></tr><tbody id="shareBody">'''
 for i,x in enumerate(shares,1):
  lu=PWANI_LOGO if x['project']=='Pwani Oil Products' else (JAVA_LOGO if x['project']=='Java House' else (SCJ_LOGO if x['project']=='SC Johnson' else ''))
  logo=f'<img src="{lu}" style="width:30px;height:30px;border-radius:999px;object-fit:cover;border:1px solid #eee;vertical-align:middle;margin-right:8px" onerror="this.style.display=\'none\'">' if lu else ''
  pc='pwani' if x['project']=='Pwani Oil Products' else ('java' if x['project']=='Java House' else ('scj' if x['project']=='SC Johnson' else ''))
  h+=f"<tr data-search='{(x['full_names']+' '+x['staff_no']+' '+x['project']).lower()}'><td>{i}</td><td>{logo}<b>{x['full_names']}</b><div style='font-size:11px;color:#667085'>{x['staff_no']} · {x['email']}</div></td><td><span class='pill {pc}'>{x['project']}</span></td><td>{x['month_joined'] or '-'}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>"
 h+="</tbody></table></div></div><script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(r=>{r.style.display=r.getAttribute('data-search').includes(q)?'':'none'})}</script>"
 return shell("Share-Out",h)
@app.route("/download/shareout")
def download_shareout():
 shares,tc,tm,rate=calc_shares()
 from openpyxl import Workbook
 from openpyxl.styles import Font,PatternFill,Alignment
 wb=Workbook();ws=wb.active;ws.title="Share-Out";ws.append(["F.I.G BRANDS WELFARE - SHARE-OUT SCHEDULE"]);ws.append(["BF less 250,000 shared per month"]);ws.append([f"BF: {BF:,} | Retained: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Months: {tm} | Value of One Month: {rate:,.2f} | Total Contributions: {tc:,}"]);ws.append([]);ws.append(["#","Staff No","Full Names","Project","Date Joined","Months","Contribution","Share Payable"])
 for c in ws[5]: c.font=Font(bold=True,color="FFFFFF");c.fill=PatternFill("solid",fgColor="0F2A44");c.alignment=Alignment(horizontal="center")
 for i,x in enumerate(shares,1): ws.append([i,x["staff_no"],x["full_names"],x["project"],x["month_joined"],x["months"],x["contribution"],round(x["share"],2)])
 ws.append([]);ws.append(["","","","","","TOTAL",tc,round(sum(x["share"] for x in shares),2)]);ws.append(["","","","","","RETAINED","",RESERVE]);ws.append(["","","","","","BF","",round(sum(x["share"] for x in shares),2)+RESERVE]);ws.freeze_panes="A6";ws.auto_filter.ref=ws.dimensions
 for col,w in zip("ABCDEFGH",[6,14,30,22,14,18,20,20]): ws.column_dimensions[col].width=w
 out=io.BytesIO();wb.save(out);out.seek(0);return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
@app.route("/members")
def members_page():
 body='''<div class="eyebrow">Directory · F.I.G Brands Welfare</div><h1>Members</h1><p id="memberCountLabel" style="color:#6B7280"></p><div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap"><input class="input" id="q" placeholder="Search by name, staff, project" oninput="fil()" style="flex:2;min-width:200px"><select class="input" id="projFilter" onchange="fil()" style="flex:1;min-width:160px"><option value="All Projects">All Projects</option></select></div></div><div id="list" style="margin-top:4px"></div><a class="btn2 adminOnly" href="/download/excel">Download Excel</a><script>let all=[];let isAdmin=(localStorage.getItem('fig_role')=='Admin');const PWANI_LOGO="'''+PWANI_LOGO+'''";const JAVA_LOGO="'''+JAVA_LOGO+'''";const SCJ_LOGO="'''+SCJ_LOGO+'''";async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('memberCountLabel').textContent=d.total_members+' members · '+d.projects_total+' projects';let sel=document.getElementById('projFilter');sel.innerHTML='<option value="All Projects">All Projects ('+d.total_members+')</option>';(d.projects||[]).forEach(p=>{let o=document.createElement('option');o.value=p;o.textContent=p+' ('+(d.projects_breakdown[p]||0)+')';sel.appendChild(o)});let r2=await fetch('/api/members');let dd=await r2.json();all=dd.members;render(all)}function ini(n){return n.split(' ').filter(w=>w).slice(0,2).map(w=>w[0]).join('').toUpperCase()}function det(l,v,full){return '<div class="mdetail'+(full?' full':'')+'"><span>'+l+'</span><b>'+(v||'-')+'</b></div>'}function render(l){let h='';l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';let isPwani=m.project=='Pwani Oil Products';let isJava=m.project=='Java House';let isScj=m.project=='SC Johnson';let logoUrl=isPwani?PWANI_LOGO:(isJava?JAVA_LOGO:(isScj?SCJ_LOGO:''));let badge=(isPwani||isJava||isScj)?'<span class="mavatarBadge"><img src="'+logoUrl+'" onerror="this.parentElement.style.display=\\'none\\'"></span>':'';let pc=isPwani?' pwani':(isJava?' java':(isScj?' scj':''));let extra=isAdmin?(det('Staff Number',m.staff_no)+det('Date Joined',m.month_joined)+det('Father ID',m.father_id)+det('Mother ID',m.mother_id)+det('Guardian ID',m.guardian_id)+det('Spouse ID',m.spouse_id)+det('Kids Birth Certs',kids,true)):(det('Date Joined',m.month_joined)+det('Status','Active'));h+='<div class="mcard"><div class="mhead"><div class="mavatar"><div class="mavatarCircle">'+ini(m.full_names)+'</div>'+badge+'</div><div class="minfo"><div class="mname">'+m.full_names+'</div><div class="memail">'+(isAdmin?m.email:'Member · F.I.G Brands')+'</div><div class="mchips"><span class="pill'+pc+'">'+m.project+'</span><span class="mstatus"><i></i>Active Member</span></div></div></div><div class="mdetails">'+extra+'</div></div>'});document.getElementById('list').innerHTML=h||'<div class="card">No members</div>'}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(m=>(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(qq)&&(pf=='All Projects'||m.project==pf)))}load();</script>'''
 return shell("Members",body)
@app.route("/register")
def register():
 opts="".join([f'<option value="{p}">{p}</option>' for p in PROJECTS]);body='''<div class="eyebrow">Create Account</div><h1>Create Account</h1><p>Create your account, then login. No automatic login.</p><div class="card"><div style="display:flex;gap:16px"><div onclick="document.getElementById('photoInput').click()" style="width:96px;height:96px;border-radius:999px;border:1px solid #D9D0BF;display:flex;align-items:center;justify-content:center;overflow:hidden;cursor:pointer"><img id="photoPreview" style="display:none;width:100%;height:100%;object-fit:cover"><span id="photoPlaceholder">Add Photo</span></div><div><b>Member Photo</b><div style="color:#6B7280">Max 2MB</div><input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></div></div>'''
 for sec,fields in [("1. Staff Information",[("staff_no","Staff Number","text"),("project","Project","select"),("month_joined","Date Joined","text"),("full_names","Full Names","text"),("email","Email","text"),("password","Password","password")]),("2. Parents IDs",[("father_id","Father ID","text"),("mother_id","Mother ID","text")]),("3. Guardian and Spouse",[("guardian_id","Guardian ID No.","text"),("spouse_id","Spouse ID No.","text")]),("4. Kids Birth Certificates",[("kid1","Kid 1","text"),("kid2","Kid 2","text"),("kid3","Kid 3","text"),("kid4","Kid 4","text"),("kid5","Kid 5","text")])]:
  body+=f"<h3 style='margin-top:22px'>{sec}</h3><div class='grid'>"
  for fid,label,typ in fields:
   if fid=="project": body+=f"<div><label>{label}</label><select class='input' id='project'>{opts}</select></div>"
   else: body+=f"<div><label>{label}</label><input class='input' id='{fid}' type='{typ}'></div>"
  body+="</div>"
 body+='''<button class="btn" onclick="doReg()" style="margin-top:20px">Create Account</button><p id="msg"></p><p style="text-align:center">Already have an account? <a href="/login">Login</a></p></div><script>let photoBase64="";function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>2*1024*1024){alert('File too large');return}let r=new FileReader();r.onload=function(ev){photoBase64=ev.target.result;document.getElementById('photoPreview').src=photoBase64;document.getElementById('photoPreview').style.display='block';document.getElementById('photoPlaceholder').style.display='none'};r.readAsDataURL(f)}async function doReg(){let d={};["staff_no","project","full_names","email","password","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>{d[k]=document.getElementById(k).value});d.photo=photoBase64;if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';return}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;if(r.ok){document.getElementById('msg').textContent='Account created. Please login now.';setTimeout(()=>location.href='/login',1200)}}</script>'''
 return shell("Register",body)
@app.route("/login")
def login_page():
 return '''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>Login - F.I.G BRANDS</title><style>body{font-family:Inter,Arial;max-width:420px;margin:40px auto;padding:20px;background:#F8F9FA}h1{font-size:28px;color:#0F2A44}.card{background:#fff;border:1px solid #E5E7EB;border-radius:16px;padding:22px;box-shadow:0 4px 16px rgba(0,0,0,.06)}label{font-size:12px;font-weight:600}input{width:100%;height:48px;border:1px solid #D1D5DB;border-radius:12px;padding:0 12px;margin:6px 0 14px;box-sizing:border-box}button{width:100%;height:48px;background:#0F2A44;color:#fff;border:0;border-radius:12px;font-weight:600;cursor:pointer}a{color:#0F2A44;font-weight:600}</style></head><body><div style="text-align:center"><div style="width:56px;height:56px;background:#0F2A44;color:#fff;border-radius:14px;display:flex;align-items:center;justify-content:center;margin:auto;font-weight:700">FIG</div><h1>F.I.G BRANDS</h1><p style="color:#6B7280">Welfare System — Please login</p></div><div class="card"><label>Email</label><input id="email" placeholder="you@example.com"><label>Password</label><input id="pass" type="password" placeholder="Password"><button onclick="doLogin()">Login</button><p id="msg"></p><p style="text-align:center">No account? <a href="/register">Create Account</a></p><p style="text-align:center;font-size:13px;color:#6B7280">Admin: marlonkikuyu@gmail.com</p></div><script>async function doLogin(){let e=document.getElementById('email').value.trim().toLowerCase();let p=document.getElementById('pass').value;if(!e||!p){document.getElementById('msg').textContent='Enter email and password';return}let r=await fetch('/api/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:e,password:p})});let j=await r.json();if(!r.ok){document.getElementById('msg').textContent=j.error||'Login failed';return}localStorage.setItem('fig_user',j.email);localStorage.setItem('fig_role',j.role);localStorage.setItem('fig_name',j.full_names);localStorage.setItem('fig_email',j.email);document.getElementById('msg').textContent='Login successful...';setTimeout(()=>location.href='/',600)}</script></body></html>'''
@app.route("/admin")
def admin_login_page():
 body='''<div class="eyebrow">Secure Area</div><h1>Admin Login</h1><div class="card"><p>Go to <a href="/login">Login</a> with admin email.</p><p>Admin: '''+ADMIN_EMAIL+'''</p></div>'''
 return shell("Admin",body)
@app.route("/admin/dashboard")
def admin_dashboard():
 body='''<div class="eyebrow">Administration</div><h1>Admin Dashboard</h1><p id="adminCheck" style="color:#B42318"></p><div class="card"><a class="btn2" href="/">Overview</a> <a class="btn2" href="/members">Members</a> <a class="btn2" href="/register">Register</a> <a class="btn2" href="/shareout">Share-Out</a> <a class="btn2" href="/breakdown2">History</a> <a class="btn2" href="/terms">Terms</a> <a class="btn2 gold" href="/download/excel">Download Excel</a></div><div class="card"><button class="btn" onclick="clearAll()" style="background:#B42318">Clear All Data</button><p id="clearMsg"></p></div><div class="card"><h2>Edit Member</h2><div id="editBox" style="display:none"><label>Full Names</label><input class="input" id="e_name"><div style="margin-top:10px"><label>Staff Number</label><input class="input" id="e_staff"></div><div style="margin-top:10px"><label>Project</label><input class="input" id="e_proj"></div><div style="margin-top:10px"><label>Date Joined</label><input class="input" id="e_joined"></div><div style="margin-top:10px"><label>Father ID</label><input class="input" id="e_father"></div><div style="margin-top:10px"><label>Mother ID</label><input class="input" id="e_mother"></div><div style="margin-top:10px"><label>Guardian ID</label><input class="input" id="e_guardian"></div><div style="margin-top:10px"><label>Spouse ID</label><input class="input" id="e_spouse"></div><div style="margin-top:10px"><label>Kid 1</label><input class="input" id="e_k1"></div><div style="margin-top:10px"><label>Kid 2</label><input class="input" id="e_k2"></div><div style="margin-top:10px"><label>Kid 3</label><input class="input" id="e_k3"></div><div style="margin-top:10px"><label>Kid 4</label><input class="input" id="e_k4"></div><div style="margin-top:10px"><label>Kid 5</label><input class="input" id="e_k5"></div><button class="btn" onclick="saveEdit()" style="margin-top:14px">Save Changes</button><p id="editMsg"></p></div></div><div class="card"><h2>Members</h2><div id="tbl"></div></div><div class="card"><h2>Support Messages</h2><div id="supList">Loading...</div></div><script>let editId=null;let allM=[];if(localStorage.getItem('fig_role')!='Admin'){document.getElementById('adminCheck').textContent='Access denied: Admins only.'}async function clearAll(){if(!confirm('DELETE ALL? Download Excel first.'))return;let r=await fetch('/api/clear-all?key='''+ADMIN_KEY+''',{method:'POST'});let j=await r.json();document.getElementById('clearMsg').textContent=j.message||j.error;load()}async function load(){if(localStorage.getItem('fig_role')!='Admin')return;let r=await fetch('/api/members_admin');let d=await r.json();allM=d.members;let h='';d.members.forEach(m=>{h+='<div class="row"><span><b>'+m.staff_no+'</b> '+m.full_names+'<div style="color:#6B7280">'+m.email+' · '+m.project+'</div></span><span><button onclick="editM('+m.id+')" style="background:#0F2A44;color:#fff;border-radius:999px;padding:6px 12px;border:0">Edit</button> <button onclick="del('+m.id+')" style="border-radius:999px;padding:6px 10px">Delete</button></span></div>'});document.getElementById('tbl').innerHTML=h||'No members';let r2=await fetch('/api/support_list');let d2=await r2.json();document.getElementById('supList').innerHTML=d2.messages.map(m=>'<div style="padding:8px 0;border-bottom:1px solid #eee"><b>'+(m.name||'Guest')+'</b> '+m.msg+'</div>').join('')||'No messages'}function editM(id){let m=allM.find(x=>x.id==id);if(!m)return;editId=id;document.getElementById('editBox').style.display='block';document.getElementById('e_name').value=m.full_names||'';document.getElementById('e_staff').value=m.staff_no||'';document.getElementById('e_proj').value=m.project||'';document.getElementById('e_joined').value=m.month_joined||'';document.getElementById('e_father').value=m.father_id||'';document.getElementById('e_mother').value=m.mother_id||'';document.getElementById('e_guardian').value=m.guardian_id||'';document.getElementById('e_spouse').value=m.spouse_id||'';document.getElementById('e_k1').value=m.kid1||'';document.getElementById('e_k2').value=m.kid2||'';document.getElementById('e_k3').value=m.kid3||'';document.getElementById('e_k4').value=m.kid4||'';document.getElementById('e_k5').value=m.kid5||'';window.scrollTo({top:0,behavior:'smooth'})}async function saveEdit(){let d={full_names:document.getElementById('e_name').value,staff_no:document.getElementById('e_staff').value,project:document.getElementById('e_proj').value,month_joined:document.getElementById('e_joined').value,father_id:document.getElementById('e_father').value,mother_id:document.getElementById('e_mother').value,guardian_id:document.getElementById('e_guardian').value,spouse_id:document.getElementById('e_spouse').value,kid1:document.getElementById('e_k1').value,kid2:document.getElementById('e_k2').value,kid3:document.getElementById('e_k3').value,kid4:document.getElementById('e_k4').value,kid5:document.getElementById('e_k5').value};let r=await fetch('/api/members/'+editId+'?key='''+ADMIN_KEY+''',{method:'PUT',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('editMsg').textContent=j.message||j.error;if(r.ok)load()}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key='''+ADMIN_KEY+''',{method:'DELETE'});let j=await r.json();if(!r.ok)alert(j.error);load()}load();</script>'''
 return shell("Admin Dashboard",body)
@app.route("/download/excel")
def download_excel():
 proj=request.args.get("project","");c=get_db()
 try:
  q="SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users ORDER BY id DESC";a=()
  if proj and proj!="All Projects": q="SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE project=? ORDER BY id DESC";a=(norm_project(proj),)
  rows=c.execute(q,a).fetchall();headers=["Staff Number","Full Names","Project","Email","Date Joined","Father ID","Mother ID","Guardian ID","Spouse ID","Kid 1","Kid 2","Kid 3","Kid 4","Kid 5"]
  from openpyxl import Workbook
  from openpyxl.styles import Font,PatternFill,Alignment
  wb=Workbook();ws=wb.active;ws.title="Members";ws.append(headers)
  for cell in ws[1]: cell.font=Font(bold=True,color="FFFFFF");cell.fill=PatternFill("solid",fgColor="0F2A44");cell.alignment=Alignment(horizontal="center")
  for r in rows: ws.append([r[x] or "" for x in ["staff_no","full_names","project","email","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]])
  ws.freeze_panes="A2";ws.auto_filter.ref=ws.dimensions;out=io.BytesIO();wb.save(out);out.seek(0);return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="FIG_BRANDS_Members.xlsx")
 finally: c.close()
@app.route("/api/stats")
def api_stats():
 c=get_db()
 try:
  total=c.execute("SELECT COUNT(*) FROM users").fetchone()[0];rows=c.execute("SELECT project, COUNT(*) AS n FROM users GROUP BY project ORDER BY project").fetchall();merged={}
  for r in rows:
   k=norm_project(r["project"]);merged[k]=merged.get(k,0)+r["n"]
  ordered={p:merged.get(p,0) for p in PROJECTS if p in merged}
  for k,v in merged.items():
   if k not in ordered: ordered[k]=v
  return jsonify({"total_members":total,"projects_total":len(merged),"projects":list(ordered.keys()),"projects_breakdown":ordered})
 finally: c.close()
@app.route("/api/clear-all",methods=["POST"])
def api_clear_all():
 if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
 c=get_db()
 try: c.execute("DELETE FROM users WHERE email != ?",(ADMIN_EMAIL,));c.execute("DELETE FROM notifications");c.execute("DELETE FROM support_msgs");c.execute("DELETE FROM beneficiaries2");c.execute("DELETE FROM fares2");c.commit();return jsonify({"message":"All data cleared. Only admin remains."})
 finally: c.close()
@app.route("/api/repair",methods=["POST"])
def api_repair():
 if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
 init_db();return jsonify({"message":"v107 re-seeded"})
@app.route("/api/breakdown")
def api_breakdown(): return jsonify({"periods":PERIODS,"beneficiaries":BENEFICIARIES2,"beneficiaries_total":sum(x[5] for x in BENEFICIARIES2),"fares":FARES2,"fares_total":sum(x[3] for x in FARES2),"bf":BF})
@app.route("/api/shareout")
def api_shareout():
 shares,tc,tm,rate=calc_shares();return jsonify({"bf":BF,"reserve":RESERVE,"distributable":DISTRIBUTABLE,"total_contributions":tc,"total_months":tm,"per_month_rate":round(rate,2),"members":len(shares),"total_shares":round(sum(x["share"] for x in shares),2),"shares":shares})
@app.route("/api/notifications")
def api_notifs():
 c=get_db()
 try: rows=c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall();notifs=[dict(r) for r in rows];return jsonify({"notifications":notifs,"unread":sum(1 for n in notifs if not n.get("is_read")),"total":len(notifs)})
 finally: c.close()
@app.route("/api/notifications/read",methods=["POST"])
def api_notifs_read_all():
 c=get_db()
 try: c.execute("UPDATE notifications SET is_read=1");c.commit();return jsonify({"message":"All read","unread":0})
 finally: c.close()
@app.route("/api/notifications/<int:nid>/read",methods=["POST"])
def api_notif_read_one(nid):
 c=get_db()
 try: c.execute("UPDATE notifications SET is_read=1 WHERE id=?",(nid,));c.commit();row=c.execute("SELECT * FROM notifications WHERE id=?",(nid,)).fetchone();return jsonify({"message":"Read","notification":dict(row) if row else None})
 finally: c.close()
@app.route("/api/support",methods=["POST"])
def api_support():
 d=request.get_json(silent=True) or {};c=get_db()
 try: c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))",(d.get("name","Guest"),d.get("msg","")));c.commit();return jsonify({"message":"Message sent. Support will reply soon."})
 finally: c.close()
@app.route("/api/support_list")
def api_support_list():
 c=get_db()
 try: rows=c.execute("SELECT * FROM support_msgs ORDER BY id DESC").fetchall();return jsonify({"messages":[dict(r) for r in rows]})
 finally: c.close()
@app.route("/api/members")
def api_members():
 proj=request.args.get("project","");c=get_db()
 try:
  q="SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users ORDER BY id DESC";a=()
  if proj and proj!="All Projects": q="SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE project=? ORDER BY id DESC";a=(norm_project(proj),)
  rows=c.execute(q,a).fetchall();return jsonify({"members":[dict(r) for r in rows]})
 finally: c.close()
@app.route("/api/members_admin")
def api_members_admin():
 c=get_db()
 try: rows=c.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users ORDER BY id DESC").fetchall();return jsonify({"members":[dict(r) for r in rows]})
 finally: c.close()
@app.route("/api/login",methods=["POST"])
def api_login():
 d=request.get_json(silent=True) or {};c=get_db()
 try:
  u=c.execute("SELECT full_names,email,password,role FROM users WHERE email=?",((d.get("email") or "").strip().lower(),)).fetchone()
  if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid email or password"}),401
  return jsonify({"email":u["email"],"full_names":u["full_names"],"role":u["role"] or "Member"})
 finally: c.close()
@app.route("/api/admin/login",methods=["POST"])
def api_admin_login():
 d=request.get_json(silent=True) or {};c=get_db()
 try:
  u=c.execute("SELECT password,api_key,role FROM users WHERE email=?",((d.get("email") or "").strip().lower(),)).fetchone()
  if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
  if u["role"]!="Admin": return jsonify({"error":"Not admin"}),403
  return jsonify({"key":u["api_key"]})
 finally: c.close()
@app.route("/api/register",methods=["POST","OPTIONS"])
def api_register():
 if request.method=="OPTIONS": return "",200
 d=request.get_json(silent=True)
 if not d or not d.get("email") or not d.get("password"): return jsonify({"error":"Email and password required"}),400
 c=get_db()
 try:
  if c.execute("SELECT id FROM users WHERE email=?",(d["email"],)).fetchone(): return jsonify({"error":"Email exists"}),400
  photo=d.get("photo","")
  if len(photo)>500000: photo=photo[:500000]
  proj=norm_project(d.get("project","HQ"))
  if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(d.get("full_names",""),)).fetchone(): return jsonify({"error":"Name exists"}),400
  c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",(d.get("staff_no",""),d.get("full_names",""),proj,d["email"],generate_password_hash(d["password"]),"fig_"+secrets.token_hex(12),d.get("month_joined",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),photo));c.execute("INSERT INTO notifications (title,msg,created,target,is_read) VALUES (?,?,?,?,?)",("New Member Registered",f"{d.get('full_names','')} joined {proj}","Just now","/members",0));c.commit();return jsonify({"message":"Account created. Please login."}),201
 except Exception as e: return jsonify({"error":str(e)}),400
 finally: c.close()
@app.route("/api/members/<int:member_id>",methods=["DELETE","PUT","OPTIONS"])
def api_member_one(member_id):
 if request.method=="OPTIONS": return "",200
 if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
 c=get_db()
 try:
  u=c.execute("SELECT email FROM users WHERE id=?",(member_id,)).fetchone()
  if not u: return jsonify({"error":"Not found"}),404
  if request.method=="DELETE":
   if u["email"]==ADMIN_EMAIL: return jsonify({"error":"Cannot delete Admin"}),403
   c.execute("DELETE FROM users WHERE id=?",(member_id,));c.commit();return jsonify({"message":"Deleted"})
  d=request.get_json(silent=True) or {};fields=["staff_no","full_names","project","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"];sets=[];vals=[]
  for f in fields:
   if f in d: sets.append(f"{f}=?");vals.append(norm_project(d[f]) if f=="project" else d[f])
  if sets: vals.append(member_id);c.execute("UPDATE users SET "+",".join(sets)+" WHERE id=?",vals);c.commit()
  return jsonify({"message":"Member updated"})
 finally: c.close()
if __name__=="__main__": app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
