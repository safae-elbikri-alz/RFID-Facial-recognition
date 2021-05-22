#include <ESP8266WiFi.h>
#include <SPI.h>
#include <PubSubClient.h>
#include <MFRC522.h>

const char* ssid = "fahdarh";
const char* password = "123456789";
const char* mqtt_server = "192.168.43.232";

WiFiClient espClient;
PubSubClient client(espClient);

const int SS_PIN = D2;
const int RST_PIN = D1;

MFRC522 mfrc522(SS_PIN, RST_PIN);   // Create MFRC522 instance.

long now = millis();
long lastMeasure = 0;

void setup_wifi() {
  delay(10);
  // We start by connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);
  WiFi.begin(ssid, password);
  while (WiFi.status() != WL_CONNECTED) {
    delay(500);
    Serial.print(".");
  }
  Serial.println("");
  Serial.print("WiFi connected - ESP IP address: ");
  Serial.println(WiFi.localIP());
}


void reconnect() {
  // Loop until we're reconnected
  while (!client.connected()) {
    Serial.print("Attempting MQTT connection...");  
    if (client.connect("ESP8266Client")) {
      Serial.println("connected");  
      // Subscribe or resubscribe to a topic
      // You can subscribe to more topics (to control more LEDs in this example)
    } else {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void setup() 
{
  Serial.begin(115200);   // Initiate a serial communication (9600)
  SPI.begin();      // Initiate  SPI bus
  setup_wifi();
  mfrc522.PCD_Init();   // Initiate MFRC522
  Serial.println("Approximate your card to the reader...");
  Serial.println();
  
  client.setServer(mqtt_server, 1883);
}

void loop() 
{
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop()) 
  client.connect("ESP8266Client");
  
  now = millis();
  // Publishes new temperature and humidity every 10 seconds
  
  // Look for new cards
  if ( ! mfrc522.PICC_IsNewCardPresent()) 
  {
    return;
  }
  // Select one of the cards
  if ( ! mfrc522.PICC_ReadCardSerial()) 
  {
    return;
  }
  lastMeasure = now;
  //Show UID on serial monitor
  
  Serial.print("UID tag :");
  String content= "";
  byte letter;
  String etat;
  for (byte i = 0; i < mfrc522.uid.size; i++) 
  {
     Serial.print(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " ");
     Serial.print(mfrc522.uid.uidByte[i], HEX);
     content.concat(String(mfrc522.uid.uidByte[i] < 0x10 ? " 0" : " "));
     content.concat(String(mfrc522.uid.uidByte[i], HEX));
  }
  Serial.println();
  Serial.print("Message : ");
  content.toUpperCase();
  if (content.substring(1) == "D1 51 C9 73") //change here the UID of the card/cards that you want to give access 
  {
    etat="1";
    Serial.println("Authorized access");
    Serial.println();
  }
 
  else {
    etat="0";
    Serial.println("Access denied");
  }
  String m="{ \"uid\": \""+content+"\",\"status\" :"+etat+"}";
  char msg[50];
  m.toCharArray(msg,50);
  client.publish("/esp8266/1/rfid", msg);
  Serial.print("status: ");
  Serial.print(etat);
  Serial.print(" \t UID: ");
  Serial.print(content);
  Serial.println(" ");
  delay(3000);
}
