---
title: ANPD Hub
layout: hextra-home
---

<div class="mt-6 mb-6">
{{< hextra/hero-badge link="blog" >}}
  <span>🎉 Novidade: o site foi ao ar</span>
  {{< icon name="arrow-circle-right" attributes="height=14" >}}
{{< /hextra/hero-badge >}}
</div>

{{< hextra/hero-headline >}}
  ANPD Hub
{{< /hextra/hero-headline >}}

<div class="mt-6 mb-6">
{{< hextra/hero-subtitle >}}
  Acompanhamento automático das publicações oficiais da Autoridade Nacional
  de Proteção de Dados — sem precisar ficar checando o site manualmente.
{{< /hextra/hero-subtitle >}}
</div>

<div class="mt-6 mb-12">
{{< hextra/hero-button text="Ver índice" link="docs" >}}
</div>

{{< hextra/feature-grid >}}
  {{< hextra/feature-card
    title="199 publicações"
    subtitle="Em 8 categorias monitoradas, de resoluções e portarias a decisões sancionadoras e notícias."
    link="docs"
    icon="document-text"
  >}}
  {{< hextra/feature-card
    title="Monitoramento contínuo"
    subtitle="Um workflow diário verifica as páginas oficiais da ANPD e registra qualquer publicação nova assim que ela aparece."
    icon="refresh"
  >}}
  {{< hextra/feature-card
    title="Sem duplicidade"
    subtitle="O estado de cada fonte é comparado a cada execução, evitando alertas repetidos para o mesmo conteúdo."
    icon="badge-check"
  >}}
  {{< hextra/feature-card
    title="Novidades no blog"
    subtitle="Atualizações e mudanças no próprio ANPD Hub são registradas na seção de blog."
    link="blog"
    icon="newspaper"
  >}}
  {{< hextra/feature-card
    title="Código aberto"
    subtitle="Todo o monitoramento é feito por um script Python simples, disponível no repositório no GitHub."
    link="https://github.com/rcapitao/anpd-hub"
    icon="github"
  >}}
  {{< hextra/feature-card
    title="Fontes oficiais"
    subtitle="Todo o conteúdo vem direto das páginas da ANPD em gov.br — nenhum dado é inventado ou resumido por IA."
    icon="shield-check"
  >}}
{{< /hextra/feature-grid >}}

## Categorias monitoradas

{{< cards cols="4" >}}
  {{< card link="docs/atos-normativos" title="Atos Normativos (visão geral)" subtitle="1 publicação" icon="document" >}}
  {{< card link="docs/regulamentacoes-anpd" title="Regulamentações da ANPD" subtitle="17 publicações" icon="scale" >}}
  {{< card link="docs/atos-gestao-interna" title="Atos de Gestão Interna" subtitle="30 publicações" icon="office-building" >}}
  {{< card link="docs/decisoes-processos-sancionadores" title="Decisões Sancionadoras" subtitle="13 publicações" icon="shield-check" >}}
  {{< card link="docs/documentos-tecnicos-orientativos" title="Documentos Técnicos e Orientativos" subtitle="55 publicações" icon="document-text" >}}
  {{< card link="docs/materiais-educativos-publicacoes" title="Materiais Educativos" subtitle="12 publicações" icon="academic-cap" >}}
  {{< card link="docs/outros-documentos-publicacoes" title="Outros Documentos" subtitle="31 publicações" icon="archive" >}}
  {{< card link="docs/noticias" title="Notícias da ANPD" subtitle="40 publicações" icon="newspaper" >}}
{{< /cards >}}
