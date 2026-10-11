import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from database.connection import get_db
from database.models import Usuario, ConfiguracaoMeta, Pesagem
from utils.auth import requer_login, get_usuario_logado
from utils.calculations import (
    calcular_imc, calcular_projecao_meta, processar_metricas_historico
)
from components.sidebar import render_sidebar
from components.metrics_cards import card_metrica, barra_progresso_meta

st.set_page_config(page_title="Dashboard & Metas — Evolução Saúde", page_icon="📊", layout="wide")
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

# ----------------- CARDS DE KPIS -----------------
imc_valor, imc_class, imc_cor = calcular_imc(metricas["peso_atual"], altura)

col1, col2, col3, col4, col5 = st.columns(5)
with col1:
    card_metrica("Peso Atual", f"{metricas['peso_atual']:.1f} kg", f"Meta: {meta_peso:.1f} kg", "#0D9488", "⚖️")
with col2:
    sinal = "-" if metricas["perdido_ate_agora"] > 0 else "+"
    cor_perda = "#10B981" if metricas["perdido_ate_agora"] >= 0 else "#EF4444"
    card_metrica("Total Eliminado", f"{metricas['perdido_ate_agora']:+.1f} kg", f"Início: {peso_inicial:.1f} kg", cor_perda, "🎯")
with col3:
    cor_7d = "#10B981" if metricas["variacao_7d"] <= 0 else "#EF4444"
    card_metrica("Últimos 7 dias", f"{metricas['variacao_7d']:+.1f} kg", "Ritmo semanal", cor_7d, "📅")
with col4:
    card_metrica("IMC Atual", f"{imc_valor}", f"{imc_class}", imc_cor, "🩺")
with col5:
    projecao = calcular_projecao_meta(metricas["peso_atual"], meta_peso, metricas["taxa_semanal"])
    if projecao["meta_atingida"]:
        card_metrica("Projeção", "Concluído!", "Meta alcançada 🏆", "#10B981", "🎉")
    else:
        card_metrica("Previsão da Meta", projecao["data_estimada"].strftime("%d/%m/%Y"), f"~{projecao['semanas']:.0f} semanas restantes", "#6366F1", "🚀")

# Barra de Progresso
barra_progresso_meta(metricas["progresso_pct"], metricas["peso_atual"], meta_peso)

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
