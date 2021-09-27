import csv
import re
from collections import Counter
from typing import List

from hp import FULL_CATALOGUE_PATH


_EXTRA_NAMES = {
    'harry potter', 'draco malfoy', 'hermione granger', 'sirius black', 'remus lupin', 'severus snape', 'tom riddle',
    'james potter', 'ginny weasley', 'lily evans potter', 'ron weasley', 'luna lovegood', 'fred weasley',
    'lucius malfoy', 'pansy parkinson', 'scorpius malfoy', 'albus dumbledore', 'regulus black',
    'bellatrix black lestrange', 'neville longbottom', 'newt scamander', 'george weasley', 'gellert grindelwald',
    'narcissa black malfoy', 'albus severus potter', 'charlie weasley', 'voldemort', 'theodore nott', 'fleur delacour',
    'oliver wood', 'percy weasley', 'nymphadora tonks', 'blaise zabini', 'percival graves', 'teddy lupin',
    'cedric diggory', 'james sirius potter', 'minerva mcgonagall', 'daphne greengrass', 'bill weasley',
    'tina goldstein', 'astoria greengrass', 'rose weasley', 'marcus flint', 'theseus scamander', 'marlene mckinnon',
    'credence barebone', 'andromeda black tonks', 'viktor krum', 'tony stark', 'lavender brown', 'loki',
    'peter pettigrew', 'dean thomas', 'seamus finnigan', 'arthur weasley', 'petunia evans dursley', 'molly weasley',
    'cho chang', 'lily luna potter', 'salazar slytherin', 'steve rogers', 'victoire weasley', 'parvati patil',
    'fenrir greyback', 'bartemius crouch jr', 'godric gryffindor', 'angelina johnson', 'percy jackson',
    'james bucky barnes', 'rodolphus lestrange', 'ted tonks', 'dorcas meadowes', 'katie bell', 'hannah abbott',
    'logan tremblay', 'vernon dursley', 'drarry', 'dudley dursley', 'antonin dolohov', 'leo knut', 'quirinus quirrell',
    'aragog', 'ludo bagman', 'winky', 'bane', 'zacharias smith', 'filius flitwick', 'frank bryce', 'augustus rookwood',
    'emmeline vance', 'roger davies', 'peeves', 'kendra dumbledore', 'pius thicknesse', 'argus filch',
    'helga hufflepuff', 'arabella figg', 'igor karkaroff', 'olympe maxime', 'aurora sinistra', 'scabbers', 'trevor',
    'helena ravenclaw', 'sybill trelawney', 'amos diggory', 'griselda marchbanks', 'hugo weasley',
    'dennis creevey', 'reginald cattermole', 'nearly headless nick', 'elphias doge', 'walden macnair',
    'horace slughorn', 'silvanus kettleburn', 'mafalda hopkirk', 'rubeus hagrid', 'kreacher', 'the fat lady',
    'amycus carrow', 'dolores umbridge', 'millicent bulstrode', 'justin finch-fletchley', 'narcissa malfoy',
    'beedle the bard', 'pomona sprout', 'aberforth dumbledore', 'dobby', 'cornelius fudge', 'bogrod', 'grawp',
    'alicia spinnet', 'crookshanks', 'mary riddle', 'mundungus fletcher', 'dirk cresswell',
    'alice and frank longbottom', 'john dawlish', 'gornuk', 'the fat friar', 'buckbeak', 'fang', 'ariana dumbledore',
    'griphook', 'bathilda bagshot', 'errol', 'sir cadogan', 'madam rosmerta', 'hokey', 'terry boot', 'cormac mclaggen',
    'irma pince', 'myrtle', 'petunia dursley', 'albert runcorn', 'rabastan lestrange',
    'anthony goldstein', 'alastor moody', 'graham montague', 'fawkes', 'rita skeeter', 'mary cattermole',
    'fluffy', 'cuthbert binns', 'travers', 'thomas riddle jr', 'magorian', 'antioch peverell', 'scabior', 'norbert',
    'ernie macmillan', 'romilda vane', 'florean fortescue', 'the bloody baron', 'poppy pomfrey', 'nott sr',
    'merope gaunt', 'garrick ollivander', 'bob ogden', 'gregorovitch', 'wilhelmina grubbly', 'gabrielle delacour',
    'andromeda tonks', 'marvolo gaunt', 'great aunt muriel', 'ronan', 'michael corner', 'padma patil', 'crabbe',
    'susan bones', 'rolanda hooch', 'morfin gaunt', 'pigwidgeon', 'sturgis podmore', 'hedwig', 'barty crouch sr',
    'colin creevey', 'rufus scrimgeour', 'lord voldemort', 'marietta edgecombe',
    'xenophilius lovegood', 'alecto carrow', 'augusta longbottom', 'penelope clearwater', 'gregory goyle',
    'madam malkin', 'wilkie twycross', 'phineas nigellus black', 'thorfinn rowle', 'amelia bones', 'thomas riddle sr',
    'charity burbage', 'lily potter', 'dedalus diggle', 'lee jordan', 'septima vector',
    'firenze', 'walburga black', 'barty crouch jr', 'kingsley shacklebolt', 'ignotus peverell', 'demelza robins',
    'stan shunpike', 'vincent crabbe', 'gilderoy lockhart', 'bellatrix lestrange', 'corban yaxley', 'marge dursley',
    'cadmus peverell', 'cole', 'percival dumbledore', 'nagini'}


_REPLACEMENTS = {
    "tom riddle": "thomas riddle sr",
    "lily evans potter": "lily evans",
    "lily potter": "lily evans",
    "ginny weasley harry potter": "ginny",
    "moaning myrtle": "myrtle",
    "myrtle warren": "myrtle",
    "harry james potter": "james potter",
    "james potter ii": "james potter",
    "fredric fred weasley": "fred weasley",
    "fredric weasley": "fred weasley",
    "lucius malfoy i": "lucius malfoy",
    "lucius malfoy'": "lucius malfoy",
    "alpha pansy parkinson": "pansy parkinson",
    "regulus black ii": "regulus black",
    "albus severus potter-weasley": "albus severus potter",
    "tom riddle voldemort": "voldemort",
    "james sirius potter-weasley": "james sirius potter",
    "loki laufeyson": "loki",
    "loki odinson": "loki",
    "loki fárbautison": "loki",
    "molly weasley ii": "molly weasley II",
    "ginevra molly weasley": "molly weasley II",
    "trevor the toad": "trevor",
    "trevor belmont": "trevor",
    "vincent crabbe": "crabbe",
    "irma crabbe black": "",
    "wilhelmina grubbly-plank": "wilhelmina grubbly",
    "harfang longbottom": "fang",
    "fangs fogarty": "fang",
    "ronan lynch": "ronan",
    "torquil travers": "travers",
}


def remove_special_characters(text: str) -> str:
    text = re.sub(r"\s*[•·]\s*", " ", text).strip()
    text = re.sub(r"\s*&quot;\s*", " ", text).strip()
    text = re.sub(r"\s*\"\s*", " ", text).strip()
    text = re.sub(r"\s*&amp;\s*", " ", text).strip()
    text = re.sub(r"\s*&#39;\s*", "'", text).strip()
    text = re.sub(r"\s*[.]\s*", " ", text).strip()
    text = re.sub(r"\s*[(].*[)]\s*", " ", text).strip()
    text = re.sub(r"\s*[|].*", " ", text).strip()
    text = re.sub(r"\s+[x×].+", " ", text).strip()
    text = re.sub(r" - relationship", " ", text, flags=re.IGNORECASE).strip()
    text = re.sub("you", " ", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"(^| )"
                  r"(oc|original|characters?|other|male|female|reader|none|ofc|omc|player|occ|mention|"
                  r"undecided|not a romance|tbd|as of yet|to be decided|may have some|future|past|"
                  r"background|minor|former|one sided|eventual|brief|post|evil|pre|implied|diary|styles|"
                  r"relationship tags to be added|no romantic relationship|everyone|relationship|or|"
                  r"non con|slash|fem)|x|are friends|hints at|almost|friendship|platonic|various"
                  r"(?=$| )",
                  " ", text, flags=re.IGNORECASE).strip()
    text = re.sub(r"(?:^| )(?:female|teen|male|fem|mal|parental|sister|dad|mom|pre)[-!]",
                  " ", text, flags=re.IGNORECASE).strip()
    text = text.lower().strip("()- !")
    return _REPLACEMENTS.get(text, text)


def _load_catalogue(min_freq: int = 100) -> List[str]:
    with open(FULL_CATALOGUE_PATH) as h:
        reader = csv.reader(h, delimiter=',', quotechar='"')
        header = next(reader)
        lovers_index = header.index("lovers")
        collected_names = []
        for line in reader:
            names = line[lovers_index]
            if names == "none":
                continue
            names = names.replace("&#39;", "'").replace("/", "SPLIT").replace("&quot;", "\"").\
                replace("&amp;", "SPLIT").replace("&", "SPLIT").replace(" and ", "SPLIT")
            variants = [remove_special_characters(v) for v in names.split("SPLIT")]
            variants = [variant for variant in variants if any(ch.isalpha() for ch in variant)]
            collected_names.extend(variants)

        characters_with_freq = sorted(Counter(collected_names).items(), key=lambda rec: -rec[1])
        preselected_characters_with_freq = {
            character: freq for character, freq in characters_with_freq if freq > min_freq}
        for name in [remove_special_characters(item) for item in _EXTRA_NAMES]:
            if name not in preselected_characters_with_freq:
                preselected_characters_with_freq[name] = 100
        for character, freq in list(preselected_characters_with_freq.items()):
            for some_character, some_freq in characters_with_freq:
                if (
                        some_freq >= 100 and character != some_character and
                        character in some_character and not character + "x" in some_character):
                    del preselected_characters_with_freq[character]
                    break

        return list(preselected_characters_with_freq.keys())


NAMES = _load_catalogue()
