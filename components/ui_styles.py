import streamlit as st

def aplicar_estilos_responsivos():
    """
    Injeta regras de CSS personalizadas com media queries para garantir
    que a interface se adapte perfeitamente a dispositivos móveis (smartphones e tablets),
    evitando zoom indesejado no iOS, quebras de layout, e melhorando espaçamentos e toques.
    """
    css = """
    <style>
    /* ============================================================
       ADAPTAÇÃO MOBILE & RESPONSIVIDADE — EVOLUÇÃO SAÚDE
       ============================================================ */
    
    /* Previne rolagem horizontal indesejada no aplicativo */
    html, body, [data-testid="stAppViewContainer"], .main {
        max-width: 100vw !important;
        overflow-x: hidden !important;
    }

    /* Otimização especial para telas de celulares (até 768px) */
    @media (max-width: 768px) {
        /* Aproveita o espaço da tela do celular removendo as margens gigantes do Streamlit */
        .block-container {
            padding-top: 1.2rem !important;
            padding-bottom: 2.5rem !important;
            padding-left: 0.75rem !important;
            padding-right: 0.75rem !important;
            max-width: 100% !important;
        }

        /* Tipografia harmoniosa e legível no mobile */
        h1 {
            font-size: 22px !important;
            line-height: 1.25 !important;
            margin-bottom: 6px !important;
        }
        h2 {
            font-size: 19px !important;
            line-height: 1.25 !important;
        }
        h3 {
            font-size: 16px !important;
            line-height: 1.3 !important;
        }
        h4, h5 {
            font-size: 14px !important;
        }
        p, span, label {
            font-size: 13.5px !important;
        }

        /* Evita o auto-zoom incômodo do iPhone / Safari ao focar inputs */
        input, select, textarea, [data-baseweb="input"] input {
            font-size: 16px !important;
        }

        /* Botões com altura tátil recomendada (mínimo 44px) */
        .stButton > button {
            min-height: 44px !important;
            font-size: 15px !important;
            font-weight: 600 !important;
            width: 100% !important;
            border-radius: 10px !important;
        }

        /* Cards de KPIs otimizados para telas estreitas */
        .card-kpi {
            padding: 12px 14px !important;
            margin-bottom: 8px !important;
        }
        .card-kpi-valor {
            font-size: 21px !important;
        }

        /* Abas com rolagem horizontal suave por toque */
        div[data-baseweb="tab-list"] {
            display: flex !important;
            flex-direction: row !important;
            overflow-x: auto !important;
            white-space: nowrap !important;
            flex-wrap: nowrap !important;
            -webkit-overflow-scrolling: touch !important;
            scroll-behavior: smooth !important;
            scrollbar-width: none !important;
            padding-bottom: 6px !important;
            gap: 6px !important;
            width: 100% !important;
        }
        div[data-baseweb="tab-list"]::-webkit-scrollbar {
            display: none !important;
        }

        /* Oculta as flechinhas quebradas do BaseWeb que travam no celular */
        div[data-baseweb="tab-list"] ~ button,
        div[data-baseweb="tab-list"] > button[aria-label*="Scroll"],
        div[data-baseweb="tab-list"] > button[aria-label="Previous"],
        div[data-baseweb="tab-list"] > button[aria-label="Next"],
        div[data-baseweb="tab-border"] ~ button {
            display: none !important;
        }

        button[data-baseweb="tab"] {
            flex: 0 0 auto !important;
            padding: 8px 14px !important;
            font-size: 13.5px !important;
            min-height: 42px !important;
            border-radius: 8px !important;
        }

        /* Botão da barra lateral touch-friendly */
        [data-testid="stSidebarCollapsedControl"],
        [data-testid="collapsedControl"] {
            top: 14px !important;
            left: 14px !important;
            z-index: 999999 !important;
            min-width: 44px !important;
            min-height: 44px !important;
            display: flex !important;
            align-items: center !important;
            justify-content: center !important;
        }

        /* Colunas fluidas empilhadas com espaçamento limpo */
        [data-testid="column"] {
            width: 100% !important;
            flex: 1 1 100% !important;
            min-width: 100% !important;
            margin-bottom: 6px !important;
        }

        /* Gráficos Plotly 100% fluidos */
        .js-plotly-plot, .plot-container {
            width: 100% !important;
            max-width: 100% !important;
        }

        /* Tabelas com rolagem lateral sem deformar a página */
        [data-testid="stDataFrame"], [data-testid="stTable"] {
            width: 100% !important;
            overflow-x: auto !important;
            -webkit-overflow-scrolling: touch !important;
        }

        /* Barra de navegação nativa e sidebar */
        [data-testid="stSidebar"] {
            min-width: 280px !important;
            max-width: 85vw !important;
        }
    }

    /* Tablets (769px a 1024px) */
    @media (min-width: 769px) and (max-width: 1024px) {
        .block-container {
            padding-left: 1.5rem !important;
            padding-right: 1.5rem !important;
        }
    }
    </style>
    """
    st.markdown(css, unsafe_allow_html=True)

