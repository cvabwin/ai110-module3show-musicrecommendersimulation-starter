"""
Command line runner for the Music Recommender Simulation.

This file helps you quickly run and test your recommender.

You will implement the functions in recommender.py:
- load_songs
- score_song
- recommend_songs
"""

if __package__:
    from .recommender import load_songs, recommend_songs
else:
    from recommender import load_songs, recommend_songs


def main() -> None:
    songs = load_songs("data/songs.csv")

    # Starter example profile
    user_prefs = {"genre": "pop", "mood": "happy", "energy": 0.8}

    recommendations = recommend_songs(user_prefs, songs, k=5)

    divider = "=" * 60
    print(divider)
    print("MUSIC RECOMMENDER")
    print(divider)
    print(f"Loaded songs: {len(songs)}")
    print(
        f"Profile: genre={user_prefs['genre']} | mood={user_prefs['mood']}"
        f" | energy={user_prefs['energy']:.2f}"
    )
    print(f"\nTop {len(recommendations)} recommendations")
    print("-" * 60)
    for rank, (song, score, explanation) in enumerate(recommendations, start=1):
        print(f"{rank}. {song['title']} - {song['artist']}")
        print(f"   Final score: {score:.3f}")
        print("   Reasons:")
        for reason in explanation.split("; "):
            print(f"     - {reason}")
        print()


if __name__ == "__main__":
    main()
