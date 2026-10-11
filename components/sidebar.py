import streamlit as st
from utils.auth import get_usuario_logado, logout

def render_sidebar():
    """Renderiza a barra lateral padronizada do aplicativo Evolução Saúde."""
    usuario = get_usuario_logado()
    if not usuario:
        return

    with st.sidebar:
        # Cabeçalho da Sidebar
        st.markdown(
            """
            <div style="text-align: center; padding: 10px 0 20px 0;">
                <div style="font-size: 38px;">🌿</div>
                <h2 style="margin: 0; color: #0D9488; font-size: 22px; font-weight: 700;">Evolução Saúde</h2>
                <p style="margin: 0; color: #64748B; font-size: 13px;">Acompanhamento & Bem-estar</p>
            </div>
            """,
            unsafe_allow_html=True
        )

        # Card do Usuário Logado
        emoji_perfil = "🌸" if usuario["login"] == "bruna" else "👤"
        st.markdown(
            f"""
            <div style="background-color: #F0FDFA; border: 1px solid #CCFBF1; border-radius: 10px; padding: 12px; margin-bottom: 20px;">
                <div style="font-size: 12px; color: #0F766E; font-weight: 600;">PERFIL ATIVO</div>
                <div style="font-size: 16px; font-weight: 700; color: #134E4A;">{emoji_perfil} {usuario['nome']}</div>
            </div>
            """,
            unsafe_allow_html=True
        )

        st.markdown("<p style='font-size: 12px; font-weight: 700; color: #94A3B8; margin-bottom: 8px;'>NAVEGAÇÃO</p>", unsafe_allow_html=True)
        
        # Links de Páginas
        st.page_link("pages/01_Dashboard.py", label="Dashboard & Metas", icon="📊")
        st.page_link("pages/02_Bioimpedancia.py", label="Bioimpedância (OKOK)", icon="⚖️")
        st.page_link("pages/03_Medidas.py", label="Medidas Corporais", icon="📏")
        st.page_link("pages/04_Habitos_Diario.py", label="Diário & Hábitos", icon="💧")
        st.page_link("pages/05_Fotos_Evolucao.py", label="Galeria de Fotos", icon="📸")
        st.page_link("pages/06_Configuracoes.py", label="Configurações", icon="⚙️")

        st.divider()

        # Botão de Logout
        if st.button("🚪 Sair do Sistema", use_container_width=True):
            logout()
