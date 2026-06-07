#include "DHT.h"

const int HORTA_ID = 2; 

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define PINO_SOLO A0
#define PINO_LUZ A1

const unsigned long INTERVALO = 1800000UL; 
unsigned long tempoAnterior = 0; 

void setup() {
  Serial.begin(115200); 
  dht.begin();
  pinMode(PINO_SOLO, INPUT);
  pinMode(PINO_LUZ, INPUT);
  
  enviarDados(); 
}

void loop() {
  unsigned long tempoAtual = millis();
  if (tempoAtual - tempoAnterior >= INTERVALO) {
    tempoAnterior = tempoAtual;
    enviarDados();
  }
}

void enviarDados() {
  float umidadeAr = dht.readHumidity();
  float temperatura = dht.readTemperature();

  int leituraSoloBruta = analogRead(PINO_SOLO);
  int umidadeSoloPorcento = map(leituraSoloBruta, 1023, 300, 0, 100);
  umidadeSoloPorcento = constrain(umidadeSoloPorcento, 0, 100);

  int leituraLuzBruta = analogRead(PINO_LUZ);
  int luminosidadePorcento = map(leituraLuzBruta, 650, 0, 0, 100);
  luminosidadePorcento = constrain(luminosidadePorcento, 0, 100);

  if (isnan(umidadeAr) || isnan(temperatura)) {
    return; 
  }

  Serial.print("{");
  Serial.print("\"horta_id\":");      Serial.print(HORTA_ID);
  Serial.print(",\"temperatura\":");   Serial.print(temperatura, 1);
  Serial.print(",\"umidade_ar\":");   Serial.print(umidadeAr, 0);
  Serial.print(",\"umidade_solo\":");      Serial.print(umidadeSoloPorcento);
  Serial.print(",\"luz\":"); Serial.print(luminosidadePorcento);
  Serial.println("}");
}