import codecs
from collections import Counter, defaultdict

from tokenizer import tokenizer
from filter_file import extract_article_text
import spacy

nlp = spacy.load("en_core_web_sm")

spacy.load("en_core_web_sm")

STOPWORDS = ["from", "in", "and", "to", "out", "up", "not", "before", "he", "she", "are",
             "is", "was", "said", "had", "would", "at", "that", "with", "whether"]
CHARACTER_NAMES = {
    "Sprout": ["Sprout"],
    "Snape": ["Severus", "Snape"],
    "Harry": ["Harry"],
    "Draco": ["Draco"],
    "Voldermort": ["Voldermort"],
    "McGonagall": ["McGonagall", "Minerva"],
    "other": ["Stark", "Albus"],
    "Lupin": ["Lupin"],
    "Peeves": ["Peeves"],
    "Sirius": ["Sirius", "Black"],
}
INVERSE_CHARACTER_NAMES = {}
for target_name, variants in CHARACTER_NAMES.items():
    for variant in variants:
        INVERSE_CHARACTER_NAMES[variant] = target_name


END = [".", "?", "!"]


def get_adjectives():
    with codecs.open("adjectives.txt", encoding="utf-8") as adj:
        data = [line.rstrip("\n").lower() for line in adj.readlines()]  # každý řádek končí znakem konec řádku \n, ten chceme oddělat
        return set(data)  # unikátní záznamy

def select_second_item_from_two_items(record):
    """For sorting, return frequency for record (word, frequency). """
    return record[1]


if __name__ == '__main__':
    known_adjectives = get_adjectives()
    adjectives = defaultdict(list)  # sem ulozime vse, co najdeme, klic bude postava, hodnota budou privlastky
    for no_article, article in enumerate(extract_article_text()):  # pro kazdy text, co mame
        tokens = tokenizer(article)  # nechme si z nej udelat tokeny
        pos_tags = [token.pos_ for token in nlp(" ".join(tokens))]  # a ted tokenum priradme vetnz clen POS
        for position, word in enumerate(tokens):
            current = []
            if word in INVERSE_CHARACTER_NAMES:
                character = INVERSE_CHARACTER_NAMES[word]
                # jdeme dozadu, dokud jsou povolene tagy dozadu, jako JJ
                for back in range(1, 10):
                    if position - back < 0:
                        break
                    current_position_word = tokens[position - back]
                    if current_position_word.lower() == "professor":
                        continue
                    elif current_position_word.lower() in known_adjectives:
                        current.append(current_position_word)
                    else:
                        break
                current.append("😀")
                for forward in range(1, 10):
                    if position + forward > len(tokens) - 1:
                        break
                    current_position_word = tokens[position + forward]
                    if current_position_word.lower() in known_adjectives:
                        current.append(current_position_word)
                    elif current_position_word in ("is", "was", "were", "will", "be", "isn't", "not"):
                        current.append(current_position_word)
                    else:
                        break
                adjectives[character].append(" ".join(current))

        if no_article % 10 == 0:
            print("----------------------------------------------", no_article)
            for character in CHARACTER_NAMES:
                counter = Counter(adjectives[character])  # {"heslo": 100 -- pocet vyskytu}
                sorted_adjectives = sorted(counter.items(), key=select_second_item_from_two_items, reverse=True)  # lambda magie: napis funkci bez def
                print(character)
                print([item for item, freq in sorted_adjectives])