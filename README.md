# Módulo Routes: 
    Responsável por organizar as rotas relacionadas a uma mesma entidade em um mesmo arquivo.
# Módulo Models: 
    Responsável pela definição das entidades do sistema, e de entidades relacionadas a elas tais como suas DTOs.
# Módulo Templates:
    Responsável por organizar os templates htmls utilizados para exibição nas rotas. Contem o template base.html e os templates separados por rotas.
# Módulo Database:
    Responsável por organizar os arquivos de bancos de dados.
# Main:
    Arquivo principal do projeto, responsável pela inicialização do servidor, onde existe o código responsável por configurar a instância da FastAPI, além de instânciar algumas rotas básicas e incluir rotas no projeto.
    Para inicializar o projeto é só executar esse arquivo main.py pelo visual studio code ou usar o comando **python .\main.py **
# Modulo de Scripts:
    Contém o script de dump inicial dos dados. É necessário instalar o mongodb no servidor/computador
    Configure um arquivo .env com a variável **DATABASE_URL** com o caminho do seu mongodb exemplo: **DATABASE_URL=mongodb://localhost:27017/Clinica-API** 
    Na pasta eventos-api (raiz do projeto), execute o comando **python -m scripts.seed**
# Módulo Tests:
    Responsável por organizar os arquivos de tests.
    Na pasta eventos-api (raiz do projeto), execute o comando **pytest -v**