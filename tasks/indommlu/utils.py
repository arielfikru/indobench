import re

LETTERS = "ABCDE"
_OPT_RE = re.compile(r"^([A-E])\. ", re.M)


def _option_letters(text):
    return _OPT_RE.findall(text)


def process_docs(dataset):
    """Keep the zero-shot test split and drop rows with a broken gold label.

    - is_for_fewshot == 1 rows (75) are the paper's few-shot exemplar pool, not test items.
    - ids 4223 and 14150 have a gold letter that is not among their options; dropped.
    """

    def keep(doc):
        if doc["is_for_fewshot"] != 0:
            return False
        letters = _option_letters(doc["jawaban"])
        return doc["kunci"] in letters and letters == list(LETTERS[: len(letters)])

    def add_choices(doc):
        n = len(_option_letters(doc["jawaban"]))
        doc["choices_letters"] = list(LETTERS[:n])
        return doc

    return dataset.filter(keep).map(add_choices)
