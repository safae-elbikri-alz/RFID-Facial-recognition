import paho.mqtt.client as mqtt
import paho.mqtt.publish as publish
import json
from cv2 import cv2

cascadePath = "haarcascade_frontalface_default.xml"
faceCascade = cv2.CascadeClassifier(cascadePath)

def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d

def on_connect(client, userdata, flags, rc):
    mqttc.subscribe("/esp8266/3/capture")
    print("LISTENING ...")

def on_message(client, userdata, message):
    if message.topic == "/esp8266/3/capture":
        reading = json.loads(message.payload.decode('utf-8'))
        if reading == 1:
            print("Taking Photo")

            # Taking picture
            cam = cv2.VideoCapture(0)
            stat = True
            while stat:
                s, frame = cam.read()
                im = frame
                gray=cv2.cvtColor(frame,cv2.COLOR_BGR2GRAY)
                faces = faceCascade.detectMultiScale(gray,1.3,5)
                for (x, y, w, h) in faces:
                    cv2.rectangle(frame, (x, y), (x+w, y+h), (255, 0, 0), 2)
                    if s:
                        cv2.imwrite("photo/shot.jpg",im)
                        stat = False
                    break

            f=open("photo/shot.jpg", "rb")
            fileContent = f.read()
            byteArr = bytearray(fileContent)

            publish.single("/esp8266/3/cam", byteArr, hostname="mqtt.eclipse.org")
            print("Published")
            
mqttc=mqtt.Client()
mqttc.on_connect=on_connect
mqttc.on_message=on_message
mqttc.connect("mqtt.eclipse.org",1883,60)
mqttc.loop_forever()