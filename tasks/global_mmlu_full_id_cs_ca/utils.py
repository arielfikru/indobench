def _keep_label(label):
    def keep(doc):
        return doc["cultural_sensitivity_label"] == label

    return keep


def process_cs(dataset):
    return dataset.filter(_keep_label("CS"))


def process_ca(dataset):
    return dataset.filter(_keep_label("CA"))
