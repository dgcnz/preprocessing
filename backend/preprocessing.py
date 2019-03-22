import json
import re
import string
import hunspell
import numpy
from collections import Counter, defaultdict
from nltk.stem import SnowballStemmer
from nltk.tokenize.toktok import ToktokTokenizer
from nltk.tokenize import sent_tokenize


def levenshtein_dist(s1, s2):
    """
    Computes levenshtein distance for 2 strings
        + Time complexity: |s1| x |s2|
        + Space complexity: |s1| x |s2|
    """

    dp = numpy.empty(shape=(len(s1), len(s2)))
    for i in range(len(s1)):
        for j in range(len(s2)):
            if i == 0:
                dp[i][j] = j
            elif j == 0:
                dp[i][j] = i

            elif s1[i - 1] == s2[j - 1]:
                dp[i][j] = dp[i - 1][j - 1]

            else:
                dp[i][j] = 1 + min(dp[i][j - 1], dp[i - 1][j],
                                   dp[i - 1][j - 1])
    return dp[i][j]


class SpanishPreprocessor:
    """
    @attributes

          $ hspell : hunspell.HunSpell object
          $ tokenizer : tokenize function
          $ stemmer : stem function
          $ abbreviations : dictionary of abbreviations
          $ stopwords : list of stopwords
          $ context_bigram : map of bigrams
    """

    def __init__(self,
                 lang_dic_path=[],
                 context_dics_paths=[],
                 context_bigram_path="",
                 abbreviations_path="",
                 stopwords=[]):
        """
        Takes 5 arguments:
            lang_dic_path : path of language .dic and .aff files
            context_dics_paths : list of paths of .dic context specific dictionaries
            context_bigram_path : path of context_bigram map
            abbreviations_path : path of abbreviations json
            stopwords : list of stopwords
        """
        print(
            f"Activated options:\nhspell: {lang_dic_path != []}\nabbreviations: {abbreviations_path !=''}\nstopwords: {stopwords!=[]}\n"
        )

        self.tokenizer = ToktokTokenizer().tokenize
        self.stemmer = SnowballStemmer('spanish').stem
        self.stopwords = stopwords

        try:
            self.hspell = hunspell.HunSpell(lang_dic_path + '/es_ES.dic',
                                            lang_dic_path + '/es_ES.aff')
        except Exception as e:
            print(
                f"Error while opening language dictionary. If not specified, ignore: {e}"
            )
            self.hspell = None
        try:
            if self.hspell is not None:
                for cs_dic_path in context_dics_paths:
                    # For some reason I've been unable to load a dic with add_dic, so I'll do it manually
                    with open(cs_dic_path, "r") as f:
                        words = f.read().split("\n")
                        for word in words:
                            code = self.hspell.add(word)
                            # print(code)
                    ## print(self.hspell.add_dic(cs_dic_path))
                    ## self.test_dic(cs_dic_path)

        except Exception as e:
            print(
                f"Error while opening context-specific dictionaries. If not specified, ignore: {e}"
            )
        try:
            with open(context_bigram_path, "r") as f:
                self.context_bigram = defaultdict(
                    Counter, json.load(
                        f, object_hook=lambda dct: Counter(dct)))
        except Exception as e:
            print(
                f"Error while opening context bigram. If not specified, ignore: {e}"
            )
        try:
            with open(abbreviations_path, "r") as f:
                self.abbreviations = json.load(f)
        except Exception as e:
            print(
                f"Error while opening abbreviations. If not specified, ignore: {e}"
            )
            self.abbreviations = {}

    def test_dic(self, dic_path):
        with open(dic_path, "r") as f:
            words = f.read().split("\n")
            for word in words:
                print(f"{word} : {self.hspell.spell(word)}\n")
        print(dic_path)

    def word_tokenize(self, sentence):
        return self.tokenizer(sentence)

    def sent_tokenize(self, doc):
        return sent_tokenize(doc)

    def untokenize(self, tokens):
        return ("".join([
            " " + token if not (token.startswith("'") or
                                tokens[i - 1] in ['¿', '¡'] or token == "...")
            and token not in string.punctuation else token
            for i, token in enumerate(tokens)
        ]).strip())

    def stem(self, token):
        return self.stemmer(token)

    def lower_sentence_t(self, tokens):
        return ([
            token.lower() if token.isalpha() else token for token in tokens
        ])

    def lower_sentence(self, sentence):
        """
        Lowercases every token in a sentence.
        """

        tokens = self.lower_sentence_t(self.word_tokenize(sentence))
        return (self.untokenize(tokens))

    def expand_abbreviations_t(self, tokens):
        for i, token in enumerate(tokens):

            if token.isalpha():
                if i == 0:
                    reduction = self.abbreviations.get(f"<s>{token}")
                    if reduction is not None:
                        tokens[i] = reduction[0]
                        pass
                reduction = self.abbreviations.get(token)
                if reduction is not None:
                    tokens[i] = reduction[0]

        return (tokens)

    def expand_abbreviations(self, sentence):
        tokens = self.expand_abbreviations_t(self.word_tokenize(sentence))

        return (self.untokenize(tokens))

    def spell_correct_t(self, tokens):
        for i, token in enumerate(tokens):
            if token.isalpha():
                if not self.hspell.spell(token):
                    suggestions = self.hspell.suggest(token)
                    if suggestions:
                        guess, prob = self.spell_guess(i, tokens,
                                                       suggestions + [token])
                        print(
                            f"\t\t <x> token : {token}   suggestions : {suggestions}  ->  {guess} ({prob} PROBABILITY)"
                        )
                        tokens[i] = guess

        return (tokens)

    def spell_guess(self, pos, tokens, suggestions):
        """
        Given a list of suggestions and a faulty word/token, returns best guess.

        Takes 3 arguments:
            pos : position of current_token
            tokens : list of tokens of sentence
            suggestions : list of suggestions

        Returns:
            Best guess for suggestion
        """

        # TODO : THRESHOLD_SPELL_P could be used later to leave non-word
        #           if candidates don't exceed threshold score

        # THRESHOLD_SPELL_P = 0.065

        LDISTANCE_WEIGHT = 1 / 7
        PENALTY_K = 0.1

        best_guess = ""
        best_score = 0

        for j, guess in enumerate(suggestions):
            penalty = 0
            if pos == 0:
                stemmed_token = r"<s>"
            if j == len(suggestions) - 1:
                penalty = PENALTY_K * 1 / (
                    1 + sum(self.context_bigram[tokens[pos]].values()))
            else:
                temp = pos - 1
                while not tokens[temp].isalpha():
                    temp -= 1

                stemmed_token = self.stem(tokens[temp])

            stemmed_guess = self.stem(guess)
            print(stemmed_token, stemmed_guess)
            try:
                p = self.context_bigram[stemmed_guess][stemmed_token] / sum(
                    self.context_bigram[stemmed_token].values())
            except Exception:
                p = 0

            levdist = levenshtein_dist(guess, tokens[pos])

            #TODO: Implement keyboard distance weight
            """
            keydist = keyboard_dist(guess, tokens[pos])
            score = p + LDISTANCE_WEIGHT * 1 / (
                1 + levdist) + KPD_WEIGHT * keydist - penalty
            """

            score = p + LDISTANCE_WEIGHT * 1 / (1 + levdist) - penalty
            print(
                f"DEBUG SPELL_GUESS:  guess = {guess} score = {score} prob = {p} levdist = {levdist}"
            )
            if score > best_score:
                best_guess = guess
                best_score = score
        return best_guess, best_score

    def spell_correct(self, sentence):
        tokens = self.spell_correct_t(self.word_tokenize(sentence))

        return (self.untokenize(tokens))

    def return_best_sentence(self,
                             sentence,
                             verbose=False,
                             options=["lower", "abbreviations", "spell"]):
        """
        Helper method for computing a series of mutations to the text specified by options.
        @params:
            sentence : str
            verbose : bool
            options : list

        Returns a dictionary structured this way:
            res = {
                "processed" : str,
                "debug" : dict
            }

        debug attribute will only be present when verbose is True.

        """
        print(f"options received: {options}")
        new_sent: str
        tokens: list
        res = defaultdict(dict)

        tokens = self.word_tokenize(sentence)
        print(f"\t<x> tokenized sentence : {tokens}")
        if verbose:
            res["debug"]["tokens"] = tokens

        if "lower" in options:
            tokens = self.lower_sentence_t(tokens)
            print(f"\t<x> lower : {tokens}")
            if verbose:
                res["debug"]["lower"] = self.untokenize(tokens)
        if "abbreviations" in options:
            tokens = self.expand_abbreviations_t(tokens)
            print(f"\t<x> abbreviations : {tokens}")
            if verbose:
                res["debug"]["abbreviations"] = self.untokenize(tokens)
        if "spell" in options:
            tokens = self.spell_correct_t(tokens)
            print(f"\t<x> spelling : {tokens}")
            if verbose:
                res["debug"]["spell"] = self.untokenize(tokens)

        new_sent = self.untokenize(tokens)
        res['processed'] = new_sent
        return res
