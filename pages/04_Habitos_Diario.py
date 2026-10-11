import streamlit as st
import pandas as pd
from datetime import date
from database.connection import get_db
from database.models import HabitoDiario, ConfiguracaoMeta
from utils.auth import requer_login, get_usuario_logado
from components.sidebar import render_sidebar
from components.metrics_cards import card_metrica

st.set_page_config(page_title="Diário de Hábitos — Evolução Saúde", page_icon="💧", layout="wide")
requer_login()
render_sidebar()

usuario = get_usuario_logado()

st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            💧 Diário & Hábitos Saudáveis
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Consistência diária: controle de hidratação, sono, treinos e impacto do ciclo biológico.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

hoje = date.today()

# Carrega os dados de hoje
with get_db() as db:
    habito_hoje = db.query(HabitoDiario).filter(
        HabitoDiario.usuario_id == usuario["id"],
        HabitoDiario.data == hoje
    ).first()
    
    meta_cfg = db.query(ConfiguracaoMeta).filter(
        ConfiguracaoMeta.usuario_id == usuario["id"]
    ).first()
    meta_agua = meta_cfg.meta_agua_ml if meta_cfg else 2500

    agua_atual = habito_hoje.agua_ml if habito_hoje else 0
    treinou_atual = habito_hoje.treinou if habito_hoje else False
    sono_atual = habito_hoje.sono_horas if habito_hoje else 7.5
    ciclo_atual = habito_hoje.ciclo_menstrual if habito_hoje else False
    humor_atual = habito_hoje.humor if habito_hoje else "Bem"

# ----------------- REGISTRO RÁPIDO DO DIA -----------------
col_esq, col_dir = st.columns([1.5, 1.2])

with col_esq:
    with st.container(border=True):
        st.markdown("### 🚰 Hidratação de Hoje")
        
        pct_agua = min(100.0, (agua_atual / meta_agua) * 100) if meta_agua > 0 else 0
        st.progress(pct_agua / 100.0)
        
        col_w1, col_w2 = st.columns([2, 1])
        with col_w1:
            st.markdown(f"Consumido: **{agua_atual} ml** / Meta: **{meta_agua} ml** ({pct_agua:.0f}%)")
        with col_w2:
            st.markdown(f"Faltam: **{max(0, meta_agua - agua_atual)} ml**")

        st.markdown("##### Adicionar Água Rápido:")
        b1, b2, b3, b4 = st.columns(4)
        adicionou = 0
        with b1:
            if st.button("🥤 +250 ml", use_container_width=True):
                adicionou = 250
        with b2:
            if st.button("🥛 +500 ml", use_container_width=True):
                adicionou = 500
        with b3:
            if st.button("🍶 +1.000 ml", use_container_width=True):
                adicionou = 1000
        with b4:
            if st.button("🔄 Zerar", use_container_width=True):
                adicionou = -agua_atual

        if adicionou != 0:
            with get_db() as db:
                h = db.query(HabitoDiario).filter(HabitoDiario.usuario_id == usuario["id"], HabitoDiario.data == hoje).first()
                if not h:
                    h = HabitoDiario(usuario_id=usuario["id"], data=hoje, agua_ml=max(0, adicionou))
                    db.add(h)
                else:
                    h.agua_ml = max(0, h.agua_ml + adicionou)
            st.rerun()

with col_dir:
    with st.container(border=True):
        st.markdown("### 📝 Check-in Completo do Dia")
        with st.form("form_checkin_habitos"):
            data_sel = st.date_input("Data do Registro", value=hoje)
            treinou = st.checkbox("🏋️ Treinei hoje!", value=treinou_atual)
            tipo_treino = st.selectbox(
                "Tipo de Atividade",
                ["Musculação", "Cardio / Corrida", "Caminhada", "Pilates / Funcional", "Descanso Ativo", "Outro"]
            )
            horas_sono = st.slider("Horas de Sono", min_value=3.0, max_value=12.0, value=float(sono_atual), step=0.5)
            
            ciclo = st.checkbox("🌸 Período Menstrual / TPM", value=ciclo_atual)
            if ciclo:
                st.caption("ℹ️ *Lembrete:* Nessa fase é natural reter até 1 a 2 kg de água temporariamente. Não se preocupe com o número na balança!")
            
            humor = st.select_slider(
                "Como está sua energia hoje?",
                options=["Muito Cansada", "Cansada", "Neutra", "Disposta", "Excelente Energia"],
                value="Disposta"
            )

            if st.form_submit_button("Salvar Check-in", type="primary", use_container_width=True):
                with get_db() as db:
                    reg_h = db.query(HabitoDiario).filter(HabitoDiario.usuario_id == usuario["id"], HabitoDiario.data == data_sel).first()
                    if not reg_h:
                        reg_h = HabitoDiario(
                            usuario_id=usuario["id"],
                            data=data_sel,
                            treinou=treinou,
                            tipo_treino=tipo_treino,
                            sono_horas=horas_sono,
                            ciclo_menstrual=ciclo,
                            humor=humor
                        )
                        db.add(reg_h)
                    else:
                        reg_h.treinou = treinou
                        reg_h.tipo_treino = tipo_treino
                        reg_h.sono_horas = horas_sono
                        reg_h.ciclo_menstrual = ciclo
                        reg_h.humor = humor
                st.success("✅ Check-in salvo!")
                st.rerun()

st.divider()

# ----------------- HISTÓRICO DE CONSISTÊNCIA -----------------
st.markdown("### 📅 Consistência dos Últimos 14 Dias")

with get_db() as db:
    historico = db.query(HabitoDiario).filter(
        HabitoDiario.usuario_id == usuario["id"]
    ).order_by(HabitoDiario.data.desc()).limit(14).all()

    dados_hab = [
        {
            "Data": h.data.strftime("%d/%m/%Y"),
            "Água (ml)": f"{h.agua_ml} ml",
            "Treinou": "✅ Sim" if h.treinou else "❌ Não",
            "Atividade": h.tipo_treino or "—",
            "Sono": f"{h.sono_horas}h",
            "TPM/Ciclo": "🌸 Sim" if h.ciclo_menstrual else "—",
            "Energia": h.humor or "—"
        }
        for h in historico
    ]

if dados_hab:
    st.dataframe(pd.DataFrame(dados_hab), use_container_width=True, hide_index=True)
else:
    st.info("Nenhum histórico de hábitos registrado ainda.")
