import unittest
from dataclasses import asdict

from lk_hansard import Hansard2020s


class TestCase(unittest.TestCase):
    def test_gen_docs_first_doc(self):
        first_doc = None
        for doc in Hansard2020s.gen_docs():
            first_doc = doc
            break

        d_first_doc = asdict(first_doc)
        print(d_first_doc)
        self.assertEqual(
            d_first_doc,
            {
                "num": "2025-11-20",
                "date_str": "2025-11-20",
                "description": "Hansard of 2025-11-20",
                "url_metadata": "https://www.parliament.lk/en/business-of-parliament/hansards",
                "lang": "si-ta-en",
                "url_pdf": "https://www.parliament.lk/uploads/businessdocs/english/22934_english_2025-11-20.pdf",
            },
        )

    def test_gen_docs(self):
        n_docs = 0
        max_n_docs = 520
        for doc in Hansard2020s.gen_docs():
            self.assertTrue(doc.url_pdf.endswith(".pdf"))
            n_docs += 1
            if n_docs >= max_n_docs:
                break

        self.assertEqual(n_docs, max_n_docs)
