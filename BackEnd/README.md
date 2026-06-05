🌿 Horta Inteligente IoT - Backend API
Este projeto consiste em uma API REST robusta, segura e de alto desempenho, desenvolvida para atuar como o cérebro de um ecossistema de Internet das Coisas (IoT) voltado para o monitoramento automatizado de hortas residenciais.

O backend atua como a ponte central do ecossistema: ele recebe e valida os dados ambientais enviados por microcontroladores (como ESP32 ou Arduino), armazena as informações de forma estruturada e serve esses dados em tempo real para um painel visual (Dashboard).

🛠️ Tecnologias Utilizadas
Linguagem: Python

Framework Web: FastAPI (Arquitetura assíncrona e alto desempenho)

Persistência de Dados (ORM): SQLModel (Fusão eficiente entre SQLAlchemy e Pydantic)

Banco de Dados: SQLite (Armazenamento leve em arquivo único, ideal para sistemas embarcados)

Segurança: Criptografia Bcrypt (Passlib) e Autenticação via Tokens JWT (PyJWT)

🚀 Funcionalidades Principais
🔒 1. Autenticação e Controle de Acesso
Cadastro Seguro: Registro de novos usuários com mascaramento de senhas via algoritmos de hash de via única (Bcrypt).

Autenticação JWT (OAuth2): Sistema de login que gera "crachás digitais" temporários (Tokens), eliminando o armazenamento de sessões pesadas na memória do servidor.

🪴 2. Gerenciamento Relacional de Hortas (CRUD)
Múltiplos Ambientes: Permite que um usuário gerencie e cadastre diferentes hortas ou canteiros (ex: "Horta da Varanda", "Horta da Cozinha").

Consistência de Chaves: Vínculo relacional estrito onde cada leitura pertence a uma horta e cada horta pertence obrigatoriamente a um usuário.

📊 3. Ingestão de Telemetria e Otimização IoT
Validação Automatizada: Filtro rigoroso contra dados corrompidos enviados pelos sensores físicos antes de tocarem o banco de dados.

Tratamento Temporal Inteligente: Padronização e arredondamento automático dos horários das leituras em janelas absolutas de 30 minutos (Fuso BRT), garantindo gráficos lineares limpos e sem ruídos de rede.

Histórico Otimizado: Consultas com paginação e limite de segurança (limit), protegendo o hardware do servidor contra travamentos por estouro de memória RAM.

🏗️ Destaques de Engenharia e Arquitetura
Foco em Hardware Limitado: O projeto foi arquitetado sob medida para rodar de forma suave em dispositivos com recursos computacionais enxutos, como uma Android TV Box, utilizando índices de busca temporal (index=True) e configurações de concorrência segura (check_same_thread: False).

Código Limpo e Escalável: Divisão clara de responsabilidades seguindo padrões de mercado (models/, routers/, core/), facilitando a expansão futura para o controle de atuadores físicos (como o acionamento automático de bombas d'água via relés).

📋 Endpoints Disponíveis (Visão Geral)
POST /auth/cadastro — Registro de novas contas.

POST /auth/token — Login de usuários e emissão de tokens de segurança.

POST /horta/ — Cadastro de novos ambientes de plantio.

GET /horta/ — Listagem de hortas associadas.

POST /telemetria/ — Ponto de recepção dos dados do microcontrolador (Temperatura, Umidade e Luz).

GET /telemetria/{horta_id} — Recuperação do histórico de dados mastigados para exibição gráfica.
