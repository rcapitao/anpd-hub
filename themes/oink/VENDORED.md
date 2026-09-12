# Tema vendorizado (não é submodule/link)

Este diretório contém uma cópia direta (vendorizada) do tema [OINK](https://github.com/pgsty/oink),
na versão `v1.0.0`, com os arquivos necessários para rodar o tema (`assets/`, `data/`,
`i18n/`, `layouts/`, `static/`, `LICENSE`, `theme.toml`, `go.mod`, `hugo.yaml`).
Arquivos de desenvolvimento do próprio repositório do tema (testes em `tests/`,
scripts de CI em `bin/`, JSON Schema de validação em `schema/`, imagens de
demonstração, docs, `CHANGELOG.md` etc.) foram deixados de fora por não serem
necessários para servir o site.

O `hugo.yaml` deste diretório **não é conteúdo específico do site** — é a
configuração de valores-padrão do próprio tema (`params.ui.*`, `outputFormats`
como `LLMS`/`print`, `mediaTypes` para fontes etc.), a mesma que o tema usa
para seu próprio site de demonstração. O Hugo mescla automaticamente a
configuração de um tema (via `theme:` no `hugo.yaml` do site, tanto para tema
vendorizado quanto via Hugo Module) por baixo da configuração do site — por
isso o `hugo.yaml` na raiz do repositório fica enxuto, só com o que é
identidade/conteúdo do ANPD Hub (título, idiomas, `baseURL` etc.), do mesmo
jeito que o [oink-starter](https://github.com/pgsty/oink-starter) oficial faz.

O OINK normalmente é usado via Hugo Modules (`module.imports` apontando para
`github.com/pgsty/oink`, como no [oink-starter](https://github.com/pgsty/oink-starter)
oficial). Aqui optamos por vendorizar em vez disso — uma cópia comum de
arquivos (sem `.git` e sem Hugo Modules) pode ser editada diretamente neste
repositório, sem depender de Go/`hugo mod` para resolver o tema no build.

Para atualizar para uma versão mais nova do tema no futuro, baixe o release
desejado de https://github.com/pgsty/oink/releases e substitua os diretórios
acima manualmente, revisando o `CHANGELOG.md` do tema para mudanças que
afetem customizações locais (em especial mudanças de schema em `hugo.yaml`,
convenções de `type`/`cascade` no front matter, e nomes de variáveis CSS).
