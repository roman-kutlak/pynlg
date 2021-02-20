# encoding: utf-8

"""Test suite of phrase realisation"""

from pynlg.lexicon.feature.number import PLURAL
from pynlg.lexicon.feature.gender import FEMININE
from pynlg.lexicon.feature import NUMBER
from pynlg.lexicon.feature.lexical import GENDER
from pynlg.lexicon.feature.category import DETERMINER, NOUN, ADJECTIVE
from pynlg import make_noun_phrase


def test_realise_noun_phrase_feminine_singular(lexicon_fr):
    un = lexicon_fr.first('un', category=DETERMINER)
    une = un.inflex(gender=FEMININE)
    maison = lexicon_fr.first('maison', category=NOUN)
    beau = lexicon_fr.first('beau', category=ADJECTIVE)
    belle = beau.inflex(gender=FEMININE)
    perdu = lexicon_fr.first('perdu', category=ADJECTIVE)
    perdue = perdu.inflex(gender=FEMININE)
    phrase = make_noun_phrase(
        lexicon=lexicon_fr, specifier=une, noun=maison, modifiers=[belle, perdue])
    phrase = phrase.realise()
    phrase = phrase.realise_morphology()
    assert phrase.components[0].realisation == 'une'
    assert phrase.components[1].realisation == 'belle'
    assert phrase.components[2].realisation == 'maison'
    assert phrase.components[3].realisation == 'perdue'


def test_realise_noun_phrase_feminine_plural(lexicon_fr):
    un = lexicon_fr.first('un', category=DETERMINER)
    des = un.inflex(gender=FEMININE, number=PLURAL)
    maison = lexicon_fr.first('maison', category=NOUN)
    maisons = maison.inflex(gender=FEMININE, number=PLURAL)
    beau = lexicon_fr.first('beau', category=ADJECTIVE)
    belles = beau.inflex(gender=FEMININE, number=PLURAL)
    perdu = lexicon_fr.first('perdu', category=ADJECTIVE)
    perdues = perdu.inflex(gender=FEMININE, number=PLURAL)
    phrase = make_noun_phrase(
        lexicon=lexicon_fr, specifier=des, noun=maisons, modifiers=[belles, perdues])
    phrase = phrase.realise()
    phrase = phrase.realise_morphology()
    assert phrase.components[0].realisation == 'des'
    assert phrase.components[1].realisation == 'belles'
    assert phrase.components[2].realisation == 'maisons'
    assert phrase.components[3].realisation == 'perdues'


def test_realise_noun_phrase_features_on_parent(lexicon_fr):
    un = lexicon_fr.first('un', category=DETERMINER)
    maison = lexicon_fr.first('maison', category=NOUN)
    beau = lexicon_fr.first('beau', category=ADJECTIVE)
    perdu = lexicon_fr.first('perdu', category=ADJECTIVE)
    phrase = make_noun_phrase(
        lexicon=lexicon_fr, specifier=un, noun=maison, modifiers=[beau, perdu])
    phrase = phrase.realise()
    phrase.features[GENDER] = FEMININE
    phrase.features[NUMBER] = PLURAL
    phrase = phrase.realise_morphology()
    assert phrase.components[0].realisation == 'des'
    assert phrase.components[1].realisation == 'belles'
    assert phrase.components[2].realisation == 'maisons'
    assert phrase.components[3].realisation == 'perdues'
