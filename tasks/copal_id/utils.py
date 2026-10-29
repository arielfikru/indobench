QUESTION = {
    "cause": "Apa penyebabnya?",
    "effect": "Apa akibatnya?",
}


def doc_to_text(doc):
    # Premise is kept whole; only a trailing period is removed so the sentence reads the same in both splits.
    premise = doc["premise"].strip().rstrip(".")
    return (
        f"{premise}.\n{QUESTION[doc['question']]}\n"
        f"A. {doc['choice1'].strip()}\nB. {doc['choice2'].strip()}\n"
        "Jawab hanya dengan huruf pilihan yang paling tepat."
    )
