import sqlite3
import os
from flask import Flask, request, jsonify, redirect

app = Flask(__name__)
DB = "lonma.db"

def get_db():
    con = sqlite3.connect(DB)
    con.row_factory = sqlite3.Row
    return con

def init_db():
    con = get_db()
    cur = con.cursor()
    cur.execute("CREATE TABLE IF NOT EXISTS users (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, staff_no TEXT, project TEXT, month_joined TEXT, status TEXT DEFAULT 'active member', father_id TEXT DEFAULT '-', mother_id TEXT DEFAULT '-', guardian_id TEXT DEFAULT '-', spouse_id TEXT DEFAULT '-', kid1 TEXT DEFAULT '-', kid2 TEXT DEFAULT '-', kid3 TEXT DEFAULT '-', kid4 TEXT DEFAULT '-', kid5 TEXT DEFAULT '-')")
    cur.execute("CREATE TABLE IF NOT EXISTS history (id INTEGER PRIMARY KEY AUTOINCREMENT, full_names TEXT, action TEXT, amount REAL DEFAULT 0, date TEXT)")
    con.commit()
    count = cur.execute("SELECT COUNT(*) FROM users").fetchone()[0]
    if count == 0:
        seed = [
            ("202973", "TF-MT", "Jan-26", "Anastacia Mwende Mutua", "12584896", "12571589", "33067411", "N/A", "5772864", "-", "-", "-", "-"),
            ("202857", "TF-MT", "2025", "Brenda joy nyongesa", "6565657", "N/A", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("-", "TF-MT", "Nov-26", "Bryton Otieno okoth", "N/A", "22959540", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("292954", "TF-MT", "Feb-26", "Christine Wangu namange", "33918462", "2059381", "N/A", "N/A", "31848814", "1832003833", "32224611", "-", "-"),
            ("202879", "TF-MT", "2024", "Daniel musyoka", "N/A", "N/A", "N/A", "37486040", "1308478", "-", "-", "-", "-"),
            ("202899", "TF-MT", "2023", "Daniel Mwangi maina", "10787780", "10058327", "N/A", "36946194", "2643331", "4350577", "-", "-", "-"),
            ("202851", "TF-MT", "2024", "Douglas lidoli lidundu", "N/A", "1142024", "N/A", "35819089", "N/A", "-", "-", "-", "-"),
            ("202898", "TF-MT", "2022", "Elizabeth Kaluki mbithe", "N/A", "30992865", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202838", "TF-MT", "2023", "Elizabeth matinde", "N/A", "30491044", "30005457", "N/A", "5052470", "-", "-", "-", "-"),
            ("202856", "TF-MT", "2025", "Elizabeth Silvia Botuba", "10430483", "20545758", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202927", "TF-MT", "Jan-26", "Esther syokau mosyoki", "N/A", "12721635", "29855331", "N/A", "N/A", "-", "-", "-", "-"),
            ("202847", "TF-MT", "2025", "Esther Wanjiku", "N/A", "N/A", "N/A", "26007857", "7871720", "-", "-", "-", "-"),
            ("202853", "TF-MT", "2025", "Eugene Ochieng", "5985386", "14443973", "N/A", "42103832", "N/A", "-", "-", "-", "-"),
            ("202886", "TF-MT", "2023", "Faith Atieno", "16066182", "N/A", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202850", "TF-MT", "2025", "Getrude kisala", "5126406", "5625403", "33633256", "26924253", "791109279", "264794549", "-", "-", "-"),
            ("202855", "TF-MT", "2025", "Jackline Njeri chomba", "N/A", "N/A", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("292982", "TF-MT", "Feb-26", "Janevick moraa", "N/A", "2058869", "2058869", "N/A", "N/A", "-", "-", "-", "-"),
            ("202860", "TF-MT", "2025", "Mark Alema Mbeche", "5339293", "13408682", "N/A", "32173580", "264970115", "-", "-", "-", "-"),
            ("-", "TF-MT", "2024", "Mary Wangari", "N/A", "23395553", "N/A", "3612145", "5953389", "5953388", "2583144", "-", "-"),
            ("202881", "TF-MT", "2024", "Melvin Mumo", "N/A", "10288319", "N/A", "39465308", "N/A", "-", "-", "-", "-"),
            ("202868", "TF-MT", "2025", "Milka Waweru Nyambura", "8483259", "30808943", "N/A", "N/A", "362101165", "-", "-", "-", "-"),
            ("202843", "TF-MT", "2023", "Mourin wangui karomo", "10502813", "10453948", "N/A", "33400723", "26479", "-", "-", "-", "-"),
            ("202865", "TF-MT", "2025", "Nyongesa rendson wekesa", "N/A", "8038054", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202842", "TF-MT", "2025", "Peninah awuor olang'o", "N/A", "13298945", "N/A", "28715422", "264168855", "264809974", "-", "-", "-"),
            ("202854", "TF-MT", "2025", "Peter omoro", "N/A", "11131310", "N/A", "37130958", "2302502581", "-", "-", "-", "-"),
            ("202872", "TF-MT", "2024", "Philip Etale", "N/A", "14446251", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("292952", "TF-MT", "Feb-26", "Protus Ojuma", "13170537", "23307688", "42717879", "N/A", "N/A", "-", "-", "-", "-"),
            ("-", "TF-MT", "Nov-26", "Purity Opiyo Anyango", "N/A", "8213405", "N/A", "N/A", "685497", "-", "-", "-", "-"),
            ("202844", "TF-MT", "2025", "purity Wambui", "12475261", "12472997", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202880", "TF-MT", "2024", "Scholastica kilonzi", "1008033", "2983637", "N/A", "N/A", "282157", "-", "-", "-", "-"),
            ("202833", "TF-MT", "2025", "Stephen Wesonga Ouma", "-", "8615924", "-", "-", "832827", "3817366", "-", "-", "-"),
            ("-", "TF-MT", "Jun-26", "Telvin gachanja", "N/A", "14417026", "N/A", "33355682", "264284946", "2839387", "-", "-", "-"),
            ("202863", "TF-MT", "2023", "Teresia Muthoni Kariuki", "N/A", "21507084", "N/A", "-", "5050624", "-", "-", "-", "-"),
            ("202864", "TF-MT", "2025", "Vincent Otieno Okello", "2739631", "21348018", "N/A", "37048476", "N/A", "-", "-", "-", "-"),
            ("202870", "TF-MT", "2025", "Vonter Moses Amuto", "N/A", "21320319", "N/A", "41465467", "N/A", "-", "-", "-", "-"),
            ("202846", "TF-MT", "2025", "Willis Ogumbo othiambo", "8671565", "11562991", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202876", "TF-MT", "2024", "Jane wanjiru", "359820", "4828287", "N/A", "33036142", "1458214", "2942546", "-", "-", "-"),
            ("202861", "TF-MT", "Mar-26", "Ann Njoroge", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("202963", "TF-MT", "Oct-26", "Fridah Gastaiti", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("-", "TF-MT", "Jul-26", "Beryl Jeptoo", "2253273", "N/A", "N/A", "35017099", "N/A", "N/A", "-", "-", "-"),
            ("202871", "TF-MT", "2024", "Loureen Anyango Agutu", "N/A", "6763274", "24720221", "27503464", "512400592", "782234653", "-", "-", "-"),
            ("202891", "TF-MT", "2023", "Maryanne Wanjiru Kariuki", "7131147", "21258218", "N/A", "22490702", "A0701169", "A4404579", "-", "-", "-"),
            ("-", "TF-MT", "2025", "Mercy Chepkemoi", "7651555", "8548725", "N/A", "23779678", "121224700", "122119234", "-", "-", "-"),
            ("202885", "TF-MT", "2020", "Mourine Akoth", "10822795", "28243742", "N/A", "33548098", "4496868", "-", "-", "-", "-"),
            ("280222", "TF-MT", "Apr-26", "Shania Joy", "N/A", "N/A", "13383612", "N/A", "N/A", "N/A", "-", "-", "-"),
            ("202874", "TF-MT", "2025", "Valary Chepkoech Bii", "1366326", "7960048", "N/A", "N/A", "-", "-", "-", "-", "-"),
            ("-", "TF-MT", "Jul-26", "Vallary Akinyi", "N/A", "20065485", "N/A", "33716569", "5059601", "-", "-", "-", "-"),
            ("202878", "TF-MT", "2024", "Brendah Achieng Gumba", "N/A", "10533906", "N/A", "N/A", "391729842", "392200448", "-", "-", "-"),
            ("280003", "TF-MT", "Jun-26", "Brian Kang'ethe", "N/A", "24705142", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202877", "TF-MT", "2025", "Catherine Awino Agutu", "-", "-", "N/A", "27422318", "4207822", "9349719", "-", "-", "-"),
            ("202893", "TF-MT", "2023", "Damaris Wekesa", "N/A", "829543", "N/A", "29621541", "-", "1311904839", "1311323602", "-", "-"),
            ("-", "TF-MT", "Nov-26", "Dorine Anyango Odongo", "7328824", "6666068", "N/A", "N/A", "2052600642", "-", "-", "-", "-"),
            ("202845", "TF-MT", "2025", "Ebby Kageha lomosi", "3243910", "6525191", "N/A", "N/A", "67646", "1055943", "-", "-", "-"),
            ("202867", "TF-MT", "2025", "Eunice Wambui", "22158745", "25712558", "N/A", "N/A", "1442211376", "-", "-", "-", "-"),
            ("202895", "TF-MT", "2014", "Jane Wairimu", "N/A", "5981674", "N/A", "N/A", "39323500", "271722809", "-", "-", "-"),
            ("280220", "TF-MT", "Mar-26", "Joseph Mumanyi", "7936972", "10003795", "N/A", "41229249", "1849133", "-", "-", "-", "-"),
            ("280507", "TF-MT", "Nov-26", "Manase Karanja Thuo", "11154721", "21620654", "N/A", "N/A", "N/A", "N/A", "-", "-", "-"),
            ("70221", "TF-MT", "2023", "Pamela Awuor Nyadodo", "N/A", "9554703", "N/A", "22793574", "391122658", "390515422", "-", "-", "-"),
            ("-", "TF-MT", "Nov-26", "Bartholomew Wekesa musundi", "9721630", "13561414", "N/A", "N/A", "172117769", "-", "-", "-", "-"),
            ("-", "TF-MT", "Oct-26", "Rachael Gathoni wangigi", "8846144", "N/A", "N/A", "N/A", "851318363", "851610578", "-", "-", "-"),
            ("292979", "TF-MT", "Jul-26", "Risper Moraa Momanyi", "8730577", "N/A", "N/A", "N/A", "246730359", "-", "-", "-", "-"),
            ("292959", "TF-MT", "Jul-26", "Samuel onyango", "N/A", "13129230", "N/A", "860805859", "N/A", "N/A", "-", "-", "-"),
            ("202890", "TF-MT", "2023", "John Mwangi", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("280270", "TF-MT", "Jul-26", "Whitney Arot Aturae", "N/A", "21596130", "N/A", "-", "-", "-", "-", "-", "-"),
            ("202873", "TF-MT", "2023", "Brian Ombwori Osese", "1618384", "7607080", "N/A", "37219432", "902027", "5733030", "-", "-", "-"),
            ("202835", "TF-MT", "2024", "Diana Nanjala wafula", "21253105", "23122140", "N/A", "32457447", "-", "-", "-", "-", "-"),
            ("202920", "TF-MT", "2025", "Elvis Shikuku", "14678081", "1181476", "N/A", "N/A", "N/A", "N/A", "-", "-", "-"),
            ("202882", "TF-MT", "2023", "Irene Ogutu", "N/A", "5772466", "N/A", "29341825", "N/A", "4057128", "4198133", "-", "-"),
            ("202859", "TF-MT", "Jan-26", "Emma Watindi", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("202849", "TF-MT", "2025", "Jacinta Apondi", "N/A", "22858932", "N/A", "N/A", "N/A", "N/A", "-", "-", "-"),
            ("202888", "TF-MT", "2017", "Jackline Kavere Ayiga", "521394", "-", "23987409", "5466522", "111414657", "111136627", "112004194", "-", "-"),
            ("202884", "TF-MT", "2024", "Mercy Achieng Onyango", "N/A", "N/A", "21999525", "28376863", "7206211", "7206057", "-", "-", "-"),
            ("202889", "TF-MT", "2021", "Naomi Jeruto Tanui", "N/A", "20153118", "N/A", "N/A", "9596061", "-", "-", "-", "-"),
            ("202839", "TF-MT", "2025", "Otieno lavenda", "N/A", "20680682", "N/A", "N/A", "N/A", "-", "-", "-", "-"),
            ("202628", "HQ", "2015", "JANEDRIX AKINYI SADAKA", "N/A", "JOYCE SAKAKA", "-", "N/A", "JAMES SADAKSA", "JOYBLESSING", "-", "-", "-"),
            ("N/A", "HQ", "2015", "CELESTINE ATIENO SADAKA", "N/A", "JOYCE SAKAKA", "-", "N/A", "LINCOL", "IAN", "ANDREY", "-", "-"),
            ("280314", "HQ", "11/082026", "LAZARUS OKECHI", "NICODEMUS OGOTI", "MARY AJIAMBO", "-", "PURITY KABATI", "AZARIA AJIAMBO", "-", "-", "-", "-"),
            ("N/A", "HQ", "2020", "PATRIC TITO", "TITO NZONGA", "FELISTERS TITO", "-", "FRIDAH KARIMI", "TIFFANY TITO", "BARAKA TITO", "-", "-", "-"),
            ("292930", "HQ", "11/082026", "EDDY NYANGORI", "JOHN NYANGORI", "HELLENE ACHIENG", "-", "N/A", "-", "-", "-", "-", "-"),
            ("Sherine Atieno", "Antonia", "1st June 2026", "Sherine Atieno Otieno", "N/A", "23333405", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"),
            ("280225", "Antonia", "1st June 2026", "Stepheny Keziah Wambui Mwangi", "10452983", "10166506", "-", "34439485", "1463604", "2498854", "-", "-", "-"),
            ("202640", "Java House", "06/01/2024", "Samuel Njeru Njiru", "NA", "12402044", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202642", "Java House", "02/01/2023", "Eugene Daudi Aura", "12684478", "22143892", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202643", "Java House", "16/06/2023", "Wamuyu Irene Wairimu", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("280226", "Java House", "22/06/2026", "Alice Maina", "21154721", "5925331", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("292965", "Java House", "05/05/2026", "Sylvia Agosa", "NA", "27589904", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202648", "Java House", "08/01/2022", "Esther Wangari Karanja", "NA", "2947799", "NA", "28442445", "661711470", "131927789", "NA", "-", "-"),
            ("202649", "Java House", "08/01/2023", "Emily Waithera Njenga", "12679084", "29681293", "NA", "31609269", "74506389", "NA", "NA", "-", "-"),
            ("280372", "Java House", "09/09/2026", "Joan Ensha Wairimu", "7178165", "10271736", "NA", "NA", "27163167", "NA", "NA", "-", "-"),
            ("202651", "Java House", "15/04/2024", "Edwin Ondieki Kiyaka", "6925315", "25820458", "NA", "36314446", "272309733", "NA", "NA", "-", "-"),
            ("202652", "Java House", "23/11/2023", "Gladys Kinuthia", "730157", "NA", "NA", "NA", "721471", "B750670", "NA", "-", "-"),
            ("280507", "Java House", "16/09/2026", "Purity mukami", "NA", "21461686", "NA", "NA", "207735072", "NA", "NA", "-", "-"),
            ("202654", "Java House", "17/05/2025", "Samwel Erick Odhiambo", "NA", "11705391", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202655", "Java House", "04/01/2025", "Felister Gatwiri Muriithi", "8601366", "21461686", "NA", "27924521", "1752770", "NA", "NA", "-", "-"),
            ("202666", "Java House", "21/07/2026", "Charity Moraa Juma", "12696585", "NA", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202660", "Java House", "01/01/2026", "Brian Mwenda Njue", "NA", "11326767", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202661", "Java House", "11/11/2025", "Emmanuel Mike Ochieng", "NA", "20465576", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202662", "Java House", "11/11/2025", "Caroline Muthoni Mugo", "NA", "9410131", "NA", "NA", "447404", "NA", "NA", "-", "-"),
            ("202664", "Java House", "13/03/2026", "Jeniffer Wanjira Ndung'u", "3081426", "NA", "NA", "NA", "4694621", "NA", "NA", "-", "-"),
            ("202670", "Java House", "06/06/2025", "Maureen Gathiru Mwaniki", "8949712", "9484232", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202671", "Java House", "01/01/2025", "Lilian Adhiambo Randa", "NA", "NA", "22175755", "28042042", "4363793", "6390498", "NA", "-", "-"),
            ("202673", "Java House", "05/05/2024", "Pauline Wambui Masila", "NA", "4872231", "NA", "28587029", "6097147", "A3489654", "NA", "-", "-"),
            ("202674", "Java House", "29/11/2023", "Anne Kamonya Mulema", "NA", "NA", "1881637", "29867375", "9746194", "7016764", "NA", "-", "-"),
            ("202675", "Java House", "06/06/2025", "Daniel Ombui Mayaka", "6925939", "5825881", "NA", "29893290", "7090003", "9105030", "NA", "-", "-"),
            ("202934", "Java House", "01/01/2026", "Jeff Otieno Maina", "NA", "NA", "33964654", "NA", "NA", "NA", "NA", "-", "-"),
            ("202935", "Java House", "01/01/2026", "Jedida Njoki Kinyanjui", "NA", "4244441", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202937", "Java House", "02/02/2026", "Clifton Kelvin Makokha", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202952", "Java House", "01/01/2026", "Collen Elizabeth Ojiambo", "NA", "NA", "NA", "NA", "7072542", "7515539", "7135442", "-", "-"),
            ("202978", "Java House", "02/02/2026", "Jackline Wanza Muthoka", "NA", "13796649", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("292915", "Java House", "05/05/2026", "Francis Omari", "NA", "21065823", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202686", "Java House", "16/04/2017", "Evaperpetual Wambui Maina", "NA", "13542413", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202603", "Java House", "01/09/2020", "Mariam Juma", "NA", "NA", "NA", "NA", "41335956", "260828238", "608994032", "-", "-"),
            ("280528", "Java House", "11/01/2026", "Hydrick Kipkorir", "NA", "NA", "NA", "620201", "NA", "NA", "NA", "-", "-"),
            ("-", "Java House", "01/11/2026", "Kendy Njeri", "NA", "26001602", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("-", "Java House", "01/11/2026", "Joseph Chege", "3054830", "NA", "NA", "38220338", "NA", "NA", "NA", "-", "-"),
            ("-", "Java House", "01/11/2026", "Specioza Matitsa", "NA", "NA", "NA", "NA", "NA", "NA", "NA", "-", "-"),
            ("202989", "SCJohnson", "Feb-26", "Bonface Nzuki", "13592548", "20001605", "-", "-", "-", "-", "-", "-", "-"),
            ("202774", "SCJohnson", "Aug-24", "Oscar kipkoech Ruto", "8715105", "25972243", "N/A", "643055126", "604533", "-", "-", "-", "-"),
            ("90117", "SCJohnson", "Aug-22", "Hilda Esende Lugangi", "22499361", "22546698", "Nil", "22499361", "330400075", "370207832", "371929483", "-", "-"),
            ("Lena Cherono", "SCJohnson", "Oct-26", "Lena Cherono", "N/A", "6013139", "6013139", "-", "-", "-", "-", "-", "-"),
            ("202788", "SCJohnson", "Aug-23", "Afline Anyango Onyango", "N/A", "N/A", "25083427", "N/A", "538317", "538318", "538342", "880993", "8908622"),
            ("202786", "SCJohnson", "Aug-22", "Judith Oweya Lukale", "6308832", "1232343", "-", "-", "7281845", "8355678", "-", "-", "-"),
            ("202784", "SCJohnson", "45839", "Farida Olesi", "N/A", "21667279", "-", "-", "4164247", "-", "-", "-", "-"),
            ("Phesial Jaramogi Ooyi", "SCJohnson", "Aug-22", "Phesial Jaramogi Ooyi", "2631938", "21217207", "N/A", "38946763", "7493054", "3486480", "-", "-", "-"),
            ("201743", "SCJohnson", "25-Apr", "Zachary Joel Moriasi", "N/A", "31295653", "N/A", "-", "-", "-", "-", "-", "-"),
            ("202976", "SCJohnson", "Feb-26", "Winfred mwende john", "N/A", "8966707", "N/A", "28782624", "-", "261287576", "-", "-", "-"),
            ("202782", "SCJohnson", "Dec-25", "Victoria wangechi Mugwe", "5988617", "11032615", "-", "-", "1512406016", "-", "-", "-", "-"),
            ("202775", "SCJohnson", "Feb-23", "Milka Wawuda Mwang'ombe", "N/A", "58719", "-", "-", "-", "-", "-", "-", "-"),
            ("202780", "SCJohnson", "2022", "Mokua Frankline", "23751234", "24351022", "-", "37120961", "-", "-", "-", "-", "-"),
            ("202765", "SCJohnson", "Aug-25", "Hannah Warukira Mwangi", "3582703", "N/A", "-", "-", "0071503182", "-", "-", "-", "-"),
            ("202977", "Scjohnsons", "26 Jan,2026", "Emily Mueni Mutua", "N/A", "N/A", "3545974", "-", "212327285", "212303274", "-", "-", "-"),
            ("202764", "Scjohnsons", "August,2025", "Agnes Wangu Mwangi", "9263345", "20409743", "-", "-", "201192", "-", "-", "-", "-"),
            ("202769", "scjohnsons", "Aug-25", "Joshua mwangi iguna", "10380353", "31107389", "-", "511795193", "-", "-", "-", "-", "-"),
            ("202761", "SC Johnson", "Apr_25", "Hannah wanjiku", "N/A", "N/A", "N/A", "N/A", "2384950", "-", "-", "-", "-"),
            ("202777", "SCJohnson", ",Sept 2022", "Caroline Kathomi Njebiu", "N/A", "N/A", "-", "-", "-", "-", "-", "-", "-"),
            ("202757", "SCJohnson", "26/22/2024", "Fedinand Kafwa", "N/A", "N/A", "-", "-", "-", "-", "-", "-", "-"),
            ("202772", "SCJohnson", ",Feb 2025", "Maureen Njeri", "N/A", "N/A", "-", "-", "-", "-", "-", "-", "-"),
            ("280267", "SCJohnson", ",July 2026", "Patrick Kabiu Waweru", "N/A", "N/A", "-", "-", "-", "-", "-", "-", "-"),
            ("202766", "SCJohnson", ",April 2025", "Veronica Mukolwe", "N/A", "21000046", "N/A", "N/A", "265075567", "-", "-", "-", "-"),
            ("202789", "SCJohnson", ",Aug 2022", "Celestine Auma Ouko", "25837011", "8212095", "-", "21166739", "6658291", "-", "-", "-", "-"),
            ("FIG001", "FIG", "2026-01", "Marlon K. Ang'undu", "-", "-", "1951498", "-", "6879175", "-", "-", "-", "-"),
            ("FIG002", "Gold Crown Beverage", "2026-01", "Mary Ngotah", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("FIG003", "SC Johnsons", "2026-01", "Celestine Ouko", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("FIG004", "Nairobi Java", "2026-01", "Irene Wamuyu", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
            ("FIG005", "Last Mile Trufoods Ltd", "2026-01", "Jonathan Mutunga", "-", "-", "-", "-", "-", "-", "-", "-", "-"),
        ]
        for s in seed:
            cur.execute("INSERT INTO users (staff_no, project, month_joined, full_names, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5, status) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?, 'active member')", s)
        con.commit()
    con.close()

init_db()

def shell(title, body):
    return f"""<!DOCTYPE html><html><head><meta name="viewport" content="width=device-width, initial-scale=1"><title>{title}</title><style>body{{font-family:Arial;margin:0;background:white;color:black}}header{{background:darkblue;color:white;padding:14px}}nav a{{color:white;margin-right:12px;text-decoration:none;font-weight:bold}}main{{padding:14px}}table{{width:100%;border-collapse:collapse}}th,td{{border:1px solid lightgray;padding:8px;text-align:left}}th{{background:lightgray}}input,select,button{{padding:10px;margin:4px 0;width:100%;box-sizing:border-box}}button{{background:darkblue;color:white;border:none;font-weight:bold}}.card{{border:1px solid lightgray;padding:12px;margin-bottom:10px}}</style></head><body><header><b>LONMA ORBIT - FIG WELFARE</b><br><nav><a href="/">Home</a><a href="/register">Register</a><a href="/members">Members</a><a href="/history">History</a><a href="/shareout">Share-Out</a><a href="/community">Community</a></nav></header><main><h1>{title}</h1>{body}</main></body></html>"""

@app.route("/")
def home():
    con = get_db()
    total = con.execute("SELECT COUNT(*) FROM users WHERE status='active member'").fetchone()[0]
    con.close()
    h = ""
    h += f"<div class='card'><b>Active Members: {total}</b><br>Contribution: Ksh 300 per month<br>Deducted from monthly pay</div>"
    h += "<div class='card'><b>Membership Rule</b><br>Once you are employed with FIG, you automatically become a member. No application needed. Membership starts on your employment date.</div>"
    h += "<div class='card'><b>Death Benefits</b><br>Member: 100,000 | Spouse: 50,000 | Child: 40,000 | Parents: 40,000<br>Loss of Earning: 50% of basic pay, max Ksh 20,000, after 10 days unable to work</div>"
    h += "<div class='card'><b>Year-End</b><br>Minimum balance Ksh 250,000. Amount above is shared only among current active members. Year ends 30 November. Audited accounts by 20 December in FACES family group.</div>"
    return shell("Home", h)

@app.route("/register", methods=["GET", "POST"])
def register():
    if request.method == "POST":
        full_names = request.form.get("full_names", "").strip()
        staff_no = request.form.get("staff_no", "").strip()
        project = request.form.get("project", "").strip()
        month_joined = request.form.get("month_joined", "").strip()
        father_id = request.form.get("father_id", "-").strip() or "-"
        mother_id = request.form.get("mother_id", "-").strip() or "-"
        guardian_id = request.form.get("guardian_id", "-").strip() or "-"
        spouse_id = request.form.get("spouse_id", "-").strip() or "-"
        kid1 = request.form.get("kid1", "-").strip() or "-"
        kid2 = request.form.get("kid2", "-").strip() or "-"
        kid3 = request.form.get("kid3", "-").strip() or "-"
        kid4 = request.form.get("kid4", "-").strip() or "-"
        kid5 = request.form.get("kid5", "-").strip() or "-"
        if full_names:
            con = get_db()
            con.execute("INSERT INTO users (full_names, staff_no, project, month_joined, status, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5) VALUES (?,?,?,?, 'active member', ?,?,?,?,?,?,?,?,?)", (full_names, staff_no, project, month_joined, father_id, mother_id, guardian_id, spouse_id, kid1, kid2, kid3, kid4, kid5))
            con.execute("INSERT INTO history (full_names, action, amount, date) VALUES (?, 'Joined - Automatic Membership on Employment', 0, ?)", (full_names, month_joined))
            con.commit()
            con.close()
            return redirect("/members")
    h = ""
    h += "<form method='POST'>"
    h += "<label>Full Names</label><input name='full_names' required>"
    h += "<label>Staff No</label><input name='staff_no'>"
    h += "<label>Project / Company</label><input name='project' placeholder='FIG'>"
    h += "<label>Year Joined / Employment Date</label><input name='month_joined' placeholder='2026-01'>"
    h += "<label>Father ID</label><input name='father_id' placeholder='-'>"
    h += "<label>Mother ID</label><input name='mother_id' placeholder='-'>"
    h += "<label>Guardian ID - if no biological parents</label><input name='guardian_id' placeholder='-'>"
    h += "<label>Spouse ID</label><input name='spouse_id' placeholder='-'>"
    h += "<label>Kid 1 - Birth Cert Number</label><input name='kid1' placeholder='-'>"
    h += "<label>Kid 2</label><input name='kid2' placeholder='-'>"
    h += "<label>Kid 3</label><input name='kid3' placeholder='-'>"
    h += "<label>Kid 4</label><input name='kid4' placeholder='-'>"
    h += "<label>Kid 5</label><input name='kid5' placeholder='-'>"
    h += "<button type='submit'>Register - Automatic Member</button></form>"
    h += "<p>By registering, you confirm employment with FIG. You automatically become a member.</p>"
    return shell("Register", h)

@app.route("/members")
def members():
    con = get_db()
    rows = con.execute("SELECT * FROM users ORDER BY full_names").fetchall()
    con.close()
    h = "<input id='q' placeholder='Search member...' onkeyup='f()'>"
    h += "<table><thead><tr><th>Staff No</th><th>Full Names</th><th>Project</th><th>Year Joined</th><th>Status</th><th>Father</th><th>Mother</th><th>Guardian</th><th>Spouse</th><th>Kid 1</th><th>Kid 2</th><th>Kid 3</th><th>Kid 4</th><th>Kid 5</th></tr></thead><tbody id='tb'>"
    for m in rows:
        h += f"<tr><td>{m['staff_no']}</td><td>{m['full_names']}</td><td>{m['project']}</td><td>{m['month_joined']}</td><td>{m['status']}</td><td>{m['father_id']}</td><td>{m['mother_id']}</td><td>{m['guardian_id']}</td><td>{m['spouse_id']}</td><td>{m['kid1']}</td><td>{m['kid2']}</td><td>{m['kid3']}</td><td>{m['kid4']}</td><td>{m['kid5']}</td></tr>"
    h += "</tbody></table>"
    h += "<script>function f(){var q=document.getElementById('q').value.toLowerCase();var tr=document.getElementById('tb').getElementsByTagName('tr');for(var i=0;i<tr.length;i++){tr[i].style.display=tr[i].textContent.toLowerCase().includes(q)?'':'none'}}</script>"
    return shell("Members", h)

@app.route("/history")
def history():
    con = get_db()
    rows = con.execute("SELECT * FROM history ORDER BY id DESC").fetchall()
    con.close()
    h = "<table><tr><th>Name</th><th>Action</th><th>Amount</th><th>Date</th></tr>"
    for r in rows:
        h += f"<tr><td>{r['full_names']}</td><td>{r['action']}</td><td>{r['amount']}</td><td>{r['date']}</td></tr>"
    h += "</table>"
    return shell("History", h)

@app.route("/shareout")
def shareout():
    con = get_db()
    rows = con.execute("SELECT * FROM users WHERE status='active member'").fetchall()
    con.close()
    total = len(rows) * 300
    above = total - 250000
    if above < 0:
        above = 0
    share = 0
    if len(rows) > 0:
        share = above / len(rows)
    h = f"<div class='card'>Active Members: {len(rows)}<br>Total Contribution: Ksh {total}<br>Minimum Balance: Ksh 250000<br>Amount Above Minimum: Ksh {above}<br>Share Per Member: Ksh {round(share,2)}</div>"
    h += "<table><tr><th>Name</th><th>Share</th></tr>"
    for m in rows:
        h += f"<tr><td>{m['full_names']}</td><td>{round(share,2)}</td></tr>"
    h += "</table>"
    return shell("Share-Out", h)

@app.route("/community")
def community():
    h = "<div class='card'><b>Officials</b><br>Marlon K. Ang'undu - Chairman, FIG - +254 707 780 807<br>Mary Ngotah - Gold Crown Beverage - 0719 203 286<br>Celestine Ouko - SC Johnsons - 0725 543 224<br>Irene Wamuyu - Nairobi Java - 0719 606 834<br>Jonathan Mutunga - Last Mile Trufoods Ltd - 0719 555 326</div>"
    h += "<div class='card'><b>Welfare Management</b><br>Welfare managed by committee elected by all members. Every project must have at least one member on board. Members elect office bearers from among themselves.</div>"
    return shell("Community", h)

@app.route("/fix_ids")
def fix_ids():
    con = get_db()
    con.execute("UPDATE users SET guardian_id='1951498', kid1='6879175' WHERE lower(full_names) LIKE '%marlon%'")
    con.commit()
    con.close()
    return "FIXED Marlon - Guardian 1951498 Kid 6879175"

@app.route("/api/members")
def api_members():
    con = get_db()
    rows = con.execute("SELECT * FROM users ORDER BY full_names").fetchall()
    con.close()
    out = []
    for m in rows:
        out.append({"full_names": m["full_names"], "staff_no": m["staff_no"], "project": m["project"], "status": m["status"], "month_joined": m["month_joined"], "father_id": m["father_id"], "mother_id": m["mother_id"], "guardian_id": m["guardian_id"], "spouse_id": m["spouse_id"], "kid1": m["kid1"], "kid2": m["kid2"], "kid3": m["kid3"], "kid4": m["kid4"], "kid5": m["kid5"]})
    return jsonify(out)

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
