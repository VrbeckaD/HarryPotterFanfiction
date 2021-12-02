from collections import Counter, defaultdict
from itertools import combinations
from pathlib import Path
from csv import DictReader
import re

from hp import FULL_CATALOGUE_PATH

HEADER = "filename,title,rating,ship,language,category,lovers,wordcount,published,hits,freeform_tags"


def _preprocess(text):
    """Spojit tagy, které jsou významově odpovídající, a lze je spojit jednoduše automaticky."""
    text = text.replace("&#39;", "'").replace('’', "'")
    text = re.sub(r"\s*[(].*", "", text)
    text = re.sub(r"\s*[,]\s*", " ", text)
    text = re.sub(r"\s*&amp;\s*", " and ", text)
    text = re.sub(r"\s*[?]\s*", "", text)
    text = re.sub(r"[?.!,;]\s*$", "", text)
    text = re.sub(r" mentioned$", "", text)
    text = re.sub(r"kisses$", "kiss", text)
    text = re.sub(r"ings$", "ing", text)
    text = re.sub(r"ables$", "able", text)
    text = text.replace("don't copy to another site", "")
    text = re.sub(r"^mentions of ", "", text)
    text = re.sub("ptsd.{0,5}post-traumatic stress disorder", "post-traumatic stress disorder", text)
    text = re.sub("post-traumatic stress disorder.{0,5}ptsd", "post-traumatic stress disorder", text)
    text = re.sub("ptsd", "post-traumatic stress disorder", text)
    text = text.replace("s' era", "s era")
    text = re.sub(r"book (\d): harry potter.*", r"book \g<1>", text)
    text = text.replace("marauders era", "marauders")
    return text.strip()


def get_tags(text):
    """Vrátit z popisku všechny unikátní tagy, které nejsou `none` a delší než 2 znaky."""
    result = [item.lower() for item in text.split("|") if item]
    result = [_preprocess(item) for item in result if item != "none"]
    result = [item for item in result if len(item) > 2]
    return result


def _get_lovers(text):
    if text.count("/") == 1:
        text = text.replace("(s)", "")
        lovers = sorted([re.sub(r"\s*[(].*", "", t.strip()) for t in text.lower().split("/")])
        if "|" in lovers[0] or "|" in lovers[1]:
            return
        if any(not i for i in lovers):
            return
        return "/".join(tuple(lovers))


def _to_date(text):
    if text.count("-") != 2:
        raise ValueError()
    return text[:text.find("-")]


def get_data():
    """Nachystat si data."""
    path = Path(FULL_CATALOGUE_PATH).resolve()
    with Path(path).open(encoding="utf-8", errors="replace") as h:
        freqs = Counter()
        data = defaultdict(list)
        cotags = Counter()
        ratings = defaultdict(Counter)
        lovers = defaultdict(Counter)
        per_person = defaultdict(Counter)
        dated = defaultdict(Counter)

        for line in DictReader(h, delimiter=",", fieldnames=HEADER.split(",")):
            tags = get_tags(line["freeform_tags"])
            for t1, t2 in combinations(tags, 2):
                if t1 == t2:
                    continue
                elif t1 < t2:
                    k = (t1, t2)
                else:
                    k = (t2, t1)
                cotags.update([k])
            for tag in tags:
                data[tag].append(line)
                freqs.update([tag])
                if line["rating"]:
                    ratings[tag].update([line["rating"]])
                pair = _get_lovers(line["lovers"])
                if pair:
                    lovers[tag].update([pair])
                    for person in pair.split("/"):
                        per_person[person].update([tag])
                try:
                    published = _to_date(line["published"])
                    dated[tag].update([published])
                except:
                    pass
        return freqs, cotags, ratings, lovers, per_person, dated, data


def main():
    """Připravit csv soubory z dat."""
    frequencies, cooccurrences, ratings, lovers, per_person_tags, per_year, records = get_data()
    with (Path("..") / "data" / "free_form_freqs.csv").open("w") as hw:
        hw.write("tag,freq\n")
        for key, freq in sorted(frequencies.items(), key=lambda r: -r[1]):
            hw.write(f"{key},{freq}\n")

    with (Path("..") / "data" / "free_form_cooccurrences.csv").open("w") as hw:
        hw.write("tags,freq\n")
        for key, freq in sorted(cooccurrences.items(), key=lambda r: -r[1]):
            hw.write(f"{'+'.join(key)},{freq}\n")

    with (Path("..") / "data" / "free_form_rating_tags_with_freq_gt_10.csv").open("w") as hw:
        CATEGORIES = ["general", "teen", "mature", "explicit", "notrated"]
        hw.write(",".join(["tag"] + CATEGORIES) + "\n")
        for tag, stats in ratings.items():
            total = 1.0 * sum(stats.values())
            if total < 10:
                continue
            r = dict.fromkeys(CATEGORIES, 0)
            r.update(stats)
            hw.write(",".join([tag] + [str(round(100 * r[k] / total)) for k in CATEGORIES]) + "\n")

    with (Path("..") / "data" / "free_form_tags_with_freq_gt_10_lovers_freq_gt_100.csv").open("w") as hw:
        all_pairs = Counter()
        for stats in lovers.values():
            all_pairs.update(stats.keys())
        lover_pairs = [pair for pair, freq in sorted(all_pairs.items(), key=lambda r: -r[1])[:100] if freq > 100]
        hw.write(",".join(["tag"] + lover_pairs) + "\n")
        for tag, stats in lovers.items():
            r = dict.fromkeys(lover_pairs, 0)
            r.update(stats)
            total = 1.0 * sum(r.values())
            for lover in list(r):
                if lover not in lover_pairs:
                    del r[lover]
            if total < 10:
                continue
            hw.write(",".join([tag] + [str(round(100 * r[k] / total)) for k in lover_pairs]) + "\n")

    for person, person_data in per_person_tags.items():
        for k, v in list(person_data.items()):
            if v < 3:
                del person_data[k]
        if sum(person_data.values()) > 1000:
            with (Path("..") / "data" / f"free_form_per_person_top_tags_{person}_filtered_le_3_freq_1000+.csv").open("w") as hw:
                hw.write("tag,freq\n")
                for tag, freq in sorted(person_data.items(), key=lambda r: -r[1]):
                    hw.write(f"{tag},{freq}\n")

    with (Path("..") / "data" / "free_form_per_year_abs_number.csv").open("w") as hw:
        years = set()
        for vals in per_year.values():
            for year in vals:
                years.add(year)
        years = sorted(years)
        hw.write(",".join(["tag"] + years) + "\n")
        for tag, stats in per_year.items():
            if sum(stats.values()) < 10:
                continue
            r = dict.fromkeys(years, 0)
            r.update(stats)
            hw.write(",".join([tag] + [str(r[k]) for k in years]) + "\n")


if __name__ == '__main__':
    main()
