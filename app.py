from flask import Flask,request,jsonify,render_template_string,redirect,send_file
import sqlite3,os,secrets,io,re
from werkzeug.security import generate_password_hash,check_password_hash
app=Flask(__name__);DB="lonma.db"
PROJECTS=["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF-LM","TF-MT"]
PWANI_LOGO="https://africasustainabilitymatters.com/wp-content/uploads/2020/03/Pwani-logo-585x390.png"
JAVA_LOGO="https://files.startupranking.com/startup/thumb/63544_1f9d3a70b8f51acd40ff73fd3e16bdefdfa00adc_java-house_l.jpg"
SCJ_LOGO="https://bhp-plus.pl/usr/s.c.-johnson-logo.png"
HIGHCHEM_LOGO="https://directory.africa-business.com/assets/uploads/logo/highchemafrica1.png"
TRUFOODS_LOGO="https://www.viprocgeneralenterprises.co.ke/site-images/Trufoods%20Limited.jpg"
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
280346|GCB-TDs|8TH SEPT 2026|OBATIAH WEKESA MAKHANU|12848951|32350703|N/A|502370256||||||
292958|GCB-TDs|1ST APRIL 2026|FRANCIS GACHERU|4292931|9126340|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202973|TF-MT|2026|Anastacia Mwende Mutua|12584896|12571589|33067411|N/A|5772864|||||
202843|TF-MT|2023|Mourin wangui karomo|10502813|10453948|N/A|33400723|26479|||||
292954|TF-MT|2026|Christine Wangu namange|33918462|2059381|N/A|N/A|31848814|1832003833|32224611||||
202865|TF-MT|2025|Nyongesa rendson wekesa|N/A|8038054|N/A|N/A|N/A|||||
202870|TF-MT|2025|Vonter Moses Amuto|N/A|21320319|N/A|41465467|N/A|||||
202855|TF-MT|2025|Jackline Njeri chomba|N/A|N/A|N/A|N/A|N/A|||||
202856|TF-MT|2025|Elizabeth Silvia Botuba|10430483|20545758|N/A|N/A|N/A|||||
202860|TF-MT|2025|Mark Alema Mbeche|5339293|13408682|N/A|32173580|264970115|||||
202844|TF-MT|2025|purity Wambui|12475261|12472997|N/A|N/A|N/A|||||
202876|TF-MT|2024|Jane wanjiru|359820|4828287|N/A|33036142|1458214|2942546||||
292950|TF-MT|2026|Johntery mwangi|N/A|26910626|N/A|N/A|N/A|||||
202853|TF-MT|2025|Eugene Ochieng|5985386|14443973|N/A|42103832|N/A|||||
Bryton Otieno okoth|TF-MT|2026|Bryton Otieno okoth|N/A|22959540|N/A|N/A|N/A|||||
202851|TF-MT|2024|Douglas lidoli lidundu|N/A|1142024|N/A|35819089|N/A|||||
202898|TF-MT|2022|Elizabeth Kaluki mbithe|N/A|30992865|N/A|N/A|N/A|||||
202879|TF-MT|2024|Daniel musyoka|N/A|N/A|N/A|37486040|1308478||||
202847|TF-MT|2025|Esther Wanjiku|N/A|N/A|N/A|26007857|7871720||||
202857|TF-MT|2025|Brenda joy nyongesa|6565657|N/A|N/A|N/A|N/A|||||
202927|TF-MT|2026|Esther syokau mosyoki|N/A|12721635|29855331|N/A|N/A|||||
292982|TF-MT|2026|Janevick moraa|N/A|2058869|2058869|N/A|N/A|||||
202838|TF-MT|2023|Elizabeth matinde|N/A|30491044|30005457|N/A|5052470||||
Evans opiyo wahona|TF-MT|2026|Evans opiyo wahona|131709903|20868984|N/A|N/A|N/A|||||
202868|TF-MT|2025|Milka Waweru Nyambura|8483259|30808943|N/A|N/A|362101165||||
292952|TF-MT|2026|Protus Ojuma|13170537|23307688|42717879|N/A|N/A|||||
202850|TF-MT|2025|Getrude kisala|5126406|5625403|33633256|26924253|791109279|264794549||||
202881|TF-MT|2024|Melvin Mumo|N/A|10288319|N/A|39465308|N/A|||||
202878|TF-MT|2024|Brendah Achieng Gumba|N/A|10533906|N/A|N/A|391729842|392200448||||
280003|TF-MT|2026|Brian Kang'ethe|N/A|24705142|N/A|N/A|N/A|||||
280220|TF-MT|2026|Joseph Mumanyi|7936972|10003795|N/A|41229249|1849133||||
280507-TFMT|TF-MT|2026|Manase Karanja Thuo|11154721|21620654|N/A|N/A|N/A|N/A||||
202867|TF-MT|2025|Eunice Wambui|22158745|25712558|N/A|N/A|1442211376||||
292959|TF-MT|2026|Samuel onyango|N/A|13129230|N/A|860805859|N/A|N/A||||
202895|TF-MT|2014|Jane Wairimu|N/A|5981674|N/A|N/A|39323500|271722809||||
202845|TF-MT|2025|Ebby Kageha lomosi|3243910|6525191|N/A|N/A|67646|1055943||||
Rachael Gathoni wangigi|TF-MT|2026|Rachael Gathoni wangigi|8846144|N/A|N/A|N/A|851318363|851610578||||
202839|TF-MT|2025|Otieno lavenda|N/A|20680682|N/A|N/A|N/A|||||
202849|TF-MT|2025|Jacinta Apondi|N/A|22858932|N/A|N/A|N/A|N/A||||
202882|TF-MT|2023|Irene Ogutu|N/A|5772466|N/A|29341825|N/A|4057128|4198133|||
202871|TF-MT|2024|Loureen Anyango Agutu|N/A|6763274|24720221|27503464|512400592|782234653||||
202874|TF-MT|2025|Valary Chepkoech Bii|1366326|7960048|N/A|N/A|||||
Mercy Chepkemoi|TF-MT|2026|Mercy Chepkemoi|7651555|8548725|N/A|23779678|121224700|122119234||||
202846|TF-MT|2025|Willis Ogumbo othiambo|8671565|11562991|N/A|N/A|N/A|||||
202854|TF-MT|2025|Peter omoro|N/A|11131310|N/A|37130958|2302502581||||
202886|TF-MT|2023|Faith Atieno|16066182|N/A|N/A|N/A|N/A|||||
202864|TF-MT|2025|Vincent Otieno Okello|2739631|21348018|N/A|37048476|N/A|||||
202842|TF-MT|2025|Peninah awuor olang'o|N/A|13298945|N/A|28715422|264168855|264809974||||
202872|TF-MT|2024|Philip Etale|N/A|14446251|N/A|N/A|N/A|||||
280318|TF-MT|2026|Daisy chepngeno|N/A|31132323|28821106|N/A|N/A|||||
202974|TF-MT|2026|Ann ndia Gitau|N/A|20162250|N/A|N/A|101500465||||
Telvin gachanja|TF-MT|2026|Telvin gachanja|N/A|14417026|N/A|33355682|264284946|2839387||||
202880|TF-MT|2024|Scholastica kilonzi|1008033|2983637|N/A|N/A|282157||||
202899|TF-MT|2023|Daniel Mwangi maina|10787780|10058327|N/A|36946194|2643331|4350577||||
202863-TFMT|TF-MT|2023|Teresia Muthoni Kariuki|N/A|21507084|N/A||5050624|||||
Purity Opiyo Anyango|TF-MT|2026|Purity Opiyo Anyango|N/A|8213405|N/A|N/A|685497|||||
Brian Otieno Nyawanda|TF-MT|2026|Brian Otieno Nyawanda|N/A|29792914|N/A|33759788|N/A|||||
Bristone Kunani|TF-MT|2026|Bristone Kunani|N/A|10003795|N/A|N/A|N/A|||||
Monica Njoki|TF-MT|2026|Monica Njoki|N/A|23025738|N/A|N/A|N/A|||||
Mary Wangari|TF-MT|2024|Mary Wangari|N/A|23395553|N/A|3612145|5953389|5953388|2583144|||
292979|TF-MT|2026|Risper Moraa Momanyi|8730577|N/A|N/A|N/A|246730359|||||
202873|TF-MT|2023|Brian Ombwori Osese|1618384|7607080|N/A|37219432|902027|5733030||||
202889|TF-MT|2021|Naomi Jeruto Tanui|N/A|20153118|N/A|N/A|9596061|||||
202920|TF-MT|2026|Elvis Shikuku|14678081|1181476|N/A|N/A|N/A|N/A||||
70221|TF-MT|2023|Pamela Awuor Nyadodo|N/A|9554703|N/A|22793574|391122658|390515422||||
280270|TF-MT|2026|Whitney Arot Aturae|N/A|21596130|N/A||||||||
dorine Anyango Odongo|TF-MT|2026|dorine Anyango Odongo|7328824|6666068|N/A|N/A|2052600642|||||
Bartholomew Wekesa musundi|TF-MT|2026|Bartholomew Wekesa musundi|9721630|13561414|N/A|N/A|172117769|||||
Beryl Jeptoo|TF-MT|2026|Beryl Jeptoo|2253273|N/A|N/A|35017099|N/A|N/A||||
202893|TF-MT|2023|Damaris Wekesa|N/A|829543|N/A|29621541||1311904839|1311323602|||
202877|TF-MT|2025|Catherine Awino Agutu||N/A|27422318|4207822|9349719||||
202884|TF-MT|2024|Mercy Achieng Onyango|N/A|N/A|21999525|28376863|7206211|7206057||||
202888|TF-MT|2017|Jackline Kavere Ayiga|521394||23987409|5466522|111414657|111136627|112004194|||
202835|TF-MT|2024|Diana Nanjala wafula|21253105|23122140|N/A|32457447|||||
280222|TF-MT|2026|Shania Joy|N/A|N/A|13383612|N/A|N/A|N/A||||
Vallary Akinyi|TF-MT|2026|Vallary Akinyi|N/A|20065485|N/A|33716569|5059601||||
202885|TF-MT|2020|Mourine Akoth|10822795|28243742|N/A|33548098|4496868||||
202891|TF-MT|2023|Maryanne Wanjiru Kariuki|7131147|21258218|N/A|22490702|A0701169|A4404579||||
202833|TF-MT|2025|Stephen Wesonga Ouma||8615924||832827|3817366||||'''
PERIODS=[{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200 | Kaysalt 72,900 | Kanji 12,600 | HQ 15,900 | GCB-MT 69,900 | TF-WS 71,100 | TF-LM 173,100 | TF-MT 259,500 | Kenafric 96,900 | GCB-TDs 51,000 | LAB 7,800"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400 | Kanji 9,900 | HQ 14,100 | GCB-MT 56,700 | TF-WS 49,200 | TF-LM 122,400 | TF-MT 236,100 | GCB-TDs 41,100 | Higchem 30,000 | Antonia 3,600"}]
SEED_DATA=[tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
