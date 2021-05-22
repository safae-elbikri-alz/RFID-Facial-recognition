from cv2 import cv2
import sqlite3,time


def createData(userFormData):
    detector=cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
    con = sqlite3.connect("IOTPlatformData.db")
    c = con.cursor()
    
    nom=userFormData["inputLastname"][0]
    prenom=userFormData["inputFirstname"][0]
    uid=userFormData["inputUID"][0]
    c.execute('INSERT INTO etudiants (uid,nom,prenom) VALUES ("'+uid+'","'+nom+'","'+prenom+'")')
    con.commit()

    c.execute('SELECT id FROM etudiants ORDER BY id DESC LIMIT 1')
    Id = c.fetchone()[0]
    con.close()

    count=0
    cam = cv2.VideoCapture(0)
    while(True):
        _, img = cam.read()
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(gray, 1.3, 5)
        for (x,y,w,h) in faces:
            cv2.rectangle(img,(x,y),(x+w,y+h),(255,0,0),2)
            count = count + 1
            cv2.imwrite("dataSet/User."+str(Id) +'.'+ str(count) + ".jpg", gray[y:y+h,x:x+w])
        if count>300:
            break

    cam.release()
    cv2.destroyAllWindows()
    return Id
