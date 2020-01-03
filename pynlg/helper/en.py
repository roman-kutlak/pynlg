
from .base import NounPhraseHelper, PhraseHelper
from ..spec.base import NLGElement
from ..spec.word import WordElement, InflectedWordElement
from ..spec.string import StringElement
from ..spec.list import ListElement
from ..spec.phrase import AdjectivePhraseElement, NounPhraseElement
from ..lexicon.feature.category import PRONOUN, ADJECTIVE, DETERMINER, COMPLEMENTISER
from ..lexicon.feature import PERSON, NUMBER
from ..lexicon.feature.lexical import GENDER
from ..lexicon.feature.person import THIRD
from ..lexicon.feature.gender import MASCULINE
from ..lexicon.feature.number import SINGULAR
from ..lexicon.feature.lexical.fr import PRONOUN_TYPE
from ..lexicon.feature.internal.fr import RELATIVISED
from ..lexicon.feature.pronoun import PERSONAL
from ..lexicon.feature.internal import DISCOURSE_FUNCTION
from ..lexicon.feature.discourse import SPECIFIER


__all__ = ['EnglishPhraseHelper', 'EnglishNounPhraseHelper']


class EnglishPhraseHelper(PhraseHelper):
    """A helper defining specific behaviour for English sentences."""


class EnglishNounPhraseHelper(NounPhraseHelper):
    """A helper defining specific behaviour for English noun phrases."""

    def add_modifier(self, phrase, modifier):
        """Add the argument modifier to the phrase pre/post modifier list.

        """
        if not modifier:
            return
        # string which is one lexicographic word is looked up in lexicon,
        # preposed adjective is preModifier
        # Everything else is postModifier
        if isinstance(modifier, NLGElement):
            modifier_element = modifier
        else:
            modifier_element = phrase.lexicon.get(modifier, create_if_missing=False)
            if modifier_element:
                modifier_element = modifier_element[0]

            # Add word to lexicon
            elif ' ' not in modifier:
                modifier_element = WordElement(
                    base_form=modifier,
                    realisation=modifier,
                    lexicon=phrase.lexicon,
                    category=ADJECTIVE)
                phrase.lexicon.create_word(modifier_element)

        # if no modifier element was found, it must be a complex string,
        # add it as postModifier
        if not modifier_element:
            phrase.add_post_modifier(StringElement(string=modifier))
            return
        #  adjective phrase is a premodifer
        elif isinstance(modifier_element, AdjectivePhraseElement):
            head = modifier_element.head
            if head.preposed and not modifier_element.complements:
                phrase.add_pre_modifier(modifier_element)
                return
        # Extract WordElement if modifier is a single word
        else:
            modifier_word = modifier_element
            #  check if modifier is an adjective
            if modifier_word and modifier_word.category == ADJECTIVE:
                phrase.add_pre_modifier(modifier_word)
                return
        #  default case
        phrase.add_post_modifier(modifier_element)
