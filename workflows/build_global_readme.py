from scraper import GlobalReadMe


def main():
    GlobalReadMe(
        {
            "lk_hansard": [
                "lk_hansard_2020s",
                "lk_hansard_2010s",
                "lk_hansard_2000s",
            ]
        }
    ).build()


if __name__ == "__main__":
    main()
