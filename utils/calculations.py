from datetime import date, timedelta
from typing import Tuple, Dict, Any
import pandas as pd

def calcular_imc(peso_kg: float, altura_cm: float) -> Tuple[float, str, str]:
    """
    Calcula o IMC e retorna (imc, classificação, cor).
    Cores: Verde (Normal), Amarelo (Sobrepeso), Laranja (Obesidade I), etc.
    """
    if not altura_cm or altura_cm <= 0 or not peso_kg or peso_kg <= 0:
        return 0.0, "Indefinido", "#64748B"
    
    altura_m = altura_cm / 100.0
    imc = peso_kg / (altura_m ** 2)
    imc = round(imc, 1)

    if imc < 18.5:
        return imc, "Abaixo do peso", "#3B82F6"
    elif imc < 25.0:
        return imc, "Peso saudável", "#10B981"
    elif imc < 30.0:
        return imc, "Sobrepeso", "#F59E0B"
    elif imc < 35.0:
        return imc, "Obesidade Grau I", "#F97316"
    elif imc < 40.0:
        return imc, "Obesidade Grau II", "#EF4444"
    else:
        return imc, "Obesidade Grau III", "#991B1B"

def calcular_tmb_mifflin(sexo: str, peso_kg: float, altura_cm: float, idade: int) -> int:
    """Calcula a Taxa Metabólica Basal pela fórmula Mifflin-St Jeor."""
    if not peso_kg or not altura_cm or not idade:
        return 1400
    
    # 10*peso + 6.25*altura - 5*idade
    base = (10 * peso_kg) + (6.25 * altura_cm) - (5 * idade)
    if sexo.lower() in ["f", "feminino", "mulher"]:
        tmb = base - 161
    else:
        tmb = base + 5
    return int(round(tmb))

def calcular_projecao_meta(peso_atual: float, peso_meta: float, taxa_kg_semana: float) -> Dict[str, Any]:
    """
    Estima as semanas e data para atingir a meta com base na taxa de perda semanal.
    """
    diferenca = peso_atual - peso_meta
    if diferenca <= 0:
        return {
            "meta_atingida": True,
            "semanas": 0,
            "data_estimada": date.today(),
            "mensagem": "🎉 Meta alcançada com sucesso!"
        }
    
    if taxa_kg_semana <= 0.05:
        # Se a taxa recente for quase nula, assume um ritmo saudável de 0.4 kg/semana como referência
        taxa_estimada = 0.4
    else:
        taxa_estimada = min(taxa_kg_semana, 1.2) # Limite seguro para projeção

    semanas = round(diferenca / taxa_estimada, 1)
    dias = int(semanas * 7)
    data_estimada = date.today() + timedelta(days=dias)

    return {
        "meta_atingida": False,
        "semanas": semanas,
        "data_estimada": data_estimada,
        "taxa_usada": taxa_estimada,
        "mensagem": f"Faltam {diferenca:.1f} kg para sua meta"
    }

def processar_metricas_historico(df_pesagens: pd.DataFrame, peso_inicial: float, meta_peso: float) -> Dict[str, Any]:
    """Analisa o dataframe de pesagens e extrai indicadores de progresso."""
    if df_pesagens.empty:
        return {
            "peso_atual": peso_inicial,
            "variacao_total": 0.0,
            "perdido_ate_agora": 0.0,
            "progresso_pct": 0.0,
            "variacao_7d": 0.0,
            "variacao_30d": 0.0,
            "taxa_semanal": 0.4,
            "tem_dados": False
        }
    
    df = df_pesagens.sort_values(by="data_pesagem").copy()
    peso_atual = float(df.iloc[-1]["peso"])
    variacao_total = peso_atual - peso_inicial
    
    total_a_perder = peso_inicial - meta_peso
    perdido_ate_agora = peso_inicial - peso_atual
    
    if total_a_perder > 0:
        progresso_pct = max(0.0, min(100.0, (perdido_ate_agora / total_a_perder) * 100))
    else:
        progresso_pct = 100.0

    # Variação últimos 7 dias
    data_max = df["data_pesagem"].max()
    data_7d_atras = data_max - timedelta(days=7)
    df_7d = df[df["data_pesagem"] <= data_7d_atras]
    if not df_7d.empty:
        peso_7d = float(df_7d.iloc[-1]["peso"])
        variacao_7d = peso_atual - peso_7d
    else:
        variacao_7d = 0.0

    # Variação últimos 30 dias
    data_30d_atras = data_max - timedelta(days=30)
    df_30d = df[df["data_pesagem"] <= data_30d_atras]
    if not df_30d.empty:
        peso_30d = float(df_30d.iloc[-1]["peso"])
        variacao_30d = peso_atual - peso_30d
    else:
        variacao_30d = 0.0

    # Taxa semanal estimada baseada nos últimos 30 dias ou período total
    dias_totais = (data_max - df["data_pesagem"].min()).days
    if dias_totais >= 7 and perdido_ate_agora > 0:
        taxa_semanal = (perdido_ate_agora / dias_totais) * 7
    else:
        taxa_semanal = 0.4

    return {
        "peso_atual": round(peso_atual, 1),
        "variacao_total": round(variacao_total, 1),
        "perdido_ate_agora": round(perdido_ate_agora, 1),
        "progresso_pct": round(progresso_pct, 1),
        "variacao_7d": round(variacao_7d, 1),
        "variacao_30d": round(variacao_30d, 1),
        "taxa_semanal": round(taxa_semanal, 2),
        "tem_dados": True
    }

