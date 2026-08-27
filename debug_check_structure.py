import monitor

URLS = [
    "https://www.gov.br/anpd/pt-br/centrais-de-conteudo/documentos-tecnicos-orientativos",
    "https://www.gov.br/anpd/pt-br/centrais-de-conteudo/materiais-educativos-e-publicacoes",
]

for url in URLS:
    print(f"===== {url} =====")
    html = monitor.fetch(url)
    soup = monitor.BeautifulSoup(html, "lxml")
    container = monitor.pick_container(soup)

    print("qual container foi escolhido:", container.name, container.get("id"), container.get("class"))
    print("numero de <table>:", len(container.select("table")))
    print("numero de <a href>:", len(container.select("a[href]")))
    print("numero de headings h2/h3:", len(container.select("h2, h3")))
    for h in container.select("h2, h3")[:20]:
        print("  heading:", h.get_text(" ", strip=True))

    # classes comuns de card/listing block do Volto
    for cls in [".ui.card", ".listing-item", ".tileItem", ".card", ".ui.cards",
                "[class*=card]", "[class*=Card]", "[class*=listing]"]:
        n = len(container.select(cls))
        if n:
            print(f"  seletor '{cls}': {n} elemento(s)")

    items = monitor.extract_items(html, url)
    print("itens extraidos por extract_items:", len(items))
    for it in items[:5]:
        print("  -", it["title"][:70], "|", it["url"])
    print()
