# encoding: utf-8

"""Definition of the lexicon handlers."""

from __future__ import absolute_import

import random

from collections import defaultdict
from xml.etree import cElementTree as ElementTree
from os.path import join, dirname, abspath, exists

from .lang import DEFAULT
from .category import ANY
from ..util import ensure_unicode as u
from ..exc import UnhandledLanguage
from ..spec.word import WordElement

__all__ = ['Lexicon']


class Lexicon(object):

    """A Lexicon is a collection of metadata about words of a specific
    language.

    """

    #  node names in lexicon XML files
    BASE = "base"

    #  base form of Word
    CATEGORY = "category"

    #  base form of Word
    ID = "id"

    #  base form of Word
    WORD = "word"

    #  node defining a word
    #  inflectional codes which need to be set as part of INFLECTION feature
    INFL_CODES = [
        "reg", "irreg", "uncount", "inv",
        "metareg", "glreg", "nonCount", "sing", "groupuncount"]

    def __init__(self, language=DEFAULT, auto_index=True):
        """Create a new Lexicon.

        If auto_index is set to True, the XML lexicon corresponding to
        the argument language will be parsed, and several indexes will
        be built at instanciation.

        :param language: the language of the lexicon (default: 'english')
        :param auto_index: whether to parse index the lexicon data at
                           instanciation (default: True)

        """
        self.language = language

        self.words = set()
        self.id_index = {}
        self.base_index = defaultdict(list)
        self.variant_index = defaultdict(list)
        self.category_index = defaultdict(list)

        if auto_index:
            self.make_indexes()

    def __getitem__(self, word_feature):
        return self.get(word_feature, category=ANY)

    def __contains__(self, word_feature):
        return bool(self[word_feature])

    def __repr__(self):
        return '<%s - %s>' % (self.__class__.__name__, self.language)

    def get(self, word_feature, category=ANY):
        """Fetch the WordElement(s) associated to the argument word
        feature (an, a base form etc) from the Lexicon indexes.

        If the word is not found, create it.

        """
        # Search by base form
        if self.base_index.get(word_feature):
            return self.indexed_words_by_category(
                word_feature, category, self.base_index)
        # Search by id
        elif self.id_index.get(word_feature):
            return [self.indexed_words_by_category(
                word_feature, category, self.id_index)]
        # Search by variant
        elif self.variant_index.get(word_feature):
            return self.indexed_words_by_category(
                word_feature, category, self.variant_index)
        return []

    def first(self, word_feature, category=ANY):
        """Return the first matching word identified by the word_feature
        in one of the Lexicon indexes.

        """
        matches = self.get(word_feature, category=category)
        return matches[0] if matches else matches

    def indexed_words_by_category(self, word_feature, category, index):
        if category == ANY:
            return index[word_feature]
        else:
            return [w for w in index[word_feature] if w.category == category]

    def parse_xml_lexicon(self):
        return ElementTree.parse(self.lexicon_filepath)

    def make_indexes(self):
        """Parse the appropriate XML lexicon, and build several indexes,
        allowing fast access using several facets (id, word, base,
        variant, category).

        """
        self.tree = self.parse_xml_lexicon()
        root = self.tree.getroot()
        for word_node in root:
            word = self.word_from_node(word_node)
            if word:
                self.words.add(word)
                self.index_word(word)

    def word_from_node(self, word_node):
        """Convert a word node of the lexicon to a WordElement."""
        if word_node.tag != self.WORD:
            return None
        word = WordElement(base_form=None, category=None, id=None, lexicon=self)
        inflections = []
        for feature_node in word_node:
            feature_name = u(feature_node.tag.strip())
            feature_value = feature_node.text
            assert bool(feature_name), "empty feature_name for word_node %s" % (
                feature_value)
            if feature_value is not None:
                feature_value = u(feature_value.strip())

            # Set word base_form, id, category, inflection codes and features
            if feature_name == self.BASE:
                word.base_form = feature_value
            elif feature_name == self.ID:
                word.id = feature_value
            elif feature_name == self.CATEGORY:
                word.category = feature_value.upper()
            elif not feature_value:
                if feature_name in self.INFL_CODES:
                    inflections.append(feature_name)
                else:
                    word[feature_name] = True
            else:
                word[feature_name] = feature_value

        # If no inflection is specified, assume the word is regular
        inflections = inflections or [u'reg']

        # The default inflection code is "reg" if we have it, else we take
        # random pick from the available inflection codes
        if u'reg' in inflections:
            default_inflection = u'reg'
        else:
            default_inflection = random.choice(inflections)

        # Set inflection information on word
        word.default_inflection_variant = default_inflection
        word.inflection_variants = inflections

        return word

    def index_word(self, word):
        if word.base_form:
            self.base_index[word.base_form].append(word)
            self.variant_index[word.base_form].append(word)
        if word.id is not None:
            if word.id in self.id_index:
                raise ValueError(
                    'Index %d already in id_index' % (int(word.id)))
            else:
                self.id_index[word.id] = word
        if word.category is not None:
            self.category_index[word.category].append(word)

    @property
    def lexicon_filepath(self):
        """Return the path to the XML lexicon file associated with the
        instance language.

        """
        filepath = abspath(join(dirname(__file__), 'data', '%s-lexicon.xml' % (
            self.language)))
        if not exists(filepath):
            raise UnhandledLanguage(
                '%s language is not handled: %s file not found.' % (
                    self.language, filepath))
        return filepath
