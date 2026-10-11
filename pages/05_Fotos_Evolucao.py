import os
import streamlit as st
import pandas as pd
from datetime import date
from PIL import Image
from database.connection import get_db
from database.models import FotoEvolucao
from utils.auth import requer_login, get_usuario_logado
from components.sidebar import render_sidebar

st.set_page_config(page_title="Galeria de Evolução — Evolução Saúde", page_icon="📸", layout="wide")
requer_login()
render_sidebar()

usuario = get_usuario_logado()

UPLOAD_DIR = os.path.join(os.path.dirname(os.path.dirname(__file__)), "uploads")
os.makedirs(UPLOAD_DIR, exist_ok=True)

st.markdown(
    """
    <div style="margin-bottom: 20px;">
        <h1 style="color: #0F172A; margin: 0; font-size: 28px; font-weight: 800;">
            📸 Galeria de Evolução & Comparativo Visual
        </h1>
        <p style="color: #64748B; font-size: 14px; margin-top: 4px;">
            Acompanhe a transformação visual no espelho lado a lado (Antes x Depois).
        </p>
    </div>
    """,
    unsafe_allow_html=True
)

tab_comp, tab_upload, tab_todas = st.tabs(["⚖️ Comparativo Antes & Depois", "📤 Enviar Nova Foto", "🖼️ Todas as Fotos"])

# ----------------- CARREGA FOTOS DO BANCO -----------------
with get_db() as db:
    fotos = db.query(FotoEvolucao).filter(
        FotoEvolucao.usuario_id == usuario["id"]
    ).order_by(FotoEvolucao.data_foto.asc()).all()
    
    lista_fotos = [
        {
            "id": f.id,
            "data": f.data_foto,
            "tipo": f.tipo,
            "path": f.caminho_arquivo,
            "peso": f.peso_no_dia,
            "notas": f.notas or ""
        }
        for f in fotos
    ]

# ----------------- ABA 1: COMPARATIVO ANTES & DEPOIS -----------------
with tab_comp:
    if len(lista_fotos) >= 2:
        st.markdown("### Selecione as fotos para comparar:")
        col_c1, col_c2 = st.columns(2)
        
        opcoes = [f["id"] for f in lista_fotos]
        def format_label(f_id):
            item = next(f for f in lista_fotos if f["id"] == f_id)
            peso_txt = f"({item['peso']} kg)" if item["peso"] else ""
            return f"{item['data'].strftime('%d/%m/%Y')} - {item['tipo'].capitalize()} {peso_txt}"

        with col_c1:
            id_antes = st.selectbox("Foto do Início (Antes)", options=opcoes, index=0, format_func=format_label)
            foto_antes = next(f for f in lista_fotos if f["id"] == id_antes)
            if os.path.exists(foto_antes["path"]):
                st.image(foto_antes["path"], caption=f"Antes: {foto_antes['data'].strftime('%d/%m/%Y')} | {foto_antes['peso'] or '—'} kg", use_container_width=True)
            else:
                st.warning("Arquivo da foto não encontrado localmente.")

        with col_c2:
            id_depois = st.selectbox("Foto Recente (Depois)", options=opcoes, index=len(opcoes)-1, format_func=format_label)
            foto_depois = next(f for f in lista_fotos if f["id"] == id_depois)
            if os.path.exists(foto_depois["path"]):
                st.image(foto_depois["path"], caption=f"Depois: {foto_depois['data'].strftime('%d/%m/%Y')} | {foto_depois['peso'] or '—'} kg", use_container_width=True)
            else:
                st.warning("Arquivo da foto não encontrado localmente.")

    elif len(lista_fotos) == 1:
        st.info("Você tem 1 foto cadastrada. Adicione mais uma foto na aba 'Enviar Nova Foto' para habilitar a comparação lado a lado!")
        f = lista_fotos[0]
        if os.path.exists(f["path"]):
            st.image(f["path"], caption=f"{f['data'].strftime('%d/%m/%Y')} - {f['tipo'].capitalize()}", width=350)
    else:
        st.info("Nenhuma foto cadastrada ainda. Envie suas fotos de evolução na aba 'Enviar Nova Foto'.")

# ----------------- ABA 2: ENVIAR NOVA FOTO -----------------
with tab_upload:
    with st.form("form_upload_foto", clear_on_submit=True):
        st.markdown("#### Fazer Upload de Foto de Evolução")
        
        col_u1, col_u2 = st.columns([1.5, 1])
        with col_u1:
            arquivo_foto = st.file_uploader("Selecione a Imagem", type=["jpg", "jpeg", "png"])
            data_foto = st.date_input("Data da Foto", value=date.today())
        with col_u2:
            tipo_foto = st.selectbox("Ângulo da Foto", ["Frente", "Lado / Perfil", "Costas"])
            peso_dia = st.number_input("Peso neste dia (kg, opcional)", min_value=0.0, max_value=250.0, value=0.0, step=0.1)
            notas_foto = st.text_input("Observações", placeholder="Ex: Início do 2º mês")

        if st.form_submit_button("Salvar Foto", type="primary", use_container_width=True):
            if not arquivo_foto:
                st.error("Por favor, selecione uma imagem.")
            else:
                # Salva o arquivo em uploads/
                nome_seguro = f"user_{usuario['id']}_{date.today().strftime('%Y%m%d%H%M%S')}_{arquivo_foto.name}"
                caminho_salvo = os.path.join(UPLOAD_DIR, nome_seguro)
                
                with open(caminho_salvo, "wb") as f_out:
                    f_out.write(arquivo_foto.getbuffer())

                with get_db() as db:
                    nova_foto = FotoEvolucao(
                        usuario_id=usuario["id"],
                        data_foto=data_foto,
                        tipo=tipo_foto.lower(),
                        caminho_arquivo=caminho_salvo,
                        peso_no_dia=round(peso_dia, 2) if peso_dia > 0 else None,
                        notas=notas_foto
                    )
                    db.add(nova_foto)
                st.success("✅ Foto salva com sucesso na galeria!")
                st.rerun()

# ----------------- ABA 3: TODAS AS FOTOS -----------------
with tab_todas:
    if lista_fotos:
        cols_grid = st.columns(3)
        for idx, item in enumerate(lista_fotos):
            col_atual = cols_grid[idx % 3]
            with col_atual:
                with st.container(border=True):
                    if os.path.exists(item["path"]):
                        st.image(item["path"], use_container_width=True)
                    st.caption(f"📅 {item['data'].strftime('%d/%m/%Y')} | **{item['tipo'].capitalize()}**")
                    if item["peso"]:
                        st.write(f"⚖️ {item['peso']:.1f} kg")
                    if item["notas"]:
                        st.caption(f"📝 {item['notas']}")
    else:
        st.write("Nenhuma foto disponível.")
