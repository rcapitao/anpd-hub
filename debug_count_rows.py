import monitor

url = "https://www.gov.br/anpd/pt-br/acesso-a-informacao/institucional/atos-normativos/regulamentacoes_anpd"
html = monitor.fetch(url)
soup = monitor.BeautifulSoup(html, "lxml")
container = monitor.pick_container(soup)

tables = container.select("table")
print("numero de tabelas encontradas:", len(tables))
total_rows = 0
for i, table in enumerate(tables):
    rows = table.find_all("tr")
    print(f"tabela {i}: {len(rows)} linhas (incluindo cabecalho)")
    total_rows += max(0, len(rows) - 1)
print("total de linhas de dados (todas as tabelas):", total_rows)
print()

items = monitor.extract_via_tables(container, url)
print("itens extraidos por extract_via_tables:", len(items))
urls = [i["url"] for i in items]
print("urls duplicadas dentro do resultado?", len(urls) != len(set(urls)))
print()

# olha tambem para headings (h2/h3) que podem indicar secoes com tabelas
# separadas (ex.: "RESOLUCOES", "PORTARIAS", "ENUNCIADOS")
for h in container.select("h2, h3"):
    print("heading:", h.get_text(" ", strip=True))
