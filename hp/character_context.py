from tokenizer import tokenizer
from filter_file import extract_article_text
import spacy
import numpy

nlp = spacy.load("en_core_web_sm")

if __name__ == '__main__':
    adjectives = []  # sem ulozime vse, co najdeme
    for article in extract_article_text():  # pro kazdy text, co mame
        tokens = tokenizer(article)  # nechme si z nej udelat tokeny
        pos_tags = [token.pos_ for token in nlp(tokens)]  # a ted tokenum priradme vetnz clen POS
        print(pos_tags)
        for position, word in enumerate(tokens):
            if word in ("Snape", "Severus", "Severe"):
                # jdeme dozadu, dokud jsou povolene tagy dozadu, jako JJ
                allowed_back_tags = ("JJ", "JJR", "JJS")
                for back in range(1, 10):
                    if pos_tags[position - back][1] in allowed_back_tags:
                        adjectives.append(pos_tags[position - back][0])
                    else:
                        break
                for forward in range(1, 10):
                    if pos_tags[position + forward][1] in allowed_back_tags:
                        adjectives.append(pos_tags[position - back][0])
                    elif pos_tags[position + forward][0] in ("is", "was", "were", "will", "be", "isn't", "not"):
                        print("is")
                        continue
                    else:
                        break
        print(adjectives)