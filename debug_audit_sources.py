import json

import yaml

import monitor

sources = yaml.safe_load(open("sources.yml", encoding="utf-8"))["sources"]

for source in sources:
    slug, url = source["slug"], source["url"]
    print(f"===== {slug} =====")
    print(url)

    # contagem via scraping de HTML (o que o monitor.py realmente usa hoje)
    try:
        html = monitor.fetch(url)
        html_items = monitor.extract_items(html, url)
    except Exception as exc:  # noqa: BLE001
        html_items = None
        print("  ERRO ao buscar/extrair HTML:", exc)
    if html_items is not None:
        print(f"  HTML: {len(html_items)} item(ns) extraído(s) pelo monitor.py")

    # contagem via API @search (sem filtro de tipo), só para auditoria
    api_url = monitor.derive_api_search_url(url)
    if not api_url:
        print("  (sem URL de API derivável)")
        print()
        continue
    try:
        resp = monitor.SESSION.get(
            api_url,
            headers={**monitor.HEADERS, "Accept": "application/json"},
            params={"b_size": 300},
            timeout=monitor.REQUEST_TIMEOUT,
        )
        resp.raise_for_status()
        data = resp.json()
    except Exception as exc:  # noqa: BLE001
        print("  ERRO ao consultar @search:", exc)
        print()
        continue

    items_total = data.get("items_total")
    items = data.get("items", [])
    tipos = {}
    for it in items:
        tipos[it.get("@type")] = tipos.get(it.get("@type"), 0) + 1
    print(f"  API @search: items_total={items_total}, nesta página={len(items)}")
    print(f"  tipos nesta página: {tipos}")
    print()
