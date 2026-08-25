import json

data = json.load(open("/tmp/resp_filtrado.json", encoding="utf-8"))
print("items_total:", data.get("items_total"))
print("batching:", data.get("batching"))
items = data.get("items", [])
print("num items retornados:", len(items))
print()

tipos = {}
for it in items:
    tipos[it.get("@type")] = tipos.get(it.get("@type"), 0) + 1
print("tipos presentes:", tipos)
print()

for it in items[:5]:
    print(it.get("title"), "|", it.get("effective"), "|", it.get("@type"))
