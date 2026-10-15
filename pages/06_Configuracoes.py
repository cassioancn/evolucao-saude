import streamlit as st
from datetime import date
from database.connection import get_db
from database.models import Usuario, ConfiguracaoMeta, hash_senha
from utils.auth import requer_login, get_usuario_logado
from utils.calculations import calcular_tmb_mifflin
from components.sidebar import render_sidebar

st.set_page_config(page_title="Configurações & Metas — Evolução Saúde", page_icon="⚙️", layout="wide", initial_sidebar_state="auto")
requer_login()
render_sidebar()

usuario = get_usuario_logado()

st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            ⚙️ Configurações & Metas Pessoais
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Ajuste sua meta de peso, dados biométricos e segurança de acesso.
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

with get_db() as db:
    meta = db.query(ConfiguracaoMeta).filter(
        ConfiguracaoMeta.usuario_id == usuario["id"]
    ).first()

    if not meta:
        meta = ConfiguracaoMeta(
            usuario_id=usuario["id"],
            altura_cm=165.0,
            peso_inicial=70.0,
            meta_peso=60.0,
            data_inicio=date.today(),
            meta_agua_ml=2500
        )
        db.add(meta)
        db.flush()

    altura_atual = meta.altura_cm
    peso_ini_atual = meta.peso_inicial
    meta_peso_atual = meta.meta_peso
    data_ini_atual = meta.data_inicio
    meta_agua_atual = meta.meta_agua_ml

tab_metas, tab_tmb, tab_senha = st.tabs(["🎯 Ajustar Metas & Biometria", "🔥 Calculadora de Gasto Calórico (TMB)", "🔒 Trocar Senha"])

# ----------------- ABA 1: METAS & BIOMETRIA -----------------
with tab_metas:
    with st.form("form_config_metas"):
        col1, col2 = st.columns(2)
        with col1:
            nova_altura = st.number_input("Sua Altura (cm)", min_value=120.0, max_value=220.0, value=float(altura_atual), step=0.5)
            novo_peso_ini = st.number_input("Peso de Início (kg)", min_value=30.0, max_value=250.0, value=float(peso_ini_atual), step=0.1)
            data_inicio = st.date_input("Data de Início da Jornada", value=data_ini_atual)

        with col2:
            nova_meta = st.number_input("Meta de Peso Alvo (kg)", min_value=30.0, max_value=200.0, value=float(meta_peso_atual), step=0.1)
            meta_agua = st.number_input("Meta Diária de Água (ml)", min_value=1000, max_value=6000, value=int(meta_agua_atual), step=250)

        if st.form_submit_button("💾 Salvar Alterações nas Metas", type="primary", use_container_width=True):
            with get_db() as db:
                m = db.query(ConfiguracaoMeta).filter(ConfiguracaoMeta.usuario_id == usuario["id"]).first()
                if m:
                    m.altura_cm = nova_altura
                    m.peso_inicial = novo_peso_ini
                    m.meta_peso = nova_meta
                    m.data_inicio = data_inicio
                    m.meta_agua_ml = meta_agua
            st.success("✅ Metas atualizadas com sucesso no Neon!")
            st.rerun()

# ----------------- ABA 2: CALCULADORA TMB -----------------
with tab_tmb:
    st.markdown("#### Estimativa de Queima Calórica Diária (Fórmula Mifflin-St Jeor)")
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        idade = st.number_input("Idade (anos)", min_value=15, max_value=90, value=30)
        sexo = st.selectbox("Sexo Biológico", ["Feminino", "Masculino"])
        nivel_atividade = st.selectbox(
            "Nível de Atividade Física Semanal",
            [
                "Sedentário (pouco ou nenhum exercício)",
                "Levemente Ativo (exercício 1 a 3 dias/semana)",
                "Moderadamente Ativo (exercício 3 a 5 dias/semana)",
                "Muito Ativo (exercício 6 a 7 dias/semana)"
            ],
            index=1
        )

    fatores = {
        "Sedentário (pouco ou nenhum exercício)": 1.2,
        "Levemente Ativo (exercício 1 a 3 dias/semana)": 1.375,
        "Moderadamente Ativo (exercício 3 a 5 dias/semana)": 1.55,
        "Muito Ativo (exercício 6 a 7 dias/semana)": 1.725
    }

    tmb = calcular_tmb_mifflin(sexo, peso_ini_atual, altura_atual, idade)
    gasto_total = int(round(tmb * fatores[nivel_atividade]))
    meta_emagrecimento = max(1200, gasto_total - 400) # Déficit seguro de 400 kcal

    with col_t2:
        with st.container(border=True):
            st.markdown(f"**🔥 Taxa Metabólica Basal (TMB):** `{tmb} kcal/dia`")
            st.caption("Energia gasta pelo corpo em repouso absoluto apenas para sobreviver.")
            
            st.markdown(f"**⚡ Gasto Calórico Total Diário (TDEE):** `{gasto_total} kcal/dia`")
            st.caption("Quantidade para manter exatamente o mesmo peso atual.")
            
            st.markdown(f"**🥗 Meta para Emagrecimento Saudável:** `{meta_emagrecimento} kcal/dia`")
            st.caption("Déficit calórico equilibrado (~0.4 a 0.5 kg de gordura perdida por semana).")

# ----------------- ABA 3: TROCAR SENHA -----------------
with tab_senha:
    with st.form("form_trocar_senha"):
        st.markdown("#### Segurança de Acesso")
        senha_atual = st.text_input("Senha Atual", type="password")
        nova_senha = st.text_input("Nova Senha", type="password")
        confirma_senha = st.text_input("Confirmar Nova Senha", type="password")

        if st.form_submit_button("Atualizar Senha", type="primary"):
            if not senha_atual or not nova_senha:
                st.warning("Preencha todos os campos.")
            elif nova_senha != confirma_senha:
                st.error("A nova senha e a confirmação não coincidem.")
            elif len(nova_senha) < 4:
                st.error("A senha deve ter no mínimo 4 caracteres.")
            else:
                with get_db() as db:
                    u = db.query(Usuario).filter(Usuario.id == usuario["id"]).first()
                    if u and u.senha_hash == hash_senha(senha_atual):
                        u.senha_hash = hash_senha(nova_senha)
                        st.success("✅ Senha alterada com sucesso!")
                    else:
                        st.error("Senha atual incorreta.")

st.divider()
st.caption(f"Conexão ativa: **PostgreSQL Neon Serverless** • Usuário ID: {usuario['id']} ({usuario['login']})")

