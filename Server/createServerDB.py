import sqlite3, os

if(os.path.exists("./IOTPlatformData.db")):
    os.remove("./IOTPlatformData.db")

con = sqlite3.connect("IOTPlatformData.db")
c = con.cursor()
c.execute("CREATE TABLE rfid_readings (id INTEGER PRIMARY KEY AUTOINCREMENT, UID TEXT, STATUS INTEGER, currentdate DATE, currentime TIME)")
c.execute("CREATE TABLE etudiants (id INTEGER PRIMARY KEY AUTOINCREMENT, uid TEXT, nom TEXT, prenom)")
c.execute("CREATE TABLE stats (id INTEGER PRIMARY KEY AUTOINCREMENT, current_date DATE, current_time TIME)")
con.commit()
c.close()