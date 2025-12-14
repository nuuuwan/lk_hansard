import sys
from functools import cache
from typing import Generator

from scraper import AbstractPDFDoc, GlobalReadMe
from utils import WWW, JSONFile, Log, TimeFormat

log = Log("Hansard")


class Hansard(AbstractPDFDoc):
    URL = "https://www.parliament.lk/en/business-of-parliament/hansards"
    DATE_FORMAT_HANSARD = TimeFormat("%B %d, %Y")
    DATE_FORMAT_GENERIC = TimeFormat("%Y-%m-%d")
    MAX_PAGES = 1000
    LANG = "si-ta-en"

    @classmethod
    def get_doc_class_description(cls) -> str:
        return "\n\n".join(
            [
                "A Hansard is the official verbatim record of parliamentary debates, preserving lawmakers’ words and decisions for history, law, and public accountability.",  # noqa: E501
            ]
        )

    @classmethod
    @cache
    def get_shard_decade(cls):
        raise NotImplementedError

    @classmethod
    def get_doc_class_label(cls):
        return "lk_hansard_" + cls.get_shard_decade()

    @classmethod
    def get_doc_class_emoji(cls) -> str:
        return "🏛️"

    @classmethod
    def __parse_date__(cls, date_str: str) -> str:
        for format_str in ["%Y-%m-%d", "%B %d, %Y"]:
            try:
                return TimeFormat(format_str).parse(date_str)
            except ValueError:
                continue
        raise ValueError(
            f"Date string '{date_str}' does not match expected formats."
        )

    @classmethod
    def __parse_row__(cls, div_row) -> "Hansard":
        h1_description = div_row.find("h1")
        assert h1_description is not None, "No h1 found in row"
        description = h1_description.get_text().strip()
        assert description.startswith("Hansard of "), description

        div_link = div_row.find("div", class_="align_center_div")
        a = div_link.find("a")
        url_pdf = a["href"]
        assert url_pdf.endswith(".pdf"), url_pdf

        date_str_formatted = description.replace("Hansard of ", "")
        date_str = cls.DATE_FORMAT_GENERIC.format(
            cls.__parse_date__(date_str_formatted)
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
    def __process_container__(cls, div_container) -> list["Hansard"]:
        doc_list = []
        for div_row in div_container.find_all("div", class_="row"):
            try:
                doc = cls.__parse_row__(div_row)
                if doc is None:
                    continue
                decade = doc.date_str[:3] + "0s"
                if decade == cls.get_shard_decade():
                    doc_list.append(doc)
            except Exception as e:
                log.error(f"{e}")
        return doc_list

    @classmethod
    def __process_page__(cls, i_page) -> list["Hansard"]:
        url_page = f"{cls.URL}?page={i_page}"
        www = WWW(url_page)

        try:
            soup = www.soup
            if soup is None:
                log.error(f"Failed to get soup for {url_page}")
                return []

            div_container = soup.find_all("div", class_="container")[4]
            if not div_container:
                log.error(f"No div_container with row child for {url_page}")
                return []
        except Exception as e:
            log.error(f"Failed to process {url_page}: {e}")
            return []

        return cls.__process_container__(div_container)

    @classmethod
    def gen_docs(cls) -> Generator["Hansard", None, None]:
        i_page = 1
        while i_page < cls.MAX_PAGES:
            doc_list = cls.__process_page__(i_page)
            if doc_list:
                yield from doc_list
            i_page += 1

    @classmethod
    def run_pipeline(cls, max_dt=None):
        max_dt = (
            max_dt
            or (float(sys.argv[2]) if len(sys.argv) > 2 else None)
            or cls.MAX_DT
        )
        log.debug(f"{max_dt=}s")

        cls.cleanup_all()
        cls.scrape_all_metadata(max_dt)
        cls.write_all()
        cls.scrape_all_extended_data(max_dt)
        cls.build_summary()
        cls.build_doc_class_readme()
        cls.build_and_upload_to_hugging_face()

        if not cls.is_multi_doc():
            GlobalReadMe(
                {cls.get_repo_name(): [cls.get_doc_class_label()]}
            ).build()
