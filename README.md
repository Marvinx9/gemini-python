### Gemini com python

Esse projeto se conecta com a AI do Gemini via API_KEY.

No arquivo chamado (categorizador) preparo um prompt onde recebo um input contendo um produto e retorno a categoria que o produto melhor se enquadra.

O prompt do sistema serve para dar diretrizes de como a AI deve se comportar quando ela receber uma pergunta.

No arquivo main contém uma configuracao de modelo, por ela posso configurar o máximo de caracteres de saída, nível de conecção entra as palavras, tipo de retorno (texto, imagem, audio, video, etc) e muito mais.

Para executar o projeto localmente é preciso gerar uma chave de api diretamente no AI Studio e colocar no seu arquivo .env no formato:
GEMINI_API_KEY="sua-chave-api"

Por fim, para utilizar o categorizador basta inserir no terminal o produto a ser categorizado. 