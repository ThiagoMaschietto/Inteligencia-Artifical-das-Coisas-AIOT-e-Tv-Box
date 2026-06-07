#include "DHT.h"

#define DHTPIN 2
#define DHTTYPE DHT11
DHT dht(DHTPIN, DHTTYPE);

#define PINO_SOLO A0
#define PINO_LUZ A1

// --- CONFIGURAÇÃO DE TEMPO ---
// 30 minutos = 30 * 60 * 1000 = 1.800.000 milissegundos
const unsigned long INTERVALO = 1800000UL; 
unsigned long tempoAnterior = 0; // Guarda o momento do último envio

void setup() {
  Serial.begin(115200);
  dht.begin();
  pinMode(PINO_SOLO, INPUT);
  pinMode(PINO_LUZ, INPUT);
  
  // Boas-vindas da Borda: Envia uma leitura IMEDIATAMENTE ao ligar para testar o fluxo
  enviarDados(); 
}

void loop() {
  // Captura o tempo atual do cronômetro interno do Arduino
  unsigned long tempoAtual = millis();
  
  // Verifica se a diferença entre o tempo atual e o último envio é maior ou igual a 30 min
  if (tempoAtual - tempoAnterior >= INTERVALO) {
    tempoAnterior = tempoAtual; // Atualiza o marcador de tempo
    enviarDados();              // Executa a transmissão
  }
}

// Isolamos a lógica de leitura e envio em uma função dedicada
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
    return; // Se o sensor falhar, ignora este ciclo
  }

  // Serialização do JSON
  Serial.print("{");
  Serial.print("\"temperatura\":");   Serial.print(temperatura, 1);
  Serial.print(",\"umidade_ar\":");   Serial.print(umidadeAr, 0);
  Serial.print(",\"umidade\":");      Serial.print(umidadeSoloPorcento);
  Serial.print(",\"luminosidade\":"); Serial.print(luminosidadePorcento);
  Serial.println("}");
}