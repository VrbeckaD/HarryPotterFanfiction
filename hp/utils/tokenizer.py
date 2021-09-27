try:
    from nltk.tokenize.nist import NISTTokenizer
except LookupError:
    import nltk

    nltk.download('perluniprops', quiet=True)

    from nltk.tokenize.nist import NISTTokenizer


nist = NISTTokenizer()


def tokenizer(text):
    return nist.tokenize(text)
