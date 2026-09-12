---
title: "Site voltou para o tema Hextra"
date: 2026-09-12
tags: ["site", "tema"]
description: "O ANPD Hub voltou a usar o tema Hextra, mantendo o mesmo estilo de homepage (números em destaque e grade de categorias) criado durante a passagem pelo OINK."
---

O site voltou a usar o tema [Hextra](https://github.com/imfing/hextra),
revertendo a troca para o [OINK](https://github.com/pgsty/oink) registrada no
post anterior.

A homepage manteve o mesmo estilo criado nessa passagem pelo OINK — a faixa
com os números em destaque (publicações, categorias, notícias, ciclo de
verificação) logo abaixo da headline, seguida da grade de categorias
monitoradas — só recriado com os componentes do próprio Hextra
(`hextra/hero-*` e o shortcode `cards`), no lugar do sistema de landing page
baseado em `data/home/<idioma>.yaml` que era específico do OINK.

O restante do conteúdo — índice por categoria, blog e a página de notícias
com tags e filtro por tema — continua o mesmo de antes.
