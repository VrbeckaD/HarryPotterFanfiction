import csv
import logging
import re
from pathlib import Path
from typing import Tuple, List

import requests

from hp import URL_LISTS_DOWNLOAD_PATH, FULL_DOWNLOAD_PATH, FULL_CATALOGUE_PATH, delay

logger = logging.getLogger(__file__)
if not FULL_DOWNLOAD_PATH.is_dir():
    FULL_DOWNLOAD_PATH.mkdir(exist_ok=True)

TEXT_URL_PREFIX = "https://archiveofourown.org/works/"
CATEGORIES = ["filename", "title", "rating", "ship", "language", "category", "lovers",
              "wordcount", "published", "hits", "freeform_tags", "kudos", "comments", "bookmarks", "archive_warnings"]
RETRY = "Retry later"
RE_ERROR = re.compile("404[\n ]+Error", flags=re.IGNORECASE)


def get_text_from_web(text_path: Path, text_block_with_id: str) -> Tuple[str, str]:
    """Download HTML text from AO3 website if not already downloaded.
    Return both filtered text and original HTML.

    Args:
        text_path: where to store text
        text_block_with_id: HTML code where is text stored

    Returns:
        Tuple clean text and full HTML block

    """
    text_with_headers_path = text_path.with_name(f"{text_path.name.split('.')[0]}_full.txt")
    if text_path.is_file() and text_with_headers_path.is_file():
        content = text_path.read_text(encoding="utf-8")
        full_content = text_with_headers_path.read_text(encoding="utf-8")
        if RETRY not in content and RETRY not in full_content and not RE_ERROR.search(full_content):
            return content, full_content
    url_id = re.search(r'<a href="/works/(\d+)">', text_block_with_id).groups()[0]
    logger.info("Downloading %s", url_id)
    url = f"{TEXT_URL_PREFIX}{url_id}?view_adult=true"
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 ' \
                 '(KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent}
    delay()
    full_content = requests.get(url, allow_redirects=True, headers=headers).text
    if RE_ERROR.search(full_content):
        raise FileNotFoundError(f"File {url} is not accessible anymore.")
    while RETRY in full_content:
        delay(minimum=5, maximum=30, multiplier=30.0)
        full_content = requests.get(url, allow_redirects=True, headers=headers).text
        logger.warning("Redownloading url %s.", url)
        if RE_ERROR.search(full_content):
            raise FileNotFoundError(f"File {url} is not accessible anymore.")
    text_with_headers_path.write_text(full_content, encoding="utf-8")

    try:
        content = re.search(
            "<!--(?:main|chapter) content-->(.*)<!--/(?:main|chapter)-->",
            full_content,
            flags=re.DOTALL).groups()[0]
    except AttributeError:
        print(full_content)
        raise
    text_path.write_text(content, encoding="utf-8")

    return content, full_content


def parse(target_name: str, part: str, full_text: str) -> List[str]:
    warnings = []
    article_result = {"filename": target_name}
    # title
    _title_prepare = re.split("</a>", part)[0]
    title = re.split(">", _title_prepare)[-1]
    article_result["title"] = title
    # rating -- age accessibility
    rating = re.search(r"rating-(\w+)", part).groups()[0]
    article_result["rating"] = rating
    # ship: who is in love with whom by gender
    # F/F
    # Female/Female relationships.
    # F/M
    # Female/Male relationships.
    # Gen
    # General: no romantic or sexual relationships, or relationships which aren't the main focus of the work.
    # M/M
    # Male/Male relationships.
    # Multi
    # More than one kind of relationship or a relationship with multiple partners.
    # Other
    # Relationships not covered by the other categories.
    try:
        ship = re.search('class="category-slasdecxh category" title="(./.)"', part).groups()[0]
    except AttributeError:
        for tag in ("F/F", "F/M", "Gen", "MPM", "Multi", "Other"):
            if tag in full_text:
                ship = tag
                break
        else:
            raise
    article_result["ship"] = ship
    # language
    language_prepare = re.split("</dd>", part)[0]
    language = re.split(">", language_prepare)[-1]
    article_result["language"] = language
    # category (slash/gen/het/multi)
    category = re.search(r"category-(\w+)", part).groups()[0]
    article_result["category"] = category
    # lovers, name/name or name/name/name or none
    try:
        lovers = re.sub("<[^>]*>", "", re.search("<li class='relationships'>((?:(?<!</).)*)", part).groups()[0])
        lovers = lovers.replace("</", "").replace(" &amp; ", "/")
        lovers = "/".join(sorted(item.strip() for item in lovers.split("/")))
    except AttributeError:
        warnings.append("no lovers")
        lovers = "none"
    article_result["lovers"] = lovers
    # wordcount
    article_result["wordcount"] = re.search(r'<dd class="words">((?:\d*,?)+)</dd>', part).groups()[0].replace(",", "")
    # published datetime or or "missing data"
    try:
        published = re.search(r'<dd class="published">(\d\d\d\d-\d\d-\d\d)</dd>', full_text).group(1)
    except AttributeError:
        warnings.append("missing publishing date")
        published = "missing data"
    article_result["published"] = published
    # hits: clicks on article
    try:
        hits = re.search(r'<dd class="hits">(\d+)</dd>', full_text).group(1)
    except AttributeError:
        warnings.append("missing hits info")
        hits = "missing data"
    article_result["hits"] = hits
    # freeform_tags: author defined tags
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
    except AttributeError:
        warnings.append("no freeform tags")
        freeform_tags = ["none"]
    article_result["freeform_tags"] = '|'.join(freeform_tags)  # propojí jednotlivé tagy svislítkem

    for feature in ("kudos", "comments", "bookmarks"):
        try:
            article_result[feature] = re.search(
                rf'<dd class="{feature}"><a href="[^"]+">(\d+)</a></dd>', full_text).group(1)
        except AttributeError:
            try:
                article_result[feature] = re.search(rf'<dd class="{feature}">(\d+)</dd>', full_text).group(1)
            except AttributeError:
                article_result[feature] = "0"
                warnings.append(f"missing {feature}")

    # archive_warnings
    searched = re.search('<dd class="warning tags">((?:\n|.)*?)</dd>', full_text)
    if searched:
        tags = []
        block = searched.group(1)
        for tag in re.finditer("<a[^>]*>([^>]*)</a>", block):
            tags.append(tag.group(1))
        article_result["archive_warnings"] = "/".join(tags)
    else:
        article_result["archive_warnings"] = "none"
        warnings.append("no archive warnings")
    if warnings:
        logger.warning("%s: %s", target_name, "; ".join(warnings))
    return [article_result[category] for category in CATEGORIES]


def main():
    """
    Create CSV catalogue with all interesting meta-tags for all documents
    mentioned in URL_LISTS_DOWNLOAD_PATH and able to download.
    """
    url_lists_paths = sorted(
        [path for path in URL_LISTS_DOWNLOAD_PATH.iterdir()
         if path.suffix == ".txt" and path.name.split(".")[0].isdigit()],
        key=lambda r: int(r.name.split(".")[0]))

    with FULL_CATALOGUE_PATH.open("w", encoding="utf-8") as csv_file:
        catalogue_writer = csv.writer(csv_file, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        catalogue_writer.writerow(CATEGORIES)

        for signpost_no, file_path in enumerate(url_lists_paths, start=1):
            path = URL_LISTS_DOWNLOAD_PATH / file_path.name
            code = file_path.name.split(".")[0]
            text = path.read_text(encoding="utf-8")

            # each segment is separated by `<!--title, author, fandom-->` HTML code
            parts = re.split("<!--title, author, fandom-->", text)[1:]
            if len(parts) != 20:
                logger.warning("%d/%s/%d", signpost_no, code, len(parts))

            for no, part in enumerate(parts, start=1):
                # nové soubory pojmenováváme jako cislorozcestniku_poradinastrance.txt
                target_name = f"{code}_{no}.txt"
                text_path = FULL_DOWNLOAD_PATH / target_name
                try:
                    text, full_text = get_text_from_web(text_path, part)
                except FileNotFoundError:
                    logger.error("Giving up on file %s.", target_name)
                    continue
                catalogue_writer.writerow(parse(target_name, part, full_text))


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)
    main()
