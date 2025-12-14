import unittest
from dataclasses import asdict

from lk_hansard import Hansard2000s, Hansard2010s, Hansard2020s


class TestCase(unittest.TestCase):
    def test_gen_docs_first_doc(self):

        for hansard_class, expected_d_first_doc in [
            (
                Hansard2000s,
                {
                    "num": "2009-12-08",
                    "date_str": "2009-12-08",
                    "description": "Hansard of December 08, 2009",
                    "url_metadata": "https://www.parliament.lk/en/business-of-parliament/hansards",
                    "lang": "si-ta-en",
                    "url_pdf": "https://www.parliament.lk/uploads/documents/hansard/PUBDOC2447_document.pdf",
                },
            ),
            (
                Hansard2010s,
                {
                    "num": "2019-11-11",
                    "date_str": "2019-11-11",
                    "description": "Hansard of November 11, 2019",
                    "url_metadata": "https://www.parliament.lk/en/business-of-parliament/hansards",
                    "lang": "si-ta-en",
                    "url_pdf": "https://www.parliament.lk/uploads/documents/hansard/1574066230045551.pdf",
                },
            ),
        ]:
            last_doc = None
            for doc in hansard_class.gen_docs():
                last_doc = doc
                break

            d_first_doc = asdict(last_doc)
            print(d_first_doc)
            self.assertEqual(d_first_doc, expected_d_first_doc)

    def test_gen_docs(self):
        max_n_docs = 520
        for hansard_class in [Hansard2000s, Hansard2010s, Hansard2020s]:
            n_docs = 0
            for doc in hansard_class.gen_docs():
                self.assertTrue(doc.url_pdf.endswith(".pdf"))
                n_docs += 1
                if n_docs >= max_n_docs:
                    break

            self.assertEqual(n_docs, max_n_docs)
