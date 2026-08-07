# monitoramento-anpd

Monitoramento automático da [Central de Conteúdos da ANPD](https://www.gov.br/anpd/pt-br/centrais-de-conteudo).
Todo dia, um workflow do GitHub Actions verifica as páginas configuradas,
compara com o conteúdo já visto anteriormente e **abre uma Issue neste
repositório** listando o que é novo — título e link de cada item. Todo o
conteúdo já visto fica organizado em **[INDEX.md](INDEX.md)**, por categoria,
com nome, link, data de publicação e uma breve descrição.

## Como funciona

1. `monitor.py` baixa cada página listada em [`sources.yml`](sources.yml) e
   extrai os itens de conteúdo (título, link, data e descrição, quando
   disponíveis na página).
2. O resultado é comparado com o estado salvo em `state/<slug>.json`
   (um arquivo por fonte, versionado no repositório).
3. Itens que não estavam no estado anterior são "novos". Nesse caso:
   - o arquivo de estado é atualizado e commitado de volta no repositório;
   - uma Issue é aberta com o título e o link de cada item novo, agrupados
     por fonte;
   - [`INDEX.md`](INDEX.md) é regenerado a partir do estado atualizado, para
     refletir o novo conteúdo.
4. Na primeira execução de uma fonte não existe estado ainda, então o
   conteúdo atual vira a "linha de base" (nenhuma Issue é aberta — do
   contrário todo o histórico existente apareceria como "novo"), mas ele já
   entra no índice normalmente.
5. Se uma página parar de retornar itens (ex.: o layout do site mudou e o
   scraper não reconhece mais a listagem), isso também vira um alerta em
   forma de Issue, em vez de falhar silenciosamente.

O `INDEX.md` é regenerado a cada execução do workflow (não só quando há
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

## Adicionar novas páginas para monitorar

Para monitorar uma nova página da central de conteúdos, edite
[`sources.yml`](sources.yml) e adicione um item:

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
pip install -r requirements.txt
python monitor.py            # roda, atualiza state/*.json e regenera INDEX.md
python monitor.py --dry-run  # roda sem gravar estado nem regenerar o índice
python generate_index.py     # regenera só o INDEX.md a partir do state/ atual
```

Se houver conteúdo novo (ou algum erro), o script gera `report.md` na raiz
do projeto com o conteúdo que seria publicado na Issue.

## Sobre o scraper

As páginas da ANPD são construídas em Plone/gov.br, cujo HTML de listagem
pode variar entre seções. `monitor.py` tenta, em ordem:

1. Seletores conhecidos de listagem do Plone (`tileItem`, `listing-item`
   etc.);
2. Um fallback genérico que varre os links dentro da área principal de
   conteúdo (ignorando menu, cabeçalho e rodapé) e filtra links de
   navegação/boilerplate comuns em sites gov.br.

Se uma fonte passar a gerar o alerta "nenhum item encontrado", é sinal de
que o layout mudou e os seletores em `monitor.py` (`ITEM_SELECTORS`,
`CONTENT_CONTAINER_SELECTORS`) precisam de ajuste — nesse caso, inspecione
o HTML atual da página e atualize os seletores de acordo.
