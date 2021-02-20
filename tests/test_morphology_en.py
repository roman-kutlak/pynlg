# encoding: utf-8

"""Test suite of the french morphology rules."""

import pytest

from pynlg.morphology.en import EnglishMorphologyRules
from pynlg.spec.phrase import PhraseElement
from pynlg.spec.string import StringElement
from pynlg.lexicon.feature import NUMBER, IS_COMPARATIVE, IS_SUPERLATIVE, POSSESSIVE
from pynlg.lexicon.feature.category import ADJECTIVE, ADVERB, VERB_PHRASE, NOUN_PHRASE, VERB, PRONOUN
from pynlg.lexicon.feature.lexical import REFLEXIVE, GENDER
from pynlg.lexicon.feature.gender import MASCULINE, FEMININE
from pynlg.lexicon.feature.number import PLURAL, SINGULAR, BOTH
from pynlg.lexicon.feature.discourse import OBJECT, PRE_MODIFIER, FRONT_MODIFIER, POST_MODIFIER
from pynlg.lexicon.feature.internal import DISCOURSE_FUNCTION, COMPLEMENTS
from pynlg.lexicon.feature.person import FIRST, SECOND, THIRD
from pynlg.lexicon.feature.tense import PRESENT, PAST, FUTURE, CONDITIONAL
from pynlg.lexicon.feature.form import (
    BARE_INFINITIVE, SUBJUNCTIVE, GERUND, INFINITIVE,
    PRESENT_PARTICIPLE, PAST_PARTICIPLE, INDICATIVE, IMPERATIVE)
from pynlg.lexicon.feature import PERSON, TENSE, FORM


@pytest.fixture
def morph_rules_en():
    return EnglishMorphologyRules()


@pytest.mark.parametrize('s, expected', [
    ('person', 'people'),
    ('fish', 'fish'),
    ('child', 'children'),
    ('book', 'books'),
    ('octopus', 'octopodes'),
    ('index', 'indices'),
    ('aquarium', 'aquaria'),
    ('analysis', 'analyses'),
])
def test_pluralize(morph_rules_en, s, expected):
    assert morph_rules_en.pluralize(s) == expected


@pytest.mark.parametrize('word, features, expected', [
    ('I', {GENDER: MASCULINE}, 'he'),
    ('I', {GENDER: FEMININE}, 'she'),
    ('I', {GENDER: MASCULINE, NUMBER: PLURAL}, 'they'),
])
def test_morph_determiner(lexicon_en, morph_rules_en, word, features, expected):
    element = lexicon_en.first(word)
    for k, v in features.items():
        element.features[k] = v
    inflected_form = morph_rules_en.morph_determiner(element)
    assert inflected_form.realisation == expected


@pytest.mark.parametrize('word, features, expected', [
    ('good', {}, 'good'),
    ('good', {IS_COMPARATIVE: True}, 'better'),
    ('good', {IS_SUPERLATIVE: True}, 'best'),
    ('sad', {}, 'sad'),
    ('sad', {IS_COMPARATIVE: True}, 'sadder'),
    ('sad', {IS_SUPERLATIVE: True}, 'saddest'),
    ('brainy', {}, 'brainy'),
    ('brainy', {IS_COMPARATIVE: True}, 'brainier'),
    ('brainy', {IS_SUPERLATIVE: True}, 'brainiest'),
    ('gray', {}, 'gray'),
    ('gray', {IS_COMPARATIVE: True}, 'grayer'),
    ('gray', {IS_SUPERLATIVE: True}, 'grayest'),
    ('densely-populated', {}, 'densely-populated'),
    ('densely-populated', {IS_COMPARATIVE: True}, 'more densely-populated'),
    ('densely-populated', {IS_SUPERLATIVE: True}, 'most densely-populated'),
    ('fine', {}, 'fine'),
    ('fine', {IS_COMPARATIVE: True}, 'finer'),
    ('fine', {IS_SUPERLATIVE: True}, 'finest'),
    ('clear', {}, 'clear'),
    ('clear', {IS_COMPARATIVE: True}, 'clearer'),
    ('clear', {IS_SUPERLATIVE: True}, 'clearest'),
    ('personal', {}, 'personal'),
    ('personal', {IS_COMPARATIVE: True}, 'more personal'),
    ('personal', {IS_SUPERLATIVE: True}, 'most personal'),
    ('apt', {}, 'apt'),
    ('apt', {IS_COMPARATIVE: True}, 'more apt'),
    ('apt', {IS_SUPERLATIVE: True}, 'most apt'),
    ('tangled', {}, 'tangled'),
    ('tangled', {IS_COMPARATIVE: True}, 'more tangled'),
    ('tangled', {IS_SUPERLATIVE: True}, 'most tangled'),
])
def test_morph_adjective(lexicon_en, morph_rules_en, word, features, expected):
    element = lexicon_en.first(word)
    for k, v in features.items():
        element.features[k] = v
    inflected_form = morph_rules_en.morph_adjective(element)
    assert inflected_form.realisation == expected


@pytest.mark.parametrize('word, features, expected', [
    ('quietly', {}, 'quietly'),
    ('quietly', {IS_COMPARATIVE: True}, 'more quietly'),
    ('quietly', {IS_SUPERLATIVE: True}, 'most quietly'),
    ('slowly', {}, 'slowly'),
    ('slowly', {IS_COMPARATIVE: True}, 'more slowly'),
    ('slowly', {IS_SUPERLATIVE: True}, 'most slowly'),
    ('seriously', {}, 'seriously'),
    ('seriously', {IS_COMPARATIVE: True}, 'more seriously'),
    ('seriously', {IS_SUPERLATIVE: True}, 'most seriously'),
    ('hard', {}, 'hard'),
    ('hard', {IS_COMPARATIVE: True}, 'harder'),
    ('hard', {IS_SUPERLATIVE: True}, 'hardest'),
    ('fast', {}, 'fast'),
    ('fast', {IS_COMPARATIVE: True}, 'faster'),
    ('fast', {IS_SUPERLATIVE: True}, 'fastest'),
    ('late', {}, 'late'),
    ('late', {IS_COMPARATIVE: True}, 'later'),
    ('late', {IS_SUPERLATIVE: True}, 'latest'),
    ('badly', {}, 'badly'),
    ('badly', {IS_COMPARATIVE: True}, 'worse'),
    ('badly', {IS_SUPERLATIVE: True}, 'worst'),
    ('far', {}, 'far'),
    ('far', {IS_COMPARATIVE: True}, 'farther'),
    ('far', {IS_SUPERLATIVE: True}, 'farthest'),
    ('early', {}, 'early'),
    ('early', {IS_COMPARATIVE: True}, 'earlier'),
    ('early', {IS_SUPERLATIVE: True}, 'earliest'),
    ('little', {}, 'little'),
    ('little', {IS_COMPARATIVE: True}, 'less'),
    ('little', {IS_SUPERLATIVE: True}, 'least'),
    ('well', {}, 'well'),
    ('well', {IS_COMPARATIVE: True}, 'better'),
    ('well', {IS_SUPERLATIVE: True}, 'best'),
])
def test_morph_adverb(lexicon_en, morph_rules_en, word, features, expected):
    element = lexicon_en.first(word, category=ADVERB)
    for k, v in features.items():
        element.features[k] = v
    inflected_form = morph_rules_en.morph_adverb(element)
    assert inflected_form.realisation == expected


@pytest.mark.parametrize('word, base_word, features, expected', [
    # No transformation
    ('book', 'book', {}, 'book'),
    # Simple pluralisation based on plural feature of base word
    ('book', 'book', {NUMBER: PLURAL}, 'books'),
    # Pluralisation based on plural feature of base word
    ('analysis', 'analysis', {NUMBER: PLURAL}, 'analyses'),
    # Simple pluralisation using +s rule, because word is not in lexicon
    ('keyboard', 'keyboard', {NUMBER: PLURAL}, 'keyboards'),
])
def test_morph_noun(lexicon_en, morph_rules_en, word, base_word, features, expected):
    base_word = lexicon_en.first(base_word)
    element = lexicon_en.first(word)
    for k, v in features.items():
        element.features[k] = v
    inflected_form = morph_rules_en.morph_noun(element, base_word)
    assert inflected_form.realisation == expected


@pytest.mark.parametrize('word, features, expected', [
    # No transformation
    ('I', {}, 'I'),
    ('I', {NUMBER: PLURAL, PERSON: FIRST}, 'we'),
    ('I', {NUMBER: PLURAL, PERSON: FIRST, REFLEXIVE: True}, 'ourselves'),
    ('I', {NUMBER: SINGULAR, PERSON: THIRD, POSSESSIVE: True, GENDER: MASCULINE}, 'his'),
])
def test_morph_pronoun(lexicon_en, morph_rules_en, word, features, expected):
    element = lexicon_en.first(word, PRONOUN)
    for k, v in features.items():
        element.features[k] = v
    inflected_form = morph_rules_en.morph_pronoun(element)
    assert inflected_form.realisation == expected

