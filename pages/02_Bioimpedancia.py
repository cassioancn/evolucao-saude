import streamlit as st
import pandas as pd
import plotly.graph_objects as go
from datetime import date
from PIL import Image
from database.connection import get_db
from database.models import Pesagem
from utils.auth import requer_login, get_usuario_logado
from utils.ocr_reader import extrair_dados_print_balanca
from components.sidebar import render_sidebar
from components.metrics_cards import card_metrica

st.set_page_config(page_title="Bioimpedância — Evolução Saúde", page_icon="⚖️", layout="wide", initial_sidebar_state="auto")
requer_login()
render_sidebar()

usuario = get_usuario_logado()

st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            ⚖️ Composição Corporal & Bioimpedância (OKOK)
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Acompanhe percentual de gordura, massa muscular, taxa de água e dados da sua balança inteligente.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

tab_print, tab_manual = st.tabs(["📸 Leitura por Print da Balança (OKOK)", "✍️ Lançamento Manual Completo"])

# ----------------- ABA 1: LEITURA POR PRINT -----------------
with tab_print:
    st.info("💡 **Dica:** Tire um print da tela de resultado do app OKOK no seu celular e envie abaixo. O sistema lerá os valores para você!")

    col_up1, col_up2 = st.columns([1.2, 1.8])

    with col_up1:
        uploaded_file = st.file_uploader(
            "Enviar print da tela do OKOK",
            type=["png", "jpg", "jpeg"],
            key="upload_print_okok"
        )
        if uploaded_file:
            st.image(uploaded_file, caption="Print enviado", use_container_width=True)

    with col_up2:
        if uploaded_file:
            with st.spinner("Processando leitura do print..."):
                dados_ocr = extrair_dados_print_balanca(uploaded_file)
            
            st.success(dados_ocr["mensagem"])

            with st.form("form_confirm_ocr"):
                st.markdown("#### Confirmar Dados Detectados")
                c_d1, c_d2 = st.columns(2)
                with c_d1:
                    data_bio_ocr = st.date_input("Data da Medição", value=date.today())
                    peso_ocr = st.number_input(
                        "Peso (kg)",
                        min_value=30.0, max_value=250.0,
                        value=float(dados_ocr["peso"]) if dados_ocr["peso"] else 68.0,
                        step=0.1
                    )
                    gordura_ocr = st.number_input(
                        "% Gordura Corporal",
                        min_value=0.0, max_value=70.0,
                        value=float(dados_ocr["percentual_gordura"]) if dados_ocr["percentual_gordura"] else 28.0,
                        step=0.1
                    )
                    musculo_ocr = st.number_input(
                        "Massa Muscular (kg)",
                        min_value=0.0, max_value=120.0,
                        value=float(dados_ocr["massa_muscular_kg"]) if dados_ocr["massa_muscular_kg"] else 42.0,
                        step=0.1
                    )
                with c_d2:
                    agua_ocr = st.number_input(
                        "% Água Corporal",
                        min_value=0.0, max_value=80.0,
                        value=float(dados_ocr["percentual_agua"]) if dados_ocr["percentual_agua"] else 50.0,
                        step=0.1
                    )
                    visceral_ocr = st.number_input(
                        "Gordura Visceral (nível)",
                        min_value=1, max_value=30,
                        value=int(dados_ocr["gordura_visceral"]) if dados_ocr["gordura_visceral"] else 4
                    )
                    tmb_ocr = st.number_input(
                        "TMB (kcal)",
                        min_value=500, max_value=3500,
                        value=int(dados_ocr["tmb"]) if dados_ocr["tmb"] else 1350
                    )
                    notas_ocr = st.text_input("Observações", value="Importado via Print OKOK")

                if st.form_submit_button("💾 Salvar Registro no Banco", type="primary", use_container_width=True):
                    with get_db() as db:
                        reg = Pesagem(
                            usuario_id=usuario["id"],
                            data_pesagem=data_bio_ocr,
                            peso=round(peso_ocr, 2),
                            percentual_gordura=round(gordura_ocr, 2),
                            massa_muscular_kg=round(musculo_ocr, 2),
                            percentual_agua=round(agua_ocr, 2),
                            gordura_visceral=int(visceral_ocr),
                            tmb=int(tmb_ocr),
                            origem="print_okok",
                            notas=notas_ocr
                        )
                        db.add(reg)
                    st.success("✅ Registro de bioimpedância salvo com sucesso!")
                    st.rerun()
        else:
            st.markdown(
                """
                <div style="border: 2px dashed #CBD5E1; border-radius: 12px; padding: 40px; text-align: center; color: #64748B;">
                    <div style="font-size: 32px; margin-bottom: 8px;">📲</div>
                    Envie a captura de tela do app OKOK ao lado para iniciar a leitura.
                </div>
                """,
                unsafe_allow_html=True
            )

# ----------------- ABA 2: LANÇAMENTO MANUAL -----------------
with tab_manual:
    with st.form("form_manual_bio", clear_on_submit=True):
        st.markdown("#### Novo Registro Manual de Bioimpedância")
        col_m1, col_m2, col_m3 = st.columns(3)
        with col_m1:
            data_m = st.date_input("Data da Medição", value=date.today(), key="data_manual_bio")
            peso_m = st.number_input("Peso (kg) *", min_value=30.0, max_value=250.0, value=68.0, step=0.1)
            gordura_m = st.number_input("% Gordura Corporal", min_value=0.0, max_value=70.0, value=28.0, step=0.1)
        with col_m2:
            musculo_m = st.number_input("Massa Muscular (kg)", min_value=0.0, max_value=120.0, value=42.0, step=0.1)
            agua_m = st.number_input("% Água Corporal", min_value=0.0, max_value=80.0, value=50.0, step=0.1)
            visceral_m = st.number_input("Gordura Visceral (nível)", min_value=1, max_value=30, value=4)
        with col_m3:
            tmb_m = st.number_input("TMB (kcal)", min_value=500, max_value=3500, value=1350)
            idade_metabolica_m = st.number_input("Idade Metabólica", min_value=10, max_value=90, value=25)
            notas_m = st.text_input("Observações", placeholder="Ex: Pesagem em jejum")

        if st.form_submit_button("Salvar Bioimpedância", type="primary", use_container_width=True):
            with get_db() as db:
                reg_manual = Pesagem(
                    usuario_id=usuario["id"],
                    data_pesagem=data_m,
                    peso=round(peso_m, 2),
                    percentual_gordura=round(gordura_m, 2),
                    massa_muscular_kg=round(musculo_m, 2),
                    percentual_agua=round(agua_m, 2),
                    gordura_visceral=int(visceral_m),
                    tmb=int(tmb_m),
                    idade_metabolica=int(idade_metabolica_m),
                    origem="manual",
                    notas=notas_m
                )
                db.add(reg_manual)
            st.success("✅ Registro de bioimpedância salvo!")
            st.rerun()

st.divider()

# ----------------- VISUALIZAÇÃO GRÁFICA DE BIOIMPEDÂNCIA -----------------
st.markdown("### 📊 Evolução da Composição Corporal")

with get_db() as db:
    historico = db.query(Pesagem).filter(
        Pesagem.usuario_id == usuario["id"],
        Pesagem.percentual_gordura.isnot(None)
    ).order_by(Pesagem.data_pesagem.asc()).all()

    dados_hist = [
        {
            "Data": p.data_pesagem,
            "Peso": p.peso,
            "Gordura": p.percentual_gordura,
            "Musculo": p.massa_muscular_kg,
            "Agua": p.percentual_agua,
            "Visceral": p.gordura_visceral
        }
        for p in historico
    ]

if dados_hist:
    df_bio = pd.DataFrame(dados_hist)
    
    # KPIs Rápidos da Última Bioimpedância
    ultimo = df_bio.iloc[-1]
    k1, k2, k3, k4 = st.columns(4)
    with k1:
        card_metrica("Gordura Corporal", f"{ultimo['Gordura']:.1f}%", "Última medição", "#F59E0B", "🔥")
    with k2:
        card_metrica("Massa Muscular", f"{ultimo['Musculo']:.1f} kg" if ultimo['Musculo'] else "—", "Massa Magra", "#10B981", "💪")
    with k3:
        card_metrica("Água Corporal", f"{ultimo['Agua']:.1f}%" if ultimo['Agua'] else "—", "Hidratação", "#06B6D4", "💧")
    with k4:
        card_metrica("Gordura Visceral", f"Nível {int(ultimo['Visceral'])}" if ultimo['Visceral'] else "—", "Saúde interna", "#6366F1", "🩺")

    # Gráfico de evolução
    fig_bio = go.Figure()
    fig_bio.add_trace(go.Scatter(
        x=df_bio["Data"], y=df_bio["Gordura"],
        mode="lines+markers", name="% Gordura",
        line=dict(color="#F59E0B", width=2.5)
    ))
    if df_bio["Musculo"].notna().any():
        fig_bio.add_trace(go.Scatter(
            x=df_bio["Data"], y=df_bio["Musculo"],
            mode="lines+markers", name="Músculo (kg)",
            line=dict(color="#10B981", width=2.5)
        ))
    if df_bio["Agua"].notna().any():
        fig_bio.add_trace(go.Scatter(
            x=df_bio["Data"], y=df_bio["Agua"],
            mode="lines+markers", name="% Água",
            line=dict(color="#06B6D4", width=2, dash="dot")
        ))

    fig_bio.update_layout(
        plot_bgcolor="#FFFFFF",
        paper_bgcolor="#FFFFFF",
        margin=dict(l=20, r=20, t=30, b=20),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9", title="Valores (% ou kg)"),
        hovermode="x unified",
        height=380
    )
    st.plotly_chart(fig_bio, use_container_width=True)

else:
    st.info("Cadastre sua primeira medição de bioimpedância acima para visualizar os gráficos de gordura e músculo.")

