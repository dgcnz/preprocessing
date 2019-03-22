import requests, json
import pandas as pd
import arrow

url = "http://localhost:7000/api/preprocess"
headers = {"Content-Type": "application/json"}

df = pd.read_csv("../data/tests.csv")
new_df = {"sentences": [], "processed": []}

for i, pregunta in enumerate(df["Pregunta"]):
    payload = {"sentence": pregunta}
    r = requests.post(url, data=json.dumps(payload), headers=headers)
    new_sentence = r.json()["result"]

    new_df["sentences"].append(pregunta)
    new_df["processed"].append(new_sentence)

new_df = pd.DataFrame(new_df)

# print(new_df)

new_df.to_csv(f"../data/processed_{arrow.now().format(YYYY-MM-DD-HH-mm)}.csv")
