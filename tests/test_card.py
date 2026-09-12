from sipa_signal.card import NoiseLevel, SignalCard


def test_compression_zero_when_no_words():
    card = SignalCard(0, 0, {}, [], [], 0.0, NoiseLevel.CLEAN)
    assert card.compression() == 0.0


def test_compression_computation():
    card = SignalCard(10, 6, {}, [], [], 0.1, NoiseLevel.CLEAN)
    assert card.compression() == 0.4


def test_to_dict_shape():
    card = SignalCard(10, 6, {"hedge": 2}, ["a"], ["b"], 0.1, NoiseLevel.NOISY)
    d = card.to_dict()
    assert set(d.keys()) == {
        "original_word_count", "signal_word_count", "filler_hits",
        "kept_sentences", "dropped_sentences", "noise_ratio", "noise_level", "compression",
    }
    assert d["noise_level"] == "NOISY"
