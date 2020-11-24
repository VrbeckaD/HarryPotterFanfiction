import os
from collections import defaultdict

if __name__ == '__main__':
    name_freq = defaultdict(int)
    with open(os.path.join("../data", "names.txt")) as names_file:
        names = [line.rstrip("\n") for line in names_file.readlines()]

    for name in names:
        variants = name.replace("/", " ").split(" ")
        for variant in variants:
            name_freq[variant] += 1

    for name in names:
        variants = name.replace("/", " ").split(" ")
        for variant in variants:
            if name_freq[variant] == 1:
                print(variant, "=>", name)
        print(name, "=>", name)


    # for no_article, article in enumerate(extract_article_text()):  # pro kazdy text, co mame
