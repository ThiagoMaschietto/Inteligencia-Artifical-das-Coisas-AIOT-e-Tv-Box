import serial
import serial.tools.list_ports
import requests
import json
import time

API_URL = "http://127.0.0.1:8000/telemetria/"
VELOCIDADE = 115200

def encontrar_todas_as_portas():
    portas_encontradas = []
    portas = list(serial.tools.list_ports.comports())
    for porta in portas:
        if "Arduino" in porta.description or "CH340" in porta.description or "USB" in porta.description:
            portas_encontradas.append(porta.device)
    return portas_encontradas

print("==================================================")
print("🌿 Gateway IoT QuerPlantar - Modo Varredura (Loop) ")
print("==================================================")

lista_de_portas = encontrar_todas_as_portas()

if not lista_de_portas:
    print("❌ Nenhum dispositivo IoT encontrado nas portas USB.")
    exit(1)

print(f"🔍 Hortas localizadas: {lista_de_portas}")
print("⚡ Abrindo conexões não-bloqueantes...")

# Dicionário para guardar todas as conexões abertas
conexoes_ativas = {}

for porta in lista_de_portas:
    try:
        # O segredo está aqui: timeout=0 faz o readline() NÃO FICAR PARADO esperando
        conexoes_ativas[porta] = serial.Serial(porta, VELOCIDADE, timeout=0)
        print(f"✅ Porta {porta} conectada com sucesso.")
    except Exception as e:
        print(f"❌ Falha ao abrir a porta {porta}: {e}")

print("\n🚀 Monitoramento unificado iniciado! Rodando em ciclo...")
print("--------------------------------------------------")

# --- LOOP ÚNICO E CONTÍNUO ---
try:
    while True:
        # Passa de placa em placa dando uma espiadinha no buffer
        for porta, arduino in list(conexoes_ativas.items()):
            try:
                # in_waiting diz quantos bytes estão dando sopa na fila daquela USB
                if arduino.in_waiting > 0:
                    # Como definimos timeout=0, ele puxa o que tiver ali na hora e já libera o código
                    linha = arduino.readline().decode('utf-8', errors='ignore').strip()
                    
                    if linha and list(linha)[0] == "{":
                        try:
                            payload = json.loads(linha)
                            id_horta = payload.get("horta_id", "Desconhecido")
                            
                            print(f"📥 [Dados Detectados] Horta ID: {id_horta} na porta {porta}")
                            
                            # Envia para a API FastAPI
                            resposta = requests.post(API_URL, json=payload)
                            
                            if resposta.status_code in [200, 210, 201]:
                                print(f"🚀 [Sucesso] Dados da Horta {id_horta} enviados ao banco de dados.")
                            else:
                                print(f"⚠️ [API Recusou] Código {resposta.status_code}: {resposta.text}")
                                
                        except json.JSONDecodeError:
                            pass # Ruído de linha parcial, ignora e espera o próximo ciclo
                            
            except serial.SerialException:
                print(f"❌ [Conexão Perdida] A placa da porta {porta} foi desconectada.")
                del conexoes_ativas[porta] # Remove da lista para não travar o loop
                
        # Uma micro pausa de 100 milissegundos para o processador do PC respirar
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Gateway por Varredura encerrado pelo usuário.")
    # Fecha todas as portas abertas antes de sair de vez
    for arduino in conexoes_ativas.values():
        arduino.close()