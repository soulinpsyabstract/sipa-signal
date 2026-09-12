from sipa_signal.card import NoiseLevel
from sipa_signal.extract import extract


def test_pure_filler_sentence_is_dropped():
    card = extract("Great question! The server has 4 CPUs and 16GB RAM.")
    assert any("Great question" in s for s in card.dropped_sentences)
    assert any("4 CPUs" in s for s in card.kept_sentences)


def test_hedge_inside_a_real_claim_is_kept_not_dropped():
    card = extract("It's worth noting that the deploy failed at 03:14 UTC.")
    # the sentence carries a real claim (a timestamp) even though it opens
    # with a hedge phrase - it must be kept, not dropped
    assert len(card.kept_sentences) == 1
    assert len(card.dropped_sentences) == 0
    assert card.filler_hits["hedge"] >= 1


def test_clean_text_has_no_filler_hits():
    card = extract("The build failed. Exit code 137. Memory limit exceeded.")
    assert sum(card.filler_hits.values()) == 0
    assert card.noise_level == NoiseLevel.CLEAN
    assert card.dropped_sentences == []


def test_very_noisy_text_classified_correctly():
    text = (
        "Great question! I'd be happy to help. As an AI, I think it's worth "
        "noting that, in my opinion, arguably, to some extent, the answer is 4."
    )
    card = extract(text)
    assert card.noise_level in (NoiseLevel.NOISY, NoiseLevel.VERY_NOISY)


def test_compression_reflects_dropped_sentences():
    card = extract("Sure, I'd be happy to help. The invoice total is $412.")
    assert card.compression() > 0
    assert card.signal_word_count < card.original_word_count


def test_original_word_count_is_stable():
    text = "One. Two. Three."
    card = extract(text)
    assert card.original_word_count == 3
