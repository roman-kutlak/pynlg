# encoding: utf-8
# encoding: utf-8

"""Definition of French morphology rules."""

from ..lexicon.feature.gender import FEMININE, MASCULINE, NEUTER
from ..lexicon.feature.discourse import (
    HEAD, FRONT_MODIFIER, PRE_MODIFIER, POST_MODIFIER,
    OBJECT, COMPLEMENT, SUBJECT, INDIRECT_OBJECT)
from ..lexicon.feature.category import (
    VERB_PHRASE, NOUN, VERB, PREPOSITIONAL_PHRASE, NOUN_PHRASE, PRONOUN, CLAUSE)
from ..lexicon.feature.lexical import (
    PRESENT_PARTICIPLE, PAST_PARTICIPLE, REFLEXIVE, GENDER)
from ..lexicon.feature.pronoun import PERSONAL, RELATIVE
from ..lexicon.feature.lexical.fr import PRONOUN_TYPE, DETACHED
from ..lexicon.feature.person import FIRST, SECOND, THIRD
from ..lexicon.feature.form import IMPERATIVE
from ..lexicon.feature.number import SINGULAR
from ..lexicon.feature import PERSON, NUMBER
from ..lexicon.feature.internal import DISCOURSE_FUNCTION
from ..spec.string import StringElement


class FrenchMorphologyRules(object):

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

    @staticmethod
    def replace_element(old_element, new_element_base_form):
        """Return a WordElement which base_form is the argument
        new_element_base_form. This element inherits its category and
        features from the argument old_element.

        Note: the old_element features do not override the new element
        ones, they can only complete them.

        """
        features = old_element.features.copy()
        element = old_element.lexicon.first(
            new_element_base_form,
            category=old_element.category)
        for feature, value in features.iteritems():
            if feature not in element.features:
                element.features[feature] = value
        return element

    @staticmethod
    def feminize_singular_element(element, realised):
        """Return the feminine singular form of the element, or apply
        feminization rules on the argument realization.

        """
        if element.base_form == realised and element.feminine_singular:
            return element.feminine_singular
        elif realised.endswith((u'el', u'eil')):
            return u'%sle' % (realised)
        elif realised.endswith(u'as'):
            return u'%sse' % (realised)
        elif realised.endswith((u'en', u'on')):
            return u'%sne' % (realised)
        elif realised.endswith(u'et'):
            return u'%ste' % (realised)
        elif realised.endswith(u'eux'):
            return u'%sse' % (realised[:-1])
        elif realised.endswith(u'er'):
            return u'%sère' % (realised[:-2])
        elif realised.endswith(u'eau'):
            return u'%selle' % (realised[:-3])
        elif realised.endswith(u'os'):
            return u'%sse' % (realised)
        elif realised.endswith(u'gu'):
            return u'%së' % (realised)
        elif realised.endswith(u'g'):
            return u'%sue' % (realised)
        elif (
                realised.endswith(u'eur')
                and u'%sant' % (realised[:-3]) in element.lexicon.variant_index
        ):
            return u'%sse' % (realised[:-1])
        elif realised.endswith(u'teur'):
            return u'%strice' % (realised[:-4])
        elif realised.endswith(u'if'):
            return '%sve' % (realised[:-1])
        else:
            return '%se' % (realised)

    @staticmethod
    def pluralize(realised):
        """Return the plural form of the argument realisation string."""
        if realised.endswith((u's', u'x', u'z')):
            return realised
        elif realised.endswith((u'au', u'eu')):
            return '%sx' % (realised)
        elif realised.endswith(u'al'):
            return '%saux' % (realised[:-2])
        else:
            return '%ss' % (realised)

    def morph_determiner(self, element):
        """Perform the morphology for determiners.

        It returns a StringElement made from the baseform, or the plural
        or feminine singular form of the determiner, if it applies.

        """
        parent = element.parent
        if parent:
            gender = parent.gender
        else:
            gender = element.gender

        # plural form
        if element.is_plural:
            if gender == FEMININE and element.feminine_plural:
                inflected_form = element.feminine_plural
            else:
                inflected_form = element.plural

            # "des" -> "de" in front of noun premodifiers
            if (
                parent
                and inflected_form == u"des"
                and parent.premodifiers
            ):
                inflected_form = u"de"
        # feminine singular form
        elif gender == FEMININE and element.feminine_singular:
            inflected_form = element.feminine_singular
        # masuculine singular form
        else:
            # remove particle if the determiner has one
            inflected_form = element.base_form.replace(
                element.particle, '').strip()

        return StringElement(string=inflected_form, word=element)

    def morph_adjective(self, element, base_word=None):
        """Performs the morphology for adjectives."""
        base_form = self.get_base_form(element, base_word)
        # Comparatives and superlatives are mainly treated by syntax
        # in French. Only exceptions, provided by the lexicon, are
        # treated by morphology.
        if element.is_comparative:
            realised = element.comparative
            element = self.replace_element(
                old_element=element, new_element_base_form=realised)
            if base_word and not realised:
                realised = base_word.comparative
            if not realised:
                realised = base_form
        else:
            realised = base_form

        #  Get gender from parent or "grandparent" or self, in that order
        discourse_function = element.discourse_function
        parent = element.parent
        if element.parent:
            if element.discourse_function == HEAD:
                discourse_function = parent.discourse_function
            if parent.gender and parent.parent:
                parent = parent.parent
        else:
            parent = element

        # If parent or grandparent is a verb phrase and the adjective is
        # a modifier, assume it's a direct object attribute if there is
        # one.
        if (
                parent.category == VERB_PHRASE and
                discourse_function in [
                    FRONT_MODIFIER, PRE_MODIFIER, POST_MODIFIER]
        ):
            complements = parent.complements
            direct_object = None
            for complement in complements:
                if complement.discourse_function == OBJECT:
                    direct_object = complement
                    break
                if direct_object:
                    parent = direct_object

        #  Feminine
        #  The rules used here apply to the most general cases.
        #  Exceptions are meant to be specified in the lexicon or by the user
        #  by means of the FrenchLexicalFeature.FEMININE_SINGULAR feature.
        if element.is_feminine:
            realised = self.feminize_singular_element(element, realised)

        # Plural
        # The rules used here apply to the most general cases.
        # Exceptions are meant to be specified in the lexicon or by the user
        # by means of the LexicalFeature.PLURAL and
        # FrenchLexicalFeature.FEMININE_PLURAL features.
        if parent.is_plural:
            if element.is_feminine:
                if element.feminine_plural:
                    realised = element.feminine_plural
                else:
                    realised = '%ss' % (realised)
            elif element.plural:
                realised = element.plural
            else:
                realised = self.pluralize(realised)

        realised = '%s%s' % (realised, element.particle)

        return StringElement(string=realised, word=element)

    def morph_noun(self, element, base_word=None):
        # The gender of the inflected word is opposite to the base word
        if (
                base_word
                and set([base_word.gender, element.gender]) == set([MASCULINE, FEMININE])
                and base_word.opposite_gender
        ):
            element.base_form = base_word.opposite_gender
            element.base_word = base_word.lexicon.first(element.base_form, category=NOUN)

        base_form = self.get_base_form(element, base_word)

        if element.is_plural and not element.proper:
            if element.plural and base_word:
                realised = base_word.plural
            else:
                realised = self.pluralize(base_form)
        else:
            realised = base_form

        realised = '%s%s' % (realised, element.particle)
        return StringElement(string=realised, word=element)


    def morph_adverb(self, element, base_word):
        base_form = self.get_base_form(element, base_word)
        #  Comparatives and superlatives are mainly treated by syntax
        #  in French. Only exceptions, provided by the lexicon, are
        #  treated by morphology.
        if element.is_comparative:
            realised = element.comparative if element.comparative else base_word.comparative
            if not realised:
                realised = base_form
        else:
            realised = base_form

        realised = '%s%s' % (realised, element.particle)
        return StringElement(string=realised, word=element)

