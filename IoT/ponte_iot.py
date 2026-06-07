import serial
import requests
import json
import time

# --- CONFIGURAÇÕES ---
PORTA_SERIAL = 'COM9'  # Ajuste para a sua porta COM do Arduino
VELOCIDADE = 115200
API_URL = "http://127.0.0.1:8000/telemetria/"
ID_DA_HORTA = 1

print("🌿 Ponte IoT QuerPlantar (Modo JSON Borda) Iniciada...")

try:
    arduino = serial.Serial(PORTA_SERIAL, VELOCIDADE, timeout=1)
    time.sleep(2)
    print("✅ Conectado ao Arduino! Aguardando pacotes JSON...")

    while True:
        if arduino.in_waiting > 0:
            linha = arduino.readline().decode('utf-8').strip()
            
            if linha:
                print(f"📥 JSON recebido da Borda: {linha}")
                
                try:
                    # O Python apenas valida se o JSON vindo do Arduino está correto
                    payload = json.loads(linha)
                    
                    # Carimba o ID do canteiro que o Python gerencia
                    payload["horta_id"] = ID_DA_HORTA
                    
                    # 🚨 CORREÇÃO AQUI: Traduz 'luminosidade' para 'luz' (o que o banco espera)
                    if "luminosidade" in payload:
                        payload["luz"] = payload.pop("luminosidade")
                    
                    # Dispara direto para o FastAPI
                    resposta = requests.post(API_URL, json=payload)
                    
                    if resposta.status_code in [200, 210, 201]:
                        print(f"🚀 Encaminhado com sucesso para a API: {payload}")
                    else:
                        print(f"⚠️ Erro na API ({resposta.status_code}): {resposta.text}")
                        
                except json.JSONDecodeError:
                    print("❌ Erro: String recebida não é um JSON válido.")
                except ValueError:
                    print("❌ Erro ao formatar tipos de dados.")
                    
        time.sleep(1)

except serial.SerialException:
    print(f"❌ Erro: Não foi possível abrir a porta {PORTA_SERIAL}.")
except KeyboardInterrupt:
    print("\n🛑 Ponte IoT encerrada.")