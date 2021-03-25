import codecs
import os
import random
import re
import time
import csv
from typing import Tuple

import requests

from hp import DOWNLOAD_PATH, FULLDOWNLOAD_PATH

if not os.path.isdir(FULLDOWNLOAD_PATH):
    os.makedirs(FULLDOWNLOAD_PATH)


TEXT_URL_PREFIX = "https://archiveofourown.org/works/"
CATEGORIES = ["filename", "title", "rating", "ship", "language", "category", "lovers",
              "wordcount", "published","hits", "freeform_tags"]


def get_text_from_web(text_path: str, text_block_with_id: str) -> Tuple[str, str]:
    """Stáhne soubor z AO3, pokud už není stažený.
    Vrací jak vyfiltrovaný text, tak i HMTL elementy pro extrahování tagů.

    Args:
        text_path: kam se uloží, když ještě není stažený
        text_block_with_id: část HTML, kde se nachází ID dokumentu


    Returns:
        dvojice čistý text a komplet HTML

    """
    try:
        text_with_headers_path = str(text_path).replace(".txt", "_full.txt")
        if not os.path.isfile(text_path) or not os.path.isfile(text_with_headers_path):
            url = TEXT_URL_PREFIX + re.search(r'<a href="/works/(\d+)">', text_block_with_id).groups(1)[0] + "?view_adult=true"
            time.sleep(random.random() / 2)  # čekat 0 až 0.5 sekundy před stažením
            user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
            headers = {'User-Agent': user_agent}  # nastavení hlaviček pro simulaci přístupu přes prohlížeč
            full_content = requests.get(url, allow_redirects=True, headers=headers).text
            with codecs.open(text_with_headers_path, "w", "utf8") as filehandler:
                filehandler.write(full_content)

            if not os.path.isfile(text_path):
                content = re.search(
                    "<!--(?:main|chapter) content-->(.*)<!--/(?:main|chapter)-->",    #první argument
                    full_content,                                                            # druhý argument
                    flags=re.DOTALL).groups(1)[0] #třetí argument
                with codecs.open(text_path, "w", "utf8") as filehandler:
                    filehandler.write(content)
            else:
                with codecs.open(text_path, "r", "utf8") as filehandler:
                    content = filehandler.read()
        else:
            with codecs.open(text_path, "r", "utf8") as filehandler:
                content = filehandler.read()
            with codecs.open(text_with_headers_path, "r", "utf8") as filehandler:
                full_content = filehandler.read()
        return content, full_content
    except:
        return "", ""  # pokud narazí na chybu, pokračujeme dále s 2 prázdnými dokumenty


def main():
    """Vytvoří katalog se všemi metatagy pro všechny dokumenty zmíněné v rozcestnících ve složce DOWNLOAD_PATH."""
    with codecs.open('HP_catalogue.csv', 'w', encoding="utf8") as csvfile:
        catalogue_writer = csv.writer(csvfile, delimiter=',',
                                      quotechar='"', quoting=csv.QUOTE_MINIMAL)
        catalogue_writer.writerow(CATEGORIES)

        all_known_files = [name for name in os.listdir(DOWNLOAD_PATH)
                           if name.endswith(".txt") and name.split(".")[0].isdigit()]
        for signpost_no, filename in enumerate(all_known_files):
            path = os.path.join(DOWNLOAD_PATH, filename)
            with codecs.open(path, encoding="utf8") as f:
                text = f.read()

            parts = re.split("<!--title, author, fandom-->", text)[1:]  # každý segment je oddělen touto HTML poznámkou
            for no, part in enumerate(parts):
                # nové soubory pojmenováváme jako cislorozcestniku_poradinastrance.txt
                target_name = filename.replace(".txt", "") + "_" + str(no + 1) + ".txt"
                text_path = os.path.join(FULLDOWNLOAD_PATH, target_name)
                text, full_text = get_text_from_web(text_path, part)

                # CATEGORIES["filename"]
                subresult = [target_name]
                # CATEGORIES["title"]
                _title_prepare = re.split("</a>", part)[0]
                title = re.split(">", _title_prepare)[-1]
                subresult.append(title)
                # CATEGORIES["rating"] vhodnost podle věku
                rating = re.search(r"rating-(\w+)", part).groups(1)[0]
                subresult.append(rating)
                # CATEGORIES["ship"] vyhledá kdo s kým se miluje
                try:
                    ship = re.search('class="category-slasdecxh category" title="(./.)"', part).groups(1)[0]
                except:
                    ship = "none"
                subresult.append(ship)
                # CATEGORIES["language"] vyhledá jazyk
                language_prepare = re.split("</dd>", part)[0]
                language = re.split(">", language_prepare)[-1]
                subresult.append(language)
                # CATEGORIES["category"] vyhledá category (slash/gen/het/multi)
                category = re.search(r"category-(\w+)", part).groups(1)[0]
                subresult.append(category)
                # CATEGORIES["lovers"] vyhledá lovers, pokud nejsou, dá "none" text
                try:
                    sublovers = re.search("<li class='relationships'>((?:(?<!</).)*)", part).groups(1)[0]
                    lovers = re.sub("<[^>]*>", "", sublovers)
                    lovers = lovers.replace("</", "").replace(" &amp; ", "/")
                    left_lover, right_lover = lovers.split("/")
                    lovers = "/".join(sorted([left_lover, right_lover]))
                except:
                    lovers = "none"
                subresult.append(lovers)
                # CATEGORIES["wordcount"] vyhledá počet slov
                wordcount = re.search(r'<dd class="words">((?:\d*,?)+)</dd>', part).groups(1)[0].replace(",", "")
                subresult.append(wordcount)
                # CATEGORIES["ship"] vyhledá datum publikování
                try:
                    published = re.search(r'<dd class="published">(\d\d\d\d-\d\d-\d\d)</dd>', full_text).group(1)
                except:
                    published = "missing data"
                subresult.append(published)
                # CATEGORIES["hits"] vyhledá počet kliknutí na povídku
                try:
                    hits = re.search(r'<dd class="hits">(\d+)</dd>', full_text).group(1)
                except:
                    hits = "missing data"
                subresult.append(hits)
                # CATEGORIES["freeform_tags"] vyhledá další tagy, kterými autoři označují povídky
                try:
                    # vyhledá daný obal/prvek v HTML, příprava na extrahování freeform tagů
                    raw_freeform_tags = re.search(r'<dd class="freeform tags">((.|\n)*?)</dd>', full_text).group(1)
                    freeform_tags = [
                        item.replace('|', '/')
                        for item in re.sub(r'<[^>]+>', 'a12b', raw_freeform_tags).split('a12b')
                        if item.strip()]
                    # nahradí všechna svislítka | v tazích lomítkem, aby se nepletlo s více tagy
                    # nahradí značky šipek stringem v tazích a potom podle něj rozseká
                    # necháme jen položky, které po odstranění mezer mají alespoň jeden znak, tj. nejsou prázdné
                except:
                    freeform_tags = ["none"]
                subresult.append('|'.join(freeform_tags)) # propojí jednotlivé tagy svislítkem
                print("\t".join([f"{signpost_no + 1}/{no + 1}."] + subresult))
                catalogue_writer.writerow(subresult)


if __name__ == '__main__':
    main()
