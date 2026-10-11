import streamlit as st
from database.models import Usuario, hash_senha
from database.connection import get_db

def verificar_credenciais(login: str, senha: str):
    """Verifica credenciais no banco de dados Neon."""
    with get_db() as db:
        senha_h = hash_senha(senha)
        usuario = db.query(Usuario).filter(
            Usuario.login == login.lower().strip(),
            Usuario.senha_hash == senha_h
        ).first()
        if usuario:
            return {
                "id": usuario.id,
                "nome": usuario.nome,
                "login": usuario.login,
                "role": usuario.role
            }
    return None

def login_usuario(usuario_dict: dict):
    """Salva os dados do usuário na sessão."""
    st.session_state["autenticado"] = True
    st.session_state["usuario"] = usuario_dict

def logout():
    """Limpa a sessão do usuário."""
    st.session_state["autenticado"] = False
    st.session_state["usuario"] = None
    st.rerun()

def get_usuario_logado():
    """Retorna o dicionário do usuário logado ou None."""
    if st.session_state.get("autenticado", False):
        return st.session_state.get("usuario")
    return None

def requer_login():
    """Garante que a página só seja acessível por usuários autenticados."""
    if not st.session_state.get("autenticado", False):
        st.warning("🔒 Por favor, faça login para acessar esta página.")
        st.page_link("app.py", label="Ir para o Login", icon="👉")
        st.stop()
