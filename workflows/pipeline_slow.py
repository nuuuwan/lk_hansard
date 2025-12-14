import sys

from lk_hansard import Hansard2000s, Hansard2010s, Hansard2020s

if __name__ == "__main__":
    doc_class_label = sys.argv[1]
    for doc_class in [
        Hansard2020s,
        Hansard2010s,
        Hansard2000s,
    ]:
        if doc_class.get_doc_class_label() == doc_class_label:
            doc_class.run_pipeline()
            sys.exit(0)
    raise ValueError(f"Unknown doc_class_label: {doc_class_label}")
