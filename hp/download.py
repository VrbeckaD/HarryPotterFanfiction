# encoding: utf8
import requests  # downloading url
import time
import random
import os
import codecs

from . import DOWNLOAD_PATH

if not os.path.isdir(DOWNLOAD_PATH):
    os.mkdir(DOWNLOAD_PATH)

for i in range(2976, 5001):
    url = "https://archiveofourown.org/tags/Harry%20Potter%20-%20J*d*%20K*d*%20Rowling/works?page={}".format(i)
    time.sleep(random.random() / 2)
    text = requests.get(url, allow_redirects=True).text
    with codecs.open("{}/{}.txt".format(DOWNLOAD_PATH, i), "w", "utf8") as hw:
        hw.write(text)

