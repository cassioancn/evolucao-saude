import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from database.connection import get_db
from database.models import Usuario, ConfiguracaoMeta, Pesagem
from utils.auth import requer_login, get_usuario_logado
from utils.calculations import (
    calcular_imc, detalhes_imc, calcular_tmb_mifflin, calcular_gasto_calorico_completo,
    calcular_projecao_meta, processar_metricas_historico
)
from components.sidebar import render_sidebar
from components.metrics_cards import card_metrica, barra_progresso_meta

st.set_page_config(
    page_title="Dashboard & Metas — Evolução Saúde",
    page_icon="📊",
    layout="wide",
    initial_sidebar_state="auto"
)
requer_login()
render_sidebar()

usuario = get_usuario_logado()

# 1. Carrega as metas do usuário
with get_db() as db:
    meta_obj = db.query(ConfiguracaoMeta).filter(ConfiguracaoMeta.usuario_id == usuario["id"]).first()
    if not meta_obj:
        meta_obj = ConfiguracaoMeta(
            usuario_id=usuario["id"],
            altura_cm=165.0,
            peso_inicial=70.0,
            meta_peso=60.0,
            data_inicio=date.today()
        )
        db.add(meta_obj)
        db.flush()
    
    altura = meta_obj.altura_cm
    peso_inicial = meta_obj.peso_inicial
    meta_peso = meta_obj.meta_peso
    idade = getattr(meta_obj, "idade", 30) or 30
    sexo = getattr(meta_obj, "sexo", "Feminino") or ("Feminino" if "bruna" in usuario.get("login", "").lower() else "Masculino")
    nivel_atividade = getattr(meta_obj, "nivel_atividade", "Moderadamente Ativo (3 a 5 dias/sem)") or "Moderadamente Ativo (3 a 5 dias/sem)"

    # 2. Carrega histórico de pesagens
    pesagens = db.query(Pesagem).filter(
        Pesagem.usuario_id == usuario["id"]
    ).order_by(Pesagem.data_pesagem.asc()).all()
    
    dados_pesagens = [
        {
            "id": p.id,
            "data_pesagem": p.data_pesagem,
            "peso": p.peso,
            "gordura": p.percentual_gordura,
            "musculo": p.massa_muscular_kg,
            "origem": p.origem,
            "notas": p.notas or ""
        }
        for p in pesagens
    ]

df_pesagens = pd.DataFrame(dados_pesagens)
metricas = processar_metricas_historico(df_pesagens, peso_inicial, meta_peso)

# Cabeçalho da Página
st.markdown(
    f"""
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            📊 Dashboard & Evolução
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Acompanhe a sua jornada, consistência e projeção de metas.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- REGISTRO RÁPIDO (QUICK LOG) -----------------
with st.expander("⚡ **Registrar Pesagem Rápida de Hoje**", expanded=not metricas["tem_dados"]):
    with st.form("form_quick_log", clear_on_submit=True):
        col_q1, col_q2, col_q3, col_q4 = st.columns([1.5, 1.5, 2, 1.2])
        with col_q1:
            data_rapida = st.date_input("Data", value=date.today(), format="DD/MM/YYYY")
        with col_q2:
            peso_rapido = st.number_input("Peso (kg)", min_value=30.0, max_value=250.0, value=float(metricas["peso_atual"]), step=0.1)
        with col_q3:
            notas_rapidas = st.text_input("Nota / Sentimento (opcional)", placeholder="Ex: Me sentindo disposta!")
        with col_q4:
            st.write("")
            st.write("")
            salvar_rapido = st.form_submit_button("Salvar Pesagem", type="primary", use_container_width=True)

        if salvar_rapido:
            with get_db() as db:
                nova_pesagem = Pesagem(
                    usuario_id=usuario["id"],
                    data_pesagem=data_rapida,
                    peso=round(peso_rapido, 2),
                    origem="manual",
                    notas=notas_rapidas
                )
                db.add(nova_pesagem)
            st.success("✅ Pesagem salva no Neon com sucesso!")
            st.rerun()

# ----------------- PARÂMETROS BIOMÉTRICOS & METABOLISMO (IMC & TMB) -----------------
# O peso de cálculo é a última pesagem cadastrada no histórico (ou o peso inicial se ainda não houver pesagens)
if not df_pesagens.empty:
    ult_row = df_pesagens.sort_values(by="data_pesagem").iloc[-1]
    peso_calc = float(ult_row["peso"])
    data_ult_str = ult_row["data_pesagem"].strftime("%d/%m/%Y")
    origem_peso_txt = f"última pesagem em {data_ult_str}"
else:
    peso_calc = float(peso_inicial)
    origem_peso_txt = "peso inicial cadastrado"

# Cálculos 100% automáticos baseados nos dados salvos do perfil do usuário e última pesagem
imc_info = detalhes_imc(peso_calc, altura)
gasto_info = calcular_gasto_calorico_completo(
    sexo,
    peso_calc,
    altura,
    idade,
    nivel_atividade
)

# ----------------- CARDS DE KPIS: LINHA 1 (PESO & METAS) -----------------
st.markdown("##### 🎯 Progresso & Metas")
col1, col2, col3, col4 = st.columns(4)
with col1:
    card_metrica("Peso Atual", f"{peso_calc:.1f} kg", f"Meta: {meta_peso:.1f} kg", "#0D9488", "⚖️")
with col2:
    perdido = metricas.get("perdido_ate_agora", 0.0)
    cor_perda = "#10B981" if perdido >= 0 else "#EF4444"
    card_metrica("Total Eliminado", f"{perdido:+.1f} kg", f"Início: {peso_inicial:.1f} kg", cor_perda, "🎯")
with col3:
    v_7d = metricas.get("variacao_7d", 0.0)
    cor_7d = "#10B981" if v_7d <= 0 else "#EF4444"
    card_metrica("Últimos 7 dias", f"{v_7d:+.1f} kg", "Ritmo semanal", cor_7d, "📅")
with col4:
    projecao = calcular_projecao_meta(peso_calc, meta_peso, metricas.get("taxa_semanal", 0.4))
    if projecao["meta_atingida"]:
        card_metrica("Projeção", "Concluído!", "Meta alcançada 🏆", "#10B981", "🎉")
    else:
        card_metrica("Previsão Meta", projecao["data_estimada"].strftime("%d/%m/%Y"), f"~{projecao['semanas']:.0f} sem. restantes", "#6366F1", "🚀")

# ----------------- CARDS DE KPIS: LINHA 2 (IMC & METABOLISMO BASAL) -----------------
st.markdown("##### 🧬 Biometria, IMC & Taxa Metabólica Basal (TMB)")
kpi_b1, kpi_b2, kpi_b3, kpi_b4 = st.columns(4)
with kpi_b1:
    card_metrica("IMC Atual", f"{imc_info['imc']}", f"{imc_info['classificacao']}", imc_info["cor"], "🩺")
with kpi_b2:
    card_metrica("Taxa Metabólica Basal", f"{gasto_info['tmb']} kcal", "Gasto em repouso vital", "#F59E0B", "🔥")
with kpi_b3:
    card_metrica("Gasto Diário (TDEE)", f"{gasto_info['tdee']} kcal", "Metabolismo + Atividades", "#3B82F6", "⚡")
with kpi_b4:
    card_metrica("Meta Calórica Diária", f"{gasto_info['deficit_sugerido']} kcal", "Déficit seguro para emagrecer", "#10B981", "🥗")

# Barra de Progresso
barra_progresso_meta(metricas.get("progresso_pct", 0.0), peso_calc, meta_peso)

# ----------------- PAINEL COMPLETO: CÁLCULOS DETALHADOS DE IMC & TMB -----------------
with st.container(border=True):
    st.markdown("### 🧮 Detalhamento dos Cálculos: IMC e Taxa de Metabolismo Basal")
    
    col_imc_box, col_tmb_box = st.columns(2)
    
    with col_imc_box:
        st.markdown("#### 🩺 Análise do seu IMC (Índice de Massa Corporal)")
        st.markdown(f"""
        - **Dados utilizados:** Peso atual de **{peso_calc:.1f} kg** ({origem_peso_txt}) e Altura de **{altura:.0f} cm** ({altura/100:.2f} m).
        - **Fórmula:** `Peso (kg) / [Altura (m)]²`
        - **Seu IMC Atual:** `{imc_info['imc']}` — <span style="color:{imc_info['cor']}; font-weight:700;">{imc_info['classificacao']}</span>
        - **Faixa de Peso Saudável (OMS):** entre **{imc_info['peso_min_ideal']} kg** e **{imc_info['peso_max_ideal']} kg** para sua altura.
        """, unsafe_allow_html=True)
        
        if imc_info["classificacao"] == "Peso saudável":
            st.success("🎉 Excelente! O seu peso atual está dentro da faixa saudável recomendada.")
        elif peso_calc > imc_info["peso_max_ideal"]:
            st.info(f"💡 Faltam **{imc_info['diferenca_saudavel']:.1f} kg** para alcançar a faixa de peso saudável ({imc_info['peso_max_ideal']} kg).")
        else:
            st.info(f"💡 Faltam **{imc_info['diferenca_saudavel']:.1f} kg** para alcançar o limite inferior saudável ({imc_info['peso_min_ideal']} kg).")
            
        st.caption("Classificação OMS: Abaixo do peso (< 18.5) • Saudável (18.5 – 24.9) • Sobrepeso (25.0 – 29.9) • Obesidade (≥ 30.0)")

    with col_tmb_box:
        st.markdown("#### 🔥 Taxa Metabólica Basal (Fórmula Mifflin-St Jeor)")
        st.markdown(f"""
        - **Dados ativos do seu Perfil:** Idade: **{idade} anos** • Sexo: **{sexo}** • Atividade: **{nivel_atividade.split('(')[0].strip()}**
        - **Peso Utilizado:** **{peso_calc:.1f} kg** ({origem_peso_txt})
        - **🔥 Taxa Metabólica Basal (TMB):** `{gasto_info['tmb']} kcal/dia`  
          *(Energia que seu corpo consome em repouso absoluto apenas para manter batimentos cardíacos, respiração e cérebro).*
        - **⚡ Gasto Total Diário (TDEE):** `{gasto_info['tdee']} kcal/dia`  
          *(Gasto estimado somando o metabolismo basal + rotina de exercícios).*
        - **🥗 Meta Calórica Sugerida:** `{gasto_info['deficit_sugerido']} kcal/dia`  
          *(Déficit seguro de ~400 kcal/dia para queimar gordura de forma contínua).*
        """)

        with st.expander("✏️ **Atualizar dados biométricos (idade, sexo, atividade) no perfil**"):
            with st.form("form_quick_biometria"):
                cb_i1, cb_i2 = st.columns(2)
                with cb_i1:
                    novo_idade = st.number_input("Idade (anos)", min_value=14, max_value=99, value=int(idade))
                    novo_sexo = st.selectbox("Sexo Biológico", ["Feminino", "Masculino"], index=0 if sexo == "Feminino" else 1)
                with cb_i2:
                    opcoes_ativ_dash = [
                        "Sedentário (pouco ou nenhum exercício)",
                        "Levemente Ativo (exercício 1 a 3 dias/semana)",
                        "Moderadamente Ativo (exercício 3 a 5 dias/semana)",
                        "Muito Ativo (exercício 6 a 7 dias/semana)"
                    ]
                    idx_ativ_dash = 2
                    for i, op in enumerate(opcoes_ativ_dash):
                        if op.split()[0].lower() in nivel_atividade.lower():
                            idx_ativ_dash = i
                            break
                    novo_ativ = st.selectbox("Atividade Semanal", opcoes_ativ_dash, index=idx_ativ_dash)
                
                if st.form_submit_button("💾 Salvar Alterações no Meu Perfil", type="primary", use_container_width=True):
                    with get_db() as db:
                        m = db.query(ConfiguracaoMeta).filter(ConfiguracaoMeta.usuario_id == usuario["id"]).first()
                        if m:
                            m.idade = novo_idade
                            m.sexo = novo_sexo
                            m.nivel_atividade = novo_ativ
                    st.success("✅ Perfil biométrico salvo com sucesso no banco Neon!")
                    st.rerun()




# ----------------- GRÁFICOS DE EVOLUÇÃO -----------------
st.markdown("### 📈 Histórico e Curva de Tendência")

if not df_pesagens.empty:
    df_chart = df_pesagens.copy()
    df_chart["data_str"] = pd.to_datetime(df_chart["data_pesagem"])
    df_chart = df_chart.sort_values(by="data_str")
    
    # Média móvel 7 dias (suavização)
    df_chart["media_movel"] = df_chart["peso"].rolling(window=3, min_periods=1).mean()

    fig = go.Figure()

    # Linha da Meta
    fig.add_trace(go.Scatter(
        x=[df_chart["data_str"].min(), df_chart["data_str"].max()],
        y=[meta_peso, meta_peso],
        mode="lines",
        name=f"Meta ({meta_peso} kg)",
        line=dict(color="#10B981", width=2, dash="dash")
    ))

    # Linha de Média Móvel (Tendência suave)
    fig.add_trace(go.Scatter(
        x=df_chart["data_str"],
        y=df_chart["media_movel"],
        mode="lines",
        name="Tendência Suavizada",
        line=dict(color="#F59E0B", width=2, dash="dot")
    ))

    # Linha do Peso Real
    fig.add_trace(go.Scatter(
        x=df_chart["data_str"],
        y=df_chart["peso"],
        mode="lines+markers",
        name="Peso Registrado",
        line=dict(color="#0D9488", width=3),
        marker=dict(size=8, color="#0F766E", symbol="circle"),
        hovertemplate="<b>Data:</b> %{x|%d/%m/%Y}<br><b>Peso:</b> %{y:.1f} kg<extra></extra>"
    ))

    fig.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=30, b=20),
        legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9", tickformat="%d/%m"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Peso (kg)"),
        hovermode="x unified",
        height=400
    )

    st.plotly_chart(fig, use_container_width=True)

    # ----------------- HISTÓRICO EM TABELA COM OPÇÃO DE EXCLUIR -----------------
    with st.expander("📋 Ver Tabela de Registros Anteriores"):
        df_exibir = df_chart.sort_values(by="data_pesagem", ascending=False).copy()
        df_exibir["Data"] = df_exibir["data_pesagem"].apply(lambda d: d.strftime("%d/%m/%Y"))
        
        cols_table = ["id", "Data", "peso", "gordura", "musculo", "origem", "notas"]
        st.dataframe(
            df_exibir[cols_table].rename(columns={
                "id": "ID", "peso": "Peso (kg)", "gordura": "% Gordura", 
                "musculo": "Músculo (kg)", "origem": "Origem", "notas": "Observações"
            }),
            use_container_width=True,
            hide_index=True
        )

        col_del1, col_del2 = st.columns([3, 1])
        with col_del1:
            id_para_excluir = st.selectbox(
                "Deseja excluir algum registro incorreto?",
                options=[None] + list(df_exibir["id"].tolist()),
                format_func=lambda x: "Selecione..." if x is None else f"ID {x} — {df_exibir[df_exibir['id'] == x]['Data'].values[0]} ({df_exibir[df_exibir['id'] == x]['peso'].values[0]} kg)"
            )
        with col_del2:
            st.write("")
            st.write("")
            if id_para_excluir and st.button("🗑️ Excluir", type="secondary"):
                with get_db() as db:
                    reg = db.query(Pesagem).filter(Pesagem.id == id_para_excluir).first()
                    if reg:
                        db.delete(reg)
                st.success("Registro excluído!")
                st.rerun()

else:
    st.info("Nenhuma pesagem cadastrada ainda. Utilize o formulário acima para registrar sua primeira pesagem!")

