# 🌿 Evolução Saúde — Sistema de Acompanhamento de Peso & Bem-estar

Aplicativo web completo desenvolvido em **Streamlit** com persistência em nuvem **PostgreSQL no Neon**, planejado para registrar e acompanhar com clareza a evolução de perda de peso, composição corporal e hábitos saudáveis.

---

## 🚀 Funcionalidades Principais

1. **📊 Dashboard & Metas:**
   - Registro de pesagem rápido (*Quick-Log*) em menos de 5 segundos.
   - KPIs automáticos: Peso Atual, Total Eliminado, Variação semanal (7d), IMC e Classificação.
   - Gráfico interativo com Linha de Tendência suavizada (média móvel de 7 dias) e linha de meta.
   - **Projeção Estimada de Data:** Cálculo preditivo do dia em que a meta será atingida com base no ritmo recente.

2. **⚖️ Composição Corporal & Bioimpedância (OKOK):**
   - **Leitor Inteligente de Captura de Tela (OCR):** Envie o print do app OKOK da balança e o sistema lê automaticamente peso, % de gordura, massa muscular e água.
   - Lançamento manual detalhado (% Gordura, Músculo em kg, % Água, Gordura Visceral, TMB e Idade Metabólica).
   - Gráfico de acompanhamento da evolução da composição corporal.

3. **📏 Medidas Corporais (Antropometria):**
   - Registro de circunferências: Cintura, Abdômen, Quadril, Coxas, Braços e Busto.
   - Indicador de **Total de Centímetros Reduzidos** (perfeito para manter a motivação mesmo quando o peso na balança oscila por retenção hídrica).

4. **💧 Diário & Hábitos Saudáveis:**
   - Tracker interativo de hidratação com botões rápidos (+250 ml, +500 ml, +1000 ml) e barra de progresso.
   - Check-in diário de treinos (Musculação, Cardio, Pilates, etc.) e horas de sono.
   - Marcador de ciclo menstrual e TPM com lembrete empático sobre retenção natural de líquidos.

5. **📸 Galeria de Evolução (Antes & Depois):**
   - Comparador visual de fotos lado a lado selecionando data de início vs data recente.
   - Armazenamento com data e peso associados.

6. **⚙️ Metas & Biometria:**
   - Ajuste de peso alvo, peso inicial, altura e meta diária de água.
   - Calculadora de Taxa Metabólica Basal (TMB - Fórmula Mifflin-St Jeor) e sugestão de déficit calórico.
   - Gerenciamento de credenciais.

---

## 🛠️ Tecnologias Utilizadas

- **Frontend & App:** [Streamlit](https://streamlit.io/)
- **Banco de Dados:** [Neon](https://neon.tech/) (PostgreSQL Serverless)
- **ORM & Conexão:** SQLAlchemy 2.0 com `psycopg2-binary`
- **Gráficos & Visualização:** Plotly Express & Graph Objects
- **Processamento de Imagens & OCR:** Pillow & Pytesseract

---

## 🏃 Como Rodar Localmente

1. Clone o repositório:
```bash
git clone https://github.com/cassioancn/evolucao-saude.git
cd evolucao-saude
```

2. Instale as dependências:
```bash
pip install -r requirements.txt
```

3. Configure os segredos em `.streamlit/secrets.toml`:
```toml
[database]
url = "postgresql://usuario:senha@ep-xyz.us-east-2.aws.neon.tech/neondb?sslmode=require"
```

4. Execute o Streamlit:
```bash
streamlit run app.py
```

---

## 👥 Usuários Padrão Inicializados
- **Bruna:** login `bruna` / senha inicial `bruna123`
- **Cássio:** login `cassio` / senha inicial `admin123`
