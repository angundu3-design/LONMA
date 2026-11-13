from flask import Flask,request,jsonify,render_template_string,redirect,send_file
import sqlite3,os,secrets,io,re
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__);DB="lonma.db"
PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PWANI_LOGO="https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png"
JAVA_LOGO="https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_l.jpg"
SCJ_LOGO="https://bhp-plus.pl/usr/s.c.-johnson-logo.png"
HIGHCHEM_LOGO="https://directory.africa-business.com/assets/uploads/logo/highchemafrica1.png"
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
202619|GCB-TDs|1ST SEP 2024|DENIS MUCHANGI WANJA|N/A|N/A|3657222|33845884||||||
202617|GCB-TDs|1ST NOV 2023|CELESTINE ACHIENG|N/A|N/A|21686696|37131073|3402966|3550299||
202622|GCB-TDs|24TH NOV 2025|ALEX MUKUNZA ODERA|1789894|3962126|N/A|34025189|392203835|1442216536|1442613443||
202623|GCB-TDs|20TH JULY 2024|ESTHER AWUOR AGUTU|7948959|11295135|N/A||501915259||||
202964|GCB-TDs|1ST FEB 2026|PERIS WAITHERA GIKURU|9912441||||161304366|161502936|||
202620|GCB-TDs|17TH MAR 2025|SHARROW IMAMI|4224728|25048563||||||
280319|GCB-TDs|10TH OCT 2026|VIVIAN ATIENO OWUONDA|10024935|20483394||||||
202942|GCB-TDs|2026 JAN|PAUL KHAEMBA WAFULA|1103349|4732318|1103349|||||
280313|GCB-TDs|3RD AUG 2026|STEPHANIE WANJIRU|9280225|12712053|N/A||0371905680||||
202618|GCB-TDs|1ST JULY 2023|JOACHIM BACHWA BACHWA|13606151|23557862||||||
202621|GCB-TDs|5TH MARCH 2025|ANNFRIDAH MAKENA|N/A|13402020|N/A|||||||
280346|GCB-TDs|8TH SEPT 2026|OBATIAH WEKESA MAKHANU|12848951|32350703|N/A|502370256||||||'''
PERIODS=[{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200 | Kaysalt 72,900 | Kanji 12,600 | HQ 15,900 | GCB-MT 69,900 | TF-WS 71,100 | TF-LM 173,100 | TF-MT 259,500 | Kenafric 96,900 | GCB-TDs 51,000 | LAB 7,800"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400 | Kanji 9,900 | HQ 14,100 | GCB-MT 56,700 | TF-WS 49,200 | TF-LM 122,400 | TF-MT 236,100 | GCB-TDs 41,100 | Higchem 30,000 | Antonia 3,600"}]
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
  mo=months_active(r["month_joined"]);out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":"","month_joined":r["month_joined"] or "","months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0})
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
 c=get_db();c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)');c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS community_posts (id INTEGER PRIMARY KEY AUTOINCREMENT, author_name TEXT, author_email TEXT, project TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS community_comments (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, author_name TEXT, author_email TEXT, msg TEXT, created TEXT)');c.execute('CREATE TABLE IF NOT EXISTS community_likes (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, email TEXT, UNIQUE(post_id,email))');c.execute('CREATE TABLE IF NOT EXISTS community_bookmarks (id INTEGER PRIMARY KEY AUTOINCREMENT, post_id INTEGER, email TEXT, UNIQUE(post_id,email))')
 for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
  try: c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
  except: pass
 for col in ["media_type","media_data","repost_of"]:
  try: c.execute(f"ALTER TABLE community_posts ADD COLUMN {col} TEXT")
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
 c.commit();c.close();print(f"v113 seeded {added}")
init_db()
@app.after_request
def after(r):
 r.headers.add('Access-Control-Allow-Origin','*');r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY');r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS');return r
@app.route("/favicon.ico")
def favicon(): return '<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="10" fill="#0F2A44"/><text x="32" y="42" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#C9A86A" text-anchor="middle">FIG</text></svg>',200,{"Content-Type":"image/svg+xml"}
def shell(title,body):
 return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800&family=Fraunces:opsz,wght@9..144,600&display=swap" rel="stylesheet"><script>if(!localStorage.getItem('fig_user')&&location.pathname!='/login'&&location.pathname!='/register'){location.href='/login'}function figLogout(){['fig_user','fig_role','fig_name','fig_email'].forEach(k=>localStorage.removeItem(k));location.href='/login'}</script><style>:root{--navy:#0F2A44;--gold:#B9975B;--ink:#111827;--muted:#6B7280;--muted2:#9CA3AF;--line:#E5E7EB;--line2:#F3F4F6;--bg:#F8F9FA;--card:#FFFFFF;--red:#B42318}*{box-sizing:border-box}body{font-family:Inter,sans-serif;background:var(--bg);color:var(--ink);margin:0;padding-bottom:140px}h1,h2,h3{font-family:Fraunces,Georgia,serif;font-weight:600;color:var(--navy);margin:0 0 10px}.top{height:58px;background:#fff;display:flex;align-items:center;gap:12px;padding:0 12px;position:sticky;top:0;z-index:20;border-bottom:1px solid var(--line)}.logo{width:40px;height:40px;background:var(--navy);color:#fff;border:0;border-radius:10px;font-family:Fraunces,Georgia,serif;font-weight:600;cursor:pointer}.top small{display:block;font-size:10px;letter-spacing:.14em;color:var(--muted);font-weight:600;text-transform:uppercase}.top b{font-size:15px;color:var(--navy)}.iconbtn{background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:38px;height:38px;cursor:pointer;position:relative;display:flex;align-items:center;justify-content:center}.avatar{width:38px;height:38px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-size:12px;font-weight:700;cursor:pointer}.bellBadge{position:absolute;top:-4px;right:-4px;background:var(--red);color:#fff;min-width:19px;height:19px;border-radius:999px;font-size:11px;display:none;align-items:center;justify-content:center;padding:0 5px;border:2px solid #fff}.bellBadge.show{display:flex}.toplinks{background:#fff;border-bottom:1px solid var(--line);padding:10px 14px;display:flex;gap:16px;flex-wrap:nowrap;overflow-x:auto;white-space:nowrap;position:sticky;top:58px;z-index:15;scrollbar-width:none}.toplinks::-webkit-scrollbar{display:none}.toplinks a{color:#374151;text-decoration:none;font-size:13px;font-weight:600;flex-shrink:0;white-space:nowrap}.page{max-width:1080px;margin:auto;padding:18px 14px 180px}.page>div:last-child{margin-bottom:110px}.card{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:18px;margin-bottom:14px;overflow:hidden;box-shadow:0 1px 3px rgba(0,0,0,.05)}.input{width:100%;height:48px;border:1px solid #D1D5DB;border-radius:12px;padding:0 14px;background:var(--card);color:var(--ink);font-size:14px}label{font-size:12px;font-weight:600;display:block;margin-bottom:6px}.btn{width:100%;height:48px;background:var(--navy);color:#fff;border:0;border-radius:12px;font-weight:600;cursor:pointer}.btn2{display:inline-flex;align-items:center;justify-content:center;min-height:44px;background:var(--navy);color:#fff;padding:10px 18px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}.btn2.gold{background:var(--gold);color:#fff}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.kpi{background:var(--card);border:1px solid var(--line);border-radius:18px;padding:16px}.kpi div:first-child{font-size:11px;letter-spacing:.12em;text-transform:uppercase;color:var(--muted);font-weight:700}.kpi h2{font-size:28px;margin:10px 0 4px}.hero{background:linear-gradient(135deg,#0F2A44 0%,#1E3A5F 100%);color:#fff;border-radius:20px;padding:20px;padding-bottom:28px;margin-bottom:16px}.hero .lbl{font-size:11px;letter-spacing:.18em;color:#D6C39A;font-weight:700}.hero h1{color:#fff;font-size:30px;margin:12px 0 8px;line-height:1.15}.hero p{color:rgba(255,255,255,.75);margin:0}.nav{position:fixed;left:10px;right:10px;bottom:calc(8px + env(safe-area-inset-bottom));height:60px;background:rgba(255,255,255,.96);backdrop-filter:blur(10px);border:1px solid var(--line);border-radius:20px;display:flex;z-index:30;box-shadow:0 8px 24px rgba(0,0,0,.12);padding:4px;gap:2px}.nav a{flex:1;color:#6B7280;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:10px;font-weight:600;border-radius:14px;white-space:nowrap}.nav a.active{color:var(--navy);background:#EEF2FF}.row{display:flex;justify-content:space-between;gap:12px;padding:12px 2px;border-bottom:1px solid var(--line2)}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid var(--line2);text-align:left}th{font-size:11px;letter-spacing:.1em;text-transform:uppercase;color:var(--muted)}td b{color:var(--navy)}.num{text-align:right;white-space:nowrap}.pill{display:inline-flex;align-items:center;background:#EEF2FF;color:#3730A3;padding:6px 12px;border-radius:999px;font-size:11px;font-weight:700;border:1px solid #C7D2FE;max-width:100%;line-height:1.3}.pill.pwani,.pill.java,.pill.scj{background:#FEF2F2;color:#991B1B;border-color:#FECACA}.pill.higchem{background:#EFF6FF;color:#1E40AF;border-color:#BFDBFE}.mcard{background:var(--card);border:1px solid var(--line);border-radius:20px;padding:0;margin-bottom:16px;overflow:hidden;box-shadow:0 2px 10px rgba(15,42,68,.07)}.mhead{display:flex;gap:14px;align-items:flex-start;padding:16px;background:linear-gradient(180deg,#F8FAFC 0%,#fff 100%)}.mavatar{position:relative;flex-shrink:0}.mavatarCircle{width:56px;height:56px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:19px}.mavatarBadge{position:absolute;right:-4px;bottom:-4px;width:24px;height:24px;border-radius:999px;background:#fff;border:1px solid #E5E7EB;display:flex;align-items:center;justify-content:center;overflow:hidden}.mavatarBadge img{width:20px;height:20px;object-fit:cover}.minfo{flex:1;min-width:0}.mname{font-family:Fraunces,Georgia,serif;font-size:20px;font-weight:600;color:var(--navy);line-height:1.25;word-break:break-word}.memail{font-size:13px;color:var(--muted);margin-top:3px;word-break:break-all;line-height:1.4}.mchips{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}.mstatus{display:inline-flex;align-items:center;gap:6px;background:#ECFDF5;color:#065F46;border:1px solid #A7F3D0;padding:5px 10px;border-radius:999px;font-size:11px;font-weight:700}.mstatus i{width:7px;height:7px;border-radius:999px;background:#10B981;display:block}.mdetails{display:grid;grid-template-columns:1fr 1fr;gap:0;border-top:1px solid var(--line2)}.mdetail{padding:13px 18px;border-bottom:1px solid var(--line2)}.mdetail:nth-child(odd){border-right:1px solid var(--line2)}.mdetail span{display:block;font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:var(--muted);font-weight:700;margin-bottom:4px}.mdetail b{font-size:14px;color:var(--ink);word-break:break-word;line-height:1.4}.mdetail.full{grid-column:1/-1}.popup{position:fixed;inset:0;background:rgba(17,24,39,.45);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:var(--card);color:var(--ink);width:100%;max-width:520px;border-radius:16px 16px 0 0;padding:20px;max-height:86vh;overflow:auto}.notifItem{padding:13px 0;border-bottom:1px solid var(--line2);cursor:pointer}.drawerOverlay{position:fixed;inset:0;background:rgba(17,24,39,.45);display:none;z-index:98}.drawerOverlay.show{display:block}.drawer{position:fixed;top:0;left:0;bottom:0;width:320px;max-width:86vw;background:#fff;z-index:99;transform:translateX(-105%);transition:transform .28s;overflow-y:auto;padding:0 0 20px}.drawer.show{transform:translateX(0)}.dhead{padding:20px;border-bottom:1px solid var(--line)}.dprofile{display:flex;gap:12px;align-items:center}.davatar{width:52px;height:52px;border-radius:999px;background:var(--navy);color:#fff;display:flex;align-items:center;justify-content:center;font-weight:700}.dstats{display:flex;gap:10px;margin-top:14px}.dstat{flex:1;background:var(--bg);border:1px solid var(--line);border-radius:10px;padding:10px}.dstat b{font-size:17px;color:var(--navy)}.dstat span{font-size:11px;color:var(--muted);display:block}.dlink{color:#1F2937;text-decoration:none;display:flex;padding:13px 20px;font-size:15px;font-weight:600}.dlink:hover{background:#F9FAFB}.dlink small{margin-left:auto;color:var(--muted2)}.dsec{padding:16px 20px 6px;font-size:11px;letter-spacing:.14em;color:var(--muted);font-weight:700}.modeBtn{flex:1;background:#fff;border:1px solid var(--line);border-radius:10px;padding:10px 4px;cursor:pointer;font-weight:600}.modeBtn.active{background:var(--navy);color:#fff}.distRow{display:flex;align-items:center;gap:10px;padding:11px 2px;border-bottom:1px solid var(--line2)}.distLogo{width:32px;height:32px;border-radius:999px;object-fit:cover;border:1px solid var(--line);background:#fff;flex-shrink:0;display:flex;align-items:center;justify-content:center;font-weight:800;font-size:12px;color:var(--navy)}.distName{flex:1;min-width:0;font-weight:600;font-size:14px}.distBar{height:6px;background:#EEF2F6;border-radius:999px;overflow:hidden;margin-top:5px}.distBar i{display:block;height:100%;background:linear-gradient(90deg,#0F2A44,#B9975B);border-radius:999px}.distCount{font-weight:700;font-size:14px;color:var(--navy);white-space:nowrap}.benefitGrid{display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:12px}.benefit{border:1px solid var(--line);border-radius:14px;padding:12px;background:#F8FAFC}.benefit b{font-size:15px;color:var(--navy);display:block}.benefit span{font-size:12px;color:var(--muted)}.stackBtns{display:flex;gap:10px;flex-wrap:wrap;margin-top:14px}.stackBtns .btn2{flex:1;min-width:140px}body.dark{--bg:#0B1220;--card:#111A2E;--ink:#F1F5F9;--muted:#94A3B8;--muted2:#64748B;--line:#1E293B;--line2:#1E293B;--navy:#FFFFFF}body.dark .top,body.dark .toplinks,body.dark .nav,body.dark .drawer{background:#0F172A}body.dark h1,body.dark h2,body.dark h3,body.dark .top b{color:#fff}body.dark .toplinks a{color:#CBD5E1}body.dark td b{color:#fff}body.dark .pill{background:#1E293B;color:#E2E8F0;border-color:#334155}body.dark .pill.pwani,body.dark .pill.java,body.dark .pill.scj{background:#450A0A;color:#FECACA;border-color:#7F1D1D}body.dark .pill.higchem{background:#1E3A8A;color:#BFDBFE;border-color:#1D4ED8}body.dark .input{background:#0B1220;border-color:#334155;color:#fff}body.dark .pop{background:#111A2E;color:#fff}body.dark .dlink{color:#E2E8F0}body.dark .mhead{background:linear-gradient(180deg,#1E293B 0%,#111A2E 100%)}body.dark .mname{color:#fff}body.dark .mstatus{background:#064E3B;color:#A7F3D0;border-color:#065F46}body.dark .iconbtn{background:#1E293B;border-color:#334155;color:#fff}body.dark .benefit{background:#1E293B}body.dark .distBar{background:#1E293B}@media(max-width:640px){.grid{grid-template-columns:1fr}.hero h1{font-size:30px}.mname{font-size:19px}}@media(max-width:420px){.stackBtns .btn2{flex:1 1 100%}}.toplinks{flex-wrap:nowrap!important;overflow-x:auto!important;white-space:nowrap!important;gap:18px!important}.toplinks a{flex-shrink:0!important;white-space:nowrap!important}.page{padding-bottom:180px!important}.page>div:last-child{margin-bottom:110px!important}.hero{padding-bottom:28px!important}.nav{bottom:calc(8px + env(safe-area-inset-bottom))!important;background:rgba(255,255,255,.96)!important}</style></head><body><div class="drawerOverlay" id="drawerOverlay" onclick="closeDrawer()"></div><div class="drawer" id="drawer"><div class="dhead"><div style="display:flex;justify-content:space-between"><span style="font-size:11px;letter-spacing:.16em;color:var(--muted);font-weight:700">F.I.G BRANDS · WELFARE</span><button onclick="closeDrawer()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:30px;height:30px;cursor:pointer">✕</button></div><div class="dprofile" style="margin-top:16px"><div class="davatar" id="drawerAvatar">--</div><div><div style="font-weight:700;font-size:17px" id="drawerName">My Account</div><div style="font-size:13px;color:var(--muted)" id="drawerEmail">Please login</div><span id="drawerRoleBadge" style="display:inline-block;margin-top:6px;background:#ECFDF5;color:#065F46;border:1px solid #A7F3D0;padding:3px 8px;border-radius:999px;font-size:11px;font-weight:600">Member</span></div></div><div class="dstats adminOnly" id="drawerStats"><div class="dstat"><b id="drawerMembers">-</b><span>Members</span></div><div class="dstat"><b id="drawerProjects">-</b><span>Projects</span></div><div class="dstat"><b>KES 605,759</b><span>To Share</span></div></div></div><a href="/" class="dlink">Overview <small>›</small></a><a href="/members" class="dlink">Members <small>›</small></a><a href="/community" class="dlink">Community Chat <small>›</small></a><a href="/register" class="dlink adminOnly">Register Member <small>›</small></a><a href="/shareout" class="dlink adminOnly">Share-Out <small>›</small></a><a href="/breakdown2" class="dlink adminOnly">History <small>›</small></a><a href="/terms" class="dlink">Terms &amp; Policies <small>›</small></a><div class="dsec">APPEARANCE</div><div style="display:flex;gap:8px;padding:0 20px"><button class="modeBtn" id="modeLight" onclick="setMode('light')">Light</button><button class="modeBtn" id="modeDark" onclick="setMode('dark')">Dark</button><button class="modeBtn" id="modeSystem" onclick="setMode('system')">System</button></div><div class="dsec">NOTIFICATIONS &amp; SETTINGS</div><a href="#" onclick="closeDrawer();openBell();return false" class="dlink">Notifications <span id="drawerBell" style="background:#B42318;color:#fff;border-radius:999px;font-size:11px;padding:2px 8px;display:none;margin-left:auto">0</span></a><a href="/admin" class="dlink adminOnly">Admin / Settings <small>›</small></a><a href="#" onclick="closeDrawer();openSupport();return false" class="dlink">Help Centre <small>›</small></a><a href="/download/excel" class="dlink adminOnly">Download Excel <small>›</small></a><div class="dsec">ACCOUNT</div><a href="#" onclick="figLogout();return false" class="dlink" style="color:#B42318">Logout <small>›</small></a><div style="padding:16px 20px;color:var(--muted);font-size:12px">F.I.G BRANDS Welfare · v113<br>Support: +254 707 780 807</div></div><div class="top"><button class="logo" onclick="openDrawer()">FIG</button><div><b>F.I.G BRANDS</b><small>Welfare System</small></div><div style="margin-left:auto;display:flex;gap:8px;align-items:center"><button class="iconbtn" id="modeToggle" onclick="toggleMode()">◐</button><button class="iconbtn" onclick="openBell()">○<span class="bellBadge" id="bellBadge">0</span></button><div class="avatar" id="topAvatar" onclick="openDrawer()">--</div></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/community">Community</a><a href="/register" class="adminOnly">Register</a><a href="/shareout" class="adminOnly">Share-Out</a><a href="/breakdown2" class="adminOnly">History</a><a href="/terms">Terms &amp; Policies</a><a href="/admin" class="adminOnly">Admin</a></div><div class="page">'''+body+'''</div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Notifications</b><button onclick="closeBell()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:32px;height:32px">✕</button></div><div id="notifList"></div><button class="btn" onclick="markRead()" style="margin-top:12px">Mark all as read</button></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="pop"><div style="display:flex;justify-content:space-between"><b>Contact Support</b><button onclick="closeSupport()" style="background:#F3F4F6;border:1px solid var(--line);border-radius:999px;width:32px;height:32px">✕</button></div><p><a href="https://wa.me/254707780807" target="_blank">WhatsApp 0707 780 807</a> · <a href="mailto:info@figbrands.co.ke">info@figbrands.co.ke</a></p><label>Your name</label><input class="input" id="supName"><div style="margin-top:12px"><label>Message</label><textarea id="supMsg" class="input" style="height:96px;padding-top:10px"></textarea></div><button class="btn" onclick="sendSupport()" style="margin-top:14px">Send Message</button><p id="supStatus"></p></div></div><nav class="nav"><a href="/" class="active">Home</a><a href="/members">Members</a><a href="/community">Community</a><a href="/shareout" class="adminOnly">Share-Out</a><a href="/terms">Terms</a><a href="/register" class="adminOnly">Add</a></nav><script>function esc(s){return String(s||'').replace(/&/g,'&amp;').replace(/</g,'&lt;')}function applyRoleUI(){var role=localStorage.getItem('fig_role')||'Member';var name=localStorage.getItem('fig_name')||'My Account';var email=localStorage.getItem('fig_email')||'';var isAdmin=(role=='Admin');document.querySelectorAll('.adminOnly').forEach(function(e){e.style.display=isAdmin?'':'none'});var dn=document.getElementById('drawerName');if(dn)dn.textContent=name;var de=document.getElementById('drawerEmail');if(de)de.textContent=(isAdmin?'Chairman · ':'Member · ')+email;var rb=document.getElementById('drawerRoleBadge');if(rb)rb.textContent=isAdmin?'Active Admin':'Member';var ini=name.split(' ').map(function(w){return w[0]}).join('').slice(0,2).toUpperCase();var av=document.getElementById('drawerAvatar');if(av)av.textContent=ini||'--';var ta=document.getElementById('topAvatar');if(ta)ta.textContent=ini||'--';if(isAdmin)loadDrawerCounts()}function applyMode(){var m=localStorage.getItem('fig_mode')||'system';var dark=(m=='dark')||(m=='system'&&window.matchMedia&&window.matchMedia('(prefers-color-scheme: dark)').matches);document.body.classList.toggle('dark',dark);var t=document.getElementById('modeToggle');if(t)t.textContent=dark?'○':'◐';['Light','Dark','System'].forEach(function(k){var b=document.getElementById('mode'+k);if(b)b.classList.toggle('active',m==k.toLowerCase())})}function setMode(m){localStorage.setItem('fig_mode',m);applyMode()}function toggleMode(){setMode(document.body.classList.contains('dark')?'light':'dark')}function openDrawer(){document.getElementById('drawer').classList.add('show');document.getElementById('drawerOverlay').classList.add('show');applyRoleUI()}function closeDrawer(){document.getElementById('drawer').classList.remove('show');document.getElementById('drawerOverlay').classList.remove('show')}async function loadDrawerCounts(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('drawerMembers').textContent=d.total_members;document.getElementById('drawerProjects').textContent=d.projects_total}catch(e){}}async function updateBell(){try{let r=await fetch('/api/notifications');let d=await r.json();let b=document.getElementById('bellBadge');let db=document.getElementById('drawerBell');if(d.unread>0){b.textContent=d.unread>99?'99+':d.unread;b.classList.add('show');db.textContent=d.unread;db.style.display='inline-block'}else{b.classList.remove('show');db.style.display='none'}}catch(e){}}async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();let h='';d.notifications.forEach(n=>{let tgt=(n.target||'/').replace(/'/g,"");h+='<div class="notifItem" onclick="tapNotif('+n.id+',\\''+esc(tgt)+'\\')"><b>'+esc(n.title)+'</b><div style="color:var(--muted)">'+esc(n.msg)+'</div><div style="font-size:11px;color:var(--muted2)">'+esc(n.created)+' · Tap to open →</div></div>'});document.getElementById('notifList').innerHTML=h||'No notifications';updateBell()}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}async function tapNotif(id,t){await fetch('/api/notifications/'+id+'/read',{method:'POST'});location.href=t||'/'}async function markRead(){await fetch('/api/notifications/read',{method:'POST'});updateBell();closeBell()}function openSupport(){document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}applyRoleUI();applyMode();updateBell();setInterval(updateBell,30000);if(window.matchMedia)window.matchMedia('(prefers-color-scheme: dark)').addEventListener('change',function(){if((localStorage.getItem('fig_mode')||'system')=='system')applyMode()});</script></body></html>''')
@app.route("/")
def index():
 body='''<div class="eyebrow">F.I.G Brands · Welfare</div><h1>Overview</h1><p style="color:#475569">Balance brought forward, less KES 250,000 retained — shared fairly, per month of contributions.</p><div class="grid"><div class="kpi"><div>Total Members</div><h2 id="total">0</h2></div><div class="kpi"><div>Projects</div><h2 id="projCount">0</h2></div></div><div class="hero" style="margin-top:14px"><div class="lbl">BALANCE BROUGHT FORWARD</div><h1>KES 855,759</h1><p>KES 605,759 to share · KES 250,000 retained</p></div><div class="grid" style="margin-top:14px"><div class="kpi"><div>Amount to Share</div><h2 style="color:#0F766E">KES 605,759</h2></div><div class="kpi"><div>Retained</div><h2 style="color:#B42318">KES 250,000</h2></div><div class="kpi"><div>Value of One Month</div><h2 id="oneMonth">-</h2><div id="oneMonthNote"></div></div></div><div class="card" style="margin-top:14px"><div class="eyebrow">Welfare Clauses 2026</div><h2 style="font-size:22px;line-height:1.3">Death Benefit</h2><div class="benefitGrid"><div class="benefit"><b>KES 100,000</b><span>Member</span></div><div class="benefit"><b>KES 50,000</b><span>Spouse</span></div><div class="benefit"><b>KES 40,000</b><span>Child</span></div><div class="benefit"><b>KES 40,000</b><span>Parents</span></div></div><p style="color:#475569;margin-top:12px;font-size:14px;line-height:1.6">Loss of Earning: 50% of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work.<br>Contribution: <b>KES 300 monthly</b></p><div class="stackBtns"><a class="btn2" href="/terms">Read Full Terms</a><a class="btn2 gold" href="/community">Join Community Chat</a></div></div><div class="card"><div class="eyebrow">Distribution</div><h2>Project Distribution</h2><div id="breakdown"></div><div class="row"><b id="projTotalLabel">Total</b><b id="projTotal">0</b></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;document.getElementById('projTotal').textContent=d.total_members;document.getElementById('projTotalLabel').textContent='Total Members ('+d.projects_total+' projects)';let logos={'Pwani Oil Products':'https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png','Java House':'https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_l.jpg','SC Johnson':'https://bhp-plus.pl/usr/s.c.-johnson-logo.png','Higchem':'https://directory.africa-business.com/assets/uploads/logo/highchemafrica1.png'};let max=Math.max(...Object.values(d.projects_breakdown),1);let h='';Object.keys(d.projects_breakdown).sort((a,b)=>d.projects_breakdown[b]-d.projects_breakdown[a]).forEach(k=>{let pct=Math.round(d.projects_breakdown[k]/max*100);let lg=logos[k]?'<img class="distLogo" src="'+logos[k]+'" onerror="this.style.display=\\'none\\'">':'<span class="distLogo">'+k.slice(0,2).toUpperCase()+'</span>';h+='<div class="distRow">'+lg+'<div style="flex:1;min-width:0"><div class="distName">'+k+'</div><div class="distBar"><i style="width:'+pct+'%"></i></div></div><span class="distCount">'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h;let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='605,759 / '+s.total_months+' months';}load();</script>'''
 return shell("Overview",body)
@app.route("/terms")
def terms_page():
 body='''<div class="eyebrow">Welfare Clauses · 2026</div><h1>Terms &amp; Policies</h1><div class="card"><h2>Death Benefits</h2><table><tr><th>Beneficiary</th><th>Benefit</th></tr><tr><td><b>Member</b></td><td><b>KES 100,000</b></td></tr><tr><td><b>Spouse</b></td><td><b>KES 50,000</b></td></tr><tr><td><b>Child</b></td><td><b>KES 40,000</b></td></tr><tr><td><b>Parents</b></td><td><b>KES 40,000</b></td></tr></table><div class="row"><span>Spouse</span><b>Must be registered</b></div><div class="row"><span>Child</span><b>Birth certificate required</b></div><div class="row"><span>Parents</span><b>Birth certificate + parent ID required</b></div><div class="row"><span>No biological parents</span><b>May nominate one guardian</b></div></div><div class="card"><h2>Loss of Earning</h2><p>After 10 days unable to work due to injury at work: 50% of basic pay, max KES 20,000, paid end of month.</p></div><div class="card"><h2>Contribution: KES 300 Monthly</h2><p>Deducted from monthly pay.</p></div><div class="card"><h2>Management</h2><p>Committee elected by all members. Every project must have at least one member on board.</p></div><div class="card"><h2>Disbursement</h2><div class="row"><span>Death</span><b>Within 2 days on death notification</b></div><div class="row"><span>Incapacitation</span><b>End of month</b></div></div><div class="card"><h2>Year-End: Min Balance KES 250,000</h2><p>Above that shared only among current active members, per contribution share. FIG Year-End 30 Nov. Audited accounts in FACES group by 20 Dec.</p></div><div class="card"><h2>Accountable Leadership</h2><div class="row"><span><b>Marlon K. Ang&apos;undu</b><div style="color:#6B7280">Chairman · FIG</div></span><b>+254 707 780 807</b></div><div class="row"><span><b>Mary Ngotah</b><div style="color:#6B7280">GCB</div></span><b>0719 203 286</b></div><div class="row"><span><b>Celestine Ouko</b><div style="color:#6B7280">SC Johnsons</div></span><b>0725 543 224</b></div><div class="row"><span><b>Irene Wamuyu</b><div style="color:#6B7280">Nairobi Java</div></span><b>0719 606 834</b></div></div>'''
 return shell("Terms",body)
@app.route("/policies")
def policies_page(): return redirect("/terms")
@app.route("/breakdown")
def breakdown_page(): return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
 h="<div class='eyebrow'>History</div><h1>Full History</h1>"
 for p in PERIODS: h+=f"<div class='card'><h3>{p['label']}</h3><div class='row'><span>Contributions</span><b>KES {p.get('total',0):,}</b></div><div class='row'><span>Beneficiaries</span><b>KES {p.get('beneficiaries',0):,}</b></div><div class='row'><span>Fares</span><b>KES {p.get('fares',0):,}</b></div><p>{p.get('detail','')}</p></div>"
 return shell("History",h)
@app.route("/community")
def community_page():
 body='''<div class="eyebrow">F.I.G Brands · Together</div><h1>Community Chat</h1><p style="color:#6B7280">Post, repost, share, save. Be kind — no insults, no politics.</p><div class="card"><div style="display:flex;gap:12px"><div class="avatar" id="comAvatar">--</div><div style="flex:1"><div id="comName" style="font-weight:700"></div><div id="comProj" style="font-size:12px;color:#6B7280"></div></div></div><textarea id="comMsg" class="input" style="height:90px;padding:12px;margin-top:12px" placeholder="What's on your mind? Share with the family..."></textarea><div id="mediaPreview" style="margin-top:10px"></div><div style="display:flex;gap:8px;margin-top:10px;flex-wrap:wrap;align-items:center"><label class="btn2" style="background:#F3F4F6;color:#111827;cursor:pointer">📷 Photo <input type="file" id="comImg" accept="image/*" style="display:none" onchange="handleMedia(event,'image')"></label><label class="btn2" style="background:#F3F4F6;color:#111827;cursor:pointer">🎬 Video <input type="file" id="comVid" accept="video/*" style="display:none" onchange="handleMedia(event,'video')"></label><button class="btn2" onclick="postMsg()">Post to Community</button></div><div class="stackBtns"><button class="btn2 gold" onclick="loadCom('mine')">My Posts</button><button class="btn2 gold" onclick="loadCom('saved')">🔖 Saved</button><button class="btn2" onclick="loadCom('all')" style="background:#F3F4F6;color:#111827">All Posts</button></div><p id="comStatus"></p></div><div id="comFeed"></div><script>let comFilter='all';let comMedia='';let comMediaType='';function comInit(){let n=localStorage.getItem('fig_name')||'Member';document.getElementById('comName').textContent=n;document.getElementById('comAvatar').textContent=n.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase();document.getElementById('comProj').textContent=localStorage.getItem('fig_email')||''}function handleMedia(e,type){let f=e.target.files[0];if(!f)return;let max=type=='video'?12*1024*1024:4*1024*1024;if(f.size>max){alert(type=='video'?'Video too big, max 12MB':'Photo too big, max 4MB');return}let r=new FileReader();r.onload=function(ev){comMedia=ev.target.result;comMediaType=type;document.getElementById('mediaPreview').innerHTML=type=='video'?'<video src="'+comMedia+'" controls style="width:100%;border-radius:12px;max-height:240px"></video><button onclick="clearMedia()" style="border:0;background:none;color:#B42318;cursor:pointer">✕ Remove video</button>':'<img src="'+comMedia+'" style="width:100%;border-radius:12px;max-height:240px;object-fit:cover"><button onclick="clearMedia()" style="border:0;background:none;color:#B42318;cursor:pointer">✕ Remove photo</button>'};r.readAsDataURL(f)}function clearMedia(){comMedia='';comMediaType='';document.getElementById('mediaPreview').innerHTML='';document.getElementById('comImg').value='';document.getElementById('comVid').value=''}function mediaHtml(p){if(!p.media_data)return '';if(p.media_type=='video')return '<video src="'+p.media_data+'" controls playsinline style="width:100%;border-radius:12px;max-height:320px;margin-top:8px"></video>';return '<img src="'+p.media_data+'" style="width:100%;border-radius:12px;max-height:320px;object-fit:cover;margin-top:8px">'}async function loadCom(f){comFilter=f||comFilter;let r=await fetch('/api/community?filter='+comFilter+'&email='+encodeURIComponent(localStorage.getItem('fig_email')||''));let d=await r.json();let h='';d.posts.forEach(p=>{let liked=p.liked?'❤️':'🤍';let saved=p.bookmarked?'🔖 Saved':'🔖 Save';let delBtn=(localStorage.getItem('fig_role')=='Admin'||p.author_email==localStorage.getItem('fig_email'))?'<button onclick="delPost('+p.id+')" style="border:0;background:none;color:#B42318;cursor:pointer;font-size:12px">Delete</button>':'';let repostBadge=p.repost_of?'<div style="background:#FFFBEB;border:1px solid #FDE68A;padding:8px 12px;border-radius:10px;font-size:13px;margin:0 18px 10px">🔁 Reposted from <b>'+(p.repost_name||'Member')+'</b><div style="color:#6B7280">'+(p.repost_msg||'')+'</div></div>':'';let coms=(p.comments||[]).map(c=>'<div style="display:flex;gap:8px;padding:8px 0;border-top:1px solid #F3F4F6"><b style="font-size:13px">'+c.author_name+'</b><span style="font-size:13px">'+c.msg+'</span></div>').join('');h+='<div class="mcard"><div class="mhead"><div class="mavatar"><div class="mavatarCircle">'+p.author_name.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()+'</div></div><div class="minfo"><div class="mname" style="font-size:17px">'+p.author_name+'</div><div class="memail">'+p.project+' · '+p.created+'</div></div>'+delBtn+'</div>'+repostBadge+'<div style="padding:0 18px 12px;font-size:15px;line-height:1.6">'+p.msg+mediaHtml(p)+'</div><div style="display:flex;gap:10px;padding:10px 18px;border-top:1px solid #F3F4F6;flex-wrap:wrap"><button onclick="likePost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">'+liked+' '+p.likes+'</button><button onclick="document.getElementById(\\'c'+p.id+'\\').focus()" style="border:0;background:none;cursor:pointer;font-weight:600">💬 '+p.comments.length+'</button><button onclick="repostPost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">🔁 '+p.reposts+' Repost</button><button onclick="sharePost('+p.id+',\\''+p.author_name.replace(/'/g,"")+'\\')" style="border:0;background:none;cursor:pointer;font-weight:600">↗️ Share</button><button onclick="bookmarkPost('+p.id+')" style="border:0;background:none;cursor:pointer;font-weight:600">'+saved+'</button></div><div style="padding:0 18px 14px"><div>'+coms+'</div><div style="display:flex;gap:8px;margin-top:8px"><input class="input" id="c'+p.id+'" placeholder="Write a reply..." style="height:40px"><button class="btn2" onclick="commentPost('+p.id+')">Reply</button></div></div></div>'});document.getElementById('comFeed').innerHTML=h||'<div class="card">No posts yet. Be the first to say hello 👋</div>'}async function postMsg(){let m=document.getElementById('comMsg').value.trim();if(!m&&!comMedia){document.getElementById('comStatus').textContent='Write something or add photo/video';return}let r=await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:m,media_type:comMediaType,media_data:comMedia})});let j=await r.json();document.getElementById('comStatus').textContent=j.message||j.error;if(r.ok){document.getElementById('comMsg').value='';clearMedia();loadCom('all')}}async function likePost(id){await fetch('/api/community/'+id+'/like',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:localStorage.getItem('fig_email')})});loadCom()}async function bookmarkPost(id){let r=await fetch('/api/community/'+id+'/bookmark',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:localStorage.getItem('fig_email')})});let j=await r.json();document.getElementById('comStatus').textContent=j.message||'';loadCom()}async function commentPost(id){let m=document.getElementById('c'+id).value.trim();if(!m)return;await fetch('/api/community/'+id+'/comment',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:m})});loadCom()}async function repostPost(id){let c=prompt('Add your comment on this repost (optional):');if(c===null)return;let r=await fetch('/api/community/'+id+'/repost',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:localStorage.getItem('fig_name'),email:localStorage.getItem('fig_email'),msg:c||'Reposted'})});let j=await r.json();alert(j.message||j.error);loadCom('all')}async function sharePost(id,author){let url=location.origin+'/community';let text='F.I.G Brands Community — Post by '+author+': '+url;if(navigator.share){try{await navigator.share({title:'F.I.G Brands Community',text:text,url:url});return}catch(e){}}try{await navigator.clipboard.writeText(text);alert('Link copied! Paste it on WhatsApp ✅')}catch(e){let w='https://wa.me/?text='+encodeURIComponent(text);window.open(w,'_blank')}}async function delPost(id){if(!confirm('Delete this post?'))return;await fetch('/api/community/'+id+'?key='''+ADMIN_KEY+'''&email='+encodeURIComponent(localStorage.getItem('fig_email')||''),{method:'DELETE'});loadCom()}comInit();loadCom('all');setInterval(()=>loadCom(),20000);</script>'''
 return shell("Community",body)
@app.route("/shareout")
def shareout_page():
 shares,tc,tm,rate=calc_shares();ts=sum(x["share"] for x in shares)
 h=f"<div class='eyebrow'>Share-Out · Dec 2025 — Sep 2026</div><h1>Share-Out</h1><div class='hero'><div class='lbl'>AMOUNT TO SHARE</div><h1>KES 605,759</h1><p>1 month = KES {rate:,.2f} · Shares KES {ts:,.2f} + Retained 250,000 = BF 855,759</p></div><div class='grid' style='margin-top:14px'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{tm}</h2></div><div class='kpi'><div>Total Contributions</div><h2>KES {tc:,}</h2></div><div class='kpi'><div>Total Shares</div><h2>KES {ts:,.2f}</h2></div></div>"
 h+='''<div class="card"><div style="display:flex;justify-content:space-between"><h2>Member Share-Out Schedule</h2><a class="btn2 gold" href="/download/shareout">Download Excel</a></div><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="margin:14px 0"><div style="overflow:auto"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share Payable</th></tr><tbody id="shareBody">'''
 for i,x in enumerate(shares,1):
  lu=PWANI_LOGO if x['project']=='Pwani Oil Products' else (JAVA_LOGO if x['project']=='Java House' else (SCJ_LOGO if x['project']=='SC Johnson' else (HIGHCHEM_LOGO if x['project']=='Higchem' else '')))
  logo=f'<img src="{lu}" style="width:30px;height:30px;border-radius:999px;object-fit:cover;border:1px solid #eee;vertical-align:middle;margin-right:8px" onerror="this.style.display=\'none\'">' if lu else ''
  pc='pwani' if x['project']=='Pwani Oil Products' else ('java' if x['project']=='Java House' else ('scj' if x['project']=='SC Johnson' else ('higchem' if x['project']=='Higchem' else '')))
  h+=f"<tr data-search='{(x['full_names']+' '+x['staff_no']+' '+x['project']).lower()}'><td>{i}</td><td>{logo}<b>{x['full_names']}</b><div style='font-size:11px;color:#667085'>Staff: {x['staff_no']}</div></td><td><span class='pill {pc}'>{x['project']}</span></td><td>{x['month_joined'] or '-'}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>"
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
    body='''<div class="eyebrow">Directory - F.I.G Brands Welfare</div><h1>Members</h1><p id="memberCountLabel" style="color:#6B7280"></p><div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap"><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="flex:1;min-width:200px"><select class="input" id="projFilter" onchange="fil()" style="max-width:220px"><option value="">All Projects</option>''' + ''.join([f'<option>{p}</option>' for p in PROJECTS]) + '''</select></div><div id="membersList" style="margin-top:14px"></div></div><script>let ALL=[];async function loadM(){let r=await fetch('/api/members');let d=await r.json();ALL=d.members;document.getElementById('memberCountLabel').textContent=ALL.length+' members - '+d.projects_total+' projects';fil()}function fil(){let q=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;let h='';ALL.filter(m=>(!q||(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(q))&&(!pf||m.project==pf)).forEach(m=>{h+='<div class="mcard"><div class="mhead"><div class="mavatar"><div class="mavatarCircle">'+m.full_names.split(' ').map(w=>w[0]).join('').slice(0,2).toUpperCase()+'</div></div><div class="minfo"><div class="mname">'+m.full_names+'</div><div class="memail">'+m.email+'</div><div class="mchips"><span class="pill">'+m.project+'</span><span class="mstatus"><i></i>Active</span></div></div></div><div class="mdetails"><div class="mdetail"><span>Staff No</span><b>'+m.staff_no+'</b></div><div class="mdetail"><span>Joined</span><b>'+(m.month_joined||'-')+'</b></div><div class="mdetail"><span>Project</span><b>'+m.project+'</b></div><div class="mdetail"><span>Months</span><b>'+m.months+'</b></div><div class="mdetail full"><span>Share Payable</span><b>KES '+m.share.toLocaleString(undefined,{minimumFractionDigits:2})+'</b></div></div></div>'});document.getElementById('membersList').innerHTML=h||'No members found';}loadM();</script>'''
    return shell("Members", body)
@app.route("/register", methods=["GET","POST"])
def register_page():
    if request.method=="POST":
        d=request.form or request.get_json(silent=True) or {}
        c=get_db()
        ok=add_user(c, d.get("staff_no",""), d.get("full_names",""), d.get("project",""), d.get("month_joined",""))
        c.commit(); c.close()
        if request.is_json: return jsonify({"ok": ok})
        return redirect("/members")
    body='''<div class="eyebrow">Join F.I.G</div><h1>Register Member</h1><div class="card"><form method="POST"><label>Staff No</label><input class="input" name="staff_no" required><div style="margin-top:12px"><label>Full Names</label><input class="input" name="full_names" required></div><div style="margin-top:12px"><label>Project</label><select class="input" name="project">''' + ''.join([f'<option>{p}</option>' for p in PROJECTS]) + '''</select></div><div style="margin-top:12px"><label>Date Joined e.g. 01/03/2025</label><input class="input" name="month_joined" placeholder="01/03/2025"></div><button class="btn" style="margin-top:16px">Register Member</button></form></div>'''
    return shell("Register", body)
@app.route("/login", methods=["GET","POST"])
def login_page():
    if request.method=="POST":
        d=request.form or request.get_json(silent=True) or {}
        email=(d.get("email") or "").strip().lower(); pw=d.get("password") or ""
        c=get_db(); u=c.execute("SELECT * FROM users WHERE email=?", (email,)).fetchone(); c.close()
        if u and check_password_hash(u["password"], pw):
            return jsonify({"ok": True, "name": u["full_names"], "email": u["email"], "role": u["role"] or "Member"})
        return jsonify({"ok": False, "error": "Invalid login"}), 401
    body='''<div class="eyebrow">Welcome Back</div><h1>Login</h1><div class="card"><label>Email</label><input class="input" id="email" value="marlonkikuyu@gmail.com"><div style="margin-top:12px"><label>Password</label><input class="input" id="pw" type="password" value="admin123"></div><button class="btn" onclick="doLogin()" style="margin-top:16px">Login</button><p id="st"></p><p style="color:#6B7280;font-size:13px">Admin: marlonkikuyu@gmail.com / admin123</p></div><script>async function doLogin(){let r=await fetch('/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('pw').value})});let j=await r.json();if(j.ok){localStorage.setItem('fig_user',j.email);localStorage.setItem('fig_name',j.name);localStorage.setItem('fig_email',j.email);localStorage.setItem('fig_role',j.role);location.href='/'}else{document.getElementById('st').textContent=j.error}}</script>'''
    return shell("Login", body)
@app.route("/admin")
def admin_page():
    body='''<div class="eyebrow">Admin</div><h1>Admin / Settings</h1><div class="card"><p>BF: 855,759 | Reserve: 250,000 | To Share: 605,759</p><div style="display:flex;gap:10px;flex-wrap:wrap"><a class="btn2" href="/download/excel">Download Excel</a><a class="btn2 gold" href="/download/shareout">Download Share-Out</a><a class="btn2" href="/register" style="background:#F3F4F6;color:#111827">Add Member</a></div></div><div class="card"><h2>Add Notification</h2><input class="input" id="nTitle" placeholder="Title"><input class="input" id="nMsg" placeholder="Message" style="margin-top:10px"><button class="btn" onclick="addN()" style="margin-top:12px">Send Notification</button><p id="nSt"></p></div><script>async function addN(){let r=await fetch('/api/notifications',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({title:document.getElementById('nTitle').value,msg:document.getElementById('nMsg').value})});let j=await r.json();document.getElementById('nSt').textContent=j.message}</script>'''
    return shell("Admin", body)
@app.route("/api/stats")
def api_stats():
    c=get_db(); rows=c.execute("SELECT project, COUNT(*) as cnt FROM users GROUP BY project").fetchall(); total=c.execute("SELECT COUNT(*) as cnt FROM users").fetchone()["cnt"]; c.close()
    bd={r["project"]: r["cnt"] for r in rows}
    return jsonify({"total_members": total, "projects_total": len(bd), "projects_breakdown": bd})
@app.route("/api/members")
def api_members():
    shares, tc, tm, rate = calc_shares()
    return jsonify({"members": shares, "total_members": len(shares), "projects_total": len(set(x["project"] for x in shares))})
@app.route("/api/shareout")
def api_shareout():
    shares, tc, tm, rate = calc_shares()
    return jsonify({"per_month_rate": rate, "total_months": tm, "total_contributions": tc, "total_shares": sum(x["share"] for x in shares), "members": len(shares)})
@app.route("/api/community", methods=["GET","POST"])
def api_community():
    c=get_db()
    if request.method=="POST":
        d=request.get_json(force=True)
        import datetime as _dt
        c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, media_type, media_data) VALUES (?,?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M"), d.get("media_type") or "", d.get("media_data") or ""))
        c.commit(); c.close(); return jsonify({"message": "Posted"})
    filt=request.args.get("filter","all"); email=request.args.get("email","")
    rows=c.execute("SELECT * FROM community_posts ORDER BY id DESC LIMIT 100").fetchall()
    posts=[]
    for p in rows:
        likes=c.execute("SELECT COUNT(*) as n FROM community_likes WHERE post_id=?", (p["id"],)).fetchone()["n"]
        reposts=c.execute("SELECT COUNT(*) as n FROM community_posts WHERE repost_of=?", (str(p["id"]),)).fetchone()["n"]
        liked=bool(c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?", (p["id"], email)).fetchone()) if email else False
        bm=bool(c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?", (p["id"], email)).fetchone()) if email else False
        coms=[dict(x) for x in c.execute("SELECT * FROM community_comments WHERE post_id=? ORDER BY id ASC", (p["id"],)).fetchall()]
        d=dict(p); d["likes"]=likes; d["reposts"]=reposts; d["liked"]=liked; d["bookmarked"]=bm; d["comments"]=coms
        d["repost_name"]=""; d["repost_msg"]=""
        if p["repost_of"]:
            orig=c.execute("SELECT * FROM community_posts WHERE id=?", (p["repost_of"],)).fetchone()
            if orig: d["repost_name"]=orig["author_name"]; d["repost_msg"]=orig["msg"]
        posts.append(d)
    if filt=="mine": posts=[x for x in posts if x["author_email"]==email]
    if filt=="saved":
        ids=[r["post_id"] for r in c.execute("SELECT post_id FROM community_bookmarks WHERE email=?", (email,)).fetchall()]
        posts=[x for x in posts if x["id"] in ids]
    c.close(); return jsonify({"posts": posts})
@app.route("/api/community/<int:pid>/like", methods=["POST"])
def api_like(pid):
    d=request.get_json(force=True) or {}; email=d.get("email") or ""
    c=get_db()
    ex=c.execute("SELECT id FROM community_likes WHERE post_id=? AND email=?", (pid, email)).fetchone()
    if ex: c.execute("DELETE FROM community_likes WHERE id=?", (ex["id"],)); msg="Unliked"
    else: c.execute("INSERT INTO community_likes (post_id,email) VALUES (?,?)", (pid, email)); msg="Liked"
    c.commit(); c.close(); return jsonify({"message": msg})
@app.route("/api/community/<int:pid>/bookmark", methods=["POST"])
def api_bookmark(pid):
    d=request.get_json(force=True) or {}; email=d.get("email") or ""
    c=get_db()
    ex=c.execute("SELECT id FROM community_bookmarks WHERE post_id=? AND email=?", (pid, email)).fetchone()
    if ex: c.execute("DELETE FROM community_bookmarks WHERE id=?", (ex["id"],)); msg="Removed from saved"
    else: c.execute("INSERT INTO community_bookmarks (post_id,email) VALUES (?,?)", (pid, email)); msg="Saved"
    c.commit(); c.close(); return jsonify({"message": msg})
@app.route("/api/community/<int:pid>/comment", methods=["POST"])
def api_comment(pid):
    d=request.get_json(force=True) or {}
    import datetime as _dt
    c=get_db(); c.execute("INSERT INTO community_comments (post_id, author_name, author_email, msg, created) VALUES (?,?,?,?,?)", (pid, d.get("name") or "Member", d.get("email") or "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Reply posted"})
@app.route("/api/community/<int:pid>/repost", methods=["POST"])
def api_repost(pid):
    d=request.get_json(force=True) or {}
    import datetime as _dt
    c=get_db(); orig=c.execute("SELECT * FROM community_posts WHERE id=?", (pid,)).fetchone()
    if not orig: c.close(); return jsonify({"error": "Not found"}), 404
    c.execute("INSERT INTO community_posts (author_name, author_email, project, msg, created, repost_of) VALUES (?,?,?,?,?,?)", (d.get("name") or "Member", d.get("email") or "", "", d.get("msg") or "Reposted", _dt.datetime.now().strftime("%d %b %Y %H:%M"), str(pid)))
    c.commit(); c.close(); return jsonify({"message": "Reposted"})
@app.route("/api/community/<int:pid>", methods=["DELETE"])
def api_del_post(pid):
    key=request.args.get("key",""); email=request.args.get("email","")
    if key!=ADMIN_KEY and email.lower()!=ADMIN_EMAIL: return jsonify({"error": "Not allowed"}), 403
    c=get_db(); c.execute("DELETE FROM community_posts WHERE id=?", (pid,)); c.execute("DELETE FROM community_comments WHERE post_id=?", (pid,)); c.commit(); c.close()
    return jsonify({"message": "Deleted"})
@app.route("/api/notifications", methods=["GET","POST"])
def api_notif():
    c=get_db()
    if request.method=="POST":
        d=request.get_json(force=True) or {}
        import datetime as _dt
        c.execute("INSERT INTO notifications (title, msg, created, target, is_read) VALUES (?,?,?,?,?)", (d.get("title") or "F.I.G", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M"), d.get("target") or "/", 0))
        c.commit(); c.close(); return jsonify({"message": "Notification sent"})
    rows=[dict(x) for x in c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 50").fetchall()]
    unread=c.execute("SELECT COUNT(*) as n FROM notifications WHERE is_read=0").fetchone()["n"]; c.close()
    return jsonify({"notifications": rows, "unread": unread})
@app.route("/api/notifications/<int:nid>/read", methods=["POST"])
def api_notif_read(nid):
    c=get_db(); c.execute("UPDATE notifications SET is_read=1 WHERE id=?", (nid,)); c.commit(); c.close(); return jsonify({"ok": True})
@app.route("/api/notifications/read", methods=["POST"])
def api_notif_read_all():
    c=get_db(); c.execute("UPDATE notifications SET is_read=1"); c.commit(); c.close(); return jsonify({"ok": True})
@app.route("/api/support", methods=["POST"])
def api_support():
    d=request.get_json(force=True) or {}
    import datetime as _dt
    c=get_db(); c.execute("INSERT INTO support_msgs (name, msg, created) VALUES (?,?,?)", (d.get("name") or "", d.get("msg") or "", _dt.datetime.now().strftime("%d %b %Y %H:%M")))
    c.commit(); c.close(); return jsonify({"message": "Message sent. We will reply on WhatsApp 0707 780 807"})
@app.route("/download/excel")
def download_excel():
    shares, tc, tm, rate = calc_shares()
    from openpyxl import Workbook
    wb=Workbook(); ws=wb.active; ws.title="Members"; ws.append(["Staff No","Full Names","Project","Email","Date Joined","Months","Contribution","Share"])
    for x in shares: ws.append([x["staff_no"], x["full_names"], x["project"], x["email"], x["month_joined"], x["months"], x["contribution"], round(x["share"],2)])
    out=io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out, mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet", as_attachment=True, download_name="FIG_Members.xlsx")
@app.route("/health")
def health(): return jsonify({"ok": True, "version": "v113-fixed"})
if __name__=="__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
