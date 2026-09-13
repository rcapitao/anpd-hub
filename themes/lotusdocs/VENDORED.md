# Como este tema foi vendorizado

Este diretório é uma cópia direta dos arquivos do tema
[Lotus Docs](https://github.com/colinwilson/lotusdocs) — sem submodule e
sem Hugo Modules — para poder ser editado diretamente neste repositório.

- **Lotus Docs**: `colinwilson/lotusdocs` commit `3d1639d13e4a4dd26e1311e9de90ad541b1048a4`
  (branch padrão, 2026-06-02).

## Dependências de Hugo Modules mescladas fisicamente

O `config.toml` original do tema declara um único import de módulo,
`github.com/gohugoio/hugo-mod-bootstrap-scss/v5` — que por sua vez importa
mais dois módulos. Como não usamos Hugo Modules aqui, cada um desses
módulos foi copiado para dentro deste diretório, nos mesmos caminhos em
que o Hugo Modules os "montaria" (`module.mounts`/`module.imports.mounts`
de cada um):

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

O `themes/lotusdocs/config.toml` deste repositório teve o bloco
`[[module.imports]]` removido (não há módulo a resolver em tempo de
build — só o `[module.hugoVersion]` foi mantido).

## Como atualizar para uma versão mais nova

1. Baixe a nova versão de `colinwilson/lotusdocs` (clone ou tarball da
   release) e copie por cima deste diretório, preservando
   `themes/lotusdocs/VENDORED.md`, `themes/lotusdocs/config.toml`
   (a versão sem o import de módulo) e os arquivos de
   `assets/scss/bootstrap/`, `assets/js/bootstrap/` e `assets/@popperjs/`
   (não fazem parte do repositório do tema).
2. Confira se as versões de `hugo-mod-bootstrap-scss`/`twbs/bootstrap`/
   `popperjs` mudaram no `exampleSite/go.sum` da nova versão do tema —
   se sim, repita os passos acima com as novas versões.
3. Rode `hugo --gc --minify` e confira o site localmente antes de
   publicar.
