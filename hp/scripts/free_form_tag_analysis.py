import argparse
import csv
from collections import Counter, defaultdict
import logging
import re

from hp import FULL_CATALOGUE_PATH, FREE_FORM_TAGS_PATH


logger = logging.getLogger(__name__)
CATEGORIES = ["all", "slash", "het", "explicit"]
FILES = {
    category: str(FREE_FORM_TAGS_PATH / ("top_100_" + category + ".csv"))
    for category in CATEGORIES
}


def clean(line):
    line = line.replace("&quot;", '"')
    line = line.replace("'", '"')
    line = line.replace("&#39;", "")
    line = re.sub(r"\s*-\s*", " - ", line)
    line = line.replace('"', "")
    line = line.replace("Post - Traumatic Stress Disorder", "Post Traumatic Stress Disorder")
    return line


def load_free_form_tags_freqs(selection="all", language="all"):
    """Načte katalog a vrátí seznam s počty jednotlivých tagů.

    Args:
        selection: filter one of all/explicit/slash/het
        language: all/English/...
    Returns:
        free form tags freqs
    """
    freeform_tags = defaultdict(int)
    with open(FULL_CATALOGUE_PATH) as h:
        reader = csv.DictReader(h, delimiter=",")
        for cols in reader:
            if language != "all" and cols["language"] != language:
                continue

            if selection == "explicit":
                if cols["rating"] != "explicit":
                    continue
            if selection == "slash":
                if "slash" not in cols["category"]:
                    continue
            if selection == "het":
                if "het" not in cols["category"]:
                    continue
            if cols["freeform_tags"]:
                for tag in clean(cols["freeform_tags"]).split("|"):
                    if tag:
                        freeform_tags[tag] += 1

    return sorted(freeform_tags.items(), key=lambda x: x[1], reverse=True)


def count_freqs(freqs):
    """Spočítá výskyty postavy v párování a seřadí podle něj. Např. [('Cormac McLaggen', 61), ...]"""
    character_in_relation_freq = defaultdict(int)
    for relation, score in freqs:
        names = relation.split("/")
        for name in names:
            character_in_relation_freq[name] += score
    return sorted(Counter(character_in_relation_freq).items(), key=lambda x: x[1], reverse=True)


def main(category="all", language="all"):
    tag_freqs = load_free_form_tags_freqs(category, language)
    target = FILES[category]
    with open(target, "w") as hw:
        for i, (tag, freq) in enumerate(tag_freqs, start=1):
            hw.write(f"{tag},{freq}")
            if i > 1000:
                break


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate lovers matrices.')
    parser.add_argument('--filter', '-f', dest='filter', default="all",
                        help='filter: all/slash/het/explicit')
    parser.add_argument('--language', '-l', dest='language', default="all",
                        help='language: all/English')

    args = parser.parse_args()

    main(args.filter, args.language)
