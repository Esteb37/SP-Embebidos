#define MIC A0

uint16_t adc;

void setup()
{
    Serial.begin(115200);
}

void loop()
{
    adc = analogRead(MIC);
    Serial.println(adc);
    
}
