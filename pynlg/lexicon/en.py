# encoding: utf-8

"""Definition of the english Lexicon."""



from .lexicon import Lexicon
from .lang import ENGLISH
from .feature.category import CONJUNCTION


class EnglishLexicon(Lexicon):

    """Lexicon defining specific rules for the english language."""

    language = ENGLISH

    @property
    def conjunction_coordination(self):
        return self.first('and', category=CONJUNCTION)
