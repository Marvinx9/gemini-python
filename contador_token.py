import os
import google.generativeai as genai
from dotenv import load_dotenv
import vertexai
from vertexai.generative_models import GenerativeModel
from google.oauth2 import service_account

load_dotenv()

GEMINI_MODELO_20_FLASH="gemini-2.0-flash"
CUSTO_ENTRADA_20_FLASH=0.10
CUSTO_SAIDA_20_FLASH=0.40
PROJECT_CREDENTIALS_LOCAL = os.getenv("PROJECT_CREDENTIALS_LOCAL")
PROJECT_ID = os.getenv("PROJECT_ID")
PROJECT_REGION = os.getenv("PROJECT_REGION")
CHAVE_API_GOOGLE = os.getenv("GEMINI_API_KEY")

credentials = service_account.Credentials.from_service_account_file(
    PROJECT_CREDENTIALS_LOCAL
)

genai.configure(api_key=CHAVE_API_GOOGLE)

vertexai.init(
    project=PROJECT_ID,
    location=PROJECT_REGION,
    credentials=credentials
)

model = GenerativeModel(GEMINI_MODELO_20_FLASH)

model_20_flash = genai.get_model(f"models/{GEMINI_MODELO_20_FLASH}")
limite_modelo_20_flash = {
    "tokens_entrada" : model_20_flash.input_token_limit,
    "tokens_saida" : model_20_flash.output_token_limit
}

print(f"Limites do modelo flash 2.0 são: {limite_modelo_20_flash}")

llm_20_flash = genai.GenerativeModel(
    f"models/{GEMINI_MODELO_20_FLASH}"
)

prompt = """
--COLOQUE AQUI O SEU PROMPT--
"""

quantidade_tokens = llm_20_flash.count_tokens(prompt)
print(f"A quantidade de tokens é: {quantidade_tokens}")

resposta = model.generate_content(prompt)
tokens_prompt = resposta.usage_metadata.prompt_token_count
tokens_resposta = resposta.usage_metadata.candidates_token_count

custo_total = (tokens_prompt * CUSTO_ENTRADA_20_FLASH) / 1000000 + (tokens_resposta * CUSTO_SAIDA_20_FLASH) / 1000000
print("Custo total U$ Modelo 2.0 Flash: ", custo_total)
