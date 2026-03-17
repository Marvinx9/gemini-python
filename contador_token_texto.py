import os
from decimal import Decimal

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODELO = os.getenv("GEMINI_MODELO")
CUSTO_ENTRADA_USD_POR_MILHAO = Decimal(os.getenv("CUSTO_ENTRADA_USD_POR_MILHAO"))
CUSTO_SAIDA_USD_POR_MILHAO = Decimal(os.getenv("CUSTO_SAIDA_USD_POR_MILHAO"))
CHAVE_API_GOOGLE = os.getenv("GEMINI_API_KEY")

if not CHAVE_API_GOOGLE:
    raise ValueError("Defina a variável GEMINI_API_KEY no arquivo .env.")

genai.configure(api_key=CHAVE_API_GOOGLE)

def obter_limites_modelo(nome_modelo):
    metadados_modelo = genai.get_model(f"models/{nome_modelo}")
    return {
        "tokens_entrada": metadados_modelo.input_token_limit,
        "tokens_saida": metadados_modelo.output_token_limit,
    }

def calcular_custo(tokens, preco_por_milhao):
    return (Decimal(tokens) * preco_por_milhao) / Decimal("1000000")


def calcular_metricas_iteracao(prompt, llm):
    resposta = llm.generate_content(prompt)
    uso = resposta.usage_metadata

    tokens_entrada = int(getattr(uso, "prompt_token_count", 0) or 0)
    tokens_saida = int(getattr(uso, "candidates_token_count", 0) or 0)
    tokens_totais = int(getattr(uso, "total_token_count", 0) or (tokens_entrada + tokens_saida))

    if not tokens_entrada:
        tokens_entrada = int(llm.count_tokens(prompt).total_tokens)
        tokens_totais = tokens_entrada + tokens_saida

    custo_entrada = calcular_custo(tokens_entrada, CUSTO_ENTRADA_USD_POR_MILHAO)
    custo_saida = calcular_custo(tokens_saida, CUSTO_SAIDA_USD_POR_MILHAO)

    return {
        "resposta": resposta.text,
        "tokens_entrada": tokens_entrada,
        "tokens_saida": tokens_saida,
        "tokens_totais": tokens_totais,
        "custo_entrada_usd": custo_entrada,
        "custo_saida_usd": custo_saida,
        "custo_total_usd": custo_entrada + custo_saida,
    }

prompt = os.getenv("PROMPT")

def main():
    limites_modelo = obter_limites_modelo(GEMINI_MODELO)
    print(f"Limites do modelo {GEMINI_MODELO}: {limites_modelo}")

    llm = genai.GenerativeModel(model_name=GEMINI_MODELO)
    metricas = calcular_metricas_iteracao(prompt, llm)

    print(f"Tokens de entrada usados: {metricas['tokens_entrada']}")
    print(f"Tokens de saída usados: {metricas['tokens_saida']}")
    print(f"Total de tokens usados: {metricas['tokens_totais']}")
    print(f"Custo de entrada (USD): ${metricas['custo_entrada_usd']:.6f}")
    print(f"Custo de saída (USD): ${metricas['custo_saida_usd']:.6f}")
    print(f"Custo total da iteração (USD): ${metricas['custo_total_usd']:.6f}")
    print(f"Resposta do modelo:\n{metricas['resposta']}")


if __name__ == "__main__":
    main()
