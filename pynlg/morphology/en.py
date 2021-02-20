# encoding: utf-8

"""Definition of French morphology rules."""


import re

from pynlg.lexicon import feature
from pynlg.lexicon.feature import category
from pynlg.lexicon.feature import pronoun
from pynlg.lexicon.feature import person
from pynlg.lexicon.feature import lexical
from pynlg.lexicon.feature import gender
from pynlg.lexicon.feature import number
from pynlg.lexicon.feature import internal
from pynlg.lexicon.feature import discourse
from pynlg.spec.string import StringElement


WORD_ENDS_WITH_VOWEL_RE = re.compile(r".*[^aeiou]y$")
CONSONANT_RE = re.compile(r'[^aeiou]')
CONSONANTS_RE = re.compile(r'[^aeiou]+')
VOWEL_RE = re.compile(r'[aeiou]')
VOWELS_RE = re.compile(r'[aeiou]+')
ENDS_WITH_VOWEL_RE = re.compile(r'.*[aeiou]$')

PRONOUNS = {
    number.SINGULAR: {
        discourse.SUBJECT: {
            person.FIRST: "I",
            person.SECOND: "you",
            person.THIRD: {
                gender.MASCULINE: "he",
                gender.FEMININE: "she",
                gender.NEUTER: "it",
            }
        },
        discourse.OBJECT: {
            person.FIRST: "me",
            person.SECOND: "you",
            person.THIRD: {
                gender.MASCULINE: "him",
                gender.FEMININE: "her",
                gender.NEUTER: "it",
            }
        },
        discourse.SPECIFIER: {
            person.FIRST: "my",
            person.SECOND: "your",
            person.THIRD: {
                gender.MASCULINE: "his",
                gender.FEMININE: "her",
                gender.NEUTER: "its",
            }
        },
        lexical.REFLEXIVE: {
            person.FIRST: "myself",
            person.SECOND: "yourself",
            person.THIRD: {
                gender.MASCULINE: "himself",
                gender.FEMININE: "herself",
                gender.NEUTER: "itself",
            }
        },
        feature.POSSESSIVE: {
            person.FIRST: "mine",
            person.SECOND: "yours",
            person.THIRD: {
                gender.MASCULINE: "his",
                gender.FEMININE: "hers",
                gender.NEUTER: "its",
            },
        },
    },
    number.PLURAL: {
        discourse.SUBJECT: {
            person.FIRST: "we",
            person.SECOND: "you",
            person.THIRD: {
                gender.MASCULINE: "they",
                gender.FEMININE: "they",
                gender.NEUTER: "they",
            }
        },
        discourse.OBJECT: {
            person.FIRST: "us",
            person.SECOND: "you",
            person.THIRD: {
                gender.MASCULINE: "them",
                gender.FEMININE: "them",
                gender.NEUTER: "them",
            }
        },
        discourse.SPECIFIER: {
            person.FIRST: "our",
            person.SECOND: "your",
            person.THIRD: {
                gender.MASCULINE: "their",
                gender.FEMININE: "their",
                gender.NEUTER: "their",
            }
        },
        lexical.REFLEXIVE: {
            person.FIRST: "ourselves",
            person.SECOND: "yourselves",
            person.THIRD: {
                gender.MASCULINE: "themselves",
                gender.FEMININE: "themselves",
                gender.NEUTER: "themselves",
            }
        },
        feature.POSSESSIVE: {
            person.FIRST: "ours",
            person.SECOND: "yours",
            person.THIRD: {
                gender.MASCULINE: "theirs",
                gender.FEMININE: "theirs",
                gender.NEUTER: "theirs",
            }
        },
    },
    number.BOTH: {}
}


WH_PRONOUNS = {"who", "what", "which", "where", "why", "how", "how many"}


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
        if element.category == category.VERB:
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
        base_word = element.base_word or base_word
        base_form = self.get_base_form(element, base_word)
        pattern_value = element.default_infl

        if element.is_comparative:
            if element.comparative:
                realised = element.comparative
            elif base_word and base_word.comparative:
                realised = base_word.comparative
            else:
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
        # NOTE: simplenlg copies over just DISCOURSE_FUNCTION feature
        return StringElement(string=realised, word=element)

    def morph_adverb(self, element, base_word=None):
        """Perform the morphology for adverbs."""
        base_word = element.base_word or base_word
        base_form = self.get_base_form(element, base_word)

        if element.is_comparative:
            if element.comparative:
                realised = element.comparative
            elif base_word and base_word.comparative:
                realised = base_word.comparative
            else:
                if base_form.endswith('ly'):
                    realised = 'more ' + base_form
                else:
                    realised = self.build_regular_comparative(base_form)
        elif element.is_superlative:
            if element.superlative:
                realised = element.superlative
            elif base_word and base_word.superlative:
                realised = base_word.superlative
            else:
                if base_form.endswith('ly'):
                    realised = 'most ' + base_form
                else:
                    realised = self.build_regular_superlative(base_form)
        else:
            realised = base_form
        # NOTE: simplenlg copies over just DISCOURSE_FUNCTION feature
        return StringElement(string=realised, word=element)

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

    def morph_pronoun(self, element):
        if element.features.get(internal.NON_MORPH):
            realised = element.base_form
        elif self.is_wh_pronoun(element):
            realised = element.base_form
        else:
            gender_value = element.gender or gender.NEUTER
            person_value = element.person or person.FIRST
            number_value = element.number or number.SINGULAR
            discourse_value = element.discourse_function or discourse.SUBJECT
            is_passive = element.passive if element.passive is not None else False
            is_specifier = discourse_value == discourse.SPECIFIER
            is_possessive = element.possessive
            is_reflexive = element.reflexive
            as_subject = (
                (discourse_value == discourse.SUBJECT and not is_passive) or
                (discourse_value == discourse.OBJECT and is_passive) or
                (discourse_value == discourse.COMPLEMENT and is_passive) or
                is_specifier
            )
            as_object = not as_subject

            if is_reflexive:
                use = lexical.REFLEXIVE
            elif is_possessive:
                use = discourse.SPECIFIER if is_specifier else feature.POSSESSIVE
            else:
                if as_subject:
                    use = discourse.SUBJECT
                elif as_object:
                    use = discourse.OBJECT
                else:
                    use = discourse.SUBJECT

            lookup = PRONOUNS.get(number_value, {}).get(use, {}).get(person_value)
            if person_value == person.THIRD and lookup:
                lookup = lookup.get(gender_value)

            realised = lookup or element.base_form

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

    @staticmethod
    def is_wh_pronoun(wordform):
        return wordform in WH_PRONOUNS
