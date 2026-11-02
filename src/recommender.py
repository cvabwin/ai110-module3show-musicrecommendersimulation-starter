import csv
from typing import List, Dict, Tuple, Optional
from dataclasses import dataclass

GENRE_MATCH_POINTS = 2.0
MOOD_MATCH_POINTS = 1.0
ENERGY_WEIGHT = 1.5
ACOUSTICNESS_WEIGHT = 0.5

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
        # TODO: Implement recommendation logic
        return self.songs[:k]

    def explain_recommendation(self, user: UserProfile, song: Song) -> str:
        # TODO: Implement explanation logic
        return "Explanation placeholder"

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

def recommend_songs(user_prefs: Dict, songs: List[Dict], k: int = 5) -> List[Tuple[Dict, float, str]]:
    """Return the top k song-score-explanation tuples, breaking score ties by ID."""
    if k <= 0:
        return []

    scored_songs = []
    for song in songs:
        score, reasons = score_song(user_prefs, song)
        scored_songs.append((song, score, "; ".join(reasons)))

    ranked_songs = sorted(scored_songs, key=lambda rec: (-rec[1], rec[0]["id"]))
    return ranked_songs[:k]
