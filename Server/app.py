import paho.mqtt.client as mqtt
from flask import Flask, render_template, request ,jsonify, url_for, redirect
import json, sqlite3, time, threading, numpy
from cv2 import cv2
import os, addDataSet, requests, training
from werkzeug.datastructures import ImmutableMultiDict

app = Flask(__name__)

cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

recognizer = cv2.face.LBPHFaceRecognizer_create()
recognizer.read('trainner/trainner.yml')

rfid_detected = 0
ledpir = 0
cam_data = {"cam_state":0,"cam_detected":0,"ledcam":0}
student_id = {'id': 0,'uid': '','nom': '','prenom': ''}
current_uid = ""
pins = {
    1 : {'name' : 'vert', 'board' : 'esp8266', 'topic' : 'esp8266/1/1', 'state' : 'False'},
    2 : {'name' : 'rouge', 'board' : 'esp8266', 'topic' : 'esp8266/1/2', 'state' : 'False'},
    3 : {'name' : 'blanche', 'board' : 'esp8266', 'topic' : 'esp8266/1/3', 'state' : 'False'}
    }

@app.route('/')
def index():
    global rfid_detected
    global ledpir
    global current_uid
    global student_id
    rfid_detected = 0
    ledpir = 0
    current_uid = ""
    student_id = {'id': 0,'uid': '','nom': '','prenom': ''}
    cam_data["cam_state"]=0
    cam_data["cam_detected"]=0
    cam_data["ledcam"]=0
    return render_template('index.html')

@app.route('/admin')
def admin():
    userData()
    return render_template('admin.html')

@app.route('/admin/userData')
def userData():
    con = sqlite3.connect("IOTPlatformData.db")
    c = con.cursor()
    c.execute("SELECT * FROM etudiants")
    data = c.fetchall()
    c.close()
    json_data = json.dumps(data)
    return json_data

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def on_connect(client, userdata, flags, rc):
    client.subscribe("/esp8266/1/rfid")
    client.subscribe("/esp8266/2/pir")
    client.subscribe("/esp8266/3/cam")

def on_message(client, userdata, message):
    if message.topic == "/esp8266/1/rfid" or message.topic == "/esp8266/2/pir" or message.topic == "/esp8266/3/cam" :
        global ledpir
        global rfid_detected
        global current_uid
        global student_id
        if message.topic == "/esp8266/1/rfid" and cam_data["cam_state"] == 0:
            readings_json = json.loads(message.payload.decode("utf-8"))
            print(readings_json)
            cam_data["ledcam"] = 0
            rfid_detected = 1
            cam_data["cam_detected"] = 0
            status = 0
            # Database Open Connection
            conn=sqlite3.connect('IOTPlatformData.db')
            conn.row_factory = dict_factory
            c=conn.cursor()
            # Database Querying
            c.execute('SELECT * from etudiants where UID="{}"'.format(readings_json["uid"]))
            student_id = c.fetchone()
            if student_id == None:
                status = 0
                cam_data["cam_state"] = 0
            else:
                status = 1
                current_uid = readings_json['uid'].strip()
                cam_data["cam_state"] = 1
                mqttc.publish("/esp8266/3/capture", 1)
            c.execute('INSERT INTO rfid_readings (UID, STATUS, currentdate, currentime) VALUES ("{}",{},date("now"),time("now"))'.format(readings_json["uid"],status))
            conn.commit()
            c.close()
            student_id = {'id': 0,'uid': '','nom': '','prenom': ''}
        if message.topic == "/esp8266/2/pir" :
            readings_json = json.loads(message.payload.decode("utf-8"))
            mqttc.publish(pins[3]['topic'],readings_json)
            ledpir = readings_json
            if readings_json == 1:
                pins[3]['state'] = 'True'
            else:
                pins[3]['state'] = 'False'
        if message.topic == "/esp8266/3/cam"  and cam_data["cam_state"] == 1:
            im=open("photo/shot.jpg","wb")
            im.write(message.payload)
            im.close()
            print("Saved")
            
            img = cv2.imread('photo/shot.jpg', 0)
            #Image Identification
            faces=faceCascade.detectMultiScale(img, 1.2,5)
            for(x,y,w,h) in faces:
                Id, conf = recognizer.predict(img[y:y+h,x:x+w])
                if(conf>=60):
                    Id=0
                print(Id)

            # Select the associated UID from database
            if(Id != 0):
                print(Id)
                con = sqlite3.connect('IOTPlatformData.db')
                con.row_factory = dict_factory
                c = con.cursor()
                c.execute('SELECT * from etudiants where id={}'.format(Id))
                student_id = c.fetchone()
                c.close()
            
            if student_id['uid'] == current_uid:
                cam_data["ledcam"] = 1
            else:
                cam_data["ledcam"] = 0
            
            rfid_detected = 0
            cam_data["cam_state"] = 0
            cam_data["cam_detected"] = 1
            current_uid = ""

@app.route('/data',methods=['GET', 'POST'])
def data():
    return dataRFID()

app.config['IMAGE_UPLOADS'] = "./static/etudiants"

@app.route('/addUser',methods=['GET', 'POST'])
def addUser():
    if(request.method == "POST"):
        try:
            userFormData = request.form.to_dict(flat=False)
            assert(userFormData["inputLastname"][0]!="")
            assert(userFormData["inputFirstname"][0]!="")
            assert(userFormData["inputUID"][0]!="")
            image = request.files['inputPhoto']
            assert(image.filename != '')
            Id = addDataSet.createData(userFormData)
            image.save(os.path.join(app.config['IMAGE_UPLOADS'], str(Id)+".jpg"))
            training.train()
            msg = json.dumps("1")
        except:
            msg = json.dumps("0")
            pass
    else:
        msg = json.dumps("0")
    return msg

@app.route('/removeUser', methods=['GET', 'POST'])
def deleteUser():
    if(request.method == "POST"):
        try:
            Id = int(json.loads(request.data)['id'])
            con = sqlite3.connect('IOTPlatformData.db')
            c = con.cursor()
            c.execute("DELETE FROM etudiants WHERE id={}".format(Id))
            con.commit()
            c.close()
            for i in range(1,252):
                os.remove("./dataSet/User."+str(Id)+"."+str(i)+".jpg")
            os.remove("./static/etudiants/"+str(Id)+".jpg")
            msg = json.dumps("1")
        except:
            msg = json.dumps("0")
    else:
        msg = json.dumps("0")
    return msg

def dataRFID():
    global rfid_detected
    rfid = []
    if(rfid_detected == 1):
        conn=sqlite3.connect('IOTPlatformData.db')
        conn.row_factory = dict_factory
        c=conn.cursor()
        c.execute('SELECT UID, STATUS FROM rfid_readings ORDER BY id DESC LIMIT 1')
        readings = c.fetchall()
        for row in readings:
            rfid.append(row["UID"])
            rfid.append(row["STATUS"])
        conn.close()
    return jsonify(rfid=rfid, ledpir=ledpir, cam_data=cam_data, student_id=student_id)
    
mqttc=mqtt.Client()
mqttc.on_connect=on_connect
mqttc.on_message=on_message
mqttc.connect("192.168.222.136",1883,60)
mqttc.loop_start()

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8181, debug=True)
