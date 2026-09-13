# monitoramento-anpd

Monitoramento automático da [Central de Conteúdos da ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo).
Todo dia, um workflow do GitHub Actions verifica as páginas configuradas,
compara com o conteúdo já visto anteriormente e **abre uma Issue neste
repositório** listando o que é novo — título e link de cada item. Todo o
conteúdo já visto fica organizado em
**[monitoramento-ANPD/INDEX.md](monitoramento-ANPD/INDEX.md)**, por
categoria, com nome, link, data de publicação e uma breve descrição.

Todos os arquivos do script de monitoramento (o que existia neste
repositório antes de ele ganhar o site Hugo) ficam em
[`monitoramento-ANPD/`](monitoramento-ANPD/) — o site (tema, conteúdo,
configuração do Hugo) ocupa a raiz do repositório.

## Como funciona

1. `monitoramento-ANPD/monitor.py` baixa cada página listada em
   [`monitoramento-ANPD/sources.yml`](monitoramento-ANPD/sources.yml) e
   extrai os itens de conteúdo (título, link, data e descrição, quando
   disponíveis na página).
2. O resultado é comparado com o estado salvo em
   `monitoramento-ANPD/state/<slug>.json` (um arquivo por fonte,
   versionado no repositório).
3. Itens que não estavam no estado anterior são "novos". Nesse caso:
   - o arquivo de estado é atualizado e commitado de volta no repositório;
   - uma Issue é aberta com o título e o link de cada item novo, agrupados
     por fonte;
   - [`INDEX.md`](monitoramento-ANPD/INDEX.md) é regenerado a partir do
     estado atualizado, para refletir o novo conteúdo.
   - Antes de considerar um item "novo", o monitor verifica se ele não é na
     verdade um documento já conhecido que só mudou de URL (ex.: de
     `in.gov.br` para uma página própria do `gov.br`) — nesse caso, só
     atualiza a URL guardada, sem notificar. Essa verificação só reconcilia
     quando a URL antiga realmente sumiu da página; documentos diferentes
     que por acaso têm o mesmo texto de link (comum em versões "em inglês"/
     "em espanhol" de uma mesma resolução) continuam sendo tratados como
     itens distintos, mesmo com título idêntico.
4. Na primeira execução de uma fonte não existe estado ainda, então o
   conteúdo atual vira a "linha de base" (nenhuma Issue é aberta — do
   contrário todo o histórico existente apareceria como "novo"), mas ele já
   entra no índice normalmente.
5. Se uma página parar de retornar itens (ex.: o layout do site mudou e o
   scraper não reconhece mais a listagem), isso também vira um alerta em
   forma de Issue, em vez de falhar silenciosamente.

O `monitoramento-ANPD/INDEX.md` é regenerado a cada execução do workflow (não só quando há
conteúdo novo), então ele nunca fica desatualizado em relação ao estado.

O workflow roda em `.github/workflows/monitor.yml`, agendado para
**09:00 (horário de Brasília)** todos os dias, e também pode ser disparado
manualmente pela aba *Actions* do GitHub (`workflow_dispatch`).

## Fontes monitoradas

- [Atos Normativos da ANPD (visão geral)](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos)
- [Regulamentações da ANPD](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd)
- [Atos de Gestão Interna](https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/atos_gestao_interna)
- [Decisões em Processos Sancionadores](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/decisoes-em-processos-sancionadores/)
- [Documentos Técnicos e Orientativos](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos)
- [Materiais Educativos e Publicações](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes)
- [Outros Documentos e Publicações Institucionais](https://www.gov.br/anpd/pt-br/centrais-de-conteudo/outros-documentos-e-publicacoes-institucionais)
- [Notícias da ANPD](https://www.gov.br/anpd/pt-br/assuntos/noticias)

## Adicionar novas páginas para monitorar

Para monitorar uma nova página da central de conteúdos, edite
[`monitoramento-ANPD/sources.yml`](monitoramento-ANPD/sources.yml) e
adicione um item:

```yaml
sources:
  - name: "Nome amigável (aparece na Issue)"
    slug: "identificador-unico"
    url: "https://www.gov.br/anpd/pt-br/..."
```

Na próxima execução, essa fonte passa pela mesma lógica de linha de base
descrita acima.

## Rodando localmente

```bash
cd "monitoramento-ANPD"
pip install -r requirements.txt
python monitor.py            # roda, atualiza state/*.json e regenera INDEX.md
python monitor.py --dry-run  # roda sem gravar estado nem regenerar o índice
python generate_index.py     # regenera só o INDEX.md a partir do state/ atual
```

Se houver conteúdo novo (ou algum erro), o script gera
`monitoramento-ANPD/report.md` com o conteúdo que seria publicado na
Issue.

## Site (Hugo + Lotus Docs)

O repositório também tem um site [Hugo](https://gohugo.io/) baseado no
tema [Lotus Docs](https://github.com/colinwilson/lotusdocs), configurado
em `hugo.toml`. Diferente das trocas de tema anteriores, o Lotus Docs
não fica num diretório `themes/<nome>/` à parte — seus arquivos
(`assets/`, `layouts/`, `static/`, `i18n/`, `archetypes/`) foram
incorporados diretamente na raiz do repositório, lado a lado com o
conteúdo próprio do ANPD Hub, sem nenhum `theme = "..."` em `hugo.toml`.
O tema é baseado em Bootstrap 5 e, no upstream, depende de outros três
módulos Hugo (`hugo-mod-bootstrap-scss`, que por sua vez importa
`github.com/twbs/bootstrap` e o popperjs) — como este repositório não
usa Hugo Modules, todos esses módulos foram mesclados fisicamente em
`assets/`, nos mesmos caminhos em que o Hugo Modules os montaria. Veja
`VENDORED.md` para os detalhes de origem, versão e de como atualizar; o
`LICENSE` na raiz é o do Lotus Docs (MIT), preservado por cobrir esse
código. (O site já passou pelo Hextra e pelo OINK antes — veja o
histórico de posts do blog — mantendo sempre o mesmo estilo de homepage.)

Busca (FlexSearch), realce de código (Prism), diagramas (Mermaid) e
fórmulas (KaTeX) já vêm vendorizados pelo próprio tema — nenhum desses
recursos depende de CDN externo para funcionar.

```bash
hugo server   # roda o site localmente em http://localhost:1313
hugo          # gera o build estático em public/
```

A homepage (`content/_index.md`) usa o sistema de landing page do tema:
o conteúdo em si mora em `data/landing.yaml` (blocos `hero`, `stats`,
`featureGrid`, ordenados por `weight`). O bloco `stats` (a faixa com os
4 números em destaque) não existe no Lotus Docs — foi adicionado em
`layouts/partials/landing/stats.html`, seguindo o mesmo padrão dos
blocos nativos do tema.

O conteúdo de `content/docs/` é dividido em uma página por categoria
(`content/docs/<slug>/index.md`, um `<slug>` por fonte de
`monitoramento-ANPD/sources.yml`). A maioria das categorias é um *leaf
bundle* (`index.md`, sem underscore) e não uma seção (`_index.md`), já
que não tem subpáginas. A exceção é **Atos Normativos**
(`content/docs/atos-normativos/_index.md`), que é uma seção de verdade
com duas subcategorias aninhadas por baixo —
`atos-normativos/regulamentacoes-anpd/` e
`atos-normativos/atos-gestao-interna/` (cada uma continua sendo seu
próprio *leaf bundle*, só que agora um nível mais fundo). O layout
`docs/list.html` do tema, usado por todas as páginas de seção, antes só
listava subpáginas e ignorava o corpo markdown da própria seção — foi
ajustado (`{{ with .Content }}`) para renderizar também o corpo antes
dos cartões, já que a página de Atos Normativos precisa mostrar seu
próprio conteúdo (a antiga "visão geral") **e** os cartões das duas
subcategorias. Categorias sem subpáginas continuam como *leaf bundle*
e usam `docs/single.html`, que só renderiza o conteúdo normalmente.
Tanto os *leaf bundles* quanto as seções aparecem na barra lateral e
nos cartões automáticos de `content/docs/_index.md` (a página de
entrada — essa sim uma seção de verdade, já que tem as categorias como
subpáginas —, cujo corpo também não é renderizado pelo mesmo motivo: o
resumo mostrado ali vem do front matter `description`, não do corpo).
São cópias estáticas do estado de quando foram geradas — não
sincronizadas automaticamente com
`monitoramento-ANPD/state/*.json`/`monitoramento-ANPD/INDEX.md` a cada
execução do monitor.

As duas subcategorias de Atos Normativos (Regulamentações da ANPD e
Atos de Gestão Interna) são, por sua vez, seções com subpáginas
próprias — um terceiro nível de aninhamento, dividido por tipo de ato:
`atos-normativos/regulamentacoes-anpd/{resolucoes,portarias,enunciados}/`
e `atos-normativos/atos-gestao-interna/{resolucoes,portarias}/`. Cada
subpágina é um *leaf bundle* com sua própria tabela `Publicação | Data
| Descrição | Status Atual`; a página mãe de cada uma
(`regulamentacoes-anpd/_index.md`, `atos-gestao-interna/_index.md`) é
só a introdução + Fonte, sem tabela — os cartões das subpáginas vêm do
`docs/list.html` de sempre. Essa divisão por tipo de ato (e a coluna
"Status Atual" separada da Descrição) espelha a estrutura das páginas
oficiais da ANPD; o campo `description` do `monitor.py` concatena
ementa e status numa string só ("... (Status: Vigente)"), então o
status foi extraído manualmente para essas tabelas — uma nova execução
do monitor não vai repopular esse split automaticamente (o texto de
`description` nos arquivos de estado continua com ementa+status juntos
como antes). Como essas subpáginas são uma seção dentro de outra seção
dentro de Atos Normativos, a barra lateral já lida com esse terceiro
nível de dropdown aninhado sem precisar de nenhum ajuste em
`layouts/partials/docs/sidebar.html` — o partial já era recursivo o
suficiente.

`content/docs/noticias/` é uma exceção às outras categorias: em vez de
uma única página por categoria, cada notícia é uma página própria
(`content/docs/noticias/<slug>.md`) — **não republica o conteúdo da
notícia**, só o **resumo** (front matter `description`) e o **link**
para a página oficial (front matter `source_url`, também linkado no
corpo como "Fonte:"). Isso existe para que cada notícia tenha uma URL
estável e apareça como um item próprio no feed RSS da seção
(`/docs/noticias/index.xml`) — pensando numa futura configuração de
alertas por e-mail ou RSS por notícia nova, e não só por categoria.

`content/docs/noticias/_index.md` é a página de listagem (front matter
`layout: "noticias-list"`, que aponta para
`layouts/docs/noticias-list.html`) — igual às outras categorias, ela só
lista as subpáginas, mas com um layout próprio: cards ordenados por
data (mais recente primeiro), com **palavras-chave** (front matter
`tags`) e resumo, mais uma barra lateral de tags com filtro em
JavaScript puro (sem dependência externa) — a cor de destaque da tag
ativa usa `var(--bs-primary)`, a variável real que o Bootstrap expõe em
tempo de execução. `layouts/docs/noticias-list.rss.xml` customiza o
RSS dessa seção para usar o resumo de cada notícia na descrição do
item, em vez do conteúdo renderizado da página (que é só "Fonte:
<link>"). Como notícias têm subpáginas de verdade (ao contrário das
outras categorias), `sidebar_flat: true` no front matter da seção evita
que a barra lateral tente listar as 40 notícias como um dropdown
aninhado — veja o guard correspondente em
`layouts/partials/docs/sidebar.html`.

Para adicionar uma notícia nova, crie um arquivo
`content/docs/noticias/<slug>.md` com `title`, `date`, `tags` (lista),
`description` (o resumo) e `source_url` (link da página oficial) no
front matter, seguindo o padrão dos arquivos existentes.

`content/blog/` é uma seção separada, para registrar atualizações e
novidades do próprio site (não é conteúdo da ANPD) — cada post é um
arquivo em `content/blog/<slug>.md`. O Lotus Docs não tem um layout de
blog nativo, então `layouts/blog/list.html` e `layouts/blog/single.html`
foram criados para essa seção, com marcação Bootstrap simples.

O modo escuro do tema é específico das páginas de `/docs/` (o CSS de
`[data-dark-mode]` só existe em `assets/docs/scss/`) — a homepage e o
`/blog/` não têm alternância de tema.

### Idiomas (i18n)

O site é multilíngue: português do Brasil (`pt-br`) é o idioma padrão,
servido na raiz (sem prefixo `/pt-br/`); inglês (`en`) e espanhol (`es`)
já estão configurados em `hugo.toml` (`[languages]`), com um seletor de
idioma (ícone de globo, ao lado do modo escuro) nas páginas de `/docs/`,
mas **sem conteúdo traduzido ainda** — hoje só existem `content/*.md`
sem sufixo de idioma, então só o pt-br tem conteúdo de verdade em
`/en/` e `/es/`. Para traduzir uma página, crie a versão com sufixo do
idioma ao lado da original (ex.: `content/_index.en.md`,
`content/_index.es.md`).

Além do conteúdo, o tema também traduz sua própria interface (busca,
"Editar esta página", rodapé, página 404 etc.) via arquivos em
`i18n/<código-do-idioma>.toml` — o Hugo casa esse arquivo pelo código
exato do idioma declarado em `[languages]`. O tema (Lotus Docs) veio
só com `i18n/en.toml`, `pt.toml`, `de.toml` e `fr.toml`; como o site
declara o idioma como `pt-br` (não `pt`), o Hugo não casava esse
arquivo, e toda a interface caía no fallback em inglês mesmo com
pt-br como idioma padrão. Criado `i18n/pt-br.toml` com todas as
chaves traduzidas para português do Brasil (algumas reescritas a
partir do `pt.toml`, que estava em português de Portugal — ex.:
"Ativar o modo de luz" → "Ativar modo claro", "Submeter" → "Enviar").
Também havia strings de interface sem chave de i18n nenhuma,
direto em inglês nos templates (página 404, "Table of Contents",
"Edit this page", "Last updated", o badge "DRAFT", o tooltip
"Directory" e vários `aria-label`) — foram convertidas para usar
`i18n`, com chaves novas adicionadas tanto em `pt-br.toml` quanto em
`en.toml` (mantendo o texto em inglês como estava, para não regredir
se `/en/` ganhar conteúdo de verdade no futuro).

## Sobre o scraper

As páginas da ANPD são construídas em Plone/Volto, cujo HTML de listagem
pode variar entre seções. `monitoramento-ANPD/monitor.py` tenta, em ordem:

1. Seletores conhecidos de listagem do Plone (`tileItem`, `listing-item`
   etc.);
2. Tabelas de listagem com colunas "Ato"/"Ementa"/"Status Atual" (usadas em
   Regulamentações e Atos de Gestão Interna);
3. Um fallback genérico que varre os links dentro da área principal de
   conteúdo (ignorando menu, cabeçalho e rodapé) e filtra links de
   navegação/boilerplate comuns em sites gov.br;
4. Se nenhuma das opções acima encontrar nada — típico de páginas
   renderizadas só no lado do cliente (React), como "Notícias da ANPD" — a
   API REST do Volto (`++api++/.../@search`), que devolve a listagem em
   JSON independentemente de como a página é renderizada no navegador.

Cada tentativa de busca também tem retry automático (até 3x, com espera
entre elas) para tolerar bloqueios/instabilidades intermitentes do site.

Se uma fonte passar a gerar o alerta "nenhum item encontrado" mesmo após os
quatro passos acima, é sinal de que o layout mudou de forma mais profunda e
os seletores em `monitor.py` (`ITEM_SELECTORS`, `CONTENT_CONTAINER_SELECTORS`,
`TABLE_*_HEADERS`) precisam de ajuste — nesse caso, inspecione o HTML (ou a
API `++api++`) atual da página e atualize de acordo.

Se, em vez disso, a Issue de alerta mostrar **todas** as fontes falhando com
o mesmo erro de conexão (`Network is unreachable`), não é um problema do
scraper nem do site: é o runner do GitHub Actions sem rota IPv6 tentando se
conectar em um endereço IPv6 anunciado por `www.gov.br`. `monitor.py` já
força as conexões a usar IPv4 (`urllib3_connection.allowed_gai_family`) e
tenta novamente automaticamente algumas vezes antes de desistir — se esse
alerta voltar a aparecer, é sinal de uma instabilidade de rede maior (do
lado do gov.br ou do próprio GitHub Actions), não do código.
