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
import socket
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from urllib.parse import urljoin, urlparse

import requests
import urllib3.util.connection as urllib3_connection
import yaml
from bs4 import BeautifulSoup
from requests.adapters import HTTPAdapter
from urllib3.util.retry import Retry

from generate_index import build_index

# Alguns runners do GitHub Actions não têm rota IPv6, mas o gov.br anuncia
# endereço AAAA para www.gov.br. Sem isso, a tentativa de conexão IPv6 falha
# com "[Errno 101] Network is unreachable" antes mesmo de tentar IPv4, e
# TODAS as fontes falham de uma vez (não é um bloqueio do site).
urllib3_connection.allowed_gai_family = lambda: socket.AF_INET

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

SESSION = requests.Session()
_retry = Retry(total=3, backoff_factor=2, status_forcelist=(429, 500, 502, 503, 504))
SESSION.mount("https://", HTTPAdapter(max_retries=_retry))
SESSION.mount("http://", HTTPAdapter(max_retries=_retry))

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

MESES_PT = {
    "janeiro": 1, "fevereiro": 2, "março": 3, "marco": 3, "abril": 4,
    "maio": 5, "junho": 6, "julho": 7, "agosto": 8, "setembro": 9,
    "outubro": 10, "novembro": 11, "dezembro": 12,
}
# Datas por extenso, como usadas nos títulos dos atos normativos da ANPD
# (ex.: "Resolução CD/ANPD nº 11, de 27 de dezembro de 2023").
LONG_DATE_RE = re.compile(
    r"\b(\d{1,2})\s+de\s+(" + "|".join(MESES_PT) + r")\s+de\s+(\d{4})\b",
    re.IGNORECASE,
)


def log(msg: str) -> None:
    print(msg, file=sys.stderr, flush=True)


def clean_text(text: str) -> str:
    text = re.sub(r"\s+", " ", text or "").strip(" ​-–—:•,.")
    return re.sub(r"\s+([,.])", r"\1", text)


def find_date(*texts: str):
    for text in texts:
        if not text:
            continue
        match = DATE_RE.search(text)
        if match:
            return match.group(0)
        match = LONG_DATE_RE.search(text)
        if match:
            day, month_name, year = match.groups()
            month = MESES_PT[month_name.lower()]
            return f"{int(day):02d}/{month:02d}/{year}"
    return None


def fetch(url: str) -> str:
    resp = SESSION.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    return resp.text


# Sinais de que a resposta é uma página de bloqueio/desafio anti-bot (ou uma
# página de manutenção) em vez do conteúdo real — usados só para deixar a
# mensagem de erro mais precisa, não para decidir se há item novo.
CHALLENGE_MARKERS = (
    "captcha", "cloudflare", "just a moment", "attention required",
    "acesso negado", "temporariamente indisponível", "em manutenção",
)


def looks_like_challenge_page(html: str) -> bool:
    lowered = html.lower()
    return len(html) < 2000 or any(marker in lowered for marker in CHALLENGE_MARKERS)


def derive_api_search_url(url: str):
    """Converte a URL de uma página do Volto na URL do endpoint REST
    @search equivalente (ex.: .../anpd/pt-br/x -> .../anpd/++api++/pt-br/x/@search).
    O site é Plone/Volto: o front-end é só a "casca" React, e o conteúdo
    real (inclusive listagens montadas no cliente via JS) vem dessa API."""
    parsed = urlparse(url)
    parts = parsed.path.strip("/").split("/")
    if len(parts) < 2:
        return None
    site, rest = parts[0], "/".join(parts[1:])
    return f"{parsed.scheme}://{parsed.netloc}/{site}/++api++/{rest}/@search"


# Tipos de conteúdo do Plone que não são "itens de listagem" de verdade —
# costumam ser imagens/arquivos anexados à mesma pasta e aparecem junto no
# @search, mas não interessam para o monitoramento.
API_EXCLUDED_TYPES = {"Image", "File"}


def extract_via_api(base_url: str, portal_type: str | None = None):
    """Busca a listagem via API REST do Volto (++api++/@search).

    Sem filtro de tipo, o @search devolve todo o conteúdo recursivo da
    pasta — inclusive imagens/arquivos anexados a cada item — então o
    total pode ficar muito maior que o número real de itens "de listagem"
    (ex.: uma pasta de notícias com 38 notícias pode ter @search com
    centenas de resultados, por causa das imagens de cada notícia). Quando
    a fonte especifica um portal_type (via `api_portal_type` em
    sources.yml), filtramos direto na consulta para pegar exatamente esse
    conteúdo, com paginação generosa o suficiente para não cortar nada.
    """
    api_url = derive_api_search_url(base_url)
    if not api_url:
        return []
    params = {"b_size": 200, "sort_on": "effective", "sort_order": "descending"}
    if portal_type:
        params["portal_type"] = portal_type
    try:
        resp = SESSION.get(api_url, headers={**HEADERS, "Accept": "application/json"},
                            params=params, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        data = resp.json()
    except (requests.RequestException, ValueError):
        return []

    base_normalized = base_url.rstrip("/")
    items = []
    for entry in data.get("items", []):
        if entry.get("@type") in API_EXCLUDED_TYPES:
            continue
        if entry.get("review_state") not in (None, "published"):
            continue
        title = clean_text(entry.get("title") or "")
        href = entry.get("@id")
        if not title or not href:
            continue
        if href.rstrip("/") == base_normalized:
            # é a própria pasta/página de índice (ex.: a página "Notícias"),
            # não um item de conteúdo dentro dela
            continue
        date = None
        effective = entry.get("effective")
        if effective:
            try:
                date = datetime.fromisoformat(effective).strftime("%d/%m/%Y")
            except ValueError:
                pass
        description = clean_text(entry.get("description") or "") or None
        items.append({
            "url": href,
            "title": title,
            "date": date,
            "description": description[:280] if description else None,
        })
    return items


def fetch_and_extract(url: str, attempts: int = 3, delay: float = 5.0,
                       api_portal_type: str | None = None):
    """Busca a página e extrai os itens, tentando de novo se a conexão
    falhar ou se a extração vier vazia — sites gov.br às vezes servem uma
    página de bloqueio/instabilidade momentânea em vez do conteúdo real, e
    uma nova tentativa alguns segundos depois costuma resolver. Se mesmo
    assim não vier nada (ex.: página renderizada só no cliente, sem
    conteúdo no HTML estático), tenta a API REST do Volto (++api++/@search)
    como último recurso antes de desistir."""
    last_html = ""
    for attempt in range(1, attempts + 1):
        try:
            last_html = fetch(url)
        except requests.RequestException:
            if attempt == attempts:
                raise
            log(f"  tentativa {attempt}/{attempts}: erro de conexão, "
                f"nova tentativa em {delay:.0f}s")
            time.sleep(delay)
            continue

        items = extract_items(last_html, url)
        if items:
            return items, last_html
        if attempt < attempts:
            log(f"  tentativa {attempt}/{attempts}: nenhum item extraído "
                f"(possível bloqueio/instabilidade temporária), nova tentativa "
                f"em {delay:.0f}s")
            time.sleep(delay)

    api_items = extract_via_api(url, portal_type=api_portal_type)
    if api_items:
        log("  itens obtidos via API REST do Volto (++api++/@search)")
        return api_items, last_html
    return [], last_html


def normalize_title(title: str) -> str:
    return clean_text(title).lower()


def reconcile_url_change(state: dict, item: dict, now_iso: str, current_urls: set) -> bool:
    """Se o item já existe no estado sob outra URL com o mesmo título (o
    site trocou o link, ex.: de in.gov.br para uma página própria do
    gov.br), atualiza a URL guardada em vez de tratar como conteúdo novo.

    Só reconcilia se a URL antiga *não* aparece mais na extração atual da
    página — ou seja, ela realmente sumiu (migração). Páginas como
    "Regulamentações da ANPD" repetem o mesmo texto genérico ("Conheça
    também, sua versão em língua inglesa...") em vários documentos
    DIFERENTES (PDFs em idiomas diferentes, por exemplo); se reconciliasse
    só por título igual, um documento real e ainda presente na página
    seria descartado silenciosamente a cada execução.

    Retorna True se reconciliou (nada a notificar), False caso contrário.
    """
    norm = normalize_title(item["title"])
    for old_url, data in list(state["items"].items()):
        if old_url == item["url"]:
            continue
        if normalize_title(data.get("title", "")) != norm:
            continue
        if old_url in current_urls:
            # a URL antiga continua presente nesta mesma extração: não é
            # uma migração, são dois documentos diferentes com título igual
            continue
        old_data = state["items"].pop(old_url)
        state["items"][item["url"]] = {
            "title": item["title"],
            "date": item.get("date") or old_data.get("date"),
            "description": item.get("description") or old_data.get("description"),
            "first_seen": old_data.get("first_seen", now_iso),
        }
        log(f"  URL atualizada para o mesmo conteúdo: {old_url} -> {item['url']}")
        return True
    return False


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
            date = find_date(el.get_text(" ", strip=True))
            items.append({
                "url": url,
                "title": title,
                "date": date,
                "description": extract_description(el, title),
            })
        if items:
            return items
    return []


# Palavras-chave (em minúsculas) usadas para reconhecer colunas de tabelas de
# listagem, como as usadas em "Regulamentações da ANPD" e "Atos de Gestão
# Interna": colunas "Ato" (título/link), "Ementa" (descrição), "Data" e
# "Status Atual".
TABLE_DESCRIPTION_HEADERS = ("ementa", "descri", "resumo")
TABLE_STATUS_HEADERS = ("status",)
TABLE_DATE_HEADERS = ("data",)


def find_column_index(headers, keywords):
    for i, header in enumerate(headers):
        if any(keyword in header for keyword in keywords):
            return i
    return None


def extract_via_tables(container, base_url: str):
    items = []
    for table in container.select("table"):
        rows = table.find_all("tr")
        if len(rows) < 2:
            continue

        header_cells = rows[0].find_all(["th", "td"])
        headers = [clean_text(c.get_text(" ", strip=True)).lower() for c in header_cells]
        desc_idx = find_column_index(headers, TABLE_DESCRIPTION_HEADERS)
        status_idx = find_column_index(headers, TABLE_STATUS_HEADERS)
        date_idx = find_column_index(headers, TABLE_DATE_HEADERS)

        for row in rows[1:]:
            cells = row.find_all(["td", "th"])
            link = row.select_one("a[href]")
            if not cells or link is None or not link.get("href"):
                continue

            title = clean_text(link.get_text(" ", strip=True))
            if not title:
                continue
            url = urljoin(base_url, link["href"])

            description = None
            if desc_idx is not None and desc_idx < len(cells):
                description = clean_text(cells[desc_idx].get_text(" ", strip=True)) or None

            status = None
            if status_idx is not None and status_idx < len(cells):
                status = clean_text(cells[status_idx].get_text(" ", strip=True)) or None
            if status:
                description = f"{description} (Status: {status})" if description else f"Status: {status}"

            date_cell_text = (
                cells[date_idx].get_text(" ", strip=True)
                if date_idx is not None and date_idx < len(cells) else None
            )
            date = find_date(date_cell_text, title, row.get_text(" ", strip=True))

            items.append({
                "url": url,
                "title": title,
                "date": date,
                "description": description[:280] if description else None,
            })
    return items


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

        description = None
        if parent_text and parent_text.lower() != title.lower():
            remainder = clean_text(parent_text.replace(title, "", 1))
            if len(remainder) > 20:
                description = remainder[:280]

        items.append({
            "url": url,
            "title": title,
            "date": find_date(parent_text, title),
            "description": description,
        })
    return items


def extract_items(html: str, base_url: str):
    soup = BeautifulSoup(html, "lxml")
    container = pick_container(soup)
    items = extract_via_item_selectors(container, base_url)
    if not items:
        items = extract_via_tables(container, base_url)
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
            items, last_html = fetch_and_extract(
                url, api_portal_type=source.get("api_portal_type"))
        except requests.RequestException as exc:
            log(f"[{slug}] ERRO ao buscar página: {exc}")
            errors.append((source, f"Falha ao acessar a página: `{exc}`"))
            continue

        log(f"[{slug}] {len(items)} item(ns) extraído(s)")

        if not items:
            if looks_like_challenge_page(last_html):
                msg = (
                    "Nenhum item foi encontrado após várias tentativas, e a "
                    "resposta recebida parece uma página de bloqueio "
                    "anti-bot ou de instabilidade temporária do site, não o "
                    "conteúdo real. Se isso persistir por vários dias "
                    "seguidos, pode ser necessário ajustar como as "
                    "requisições são feitas (ex.: user-agent, cabeçalhos)."
                )
            else:
                msg = (
                    "Nenhum item foi encontrado na página. O layout do site "
                    "pode ter mudado e os seletores em `monitor.py` "
                    "provavelmente precisam ser ajustados."
                )
            errors.append((source, msg))
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
        current_urls = {i["url"] for i in items}
        candidates = [item for item in items if item["url"] not in known_urls]
        new_items = [
            item for item in candidates
            if not reconcile_url_change(state, item, now_iso, current_urls)
        ]

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
