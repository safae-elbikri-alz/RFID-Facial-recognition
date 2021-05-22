#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "fahdarh";
const char* password = "123456789";
const char* mqtt_server= "192.168.43.42";

WiFiClient espClient;
PubSubClient client(espClient);

int PIR_PIN = D4;              // the pin that the sensor is atteched to

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
    if (client.connect("ESP8266Client3")) {
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

void setup() {
  pinMode(PIR_PIN, INPUT);    // initialize sensor as an input
  Serial.begin(115200);        // initialize serial (9600)
  setup_wifi();
  Serial.println();
  
  client.setServer(mqtt_server, 1883);
}

void loop(){
  if (!client.connected()) {
    reconnect();
  }
  if(!client.loop())
/*
     YOU  NEED TO CHANGE THIS NEXT LINE, IF YOU'RE HAVING PROBLEMS WITH MQTT MULTIPLE CONNECTIONS
     To change the ESP device ID, you will have to give a unique name to the ESP8266.
     Here's how it looks like now:
       client.connect("ESP8266Client");
     If you want more devices connected to the MQTT broker, you can do it like this:
       client.connect("ESPOffice");
     Then, for the other ESP:
       client.connect("ESPGarage");
      That should solve your MQTT multiple connections problem

     THE SECTION IN recionnect() function should match your device name
    */    
  client.connect("ESP8266Client3");
  
  if (digitalRead(PIR_PIN) == HIGH) {           // check if the sensor is HIGH
    client.publish("/esp8266/2/pir", "1");
    Serial.println("LED ON");
    delay(5000);
  } 
  else {
      client.publish("/esp8266/2/pir", "0");
      Serial.println("LED OFF");
      delay(500);             // delay 200 milliseconds
  }
}
