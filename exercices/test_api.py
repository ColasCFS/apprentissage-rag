questions = [{"id": "Q01"}, {"id": "Q02"}]
trouvee = None

for q in questions:
    if q["id"] == "Q02":
        trouvee = q
    if trouvee is None:
        print("introuvable")

print(trouvee)