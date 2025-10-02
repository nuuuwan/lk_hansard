from typing import Generator

from utils import JSONFile, Log, TimeFormat

from scraper import AbstractPDFDoc
from utils import WWW

log = Log("Hansard")


class Hansard(AbstractPDFDoc):
    URL = "https://www.parliament.lk/en/business-of-parliament/hansards"
    DATE_FORMAT_HANSARD = TimeFormat("%B %d, %Y")
    DATE_FORMAT_GENERIC = TimeFormat("%Y-%m-%d")
    MAX_PAGES = 100
    LANG = "si-ta-en"

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "\n\n".join(
            [
                "A Hansard is the official verbatim record of parliamentary debates, preserving lawmakers’ words and decisions for history, law, and public accountability.",  # noqa: E501
            ]
        )

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "🏛️"

    @classmethod
    def __parse_tr__(cls, tr) -> "Hansard":
        td = tr.find("td")
        description = td.get_text().strip()
        assert description.startswith("Hansard of "), description

        a = td.find("a")
        url_pdf = a["href"]
        assert url_pdf.endswith(".pdf"), url_pdf

        date_str_formatted = description.replace("Hansard of ", "")
        date_str = cls.DATE_FORMAT_GENERIC.format(
            cls.DATE_FORMAT_HANSARD.parse(date_str_formatted)
        )
        assert len(date_str) == 10, date_str

        doc = cls(
            num=date_str,
            date_str=date_str,
            description=description,
            url_metadata=cls.URL,
            lang=cls.LANG,
            url_pdf=url_pdf,
        )
        return doc

    @classmethod
    def add_lang(cls, json_path):
        json_file = JSONFile(json_path)
        d = json_file.read()
        if "lang" not in d or d["lang"] != cls.LANG:
            d["lang"] = cls.LANG
            json_file.write(d)
            log.warning(f"➕ Added lang={cls.LANG} to {json_path}")

    @classmethod
    def __process_table__(cls, table) -> list["Hansard"]:
        doc_list = []
        for tr in table.find_all("tr"):
            try:
                doc = cls.__parse_tr__(tr)
                doc_list.append(doc)
            except Exception as e:
                log.error(f"{e}")
        return doc_list

    @classmethod
    def __process_page__(cls, i_page) -> list["Hansard"]:
        start = i_page * 20
        url_page = f"{cls.URL}?start={start}"
        www = WWW(url_page)

        try:
            soup = www.soup
            if soup is None:
                log.error(f"Failed to get soup for {url_page}")
                return []

            table = soup.find("table", class_="tablearticle")
            if table is None:
                log.error(f"Failed to find table for {url_page}")
                return []
        except Exception as e:
            log.error(f"Failed to process {url_page}: {e}")
            return []

        return cls.__process_table__(table)

    @classmethod
    def gen_docs(cls) -> Generator["Hansard", None, None]:
        i_page = 0
        while i_page < cls.MAX_PAGES:
            doc_list = cls.__process_page__(i_page)
            if not doc_list:
                return
            yield from doc_list
            i_page += 1
