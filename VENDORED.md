# Origem do tema (Lotus Docs)

O site é baseado no tema [Lotus Docs](https://github.com/colinwilson/lotusdocs),
mas seus arquivos não vivem mais em `themes/lotusdocs/` — foram
incorporados diretamente na raiz do repositório (`assets/`, `layouts/`,
`static/`, `i18n/`, `archetypes/`), junto com o conteúdo próprio do ANPD
Hub. Não há mais `theme = "..."` em `hugo.toml`: o Hugo usa esses
diretórios diretamente, sem nenhuma camada de tema por cima. O `LICENSE`
na raiz é o do Lotus Docs (MIT), preservado por cobrir boa parte do
código em `assets/` e `layouts/`.

- **Lotus Docs**: `colinwilson/lotusdocs` commit `3d1639d13e4a4dd26e1311e9de90ad541b1048a4`
  (branch padrão, 2026-06-02).

## Dependências de Hugo Modules mescladas fisicamente

O `config.toml` original do tema declarava um único import de módulo,
`github.com/gohugoio/hugo-mod-bootstrap-scss/v5` — que por sua vez importa
mais dois módulos. Como este repositório não usa Hugo Modules, cada um
desses módulos foi copiado fisicamente para dentro de `assets/`, nos
mesmos caminhos em que o Hugo Modules os "montaria"
(`module.mounts`/`module.imports.mounts` de cada um):

- **`github.com/gohugoio/hugo-mod-bootstrap-scss/v5`**
  commit `65c073a5941a7c76d90ad4d67bf152cad50abd1c` (2026-03-01) —
  `assets/scss/bootstrap/_vendor/_rfs.scss` (o patch do próprio módulo)
  → copiado para `assets/scss/bootstrap/vendor/_rfs.scss`, sobrescrevendo
  o arquivo equivalente do Bootstrap puro (workaround documentado no
  próprio módulo para https://github.com/gohugoio/hugo/issues/6945).
- **`github.com/twbs/bootstrap`** tag `v5.3.2`
  commit `344e912d04b5b6a04482113eff20ab416ff01048` — `scss/` copiado
  para `assets/scss/bootstrap/`, `js/` copiado para `assets/js/bootstrap/`.
- **`github.com/gohugoio/hugo-mod-jslibs-dist/popperjs/v2`**
  commit `ee5a18bea6e41a065050a9a6fc0252e29d28a1d6` (2026-06-05) —
  `package/dist/cjs/popper.js` copiado para `assets/@popperjs/core.js`.

O `config.toml` do próprio tema (que declarava o `[[module.imports]]`
acima) não foi trazido para a raiz — não tem mais função nenhuma sem o
conceito de tema, já que `hugo.toml` na raiz já é toda a configuração do
site. Os demais arquivos de metadados do repositório do tema
(`theme.toml`, `README.md`, `SECURITY.md`, `CODE_OF_CONDUCT.md`, `go.mod`)
também não foram trazidos, pelo mesmo motivo.

`layouts/partials/docs/top-header.html` é a única página do tema com uma
mudança nossa: o seletor de idioma virou um ícone (globo), posicionado
entre o ícone do GitHub e o de modo escuro, em vez de um botão de texto
("PT-BR") em outra posição.

## Como atualizar para uma versão mais nova

1. Baixe a nova versão de `colinwilson/lotusdocs` (clone ou tarball da
   release).
2. Compare `assets/`, `layouts/`, `static/`, `i18n/` e `archetypes/`
   deste repositório com os da nova versão do tema, arquivo por arquivo
   — copiando por cima os que só têm mudanças do upstream e revisando
   manualmente os que este repositório também modificou (hoje, só
   `layouts/partials/docs/top-header.html`) e os merges de
   `assets/scss/bootstrap/`, `assets/js/bootstrap/` e `assets/@popperjs/`
   (não fazem parte do repositório do tema — veja acima).
3. Confira se as versões de `hugo-mod-bootstrap-scss`/`twbs/bootstrap`/
   `popperjs` mudaram no `exampleSite/go.sum` da nova versão do tema —
   se sim, repita a mesclagem física dessas dependências com as novas
   versões.
4. Rode `hugo --gc --minify` e confira o site localmente antes de
   publicar.
