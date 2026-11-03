from copy import deepcopy
from unittest.mock import patch

import pytest

from src.recommender import Recommender, Song, UserProfile, load_songs, recommend_songs


def test_repeats_are_normalized_cumulative_and_recomputed_after_each_selection():
    songs = [
        {"id": 1, "artist": "Artist A", "genre": "rock"},
        {"id": 2, "artist": " ARTIST A ", "genre": " ROCK "},
        {"id": 3, "artist": "Artist B", "genre": "jazz"},
        {"id": 4, "artist": "Artist C", "genre": "rock"},
        {"id": 5, "artist": "Artist A", "genre": "rock"},
    ]
    original = deepcopy(songs)
    with patch("src.recommender.score_song", side_effect=[
        (5.0, ["match"]), (4.9, ["match"]), (4.0, ["match"]),
        (3.9, ["match"]), (4.8, ["match"]),
    ]) as scorer:
        results = recommend_songs({}, songs, k=5)

    assert scorer.call_count == 5
    assert [song["id"] for song, _, _ in results] == [1, 3, 2, 4, 5]
    assert [score for _, score, _ in results] == pytest.approx([5, 4, 3.4, 2.9, 1.3])
    assert results[0][2] == "match"
    assert results[2][2] == (
        "match; repeated artist penalty (-1.000); repeated genre penalty (-0.500)"
    )
    assert results[-1][2] == (
        "match; repeated artist penalty (-2.000); repeated genre penalty (-1.500)"
    )
    assert songs == original


@pytest.mark.parametrize("artist_penalty, genre_penalty", [(1.0, 0), (0, 0.5)])
def test_each_penalty_can_promote_a_different_artist_or_genre(artist_penalty, genre_penalty):
    songs = [
        {"id": 1, "artist": "A", "genre": "pop"},
        {"id": 2, "artist": "A", "genre": "pop"},
        {"id": 3, "artist": "B", "genre": "jazz"},
    ]
    with patch("src.recommender.score_song", side_effect=[
        (4.0, []), (3.9, []), (3.6, []),
    ]):
        results = recommend_songs(
            {}, songs, k=2, artist_penalty=artist_penalty, genre_penalty=genre_penalty
        )
    assert [song["id"] for song, _, _ in results] == [1, 3]


def test_penalties_are_soft_and_can_produce_negative_scores():
    songs = [
        {"id": 1, "artist": "A", "genre": "pop"},
        {"id": 2, "artist": "A", "genre": "pop"},
    ]
    with patch("src.recommender.score_song", return_value=(1.0, [])):
        results = recommend_songs({}, songs, k=5)
    assert [score for _, score, _ in results] == [1.0, -0.5]


@pytest.mark.parametrize("value", [-1, float("nan"), float("inf")])
@pytest.mark.parametrize("field", ["artist_penalty", "genre_penalty"])
def test_rejects_invalid_penalty_weights(field, value):
    with pytest.raises(ValueError, match="finite and nonnegative"):
        recommend_songs({}, [], **{field: value})


def test_object_interface_uses_the_same_diversity_selection():
    catalog = load_songs("data/songs.csv")
    prefs = {"favorite_genre": "lofi", "favorite_mood": "chill",
             "target_energy": 0.4, "likes_acoustic": True}
    recommender = Recommender([Song(**song) for song in catalog])
    results = recommender.recommend(UserProfile(**prefs))
    expected = recommend_songs(prefs, catalog)
    assert [song.id for song in results] == [song["id"] for song, _, _ in expected]
    assert results[0] is next(song for song in recommender.songs if song.id == results[0].id)
