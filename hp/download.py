# encoding: utf8
import requests  # downloading url
import time
import random
import os
import codecs

from hp import DOWNLOAD_PATH

if not os.path.isdir(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)

if __name__ == '__main__':

    for i in range(0, 5001):
        print(i)
        url = "https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?page={}".format(i)
        time.sleep(random.random() / 4)
        text = requests.get(url, allow_redirects=True).text
        with codecs.open("{}/{}.txt".format(DOWNLOAD_PATH, i), "w", "utf8") as hw:
            hw.write(text)


