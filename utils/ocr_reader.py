import re
from typing import Dict, Any
from PIL import Image

def extrair_dados_print_balanca(imagem_file) -> Dict[str, Any]:
    """
    Tenta realizar OCR na imagem do print da balança OKOK / app de saúde.
    Retorna um dicionário com os campos detectados.
    Se o OCR não estiver disponível ou falhar, retorna campos vazios com mensagem.
    """
    resultados = {
        "sucesso": False,
        "peso": None,
        "percentual_gordura": None,
        "massa_muscular_kg": None,
        "percentual_agua": None,
        "gordura_visceral": None,
        "tmb": None,
        "texto_detectado": "",
        "mensagem": ""
    }

    try:
        import pytesseract
        imagem = Image.open(imagem_file)
        
        # Converte para tons de cinza para melhor contraste
        imagem_cinza = imagem.convert("L")
        
        texto = pytesseract.image_to_string(imagem_cinza, config="--psm 6")
        resultados["texto_detectado"] = texto

        # Regex para Peso (ex: 68.4 kg ou 68,40)
        match_peso = re.search(r"(\b\d{2,3}[.,]\d{1,2}\b)\s*(?:kg|KG)?", texto)
        if match_peso:
            peso_str = match_peso.group(1).replace(",", ".")
            val = float(peso_str)
            if 35.0 <= val <= 250.0:
                resultados["peso"] = val

        # Regex para % Gordura
        match_fat = re.search(r"(?:fat|gordura|bf)[\s:]*(\b\d{1,2}[.,]\d{1,2}\b)%?", texto, re.IGNORECASE)
        if match_fat:
            resultados["percentual_gordura"] = float(match_fat.group(1).replace(",", "."))

        # Regex para Massa Muscular
        match_muscle = re.search(r"(?:m[uú]sculo|muscle|muscular)[\s:]*(\b\d{1,2}[.,]\d{1,2}\b)", texto, re.IGNORECASE)
        if match_muscle:
            resultados["massa_muscular_kg"] = float(match_muscle.group(1).replace(",", "."))

        # Regex para Água
        match_water = re.search(r"(?:water|[aá]gua)[\s:]*(\b\d{1,2}[.,]\d{1,2}\b)%?", texto, re.IGNORECASE)
        if match_water:
            resultados["percentual_agua"] = float(match_water.group(1).replace(",", "."))

        # Regex para Gordura Visceral
        match_visceral = re.search(r"(?:visceral)[\s:]*(\b\d{1,2}\b)", texto, re.IGNORECASE)
        if match_visceral:
            resultados["gordura_visceral"] = int(match_visceral.group(1))

        # Regex para TMB / BMR
        match_bmr = re.search(r"(?:bmr|tmb)[\s:]*(\b\d{3,4}\b)", texto, re.IGNORECASE)
        if match_bmr:
            resultados["tmb"] = int(match_bmr.group(1))

        resultados["sucesso"] = resultados["peso"] is not None
        resultados["mensagem"] = "Leitura concluída! Confira os valores abaixo antes de salvar."
    
    except Exception as e:
        # Fallback elegante caso Tesseract não esteja instalado no sistema operacional
        resultados["sucesso"] = False
        resultados["mensagem"] = (
            "Não foi possível ler o texto automaticamente da imagem. "
            "Você pode conferir a imagem na tela e preencher os campos rapidamente abaixo!"
        )

    return resultados
