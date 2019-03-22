# Preprocessing API

Small utility for preprocessing.

## Instructions for querying endpoint
```
import requests, json

BASE_URL = http://localhost:7000  # Example
url = f"{BASE_URL}/api/preprocess"
headers = {"Content-Type": "application/json"}

# Define sentence
sentence = "Ojalá no se desconfigure esto."

payload = {"sentence": sentence}

r = requests.post(url, data=json.dumps(payload), headers=headers)
res = r.json()
new_sentence = res["processed"]

print(new_sentence)
# Output: "ojalá no se des configure esto."
```

## Features

+ light preprocessing
    + uniform spacing/delimitation
    + lowercasing
+ abbreviation expansion
    + handles 2 wildcards: `<s>` and `</s>` for start and end of sentence respectively
+ spell correction
    + (Currently using hunspell's spell-checking and candidate generator)
    + LD weighting
    + context-specific bigram probability weighting (needs context-specific corpus)

## TODO

+ Build own spell checker and candidate generator (Hunspell integration is too complicated)
    + Trie-based spell checker
+ Phonetic candidate suggestion
+ Key proximity distance
+ O(mn) dl-distance


## Sources and references:

+ [Wagner, Robert. *An Extension of the String-to-String Correction Problem*](https://dl.acm.org/citation.cfm?doid=321879.321880)
+ [Jurafsky, Dan. *Spelling Correction and the Noisy Channel*](https://web.stanford.edu/class/cs124/lec/spelling.pdf)
