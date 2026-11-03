import csv
from collections import Counter
from math import isfinite
from typing import List, Dict, Tuple, Optional
from dataclasses import asdict, dataclass

# Sensitivity experiment: halve the baseline genre bonus (2.0 -> 1.0)
# and double the baseline energy weight (1.5 -> 3.0).
GENRE_MATCH_POINTS = 1.0
MOOD_MATCH_POINTS = 1.0
ENERGY_WEIGHT = 3.0
ACOUSTICNESS_WEIGHT = 0.5
ARTIST_REPEAT_PENALTY = 1.0
GENRE_REPEAT_PENALTY = 0.5

@dataclass
class Song:
    """
    Represents a song and its attributes.
    Required by tests/test_recommender.py
    """
    id: int
    title: str
    artist: str
    genre: str
    mood: str
    energy: float
    tempo_bpm: float
    valence: float
    danceability: float
    acousticness: float

@dataclass
class UserProfile:
    """
    Represents a user's taste preferences.
    Required by tests/test_recommender.py
    """
    favorite_genre: str
    favorite_mood: str
    target_energy: float
    likes_acoustic: bool

class Recommender:
    """
    OOP implementation of the recommendation logic.
    Required by tests/test_recommender.py
    """
    def __init__(self, songs: List[Song]):
        self.songs = songs

    def recommend(self, user: UserProfile, k: int = 5) -> List[Song]:
        songs_by_id = {song.id: song for song in self.songs}
        results = recommend_songs(asdict(user), [asdict(song) for song in self.songs], k)
        return [songs_by_id[song["id"]] for song, _, _ in results]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # List-dependent penalties are included by recommend_songs; this method
        # explains one song's preference match without a selected-list context.
        _, reasons = score_song(asdict(user), asdict(song))
        return "; ".join(reasons)

def load_songs(csv_path: str) -> List[Dict]:
    """Load song dictionaries with integer IDs and floating-point audio attributes."""
    numeric_fields = (
        "energy", "tempo_bpm", "valence", "danceability", "acousticness"
    )
    with open(csv_path, newline="", encoding="utf-8") as csv_file:
        songs = []
        for song in csv.DictReader(csv_file):
            song["id"] = int(song["id"])
            for field in numeric_fields:
                song[field] = float(song[field])
            songs.append(song)
    return songs

def score_song(user_prefs: Dict, song: Dict) -> Tuple[float, List[str]]:
    """Return a full-precision preference score and reasons for its points."""
    genre = user_prefs.get("favorite_genre", user_prefs.get("genre", ""))
    mood = user_prefs.get("favorite_mood", user_prefs.get("mood", ""))
    target_energy = (
        user_prefs["target_energy"]
        if "target_energy" in user_prefs else user_prefs["energy"]
    )
    energy = song["energy"]
    acousticness = song["acousticness"]
    for name, value in (
        ("target_energy", target_energy),
        ("song energy", energy),
        ("acousticness", acousticness),
    ):
        if not 0 <= value <= 1:
            raise ValueError(f"{name} must be between 0 and 1")

    score = 0.0
    reasons = []
    if genre.strip().casefold() == song["genre"].strip().casefold():
        score += GENRE_MATCH_POINTS
        reasons.append(f"genre match (+{GENRE_MATCH_POINTS:.1f})")
    if mood.strip().casefold() == song["mood"].strip().casefold():
        score += MOOD_MATCH_POINTS
        reasons.append(f"mood match (+{MOOD_MATCH_POINTS:.1f})")

    energy_points = ENERGY_WEIGHT * (1 - abs(energy - target_energy))
    score += energy_points
    reasons.append(f"energy similarity (+{energy_points:.3f})")

    if user_prefs.get("likes_acoustic", False):
        acoustic_points = ACOUSTICNESS_WEIGHT * acousticness
        score += acoustic_points
        reasons.append(f"acoustic preference (+{acoustic_points:.3f})")

    return score, reasons

def recommend_songs(
    user_prefs: Dict,
    songs: List[Dict],
    k: int = 5,
    *,
    artist_penalty: float = ARTIST_REPEAT_PENALTY,
    genre_penalty: float = GENRE_REPEAT_PENALTY,
) -> List[Tuple[Dict, float, str]]:
    """Select songs greedily using scores reduced by prior artist/genre counts.

    Each earlier artist match costs artist_penalty points; each earlier genre
    match costs genre_penalty points. Both apply when both labels repeat.
    Returned scores include the penalties at selection time and may be negative.
    Set both penalties to zero to reproduce ranking by preference score alone.
    """
    for name, penalty in (("artist_penalty", artist_penalty), ("genre_penalty", genre_penalty)):
        if not isfinite(penalty) or penalty < 0:
            raise ValueError(f"{name} must be finite and nonnegative")
    if k <= 0:
        return []

    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, reasons))

    artist_counts = Counter()
    genre_counts = Counter()
    recommendations = []
    while scored_songs and len(recommendations) < k:
        candidates = []
        for index, (song, base_score, reasons) in enumerate(scored_songs):
            artist = song["artist"].strip().casefold()
            genre = song["genre"].strip().casefold()
            artist_cost = artist_penalty * artist_counts[artist]
            genre_cost = genre_penalty * genre_counts[genre]
            adjusted_reasons = list(reasons)
            if artist_cost:
                adjusted_reasons.append(f"repeated artist penalty (-{artist_cost:.3f})")
            if genre_cost:
                adjusted_reasons.append(f"repeated genre penalty (-{genre_cost:.3f})")
            candidates.append((
                index, base_score - artist_cost - genre_cost, adjusted_reasons,
            ))

        index, score, reasons = min(
            candidates, key=lambda item: (-item[1], scored_songs[item[0]][0]["id"])
        )
        song, _, _ = scored_songs.pop(index)
        recommendations.append((song, score, "; ".join(reasons)))
        artist_counts[song["artist"].strip().casefold()] += 1
        genre_counts[song["genre"].strip().casefold()] += 1

    return recommendations
