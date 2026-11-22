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
            ("Sherine Atieno", "Antonia", "Jun-26", "Sherine Atieno Otieno", "N/A", "23333405", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A", "N/A"),
("280225", "Antonia", "Jun-26", "Stepheny Keziah Wambui Mwangi", "10452983", "10166506", "-", "34439485", "1463604", "2498854", "-", "-", "-"),
