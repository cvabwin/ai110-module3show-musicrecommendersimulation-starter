import pytest

from src.recommender import load_songs, score_song


def test_study_profile_matches_recipe_examples():
    songs = load_songs("data/songs.csv")
    profile = {
        "favorite_genre": " LOFI ",
        "favorite_mood": " Chill ",
        "target_energy": 0.40,
        "likes_acoustic": True,
    }

    score, reasons = score_song(profile, songs[1])

    assert score == pytest.approx(4.825)
    assert reasons == [
        "genre match (+2.0)",
        "mood match (+1.0)",
        "energy similarity (+1.470)",
        "acoustic preference (+0.355)",
    ]
    assert score_song(profile, songs[2])[0] == pytest.approx(0.785)


@pytest.mark.parametrize("energy, expected", [(0.0, 1.5), (0.5, 0.75), (1.0, 0.0)])
def test_energy_rewards_closeness_without_category_or_acoustic_bonus(energy, expected):
    profile = {"genre": "pop", "mood": "happy", "energy": 0.0}
    song = {"genre": "rock", "mood": "intense", "energy": energy, "acousticness": 1.0}

    score, reasons = score_song(profile, song)

    assert score == pytest.approx(expected)
    assert reasons == [f"energy similarity (+{expected:.3f})"]


def test_perfect_match_earns_maximum_score():
    profile = {"genre": "pop", "mood": "happy", "energy": 0.8, "likes_acoustic": True}
    song = {"genre": " POP ", "mood": " Happy ", "energy": 0.8, "acousticness": 1.0}

    assert score_song(profile, song)[0] == pytest.approx(5.0)


@pytest.mark.parametrize("value", [-0.1, 1.1, float("nan")])
@pytest.mark.parametrize("field", ["target_energy", "energy", "acousticness"])
def test_rejects_features_outside_unit_interval(field, value):
    profile = {"favorite_genre": "pop", "favorite_mood": "happy", "target_energy": 0.8}
    song = {"genre": "pop", "mood": "happy", "energy": 0.8, "acousticness": 0.2}
    if field == "target_energy":
        profile[field] = value
    else:
        song[field] = value

    with pytest.raises(ValueError, match="must be between 0 and 1"):
        score_song(profile, song)
