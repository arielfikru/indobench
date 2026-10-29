import ast
import re

LETTERS = "ABC"
_OPT_RE = re.compile(r"^([A-C])\. ", re.M)


def process_docs(dataset):
    """Parse the stringified options list and expose letters + a newline-joined options block."""

    def add(doc):
        opts = ast.literal_eval(doc["options"])
        assert len(opts) == len(LETTERS), doc["id"]
        assert all(o.startswith(f"{LETTERS[i]}. ") for i, o in enumerate(opts)), doc["id"]
        doc["options_text"] = "\n".join(opts)
        doc["choices_letters"] = list(LETTERS)
        return doc

    return dataset.map(add)
