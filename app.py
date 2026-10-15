import streamlit as st
from database.models import init_db
from utils.auth import verificar_credenciais, login_usuario, get_usuario_logado
from components.sidebar import render_sidebar
from components.ui_styles import aplicar_estilos_responsivos

st.set_page_config(
    page_title="Evolução Saúde",
    page_icon="🌿",
    layout="wide",
    initial_sidebar_state="auto"
)
aplicar_estilos_responsivos()

# Inicializa as tabelas no Neon (se ainda não existirem)
try:
    init_db()
except Exception as e:
    st.error(f"Erro ao conectar com o banco Neon: {e}")

usuario = get_usuario_logado()

if usuario:
    render_sidebar()
    # Se já estiver logado, redireciona diretamente para o Dashboard
    st.switch_page("pages/01_Dashboard.py")
else:
    # Tela de Login Centralizada e Elegante
    col_left, col_center, col_right = st.columns([1, 1.8, 1])

    with col_center:
        st.markdown(
            """
            <div style="text-align: center; margin-top: 40px; margin-bottom: 25px;">
                <div style="font-size: 55px; margin-bottom: 8px;">🌿</div>
                <h1 style="color: #0D9488; margin: 0; font-size: 32px; font-weight: 800;">Evolução Saúde</h1>
                <p style="color: #64748B; font-size: 15px; margin-top: 6px;">
                    Acompanhamento de peso, composição corporal e bem-estar
                </p>
            </div>
            """,
            unsafe_allow_html=True
        )

        with st.container(border=True):
            st.markdown("### 🔐 Acessar Sistema")
            
            perfil_rapido = st.radio(
                "Quem está acessando?",
                ["Bruna 🌸", "Cássio 👤", "Outro usuário"],
                horizontal=True
            )
            
            if perfil_rapido == "Bruna 🌸":
                login_padrao = "bruna"
            elif perfil_rapido == "Cássio 👤":
                login_padrao = "cassio"
            else:
                login_padrao = ""

            usuario_input = st.text_input("Usuário", value=login_padrao)
            senha_input = st.text_input("Senha", type="password")

            if st.button("Entrar", type="primary", use_container_width=True):
                if not usuario_input or not senha_input:
                    st.warning("Preencha o usuário e a senha.")
                else:
                    user_data = verificar_credenciais(usuario_input, senha_input)
                    if user_data:
                        login_usuario(user_data)
                        st.success(f"Bem-vinda(o), {user_data['nome']}! Entrando...")
                        st.switch_page("pages/01_Dashboard.py")
                    else:
                        st.error("Usuário ou senha incorretos.")

        st.markdown(
            """
            <div style="text-align: center; margin-top: 25px; color: #94A3B8; font-size: 12px;">
                Evolução Saúde &copy; 2026 &bull; Conectado ao PostgreSQL Neon
            </div>
            """,
            unsafe_allow_html=True
        )

