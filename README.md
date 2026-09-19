# Gestão de Documentos

Aplicação web simples para gestão de documentos, desenvolvida como prova técnica para o processo seletivo de Estágio Desenvolvedor Full Stack. Permite fazer upload de arquivos (PDF, JPG ou PNG) com título e descrição opcional, listar os documentos cadastrados e registrar um histórico de comentários vinculado a cada documento.

## Tecnologias utilizadas

- **Back-end:** Python + FastAPI
- **Banco de dados:** SQLite (via SQLAlchemy)
- **Front-end:** HTML5, CSS3 e JavaScript puro (sem frameworks)
- **Armazenamento de arquivos:** sistema de arquivos local do servidor

## Estrutura do projeto

```
/
├── backend/
│   ├── main.py        # rotas da API
│   ├── models.py      # modelos de dados (Documento e Comentario)
│   ├── database.py    # configuração da conexão com o SQLite
│   └── uploads/        # arquivos enviados pelos usuários
├── frontend/
│   ├── index.html      # página principal (upload e listagem)
│   ├── documento.html   # detalhes do documento e comentários
│   ├── css/
│   └── js/
├── requirements.txt
└── README.md
```

## Como executar localmente

1. Clone o repositório e entre na pasta do projeto:
   ```bash
   git clone <url-do-repositorio>
   cd PROVA-TECNICA-master
   ```

2. Crie e ative um ambiente virtual:
   ```bash
   python -m venv venv
   source venv/bin/activate   # Windows: venv\Scripts\activate
   ```

3. Instale as dependências:
   ```bash
   pip install -r requirements.txt
   ```

4. Inicie a aplicação (a partir da raiz do projeto):
   ```bash
   uvicorn backend.main:app --reload
   ```

5. Acesse no navegador:
   ```
   http://localhost:8000
   ```

O próprio back-end já serve a interface do front-end, então essa única URL dá acesso à aplicação completa (não é necessário nenhum servidor separado para os arquivos estáticos).

O banco de dados (`database.db`) e a pasta de uploads são criados automaticamente na primeira execução.

## Observações e limitações

- Conforme especificado no edital, não há controle de acesso, login ou autenticação de usuários.
- Os arquivos enviados são armazenados diretamente no disco do servidor, e os metadados (título, descrição, data) ficam no SQLite.
- Em ambiente de produção, o caminho do banco de dados e da pasta de uploads pode ser customizado através das variáveis de ambiente `DB_PATH` e `UPLOAD_DIR`, para permitir o uso de um volume persistente.

## Link do deploy

**https://prova-tecnica-production.up.railway.app/**