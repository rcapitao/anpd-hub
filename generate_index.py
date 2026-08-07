#!/usr/bin/env python3
"""
Gera INDEX.md: um índice, por categoria, de todo o conteúdo já visto pelo
monitoramento (state/<slug>.json), com nome da publicação, link, data e uma
breve descrição quando disponível.

É chamado automaticamente ao final de cada execução de monitor.py, então
fica atualizado sempre que um novo conteúdo é encontrado — mas também pode
ser rodado isoladamente:

    python generate_index.py
"""
from __future__ import annotations

import json
import re
from datetime import datetime, timezone
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parent
STATE_DIR = ROOT / "state"
SOURCES_FILE = ROOT / "sources.yml"
INDEX_FILE = ROOT / "INDEX.md"


def parse_br_date(date_str: str | None):
    if not date_str:
        return None
    try:
        day, month, year = re.split(r"/", date_str)
        year = int(year)
        if year < 100:
            year += 2000
        return datetime(year, int(month), int(day))
    except (ValueError, TypeError):
        return None


def sort_key(entry: dict):
    parsed = parse_br_date(entry.get("date"))
    # itens com data conhecida vêm primeiro, ordenados do mais recente ao mais
    # antigo; sem data conhecida, cai para o fim, ordenado por título.
    if parsed is not None:
        return (0, -parsed.timestamp())
    return (1, entry.get("title", "").lower())


def build_index() -> None:
    sources = yaml.safe_load(SOURCES_FILE.read_text(encoding="utf-8"))["sources"]

    lines = [
        "# Índice de Publicações — Monitoramento ANPD",
        "",
        "> Gerado automaticamente pelo workflow de monitoramento a partir do "
        "conteúdo já detectado nas páginas monitoradas. Não edite manualmente "
        "— veja [`sources.yml`](sources.yml) e [`monitor.py`](monitor.py). "
        "Datas e descrições são um melhor esforço extraído da própria página "
        "e podem estar ausentes.",
        "",
    ]

    total_items = 0
    for source in sources:
        state_path = STATE_DIR / f"{source['slug']}.json"
        if not state_path.exists():
            continue
        state = json.loads(state_path.read_text(encoding="utf-8"))
        entries = [
            {"url": url, **data}
            for url, data in state.get("items", {}).items()
        ]
        if not entries:
            continue
        entries.sort(key=sort_key)
        total_items += len(entries)

        lines.append(f"## {source['name']} ({len(entries)})")
        lines.append("")
        lines.append(f"Fonte: <{source['url']}>")
        lines.append("")
        lines.append("| Publicação | Data | Descrição |")
        lines.append("|---|---|---|")
        for entry in entries:
            title = (entry.get("title") or "").replace("|", "/").strip() or "(sem título)"
            date = entry.get("date") or "—"
            description = (entry.get("description") or "—").replace("|", "/").replace("\n", " ")
            lines.append(f"| [{title}]({entry['url']}) | {date} | {description} |")
        lines.append("")

    categorias_com_dados = sum(
        1 for s in sources if (STATE_DIR / f"{s['slug']}.json").exists()
    )
    header_note = (
        f"_Última atualização: {datetime.now(timezone.utc).isoformat()} · "
        f"{total_items} publicação(ões) em {categorias_com_dados} categoria(s)._"
    )
    lines.insert(2, header_note)
    lines.insert(3, "")

    INDEX_FILE.write_text("\n".join(lines) + "\n", encoding="utf-8")


if __name__ == "__main__":
    build_index()
