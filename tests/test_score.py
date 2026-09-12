from sipa_signal.card import NoiseLevel
from sipa_signal.score import classify_noise, noise_score


def test_noise_score_ratio():
    assert noise_score(5, 100) == 0.05
    assert noise_score(0, 100) == 0.0
    assert noise_score(0, 0) == 0.0


def test_classify_boundaries():
    assert classify_noise(0.0) == NoiseLevel.CLEAN
    assert classify_noise(0.05) == NoiseLevel.CLEAN
    assert classify_noise(0.051) == NoiseLevel.NOISY
    assert classify_noise(0.20) == NoiseLevel.NOISY
    assert classify_noise(0.201) == NoiseLevel.VERY_NOISY


def test_same_ratio_always_same_class():
    results = {classify_noise(0.3) for _ in range(20)}
    assert len(results) == 1
