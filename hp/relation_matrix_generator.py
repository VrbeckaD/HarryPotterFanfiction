import argparse
import re
import sys
from collections import Counter, defaultdict

import pandas as pd
import numpy as np

from hp import FULL_CATALOGUE_PATH, RELATIONS_HTML, LOVERS


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


def load(selection=None):
    """Načte katalog a vrátí seznam s počty jednotlivých vztahů, např. [('Delphi/Rodolphus Lestrange', 3), ...]."""
    with open(FULL_CATALOGUE_PATH) as h:
        lines = h.readlines()
    shiplist_raw = []
    for line in lines[1:]:
        cols = line.split(",")
        if selection == "explicit":
            if cols[2] != "explicit":
                continue
        if selection == "slash":
            if "slash" not in cols[5]:
                continue
        if selection == "het":
            if "het" not in cols[5]:
                continue
        if "/" in cols[6]:
            shiplist_raw.append(clean(cols[6]))
    return sorted(Counter(shiplist_raw).items(), key=lambda x: x[1], reverse=True)


def count_freqs(freqs):
    """Spočítá výskyty postavy v párování a seřadí podle něj. Např. [('Cormac McLaggen', 61), ...]"""
    char_in_pair_freq = defaultdict(int)
    for pair, score in freqs:
        left_name, right_name = pair.split("/")
        char_in_pair_freq[left_name] += score
        char_in_pair_freq[right_name] += score
    return sorted(Counter(char_in_pair_freq).items(), key=lambda x: x[1], reverse=True)


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
    target = RELATIONS_HTML
    if cat:
        target = target.replace(".html", "_" + cat + ".html")

    with open(target, "w") as hw:
        hw.write(html_table)


def main(min_freq=50, category=None):
    if category == "none":
        category = None

    shiplist = load(category)
    sorted_char_in_pairs = count_freqs(shiplist)

    filtered_char_in_ship_103_best = [(char, freq) for char, freq in sorted_char_in_pairs if freq >= min_freq]

    print(f"Nechme si jen jména s frekvencí {min_freq} a větší, zbyde nám {len(filtered_char_in_ship_103_best)} jmen.")

    empty = np.zeros((len(filtered_char_in_ship_103_best), len(filtered_char_in_ship_103_best)), dtype=int)

    filtered_shiplist = []
    filtered_char_without_freq = [ship for ship, _ in filtered_char_in_ship_103_best]

    def index(name):
        """Harry je na nulté pozici, když mu zadám Harry, vrátí 0."""
        return filtered_char_without_freq.index(name)

    print("Nyní provedeme kontrolu a zjistíme, jestli mají postavy \"sebevztahy\". U toho vytvoříme matici vztahů.")
    for ship, count in shiplist:
        left_name, right_name = ship.split("/")
        if left_name in filtered_char_without_freq and right_name in filtered_char_without_freq:
            filtered_shiplist.append((ship, count))
            if left_name == right_name:
                print("    * Sebevztah", left_name, count)
                empty[index(left_name), index(right_name)] = count
            else:
                empty[index(left_name), index(right_name)] = count
                empty[index(right_name), index(left_name)] = count

    print(f"V matici získáme {len(filtered_shiplist)} vztahů.")

    print(category)

    create_html(filtered_char_without_freq, empty, category)

    target = LOVERS
    if category:
        target = target.replace(".csv", "_" + category + ".csv")

    pd.DataFrame(data=empty,
                 index=[i.replace(" ", "_") for i in filtered_char_without_freq],
                 columns=[i.replace(" ", "_") for i in filtered_char_without_freq]
                 ).to_csv(target)

    output = [i.replace("Harry Potter", "").replace("/", "") for i, _ in filtered_shiplist[1:] if "Harry" in i]
    out = '\n    * '.join(i for i in output if i)
    print(f"Pro ilustraci vztahy Harryho Pottera:\n    * {out}")


if __name__ == '__main__':

    parser = argparse.ArgumentParser(description='Generate lovers matrices.')
    parser.add_argument('--min-count', '-m', dest='freq', type=int, default=50,
                        help='minimal frequency of character to be displayed')
    parser.add_argument('--filter', '-f', dest='filter', default=None,
                        help='filter: none/slash/het/explicit')

    args = parser.parse_args()

    main(args.freq, args.filter)
