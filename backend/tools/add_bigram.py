# -*- coding: utf-8 -*-
from nltk.stem import SnowballStemmer
from collections import defaultdict, Counter
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.tokenize import sent_tokenize
import string, json, os, re


class UnsupportedFileType(Exception):
    pass


class EmptyFile(Exception):
    pass


def checker(bigram_map, token1, token2):
    return True if token1 in bigram_map and token2 in bigram_map[
        token1] else False


def backup(obj, format_, path_, permissions):
    try:
        with open(path_, permissions, encoding="utf-8") as f:
            if format_ == "json":
                f.write(json.dumps(obj, indent=2, ensure_ascii=False))
            elif format_ == "txt":
                f.write(obj)
            else:
                raise UnsupportedFileType(f"{path_}")
    except Exception as e:
        raise Exception("Couldn't open backup file.")


def open_and_backup(dest_path, backup_path, format_):
    try:
        if os.stat(dest_path).st_size == 0:
            raise EmptyFile(f"{dest_path}")

        with open(dest_path, 'r', encoding="utf-8") as f:
            if format_ == "json":
                print("loading json")
                obj = defaultdict(
                    Counter, json.load(
                        f, object_hook=lambda dct: Counter(dct)))
            elif format_ == "txt":
                obj = f.read()
            else:
                raise UnsupportedFileType(f"{dest_path}")
            backup(obj, format_=format_, path_=backup_path, permissions="a+")
    except UnsupportedFileType as e:
        raise Exception("Failed to open file or backup.")
    except EmptyFile as e:
        if format_ == "json":
            obj = defaultdict(Counter)
        elif format_ == "txt":
            obj = ""
        else:
            raise UnsupportedFileType(f"Unknown type: {format_}")
    except Exception as e:
        raise Exception("Failed to open file or backup.")

    return obj


def main():

    # ***************** aliasing *****************

    word_tokenize = ToktokTokenizer().tokenize
    stem = SnowballStemmer('spanish').stem

    # ********************************************

    bigram_map = open_and_backup("../resources/bigram.json",
                                 "../resources/old_bigram.json", "json")
    print(type(bigram_map))
    input_file = ""
    while input_file == "":
        input_file = input(
            "Enter file for new entries. (Should be a .txt inside backend/data/)\n >> "
        )

    new_entries = open_and_backup(f"../data/{input_file}",
                                  "../data/old_entries.txt", "txt")

    pattern = re.compile(r"(?<=\w) ?/ ?(?=\w)")

    for sentence in sent_tokenize(new_entries):
        sentence = sentence.replace('“', '"').replace(
            '”', '"')  # Flattening smart quotes
        sentence = re.sub(pattern=pattern, string=sentence, repl=" o ")
        tokens = word_tokenize(sentence)
        bigram_map["<s>"]["</s>"] += 1
        for i, token in enumerate(tokens):
            if token.isalpha():
                if i == 0:
                    bigram_map[stem(token)]["<s>"] += 1
                elif i == len(tokens) - 1:
                    bigram_map["</s>"][stem(token)] += 1
                else:
                    tmp = i - 1
                    last = tokens[tmp]
                    while len(
                            last) == 1 and last != "," and not last.isalpha():
                        last = tokens[tmp]
                        tmp -= 1
                        if tmp == -1:
                            last = "<s>"
                            break
                    if last != "<s>":
                        last = stem(last)

                    bigram_map[stem(token)][last] += 1

    print(bigram_map)
    b = input(
        "Everything was done correctly, are you sure you want to write on top of bigram.json? (y/n)\n >> "
    )
    if b != "y":
        print("quitting.")

    else:
        b = input("Do you want to clear entries file?(y/n)\n >> ")
        if b == "y":
            open(f"../data/{input_file}", 'w').close()
        with open("../resources/bigram.json", "w", encoding="utf-8") as f:
            f.write(json.dumps(bigram_map, indent=2, ensure_ascii=False))


if __name__ == '__main__':
    main()
