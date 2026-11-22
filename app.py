import sqlite3, os, csv, io
from flask import Flask, request, jsonify, redirect
app = Flask(__name__)
DB = "lonma.db"
def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con
SEED = """202973|TF-MT|Jan-26|Anastacia Mwende Mutua|12584896|12571589|33067411|N/A|5772864|-|-|-|-
202857|TF-MT|2025|Brenda joy nyongesa|6565657|N/A|N/A|N/A|N/A|-|-|-|-
-|TF-MT|Nov-26|Bryton Otieno okoth|N/A|22959540|N/A|N/A|N/A|-|-|-|-
292954|TF-MT|Feb-26|Christine Wangu namange|33918462|2059381|N/A|N/A|31848814|1832003833|32224611|-|-
202879|TF-MT|2024|Daniel musyoka|N/A|N/A|N/A|37486040|1308478|-|-|-|-
202899|TF-MT|2023|Daniel Mwangi maina|10787780|10058327|N/A|36946194|2643331|4350577|-|-|-
202851|TF-MT|2024|Douglas lidoli lidundu|N/A|1142024|N/A|35819089|N/A|-|-|-|-
202898|TF-MT|2022|Elizabeth Kaluki mbithe|N/A|30992865|N/A|N/A|N/A|-|-|-|-
202838|TF-MT|2023|Elizabeth matinde|N/A|30491044|30005457|N/A|5052470|-|-|-|-
202856|TF-MT|2025|Elizabeth Silvia Botuba|10430483|20545758|N/A|N/A|N/A|-|-|-|-
202927|TF-MT|Jan-26|Esther syokau mosyoki|N/A|12721635|29855331|N/A|N/A|-|-|-|-
202847|TF-MT|2025|Esther Wanjiku|N/A|N/A|N/A|26007857|7871720|-|-|-|-
202853|TF-MT|2025|Eugene Ochieng|5985386|14443973|N/A|42103832|N/A|-|-|-|-
202886|TF-MT|2023|Faith Atieno|16066182|N/A|N/A|N/A|N/A|-|-|-|-
202850|TF-MT|2025|Getrude kisala|5126406|5625403|33633256|26924253|791109279|264794549|-|-|-
202855|TF-MT|2025|Jackline Njeri chomba|N/A|N/A|N/A|N/A|N/A|-|-|-|-
292982|TF-MT|Feb-26|Janevick moraa|N/A|2058869|2058869|N/A|N/A|-|-|-|-
202860|TF-MT|2025|Mark Alema Mbeche|5339293|13408682|N/A|32173580|264970115|-|-|-|-
-|TF-MT|2024|Mary Wangari|N/A|23395553|N/A|3612145|5953389|5953388|2583144|-|-
202881|TF-MT|2024|Melvin Mumo|N/A|10288319|N/A|39465308|N/A|-|-|-|-
202868|TF-MT|2025|Milka Waweru Nyambura|8483259|30808943|N/A|N/A|362101165|-|-|-|-
202843|TF-MT|2023|Mourin wangui karomo|10502813|10453948|N/A|33400723|26479|-|-|-|-
202865|TF-MT|2025|Nyongesa rendson wekesa|N/A|8038054|N/A|N/A|N/A|-|-|-|-
202842|TF-MT|2025|Peninah awuor olang'o|N/A|13298945|N/A|28715422|264168855|264809974|-|-|-
202854|TF-MT|2025|Peter omoro|N/A|11131310|N/A|37130958|2302502581|-|-|-|-
202872|TF-MT|2024|Philip Etale|N/A|14446251|N/A|N/A|N/A|-|-|-|-
292952|TF-MT|Feb-26|Protus Ojuma|13170537|23307688|42717879|N/A|N/A|-|-|-|-
-|TF-MT|Nov-26|Purity Opiyo Anyango|N/A|8213405|N/A|N/A|685497|-|-|-|-
202844|TF-MT|2025|purity Wambui|12475261|12472997|N/A|N/A|N/A|-|-|-|-
202880|TF-MT|2024|Scholastica kilonzi|1008033|2983637|N/A|N/A|282157|-|-|-|-
202833|TF-MT|2025|Stephen Wesonga Ouma|-|8615924|-|-|832827|3817366|-|-|-
-|TF-MT|Jun-26|Telvin gachanja|N/A|14417026|N/A|33355682|264284946|2839387|-|-|-
202863|TF-MT|2023|Teresia Muthoni Kariuki|N/A|21507084|N/A|-|5050624|-|-|-|-
202864|TF-MT|2025|Vincent Otieno Okello|2739631|21348018|N/A|37048476|N/A|-|-|-|-
202870|TF-MT|2025|Vonter Moses Amuto|N/A|21320319|N/A|41465467|N/A|-|-|-|-
202846|TF-MT|2025|Willis Ogumbo othiambo|8671565|11562991|N/A|N/A|N/A|-|-|-|-
202876|TF-MT|2024|Jane wanjiru|359820|4828287|N/A|33036142|1458214|2942546|-|-|-
202861|TF-MT|Mar-26|Ann Njoroge|-|-|-|-|-|-|-|-|-
202963|TF-MT|Oct-26|Fridah Gastaiti|-|-|-|-|-|-|-|-|-
-|TF-MT|Jul-26|Beryl Jeptoo|2253273|N/A|N/A|35017099|N/A|N/A|-|-|-
202871|TF-MT|2024|Loureen Anyango Agutu|N/A|6763274|24720221|27503464|512400592|782234653|-|-|-
202891|TF-MT|2023|Maryanne Wanjiru Kariuki|7131147|21258218|N/A|22490702|A0701169|A4404579|-|-|-
-|TF-MT|2025|Mercy Chepkemoi|7651555|8548725|N/A|23779678|121224700|122119234|-|-|-
202885|TF-MT|2020|Mourine Akoth|10822795|28243742|N/A|33548098|4496868|-|-|-|-
280222|TF-MT|Apr-26|Shania Joy|N/A|N/A|13383612|N/A|N/A|N/A|-|-|-
202874|TF-MT|2025|Valary Chepkoech Bii|1366326|7960048|N/A|N/A|-|-|-|-|-
-|TF-MT|Jul-26|Vallary Akinyi|N/A|20065485|N/A|33716569|5059601|-|-|-|-
202878|TF-MT|2024|Brendah Achieng Gumba|N/A|10533906|N/A|N/A|391729842|392200448|-|-|-
280003|TF-MT|Jun-26|Brian Kang'ethe|N/A|24705142|N/A|N/A|N/A|-|-|-|-
202877|TF-MT|2025|Catherine Awino Agutu|-|-|N/A|27422318|4207822|9349719|-|-|-
202893|TF-MT|2023|Damaris Wekesa|N/A|829543|N/A|29621541|-|1311904839|1311323602|-|-
-|TF-MT|Nov-26|Dorine Anyango Odongo|7328824|6666068|N/A|N/A|2052600642|-|-|-|-
202845|TF-MT|2025|Ebby Kageha lomosi|3243910|6525191|N/A|N/A|67646|1055943|-|-|-
202867|TF-MT|2025|Eunice Wambui|22158745|25712558|N/A|N/A|1442211376|-|-|-|-
202895|TF-MT|2014|Jane Wairimu|N/A|5981674|N/A|N/A|39323500|271722809|-|-|-
280220|TF-MT|Mar-26|Joseph Mumanyi|7936972|10003795|N/A|41229249|1849133|-|-|-|-
280507|TF-MT|Nov-26|Manase Karanja Thuo|11154721|21620654|N/A|N/A|N/A|N/A|-|-|-
70221|TF-MT|2023|Pamela Awuor Nyadodo|N/A|9554703|N/A|22793574|391122658|390515422|-|-|-
-|TF-MT|Nov-26|Bartholomew Wekesa musundi|9721630|13561414|N/A|N/A|172117769|-|-|-|-
-|TF-MT|Oct-26|Rachael Gathoni wangigi|8846144|N/A|N/A|N/A|851318363|851610578|-|-|-
292979|TF-MT|Jul-26|Risper Moraa Momanyi|8730577|N/A|N/A|N/A|246730359|-|-|-|-
292959|TF-MT|Jul-26|Samuel onyango|N/A|13129230|N/A|860805859|N/A|N/A|-|-|-
202890|TF-MT|2023|John Mwangi|-|-|-|-|-|-|-|-|-
280270|TF-MT|Jul-26|Whitney Arot Aturae|N/A|21596130|N/A|-|-|-|-|-|-
202873|TF-MT|2023|Brian Ombwori Osese|1618384|7607080|N/A|37219432|902027|5733030|-|-|-
202835|TF-MT|2024|Diana Nanjala wafula|21253105|23122140|N/A|32457447|-|-|-|-|-
202920|TF-MT|2025|Elvis Shikuku|14678081|1181476|N/A|N/A|N/A|N/A|-|-|-
202882|TF-MT|2023|Irene Ogutu|N/A|5772466|N/A|29341825|N/A|4057128|4198133|-|-
202859|TF-MT|Jan-26|Emma Watindi|-|-|-|-|-|-|-|-|-
202849|TF-MT|2025|Jacinta Apondi|N/A|22858932|N/A|N/A|N/A|N/A|-|-|-
202888|TF-MT|2017|Jackline Kavere Ayiga|521394|-|23987409|5466522|111414657|111136627|112004194|-|-
202884|TF-MT|2024|Mercy Achieng Onyango|N/A|N/A|21999525|28376863|7206211|7206057|-|-|-
202889|TF-MT|2021|Naomi Jeruto Tanui|N/A|20153118|N/A|N/A|9596061|-|-|-|-
202839|TF-MT|2025|Otieno lavenda|N/A|20680682|N/A|N/A|N/A|-|-|-|-
202628|HQ|2015|JANEDRIX AKINYI SADAKA|N/A|JOYCE SAKAKA|-|N/A|JAMES SADAKSA|JOYBLESSING|-|-|-
N/A|HQ|2015|CELESTINE ATIENO SADAKA|N/A|JOYCE SAKAKA|-|N/A|LINCOL|IAN|ANDREY|-|-
280314|HQ|11/082026|LAZARUS OKECHI|NICODEMUS OGOTI|MARY AJIAMBO|-|PURITY KABATI|AZARIA AJIAMBO|-|-|-
N/A|HQ|2020|PATRIC TITO|TITO NZONGA|FELISTERS TITO|-|FRIDAH KARIMI|TIFFANY TITO|BARAKA TITO|-|-
292930|HQ|11/082026|EDDY NYANGORI|JOHN NYANGORI|HELLENE ACHIENG|-|N/A|-|-|-|-|-
Sherine Atieno|Antonia|Jun-26|Sherine Atieno Otieno|N/A|23333405|N/A|N/A|N/A|N/A|N/A|N/A|N/A
280225|Antonia|Jun-26|Stepheny Keziah Wambui Mwangi|10452983|10166506|-|34439485|1463604|2498854|-|-|-
202640|Java House|06/01/2024|Samuel Njeru Njiru|NA|12402044|NA|NA|NA|NA|NA|-|-
202642|Java House|02/01/2023|Eugene Daudi Aura|12684478|22143892|NA|NA|NA|NA|NA|-|-
202643|Java House|16/06/2023|Wamuyu Irene Wairimu|NA|NA|NA|NA|NA|NA|NA|-|-
280226|Java House|22/06/2026|Alice Maina|21154721|5925331|NA|NA|NA|NA|NA|-|-
292965|Java House|05/05/2026|Sylvia Agosa|NA|27589904|NA|NA|NA|NA|NA|-|-
202648|Java House|08/01/2022|Esther Wangari Karanja|NA|2947799|NA|28442445|661711470|131927789|NA|-|-
202649|Java House|08/01/2023|Emily Waithera Njenga|12679084|29681293|NA|31609269|74506389|NA|NA|-|-
280372|Java House|09/09/2026|Joan Ensha Wairimu|7178165|10271736|NA|NA|27163167|NA|NA|-|-
202651|Java House|15/04/2024|Edwin Ondieki Kiyaka|6925315|25820458|NA|36314446|272309733|NA|NA|-|-
202652|Java House|23/11/2023|Gladys Kinuthia|730157|NA|NA|NA|721471|B750670|NA|-|-
280507|Java House|16/09/2026|Purity mukami|NA|21461686|NA|NA|207735072|NA|NA|-|-
202654|Java House|17/05/2025|Samwel Erick Odhiambo|NA|11705391|NA|NA|NA|NA|NA|-|-
202655|Java House|04/01/2025|Felister Gatwiri Muriithi|8601366|21461686|NA|27924521|1752770|NA|NA|-|-
202666|Java House|21/07/2026|Charity Moraa Juma|12696585|NA|NA|NA|NA|NA|NA|-|-
202660|Java House|01/01/2026|Brian Mwenda Njue|NA|11326767|NA|NA|NA|NA|NA|-|-
202661|Java House|11/11/2025|Emmanuel Mike Ochieng|NA|20465576|NA|NA|NA|NA|NA|-|-
202662|Java House|11/11/2025|Caroline Muthoni Mugo|NA|9410131|NA|NA|447404|NA|NA|-|-
202664|Java House|13/03/2026|Jeniffer Wanjira Ndung'u|3081426|NA|NA|NA|4694621|NA|NA|-|-
202670|Java House|06/06/2025|Maureen Gathiru Mwaniki|8949712|9484232|NA|NA|NA|NA|NA|-|-
202671|Java House|01/01/2025|Lilian Adhiambo Randa|NA|NA|22175755|28042042|4363793|6390498|NA|-|-
202673|Java House|05/05/2024|Pauline Wambui Masila|NA|4872231|NA|28587029|6097147|A3489654|NA|-|-
202674|Java House|29/11/2023|Anne Kamonya Mulema|NA|NA|1881637|29867375|9746194|7016764|NA|-|-
202675|Java House|06/06/2025|Daniel Ombui Mayaka|6925939|5825881|NA|29893290|7090003|9105030|NA|-|-
202934|Java House|01/01/2026|Jeff Otieno Maina|NA|NA|33964654|NA|NA|NA|NA|-|-
202935|Java House|01/01/2026|Jedida Njoki Kinyanjui|NA|4244441|NA|NA|NA|NA|NA|-|-
202937|Java House|02/02/2026|Clifton Kelvin Makokha|NA|NA|NA|NA|NA|NA|NA|-|-
202952|Java House|01/01/2026|Collen Elizabeth Ojiambo|NA|NA|NA|NA|7072542|7515539|7135442|-|-
202978|Java House|02/02/2026|Jackline Wanza Muthoka|NA|13796649|NA|NA|NA|NA|NA|-|-
292915|Java House|05/05/2026|Francis Omari|NA|21065823|NA|NA|NA|NA|NA|-|-
202686|Java House|16/04/2017|Evaperpetual Wambui Maina|NA|13542413|NA|NA|NA|NA|NA|-|-
202603|Java House|01/09/2020|Mariam Juma|NA|NA|NA|NA|41335956|260828238|608994032|-|-
280528|Java House|11/01/2026|Hydrick Kipkorir|NA|NA|NA|620201|NA|NA|NA|-|-
-|Java House|01/11/2026|Kendy Njeri|NA|26001602|NA|NA|NA|NA|NA|-|-
-|Java House|01/11/2026|Joseph Chege|3054830|NA|NA|38220338|NA|NA|NA|-|-
-|Java House|01/11/2026|Specioza Matitsa|NA|NA|NA|NA|NA|NA|NA|-|-
202989|SCJohnson|Feb-26|Bonface Nzuki|13592548|20001605|-|-|-|-|-|-|-
202774|SCJohnson|Aug-24|Oscar kipkoech Ruto|8715105|25972243|N/A|643055126|604533|-|-|-|-
90117|SCJohnson|Aug-22|Hilda Esende Lugangi|22499361|22546698|Nil|22499361|330400075|370207832|371929483|-|-
Lena Cherono|SCJohnson|Oct-26|Lena Cherono|N/A|6013139|6013139|-|-|-|-|-|-
202788|SCJohnson|Aug-23|Afline Anyango Onyango|N/A|N/A|25083427|N/A|538317|538318|538342|880993|8908622
202786|SCJohnson|Aug-22|Judith Oweya Lukale|6308832|1232343|-|-|7281845|8355678|-|-|-
202784|SCJohnson|45839|Farida Olesi|N/A|21667279|-|-|4164247|-|-|-|-
Phesial Jaramogi Ooyi|SCJohnson|Aug-22|Phesial Jaramogi Ooyi|2631938|21217207|N/A|38946763|7493054|3486480|-|-|-
201743|SCJohnson|25-Apr|Zachary Joel Moriasi|N/A|31295653|N/A|-|-|-|-|-|-
202976|SCJohnson|Feb-26|Winfred mwende john|N/A|8966707|N/A|28782624|-|261287576|-|-|-
202782|SCJohnson|Dec-25|Victoria wangechi Mugwe|5988617|11032615|-|-|1512406016|-|-|-|-
202775|SCJohnson|Feb-23|Milka Wawuda Mwang'ombe|N/A|58719|-|-|-|-|-|-|-
202780|SCJohnson|2022|Mokua Frankline|23751234|24351022|-|37120961|-|-|-|-|-
202765|SCJohnson|Aug-25|Hannah Warukira Mwangi|3582703|N/A|-|-|0071503182|-|-|-|-
202977|Scjohnsons|26 Jan,2026|Emily Mueni Mutua|N/A|N/A|3545974|-|212327285|212303274|-|-|-
202764|Scjohnsons|August,2025|Agnes Wangu Mwangi|9263345|20409743|-|-|201192|-|-|-|-
202769|scjohnsons|Aug-25|Joshua mwangi iguna|10380353|31107389|-|511795193|-|-|-|-|-
202761|SC Johnson|Apr_25|Hannah wanjiku|N/A|N/A|N/A|N/A|2384950|-|-|-|-
202777|SCJohnson|,Sept 2022|Caroline Kathomi Njebiu|N/A|N/A|-|-|-|-|-|-|-
202757|SCJohnson|26/22/2024|Fedinand Kafwa|N/A|N/A|-|-|-|-|-|-|-
202772|SCJohnson|,Feb 2025|Maureen Njeri|N/A|N/A|-|-|-|-|-|-|-
280267|SCJohnson|,July 2026|Patrick Kabiu Waweru|N/A|N/A|-|-|-|-|-|-|-
202766|SCJohnson|,April 2025|Veronica Mukolwe|N/A|21000046|N/A|N/A|265075567|-|-|-|-
202789|SCJohnson|,Aug 2022|Celestine Auma Ouko|25837011|8212095|-|21166739|6658291|-|-|-|-
202697|Pwani Oil|Sept.2017|Naomi Mwango Abenga|1658833|NA|NA|22188003|121032026|121622654|112220451|-|-
202700|Pwani Oil|Mar-25|Charles kimutai Kirui|3872261|3872429|N/A|31045698|612112010|N/A|N/A|N/A|N/A
202709|Pwani Oil|Mar-25|Oyoyo Yvonne Bentar|N/A|11801824|N/A|27464418|N/A|N/A|N/A|N/A|N/A
202678|Pwani Oil|Mar-25|Owen Muthee Waithaka|21217575|22555615|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202733|Pwani Oil|Mar-25|Sharon Cherono|N/A|11635405|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202529|Pwani Oil|Mar-25|Alex Shangala|4176764|7956390|N/A|33313078|692102029|691828162|N/A|N/A|N/A
202729|Pwani Oil|Mar-25|ROSE LUMONYA SAIDI|N/A|4252080|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202747|Pwani Oil|Jul-25|BRENDA NELIMA WAFULA|N/A|133101|N/A|N/A|N/A|N/A|N/A|N/A|N/A
10405|Pwani Oil|Mar-25|Diana Atieno Oduor|NA|4722494|757617564|28078423|370702896|21506184|Joy Nelima|Samantha|-
202749|Pwani Oil|Mar-25|Celine Nasimiyu Wamalwa|N/A|8784757|NA|28990208|William Musungu|Moses Musungu|Bryton Musungu|N/A|N/A
292976|Pwani Oil|01/04/2026|Belinda chemtai|N/A|4722288|N/A|N/A|372315084|182018971|N/A|N/A|N/A
202702|Pwani Oil|May-25|Betty Akinyi Namamba|Fabians Namamba|Janet Atieno|N/A|N/A|N/A|N/A|N/A|N/A|N/A
202723|Pwani Oil|Mar-25|Metrine Cherop Chumo|N/A|N/A|N/A|29934624|411700883|411506469|N/A|N/A|N/A
50516|Pwani Oil|May-25|SHEILA ADISA VOLEMI|VOLEMI|TERESIA|HUDSON IMBAYI|22175541|NA|NA|NA|N/A|N/A
202701|Pwani Oil|Mar-25|Everlyne mukoya Stephen|NA|N/A|N/A|23600368|N/A|671767|395330|N/A|N/A
202703|Pwani Oil|Mar-25|Caren Nanjala Chonge|NA|5639451|Later|22086206|364057|6090663|N/A|N/A|N/A
202704|Pwani Oil|Mar-25|Hellen Achieng Onyango|711723882|726994852|N/A|722618476|N/A|N/A|N/A|N/A|N/A
202724|Pwani Oil|Mar-25|BENTA ACHIENG MURUKA|CHRISTOPHER MURUKA|JANE MAGENGA|N/A|28687282|1311214785|21910561|N/A|-|-
202696|Pwani Oil|2015|Lydiah Nyaanga Osengo|1649626|1637770|-|10020853|160900879|168706540/19|-|-|-
202693|Pwani Oil|May.2022|Meggiling Abuga Nyakerario|-|8647005|-|-|160900879|-|-|-|-
202695|Pwani Oil|2022|Gorrety Adhiambo Otieno|9807667|26810228|-|30257258|2348625|2350080|3743676|-|-
202699|Pwani Oil|14/12/2022|Sophia Nyamoita Mokaya|-|6541570|-|27233755|-|-|-|-|-
202751|Pwani Oil|02/10/2023|Benjamin Odiwuor Mboya|10596034|20015894|-|466468971|7893744|-|-|-|-
202730|Pwani Oil|4.8.2025|Orwa Diana Atieno|96811362|21136615|-|36519946|-|will provide later|-|-|-
202694|Pwani Oil|02/01/2020|Charles Adika|8837595|11833576|-|-|-|-|-|-|-
282000|Pwani Oil|5/1/2026|Hyphine chepkoech Mutai|10383876|28240917|-|26261936|-|-|-|-|-
202750|Pwani Oil|May.2025|Priscah Anjemo Injili|-|21842168|-|32990585|795787|978435|-|-|-
202698|Pwani Oil|14/02/2022|Postine Atieno|7921446|8398928|-|38801320|122318007|-|-|-|-
202744|Pwani Oil|Mar-24|Anthony Manyara Chania|21022712|86260659|-|923456988|-|-|-|-|-
202683|Pwani Oil|Mar-13|Eunice Makona|-|4722288|N/A|210327239|7575163|7575161|7575162|-|-
FIG001|FIG|2026-01|Marlon K. Ang'undu|-|-|1951498|-|6879175|-|-|-|-
FIG002|Gold Crown Beverage|2026-01|Mary Ngotah|-|-|-|-|-|-|-|-|-
FIG003|SC Johnsons|2026-01|Celestine Ouko|-|-|-|-|-|-|-|-|-
FIG004|Nairobi Java|2026-01|Irene Wamuyu|-|-|-|-|-|-|-|-|-
FIG005|Last Mile Trufoods Ltd|2026-01|Jonathan Mutunga|-|-|-|-|-|-|-|-|-
"""
def init_db():
    con=get_db();cur=con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, staff_no TEXT, project TEXT, month_joined TEXT, status TEXT DEFAULT 'active member', father_id TEXT DEFAULT '-', mother_id TEXT DEFAULT '-', guardian_id TEXT DEFAULT '-', spouse_id TEXT DEFAULT '-', kid1 TEXT DEFAULT '-', kid2 TEXT DEFAULT '-', kid3 TEXT DEFAULT '-', kid4 TEXT DEFAULT '-', kid5 TEXT DEFAULT '-')")
    cur.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, action TEXT, amount REAL DEFAULT 0, date TEXT)")
    con.commit()
    if cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]==0:
        for line in SEED.strip().splitlines():
            p=[x.strip() for x in line.split("|")]
            p=(p+["-"]*13)[:13]
            cur.execute("INSERT INTO users (staff_no, project, month_joined, full_names, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 'active member')", p)
        con.commit()
    con.close()
init_db()
def clean(v):
    v=(v or "").strip()
    return v if v not in ("","-","N/A","NA","Nil") else "—"
def initials(n):
    a=[x for x in (n or "").split() if x]
    return ((a[0][0]+(a[-1][0] if len(a)>1 else "")).upper() if a else "?")
def pcolor(p):
    p=(p or "").lower()
    return "blue" if "tf-mt" in p else "amber" if "java" in p else "green" if "sc" in p else "purple" if "pwani" in p else "red" if "hq" in p else "pink" if "antonia" in p else "gray"
def shell(title,body,active=""):
    links=[("Home","/"),("Members","/members"),("Register","/register"),("Share-Out","/shareout"),("History","/history"),("Community","/community")]
    nav="".join([f"<a href='{u}' class='{'on' if n==active else ''}'>{n}</a>" for n,u in links])
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>*{{box-sizing:border-box}}body{{font-family:Arial,sans-serif;margin:0;background:#F4F6FB}}header{{background:#0B1D8A;color:#fff;padding:14px 16px 0;position:sticky;top:0}}nav{{max-width:1100px;margin:12px auto 0;display:flex;gap:6px;overflow-x:auto;padding-bottom:12px}}nav a{{color:#D6DBFF;text-decoration:none;padding:8px 14px;border-radius:999px;font-weight:700;font-size:14px;white-space:nowrap}}nav a.on{{background:#fff;color:#0B1D8A}}main{{max-width:1100px;margin:auto;padding:16px}}.card{{background:#fff;border:1px solid #E5E8F0;border-radius:16px;padding:16px;margin-bottom:12px}}.grid{{display:grid;grid-template-columns:repeat(4,1fr);gap:12px;margin-bottom:16px}}@media(max-width:700px){{.grid{{grid-template-columns:repeat(2,1fr)}}}}.stat{{background:#fff;border:1px solid #E5E8F0;border-radius:16px;padding:16px}}.stat b{{font-size:26px;display:block}}input,select,button{{padding:12px;border:1px solid #E5E8F0;border-radius:12px;font-size:15px;width:100%}}.btn{{background:#0B1D8A;color:#fff;font-weight:800;border:none}}.btn2{{background:#EEF2FF;color:#0B1D8A;font-weight:800}}.row{{display:flex;gap:10px;flex-wrap:wrap}}.row>*{{flex:1;min-width:140px}}.chips{{display:flex;gap:8px;flex-wrap:wrap;margin-top:10px}}.chip{{border:1px solid #E5E8F0;background:#F8FAFF;padding:7px 11px;border-radius:999px;font-size:13px;font-weight:700;text-decoration:none;color:#111}}.chip.on{{background:#0B1D8A;color:#fff}}.list{{display:grid;grid-template-columns:1fr 1fr;gap:12px}}@media(max-width:700px){{.list{{grid-template-columns:1fr}}}}.member{{background:#fff;border:1px solid #E5E8F0;border-radius:16px;padding:14px;display:flex;gap:12px}}.avatar{{width:48px;height:48px;min-width:48px;border-radius:50%;display:grid;place-items:center;font-weight:900;color:#fff}}.blue{{background:#1E3AE0}}.amber{{background:#D97706}}.green{{background:#059669}}.purple{{background:#7C3AED}}.red{{background:#DC2626}}.pink{{background:#DB2777}}.gray{{background:#6B7280}}.pill{{display:inline-block;padding:4px 8px;border-radius:999px;font-size:11px;font-weight:800;background:#EEF2FF;color:#0B1D8A}}.pill.ok{{background:#DCFCE7;color:#166534}}.fam{{display:grid;grid-template-columns:1fr 1fr;gap:6px;font-size:13px}}.fam div{{background:#F8FAFF;padding:7px 9px;border-radius:10px}}table{{width:100%;border-collapse:collapse}}th,td{{padding:10px;border-bottom:1px solid #E5E8F0;text-align:left}}</style></head><body><header><b>LONMA ORBIT - FIG WELFARE</b><nav>{nav}</nav></header><main><h1>{title}</h1>{body}</main></body></html>"""
@app.route("/")
def home():
    con=get_db();total=con.execute("SELECT COUNT(*) FROM users WHERE status='active member'").fetchone()[0];projects=con.execute("SELECT project, COUNT(*) c FROM users GROUP BY project ORDER BY c DESC").fetchall();con.close()
    chips="".join([f"<a class='chip' href='/members?project={p['project']}'>{p['project']} • {p['c']}</a>" for p in projects])
    h=f"<div class='grid'><div class='stat'><b>{total}</b><span>Active Members</span></div><div class='stat'><b>Ksh {total*300:,}</b><span>Monthly</span></div><div class='stat'><b>Ksh 100,000</b><span>Member Benefit</span></div><div class='stat'><b>30 Nov</b><span>Year-End</span></div></div><div class='card'><b>Browse by Project</b><div class='chips'>{chips}</div></div><div class='card'><b>Membership:</b> Automatic on employment with FIG.<br><b>Benefits:</b> Member 100,000 | Spouse 50,000 | Child 40,000 | Parents 40,000<br><b>Year-End:</b> Min balance 250,000. Above shared among active members.</div>"
    return shell("Home",h,"Home")
@app.route("/members")
def members():
    q=request.args.get("q","").strip();proj=request.args.get("project","").strip();sort=request.args.get("sort","name");kids=request.args.get("kids","")
    con=get_db();projects=[r["project"] for r in con.execute("SELECT DISTINCT project FROM users ORDER BY project").fetchall()];rows=con.execute("SELECT * FROM users ORDER BY full_names").fetchall();con.close()
    f=[]
    for m in rows:
        if proj and m["project"]!=proj: continue
        if q and q.lower() not in f"{m['full_names']} {m['staff_no']} {m['project']}".lower(): continue
        if kids=="yes" and clean(m["kid1"])=="—" and clean(m["kid2"])=="—": continue
        if kids=="no" and clean(m["kid1"])!="—": continue
        f.append(m)
    if sort=="project": f=sorted(f,key=lambda x:(x["project"] or "",x["full_names"] or ""))
    opts="".join([f"<option value='{p}' {'selected' if p==proj else ''}>{p}</option>" for p in projects])
    h=f"<form method='GET' class='card'><div class='row'><input name='q' value='{q}' placeholder='Search name, staff no...'><select name='project'><option value=''>All Projects</option>{opts}</select><select name='sort'><option value='name'>Sort: Name</option><option value='project' {'selected' if sort=='project' else ''}>Sort: Project</option></select><select name='kids'><option value=''>All</option><option value='yes' {'selected' if kids=='yes' else ''}>Has Kids</option><option value='no' {'selected' if kids=='no' else ''}>No Kids</option></select></div><br><div class='row'><button class='btn'>Apply Filters</button><a href='/members'><button type='button' class='btn2'>Clear</button></a></div><div class='chips'><a class='chip {'on' if not proj else ''}' href='/members'>All</a>"+"".join([f"<a class='chip {'on' if p==proj else ''}' href='/members?project={p}'>{p}</a>" for p in projects])+"</div></form>"
    h+=f"<p>Showing <b>{len(f)}</b> of {len(rows)}</p><div class='list'>"
    for m in f:
        kc=len([x for x in [clean(m[f'kid{i}']) for i in range(1,6)] if x!="—"])
        h+=f"<div class='member'><div class='avatar {pcolor(m['project'])}'>{initials(m['full_names'])}</div><div style='flex:1'><b>{m['full_names']}</b><br><small>Staff {clean(m['staff_no'])} • Joined {clean(m['month_joined'])}</small><br><span class='pill'>{m['project']}</span> <span class='pill ok'>{m['status']}</span><details><summary>View Family • {kc} kid(s)</summary><div class='fam'><div>Father<br>{clean(m['father_id'])}</div><div>Mother<br>{clean(m['mother_id'])}</div><div>Guardian<br>{clean(m['guardian_id'])}</div><div>Spouse<br>{clean(m['spouse_id'])}</div><div>Kid1<br>{clean(m['kid1'])}</div><div>Kid2<br>{clean(m['kid2'])}</div><div>Kid3<br>{clean(m['kid3'])}</div><div>Kid4<br>{clean(m['kid4'])}</div><div>Kid5<br>{clean(m['kid5'])}</div></div></details></div></div>"
    h+="</div>"
    return shell("Members",h,"Members")
@app.route("/register",methods=["GET","POST"])
def register():
    if request.method=="POST":
        f=request.form;name=f.get("full_names","").strip()
        if name:
            con=get_db();con.execute("INSERT INTO users (full_names,staff_no,project,month_joined,status,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5) VALUES (?,?,?,?, 'active member',?,?,?,?,?,?,?,?,?)",(name,f.get("staff_no",""),f.get("project",""),f.get("month_joined",""),f.get("father_id","-") or "-",f.get("mother_id","-") or "-",f.get("guardian_id","-") or "-",f.get("spouse_id","-") or "-",f.get("kid1","-") or "-",f.get("kid2","-") or "-",f.get("kid3","-") or "-",f.get("kid4","-") or "-",f.get("kid5","-") or "-"));con.commit();con.close();return redirect("/members")
    h="<form method='POST' class='card'><div class='row'><input name='full_names' required placeholder='Full Names'><input name='staff_no' placeholder='Staff No'><input name='project' placeholder='Project'><input name='month_joined' placeholder='Jun-26'><input name='father_id' placeholder='Father ID'><input name='mother_id' placeholder='Mother ID'><input name='guardian_id' placeholder='Guardian ID'><input name='spouse_id' placeholder='Spouse ID'><input name='kid1' placeholder='Kid 1'><input name='kid2' placeholder='Kid 2'><input name='kid3' placeholder='Kid 3'><input name='kid4' placeholder='Kid 4'><input name='kid5' placeholder='Kid 5'></div><br><button class='btn'>Add Member</button></form>"
    return shell("Register",h,"Register")
@app.route("/shareout")
def shareout():
    con=get_db();rows=con.execute("SELECT * FROM users WHERE status='active member'").fetchall();con.close();total=len(rows)*300;above=max(0,total-250000);share=above/len(rows) if rows else 0
    h=f"<div class='grid'><div class='stat'><b>{len(rows)}</b><span>Members</span></div><div class='stat'><b>Ksh {total:,}</b><span>Total</span></div><div class='stat'><b>Ksh {above:,}</b><span>Above 250k</span></div><div class='stat'><b>Ksh {round(share,2):,}</b><span>Per Member</span></div></div><div class='card'><table><tr><th>Name</th><th>Project</th><th>Share</th></tr>"
    for m in sorted(rows,key=lambda x:x["full_names"] or ""): h+=f"<tr><td>{m['full_names']}</td><td>{m['project']}</td><td>{round(share,2)}</td></tr>"
    return shell("Share-Out",h+"</table></div>","Share-Out")
@app.route("/history")
def history():
    con=get_db();rows=con.execute("SELECT * FROM history ORDER BY id DESC").fetchall();con.close()
    h="<div class='card'><table><tr><th>Name</th><th>Action</th><th>Date</th></tr>"+"".join([f"<tr><td>{r['full_names']}</td><td>{r['action']}</td><td>{r['date']}</td></tr>" for r in rows])+"</table></div>"
    return shell("History",h,"History")
@app.route("/community")
def community():
    h="<div class='card'><b>Officials</b><br>Marlon K. Ang'undu - Chairman, FIG - +254 707 780 807<br>Mary Ngotah - Gold Crown - 0719 203 286<br>Celestine Ouko - SC Johnsons - 0725 543 224<br>Irene Wamuyu - Nairobi Java - 0719 606 834<br>Jonathan Mutunga - Last Mile - 0719 555 326</div>"
    return shell("Community",h,"Community")
@app.route("/api/members")
def api_members():
    con=get_db();rows=con.execute("SELECT * FROM users ORDER BY full_names").fetchall();con.close()
    return jsonify([dict(m) for m in rows])
@app.route("/api/stats")
def api_stats():
    con=get_db();c=con.execute("SELECT COUNT(*) FROM users").fetchone()[0];con.close();return jsonify({"total":c})
@app.route("/api/notifications")
def api_notif():
    return jsonify([])
if __name__=="__main__":
    app.run(host="0.0.0.0",port=int(os.environ.get("PORT",10000)))
