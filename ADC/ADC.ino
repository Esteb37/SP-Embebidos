#define MIC A0

uint16_t adc;

void setup()
{
    Serial.begin(9600);
}

void loop()
{
    adc = analogRead(MIC);
    Serial.println(adc);
    delay(1);
}
