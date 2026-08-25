html = open("/tmp/noticias.html", encoding="utf-8", errors="replace").read()

print("=== OCORRENCIAS DE PADROES CONHECIDOS ===")
padroes = [
    "tileItem", "listing-item", "<table", "<article",
    "/assuntos/noticias/", "searchResults", "content-core",
    "__data", "window.__", "REDUX", "initialState", "Loadable",
]
lowered = html.lower()
for pat in padroes:
    print(pat, ":", lowered.count(pat.lower()))

print()
print("=== PRIMEIRAS OCORRENCIAS DE /assuntos/noticias/ (link individual) ===")
marker = "/anpd/pt-br/assuntos/noticias/"
start = 0
count = 0
while count < 5:
    idx = html.find(marker, start)
    if idx == -1:
        break
    print(repr(html[max(0, idx - 80):idx + 160]))
    start = idx + len(marker)
    count += 1
if count == 0:
    print("NENHUMA OCORRENCIA")

print()
print("=== TRECHO POR VOLTA DE content-core ===")
idx = html.find("content-core")
print("idx:", idx)
if idx >= 0:
    print(html[max(0, idx - 200):idx + 3000])
else:
    print("NAO ENCONTRADO")
