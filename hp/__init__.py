from pathlib import Path
import random
import time


URL_LISTS_DOWNLOAD_PATH: Path = (Path(__file__).parent.parent / "downloaded_url_lists").resolve()
FULL_DOWNLOAD_PATH: Path = (Path(__file__).parent.parent / "downloaded_fullarticles").resolve()
PARTIAL_CATALOGUE_PATH: Path = (Path(__file__).parent / "partial_HP_catalogue.csv")
FULL_CATALOGUE_PATH: Path = (Path(__file__).parent / "HP_catalogue.csv")
CLEAN_CATALOGUE_PATH: Path = (Path(__file__).parent / "HP_catalogue_clean.csv")
RELATIONS_HTML_PATH: Path = (Path(__file__).parent / "relations.html")
LOVERS_CSV_PATH: Path = (Path(__file__).parent / "lovers")
LOVERS_CSV_PATH.mkdir(exist_ok=True)
FREE_FORM_TAGS_PATH: Path = (Path(__file__).parent / "free_form_tags_data")
FREE_FORM_TAGS_PATH.mkdir(exist_ok=True)
FREE_FORM_TAGS_PER_PERSON_PATH: Path = (Path(__file__).parent / "free_form_tags_per_person_data")
FREE_FORM_TAGS_PER_PERSON_PATH.mkdir(exist_ok=True)


def delay(multiplier: float = 0.85, minimum: float = 0.15, maximum: float = 0.85) -> None:
    time.sleep(min(maximum, max(minimum, random.random() * multiplier)))
