from typing import Generator

from utils import Log, TimeFormat

from pdf_scraper import AbstractDoc
from utils_future import WWW

log = Log("Hansard")


class Hansard(AbstractDoc):
    URL = "https://www.parliament.lk/en/business-of-parliament/hansards"
    DATE_FORMAT_HANSARD = TimeFormat("%B %d, %Y")
    DATE_FORMAT_GENERIC = TimeFormat("%Y-%m-%d")
    MAX_PAGES = 100

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
            url_pdf=url_pdf,
            url_metadata=cls.URL,
        )
        return doc

    @classmethod
    def __process_table__(cls, table) -> Generator["Hansard", None, None]:
        for tr in table.find_all("tr"):
            try:
                doc = cls.__parse_tr__(tr)
                yield doc
            except Exception as e:
                log.error(f"{e}")

    @classmethod
    def __process_page__(cls, i_page) -> Generator["Hansard", None, None]:
        start = i_page * 20
        url_page = f"{cls.URL}?start={start}"
        www = WWW(url_page)

        try:
            soup = www.soup
            if soup is None:
                log.error(f"Failed to get soup for {url_page}")
                return

            table = soup.find("table", class_="tablearticle")
            if table is None:
                log.error(f"Failed to find table for {url_page}")
                return
        except Exception as e:
            log.error(f"Failed to process {url_page}: {e}")
            return

        for doc in cls.__process_table__(table):
            yield doc

    @classmethod
    def gen_docs(cls) -> Generator["Hansard", None, None]:
        i_page = 0
        while i_page < cls.MAX_PAGES:
            for doc in cls.__process_page__(i_page):
                yield doc
            i_page += 1
