# Cardapio Digital (Flask)

Aplicacao web para cardapio digital com:
- pagina publica por categorias
- painel administrativo com login
- cadastro, edicao e exclusao de itens
- suporte a imagens locais em `repositorio/`

## Requisitos
- Python 3.10+

## Instalação
1. Crie e ative um ambiente virtual.
2. Instale as dependencias:

```bash
pip install -r requirements.txt
```

## Configuração
1. Crie um arquivo `.env` baseado em `.env.example`.
2. Defina, no minimo:
- `SECRET_KEY`
- `ADMIN_PASSWORD`

Exemplo de `.env`:

```env
SECRET_KEY=sua-chave-forte
ADMIN_PASSWORD=sua-senha-forte
FLASK_DEBUG=0
```

## Executar localmente
```bash
python app.py
```

Aplicacao: `http://127.0.0.1:5000`

## Estrutura principal
- `app.py`: aplicacao Flask e rotas
- `templates/`: paginas HTML
- `static/`: CSS e JavaScript
- `data/`: dados do cardapio e categorias
- `repositorio/`: midias (imagens/video)

## Publicar no GitHub
```bash
git init
git add .
git commit -m "feat: estrutura inicial do cardapio"
git branch -M main
git remote add origin <URL_DO_SEU_REPOSITORIO>
git push -u origin main
```

## Observações
- O arquivo `repositorio/video.mp4` foi ignorado no `.gitignore` por poder ser grande.
- Se quiser versionar esse video, remova essa linha do `.gitignore`.
