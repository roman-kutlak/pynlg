# encoding: utf-8

"""Definition of French morphology rules."""


import re

from collections import namedtuple

from ..lexicon.feature.gender import FEMININE, MASCULINE, NEUTER
from ..lexicon.feature.discourse import (
    HEAD, FRONT_MODIFIER, PRE_MODIFIER, POST_MODIFIER,
    OBJECT, COMPLEMENT, SUBJECT, INDIRECT_OBJECT)
from ..lexicon.feature.category import (
    VERB_PHRASE, NOUN, VERB, PREPOSITIONAL_PHRASE, NOUN_PHRASE, PRONOUN, CLAUSE)
from ..lexicon.feature.lexical import REFLEXIVE, GENDER
from ..lexicon.feature.pronoun import PERSONAL, RELATIVE
from ..lexicon.feature.lexical.fr import PRONOUN_TYPE, DETACHED
from ..lexicon.feature.person import FIRST, SECOND, THIRD
from ..lexicon.feature.form import IMPERATIVE
from ..lexicon.feature.number import SINGULAR, PLURAL, BOTH
from ..lexicon.feature.tense import PRESENT, FUTURE, CONDITIONAL, PAST
from ..lexicon.feature import PERSON, NUMBER
from ..lexicon.feature.internal import DISCOURSE_FUNCTION
from ..lexicon.feature.form import (
    BARE_INFINITIVE, SUBJUNCTIVE, GERUND, INFINITIVE, PRESENT_PARTICIPLE,
    PAST_PARTICIPLE, INDICATIVE)
from ..spec.string import StringElement


Verb = namedtuple('Radical', ['radical', 'group'])


class EnglishMorphologyRules(object):

    """Class in charge of performing french morphology rules for any
    type of words: verbs, nouns, determiners, etc.

    """

    @staticmethod
    def get_base_form(element, base_word):
        """Return a word base_form, either from the element or the base word.

        If the element is a verb and the base_word has a base form, or
        if the element has no base form return the base_word base form.
        Else, the base_word base_form is returned.

        """
        if element.category == VERB:
            if base_word and base_word.base_form:
                return base_word.base_form
            else:
                return element.base_form
        else:
            if element.base_form:
                return element.base_form
            elif base_word:
                return base_word.base_form

    def morph_adjective(self, element, base_word=None):
        """Performs the morphology for adjectives."""
        realised = element.base_form
        return StringElement(string=realised, word=element)

    @staticmethod
    def pluralize(realised):
        """Return the plural form of the argument realisation string."""
        if realised.endswith(u's'):
            return '%ses' % (realised)
        else:
            return '%ss' % (realised)

    def morph_determiner(self, element):
        return StringElement(string=element.base_form, word=element)

    def morph_noun(self, element, base_word=None):
        base_form = self.get_base_form(element, base_word)
        base_word = element.base_word or base_word

        if (
                (element.parent and element.parent.is_plural
                 or element.is_plural) and not
                element.proper
        ):
            if element.plural and base_word:
                realised = base_word.plural
            else:
                realised = self.pluralize(base_form)
        else:
            realised = base_form

        realised = '%s%s' % (realised, element.particle)
        return StringElement(string=realised, word=element)