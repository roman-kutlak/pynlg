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


WORD_ENDS_WITH_VOWEL_RE = re.compile(r".*[^aeiou]y$")
CONSONANT_RE = re.compile(r'[^aeiou]')
CONSONANTS_RE = re.compile(r'[^aeiou]+')
VOWEL_RE = re.compile(r'[aeiou]')
VOWELS_RE = re.compile(r'[aeiou]+')
ENDS_WITH_VOWEL_RE = re.compile(r'[aeiou]$')



class EnglishMorphologyRules(object):

    """Class in charge of performing English morphology rules for any
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

    @staticmethod
    def pluralize(realised):
        """Return the plural form of the argument realisation string."""
        if realised.endswith('s'):
            return '%ses' % realised
        else:
            return '%ss' % realised

    def morph_adjective(self, element, base_word=None):
        """Perform the morphology for adjectives."""
        base_form = self.get_base_form(element, base_word)
        base_word = element.base_word or base_word
        pattern_value = element.default_infl

        if element.is_comparative:
            realised = element.comparative
            if not realised and base_word:
                realised = base_word.comparative
            if not realised:
                if pattern_value == 'glreg':  # regular doubling form; big/bigger
                    realised = self.build_double_comparative(base_form)
                else:
                    realised = self.build_regular_comparative(base_form)

        elif element.is_superlative:
            realised = element.superlative
            if not realised and base_word:
                realised = base_word.superlative
            if not realised:
                if pattern_value == 'glreg':  # regular doubling form; big/biggest
                    realised = self.build_double_superlative(base_form)
                else:
                    realised = self.build_regular_superlative(base_form)

        else:
            realised = base_form

        return StringElement(string=realised, word=element)

    def morph_adverb(self, element, base_word=None):
        """Perform the morphology for adverbs."""
        # if word ends with '-ly',
        return self.morph_adjective(element, base_word)

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


    @staticmethod
    def build_double_comparative(base_form):
        """Build the comparative form for adjectives that follow the doubling form
        of the last consonant. 
        
        <em>-er</em> is added to the end after the last consonant is doubled.
        For example, <em>fat</em> becomes <em>fatter</em>.
         
        Args:
             base_form: the base form of the word.
        Returns:
             the inflected word

        """
        morphology = None
        if base_form:
            morphology = base_form + base_form[-1] + "er"
        return morphology

    @staticmethod
    def build_regular_comparative(base_form):
        """Build the comparative form for regular adjectives.

        The rules are performed in this order:
        <ul>
        <li>adjectives with 2 and more syllables are returned with 'more'</li>
        <li>For adjectives ending <em>-Cy</em>, where C is any consonant, the
        ending becomes <em>-ier</em>. For example, <em>brainy</em> becomes
        <em>brainier</em>.</li>
        <li>For adjectives ending <em>-e</em> the ending becomes <em>-er</em>.
        For example, <em>fine</em> becomes <em>finer</em>.</li>
        <li>For all other adjectives, <em>-er</em> is added to the end. For
        example, <em>clear</em> becomes <em>clearer</em>.</li>
        </ul>

        Technically many disyllable words can take both forms but we are being
        cautious and use 'more'; you can add the word to the lexicon to avoid this.

        For example, 'fine' is in the english lexicon so it is realised
        as 'finest' instead of 'more fine'.

        Args:
             base_form: the base form of the word.
        Returns:
             the inflected word

        """
        morphology = None
        if base_form:
            num_syllables = EnglishMorphologyRules.count_syllables(base_form)
            if num_syllables >= 2:
                return 'more ' + base_form
            if WORD_ENDS_WITH_VOWEL_RE.match(base_form):
                morphology = re.sub(r"y\b", "ier", base_form)
            elif base_form.endswith("e"):
                morphology = base_form + "r"
            else:
                morphology = base_form + "er"
        return morphology


    @staticmethod
    def build_double_superlative(base_form):
        """Build the superlative form for adjectives that follow the doubling form
        of the last consonant.

        <em>-er</em> is added to the end after the last consonant is doubled.
        For example, <em>fat</em> becomes <em>fattest</em>.

        Args:
             base_form: the base form of the word.
        Returns:
             the inflected word

        """
        morphology = None
        if base_form:
            morphology = base_form + base_form[-1] + "est"
        return morphology

    @staticmethod
    def build_regular_superlative(base_form):
        """Build the superlative form for regular adjectives.

        The rules are performed in this order:
        <ul>
        <li>adjectives with 2 and more syllables are returned with 'most'</li>
        <li>For adjectives ending <em>-Cy</em>, where C is any consonant, the
        ending becomes <em>-iest</em>. For example, <em>brainy</em> becomes
        <em>brainiest</em>.</li>
        <li>For adjectives ending <em>-e</em> the ending becomes <em>-est</em>.
        For example, <em>fine</em> becomes <em>finest</em>.</li>
        <li>For all other adjectives, <em>-est</em> is added to the end. For
        example, <em>clear</em> becomes <em>clearest</em>.</li>
        </ul>

        Similarly to comparative, many disyllable adjectives can be used
        with 'most' or can be morphed; you can add the word to the lexicon
        to avoid using 'most'.

        For example, 'fine' is in the english lexicon so it is realised
        as 'finest' instead of 'more fine'.

        Args:
             base_form: the base form of the word.
        Returns:
             the inflected word

        """
        morphology = None
        if base_form:
            num_syllables = EnglishMorphologyRules.count_syllables(base_form)
            if num_syllables >= 2:
                return 'most ' + base_form
            if WORD_ENDS_WITH_VOWEL_RE.match(base_form):
                morphology = re.sub(r"y\b", "iest", base_form)
            elif base_form.endswith("e"):
                morphology = base_form + "st"
            else:
                morphology = base_form + "est"
        return morphology

    @staticmethod
    def count_syllables(wordform):
        """Return the estimated number of syllables in a wordform."""
        # if wordform contains *, replace it with x so we don't mix them
        wordform = wordform.replace('*', 'x')
        # replace vowel groups with *
        vowel_groups = re.sub(VOWELS_RE, '*', wordform)
        ends_with_vowel = int(bool(ENDS_WITH_VOWEL_RE.match(wordform)))
        num_syllables = vowel_groups.count('*') - ends_with_vowel
        # if there is only one vowel group and it is at the end return 1 instead of 0
        return max(1, num_syllables)
