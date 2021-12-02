import argparse
import csv
import logging
from collections import Counter
from pathlib import Path

from hp import CLEAN_CATALOGUE_PATH, FULL_CATALOGUE_PATH

logger = logging.getLogger(__name__)


def main(source: Path, target: Path, min_length: int, max_length: int, min_lang_freq: int):
    with source.open() as csv_file:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        header = next(reader)

        wordcount_index = header.index("wordcount")
        lang_index = header.index("language")

        languages = Counter()
        for line in reader:
            language = line[lang_index]
            languages.update([language])

    with source.open() as csv_file, target.open("w") as csv_file_clean:
        reader = csv.reader(csv_file, delimiter=',', quotechar='"')
        next(reader)
        writer = csv.writer(csv_file_clean, delimiter=',', quotechar='"', quoting=csv.QUOTE_MINIMAL)
        writer.writerow(header)

        stats = {
            "min_length": 0,
            "max_length": 0,
            "language": 0,
            "kept": 0
        }
        logger.info("Corpus languages (min. allowed frequency %d):", min_lang_freq)
        for language, freq in sorted(languages.items(), key=lambda rec: -rec[1]):
            logger.info("%s %s (%d)", "✓" if freq >= min_lang_freq else "✕", language, freq)
        allowed_languages = set(language for language, freq in languages.items() if freq >= min_lang_freq)

        for line in reader:
            try:
                wordcount = int(line[wordcount_index])
            except ValueError:
                wordcount = 0
            language = line[lang_index]
            languages.update([language])
            if wordcount < min_length:
                stats["min_length"] += 1
                if language not in allowed_languages:
                    stats["language"] += 1
            elif wordcount > max_length:
                stats["max_length"] += 1
                if language not in allowed_languages:
                    stats["language"] += 1
            elif language not in allowed_languages:
                stats["language"] += 1
            else:
                writer.writerow(line)
                stats["kept"] += 1

        for stat, value in stats.items():
            logger.info("Category %s: %6d affected documents.", stat, value)


if __name__ == '__main__':
    logging.basicConfig(format="%(asctime)s %(levelname)s %(message)s", level=logging.INFO)

    parser = argparse.ArgumentParser(description="Clean metadata.")
    parser.add_argument("-i", "--input", dest="input", default=str(FULL_CATALOGUE_PATH), type=str, help="Original CSV")
    parser.add_argument("-o", "--output", dest="output", default=str(CLEAN_CATALOGUE_PATH), type=str,
                        help="Cleaned CSV")
    parser.add_argument("-m", "--min-length", dest="min", default=500, type=int, help="Min character length")
    parser.add_argument("-M", "--max-length", dest="max", default=10000, type=int, help="Max character length")
    parser.add_argument("-l", "--min-lang-freq", dest="lang", default=5000, type=int, help="Min language frequency")
    args = parser.parse_args()

    input_path = Path(args.input)
    if not input_path.is_file():
        input_path = FULL_CATALOGUE_PATH

    output_path = Path(args.output)
    if not output_path.is_file():
        output_path = CLEAN_CATALOGUE_PATH

    main(input_path, output_path, args.min, args.max, args.lang)
    logger.info("Original file `%s` filtered to `%s`.", input_path, output_path)
