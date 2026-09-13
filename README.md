# monitoramento-anpd

Monitoramento automático da [Central de Conteúdos da ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo).
Todo dia, um workflow do GitHub Actions verifica as páginas configuradas,
compara com o conteúdo já visto anteriormente e **abre uma Issue neste
repositório** listando o que é novo — título e link de cada item. Todo o
conteúdo já visto fica organizado em
**[Monitoramento ANPD/INDEX.md](Monitoramento%20ANPD/INDEX.md)**, por
categoria, com nome, link, data de publicação e uma breve descrição.

Todos os arquivos do script de monitoramento (o que existia neste
repositório antes de ele ganhar o site Hugo) ficam em
[`Monitoramento ANPD/`](Monitoramento%20ANPD/) — o site (tema, conteúdo,
configuração do Hugo) ocupa a raiz do repositório.

## Como funciona

1. `Monitoramento ANPD/monitor.py` baixa cada página listada em
   [`Monitoramento ANPD/sources.yml`](Monitoramento%20ANPD/sources.yml) e
   extrai os itens de conteúdo (título, link, data e descrição, quando
   disponíveis na página).
2. O resultado é comparado com o estado salvo em
   `Monitoramento ANPD/state/<slug>.json` (um arquivo por fonte,
   versionado no repositório).
3. Itens que não estavam no estado anterior são "novos". Nesse caso:
   - o arquivo de estado é atualizado e commitado de volta no repositório;
   - uma Issue é aberta com o título e o link de cada item novo, agrupados
     por fonte;
   - [`INDEX.md`](Monitoramento%20ANPD/INDEX.md) é regenerado a partir do
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

O `Monitoramento ANPD/INDEX.md` é regenerado a cada execução do workflow (não só quando há
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
[`Monitoramento ANPD/sources.yml`](Monitoramento%20ANPD/sources.yml) e
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
cd "Monitoramento ANPD"
pip install -r requirements.txt
python monitor.py            # roda, atualiza state/*.json e regenera INDEX.md
python monitor.py --dry-run  # roda sem gravar estado nem regenerar o índice
python generate_index.py     # regenera só o INDEX.md a partir do state/ atual
```

Se houver conteúdo novo (ou algum erro), o script gera
`Monitoramento ANPD/report.md` com o conteúdo que seria publicado na
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
`Monitoramento ANPD/sources.yml`). Cada categoria é um *leaf bundle*
(`index.md`, sem underscore) e não uma seção (`_index.md`, que teria
isso) — o layout `docs/list.html` do tema, usado para páginas de seção,
só lista subpáginas e ignora o corpo markdown, então qualquer categoria
sem subpáginas ficaria com o conteúdo invisível se fosse `_index.md`.
Como *leaf bundle*, a página usa `docs/single.html`, que renderiza o
conteúdo normalmente, e continua aparecendo do mesmo jeito na barra
lateral e nos cartões automáticos de `content/docs/_index.md` (a
página de entrada — essa sim uma seção de verdade, já que tem as 8
categorias como subpáginas —, cujo corpo também não é renderizado pelo
mesmo motivo: o resumo mostrado ali vem do front matter `description`,
não do corpo). São cópias estáticas do estado de quando foram geradas —
não sincronizadas automaticamente com
`Monitoramento ANPD/state/*.json`/`Monitoramento ANPD/INDEX.md` a cada
execução do monitor.

`content/docs/noticias/index.md` tem um formato à parte: em vez da
tabela markdown simples (Publicação/Data/Descrição), usa uma lista de
cards em HTML com **palavras-chave** (tags de tema — LGPD, IA, ECA
Digital, Sanção etc.) e **resumo** (uma frase para o leitor decidir se
quer abrir a notícia), mais uma barra lateral de tags com filtro em
JavaScript puro (sem dependência externa) — a cor de destaque da tag
ativa usa `var(--bs-primary)`, a variável real que o Bootstrap expõe em
tempo de execução. Tags e resumos são autorados manualmente por item —
ao adicionar uma notícia nova a essa página, inclua `data-tags` com os
temas relevantes e um resumo curto seguindo o mesmo padrão.

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

## Sobre o scraper

As páginas da ANPD são construídas em Plone/Volto, cujo HTML de listagem
pode variar entre seções. `Monitoramento ANPD/monitor.py` tenta, em ordem:

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
