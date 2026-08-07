#!/usr/bin/env python3
"""
Monitora páginas da Central de Conteúdos da ANPD (gov.br) em busca de
conteúdo novo, comparando com um estado salvo em disco (state/<slug>.json).

Uso:
    python monitor.py                # roda o monitoramento e atualiza o estado
    python monitor.py --dry-run      # roda sem gravar o estado em disco

Saídas (para consumo pelo workflow do GitHub Actions):
    - report.md         Corpo em Markdown para abrir uma Issue (só é criado
                         se houver conteúdo novo e/ou erros a reportar).
    - $GITHUB_OUTPUT     has_report=true/false, title=<título da issue>
"""
from __future__ import annotations

import argparse
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import yaml
from bs4 import BeautifulSoup

from generate_index import build_index

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / "state"
SOURCES_FILE = ROOT / "sources.yml"
REPORT_FILE = ROOT / "report.md"

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
        "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
    ),
    "Accept-Language": "pt-BR,pt;q=0.9,en;q=0.5",
}
REQUEST_TIMEOUT = 30

# Seletores CSS candidatos para o container principal de conteúdo (evita
# pegar menu, cabeçalho e rodapé, que se repetem em todas as páginas gov.br).
CONTENT_CONTAINER_SELECTORS = [
    "#content-core",
    "main#content",
    "main",
    "article",
    ".content-area",
    "#content",
    "body",
]

# Seletores candidatos para "cada item da listagem", na ordem em que serão
# tentados. Cobrem tanto o Plone clássico (tileItem) quanto variações comuns
# de temas Volto usados em sites gov.br.
ITEM_SELECTORS = [
    "div.tileItem",
    "article.tileItem",
    "div.listing-item",
    "li.listing-item",
    "div.searchResults .item",
    "ul.listing > li",
]

BOILERPLATE_TEXTS = {
    "anterior", "próxima", "proxima", "próximo", "proximo",
    "página inicial", "pagina inicial", "voltar ao topo", "imprimir",
    "compartilhar", "acessibilidade", "alto contraste", "mapa do site",
    "ouvidoria", "fale conosco", "ir para o conteúdo", "ir para o menu",
    "ir para a busca", "brasil", "governo federal", "menu principal",
    "abrir menu", "fechar menu", "pesquisar", "buscar", "assine a newsletter",
}

# Texto de link genérico (tipo "clique aqui") que não serve como título: nesse
# caso usamos o texto do parágrafo ao redor do link como título.
GENERIC_LINK_TEXTS = {
    "aqui", "clique aqui", "clicando aqui", "acesse aqui", "saiba mais",
    "leia mais", "confira aqui", "veja aqui", "veja mais", "confira",
}

DATE_RE = re.compile(r"\b\d{1,2}/\d{1,2}/\d{2,4}\b")


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip(" ​-–—:•,.")
    return re.sub(r"\s+([,.])", r"\1", text)


def fetch(url: str) -> str:
    resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


def pick_container(soup: BeautifulSoup):
    for tag in soup.select("script, style, nav, header, footer, aside"):
        tag.decompose()
    for sel in CONTENT_CONTAINER_SELECTORS:
        node = soup.select_one(sel)
        if node is not None:
            return node
    return soup


def extract_description(el, title: str):
    for sel in (".description", ".tileBody", ".documentDescription", ".subtitle", "p"):
        desc_el = el.select_one(sel)
        if desc_el is None:
            continue
        text = clean_text(desc_el.get_text(" ", strip=True))
        if text and text.lower() != title.lower():
            return text[:280]
    return None


def extract_via_item_selectors(container, base_url: str):
    for sel in ITEM_SELECTORS:
        elements = container.select(sel)
        if not elements:
            continue
        items = []
        for el in elements:
            link = el if el.name == "a" else el.select_one("a[href]")
            if link is None or not link.get("href"):
                continue
            heading = el.select_one("h1, h2, h3, h4")
            title = clean_text(heading.get_text(" ", strip=True) if heading else
                                link.get_text(" ", strip=True))
            if not title:
                continue
            url = urljoin(base_url, link["href"])
            date_match = DATE_RE.search(el.get_text(" ", strip=True))
            items.append({
                "url": url,
                "title": title,
                "date": date_match.group(0) if date_match else None,
                "description": extract_description(el, title),
            })
        if items:
            return items
    return []


def extract_via_generic_links(container, base_url: str):
    items = []
    seen = set()
    for link in container.select("a[href]"):
        href = link["href"].strip()
        if not href or href.startswith("#"):
            continue
        if href.startswith(("javascript:", "mailto:", "tel:")):
            continue
        title = clean_text(link.get_text(" ", strip=True))
        parent_text = clean_text(link.parent.get_text(" ", strip=True)) if link.parent else ""

        if title.strip(".…").lower() in GENERIC_LINK_TEXTS:
            # texto do link é genérico ("clique aqui"); usa a frase ao redor,
            # removendo a própria expressão genérica do resultado
            title = parent_text
            for phrase in sorted(GENERIC_LINK_TEXTS, key=len, reverse=True):
                title = re.sub(rf"\b{re.escape(phrase)}\b\s*\.?", "", title, flags=re.IGNORECASE)
            title = clean_text(title)

        if len(title) < 8:
            continue
        if title.strip(".…").lower() in BOILERPLATE_TEXTS:
            continue
        if title.isdigit():
            continue

        url = urljoin(base_url, href)
        if url in seen:
            continue
        seen.add(url)

        date_match = DATE_RE.search(parent_text)
        description = None
        if parent_text and parent_text.lower() != title.lower():
            remainder = clean_text(parent_text.replace(title, "", 1))
            if len(remainder) > 20:
                description = remainder[:280]

        items.append({
            "url": url,
            "title": title,
            "date": date_match.group(0) if date_match else None,
            "description": description,
        })
    return items


def extract_items(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    container = pick_container(soup)
    items = extract_via_item_selectors(container, base_url)
    if not items:
        items = extract_via_generic_links(container, base_url)
    # dedupe preservando ordem
    dedup = {}
    for item in items:
        dedup.setdefault(item["url"], item)
    return list(dedup.values())


def load_state(slug: str):
    path = STATE_DIR / f"{slug}.json"
    if not path.exists():
        return None
    return json.loads(path.read_text(encoding="utf-8"))


def save_state(slug: str, state: dict) -> None:
    STATE_DIR.mkdir(parents=True, exist_ok=True)
    path = STATE_DIR / f"{slug}.json"
    path.write_text(json.dumps(state, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                     encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--dry-run", action="store_true",
                         help="não grava o estado atualizado em disco")
    args = parser.parse_args()

    sources = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))["sources"]

    now_iso = datetime.now(timezone.utc).isoformat()
    new_by_source = []   # [(source, [items])]
    baselined = []       # sources com estado criado agora pela primeira vez
    errors = []          # (source, mensagem)

    for source in sources:
        name, slug, url = source["name"], source["slug"], source["url"]
        log(f"[{slug}] buscando {url}")
        try:
            html = fetch(url)
        except requests.RequestException as exc:
            log(f"[{slug}] ERRO ao buscar página: {exc}")
            errors.append((source, f"Falha ao acessar a página: `{exc}`"))
            continue

        items = extract_items(html, url)
        log(f"[{slug}] {len(items)} item(ns) extraído(s)")

        if not items:
            errors.append((
                source,
                "Nenhum item foi encontrado na página. O layout do site pode "
                "ter mudado e os seletores em `monitor.py` provavelmente "
                "precisam ser ajustados.",
            ))
            continue

        state = load_state(slug)
        if state is None:
            state = {
                "items": {
                    item["url"]: {
                        "title": item["title"],
                        "date": item.get("date"),
                        "description": item.get("description"),
                        "first_seen": now_iso,
                    }
                    for item in items
                },
                "last_checked": now_iso,
            }
            if not args.dry_run:
                save_state(slug, state)
            baselined.append((source, len(items)))
            continue

        known_urls = set(state["items"].keys())
        new_items = [item for item in items if item["url"] not in known_urls]

        for item in new_items:
            state["items"][item["url"]] = {
                "title": item["title"],
                "date": item.get("date"),
                "description": item.get("description"),
                "first_seen": now_iso,
            }
        state["last_checked"] = now_iso
        if not args.dry_run:
            save_state(slug, state)

        if new_items:
            new_by_source.append((source, new_items))

    # monta o report.md, se houver algo a dizer
    sections = []
    title = None

    if new_by_source:
        total = sum(len(items) for _, items in new_by_source)
        title = f"🔔 Novo conteúdo na ANPD ({total} item{'s' if total != 1 else ''})"
        for source, items in new_by_source:
            sections.append(f"### {source['name']}\n")
            for item in items:
                date_part = f" — _{item['date']}_" if item.get("date") else ""
                sections.append(f"- [{item['title']}]({item['url']}){date_part}")
            sections.append(f"\nFonte monitorada: <{source['url']}>\n")

    if errors:
        err_title = f"⚠️ Falha ao monitorar {len(errors)} fonte(s) da ANPD"
        title = f"{title} / {err_title}" if title else err_title
        sections.append("## ⚠️ Alertas de monitoramento\n")
        for source, msg in errors:
            sections.append(f"- **{source['name']}** (`{source['url']}`): {msg}")

    if sections:
        header = f"_Verificação executada em {now_iso}._\n"
        REPORT_FILE.write_text(header + "\n" + "\n".join(sections) + "\n", encoding="utf-8")
        log(f"report.md gerado: {title}")
    else:
        if REPORT_FILE.exists():
            REPORT_FILE.unlink()
        log("Nada de novo a reportar.")

    if baselined:
        for source, count in baselined:
            log(f"[{source['slug']}] estado inicial criado com {count} item(ns) "
                f"(nenhuma notificação enviada nesta primeira execução)")

    if not args.dry_run:
        build_index()
        log("INDEX.md atualizado.")

    github_output = os.environ.get("GITHUB_OUTPUT")
    if github_output:
        with open(github_output, "a", encoding="utf-8") as fh:
            fh.write(f"has_report={'true' if sections else 'false'}\n")
            if title:
                safe_title = title.replace("\n", " ")
                fh.write(f"title={safe_title}\n")

    return 0


if __name__ == "__main__":
    raise SystemExit(main())
