
#include <ESP8266WiFi.h> //Whe using ESP8266
#include <PubSubClient.h>
#include <arduinoFFT.h>

#define MIC A0

// Wifi security
const char *ssid = "INFINITUM3DB3_2.4";
const char *password = "Dragon2075";

// MQTT Broker IP address
const char *mqtt_server = "192.168.1.141";
// const char* mqtt_server = "10.25.18.8";

WiFiClient espClient;
PubSubClient client(espClient);

long start = 0;

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
    if (client.connect("ESP32Client_rojo"))
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

    Serial.println((float)(millis() - start) / 1000);
    Serial.println(counter);
    counter |= 0x8000;
    client.beginPublish("mic", 2, false);
    client.write((uint8_t *)&counter, 2);
    client.endPublish();
    start = millis();
    counter = 0;
  }
  else
  {

    client.beginPublish("mic", 2, false);
    client.write((uint8_t *)&adc, 2);
    client.endPublish();
  }
}
