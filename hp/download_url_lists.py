import argparse
import logging
import requests

from hp import URL_LISTS_DOWNLOAD_PATH, delay


logger = logging.getLogger(__name__)
if not URL_LISTS_DOWNLOAD_PATH.is_dir():
    URL_LISTS_DOWNLOAD_PATH.mkdir(exist_ok=True)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description="Each url list contains 20 links. How many url lists to download?")
    parser.add_argument("-u", "--url-list-count", dest="total", default=5000, type=int,
                        help="How many pages to crawl, cannot be more than 5000.")
    args = parser.parse_args()

    for page_no in range(1, min(5000, args.total) + 1):
        url = f"https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?page={page_no}"
        delay()
        content = requests.get(url, allow_redirects=True).text
        while "Retry later" in content:
            delay(minimum=3.0, maximum=6.0, multiplier=6.0)
            content = requests.get(url, allow_redirects=True).text
            logger.warning("Repeating for url %s.", url)
        (URL_LISTS_DOWNLOAD_PATH / f'{page_no}.txt').write_text(content)
        if page_no % 50 == 0:
            logger.info(f"Downloaded page with url id {page_no}.")
    logger.info("Downloaded all requested url lists.")
