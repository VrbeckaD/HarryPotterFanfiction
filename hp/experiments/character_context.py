import codecs
import os
from collections import Counter, defaultdict

from pathlib import Path

from hp.utils.tokenizer import tokenizer
from hp.utils.filter_file import extract_article_text


DIR_PATH = os.path.join("data", "character_context")
STOPWORDS = ["from", "in", "and", "to", "out", "up", "not", "before", "he", "she", "on", "only", "about",
             "would", "at", "that", "with", "whether", "just", "in", "even",
             "here", "one", "near", "all", "sure", "still", "Black", "through", "i",
             "Potter's", "as", "his", "her", "its", "himself", "herself", "a", "an", "the"
             ]
CHARACTER_NAMES = {
    "Sprout": ["Sprout"],
    "Snape": ["Severus", "Snape"],
    "Harry": ["Harry"],
    "Draco": ["Draco"],
    "Voldermort": ["Voldermort", "Tom", "Riddle", "Marvolo"],
    "McGonagall": ["McGonagall", "Minerva"],
    "other": ["Stark", "Albus"],
    "Lupin": ["Lupin", "Remus"],
    "Peeves": ["Peeves"],
    "Sirius": ["Sirius"],
    "Ronald": ["Ronald", "Ron"],
    "Narcissa": ["Narcissa"],
    "Bellatrix": ["Bellatrix", "Bella"],
    "Hermione": ["Hermione", "Granger"],
    "Luna": ["Luna", "Lovegood", "Loony"],
    "Newt": ["Newt", "Scamander"],
    "Dumbledore": ["Albus", "Dumbledore"],
    "Moody": ["Alastor", "Moody", "Madeye", "Mad-eye"],
    "Cedric": ["Cedric", "Diggory"],
    "Cho": ["Cho", "Chang"],
    "Neville": ["Neville", "Longbottom"],
    "Scorpius": ["Scorpius"],
    "Ginny": ["Ginny"],
    "Tina": ["Tina", "Goldstein"],
    "Grindelwald": ["Grindelwald", "Gellert"],
    "Pansy": ["Pansy", "Parkinson"],
    "Credence": ["Credence", "Barebone"],
    "Charlie": ["Charlie"],
}
INVERSE_CHARACTER_NAMES = {}
for target_name, variants in CHARACTER_NAMES.items():
    for variant in variants:
        INVERSE_CHARACTER_NAMES[variant] = target_name


SENTENCE_END = [".", "?", "!", ",", ";", "then", "–", "and"]
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
    for stopword in STOPWORDS:
        if stopword in known_adjectives:
            known_adjectives.remove(stopword)
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
                annotation = []
                extensions = []
                for forward in range(1, 10):
                    if position + forward > len(tokens) - 1:
                        break
                    current_position_word = tokens[position + forward].lower()
                    if current_position_word in SENTENCE_END:
                        break
                    if current_position_word in STOPWORDS:
                        continue
                    if current_position_word.lower() in known_adjectives:
                        annotation.append("ok")
                    elif current_position_word in ("is", "was", "were", "are", "should", "'ll", "am", "'m", "will", "be", "isn't", "not", "would", "hadn't", "going", "to", "must", "have"):
                        annotation.append("not ok verb")
                    else:
                        annotation.append("not ok other")
                    extensions.append(current_position_word)
                if "ok" not in annotation:
                    extensions = []
                for i in range(1, len(extensions)):
                    if "not ok other" in annotation[:i]:
                        if "ok" in annotation[:i]:
                            extensions = extensions[:i]
                        else:
                            extensions = []
                        break
                current.extend(extensions)
                if len(current) > 1:
                    adjectives[character].append(" ".join(current))

        if no_article % 1000 == 0:
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
    os.chdir("hp")
    generate_context_for_all_characters()
    character_preferences()
    phrases = defaultdict(dict)
    for character in CHARACTER_NAMES:
        text = (Path("data") / "character_context" / (character.lower() + ".txt")).read_text()
        lines = [line.replace(PERSON_CHAR, "").strip() for line in text.split("\n") if line.startswith(PERSON_CHAR) and "black" not in line.lower()]
        total = sum([int(line.split("\t")[1]) for line in lines])
        for line in lines[:20]:
            phrase, freq = line.rstrip("\n").split("\t")
            phrases[phrase][character] = round(100 * float(freq) / total, 1)
    for phrase, data in sorted(phrases.items(), key=lambda rec: sum(rec[1].values()), reverse=True):
        if len(data) == 1:
            continue
        print()
        print(phrase)
        for name, val in sorted(data.items(), key=lambda rec: -rec[1]):
            print(f"{name}\t{val} %")
