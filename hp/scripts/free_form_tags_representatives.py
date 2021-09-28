import argparse
import csv
from collections import defaultdict, Counter
import logging

from hp import FULL_CATALOGUE_PATH, FREE_FORM_TAGS_REPRESENTATIVES_PATH
from hp.scripts.relation_matrix_generator import clean as clean_ship
from hp.scripts.free_form_tag_analysis import clean as clean_tag


logger = logging.getLogger(__name__)
CATEGORIES = ["all", "explicit"]

TAGS = """Fluff,Angst,none,Romance,Alternate Universe - Canon Divergence,Hurt/Comfort,Slow Burn,Smut,Alternate Universe,Harry Potter Epilogue What Epilogue / EWE,Established Relationship,Marauders Era (Harry Potter),Fluff and Angst,Humor,Hogwarts,Friendship,Friends to Lovers,One Shot,Post - Hogwarts,Post - War,Anal Sex,Hogwarts Eighth Year,Time Travel,Angst with a Happy Ending,Explicit Sexual Content,Oral Sex,Drama,Marauders,Implied/Referenced Child Abuse,Drabble,Other Additional Tags to Be Added,Mutual Pining,Canon Compliant,Fluff and Smut,Crossover,Pining,wolfstar,Emotional Hurt/Comfort,Fluff and Humor,Alternate Universe - Modern Setting,First Kiss,Love,Enemies to Friends to Lovers,Family,Light Angst,Post Traumatic Stress Disorder - PTSD,Getting Together,Dont copy to another site,Domestic Fluff,Happy Ending,Enemies to Lovers,Falling In Love,Plot What Plot/Porn Without Plot,Christmas,Character Death,Female Harry Potter,Auror Harry Potter,Eventual Romance,Magic,Post - Battle of Hogwarts,Alternate Universe - Harry Potter Setting,Albus Dumbledore Bashing,Alternate Universe - Muggle,Kissing,Eventual Smut,Blow Jobs,Manipulative Albus Dumbledore,POV Draco Malfoy,Not Canon Compliant,Crack,Violence,Quidditch,Secret Relationship,Angst and Hurt/Comfort,Marauders Friendship (Harry Potter),Mpreg,Sex,Original Character(s),Minor Character Death,Soulmates,Master of Death Harry Potter,Rough Sex,Alternate Universe - Hogwarts,Christmas Fluff,Drarry,Anal Fingering,Good Draco Malfoy,Ron Weasley Bashing,Grief/Mourning,Depression,First Time,Dirty Talk,First War with Voldemort,Post - Canon,Slytherin Harry Potter,Love Confessions,AU,Vaginal Sex,Shameless Smut,Canonical Character Death,Child Abuse,Masturbation,Idiots in Love,Explicit Language,Death Eaters,Art,Not Epilogue Compliant,Tooth - Rotting Fluff,Alternate Universe - Soulmates,Severus Snape Lives,POV Harry Potter,Age Difference,Hogwarts Sixth Year,Torture,Mystery,Good Severus Snape,Alternate Universe - Non - Magical,Slytherin,Coming Out,Slash,Cute,Book 5: Harry Potter and the Order of the Phoenix,Sexual Content,Slow Build,Mental Health Issues,Sirius Black Lives,Jealousy,Swearing,Rimming,Family Fluff,Friendship/Love,Canon - Typical Violence,Not Beta Read,Dark Magic,Fanart,Harry Potter Next Generation,Redeemed Draco Malfoy,Romantic Fluff,Boys In Love,Bottom Draco Malfoy,Dom/sub,Good Slytherins,Drama &amp; Romance,BDSM,Dark,Family Feels,Vaginal Fingering,Top Harry Potter,Panic Attacks,Flirting""".split(",")


def load_free_form_tags_freqs(selection="all", language="all"):
    """Načte katalog a vrátí seznam s počty jednotlivých tagů.

    Args:
        selection: filter one of all/explicit/slash/het
        language: all/English/...
    Returns:
        free form tags freqs
    """
    freeform_tags = defaultdict(Counter)
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
            tags = clean_tag(cols["freeform_tags"]).split("|")
            people = [item for item in clean_ship(cols["lovers"]).split("/") if item]
            for tag in tags:
                if tag in TAGS:
                    freeform_tags[tag].update(people)

    return freeform_tags


def main(language="all"):
    for category in CATEGORIES:
        tag_freqs = load_free_form_tags_freqs(category, language)
        for tag, data in tag_freqs.items():
            target = FREE_FORM_TAGS_REPRESENTATIVES_PATH / f"{tag.replace('/', '_')}_{category}.csv"
            with open(target, "w") as hw:
                hw.write(f"{tag},freq\n")
                for i, (person, freq) in enumerate(sorted(data.items(), key=lambda r: -r[1]), start=1):
                    hw.write(f"{person},{freq}\n")
                    if i > 100:
                        break


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate free form tags per person freqs.')
    parser.add_argument('--language', '-l', dest='language', default="all",
                        help='language: all/English')

    args = parser.parse_args()

    main(args.language)
