import codecs
import os
from collections import Counter, defaultdict

from tokenizer import tokenizer
from filter_file import extract_article_text
import spacy

nlp = spacy.load("en_core_web_sm")

spacy.load("en_core_web_sm")

DIR_PATH = os.path.join(".", "data", "character_context")
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


SENTENCE_END = [".", "?", "!"]
PERSON_CHAR = "😀"

def get_adjectives():
    with codecs.open("adjectives.txt", encoding="utf-8") as adj:
        data = [line.rstrip("\n").lower() for line in adj.readlines()]  # každý řádek končí znakem konec řádku \n, ten chceme oddělat
        return set(data)  # unikátní záznamy

def select_second_item_from_two_items(record):
    """For sorting, return frequency for record (word, frequency). """
    return record[1]


def generate_context_for_all_characters():
    known_adjectives = get_adjectives()
    adjectives = defaultdict(list)  # sem ulozime vse, co najdeme, klic bude postava, hodnota budou privlastky
    for no_article, article in enumerate(extract_article_text()):  # pro kazdy text, co mame
        tokens = tokenizer(article)  # nechme si z nej udelat tokeny
        for position, word in enumerate(tokens):
            current = []
            if word in INVERSE_CHARACTER_NAMES:
                character = INVERSE_CHARACTER_NAMES[word]
                last_member = "ok"
                for back in range(1, 10):
                    if position - back < 0:
                        break
                    current_position_word = tokens[position - back]
                    if current_position_word.lower() == "professor":
                        last_member = "not ok professor"
                        continue
                    elif current_position_word.title() in CHARACTER_NAMES:
                        last_member = "not ok name"
                        continue
                    elif current_position_word.lower() in known_adjectives:
                        last_member = "ok"
                        current.append(current_position_word)
                    else:
                        break
                if last_member != "ok":
                    current = []  # vše smaž
                current.append(PERSON_CHAR)
                last_member = "ok"
                for forward in range(1, 10):
                    if position + forward > len(tokens) - 1:
                        break
                    current_position_word = tokens[position + forward]
                    if current_position_word in SENTENCE_END:
                        break
                    elif current_position_word.lower() in known_adjectives:
                        last_member = "ok"
                        current.append(current_position_word)
                    elif current_position_word in ("is", "was", "were", "will", "be", "isn't", "not", "would"):
                        last_member = "not ok verb"
                        current.append(current_position_word)
                    else:
                        break
                if last_member != "ok":
                    current = current[:current.index(PERSON_CHAR)]
                if len(current) > 1:
                    adjectives[character].append(" ".join(current))

        if no_article % 10 == 0:
            print("----------------------------------------------", no_article)
            for character in CHARACTER_NAMES:
                counter = Counter(adjectives[character])  # {"heslo": 100 -- pocet vyskytu}
                sorted_adjectives = sorted(counter.items(), key=select_second_item_from_two_items, reverse=True)  # lambda magie: napis funkci bez def
                print(character)
                print([item for item, freq in sorted_adjectives])

    # finalni ulozeni do souboru
    for character in CHARACTER_NAMES:
        path = os.path.join(DIR_PATH, character.lower() + ".txt")
        with open(path, "w") as hw:
            counter = Counter(adjectives[character])  # {"heslo": 100 -- pocet vyskytu}
            sorted_adjectives = sorted(counter.items(), key=select_second_item_from_two_items,
                                       reverse=True)  # lambda magie: napis funkci bez def
            for item, freq in sorted_adjectives:
                hw.write(f"{item}\t{freq}\n")


def character_preferences():
    stats = {}
    for character in CHARACTER_NAMES:
        path = os.path.join(DIR_PATH, character.lower() + ".txt")
        with open(path) as h:
            for line in h:
                phrase, freq = line.rstrip("\n").split("\t")
                stats.setdefault(phrase, defaultdict(int))
                stats[phrase][character] += int(freq)
    for phrase, data in stats.items():
        scores = list(data.values())
        top = max(scores)
        scores.remove(top)
        if not scores:
            # jenom jeden charakter ma tuto frazi
            if top == 1:
                # fráze jedenkrát jsou nuda
                continue
        elif top in scores:
            # dva charaktery maji stejnou frekvenci, zadna super charakteristika
            continue
        elif top < max(scores) - 2:
            # frekvence je podobná jiným postavám
            continue
        for character, score in data.items():
            if score == top:
                print(character, ":", phrase, score)

if __name__ == '__main__':
    generate_context_for_all_characters()
    character_preferences()
