---
title: ANPD Hub
layout: hextra-home
---

<div class="mt-6 mb-6">
{{< hextra/hero-badge link="blog/anpd-hub-no-ar/" >}}
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

<div class="anpd-stats">
  <div class="anpd-stat">
    <div class="anpd-stat-icon">{{< icon name="document-text" attributes="height=28" >}}</div>
    <div class="anpd-stat-value">199</div>
    <div class="anpd-stat-label">Publicações monitoradas</div>
  </div>
  <div class="anpd-stat">
    <div class="anpd-stat-icon">{{< icon name="view-grid" attributes="height=28" >}}</div>
    <div class="anpd-stat-value">8</div>
    <div class="anpd-stat-label">Categorias acompanhadas</div>
  </div>
  <div class="anpd-stat">
    <div class="anpd-stat-icon">{{< icon name="newspaper" attributes="height=28" >}}</div>
    <div class="anpd-stat-value">40</div>
    <div class="anpd-stat-label">Notícias da ANPD</div>
  </div>
  <div class="anpd-stat">
    <div class="anpd-stat-icon">{{< icon name="refresh" attributes="height=28" >}}</div>
    <div class="anpd-stat-value">Diário</div>
    <div class="anpd-stat-label">Ciclo de verificação</div>
  </div>
</div>

<style>
.anpd-stats {
  display: grid;
  grid-template-columns: repeat(2, minmax(0, 1fr));
  gap: 1rem;
  width: 100%;
  margin: 0 0 3rem;
}
@media (min-width: 768px) {
  .anpd-stats { grid-template-columns: repeat(4, minmax(0, 1fr)); }
}
.anpd-stat {
  border: 1px solid #e5e7eb;
  border-radius: 1.5rem;
  padding: 1.5rem;
  text-align: center;
}
.dark .anpd-stat { border-color: #262626; }
.anpd-stat-icon {
  display: flex;
  justify-content: center;
  margin-bottom: 0.5rem;
  color: hsl(var(--primary-hue) var(--primary-saturation) var(--primary-lightness));
}
.anpd-stat-value { font-size: 1.875rem; line-height: 2.25rem; font-weight: 700; }
.anpd-stat-label { margin-top: 0.25rem; font-size: 0.875rem; color: #6b7280; }
.dark .anpd-stat-label { color: #9ca3af; }
</style>

## Categorias monitoradas

{{< cards cols="4" >}}
  {{< card link="docs/atos-normativos" title="Atos Normativos (visão geral)" subtitle="1 publicação" icon="document" >}}
  {{< card link="docs/regulamentacoes-anpd" title="Regulamentações da ANPD" subtitle="17 publicações" icon="scale" >}}
  {{< card link="docs/atos-gestao-interna" title="Atos de Gestão Interna" subtitle="30 publicações" icon="office-building" >}}
  {{< card link="docs/decisoes-processos-sancionadores" title="Decisões Sancionadoras" subtitle="13 publicações" icon="shield-check" >}}
  {{< card link="docs/documentos-tecnicos-orientativos" title="Documentos Técnicos e Orientativos" subtitle="55 publicações" icon="document-text" >}}
  {{< card link="docs/materiais-educativos-publicacoes" title="Materiais Educativos" subtitle="12 publicações" icon="academic-cap" >}}
  {{< card link="docs/outros-documentos-publicacoes" title="Outros Documentos" subtitle="31 publicações" icon="archive" >}}
  {{< card link="docs/noticias" title="Notícias da ANPD" subtitle="40 publicações, com tags e filtro por tema" icon="newspaper" >}}
{{< /cards >}}
