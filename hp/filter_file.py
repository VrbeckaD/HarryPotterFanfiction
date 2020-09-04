from hp import FULLDOWNLOAD_PATH, DOWNLOAD_PATH, CSV_CATALOGUE_PATH # říká, že z tohoto souboru, importuj proměnnou nebo N proměnných
import os
from io import StringIO
from html.parser import HTMLParser
import codecs

class MLStripper(HTMLParser): # HTML parser, zbaví plné verze článků HTML prvků a zanechá mi jenom čistý text fanfikce
    def __init__(self):
        super().__init__()
        self.reset()
        self.strict = False
        self.convert_charrefs= True
        self.text = StringIO()
    def handle_data(self, d):
        self.text.write(d)
    def get_data(self):
        return self.text.getvalue()

def strip_tags(html):
    s = MLStripper()
    s.feed(html)
    return s.get_data()


def iter_files():
    with open(CSV_CATALOGUE_PATH) as catalogue_file:
        lines = catalogue_file.readlines()  #seznam vet = stringu
        records = [line.strip("\n").split(";") for line in lines] #n = zkratka pro newline, seznam seznamu slov
        lookup_dictionary = dict((record[0], record[1:]) for record in records)
    for filename in os.listdir(FULLDOWNLOAD_PATH):
        try:
            record = lookup_dictionary[filename]
            yield (record, filename) # vyhazuje všechny názvy souborů
        except:
            print("soubor_neexistuje", filename)  # pokud nenajde v CSV soubor odpovídající název (1321_1 třeba), tak místo toho vypíše soubor_neexistuje


def filter(language="English", word_count=600): # vyfiltruje z CSV katalogu položky, které jako jazyk mají angličtinu + počet slov, aby zůstaly texty delší než 600 slov (cca 2 A4)
    for record, filename in iter_files():
        if record[3] != language:
            continue
        try:
            if int(record[6]) < word_count:
                continue
        except:
            continue
        yield filename

def extract_article_text(): # extrahuje čisté texty fanfikcí ze souboru
    for filename in filter():
        with codecs.open(os.path.join(FULLDOWNLOAD_PATH, filename), "r", "utf-8") as file:
            text = file.read()

        yield strip_tags(text)

