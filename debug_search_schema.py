import json

data = json.load(open("/tmp/resp.json", encoding="utf-8"))
print("items_total:", data.get("items_total"))
print("batching:", data.get("batching"))
print("num items nesta pagina:", len(data.get("items", [])))
print()
first = data["items"][0]
print("chaves do primeiro item:", sorted(first.keys()))
print()
for it in data["items"][:3]:
    print("title:", it.get("title"))
    print("@id:", it.get("@id"))
    print("effective:", it.get("effective"))
    print("description:", it.get("description"))
    print("review_state:", it.get("review_state"))
    print("---")
