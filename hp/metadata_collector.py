import codecs
import os
import random
import re
import time
import csv

import requests

from hp import DOWNLOAD_PATH, FULLDOWNLOAD_PATH

if not os.path.isdir(FULLDOWNLOAD_PATH):
    os.makedirs(FULLDOWNLOAD_PATH)

result = []


def get_text(text_path):
    """

    Args:
        text_path: #sem dopsat popisky, co to dělá

    Returns:

    """
    if not os.path.isfile(text_path):  # tady budeme stahovat soubor
        url = "https://archiveofourown.org/works/" + re.search(r'<a href="/works/(\d+)">', part).groups(1)[
            0] + "?view_adult=true"
        time.sleep(random.random() / 2)
        print(url)
        user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
        headers = {'User-Agent': user_agent}
        content = requests.get(url, allow_redirects=True, headers=headers).text # na tomto místě fejkujeme prohlížeč
        try:
            content = re.search(
                "<!--(?:main|chapter) content-->(.*)<!--/(?:main|chapter)-->",    #první argument
                content,                                                            # druhý argument
                flags=re.DOTALL).groups(1)[0] #třetí argument
            with codecs.open(text_path, "w", "utf8") as hw:
                hw.write(content)
        except:
            return ""    # pokud narazí na chybu, pokračujeme dále s prázdným dokumentem
    else:
        with codecs.open(text_path, "r", "utf8") as hw:
            content = hw.read()
    return content

with codecs.open('HP_catalogue.csv', 'w', encoding="utf8") as csvfile:
    catalogue_writer = csv.writer(csvfile, delimiter=',',
                                  quotechar='"', quoting=csv.QUOTE_MINIMAL)
    catalogue_writer.writerow(["filename","title", "rating", "ship", "language", "category", "lovers", "wordcount", "published","hits"])

    for filename in [str(name) + ".txt" for name in range(1, 4300)]:
        path = os.path.join(DOWNLOAD_PATH, filename)
        with codecs.open(path, encoding="utf8") as f:
            text = f.read()
        print(text)
        parts = re.split("<!--title, author, fandom-->", text)[1:]
        for no, part in enumerate(parts):
            targetname = filename.replace(".txt", "") + "_" + str(no + 1) + ".txt"
            text_path = os.path.join(FULLDOWNLOAD_PATH, targetname)
            text = get_text(text_path)
            subresult = [targetname]
            # vyhledá title
            _title_prepare = re.split("</a>", part)[0]
            title = re.split(">", _title_prepare)[-1]
            subresult.append(title)
            # vyhledá rating
            rating = re.search(r"rating-(\w+)", part).groups(1)[0]
            subresult.append(rating)
            # vyhledá kdo s kým se miluje
            try:
                ship = re.search('class="category-slasdecxh category" title="(./.)"', part).groups(1)[0]
            except:
                ship = "none"
            subresult.append(ship)
            result.append(subresult)
            # vyhledá jazyk
            language_prepare = re.split("</dd>", part)[0]
            language = re.split(">", language_prepare)[-1]
            subresult.append(language)
            # vyhledá category (slash/gen/het/multi)
            category = re.search(r"category-(\w+)", part).groups(1)[0]
            subresult.append(category)
            # vyhledá lovers
            try:
                sublovers = re.search("<li class='relationships'>((?:(?<!</).)*)", part).groups(1)[0]
                lovers = re.sub("<[^>]*>", "", sublovers)
                lovers = lovers.replace("</", "").replace(" &amp; ", "/")
                left_lover, right_lover = lovers.split("/")
                lovers = "/".join(sorted([left_lover, right_lover]))
            except:
                lovers = "none"
            subresult.append(lovers)
            # vyhledá počet slov
            wordcount = re.search(r'<dd class="words">((?:\d*,?)+)</dd>', part).groups(1)[0].replace(",", "")
            subresult.append(wordcount)
            # vyhledá datum publikování
            published= re.search (r'<dd class="published">(\d\d\d\d-\d\d-\d\d)</dd>', part).group(1)[0]
            subresult.append(published)
            # vyhledá počet kliknutí na povídku
            hits= re.search(r'<dd class="hits">\d+</dd>', part).group(1)
            subresult.append(hits)
           
            print(subresult)
            catalogue_writer.writerow(subresult)
            

    for line in result:
        print("\t".join(line))


if __name__ == '__main__':
    pass
