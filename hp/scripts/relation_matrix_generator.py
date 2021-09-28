import argparse
import csv
import itertools
from collections import Counter, defaultdict
import logging
import re

import holoviews as hv
from holoviews import dim
import numpy as np
import pandas as pd

from hp import FULL_CATALOGUE_PATH, RELATIONS_HTML_PATH, LOVERS_CSV_PATH


hv.extension('matplotlib')
hv.output(fig='svg', size=300)

logger = logging.getLogger(__name__)
CATEGORIES = ["all", "slash", "het", "explicit"]
FILES = {
    category: str(LOVERS_CSV_PATH / ("lovers_" + category + ".csv"))
    for category in CATEGORIES
}


def rotate_label(plot, element):
    labels = plot.handles["labels"]
    for annotation in labels:
        angle = annotation.get_rotation()
        if 90 < angle < 270:
            annotation.set_rotation(180 + angle)
            annotation.set_horizontalalignment("right")


def log(val):
    if val < 10:
        return 0
    elif val < 50:
        return 3
    elif val < 100:
        return 5
    elif val < 200:
        return 10
    elif val < 500:
        return 30
    elif val < 1000:
        return 50
    elif val < 2000:
        return 100
    else:
        return 150


def clean(line):
    orig = line
    line = line.replace("&quot;", '"')
    line = line.replace("'", '"')
    line = line.replace("Tom Riddle | Voldemort", "Voldemort")
    line = line.replace("Tom Riddle |Voldemort", "Voldemort")
    line = line.replace("Tom Riddle| Voldemort", "Voldemort")
    line = line.replace("Tom Riddle|Voldemort", "Voldemort")
    line = line.replace("Voldemort (Tom Riddle jr.) ", "Voldemort")
    line = re.sub(r"Voldemort [(]T[^)]+[)]\s*", "Voldemort", line)
    line = line.replace("Tom Marvolo Riddle", "Tom Riddle")
    line = re.sub("Tom Riddle Jr[.]?", "Tom Riddle", line)
    line = line.replace("You", "Reader")
    line = line.replace("(s)", "")
    line = line.replace("- Relationship ", "")
    line = line.replace("(implied) ", "")
    line = line.replace("- implied", "")
    line = line.replace("implied ", "")
    line = line.replace("Ronald Weasley", "Ron Weasley")
    line = line.replace("Narcissa Malfoy", "Narcissa Black Malfoy")
    line = line.replace("Bellatrix Lestrange", "Bellatrix Black Lestrange")
    line = line.replace("FOC", "Original Female Character")
    line = line.replace("OC", "Original Character")
    line = line.replace("Harry James Potter", "Harry Potter")
    line = line.replace("Harry/", "Harry Potter/")
    line = line.replace("Harry /", "Harry Potter/")
    line = line.replace("Lilly Potter", "Lily James Potter")
    line = line.replace("Lily Potter", "Lily Evans Potter")
    line = line.replace("Alastor \"Mad-Eye\" Moody", "Alastor Moody")
    line = line.replace("James \"Bucky\" Barnex", "James Barnes")
    line = line.replace("Ben Solo | Kylo Ren", "Kylo Ren")
    line = line.replace("Ben Solo |Kylo Ren", "Kylo Ren")
    line = line.replace("Ben Solo| Kylo Ren", "Kylo Ren")
    line = line.replace("Ben Solo|Kylo Ren", "Kylo Ren")
    line = line.replace('(Marvel)', "")
    line = line.replace('(Good Omens)', "")
    line = line.replace("Percival Graves | Gellert Grindenwald ", "Gellert_Grindelwald_pretending_Percival_Graves")
    line = re.sub(r"\s*-\s*", " - ", line)
    line = line.replace('"', "")
    if "/" not in line:
        print(orig, "=>", line)
    return line


def load_relation_freqs(selection="all", language="all"):
    """Načte katalog a vrátí seznam s počty jednotlivých vztahů, např. [('Delphi/Rodolphus Lestrange', 3), ...].

    Args:
        selection: filter one of all/explicit/slash/het
        language: all/English/...
    Returns:
        list of pairs relation, freq
    """
    shiplist_raw = []
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
            if "/" in cols["lovers"]:
                shiplist_raw.append(clean(cols["lovers"]))

    return sorted(Counter(shiplist_raw).items(), key=lambda x: x[1], reverse=True)


def count_freqs(freqs):
    """Spočítá výskyty postavy v párování a seřadí podle něj. Např. [('Cormac McLaggen', 61), ...]"""
    character_in_relation_freq = defaultdict(int)
    for relation, score in freqs:
        names = relation.split("/")
        for name in names:
            character_in_relation_freq[name] += score
    return sorted(Counter(character_in_relation_freq).items(), key=lambda x: x[1], reverse=True)


def create_html(data, matrix, cat):
    body = []
    beautify_chars = [name.replace("_", "&nbsp;") for name in data]
    for row_number, name in enumerate(beautify_chars):
        start = f"<tr>"
        start += f"<td style='width: 150px'>{name}</td>"
        for col_number in range(len(beautify_chars)):
            value = matrix[row_number, col_number]
            if col_number == row_number:
                if value > 0:
                    start += f"<td style='background-color: darkred'>{value}</td>"
                else:
                    start += f"<td style='background-color: white; color: lightgray'>{value}</td>"
            elif col_number > row_number:
                # obarvení podle hodnoty
                if value >= 500:
                    start += f"<td style='background-color: #caffc4'>{value}</td>"
                elif value >= 100:
                    start += f"<td style='background-color: #c2e3bf'>{value}</td>"
                elif value == 0:
                    start += f"<td style='background-color: white; color: lightgray'>{value}</td>"
                else:
                    start += f"<td style='background-color: #829487'>{value}</td>"
            else:
                start += "<td></td>"
        start += "</tr>\n"
        body.append(start)

    html_table = f"""<!doctype html>
    <html lang="cs">
    <head>
        <meta charset="utf-8" />
        <title>HP relations</title>
        <style>
            table {{table-layout:fixed; width: 5000px}}
            td {{width: 50px; height: 50px; vertical-align: middle; text-align: center}}
            td:td:nth-of-type(1)  {{width: 150px;}}
        </style>
    </head>
    <body>
    <table>
        <thead style="writing-mode: vertical-lr; text-orientation: use-glyph-orientation; text-align: right">
            <th>&nbsp;</th><th>{"</th><th>".join(beautify_chars)}</th>
        </thead>
        {"".join(body)}
    </table>
    </body>
    </html>
    """
    target = RELATIONS_HTML_PATH
    if cat:
        target = str(target).replace(".html", "_" + cat + ".html")

    with open(target, "w") as hw:
        hw.write(html_table)


def main(min_freq=50, category="all", language="all"):

    shiplist = load_relation_freqs(category, language)
    sorted_char_in_relations = count_freqs(shiplist)
    filtered_char_in_ship_best = [(char, freq) for char, freq in sorted_char_in_relations if freq >= min_freq]

    logger.info(f"Let keep only names with frequency > {min_freq} to obtain {len(filtered_char_in_ship_best)} names.")

    empty = np.zeros((len(filtered_char_in_ship_best), len(filtered_char_in_ship_best)), dtype=int)

    filtered_shiplist = []
    filtered_char_without_freq = [ship for ship, _ in filtered_char_in_ship_best]

    def index(name):
        """Harry je na nulté pozici, když mu zadám Harry, vrátí 0."""
        return filtered_char_without_freq.index(name)

    logger.info("Perform check to find out self-relations. They shouldn't be frequent, but they are possible.")
    for ship, count in shiplist:
        names = ship.split("/")
        if all(name in filtered_char_without_freq for name in names):
            filtered_shiplist.append((ship, count))
            if len(set(names)) == 1:
                logger.info("    * self-relation %s: %d", names[0], count)
                empty[index(names[0]), index(names[0])] += count
            else:
                for left_name, right_name in itertools.combinations(names, 2):
                    empty[index(left_name), index(right_name)] += count
                    empty[index(right_name), index(left_name)] += count

    logger.info(f"The final matrix contains {len(filtered_shiplist)} lovers for category {category}.")

    create_html(filtered_char_without_freq, empty, category)

    target = FILES[category]
    if language != "all":
        target = target.replace(".csv", f"_{language}.csv")

    pd.DataFrame(data=empty,
                 index=[i.replace(" ", "_") for i in filtered_char_without_freq],
                 columns=[i.replace(" ", "_") for i in filtered_char_without_freq]
                 ).to_csv(target)

    output = [(re.sub("/?Harry Potter/?", "", i), c) for i, c in filtered_shiplist[1:] if "Harry" in i and c >= 50]
    out = '\n    * '.join(f"{i} ({c})" for i, c in output if i)
    print(f"To illustrate outputs, the relations of Harry Potter with freq >= 50 are following:\n    * {out}")

    data = pd.read_csv(target)
    matrix = data.to_numpy()
    keys = tuple(matrix[:, 0])
    key2index = {k: i for i, k in enumerate(keys)}

    def node_name(original):
        index = key2index[original]
        total = sum(int(i) for i in matrix[index, 1:])
        if total < 10:
            return "others"
        if total < 200:
            return ""
        return original.replace("_", " ")

    routes = []
    for r, row in enumerate(matrix):
        key = row[0]
        for c, col in enumerate(row[1:], start=1):
            if r >= c - 1:
                if int(matrix[r, c]) > 10:
                    routes.append((key2index[key], c - 1, log(int(matrix[r, c]))))
    routes = pd.DataFrame.from_records(data=routes, columns=["source", "target", "value"])

    new_nodes = hv.core.data.Dataset(
        pd.DataFrame.from_records([(key2index[key], node_name(key), key) for key in keys],
                                  columns=["index", "name", "group"]), 'index')

    graph = hv.Chord((routes, new_nodes))
    graph.opts(cmap='Category20',
               edge_cmap='Category20',
               edge_color=dim('source').str(),
               labels='name',
               node_color=dim('index').str(),
               hooks=[rotate_label]
               )
    hv.save(graph, target.replace(".csv", ".svg"), fmt="svg", backend="matplotlib",
            title=f"Lovers for {category}")

    matrix = data.to_numpy()
    names = matrix[:, 0]
    items = matrix[:, 1:]

    max_values = []
    for rn, row in enumerate(items):
        for cn, value in enumerate(row):
            if rn >= cn:
                max_values.append((value, "/".join(sorted([names[cn], names[rn]]))))
    max_values.sort(key=lambda rec: -rec[0])
    pd.DataFrame(data=max_values[:100], columns=["freq", "lovers"]).to_csv(target.replace(".csv", "_top100.csv"))

    with open(target.replace(".csv", "_top100_people.csv"), "w") as hw:
        for name, count in sorted(zip(names, [sum(row) for row in items]), key=lambda r: -r[1])[:100]:
            hw.write(f"{name},{count}\n")


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description='Generate lovers matrices.')
    parser.add_argument('--min-count', '-m', dest='freq', type=int, default=50,
                        help='minimal frequency of character to be displayed')
    parser.add_argument('--filter', '-f', dest='filter', default="all",
                        help='filter: all/slash/het/explicit')
    parser.add_argument('--language', '-l', dest='language', default="all",
                        help='language: all/English')

    args = parser.parse_args()

    main(args.freq, args.filter, args.language)
