import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from database.connection import get_db
from database.models import MedidaCorporal
from utils.auth import requer_login, get_usuario_logado
from components.sidebar import render_sidebar
from components.metrics_cards import card_metrica

st.set_page_config(page_title="Medidas Corporais — Evolução Saúde", page_icon="📏", layout="wide", initial_sidebar_state="auto")
requer_login()
render_sidebar()

usuario = get_usuario_logado()

st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            📏 Medidas Corporais (Antropometria)
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Acompanhe a redução de medidas da cintura, quadril, abdômen e coxas mesmo quando o peso na balança oscila!
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

# ----------------- FORMULÁRIO DE NOVA MEDIÇÃO -----------------
with st.expander("➕ **Registrar Novas Medidas (cm)**", expanded=False):
    with st.form("form_medidas", clear_on_submit=True):
        col_d1, col_d2, col_d3 = st.columns(3)
        with col_d1:
            data_m = st.date_input("Data da Medição", value=date.today())
            cintura_m = st.number_input("Cintura (cm)", min_value=40.0, max_value=200.0, value=75.0, step=0.5)
            abdomen_m = st.number_input("Abdômen (cm)", min_value=40.0, max_value=200.0, value=85.0, step=0.5)
        with col_d2:
            quadril_m = st.number_input("Quadril (cm)", min_value=50.0, max_value=220.0, value=100.0, step=0.5)
            coxa_dir_m = st.number_input("Coxa Direita (cm)", min_value=20.0, max_value=120.0, value=58.0, step=0.5)
            coxa_esq_m = st.number_input("Coxa Esquerda (cm)", min_value=20.0, max_value=120.0, value=58.0, step=0.5)
        with col_d3:
            braco_dir_m = st.number_input("Braço Direito (cm)", min_value=15.0, max_value=80.0, value=28.0, step=0.5)
            braco_esq_m = st.number_input("Braço Esquerdo (cm)", min_value=15.0, max_value=80.0, value=28.0, step=0.5)
            busto_m = st.number_input("Busto (cm)", min_value=40.0, max_value=200.0, value=90.0, step=0.5)
        
        notas_m = st.text_input("Observações", placeholder="Ex: Medido pela manhã em jejum")

        if st.form_submit_button("Salvar Medidas", type="primary", use_container_width=True):
            with get_db() as db:
                nova_medida = MedidaCorporal(
                    usuario_id=usuario["id"],
                    data_registro=data_m,
                    cintura=cintura_m,
                    abdomen=abdomen_m,
                    quadril=quadril_m,
                    coxa_dir=coxa_dir_m,
                    coxa_esq=coxa_esq_m,
                    braco_dir=braco_dir_m,
                    braco_esq=braco_esq_m,
                    busto=busto_m,
                    notas=notas_m
                )
                db.add(nova_medida)
            st.success("✅ Medidas salvas com sucesso!")
            st.rerun()

# ----------------- HISTÓRICO E GRÁFICOS -----------------
with get_db() as db:
    registros = db.query(MedidaCorporal).filter(
        MedidaCorporal.usuario_id == usuario["id"]
    ).order_by(MedidaCorporal.data_registro.asc()).all()

    dados = [
        {
            "id": r.id,
            "Data": r.data_registro,
            "Cintura": r.cintura,
            "Abdômen": r.abdomen,
            "Quadril": r.quadril,
            "Coxa Dir": r.coxa_dir,
            "Braço Dir": r.braco_dir,
            "Busto": r.busto,
            "Observações": r.notas or ""
        }
        for r in registros
    ]

if dados:
    df_m = pd.DataFrame(dados)
    primeiro = df_m.iloc[0]
    ultimo = df_m.iloc[-1]

    # Cards comparativos de Centímetros eliminados
    diff_cintura = (ultimo["Cintura"] or 0) - (primeiro["Cintura"] or 0)
    diff_abdomen = (ultimo["Abdômen"] or 0) - (primeiro["Abdômen"] or 0)
    diff_quadril = (ultimo["Quadril"] or 0) - (primeiro["Quadril"] or 0)

    c1, c2, c3, c4 = st.columns(4)
    with c1:
        cor = "#10B981" if diff_cintura <= 0 else "#EF4444"
        card_metrica("Cintura Atual", f"{ultimo['Cintura']:.1f} cm", f"Variação: {diff_cintura:+.1f} cm", cor, "⏳")
    with c2:
        cor = "#10B981" if diff_abdomen <= 0 else "#EF4444"
        card_metrica("Abdômen Atual", f"{ultimo['Abdômen']:.1f} cm", f"Variação: {diff_abdomen:+.1f} cm", cor, "📉")
    with c3:
        cor = "#10B981" if diff_quadril <= 0 else "#EF4444"
        card_metrica("Quadril Atual", f"{ultimo['Quadril']:.1f} cm", f"Variação: {diff_quadril:+.1f} cm", cor, "✨")
    with c4:
        total_cm_perdidos = (diff_cintura + diff_abdomen + diff_quadril)
        cor_tot = "#10B981" if total_cm_perdidos <= 0 else "#EF4444"
        card_metrica("Total Reduzido", f"{total_cm_perdidos:+.1f} cm", "Soma das 3 regiões", cor_tot, "🏆")

    # Gráfico de evolução das medidas
    fig = go.Figure()
    fig.add_trace(go.Scatter(x=df_m["Data"], y=df_m["Cintura"], mode="lines+markers", name="Cintura (cm)", line=dict(color="#0D9488", width=2.5)))
    fig.add_trace(go.Scatter(x=df_m["Data"], y=df_m["Abdômen"], mode="lines+markers", name="Abdômen (cm)", line=dict(color="#F59E0B", width=2.5)))
    fig.add_trace(go.Scatter(x=df_m["Data"], y=df_m["Quadril"], mode="lines+markers", name="Quadril (cm)", line=dict(color="#6366F1", width=2.5)))

    fig.update_layout(
        title="Curva de Redução de Medidas (cm)",
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=40, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Centímetros (cm)"),
        hovermode="x unified",
        height=380
    )
    st.plotly_chart(fig, use_container_width=True)

    # Tabela
    st.markdown("### 📋 Tabela de Medições")
    st.dataframe(df_m.drop(columns=["id"]), use_container_width=True, hide_index=True)

else:
    st.info("Nenhuma medição de circunferência registrada ainda. Clique em 'Registrar Novas Medidas' acima.")

