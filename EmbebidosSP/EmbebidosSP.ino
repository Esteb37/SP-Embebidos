
#include <ESP8266WiFi.h> //Whe using ESP8266
#include <PubSubClient.h>

#define MIC A0

#define NODE_FLAG 0x0000

const char *CLIENT_NAME = "NODE_2";

const char AVG_FREQ = NODE_FLAG == 0x4000 ? 64 : 65;

uint16_t END_FLAG = 0x8000 | NODE_FLAG;

// Wifi security
const char *ssid = "Hilda";
const char *password = "hildab04";

// MQTT Broker IP address
// const char *mqtt_server = "192.168.135.36";
const char *mqtt_server = "172.20.10.2";
// const char* mqtt_server = "10.25.18.8";

WiFiClient espClient;
PubSubClient client(espClient);

long start = 0;

long elapsed = 0;

uint16_t counter = 0;

// LED Pin
const int ledPin = 2;

uint16_t adc;
uint16_t samples;

uint16_t data[5000];

void setup()
{
  Serial.begin(9600);
  Serial.println("Starting");
  setup_wifi();
  client.setServer(mqtt_server, 1883);
  start = millis();
}

void setup_wifi()
{
  delay(10);
  // connecting to a WiFi network
  Serial.println();
  Serial.print("Connecting to ");
  Serial.println(ssid);

  WiFi.begin(ssid, password);

  while (WiFi.status() != WL_CONNECTED)
  {
    delay(500);
    Serial.print(".");
  }

  Serial.println("");
  Serial.println("WiFi connected");
  Serial.println("IP address: ");
  Serial.println(WiFi.localIP());
}

void reconnect()
{
  // Reconnect
  while (!client.connected())
  {
    Serial.print("Attempting MQTT connection...");
    // Attempt to connect
    if (client.connect(CLIENT_NAME))
    { //"ESPClient_3" represent the client name that connects to broker
      Serial.println("connected");
    }
    else
    {
      Serial.print("failed, rc=");
      Serial.print(client.state());
      Serial.println(" try again in 5 seconds");
      // Wait 5 seconds before retrying
      delay(5000);
    }
  }
}

void loop()
{
  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  adc = analogRead(MIC);

  counter++;

  if (millis() - start > 1000)
  {
    Serial.println("Publishing");
    client.beginPublish(CLIENT_NAME, 2, false);
    client.write((uint8_t *)&END_FLAG, 2);
    client.endPublish();
    start = millis();
    counter = 0;
  }
  else
  {

    adc |= NODE_FLAG;
    client.beginPublish(CLIENT_NAME, 2, false);
    client.write((uint8_t *)&adc, 2);
    client.endPublish();
  }
}
