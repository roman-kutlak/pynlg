from pynlg.lexicon.feature.category import NOUN, ADJECTIVE, DETERMINER
from pynlg.lexicon.feature.gender import FEMININE
from pynlg import make_noun_phrase


def test_basic_example(lexicon_fr):
    """Test from original github page."""
    un = lexicon_fr.first(u'un', category=DETERMINER)
    maison = lexicon_fr.first(u'maison', category=NOUN)
    maison = maison.inflex(gender=FEMININE)
    beau = lexicon_fr.first(u'beau', category=ADJECTIVE)
    perdu = lexicon_fr.first(u'perdu', category=ADJECTIVE)
    phrase = make_noun_phrase(lexicon=lexicon_fr, specifier=un, noun=maison, modifiers=[beau, perdu])
    syntaxically_realised_phrase = phrase.realise()
    # FIXME: there is a bug which loses the features of the head noun
    syntaxically_realised_phrase.gender = FEMININE
    morphologically_realised_phrase = syntaxically_realised_phrase.realise_morphology()

    expected = ['une', 'belle', 'maison', 'perdue']
    actual = [x.realisation for x in morphologically_realised_phrase.components]
    assert actual == expected
