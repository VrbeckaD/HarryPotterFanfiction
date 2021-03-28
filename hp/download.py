# encoding: utf8
import requests  # downloading url
import time
import random
import os
import codecs
import sys

from hp import DOWNLOAD_PATH


if not os.path.isdir(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)


if __name__ == '__main__':

    if len(sys.argv) == 2 and isinstance(sys.argv[1], str) and sys.argv[1].isdigit():
        try:
            total = int(sys.argv[1])
            if total <= 0:
                total = 5000
        except ValueError:
            total = 5000
    else:
        total = 5000

    for i in range(0, total):
        url = "https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?page={}".format(i)
        time.sleep(random.random() / 4)
        text = requests.get(url, allow_redirects=True).text
        with codecs.open("{}/{}.txt".format(DOWNLOAD_PATH, i), "w", "utf8") as hw:
            hw.write(text)
        if i % 10 == 0:
            print(f"Downloaded page with url id {i}.")
    print("Downloaded all.")
