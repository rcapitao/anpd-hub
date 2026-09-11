# Tema vendorizado (não é submodule/link)

Este diretório contém uma cópia direta (vendorizada) do tema [Hextra](https://github.com/imfing/hextra),
na versão `v0.12.3`, com os arquivos necessários para rodar o tema (`assets/`, `data/`, `i18n/`,
`layouts/`, `static/`, `LICENSE`, `theme.toml`, `go.mod`). Arquivos de desenvolvimento do próprio
repositório do tema (testes, CI, docs, package.json etc.) foram deixados de fora por não serem
necessários para servir o site.

Por ser uma cópia comum de arquivos (sem `.git` e sem Hugo Modules), o tema pode ser editado
diretamente aqui no repositório.

Para atualizar para uma versão mais nova do tema no futuro, baixe o release desejado de
https://github.com/imfing/hextra/releases e substitua os arquivos acima manualmente, revisando
o changelog do tema para mudanças que afetem customizações locais.
