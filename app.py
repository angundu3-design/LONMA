from flask import Flask, request, jsonify, render_template_string, redirect, send_file
import sqlite3, os, secrets, io, re
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)
DB = "lonma.db"
VERSION = "v163"
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
"""
