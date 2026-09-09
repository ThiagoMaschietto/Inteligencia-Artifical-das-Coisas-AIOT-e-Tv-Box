import serial
import serial.tools.list_ports
import json
import time
import pandas as pd
import numpy as np
import joblib 
import shap
import os
import requests  # 👈 1. IMPORTANTE: Adicionado para envio Web

API_URL = "http://127.0.0.1:8000/telemetria/"
VELOCIDADE = 115200

# 1. Descobre a pasta exata onde este script (teste.py) está a rodar
DIRETORIO_ATUAL = os.path.dirname(os.path.abspath(__file__))

# 2. Constrói o caminho seguro para entrar na pasta 'IA' e pegar o ficheiro
CAMINHO_MODELO = os.path.join(DIRETORIO_ATUAL, 'IA', 'modelo_isolation_forest.joblib')

# ==================================================
# 🧠 INICIALIZAÇÃO DA IA (Carregamento do Cérebro)
# ==================================================
print("==================================================")
print("🧠 A iniciar o Motor de Inteligência Artificial...")
try:
    modelo_if = joblib.load(CAMINHO_MODELO)
    explainer_shap = shap.TreeExplainer(modelo_if)
    print("✅ IA Carregada com sucesso! Pronta para análise local.")
except Exception as e:
    print(f"⚠️ AVISO: Não foi possível carregar o modelo de IA. O ficheiro está na pasta correta? Erro: {e}")
    modelo_if = None

def aplicar_camada1(dados_sensores):
    """ Filtros Físicos Absolutos (O Segurança do Edge) """
    sensores_esperados = ['Temperatura (°C)', 'Umidade do Ar (%)', 'Umidade do Solo (%)', 'Luminosidade']
    for sensor in sensores_esperados:
        if sensor not in dados_sensores or dados_sensores[sensor] is None:
            return False, f"Hardware/Rede: Leitura do sensor '{sensor}' falhou ou está vazia."

    temp = dados_sensores['Temperatura (°C)']
    u_ar = dados_sensores['Umidade do Ar (%)']
    u_solo = dados_sensores['Umidade do Solo (%)']
    lum = dados_sensores['Luminosidade']

    if not (-10.0 <= temp <= 60.0):
        return False, f"Erro Físico Absoluto: Temperatura impossível de {temp}°C."
        
    if not (0.0 <= u_ar <= 100.0):
        return False, f"Erro Físico Absoluto: Umidade do Ar impossível de {u_ar}%."
        
    if not (0.0 <= u_solo <= 100.0):
        return False, f"Erro Físico Absoluto: Umidade do Solo impossível de {u_solo}%."
        
    if not (0.0 <= lum <= 100.0):
        return False, f"Erro Físico Absoluto: Luminosidade impossível de {lum}%."

    return True, "Válido"

# ==================================================
# ROTINAS DE CONEXÃO SÉRIE
# ==================================================
def encontrar_todas_as_portas():
    portas_encontradas = []
    portas = list(serial.tools.list_ports.comports())
    for porta in portas:
        if "Arduino" in porta.description or "CH340" in porta.description or "USB" in porta.description:
            portas_encontradas.append(porta.device)
    return portas_encontradas

print("==================================================")
print("🌿 Gateway de Teste Local - Modo Varredura ")
print("==================================================")

lista_de_portas = encontrar_todas_as_portas()
if not lista_de_portas:
    print("❌ Nenhum dispositivo IoT encontrado nas portas USB.")
    exit(1)

conexoes_ativas = {}
for porta in lista_de_portas:
    try:
        conexoes_ativas[porta] = serial.Serial(porta, VELOCIDADE, timeout=0)
        print(f"🔌 Porta {porta} conectada.")
    except Exception as e:
        print(f"❌ Falha ao abrir a porta {porta}: {e}")

print("\n🚀 A escutar os sensores... (Pressione Ctrl+C para parar)")
print("--------------------------------------------------")

# ==================================================
# LOOP PRINCIPAL (Leitura, Análise e Disparo Web)
# ==================================================
try:
    while True:
        for porta, arduino in list(conexoes_ativas.items()):
            try:
                if arduino.in_waiting > 0:
                    linha = arduino.readline().decode('utf-8', errors='ignore').strip()
                    
                    # 🔍 DEBUG: Descomente a linha abaixo se quiser ver TUDO o que chega na porta USB
                    # print(f"Raw recebido: {linha}")
                    
                    # Usamos startswith em vez de list()[0] (é mais seguro)
                    if linha and linha.startswith("{"):
                        try:
                            payload = json.loads(linha)
                            id_horta = payload.get("horta_id", "Desconhecido")
                            
                            # 👈 MAPEAMENTO CORRIGIDO
                            dados_normalizados = {
                                'Temperatura (°C)': payload.get('temperatura', 0),
                                'Umidade do Ar (%)': payload.get('umidade_ar', 0), 
                                'Umidade do Solo (%)': payload.get('umidade_solo', 0),
                                'Luminosidade': payload.get('luz', 0)
                            }
                            
                            valores_str = f"Temp:{dados_normalizados['Temperatura (°C)']} | U.Ar:{dados_normalizados['Umidade do Ar (%)']} | U.Solo:{dados_normalizados['Umidade do Solo (%)']} | Lum:{dados_normalizados['Luminosidade']}"
                            
                            status_anomalia = False
                            causa_raiz = "Nenhuma"
                            
                            # Passo 1: Camada 1 (Filtro Físico)
                            passou_camada1, motivo = aplicar_camada1(dados_normalizados)
                            
                            if not passou_camada1:
                                status_anomalia = True
                                causa_raiz = f"Erro Físico: {motivo}"
                                print(f"\n🛑 [CAMADA 1 - BLOQUEADO] Horta {id_horta} | Motivo: {motivo}")
                            
                            elif modelo_if is not None:
                                # Passo 2 e 3: Camada 2 (Isolation Forest) e Camada 3 (SHAP)
                                colunas = ['Temperatura (°C)', 'Umidade do Ar (%)', 'Umidade do Solo (%)', 'Luminosidade']
                                df_leitura = pd.DataFrame([[dados_normalizados[c] for c in colunas]], columns=colunas)
                                
                                previsao = modelo_if.predict(df_leitura)
                                
                                if previsao[0] == -1: 
                                    shap_values = explainer_shap.shap_values(df_leitura)
                                    importancia = pd.Series(np.abs(shap_values[0]), index=colunas).sort_values(ascending=False)
                                    
                                    sensor_culpado = importancia.index[0]
                                    peso = importancia.iloc[0]
                                    
                                    status_anomalia = True
                                    causa_raiz = sensor_culpado
                                    
                                    print(f"\n⚠️ [CAMADA 2 - ANOMALIA IA] Horta {id_horta} | {valores_str}")
                                    print(f"   🔍 Causa Raiz: '{sensor_culpado}' (Peso: {peso:.2f})")
                                else:
                                    status_anomalia = False
                                    causa_raiz = "Nenhuma"
                                    print(f"✅ [NORMAL] Horta {id_horta} | {valores_str}")
                            
                            # 📡 INTEGRAÇÃO WEB
                            payload_web = {
                                "horta_id": id_horta,
                                "temperatura": dados_normalizados['Temperatura (°C)'],
                                "umidade_ar": dados_normalizados['Umidade do Ar (%)'],
                                "umidade_solo": dados_normalizados['Umidade do Solo (%)'],
                                "luz": dados_normalizados['Luminosidade'],
                                "status_anomalia": status_anomalia,
                                "causa_raiz": causa_raiz
                            }

                            try:
                                resposta = requests.post(API_URL, json=payload_web, timeout=2)
                                if resposta.status_code in [200, 201]:
                                    print(f"   📡 [WEB] Enviado (HTTP {resposta.status_code})")
                                else:
                                    print(f"   ⚠️ [WEB] Erro HTTP {resposta.status_code}")
                            except requests.exceptions.RequestException as req_err:
                                print(f"   🔌 [WEB] Sem conexão com a API.")

                        except json.JSONDecodeError:
                            # Removido o 'pass' assassino. Agora ele avisa se o JSON vier quebrado!
                            print(f"❌ [ERRO] JSON inválido recebido do Arduino: {linha}")
                            
            except serial.SerialException:
                print(f"\n❌ [Desconectado] Placa na porta {porta} removida.")
                del conexoes_ativas[porta]
                
        time.sleep(0.1)

except KeyboardInterrupt:
    print("\n🛑 Gateway de teste encerrado.")
    for arduino in conexoes_ativas.values():
        arduino.close()