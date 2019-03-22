import json
import os

data = None

def menu():
    print("What do you want to do?")
    print("1             : Add new entry")
    print("2             : See all entries")
    print("3             : See all entries and definitions")
    print("4             : Add new entry repeatedly")
    print("anything else : Quit.")

    n = input("Write option here:\n >> ")
    if (n == "1"):
        return(add_new())
    elif (n == "2"):
        return(display_entries())
    elif (n == "3"):
        return(display_all())
    elif (n == "4"):
        return(add_new_chain())
    else:
        return (0)

def add_new():
    global data

    word = input("Ingresa palabra:\n >> ")
    definition = input("Ingresa sinónimo:\n >> ")

    data[word] = [definition]
    return (1)

def add_new_chain():
    global data

    while (True):
        word = input("Ingresa palabra:\n >> ")
        if not word:
            break
        definition = input("Ingresa sinónimo:\n >> ")
        if not definition:
            break
        data[word] = [definition]
    return (1)


def display_entries():
    if (data):
        print(list(data.keys()))
    else:
        print("There's no data to show.")
    return (1)

def display_all():
    if (len(data) != 0):
        print()
        for word, definitions in data.items():
            print("\t", word, " : ", definitions)

        print()
    else:
        print("There's no data to show.")

def main():
    global data
    json_file = 'resources/slang.json'

    with open(json_file) as f:
        if(os.stat(json_file).st_size == 0):
            data = {}
            print("Creating...")
        else:
            data = json.load(f)

    while (menu() != 0):
        pass

    with open(json_file, 'w', encoding='utf8') as fp:
        if (len(data) != 0):
            json.dump(data, fp, sort_keys=True, indent=4, ensure_ascii=False)

if __name__ == '__main__':
    main()
