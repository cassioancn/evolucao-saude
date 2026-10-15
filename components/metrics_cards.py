import streamlit as st

def card_metrica(titulo: str, valor: str, subtitulo: str = "", cor_borda: str = "#0D9488", icone: str = ""):
    """Renderiza um card visual moderno para KPIs com design clean."""
    st.markdown(
        f"""
        <div class="card-kpi" style="
            background: #FFFFFF;
            border-radius: 12px;
            padding: 16px 20px;
            border-left: 5px solid {cor_borda};
            box-shadow: 0 1px 3px rgba(0,0,0,0.06);
            margin-bottom: 12px;
        ">
            <div style="display: flex; justify-content: space-between; align-items: center;">
                <span style="font-size: 13px; font-weight: 600; color: #64748B; text-transform: uppercase; letter-spacing: 0.5px;">{titulo}</span>
                <span style="font-size: 20px;">{icone}</span>
            </div>
            <div class="card-kpi-valor" style="font-size: 26px; font-weight: 700; color: #0F172A; margin: 4px 0;">{valor}</div>
            <div style="font-size: 12px; color: #64748B;">{subtitulo}</div>
        </div>
        """,
        unsafe_allow_html=True
    )

def barra_progresso_meta(progresso_pct: float, peso_atual: float, peso_meta: float):
    """Renderiza uma barra de progresso estilizada com percentual e pesos."""
    progresso_clamped = max(0.0, min(100.0, progresso_pct))
    st.markdown(
        f"""
        <div style="background: #FFFFFF; border-radius: 12px; padding: 18px; box-shadow: 0 1px 3px rgba(0,0,0,0.06); margin-bottom: 16px;">
            <div style="display: flex; justify-content: space-between; margin-bottom: 8px;">
                <span style="font-size: 14px; font-weight: 600; color: #334155;">Progresso até o Alvo</span>
                <span style="font-size: 15px; font-weight: 700; color: #0D9488;">{progresso_clamped:.1f}%</span>
            </div>
            <div style="background: #E2E8F0; border-radius: 10px; height: 14px; overflow: hidden; width: 100%;">
                <div style="background: linear-gradient(90deg, #14B8A6, #0D9488); width: {progresso_clamped}%; height: 100%; border-radius: 10px; transition: width 0.5s ease-in-out;"></div>
            </div>
            <div style="display: flex; justify-content: space-between; margin-top: 8px; font-size: 12px; color: #64748B;">
                <span>📍 Atual: <b>{peso_atual:.1f} kg</b></span>
                <span>🎯 Meta: <b>{peso_meta:.1f} kg</b></span>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

