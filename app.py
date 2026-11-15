from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
VERSION = "v162"
BF = 855759
RESERVE = 250000
DISTRIBUTABLE = BF - RESERVE
MONTHLY_RATE = 300
FULL_MONTHS = 12
SHARE_TABLE_2026 = {1:11,2:10,3:9,4:8,5:7,6:6,7:5,8:4,9:3,10:2,11:1}
ADMIN_KEY = "lonma_api_key_12345"
ADMIN_EMAIL = "admin@lonma.com"
ADMIN_PASS = "admin123"
PROJ = {"P":"Pwani Oil Products","S":"SC Johnson","H":"Higchem","A":"Antonia","J":"Java House","G":"GCB-MT","D":"GCB-TDs","Q":"HQ","M":"TF-MT","W":"TF WSL"}
PROJECTS = ["Antonia","GCB-MT","GCB-TDs","Higchem","HQ","Java House","Kanji","Pwani Oil Products","SC Johnson","TF WSL","TF-LM","TF-MT"]
def norm_project(p):
    p=(p or "").strip()
    if p in PROJ: return PROJ[p]
    m={"Antonio":"Antonia","ANTONIA":"Antonia","GCB":"GCB-MT","GCB-Ws":"GCB-TDs","GCB TDS":"GCB-TDs","HIGHCHEM":"Higchem","KHS":"Kanji","Kaysalt":"Kanji","Kenafric":"Kanji","LAB":"Kanji","JAVA":"Java House","Java":"Java House","PWANI":"Pwani Oil Products","Pwani":"Pwani Oil Products","SJ":"SC Johnson","Johnson":"SC Johnson","JOHNSON":"SC Johnson","TF":"TF WSL","TF-WS":"TF WSL","TF WS":"TF WSL","TF-LM":"TF-LM","TF LM":"TF-LM","TF-MT":"TF-MT","TF MT":"TF-MT"}
    if p in m: return m[p]
    up=" ".join(p.upper().split())
    if up in m: return m[up]
    return p or "Pwani Oil Products"
def project_badge(p):
    c={"Antonia":"#111111","Pwani Oil Products":"#E31E24","Java House":"#C1272D","SC Johnson":"#E23A3A","TF-MT":"#1B4F9C","TF-LM":"#1B4F9C","TF WSL":"#1B4F9C","GCB-MT":"#1E3A2A","GCB-TDs":"#1E3A2A"}.get(p,"#0F2233")
    return f"<span style='display:inline-flex;align-items:center;gap:8px'><span style='width:36px;height:36px;border-radius:10px;background:{c};color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:800;font-size:12px'>{p[:2].upper()}</span><b>{p}</b></span>"
SEED1 = """202731|P|2025|Angela Nyaguthii Gathege
202863|P|2025|Peter Olonde
202656|P|2025|Patrick Sifuna Wanjala
202679|P|2016|Jack Omondi Juma
202680|P|2016|Marlon Ang'undu Kikuyu
202712|P|Nov.2022|Laura Imali
202710|P|Dec.2020|Edith Kabera
202677|P|October.2024|Phoebe Anyango
202706|P|Aug.2021|Cynthia Awuor
202707|P|Nov.2021|Maureen Owino
202721|P|March .2023|Merceline Adhiambo
202705|P|Marh 2019|Odiembo Yvonne
202722|P|Dec.2023|Linet oduor
202746|P|Nov.2025|Divyan Dorcas
202708|P|Jan. 2020|Lilian muchuma
202711|P|Sept.2021|John Adiel
292932|P|May.2026|Milcah Otiende
280370|P|Sept. 2026|Lucy Mwende Mbatha
202697|P|Sept.2017|Naomi Mwango Abenga
202696|P|2015|Lydiah Nyaanga Osengo
202693|P|May.2022|Meggiling Abuga Nyakerario
202695|P|2022|Gorrety Adhiambo Otieno
202699|P|14/12/2022|Sophia Nyamoita Mokaya
202751|P|02/10/2023|Benjamin Odiwuor Mboya
202730|P|4.8.2025|Orwa Diana Atieno
202694|P|02/01/2020|Charles Adika
282000|P|01/05/2026|Hyphine chepkoech Mutai
202750|P|May.2025|Priscah Anjemo Injili
202698|P|14/02/2022|Postine Atieno
202744|P|01/03/2024|Anthony Manyara Chania
202683|P|01/03/2013|Eunice Makona
202700|P|01/03/2025|Charles kimutai Kirui
202709|P|01/03/2025|Oyoyo Yvonne Bentar
202678|P|01/03/2025|Owen Muthee Waithaka
202733|P|01/03/2025|Sharon Cherono
202529|P|01/03/2025|Alex Shangala
202729|P|01/03/2025|ROSE LUMONYA SAIDI
202747|P|01/07/2025|BRENDA NELIMA WAFULA
10405|P|01/03/2025|Diana Atieno Oduor
202749|P|01/03/2025|Celine Nasimiyu Wamalwa
292976|P|01/04/2026|Belinda chemtai
202702|P|01/05/2025|Betty Akinyi Namamba
202723|P|01/03/2025|Metrine Cherop Chumo
50516|P|01/05/2025|SHEILA ADISA VOLEMI
202701|P|01/03/2025|Everlyne mukoya Stephen
202703|P|01/03/2025|Caren Nanjala Chonge
202704|P|01/03/2025|Hellen Achieng Onyango
202724|P|01/03/2025|BENTA ACHIENG MURUKA
280472|P|01/09/2026|Samuel Kikweo Nthenya
202989|S|01/02/2026|Bonface Nzuki
202774|S|01/08/2024|Oscar kipkoech Ruto
90117|S|01/08/2022|Hilda Esende Lugangi
Lena Cherono|S|01/10/2026|Lena Cherono
202788|S|01/08/2023|Afline Anyango Onyango
202786|S|01/08/2022|Judith Oweya Lukale
202784|S|01/07/2025|Farida Olesi
Phesial Jaramogi Ooyi|S|01/08/2022|Phesial Jaramogi Ooyi
201743|S|25/04/2026|Zachary Joel Moriasi
202976|S|01/02/2026|Winfred mwende john
202782|S|01/12/2025|Victoria wangechi Mugwe
202775|S|01/02/2023|Milka Wawuda Mwang'ombe
202780|S|2022|Mokua Frankline
202765|S|01/08/2025|Hannah Warukira Mwangi
202977|S|26 Jan,2026|Emily Mueni Mutua
202764|S|August,2025|Agnes Wangu Mwangi
202769|S|01/08/2025|Joshua mwangi iguna
202761|S|Apr_25|Hannah wanjiku
202777|S|,Sept 2022|Caroline Kathomi Njebiu
202757|S|2024|Fedinand Kafwa
202772|S|,Feb 2025|Maureen Njeri
280267|S|,July 2026|Patrick Kabiu Waweru
202766|S|,April 2025|Veronica Mukolwe
202789|S|,Aug 2022|Celestine Auma Ouko
202641|H|18/05/2026|Irene Waeni Mwangangi
202657|H|16/06/2026|Isaac Ombati Rioba
202787|H|18/05/2026|Emily Nanjala Wafula
202998|H|18/05/2026|Millianna Anyango Sadaka
280005|H|18/05/2026|Faith Njeri Kibungi
280007|H|18/05/2026|Collins Ofula Mabwa
280008|H|18/05/2026|Wanga Atieno Beryl
280009|H|18/05/2026|Nelson Miruka Kiyondi
280012|H|18/05/2026|Robert Kariuki Macharia
280013|H|18/05/2026|Thomas Felix Mwatu
280014|H|18/05/2026|Mercy Nabulo Khabala
280078|H|28/05/2026|Joan Anyango Otewa
280266|H|08/07/2026|Anna Mbinya Kalia
280325|H|19/08/2026|Marion Waheto
280326|H|03/08/2026|Maureen Wanjiru Kiarie
280349|H|01/09/2026|Wicklife Okemwa Nyangaresi
Sherine Atieno|A|2025|Sherine Atieno Otieno
280225|A|2026|Stepheny Keziah Wambui Mwangi
"""SEED2 = """202640|J|06/01/2024|Samuel Njeru Njiru
202642|J|02/01/2023|Eugene Daudi Aura
202643|J|16/06/2023|Wamuyu Irene Wairimu
280226|J|22/06/2026|Alice Maina
292965|J|05/05/2026|Sylvia Agosa
202648|J|08/01/2022|Esther Wangari Karanja
202649|J|08/01/2023|Emily Waithera Njenga
280372|J|09/09/2026|Joan Ensha Wairimu
202651|J|15/04/2024|Edwin Ondieki Kiyaka
202652|J|23/11/2023|Gladys Kinuthia
280507|J|16/09/2026|Purity mukami
202654|J|17/05/2025|Samwel Erick Odhiambo
202655|J|04/01/2025|Felister Gatwiri Muriithi
202666|J|21/07/2026|Charity Moraa Juma
202660|J|01/01/2026|Brian Mwenda Njue
202661|J|11/11/2025|Emmanuel Mike Ochieng
202662|J|11/11/2025|Caroline Muthoni Mugo
202664|J|13/03/2026|Jeniffer Wanjira Ndung'u
202670|J|06/06/2025|Maureen Gathiru Mwaniki
202671|J|01/01/2025|Lilian Adhiambo Randa
202673|J|05/05/2024|Pauline Wambui Masila
202674|J|29/11/2023|Anne Kamonya Mulema
202675|J|06/06/2025|Daniel Ombui Mayaka
202934|J|01/01/2026|Jeff Otieno Maina
202935|J|01/01/2026|Jedida Njoki Kinyanjui
202937|J|02/02/2026|Clifton Kelvin Makokha
202952|J|01/01/2026|Collen Elizabeth Ojiambo
202978|J|02/02/2026|Jackline Wanza Muthoka
292915|J|05/05/2026|Francis Omari
202686|J|16/04/2026|Evaperpetual Wambui Maina
202603|J|01/09/2026|Mariam Juma
280528|J|11/01/2026|Hydrick Kipkorir
Kendy Njeri|J|01/11/2026|Kendy Njeri
Joseph Chege|J|01/11/2026|Joseph Chege
Specioza Matitsa|J|01/11/2026|Specioza Matitsa
202607|G|1st Dec 2019|Mary ngotah
202602|G|19th Dec|Hillary nzive kasiva
202609|G|11th Nov|Joan Atieno Odhiambo
202612|G|2025 November|purity ndunda
280322|G|01/08/2021|Nelson karani
292916|G|1st Aug 2026|Grace muthoni chege
202606|G|11th Nov 2022|peter omondi
202613|G|1st jan 2026|Joan wambui
292962|G|1st September 2026|Stephen Mwose
280265|G|1st July 2026|Caroline Maina
202610|G|15th November 2025|Mercy Wambui Njer
292964|G|1st june 2026|Mary Mbinya
280315|G|1st Aug 2026|Dorcas Mukenyi
202926|G|1st Jan ,2026|Stephen Mwalimu
202604|G|14th September 2020|Dennis Mbindyo Mwamuli
280321|G|19th August 2026|Geoffrey Matata Mbeva
202611|G|1st Dec 2025|Robert Muthui Matheka
202601|G|1st Feb 2011|Evelyne Mpinda Kinyua
202615|G|4th April 2019|Emiliana mwanaidi
202628|Q|2015|JANEDRIX AKINYI SADAKA
CELESTINE ATIENO SADAKA|Q|2015|CELESTINE ATIENO SADAKA
280314|Q|AUGUST 1ST 2026|LAZARUS OKECHI
PATRIC TITO|Q|2020|PATRIC TITO
292930|Q|AUGUST 1ST 2026|EDDY NYANGORI
202619|D|1ST SEP 2024|DENIS MUCHANGI WANJA
202617|D|1ST NOV 2023|CELESTINE ACHIENG
202622|D|24TH NOV 2025|ALEX MUKUNZA ODERA
202623|D|20TH JULY 2024|ESTHER AWUOR AGUTU
202964|D|1ST FEB 2026|PERIS WAITHERA GIKURU
202620|D|17TH MAR 2025|SHARROW IMAMI
280319|D|10TH OCT 2026|VIVIAN ATIENO OWUONDA
202942|D|2026 JAN|PAUL KHAEMBA WAFULA
280313|D|3RD AUG 2026|STEPHANIE WANJIRU
202618|D|1ST JULY 2023|JOACHIM BACHWA BACHWA
202973|M|Jan-26|Anastacia Mwende Mutua
202857|M|2025|Brenda joy nyongesa
Bryton Otieno okoth|M|Nov-26|Bryton Otieno okoth
292954|M|Feb-26|Christine Wangu namange
202879|M|2024|Daniel musyoka
202899|M|2023|Daniel Mwangi maina
202851|M|2024|Douglas lidoli lidundu
202898|M|2022|Elizabeth Kaluki mbithe
202838|M|2023|Elizabeth matinde
202856|M|2025|Elizabeth Silvia Botuba
202927|M|Jan-26|Esther syokau mosyoki
202847|M|2025|Esther Wanjiku
202853|M|2025|Eugene Ochieng
202886|M|2023|Faith Atieno
202850|M|2025|Getrude kisala
202855|M|2025|Jackline Njeri chomba
292982|M|Feb-26|Janevick moraa
202860|M|2025|Mark Alema Mbeche
Mary Wangari TFMT|M|2024|Mary Wangari
202881|M|2024|Melvin Mumo
"""
SEED3 = """202868|M|2025|Milka Waweru Nyambura
202843|M|2023|Mourin wangui karomo
202865|M|2025|Nyongesa rendson wekesa
202842|M|2025|Peninah awuor olang'o
202854|M|2025|Peter omoro
202872|M|2024|Philip Etale
292952|M|Feb-26|Protus Ojuma
Purity Opiyo Anyango|M|Nov-26|Purity Opiyo Anyango
202844|M|2025|purity Wambui
202880|M|2024|Scholastica kilonzi
202833|M|2025|Stephen Wesonga Ouma
Telvin gachanja|M|Jun-26|Telvin gachanja
202863TFMT|M|2023|Teresia Muthoni Kariuki
202864|M|2025|Vincent Otieno Okello
202870|M|2025|Vonter Moses Amuto
202846|M|2025|Willis Ogumbo othiambo
202876|M|2024|Jane wanjiru
202861|M|Mar-26|Ann Njoroge
202963|M|Oct-26|Fridah Gastaiti
Beryl Jeptoo|M|Jul-26|Beryl Jeptoo
202871|M|2024|Loureen Anyango Agutu
202891|M|2023|Maryanne Wanjiru Kariuki
Mercy Chepkemoi|M|2025|Mercy Chepkemoi
202885|M|2020|Mourine Akoth
280222|M|Apr-26|Shania Joy
202874|M|2025|Valary Chepkoech Bii
Vallary Akinyi|M|Jul-26|Vallary Akinyi
202878|M|2024|Brendah Achieng Gumba
280003|M|Jun-26|Brian Kang'ethe
202877|M|2025|Catherine Awino Agutu
202893|M|2023|Damaris Wekesa
Dorine Anyango Odongo|M|Nov-26|Dorine Anyango Odongo
202845|M|2025|Ebby Kageha lomosi
202867|M|2025|Eunice Wambui
202895|M|2014|Jane Wairimu
280220|M|Mar-26|Joseph Mumanyi
280507TFMT|M|Nov-26|Manase Karanja Thuo
70221|M|2023|Pamela Awuor Nyadodo
Bartholomew Wekesa musundi|M|Nov-26|Bartholomew Wekesa musundi
Rachael Gathoni wangigi|M|Oct-26|Rachael Gathoni wangigi
292979|M|Jul-26|Risper Moraa Momanyi
292959|M|Jul-26|Samuel onyango
202890|M|2023|John Mwangi
280270|M|Jul-26|Whitney Arot Aturae
202873|M|2023|Brian Ombwori Osese
202835|M|2024|Diana Nanjala wafula
202920|M|2025|Elvis Shikuku
202882|M|2023|Irene Ogutu
202859|M|Jan-26|Emma Watindi
202849|M|2025|Jacinta Apondi
202888|M|2017|Jackline Kavere Ayiga
202884|M|2024|Mercy Achieng Onyango
202889|M|2021|Naomi Jeruto Tanui
202839|M|2025|Otieno lavenda
202914|W|20-Jan-25|SAID ROSELINE HERI
202906|W|27-Mar-25|JECINTA KARANJA
202905|W|05-Feb-25|MARY ATIENO
202915|W|13-Jan-25|PAULINE MURATHI
202916|W|27-Jan-25|ANN NJERI KAREIYA
202913|W|13-Jan-25|TABITHA WANJIKU
202917|W|13-Jan-25|PRUDENCE ACHIENG WANYANGU
292943|W|15-Jan-26|LINDA NALIAKA JUMA
202908|W|12-Sep-25|PASCALINE NJOKI
202910|W|16-Oct-25|LUCY NYAMBURA
292977|W|18-Jul-05|DIANA MUSE
202907|W|22-Jul-26|JANET WAIRIMU
280293|W|13-Jul-26|CATHERINE MUKAMI
"""
SEED_TXT = SEED1 + SEED2 + SEED3
FARES_TXT = """P1|Peter Ikegu|0704886421|1000|65;P1|George Ibuba|0113964865|1000|65;P1|Kevin Kipkurui|0704284388|1000|65;P1|Valary Chepkoech|0713053696|1500|65;P1|Mercy Njeri|0713881793|1500|65;P1|Margaret Wangari|0720331094|1000|65;P1|Mary Wangare|0796805933|1000|65;P1|Daniel Mayaka|0722620252|1000|65;P1|Unnamed|-|1000|65;P1|Unnamed|-|1000|65;P1|Unnamed|-|1000|65;P1|Rose|-|3000|65;P1|Jecinta Apondi|-|1000|65;P1|Mercy Onyango|-|1000|65;P1|Preskila Ondiek|-|1000|65;P1|Jane Wangari|-|1500|65;P1|Caroline Wachira|-|1500|65;P1|Joy|-|1500|65;P1|Berbciter|-|1500|65;P1|Irene Wamuyu|0719606834|1000|65;P1|Ann Mulema|0729218786|1000|65;P1|Gloria Luksenaka|0796426074|1000|65;P1|Mary Thika|0719572174|1000|65;P1|Joshua Iguna|0792529926|1000|65;P1|Jackline Kamau|0724562145|1000|65;P2|Eunice Makona|0714910135|1200|100;P2|Hellen Onyango|0724570228|1200|100;P2|Caren Chonge|0710427468|900|100;P2|Antony Mwendia|-|1500|100;P2|Gladys Nyaga|-|1500|100;P2|Marlon K. Angundu|-|1200|100;P2|Gladys Wambaire Kinuthia|-|1200|100;P2|Evapertual Wambui|-|1200|100;P2|Catheine Ogutu|-|1700|100;P2|Ebby Lomoi|-|1700|100;P2|Jackline Ayiga|-|1700|100;P2|Esther Marenya|-|1600|100;P2|George Odhiambo|-|1400|100;P2|Kiplimo|-|4200|100;P2|Maureen Njeri Kamunyu|-|1500|100;P2|Eunice Wairimu|-|2000|100;P2|Victoria Wangechi Mugwe|-|2000|100;P2|Unnamed|-|500|100;P2|Marlon K. Angundu|-|600|100;P2|Patrick Macharia Mugo|-|600|100;P2|Stepheny Keziah Wambui Mwangi|-|600|100"""
BEN_TXT = """P1|Mary Ngota|GCB|Dad-Death|01/11/2024|30000|100;P1|Mariamu|GCB|Dad-Death|01/12/2024|30000|100;P1|Claire Osiako|Kaysalt|Dad-Death|02/12/2024|30000|100;P1|Rachael Ndungu|Pwani|Mum-Death|10/12/2024|30000|100;P1|Teresih Kariuki|TF|Dad-Death|17/12/2024|30000|100;P1|Hannah Ngaruiya|Pwani|Loss of earning|04/12/2024|9500|100;P1|Hannah Ngaruiya|Pwani|Loss of earning|02/01/2025|9500|100;P1|Hannah Ngaruiya|Pwani|Loss of earning|02/02/2025|9500|100;P1|Unnamed|SJ|Daughter-Death|-|30000|100;P1|Jecinta Nduta Karanja|TF|Loss of earning|-|9000|100;P1|Winnie|TF B|Dad-Death|-|30000|100;P1|Maureen Kiare|Kenafric|Dad-Death|July|30000|100;P1|Eugene Otieno|TF|Dad-Death|July|30000|100;P1|Ann Wambui Muchemi|Java|Loss of earning|Aug 2025|22000|100;P1|Mercy Mwikali|TF|Guardian|Aug 2025|30000|100;P1|Ann Wambui Muchemi|Java|Loss of earning|Aug 2025|11000|100;P1|Annah Nthamba Musyoki|Java|Dad-Death|Sep 2025|30000|100;P1|Eunice Wairimu Wanjiku|SJ|Dad-Death|Oct 2025|30000|100;P1|JJJJ|-|Loss of earning|-|11500|100;P1|Nostar|TF|Loss of earning|-|19000|100;P2|Rose Lumonya Saidi|POPL|Death-Father|01/12/2025|40000|100;P2|Nostar|TF|Loss of earning|01/12/2025|19000|100;P2|Susan Ndungu|TF|Death-Father|26/01/2026|40000|100;P2|Irene Wairimu|Java|Death-Guardian|01/05/2026|40000|100;P2|Mercy Mwende|GCB|Loss of earning|01/05/2026|11075|100;P2|Damarais Muyoka|TF|Death-Father|01/05/2026|40000|100;P2|Ruth Amollo Nyangun|-|Death-Father|01/06/2026|40000|100;P2|Sheila Okomo|TF|Loss of earning|May|9000|100;P2|Sheila Okomo|TF|Loss of earning|June|9000|100;P2|Unnamed|TF|Death-Father|-|40000|100;P2|Vivian Moraa|Java|Loss of earning|-|11000|100;P2|Hannah Wanjiku|TF|Death-Father|17/08/2026|40000|100;P2|Sherine Atieno Otieno|Antonia|Mother-Death|Nov 2026|40000|100"""
def parse_fares():
    o=[]
    for l in FARES_TXT.strip().split(";"):
        a=l.split("|")
        if len(a)==5: o.append((a[0],a[1],a[2],int(a[3]),int(a[4])))
    return o
def parse_ben():
    o=[]
    for l in BEN_TXT.strip().split(";"):
        a=l.split("|")
        if len(a)==7: o.append((a[0],a[1],a[2],a[3],a[4],int(a[5]),int(a[6])))
    return o
FARES = parse_fares()
BENEF = parse_ben()
MONTHS_2425 = ["Oct 24","Nov 24","Dec 24","Jan 25","Feb 25","Mar 25","Apr 25","May 25","Jun 25","Jul 25","Aug 25","Sep 25","Oct 25","Nov 25","Dec 25"]
MONTHLY_2425 = [("Pwani",[24600,23700,22500,24900,21600,21900,21600,21300,21900,21600,21300,21300,21300,21000,0]),("Java",[8700,8400,8700,9300,7800,7800,8700,8100,9600,9300,9600,8700,9600,9300,0]),("Johnson",[10500,10800,10200,9300,9000,9000,10200,9900,10200,9900,10200,10200,10200,9600,0]),("Kaysalt",[9600,9600,9300,9600,9000,8400,8700,8700,0,0,0,0,0,0,0]),("Kanji",[900,900,900,900,900,900,900,900,900,900,900,900,900,900,0]),("HQ",[900,0,1800,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,1200,0]),("GCB-MT",[5400,4800,5100,4800,4800,4800,5100,5700,4800,4800,4800,4800,5100,5100,0]),("TF WSL",[3300,3300,3000,6300,6900,6900,5700,5100,5100,5700,5400,4800,4800,4800,0]),("TF-LM",[11700,12300,12300,11700,13200,13200,12600,12600,12300,12300,12000,12000,12600,12300,0]),("TF-MT",[19200,18000,17700,19800,17700,18000,18600,18000,18900,18000,18600,18300,18600,20100,0]),("Kenafric",[0,0,0,0,11700,12000,12300,12000,12300,12000,12600,12000,0,0,0]),("GCB-TDs",[3300,3600,3900,3900,4200,3900,5100,4800,3900,3600,3300,2400,2400,2700,0]),("LAB",[0,0,0,0,0,0,0,2400,3000,2400,0,0,0,0,0])]
TOTAL_2425_MONTH = [98100,95400,95400,101700,108000,108000,110700,110700,104100,101700,99900,96600,86700,87000,0]
MONTHS_2026 = ["Dec 25","Jan 26","Feb 26","Mar 26","Apr 26","May 26","Jun 26","Jul 26","Aug 26","Sep 26","Oct 26","Nov 26"]
MONTHLY_2026 = [("Pwani",[21000,20400,21300,21000,21300,21600,21300,21600,20700,15300,14700,0]),("Java House",[9000,9600,9900,9900,9600,9300,9600,9300,9900,9900,10200,0]),("SC Johnson",[10500,9600,10200,9900,9900,9300,8400,8700,8700,8100,8100,0]),("Kanji",[900,900,900,900,900,900,900,900,900,900,900,0]),("HQ",[1200,1200,1200,1200,1200,1200,1200,1200,1500,1500,1500,0]),("GCB-MT",[4500,4500,4800,4800,4800,4500,6000,5100,6000,5700,6000,0]),("TF WSL",[4800,5100,4800,4800,4800,4500,4500,4200,3900,3900,3900,0]),("TF-LM",[12300,12300,11700,11700,12600,9300,9000,9900,10200,12000,11400,0]),("TF-MT",[19800,20700,21900,22200,21300,21300,21900,21900,22200,21900,21000,0]),("GCB-TDs",[2700,3000,3000,3300,3600,3600,3600,3600,4800,5100,4800,0]),("Higchem",[0,0,0,0,0,4800,5100,5100,5400,4800,4800,0]),("Antonia",[0,0,0,0,0,0,900,900,600,600,600,0])]
TOTAL_2026_MONTH = [86700,87300,89700,89700,90000,90300,92400,92400,94800,89700,87900,0]
def clean(v):
    if v is None: return ""
    s=str(v).strip()
    if s.upper() in ("NA","N/A","-","NONE","LATER","NULL","NIL"): return ""
    return s
def make_email(n, staff):
    p=[x for x in n.lower().replace(".","").split() if x.isalpha()]
    return f"{p[0]}.{p[-1]}@figbrands.co.ke" if len(p)>=2 else f"{p[0] if p else 'member'}.{staff}@figbrands.co.ke"
MONTHS_MAP = {"january":1,"february":2,"march":3,"april":4,"may":5,"june":6,"july":7,"august":8,"september":9,"october":10,"november":11,"december":12,"jan":1,"feb":2,"mar":3,"apr":4,"jun":6,"jul":7,"aug":8,"sep":9,"sept":9,"oct":10,"nov":11,"dec":12}
def parse_join(s):
    if not s: return None
    t=str(s).strip().lower()
    t=re.sub(r"(\d+)(st|nd|rd|th)\b",r"\1",t)
    t=t.replace(","," ").replace("."," ").replace("_"," ").replace("/"," ").replace("-"," ")
    t=re.sub(r"\s+"," ",t).strip()
    if not t: return None
    m=re.search(r"(\d{1,2})\s+(\d{1,2})\s+(\d{4})",t)
    if m:
        d,mo,y=int(m.group(1)),int(m.group(2)),int(m.group(3))
        if mo>12: d,mo=mo,d
        if 1<=mo<=12: return (y,mo)
    for mon in sorted(MONTHS_MAP,key=len,reverse=True):
        mm=re.search(r"\b"+mon+r"\b\s+(\d{1,2})\s+(\d{4})",t)
        if mm: return (int(mm.group(2)),MONTHS_MAP[mon])
        mm=re.search(r"(\d{1,2})\s+\b"+mon+r"\b\s+(\d{4})",t)
        if mm: return (int(mm.group(2)),MONTHS_MAP[mon])
        mm=re.search(r"\b"+mon+r"\b\s+(\d{4})",t)
        if mm: return (int(mm.group(1)),MONTHS_MAP[mon])
        mm=re.search(r"\b"+mon+r"\b\s+(\d{2})\b",t)
        if mm:
            yy=int(mm.group(1)); return (2000+yy if yy<50 else 1900+yy,MONTHS_MAP[mon])
    m=re.search(r"(\d{4})",t)
    if m: return (int(m.group(1)),1)
    return None
def share_basis(join_str):
    p=parse_join(join_str)
    if not p: return (FULL_MONTHS,"Joined before 2025 - Full share")
    y,m=p
    if y<2025: return (FULL_MONTHS,"Joined before 2025 - Full share")
    if y==2025: return (FULL_MONTHS,"Joined 2025 - Full share")
    if y==2026:
        if m not in SHARE_TABLE_2026: return (0,"Joined after Nov 2026 - No share")
        mo=SHARE_TABLE_2026[m]
        return (mo,f"Joined {m:02d}/2026 - Pro-rated {mo} months")
    return (0,"Joined after Nov 2026 - No share")
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
        mo,basis=share_basis(r["month_joined"])
        out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","months":mo,"basis":basis,"contribution":mo*MONTHLY_RATE,"share":0.0,"per_month":0.0,"badge":project_badge(norm_project(r["project"]))})
    tm=sum(x["months"] for x in out); tc=sum(x["contribution"] for x in out); rate=DISTRIBUTABLE/tm if tm else 0
    for x in out: x["per_month"]=round(rate,2); x["share"]=round(x["months"]*rate,2)
    diff=round(DISTRIBUTABLE-sum(x["share"] for x in out),2)
    if out and diff!=0:
        out.sort(key=lambda x: x["share"],reverse=True); out[0]["share"]=round(out[0]["share"]+diff,2)
    out.sort(key=lambda x: x["share"],reverse=True)
    return out,tc,tm,rate
def add_user(c,staff,names,project,month):
    staff=clean(staff); names=clean(names); project=norm_project(project)
    if not staff or not names: return False
    if c.execute("SELECT id FROM users WHERE staff_no=?",(staff,)).fetchone(): return False
    if c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(names,)).fetchone(): return False
    email=make_email(names,staff)
    if c.execute("SELECT id FROM users WHERE email=?",(email,)).fetchone(): email=f"member.{staff}@figbrands.co.ke"
    vals=(staff,names,project,email,generate_password_hash(staff),"fig_"+secrets.token_hex(12),clean(month),"","","","","","","","","")
    c.execute("INSERT INTO users (staff_no,full_names,project,email,password,api_key,month_joined,father_id,mother_id,guardian_id,spouse_id,kid1,kid2,kid3,kid4,kid5,photo) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)",vals)
    return True
def init_db():
    c=get_db()
    c.execute('CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, staff_no TEXT, full_names TEXT, project TEXT, email TEXT UNIQUE, password TEXT, role TEXT, phone TEXT, api_key TEXT, is_protected INTEGER DEFAULT 0, month_joined TEXT, father_id TEXT, mother_id TEXT, guardian_id TEXT, spouse_id TEXT, kid1 TEXT, kid2 TEXT, kid3 TEXT, kid4 TEXT, kid5 TEXT, photo TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS notifications (id INTEGER PRIMARY KEY AUTOINCREMENT, title TEXT, msg TEXT, created TEXT)')
    c.execute('CREATE TABLE IF NOT EXISTS support_msgs (id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT, msg TEXT, created TEXT)')
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
    for line in SEED_TXT.strip().splitlines():
        parts=[x.strip() for x in line.split("|")]
        if len(parts)<4: continue
        staff,code,month,names=parts[0],parts[1],parts[2],parts[3]
        project=norm_project(code)
        ex=c.execute("SELECT id FROM users WHERE staff_no=?",(clean(staff),)).fetchone()
        if ex:
            c.execute("UPDATE users SET full_names=?,project=?,month_joined=? WHERE staff_no=?",(clean(names),project,clean(month),clean(staff))); continue
        ex2=c.execute("SELECT id FROM users WHERE lower(full_names)=lower(?)",(clean(names),)).fetchone()
        if ex2:
            c.execute("UPDATE users SET staff_no=?,project=?,month_joined=? WHERE id=?",(clean(staff),project,clean(month),ex2["id"])); continue
        if add_user(c,staff,names,project,month): added+=1
    c.commit(); c.close(); print(f"{VERSION} seeded 247 added {added}")
init_db()
@app.after_request
def after(r):
    r.headers.add('Access-Control-Allow-Origin','*'); r.headers.add('Access-Control-Allow-Headers','Content-Type,X-API-KEY'); r.headers.add('Access-Control-Allow-Methods','GET,POST,DELETE,OPTIONS'); return r
@app.route("/favicon.ico")
def favicon():
    svg='<svg xmlns="http://www.w3.org/2000/svg" width="64" height="64"><rect width="64" height="64" rx="14" fill="#0A1F33"/><text x="32" y="42" font-family="Georgia, serif" font-size="24" font-weight="700" fill="#C9A86A" text-anchor="middle">FIG</text></svg>'
    return svg,200,{"Content-Type":"image/svg+xml"}def shell(title,body):
    h=[]
    h.append("<!DOCTYPE html><html><head><meta name=\"viewport\" content=\"width=device-width,initial-scale=1\">")
    h.append("<title>"+title+" | F.I.G Brands Welfare</title>")
    h.append("<style>")
    h.append("body{font-family:Inter,Arial,sans-serif;background:#F4F5F7;color:#1A2332;margin:0;padding-bottom:92px;font-size:15px;line-height:1.55}")
    h.append("h1{font-size:28px;margin:0 0 8px;color:#0F2233}h2{font-size:18px;margin:0 0 8px;color:#0F2233}")
    h.append(".top{height:60px;background:#fff;display:flex;align-items:center;gap:12px;padding:0 16px;position:sticky;top:0;z-index:20;border-bottom:1px solid #E7E7E7}")
    h.append(".brandmark{width:38px;height:38px;background:#0F2233;color:#fff;border-radius:9px;display:flex;align-items:center;justify-content:center;font-weight:800;cursor:pointer}")
    h.append(".toplinks{background:#fff;border-bottom:1px solid #E7E7E7;padding:10px 16px;display:flex;gap:18px;flex-wrap:wrap;position:sticky;top:60px;z-index:15}")
    h.append(".toplinks a{color:#344054;text-decoration:none;font-size:13px;font-weight:600}")
    h.append(".page{max-width:1040px;margin:auto;padding:20px 16px}")
    h.append(".card{background:#fff;border:1px solid #EDEDED;border-radius:14px;padding:20px;margin-bottom:14px}")
    h.append(".input{width:100%;height:46px;border:1px solid #D0D5DD;border-radius:10px;padding:0 13px;background:#fff;font-size:14px}")
    h.append(".btn{width:100%;height:46px;background:#0F2233;color:#fff;border:0;border-radius:10px;font-weight:600;cursor:pointer}")
    h.append(".btn2{display:inline-block;background:#0F2233;color:#fff;padding:10px 16px;border-radius:999px;text-decoration:none;font-weight:600;font-size:13px}")
    h.append(".btn2.gold{background:#B9975B;color:#fff}.grid{display:grid;grid-template-columns:1fr 1fr;gap:14px}")
    h.append(".kpi{background:#fff;border:1px solid #EDEDED;border-radius:14px;padding:18px}.kpi div:first-child{font-size:11px;letter-spacing:.08em;text-transform:uppercase;color:#667085;font-weight:600}.kpi h2{font-size:30px;margin:8px 0 2px}")
    h.append(".hero{background:#0F2233;color:#fff;border-radius:16px;padding:24px}.hero h1{color:#fff;font-size:34px}.hero p{color:#D0D5DD}")
    h.append(".nav{position:fixed;left:0;right:0;bottom:0;height:64px;background:#fff;border-top:1px solid #E7E7E7;display:flex;z-index:30;padding:6px 8px}.nav a{flex:1;color:#667085;text-decoration:none;display:flex;flex-direction:column;align-items:center;justify-content:center;font-size:11px;font-weight:600}")
    h.append(".row{display:flex;justify-content:space-between;gap:12px;padding:12px 0;border-bottom:1px solid #F2F4F7}")
    h.append("table{width:100%;border-collapse:collapse;font-size:13px}th,td{padding:11px 10px;border-bottom:1px solid #F2F4F7;text-align:left}th{font-size:11px;letter-spacing:.06em;text-transform:uppercase;color:#667085}.num{text-align:right;white-space:nowrap}")
    h.append(".chip{display:inline-block;border:1px solid #D0D5DD;background:#fff;border-radius:999px;padding:8px 14px;font-size:13px;font-weight:600;cursor:pointer;color:#344054}.chip.on{background:#0F2233;color:#fff}")
    h.append(".postimg{width:100%;border-radius:12px;margin-top:10px;max-height:420px;object-fit:cover}.postvideo{width:100%;border-radius:12px;margin-top:10px;max-height:420px;background:#000}")
    h.append(".side{position:fixed;inset:0;background:rgba(15,34,51,.45);display:none;z-index:99}.side.show{display:block}.sidepanel{position:absolute;left:0;top:0;bottom:0;width:300px;max-width:86vw;background:#0F2233;color:#fff;padding:22px 16px;overflow-y:auto}.sidepanel a{display:flex;gap:12px;color:#E7EAF0;text-decoration:none;font-size:14.5px;padding:11px 12px;border-radius:10px}")
    h.append(".popup{position:fixed;inset:0;background:rgba(15,34,51,.45);display:none;align-items:flex-end;justify-content:center;z-index:99}.popup.show{display:flex}.pop{background:#fff;width:100%;max-width:520px;border-radius:16px 16px 0 0;padding:20px;max-height:86vh;overflow:auto}")
    h.append("@media(max-width:640px){.grid{grid-template-columns:1fr}.hero h1{font-size:28px}}")
    h.append("</style></head><body>")
    h.append("<div class=\"top\"><div class=\"brandmark\" onclick=\"openSide()\">FIG</div><div><b>F.I.G Brands</b><div style=\"font-size:10px;letter-spacing:.16em;color:#667085;font-weight:600\">WELFARE SYSTEM</div></div><div style=\"margin-left:auto;display:flex;gap:8px\"><button onclick=\"openBell()\" style=\"width:38px;height:38px;border:1px solid #E7E7E7;background:#fff;border-radius:999px;cursor:pointer\">B</button><button onclick=\"openSupport()\" style=\"width:38px;height:38px;border:1px solid #E7E7E7;background:#fff;border-radius:999px;cursor:pointer\">?</button></div></div>")
    h.append("<div class=\"toplinks\"><a href=\"/\">Overview</a><a href=\"/members\">Members</a><a href=\"/register\">Register</a><a href=\"/shareout\">Share-Out</a><a href=\"/breakdown2\">History</a><a href=\"/community\">Community</a><a href=\"/friends\">Friends</a><a href=\"/terms\">Terms</a><a href=\"/admin\">Admin</a></div>")
    h.append("<div class=\"page\">"+body+"<div style=\"text-align:center;color:#98A2B3;font-size:12px;padding:18px 0 4px\">F.I.G Brands Welfare - marlonkikuyu@gmail.com - 0707 780 807</div></div>")
    h.append("<div class=\"side\" id=\"sideMenu\" onclick=\"if(event.target===this)closeSide()\"><div class=\"sidepanel\"><div style=\"display:flex;justify-content:space-between\"><b>F.I.G Brands</b><button onclick=\"closeSide()\" style=\"border:1px solid rgba(255,255,255,.2);background:transparent;color:#fff;border-radius:999px;width:32px;height:32px;cursor:pointer\">X</button></div><a href=\"/\">Overview</a><a href=\"/members\">Members</a><a href=\"/register\">Register Member</a><a href=\"/shareout\">Share-Out</a><a href=\"/breakdown2\">History</a><a href=\"/terms\">Terms</a><a href=\"/community\">Community</a><a href=\"/friends\">Friends</a><a href=\"/admin\">Admin</a><a href=\"/download/excel\">Download Excel</a></div></div>")
    h.append("<div class=\"popup\" id=\"bellPopup\" onclick=\"if(event.target===this)closeBell()\"><div class=\"pop\"><b>Notifications</b><div id=\"notifList\"></div><button class=\"btn\" onclick=\"markRead()\" style=\"margin-top:12px\">Mark all as read</button></div></div>")
    h.append("<div class=\"popup\" id=\"supportPopup\" onclick=\"if(event.target===this)closeSupport()\"><div class=\"pop\"><b>Contact Support</b><p><a href=\"https://wa.me/254707780807\" target=\"_blank\">WhatsApp 0707 780 807</a> - <a href=\"mailto:info@figbrands.co.ke\">info@figbrands.co.ke</a></p><input class=\"input\" id=\"supName\" placeholder=\"Your name\"><textarea id=\"supMsg\" class=\"input\" style=\"height:96px;margin-top:12px\" placeholder=\"Message\"></textarea><button class=\"btn\" onclick=\"sendSupport()\" style=\"margin-top:14px\">Send</button><p id=\"supStatus\"></p></div></div>")
    h.append("<nav class=\"nav\"><a href=\"/\">Home</a><a href=\"/members\">Members</a><a href=\"/community\">Community</a><a href=\"/friends\">Friends</a><a href=\"/register\">Add</a></nav>")
    h.append("<script>")
    h.append("function badge(p){return '<span style=\"display:inline-flex;align-items:center;gap:8px\"><span style=\"width:36px;height:36px;border-radius:10px;background:#0F2233;color:#fff;display:inline-flex;align-items:center;justify-content:center;font-weight:800\">'+p.slice(0,2).toUpperCase()+'</span><b>'+p+'</b></span>'}")
    h.append("function openSide(){document.getElementById('sideMenu').classList.add('show')}")
    h.append("function closeSide(){document.getElementById('sideMenu').classList.remove('show')}")
    h.append("async function openBell(){document.getElementById('bellPopup').classList.add('show');let r=await fetch('/api/notifications');let d=await r.json();document.getElementById('notifList').innerHTML=d.notifications.map(function(n){return '<div style=\"padding:10px 0;border-bottom:1px solid #eee\"><b>'+n.title+'</b><div>'+n.msg+'</div></div>'}).join('')||'No notifications'}")
    h.append("function closeBell(){document.getElementById('bellPopup').classList.remove('show')}")
    h.append("async function markRead(){await fetch('/api/notifications/read',{method:'POST'});closeBell()}")
    h.append("function openSupport(){document.getElementById('supportPopup').classList.add('show')}")
    h.append("function closeSupport(){document.getElementById('supportPopup').classList.remove('show')}")
    h.append("async function sendSupport(){let r=await fetch('/api/support',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({name:document.getElementById('supName').value,msg:document.getElementById('supMsg').value})});let j=await r.json();document.getElementById('supStatus').textContent=j.message}")
    h.append("</script></body></html>")
    return render_template_string("".join(h))
@app.route("/")
def home():
    p=[]
    p.append("<div style=\"font-size:11px;letter-spacing:.14em;color:#B9975B;font-weight:700\">F.I.G BRANDS - WELFARE</div><h1>Overview</h1>")
    p.append("<p style=\"color:#475467\">Balance brought forward, less KES 250,000 retained - shared fairly, per month. Period Dec 2025 - Nov 2026.</p>")
    p.append("<div class=\"grid\"><div class=\"kpi\"><div>Total Members</div><h2 id=\"total\">0</h2></div><div class=\"kpi\"><div>Projects</div><h2 id=\"projCount\">0</h2></div></div>")
    p.append("<div class=\"hero\" style=\"margin-top:14px\"><div style=\"font-size:11px;letter-spacing:.14em;color:#B9975B;font-weight:700\">BALANCE BROUGHT FORWARD</div><h1>KES 855,759</h1><p>KES 605,759 to share - KES 250,000 retained</p></div>")
    p.append("<div class=\"grid\" style=\"margin-top:14px\"><div class=\"kpi\"><div>Amount to Share</div><h2>KES 605,759</h2></div><div class=\"kpi\"><div>Retained</div><h2>KES 250,000</h2></div><div class=\"kpi\"><div>Value of One Month</div><h2 id=\"oneMonth\" style=\"font-size:24px\">-</h2><div id=\"oneMonthNote\" style=\"color:#667085;font-size:13px\"></div></div></div>")
    p.append("<div class=\"card\" style=\"margin-top:14px\"><h2>Fair Share-Out Rule</h2><p style=\"color:#475467\"><b>Joined before 2025 = Full 12 months.</b> Joined 2025 = Full 12 months. Joined 2026 = Pro-rated: Jan 11, Feb 10, Mar 9, Apr 8, May 7, Jun 6, Jul 5, Aug 4, Sep 3, Oct 2, Nov 1.</p><a class=\"btn2\" href=\"/shareout\">View Share-Out Schedule</a></div>")
    p.append("<div class=\"card\"><h2>Combined Expenses</h2><table><tr><th>Expense</th><th class=\"num\">Combined</th></tr><tr><td>Beneficiaries (incl. transactions)</td><td class=\"num\">KES 843,375</td></tr><tr><td>Fares (incl. transactions)</td><td class=\"num\">KES 63,725</td></tr><tr><td>Bank / Transfer</td><td class=\"num\">KES 14,866</td></tr><tr><td><b>Total Expenses Combined</b></td><td class=\"num\"><b>KES 921,966</b></td></tr></table><a class=\"btn2 gold\" href=\"/breakdown2\">View Full History</a></div>")
    p.append("<div class=\"card\"><h2>Project Distribution</h2><div id=\"breakdown\"></div></div>")
    p.append("<script>async function load(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('total').textContent=d.total_members;document.getElementById('projCount').textContent=d.projects_total;let h='';Object.keys(d.projects_breakdown).sort().forEach(function(k){h+='<div class=\"row\"><b>'+badge(k)+'</b><span>'+d.projects_breakdown[k]+'</span></div>'});document.getElementById('breakdown').innerHTML=h;}catch(e){}try{let r2=await fetch('/api/shareout');let s=await r2.json();document.getElementById('oneMonth').textContent='KES '+s.per_month_rate.toFixed(2);document.getElementById('oneMonthNote').textContent='605,759 / '+s.total_months+' months';}catch(e){}}load();</script>")
    return shell("Overview","".join(p))
@app.route("/terms")
def terms_page():
    p=[]
    p.append("<h1>Terms and Policies</h1>")
    p.append("<div class=\"card\"><h2>Death Benefits</h2><table><tr><th>Beneficiary</th><th>Benefit</th></tr><tr><td>Member</td><td>KES 100,000</td></tr><tr><td>Spouse</td><td>KES 50,000</td></tr><tr><td>Child</td><td>KES 40,000</td></tr><tr><td>Parents</td><td>KES 40,000</td></tr></table><p>Spouse must be registered. Child: birth certificate required. Parents: cover applies only to principal member. Birth certificate + parent ID required. No biological parents: may nominate one guardian.</p></div>")
    p.append("<div class=\"card\"><h2>Loss of Earning</h2><p>50% of basic pay, max KES 20,000, after 10 days unable to work due to injury at work. Paid at end of month.</p></div>")
    p.append("<div class=\"card\"><h2>Contribution</h2><p>KES 300 monthly, deducted from pay.</p></div>")
    p.append("<div class=\"card\"><h2>Year-End</h2><p>Minimum balance KES 250,000. Excess shared only among current active members. FIG Year-End 30 November. Audited accounts by 20 December.</p></div>")
    p.append("<div class=\"card\"><h2>Officials</h2><p>Marlon K. Angundu - Chairman - 0707 780 807 - marlonkikuyu@gmail.com<br>Mary Ngotah - GCB - 0719 203 286<br>Celestine Ouko - SC Johnson - 0725 543 224<br>Irene Wamuyu - Java - 0719 606 834<br>Jonathan Mutunga - Trufoods Last Mile - 0719 555 326</p></div>")
    return shell("Terms","".join(p))
@app.route("/breakdown2")
def breakdown2_page():
    h=[]
    h.append("<h1>Full History - Professional Combined</h1><p style=\"color:#475467\">All expenses combined. Source: 111F.I.G_Staff_Welfare.xlsx BREAKDOWN + 2026.</p>")
    h.append("<div class=\"hero\"><div style=\"font-size:11px;letter-spacing:.14em;color:#B9975B;font-weight:700\">BALANCE BROUGHT FORWARD - AGREED</div><h1>KES 855,759</h1><p>605,759 to share + 250,000 retained = 855,759</p></div>")
    h.append("<div class=\"card\"><h2>1. Combined Expenses - ALL Expenses Combined</h2><table><tr><th>Expense line</th><th class=\"num\">Period 1</th><th class=\"num\">Period 2</th><th class=\"num\">Combined</th></tr><tr><td>Fares paid</td><td class=\"num\">30,000</td><td class=\"num\">30,000</td><td class=\"num\">60,000</td></tr><tr><td>Fares transaction charges</td><td class=\"num\">1,625</td><td class=\"num\">2,100</td><td class=\"num\">3,725</td></tr><tr><td><b>Fares total</b></td><td class=\"num\"><b>31,625</b></td><td class=\"num\"><b>32,100</b></td><td class=\"num\"><b>63,725</b></td></tr><tr><td>Beneficiaries paid</td><td class=\"num\">461,000</td><td class=\"num\">379,075</td><td class=\"num\">840,075</td></tr><tr><td>Beneficiaries transaction charges</td><td class=\"num\">2,000</td><td class=\"num\">1,300</td><td class=\"num\">3,300</td></tr><tr><td><b>Beneficiaries total</b></td><td class=\"num\"><b>463,000</b></td><td class=\"num\"><b>380,375</b></td><td class=\"num\"><b>843,375</b></td></tr><tr><td>Bank transaction charges</td><td class=\"num\">0</td><td class=\"num\">14,400</td><td class=\"num\">14,400</td></tr><tr><td>Transfer charges</td><td class=\"num\">0</td><td class=\"num\">466</td><td class=\"num\">466</td></tr><tr><td><b>Bank / Transfer total</b></td><td class=\"num\"><b>0</b></td><td class=\"num\"><b>14,866</b></td><td class=\"num\"><b>14,866</b></td></tr><tr><td><b>TOTAL EXPENSES COMBINED</b></td><td class=\"num\"><b>494,625</b></td><td class=\"num\"><b>427,341</b></td><td class=\"num\"><b>921,966</b></td></tr></table><p>Check: 63,725 + 843,375 + 14,866 = 921,966</p></div>")
    h.append("<div class=\"card\"><h2>2. Contributions Summary</h2><table><tr><th>Period</th><th class=\"num\">Contributions</th><th class=\"num\">Expenses</th><th class=\"num\">Surplus</th></tr><tr><td>Period 1 Oct 24 - Dec 25</td><td class=\"num\">1,404,000</td><td class=\"num\">494,625</td><td class=\"num\">909,375</td></tr><tr><td>Period 2 Dec 25 - Nov 26</td><td class=\"num\">991,100</td><td class=\"num\">427,341</td><td class=\"num\">563,759</td></tr><tr><td><b>Combined</b></td><td class=\"num\"><b>2,395,100</b></td><td class=\"num\"><b>921,966</b></td><td class=\"num\"><b>1,473,134</b></td></tr></table><p style=\"font-size:13px;color:#475467\">Audit note: Old 2026 sheet wrote Grand Total 1,240,900 but detail sums to 991,100 + 250,000 = 1,241,100. Difference KES 200 kept visible. Does not change agreed BF 855,759.</p></div>")
    h.append("<div class=\"card\"><h2>3. Monthly Contributions Oct 2024 - Dec 2025</h2><div style=\"overflow:auto\"><table><tr><th>Project</th>")
    for m in MONTHS_2425: h.append(f"<th class='num'>{m}</th>")
    h.append("<th class='num'>Total</th></tr>")
    for name,vals in MONTHLY_2425: h.append(f"<tr><td><b>{name}</b></td>" + "".join(f"<td class='num'>{v:,}</td>" if v else "<td class='num'>-</td>" for v in vals) + f"<td class='num'><b>{sum(vals):,}</b></td></tr>")
    h.append("<tr><td><b>TOTAL</b></td>" + "".join(f"<td class='num'><b>{v:,}</b></td>" for v in TOTAL_2425_MONTH) + "<td class='num'><b>1,404,000</b></td></tr></table></div></div>")
    h.append("<div class=\"card\"><h2>4. Monthly Contributions Dec 2025 - Nov 2026</h2><div style=\"overflow:auto\"><table><tr><th>Project</th>")
    for m in MONTHS_2026: h.append(f"<th class='num'>{m}</th>")
    h.append("<th class='num'>Total</th></tr>")
    for name,vals in MONTHLY_2026: h.append(f"<tr><td><b>{name}</b></td>" + "".join(f"<td class='num'>{v:,}</td>" if v else "<td class='num'>-</td>" for v in vals) + f"<td class='num'><b>{sum(vals):,}</b></td></tr>")
    h.append("<tr><td><b>TOTAL</b></td>" + "".join(f"<td class='num'><b>{v:,}</b></td>" for v in TOTAL_2026_MONTH) + "<td class='num'><b>991,100</b></td></tr></table></div></div>")
    h.append("<div class=\"card\"><h2>5. Fares - ALL - Period 1 - 25 payments</h2><table><tr><th>Name</th><th>Phone</th><th class=\"num\">Amount</th><th class=\"num\">Trans.</th><th class=\"num\">Total</th></tr>")
    for per,n,ph,a,t in FARES:
        if per=="P1": h.append(f"<tr><td><b>{n}</b></td><td>{ph}</td><td class='num'>KES {a:,}</td><td class='num'>KES {t:,}</td><td class='num'>KES {a+t:,}</td></tr>")
    h.append("<tr><td colspan='2'><b>TOTAL P1</b></td><td class='num'><b>KES 30,000</b></td><td class='num'><b>KES 1,625</b></td><td class='num'><b>KES 31,625</b></td></tr></table></div>")
    h.append("<div class=\"card\"><h2>6. Fares - ALL - Period 2 - 21 payments</h2><table><tr><th>Name</th><th>Phone</th><th class=\"num\">Amount</th><th class=\"num\">Trans.</th><th class=\"num\">Total</th></tr>")
    for per,n,ph,a,t in FARES:
        if per=="P2": h.append(f"<tr><td><b>{n}</b></td><td>{ph}</td><td class='num'>KES {a:,}</td><td class='num'>KES {t:,}</td><td class='num'>KES {a+t:,}</td></tr>")
    h.append("<tr><td colspan='2'><b>TOTAL P2</b></td><td class='num'><b>KES 30,000</b></td><td class='num'><b>KES 2,100</b></td><td class='num'><b>KES 32,100</b></td></tr></table></div>")
    h.append("<div class=\"card\"><h2>7. Beneficiaries - ALL - Period 1 - 20 rows</h2><table><tr><th>Name</th><th>Project</th><th>Reason / Date</th><th class=\"num\">Amount</th><th class=\"num\">Trans.</th><th class=\"num\">Total</th></tr>")
    for per,n,pr,reason,date,a,t in BENEF:
        if per=="P1": h.append(f"<tr><td><b>{n}</b></td><td>{pr}</td><td>{reason} - {date}</td><td class='num'>KES {a:,}</td><td class='num'>KES {t:,}</td><td class='num'>KES {a+t:,}</td></tr>")
    h.append("<tr><td colspan='3'><b>TOTAL P1</b></td><td class='num'><b>KES 461,000</b></td><td class='num'><b>KES 2,000</b></td><td class='num'><b>KES 463,000</b></td></tr></table></div>")
    h.append("<div class=\"card\"><h2>8. Beneficiaries - ALL - Period 2 - 13 rows</h2><table><tr><th>Name</th><th>Project</th><th>Reason / Date</th><th class=\"num\">Amount</th><th class=\"num\">Trans.</th><th class=\"num\">Total</th></tr>")
    for per,n,pr,reason,date,a,t in BENEF:
        if per=="P2": h.append(f"<tr><td><b>{n}</b></td><td>{pr}</td><td>{reason} - {date}</td><td class='num'>KES {a:,}</td><td class='num'>KES {t:,}</td><td class='num'>KES {a+t:,}</td></tr>")
    h.append("<tr><td colspan='3'><b>TOTAL P2</b></td><td class='num'><b>KES 379,075</b></td><td class='num'><b>KES 1,300</b></td><td class='num'><b>KES 380,375</b></td></tr></table></div>")
    h.append("<div class=\"card\"><h2>9. Bank / Transfer - Period 2</h2><table><tr><th>Item</th><th class=\"num\">Amount</th></tr><tr><td>Bank charges - 288 x KES 50</td><td class='num'>KES 14,400</td></tr><tr><td>Transfer charges - Transfer of KES 673,270</td><td class='num'>KES 466</td></tr><tr><td><b>Total Bank / Transfer</b></td><td class='num'><b>KES 14,866</b></td></tr></table></div>")
    h.append("<div class=\"card\"><h2>10. Reconciliation</h2><table><tr><th>Item</th><th class=\"num\">Amount</th></tr><tr><td>Period 1 BF: 1,404,000 - 494,625</td><td class='num'><b>KES 909,375</b></td></tr><tr><td>Period 2 Closing (written): 1,240,900 - 427,341</td><td class='num'><b>KES 813,559</b></td></tr><tr><td>Period 2 Closing (recomputed): 1,241,100 - 427,341</td><td class='num'><b>KES 813,759</b></td></tr><tr><td>Agreed BF for share-out</td><td class='num'><b>KES 855,759</b></td></tr><tr><td>Retained</td><td class='num'><b>KES 250,000</b></td></tr><tr><td>Amount to Share Now</td><td class='num'><b>KES 605,759</b></td></tr></table><a class='btn2' href='/shareout'>Go to Share-Out</a></div>")
    return shell("History","".join(h))
@app.route("/shareout")
def shareout_page():
    shares,total_contrib,total_months,per_month_rate=calc_shares(); total_shares=sum(x["share"] for x in shares)
    h=[]
    h.append(f"<h1>Share-Out</h1><p style='color:#475467'>Period: Dec 2025 - Nov 2026. Fair - by contribution months.</p><div class='hero'><div style='font-size:11px;letter-spacing:.14em;color:#B9975B;font-weight:700'>AMOUNT TO SHARE</div><h1>KES 605,759</h1><p>1 month = KES {per_month_rate:,.2f} - Shares KES {total_shares:,.2f} + Retained 250,000 = BF 855,759</p></div>")
    h.append("<div class=\"card\"><h2>How Your Share Is Calculated</h2><table><tr><th>Joined</th><th>Months</th><th>Share</th></tr><tr><td><b>Before 2025</b></td><td><b>12 - Full</b></td><td>Same amount</td></tr><tr><td><b>2025</b></td><td><b>12 - Full</b></td><td>Same amount</td></tr><tr><td><b>Jan 2026</b></td><td>11</td><td>11 x 1 month</td></tr><tr><td><b>Feb 2026</b></td><td>10</td><td>10 x 1 month</td></tr><tr><td><b>Mar 2026</b></td><td>9</td><td>9 x 1 month</td></tr><tr><td><b>Apr 2026</b></td><td>8</td><td>8 x 1 month</td></tr><tr><td><b>May 2026</b></td><td>7</td><td>7 x 1 month</td></tr><tr><td><b>Jun 2026</b></td><td>6</td><td>6 x 1 month</td></tr><tr><td><b>Jul 2026</b></td><td>5</td><td>5 x 1 month</td></tr><tr><td><b>Aug 2026</b></td><td>4</td><td>4 x 1 month</td></tr><tr><td><b>Sep 2026</b></td><td>3</td><td>3 x 1 month</td></tr><tr><td><b>Oct 2026</b></td><td>2</td><td>2 x 1 month</td></tr><tr><td><b>Nov 2026</b></td><td>1</td><td>1 x 1 month</td></tr></table></div>")
    h.append(f"<div class='grid'><div class='kpi'><div>Members</div><h2>{len(shares)}</h2></div><div class='kpi'><div>Total Months</div><h2>{total_months}</h2></div><div class='kpi'><div>Contributions</div><h2 style='font-size:24px'>KES {total_contrib:,}</h2></div><div class='kpi'><div>Total Shares</div><h2 style='font-size:24px'>KES {total_shares:,.2f}</h2></div></div>")
    h.append("<div class=\"card\"><div style=\"display:flex;justify-content:space-between;gap:12px;flex-wrap:wrap\"><h2 style=\"margin:0\">Member Share-Out Schedule</h2><a class=\"btn2 gold\" href=\"/download/shareout\">Download Excel</a></div><input class=\"input\" id=\"q\" placeholder=\"Search by name, staff or project\" oninput=\"fil()\" style=\"margin:14px 0\"><div style=\"overflow:auto\"><table><tr><th>#</th><th>Member</th><th>Project</th><th>Date Joined</th><th>Basis</th><th class=\"num\">Months</th><th class=\"num\">Contribution</th><th class=\"num\">Share</th></tr><tbody id=\"shareBody\">")
    for i,x in enumerate(shares,1): h.append(f"<tr data-search='{(x['full_names']+' '+x['staff_no']+' '+x['project']).lower()}'><td>{i}</td><td><b>{x['full_names']}</b><div style='font-size:12px;color:#667085'>{x['staff_no']} {x['email']}</div></td><td>{x['badge']}</td><td>{x['month_joined'] or '-'}</td><td style='font-size:12px'>{x['basis']}</td><td class='num'>{x['months']}</td><td class='num'>KES {x['contribution']:,}</td><td class='num'><b>KES {x['share']:,.2f}</b></td></tr>")
    h.append("</tbody></table></div></div><script>function fil(){let q=document.getElementById('q').value.toLowerCase();document.querySelectorAll('#shareBody tr').forEach(function(r){r.style.display=r.getAttribute('data-search').includes(q)?'':'none'})}</script>")
    return shell("Share-Out","".join(h))
@app.route("/members")
def members_page():
    p=[]
    p.append("<h1>Members</h1><p id=\"memberCountLabel\" style=\"color:#475467\"></p>")
    p.append("<div class=\"card\"><div style=\"display:flex;gap:10px;flex-wrap:wrap\"><input class=\"input\" id=\"q\" placeholder=\"Search by name, staff, project\" oninput=\"fil()\" style=\"flex:2;min-width:200px\"><select class=\"input\" id=\"projFilter\" onchange=\"fil()\" style=\"flex:1;min-width:160px\"><option value=\"All Projects\">All Projects</option></select></div><div id=\"list\" style=\"margin-top:14px\"></div><a class=\"btn2\" href=\"/download/excel\">Download Excel</a></div>")
    p.append("<script>let all=[];")
    p.append("async function load(){try{let r=await fetch('/api/stats');let d=await r.json();document.getElementById('memberCountLabel').textContent=d.total_members+' members';let sel=document.getElementById('projFilter');sel.innerHTML='<option value=\"All Projects\">All Projects ('+d.total_members+')</option>';(d.projects||[]).forEach(function(p){let o=document.createElement('option');o.value=p;o.textContent=p+' ('+(d.projects_breakdown[p]||0)+')';sel.appendChild(o)});}catch(e){}try{let r2=await fetch('/api/members');let dd=await r2.json();all=dd.members;render(all);}catch(e){}}")
    p.append("function row(l,v){return '<div class=\"row\"><span style=\"color:#667085\">'+l+'</span><b>'+(v||'-')+'</b></div>'}")
    p.append("function render(l){let h='';l.forEach(function(m){let kids=[m.kid1,m.kid2,m.kid3,m.kid4,m.kid5].filter(function(x){return x}).join(', ')||'-';let q=String.fromCharCode(39);let safe=m.full_names.split(q).join('');h+='<div class=\"card\"><div style=\"display:flex;justify-content:space-between;gap:12px\"><div><b style=\"font-size:17px\">'+m.full_names+'</b><div style=\"color:#667085;font-size:13px\">'+m.email+'</div></div><span>'+badge(m.project)+'</span></div>'+row('Staff Number',m.staff_no)+row('Date Joined',m.month_joined)+row('Father ID',m.father_id)+row('Mother ID',m.mother_id)+row('Guardian ID',m.guardian_id)+row('Spouse ID',m.spouse_id)+row('Kids Birth Certs',kids)+'<div style=\"margin-top:12px\"><button class=\"btn2 gold\" onclick=\"addF('+q+safe+q+')\">+ Add Friend</button></div></div>'});document.getElementById('list').innerHTML=h||'No members found'}")
    p.append("async function addF(to){let me=prompt('Your name to send friend request as:');if(!me)return;let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from_name:me,to_name:to})});let j=await r.json();alert(j.message||j.error)}")
    p.append("function fil(){let qq=document.getElementById('q').value.toLowerCase();let pf=document.getElementById('projFilter').value;render(all.filter(function(m){return (m.full_names+' '+m.staff_no+' '+m.project).toLowerCase().includes(qq)&&(pf=='All Projects'||m.project==pf)}))}")
    p.append("load();</script>")
    return shell("Members","".join(p))
@app.route("/community")
def community_page():
    p=[]
    p.append("<h1>Community</h1>")
    p.append("<div style=\"display:flex;gap:8px;flex-wrap:wrap;margin-bottom:14px\">")
    p.append("<button class=\"chip on\" id=\"chipAll\" onclick=\"setFilter('all')\">All Posts</button>")
    p.append("<button class=\"chip\" id=\"chipPhoto\" onclick=\"setFilter('photo')\">Photos</button>")
    p.append("<button class=\"chip\" id=\"chipVideo\" onclick=\"setFilter('video')\">Videos</button>")
    p.append("<a class=\"chip\" href=\"/friends\" style=\"text-decoration:none\">Friends</a></div>")
    p.append("<div class=\"card\"><label>Your name</label>")
    p.append("<input class=\"input\" id=\"cName\" placeholder=\"Your name\">")
    p.append("<div style=\"margin-top:12px\"><label>Message</label>")
    p.append("<textarea id=\"cMsg\" class=\"input\" style=\"height:96px\" placeholder=\"Share something...\"></textarea></div>")
    p.append("<div style=\"display:grid;grid-template-columns:1fr 1fr;gap:10px;margin-top:14px\">")
    p.append("<label class=\"chip\" style=\"text-align:center;padding:13px\">Add Photo")
    p.append("<input type=\"file\" id=\"photoInput\" accept=\"image/*\" style=\"display:none\" onchange=\"handlePhoto(event)\"></label>")
    p.append("<label class=\"chip\" style=\"text-align:center;padding:13px\">Add Video")
    p.append("<input type=\"file\" id=\"videoInput\" accept=\"video/*\" style=\"display:none\" onchange=\"handleVideo(event)\"></label></div>")
    p.append("<div id=\"preview\"></div>")
    p.append("<button class=\"btn\" onclick=\"sendC()\" style=\"margin-top:14px\">Post</button><p id=\"cStatus\"></p></div>")
    p.append("<div class=\"card\"><h2>Posts</h2><div id=\"cList\">Loading...</div></div>")
    p.append("<script>")
    p.append("let mediaType='';let mediaData='';let curFilter='all';")
    p.append("function setFilter(f){curFilter=f;")
    p.append("document.getElementById('chipAll').classList.toggle('on',f=='all');")
    p.append("document.getElementById('chipPhoto').classList.toggle('on',f=='photo');")
    p.append("document.getElementById('chipVideo').classList.toggle('on',f=='video');loadC()}")
    p.append("function handlePhoto(e){let f=e.target.files[0];if(!f)return;")
    p.append("let r=new FileReader();")
    p.append("r.onload=function(){mediaType='photo';mediaData=r.result;")
    p.append("document.getElementById('preview').innerHTML='<img src='+mediaData+' class=\"postimg\">'};")
    p.append("r.readAsDataURL(f)}")
    p.append("function handleVideo(e){let f=e.target.files[0];if(!f)return;")
    p.append("let r=new FileReader();")
    p.append("r.onload=function(){mediaType='video';mediaData=r.result;")
    p.append("document.getElementById('preview').innerHTML='<video src='+mediaData+' class=\"postvideo\" controls></video>'};")
    p.append("r.readAsDataURL(f)}")
    p.append("async function sendC(){")
    p.append("let r=await fetch('/api/community',{method:'POST',headers:{'Content-Type':'application/json'},")
    p.append("body:JSON.stringify({name:document.getElementById('cName').value,")
    p.append("msg:document.getElementById('cMsg').value,media_type:mediaType,media:mediaData})});")
    p.append("let j=await r.json();document.getElementById('cStatus').textContent=j.message||j.error;")
    p.append("if(j.ok){document.getElementById('cMsg').value='';mediaType='';mediaData='';")
    p.append("document.getElementById('preview').innerHTML='';loadC()}}")
    p.append("async function loadC(){")
    p.append("let r=await fetch('/api/community');let d=await r.json();")
    p.append("let posts=d.posts.filter(function(p){return curFilter=='all'||p.media_type==curFilter});")
    p.append("document.getElementById('cList').innerHTML=posts.map(function(p){")
    p.append("let q=String.fromCharCode(39);let safe=p.name.split(q).join('');let m='';")
    p.append("if(p.media_type=='photo'){m='<img src='+p.media+' class=\"postimg\">'}")
    p.append("if(p.media_type=='video'){m='<video src='+p.media+' class=\"postvideo\" controls></video>'}")
    p.append("return '<div style=\"padding:14px 0;border-bottom:1px solid #eee\"><b>'+p.name+'</b>'")
    p.append("+'<div style=\"color:#667085;font-size:12px\">'+p.created+'</div>'")
    p.append("+'<div style=\"margin-top:6px;white-space:pre-wrap\">'+p.msg+'</div>'+m")
    p.append("+'<div style=\"margin-top:10px;display:flex;gap:8px\">'")
    p.append("+'<button class=\"chip\" onclick=\"likeC('+p.id+',this)\">Like '+p.likes+'</button>'")
    p.append("+'<button class=\"chip\" onclick=\"addFriendFromPost('+q+safe+q+')\">+ Add Friend</button></div></div>'}).join('')||'No posts yet'}")
    p.append("async function likeC(id,el){")
    p.append("let r=await fetch('/api/community/like/'+id,{method:'POST'});")
    p.append("let j=await r.json();if(j.ok)loadC()}")
    p.append("async function addFriendFromPost(to){")
    p.append("let me=prompt('Your name to send friend request as:');if(!me)return;")
    p.append("let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},")
    p.append("body:JSON.stringify({from_name:me,to_name:to})});")
    p.append("let j=await r.json();alert(j.message||j.error)}")
    p.append("loadC();")
    p.append("</script>")
    return shell("Community","".join(p))
@app.route("/friends")
def friends_page():
    p=[]
    p.append("<h1>Friends</h1><p style=\"color:#475467\">Find members and send friend requests.</p>")
    p.append("<div class=\"card\"><label>Your name</label><input class=\"input\" id=\"myName\" placeholder=\"Your name\">")
    p.append("<div style=\"margin-top:12px\"><label>Search members</label><input class=\"input\" id=\"fq\" placeholder=\"Search by name\" oninput=\"renderF()\"></div><div id=\"findList\" style=\"margin-top:14px\"></div></div>")
    p.append("<div class=\"card\"><h2>Friend Requests</h2><div id=\"reqList\">Loading...</div></div>")
    p.append("<div class=\"card\"><h2>My Friends</h2><div id=\"myFriends\">Loading...</div></div>")
    p.append("<script>let allF=[];")
    p.append("async function loadF(){let r=await fetch('/api/members');let d=await r.json();allF=d.members;renderF();loadReq()}")
    p.append("function renderF(){let q=document.getElementById('fq').value.toLowerCase();let list=allF.filter(function(m){return m.full_names.toLowerCase().includes(q)}).slice(0,30);document.getElementById('findList').innerHTML=list.map(function(m){let qq=String.fromCharCode(39);let safe=m.full_names.split(qq).join('');return '<div class=\"row\"><span><b>'+m.full_names+'</b><div style=\"font-size:12px;color:#667085\">'+m.project+'</div></span><button class=\"btn2 gold\" onclick=\"sendReq('+qq+safe+qq+')\">+ Add Friend</button></div>'}).join('')||'No members'}")
    p.append("async function sendReq(to){let me=document.getElementById('myName').value;if(!me){alert('Enter your name first');return}let r=await fetch('/api/friends/add',{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify({from_name:me,to_name:to})});let j=await r.json();alert(j.message||j.error);loadReq()}")
    p.append("async function loadReq(){let me=document.getElementById('myName').value;let r=await fetch('/api/friends?me='+encodeURIComponent(me));let d=await r.json();document.getElementById('reqList').innerHTML=(d.requests||[]).map(function(f){return '<div class=\"row\"><span><b>'+f.from_name+'</b> wants to be your friend</span><span><button class=\"btn2\" onclick=\"actReq('+f.id+',\\'accept\\')\">Accept</button> <button class=\"btn2 gold\" onclick=\"actReq('+f.id+',\\'reject\\')\">Reject</button></span></div>'}).join('')||'No requests';document.getElementById('myFriends').innerHTML=(d.friends||[]).map(function(f){return '<div class=\"row\"><b>'+f+'</b><span>Friend</span></div>'}).join('')||'No friends yet'}")
    p.append("async function actReq(id,action){let r=await fetch('/api/friends/'+action+'/'+id,{method:'POST'});let j=await r.json();alert(j.message||j.error);loadReq()}")
    p.append("document.getElementById('myName').addEventListener('change',loadReq);loadF();</script>")
    return shell("Friends","".join(p))
@app.route("/register", methods=["GET","POST"])
def register_page():
    if request.method=="POST":
        staff=request.form.get("staff_no","").strip(); names=request.form.get("full_names","").strip(); project=norm_project(request.form.get("project","")); month=request.form.get("month_joined","").strip()
        c=get_db()
        try:
            ok=add_user(c,staff,names,project,month)
            if ok: c.commit()
            else: c.rollback()
        finally: c.close()
        if ok: return redirect("/members")
        return shell("Register","<div class=\"card\"><h2>Could not register</h2><p>Staff number or name already exists.</p><a class=\"btn2\" href=\"/register\">Try again</a></div>")
    opts="".join(f"<option value=\"{p}\">{p}</option>" for p in PROJECTS)
    body="<h1>Register Member</h1><form class=\"card\" method=\"POST\" action=\"/register\">"
    body+="<label>Staff Number</label><input class=\"input\" name=\"staff_no\" required>"
    body+="<div style=\"margin-top:12px\"><label>Full Names</label><input class=\"input\" name=\"full_names\" required></div>"
    body+="<div style=\"margin-top:12px\"><label>Project</label><select class=\"input\" name=\"project\">"+opts+"</select></div>"
    body+="<div style=\"margin-top:12px\"><label>Date Joined</label><input class=\"input\" name=\"month_joined\" placeholder=\"e.g. Jan 2026\" required></div>"
    body+="<button class=\"btn\" type=\"submit\" style=\"margin-top:16px\">Register Member</button></form>"
    return shell("Register",body)
@app.route("/admin", methods=["GET","POST"])
def admin_page():
    if request.method=="POST":
        email=request.form.get("email","").strip(); password=request.form.get("password","")
        c=get_db()
        try: u=c.execute("SELECT * FROM users WHERE email=?",(email,)).fetchone()
        finally: c.close()
        if u and check_password_hash(u["password"],password): return redirect("/admin?ok=1&email="+email)
        return shell("Admin","<div class=\"card\"><h2>Login failed</h2><a class=\"btn2\" href=\"/admin\">Try again</a></div>")
    ok=request.args.get("ok")
    if ok:
        c=get_db()
        try:
            msgs=c.execute("SELECT * FROM support_msgs ORDER BY id DESC LIMIT 20").fetchall()
            notifs=c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 20").fetchall()
        finally: c.close()
        h="<h1>Admin</h1><div class=\"card\"><h2>Send Notification</h2><form method=\"POST\" action=\"/api/admin/notify\"><input class=\"input\" name=\"title\" placeholder=\"Title\" required><input class=\"input\" name=\"msg\" placeholder=\"Message\" style=\"margin-top:10px\" required><input class=\"input\" name=\"target\" placeholder=\"Target - leave blank for all\" style=\"margin-top:10px\"><button class=\"btn\" type=\"submit\" style=\"margin-top:12px\">Send Notification</button></form></div>"
        h+="<div class=\"card\"><h2>Add Member</h2><a class=\"btn2\" href=\"/register\">Register Member</a> <a class=\"btn2 gold\" href=\"/download/excel\">Download Excel</a> <a class=\"btn2 gold\" href=\"/download/shareout\">Download Share-Out</a></div><div class=\"card\"><h2>Support Messages</h2>"
        for m in msgs: h+=f"<div class=\"row\"><span><b>{m['name']}</b><div>{m['msg']}</div></span><span>{m['created']}</span></div>"
        h+="</div><div class=\"card\"><h2>Notifications Sent</h2>"
        for n in notifs: h+=f"<div class=\"row\"><span><b>{n['title']}</b><div>{n['msg']}</div></span><span>{n['created']}</span></div>"
        h+="</div>"
        return shell("Admin",h)
    body="<h1>Admin Login</h1><div class=\"card\"><form method=\"POST\" action=\"/admin\"><label>Email</label><input class=\"input\" name=\"email\" value=\"admin@lonma.com\" required><div style=\"margin-top:12px\"><label>Password</label><input class=\"input\" name=\"password\" type=\"password\" value=\"admin123\" required></div><button class=\"btn\" type=\"submit\" style=\"margin-top:14px\">Login</button></form></div>"
    return shell("Admin",body)
@app.route("/download/excel")
def download_excel():
    try:
        import openpyxl
        wb=openpyxl.Workbook(); ws=wb.active; ws.title="Members"
        ws.append(["Staff No","Full Names","Project","Email","Date Joined"])
        c=get_db()
        try: rows=c.execute("SELECT * FROM users ORDER BY full_names").fetchall()
        finally: c.close()
        for r in rows: ws.append([r["staff_no"],r["full_names"],r["project"],r["email"],r["month_joined"]])
        ws2=wb.create_sheet("Share-Out"); ws2.append(["Staff No","Full Names","Project","Date Joined","Basis","Months","Contribution","Share"])
        shares,_,_,_=calc_shares()
        for x in shares: ws2.append([x["staff_no"],x["full_names"],x["project"],x["month_joined"],x["basis"],x["months"],x["contribution"],x["share"]])
        ws3=wb.create_sheet("Combined Expenses"); ws3.append(["Expense line","Period 1","Period 2","Combined"])
        ws3.append(["Fares paid",30000,30000,60000]); ws3.append(["Fares transactions",1625,2100,3725]); ws3.append(["Fares total",31625,32100,63725]); ws3.append(["Beneficiaries paid",461000,379075,840075]); ws3.append(["Beneficiaries transactions",2000,1300,3300]); ws3.append(["Benefici```python
        ws3.append(["Beneficiaries paid",461000,379075,840075])
        ws3.append(["Beneficiaries transactions",2000,1300,3300])
        ws3.append(["Beneficiaries total",463000,380375,843375])
        ws3.append(["Bank charges",0,14400,14400])
        ws3.append(["Transfer charges",0,466,466])
        ws3.append(["Bank / Transfer total",0,14866,14866])
        ws3.append(["TOTAL EXPENSES COMBINED",494625,427341,921966])
        ws4=wb.create_sheet("Fares ALL")
        ws4.append(["Period","Name","Phone","Amount","Trans","Total"])
        for per,n,ph,a,t in FARES: ws4.append([per,n,ph,a,t,a+t])
        ws5=wb.create_sheet("Beneficiaries ALL")
        ws5.append(["Period","Name","Project","Reason","Date","Amount","Trans","Total"])
        for per,n,pr,reason,date,a,t in BENEF: ws5.append([per,n,pr,reason,date,a,t,a+t])
        bio=io.BytesIO(); wb.save(bio); bio.seek(0)
        return send_file(bio,as_attachment=True,download_name="FIG_Members.xlsx",mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"error":str(e)}),500
@app.route("/download/shareout")
def download_shareout():
    try:
        import openpyxl
        wb=openpyxl.Workbook(); ws=wb.active; ws.title="Share-Out"
        ws.append(["#","Staff No","Full Names","Project","Date Joined","Basis","Months","Contribution","Share"])
        shares,_,_,_=calc_shares()
        for i,x in enumerate(shares,1): ws.append([i,x["staff_no"],x["full_names"],x["project"],x["month_joined"],x["basis"],x["months"],x["contribution"],x["share"]])
        bio=io.BytesIO(); wb.save(bio); bio.seek(0)
        return send_file(bio,as_attachment=True,download_name="FIG_ShareOut.xlsx",mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet")
    except Exception as e:
        return jsonify({"error":str(e)}),500
@app.route("/api/stats")
def api_stats():
    c=get_db()
    try:
        rows=c.execute("SELECT project, COUNT(*) as n FROM users WHERE email != ? GROUP BY project ORDER BY project",(ADMIN_EMAIL,)).fetchall()
        total=c.execute("SELECT COUNT(*) as n FROM users WHERE email != ?",(ADMIN_EMAIL,)).fetchone()["n"]
    finally: c.close()
    bd={}; plist=[]
    for r in rows:
        p=norm_project(r["project"]); bd[p]=bd.get(p,0)+r["n"]
        if p not in plist: plist.append(p)
    return jsonify({"total_members":total,"projects_total":len(plist),"projects":sorted(plist),"projects_breakdown":bd,"version":VERSION})
@app.route("/api/members")
def api_members():
    c=get_db()
    try: rows=c.execute("SELECT * FROM users WHERE email != ? ORDER BY full_names",(ADMIN_EMAIL,)).fetchall()
    finally: c.close()
    out=[]
    for r in rows: out.append({"id":r["id"],"staff_no":r["staff_no"] or "","full_names":r["full_names"] or "","project":norm_project(r["project"]),"email":r["email"] or "","month_joined":r["month_joined"] or "","father_id":r["father_id"] or "","mother_id":r["mother_id"] or "","guardian_id":r["guardian_id"] or "","spouse_id":r["spouse_id"] or "","kid1":r["kid1"] or "","kid2":r["kid2"] or "","kid3":r["kid3"] or "","kid4":r["kid4"] or "","kid5":r["kid5"] or "","photo":r["photo"] or ""})
    return jsonify({"members":out})
@app.route("/api/shareout")
def api_shareout():
    shares,tc,tm,rate=calc_shares()
    return jsonify({"members":shares,"total_contribution":tc,"total_months":tm,"per_month_rate":rate,"distributable":DISTRIBUTABLE,"retained":RESERVE,"bf":BF,"version":VERSION})
@app.route("/api/expenses")
def api_expenses():
    return jsonify({"fares":{"period1":{"principal":30000,"transactions":1625,"total":31625},"period2":{"principal":30000,"transactions":2100,"total":32100},"combined":63725},"beneficiaries":{"period1":{"principal":461000,"transactions":2000,"total":463000},"period2":{"principal":379075,"transactions":1300,"total":380375},"combined":843375},"bank":{"period1":0,"period2":14866,"combined":14866},"total_expenses":{"period1":494625,"period2":427341,"combined":921966},"contributions":{"period1":1404000,"period2":991100,"combined":2395100},"version":VERSION})
@app.route("/api/fares")
def api_fares():
    return jsonify({"fares":[{"period":per,"name":n,"phone":ph,"amount":a,"transaction":t,"total":a+t} for per,n,ph,a,t in FARES]})
@app.route("/api/beneficiaries")
def api_beneficiaries():
    return jsonify({"beneficiaries":[{"period":per,"name":n,"project":pr,"reason":reason,"date":date,"amount":a,"transaction":t,"total":a+t} for per,n,pr,reason,date,a,t in BENEF]})
@app.route("/api/notifications")
def api_notifications():
    c=get_db()
    try: rows=c.execute("SELECT * FROM notifications ORDER BY id DESC LIMIT 20").fetchall()
    finally: c.close()
    return jsonify({"notifications":[{"id":r["id"],"title":r["title"],"msg":r["msg"],"created":r["created"]} for r in rows]})
@app.route("/api/notifications/read", methods=["POST"])
def api_notifications_read():
    return jsonify({"ok":True})
@app.route("/api/support", methods=["POST"])
def api_support():
    d=request.get_json(silent=True) or {}
    name=(d.get("name") or "").strip(); msg=(d.get("msg") or "").strip()
    if not name or not msg: return jsonify({"error":"Name and message required"}),400
    c=get_db()
    try: c.execute("INSERT INTO support_msgs (name,msg,created) VALUES (?,?,datetime('now'))",(name,msg,)); c.commit()
    finally: c.close()
    return jsonify({"ok":True,"message":"Message sent."})
@app.route("/api/admin/notify", methods=["POST"])
def api_admin_notify():
    title=request.form.get("title","").strip(); msg=request.form.get("msg","").strip(); target=request.form.get("target","").strip()
    if not title or not msg: return jsonify({"error":"Title and message required"}),400
    c=get_db()
    try: c.execute("INSERT INTO notifications (title,msg,created,target) VALUES (?,?,datetime('now'),?)",(title,msg,target)); c.commit()
    finally: c.close()
    return redirect("/admin?ok=1")
@app.route("/api/community", methods=["GET","POST"])
def api_community():
    if request.method=="POST":
        d=request.get_json(silent=True) or {}
        name=(d.get("name") or "").strip(); msg=(d.get("msg") or "").strip()
        if not name or not msg: return jsonify({"error":"Name and message required"}),400
        c=get_db()
        try: c.execute("INSERT INTO community (name,msg,created,media_type,media,likes) VALUES (?,?,datetime('now'),?,?,0)",(name,msg,d.get("media_type") or "",d.get("media") or "")); c.commit()
        finally: c.close()
        return jsonify({"ok":True,"message":"Posted"})
    c=get_db()
    try: rows=c.execute("SELECT * FROM community ORDER BY id DESC LIMIT 100").fetchall()
    finally: c.close()
    return jsonify({"posts":[{"id":r["id"],"name":r["name"],"msg":r["msg"],"created":r["created"],"media_type":r["media_type"] or "","media":r["media"] or "","likes":r["likes"] or 0} for r in rows]})
@app.route("/api/community/like/<int:pid>", methods=["POST"])
def api_community_like(pid):
    c=get_db()
    try:
        r=c.execute("SELECT likes FROM community WHERE id=?",(pid,)).fetchone()
        if not r: return jsonify({"error":"Not found"}),404
        c.execute("UPDATE community SET likes=? WHERE id=?",((r["likes"] or 0)+1,pid)); c.commit()
    finally: c.close()
    return jsonify({"ok":True})
@app.route("/api/friends")
def api_friends():
    me=(request.args.get("me") or "").strip()
    c=get_db()
    try:
        reqs=c.execute("SELECT * FROM friends WHERE lower(to_name)=lower(?) AND status='pending' ORDER BY id DESC",(me,)).fetchall() if me else []
        allf=c.execute("SELECT * FROM friends WHERE status='accepted' AND (lower(from_name)=lower(?) OR lower(to_name)=lower(?))",(me,me)).fetchall() if me else []
    finally: c.close()
    friends=[]
    for f in allf:
        other=f["to_name"] if f["from_name"].lower()==me.lower() else f["from_name"]
        if other not in friends: friends.append(other)
    return jsonify({"requests":[{"id":r["id"],"from_name":r["from_name"],"to_name":r["to_name"]} for r in reqs],"friends":friends})
@app.route("/api/friends/add", methods=["POST"])
def api_friends_add():
    d=request.get_json(silent=True) or {}
    frm=(d.get("from_name") or "").strip(); to=(d.get("to_name") or "").strip()
    if not frm or not to: return jsonify({"error":"Both names required"}),400
    if frm.lower()==to.lower(): return jsonify({"error":"Cannot add yourself"}),400
    c=get_db()
    try:
        ex=c.execute("SELECT id FROM friends WHERE (lower(from_name)=lower(?) AND lower(to_name)=lower(?)) OR (lower(from_name)=lower(?) AND lower(to_name)=lower(?))",(frm,to,to,frm)).fetchone()
        if ex: return jsonify({"message":"Request already exists"})
        c.execute("INSERT INTO friends (from_name,to_name,status,created) VALUES (?,?,?,datetime('now'))",(frm,to,"pending")); c.commit()
    finally: c.close()
    return jsonify({"ok":True,"message":"Friend request sent to "+to})
@app.route("/api/friends/accept/<int:fid>", methods=["POST"])
def api_friends_accept(fid):
    c=get_db()
    try: c.execute("UPDATE friends SET status='accepted' WHERE id=?",(fid,)); c.commit()
    finally: c.close()
    return jsonify({"ok":True,"message":"Friend accepted"})
@app.route("/api/friends/reject/<int:fid>", methods=["POST"])
def api_friends_reject(fid):
    c=get_db()
    try: c.execute("UPDATE friends SET status='rejected' WHERE id=?",(fid,)); c.commit()
    finally: c.close()
    return jsonify({"ok":True,"message":"Friend rejected"})
@app.route("/api/health")
def api_health():
    return jsonify({"ok":True,"version":VERSION})
if __name__=="__main__":
    port=int(os.environ.get("PORT",5000))
    app.run(host="0.0.0.0",port=port,debug=False)
