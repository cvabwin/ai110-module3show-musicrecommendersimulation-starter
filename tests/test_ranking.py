from copy import deepcopy
from unittest.mock import patch

import pytest

from src.recommender import load_songs, recommend_songs, score_song


def test_scores_every_song_once_and_ranks_before_selecting():
    songs = [{"id": i, "artist": str(i), "genre": str(i)} for i in (3, 2, 1, 4)]
    original = deepcopy(songs)
    # A small score difference must outrank the ID tie-breaker.
    with patch("src.recommender.score_song", side_effect=[
        (1.0, ["first reason"]),
        (2.0, ["genre match", "energy similarity"]),
        (2.0, ["tied score"]),
        (2.0001, ["highest score"]),
    ]) as judge:
        results = recommend_songs({}, songs, k=3)

    assert judge.call_count == len(songs)
    assert [call.args for call in judge.call_args_list] == [({}, song) for song in songs]
    assert [song["id"] for song, _, _ in results] == [4, 1, 2]
    assert results[-1][2] == "genre match; energy similarity"
    assert songs == original


def test_catalog_recommendations_include_scores_and_explanations():
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    results = recommend_songs(prefs, songs, artist_penalty=0, genre_penalty=0)

    assert len(results) == 5
    assert results[0][0]["title"] == "Sunrise City"
    for song, score, explanation in results:
        expected_score, reasons = score_song(prefs, song)
        assert score == expected_score
        assert explanation == "; ".join(reasons)


@pytest.mark.parametrize("k, expected_count", [(0, 0), (-1, 0), (1, 1), (30, 18)])
def test_result_limit(k, expected_count):
    songs = load_songs("data/songs.csv")
    prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    assert len(recommend_songs(prefs, songs, k)) == expected_count


def test_empty_catalog():
    assert recommend_songs({}, []) == []
