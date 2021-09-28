import argparse
import csv
from collections import defaultdict
import datetime
import logging

from hp import FULL_CATALOGUE_PATH, TIMELINE_PATH


logger = logging.getLogger(__name__)
CATEGORIES = ["all", "slash", "het", "explicit"]


def start_week(date_string):
    datet = datetime.date.fromisoformat(date_string)
    start_week = datet - datetime.timedelta(days=datet.weekday())
    return "%04d-%02d-%02d" % (start_week.year, start_week.month, start_week.day)


def load_dates(person, selection="all", language="all"):
    """Načte katalog a vrátí data shluknutá.

    Args:
        selection: filter one of all/explicit/slash/het
        language: all/English/...
    Returns:
        dates merged
    """
    dates = defaultdict(int)
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
            if cols["published"]:
                representant = start_week(cols["published"])
                dates[representant] += 1

    return dates


def main(language="all"):
    for category in CATEGORIES:
        dates = load_dates(category, language)
        sorted_dates = sorted(dates.items(), key=lambda rec: rec[0])[3:]
        oldest = sorted_dates[3][0]
        newest = sorted_dates[-1][0]
        current = oldest
        output = []
        while True:
            output.append(f"{current},{dates.get(current, 0)}")
            new_date = (datetime.datetime.fromisoformat(current) + datetime.timedelta(days=7))
            current = "%04d-%02d-%02d" % (new_date.year, new_date.month, new_date.day)
            if current >= newest:
                break
        target = TIMELINE_PATH / f"timeline_{category}.csv"
        with open(target, "w") as hw:
            hw.write("\n".join(output))


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate free form tags per person freqs.')
    parser.add_argument('--language', '-l', dest='language', default="all",
                        help='language: all/English')

    args = parser.parse_args()

    main(args.language)
