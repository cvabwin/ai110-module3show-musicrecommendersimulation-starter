"""
Command line runner for the Music Recommender Simulation.

Run diverse preference profiles and edge cases against the same catalog.
"""

from itertools import zip_longest
from textwrap import wrap

if __package__:
    from .recommender import load_songs, recommend_songs
else:
    from recommender import load_songs, recommend_songs


# Named dictionaries make each evaluation profile easy to reproduce or adjust.
EVALUATION_PROFILES = {
    "High-Energy Pop": {"genre": "pop", "mood": "happy", "energy": 0.8},
    "Chill Lofi": {
        "genre": "lofi", "mood": "chill", "energy": 0.4, "likes_acoustic": True,
    },
    "Deep Intense Rock": {"genre": "rock", "mood": "intense", "energy": 0.9},
    # Sad has no exact catalog match; high energy still contributes normally.
    "High-Energy Sad Pop": {"genre": "pop", "mood": "sad", "energy": 0.9},
    # Unknown categories remove both category bonuses; zero tests the lower bound.
    "Unknown Labels, Zero Energy": {
        "genre": "unknown", "mood": "unknown", "energy": 0.0,
    },
    # Probe competing intensity/acoustic signals and the upper energy bound.
    "Maximum-Energy Acoustic Rock": {
        "genre": "rock", "mood": "intense", "energy": 1.0, "likes_acoustic": True,
    },
    # Should produce exactly the same rankings and scores as High-Energy Pop.
    "Pop with Mixed Case and Spaces": {
        "genre": " POP ", "mood": " HaPpY ", "energy": 0.8,
    },
}


def format_recommendation_table(recommendations: list) -> str:
    """Format scores and all reasons in wrapped columns without extra packages."""
    if not recommendations:
        return "No recommendations available."

    headers = ("Rank", "Song", "Artist", "Score", "Reasons")
    widths = (4, 24, 18, 7, 40)
    border = "+" + "+".join("-" * (width + 2) for width in widths) + "+"

    def row(cells: tuple) -> str:
        return "| " + " | ".join(
            cell.ljust(width) for cell, width in zip(cells, widths)
        ) + " |"

    lines = [border, row(headers), border]
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        reasons = []
        for reason in explanation.split("; "):
            reasons.extend(wrap(
                reason, width=widths[4], initial_indent="- ", subsequent_indent="  "
            ))
        columns = (
            wrap(str(rank), widths[0]),
            wrap(song["title"], widths[1]),
            wrap(song["artist"], widths[2]),
            wrap(f"{score:.3f}", widths[3]),
            reasons,
        )
        lines.extend(row(cells) for cells in zip_longest(*columns, fillvalue=""))
        lines.append(border)
    return "\n".join(lines)


def print_recommendations(profile_name: str, user_prefs: dict, songs: list) -> None:
    recommendations = recommend_songs(user_prefs, songs, k=5)

    divider = "=" * 60
    print(divider)
    print(f"MUSIC RECOMMENDER | {profile_name}")
    print(divider)
    print(f"Loaded songs: {len(songs)}")
    print(
        f"Profile: genre={user_prefs['genre']} | mood={user_prefs['mood']}"
        f" | energy={user_prefs['energy']:.2f}"
        f" | likes_acoustic={user_prefs.get('likes_acoustic', False)}"
    )
    print(f"\nTop {len(recommendations)} recommendations")
    print(format_recommendation_table(recommendations))
    print()


def main() -> None:
    songs = load_songs("data/songs.csv")
    for profile_name, user_prefs in EVALUATION_PROFILES.items():
        print_recommendations(profile_name, user_prefs, songs)


if __name__ == "__main__":
    main()
