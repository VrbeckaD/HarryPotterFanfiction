try:
    from nltk.tokenize.nist import NISTTokenizer
except LookupError:
    import nltk

    nltk.download('perluniprops', quiet=True)

    from nltk.tokenize.nist import NISTTokenizer


nist = NISTTokenizer()


def tokenizer(text):
    return nist.tokenize(text)


if __name__ == '__main__':
    from filter_file import extract_article_text

    for file in extract_article_text():
        print(tokenizer(file))