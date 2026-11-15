from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
VERSION = "v138"
PROJECTS = ["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
PMAP = {"Antonio":"Antonia","ANTONIA":"Antonia","Antonia":"Antonia","GCB-MT":"GCB-MT","GCB MT":"GCB-MT","GCB":"GCB-MT","GCB-Ws":"GCB-TDs","GCB Ws":"GCB-TDs","GCB TDS":"GCB-TDs","GCB-TDs":"GCB-TDs","GCB-TDS":"GCB-TDs","GCB WS":"GCB-TDs","Higchem":"Higchem","HIGHCHEM":"Higchem","HQ":"HQ","Kanji":"Kanji","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","Java House":"Java House","JAVA":"Java House","Java":"Java House","Pwani Oil Products":"Pwani Oil Products","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","SC Johnson":"SC Johnson","SJ Johnson":"SC Johnson","JOHNSON":"SC Johnson","Johnson":"SC Johnson","SJ":"SC Johnson","SCJohnson":"SC Johnson","TF WSL":"TF WSL","TF WS":"TF WSL","TF-WS":"TF WSL","TF":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
def norm_project(p):
    p=(p or "").strip()
    if p in PMAP: return PMAP[p]
    up=" ".join(p.upper().split())
    if up in PMAP: return PMAP[up]
    return PMAP.get(p.title(), p or "Pwani Oil Products")
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
BF = 855759
RESERVE = 250000
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
10405|Pwani Oil Products|01/03/2025|Diana Atieno Oduor|NA|4722494|757617564|28078423|N/A|N/A|370702896|21506184|Samantha malia Achieng
202749|Pwani Oil Products|01/03/2025|Celine Nasimiyu Wamalwa|N/A|8784757|NA|28990208|William Musungu|Moses Musungu|Bryton Musungu|N/A|N/A
292976|Pwani Oil Products|01/04/2026|Belinda chemtai|N/A|4722288|N/A|N/A|372315084|182018971|N/A|N/A|N/A
202702|Pwani Oil Products|01/05/2025|Betty Akinyi Namamba|Fabians Namamba|Janet Atieno|N/A|N/A|N/A|N/A|N/A|N/A|N/A
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
202607|GCB-MT|1st Dec 2019|Mary ngotah|||6514355|5647988|5029251|821770||
202602|GCB-MT|19th Dec|Hillary nzive kasiva|mumo|Christabel||33080053|5523041707|552304792||
202609|GCB-MT|11th Nov|Joan Atieno Odhiambo||Roseline|9007625||710552151||||
202612|GCB-MT|2025 November|purity ndunda|ndunda|Jemima|20451178|56342190||3820546|||
280322|GCB-MT|01/08/2021|Nelson karani|Patrick|Martha|20035038|35833677|||||
292916|GCB-MT|1st Aug 2026|Grace muthoni chege|Benson|Elizabeth||31744265|3820546||||
202606|GCB-MT|11th Nov 2022|peter omondi|maurice|Teressa|||||||
202613|GCB-MT|1st jan 2026|Joan wambui|none|hannah njeri|6431600||3954756|4681696|||
292962|GCB-MT|1st September 2026|Stephen Mwose|Antony|Magdaline|4916541|37679067|Brielle Mbithe||||
280265|GCB-MT|1st July 2026|Caroline Maina|Maina|Jane|8812236||||||
202610|GCB-MT|15th November 2025|Mercy Wambui Njer|none|none|21785795||2739159||||
292964|GCB-MT|1st june 2026|Mary Mbinya|Musyoka|Ruth|9224221|34123070|0212336591||||
280315|GCB-MT|1st Aug 2026|Dorcas Mukenyi|Mwanzia|Joyce||22228902|Geoffrey||||
202926|GCB-MT|1st Jan ,2026|Stephen Mwalimu|Mwalimu|Damaris|21459928|N/A|||||
202604|GCB-MT|14th September 2020|Dennis Mbindyo Mwamuli|Alfred Mwamuli|Catherine Monica|||||||
280321|GCB-MT|19th August 2026|Geoffrey Matata Mbeva||Rosina Beth Mbeva|73696420|32512477|0262718439|0262718432|0265294261||
202611|GCB-MT|1st Dec 2025|Robert Muthui Matheka|Julius Matheka|Jedidah Matheka|||||||
202601|GCB-MT|1st Feb 2011|Evelyne Mpinda Kinyua|||Sophia Mbiriga|8351177|481336|5167251|||
202615|GCB-MT|4th April 2019|Emiliana mwanaidi||Diana mwandisha|8464065|22582763|0572301813|5170301|||
202628|HQ|2015|JANEDRIX AKINYI SADAKA|N/A|JOYCE SAKAKA||N/A|JAMES SADAKSA|JOYBLESSING|||
CELESTINE ATIENO SADAKA|HQ|2015|CELESTINE ATIENO SADAKA|N/A|JOYCE SAKAKA||N/A|LINCOL|IAN|ANDREY||
280314|HQ|AUGUST 1ST 2026|LAZARUS OKECHI|NICODEMUS OGOTI|MARY AJIAMBO||PURITY KABATI|AZARIA AJIAMBO||||
PATRIC TITO|HQ|2020|PATRIC TITO|TITO NZONGA|FELISTERS TITO||FRIDAH KARIMI|TIFFANY TITO|BARAKA TITO|||
292930|HQ|AUGUST 1ST 2026|EDDY NYANGORI|JOHN NYANGORI|HELLENE ACHIENG||N/A|||||
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
202618|GCB-TDs|1ST JULY 2023|JOACHIM BACHWA BACHWA|13606151|23557862||||||
202973|TF-MT|Jan-26|Anastacia Mwende Mutua|12584896|12571589|33067411|N/A|5772864||||
202857|TF-MT|2025|Brenda joy nyongesa|6565657||||||||
Bryton Otieno okoth|TF-MT|Nov-26|Bryton Otieno okoth|N/A|22959540||||||||
292954|TF-MT|Feb-26|Christine Wangu namange|33918462|2059381|N/A|N/A|31848814|1832003833|32224611||
202879|TF-MT|2024|Daniel musyoka|N/A|N/A|N/A|37486040|1308478||||
202899|TF-MT|2023|Daniel Mwangi maina|10787780|10058327|N/A|36946194|2643331|4350577|||
202851|TF-MT|2024|Douglas lidoli lidundu|N/A|1142024|N/A|35819089|N/A||||
202898|TF-MT|2022|Elizabeth Kaluki mbithe|N/A|30992865||||||||
202838|TF-MT|2023|Elizabeth matinde|N/A|30491044|30005457|N/A|5052470||||
202856|TF-MT|2025|Elizabeth Silvia Botuba|10430483|20545758||||||||
202927|TF-MT|Jan-26|Esther syokau mosyoki|N/A|12721635|29855331||||||||
202847|TF-MT|2025|Esther Wanjiku|N/A|N/A|N/A|26007857|7871720||||
202853|TF-MT|2025|Eugene Ochieng|5985386|14443973|N/A|42103832|N/A||||
202886|TF-MT|2023|Faith Atieno|16066182||||||||
202850|TF-MT|2025|Getrude kisala|5126406|5625403|33633256|26924253|791109279|264794549||
202855|TF-MT|2025|Jackline Njeri chomba|N/A|N/A|N/A|N/A|N/A||||
292982|TF-MT|Feb-26|Janevick moraa|N/A|2058869|2058869||||||||
202860|TF-MT|2025|Mark Alema Mbeche|5339293|13408682|N/A|32173580|264970115||||
Mary Wangari TFMT|TF-MT|2024|Mary Wangari|N/A|23395553|N/A|3612145|5953389|5953388|2583144||
202881|TF-MT|2024|Melvin Mumo|N/A|10288319|N/A|39465308|N/A||||
202868|TF-MT|2025|Milka Waweru Nyambura|8483259|30808943||||||||
202843|TF-MT|2023|Mourin wangui karomo|10502813|10453948|N/A|33400723|26479||||
202865|TF-MT|2025|Nyongesa rendson wekesa|N/A|8038054||||||||
202842|TF-MT|2025|Peninah awuor olang'o|N/A|13298945|N/A|28715422|264168855|264809974||
202854|TF-MT|2025|Peter omoro|N/A|11131310|N/A|37130958|2302502581||||
202872|TF-MT|2024|Philip Etale|N/A|14446251||||||||
292952|TF-MT|Feb-26|Protus Ojuma|13170537|23307688|42717879||||||||
Purity Opiyo Anyango|TF-MT|Nov-26|Purity Opiyo Anyango|N/A|8213405|N/A|N/A|685497||||
202844|TF-MT|2025|purity Wambui|12475261|12472997||||||||
202880|TF-MT|2024|Scholastica kilonzi|1008033|2983637||||||||
202833|TF-MT|2025|Stephen Wesonga Ouma||8615924|||832827|3817366|||
Telvin gachanja|TF-MT|Jun-26|Telvin gachanja|N/A|14417026|N/A|33355682|264284946|2839387||
202863TFMT|TF-MT|2023|Teresia Muthoni Kariuki|N/A|21507084|N/A||5050624||||
202864|TF-MT|2025|Vincent Otieno Okello|2739631|21348018|N/A|37048476|N/A||||
202870|TF-MT|2025|Vonter Moses Amuto|N/A|21320319|N/A|41465467|N/A||||
202846|TF-MT|2025|Willis Ogumbo othiambo|8671565|11562991||||||||
202876|TF-MT|2024|Jane wanjiru|359820|4828287|N/A|33036142|1458214|2942546||
202861|TF-MT|Mar-26|Ann Njoroge||||||||
202963|TF-MT|Oct-26|Fridah Gastaiti||||||||
Beryl Jeptoo|TF-MT|Jul-26|Beryl Jeptoo|2253273|N/A|N/A|35017099|N/A||||
202871|TF-MT|2024|Loureen Anyango Agutu|N/A|6763274|24720221|27503464|512400592|782234653||
202891|TF-MT|2023|Maryanne Wanjiru Kariuki|7131147|21258218|N/A|22490702|A0701169|A4404579||
Mercy Chepkemoi|TF-MT|2025|Mercy Chepkemoi|7651555|8548725|NA|23779678|121224700|122119234||
202885|TF-MT|2020|Mourine Akoth|10822795|28243742|NA|33548098|4496868||||
280222|TF-MT|Apr-26|Shania Joy|N/A|N/A|13383612|N/A|N/A||||
202874|TF-MT|2025|Valary Chepkoech Bii|1366326|7960048||||||||
Vallary Akinyi|TF-MT|Jul-26|Vallary Akinyi|NA|20065485|NA|33716569|5059601||||
202878|TF-MT|2024|Brendah Achieng Gumba|N/A|10533906|N/A|N/A|391729842|392200448||
280003|TF-MT|Jun-26|Brian Kang'ethe|N/A|24705142|N/A|N/A|N/A||||
202877|TF-MT|2025|Catherine Awino Agutu||N/A|27422318|4207822|9349719|||
202893|TF-MT|2023|Damaris Wekesa|N/A|829543|N/A|29621541||1311904839|1311323602||
Dorine Anyango Odongo|TF-MT|Nov-26|Dorine Anyango Odongo|7328824|6666068|N/A|N/A|2052600642||||
202845|TF-MT|2025|Ebby Kageha lomosi|3243910|6525191|N/A|N/A|67646|1055943||
202867|TF-MT|2025|Eunice Wambui|22158745|25712558||||||||
202895|TF-MT|2014|Jane Wairimu|N/A|5981674|NA|NA|39323500|271722809||
280220|TF-MT|Mar-26|Joseph Mumanyi|7936972|10003795|NL|41229249|1849133||||
280507TFMT|TF-MT|Nov-26|Manase Karanja Thuo|11154721|21620654|N/A|N/A|N/A||||
70221|TF-MT|2023|Pamela Awuor Nyadodo|N/A|9554703|N/A|22793574|391122658|390515422||
Bartholomew Wekesa musundi|TF-MT|Nov-26|Bartholomew Wekesa musundi|9721630|13561414|N/A|N/A|172117769||||
Rachael Gathoni wangigi|TF-MT|Oct-26|Rachael Gathoni wangigi|8846144|N/A|N/A|N/A|851318363|851610578||
292979|TF-MT|Jul-26|Risper Moraa Momanyi|8730577|N/A|N/A|N/A|246730359||||
292959|TF-MT|Jul-26|Samuel onyango|N/A|13129230|N/A|860805859|N/A||||
202890|TF-MT|2023|John Mwangi||||||||
280270|TF-MT|Jul-26|Whitney Arot Aturae|N/A|21596130||||||||
202873|TF-MT|2023|Brian Ombwori Osese|1618384|7607080|N/A|37219432|902027|5733030||
202835|TF-MT|2024|Diana Nanjala wafula|21253105|23122140|N/A|32457447||||||||
202920|TF-MT|2025|Elvis Shikuku|14678081|1181476|N/A|N/A|N/A||||
202882|TF-MT|2023|Irene Ogutu|NA|5772466|N/A|29341825|N/A|4057128|4198133||
202859|TF-MT|Jan-26|Emma Watindi||||||||
202849|TF-MT|2025|Jacinta Apondi|N/A|22858932|N/A|N/A|N/A||||
202888|TF-MT|2017|Jackline Kavere Ayiga|521394||23987409|5466522|111414657|111136627|112004194||
202884|TF-MT|2024|Mercy Achieng Onyango|NA|NA|21999525|28376863|7206211|7206057||
202889|TF-MT|2021|Naomi Jeruto Tanui|N/A|20153118|N/A|N/A|9596061||||
202839|TF-MT|2025|Otieno lavenda|N/A|20680682||||||||
202914|TF WSL|20-Jan-25|SAID ROSELINE HERI||1319025||9765327|4408202|7758933|7108428||
202906|TF WSL|27-Mar-25|JECINTA KARANJA|8483221|11114948||30461200|1358036|614595|||
202905|TF WSL|05-Feb-25|MARY ATIENO||14438209||001432321|4898710|||
202915|TF WSL|13-Jan-25|PAULINE MURATHI|20964177|23236444|||||
202916|TF WSL|27-Jan-25|ANN NJERI KAREIYA|Deceased|6106608||23524787|9901560|||
202913|TF WSL|13-Jan-25|TABITHA WANJIKU|8040754|10893197||33095213|37220833|||
202917|TF WSL|13-Jan-25|PRUDENCE ACHIENG WANYANGU||22482407||37155644|||
292943|TF WSL|15-Jan-26|LINDA NALIAKA JUMA|21927102|20475201||None|9655625|Notification: 6031104|||
202908|TF WSL|12-Sep-25|PASCALINE NJOKI|Deceased|23429425||645865||||
202910|TF WSL|16-Oct-25|LUCY NYAMBURA||14495721|||||
292977|TF WSL|18-Jul-05|DIANA MUSE|5675695|5301379|||||
202907|TF WSL|22-Jul-26|JANET WAIRIMU|10767868|13507411||3868681||||
280293|TF WSL|13-Jul-26|CATHERINE MUKAMI|16005886|16022069||24041649|361716972|Notification: 5810997|||'''
PERIODS = [{"label":"Oct 2024 - Dec 2025","total":1404000,"beneficiaries":463000,"fares":31625,"detail":"Pwani 310,500 | Java 123,600 | SC Johnson 139,200"},{"label":"Dec 2025 - Nov 2026","total":991100,"beneficiaries":379075,"fares":32100,"expenditures":427341,"detail":"Pwani 220,200 | Java House 106,200 | SC Johnson 101,400"}]
BENEFICIARIES2 = [("Oct 2024 - Dec 2025","Mary Ngota","GCB","Dad-Death","01/11/2024",30000),("Dec 2025 - Nov 2026","ROSE Lumonya SAIDI","POPL","Death-Father","01/12/2025",40000),("Dec 2025 - Nov 2026","Sherine Atieno Otieno","Antonia","Mother-Death","Nov 2026",40000)]
FARES2 = [("Oct 2024 - Dec 2025","Peter Ikegu","0704886421",1000),("Dec 2025 - Nov 2026","EUNICE MAKONA","0714910135",1200)]
MONTHLY_INDIVIDUAL = []
SEED_DATA = [tuple((l.split('|')+['']*13)[:13]) for l in SEED_TXT.strip().splitlines()]
def clean(v):
    if v is None: return ""
    s=str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL","NIL"): return ""
    if "will give" in s.lower(): return ""
    if "will provide" in s.lower(): return ""
    if "notification:" in s.lower(): return s.split(":",1)[1].strip()
    return s
def make_email(n, staff):
    p=[x for x in n.lower().replace(".","").split() if x.isalpha()]
    return f"{p[0]}.{p[-1]}@figbrands.co.ke" if len(p)>=2 else f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
def parse_join(s):
    if not s: return None
    s=str(s).strip().lower()
    months={"jan":1,"feb":2,"mar":3,"apr":4,"may":5,"jun":6,"jul":7,"aug":8,"sep":9,"oct":10,"nov":11,"dec":12,"january":1,"february":2,"march":3,"april":4,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12}
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
    sy,sm=PERIOD_START; ey,em=PERIOD_END
    p=parse_join(j)
    if p and (p[0],p[1])>(sy,sm): sy,sm=p
    if (sy,sm)>(ey,em): return 0
    return (ey-sy)*12+(em-sm)+1
def get_db():
    c=sqlite3.connect(DB,timeout=10,check_same_thread=False,isolation_level=None); c.row_factory=sqlite3.Row
    try: c.execute("PRAGMA journal_mode=WAL;"); c.execute("PRAGMA busy_timeout=10000;")
    except: pass
    return c
def calc_shares():
    c=get_db()
    try: rows=c.execute("SELECT id,staff_no,full_names,project,email,month_joined FROM users WHERE email != ? ORDER BY full_names",(ADMIN_EMAIL,)).fetchall()
    finally: c.close()
    out=[]
    for r in rows:
        mo=months_active(r["month_joined"])
        out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","months":mo,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0})
    tm=sum(x["months"] for x in out); tc=sum(x["contribution"] for x in out); rate=DISTRIBUTABLE/tm if tm else 0
    for x in out: x["per_month"]=round(rate,2); x["share"]=round(x["months"]*rate,2)
    diff=round(DISTRIBUTABLE-sum(x["share"] for x in out),2)
    if out and diff!=0:
        out.sort(key=lambda x: x["share"],reverse=True); out[0]["share"]=round(out[0]["share"]+diff,2)
    out.sort(key=lambda x: x["share"],reverse=True)
    return out,tc,tm,rate
def add_user(c,staff,names,project,month,father="",mother="",guardian="",spouse="",k1="",k2="",k3="",k4="",k5="",photo=""):
    staff=clean(staff); names=clean(names); project=norm_project(project)
    if not staff or not names: return False
    if c.execute("SELECT id FROM users WHERE staff_no=?",(staff,)).fetchone(): return False
    if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(names,)).fetchone(): return False
    email=make_email(names,staff)
    if c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone(): email=f"member.{staff}@figbrands.co.ke"
    vals=(staff,names,project,email,generate_password_hash(staff),"fig_"+secrets.token_hex(12),clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),photo)
    c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    return True
def init_db():
    c=get_db()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS beneficiaries2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, project TEXT, reason TEXT, date_str TEXT, amount REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS fares2 (id INTEGER PRIMARY KEY AUTOINCREMENT, period TEXT, name TEXT, phone TEXT, amount REAL)')
    c.execute('CREATE TABLE IF NOT EXISTS community (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS friends (id INTEGER PRIMARY KEY AUTOINCREMENT, from_name TEXT, to_name TEXT, status TEXT DEFAULT "pending", created TEXT)')
    for col in ["month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5","photo"]:
        try: c.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT")
        except: pass
    for col,typ in [("target","TEXT"),("is_read","INTEGER DEFAULT 0")]:
        try: c.execute(f"ALTER TABLE notifications ADD COLUMN {col} {typ}")
        except: pass
    for col,typ in [("media_type","TEXT"),("media","TEXT"),("likes","INTEGER DEFAULT 0")]:
        try: c.execute(f"ALTER TABLE community ADD COLUMN {col} {typ}")
        except: pass
    for r in c.execute("SELECT id, project FROM users").fetchall():
        np=norm_project(r["project"])
        if np!=r["project"]: c.execute("UPDATE users SET project=? WHERE id=?",(np,r["id"]))
    if not c.execute("SELECT id FROM users WHERE email=?",(ADMIN_EMAIL,)).fetchone():
        c.execute("INSERT INTO users (staff_no,full_names,project,email,password,role,phone,api_key,is_protected) VALUES (?,?,?,?,?,?,?,?,?)",("HQ/001","System Administrator","HQ",ADMIN_EMAIL,generate_password_hash(ADMIN_PASS),"Admin","0700000000",ADMIN_KEY,1))
    added=0
    for r in SEED_DATA:
        staff,proj_raw,month,names,father,mother,guardian,spouse,k1,k2,k3,k4,k5=r
        project=norm_project(proj_raw)
        ex=c.execute("SELECT id FROM users WHERE staff_no=?",(clean(staff),)).fetchone()
        if ex:
            c.execute("UPDATE users SET full_names=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE staff_no=?",(clean(names),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),clean(staff))); continue
        ex2=c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(clean(names),)).fetchone()
        if ex2:
            c.execute("UPDATE users SET staff_no=?,project=?,month_joined=?,father_id=?,mother_id=?,guardian_id=?,spouse_id=?,kid1=?,kid2=?,kid3=?,kid4=?,kid5=? WHERE id=?",(clean(staff),project,clean(month),clean(father),clean(mother),clean(guardian),clean(spouse),clean(k1),clean(k2),clean(k3),clean(k4),clean(k5),ex2["id"])); continue
        if add_user(c,staff,names,project,month,father,mother,guardian,spouse,k1,k2,k3,k4,k5): added+=1
    c.commit(); c.close(); print(f"{VERSION} seeded {len(SEED_DATA)} added {added}")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); return r
@app.route("/favicon.ico")
def favicon():
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="14" fill="#0A1F33"/><text x="32" y="42" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#C9A86A" text-anchor="middle">FIG</text></svg>'
    return svg,200,{"Content-Type":"image/svg+xml"}
def shell(title,body):
    return render_template_string('''<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width,initial-scale=1"><title>'''+title+''' - F.I.G BRANDS</title><style>:root{--navy:#0A1F33;--gold:#C9A86A;--line:#E9E2D6;--bg:#F7F5F0}*{box-sizing:border-box}body{font-family:Inter,system-ui,sans-serif;background:var(--bg);margin:0;padding-bottom:120px}h1,h2,h3{color:var(--navy)}.top{height:64px;background:var(--navy);color:#fff;display:flex;align-items:center;gap:12px;padding:0 16px;position:sticky;top:0;z-index:20;border-bottom:2px solid var(--gold)}.logo{background:#fff;color:var(--navy);border-radius:12px;padding:7px 10px;font-weight:700}.toplinks{background:#fff;border-bottom:1px solid var(--line);padding:11px 16px;display:flex;gap:18px;flex-wrap:wrap}.toplinks a{color:var(--navy);text-decoration:none;font-size:13px;font-weight:600}.page{max-width:1080px;margin:auto;padding:22px 16px}.card{background:#fff;border:1px solid var(--line);border-radius:20px;padding:20px;margin-bottom:14px}.input{width:100%;height:46px;border:1px solid #D9D0BF;border-radius:12px;padding:0 13px}.btn{width:100%;height:48px;background:var(--navy);color:#fff;border:0;border-radius:12px;font-weight:700;cursor:pointer}.btn2{display:inline-block;background:var(--navy);color:#fff;padding:11px 16px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}.btn2.gold{background:var(--gold);color:var(--navy)}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}.kpi{background:#fff;border:1px solid var(--line);border-radius:20px;padding:18px}.hero{background:linear-gradient(135deg,#0A1F33,#122F4A 58%,#0E6B4A);color:#fff;border-radius:22px;padding:24px}.nav{position:fixed;left:16px;right:16px;bottom:20px;height:64px;background:rgba(10,31,51,.92);border-radius:999px;display:flex;z-index:30;padding:6px}.nav a{flex:1;color:#fff;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:700}.row{display:flex;justify-content:space-between;gap:12px;padding:13px 2px;border-bottom:1px solid #F1EDE3}table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid #EEEBE0;text-align:left}.num{text-align:right}.pill{display:inline-block;background:#F3EDDD;padding:4px 10px;border-radius:999px;font-size:11px;font-weight:700}.chip{display:inline-block;border:1px solid #E9E2D6;background:#fff;border-radius:999px;padding:8px 12px;font-size:13px;font-weight:600;cursor:pointer}.chip.on{background:#0A1F33;color:#fff}.postimg{width:100%;border-radius:14px;margin-top:10px;max-height:420px;object-fit:cover}.postvideo{width:100%;border-radius:14px;margin-top:10px;max-height:420px;background:#000}.popup{position:fixed;inset:0;background:rgba(10,31,51,.5);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:#fff;width:100%;max-width:520px;border-radius:22px 22px 0 0;padding:20px;max-height:86vh;overflow:auto}@media(max-width:640px){.grid{grid-template-columns:1fr}}</style></head><body><div class="top"><div class="logo">FIG</div><div><b>F.I.G BRANDS</b><div style="font-size:9px;letter-spacing:.28em;color:var(--gold)">WELFARE SYSTEM v138</div></div><div style="margin-left:auto;display:flex;gap:8px"><button onclick="openBell()" style="border-radius:999px;width:40px;height:40px">🔔</button><button onclick="openSupport()" style="border-radius:999px;width:40px;height:40px">💬</button></div></div><div class="toplinks"><a href="/">Overview</a><a href="/members">Members</a><a href="/register">Register</a><a href="/shareout">Share-Out</a><a href="/breakdown2">History</a><a href="/community">Community</a><a href="/friends">Friends</a><a href="/terms">Terms</a><a href="/admin">Admin</a></div><div class="page">'''+body+'''</div><div class="popup" id="bellPopup" onclick="if(event.target===this)closeBell()"><div class="pop"><b>Notifications</b><div id="notifList"></div><button class="btn" onclick="markRead()" style="margin-top:12px">Mark all as read</button></div></div><div class="popup" id="supportPopup" onclick="if(event.target===this)closeSupport()"><div class="pop"><b>Contact Support</b><p><a href="https://wa.me/254707780807" target="_blank">WhatsApp 0707 780 807</a> · <a href="mailto:info@figbrands.co.ke">info@figbrands.co.ke</a></p><input class="input" id="supName" placeholder="Your name"><textarea id="supMsg" class="input" style="height:96px;margin-top:12px" placeholder="Message"></textarea><button class="btn" onclick="sendSupport()" style="margin-top:14px">Send</button><p id="supStatus"></p></div></div><nav class="nav"><a href="/">Home</a><a href="/members">Members</a><a href="/community">Community</a><a href="/friends">Friends</a><a href="/register">Add</a></nav><script>async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();document.getElementById('notifList').innerHTML=d.notifications.map(n=>'<div style="padding:10px 0;border-bottom:1px solid #eee"><b>'+n.title+'</b><div>'+n.msg+'</div></div>').join('')||'No notifications'}function closeBell(){document.getElementById('bellPopup').classList.remove('show')}async function markRead(){await fetch('/api/notifications/read',{method:'POST'});closeBell()}function openSupport(){document.getElementById('supportPopup').classList.add('show')}function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}</script></body></html>''')
@app.route("/")
def home():
    body='''<h1>Overview</h1><p>Balance brought forward, less KES 250,000 retained — shared fairly, per month.</p><div class="grid"><div class="kpi"><div>Total Members</div><h2 id="total">0</h2></div><div class="kpi"><div>Projects</div><h2 id="projCount">0</h2></div></div><div class="hero" style="margin-top:14px"><h1>KES 855,759</h1><p>KES 605,759 to share · KES 250,000 retained</p></div><div class="grid" style="margin-top:14px"><div class="kpi"><div>Amount to Share</div><h2>KES 605,759</h2></div><div class="kpi"><div>Retained</div><h2>KES 250,000</h2></div><div class="kpi"><div>Value of One Month</div><h2 id="oneMonth">-</h2><div id="oneMonthNote"></div></div></div><div class="card" style="margin-top:14px"><h2>Death Benefit: Member 100,000 · Spouse 50,000 · Child 40,000 · Parents 40,000</h2><p>Loss of Earning: 50% of basic pay, up to KES 20,000, after 10 days unable to work due to injury at work. Contribution: KES 300 monthly.</p><a class="btn2" href="/terms">Read Full Terms</a></div><div class="card"><h2>Project Distribution</h2><div id="breakdown"></div></div><script>async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;let h='';Object.keys(d.projects_breakdown).sort().forEach(k=>{h+='<div class="row"><b>'+k+'</b><span>'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h;let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='605,759 / '+s.total_months+' months';}load();</script>'''
    return shell("Overview",body)
@app.route("/terms")
def terms_page():
    body='''<h1>Terms &amp; Policies</h1><p>F.I.G Brands Welfare — presented by Marlon.</p><div class="card"><h2>Death Benefits</h2><table><tr><th>Beneficiary</th><th>Death Benefit</th></tr><tr><td>Member</td><td>KES 100,000</td></tr><tr><td>Spouse</td><td>KES 50,000</td></tr><tr><td>Child</td><td>KES 40,000</td></tr><tr><td>Parents</td><td>KES 40,000</td></tr></table><p>Spouse must be registered. Child: birth certificate required. Parents: cover applies only to principal member. Birth certificate + parent ID required. No biological parents: may nominate one guardian. Payment upon proof of demise.</p></div><div class="card"><h2>Loss of Earning</h2><p>50% of basic pay, max KES 20,000, after 10 days unable to work due to injury at work. Paid at end of month.</p></div><div class="card"><h2>Contribution</h2><p>KES 300 monthly, deducted from pay.</p></div><div class="card"><h2>Management</h2><p>Committee elected by all members. Every project must have at least one member on board.</p></div><div class="card"><h2>Disbursement</h2><p>Death: within 2 days upon death notification. Incapacitation: end of month.</p></div><div class="card"><h2>Year-End</h2><p>Minimum balance KES 250,000 at year end. Excess shared only among current active members. FIG Year-End 30 November. Audited accounts in FACES family group by 20 December.</p></div><div class="card"><h2>Officials</h2><p>Marlon K. Ang'undu - Chairman - 0707 780 807 - marlonkikuyu@gmail.com<br>Mary Ngotah - Gold Crown Beverage - 0719 203 286<br>Celestine Ouko - SC Johnsons - 0725 543 224<br>Irene Wamuyu - Nairobi Java - 0719 606 834<br>Jonathan Mutunga - Last Mile Trufoods - 0719 555 326</p></div>'''
    return shell("Terms",body)
@app.route("/policies")
def policies_page(): return redirect("/terms")
@app.route("/breakdown")
def breakdown_page(): return redirect("/breakdown2")
@app.route("/breakdown2")
def breakdown2_page():
    h="<h1>Full History</h1>"
    for p in PERIODS: h+=f"<div class='card'><h3>{p['label']}</h3><div class='row'><span>Contributions</span><b>KES {p.get('total',0):,}</b></div><div class='row'><span>Beneficiaries</span><b>KES {p.get('beneficiaries',0):,}</b></div><div class='row'><span>Fares</span><b>KES {p.get('fares',0):,}</b></div><p>{p.get('detail','')}</p></div>"
    h+="<div class='card'><h2>Beneficiaries</h2>"
    for per,n,pr,r2,d,a in BENEFICIARIES2: h+=f"<div class='row'><span><b>{n}</b> {per} {pr} {r2} {d}</span><b>KES {a:,}</b></div>"
    h+=f"<div class='row'><b>Total</b><b>KES {sum(x[5] for x in BENEFICIARIES2):,}</b></div></div><div class='card'><h2>Fares</h2>"
    for per,n,ph,a in FARES2: h+=f"<div class='row'><span><b>{n}</b> {per} {ph}</span><b>KES {a:,}</b></div>"
    h+=f"<div class='row'><b>Total</b><b>KES {sum(x[3] for x in FARES2):,}</b></div></div>"
    return shell("History",h)
@app.route("/shareout")
def shareout_page():
    shares,total_contrib,total_months,per_month_rate=calc_shares(); total_shares=sum(x["share"] for x in shares)
    h=f"<h1>Share-Out</h1><div class='hero'><h1>KES 605,759</h1><p>1 month = KES {per_month_rate:,.2f} · Shares KES {total_shares:,.2f} + Retained 250,000 = BF 855,759</p></div><div class='grid' style='margin-top:14px'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{total_months}</h2></div><div class='kpi'><div>Contributions</div><h2>KES {total_contrib:,}</h2></div><div class='kpi'><div>Total Shares</div><h2>KES {total_shares:,.2f}</h2></div></div>"
    h+='''<div class="card"><h2>Member Share-Out Schedule</h2><a class="btn2 gold" href="/download/shareout">Download Excel</a><input class="input" id="q" placeholder="Search by name, staff or project" oninput="fil()" style="margin:14px 0"><div style="overflow:auto"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th class="num">Months</th><th class="num">Contribution</th><th class="num">Share</th></tr><tbody id="shareBody">'''
    for i,x in enumerate(shares,1): h+=f"<tr data-search='{(x['full_names']+' '+x['staff_no']+' '+x['project']).lower()}'><td>{i}</td><td><b>{x['full_names']}</b><div>{x['staff_no']} {x['email']}</div></td><td><span class='pill'>{x['project']}</span></td><td>{x['month_joined'] or '-'}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>"
    h+="</tbody></table></div></div><script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(r=>{r.style.display=r.getAttribute('data-search').includes(q)?'':'none'})}</script>"
    return shell("Share-Out",h)
@app.route("/download/shareout")
def download_shareout():
    shares,total_contrib,total_months,per_month_rate=calc_shares()
    from openpyxl import Workbook
    from openpyxl.styles import Font,PatternFill,Alignment
    wb=Workbook(); ws=wb.active; ws.title="Share-Out"
    ws.append(["F.I.G BRANDS WELFARE - SHARE-OUT SCHEDULE"]); ws.append(["BF less 250,000 shared per month of contributions"])
    ws.append([f"BF: {BF:,} | Retained: {RESERVE:,} | To Share: {DISTRIBUTABLE:,} | Total Months: {total_months} | Value of One Month: {per_month_rate:,.2f} | Total Contributions: {total_contrib:,}"]); ws.append([])
    ws.append(["#","Staff No","Full Names","Project","Date Joined","Months Contributed","Contribution (Months x 300)","Share Payable"])
    for c in ws[5]: c.font=Font(bold=True,color="FFFFFF"); c.fill=PatternFill("solid",fgColor="0A1F33"); c.alignment=Alignment(horizontal="center",vertical="center")
    for i,x in enumerate(shares,1): ws.append([i,x["staff_no"],x["full_names"],x["project"],x["month_joined"],x["months"],x["contribution"],round(x["share"],2)])
    ws.append([]); ws.append(["","","","","","TOTAL",total_contrib,round(sum(x["share"] for x in shares),2)]); ws.append(["","","","","","RETAINED IN ACCOUNT","",RESERVE]); ws.append(["","","","","","BALANCE BROUGHT FORWARD","",round(sum(x["share"] for x in shares),2)+RESERVE])
    ws.freeze_panes="A6"; ws.auto_filter.ref=ws.dimensions
    for col,w in zip("ABCDEFGH",[6,14,30,22,14,18,20,20]): ws.column_dimensions[col].width=w
    out=io.BytesIO(); wb.save(out); out.seek(0)
    return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="FIG_BRANDS_Share_Out_Schedule.xlsx")
@app.route("/members")
def members_page():
    body='''<h1>Members</h1><p id="memberCountLabel"></p><div class="card"><div style="display:flex;gap:10px;flex-wrap:wrap"><input class="input" id="q" placeholder="Search by name, staff, project" oninput="fil()" style="flex:2;min-width:200px"><select class="input" id="projFilter" onchange="fil()" style="flex:1;min-width:160px"><option value="All Projects">All Projects</option></select></div><div id="list" style="margin-top:14px"></div><a class="btn2" href="/download/excel">Download Excel</a></div><script>let all=[];async function load(){let r=await fetch('/api/stats');let d=await r.json();document.getElementById('memberCountLabel').textContent=d.total_members+' members';let sel=document.getElementById('projFilter');sel.innerHTML='<option value="All Projects">All Projects ('+d.total_members+')</option>';(d.projects||[]).forEach(p=>{let o=document.createElement('option');o.value=p;o.textContent=p+' ('+(d.projects_breakdown[p]||0)+')';sel.appendChild(o)});let r2=await fetch('/api/members');let dd=await r2.json();all=dd.members;render(all)}function row(l,v){return '<div class="row"><span>'+l+'</span><b>'+(v||'-')+'</b></div>'}function render(l){let h='';l.forEach(m=>{let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(x=>x).join(', ')||'-';h+='<div class="card"><div style="display:flex;justify-content:space-between"><div><b>'+m.full_names+'</b><div>'+m.email+'</div></div><span class="pill">'+m.project+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID',m.guardian_id)+row('Spouse ID',m.spouse_id)+row('Kids Birth Certs',kids)+'<div style="margin-top:12px"><button class="btn2 gold" onclick="addF(\\''+m.full_names.replace(/'/g,'')+'\\')">+ Add Friend</button></div></div>'});document.getElementById('list').innerHTML=h||'No members found'}async function addF(to){let me=prompt('Your name to send friend request as:');if(!me)return;let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from_name:me,to_name:to})});let j=await r.json();alert(j.message||j.error)}function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(m=>(m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(qq)&&(pf=='All Projects'||m.project==pf)))}load();</script>'''
    return shell("Members",body)
@app.route("/community")
def community_page():
    body='''<h1>Community</h1><div style="display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px"><button class="chip on" id="chipAll" onclick="setFilter('all')">All Posts</button><button class="chip" id="chipPhoto" onclick="setFilter('photo')">Photos</button><button class="chip" id="chipVideo" onclick="setFilter('video')">Videos</button><a class="chip" href="/friends" style="text-decoration:none">Friends</a></div><div class="card"><label>Your name</label><input class="input" id="cName" placeholder="Your name"><div style="margin-top:12px"><label>Message</label><textarea id="cMsg" class="input" style="height:96px" placeholder="Share something..."></textarea></div><div style="display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px"><label class="chip" style="text-align:center;padding:14px">Add Photo<input type="file" id="photoInput" accept="image/*" style="display:none" onchange="handlePhoto(event)"></label><label class="chip" style="text-align:center;padding:14px">Add Video<input type="file" id="videoInput" accept="video/*" style="display:none" onchange="handleVideo(event)"></label></div><div id="preview"></div><button class="btn" onclick="sendC()" style="margin-top:14px">Post</button><p id="cStatus"></p></div><div class="card"><h2>Posts</h2><div id="cList">Loading...</div></div><script>let mediaType='';let mediaData='';let curFilter='all';function setFilter(f){curFilter=f;document.getElementById('chipAll').className='chip'+(f=='all'?' on':'');document.getElementById('chipPhoto').className='chip'+(f=='photo'?' on':'');document.getElementById('chipVideo').className='chip'+(f=='video'?' on':'');loadC()}function handlePhoto(e){let f=e.target.files[0];if(!f)return;if(f.size>3*1024*1024){alert('Photo too large, max 3MB');return}let r=new FileReader();r.onload=function(ev){mediaType='photo';mediaData=ev.target.result;document.getElementById('preview').innerHTML='<img src="'+mediaData+'" style="width:100%;border-radius:14px;margin-top:10px">'};r.readAsDataURL(f)}function handleVideo(e){let f=e.target.files[0];if(!f)return;if(f.size>12*1024*1024){alert('Video too large, max 12MB');return}let r=new FileReader();r.onload=function(ev){mediaType='video';mediaData=ev.target.result;document.getElementById('preview').innerHTML='<video src="'+mediaData+'" controls style="width:100%;border-radius:14px;margin-top:10px"></video>'};r.readAsDataURL(f)}async function loadC(){let r=await fetch('/api/community');let d=await r.json();let list=d.messages.filter(m=>curFilter=='all'||m.media_type==curFilter);document.getElementById('cList').innerHTML=list.map(m=>{let med='';if(m.media_type=='photo'&&m.media){med='<img src="'+m.media+'" class="postimg">'}if(m.media_type=='video'&&m.media){med='<video src="'+m.media+'" controls class="postvideo"></video>'}return '<div style="padding:14px 0;border-bottom:1px solid #eee"><b>'+m.name+'</b> <span>'+m.created+'</span><div>'+m.msg+'</div>'+med+'<div style="display:flex;gap:8px;margin-top:10px"><button class="chip" onclick="likePost('+m.id+')">Like '+(m.likes||0)+'</button><button class="chip" onclick="addFriendFromPost(\\''+m.name.replace(/'/g,'')+'\\')">+ Add Friend</button></div></div>'}).join('')||'No posts yet'}async function likePost(id){await fetch('/api/community/'+id+'/like',{method:'POST'});loadC()}async function addFriendFromPost(to){let me=document.getElementById('cName').value;if(!me){me=prompt('Your name:');if(!me)return}let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from_name:me,to_name:to})});let j=await r.json();alert(j.message||j.error)}async function sendC(){let name=document.getElementById('cName').value;let msg=document.getElementById('cMsg').value;if(!name){document.getElementById('cStatus').textContent='Enter your name';return}if(!msg&&!mediaData){document.getElementById('cStatus').textContent='Write a message or add a photo / video';return}let r=await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:name,msg:msg,media_type:mediaType,media:mediaData})});let j=await r.json();document.getElementById('cStatus').textContent=j.message;document.getElementById('cMsg').value='';mediaType='';mediaData='';document.getElementById('preview').innerHTML='';loadC()}loadC();</script>'''
    return shell("Community",body)
@app.route("/friends")
def friends_page():
    body='''<h1>Make Friends</h1><div class="card"><label>Your name</label><input class="input" id="myName" placeholder="Your full name"><button class="btn2 gold" onclick="loadF()" style="margin-top:12px">Show My Friends &amp; Requests</button></div><div class="card"><h2>Friend Requests For Me</h2><div id="reqList">Enter your name above and tap Show</div></div><div class="card"><h2>My Friends</h2><div id="friendList">Enter your name above and tap Show</div></div><div class="card"><h2>Find Friends</h2><input class="input" id="fq" placeholder="Search member by name or project" oninput="filF()"><div id="findList" style="margin-top:12px">Loading...</div></div><script>let allF=[];async function loadF(){let me=document.getElementById('myName').value;if(!me){alert('Enter your name first');return}let r=await fetch('/api/friends?me='+encodeURIComponent(me));let d=await r.json();document.getElementById('reqList').innerHTML=d.requests.map(x=>'<div class="row"><span><b>'+x.from_name+'</b></span><button class="btn2 gold" onclick="acceptF('+x.id+')">Accept</button></div>').join('')||'No new requests';document.getElementById('friendList').innerHTML=d.friends.map(x=>'<div class="row"><b>'+x+'</b><span class="pill">Friend</span></div>').join('')||'No friends yet.'}async function acceptF(id){let me=document.getElementById('myName').value;await fetch('/api/friends/accept',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({id:id,me:me})});loadF()}async function sendReq(to){let me=document.getElementById('myName').value;if(!me){me=prompt('Your name:');if(!me)return;document.getElementById('myName').value=me}let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from_name:me,to_name:to})});let j=await r.json();alert(j.message||j.error)}async function loadMembersF(){let r=await fetch('/api/members');let d=await r.json();allF=d.members;renderF(allF)}function renderF(l){document.getElementById('findList').innerHTML=l.slice(0,60).map(m=>'<div class="row"><span><b>'+m.full_names+'</b><div>'+m.project+' '+m.staff_no+'</div></span><button class="btn2" onclick="sendReq(\\''+m.full_names.replace(/'/g,'')+'\\')">+ Add Friend</button></div>').join('')||'No members'}function filF(){let q=document.getElementById('fq').value.toLowerCase();renderF(allF.filter(m=>(m.full_names+' '+m.project).toLowerCase().includes(q)))}loadMembersF();</script>'''
    return shell("Friends",body)
@app.route("/register")
def register_page():
    opts="".join([f'<option value="{p}">{p}</option>' for p in PROJECTS])
    body='''<h1>Register Member</h1><div class="card">'''
    for sec,fields in [("1. Staff Information",[("staff_no","Staff Number","text"),("project","Project","select"),("month_joined","Date Joined","text"),("full_names","Full Names","text"),("email","Email","text"),("password","Password","password")]),("2. Parents IDs",[("father_id","Father ID","text"),("mother_id","Mother ID","text")]),("3. Guardian and Spouse",[("guardian_id","Guardian ID No.","text"),("spouse_id","Spouse ID No.","text")]),("4. Kids Birth Certificates",[("kid1","Kid 1","text"),("kid2","Kid 2","text"),("kid3","Kid 3","text"),("kid4","Kid 4","text"),("kid5","Kid 5","text")])]:
        body+=f"<h3>{sec}</h3><div class='grid'>"
        for fid,label,typ in fields:
            if fid=="project": body+=f"<div><label>{label}</label><select class='input' id='project'>{opts}</select></div>"
            else: body+=f"<div><label>{label}</label><input class='input' id='{fid}' type='{typ}'></div>"
        body+="</div>"
    body+='''<button class="btn" onclick="doReg()" style="margin-top:20px">Create Member</button><p id="msg"></p></div><script>async function doReg(){let d={};["staff_no","project","full_names","email","password","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"].forEach(k=>{d[k]=document.getElementById(k).value});if(!d.email||!d.password||!d.full_names){document.getElementById('msg').textContent='Required: Full Names, Email, Password';return}let r=await fetch('/api/register',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(d)});let j=await r.json();document.getElementById('msg').textContent=j.error||j.message;if(r.ok)setTimeout(()=>location.href='/members',800)}</script>'''
    return shell("Register",body)
@app.route("/admin")
def admin_login_page():
    body='''<h1>Admin Login</h1><div class="card"><label>Email</label><input class="input" id="email" value="admin@lonma.com"><div style="margin-top:14px"><label>Password</label><input class="input" id="pass" type="password" value="admin123"></div><button class="btn" onclick="login()" style="margin-top:18px">Login</button><p id="msg"></p></div><script>async function login(){let r=await fetch('/api/admin/login',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({email:document.getElementById('email').value,password:document.getElementById('pass').value})});let j=await r.json();if(r.ok)location.href='/admin/dashboard?key='+j.key;else document.getElementById('msg').textContent=j.error}</script>'''
    return shell("Admin",body)
@app.route("/admin/dashboard")
def admin_dashboard():
    if request.args.get("key")!=ADMIN_KEY: return redirect("/admin")
    body='''<h1>Admin Dashboard</h1><div class="card"><button class="btn" onclick="clearAll()" style="background:#9A1B1B">Clear All Data</button><p id="clearMsg"></p></div><div class="card"><h2>Members</h2><a class="btn2" href="/download/excel">Download Excel</a><div id="tbl" style="margin-top:12px"></div></div><div class="card"><h2>Support Messages</h2><div id="supList">Loading...</div></div><script>async function clearAll(){if(!confirm('DELETE ALL MEMBERS + HISTORY?'))return;let r=await fetch('/api/clear-all?key='''+ADMIN_KEY+''',{method:'POST'});let j=await r.json();document.getElementById('clearMsg').textContent=j.message||j.error;load()}async function load(){let r=await fetch('/api/members_admin');let d=await r.json();let h='';d.members.forEach(m=>{h+='<div class="row"><span><b>'+m.staff_no+'</b> '+m.full_names+'<div>'+m.email+'</div></span><span>'+m.project+' <button onclick="del('+m.id+')" style="border:1px solid #E9E2D6;background:#fff;border-radius:999px;padding:6px 10px;cursor:pointer">Delete</button></span></div>'});document.getElementById('tbl').innerHTML=h||'No members';let r2=await fetch('/api/support_list');let d2=await r2.json();document.getElementById('supList').innerHTML=d2.messages.map(m=>'<div><b>'+(m.name||'Guest')+'</b> '+m.msg+'</div>').join('')||'No messages'}async function del(id){if(!confirm('Delete this member?'))return;let r=await fetch('/api/members/'+id+'?key='''+ADMIN_KEY+''',{method:'DELETE'});let j=await r.json();if(!r.ok)alert(j.error);load()}load();</script>'''
    return shell("Admin Dashboard",body)
@app.route("/download/excel")
def download_excel():
    proj=request.args.get("project",""); c=get_db()
    try:
        q="SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"; a=(ADMIN_EMAIL,)
        if proj and proj!="All Projects": q="SELECT staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a=(ADMIN_EMAIL,norm_project(proj))
        rows=c.execute(q,a).fetchall(); headers=["Staff Number","Full Names","Project","Email","Date Joined","Father ID","Mother ID","Guardian ID","Spouse ID","Kid 1","Kid 2","Kid 3","Kid 4","Kid 5"]
        from openpyxl import Workbook
        from openpyxl.styles import Font,PatternFill,Alignment
        wb=Workbook(); ws=wb.active; ws.title="Members"; ws.append(headers)
        for cell in ws[1]: cell.font=Font(bold=True,color="FFFFFF"); cell.fill=PatternFill("solid",fgColor="0A1F33"); cell.alignment=Alignment(horizontal="center")
        for r in rows: ws.append([r[x] or "" for x in ["staff_no","full_names","project","email","month_joined","father_id","mother_id","guardian_id","spouse_id","kid1","kid2","kid3","kid4","kid5"]])
        ws.freeze_panes="A2"; ws.auto_filter.ref=ws.dimensions; out=io.BytesIO(); wb.save(out); out.seek(0)
        return send_file(out,mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",as_attachment=True,download_name="FIG_BRANDS_Members.xlsx")
    finally: c.close()
@app.route("/api/stats")
def api_stats():
    c=get_db()
    try:
        total=c.execute("SELECT COUNT(*) FROM users WHERE email != ?",(ADMIN_EMAIL,)).fetchone()[0]
        rows=c.execute("SELECT project, COUNT(*) AS n FROM users WHERE email != ? GROUP BY project ORDER BY project",(ADMIN_EMAIL,)).fetchall()
        merged={}
        for r in rows:
            k=norm_project(r["project"]); merged[k]=merged.get(k,0)+r["n"]
        ordered={p:merged.get(p,0) for p in PROJECTS if p in merged}
        for k,v in merged.items():
            if k not in ordered: ordered[k]=v
        return jsonify({"total_members":total,"projects_total":len(merged),"projects":list(ordered.keys()),"projects_breakdown":ordered})
    finally: c.close()
@app.route("/api/clear-all",methods=["POST"])
def api_clear_all():
    if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
    c=get_db()
    try:
        c.execute("DELETE FROM users WHERE email != ?",(ADMIN_EMAIL,)); c.execute("DELETE FROM notifications"); c.execute("DELETE FROM support_msgs"); c.execute("DELETE FROM beneficiaries2"); c.execute("DELETE FROM fares2"); c.execute("DELETE FROM community"); c.execute("DELETE FROM friends"); c.commit()
        return jsonify({"message":"All data cleared. Only admin remains."})
    finally: c.close()
@app.route("/api/repair",methods=["POST"])
def api_repair():
    if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
    init_db()
    return jsonify({"message":"v138 re-seeded / updated"})
@app.route("/api/breakdown")
def api_breakdown():
    return jsonify({"periods":PERIODS,"monthly_individual":MONTHLY_INDIVIDUAL,"beneficiaries":BENEFICIARIES2,"beneficiaries_total":sum(x[5] for x in BENEFICIARIES2),"fares":FARES2,"fares_total":sum(x[3] for x in FARES2),"grand_total":sum(x.get("total",0) for x in PERIODS),"bf":BF,"transfer_total":0})
@app.route("/api/shareout")
def api_shareout():
    shares,total_contrib,total_months,per_month_rate=calc_shares()
    return jsonify({"bf":BF,"reserve":RESERVE,"distributable":DISTRIBUTABLE,"total_contributions":total_contrib,"total_months":total_months,"per_month_rate":round(per_month_rate,2),"members":len(shares),"total_shares":round(sum(x["share"] for x in shares),2),"shares":shares})
@app.route("/api/community",methods=["GET","POST"])
def api_community():
    c=get_db()
    try:
        if request.method=="POST":
            d=request.get_json(silent=True) or {}
            if not d.get("name"): return jsonify({"message":"Name required"}),400
            if not d.get("msg") and not d.get("media"): return jsonify({"message":"Write a message or add a photo / video"}),400
            media=(d.get("media") or "")[:9000000]
            c.execute("INSERT INTO community (name,msg,created,media_type,media,likes) VALUES (?,?,datetime('now'),?,?,0)",(d.get("name","Guest"),d.get("msg",""),d.get("media_type",""),media)); c.commit()
            return jsonify({"message":"Posted"})
        rows=c.execute("SELECT * FROM community ORDER BY id DESC LIMIT 100").fetchall()
        return jsonify({"messages":[dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/community/<int:pid>/like",methods=["POST"])
def api_like(pid):
    c=get_db()
    try:
        c.execute("UPDATE community SET likes=COALESCE(likes,0)+1 WHERE id=?",(pid,)); c.commit()
        row=c.execute("SELECT likes FROM community WHERE id=?",(pid,)).fetchone()
        return jsonify({"message":"Liked","likes":row["likes"] if row else 0})
    finally: c.close()
@app.route("/api/friends",methods=["GET"])
def api_friends():
    me=(request.args.get("me") or "").strip()
    c=get_db()
    try:
        if not me: return jsonify({"friends":[],"requests":[]})
        rows=c.execute("SELECT * FROM friends WHERE status='accepted' AND (lower(from_name)=lower(?) OR lower(to_name)=lower(?)) ORDER BY id DESC",(me,me)).fetchall()
        friends=[]
        for r in rows:
            friends.append(r["to_name"] if r["from_name"].lower()==me.lower() else r["from_name"])
        req=c.execute("SELECT * FROM friends WHERE status='pending' AND lower(to_name)=lower(?) ORDER BY id DESC",(me,)).fetchall()
        return jsonify({"friends":friends,"requests":[dict(x) for x in req]})
    finally: c.close()
@app.route("/api/friends/add",methods=["POST"])
def api_friends_add():
    d=request.get_json(silent=True) or {}
    frm=(d.get("from_name") or "").strip(); to=(d.get("to_name") or "").strip()
    if not frm or not to: return jsonify({"error":"Both names required"}),400
    if frm.lower()==to.lower(): return jsonify({"error":"You cannot add yourself"}),400
    c=get_db()
    try:
        ex=c.execute("SELECT id FROM friends WHERE (lower(from_name)=lower(?) AND lower(to_name)=lower(?)) OR (lower(from_name)=lower(?) AND lower(to_name)=lower(?))",(frm,to,to,frm)).fetchone()
        if ex: return jsonify({"message":"Already friends or request sent"})
        c.execute("INSERT INTO friends (from_name,to_name,status,created) VALUES (?,?,?,datetime('now'))",(frm,to,"pending")); c.commit()
        return jsonify({"message":"Friend request sent to "+to})
    finally: c.close()
@app.route("/api/friends/accept",methods=["POST"])
def api_friends_accept():
    d=request.get_json(silent=True) or {}
    c=get_db()
    try:
        c.execute("UPDATE friends SET status='accepted' WHERE id=?",(d.get("id"),)); c.commit()
        return jsonify({"message":"Friend accepted"})
    finally: c.close()
@app.route("/api/notifications")
def api_notifs():
    c=get_db()
    try:
        rows=c.execute("SELECT * FROM notifications ORDER BY id DESC").fetchall(); notifs=[dict(r) for r in rows]; unread=sum(1 for n in notifs if not n.get("is_read"))
        return jsonify({"notifications":notifs,"unread":unread,"total":len(notifs)})
    finally: c.close()
@app.route("/api/notifications/read",methods=["POST"])
def api_notifs_read_all():
    c=get_db()
    try: c.execute("UPDATE notifications SET is_read=1"); c.commit(); return jsonify({"message":"All read","unread":0})
    finally: c.close()
@app.route("/api/notifications/<int:nid>/read",methods=["POST"])
def api_notif_read_one(nid):
    c=get_db()
    try:
        c.execute("UPDATE notifications SET is_read=1 WHERE id=?",(nid,)); c.commit(); row=c.execute("SELECT * FROM notifications WHERE id=?",(nid,)).fetchone()
        return jsonify({"message":"Read","notification":dict(row) if row else None})
    finally: c.close()
@app.route("/api/support",methods=["POST"])
def api_support():
    d=request.get_json(silent=True) or {}; c=get_db()
    try: c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))",(d.get("name","Guest"),d.get("msg",""))); c.commit(); return jsonify({"message":"Message sent. Support will reply soon."})
    finally: c.close()
@app.route("/api/support_list")
def api_support_list():
    c=get_db()
    try:
        rows=c.execute("SELECT * FROM support_msgs ORDER BY id DESC").fetchall(); return jsonify({"messages":[dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/members")
def api_members():
    proj=request.args.get("project",""); c=get_db()
    try:
        q="SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? ORDER BY id DESC"; a=(ADMIN_EMAIL,)
        if proj and proj!="All Projects": q="SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5 FROM users WHERE email != ? AND project=? ORDER BY id DESC"; a=(ADMIN_EMAIL,norm_project(proj))
        rows=c.execute(q,a).fetchall(); return jsonify({"members":[dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/members_admin")
def api_members_admin():
    c=get_db()
    try:
        rows=c.execute("SELECT id,staff_no,full_names,project,email,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo FROM users ORDER BY id DESC").fetchall(); return jsonify({"members":[dict(r) for r in rows]})
    finally: c.close()
@app.route("/api/admin/login",methods=["POST"])
def api_admin_login():
    d=request.get_json(silent=True) or {}; c=get_db()
    try:
        u=c.execute("SELECT password,api_key FROM users WHERE email=?",(d.get("email"),)).fetchone()
        if not u or not check_password_hash(u["password"],d.get("password","")): return jsonify({"error":"Invalid"}),401
        return jsonify({"key":u["api_key"]})
    finally: c.close()
@app.route("/api/register",methods=["POST","OPTIONS"])
def api_register():
    if request.method=="OPTIONS": return "",200
    d=request.get_json(silent=True) or {}
    c=get_db()
    if not d.get("email") or not d.get("password"): c.close(); return jsonify({"error":"Email and password required"}),400
    if c.execute("SELECT id FROM users WHERE email=?",(d.get("email",""),)).fetchone(): c.close(); return jsonify({"error":"Email exists"}),400
    if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(d.get("full_names",""),)).fetchone(): c.close(); return jsonify({"error":"Name exists"}),400
    proj=norm_project(d.get("project","HQ"))
    vals=(d.get("staff_no",""),d.get("full_names",""),proj,d.get("email",""),generate_password_hash(d.get("password","")),"fig_"+secrets.token_hex(12),d.get("month_joined",""),d.get("father_id",""),d.get("mother_id",""),d.get("guardian_id",""),d.get("spouse_id",""),d.get("kid1",""),d.get("kid2",""),d.get("kid3",""),d.get("kid4",""),d.get("kid5",""),d.get("photo",""))
    c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    c.execute("INSERT INTO notifications (title,msg,created,target,is_read) VALUES (?,?,?,?,?)",("New Member Registered",f"{d.get('full_names','')} joined {proj}","Just now","/members",0))
    c.commit(); c.close(); return jsonify({"message":"Member created"}),201
@app.route("/api/members/<int:member_id>",methods=["DELETE","OPTIONS"])
def api_delete(member_id):
    if request.method=="OPTIONS": return "",200
    if request.args.get("key")!=ADMIN_KEY: return jsonify({"error":"Admin key required"}),401
    c=get_db()
    u=c.execute("SELECT email FROM users WHERE id=?",(member_id,)).fetchone()
    if not u or u["email"]==ADMIN_EMAIL: c.close(); return jsonify({"error":"Cannot delete Protected Admin"}),403
    c.execute("DELETE FROM users WHERE id=?",(member_id,)); c.commit(); c.close(); return jsonify({"message":"Deleted"})
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT",10000)))
