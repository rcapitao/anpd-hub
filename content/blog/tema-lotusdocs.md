---
title: "Site migrado para o tema Lotus Docs"
date: 2026-09-13
tags: ["site", "tema"]
description: "O ANPD Hub trocou de tema (Hextra → Lotus Docs), com busca offline, modo escuro, ícones Material e uma homepage em blocos configuráveis."
---

O site trocou de tema: de [Hextra](https://github.com/imfing/hextra) para
[Lotus Docs](https://github.com/colinwilson/lotusdocs), um tema Hugo baseado
em Bootstrap 5, com busca offline (FlexSearch), realce de código (Prism) e
suporte a diagramas (Mermaid) e fórmulas (KaTeX) todos vendorizados — sem
depender de nenhum serviço externo para funcionar.

O que muda para quem visita:

- **Busca offline** e navegação lateral por categoria, com ícones.
- **Modo escuro** com alternância manual.
- **Homepage em blocos configuráveis** (`data/landing.yaml`): destaque,
  números em resumo e grade de categorias — o mesmo conteúdo das versões
  anteriores, só reorganizado no novo formato do tema.

O conteúdo em si — o índice por categoria, o blog, e a página de notícias
com tags e filtro por tema — continua o mesmo; só a apresentação visual e a
estrutura de configuração do site mudaram.
