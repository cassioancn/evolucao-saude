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

import base64
import streamlit.components.v1 as components
from pathlib import Path

# Injeção de Meta Tags Apple Touch Icon e Web App para iOS Safari
def inject_pwa_meta_tags(app_title: str, icon_file: Path):
    """Injeta meta tags iOS e Apple Touch Icon diretamente no head do navegador."""
    if not icon_file.exists():
        return
    try:
        with open(icon_file, "rb") as f:
            b64_str = base64.b64encode(f.read()).decode("utf-8")
        data_uri = f"data:image/png;base64,{b64_str}"
        
        components.html(f"""
        <script>
        (function() {{
            try {{
                const doc = window.parent.document;
                const head = doc.head;
                
                // 1. Remove qualquer apple-touch-icon anterior
                const oldIcons = head.querySelectorAll("link[rel*='apple-touch-icon']");
                oldIcons.forEach(el => el.remove());

                // 2. Adiciona o novo apple-touch-icon em alta resolução
                const link = doc.createElement("link");
                link.rel = "apple-touch-icon";
                link.sizes = "180x180";
                link.href = "{data_uri}";
                head.appendChild(link);

                const linkPre = doc.createElement("link");
                linkPre.rel = "apple-touch-icon-precomposed";
                linkPre.href = "{data_uri}";
                head.appendChild(linkPre);

                // 3. Atualiza o favicon
                const favicons = head.querySelectorAll("link[rel*='icon']");
                favicons.forEach(el => el.href = "{data_uri}");

                // 4. Meta tags para Web App standalone no iOS
                let metaCap = doc.querySelector("meta[name='apple-mobile-web-app-capable']");
                if (!metaCap) {{
                    metaCap = doc.createElement("meta");
                    metaCap.name = "apple-mobile-web-app-capable";
                    head.appendChild(metaCap);
                }}
                metaCap.content = "yes";

                let metaTitle = doc.querySelector("meta[name='apple-mobile-web-app-title']");
                if (!metaTitle) {{
                    metaTitle = doc.createElement("meta");
                    metaTitle.name = "apple-mobile-web-app-title";
                    head.appendChild(metaTitle);
                }}
                metaTitle.content = "{app_title}";

                let metaStatus = doc.querySelector("meta[name='apple-mobile-web-app-status-bar-style']");
                if (!metaStatus) {{
                    metaStatus = doc.createElement("meta");
                    metaStatus.name = "apple-mobile-web-app-status-bar-style";
                    head.appendChild(metaStatus);
                }}
                metaStatus.content = "black-translucent";
            }} catch(e) {{
                console.warn("PWA inject error:", e);
            }}
        }})();
        </script>
        """, height=0, width=0)
    except Exception:
        pass

pwa_icon_path = Path(__file__).resolve().parent / "assets" / "apple-touch-icon.png"
inject_pwa_meta_tags("Evolução Saúde", pwa_icon_path)

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

