from bs4 import BeautifulSoup
import re
import requests

url = "https://www.plannedparenthood.org/es/temas-de-salud/glosario"
html_doc = requests.get(url).text

fp = '/Users/dgcnz/development/cognitiva/preprocessing/backend/resources/dictionaries/es_ES_expanded.dic'

with open(fp, "r") as f:
    sp = f.read()

es = sp.split("\n")
es_lower = [x.lower() for x in es]

soup = BeautifulSoup(html_doc, 'html.parser')
definitions_raw = soup.find_all("dt", class_="def-term")

new_glosario_raw = []
for d in definitions_raw:
    new_glosario_raw.append(d.contents[0])

delimiter = r'[\s/]'
new_glosario = []
for term in new_glosario_raw:
    words = re.split(delimiter, term)
    for word in words:
        word = re.sub(r'["“”(),]', '', word)
        if len(word) >= 3:
            new_glosario.append(word)

new_glosario = {v.lower(): v for v in new_glosario}.values()
difference = set()

for word in new_glosario:
    if word.lower() not in es_lower:
        difference.add(word)

print(difference)
difference = sorted(difference)
fp = '/Users/dgcnz/development/cognitiva/preprocessing/backend/resources/dictionaries/context_specific.dic'
with open(fp, "w+") as f:
    for word in difference:
        f.write(f"{word}\n")
