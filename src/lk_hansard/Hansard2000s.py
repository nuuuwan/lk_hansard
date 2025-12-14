from functools import cache

from lk_hansard.Hansard import Hansard


class Hansard2000s(Hansard):
    @classmethod
    @cache
    def get_shard_decade(cls):
        return "2000s"
