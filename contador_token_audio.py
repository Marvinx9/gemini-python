import base64
import mimetypes
import os
import sys
from decimal import Decimal
from pathlib import Path

import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_MODELO = os.getenv("GEMINI_MODELO")
URL_GEMINI = (
    f"https://generativelanguage.googleapis.com/v1beta/models/{GEMINI_MODELO}:generateContent"
)
CUSTO_TEXTO_ENTRADA_USD_POR_MILHAO = Decimal(os.getenv("CUSTO_TEXTO_ENTRADA_USD_POR_MILHAO"))
CUSTO_AUDIO_ENTRADA_USD_POR_MILHAO = Decimal(os.getenv("CUSTO_AUDIO_ENTRADA_USD_POR_MILHAO"))
CUSTO_SAIDA_USD_POR_MILHAO = Decimal(os.getenv("CUSTO_SAIDA_USD_POR_MILHAO"))
PASTA_AUDIO = Path(__file__).resolve().parent / "audio"
EXTENSOES_AUDIO_SUPORTADAS = {".mp3", ".wav", ".aac", ".flac", ".ogg", ".m4a"}
PROMPT_TRANSCRICAO = os.getenv("PROMPT_TRANSCRICAO", """
Generate a Brazilian Portuguese transcript for this file related to a call from (SAC Liv Saúde), consider and count the time of silence in secounds and attendant's name. You should return only the transcript without comments and time, in the array JSON format: {"transcricao": [{"speaker": "cliente","transcript": "SAC Liv Saúde Liliane. Bom dia"}],"tempo_silencio": 6, "nome_atendente": "Liliane"}
""".strip())

CHAVE_API_GOOGLE = os.getenv("GEMINI_API_KEY")

if not CHAVE_API_GOOGLE:
    raise ValueError("Defina a variável GEMINI_API_KEY no arquivo .env.")


def calcular_custo(tokens, preco_por_milhao):
    return (Decimal(tokens) * preco_por_milhao) / Decimal("1000000")


def resolver_caminho_audio():
    if len(sys.argv) > 1:
        caminho_audio = Path(sys.argv[1]).expanduser()
        if not caminho_audio.is_absolute():
            caminho_audio = Path.cwd() / caminho_audio
        if not caminho_audio.exists():
            raise FileNotFoundError(f"Arquivo de áudio não encontrado: {caminho_audio}")
        return caminho_audio

    arquivos_audio = sorted(
        caminho for caminho in PASTA_AUDIO.iterdir()
        if caminho.is_file() and caminho.suffix.lower() in EXTENSOES_AUDIO_SUPORTADAS
    )

    if not arquivos_audio:
        raise FileNotFoundError(
            f"Nenhum áudio compatível foi encontrado em: {PASTA_AUDIO}"
        )

    return arquivos_audio[0]


def montar_payload(caminho_audio):
    mime_type, _ = mimetypes.guess_type(caminho_audio.name)
    if mime_type is None:
        raise ValueError(
            f"Não foi possível identificar o MIME type do arquivo: {caminho_audio.name}"
        )

    audio_base64 = base64.b64encode(caminho_audio.read_bytes()).decode("utf-8")

    payload = {
        "contents": [
            {
                "role": "user",
                "parts": [
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": audio_base64,
                        }
                    },
                    {
                        "text": PROMPT_TRANSCRICAO,
                    },
                ],
            }
        ]
    }
    return payload, mime_type


def chamar_gemini(payload):
    resposta = requests.post(
        URL_GEMINI,
        params={"key": CHAVE_API_GOOGLE},
        json=payload,
        timeout=120,
    )
    resposta.raise_for_status()
    return resposta.json()


def obter_tokens_prompt_por_modalidade(usage_metadata):
    tokens_texto = 0
    tokens_audio = 0

    for detalhe in usage_metadata.get("promptTokensDetails", []):
        modalidade = detalhe.get("modality")
        quantidade = int(detalhe.get("tokenCount", 0) or 0)

        if modalidade == "TEXT":
            tokens_texto += quantidade
        elif modalidade == "AUDIO":
            tokens_audio += quantidade

    return tokens_texto, tokens_audio


def extrair_texto_resposta(body):
    candidatos = body.get("candidates", [])
    if not candidatos:
        raise RuntimeError("Gemini retornou vazio.")

    partes = candidatos[0].get("content", {}).get("parts", [])
    textos = [parte["text"] for parte in partes if "text" in parte]
    return "\n".join(textos).strip()


def calcular_metricas_transcricao(body):
    usage_metadata = body.get("usageMetadata", {})
    tokens_texto_entrada, tokens_audio_entrada = obter_tokens_prompt_por_modalidade(
        usage_metadata
    )
    tokens_saida = int(usage_metadata.get("candidatesTokenCount", 0) or 0)
    tokens_thoughts = int(usage_metadata.get("thoughtsTokenCount", 0) or 0)
    tokens_entrada_total = int(usage_metadata.get("promptTokenCount", 0) or 0)
    tokens_totais_api = int(usage_metadata.get("totalTokenCount", 0) or 0)
    tokens_totais_faturaveis = tokens_texto_entrada + tokens_audio_entrada + tokens_saida

    custo_texto_entrada = calcular_custo(
        tokens_texto_entrada,
        CUSTO_TEXTO_ENTRADA_USD_POR_MILHAO,
    )
    custo_audio_entrada = calcular_custo(
        tokens_audio_entrada,
        CUSTO_AUDIO_ENTRADA_USD_POR_MILHAO,
    )
    custo_saida = calcular_custo(tokens_saida, CUSTO_SAIDA_USD_POR_MILHAO)

    return {
        "resposta": extrair_texto_resposta(body),
        "tokens_texto_entrada": tokens_texto_entrada,
        "tokens_audio_entrada": tokens_audio_entrada,
        "tokens_entrada_total": tokens_entrada_total,
        "tokens_saida": tokens_saida,
        "tokens_thoughts": tokens_thoughts,
        "tokens_totais_api": tokens_totais_api,
        "tokens_totais_faturaveis": tokens_totais_faturaveis,
        "custo_texto_entrada_usd": custo_texto_entrada,
        "custo_audio_entrada_usd": custo_audio_entrada,
        "custo_saida_usd": custo_saida,
        "custo_total_usd": custo_texto_entrada + custo_audio_entrada + custo_saida,
    }


def main():
    caminho_audio = resolver_caminho_audio()
    payload, mime_type = montar_payload(caminho_audio)
    body = chamar_gemini(payload)
    metricas = calcular_metricas_transcricao(body)

    print(f"Modelo: {GEMINI_MODELO}")
    print(f"Arquivo de áudio: {caminho_audio}")
    print(f"MIME type: {mime_type}")
    print(f"Tokens de entrada (texto): {metricas['tokens_texto_entrada']}")
    print(f"Tokens de entrada (áudio): {metricas['tokens_audio_entrada']}")
    print(f"Tokens de entrada (total): {metricas['tokens_entrada_total']}")
    print(f"Tokens de saída: {metricas['tokens_saida']}")
    print(f"Tokens thoughts reportados pela API: {metricas['tokens_thoughts']}")
    print(f"Total de tokens faturáveis: {metricas['tokens_totais_faturaveis']}")
    print(f"Total de tokens reportados pela API: {metricas['tokens_totais_api']}")
    print(f"Custo de entrada texto (USD): ${metricas['custo_texto_entrada_usd']:.6f}")
    print(f"Custo de entrada áudio (USD): ${metricas['custo_audio_entrada_usd']:.6f}")
    print(f"Custo de saída (USD): ${metricas['custo_saida_usd']:.6f}")
    print(f"Custo total estimado da transcrição (USD): ${metricas['custo_total_usd']:.6f}")
    print("Observação: o custo acima considera texto de entrada, áudio de entrada e saída.")
    print("Observação: os tokens de thoughts foram exibidos separadamente e não entraram no custo.")
    print(f"Transcrição retornada:\n{metricas['resposta']}")


if __name__ == "__main__":
    main()
