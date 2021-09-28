import argparse
import csv
from collections import defaultdict
import logging

from hp import FULL_CATALOGUE_PATH, FREE_FORM_TAGS_PER_PERSON_PATH
from hp.scripts.relation_matrix_generator import clean as clean_ship
from hp.scripts.free_form_tag_analysis import clean as clean_tag


logger = logging.getLogger(__name__)
CATEGORIES = ["all", "slash", "het", "explicit"]
SELECTION = "Harry_Potter,Draco_Malfoy,Hermione_Granger,Sirius_Black,Remus_Lupin,Severus_Snape,Original_Female_Character,Ginny_Weasley,Ron_Weasley,Tom_Riddle,Reader,You,Voldemort".split(",")


def load_free_form_tags_freqs(person, selection="all", language="all"):
    """Načte katalog a vrátí seznam s počty jednotlivých tagů.

    Args:
        person
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
            if person.lower().replace(" ", "_") in clean_ship(cols["lovers"]).lower().replace(" ", "_") and cols["freeform_tags"]:
                for tag in clean_tag(cols["freeform_tags"]).split("|"):
                    if tag:
                        freeform_tags[tag] += 1

    return sorted(freeform_tags.items(), key=lambda x: x[1], reverse=True)


def main(language="all"):
    for person in SELECTION:
        for category in CATEGORIES:
            tag_freqs = load_free_form_tags_freqs(person, category, language)
            target = FREE_FORM_TAGS_PER_PERSON_PATH / f"{person}_{category}.csv"
            with open(target, "w") as hw:
                for i, (tag, freq) in enumerate(tag_freqs, start=1):
                    hw.write(f"{tag},{freq}\n")
                    if i > 100:
                        break


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate free form tags per person freqs.')
    parser.add_argument('--language', '-l', dest='language', default="all",
                        help='language: all/English')

    args = parser.parse_args()

    main(args.language)
