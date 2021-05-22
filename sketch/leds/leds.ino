#include <ESP8266WiFi.h>
#include <PubSubClient.h>

const char* ssid = "";
const char* password = "";
const char* mqtt_server= "";

WiFiClient espClient;
PubSubClient client(espClient);

const int ledGPIO1 = D2;
const int ledGPIO2 = D3;
const int ledGPIO3 = D4;

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
    if (client.connect("ESP8266Client1")) {
      Serial.println("connected");  
      // Subscribe or resubscribe to a topic
      // You can subscribe to more topics (to control more LEDs in this example)
      client.subscribe("esp8266/1/1");
      client.subscribe("esp8266/1/2");
      client.subscribe("esp8266/1/3");
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
  pinMode(ledGPIO1, OUTPUT);
  pinMode(ledGPIO2, OUTPUT);
  pinMode(ledGPIO3, OUTPUT);
  Serial.begin(115200);   // Initiate a serial communication (9600)
  setup_wifi();
  Serial.println();
  
  client.setServer(mqtt_server, 1883);
  client.setCallback(callback);
}

void callback(String topic, byte* message, unsigned int length) {
  Serial.print("Message arrived on topic: ");
  Serial.print(topic);
  Serial.print(". Message: ");
  String messageLED;
  
  for (int i = 0; i < length; i++) {
    Serial.print((char)message[i]);
    messageLED += (char)message[i];
  }
  Serial.println();
  
  // Feel free to add more if statements to control more GPIOs with MQTT
  
  // If a message is received on the topic home/office/esp1/gpio2, you check if the message is either 1 or 0. Turns the ESP GPIO according to the message
  if(topic=="esp8266/1/1"){
    Serial.print("Changing GPIO 1 to ");
    if(messageLED == "1"){
      digitalWrite(ledGPIO1, HIGH);
      Serial.print("On");
    }
    else if(messageLED == "0"){
      digitalWrite(ledGPIO1, LOW);
      Serial.print("Off");
    }
  }
  if(topic=="esp8266/1/2"){
    Serial.print("Changing GPIO 2 to ");
    if(messageLED == "1"){
      digitalWrite(ledGPIO2, HIGH);
      Serial.print("On");
    }
    else if(messageLED == "0"){
      digitalWrite(ledGPIO2, LOW);
      Serial.print("Off");
    }
  }
  if(topic=="esp8266/1/3"){
    Serial.print("Changing GPIO 3 to ");
    if(messageLED == "1"){
      digitalWrite(ledGPIO3, HIGH);
      Serial.print("On");
    }
    else if(messageLED == "0"){
      digitalWrite(ledGPIO3, LOW);
      Serial.print("Off");
    }
  }
  Serial.println();
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
  client.connect("ESP8266Client1");
}
