### Gemini com python

Esse projeto se conecta com a AI do Gemini via API_KEY.

No arquivo denominado (contador_token_audio.py) se localiza o calculador de audio transcrição. Você precisa preencher a pasta em ./audio com o seu audio que deseja transcrever

Variáveis de ambiente:

Para arquivo de calculo para áudio (contador_token_audio.py) será preciso preenche essas variáveis:
GEMINI_API_KEY coloque a chave da sua api do GCP
GEMINI_MODELO informe o modelo do gemini que deseja calcular o preço
PROMPT_TRANSCRICAO coloque o prompt que irá enviar junto ao arquivo de audio
CUSTO_TEXTO_ENTRADA_USD_POR_MILHAO coloque o valor em USD do modelo para texto (entrada)
CUSTO_AUDIO_ENTRADA_USD_POR_MILHAO coloque o valor em USD do modelo para audio (entrada)
CUSTO_SAIDA_USD_POR_MILHAO coloque o valor em USD do modelo para (saída)

Para arquivo de calculo de apenas texto (contador_token_texto.py) será preciso preenche essas variáveis:
GEMINI_API_KEY coloque a chave da sua api do GCP
GEMINI_MODELO informe o modelo do gemini que deseja calcular o preço
CUSTO_ENTRADA_USD_POR_MILHAO coloque o custo de entrada do modelo
CUSTO_SAIDA_USD_POR_MILHAO coloque o custo de saida do modelo
PROMPT coloque o prompt completo que você deseja calcular o preço
