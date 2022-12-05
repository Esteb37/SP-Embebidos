
#include <ESP8266WiFi.h> //Whe using ESP8266
#include <PubSubClient.h>

#define MIC A0

const char *CLIENT_NAME = "NODE_2";

const uint16_t END_FLAG = 0x8000;

uint8_t message_id = 0;

uint16_t payload = 0;

// Wifi security
const char *ssid = "INFINITUM3DB3_2.4";
const char *password = "Dragon2075";

// MQTT Broker IP address
const char *mqtt_server = "192.168.1.141";

WiFiClient espClient;
PubSubClient client(espClient);

uint64_t start = 0;

uint64_t elapsed = 0;

uint16_t counter = 0;

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

uint64_t micavg = 0;

void loop()
{

  if (!client.connected())
  {
    reconnect();
  }
  client.loop();

  if (millis() - start > 1000)
  {
    payload = (millis() - start) | END_FLAG;
    client.beginPublish(CLIENT_NAME, 2, false);
    client.write((uint8_t *)&payload, 2);
    client.endPublish();
    start = millis();
    counter = 0;
  }
  else
  {
    payload = analogRead(MIC);
    client.beginPublish(CLIENT_NAME, 2, false);
    client.write((uint8_t *)&payload, 2);
    client.endPublish();
  }
  counter++;
  delayMicroseconds(150);
}
